"""Native full-game controls, companions and safe-camp initialization.

No writes occur at import. The integrators scope freshly authored IDs per
resource path after combining these events with the room's original scripts.
"""
import json
from pathlib import Path
from full_game_support import SOURCE, uid, copy_events

CAMPS = {'R01': 0, 'R07': 1, 'R13': 2, 'R19': 3}
SPRITES = {'roam': '441ccb85-e71b-5fe6-b660-cef68752969d',
           'marty': '536f281c-c90d-5d56-baf6-b280f2ddf557',
           1: '81acd809-6a18-5965-a8f4-fc4cb8c879a1',
           2: 'dd90932f-c028-5da9-b533-c892da1c10ad',
           3: '7d788b83-0487-5c04-888a-29620c966f07'}
PALETTES = {'roam': '4257fff7-f29f-561a-be22-65d1451749cd',
            'marty': 'b0b795bd-6582-55f8-91ce-af3d629a02de',
            1: '0e3736db-2b23-51f3-8c8a-e657fa29e05f',
            2: '07d58cbc-fb55-5936-9445-39285392e4ba',
            3: 'ebf171a2-c6dd-5d22-b5cc-4c08f0ce2337',
            'wood': '72ac1637-8a0a-5e42-9294-bf0ccb68c60c',
            'water': '137a6b22-154c-539d-ac69-a7b672986efa',
            'dusk': 'a89e727c-9a41-5858-9a04-8c19faec44d1',
            'duskwood': '96dbcdf8-2c47-567f-b77b-300e57cfe917',
            'night': '103752d1-a4a7-5c30-b66a-87f5ff883551',
            'nightwood': '656a3609-ce78-5a1e-8edf-b0a88c5c377e'}


def actor_id(h, code, row):
    return row.get('id') or h.actor_id(code, row['key'])


def palette(h, slot, value):
    args = {f'palette{i}': 'keep' for i in range(8)}
    args[f'palette{slot}'] = value
    return h.e('EVENT_PALETTE_SET_SPRITE', args)


def text_speed(h):
    def setting(speed):
        return h.e('EVENT_TEXT_SET_ANIMATION_SPEED', {
            'speedIn': 0, 'speedOut': 0, 'speed': speed, 'allowFastForward': True})
    return [h.cond('FAST_TEXT', 2, [setting(0)],
            [h.cond('FAST_TEXT', 1, [setting(1)], [setting(2)])])]


def music(h, code=None):
    songs = {p.stem.replace('.uge', ''): json.loads(p.read_text())['id']
             for p in (Path(__file__).parent/'assets/music').glob('*.gbsres')}
    def play(name):
        return [h.e('EVENT_MUSIC_PLAY', {'musicId': songs[name]})]
    if code is not None:
        room = int(code[1:]) if code.startswith('R') else 1
        name = 'creek' if 7 <= room <= 12 else 'ridge' if 13 <= room <= 18 else 'hollow' if 19 <= room <= 22 else 'porch'
        normal = play(name)
    else:
        normal = play('porch')
        for lo, hi, name in [(19, 22, 'hollow'), (13, 18, 'ridge'), (7, 12, 'creek')]:
            normal = [h.cond('CURRENT_ROOM', lo,
                [h.cond('CURRENT_ROOM', hi, play(name), copy_events(normal), op='lte')],
                copy_events(normal), op='gte')]
    return [h.cond('AUDIO_OFF', 1, [h.e('EVENT_MUSIC_STOP')],
        [h.cond('MUSIC_OFF', 1, [h.e('EVENT_MUSIC_STOP')],
            [h.cond('P12', 1, play('dawn'), normal)])])]


def apply_options(h, code=None):
    return text_speed(h) + music(h, code)


def character(h):
    return [h.cond('PLAYER_CHARACTER', 1, [h.setv('PLAYER_CHARACTER', 0)], op='gt'),
        h.cond('PLAYER_CHARACTER', 0, [h.setv('PLAYER_CHARACTER', 0)], op='lt'), h.cond('PLAYER_CHARACTER', 1,
        [h.e('EVENT_PLAYER_SET_SPRITE', {'spriteSheetId': SPRITES['marty']}), palette(h, 0, PALETTES['marty'])],
        [h.e('EVENT_PLAYER_SET_SPRITE', {'spriteSheetId': SPRITES['roam']}), palette(h, 0, PALETTES['roam'])])]


def phase_palette(h):
    def colors(leaf, wood):
        return h.e('EVENT_PALETTE_SET_BACKGROUND', {'palette0': PALETTES[leaf], 'palette1': PALETTES[wood],
            **{f'palette{i}': 'keep' for i in range(2, 8)}})
    return [h.cond('PHASE', 1, [colors('dusk', 'duskwood')],
        [h.cond('PHASE', 2, [colors('night', 'nightwood')], [colors(2, 'wood')])])]


def follower_refresh(h, code, actors):
    row = next((a for a in actors if a.get('key') in ['companion', 'moth']), None)
    if row is None:
        return []
    aid = actor_id(h, code, row)
    result = [h.e('EVENT_ACTOR_HIDE', {'actorId': aid})]
    for value, flag in [(3, 'RECRUITED_THUNDERBIRD'), (2, 'RECRUITED_TURTLE'), (1, 'RECRUITED_MOTH')]:
        result = [h.cond('ACTIVE_COMPANION', value,
            [h.cond(flag, 1,
                [h.e('EVENT_ACTOR_SET_SPRITE', {'actorId': aid, 'spriteSheetId': SPRITES[value]}),
                 palette(h, 1, PALETTES[value]), h.e('EVENT_ACTOR_SHOW', {'actorId': aid})],
                [h.e('EVENT_ACTOR_HIDE', {'actorId': aid})])], result)]
    return [h.e('EVENT_ACTOR_COLLISIONS_DISABLE', {'actorId': aid})] + result


def follower_update(h, code, row):
    aid = actor_id(h, code, row)
    return [h.cond('ACTIVE_COMPANION', 0, [h.e('EVENT_ACTOR_HIDE', {'actorId': aid})],
        [h.e('EVENT_ACTOR_GET_POSITION', {'actorId': 'player', 'vectorX': h.V['PX'], 'vectorY': h.V['PY'], 'units': 'pixels'}),
         h.e('EVENT_ACTOR_SET_POSITION', {'actorId': aid,
            'x': {'type': 'max', 'valueA': h.num(8), 'valueB': {'type': 'sub', 'valueA': h.var('PX'), 'valueB': h.num(12)}},
            'y': {'type': 'max', 'valueA': h.num(8), 'valueB': {'type': 'sub', 'valueA': h.var('PY'), 'valueB': h.num(10)}},
            'units': 'pixels'})]), h.wait(2)]


def facing(h, x, y, action):
    """Pixel-exact 2x2-player adjacency with a one-tile overlap on each side."""
    events = [h.setv('NEAR_TARGET', 0)]
    for dx, dy, direction in [(0, 2, 'up'), (0, -2, 'down'), (-2, 0, 'right'), (2, 0, 'left'),
                              (-1, 0, 'right'), (1, 0, 'left'), (0, 1, 'up'), (0, -1, 'down')]:
        def add(value, amount):
            return value if amount == 0 else {'type': 'add', 'valueA': value, 'valueB': h.num(amount)}
        xx = h.num(x) if isinstance(x, int) else x
        yy = h.num(y) if isinstance(y, int) else y
        events.append(h.cond('TARGET_USED', 0, [h.e('EVENT_IF_ACTOR_AT_POSITION',
            {'actorId': 'player', 'x': add(xx, dx), 'y': add(yy, dy), 'units': 'tiles'},
            true=[h.e('EVENT_IF_ACTOR_DIRECTION', {'actorId': 'player', 'direction': {'type': 'direction', 'value': direction}},
                true=[h.setv('NEAR_TARGET', 1)], false=[])], false=[])]))
    return events + [h.cond('TARGET_USED', 0, [h.cond('NEAR_TARGET', 1,
        [h.setv('TARGET_USED', 1)] + copy_events(action))])]


def banked(h, name, script, owner=None):
    """Compile one action once in a banked native custom event.

    Actor parameters are explicit: GB Studio custom events require them for
    scene actor references. Global variables retain their frozen numeric IDs.
    """
    sid = uid('full-banked/' + name)
    if len(script) == 1 and script[0]['command'] == 'EVENT_CALL_CUSTOM_EVENT' and script[0]['args'].get('customEventId') == sid:
        return copy_events(script)
    body = copy_events(script)
    actor_map = {}
    def parameter(original):
        if original == '$self$':
            original = owner or 'player'
        if original == 'player':
            return original
        if original not in actor_map:
            actor_map[original] = str(len(actor_map))
        return actor_map[original]
    def rewrite(value):
        if isinstance(value, dict):
            if 'actorId' in value:
                value['actorId'] = parameter(value['actorId'])
            for key in list(value):
                # Nested far calls bind their actors through the outer event's
                # parameters, rather than embedding scene UUIDs in a function.
                if key.startswith('$actor[') and key.endswith(']$'):
                    value[key] = parameter(value[key])
            if value.get('type') == 'property' and 'target' in value:
                value['target'] = parameter(value['target'])
            for child in value.values():
                rewrite(child)
        elif isinstance(value, list):
            for child in value:
                rewrite(child)
    rewrite(body)
    scope_events(body, 'custom_events/' + name + '.gbsres')
    if not hasattr(h, 'custom_scripts'):
        h.custom_scripts = {}
    h.custom_scripts[sid] = {'_resourceType': 'script', 'id': sid, 'name': name.replace('_', ' '),
        'symbol': 'script_full_' + name.lower(), 'description': 'PocketHoller banked native action.',
        'variables': {}, 'actors': {index: {'id': index, 'name': 'Actor ' + index} for index in actor_map.values()}, 'script': body}
    args = {'customEventId': sid, **{'$actor[' + index + ']$': aid for aid, index in actor_map.items()}}
    return [h.e('EVENT_CALL_CUSTOM_EVENT', args)]


def flush_banked(h):
    """Explicitly materialize registered custom events inside the project."""
    target = SOURCE/'project/custom_events'
    target.mkdir(exist_ok=True)
    for script in getattr(h, 'custom_scripts', {}).values():
        filename = script['symbol'].removeprefix('script_') + '.gbsres'
        (target/filename).write_text(json.dumps(script, indent=2) + '\n')
    return len(getattr(h, 'custom_scripts', {}))


def bank_actor_resources(h):
    """Preserve actors while replacing interaction bodies with native far calls."""
    count = 0
    for scene_path in (SOURCE/'project/scenes').glob('*/scene.gbsres'):
        code = json.loads(scene_path.read_text())['name'].split()[0]
        if not code.startswith('R'):
            continue
        for path in scene_path.parent.glob('actors/*.gbsres'):
            row = json.loads(path.read_text())
            if not row.get('script') or path.stem in ['companion', 'moth']:
                continue
            replacement = banked(h, 'actor_' + code + '_' + path.stem,
                                 row['script'], owner=row['id'])
            scope_events(replacement, str(path.relative_to(SOURCE)))
            row['script'] = replacement
            path.write_text(json.dumps(row, indent=2) + '\n')
            count += 1
    return count


def repair_native_visibility():
    """Pair hide/show with intended collisions, without changing existing IDs.

    Banked actor arguments are resolved through native call sites. Only known
    blocking reset targets regain collision; followers and decorative props
    never acquire it from this repair.
    """
    resources = [(p, json.loads(p.read_text())) for p in (SOURCE/'project').rglob('*.gbsres')]
    scripts = {d['id']: d for _, d in resources if d.get('_resourceType') == 'script'}
    bindings = {sid: {arg: set() for arg in d.get('actors', {})} for sid, d in scripts.items()}
    blockers = set()
    visible_blockers = {'R01': {'marty', 'roam_at_porch'},
        'R09': {'upstream_gate', 'downstream_gate', 'turtle'},
        'R10': {'near_wave', 'middle_wave', 'far_wave'},
        'R11': {'wheel_brace'}, 'R12': {'spillway_wave'}}
    for p, d in resources:
        if d.get('_resourceType') == 'actor':
            scene = json.loads((p.parent.parent/'scene.gbsres').read_text())
            code = scene['name'].split()[0]
            if p.stem in visible_blockers.get(code, set()):
                blockers.add(d['id'])
    def events(value):
        if isinstance(value, dict):
            if 'command' in value:
                yield value
            for child in value.values():
                yield from events(child)
        elif isinstance(value, list):
            for child in value:
                yield from events(child)
    changed = True
    while changed:
        changed = False
        for _, resource in resources:
            context = bindings.get(resource.get('id'), {})
            for event in events(resource):
                if event['command'] != 'EVENT_CALL_CUSTOM_EVENT':
                    continue
                args = event['args']; sid = args['customEventId']
                for arg, values in bindings.get(sid, {}).items():
                    actual = args.get('$actor[' + arg + ']$')
                    resolved = context.get(actual, set()) if actual in context else {actual}
                    before = len(values); values.update(v for v in resolved if v)
                    changed |= len(values) != before
    added = 0; files = 0
    for path, resource in resources:
        context = bindings.get(resource.get('id'), {})
        before = json.dumps(resource)
        def repair(value):
            nonlocal added
            if isinstance(value, dict):
                for child in value.values():
                    repair(child)
            elif isinstance(value, list):
                for child in list(value):
                    repair(child)
                index = 0
                while index < len(value):
                    event = value[index]
                    if not isinstance(event, dict) or 'command' not in event:
                        index += 1; continue
                    aid = event.get('args', {}).get('actorId')
                    actual = context.get(aid, {aid})
                    command = None
                    if event['command'] == 'EVENT_ACTOR_HIDE':
                        command = 'EVENT_ACTOR_COLLISIONS_DISABLE'
                    elif event['command'] == 'EVENT_ACTOR_SHOW' and actual and actual <= blockers:
                        command = 'EVENT_ACTOR_COLLISIONS_ENABLE'
                    if command:
                        following = value[index + 1] if index + 1 < len(value) else {}
                        if following.get('command') != command or following.get('args', {}).get('actorId') != aid:
                            value.insert(index + 1, {'id': uid('visibility/' + str(path.relative_to(SOURCE)) + '/' + event['id'] + '/' + command),
                                'command': command, 'args': {'actorId': aid}})
                            added += 1; index += 1
                    index += 1
        repair(resource)
        if json.dumps(resource) != before:
            path.write_text(json.dumps(resource, indent=2) + '\n'); files += 1
    return {'changedResources': files, 'collisionEventsAdded': added}


def opening_targets(h, code):
    if code == 'R05':
        return [{'key': 'bark_mark', 'x': 12, 'y': 10, 'companion': 1,
            'action': [h.cond('BARK_REVEALED', 0,
                [h.setv('BARK_REVEALED', 1), h.sound('reveal'), h.text('Moth reveals: Trust living light. Try this at the boundary.')],
                [h.text('The bark mark stays clear.')])],
            'wrong': 'A ray mark. LanternMoth can reveal it.'}]
    if code == 'R06':
        return [{'key': 'inscription', 'x': 8, 'y': 8, 'companion': 1,
            'action': [h.cond('GATE_REVEALED', 0,
                [h.setv('GATE_REVEALED', 1), h.sound('reveal'),
                 h.text('The painted arrow fades. The inscription reads:', 'Follow the rays. Turn the latch to the left.')],
                [h.text('Follow the ray latch to the left.')])],
            'wrong': 'This needs Moth. Choose Companion at a safe camp.'}]
    return []


def ability(h, code, targets):
    targets = targets or opening_targets(h, code)
    result = []
    for target in targets:
        action = banked(h, 'ability_' + code + '_' + target['key'], target['action'])
        result += facing(h, target['x'], target['y'], [h.cond('ACTIVE_COMPANION', target['companion'],
            action, [h.text(target['wrong'])])])
    # Empty use is a short non-blocking companion emote, never a dialogue loop.
    result += [h.cond('TARGET_USED', 0, [h.cond('ACTIVE_COMPANION', 0, [], [h.sound('click')])])]
    return result


def interact(h, code, actors):
    result = []
    for row in actors:
        if not row.get('script') or row.get('key') in ['companion', 'moth']:
            continue
        aid = actor_id(h, code, row)
        invocation = banked(h, 'actor_' + code + '_' + row['key'], row['script'], owner=aid)
        checks = [h.e('EVENT_ACTOR_GET_POSITION', {'actorId': aid, 'vectorX': h.V['PX'], 'vectorY': h.V['PY'], 'units': 'tiles'})]
        checks += facing(h, h.var('PX'), h.var('PY'), invocation)
        # R01 has two guides at one coordinate, with one hidden counterpart.
        key = row.get('key')
        if code == 'R01' and key in ['marty', 'roam_at_porch']:
            checks = [h.cond('PLAYER_CHARACTER', 0 if key == 'marty' else 1, checks)]
        if code == 'R09' and key == 'turtle':
            checks = [h.cond('P03', 1, [h.cond('ACTIVE_COMPANION', 2, [], checks)])]
        result += [h.cond('TARGET_USED', 0, checks)]
    return result


def input_bindings(h, code, actors, ability_targets):
    interaction = banked(h, 'interact_' + code, interact(h, code, actors))
    use_ability = banked(h, 'ability_dispatch_' + code, ability(h, code, ability_targets))
    def routed(button):
        ordinary = interaction if button == 'a' else use_ability
        swapped = use_ability if button == 'a' else interaction
        return [h.lock(), h.e('EVENT_SCENE_UPDATE_PAUSE'), h.setv('TARGET_USED', 0), h.cond('SWAP_BUTTONS', 0, copy_events(ordinary), copy_events(swapped))] + follower_refresh(h, code, actors) + [h.e('EVENT_SCENE_UPDATE_RESUME')] + h.release() + [h.unlock()]
    objective = h.objective()
    def any_button(events):
        for event in events:
            if event['command'] == 'EVENT_TEXT':
                event['args']['closeButton'] = 'any'
            for children in event.get('children', {}).values():
                any_button(children)
    any_button(objective)
    quick = [h.lock(), h.e('EVENT_SCENE_UPDATE_PAUSE')] + h.release() + objective + [h.e('EVENT_SCENE_UPDATE_RESUME')] + h.release() + [h.unlock()]
    return [h.e('EVENT_SET_INPUT_SCRIPT', {'input': [button], 'override': True}, true=routed(button)) for button in ['a', 'b']] + [
        h.e('EVENT_SET_INPUT_SCRIPT', {'input': ['start'], 'override': True}, true=banked(h, 'pause', h.pause())),
        h.e('EVENT_SET_INPUT_SCRIPT', {'input': ['select'], 'override': True}, true=quick)]


def reunion(h):
    return [h.cond('P12', 1, [h.cond('ENDING_SEEN', 0,
        [h.text('The real porch lamp burns steady. A familiar voice welcomes you.',
                'You checked the clues, trusted your friends, and brought the light home.',
                'Moth finds the window. Turtle finds the sun. Thunderbird steals toast.'),
         h.text('PocketHoller: After Sundown', 'For Marty and Roam. Thank you for playing.',
                'Story, native art and original music: PocketHoller team.',
                'Created with OpenAI Codex. Engine: GB Studio, Chris Maltby and contributors.',
                'Runtime and template notices: see the source credits.', 'Morning again. Everyone made it home.'),
         h.setv('ENDING_SEEN', 1), h.setv('CAMP_ID', 0),
         h.text('Save now to continue from the peaceful dawn.')] + h.save('R01', 0))])]


def common_init(h, code, actors, ability_targets):
    result = [h.e('EVENT_SHOW_SPRITES'), h.setv('CURRENT_ROOM', int(code[1:])),
              h.setv('TARGET_USED', 0), h.e('EVENT_SCENE_UPDATE_RESUME')]
    result += character(h)
    if code == 'R01':
        guides = {a.get('key'): a for a in actors}
        for key, player in [('marty', 0), ('roam_at_porch', 1)]:
            if key in guides:
                aid = actor_id(h, code, guides[key])
                result.append(h.cond('PLAYER_CHARACTER', player,
                    [h.e('EVENT_ACTOR_ACTIVATE', {'actorId': aid}), h.e('EVENT_ACTOR_SHOW', {'actorId': aid}), h.e('EVENT_ACTOR_COLLISIONS_ENABLE', {'actorId': aid})],
                    [h.e('EVENT_ACTOR_DEACTIVATE', {'actorId': aid}), h.e('EVENT_ACTOR_HIDE', {'actorId': aid}), h.e('EVENT_ACTOR_COLLISIONS_DISABLE', {'actorId': aid})]))
    for slot, pal in [(2, 'marty'), (3, 'roam'), (4, 2), (5, 3), (6, 'water'), (7, 'wood')]:
        result.append(palette(h, slot, PALETTES[pal]))
    result += follower_refresh(h, code, actors) + phase_palette(h) + apply_options(h, code)
    result += input_bindings(h, code, actors, ability_targets)
    if code in CAMPS:
        result.append(h.setv('CAMP_ID', CAMPS[code]))
        if code == 'R19':
            result.append(h.cond('VISITED_R19', 0,
                [h.setv('VISITED_R19', 1), h.text('The roots open a dry trail back to your porch.', 'All three companions can help here. Save before the bell.')]))
        if code == 'R01':
            result += reunion(h)
        checkpoint = h.e('EVENT_IF', {'condition': {'type': 'gt', 'valueA': h.var('CHAPTER'), 'valueB': h.var('LAST_CHECKPOINT')}},
            true=[h.text('A new chapter is ready. Save at this safe camp?')] + h.save(code, CAMPS[code]), false=[])
        result.append(h.cond('P12', 0, [checkpoint]) if code == 'R01' else checkpoint)
    return result + h.release()


def scope_events(value, resource, path='script'):
    """Scope wholly replaced scripts without touching stable resource IDs."""
    if isinstance(value, dict):
        if 'command' in value:
            value['id'] = uid('native-runtime/' + resource + '/' + path)
        for key, child in value.items():
            if key != 'id':
                scope_events(child, resource, path + '/' + key)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            scope_events(child, resource, path + '/' + str(index))


def title_script(h):
    options = {'AUDIO_OFF', 'MUSIC_OFF', 'EFFECTS_OFF', 'REDUCED_SCARES', 'FAST_TEXT', 'SWAP_BUTTONS'}
    newgame = [h.setv(name, 0) for name in h.V if name not in options] + [
        h.setv('SAVE_SCHEMA', 1), h.setv('BUILD_SAVE_EPOCH', 2), h.setv('SESSION_REPLACES_SAVE', 1),
        h.switch('R01', 8, 12, 'up')]
    incompatible = [h.text('This save belongs to another build family. It remains untouched.',
        'Choose New Game for a separate session. Only an explicit camp Save replaces it.')]
    load = [h.e('EVENT_IF_SAVED_DATA', {'saveSlot': 0}, true=[
        h.e('EVENT_PEEK_DATA', {'saveSlot': 0, 'variableSource': h.V['SAVE_SCHEMA'], 'variableDest': h.V['SCHEMA_PEEK']}),
        h.e('EVENT_PEEK_DATA', {'saveSlot': 0, 'variableSource': h.V['BUILD_SAVE_EPOCH'], 'variableDest': h.V['EPOCH_PEEK']}),
        h.cond('SCHEMA_PEEK', 1, [h.cond('EPOCH_PEEK', 2,
            [h.e('EVENT_LOAD_DATA', {'saveSlot': 0})], copy_events(incompatible))], copy_events(incompatible))],
        false=[h.text('No camp save yet. Choose New Game.')])]
    menu = [h.lock()] + h.release() + [h.e('EVENT_DEFINE_LABEL', {'label': 'full-title-menu'}),
        h.menu(['New Game', 'Continue', 'Settings'], 'MENU'),
        h.cond('MENU', 1, [h.e('EVENT_IF_SAVED_DATA', {'saveSlot': 0},
            true=[h.text('Begin a new session? The old save stays until you choose Save.'),
                  h.menu(['Begin', 'Cancel']), h.cond('SUBMENU', 1, copy_events(newgame))],
            false=copy_events(newgame))]), h.cond('MENU', 2, load), h.cond('MENU', 3, h.settings())] + h.release() + [
        h.cond('MENU', 0, [h.unlock(), h.e('EVENT_STOP')]), h.e('EVENT_GOTO_LABEL', {'label': 'full-title-menu'})]
    return [h.e('EVENT_HIDE_SPRITES'), h.e('EVENT_REMOVE_INPUT_SCRIPT', {'input': ['a', 'b', 'start', 'select']}),
        h.setv('CURRENT_ROOM', 0)] + apply_options(h, 'TITLE') + [
        h.e('EVENT_SET_INPUT_SCRIPT', {'input': ['start', 'a'], 'override': True}, true=menu)]


def install_opening():
    """Explicit authorized integration entry point, not an import side effect."""
    from full_game_support import Helpers
    h = Helpers()
    roles = json.loads((Path(__file__).parent/'sprite-role-map.json').read_text())
    replacements = {v['sourceId']: v['id'] for k, v in roles.items() if 'sourceId' in v and not k.startswith('follower')}
    variables = SOURCE/'project/variables.gbsres'
    variables.write_text(json.dumps(h.variables, indent=2) + '\n')
    changed = [str(variables)]
    for scene_path in (SOURCE/'project/scenes').glob('*/scene.gbsres'):
        scene = json.loads(scene_path.read_text())
        code = scene['name'].split()[0]
        if code not in {'TITLE', 'R01', 'R02', 'R03', 'R04', 'R05', 'R06'}:
            continue
        if code == 'TITLE':
            scene['script'] = title_script(h)
            scope_events(scene['script'], str(scene_path.relative_to(SOURCE)))
            scene_path.write_text(json.dumps(scene, indent=2) + '\n')
            changed.append(str(scene_path))
            continue
        rows = []
        actor_files = []
        for path in scene_path.parent.glob('actors/*.gbsres'):
            row = json.loads(path.read_text())
            key = 'companion' if path.stem == 'moth' else path.stem
            row['key'] = key
            if row['spriteSheetId'] in replacements:
                row['spriteSheetId'] = replacements[row['spriteSheetId']]
            if key == 'companion':
                row['animate'] = True
                row['collisionGroup'] = ''
                row['startScript'] = [h.e('EVENT_ACTOR_COLLISIONS_DISABLE', {'actorId': row['id']})]
                row['updateScript'] = follower_update(h, code, row)
                scope_events(row['startScript'], str(path.relative_to(SOURCE)), 'startScript')
                scope_events(row['updateScript'], str(path.relative_to(SOURCE)), 'updateScript')
            elif code == 'R01' and key in ['marty', 'roam_at_porch']:
                guide = 'Marty' if key == 'marty' else 'Roam'
                row['script'] = [h.cond('P12', 1,
                    [h.text(guide + ': Breakfast is ready. Your friends have places at the table.')],
                    [h.cond('P02', 1,
                        [h.text(guide + ': The porch light is steady. Follow the creek when you are ready.', 'We can always rest, swap companions, and save here.')],
                        [h.text(guide + ': I will keep this porch signal lit.', 'Ask June in the store. Then check the orchard lantern.')])])] + h.camp(code, 0) + h.release()
                scope_events(row['script'], str(path.relative_to(SOURCE)))
            else:
                # Preserve original puzzle IDs/conditions and unknown fields;
                # only obsolete opening-only text and effects gates change.
                def touch(events):
                    for event in events:
                        if event['command'] == 'EVENT_TEXT':
                            raw = event['args']['text']
                            joined = ' '.join((' '.join(raw) if isinstance(raw, list) else raw).split())
                            if 'CREEK ROUTE FOLLOWS IN THE FULL GAME' in joined:
                                event['args']['text'] = h.text('The boundary is open. Creek camp lies beyond the gate.')['args']['text']
                            elif 'GO HOME TO MARTY. SAVE AT THE PORCH.' in joined:
                                event['args']['text'] = h.text('Light 1 is lit. Save at a safe camp, then follow the creek.')['args']['text']
                        for branch in event.get('children', {}).values():
                            touch(branch)
                    for index, event in enumerate(list(events)):
                        if event['command'] == 'EVENT_SOUND_PLAY_EFFECT':
                            wrapper = h.cond('EFFECTS_OFF', 0, [event])
                            wrapper['id'] = uid('native-effect-gate/' + str(path.relative_to(SOURCE)) + '/' + event['id'])
                            events[index] = wrapper
                touch(row.get('script', []))
            if row.get('collisionGroup') == 'none':
                row['collisionGroup'] = ''
            rows.append(row)
            actor_files.append((path, row))
        # Retain the original one-shot introduction, wind reset and solved
        # boundary reconstruction. Old opening-only save/input branches go.
        retained = []
        for event in scene['script']:
            if event['command'] == 'EVENT_IF':
                c = event.get('args', {}).get('condition', {})
                variable = c.get('valueA', {}).get('value')
                if (code == 'R01' and variable == h.V['INTRO_SEEN']) or \
                   (code == 'R05' and variable == h.V['P01']) or \
                   (code == 'R06' and variable == h.V['P02']):
                    retained.append(event)
        scene['script'] = common_init(h, code, rows, []) + retained + h.release()
        scene['spritePaletteIds'] = [PALETTES['roam'], PALETTES[1], PALETTES['marty'], PALETTES['roam'],
                                     PALETTES[2], PALETTES[3], PALETTES['water'], PALETTES['wood']]
        scope_events(scene['script'], str(scene_path.relative_to(SOURCE)))
        scene_path.write_text(json.dumps(scene, indent=2) + '\n')
        changed.append(str(scene_path))
        for path, row in actor_files:
            row.pop('key', None)
            path.write_text(json.dumps(row, indent=2) + '\n')
            changed.append(str(path))
    bank_actor_resources(h)
    scripts = flush_banked(h)
    repair_native_visibility()
    return {'changedResources': len(changed), 'variableCount': len(h.V), 'saveEpoch': 2,
            'bankedScriptsWritten': scripts, 'nativeBuildRun': False}
