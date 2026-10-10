# Verified development setup

Verified on macOS, 9 October 2026: ModRetro Chromatic plugin 1.0.33; official bundled GB Studio CLI 4.3.2; Node 26.5.0; Python 3.13; PyBoy 2.7.0; Pillow 12.3.0. The native descriptor retains schema 4.2.0/release 10. No desktop editor was installed at the configured plugin path; desktop editor opening is still a human check.

Select `/Users/martinbowling/Projects/pocket-holler/native/project.gbsproj` through ModRetro. `rom_build` with `captureDebugArtifacts: true` and `outputPath: "dist/PocketHoller-opening.gbc"` was verified. It returns matching source-debug symbols and cartridge identity.

The exact verified underlying command is:

```sh
'/opt/homebrew/Cellar/node/26.5.0/bin/node' \
  '/Users/martinbowling/Library/Application Support/modretro-chromatic/toolchain/.local/vendor/gb-studio/out/cli/gb-studio-cli.js' \
  make:rom '/Users/martinbowling/Projects/pocket-holler/native/project.gbsproj' \
  '/Users/martinbowling/Projects/pocket-holler/native/dist/PocketHoller-opening.gbc' --verbose
```

`sh native/tools/build.sh` resolves project paths relative to itself. Override `POCKETHOLLER_NODE` and `POCKETHOLLER_CLI` for other installations. Use the plugin setup/doctor workflow for missing dependencies. No compiler binaries are shipped in the review package.

The cartridge is 128 KiB, GBC-only, MBC5 with 32 KiB battery RAM. Its mapper header advertises rumble; no rumble is authored. No proprietary boot ROM is included. `evidence/build-final.json` retains compiler output, source identity, header validation and ROM hash. The only final warning is upstream Node DEP0190. No missing-resource or authored-event warning remains.

A separate copy of descriptor, project, assets, and plugins was built with the official CLI. See `evidence/clean-build-report.json` and `clean-build.log` for the result and exact binary comparison. Cross-build fixtures are not interchangeable merely because gameplay content is identical.

Run `python3 native/tests/check_project.py` for identities, destinations and text fit. Run `native/tests/persistent_save.py` with the installed PyBoy Python to replay the controlled opening, collect genuine frames, save, cold boot, Continue, change options and cold boot again. It needs matching `.gbc.debug` files from the plugin build; the plain wrapper does not generate them. The test refuses a ROM that differs from the build receipt, creates fresh QA-only files, and never touches user saves.

Art exports are reproducible from `art/source/draw_opening.py` with Pillow. Generated creation batches must not be replayed over this project: the native resources include later event-ID, symbol, visibility and placement corrections. Native resources are the source of truth.

The intro art is hand-authored at 160×144 in `art/source/intro_v3.py`, using the character cell rows and native four-shade PNG. `title-v3-palettes.json` records seven palettes and the 20×18 tile palette map. Regenerating pixels does not register assets or change palette bindings: native resource files remain authoritative. `tests/intro_screen.py` checks genuine boot/motion/menu behavior. Run the persistent save test, copy its reported evidence to `evidence/opening-final/` without temporary cartridges or live RAM, then run character and exit tests against that paired fixture.
