# Ridge, hollow and dawn staged implementation

`ridge_hollow.py` is a pure authoring module for R13–R23. It returns native
event descriptions through the provided helper object. It does not select,
modify or build the relocated native project. Integration and ROM evidence
remain separate.

## Puzzle answers and persistent flags

| Contract | Room | Answer | Persistent completion |
| --- | --- | --- | --- |
| P07 | R15 | West shelter vane EAST; east shelter vane WEST; inspect central perch | P07, RECRUITED_THUNDERBIRD, ACTIVE_COMPANION=3 |
| P08 | R16 | Thunderbird Spark: LEAF, WAVE, STAR | P08, CHAPTER=3; third light derives from P08 |
| P09 | R20 | Moth Reveal all three plaques; choose CALL PEOPLE HOME | P09 |
| P10 | R21 | Left channel EAST; right channel WEST; Turtle Steady spring stone | P10 |
| P11 | R22 | Thunderbird Spark each ceramic lamp in any order | P11 |
| P12 | R22 | RING FOR ALL, then fresh A confirmation on RING NOW | P12, CHAPTER=4, PHASE=3; enters R23 |

P12 checks P02/P06/P08/P09/P10/P11. No companion is required at the ringing
decision. It never sets ENDING_SEEN, which remains the porch reunion/credits
milestone. It clearly states that ringing does not save. The final objective
must remain Go home until that reunion has been shown.

The unfinished local arrangements reset only while their puzzle is incomplete:
VANEA/VANEB, RELAY_STAGE, PLAQUE_A/B/C, CHANNEL_A/B, BELL_LAMPS. The parent should
clear the same arrangements on Return to Camp. Completed states never reset.
P11 uses a three-bit finite-state bitset and accepts all six lamp orders.

## Optional content and encounters

- J3 trail sketch in R14; J4 rhyme in R17; J5 optional Moth reveal in R18;
  J6 dawn drawing in R23. No journal flag gates any mandatory puzzle.
- H3 extra footprint is an A inspection before P07, with a persistent icon;
  its one-shot flag is set before the text and optional sound.
- H2 sign reads STAY after P08, on inspection, and HOME again at dawn. Its
  one-shot flag is set before the beat. It never removes the real return edge.
- H4 borrowed invitation accompanies the first P09 reveal. Speaker is
  A voice in the woods, never Marty. Its flag is set before presentation.
- Reduced Scares omits optional clicks and keeps every clue and caption.
  No camera shake, movement, full-screen flash or maximum-volume burst is used.
- False inscription and optional false doorway return safely to R19 without
  changing authoritative progression. Dawn inspections remain calm.

## Integration contract

Parent helpers: `e`, `text`, `setv`, `cond`, `num`, `var`, `sound`, `hide`, `actor_id`,
`menu`, `switch`. `sound('click')` must respect AUDIO_OFF as normal success
sounds do. If only the default success sound exists, map click to a quiet tone.
`hide(code,key)` uses the same stable actor ID as the returned actor description.
The actors use the requested sprite keys, including thunderbird, footprint,
spark, wave, bell and reflection. The optional property dictionary is currently
unused. Camp marker rows are consumed by the parent's full camp implementation.

Parent owns scene geometry, gates, transitions, safehub/CAMP_ID, companion
dispatch/follower, journal aggregation, hint tiers, sound/musical hooks and
save/load validation. Required new variables are VANEA, VANEB, RELAY_STAGE,
PLAQUE_A, PLAQUE_B, PLAQUE_C, CHANNEL_A, CHANNEL_B and BELL_LAMPS. Existing
P07–P12/J3–J6/H2–H4/PHASE/CHAPTER flags retain their IDs.

All actors stay away from central edge exit lanes. Each ability actor is
reachable from the tile below on the intended open floor. Largest scene is
R20/R22 with five authored actors plus the parent's visible follower. Keep
actor collision footprints and the wall decoration clear beneath targets.

The module inserts a native A-release loop immediately before the final
confirmation menu. The parent should likewise consume held inputs across
dialogue and ordinary menus/transitions. The release loop uses the single
stable label returned by `actor_id('R22', 'final-confirm-release')`, scoped to
the bell script.

## Verification needed after permitted integration

Run P07–P12 legitimately from P06 completion, with each wrong direction/order,
wrong companion and cancellation; leave/re-enter every unfinished puzzle;
complete each puzzle twice; revisit after switching companions; verify all
six lamp orders. Save/cold-load from R13 and R19 before and after milestones.
Check optional pages never gate progress, all three scare flags are one-shot,
and Reduced Scares with Audio Off retains the complete clue route. Finish at
R01 to prove reunion/credits and ENDING_SEEN rather than stopping at P12.

The staged module is authored content, not compiled or emulator-tested proof.

A local interpreter over the returned event tree verified 11 room descriptions,
39 actors, 12 ability targets and 449 unique event IDs. It exercised P07 wrong
and correct vanes; P08 wrong and correct relay orders; P09 false return and
re-entry reset followed by true choice; P10 wrong and correct channels; all six
P11 lamp orders with repeat-use guards; P12 waiting, cancelling final confirmation
and completing it. It verified dawn/CHAPTER=4/R23 and ENDING_SEEN still unset.
The interpreter does not prove actual GB Studio event compilation, input timing,
ability dispatch, collision, framebuffer readability, save durability or audio.
