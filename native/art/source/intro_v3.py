"""PocketHoller title: hand-authored native pixels and 8x8 palette cells.
No raster resampling. Typography, silhouettes and landscape remain editable.
Source PNG uses the standard four GB Studio shades; palette map is separate.
"""
from pathlib import Path
from PIL import Image, ImageDraw
import json, random
ROOT=Path(__file__).resolve().parents[2]
im=Image.new('L',(160,144),3);d=ImageDraw.Draw(im)
slots=[[0]*20 for _ in range(18)]
PAL=[['D8C8A8','788098','384058','182030'],
     ['F8D098','D89850','986038','182030'],
     ['B0B098','788878','405858','182030'],
     ['A0A870','607048','304838','182030'],
     ['F8D098','C06830','605048','182030'],
     ['F8D098','789058','485840','182030'],
     ['F8E0A0','E8A850','987040','182030']]
FONT={
'A':['01110','10001','10001','11111','10001','10001','10001'],
'B':['11110','10001','10001','11110','10001','10001','11110'],
'C':['01111','10000','10000','10000','10000','10000','01111'],
'D':['11110','10001','10001','10001','10001','10001','11110'],
'E':['11111','10000','10000','11110','10000','10000','11111'],
'F':['11111','10000','10000','11110','10000','10000','10000'],
'H':['10001','10001','10001','11111','10001','10001','10001'],
'I':['111','010','010','010','010','010','111'],
'K':['10001','10010','10100','11000','10100','10010','10001'],
'L':['10000','10000','10000','10000','10000','10000','11111'],
'M':['10001','11011','10101','10101','10001','10001','10001'],
'N':['10001','11001','11001','10101','10011','10011','10001'],
'O':['01110','10001','10001','10001','10001','10001','01110'],
'P':['11110','10001','10001','11110','10000','10000','10000'],
'R':['11110','10001','10001','11110','10100','10010','10001'],
'S':['01111','10000','10000','01110','00001','00001','11110'],
'T':['11111','00100','00100','00100','00100','00100','00100'],
'U':['10001','10001','10001','10001','10001','10001','01110'],
'W':['10001','10001','10001','10101','10101','11011','10001'],
'Y':['10001','10001','01010','00100','00100','00100','00100'],
' ':['000']*7}
def text(s,y,scale=1,color=0,x=None,shadow=False):
    w=sum((len(FONT[c][0])+1)*scale for c in s)-scale
    x=(160-w)//2 if x is None else x
    for c in s:
        for yy,row in enumerate(FONT[c]):
            for xx,v in enumerate(row):
                if v=='1':
                    box=(x+xx*scale,y+yy*scale,x+(xx+1)*scale-1,y+(yy+1)*scale-1)
                    if shadow:d.rectangle(tuple(q+1 for q in box),fill=2)
                    d.rectangle(box,fill=color if yy<4 else min(color+1,2))
        x+=(len(FONT[c][0])+1)*scale
def region(x0,y0,x1,y1,slot):
    for y in range(y0,y1):
        for x in range(x0,x1):slots[y][x]=slot
def pine(x,y,h,shade):
    d.line((x,y,x,y+h),fill=shade,width=2)
    for k in range(3):
        top=y+k*h//5; half=(k+2)*h//8
        d.polygon([(x,top),(x-half,top+h//2),(x+half,top+h//2)],fill=shade)
# Stars, crescent and deep overlapping ridges.
for x,y in [(12,42),(29,38),(52,44),(101,41),(146,38),(114,51),(6,60)]:d.point((x,y),fill=1)
d.ellipse((129,42,144,57),fill=0);d.ellipse((124,38,139,54),fill=3)
d.polygon([(0,77),(0,70),(20,53),(46,68),(73,48),(110,69),(135,60),(160,71),(160,105)],fill=2)
d.line([(1,71),(20,55),(45,70),(73,50),(111,71)],fill=1)
region(0,8,20,11,2)
d.polygon([(0,89),(20,73),(52,86),(83,70),(121,84),(159,75),(160,144),(0,144)],fill=2)
for x,y,h in [(5,60,30),(19,67,21),(145,62,28),(159,53,41),(32,80,15),(127,80,14)]:pine(x,y,h,3)
region(0,11,20,16,3)
# The lit windows of the holler, with steep cottage roofs.
for x,y in [(22,78),(121,77)]:
    d.rectangle((x,y,x+14,y+11),fill=3)
    d.polygon([(x-2,y),(x+7,y-7),(x+17,y)],fill=3)
    d.line((x-2,y,x+7,y-7,x+17,y),fill=1)
    d.rectangle((x+3,y+3,x+5,y+6),fill=0);d.rectangle((x+9,y+3,x+11,y+6),fill=0)
    region(x//8,(y-8)//8,(x+18+7)//8,(y+12+7)//8,6)
# Winding trail and a low fence. Sparse pixels give texture without noise.
d.polygon([(76,79),(82,79),(76,92),(91,107),(104,127),(60,127),(65,111),(68,96)],fill=1)
d.line([(76,84),(72,96),(76,104),(74,115),(69,123)],fill=0)
d.line((0,108,36,111),fill=1);d.line((0,114,36,117),fill=1)
for x in [6,22,35]:d.rectangle((x,104,x+2,121),fill=1)
rng=random.Random(17)
for _ in range(48):
    x=rng.randrange(160);y=rng.randrange(99,126)
    if x<43 or x>118:d.line((x,y,x+1,y-2),fill=1)
# Lantern Moth floats above the pair. Larger explicit cells, not an illustration shrink.
cells=json.loads((ROOT/'art/source/characters-v2-cells.json').read_text())
def person(rows,x,y):
    for yy,row in enumerate(rows):
        for xx,c in enumerate(row):
            if c!='0':
                shade={'1':3,'2':1,'3':0}[c]
                d.rectangle((x+xx*2,y+yy*2,x+xx*2+1,y+yy*2+1),fill=shade)
# Keep the character palette boundaries exactly on tile cells.
region(6,11,10,15,4);region(11,11,15,15,5)
person(cells['marty'],48,88);person(cells['roam'],88,88)
# Warm moth and its hanging light form the central emblem.
d.ellipse((66,57,94,83),fill=2);d.ellipse((70,60,90,79),fill=1)
for yy,row in enumerate(cells['moth']):
    for xx,c in enumerate(row):
        if c!='0':d.point((72+xx,63+yy),fill={'1':3,'2':1,'3':0}[c])
region(8,7,12,10,6)
# Lettering and framing have dedicated, warm palette cells.
region(0,0,20,4,1)
text('POCKETHOLLER',10,2,0,shadow=True)
d.line((15,5,62,5),fill=2);d.line((97,5,144,5),fill=2)
d.polygon([(77,3),(80,0),(83,3),(80,6)],fill=0)
text('AFTER SUNDOWN',31,color=0)
d.line((13,124,147,124),fill=2)
region(0,15,20,18,1)
text('MARTY',126,x=46);text('ROAM',126,x=94)
text('PRESS START',136)
# Native shade PNG plus a human-readable preview from the same palette cells.
SOURCE=['e0f8cf','86c06c','306850','071821']
native=Image.new('RGB',im.size);preview=Image.new('RGB',im.size)
for y in range(144):
    for x in range(160):
        idx=im.getpixel((x,y))
        native.putpixel((x,y),tuple(bytes.fromhex(SOURCE[idx])))
        preview.putpixel((x,y),tuple(bytes.fromhex(PAL[slots[y//8][x//8]][idx])))
native.save(ROOT/'assets/backgrounds/title-v3.png')
preview.save(ROOT/'art/title-v3-preview.png')
(ROOT/'art/source/title-v3-palettes.json').write_text(json.dumps({'paletteColors':PAL,'tileSlots':slots,'sourceColors':SOURCE,'dimensions':[160,144],'method':'Hand-authored native cells, no image resizing'},indent=2))
tiles={bytes(im.crop((x,y,x+8,y+8)).getdata()) for y in range(0,144,8) for x in range(0,160,8)}
print(json.dumps({'uniqueTiles':len(tiles),'source':'assets/backgrounds/title-v3.png'}))
