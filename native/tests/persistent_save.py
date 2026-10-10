"""Replay the model-controlled plugin recording using file-backed PyBoy RAM.
Never reads or changes user saves; its cartridge and RAM live in a fresh QA dir.
Verifies recorded frame hashes and cold-boot Continue against the same ROM.
"""
from pathlib import Path
import hashlib, json, re, shutil, tempfile
from pyboy import PyBoy

ROOT=Path(__file__).resolve().parents[1]
ROM=ROOT/'dist/PocketHoller-opening.gbc'
EVENTS=ROOT/'tests/fixtures/opening-reference.jsonl'
rows=[json.loads(s) for s in EVENTS.read_text().splitlines()]
expected=json.loads((ROOT/'evidence/build-final.json').read_text())['rom']['sha256']
assert hashlib.sha256(ROM.read_bytes()).hexdigest()==expected
qa=Path(tempfile.mkdtemp(prefix='save-qa-',dir=ROOT/'evidence'))
cart=qa/ROM.name;shutil.copy2(ROM,cart)
p=PyBoy(str(cart),window='null',sound_emulated=False,cgb=True)
p.set_emulation_speed(0)
[p.tick(1,True) for _ in range(180)]
held=set();samples=0;matched=0;capture=[];frame_count=180;film=[]
capture_dir=qa/'frames';capture_dir.mkdir()
def tick(frames):
    global frame_count
    for _ in range(frames):
        p.tick(1,True);frame_count+=1
        if 9250<=frame_count<=10650 and frame_count%4==0:
            film.append(p.screen.image.copy())
capture.append({'kind':'header','romSha256':expected,'referenceInputRomSha256':rows[0]['rom']['sha256'],'runtime':'PyBoy 2.7.0','startingCondition':'clean boot, 180 frames','source':'Input-driven replay; no memory writes'})
title_presses=0
for row in rows:
    if row['kind']=='action':
        action=dict(row['action'])
        # The recorded opening formerly had four title dialogue pages. Keep
        # its timing, replacing those presses with Start and neutral waits.
        # All subsequent gameplay inputs are preserved verbatim.
        if action['type']=='set_buttons' and action['buttons']==['a'] and title_presses<4:
            title_presses+=1
            action['buttons']=['start'] if title_presses==1 else []
        if action['type']=='set_buttons':
            new=set(action['buttons'])
            for b in held-new:p.button_release(b)
            for b in new-held:p.button_press(b)
            held=new
        elif action['type']=='step':tick(action['frames'])
        capture.append({'kind':'action','frame':frame_count,'action':action})
    elif row['kind']=='frame' and row['frame']>=180:
        actual=hashlib.sha256(p.screen.image.convert('RGBA').tobytes()).hexdigest()
        matched+=actual==row['rgbaSha256']
        if expected==rows[0]['rom']['sha256']:
            assert actual==row['rgbaSha256'],f"Replay differs at frame {row['frame']}"
        filename='frames/'+actual+'.png';p.screen.image.save(qa/filename)
        capture.append({'kind':'frame','frame':frame_count,'rgbaSha256':actual,'file':filename})
        samples+=1
p.screen.image.save(qa/'saved-message.png')
(qa/'events.jsonl').write_text('\n'.join(json.dumps(r) for r in capture)+'\n')
film[0].save(qa/'boundary-gameplay.gif',save_all=True,append_images=film[1:],duration=67,loop=0)

# Resolve this build's reserved variables from its actual compiler outputs.
symbols=(ROOT/'dist/PocketHoller-opening.gbc.debug/symbols.noi').read_text()
glob=(ROOT/'dist/PocketHoller-opening.gbc.debug/globals.i').read_text()
base=int(re.search(r'DEF _script_memory 0x([0-9A-Fa-f]+)',symbols)[1],16)
names=['SAVE_SCHEMA','BUILD_SAVE_EPOCH','P01','P02','PHASE','CHAPTER','RECRUITED_MOTH','ACTIVE_COMPANION','J1','MILESTONE_SAVED','AUDIO_OFF','REDUCED_SCARES','FAST_TEXT','PLAYER_CHARACTER']
offsets={n:int(re.search(r'VAR_'+n+r'\s*=\s*(\d+)',glob)[1]) for n in names}
def values():
    return {n:p.memory[base+2*i]+256*p.memory[base+2*i+1] for n,i in offsets.items()}
before=values()
assert before['P01']==before['P02']==before['RECRUITED_MOTH']==1
p.stop(save=True)
ram=Path(str(cart)+'.ram');assert ram.exists(), 'PyBoy did not write cartridge RAM'
shutil.copy2(ram,qa/'porch-completed.ram.fixture')
p=PyBoy(str(cart),window='null',sound_emulated=False,cgb=True)
p.set_emulation_speed(0);[p.tick(1,True) for _ in range(180)]
held=set()
actions=[]
def step(buttons,frames):
    global held
    new=set(buttons)
    for b in held-new:p.button_release(b)
    for b in new-held:p.button_press(b)
    held=new;[p.tick(1,True) for _ in range(frames)];actions.append({'buttons':buttons,'frames':frames})
def press(b):step([b],8);step([],110)
press('start')
press('down');press('a');step([],140)
after=values();p.screen.image.save(qa/'continued-at-porch.png')
for n in names:assert before[n]==after[n],f'{n} changed: {before[n]} -> {after[n]}'
pos_base=int(re.search(r'DEF _actors 0x([0-9A-Fa-f]+)',symbols)[1],16)
xy=[(p.memory[pos_base+i]+256*p.memory[pos_base+i+1])/256 for i in [1,3]]
assert xy==[8,12],xy
report={'romSha256':expected,'runtime':'PyBoy 2.7.0 file-backed RAM','frameSamplesCaptured':samples,'referenceFrameMatches':matched,'referenceInputRomSha256':rows[0]['rom']['sha256'],'before':before,'after':after,'safeSpawn':xy,'ramSha256':hashlib.sha256(ram.read_bytes()).hexdigest(),'additionalActions':actions,'fixture':'porch-completed.ram.fixture','physicalTested':False}

# Exercise menus with ordinary presses from the genuine continued porch.
# A is neutral between each press; none of these actions writes emulator memory.
for index in [0,1,2]:
    press('start');press('down');press('a')
    for _ in range(index):press('down')
    press('a')
    for _ in range(2 if index==1 else 1):press('a')
assert all(values()[n]==1 for n in ['AUDIO_OFF','REDUCED_SCARES','FAST_TEXT'])
p.screen.image.save(qa/'comfort-settings-on.png')
step(['up'],24);step([],20)
press('a')
for _ in range(4):press('a')
press('a');press('down');press('a');press('a')
assert values()['ACTIVE_COMPANION']==0
assert values()['P01']==values()['P02']==1
p.screen.image.save(qa/'moth-resting-at-camp.png')

# A second solve acknowledgement cannot remove progression.
# Save the changed options through the actual camp menu.
press('a')
for _ in range(4):press('a')
press('down');press('down');press('a');press('a');press('a')
for _ in range(2):press('a')
options_before=values();assert options_before['ACTIVE_COMPANION']==0
p.stop(save=True)
shutil.copy2(ram,qa/'porch-comfort-options.ram.fixture')
p=PyBoy(str(cart),window='null',sound_emulated=False,cgb=True)
p.set_emulation_speed(0);[p.tick(1,True) for _ in range(180)];held=set()
press('start')
press('down');press('a');step([],140)
options_after=values()
assert all(options_after[n]==1 for n in ['AUDIO_OFF','REDUCED_SCARES','FAST_TEXT','P01','P02'])
assert options_after['ACTIVE_COMPANION']==1 # loader deliberately defaults to recruited Moth
p.screen.image.save(qa/'continued-with-comfort-options.png')
report.update(comfortOptionsBefore=options_before,comfortOptionsAfter=options_after,
              companionRestTest=True,optionsColdbootTest=True)
(qa/'report.json').write_text(json.dumps(report,indent=2))
p.stop(save=True)
print(json.dumps({'qa':str(qa),'report':report},indent=2))
