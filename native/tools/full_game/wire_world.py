"""Wire the complete native room graph inside the selected working project.

Run after chapter/core integration has finished. Generated transitions stay
inside the game source; live saves, recordings and preview exports are untouched.
"""
from pathlib import Path
import json,copy,hashlib
from full_game_support import Helpers,uid,EDGES,SOURCE

def load(path):return json.loads(path.read_text())
def write(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,indent=2)+'\n')
def scope(value,path):
    if isinstance(value,dict):
        if 'command' in value:value['id']=uid('native/'+path)
        for k,v in value.items():
            if k!='id':scope(v,path+'/'+k)
    elif isinstance(value,list):
        for i,v in enumerate(value):scope(v,path+'/'+str(i))
def decode(raw):
    result=[];i=0
    while i<len(raw):
        value=int(raw[i:i+2],16);i+=2
        if raw[i]=='!':n=1;i+=1
        else:
            end=raw.index('+',i);n=int(raw[i:end],16);i=end+1
        result.extend([value]*n)
    return result
def encode(values):
    parts=[];i=0
    while i<len(values):
        j=i+1
        while j<len(values) and values[j]==values[i]:j+=1
        n=j-i;parts.append(f'{values[i]:02x}'+('!' if n==1 else f'{n:x}+'));i=j
    return ''.join(parts)

SHAPES={'north':(8,0,4,2),'south':(8,16,4,2),'west':(0,10,2,4),'east':(18,10,2,4)}
LANDINGS={'north':(8,3,'down'),'south':(8,14,'up'),'west':(2,10,'right'),'east':(16,10,'left')}
CLUES={'P02':'Repair the boundary light. Reveal its plaque, then use the ray latch.',
 'P03':'Open the upstream reed gate, then downstream. Turtle will join you.',
 'P04':'Turtle must Steady the near, middle and far causeway stations.',
 'P05':'Match the flow diagram, then Steady the wheel brace.',
 'P06':'Steady the spillway, then turn the creek light crank.',
 'P07':'Shelter the roost and meet Thunderbird before this trail.',
 'P08':'Spark the leaf, wave and star relays to light the ridge.',
 'P12':'The dawn trail opens after the hollow bell has rung.',
 'VISITED_R19':'The home shortcut opens from the root threshold. Follow the bell road first.'}

def main():
    h=Helpers();directories={}
    for path in (SOURCE/'project/scenes').glob('*/scene.gbsres'):
        directories[load(path)['name'].split()[0]]=path.parent
    assert set(directories)==set(h.scenes), 'Integrate all scene resources before wiring'
    manifest=[]
    def trigger(code,edge,dest,dest_edge,gate=None,landing=None):
        x,y,w,height=SHAPES[edge]
        dx,dy,direction=landing or LANDINGS[dest_edge]
        destid=h.scenes[dest]
        existing=[]
        for p in (directories[code]/'triggers').glob('*.gbsres'):
            d=load(p)
            if (d['x'],d['y'],d['width'],d['height'])==(x,y,w,height):existing.append((p,d))
        assert len(existing)<=1,(code,edge,'Ambiguous existing edge')
        if existing:path,data=existing[0]
        else:
            path=directories[code]/'triggers'/f'to_{dest.lower()}.gbsres'
            data={'_resourceType':'trigger','id':uid(code+'-edge-'+edge),'_index':len(list((directories[code]/'triggers').glob('*.gbsres'))),'name':'To '+dest,'symbol':'trigger_'+code.lower()+'_to_'+dest.lower(),'x':x,'y':y,'width':w,'height':height,'script':[],'leaveScript':[]}
        success=[h.switch(dest,dx,dy,direction)]
        if gate:
            rx,ry,rd=LANDINGS[edge]
            fail=[h.text(CLUES[gate]),h.e('EVENT_ACTOR_SET_POSITION',{'actorId':'player','x':h.num(rx),'y':h.num(ry),'units':'tiles'}),h.e('EVENT_ACTOR_SET_DIRECTION',{'actorId':'player','direction':{'type':'direction','value':rd}}),h.unlock()]
            action=[h.cond(gate,1,success,fail)]
        else:action=success
        data['script']=[h.lock()]+h.release()+action
        scope(data['script'],str(path.relative_to(SOURCE))+'/script');write(path,data)
        scene_path=directories[code]/'scene.gbsres';scene=load(scene_path);cells=decode(scene['collisions'])
        assert len(cells)==360
        # Open only this exact landing/edge corridor. Other source geometry stays.
        if edge=='north':region=(8,0,4,5)
        elif edge=='south':region=(8,14,4,4)
        elif edge=='west':region=(0,10,4,4)
        else:region=(16,10,4,4)
        gx,gy,gw,gh=region
        for yy in range(gy,gy+gh):
            for xx in range(gx,gx+gw):cells[yy*20+xx]=0
        scene['collisions']=encode(cells);write(scene_path,scene)
        manifest.append({'from':code,'edge':edge,'to':dest,'destinationEdge':dest_edge,'gate':gate,'triggerId':data['id'],'landing':[dx,dy,direction]})
    def portal_actor(code,key,x,y,dest,gate=None,landing=(8,12,'up'),existing_key=None):
        directory=directories[code]/'actors'
        path=directory/((existing_key or key)+'.gbsres')
        if path.exists():actor=load(path)
        else:
            template=next(p for p in (directories['R02']/'actors').glob('*.gbsres') if load(p)['name'].lower()=='directions')
            actor=load(template);actor.update({'id':h.actor_id(code,key),'_index':len(list(directory.glob('*.gbsres'))),'name':key.replace('_',' ').title(),'symbol':'actor_'+code.lower()+'_'+key,'x':x,'y':y,'script':[],'startScript':[],'updateScript':[]})
        dx,dy,direction=landing
        success=[h.switch(dest,dx,dy,direction)]
        script=[h.lock()]+h.release()+([h.cond(gate,1,success,[h.text(CLUES[gate])]+h.release()+[h.unlock()])] if gate else success)
        actor['script']=script;scope(actor['script'],str(path.relative_to(SOURCE))+'/script');write(path,actor)
        manifest.append({'from':code,'actor':key,'to':dest,'gate':gate,'actorId':actor['id'],'landing':[dx,dy,direction]})
    for a,ae,b,be,gate in EDGES:
        if ae=='shortcut':
            portal_actor(a,'home_shortcut',14,12,b,gate)
            portal_actor(b,'home_shortcut',14,12,a,gate)
        elif be=='dawn':
            trigger(a,ae,b,'south',gate,landing=(12,12,'right'))
            portal_actor(b,'dawn_path',14,12,a,gate)
        elif a=='R01' and b=='R24':
            portal_actor(a,'interior_notice',4,8,b,existing_key='interior_notice',landing=LANDINGS['east'])
            trigger(b,'east',a,'west',landing=(4,10,'up'))
        else:
            trigger(a,ae,b,be,gate)
            # Return path is unconditional; shortcut edges retain their gate
            # at both ends so the first legitimate threshold visit is preserved.
            trigger(b,be,a,ae,None)
    # Manual A/B interaction dispatch must see the final portal actor set.
    from common_runtime import input_bindings,flush_banked,bank_actor_resources,repair_native_visibility
    bank_actor_resources(h)
    for code,directory in directories.items():
        if code=='TITLE':continue
        scene_path=directory/'scene.gbsres';scene=load(scene_path)
        actors=[]
        for p in (directory/'actors').glob('*.gbsres'):
            d=load(p);actors.append({**d,'key':p.stem})
        # Existing B targets stay in the installed scene's binding. Input helper
        # receives their same source-room proposal for new rooms.
        from creek import build as creek
        from ridge_hollow import build as ridge
        proposals=creek(h);proposals.update(ridge(h))
        targets=proposals.get(code,{}).get('abilityTargets',[])
        if code=='R20':
            for target in targets:
                target['action']=[h.cond('P12',1,[h.text('The bell has called everyone home. Only ordinary letters remain in morning light.')],target['action'])]
        new_bindings=input_bindings(h,code,actors,targets)
        scene['script']=[e for e in scene['script'] if e['command'] not in ['EVENT_SET_INPUT_SCRIPT','EVENT_REMOVE_INPUT_SCRIPT']]
        scene['script'][0:0]=new_bindings
        scope(scene['script'],str(scene_path.relative_to(SOURCE))+'/script');write(scene_path,scene)
    flush_banked(h)
    repair_native_visibility()
    (SOURCE/'evidence/full-world-map.json').write_text(json.dumps({'edges':manifest,'playableRooms':24,'UI':['TITLE']},indent=2)+'\n')
    print(json.dumps({'wiredDirectedConnections':len(manifest),'playableRooms':24}))

if __name__=='__main__':main()
