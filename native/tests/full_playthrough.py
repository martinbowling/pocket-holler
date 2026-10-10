"""One continuous ordinary-input, normal-audio full-game capture route.

Fresh boot through all 12 puzzles, all 24 rooms and dawn reunion; no cold boots,
save-state shortcuts, initial RAM fixtures or progression writes. The parent
encoder can replay this exact retained input journal to record every APU/frame.
"""
from pathlib import Path
import argparse,json,traceback
from full_game_driver import Driver


def playthrough(d):
    d.reading_frames=48
    d.release(300)
    d.new_game();d.assert_values(AUDIO_OFF=0,MUSIC_OFF=0,EFFECTS_OFF=0)
    d.character(2);d.assert_values(PLAYER_CHARACTER=1)
    d.go_room('R24');d.interact('porch_note');d.settle()
    d.go_room('R03');d.interact('june');d.settle();d.interact('journal_page');d.settle()
    d.go_room('R05');d.interact('weather_vane');d.settle()
    d.interact('windscreen',[2]);d.settle();d.interact('old_lantern');d.settle()
    d.ability('bark_mark');d.assert_values(P01=1)
    d.go_room('R06');d.ability('inscription');d.interact('true_latch');d.settle()
    d.assert_values(P02=1);d.go_room('R01');d.save()
    d.go_room('R07');d.interact('creek_map');d.settle();d.save()
    d.go_room('R08');d.interact('pool_bank');d.settle()
    d.go_room('R09');d.interact('flow_clue');d.settle()
    d.interact('upstream_gate');d.settle();d.interact('downstream_gate');d.settle()
    d.ability('practice_wave');d.assert_values(P03=1)
    d.go_room('R10');d.interact('causeway_order');d.settle()
    for key in ['near_wave','middle_wave','far_wave']:d.ability(key)
    d.assert_values(P04=1)
    d.go_room('R11');d.interact('flow_diagram');d.settle()
    d.interact('inlet');d.settle();d.interact('outlet');d.settle();d.ability('wheel_brace')
    d.assert_values(P05=1)
    d.go_room('R12');d.ability('spillway_wave');d.interact('light_crank');d.settle()
    d.assert_values(P06=1);d.go_room('R07');d.save()
    d.go_room('R13');d.interact('ridge_notice');d.settle();d.character(1);d.save()
    d.go_room('R14');d.interact('extra_footprint');d.settle();d.interact('trail_sketch');d.settle()
    d.go_room('R15');d.interact('feather_board');d.settle()
    d.interact('west_vane',[2]);d.settle();d.interact('east_vane',[4]);d.settle()
    d.interact('central_perch');d.settle();d.ability('practice_socket');d.assert_values(P07=1)
    d.go_room('R16');d.interact('relay_board');d.settle()
    for key in ['leaf_relay','wave_relay','star_relay']:d.ability(key)
    d.assert_values(P08=1);d.go_room('R13');d.save()
    d.go_room('R17');d.interact('changed_sign');d.settle();d.interact('bell_rhyme');d.settle()
    d.go_room('R18');d.interact('old_notice');d.settle();d.interact('all_lights_notice');d.settle()
    d.go_room('R19');d.companion('Moth');d.save()
    d.go_room('R18');d.ability('hidden_notice');d.go_room('R20')
    for key in ['plaque_a','plaque_b','plaque_c']:d.ability(key)
    d.interact('bell_instruction',[1]);d.settle();d.assert_values(P09=1)
    d.go_room('R19');d.companion('Turtle');d.go_room('R21')
    d.interact('spring_diagram');d.settle()
    d.interact('left_channel',[2]);d.settle();d.interact('right_channel',[4]);d.settle()
    d.ability('spring_stone');d.assert_values(P10=1)
    d.go_room('R19');d.companion('Thunderbird');d.go_room('R22')
    d.interact('bell_notice');d.settle()
    for key in ['bell_lamp_a','bell_lamp_b','bell_lamp_c']:d.ability(key)
    d.assert_values(P11=1);d.go_room('R19');d.save();d.go_room('R22')
    d.interact('hollow_bell',[1,1]);d.settle()
    d.assert_values(P12=1,PHASE=3,ENDING_SEEN=0)
    d.interact('dawn_notice');d.settle();d.interact('dawn_drawing');d.settle();d.release(180)
    d.go_room('R01')
    if not d.value('ENDING_SEEN'):
        d.open_camp();d.settle()
    d.assert_values(ENDING_SEEN=1);d.save();d.release(240)
    d.assert_values(**{f'P{i:02}':1 for i in range(1,13)})
    d.assert_values(**{f'J{i}':1 for i in range(1,7)})
    d.assert_values(**{f'H{i}':1 for i in range(1,5)})
    assert len(d.visited)==24 and d.boots==1


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--rom',type=Path);parser.add_argument('--receipt',type=Path)
    args=parser.parse_args();d=Driver(args.rom,args.receipt,label='full-playthrough',sound=True)
    try:
        playthrough(d)
    except Exception:
        report=d.finish(error=traceback.format_exc());print(json.dumps(report,indent=2));raise
    report=d.finish(passed=True);report['captureRoute']='Continuous clean boot to dawn reunion, normal game audio, 24 rooms'
    (d.qa/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
