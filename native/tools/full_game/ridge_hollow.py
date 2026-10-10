"""Staged native authoring for PocketHoller ridge, hollow and dawn rooms.

Pure resource descriptions: build(h) does not select, read, write or compile a
native project. The integrator supplies stable event/actor IDs and common UI.
"""


def build(h):
    rooms = {f"R{i:02}": {"actors": [], "abilityTargets": [], "onEnter": []}
             for i in range(13, 24)}

    def actor(code, key, x, y, sprite, script, **properties):
        item = {"key": key, "x": x, "y": y, "sprite": sprite, "script": script}
        if properties:
            item["properties"] = properties
        rooms[code]["actors"].append(item)

    def target(code, key, x, y, companion, action, wrong):
        rooms[code]["abilityTargets"].append({"key": key, "x": x, "y": y,
            "companion": companion, "action": action, "wrong": wrong})

    def require(flags, action, failure):
        body = action
        for flag in reversed(flags):
            body = [h.cond(flag, 1, body, [h.text(failure)])]
        return body

    def reset_unsolved(code, puzzle, *variables):
        rooms[code]["onEnter"].append(h.cond(puzzle, 0,
            [h.setv(variable, 0) for variable in variables]))

    def journal(code, key, x, y, sprite, flag, title, *pages):
        actor(code, key, x, y, sprite, [h.cond(flag, 0,
            [h.setv(flag, 1), h.sound(), h.text(title, *pages)],
            [h.text(title, *pages)])])

    def fresh_a(label):
        # A dialogue-closing hold must never count as the final decision.
        return [h.e("EVENT_DEFINE_LABEL", {"label": label}),
            h.e("EVENT_IF_INPUT", {"input": ["a"]}, true=[
                h.e("EVENT_WAIT", {"units": "frames", "frames": h.num(1)}),
                h.e("EVENT_GOTO_LABEL", {"label": label})], false=[])]

    def optional_sting():
        return h.cond("REDUCED_SCARES", 0, [h.sound("click")])

    # R13: the ridge save hub. The parent supplies its complete camp menu.
    rooms["R13"]["actors"].append({"key": "camp", "x": 8, "y": 8,
        "sprite": "sign", "camp": True, "script": []})
    actor("R13", "ridge_notice", 4, 6, "sign", [h.cond("P08", 1,
        [h.text("THREE LIGHTS LIT. THE BELL ROAD IS OPEN.",
                "THE RIDGE LOOP RETURNS HERE. REST AND SAVE WHEN YOU LIKE.")],
        [h.cond("P07", 1,
            [h.text("THUNDERBIRD SPARKS ZIGZAG SOCKETS.",
                    "THE RELAY BOARD SHOWS LEAF, WAVE, STAR.")],
            [h.text("FOLLOW THE BRAMBLE STAIRS TO THE ROOST.",
                    "FIXED FEATHER ARROWS POINT BOTH VANES TO THE PERCH.")])])])
    actor("R13", "safe_lantern", 14, 8, "lantern",
          [h.text("THE CAMP LANTERN IS REAL. YOUR COMPANIONS REST SAFELY HERE.")])

    # R14: bounded trail story and an inspectable visual footstep clue.
    journal("R14", "trail_sketch", 4, 6, "sign", "J3", "JOURNAL 3: TRAIL SKETCH.",
            "AN OLD SKETCH SHOWS A LOOP FROM THE RELAYS BACK TO CAMP.",
            "THE DRAWN PERCH HAS TWO FEATHERS POINTING INWARD.")
    actor("R14", "extra_footprint", 14, 8, "footprint", [h.cond("PHASE", 3,
        [h.text("ONLY YOUR OWN TRACKS NOW. THE MORNING TRAIL IS QUIET.")],
        [h.cond("H3", 0, [h.cond("P07", 0,
            [h.setv("H3", 1), optional_sting(),
             h.text("ONE MORE PRINT THAN STEPS. THE PATH AHEAD STAYS CLEAR.",
                    "THE CREATURE BESIDE YOU WATCHES THE REAL TRAIL.")],
            [h.text("AN OLD FOOTPRINT. THE TRAIL IS DRY AND CLEAR.")])],
            [h.text("THE EXTRA PRINT ENDS HERE. YOUR RETURN PATH IS CLEAR.")])])])

    # P07: ordinary A interactions shelter a creature, with no timing gate.
    reset_unsolved("R15", "P07", "VANEA", "VANEB")
    for key, x, variable, answer, side in [
            ("west_vane", 4, "VANEA", 2, "WEST"),
            ("east_vane", 14, "VANEB", 4, "EAST")]:
        actor("R15", key, x, 6, "vane", [h.cond("P07", 1,
            [h.text("THE SHELTER VANE STAYS FIXED TOWARD THE PERCH.")],
            [h.text(side + " SHELTER VANE. TURN ITS OPEN SIDE."),
             h.menu(["North", "East", "South", "West"], "SUBMENU"),
             *[h.cond("SUBMENU", i, [h.setv(variable, i),
                  h.text("OPEN SIDE: " + direction + ".")])
               for i, direction in enumerate(["NORTH", "EAST", "SOUTH", "WEST"], 1)]])])
    actor("R15", "feather_board", 4, 12, "sign",
          [h.text("WEST FEATHER: EAST. EAST FEATHER: WEST.",
                  "BOTH OPEN SIDES FACE THE CENTRAL PERCH.")])
    actor("R15", "central_perch", 9, 8, "thunderbird", [h.cond("P07", 1,
        [h.text("THE ROOST IS SHELTERED. THUNDERBIRD IS ALWAYS WELCOME.")],
        require(["P06"], [h.cond("VANEA", 2, [h.cond("VANEB", 4,
            [h.setv("P07", 1), h.setv("RECRUITED_THUNDERBIRD", 1),
             h.setv("ACTIVE_COMPANION", 3), h.hide("R15", "central_perch"),
             h.sound(), h.text("THE WIND PASSES AROUND THE SHELTER.",
                 "BABYTHUNDERBIRD JOINS YOU. B: SPARK ZIGZAG SOCKETS.",
                 "TRY THE PRACTICE SOCKET. THEN VISIT THE RELAY YARD.")],
            [h.text("THE EAST VANE STILL LETS WIND IN. READ ITS FEATHER ARROW.")])],
            [h.text("THE WEST VANE STILL LETS WIND IN. READ ITS FEATHER ARROW.")])],
            "REPAIR THE CREEK LIGHT BEFORE PREPARING THIS ROOST."))])
    rooms["R15"]["onEnter"].append(h.cond("P07", 1,
        [h.hide("R15", "central_perch")]))
    actor("R15", "practice_socket", 14, 12, "spark",
          [h.text("A SAFE CERAMIC SOCKET. THUNDERBIRD CAN SPARK IT WITH B.")])
    target("R15", "practice_socket", 14, 12, 3,
           [h.sound(), h.text("A TINY WARM SPARK. NO CHARGE OR FUEL NEEDED.")],
           "A ZIGZAG SOCKET. SELECT THUNDERBIRD AT CAMP.")

    # P08: the symbol board carries the only sequence rule, independent of hue.
    reset_unsolved("R16", "P08", "RELAY_STAGE")
    actor("R16", "relay_board", 4, 12, "sign",
          [h.text("RELAY ORDER: LEAF, WAVE, STAR.",
                  "SPARK EACH SAFE SOCKET WITH THUNDERBIRD. A WRONG STEP RESETS ONLY THIS TRY.")])
    for key, x, stage, name in [("leaf_relay", 4, 0, "LEAF"),
                               ("wave_relay", 9, 1, "WAVE"),
                               ("star_relay", 14, 2, "STAR")]:
        actor("R16", key, x, 6, "spark",
              [h.cond("P08", 1, [h.text(name + " RELAY: LIT.")],
                   [h.text(name + " RELAY. FACE THE SOCKET AND PRESS B.")])])
        success = ([h.setv("RELAY_STAGE", 3), h.setv("P08", 1),
                    h.setv("CHAPTER", 3), h.sound(),
                    h.text("ALL THREE RELAYS GLOW. LIGHT 3 IS LIT.",
                           "THE CAMP LOOP AND BELL ROAD ARE OPEN.",
                           "REST AND SAVE BEFORE THE HOLLOW. ALL THREE FRIENDS CAN HELP.")]
                   if stage == 2 else
                   [h.setv("RELAY_STAGE", stage + 1), h.sound(),
                    h.text(name + " RELAY CHARGED.")])
        target("R16", key, x, 6, 3, [h.cond("P08", 1,
            [h.text("THE RELAYS STAY LIT. NO NEED TO CHARGE THEM AGAIN.")],
            require(["P07"], [h.cond("RELAY_STAGE", stage, success,
                [h.setv("RELAY_STAGE", 0), h.sound("click"),
                 h.text("A SOFT CLICK. THIS TRY RESETS. LEAF, WAVE, STAR.")])],
                "SHELTER THUNDERBIRD AT THE ROOST FIRST."))],
            "THE ZIGZAG RELAY NEEDS THUNDERBIRD'S SPARK.")
    actor("R16", "ridge_light", 14, 12, "lantern", [h.cond("P08", 1,
        [h.text("THE RIDGE LIGHT SENDS A STEADY SIGNAL TO TOWN.")],
        [h.text("THE RIDGE LIGHT WAITS FOR THE THREE RELAYS.")])])

    # H2: never use Marty's trusted speaker label for a copied invitation.
    actor("R17", "changed_sign", 4, 6, "sign", [h.cond("PHASE", 3,
        [h.text("HOME. THE ROAD SIGN IS ORDINARY AGAIN.")],
        [h.cond("P08", 1, [h.cond("H2", 0,
            [h.setv("H2", 1), optional_sting(),
             h.text("HOME HAS BECOME STAY. THE PAINT LOOKS TOO NEW.",
                    "YOUR FRIEND FACES THE REAL ROAD. THE RETURN PATH IS STILL THERE.")],
            [h.text("STAY. ONLY THE WORD CHANGED. THE ROAD DID NOT.")])],
            [h.text("HOME. A WEATHERED SIGN POINTS BACK TO TOWN.")])])])
    journal("R17", "bell_rhyme", 14, 8, "sign", "J4", "JOURNAL 4: BELL RHYME.",
            "THREE LIGHTS ABOVE. A SPRING BELOW. RING FOR THE FOLKS WHO NEED TO GO.",
            "THE RHYME IS A TOWN SONG, WRITTEN IN A LAMPLIGHTER'S HAND.")

    # The mandatory explanation and route requirements are ordinary inspection.
    actor("R18", "old_notice", 4, 6, "sign", [h.text(
        "THE BELL USED TO CALL EVERYONE HOME. ITS SPRING STOPPED AFTER A STORM.",
        "THE HOLLOW KEPT THE VOICES THAT THE BELL COULD NO LONGER CARRY.",
        "IT MISTOOK KEEPING EVERYONE HERE FOR KEEPING THEM SAFE.",
        "IT CAN BORROW WORDS. IT CANNOT COPY A FRIEND'S LIVING GLOW.")])
    actor("R18", "all_lights_notice", 14, 12, "sign", [h.cond("P08", 1,
        [h.text("ALL THREE WARNING LIGHTS ARE LIT. THE ROOT THRESHOLD IS READY.",
                "MOTH READS THE BELL. TURTLE RESTORES THE SPRING. THUNDERBIRD CHARGES THE LAMPS.")],
        [h.text("THE ROOT PATH NEEDS ALL THREE WARNING LIGHTS. CHECK THE RIDGE RELAYS.")])])
    actor("R18", "hidden_notice", 14, 6, "ray", [h.cond("J5", 1,
        [h.text("THE CALLER GREW FROM VOICES CAUGHT AROUND THE QUIET BELL.")],
        [h.text("A RAY MARK ON AN OLD NOTICE. MOTH CAN REVEAL AN OPTIONAL JOURNAL PAGE.")])])
    target("R18", "hidden_notice", 14, 6, 1, [h.cond("J5", 0,
        [h.setv("J5", 1), h.sound(), h.text("JOURNAL 5: THE QUIET BELL.",
            "THE CALLER GREW AROUND THE VOICES CAUGHT HERE.",
            "A NOTE SAYS: DO NOT KEEP A VOICE. HELP IT FIND ITS WAY HOME.")],
        [h.text("THE QUIET BELL NOTE IS ALREADY IN YOUR JOURNAL.")])],
        "THE RAY MARK NEEDS MOTH'S REVEAL. THE MAIN NOTICE HAS THE STORY.")

    rooms["R19"]["actors"].append({"key": "camp", "x": 8, "y": 8,
        "sprite": "sign", "camp": True, "script": []})
    actor("R19", "hollow_map", 4, 6, "sign", [h.text(
        "THREE SHORT PATHS: ECHO HALL, SPRING CHAMBER, BELL CHAMBER.",
        "MOTH, THEN TURTLE, THEN THUNDERBIRD. CHANGE FRIENDS HERE AND SAVE.",
        "THE MARKED HOME SHORTCUT NOW OPENS BOTH WAYS.")])
    actor("R19", "safe_lantern", 14, 8, "lantern",
          [h.text("REAL WARM LIGHT. NO BORROWED VOICE ENTERS THIS CAMP.")])

    # P09: three visible marks, a reversible choice, and a safe false doorway.
    reset_unsolved("R20", "P09", "PLAQUE_A", "PLAQUE_B", "PLAQUE_C")
    def borrowed():
        return [h.cond("PHASE", 3, [], [h.cond("H4", 0,
            [h.setv("H4", 1), optional_sting(),
             h.text("A VOICE IN THE WOODS: COME STAY. THE LIGHT IS WAITING.",
                    "ONE WORD IS WRONG. MOTH'S LIVING GLOW STAYS TRUE.")])])]
    plaques = [
        ("plaque_a", 4, "PLAQUE_A", "KEEP EVERY VOICE HERE. NEVER LET THEM GO."),
        ("plaque_b", 9, "PLAQUE_B", "THE BELL CALLS PEOPLE HOME. RING FOR EVERYONE."),
        ("plaque_c", 14, "PLAQUE_C", "FOLLOW THE VOICE ALONE. STAY IN THE WOODS.")]
    for key, x, flag, wording in plaques:
        actor("R20", key, x, 6, "ray", [h.cond(flag, 1,
            [h.text(wording)], [h.text("A RAY PLAQUE. FACE IT AND USE MOTH'S REVEAL WITH B.")])])
        target("R20", key, x, 6, 1, [h.cond(flag, 1,
            [h.text(wording)], borrowed() + [h.setv(flag, 1), h.sound(), h.text(wording)])],
            "THIS RAY PLAQUE NEEDS MOTH'S REVEAL.")
    def false_return():
        return [h.text("MOTH TURNS BACK TO THE REAL CAMP. NOTHING YOU FINISHED IS LOST."),
                h.switch("R19", 8, 12, "up")]
    actor("R20", "bell_instruction", 9, 10, "bell", [h.cond("P09", 1,
        [h.text("THE TRUE BELL CALLS PEOPLE HOME. THE SPRING CAN BE RESTORED.")],
        require(["PLAQUE_A", "PLAQUE_B", "PLAQUE_C"], [
            h.text("WHICH INSCRIPTION MATCHES THE BELL'S PURPOSE?"),
            h.menu(["Call people home", "Keep them here", "Wait"], "SUBMENU"),
            h.cond("SUBMENU", 1, [h.setv("P09", 1), h.sound(),
                h.text("TRUE: THE BELL CALLS PEOPLE HOME.",
                       "TAKE TURTLE TO THE SPRING. THE CHANNEL DIAGRAM WILL HELP.")]),
            h.cond("SUBMENU", 2, false_return())],
            "REVEAL ALL THREE RAY PLAQUES BEFORE CHOOSING."))])
    actor("R20", "false_door", 14, 12, "reflection", [h.cond("PHASE", 3,
        [h.text("JUST AN EMPTY ALCOVE. THE MORNING WIND HAS PASSED THROUGH.")],
        [h.text("A PAINTED DOOR PROMISES AN EASY WAY HOME. YOUR FRIEND REFUSES IT."),
         h.menu(["Return to camp", "Stay here"], "SUBMENU"),
         h.cond("SUBMENU", 1, false_return())])])

    # P10: directions have permanent printed labels and no color-only solution.
    reset_unsolved("R21", "P10", "CHANNEL_A", "CHANNEL_B")
    actor("R21", "spring_diagram", 4, 12, "sign", [h.text(
        "WALL DIAGRAM: LEFT CHANNEL EAST. RIGHT CHANNEL WEST.",
        "BOTH LEAD TO THE BELL GLYPH. THEN TURTLE STEADIES THE SPRING STONE.")])
    for key, x, variable, label in [("left_channel", 4, "CHANNEL_A", "LEFT"),
                                    ("right_channel", 14, "CHANNEL_B", "RIGHT")]:
        actor("R21", key, x, 6, "vane", [h.cond("P10", 1,
            [h.text(label + " CHANNEL FLOWS TO THE BELL.")],
            require(["P09"], [h.text(label + " CHANNEL. SET THE FLOW."),
                h.menu(["North", "East", "South", "West"], "SUBMENU"),
                *[h.cond("SUBMENU", i, [h.setv(variable, i),
                    h.text("FLOW: " + direction + ".")])
                  for i, direction in enumerate(["NORTH", "EAST", "SOUTH", "WEST"], 1)]],
                "READ THE TRUE BELL INSCRIPTION IN THE ECHO HALL FIRST."))])
    actor("R21", "spring_stone", 9, 8, "wave", [h.cond("P10", 1,
        [h.text("THE SPRING RUNS STEADY. TURTLE TRAVELS WITH YOU.")],
        [h.text("WAVE STONE: SET BOTH CHANNELS. THEN USE TURTLE'S STEADY WITH B.")])])
    target("R21", "spring_stone", 9, 8, 2, [h.cond("P10", 1,
        [h.text("THE SPRING IS ALREADY RESTORED.")], require(["P09"],
        [h.cond("CHANNEL_A", 2, [h.cond("CHANNEL_B", 4,
            [h.setv("P10", 1), h.sound(), h.text("WATER REACHES THE BELL SPRING.",
                "TURTLE RETURNS TO YOUR SIDE. THUNDERBIRD CAN CHARGE THE THREE BELL LAMPS.")],
            [h.text("THE RIGHT CHANNEL DOES NOT REACH THE BELL. READ THE WALL DIAGRAM.")])],
            [h.text("THE LEFT CHANNEL DOES NOT REACH THE BELL. READ THE WALL DIAGRAM.")])],
        "REVEAL AND CHOOSE THE TRUE INSCRIPTION BEFORE RESTORING THE SPRING."))],
        "A WAVE STONE. TURTLE CAN STEADY IT AFTER THE CHANNELS ARE SET.")

    # P11: a finite bitset allows the three lamps to be charged in any order.
    reset_unsolved("R22", "P11", "BELL_LAMPS")
    actor("R22", "bell_notice", 4, 12, "sign", [h.text(
        "THREE CERAMIC LAMPS. SPARK EACH WITH THUNDERBIRD.",
        "ALL WARNING LIGHTS AND THE RESTORED SPRING MUST BE READY.",
        "BEFORE RINGING, YOU CAN RETURN TO CAMP, CHANGE SETTINGS AND SAVE.")])
    for key, x, bit, label in [("bell_lamp_a", 4, 1, "LEFT"),
                              ("bell_lamp_b", 9, 2, "MIDDLE"),
                              ("bell_lamp_c", 14, 4, "RIGHT")]:
        actor("R22", key, x, 6, "spark", [h.cond("P11", 1,
            [h.text(label + " BELL LAMP: CHARGED.")],
            [h.text(label + " CERAMIC LAMP. PRESS B WITH THUNDERBIRD.")])])
        def lamp_attempt(state=0):
            if state > 7:
                return [h.setv("BELL_LAMPS", 0), h.text("THE LAMPS RESET SAFELY. TRY EACH SOCKET AGAIN.")]
            if state & bit:
                response = [h.text(label + " LAMP IS ALREADY CHARGED.")]
            else:
                next_state = state | bit
                response = [h.setv("BELL_LAMPS", next_state), h.sound(),
                            h.text(label + " BELL LAMP CHARGED.")]
                if next_state == 7:
                    response += [h.setv("P11", 1),
                        h.text("ALL THREE BELL LAMPS GLOW. THE BELL IS READY.",
                               "CHANGE FRIENDS FREELY. INSPECT THE BELL WHEN YOU ARE READY.")]
            return [h.cond("BELL_LAMPS", state, response, lamp_attempt(state + 1))]
        target("R22", key, x, 6, 3, [h.cond("P11", 1,
            [h.text("ALL BELL LAMPS STAY CHARGED.")],
            require(["P02", "P06", "P08", "P09", "P10"], lamp_attempt(),
                    "THE THREE WARNING LIGHTS, TRUE INSCRIPTION AND SPRING MUST BE READY."))],
            "THE CERAMIC LAMP NEEDS THUNDERBIRD'S SPARK.")

    # P12 has two explicit choices separated by neutral input consumption.
    finale = [h.setv("P12", 1), h.setv("CHAPTER", 4), h.setv("PHASE", 3),
        h.sound(), h.text("THE BELL RINGS FOR EVERYONE. THE TOWN ANSWERS WITH ITS OWN LIGHT.",
            "THE BORROWED WORDS LOOSEN INTO HARMLESS ECHOES. ONLY WIND REMAINS.",
            "ALL THREE FRIENDS ARE SAFE. DAWN RETURNS TO POCKETHOLLER.",
            "GO HOME FOR BREAKFAST. YOUR FINISHED PUZZLES STAY FINISHED.",
            "THIS DOES NOT WRITE A SAVE. SAVE AT THE PORCH AFTER THE REUNION."),
        h.switch("R23", 8, 12, "up")]
    bell_ready = [h.text("THE TRUE BELL CALLS PEOPLE HOME. RING FOR EVERYONE?",
                        "YOU CAN WAIT, RETURN TO CAMP OR SAVE BEFORE DECIDING."),
        h.menu(["Ring for all", "Wait", "Leave"], "SUBMENU"),
        h.cond("SUBMENU", 1,
            [h.text("RING FOR EVERYONE. PRESS A ON RING NOW TO CONFIRM."),
             *fresh_a(h.actor_id("R22", "final-confirm-release")),
             h.menu(["Ring now", "Not yet"], "SUBMENU"),
             h.cond("SUBMENU", 1, finale,
                    [h.text("THE BELL WAITS. NO PROGRESS HAS CHANGED.")])],
            [h.text("THE BELL WAITS. YOU MAY SAVE OR CHANGE SETTINGS AT CAMP.")])]
    actor("R22", "hollow_bell", 9, 10, "bell", [h.cond("P12", 1,
        [h.text("THE BELL HAS CALLED EVERYONE HOME. THE HOLLOW IS QUIET.")],
        require(["P02", "P06", "P08", "P09", "P10", "P11"], bell_ready,
                "REVEAL THE TRUE WORDS, RESTORE THE SPRING AND CHARGE EVERY BELL LAMP FIRST."))])

    # Dawn is playable. Credits and ENDING_SEEN belong only to the home reunion.
    actor("R23", "dawn_notice", 4, 6, "sign", [h.text(
        "MORNING LIGHT RESTS ON THE ROOFS. EVERY HOME SIGNAL ANSWERED.",
        "FOLLOW THE PATH TO THE FESTIVAL GREEN, THEN HOME TO THE PORCH.",
        "YOUR FRIENDS ARE READY FOR BREAKFAST TOO.")])
    journal("R23", "dawn_drawing", 14, 8, "sign", "J6", "JOURNAL 6: DAWN DRAWING.",
            "THREE FRIENDS BESIDE A BRIGHT WINDOW. TWO PLACES AT THE BREAKFAST TABLE.",
            "UNDER THE DRAWING: EVERYONE GETS TO COME HOME.")
    return rooms
