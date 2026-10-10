# Save policy

The full game uses one native slot, schema **1**, build epoch **2**. Safe camps
are R01 porch, R07 creek, R13 ridge and R19 root threshold. Save requires the
visible Save/Cancel choice and places the player at a clear camp checkpoint
before snapshotting. A chapter checkpoint offers Save; cancellation never
silently commits progress.

Confirmed saves retain completed puzzles P01–P12, companion recruitment and
selection, repaired lights represented by their puzzle flags, phase, chapter,
visited shortcut, six optional journal flags, ending state, selected player
and comfort/control options. `PLAYER_CHARACTER` ID 52 uses 0=Roam and 1=Marty.
Scene initialization restores the chosen sprite and native object palette;
invalid character values fall back to Roam. Companion selection accepts only
recruited companions, with a safe recruited-Moth or travel-alone fallback.

Continue checks slot existence and peeks schema/epoch before loading. The engine
also binds saves to its compiled project-data signature. Opening epoch-1 saves
are not promised to migrate into the full game. An incompatible slot remains
untouched; starting a fresh session replaces it only at a later explicit Save.
Fixtures therefore need the exact matching ROM hash, not just the same title.

Load recovery derives permanent progression from completed milestones, restores
the appropriate chapter and DAY/DUSK/NIGHT/DAWN phase, and reconstructs earlier
required puzzles and recruited companions when a later milestone implies them.
Transient reed, stone, water-control, vane, relay, plaque, channel and lamp
arrangements reset; completed room layouts reconstruct their solved appearance
from permanent flags. Optional journal pages are never required by that repair.

Return to Camp keeps session progression, sends the player to the latest visited
safe camp, and allows unfinished local arrangements to reset. It is **not a disk
save**. At dawn it returns to R01 so the reunion cannot be skipped. P12 begins
dawn; `ENDING_SEEN` is set by the porch reunion and credits. A confirmed dawn save
continues at the peaceful porch, with optional pages still available.

New Game asks before beginning when a slot exists, resets quest state and player
selection to Roam, retains the comfort/control preferences, and leaves the old
slot intact until confirmed Save. Quit asks before discarding unsaved session
progress. Character switching at camp shares all progression; it is not a second
save slot.

The final [full-game emulator regression](../evidence/full-route-g4s6xp4r/report.json)
passes on SHA256
`de3ed696c6a80b5007ccc825693fabb781a661d30814fa6694864c467453b5d2`.
It uses 15 fresh emulator boots and ordinary camp saves/Continue, checks recovered
quest state, player/companion choices and settings, and verifies dawn recovery.
No progression memory writes or initial save fixture injection are used. Its
file-backed emulator results do not establish browser or physical-cartridge
persistence. Cross-build migration and incompatible-slot recovery require their
own exact evidence. Prior opening-ROM tests cover only their bound opening
cartridge. See [qa-report.md](qa-report.md) for the release evidence.

Use a copied ROM and private RAM file for file-backed emulator tests. The plugin
stepped emulator's in-memory session, the browser emulator's storage, and a
physical cartridge have separate persistence behavior and require separate
evidence. Never substitute a QA fixture for a user's save.
