# PocketHoller opening review build

Editable native source: `project.gbsproj` plus `project/` and `assets/`. Play `dist/PocketHoller-opening.gbc` in a GBC emulator; this is Color Only. Physical Chromatic testing is pending. See [QA report](docs/qa-report.md) for the exact tested hash and evidence.

The title opens on a moonlit mountain scene with Marty, Roam, Lantern Moth, lit cabins, and copper lettering. The lantern light breathes gently. Press **Start** or **A** for New Game, Continue, and Settings; **B** returns to the title artwork. Browser Start is **Enter**. Editable pixels and palette cells are in `art/source/intro_v3.py` and `title-v3-palettes.json`; `evidence/intro-final/` contains genuine cartridge frames and a four-second motion capture.

Marty and Roam are both playable. At the porch, talk to the other character and choose **Character**, then **Roam** or **Marty**. Roam wears green and has curly hair; Marty wears orange and has glasses. The other character stays as porch guide. Switching preserves quests and companions; Save/Continue retains the selected character.

Visit the porch, lane, store, festival green, orchard, and boundary gate. Talk to the porch guide and June, watch the wind, find LanternMoth, use Reveal, repair the first light, return home, and save. The optional store journal page is not required. The future creek chapter stops at the review boundary.

| Input | Action |
| --- | --- |
| D-pad | Walk; move menu selection |
| A | Talk, inspect, advance text, confirm |
| B | Moth Reveal on a faced marked target; cancel menus |
| Start | Open pause menu |
| Select | Show current objective and companion |

Browser keys: arrows, Z for A, X for B, Enter for Start, P for Select. In this candidate, A closes the objective and B cancels pause menus. Start/Select do not yet close their own panels as specified in the handoff. This opening has no threats or timers.

Pause offers Journal, Settings, Return to Camp, Quit, and Resume. Porch camp offers Companion, Hint, Save, Leave, and Character. Moth can rest while Roam travels alone. Reveal has no charges. Wrong puzzle choices are freely correctable. Face the ray-marked tile before pressing B.

Settings provide Audio Off, Reduced Scares, and Fast Text. The opening has text-only unease and simple original effects; production music and scare variants remain pending. All mandatory clues have text or shape cues.

Save at the porch and confirm. Return to Camp preserves completed puzzles in the session but does not save. Quit warns about unsaved loss. New Game confirms when a slot exists and leaves it untouched until a later confirmed Save. Continue restores a safe porch checkpoint and deliberately activates recruited Moth, including after a save while traveling alone. There is one slot. Preserve the emulator's battery RAM alongside its ROM.

Fixtures are paired with this exact build. Cross-build migration, browser battery persistence, incompatible-save runtime fixtures and hardware power cycles remain pending. The stepped plugin emulator has transient RAM; persistence was verified separately using file-backed PyBoy. See [save policy](docs/save-policy.md).

The native resources are authoritative. Generated operation batches are development records, not an installer: replaying them can duplicate actors. Preserve resource IDs when editing. Report bugs with ROM hash, emulator/version, starting state, room, inputs and screenshot. Keep family photos and private details out of reports.
