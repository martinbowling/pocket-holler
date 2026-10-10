"""Native 16x16 reconstructions of the owner's Marty/Roam concept direction.
Explicit editable cell rows; concept sheet itself is never included or sampled.
Palette: 0 transparent, 1 dark brown hair/ink, 2 jacket, 3 cream face/hands.
"""
from pathlib import Path
from PIL import Image,ImageDraw
import json
ROOT=Path(__file__).resolve().parents[2]
SOURCE=['65ff00','071821','86c06c','e0f8cf']
ROAM=[
'0000000000000000','0000010110000000','0000111111000000','0001111111100000',
'0001133311100000','0001313313100000','0001333333100000','0000133131000000',
'0000122221000000','0001321123100000','0001322223100000','0000122221000000',
'0000111111000000','0000110011000000','0000110011000000','0000000000000000']
MARTY=[
'0000001110000000','0000011111000000','0000111111100000','0001133331100000',
'0001311313100000','0001311113100000','0000133331000000','0000113311000000',
'0001221122100000','0013221122310000','0013221122310000','0001221122100000',
'0000111111000000','0000110011000000','0000110011000000','0001110011100000']
MOTH=[
'0000000000000000','0000010000100000','0000001001000000','0012100110021000',
'0123211331123210','0122321331322210','0012221331222100','0001211331121000',
'0000011331100000','0001211331121000','0012321331232100','0012210110122100',
'0001100110011000','0000000000000000','0000000000000000','0000000000000000']
def image(rows):
    assert len(rows)==16 and all(len(r)==16 for r in rows)
    im=Image.new('RGB',(16,16))
    for y,row in enumerate(rows):
        for x,c in enumerate(row):im.putpixel((x,y),tuple(bytes.fromhex(SOURCE[int(c)])))
    return im
def directions(rows,is_marty):
    front=image(rows);back=front.copy();d=ImageDraw.Draw(back)
    # Back keeps the original silhouette, with dark hair and a outlined pack.
    d.rectangle((5,3,10,7),fill=tuple(bytes.fromhex(SOURCE[1])))
    d.rectangle((6,9,9,11),fill=tuple(bytes.fromhex(SOURCE[1])))
    d.point((8,10),fill=tuple(bytes.fromhex(SOURCE[3])))
    side=front.copy();d=ImageDraw.Draw(side)
    d.rectangle((4,4,7,6),fill=tuple(bytes.fromhex(SOURCE[1])))
    d.point((10,5),fill=tuple(bytes.fromhex(SOURCE[1])))
    frames=[]
    for base in [front,back,side]:
        frames.append(base)
        step=base.copy();d=ImageDraw.Draw(step)
        d.rectangle((4,14,6,15),fill=tuple(bytes.fromhex(SOURCE[0])))
        d.rectangle((5,14,7,15 if is_marty else 14),fill=tuple(bytes.fromhex(SOURCE[1])))
        d.rectangle((8,14,10,15),fill=tuple(bytes.fromhex(SOURCE[0])))
        d.rectangle((9,13 if not is_marty else 14,11,14 if not is_marty else 15),fill=tuple(bytes.fromhex(SOURCE[1])))
        frames.append(step)
    sheet=Image.new('RGB',(96,16),tuple(bytes.fromhex(SOURCE[0])))
    for i,f in enumerate(frames):sheet.paste(f,(16*i,0))
    return sheet
for name,rows in [('roam-v2',ROAM),('marty-v2',MARTY)]:directions(rows,name.startswith('marty')).save(ROOT/'assets/sprites'/f'{name}.png')
image(MOTH).save(ROOT/'assets/sprites/moth-v2.png')
(ROOT/'art/source/characters-v2-cells.json').write_text(json.dumps({'roam':ROAM,'marty':MARTY,'moth':MOTH,'sourcePalette':SOURCE,'nativeSize':[16,16],'method':'Explicit native cell reconstruction from concept direction; no raster shrink'},indent=2))
print('Authored Marty, Roam and Moth v2 native sprites')
