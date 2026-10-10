# Provenance and distribution terms

This source contains the authored full PocketHoller game: 24 rooms plus the intro,
Marty and Roam, three companions, twelve required puzzles, optional journals and
the dawn reunion. The owner authorized source and ROM delivery to their existing
private repository. That delivery does not change repository visibility or choose
a public license. MIT for new scripts and CC BY 4.0 for cleared new content were
proposals in the design handoff; no overall license grant is selected here. Do
not interpret the upstream `LICENSE` as a blanket license for new PocketHoller
art, music, dialogue or character designs.

| Group | Provenance and terms | Included material |
| --- | --- | --- |
| Native format and GB Studio engine | Chris Maltby / GB Studio, MIT notice retained in `LICENSE` and `licenses/GB-Studio-MIT.txt` | Native metadata; compiler-generated runtime in ROM |
| ModRetro original starter presentation | Eric Provencher / ModRetro plugin original pixel recipes, repository MIT; notice in `licenses/ModRetro-plugin-MIT.txt` | Bench Mono font, dialogue frame/cursor; unused workshop/player sources |
| New PocketHoller pixels | Original Codex-assisted explicit tile/sprite recipes on 9 October 2026 | 24 room backgrounds, intro illustration, Marty/Roam/June and companion/target sprites; `art/source/draw_opening.py`, `characters_v2.py`, `intro_v3.py`, and `full_game/` |
| New scripts/dialogue | Codex-assisted implementation of owner-supplied handoff | Native scene/actor/trigger scripts and development tools |
| Original music and effects | Five original tracker compositions and authored native beep settings | Porch, creek, ridge, hollow and dawn `.uge` loops; editable sequence/generator sources; gentle interaction effects |
| Original palette resources | Authored daylight, dusk, night, dawn and object colors | Distinct readable blue night/nightwood resources; retained upstream defaults separately identified |
| Tools | ModRetro 1.0.33, GB Studio CLI 4.3.2, Node, PyBoy, Pillow | Not bundled as executables; preserve their own terms in installations |

`docs/asset-inventory.csv` records exact file and native metadata hashes, source,
authorship method, modifications, attribution and supplied notices per asset,
including retained unused startup art. `licenses/starter-provenance.json`
preserves the supplied upstream receipts. Portable starter pixel/glyph recipes
and cells are retained in `art/source/starter/`. Eleven font glyphs reuse original
Signal Lost glyph definitions identified by that provenance. These supplied
notices apply to their specific upstream material.

The new art uses editable explicit native pixel cells. The user-provided character
concept informed broad direction; its original attachment and any family photo
are excluded from the game assets. No exclusive copyright ownership or outside
contributor consent is asserted. Dialogue adapts the owner-supplied brief. Five
original music generators preserve note sequences, instruments and waveforms;
no bundled song, downloaded music or third-party audio recording was copied.

The art/music inventory and source recipes do not contain commercial-game art,
ROMs or proprietary boot ROMs. Development tools retain their own installation
terms. Private owner delivery, public licensing and physical cartridge flashing
are separate actions; this document authorizes none beyond the owner's existing
delivery instruction. Source validation and approximate composition previews do
not establish native audio playback, physical-hardware behavior or human pacing.
See `docs/credits.md` for attribution and `docs/qa-report.md` for actual build and
runtime evidence.

The two original night palette resources were authored directly as editable
four-color native JSON on 9 October 2026. Their light-to-dark colors preserve
ordered brightness and distinct blue shadows; their actual scene application
and emulator readability require current runtime evidence.

| Resource | Stable ID | Colors, light to dark | SHA256 |
| --- | --- | --- | --- |
| `project/palettes/night.gbsres` | `103752d1-a4a7-5c30-b66a-87f5ff883551` | `BDD5D2`, `607E96`, `354A6B`, `101A32` | `67fdb2879bd051b2eee6d87eb12c0a73a0e1fa1012cef0abf981372989c264b4` |
| `project/palettes/nightwood.gbsres` | `656a3609-ce78-5a1e-8edf-b0a88c5c377e` | `DECBA8`, `967B84`, `514563`, `101A32` | `c5d9846409c021ec77c2add8c449c635c80b2f865dd3feb81933086976b00969` |
