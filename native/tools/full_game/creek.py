"""PocketHoller R07–R12. Staged proposal; never edits native resources.

The parent owns IDs, shared controls, camps, collision and route transitions.
Transient arrangements reset on entry; solved routes retain permanent flags.
"""


def build(h):
    def actor(key, x, y, sprite, script, **properties):
        out = {'key': key, 'x': x, 'y': y, 'sprite': sprite, 'script': script}
        if properties:
            out['properties'] = properties
        return out

    def target(key, x, y, action, wrong='Wave mark: Turtle can Steady this. Choose Turtle at camp.'):
        return {'key': key, 'x': x, 'y': y, 'companion': 2,
                'action': action, 'wrong': wrong}

    def position(code, key, x, y):
        return h.e('EVENT_ACTOR_SET_POSITION', {
            'actorId': h.actor_id(code, key), 'x': h.num(x),
            'y': h.num(y), 'units': 'tiles'})

    def require(flag, action, clue):
        return h.cond(flag, 1, action, [h.text(clue)])

    rooms = {}
    rooms['R07'] = {
        'actors': [
            {'key': 'camp', 'x': 8, 'y': 8, 'sprite': 'sign', 'camp': True, 'script': []},
            actor('creek_map', 4, 6, 'sign', [h.cond('P06', 1,
                [h.text('Creek light: lit. The ridge path is open.', 'The loop from the light returns here. Save before the ridge.')],
                [h.cond('P03', 1,
                    [h.text('Turtle steadies wave marks. Three stones lead to the wheelhouse.', 'Next: near, middle, far. Stay on the dry walkway.')],
                    [h.text('The reed gates follow the leaves: upstream, then downstream.', 'The pool bank is safe. Check a reflection against living light.')])])]),
            actor('camp_lantern', 14, 6, 'lantern', [h.text('A warm camp light. Friends rest here. Nothing follows you into camp.')]),
        ], 'abilityTargets': [], 'onEnter': []}

    # H1 starts only through an ordinary A inspection at the accessible bank.
    # Its flag is committed before text. Both paths keep the necessary clue.
    reflection = [h.setv('H1', 1), h.show('R08', 'wrong_reflection'),
                  h.cond('REDUCED_SCARES', 1,
                    [h.text('A still reflection faces the wrong path.', 'The living companion points along the dry bank. Trust the living one.')],
                    [h.text('You turn from the pool. The reflected shape seems to stay behind.', 'It points into water. Your living companion stays on the dry path.')])]
    rooms['R08'] = {
        'actors': [
            actor('pool_bank', 6, 6, 'sign', [require('P02', [h.cond('H1', 0, reflection,
                [h.show('R08', 'wrong_reflection'), h.text('A borrowed shape in the pool. Living glow tells the true path.')])],
                'The boundary light must be repaired before the creek walk.')]),
            actor('wrong_reflection', 13, 5, 'reflection', [], collisionGroup='none'),
            actor('safe_bank', 12, 10, 'sign', [h.text('Dry bank: continue to the reeds. Water is not a path.', 'If anything feels strange, Return to Camp is always available.')]),
        ], 'abilityTargets': [], 'onEnter': [h.hide('R08', 'wrong_reflection')]}

    # P03: upstream followed by downstream. Wrong order resets only reed state.
    def reed_reset():
        return [h.setv('REED_STAGE', 0), h.show('R09', 'upstream_gate'),
                h.show('R09', 'downstream_gate')]
    recruit = [h.setv('P03', 1), h.setv('REED_STAGE', 2),
               h.setv('RECRUITED_TURTLE', 1), h.setv('ACTIVE_COMPANION', 2),
               h.hide('R09', 'upstream_gate'), h.hide('R09', 'downstream_gate'),
               h.show('R09', 'turtle'), h.sound(),
               h.text('The reeds part. MossbackTurtle lifts a mossy head.',
                      'Turtle joins you. It reads the current and steadies wave marks.',
                      'Try B at the practice wave. Then follow the causeway.')]
    rooms['R09'] = {
        'actors': [
            actor('flow_clue', 8, 4, 'sign', [h.text('Leaves move from the high bank to the low bank.', 'Open UPSTREAM first. Then open DOWNSTREAM. A works each reed gate.')]),
            actor('upstream_gate', 4, 6, 'windscreen', [h.cond('P03', 1,
                [h.text('Both reed gates are open. Turtle travels with you.')],
                [require('P02', [h.cond('REED_STAGE', 0,
                    [h.setv('REED_STAGE', 1), h.hide('R09', 'upstream_gate'), h.sound(),
                     h.text('Upstream opens. The leaves now reach the lower gate.')],
                    [h.text('Upstream is open. Downstream is next.')])], 'Repair the boundary light first.')])]),
            actor('downstream_gate', 12, 6, 'windscreen', [h.cond('P03', 1,
                [h.text('The reed passage stays clear.')],
                [require('P02', [h.cond('REED_STAGE', 1, recruit,
                    reed_reset() + [h.text('The leaves catch in the reeds. Both gates close.', 'Try upstream, then downstream. Nothing else was lost.')])],
                    'Repair the boundary light first.')])]),
            actor('turtle', 8, 8, 'turtle', [h.text('Turtle: Slow water still has a direction.', 'The wave mark names a safe place to brace. I will never be left behind.')]),
            actor('practice_wave', 4, 12, 'wave', [h.text('Practice wave: face it and press B with Turtle.', 'Steady works only at safe marked stones.')]),
            actor('reed_reset', 12, 12, 'sign', [h.cond('P03', 1,
                [h.text('The passage is finished. It will not close again.')],
                reed_reset() + [h.text('Reed gates reset. Upstream, then downstream.')])]),
        ],
        'abilityTargets': [target('practice_wave', 4, 12, [require('P03',
            [h.sound(), h.text('Turtle braces the practice stone. The wave stays steady.', 'On the causeway: near, middle, far. Use B from the safe bank.')],
            'Meet Turtle by opening the two reed gates first.')])],
        'onEnter': [h.cond('P03', 1,
            [h.setv('REED_STAGE', 2), h.hide('R09', 'upstream_gate'),
             h.hide('R09', 'downstream_gate'), h.show('R09', 'turtle')],
            reed_reset() + [h.hide('R09', 'turtle')])],
    }

    # P04: the walkway approaches all three stones without entering water.
    stations = [('near_wave', 4, 6), ('middle_wave', 8, 6), ('far_wave', 12, 6)]
    def stone_reset():
        return [h.setv('STONE_STAGE', 0)] + [h.show('R10', key) for key, _, _ in stations]
    stone_actions = []
    for stage, (key, x, y) in enumerate(stations):
        correct = [h.setv('STONE_STAGE', stage + 1), h.hide('R10', key), h.sound()]
        if stage == 2:
            correct += [h.setv('P04', 1), h.text('All three stones settle. The causeway is open.', 'Turtle comes with you. Any companion can cross the finished path.')]
        else:
            correct += [h.text(('Near stone steady. Middle is next.', 'Middle stone steady. Far is next.')[stage])]
        stone_actions.append(target(key, x, y, [h.cond('P04', 1,
            [h.text('The causeway is finished. Its stones stay steady.')],
            [require('P03', [h.cond('STONE_STAGE', stage, correct,
                stone_reset() + [h.text('The current pulls the stones loose. Try near, middle, far.', 'You remain on the safe bank. Turtle stays beside you.')])],
                'Open the reed passage and recruit Turtle first.')])]))
    rooms['R10'] = {
        'actors': [actor(key, x, y, 'wave', [h.cond('P04', 1,
            [h.text('The crossing stays steady.')],
            [h.text(label + ' station. Use B with Turtle from the dry walkway.')])])
            for (key, x, y), label in zip(stations, ['Near', 'Middle', 'Far'])] + [
                actor('causeway_order', 6, 11, 'sign', [h.text('Three safe stations, left to right: NEAR, MIDDLE, FAR.', 'Face each wave mark. B with Turtle. Stay on the dry bank.')]),
                actor('causeway_reset', 13, 11, 'sign', [h.cond('P04', 1,
                    [h.text('All stones are fixed. No reset is needed.')],
                    stone_reset() + [h.text('Unfinished stones reset. Near, middle, far.')])]),
            ], 'abilityTargets': stone_actions,
        'onEnter': [h.cond('P04', 1,
            [h.setv('STONE_STAGE', 3)] + [h.hide('R10', key) for key, _, _ in stations],
            stone_reset())],
    }

    # P05: movable switch actors make each open/closed state visible with
    # existing one-frame assets. They remain interactive at either position.
    controls = [('inlet', 'INLET', 4), ('bypass', 'BYPASS', 8), ('outlet', 'OUTLET', 12)]
    def wheel_reset():
        return [h.setv(variable, 0) for _, variable, _ in controls] + [
            position('R11', key, x, 6) for key, _, x in controls] + [h.show('R11', 'wheel_brace')]
    def wheel_complete_visual():
        return [h.setv('INLET', 1), h.setv('BYPASS', 0), h.setv('OUTLET', 1),
                position('R11', 'inlet', 4, 7), position('R11', 'bypass', 8, 6),
                position('R11', 'outlet', 12, 7), h.hide('R11', 'wheel_brace')]
    wheel_success = [h.setv('P05', 1)] + wheel_complete_visual() + [h.sound(),
        h.text('Turtle braces the wheel. Water follows the diagram.',
               'The wheel turns. The creek light route stays open.')]
    def failed():
        return [h.text('The wheel cannot turn with this flow.', 'Set inlet OPEN, bypass CLOSED, outlet OPEN. Then B at the brace.')]
    wheel_attempt = [h.cond('P05', 1, [h.text('The wheel is running. The light route remains open.')],
        [require('P04', [h.cond('INLET', 1,
            [h.cond('BYPASS', 0, [h.cond('OUTLET', 1, wheel_success, failed())], failed())], failed())],
            'Steady the causeway stones before starting the wheel.')])]
    rooms['R11'] = {
        'actors': [actor(key, x, 6, 'windscreen', [h.cond('P05', 1,
            [h.text(key + ': fixed in the working flow. The wheel keeps turning.')],
            [require('P04', [h.cond(variable, 0,
                [h.setv(variable, 1), position('R11', key, x, 7), h.text(key + ': OPEN. The switch moves down.')],
                [h.setv(variable, 0), position('R11', key, x, 6), h.text(key + ': CLOSED. The switch moves up.')])],
                'Cross the finished causeway before adjusting the wheel.')])])
            for key, variable, x in controls] + [
                actor('flow_diagram', 15, 3, 'sign', [h.cond('P05', 1,
                    [h.text('The wheel runs steadily. Light route: open.')],
                    [h.text('Flow diagram: INLET open, BYPASS closed, OUTLET open.', 'Switch down = open. Switch up = closed.', 'A changes each switch. Then Turtle uses B at the wave brace.')])]),
                actor('wheel_brace', 5, 12, 'wave', [h.cond('P05', 1,
                    [h.text('The brace is fixed. Turtle remains free to travel.')],
                    [h.text('Wheel brace. Match the flow diagram, then use B with Turtle.')])]),
                actor('wheel_reset', 13, 12, 'sign', [h.cond('P05', 1,
                    [h.text('The working flow is permanent. It will not reset.')],
                    wheel_reset() + [h.text('All three switches closed. Try the flow diagram again.')])]),
            ], 'abilityTargets': [target('wheel_brace', 5, 12, wheel_attempt)],
        'onEnter': [h.cond('P05', 1, wheel_complete_visual(), wheel_reset())],
    }

    # P06: B steadies the spillway; A turns the physically powered crank.
    def light_complete_visual():
        return [h.hide('R12', 'spillway_wave'), h.show('R12', 'creek_lamp')]
    steady_spillway = [h.cond('P06', 1, [h.text('The spillway and creek light stay steady.')],
        [require('P05', [h.cond('SPILLWAY_READY', 1,
            [h.text('The spillway is braced. Use A at the light crank.')],
            [h.setv('SPILLWAY_READY', 1), h.hide('R12', 'spillway_wave'), h.sound(),
             h.text('Turtle steadies the spillway. The crank catches the water power.', 'Use A at the light crank. Turtle can travel with you.')])],
            'Start the wheelhouse with the right flow first.')])]
    light_success = [h.setv('P06', 1), h.setv('SPILLWAY_READY', 1),
                     h.setv('CHAPTER', 2), h.setv('PHASE', 2)] + light_complete_visual() + [h.sound(),
        h.text('The second warning light shines over the creek. Night settles.',
               'The ridge gate opens. A short path returns to the creek camp.',
               'This is not a disk save. Save at camp before the ridge.')]
    rooms['R12'] = {
        'actors': [
            actor('spillway_wave', 5, 7, 'wave', [h.cond('P06', 1,
                [h.text('The spillway stays steady.')],
                [h.text('Steady the spillway with B and Turtle. Then A at the crank.')])]),
            actor('light_crank', 12, 7, 'vane', [h.cond('P06', 1,
                [h.text('Creek light: lit. Ridge gate and camp shortcut: open.')],
                [require('P05', [h.cond('SPILLWAY_READY', 1, light_success,
                    [h.text('The crank slips. Turtle must Steady the spillway first.', 'Use B at its wave mark, then return to this crank.')])],
                    'The wheelhouse must run before the light can turn.')])]),
            actor('creek_lamp', 12, 4, 'lantern', [h.text('The creek lamp shines with a real, steady light.')], collisionGroup='none'),
            actor('ridge_notice', 6, 12, 'sign', [h.cond('P06', 1,
                [h.text('Ridge path: open. The roost light is next.', 'Return to the creek camp to save and choose your companion.')],
                [h.text('Ridge gate waits for the creek light. The route back stays clear.')])]),
        ], 'abilityTargets': [target('spillway_wave', 5, 7, steady_spillway)],
        'onEnter': [h.cond('P06', 1,
            [h.setv('SPILLWAY_READY', 1)] + light_complete_visual(),
            [h.setv('SPILLWAY_READY', 0), h.show('R12', 'spillway_wave'), h.hide('R12', 'creek_lamp')])],
    }
    return rooms
