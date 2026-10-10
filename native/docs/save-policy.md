# Save policy

One native slot, schema 1, build epoch 1. Porch Save requires visible confirmation. It records the milestone before snapshotting and uses a safe porch checkpoint. Completed puzzles, phase, Moth recruitment, journal page, comfort flags and selected player persist. Return to Camp can reset unfinished windscreen work.

Continue checks slot existence and peeks schema/epoch before loading, then rebuilds the porch from quest flags. P02 reconstructs Moth/P01 and dusk/chapter state. Recruited Moth becomes active. Cross-build migration is not promised: GB Studio also embeds a project-data save signature. Pair fixtures with their exact ROM hash.

Return to Camp preserves session progress without a disk save. Quit confirms unsaved loss. New Game confirms when a slot exists, resets quest state while retaining comfort options, and keeps the old slot until confirmed Save. Overwrite and incompatible-save branches are authored; broader runtime coverage remains pending.

The final file-backed PyBoy test uses a copied ROM and private RAM file. Ordinary inputs reach the porch after P01/P02, save, stop the emulator, boot a new instance and Continue. A second test enables all comfort options, rests Moth, saves and cold boots again. Fixtures, states and the bound input trace are in `evidence/opening-final/`.

The plugin's stepped emulator uses an in-memory cartridge and closes without writing battery RAM. A fresh plugin session therefore has no slot. That is separate from the passed file-backed persistence result. Browser and physical persistence require their own tests. Never overwrite a user save with a fixture; copy ROM and fixture to a separate test directory.

PLAYER_CHARACTER (ID 52) uses 0=Roam, 1=Marty. Scene entry restores the chosen sprite and palette. The third cold-boot regression retains Marty after a confirmed porch Save. New Game currently retains character choice as a preference, alongside comfort options.
