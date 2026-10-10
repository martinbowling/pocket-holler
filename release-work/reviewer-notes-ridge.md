# Ridge/finale source review

Extended `verify_proposals.py` with source-model contracts for P07–P12 while
preserving the existing static and creek checks. This is authored-source and
host-side model evidence only. No selected native project or ROM was changed,
built or played by these checks.

The model checks wrong shelter directions, relay order recovery, unfinished
re-entry resets, wrong companion dispatch, false inscription/door return to R19
without persistent flag loss, wrong spring channels, repeat solves, all six lamp
orders and repeated lamps, mandatory preconditions, waiting and cancellation at
both finale menus, dawn before ENDING_SEEN, and reunion/credits with all six
journal flags still zero. Reduced Scares plus Audio Off leave the logical route
and encounter flags available. Physical A-release timing, native dispatch and
quiet audio still require compiled-ROM inspection.

The art collision review identified an unsafe below approach for the optional
R15 practice socket at y13: a conservative 2x2 player standing at y15 reaches the
blocked row16 scenic rim. With parent authorization, every ridge/hollow y13
inspection actor moved to y12, and the practice target moved with its actor.
Affected actors: R15 feather board/practice socket, R16 relay board/ridge light,
R18 all-lights notice, R20 false doorway, R21 spring diagram, R22 bell notice.
No artwork or art manifest was edited.

After correction, a conservative 2x2 player flood fill from each room's lower
landing reaches the below approach of all 39 ridge/finale actors while treating
every other actor as solid. All 12 ability target coordinates match their actor
coordinates and their below-standing footprints avoid the water palette. This
uses the staged collision manifest and approximate sprite footprints; it cannot
establish native collision timing, real actor bounds or in-game readability.

Executed checks passed: existing static structure (24 connected rooms), creek
contracts, ridge/finale contracts and source geometry. The parent should rerun
the script after assembling the latest proposal so its retained JSON report
matches the final staged source revision.
