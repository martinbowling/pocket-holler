# PocketHoller full-game art and music handoff

These are original, editable standalone production assets for integration after
the intended native project can be selected. Nothing in the active native
project, current ROM, emulator, recordings, or user saves was modified.

## Room art

`art/generate_art.py` creates eighteen 160×144 backgrounds, R07–R24. The actual
manual source shades are `071821`, `306850`, `86c06c`, `e0f8cf`, darkest first.
No photo, sprite concept sheet, screenshot, template bitmap, or external artwork
is read or sampled. The source tiles and drawn landmarks are explicitly authored.

Each background has a native `.png.gbsres` sidecar and a 360-cell palette and
collision array in `art/art-manifest.json`. Use `solid` as the room's collision
input, not an inferred bitmap mask. Clear floor covers tiles x2–17, y3–15.
Candidate top/bottom exits x8–11 and side exits y10–13 have clear landing areas.
Only perimeter decorations are blocked. Central stepping surfaces are wood or
stone; no central water is falsely drawn as walkable. The widest tile budget is
18 unique tiles, well below the requested 200-tile cap.

Palette indices are 0 foliage, 1 wood, 2 glow, 3 water, using the existing palette
resources. Slot 7 remains untouched for UI. These sidecars decode correctly with
the official installed GB Studio byte-run codec. Preview images apply those
existing display palettes; they are source projections, not emulator captures.

Distinct rim landmarks include creek reeds and reflection, a broad wooden
causeway, wheelhouse wheel, spillway/light, ridge cliffs and stairs, a roost,
ceramic relays, bell road, noticehouse books, root hub, echo windows, spring,
mounted bell, dawn horizon, and a warm porch interior. The intentionally simple
central floors leave room for the chapter agents' actors, interactions and clues.

Review files:

- `art/previews/rooms-contact-1x.png`: labelled backgrounds at native size.
- `art/previews/rooms-contact-2x.png`: exact nearest-neighbor 2× review.
- `art/previews/r07-color.png` through `r24-color.png`: individual projected rooms.

## Companions and target sprites

Seven original 96×16 sheets provide six horizontal 16×16 frames each: turtle,
thunderbird, wave, spark, bell, footprint and reflection. `art/sprite-cells.json`
holds the editable base cells; the generator explicitly applies each idle/effect
variation. Marty and Roam's approved existing sprites are preserved.

The only sprite source colors are transparent marker `65ff00` and opaque
`071821`, `86c06c`, `e0f8cf`. Sheets never contain background-only `306850`.
Native sidecars use a compatible fixed-animation state, all eight native animation
slots, deterministic IDs, six primary frames, correct frame slices, a SHA-1
checksum, and a conservative twelve 8×16 tile-pair budget. Set the intended
actor's animation behavior deliberately; do not import these as a directional
player sheet merely because their width is 96 pixels.

`art/previews/sprites-contact-3x.png` shows every authored frame. Source silhouettes
were inspected at native and enlarged sizes. Runtime layering, follower position,
comfort-setting effects, OAM crowding and actual timed playback still need native
emulator checks after integration.

## Original music

`art/generate_music.py` writes five original hUGETracker version-6 loops and their
native music sidecars. Explicit note/chord lists, all instrument definitions and
the original 32-sample waveform remain editable in that script and per-song
`.sequence.json` files. Each loop has an authored answering phrase; no bundled
music data or third-party recording is copied.

| Music | Intended scenes | Loop length |
|---|---|---:|
| Porch lanterns | Title, porch, opening town, interior | about 34.3 seconds |
| Leaves on the creek | R07–R12 | about 38.6 seconds |
| Three ridge lamps | R13–R18 | about 34.3 seconds |
| The spring remembers | R19–R22 | about 42.9 seconds |
| Breakfast after sundown | All DAWN rooms and reunion | about 52.5 seconds |

Pulse melody initial volume is 5, supporting pulse 3, wave output level 3 (quarter
volume), and the brief noise brush 1. These are authored quiet instrument levels;
actual Game Boy master volume and mix depend on the engine/runtime settings.
Honor Music Off, reduced effects and calm-room settings when integrating.

All final `.uge` files pass the installed official GB Studio `loadUGESong`, note
and instrument comparisons for every pattern cell, `saveUGESong` roundtrip, and
`exportToC`. All thirty background/sprite/music sidecars pass official resource
schemas. See `art/validation-report.json`. This check selects or builds no native
project and does not use another caller to bypass the project's path refusal.

The `.wav` files are approximate composition previews using original pulse,
triangle and deterministic brush synthesis. They are never represented as Game
Boy APU or cartridge recordings. Their numeric level checks are in
`art/audio-preview-check.json`. No listening tool is exposed in this session, so
auditory review and exact in-ROM playback remain outstanding. A player/owner can
listen to these files during review; the full-game QA must capture the real ROM.

## Reproduction and integration

Run `generate_art.py` and `generate_music.py` from this directory with Python and
Pillow. Run `node validate_uge.cjs /absolute/path/to/installed/gb-studio` to check
the output against the official reader/writer and native resource schemas.
The scripts write only beside themselves. Keep these editable sources when
integrating, and preserve the proposal previews separately from runtime evidence.

Every generated file is listed in `art/SHA256SUMS`; the files are proposals until
the parent agent integrates and builds the intended project through an authorized
native workflow. Artwork/audio originality is recorded here; these notes do not
choose or grant a blanket public license for the game or family character art.

## Remaining visual and audio review

The base floors are deliberately spacious and repetitive to fit the shared actor
contract. Functional actors, readable targets and clue text must complete the
scene composition. Every candidate rim exit is visually open; integration must
align the actual room connections with those openings so an unused doorway does
not confuse players. Room palettes use existing families rather than introduce
an unreviewed night color system. Verify phase changes in the actual ROM.

These checks do not establish hardware behavior, first-time play duration, real
audio balance, absence of sprite flicker, or full-game release readiness.
