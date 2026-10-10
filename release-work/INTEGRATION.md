# Integration and release status

The eighteen new rooms are authored proposals, not scenes installed in the current cartridge. The existing six-room opening ROM remains byte-identical (`511e690076d4a500a21c7f65d238a4f67b807d5a53d2f40a12115c7336b2d06a`). There is no full-game release ROM yet.

## Current blocker

ModRetro reports its selected project and authorized workspace as `/Users/martinbowling/Projects/pocket-holler/native`. The relocated source is `/Users/martinbowling/Projects/pocket-holler/src/native/project.gbsproj`; selection was refused with `PATH_OUTSIDE_PROJECT`. The documented server configuration for a common workspace is `GB_STUDIO_WORKSPACE_ROOT`, set before server startup. The owner has been asked to reconnect the server with `/Users/martinbowling/Projects/pocket-holler` as that workspace. No alternate caller, symlink, server reconfiguration or build was used to route around the refusal. Existing browser gameplay and saves were preserved.

## Prepared source

- R07–R12: Turtle, reeds, safe causeway stations, wheel flow controls and second light.
- R13–R23: Thunderbird, relay order, true plaques, spring channels, three bell lamps, explicit finale confirmation, optional pages and calm dawn.
- R24: fictional porch note and breakfast interior.
- Shared proposal: 24-room graph, four camps, both playable characters, recruited-only companion menus, journal, hints, quiet/audio options, new save epoch and dawn reunion/credits.
- Original art: eighteen native room backgrounds, seven six-frame sprite sheets, palette/collision arrays and editable generators.
- Original audio: five editable UGE loops, composition data and official format-validation receipts. Local approximate WAV previews remain outside Git.

`verify_proposals.py` and `verify_shared.py` check native event descriptions using a host-side state model. They prove authored conditions and static geometry only. They do not prove GBVM behavior, timing, input ownership, native menus, layering, audio, SRAM persistence or compatibility.

## Work required after authorized selection

1. Inspect the actual relocated project through ModRetro and preserve its revision. Add R07–R24 scene resources, assets and metadata using the proposed stable IDs. Keep existing resource/event IDs except deliberately replaced scripts. Register proposed music and assign phase/area tracks with Music/Effects/Quiet controls.
2. Install common controls and scripts efficiently as shared custom events. Expand the visible non-colliding follower to all three companions; preserve Marty/Roam sprites and selected character across every scene and load. Wire all graph edges and conditional shortcuts, including R01 interior and R04 dawn return. Align authored art exits with actual connections and collision; unused apparent exits need a clear closure.
3. Replace opening-only camp, goal, save and title-load branches. Save epoch becomes 2; refuse old opening snapshots without deleting them. Apply Normal/Fast/Instant text immediately and on entry/load. Implement and test actual A/B swap routing, including confirm/back labels; the proposed setting flag alone does not implement routing. Close Start/Select panels with their matching buttons or record an explicit reviewed change in controls.
4. Add native state feedback for all puzzle stages and light repairs, including effects/music changes on milestone completion. Scares are currently authored as safe inspections; delayed reflection timing and production presentation still need review. Dawn must suppress all scares. Finish specific engine/provenance credits before distribution.
5. Build the selected native project with debug artifacts; inspect ROM header, banks, warnings, exact hash and GBC/save settings. Build a fresh clean source copy independently within authorized paths. Preserve opening artifacts and fixtures; regenerate full-game test fixtures against the new exact ROM.
6. Play the complete route through ordinary controller input from clean boot, both characters and all three companions, P01–P12, all twenty-four rooms, reunion and credits. Retain actual 160×144 frame evidence, input journal and native game-audio playthrough video. Source-model evidence must remain labeled separately.
7. Test each puzzle's wrong actions, wrong companion, cancellation, unfinished re-entry, repeated completion and completed-route backtracking. Try all six lamp orders, all eight wheel configurations, optional-page-free completion, every exit, Return to Camp and comfort options. Cold-load saves at all four camps, after chapter milestones and dawn, including selected player and companion/options preservation.
8. Listen to real cartridge music/effects with quiet mixing and test Audio Off/Reduced Scares. Review worst-case sprite overlap/animation and input latency. Obtain fresh-player pacing notes before claiming the 60–90 minute target. Keep physical Chromatic status pending unless actually tested; do not flash hardware implicitly.
9. Update source README, credits, asset inventory, known issues and build instructions with actual full-game evidence. Resolve public licensing and visibility with the owner. Package the final editable source, ROM/hash, source commit, tests and notices, then publish the owner-authorized release. Do not tag the current staged proposal as a completed game.
