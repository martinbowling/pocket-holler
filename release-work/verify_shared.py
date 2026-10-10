"""Shared-helper source-model checks. This never runs a native ROM.

Run with PYTHONDONTWRITEBYTECODE=1. The report goes to stdout only; there are
no save fixtures, native edits, generated receipts or build operations here.
Controller routing, text-speed application and durable saves require runtime
integration and tests on a matching compiled cartridge.
"""
import itertools
import json
from full_game_support import Helpers
from verify_proposals import Model


class ObservedModel(Model):
    """Record branches actually reached by the existing logical event model."""
    def __init__(self, h):
        super().__init__(h)
        self.menus = []
        self.texts = []
        self.effects = []

    def _run(self, script):
        for event in script:
            command, args = event['command'], event.get('args', {})
            if command == 'EVENT_MENU':
                self.menus.append([args['option' + str(i)] for i in range(1, args['items'] + 1)])
            elif command == 'EVENT_TEXT':
                pages = args['text']
                self.texts.extend([pages] if isinstance(pages, str) else pages)
            elif command == 'EVENT_SOUND_PLAY_EFFECT':
                self.effects.append(args)
            super()._run([event])


def descendants(script):
    for event in script:
        yield event
        for branch in event.get('children', {}).values():
            yield from descendants(branch)


def verify():
    h = Helpers()
    failures = []
    checks = 0

    def check(condition, label):
        nonlocal checks
        checks += 1
        if not condition:
            failures.append(label)

    # Reaching a sound event means its source gate permits the effect. The
    # host model neither plays audio nor measures audibility.
    m = ObservedModel(h)
    m.run(h.settings(), [6])
    check([m.get(x) for x in ['MUSIC_OFF', 'EFFECTS_OFF', 'AUDIO_OFF']] == [1, 1, 1],
          'Quiet preset must disable both audio groups')
    m.run([h.sound()])
    check(not m.effects, 'Quiet preset must block the effect source branch')
    m.run(h.settings(), [2])
    check([m.get(x) for x in ['MUSIC_OFF', 'EFFECTS_OFF', 'AUDIO_OFF']] == [1, 0, 0],
          'Effects-on after Quiet must leave music off and clear legacy mute')
    m.run([h.sound()])
    check(len(m.effects) == 1, 'Effects-on after Quiet must reach the sound event branch')
    m.run(h.settings(), [6])
    m.run(h.settings(), [1])
    check([m.get(x) for x in ['MUSIC_OFF', 'EFFECTS_OFF', 'AUDIO_OFF']] == [0, 1, 0],
          'Music-on after Quiet must leave effects off')
    before = len(m.effects)
    m.run([h.sound()])
    check(len(m.effects) == before, 'Music-on alone must not permit effects')

    recruitment = ['RECRUITED_MOTH', 'RECRUITED_TURTLE', 'RECRUITED_THUNDERBIRD']
    names = ['MOTH', 'TURTLE', 'THUNDERBIRD']
    menu_cases = 0
    malformed_menu_cases = []
    # All eight flag combinations deliberately include malformed saved states;
    # a shown companion must always be owned, even before load repair.
    for bits in itertools.product([0, 1], repeat=3):
        q = ObservedModel(h)
        for flag, value in zip(recruitment, bits):
            q.put(flag, value)
        q.run(h.companion_menu())
        expected = [name for name, owned in zip(names, bits) if owned]
        shown = [name for name in (q.menus[0] if q.menus else []) if name in names]
        check(shown == expected, 'Recruited-only menu flags ' + str(bits))
        if shown != expected:
            malformed_menu_cases.append({'flags': list(bits), 'expected': expected, 'shown': shown})
        if q.menus:
            options = q.menus[0]
            for name in shown:
                selected = ObservedModel(h)
                for flag, value in zip(recruitment, bits):
                    selected.put(flag, value)
                selected.run(h.companion_menu(), [options.index(name) + 1])
                active = selected.get('ACTIVE_COMPANION')
                check(active in [1, 2, 3] and selected.get(recruitment[active - 1]) == 1,
                      'Selected companion must be owned for flags ' + str(bits) + ', ' + name)
            q.put('ACTIVE_COMPANION', next((i + 1 for i, owned in enumerate(bits) if owned), 0))
            previous = q.get('ACTIVE_COMPANION')
            q.run(h.companion_menu(), [0])
            check(q.get('ACTIVE_COMPANION') == previous, 'B-cancel preserves active companion ' + str(bits))
            q.run(h.companion_menu(), [options.index('TRAVEL ALONE') + 1])
            check(q.get('ACTIVE_COMPANION') == 0, 'Travel alone clears active companion ' + str(bits))
        menu_cases += 1

    # Companion descriptions remain in the reached journal text after recruit.
    for count in range(4):
        q = ObservedModel(h)
        for flag in recruitment[:count]:
            q.put(flag, 1)
        q.run(h.journal())
        text = ' '.join(' '.join(page.split()) for page in q.texts)
        for i, name in enumerate(names):
            check((name + ':') in text if i < count else (name + ':') not in text,
                  'Journal recruited companion description ' + name + ', count=' + str(count))
        check(all('LIGHT ' + str(i) + ':' in text for i in range(1, 4)),
              'Journal shows all three light states, count=' + str(count))

    save_script = h.save('R07', 1)
    save_event = next(e for e in descendants(save_script) if e['command'] == 'EVENT_SAVE_DATA')
    load = save_event['children']['load']
    milestone_cases = []
    for milestone, last, chapter, phase in [
        ('P02', 2, 1, 1), ('P03', 3, 1, 1), ('P06', 6, 2, 2),
        ('P07', 7, 2, 2), ('P08', 8, 3, 2), ('P12', 12, 4, 3)
    ]:
        q = ObservedModel(h)
        q.put(milestone, 1)
        q.put('ACTIVE_COMPANION', 99)
        q.put('CAMP_ID', 1)
        q.put('REED_STAGE', 1)
        q.put('INLET', 1)
        q.run(load)
        check(all(q.get('P' + str(i).zfill(2)) == 1 for i in range(1, last + 1)),
              milestone + ' load repairs all prerequisite puzzle flags')
        expected_count = 3 if last >= 7 else 2 if last >= 3 else 1
        check(all(q.get(flag) == 1 for flag in recruitment[:expected_count]),
              milestone + ' load repairs recruited companion flags')
        check(q.get('ACTIVE_COMPANION') == 1, milestone + ' load clamps invalid companion to recruited Moth')
        check((q.get('CHAPTER'), q.get('PHASE')) == (chapter, phase),
              milestone + ' load derives chapter and phase')
        check(q.get('REED_STAGE') == 0 and q.get('INLET') == 0,
              milestone + ' load clears unfinished local state')
        expected_room = 'R01' if milestone == 'P12' else 'R07'
        check(q.destination == h.scenes[expected_room], milestone + ' load restores expected safe camp')
        milestone_cases.append(milestone)

    # Selected but unowned companion, no recruited creature, and out-of-range
    # values must all recover safely. Signed negative values are included.
    clamp_cases = 0
    for moth in [0, 1]:
        for active in [-1, 0, 1, 2, 3, 4, 99]:
            q = ObservedModel(h)
            q.put('RECRUITED_MOTH', moth)
            q.put('ACTIVE_COMPANION', active)
            q.run(load)
            result = q.get('ACTIVE_COMPANION')
            valid = result == 0 or (1 <= result <= 3 and q.get(recruitment[result - 1]) == 1)
            check(valid, 'Load clamp active=' + str(active) + ', recruited Moth=' + str(moth))
            clamp_cases += 1

    destination_cases = 0
    for camp_id, room in [(0, 'R01'), (1, 'R07'), (2, 'R13'), (3, 'R19'), (99, 'R01')]:
        for dawn in [0, 1]:
            for ending_seen in [0, 1]:
                q = ObservedModel(h)
                q.put('CAMP_ID', camp_id)
                q.put('P12', dawn)
                q.put('ENDING_SEEN', ending_seen)
                q.run(h.return_camp())
                expected = 'R01' if dawn else room
                check(q.destination == h.scenes[expected],
                      'Safe camp destination id=' + str(camp_id) + ', dawn=' + str(dawn))
                destination_cases += 1

    q = ObservedModel(h)
    q.put('CHAPTER', 2)
    q.run(save_script, [1])
    check(q.get('SAVE_SCHEMA') == 1 and q.get('BUILD_SAVE_EPOCH') == 2,
          'Planned save writes schema 1 and epoch 2')
    check(q.get('CAMP_ID') == 1 and q.get('LAST_CHECKPOINT') == 2,
          'Save records selected camp and current chapter checkpoint')
    cancelled = ObservedModel(h)
    cancelled.put('BUILD_SAVE_EPOCH', 1)
    cancelled.run(save_script, [2])
    check(cancelled.get('BUILD_SAVE_EPOCH') == 1,
          'Cancel does not overwrite planned save compatibility fields')

    return {
        'passed': not failures, 'checks': checks, 'failures': failures,
        'audioSourceGatesChecked': True, 'companionRecruitmentStatesChecked': menu_cases,
        'malformedCompanionMenuStates': malformed_menu_cases,
        'loadMilestonesChecked': milestone_cases, 'activeCompanionClampCases': clamp_cases,
        'safeCampDestinationCases': destination_cases,
        'plannedSaveSchema': 1, 'plannedSaveEpoch': 2,
        'scope': 'Host-side source model only. No native ROM was run.',
        'compiledRom': False, 'emulatorTested': False, 'nativeSaveDurabilityTested': False,
        'unresolvedIntegrationTasks': [
            'Implement and verify actual A/B routing for SWAP_BUTTONS.',
            'Apply and verify Normal/Fast/Instant native text speeds immediately and on entry/load.',
            'Run native camp/save/load/input/audio regressions against the compiled ROM.'
        ]
    }


if __name__ == '__main__':
    report = verify()
    print(json.dumps(report, indent=2))
    raise SystemExit(0 if report['passed'] else 1)
