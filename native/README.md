# PocketHoller: After Sundown

A native Game Boy Color adventure with **Marty and Roam**, 24 playable rooms, twelve lantern puzzles, three companions, four safe camps, six optional journal pages, a dawn reunion and credits. Editable GB Studio source is `project.gbsproj` with its adjacent `project/` and `assets/` folders. The full cartridge is `dist/PocketHoller-full.gbc`; the historical six-room opening is preserved separately.

The moonlit intro features both characters beneath Lantern Moth, copper lettering, lit cabins and a gently breathing lantern. Press **Start** or **A** for New Game, Continue and Settings; **B** returns to the artwork.

## Play

| Input | Action |
| --- | --- |
| D-pad | Walk; select a menu row |
| A | Talk, inspect, advance text, confirm |
| B | Use the selected companion's ability; cancel menus |
| Start | Open Journal, Settings, Return to Camp, Quit and Resume |
| Select | Show the next objective |

Browser controls are arrows, Z, X, Enter and P respectively. Choose Resume or B to close pause. Select objective pages accept any button, including Select; several pages can require several presses. **Swap Actions** exchanges A/B in exploration; menus retain A confirmation and B cancellation, as shown by the settings text.

Roam wears green and has curly hair; Marty wears orange and glasses. At a safe camp choose **Character** to switch freely. Both share quests and companion abilities. The other character is your porch guide. New Game begins as Roam; camp Save/Continue retains the selected character.

Lantern Moth reveals ray marks, Mossback Turtle steadies wave stones, and Thunderbird sparks zigzag fixtures. Face a marked actor from an adjacent tile, then use the ability button. Companions have no fuel, charges or health. Swap recruited companions at camps or choose Travel alone. They remain dependable and cannot block doors. Wrong actions are correctable; completed puzzles stay complete.

The route follows the porch and orchard to the boundary light, then the creek reeds, causeway and wheelhouse, ridge roost and relays, and hollow bell. Each chapter has a camp and hints. The bell asks for confirmation before dawn. Return home for breakfast and credits, then revisit the peaceful town. Journal pages are optional, including the porch interior page.

## Saves and comfort

Save explicitly at R01 porch, R07 creek camp, R13 ridge camp or R19 root threshold. Confirming Save replaces the one slot. **Return to Camp** preserves session progress but does not save. Quit warns about unsaved progress. New Game leaves an existing slot intact until you explicitly save the new session.

Continue restores the saved character, recruited companion choice, completed puzzles, pages and settings at a safe camp. Unfinished room attempts reset. After the bell, returning to camp leads home for the reunion. Preserve the emulator battery RAM with its cartridge. Full-game epoch 2 and historical opening epoch 1 are distinct; cross-build save migration is not promised.

Music and Effects can be turned off separately. Quiet preset silences both. Reduced Scares keeps clues in ordinary text; Normal, Fast and Instant text speeds are available. No combat, death, companion harm, timers, flashing or screen shake is authored. Atmospheric encounters use restrained inspection text and visible symbols.

## Source and verification

See `docs/build.md`, `docs/qa-report.md`, `docs/save-policy.md` and `docs/known-issues.md` for build steps, exact cartridge evidence and remaining limitations. Native resources are authoritative; historical proposal/operation batches should not be replayed as installers. Original editable art/music recipes are under `art/source/`.

The full source check is `python3 native/tests/check_project.py` from a repository root. The receipt-paired input regression is `native/tests/full_game.py`; `native/tests/full_playthrough.py` records one continuous ordinary-input journey for `tools/render_full_playthrough.py`. Each uses private emulator files and retains exact controller/frame evidence. Physical hardware, audio listening and first-time human pacing are separate checks.

An overall public license for new game content has not been chosen. Upstream MIT notices remain in `licenses/` and `LICENSE`; they do not grant a blanket license for all PocketHoller content. See `THIRD_PARTY.md` and the asset inventory. The owner-supplied concept sheet and family photos are excluded from the cartridge and repository.
