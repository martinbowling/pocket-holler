"""Original PocketHoller production pixels, authored on native cell grids.

Run with Pillow. Writes only beside this file, never to the active native project.
No reference image, screenshot, or third-party art is read by this generator.
Background palette assignments match foliage/wood/glow/water slots 0/1/2/3.
"""
from pathlib import Path
from PIL import Image, ImageDraw
import hashlib, json, uuid

HERE = Path(__file__).resolve().parent
BG = ['071821', '306850', '86c06c', 'e0f8cf']
SP = ['65ff00', '071821', '86c06c', 'e0f8cf']
DISPLAY = [
    ['182838', '405840', '809858', 'D8E8B8'],
    ['202838', '705038', 'C09058', 'F0D8A0'],
    ['282038', 'A85830', 'F0B850', 'FFF0C0'],
    ['182838', '386870', '60A098', 'C0E0D0'],
]
NAMES = {
7:'Creek camp',8:'Mirror pool',9:'Reedbank',10:'Flooded causeway',
11:'Wheelhouse',12:'Creek light',13:'Ridge camp',14:'Bramble stairs',
15:'Thunder roost',16:'Relay yard',17:'Bell road',18:'Old noticehouse',
19:'Root threshold',20:'Echo hall',21:'Spring chamber',22:'Bell chamber',
23:'Dawn overlook',24:'Porch interior'}

TILES = {
'grass': ['22222222','22222222','22122222','22222222','22222222','22222212','22222222','22222222'],
'grass2':['22222222','22222222','22222222','22212222','22222222','22222222','22222222','22222222'],
'path': ['33333333','33333333','33233333','33333333','33333333','33333333','33333233','33333333'],
'path2':['33333333','33333333','33333333','33333333','33333333','33233333','33333333','33333333'],
'stone':['12222221','23333332','23323332','23333332','23333332','23333332','23333332','12222221'],
'stairs':['11111111','22222222','33333333','33333333','33333333','33333333','33333333','33333333'],
'plank':['12222222','12222222','12222222','12221222','12222222','12222222','12222222','11111111'],
'deckedge':['11111111','23333332','22222222','22222222','22212222','22222222','22222222','11111111'],
'rug': ['22222222','23233232','22322322','23233232','23233232','22322322','23233232','22222222'],
'leaf': ['00000000','01122110','11222211','12233221','12232221','11222211','01111110','00000000'],
'pine': ['00011000','00122100','01122110','11222211','00122100','01233210','12233221','00011000'],
'rock': ['00000000','01111110','12322221','12222211','12222111','12211111','01111110','00000000'],
'cliff':['01111110','12322221','12322211','12221111','01111110','00111100','00000000','00000000'],
'brick':['11111111','22212221','22212221','22212221','11111111','12221222','12221222','12221222'],
'fence':['22222222','10111101','10111101','10111101','00111100','10111101','10111101','22222222'],
'water':['11111111','12331111','11111111','11111221','11111111','11111111','11133111','11111111'],
'deep': ['00000000','01100000','00000000','00011000','00000000','00000000','01110000','00000000'],
'reed': ['00110000','00220010','00110020','00110010','00121010','00122110','11122111','11111111'],
'root': ['00111000','00122100','01221100','12210000','12211000','01221110','00122221','00011110'],
'bough':['11111111','12222221','11222211','01122110','00111000','00011000','00000000','00000000'],
'roof': ['00000000','12222221','01222210','22222222','00000000','12222221','01222210','22222222'],
'wall': ['33333333','33333333','22222222','33333333','33333333','22222222','33333333','33333333'],
'window':['11111111','13311331','13311331','13311331','11111111','13311331','13311331','11111111'],
'lamp': ['00111100','00122100','01111110','01333310','01233210','01333310','01111110','00011000'],
'socket':['22222222','22111122','21233212','21311312','21311312','21233212','22111122','22222222'],
'books':['12222221','13121331','13121331','13121331','13121331','13121331','11111111','22222222'],
'star': ['00000000','00030000','00131000','03333300','00131000','00030000','00000000','00000000'],
}

def image(rows, colors):
    im = Image.new('RGB', (len(rows[0]), len(rows)))
    for y,row in enumerate(rows):
        for x,c in enumerate(row): im.putpixel((x,y),tuple(bytes.fromhex(colors[int(c)])))
    return im

def uid(name): return str(uuid.uuid5(uuid.NAMESPACE_URL, 'PocketHoller/full-game/' + name))

def runs(values):
    # GB Studio hexadecimal byte-run codec: count and value are hexadecimal.
    # Kept explicit as one-cell runs; assets are small and unambiguous.
    return ''.join(f'{v:02x}!' for v in values)

def background(number):
    code=f'R{number:02d}'
    im=Image.new('RGB',(160,144)); slots=[0]*360; collisions=[0]*360
    floor='grass'; floor_slot=0
    if number in (10,11,18,24): floor='plank'; floor_slot=1
    if number in (12,14,15,16,20,21,22): floor='stone'; floor_slot=1
    if number==19: floor='path'; floor_slot=1
    def tile(x,y,key,slot=0,block=False):
        if 0<=x<20 and 0<=y<18:
            im.paste(image(TILES[key],BG),(x*8,y*8))
            slots[y*20+x]=slot;collisions[y*20+x]=15 if block else 0
    def rect(x,y,w,h,key,slot=0,block=False):
        for yy in range(y,y+h):
            for xx in range(x,x+w):tile(xx,yy,key,slot,block)
    rect(0,0,20,18,floor,floor_slot)
    # Scenic rim is deliberately separate from the navigable central ground.
    rim = 'leaf' if number<13 or number==23 else 'pine'
    if number in (18,20,21,22,24): rim='brick'
    if number==19:rim='root'
    rect(0,0,20,3,rim,0,True);rect(0,16,20,2,rim,0,True)
    rect(0,0,2,18,rim,0,True);rect(18,0,2,18,rim,0,True)
    # Spacious horizontal and vertical routes. Stone/plank floors remain floors.
    if floor=='grass':
        rect(2,10,16,4,'path',1)
        rect(8,3,4,13,'path',1)
        for y in range(3,16):
            for x in range(2,18):
                if not (8<=x<=11 or 10<=y<=13):
                    if (x*3+y+number)%7==0:tile(x,y,'grass2',0)
    if number==7:
        rect(2,0,5,2,'roof',1,True);rect(3,2,3,1,'plank',1,True)
        tile(6,2,'lamp',2,True)
        rect(12,16,6,2,'water',3,True)
        for x in (13,16):tile(x,16,'reed',3,True)
    elif number==8:
        rect(2,0,16,3,'deep',3,True)
        rect(0,3,2,7,'water',3,True);rect(18,3,2,7,'water',3,True)
        for x in (3,5,14,16):tile(x,2,'reed',3,True)
        # A silhouette only in inaccessible water. Reflection never suggests floor.
        d=ImageDraw.Draw(im)
        d.rectangle((35,5,39,12),fill='#071821');d.rectangle((33,12,41,15),fill='#306850')
        d.line((31,18,43,18),fill='#86c06c')
        rect(2,16,16,2,'reed',3,True)
    elif number==9:
        rect(2,0,16,2,'water',3,True)
        for x in range(2,18):tile(x,2,'reed',3,True)
        rect(0,3,2,7,'reed',3,True);rect(18,3,2,7,'reed',3,True)
        rect(2,16,16,2,'reed',3,True)
    elif number==10:
        rect(0,0,20,3,'water',3,True);rect(0,16,20,2,'water',3,True)
        rect(0,3,2,13,'water',3,True);rect(18,3,2,13,'water',3,True)
        # Broad wooden platform surrounded by real blocked water; all stations safe.
        rect(2,3,16,1,'deckedge',1);rect(2,15,16,1,'deckedge',1)
    elif number==11:
        rect(0,0,20,1,'roof',1,True);rect(2,1,16,2,'wall',1,True)
        for x in (3,4,14,15):tile(x,1,'window',2,True)
        rect(0,16,20,2,'water',3,True)
        d=ImageDraw.Draw(im)
        d.ellipse((111,1,133,23),fill='#071821',outline='#e0f8cf')
        d.ellipse((115,5,129,19),outline='#86c06c')
        d.line((112,12,132,12),fill='#e0f8cf');d.line((122,2,122,22),fill='#e0f8cf')
        for x in range(14,17):slots[1*20+x]=1;slots[2*20+x]=1
    elif number==12:
        rect(2,0,16,3,'brick',1,True);rect(2,16,16,2,'water',3,True)
        tile(5,1,'lamp',2,True);tile(14,1,'lamp',2,True)
        rect(0,3,2,7,'cliff',1,True);rect(18,3,2,7,'water',3,True)
    elif number==13:
        rect(2,0,16,2,'cliff',1,True)
        for x in (3,6,13,16):tile(x,2,'pine',0,True)
        tile(5,16,'lamp',2,True);tile(14,16,'lamp',2,True)
    elif number==14:
        rect(0,3,2,13,'bough',0,True);rect(18,3,2,13,'bough',0,True)
        for y in (4,8,12):rect(2,y,16,1,'stairs',1)
        rect(2,0,16,2,'cliff',1,True)
    elif number==15:
        rect(2,0,16,2,'cliff',1,True)
        for x in range(2,18):tile(x,2,'root',1,True)
        d=ImageDraw.Draw(im)
        d.arc((25,-9,60,22),0,180,fill='#e0f8cf',width=2)
        d.arc((105,-9,139,22),0,180,fill='#e0f8cf',width=2)
        for x in (3,6,13,16):tile(x,0,'star',3,True)
    elif number==16:
        rect(2,0,16,3,'fence',1,True)
        for x in (4,6,13,15):tile(x,1,'socket',2,True)
        rect(0,3,2,7,'brick',1,True);rect(18,3,2,7,'brick',1,True)
        rect(2,16,16,2,'cliff',1,True)
    elif number==17:
        rect(2,0,16,2,'pine',0,True);rect(2,16,16,2,'fence',1,True)
        tile(4,2,'lamp',2,True);tile(15,2,'lamp',2,True)
        rect(0,3,2,7,'root',1,True);rect(18,3,2,7,'root',1,True)
    elif number==18:
        rect(2,0,16,1,'roof',1,True);rect(2,1,16,2,'wall',1,True)
        for x in (2,3,4,5,14,15,16,17):tile(x,2,'books',1,True)
        for x in (4,5,14,15):tile(x,1,'window',3,True)
        rect(5,7,10,6,'rug',0)
    elif number==19:
        for x in range(2,18):tile(x,2,'root',1,True)
        for y in range(3,16):
            tile(0,y,'root',1,True);tile(19,y,'root',1,True)
        tile(4,1,'lamp',2,True);tile(15,1,'lamp',2,True)
        rect(2,16,16,2,'rock',1,True)
    elif number==20:
        rect(2,0,16,3,'brick',3,True)
        for x in (3,4,5,14,15,16):tile(x,1,'window',3,True)
        rect(0,3,2,7,'deep',3,True);rect(18,3,2,7,'deep',3,True)
        rect(2,16,16,2,'brick',3,True)
    elif number==21:
        rect(2,0,16,3,'water',3,True);rect(2,16,16,2,'water',3,True)
        rect(0,3,2,7,'water',3,True);rect(18,3,2,7,'water',3,True)
        for x in (3,6,13,16):tile(x,2,'rock',1,True)
    elif number==22:
        rect(2,0,16,3,'brick',1,True)
        for x in (3,6,13,16):tile(x,1,'lamp',2,True)
        rect(0,3,2,7,'root',1,True);rect(18,3,2,7,'root',1,True)
        # Large mounted bell on the upper rim; playable bell itself is an actor.
        d=ImageDraw.Draw(im)
        d.rectangle((107,0,140,2),fill='#071821')
        d.polygon([(116,3),(130,3),(131,14),(137,18),(137,21),(109,21),(109,18),(115,14)],fill='#071821')
        d.polygon([(117,4),(129,4),(129,14),(134,18),(112,18),(117,14)],fill='#e0f8cf')
        d.rectangle((121,20,125,23),fill='#86c06c')
        for y in range(3):
            for x in range(13,18):slots[y*20+x]=2
    elif number==23:
        rect(2,0,16,3,'cliff',1,True)
        # Clear dawn horizon above the trail, in blocked distant scenery.
        d=ImageDraw.Draw(im)
        d.rectangle((16,0,63,4),fill='#e0f8cf');d.rectangle((96,0,143,4),fill='#e0f8cf')
        d.ellipse((119,-5,134,10),fill='#86c06c')
        for x in range(12,18):slots[x]=2
        rect(2,16,16,2,'fence',1,True)
    elif number==24:
        rect(2,0,16,3,'wall',1,True)
        for x in (3,4,14,15):tile(x,1,'window',2,True)
        rect(5,7,10,6,'rug',1);rect(0,16,20,2,'books',1,True)
        tile(5,2,'lamp',2,True)
    # All four candidate exits have guaranteed two-tile depth and 32px width.
    rect(8,0,4,3,floor if floor!='grass' else 'path',floor_slot if floor!='grass' else 1)
    rect(8,16,4,2,floor if floor!='grass' else 'path',floor_slot if floor!='grass' else 1)
    rect(0,10,2,4,floor if floor!='grass' else 'path',floor_slot if floor!='grass' else 1)
    rect(18,10,2,4,floor if floor!='grass' else 'path',floor_slot if floor!='grass' else 1)
    assert all(collisions[y*20+x]==0 for y in range(3,16) for x in range(2,18))
    assert set(im.getdata())<=set(tuple(bytes.fromhex(c)) for c in BG)
    unique=len({im.crop((x*8,y*8,x*8+8,y*8+8)).tobytes() for y in range(18) for x in range(20)})
    assert unique<=200,(code,unique)
    im.save(HERE/'backgrounds'/f'{code.lower()}.png')
    res={'_resourceType':'background','id':uid(code),'name':code+' '+NAMES[number],
         'symbol':'bg_'+code.lower(),'tileColors':runs(slots),'filename':code.lower()+'.png',
         'width':20,'height':18,'imageWidth':160,'imageHeight':144,'autoColor':False}
    (HERE/'backgrounds'/f'{code.lower()}.png.gbsres').write_text(json.dumps(res,indent=2)+'\n')
    preview=Image.new('RGB',(160,144))
    shade={tuple(bytes.fromhex(c)):i for i,c in enumerate(BG)}
    for y in range(144):
        for x in range(160):
            preview.putpixel((x,y),tuple(bytes.fromhex(DISPLAY[slots[(y//8)*20+x//8]][shade[im.getpixel((x,y))]])))
    preview.save(HERE/'previews'/f'{code.lower()}-color.png')
    return {'code':code,'name':NAMES[number],'background':f'backgrounds/{code.lower()}.png',
            'uniqueTiles':unique,'slots':slots,'solid':collisions,
            'paletteSlots':['foliage','wood','glow','water'],
            'safeRectangleTiles':{'x':2,'y':3,'width':16,'height':13}}

SPRITES={
'turtle':[
'0000000000000000','0000001111000000','0000012222100000','0001122222211000',
'0012332332322100','0123232232322210','0122333322332210','0123232232322210',
'0122333322332210','0012222222221100','0011101111011100','0012102333012100',
'0001102313011000','0000002333000000','0000001111000000','0000000000000000'],
'thunderbird':[
'0000000010000000','0000000131000000','0000001321000000','0000013333100000',
'0000131313310000','0000013331100000','0111112321111100','0122222332222100',
'0012223332221000','0001223332210000','0000123332100000','0000012321000000',
'0000011111000000','0000010011000000','0000110011100000','0000000000000000'],
'wave':[
'0000000000000000','0000000000000000','0000000000000000','0000000000000000',
'0001110001110000','0013331013331000','0133333133333100','0011111011111000',
'0000000000000000','0001110001110000','0012221012221000','0122222122222100',
'0011111011111000','0000000000000000','0000000000000000','0000000000000000'],
'spark':[
'0000000000000000','0000000111100000','0000001333100000','0000013331000000',
'0000133310000000','0001333100000000','0013331111100000','0013333333100000',
'0001113331000000','0000013310000000','0000133100000000','0001331000000000',
'0013310000000000','0011100000000000','0000000000000000','0000000000000000'],
'bell':[
'0000001111000000','0000012332100000','0000011111100000','0000013331100000',
'0000133333110000','0000133333110000','0000133333110000','0001333333310000',
'0013333333331000','0013333333331000','0111111111111100','0122222222222100',
'0111111111111100','0000001221000000','0000001111000000','0000000000000000'],
'footprint':[
'0000000000000000','0000000110000000','0000001221000000','0000001221000000',
'0000001221000000','0000000110000000','0000000110000000','0000000000000000',
'0001100000000000','0012210000000000','0012210000000000','0012210000000000',
'0001100000000000','0001100000000000','0000000000000000','0000000000000000'],
'reflection':[
'0000000000000000','0000111111000000','0001122221100000','0001222222100000',
'0001232232100000','0001122221100000','0000111111000000','0000122221000000',
'0001222222100000','0001222222100000','0000122221000000','0000011110000000',
'0000000000000000','0000110011100000','0000000000000000','0001111000111000'],
}

def sprite(name,rows):
    assert len(rows)==16 and all(len(r)==16 for r in rows),(name,[len(r) for r in rows])
    frames=[]
    for frame in range(6):
        im=image(rows,SP);d=ImageDraw.Draw(im)
        if name=='turtle':
            if frame in (2,3):d.line((5,3,10,3),fill='#86c06c')
            if frame in (1,4):d.point((3,12),fill='#86c06c');d.point((9,12),fill='#86c06c')
        elif name=='thunderbird':
            if frame in (1,2,4,5):
                d.line((1,6,3,5),fill='#86c06c');d.line((12,5,14,6),fill='#86c06c')
                d.line((1,8,3,8),fill='#65ff00');d.line((12,8,14,8),fill='#65ff00')
            if frame==3:d.point((6,4),fill='#e0f8cf')
        elif name in ('wave','spark'):
            if frame%2:
                for y,row in enumerate(rows):
                    for x,c in enumerate(row):
                        if c=='3':im.putpixel((x,y),tuple(bytes.fromhex(SP[2])))
            if name=='spark' and frame in (2,5):
                d.point((12,3),fill='#e0f8cf');d.point((3,5),fill='#e0f8cf')
        elif name=='bell':
            if frame in (1,2):
                d.rectangle((6,13,9,14),fill='#65ff00');d.line((5,13,7,14),fill='#86c06c')
            if frame in (4,5):
                d.rectangle((6,13,9,14),fill='#65ff00');d.line((8,14,10,13),fill='#86c06c')
        elif name=='footprint':
            if frame in (2,3):
                for y,row in enumerate(rows):
                    for x,c in enumerate(row):
                        if c=='2':im.putpixel((x,y),tuple(bytes.fromhex(SP[3])))
        elif name=='reflection':
            if frame in (1,2,4,5):
                d.line((4,7,10,7),fill='#65ff00');d.line((3,10,11,10),fill='#65ff00')
        frames.append(im)
    sheet=Image.new('RGB',(96,16),'#65ff00')
    for n,im in enumerate(frames):sheet.paste(im,(n*16,0))
    assert set(sheet.getdata())<=set(tuple(bytes.fromhex(c)) for c in SP)
    sheet.save(HERE/'sprites'/f'{name}.png')
    animations=[]
    for a in range(8):
        native_frames=[]
        for n in range(6 if a==0 else 1):
            tiles=[]
            if a==0:
                for x in (0,8):
                    tiles.append({'id':uid(f'{name}/a{a}/f{n}/t{x}'),'x':x,'y':0,
                         'sliceX':n*16+x,'sliceY':0,'flipX':False,'flipY':False,'palette':0,
                         'paletteIndex':0,'objPalette':'OBP0','priority':False})
            native_frames.append({'id':uid(f'{name}/a{a}/f{n}'),'tiles':tiles})
        animations.append({'id':uid(f'{name}/a{a}'),'frames':native_frames})
    # Native metadata counts 8x16 object pairs. Conservative non-dedup total.
    res={'_resourceType':'sprite','id':uid('sprite/'+name),'name':name,'symbol':'sprite_'+name,
         'states':[{'id':uid('sprite/'+name+'/state'),'name':'','animationType':'fixed',
                    'flipLeft':False,'animations':animations}],
         'numTiles':12,'canvasOriginX':0,'canvasOriginY':0,'canvasWidth':16,'canvasHeight':16,
         'boundsX':0,'boundsY':-8,'boundsWidth':16,'boundsHeight':16,'animSpeed':15,
         'filename':name+'.png','width':96,'height':16,
         'checksum':hashlib.sha1((HERE/'sprites'/f'{name}.png').read_bytes()).hexdigest()}
    (HERE/'sprites'/f'{name}.png.gbsres').write_text(json.dumps(res,indent=2)+'\n')
    return {'name':name,'image':f'sprites/{name}.png','profile':'template/fixed six-frame animation',
            'frameSize':[16,16],'frames':6,'nativeNumTilesUpperBound':12,'resourceId':res['id']}

def main():
    for d in ('backgrounds','sprites','previews'): (HERE/d).mkdir(exist_ok=True)
    rooms=[background(i) for i in range(7,25)]
    sprites=[sprite(k,v) for k,v in SPRITES.items()]
    # A labelled native-scale montage and exact 2x nearest neighbour version.
    contact=Image.new('RGB',(4*176,5*172),'#101824');d=ImageDraw.Draw(contact)
    for n,r in enumerate(rooms):
        x=(n%4)*176+8;y=(n//4)*172+20
        contact.paste(Image.open(HERE/'previews'/f'{r["code"].lower()}-color.png'),(x,y))
        d.text((x,y-14),r['code']+' '+r['name'],fill='#fff0c0')
    contact.save(HERE/'previews/rooms-contact-1x.png')
    contact.resize((contact.width*2,contact.height*2),Image.Resampling.NEAREST).save(HERE/'previews/rooms-contact-2x.png')
    spr=Image.new('RGB',(224,7*28+12),'#182838');d=ImageDraw.Draw(spr)
    for i,s in enumerate(sprites):
        y=i*28+6;d.text((4,y+2),s['name'],fill='#fff0c0')
        original=Image.open(HERE/s['image']).convert('RGBA')
        px=original.load()
        for yy in range(16):
            for xx in range(96):
                if px[xx,yy][:3]==(101,255,0):px[xx,yy]=(0,0,0,0)
                else:
                    idx=SP.index(bytes(px[xx,yy][:3]).hex())
                    palette=DISPLAY[0] if s['name']=='turtle' else DISPLAY[2]
                    px[xx,yy]=tuple(bytes.fromhex(palette[{1:0,2:2,3:3}[idx]]))+(255,)
        spr.paste(original,(112,y),original)
    spr.resize((spr.width*3,spr.height*3),Image.Resampling.NEAREST).save(HERE/'previews/sprites-contact-3x.png')
    (HERE/'sprite-cells.json').write_text(json.dumps({'sourcePalette':SP,'sprites':SPRITES},indent=2)+'\n')
    manifest={'provenance':'Original explicitly authored native pixels; no raster sampling or imported game art.',
              'status':'Standalone proposed assets; not yet an emulator-verified scene.',
              'backgroundSourcePalette':BG,'spriteSourcePalette':SP,'rooms':rooms,'sprites':sprites,
              'limits':{'backgroundUniqueTiles':200,'uiSlotReserved':7},
              'candidateExits':{'topBottom':{'x':8,'width':4},'leftRight':{'y':10,'height':4}}}
    (HERE/'art-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({'rooms':len(rooms),'maximumUniqueBackgroundTiles':max(r['uniqueTiles'] for r in rooms),
                      'sprites':len(sprites),'safeFloorChecked':True,'sourceColorsChecked':True}))

if __name__=='__main__':main()
