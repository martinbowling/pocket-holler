"""Ordinary-input character switch, movement, save/Continue and switch-back QA."""
from pathlib import Path
import json,hashlib,shutil,re,tempfile
from pyboy import PyBoy
ROOT=Path(__file__).resolve().parents[1]
source=ROOT/'tests/fixtures'
qa=Path(tempfile.mkdtemp(prefix='character-qa-',dir=ROOT/'evidence'))
rom=ROOT/'dist/PocketHoller-opening.gbc';cart=qa/rom.name;shutil.copy2(rom,cart)
shutil.copy2(source/'porch-completed.ram.fixture',Path(str(cart)+'.ram'))
symbols=(ROOT/'dist/PocketHoller-opening.gbc.debug/symbols.noi').read_text();glob=(ROOT/'dist/PocketHoller-opening.gbc.debug/globals.i').read_text()
base=int(re.search(r'DEF _script_memory 0x([0-9A-Fa-f]+)',symbols)[1],16)
var={n:int(re.search(r'VAR_'+n+r'\s*=\s*(\d+)',glob)[1]) for n in ['PLAYER_CHARACTER','CURRENT_ROOM','P01','P02']}
actions=[];held=set()
def boot():
    global p,held
    p=PyBoy(str(cart),window='null',sound_emulated=False,cgb=True);p.set_emulation_speed(0);held=set();step([],180)
def step(buttons,n):
    global held
    new=set(buttons)
    for b in held-new:p.button_release(b)
    for b in new-held:p.button_press(b)
    held=new
    for _ in range(n):p.tick(1,True)
    actions.append({'buttons':buttons,'frames':n})
def press(b):step([b],8);step([],110)
def value(n):
    i=base+2*var[n];return p.memory[i]+256*p.memory[i+1]
def photo(name):p.screen.image.save(qa/(name+'.png'))
def continue_game():
    press('start')
    press('down');press('a');step([],140)
boot();continue_game();assert value('PLAYER_CHARACTER')==0
step(['up'],24);step([],20);press('a')
for _ in range(4):press('a')
for _ in range(4):press('down')
photo('character-menu');press('a');photo('roam-marty-choice')
press('down');press('a');press('a')
assert value('PLAYER_CHARACTER')==1;photo('marty-playable-roam-at-porch')
step(['down'],56);step([],110)
assert value('CURRENT_ROOM')==2 and value('PLAYER_CHARACTER')==1
step(['right'],16);step([],20);step(['down'],8);step([],20);photo('marty-walking-town')
# Return through the native pause flow.
press('start');press('down');press('down');press('a');press('a');press('a');press('a');step([],140)
assert value('CURRENT_ROOM')==1;step(['up'],24);step([],20)
press('a');press('a') # Roam's one-page porch guide, then camp menu.
press('down');press('down');press('a');press('a');press('a')
for _ in range(2):press('a')
assert value('PLAYER_CHARACTER')==1;photo('marty-save')
p.stop(save=True);shutil.copy2(Path(str(cart)+'.ram'),qa/'marty-completed.ram.fixture')
boot();continue_game();assert value('PLAYER_CHARACTER')==1 and value('P01')==value('P02')==1
photo('continued-as-marty');step(['up'],24);step([],20);press('a');press('a')
for _ in range(4):press('down')
press('a');press('a');press('a')
assert value('PLAYER_CHARACTER')==0;step(['down'],8);step([],20);photo('switched-back-to-roam')
report={'passed':True,'romSha256':hashlib.sha256(rom.read_bytes()).hexdigest(),'startingCondition':'Paired completed-porch fixture, fresh boot Continue','checks':['Roam to Marty via Character menu','Marty walks and crosses to town','Return to Camp as Marty','Roam porch guide offers Save','Cold boot Continue retains Marty and P01/P02','Switch back to Roam restores Marty guide'],'actions':actions,'memoryWrites':False}
(qa/'report.json').write_text(json.dumps(report,indent=2));p.stop(save=False)
print(json.dumps({'qa':str(qa),'report':report},indent=2))
