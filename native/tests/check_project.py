"""Check native identities, destinations, collision landings and text fit."""
from pathlib import Path
import csv,json
ROOT=Path(__file__).resolve().parents[1]
resources=[(p,json.loads(p.read_text())) for p in (ROOT/'project').rglob('*.gbsres')]
scenes={d['id']:d for p,d in resources if d.get('_resourceType')=='scene'}
scripts={d['id'] for p,d in resources if d.get('_resourceType')=='script'}
seen=set();symbols=set();events=set();count=0;transitions=0;pages=0
def collisions(s):
    raw=s['collisions'];out=[];i=0
    while i<len(raw):
        value=int(raw[i:i+2],16);i+=2
        if raw[i]=='!':n=1;i+=1
        else:
            end=raw.index('+',i);n=int(raw[i:end],16);i=end+1
        out.extend([value]*n)
    assert len(out)==s['width']*s['height']
    return out
tiles={sid:collisions(s) for sid,s in scenes.items()}
def walk(o):
    global count,transitions,pages
    if isinstance(o,dict):
        cmd=o.get('command');a=o.get('args',{})
        if cmd:
            assert o['id'] not in events,f"Duplicate event {o['id']}"
            events.add(o['id']);count+=1
        if cmd=='EVENT_SWITCH_SCENE':
            sid=a['sceneId'];assert sid in scenes;scene=scenes[sid]
            x,y=a['x']['value'],a['y']['value']
            assert 0<=x<scene['width']-1 and 0<=y<scene['height']
            assert all(tiles[sid][y*scene['width']+t]==0 for t in [x,x+1]),(scene['name'],x,y)
            transitions+=1
        if cmd=='EVENT_TEXT':
            text=a['text'];text=[text] if isinstance(text,str) else text
            for page in text:
                lines=page.split('\n');assert len(lines)<=3,page
                assert all(len(line)<=16 for line in lines),page
                assert all(32<=ord(c)<=126 or c=='\n' for c in page),page
                pages+=1
        if cmd=='EVENT_MENU':
            assert all(len(a['option'+str(i)])<=16 for i in range(1,a['items']+1))
        if cmd=='EVENT_CALL_CUSTOM_EVENT':
            assert a['customEventId'] in scripts,('Missing banked action',a['customEventId'])
        for value in o.values():walk(value)
    elif isinstance(o,list):
        for value in o:walk(value)
for path,d in resources:
    if 'id' in d:
        assert d['id'] not in seen,(path,d['id']);seen.add(d['id'])
    if 'symbol' in d:
        assert d['symbol'] not in symbols,(path,d['symbol']);symbols.add(d['symbol'])
    walk(d)
rows=list(csv.DictReader((ROOT/'docs/room-map.csv').open()))
assert {r['native_scene_id'] for r in rows if r['status'] in ['playable','UI']}==set(scenes)
assert len(scenes)==25
assert {s['name'].split()[0] for s in scenes.values()}=={'TITLE'}|{f'R{i:02}' for i in range(1,25)}
variables=json.loads((ROOT/'project/variables.gbsres').read_text())['variables']
assert len({v['id'] for v in variables})==len(variables)
assert len({v['name'] for v in variables})==len(variables)
assets=[json.loads(p.read_text()) for p in (ROOT/'assets').rglob('*.gbsres')]
asset_ids={d['id'] for d in assets if 'id' in d}
for p,d in resources:
    if d.get('_resourceType')=='scene':assert d['backgroundId'] in asset_ids,(p,'Missing background')
    if d.get('_resourceType')=='actor':
        assert d['spriteSheetId'] in asset_ids,(p,'Missing sprite')
        assert d.get('collisionGroup','') in ['', '1','2','3'],(p,'Invalid collision group')
        scene=next(s for sp,s in resources if sp==p.parent.parent/'scene.gbsres')
        assert 0<=d['x']<scene['width']-1 and 0<=d['y']<scene['height']-1,(p,'Actor out of bounds')
print(json.dumps({'passed':True,'scenes':len(scenes),'playableRooms':24,'events':count,'transitions':transitions,'textPages':pages,'uniqueSymbols':len(symbols),'variables':len(variables),'bankedActions':len(scripts),'scope':'Native source identities, asset/action references, collision landing tiles and text fit; input-driven runtime route is checked separately'},indent=2))
