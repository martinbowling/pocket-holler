# Native build workflow

The full project has 24 playable rooms and a title scene. Open `native/project.gbsproj` in GB Studio with its adjacent `project/`, `assets/` and `plugins/` directories intact. Those native resources are authoritative; historical operation batches and `release-work/` proposals are development records, not installers.

Development environment: macOS, ModRetro Chromatic plugin 1.0.33, official bundled GB Studio CLI 4.3.2, Node 26.5.0, PyBoy 2.7.0, Pillow 12.3.0. The native descriptor retains schema 4.2.0/release 10. Tool binaries and proprietary boot ROMs are not distributed.

From the repository root:

```sh
sh native/tools/build.sh
python3 native/tests/check_project.py
```

The wrapper writes `native/dist/PocketHoller-full.gbc`, preserving the historical opening cartridge. On another installation set `POCKETHOLLER_NODE` and `POCKETHOLLER_CLI` to your Node executable and official CLI. It does not capture debug symbols; source debugging and runtime tests require ModRetro `rom_build` with `captureDebugArtifacts: true`, color mode `gbc-only`, and output `dist/PocketHoller-full.gbc`.

In Martin's workspace, the Git repository is `/Users/martinbowling/Projects/pocket-holler/src`; the authorized ModRetro working copy is `/Users/martinbowling/Projects/pocket-holler/native`. Edit and test in that working copy, then run `python3 native/tools/sync_source_repo.py` from the parent workspace for a dry run and append `--apply` after review. The utility verifies repository files against the original baseline before overwriting and preserves recordings, saves, and preview exports. In a normal clone, build the native folder directly; the local synchronization helper requires the sibling layout and its baseline file.

Run `native/tests/full_game.py` with the pinned PyBoy Python after obtaining the exact paired `evidence/full-build.json` and `.gbc.debug` directory. It refuses mismatched ROM/debug hashes and creates disposable QA files. Progression uses ordinary controller inputs, including confirmed camp saves and actual cold Continue. Old opening fixtures and tests remain paired only with `PocketHoller-opening.gbc`; they do not validate the full cartridge.

The full build receipt and QA report identify tested cartridge hashes and limitations. A clean source build is a separate reproducibility check. GB Studio embeds a project-data save signature, so identical visible gameplay does not establish compatibility between different builds. Preserve your original ROM and battery RAM when changing versions.

Editable art and original music generators are under `art/source/`, including `full_game/`. Regenerating exports does not update native registration or palette bindings automatically. Preserve resource IDs when editing. Physical Chromatic checks, desktop editor opening and fresh-player pacing require separate evidence.
