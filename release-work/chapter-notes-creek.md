# Creek chapter proposal — R07–R12

This module is staged source only. No native resource has been modified, and no ROM build or emulator claim is made. The relocated project selection remains refused by ModRetro's configured access boundary. The parent assigns stable IDs, registers variables, applies authorized semantic edits, connects scenes, and owns shared camps, input, saves and follower scripts.

Both Marty and Roam can complete this chapter. Dialogue addresses the player without assuming which character travels. Companions remain trustworthy and never become a platform left behind.

## Puzzle contracts

- P03 at R09: A at upstream, then A at downstream. Reversing the order resets only REED_STAGE and the two gates. Completion recruits Turtle, selects companion 2, opens the route, and offers a repeatable B practice target.
- P04 at R10: Turtle uses B at near, middle and far stations, left to right. A wrong station resets only STONE_STAGE. All three are approached from dry land; no unsafe-water traversal is required. Success hides the temporary wave marks and permanently opens the causeway.
- P05 at R11: A toggles inlet/bypass/outlet; open is one tile lower and closed is one tile higher. Set 1/0/1, then B with Turtle at the brace. A wrong arrangement gives a concrete explanation and preserves the freely editable arrangement. Reset is always reachable. Success fixes the arrangement and hides the brace wave mark.
- P06 at R12: B with Turtle at spillway after P05, then A at crank. Completion sets P06, CHAPTER=2 and PHASE=2. The light becomes visible. The parent opens both the ridge route and R07 shortcut. Text explicitly asks for a camp save and does not claim that the solve saved to disk.

Every solve is guarded by its prior dependency. Repeating a completed actor acknowledges success without replaying rewards or closing routes. Entry clears only unfinished local arrangements; it reconstructs the solved appearance using P03–P06. A later visit never rolls PHASE or CHAPTER backward. The parent must implement opened exits using permanent flags rather than current companion selection.

## H1

The pool-bank A inspection commits H1 before presentation. Reduced Scares shows a still reflection and a clear caption without movement or sound. Standard uses restrained descriptive text while the same reflection appears. No timer, sting or forced entry cutscene owns input; the living-companion clue is identical. This is a deliberately static initial implementation: the brief's approximately one-second delayed moving silhouette still needs a separately reviewed runtime presentation if retained for the production pass. Do not describe that motion as implemented or tested.

## Integration and navigation requirements

All coordinates are actor origins in 8-pixel gameplay tiles. The player occupies 2×2 tiles. Keep a 2×2 standing area immediately below each interactive actor, and connect it to the central dry walking area. Main exits reserve x8–11 at y0–2 and y16–17; side exits reserve y10–13 at x0–2 and x17–19. The following pairs are minimum approach checks, not a collision proof:

| Room | Actor/target | Origin | Safe standing origin below |
| --- | --- | --- | --- |
| R07 | creek_map / camp / camp_lantern | 4,6 / 8,8 / 14,6 | 4,8 / 8,10 / 14,8 |
| R08 | pool_bank / safe_bank | 6,6 / 12,10 | 6,8 / 12,12 |
| R09 | flow_clue | 8,4 | 8,6 |
| R09 | upstream / downstream | 4,6 / 12,6 | 4,8 / 12,8 |
| R09 | Turtle | 8,8 | 8,10 |
| R09 | practice_wave / reed_reset | 4,12 / 12,12 | 4,14 / 12,14 |
| R10 | near / middle / far wave stations | 4,6 / 8,6 / 12,6 | 4,8 / 8,8 / 12,8 |
| R10 | order clue / reset | 6,11 / 13,11 | 6,13 / 13,13 |
| R11 | flow diagram | 15,3 | 15,5 |
| R11 | inlet / bypass / outlet CLOSED | 4,6 / 8,6 / 12,6 | 4,8 / 8,8 / 12,8 |
| R11 | inlet / bypass / outlet OPEN | 4,7 / 8,7 / 12,7 | 4,9 / 8,9 / 12,9 |
| R11 | brace / reset | 5,12 / 13,12 | 5,14 / 13,14 |
| R12 | spillway / crank | 5,7 / 12,7 | 5,9 / 12,9 |
| R12 | ridge notice | 6,12 | 6,14 |

The non-colliding R08 reflection at 13,5 is a water decoration, never a walking target. The non-colliding R12 light at 12,4 is a visual indicator, with the crank carrying all mandatory interaction. Do not put water collision under ability approach squares. Do not put required interactions into the exit-trigger bands.

Actor counts exclude the parent's follower: R07=3, R08=3, R09=6, R10=5, R11=6, R12=4. The placed-actor count fits the preferred eight-actor ceiling; native scanline visibility still needs framebuffer inspection. The parent may replace hidden solved target marks with background stone artwork without changing puzzle flags.

## Acceptance cases after authorized integration

Check the legitimate P03→P04→P05→P06 route with both players; every wrong gate/station order; each of the eight wheel arrangements; reset and reentry after partial puzzles; wrong companion at all wave marks; solved routes with Moth, Turtle, Thunderbird and no companion; H1 standard/reduced/audio-off without retriggering; Return to Camp after each unfinished stage; cold-load at C1 after each solved milestone; and every return exit before/after gates. Pair those checks with the exact final ROM hash. No generated stage data establishes those runtime results.
