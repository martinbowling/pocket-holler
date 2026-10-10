# Credits and provenance

PocketHoller: After Sundown follows the owner's Full Game Agent Handoff, design
version 1.0, 9 October 2026. Marty and Roam are the owner's requested playable
character names. Both share the same quest progression. The owner supplied the
character concept direction; explicit native cell drawings preserve it without
shipping the original attachment or a family photograph.

Story adaptation, native game implementation, original room art, character cell
drawings, companion/target animations, original tracker compositions and
development tooling were prepared by the PocketHoller team with OpenAI Codex.
No exclusive copyright ownership or consent from an outside contributor is
asserted here. The five music tracks use original note/chord sequences,
instruments and waveform data; they contain no copied bundled song or external
recording. Original interaction sounds use authored native beep events.

The original full-game art and music generators are in
[art/source/full_game](../art/source/full_game/README.md). Opening pixel recipes,
the Marty/Roam/Moth cell drawings and the current intro illustration are in
`art/source/draw_opening.py`, `characters_v2.py` and `intro_v3.py`. Full-game
integration preserves these pixels and assigns native palette indices through
separate resource variants. [asset-inventory.csv](asset-inventory.csv) records
every registered asset, the retained unused originals, exact file and metadata
hashes, source recipes, attribution and supplied notices.

Native editor/compiler/runtime: GB Studio, Chris Maltby and contributors. Preserve
[GB-Studio-MIT.txt](../licenses/GB-Studio-MIT.txt) and the original
[native LICENSE](../LICENSE). ModRetro Chromatic plugin and original starter
presentation: Eric Provencher and the credited plugin authors; preserve
[ModRetro-plugin-MIT.txt](../licenses/ModRetro-plugin-MIT.txt).

The retained starter font, dialogue frame/cursor, workshop background and workshop
player follow their original cell recipes and MIT provenance. Eleven starter
font glyphs preserve the original Signal Lost title glyph definitions at commit
`5929961b938260ad112b87fc57145b7b23c7a196`; lowercase ASCII uses small-cap aliases.
See [starter source notes](../art/source/starter/README.md) and
[starter-provenance.json](../licenses/starter-provenance.json). These specific
upstream licenses are not a blanket license for new PocketHoller art, music,
dialogue or family character designs.

Development and verification tools include PyBoy, Pillow, Node.js and FFmpeg.
Their tool binaries are separately installed. Source checks, source projections
and approximate composition previews do not establish cartridge playback,
hardware behavior or a first-time player's experience. The final full cartridge
is bound by [its build receipt](../evidence/full-build.json) and
[passing emulator report](../evidence/full-route-g4s6xp4r/report.json) to SHA256
`de3ed696c6a80b5007ccc825693fabb781a661d30814fa6694864c467453b5d2`.
See [qa-report.md](qa-report.md) for the release evidence and its practical limits.

The owner authorized full-game implementation and source/ROM delivery. This
credits file preserves factual attribution and existing notices; it does not
choose an overall public distribution license or replace the owner's naming and
likeness decisions.
