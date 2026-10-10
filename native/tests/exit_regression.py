"""Check remaining reverse exits with ordinary inputs and private battery RAM."""
from pathlib import Path
import hashlib,json,re,shutil,tempfile
from pyboy import PyBoy
root=Path(__file__).resolve().parents[1]
qa=Path(tempfile.mkdtemp(prefix='exit-qa-',dir=root/'evidence'))
rom=root/'dist/PocketHoller-opening.gbc';cart=qa/rom.name;shutil.copy2(rom,cart)
shutil.copy2(root/'tests/fixtures/porch-completed.ram.fixture',Path(str(cart)+'.ram'))
symbols=(root/'dist/PocketHoller-opening.gbc.debug/symbols.noi').read_text()
base=int(re.search(r'DEF _actors 0x([0-9A-Fa-f]+)',symbols)[1],16)
glob=(root/'dist/PocketHoller-opening.gbc.debug/globals.i').read_text()
memory=int(re.search(r'DEF _script_memory 0x([0-9A-Fa-f]+)',symbols)[1],16)
variables={n:int(re.search(r'VAR_'+n+r'\s*=\s*(\d+)',glob)[1]) for n in ['CURRENT_ROOM','P01','P02']}
p=PyBoy(str(cart),window='null',sound_emulated=False,cgb=True);p.set_emulation_speed(0)
held=set();actions=[];checks=[]
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
    a=memory+2*variables[n];return p.memory[a]+256*p.memory[a+1]
def check(name,room):
    xy=[(p.memory[base+i]+256*p.memory[base+i+1])/256 for i in [1,3]]
    assert value('CURRENT_ROOM')==room,(name,value('CURRENT_ROOM'),xy)
    assert value('P01')==value('P02')==1
    p.screen.image.save(qa/(name+'.png'));checks.append({'exit':name,'room':room,'position':xy})
step([],180)
press('start')
press('down');press('a');step([],140);check('continue',1)
step(['down'],32);step([],110);check('porch-to-lane',2)
step(['up'],24);step([],110);check('lane-to-porch',1)
step(['down'],16);step([],110);check('porch-to-lane-again',2)
step(['down'],104);step([],110);check('lane-to-green',4)
step(['up'],24);step([],110);check('green-to-lane',2)
step(['down'],16);step([],110);check('lane-to-green-again',4)
step(['right'],32);step([],20);step(['down'],64);step([],20)
step(['right'],48);step([],110);check('green-to-boundary',6)
step(['left'],24);step([],110);check('boundary-to-green',4)
report={'passed':True,'romSha256':hashlib.sha256(rom.read_bytes()).hexdigest(),'startingState':'Copy of paired porch-completed RAM; cold boot Continue','checks':checks,'actions':actions,'memoryWrites':False}
(qa/'report.json').write_text(json.dumps(report,indent=2));p.stop(save=False)
print(json.dumps({'qa':str(qa),'checks':checks}))
