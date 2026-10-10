# Original full-game artwork and music

The original generators, explicit cell data, compositions and provenance are
preserved here. They create editable output beside themselves. To regenerate,
run both Python generators, then run native/tools/full_game/integrate_world.py
with --assets-root pointing here, after selecting the intended native project.
The integrator closes unused perimeter exits and applies native sprite palettes
to the actual registered resource variants. It preserves project/version IDs.

Source projections and composition preview WAVs are not emulator evidence.
Native rooms, actors, palettes and original music have been authored; build,
complete cartridge playthrough, save recovery and physical QA remain separate.
No reference photo or third-party song data is copied into these originals.
No blanket game or character-art license is chosen here.

## Integrated verification

These original exports are now registered in the full native game. The exact DE3ED696 cartridge passed all 24 rooms and P01–P12 in `../../../docs/qa-report.md`. Independent input replay matched 984 framebuffer hashes and sampled native OAM every frame without exceeding ten objects per scanline on the recorded route. The continuous movie contains native APU audio from the five UGE songs; composition preview WAVs are not playback evidence. Human visual/audio review and physical hardware remain unverified.
