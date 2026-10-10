# QA fixtures

These are test-only data, created through ordinary emulator controls. They are not user save files.

- `opening-reference.jsonl` retains controller actions and framebuffer hashes from the original recorded opening. Integrity-chain and file-location fields were removed to keep the source fixture compact. `manifest.json` records the original journal hash. The replay adapts the former four-page title to the current Start menu while preserving gameplay input timing. Older framebuffer hashes are compared strictly only against their original ROM; the current cartridge gets fresh captures.
- `porch-completed.ram.fixture` is the completed opening checkpoint paired with the included review ROM. It has both puzzles completed, Moth recruited, and the journal found, with Roam selected. Character and exit regressions copy it to a fresh QA cartridge path.
- `manifest.json` binds the fixture hashes and paired ROM identity.

A ROM rebuild may change its save signature even when content is unchanged. Build with matching debug artifacts, write the new build receipt to `native/evidence/build-final.json`, and run `persistent_save.py` to produce a fresh checkpoint. Copy the newly reported `porch-completed.ram.fixture` here and refresh its manifest before running character/exit checks against the new ROM. Do not replace a user save to prepare tests.

Test outputs are written to ignored folders under `native/evidence/`. The large recording journals and frame collections used during development are retained in the local review package.
