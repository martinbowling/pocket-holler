"""Legitimate full-route runtime regression, no initial RAM/state fixtures.

Run with the pinned PyBoy Python after the full ROM and paired receipt exist:
  <pyboy-python> native/tests/full_game.py

All progression comes from controller inputs. Optional pages are deliberately
left at zero until dawn reunion/credits, then collected by ordinary revisits.
"""
from pathlib import Path
import argparse,itertools,json,traceback
from full_game_driver import Driver,ROOT

PROGRESS=[f'P{i:02}' for i in range(1,13)]+[
    'RECRUITED_MOTH','RECRUITED_TURTLE','RECRUITED_THUNDERBIRD',
    'PHASE','CHAPTER','PLAYER_CHARACTER','ACTIVE_COMPANION','ENDING_SEEN',
    'AUDIO_OFF','REDUCED_SCARES','FAST_TEXT','MUSIC_OFF','EFFECTS_OFF']


def full_route(d,optional=True):
    d.new_game()
    d.assert_values(P01=0,P12=0,ENDING_SEEN=0)
    d.settings(6)  # Quiet preset; the full clue route must still work.
    d.settings(3)  # Reduced Scares on, independent of audio silence.
    d.settings(4,3)  # Instant text is an ordinary comfort option.
    d.assert_values(AUDIO_OFF=1,REDUCED_SCARES=1,FAST_TEXT=2)
    d.settings(5);d.assert_values(SWAP_BUTTONS=1)
    d.character(2);d.assert_values(PLAYER_CHARACTER=1)  # Inspect through physical B.
    d.settings(5);d.assert_values(SWAP_BUTTONS=0)
    d.character(3);d.assert_values(PLAYER_CHARACTER=1)  # Leave changes nothing.
    d.character(1);d.assert_values(PLAYER_CHARACTER=0)
    d.go_room('R03');d.interact('june');d.settle()
    d.go_room('R05')
    d.interact('windscreen',[1]);d.settle()
    d.interact('old_lantern');d.settle();d.assert_values(P01=0)
    d.interact('windscreen',[2]);d.settle()
    d.interact('old_lantern');d.settle()
    d.assert_values(P01=1,RECRUITED_MOTH=1,ACTIVE_COMPANION=1)
    d.settings(5);d.assert_values(SWAP_BUTTONS=1)
    d.ability('bark_mark');d.assert_values(BARK_REVEALED=1)  # Ability through physical A.
    d.settings(5);d.assert_values(SWAP_BUTTONS=0)
    d.go_room('R06');d.ability('inscription');d.interact('true_latch');d.settle()
    d.assert_values(P02=1,PHASE=1)
    d.go_room('R01');d.character(2);d.companion('Travel alone')
    d.assert_values(PLAYER_CHARACTER=1,ACTIVE_COMPANION=0)
    d.companion('Moth')
    assert [s.upper() for s in d.companion_options()]==['MOTH','TRAVEL ALONE','LEAVE']
    d.assert_values(ACTIVE_COMPANION=1)
    d.save();d.cold_continue(PROGRESS)
    d.assert_values(P02=1,PLAYER_CHARACTER=1,ACTIVE_COMPANION=1,CAMP_ID=0)

    # Camp1 cold-load before entering the creek puzzles; no chapter/save injection.
    d.go_room('R07');d.save();d.cold_continue(PROGRESS)
    d.assert_values(CAMP_ID=1,P03=0)
    d.go_room('R08');d.interact('pool_bank');d.settle();d.assert_values(H1=1)
    d.go_room('R09');d.interact('downstream_gate');d.settle()
    d.assert_values(P03=0,REED_STAGE=0)
    d.interact('upstream_gate');d.settle()
    d.go_room('R08');d.go_room('R09');d.assert_values(REED_STAGE=0)
    d.interact('upstream_gate');d.settle();d.interact('downstream_gate');d.settle()
    d.assert_values(P03=1,RECRUITED_TURTLE=1,ACTIVE_COMPANION=2)
    d.ability('practice_wave')
    d.go_room('R10');d.ability('far_wave');d.assert_values(P04=0,STONE_STAGE=0)
    d.ability('near_wave');d.go_room('R09');d.go_room('R10')
    d.assert_values(STONE_STAGE=0)
    for key in ['near_wave','middle_wave','far_wave']:d.ability(key)
    d.assert_values(P04=1)
    d.ability('far_wave');d.assert_values(P04=1)
    d.go_room('R11');d.ability('wheel_brace');d.assert_values(P05=0)
    d.interact('bypass');d.settle();d.ability('wheel_brace');d.assert_values(P05=0)
    d.interact('wheel_reset');d.settle()
    d.interact('inlet');d.settle();d.interact('outlet');d.settle()
    d.ability('wheel_brace');d.assert_values(P05=1)
    d.ability('wheel_brace');d.assert_values(P05=1)
    d.go_room('R12');d.interact('light_crank');d.settle();d.assert_values(P06=0)
    d.ability('spillway_wave');d.interact('light_crank');d.settle()
    d.assert_values(P06=1,PHASE=2)
    d.go_room('R07');d.companion('Moth');d.save();d.cold_continue(PROGRESS)
    d.assert_values(P06=1,CAMP_ID=1,ACTIVE_COMPANION=1)
    d.go_room('R12');d.interact('light_crank');d.settle();d.assert_values(P06=1)

    d.go_room('R13');d.save();d.cold_continue(PROGRESS)
    d.assert_values(CAMP_ID=2,P07=0)
    d.go_room('R14');d.interact('extra_footprint');d.settle();d.assert_values(H3=1)
    d.go_room('R15')
    d.interact('west_vane',[1]);d.settle();d.interact('east_vane',[4]);d.settle()
    d.interact('central_perch');d.settle();d.assert_values(P07=0)
    d.go_room('R14');d.go_room('R15');d.assert_values(VANEA=0,VANEB=0)
    d.interact('west_vane',[2]);d.settle();d.interact('east_vane',[4]);d.settle()
    d.interact('central_perch');d.settle()
    d.assert_values(P07=1,RECRUITED_THUNDERBIRD=1,ACTIVE_COMPANION=3)
    d.ability('practice_socket')
    d.go_room('R16');d.ability('wave_relay');d.assert_values(P08=0,RELAY_STAGE=0)
    d.ability('leaf_relay');d.go_room('R15');d.go_room('R16');d.assert_values(RELAY_STAGE=0)
    for key in ['leaf_relay','wave_relay','star_relay']:d.ability(key)
    d.assert_values(P08=1,CHAPTER=3)
    d.ability('star_relay');d.assert_values(P08=1)
    d.go_room('R13')
    for label,active in [('Moth',1),('Turtle',2),('Thunderbird',3),('Leave',3),('Travel alone',0),('Thunderbird',3)]:
        d.companion(label);d.assert_values(ACTIVE_COMPANION=active)
    d.save();d.cold_continue(PROGRESS);d.assert_values(CAMP_ID=2,P08=1)
    d.go_room('R17');d.interact('changed_sign');d.settle();d.assert_values(H2=1)
    d.go_room('R18');d.interact('old_notice');d.settle()
    d.go_room('R19');d.assert_values(VISITED_R19=1,CAMP_ID=3)
    d.save();d.cold_continue(PROGRESS);d.assert_values(CAMP_ID=3,P09=0)

    # Wrong selected companions do not solve either finale ability.
    d.companion('Turtle');d.go_room('R20');d.ability('plaque_a')
    d.assert_values(P09=0,PLAQUE_A=0)
    d.go_room('R19');d.companion('Moth');d.go_room('R20')
    for key in ['plaque_a','plaque_b','plaque_c']:d.ability(key)
    d.assert_values(H4=1)
    permanent=d.state([f'P{i:02}' for i in range(1,9)])
    d.interact('bell_instruction',[2]);d.settle()
    assert d.room()=='R19' and d.state(permanent)==permanent
    d.go_room('R20');d.interact('false_door',[1]);d.settle()
    assert d.room()=='R19' and d.state(permanent)==permanent
    d.go_room('R20')
    for key in ['plaque_a','plaque_b','plaque_c']:d.ability(key)
    d.interact('bell_instruction',[1]);d.settle();d.assert_values(P09=1)
    d.interact('bell_instruction');d.settle();d.assert_values(P09=1)
    d.go_room('R21');d.interact('left_channel',[2]);d.settle()
    d.interact('right_channel',[4]);d.settle();d.ability('spring_stone')
    d.assert_values(P10=0)  # Still Moth: wrong companion cannot Steady.
    d.go_room('R19');d.companion('Turtle');d.go_room('R21')
    d.interact('left_channel',[2]);d.settle();d.interact('right_channel',[1]);d.settle()
    d.ability('spring_stone');d.assert_values(P10=0)
    d.interact('right_channel',[4]);d.settle();d.ability('spring_stone');d.assert_values(P10=1)
    d.ability('spring_stone');d.assert_values(P10=1)
    d.go_room('R22');d.ability('bell_lamp_a');d.assert_values(P11=0,BELL_LAMPS=0)
    d.go_room('R19');d.companion('Thunderbird');d.save();d.go_room('R22')
    d.ability('bell_lamp_c');d.assert_values(P11=0,BELL_LAMPS=4)
    d.ability('bell_lamp_c');d.assert_values(BELL_LAMPS=4)
    d.go_room('R19');d.go_room('R22');d.assert_values(BELL_LAMPS=0)
    lamps=['bell_lamp_a','bell_lamp_b','bell_lamp_c']
    # Genuine disk checkpoint before P11 lets each order be tried without
    # injecting flags or fixtures. Discarding unsaved attempts is normal play.
    for order_index,order in enumerate(itertools.permutations(lamps)):
        if order_index:
            d.cold_continue();d.assert_values(P10=1,P11=0,P12=0,CAMP_ID=3)
            d.go_room('R22')
        for index,key in enumerate(order):
            d.ability(key);d.assert_values(P11=int(index==2))
            bit_state=d.value('BELL_LAMPS');d.ability(key)
            d.assert_values(BELL_LAMPS=bit_state)
        d.assert_values(P11=1,BELL_LAMPS=7)
    d.interact('hollow_bell',[2]);d.settle();d.assert_values(P12=0,PHASE=2)
    d.interact('hollow_bell',[1,2]);d.settle();d.assert_values(P12=0,PHASE=2)
    d.interact('hollow_bell',[1,0]);d.settle();d.assert_values(P12=0,PHASE=2)
    d.go_room('R19');d.companion('Travel alone');d.save();d.cold_continue(PROGRESS)
    d.assert_values(P11=1,ACTIVE_COMPANION=0,CAMP_ID=3)
    d.go_room('R22');d.interact('hollow_bell',[1,1]);d.settle()
    d.assert_values(P12=1,CHAPTER=4,PHASE=3,ENDING_SEEN=0)
    assert d.room()=='R23'
    assert all(d.value('J'+str(i))==0 for i in range(1,7)), 'Mandatory route accidentally collected journals'
    d.photo('dawn-before-home')
    d.go_room('R01')
    # Reunion is an ordinary guide interaction if not automatically presented.
    if not d.value('ENDING_SEEN'):
        d.open_camp();d.settle()
    d.assert_values(ENDING_SEEN=1,P12=1,PHASE=3)
    assert all(d.value('J'+str(i))==0 for i in range(1,7))
    d.save();d.cold_continue(PROGRESS);assert d.room()=='R01'
    d.assert_values(ENDING_SEEN=1,PHASE=3)
    d.character(1);d.assert_values(PLAYER_CHARACTER=0)

    if optional:
        for room,key,flag in [('R03','journal_page','J1'),('R24','porch_note','J2'),
                              ('R14','trail_sketch','J3'),('R17','bell_rhyme','J4')]:
            d.go_room(room);d.interact(key);d.settle();d.assert_values(**{flag:1})
        d.go_room('R19');d.companion('Moth');d.go_room('R18');d.ability('hidden_notice');d.assert_values(J5=1)
        d.go_room('R23');d.interact('dawn_drawing');d.settle();d.assert_values(J6=1)
        d.go_room('R01');d.save();d.cold_continue(PROGRESS+[f'J{i}' for i in range(1,7)])
        assert len(d.visited)==24,('Not every room visited',d.visited)
        d.cover_world_edges();d.go_room('R01')
    d.assert_values(**{f'P{i:02}':1 for i in range(1,13)})


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--rom',type=Path)
    parser.add_argument('--receipt',type=Path);parser.add_argument('--no-optional',action='store_true')
    args=parser.parse_args();driver=Driver(args.rom,args.receipt)
    try:
        full_route(driver,optional=not args.no_optional)
    except Exception:
        report=driver.finish(error=traceback.format_exc())
        print(json.dumps({'qa':str(driver.qa),'passed':False,'error':report['error']},indent=2));raise
    report=driver.finish(passed=True)
    print(json.dumps({'qa':str(driver.qa),'report':report},indent=2))


if __name__=='__main__':main()
