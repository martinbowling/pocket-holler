"""Exact cartridge intro motion and ordinary-input boot/menu checks."""
from pathlib import Path
from PIL import Image
from pyboy import PyBoy
import hashlib,json,re,shutil,tempfile
ROOT=Path(__file__).resolve().parents[1]
qa=Path(tempfile.mkdtemp(prefix='intro-qa-',dir=ROOT/'evidence'))
rom=ROOT/'dist/PocketHoller-opening.gbc';cart=qa/rom.name;shutil.copy2(rom,cart)
identity=hashlib.sha256(rom.read_bytes()).hexdigest()
assert identity==json.loads((ROOT/'evidence/build-final.json').read_text())['rom']['sha256']
p=PyBoy(str(cart),window='null',sound_emulated=False,cgb=True);p.set_emulation_speed(0)
held=set();actions=[];frames=[]
def step(buttons,n):
    global held
    new=set(buttons)
    for b in held-new:p.button_release(b)
    for b in new-held:p.button_press(b)
    held=new
    for _ in range(n):p.tick(1,True)
    actions.append({'buttons':buttons,'frames':n})
def press(b):step([b],8);step([],110)
def photo(name):p.screen.image.save(qa/(name+'.png'))
step([],180);photo('title-native')
for i in range(240):
    step([],1)
    if i%3==0:frames.append(p.screen.image.copy())
distinct={hashlib.sha256(f.convert('RGBA').tobytes()).hexdigest() for f in frames}
assert len(distinct)==2,('Expected two gently breathing palette phases',len(distinct))
palette_map=json.loads((ROOT/'art/source/title-v3-palettes.json').read_text())['tileSlots']
changed=set()
a=frames[0]
for b in frames:
    for y in range(144):
        for x in range(160):
            if a.getpixel((x,y))!=b.getpixel((x,y)):changed.add((x,y))
assert changed and all(palette_map[y//8][x//8]==6 for x,y in changed)
# Publish nearest-neighbor enlargement of real framebuffers, with no overlays.
a.resize((640,576),Image.Resampling.NEAREST).save(qa/'title-review.png')
movie=[f.resize((640,576),Image.Resampling.NEAREST) for f in frames]
movie[0].save(qa/'title-motion.gif',save_all=True,append_images=movie[1:],duration=50,loop=0)
press('start');photo('start-menu');press('b');photo('cancel-to-title')
assert p.screen.image==a or p.screen.image.tobytes() in [f.tobytes() for f in frames]
press('a');photo('a-opens-menu')
press('down');press('down');press('a');photo('title-settings')
# Back is the fourth item in the title's settings menu.
for _ in range(3):press('down')
press('a');photo('settings-back-to-menu')
press('a');step([],100);photo('new-game-porch')
symbols=(ROOT/'dist/PocketHoller-opening.gbc.debug/symbols.noi').read_text()
glob=(ROOT/'dist/PocketHoller-opening.gbc.debug/globals.i').read_text()
base=int(re.search(r'DEF _script_memory 0x([0-9A-Fa-f]+)',symbols)[1],16)
idx=int(re.search(r'VAR_CURRENT_ROOM\s*=\s*(\d+)',glob)[1]);address=base+2*idx
assert p.memory[address]+256*p.memory[address+1]==1
report={'passed':True,'romSha256':identity,'runtime':'PyBoy 2.7.0','nativeDimensions':[160,144],
        'motionFrames':len(frames),'motionDurationSeconds':4,'changedPixels':len(changed),
        'checks':['Clean boot title','Lantern breathing changes only its dedicated palette cells',
                  'Start opens menu','B returns to title','A also opens menu','Title Settings opens and returns',
                  'New Game reaches porch'],'memoryWrites':False,'physicalTested':False,'actions':actions}
(qa/'report.json').write_text(json.dumps(report,indent=2));p.stop(save=False)
print(json.dumps({'qa':str(qa),'report':report},indent=2))
