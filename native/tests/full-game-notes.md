# Full cartridge input regression

`full_game_driver.py` supplies bounded controller presses, neutral releases,
real window/cursor-based dialogue draining, menu selection, collision-aware
walking, source-trigger room navigation, actor approach, read-only quest values,
private camp saves and cold Continue. It verifies the ROM SHA against
`evidence/full-build.json` and requires matching debug ROM, symbols and globals
hashes before opening PyBoy. Memory writes, injected RAM fixtures and emulator
save-state loading are absent from the driver.

Companion choices resolve the native conditional menu's labels. Unrecruited
companions are absent, and their later addition does not change how the test
selects Travel alone or Leave.

`full_game.py` starts a clean cartridge, reaches all twelve puzzles and dawn
credits without collecting a journal page, saves and cold-loads at every camp,
walks as both protagonists, selects all companions and Travel alone, exercises
quiet/reduced-scare/instant-text/swapped-input settings, and checks wrong puzzle
actions, unfinished room resets, wrong companions, repeated solved actions and
both safe false routes. Six lamp orders are tested by normal cold Continue from
the genuinely saved pre-P11 camp, discarding unsaved attempts each time. Optional
pages and the porch interior are visited after the zero-journal ending, giving
24-room coverage without making collectibles a hidden progression dependency.

Each run copies only the matching ROM into a new evidence directory; PyBoy
writes a disposable RAM file there. Existing player RAM, old opening fixtures,
browser sessions and recordings are not read or changed. The run retains an
input/frame-hash journal, native PNG samples, private RAM checkpoints and a JSON
report containing the exact ROM hash, flags, visited rooms and any failure.

The driver assumes the inspected pinned GBVM actor layout and native cursor
tile. These are checked against the build's debug ABI but UI/navigation details
must be verified on the new cartridge. Source collision planning is a means of
choosing ordinary walking inputs, not a substitute for runtime collision proof.
The test must only run after the full build receipt and matching debug artifacts
exist. Initial authoring passed syntax checks. Runtime attempts are retained separately
and only a report with `passed: true` establishes route completion. Audio listening, first-time human pacing and physical hardware remain
separate tests even after this regression passes.

`full_playthrough.py` is a separate continuous capture route for a video: one
fresh boot, normal native audio, no cold loads or regression retries, all 24
rooms/twelve puzzles/six journal pages/four encounters through dawn reunion.
It retains the same ordinary-controller journal for the parent's full-frame
and native-APU encoder. Its source resolver follows banked custom event calls
for discovery without bypassing those calls in the actual cartridge.


## Runtime attempt on build3

The receipt-paired EA3390 cartridge booted cleanly with save epoch2, completed
P01/P02, switched Roam/Marty through real camp menus, applied quiet/reduced-scare/
instant-text settings and both input swap toggles, and saved/continued through
ordinary input. The complete route has not passed on this cartridge.

The first confirmed game defect is an invisible R06 gate after P02: both gate
actors have HIDDEN set while COLLISION remains set. A player at (8,3) cannot
move up despite P02=1/GATE_REVEALED=1. The native actor overlap routine checks
collision rather than visibility. Evidence is retained in
`evidence/gate-diagnostic-esk7ktbu` (input journal, native PNG and failed report).
The parent owns the resource repair and replacement build; this test agent has
not altered gameplay resources or used memory writes to bypass the gate.

Driver discoveries now reflected in its inputs: two-frame direction taps,
actual runtime actor bounds (including one tile above sprite origin), neutral
frames between dialogue and asynchronously drawn menus, and destination
on-enter completion after exit fades. Menu selection reads the visible native
cursor. The regression additionally walks all 49 native triggers and four manifest actor portals (53 connections)
after the earned reunion and asserts that permanent progression remains intact.
These expanded contracts subsequently passed on build4, as recorded below.


## Passed on build4

ROM SHA256: `de3ed696c6a80b5007ccc825693fabb781a661d30814fa6694864c467453b5d2`.
Receipt and debug artifact hashes were checked before each clean private boot.

- `evidence/full-route-g4s6xp4r/report.json`: passed; 175,653 ordinary input
  frames, 15 boots, 126 quest assertions, all 24 rooms, all 49 native triggers and
  four actor portals (53 directed connections). Twelve puzzles and reunion
  completed with all journals zero, followed by all six optional pages. Four
  camp cold-load locations, recruited companion menus, both protagonists,
  physical swapped actions, quiet/reduced scares, wrong orders/companions,
  unfinished resets, solved repeat guards, safe false routes, six lamp orders,
  final Not yet/B-cancel and dawn-before-reunion all passed.
- `evidence/full-playthrough-6ix0srxg/report.json`: passed; 107,468 frames in
  one uninterrupted clean boot, all 24 rooms/twelve puzzles/six pages/four
  encounters through the reunion. Native sound was emulated, with all three
  silence flags and Reduced Scares remaining zero. `events.jsonl` provides the
  complete ordinary-controller sequence and native frame hashes for the video
  encoder. PNG samples are 160×144. The input route is complete; video encoding
  is a separate artifact produced by the parent.

All progression and private SRAM saves arose from real controller actions.
No memory writes, initial save fixture, save-state injection, or teleport was
used. Passed reports do not claim physical hardware, listening QA or first-time
human pacing. The earlier build3 gate failure remains retained as a regression
history rather than being erased after repair.
