# Comfort, controls and readability

The authored full game has no combat, health loss, countdown, random encounter,
forced reflex sequence, companion harm or companion ability fuel. Wrong puzzle
arrangements reset only their unfinished local state. Solved routes remain open
with any selected companion. Optional journal pages never gate the ending.

Mandatory clues have text or shapes as well as color: rays mean Moth's Reveal,
waves mean Turtle's Steady, and zigzags mean Thunderbird's Spark. Direction and
sequence clues use printed words. The three living companions remain trustworthy;
the Caller never imitates a save error, system menu or corrupted cartridge.

Ordinary exploration uses D-pad movement, A inspection and B companion ability.
The Controls setting swaps exploration actions: B inspects and A uses abilities.
Menu confirmation remains A and cancellation remains B. Start opens the pause
menu; Resume or cancellation returns to exploration. Select opens the current
objective panel, whose pages accept any button to advance or close. Native input
scripts consume held buttons around dialogue and transitions. The final
[input-driven emulator regression](../evidence/full-route-g4s6xp4r/report.json)
exercises standard and swapped actions, both characters, companion selection,
Quiet/Reduced Scares and all twelve puzzles on the cartridge below.

Settings are authored for separate Music Off and Effects Off choices, a Quiet
preset, Reduced Scares, and Normal/Fast/Instant text. Quiet suppresses music and
effects while keeping every clue visible. Music and text settings apply when
changed and on scene entry. Reduced Scares uses the calmer pool text and keeps
the necessary visual clue; it suppresses optional scare tones. Dawn revisits
acknowledge calm rooms rather than replay a first-time scare. No authored scare
uses rapid flashing, screen shake or a jump cut.

R01, R07, R13 and R19 are safe camps. Camp menus offer companion changes,
Roam/Marty selection, a first hint followed by explicit help on request, confirmed
Save and Leave. Return to Camp preserves permanent session progress and does not
silently write a save. The final hub places companion changes within one room of
each finale task. The final bell asks for two separate choices before ringing.

Dialogue wraps to sixteen characters per line and three lines per page, using
the retained fixed-width font. Both faces and target silhouettes are authored at
native 16×16 size. Source palette, geometry, text fit and tracker format checks
are useful evidence; they do not establish real audio balance, OAM behavior,
timed readability or player comfort.

The tested full cartridge SHA256 is
`de3ed696c6a80b5007ccc825693fabb781a661d30814fa6694864c467453b5d2`.
Its regression visits all 24 rooms and completes the ending before collecting
optional journal pages. Ordinary-input emulator success does not establish
first-time human readability, comfort or audio balance.

An [independent fresh replay and OAM audit](../evidence/independent-oam-hax1iz98/report.json)
matches all 984 recorded framebuffer samples across 107,468 emulated frames.
Per-frame sprite candidate counts never exceed the ten-object scanline limit;
R01, R10, R11, R16, R20 and R22 reach exactly ten. This result covers the recorded
route, including all 24 rooms, rather than every possible player position or
physical hardware. Peak-scene screenshots remain beside the report.

Before treating human pacing as verified, have fresh players complete the full
game without coaching until stuck. Include a Quiet/Reduced Scares run and a
swapped-actions run. Record hints, missed targets, menu confusion, text clarity,
tone, chapter times and finale understanding. The 60–90 minute duration remains
a design target until those runs exist. See [qa-report.md](qa-report.md) for actual cartridge
test evidence and [known-issues.md](known-issues.md) for unresolved behavior.
