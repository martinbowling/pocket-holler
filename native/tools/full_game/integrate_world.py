"""Integrate authorized original full-game room resources, R07--R24.

This source reads the selected native templates and compatible resource proposals.
The parent has successfully selected this project through ModRetro. No build,
emulator reset, old room, trigger, global variable or setting is owned here.
Reapply generated art with --assets-root after deliberate source-art regeneration.
"""
from pathlib import Path
import argparse, copy, hashlib, json, shutil
from PIL import Image
from full_game_support import Helpers, SOURCE, uid, EDGES, ROOM_NAMES
from prepare_integration import gather

HERE=Path(__file__).resolve().parent
DEFAULT_ASSETS=HERE/'assets'
PALETTE_NAMES=['roam_green','moth_orange','marty_orange','roam_green','foliage','glow','water','wood']

def read(path):return json.loads(path.read_text())
def write(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,indent=2)+'\n')
def compress(values):
    out=[];i=0
    while i<len(values):
        j=i+1
        while j<len(values) and values[j]==values[i]:j+=1
        out.append(f'{values[i]:02x}'+('!' if j-i==1 else f'{j-i:x}+'));i=j
    return ''.join(out)

def scoped_events(value,resource,path=''):
    if isinstance(value,dict):
        if 'command' in value:value['id']=uid('native/'+resource+'/'+path)
        for k,v in value.items():
            if k!='id':scoped_events(v,resource,path+'/'+k)
    elif isinstance(value,list):
        for i,v in enumerate(value):scoped_events(v,resource,path+'/'+str(i))

def native_write(path,value):
    value=json.loads(json.dumps(value))
    scoped_events(value,path.relative_to(SOURCE).as_posix())
    write(path,value)

def sprite_variant(source,name,index):
    data=read(source)
    original_id=data['id'];data['id']=uid('sprite-variant-'+name)
    data['name']=name;data['symbol']='sprite_'+name.replace('-','_')
    data['filename']=name+'.png'
    def rekey(obj,route=''):
        if isinstance(obj,dict):
            for k,v in obj.items():
                if k=='id' and route:obj[k]=uid('sprite-variant-'+name+'/'+route)
                elif k!='id':rekey(v,route+'/'+k)
            if 'sliceX' in obj:obj['paletteIndex']=index
        elif isinstance(obj,list):
            for i,v in enumerate(obj):rekey(v,route+'/'+str(i))
    rekey(data)
    original_png=source.parent/(read(source)['filename'])
    png=SOURCE/'assets/sprites'/data['filename']
    shutil.copyfile(original_png,png)
    data['checksum']=hashlib.sha1(png.read_bytes()).hexdigest()
    write(SOURCE/'assets/sprites'/(data['filename']+'.gbsres'),data)
    return {'id':data['id'],'filename':data['filename'],'paletteIndex':index,'sourceId':original_id}

def install_sprites(assets):
    for p in (assets/'sprites').glob('*'):
        if p.is_file():shutil.copyfile(p,SOURCE/'assets/sprites'/p.name)
    # Main companion sheets reserve the same dynamic object palette1.
    for name in ['moth-v2','turtle','thunderbird']:
        path=SOURCE/'assets/sprites'/f'{name}.png.gbsres';data=read(path)
        for state in data['states']:
            for animation in state['animations']:
                for frame in animation['frames']:
                    for tile in frame['tiles']:tile['paletteIndex']=1
        write(path,data)
    roles={}
    for name,index in [('sign',7),('vane',7),('windscreen',7),('lantern',5),('ray',5),
                       ('wave',6),('spark',5),('bell',5),('reflection',6),('footprint',7)]:
        roles[name]=sprite_variant(SOURCE/'assets/sprites'/f'{name}.png.gbsres',name+'-full',index)
    roles['turtle']=sprite_variant(SOURCE/'assets/sprites/turtle.png.gbsres','turtle-rest-full',4)
    roles['thunderbird']=sprite_variant(SOURCE/'assets/sprites/thunderbird.png.gbsres','thunderbird-roost-full',5)
    roles['martyGuide']=sprite_variant(SOURCE/'assets/sprites/marty-v2.png.gbsres','marty-guide-full',2)
    roles['roamGuide']=sprite_variant(SOURCE/'assets/sprites/roam-v2.png.gbsres','roam-guide-full',3)
    roles['juneGuide']=sprite_variant(SOURCE/'assets/sprites/june.png.gbsres','june-guide-full',2)
    roles['follower']={'id':read(SOURCE/'assets/sprites/moth-v2.png.gbsres')['id'],'paletteIndex':1}
    roles['followerTurtle']={'id':read(SOURCE/'assets/sprites/turtle.png.gbsres')['id'],'paletteIndex':1}
    roles['followerThunderbird']={'id':read(SOURCE/'assets/sprites/thunderbird.png.gbsres')['id'],'paletteIndex':1}
    write(HERE/'sprite-role-map.json',roles)
    return roles

def close_unused(code,room,asset_path):
    data=copy.deepcopy(room)
    im=Image.open(asset_path).convert('RGB');slots=data['slots'];solid=data['solid']
    used=set()
    for a,ae,b,be,_ in EDGES:
        if a==code:used.add(ae)
        if b==code:used.add(be)
    def replace(x,y,sx,sy):
        im.paste(im.crop((sx*8,sy*8,sx*8+8,sy*8+8)),(x*8,y*8))
        slots[y*20+x]=slots[sy*20+sx];solid[y*20+x]=15
    for edge in ['north','south','west','east']:
        if edge in used:continue
        if edge in ('north','south'):
            for y in (range(3) if edge=='north' else range(16,18)):
                for x in range(8,12):replace(x,y,6,y)
        else:
            for y in range(10,14):
                for x in (range(2) if edge=='west' else range(18,20)):replace(x,y,x,8)
    # The actor rectangle remains genuinely walkable; only unused rim openings close.
    assert all(solid[y*20+x]==0 for y in range(3,16) for x in range(2,18))
    for edge in used&{'north','south','west','east'}:
        cells={'north':[(x,y) for x in range(8,12) for y in range(3)],
               'south':[(x,y) for x in range(8,12) for y in range(16,18)],
               'west':[(x,y) for x in range(2) for y in range(10,14)],
               'east':[(x,y) for x in range(18,20) for y in range(10,14)]}[edge]
        assert all(solid[y*20+x]==0 for x,y in cells)
    output=SOURCE/'assets/backgrounds'/asset_path.name;im.save(output)
    sidecar=read(asset_path.with_name(asset_path.name+'.gbsres'))
    sidecar['tileColors']=compress(slots);write(output.with_name(output.name+'.gbsres'),sidecar)
    data['openEdges']=sorted(used&{'north','south','west','east'})
    data['uniqueTiles']=len({im.crop((x*8,y*8,x*8+8,y*8+8)).tobytes() for y in range(18) for x in range(20)})
    assert data['uniqueTiles']<=200
    return data,sidecar['id']

def preserve_sources(assets):
    destination=SOURCE/'art/source/full_game';destination.mkdir(parents=True,exist_ok=True)
    # Retain original generators from this agent's standalone art workspace.
    # This never reads or selects the previously denied relocated native project.
    for name in ['generate_art.py','generate_music.py','validate_uge.cjs','sprite-cells.json',
                 'art-manifest.json','music-manifest.json','validation-report.json']:
        path=assets/name
        if not path.is_file():path=SOURCE.parent/'full-game-staging/art'/name
        if path.is_file() and path.resolve()!=(destination/name).resolve():shutil.copyfile(path,destination/name)
    (destination/'README.md').write_text('''# Original full-game artwork and music

The original generators, explicit cell data, compositions and provenance are
preserved here. They create editable output beside themselves. To regenerate,
run both Python generators, then run native/tools/full_game/integrate_world.py
with --assets-root pointing here, after selecting the intended native project.
The integrator closes unused perimeter exits and applies native sprite palettes
to the actual registered resource variants. It preserves project/version IDs.

Source projections and composition preview WAVs are not emulator evidence.
Native rooms, actors, palettes and original music have been authored; build,
complete cartridge playthrough, save recovery and physical QA remain separate.
No reference photo or third-party song data is copied into these originals.
No blanket game or character-art license is chosen here.
''')

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--assets-root',type=Path,default=DEFAULT_ASSETS)
    parser.add_argument('--geometry-only',action='store_true');args=parser.parse_args();assets=args.assets_root.resolve()
    h,rooms,camps=gather();art=read(assets/'art-manifest.json')
    art_by_code={r['code']:r for r in art['rooms']}
    roles=install_sprites(assets)
    for p in (assets/'music').glob('*.uge*'):
        if p.is_file():shutil.copyfile(p,SOURCE/'assets/music'/p.name)
    preserve_sources(assets)
    actor_template=read(SOURCE/'project/scenes/r06_boundary_gate/actors/inscription.gbsres')
    scene_template=read(SOURCE/'project/scenes/r02_town_lane/scene.gbsres')
    palette_ids=[read(SOURCE/'project/palettes'/f'{name}.gbsres')['id'] for name in PALETTE_NAMES]
    bg_palette_ids=[read(SOURCE/'project/palettes'/f'{name}.gbsres')['id'] for name in ['foliage','wood','glow','water']]
    integrated=[]
    for number in range(7,25):
        code=f'R{number:02d}';spec=copy.deepcopy(rooms[code])
        if code=='R20':
            for target in spec['abilityTargets']:
                target['action']=[h.cond('P12',1,[h.text('The bell has called everyone home. Only ordinary letters remain in morning light.')],target['action'])]
        artroom,bgid=close_unused(code,art_by_code[code],assets/art_by_code[code]['background'])
        slug=code.lower()+'_'+ROOM_NAMES[number-1].lower().replace(' ','_')
        scene_dir=SOURCE/'project/scenes'/slug
        scene_dir.mkdir(exist_ok=True)
        actual_actors=[]
        for index,item in enumerate(spec['actors']):
            calm={('R08','pool_bank'):'Morning water mirrors the real trail. The dry bank is safe.',
                  ('R14','extra_footprint'):'Only your own tracks now. The morning trail is quiet.',
                  ('R17','changed_sign'):'HOME. The road sign is ordinary again.'}
            if (code,item['key']) in calm:
                item['script']=[h.cond('P12',1,[h.text(calm[(code,item['key'])])],item['script'])]
            if code=='R20' and item['key'] in ['plaque_a','plaque_b','plaque_c']:
                item['script']=[h.cond('P12',1,[h.text('Morning light reveals the weathered letters. The true bell calls everyone home.')],item['script'])]
            if code=='R09':
                def resting_turtle(value):
                    if isinstance(value,dict):
                        if value.get('command')=='EVENT_ACTOR_SHOW' and value.get('args',{}).get('actorId')==h.actor_id(code,'turtle'):
                            return h.cond('ACTIVE_COMPANION',2,[h.hide(code,'turtle')],[value])
                        return {k:resting_turtle(v) for k,v in value.items()}
                    if isinstance(value,list):return [resting_turtle(v) for v in value]
                    return value
                item['script']=resting_turtle(item['script'])
            if item.get('camp'):
                item['script']=h.camp(code,{'R07':1,'R13':2,'R19':3}[code])
            if item['script']:item['script']+=h.release()
            actor=copy.deepcopy(actor_template)
            for key in ['script','startScript','updateScript','hit1Script','hit2Script','hit3Script']:actor[key]=[]
            actor.update({'id':h.actor_id(code,item['key']),'_index':index,'symbol':'actor_'+code.lower()+'_'+item['key'],
                'name':item['key'].replace('_',' ').title(),'x':item['x'],'y':item['y'],
                'spriteSheetId':roles[item['sprite']]['id'],'paletteId':palette_ids[roles[item['sprite']]['paletteIndex']],
                'script':item['script'],'animate':False,'collisionGroup':''})
            actor.update(item.get('properties',{}))
            if actor['collisionGroup']=='none':
                actor['collisionGroup']=''
                actor['startScript']=[h.e('EVENT_ACTOR_COLLISIONS_DISABLE',{'actorId':actor['id']})]
            actual_actors.append({**item,'id':actor['id']})
            native_write(scene_dir/'actors'/f'{item["key"]}.gbsres',actor)
        follower=copy.deepcopy(actor_template)
        for key in ['script','startScript','updateScript','hit1Script','hit2Script','hit3Script']:follower[key]=[]
        follower.update({'id':h.actor_id(code,'companion'),'_index':len(actual_actors),
            'symbol':'actor_'+code.lower()+'_companion','name':'Companion','x':14,'y':14,
            'spriteSheetId':roles['follower']['id'],'paletteId':palette_ids[1],
            'animate':True,'collisionGroup':''})
        follower['startScript']=[h.e('EVENT_ACTOR_COLLISIONS_DISABLE',{'actorId':follower['id']})]
        if not args.geometry_only:
            from common_runtime import follower_update
            follower['updateScript']=follower_update(h,code,{'key':'companion','id':follower['id']})
        native_write(scene_dir/'actors/companion.gbsres',follower)
        actual_actors.append({'key':'companion','id':follower['id'],'x':14,'y':14,'script':[],
                             'properties':{'collisionGroup':'none'}})
        scene=copy.deepcopy(scene_template)
        for key in ['script','playerHit1Script','playerHit2Script','playerHit3Script']:scene[key]=[]
        scene.update({'id':h.scenes[code],'_index':number,'name':code+' '+ROOM_NAMES[number-1],
            'symbol':'scene_'+slug,'x':((number-7)%4)*230,'y':450+((number-7)//4)*210,
            'width':20,'height':18,'backgroundId':bgid,'paletteIds':bg_palette_ids,
            'spritePaletteIds':palette_ids,'collisions':compress(artroom['solid'])})
        if args.geometry_only:
            scene['script']=[h.e('EVENT_SHOW_SPRITES'),h.setv('CURRENT_ROOM',number)]+spec['onEnter']
        else:
            from common_runtime import common_init
            scene['script']=common_init(h,code,actual_actors,spec['abilityTargets'])+spec['onEnter']
        if args.geometry_only and code in camps:scene['script']+=camps[code]['onEnter']
        if code=='R09':
            scene['script']+=[h.cond('ACTIVE_COMPANION',2,[h.hide(code,'turtle')])]
        scene['script']+=h.release()
        native_write(scene_dir/'scene.gbsres',scene)
        integrated.append({'code':code,'scenePath':scene_dir.relative_to(SOURCE).as_posix(),
            'sceneId':scene['id'],'actors':len(actual_actors),'backgroundId':bgid,
            'uniqueTiles':artroom['uniqueTiles'],'openEdges':artroom['openEdges'],
            'commonInitIntegrated':not args.geometry_only})
    if not args.geometry_only:
        from common_runtime import bank_actor_resources,flush_banked,repair_native_visibility
        bank_actor_resources(h)
        flush_banked(h)
        repair_native_visibility()
    write(HERE/'integrated-art-manifest.json',{'rooms':integrated,'spriteRoles':roles,
          'status':'Native resources authored; runtime QA pending','sourceRoot':str(SOURCE),
          'romModified':False,'geometryOnly':args.geometry_only})
    print(json.dumps({'rooms':len(integrated),'actors':sum(r['actors'] for r in integrated),
        'commonRuntime':not args.geometry_only,'maximumUniqueBackgroundTiles':max(r['uniqueTiles'] for r in integrated)}))

if __name__=='__main__':main()
