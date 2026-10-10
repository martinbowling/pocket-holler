"""Static and host-side contract checks; this is not ROM/emulator evidence."""
from pathlib import Path
import json,ast,itertools
from prepare_integration import gather,main
from full_game_support import Helpers,EDGES

HERE=Path(__file__).resolve().parent
class Model:
    def __init__(self,h):self.h=h;self.state={v:0 for v in h.V.values()};self.choices=[];self.destination=None
    def get(self,name):return self.state[self.h.V[name]]
    def put(self,name,value):self.state[self.h.V[name]]=value
    def value(self,x):
        if x['type']=='number':return x['value']
        if x['type']=='variable':return self.state[x['value']]
        a,b=self.value(x['valueA']),self.value(x['valueB'])
        return {'eq':a==b,'ne':a!=b,'gt':a>b,'gte':a>=b,'lt':a<b,'lte':a<=b,'add':a+b,'sub':a-b,'mul':a*b,'max':max(a,b),'min':min(a,b)}[x['type']]
    def run(self,script,choices=()):
        self.choices=list(choices);self._run(script)
        assert not self.choices,('Unused menu choices',self.choices)
    def _run(self,script):
        for event in script:
            cmd=event['command'];a=event.get('args',{});children=event.get('children',{})
            if cmd=='EVENT_SET_VALUE':self.state[a['variable']]=self.value(a['value'])
            elif cmd=='EVENT_IF':self._run(children['true' if self.value(a['condition']) else 'false'])
            elif cmd=='EVENT_MENU':self.state[a['variable']]=self.choices.pop(0) if self.choices else 0
            elif cmd=='EVENT_SWITCH_SCENE':self.destination=a['sceneId']
            elif cmd=='EVENT_SAVE_DATA':self._run(children.get('true',[]))
            # Rendering, controller timing, event locks, audio and native saves
            # must be checked in the compiled game; the model cannot prove them.
    def actor(self,rooms,code,key,choices=()):
        self.run(next(a for a in rooms[code]['actors'] if a['key']==key)['script'],choices)
    def ability(self,rooms,code,key):
        target=next(t for t in rooms[code]['abilityTargets'] if t['key']==key)
        if self.get('ACTIVE_COMPANION')==target['companion']:self.run(target['action'])

def static(proposal):
    ids=set();events=0;text_pages=0;validvars={v['id'] for v in proposal['variables']['variables']}
    def walk(x):
        nonlocal events,text_pages
        if isinstance(x,dict):
            if 'command' in x:
                assert x['id'] not in ids,('Repeated proposed event',x['id']);ids.add(x['id']);events+=1
                if x['command']=='EVENT_TEXT':
                    pages=x['args']['text'];pages=[pages] if isinstance(pages,str) else pages
                    for page in pages:
                        lines=page.split('\n');assert len(lines)<=3
                        assert all(len(line)<=16 for line in lines),page
                        assert all(32<=ord(c)<=126 or c=='\n' for c in page),page
                        text_pages+=1
                if x['command']=='EVENT_MENU':
                    a=x['args'];assert a['items']<=8
                    assert all(len(a['option'+str(i)])<=16 for i in range(1,a['items']+1))
            if x.get('type')=='variable':assert x['value'] in validvars
            for v in x.values():walk(v)
        elif isinstance(x,list):
            for v in x:walk(v)
    walk(proposal)
    assert set(proposal['rooms'])=={f'R{i:02}' for i in range(7,25)}
    assert len(proposal['sceneIds'])==25
    for code,r in proposal['rooms'].items():
        keys={a['key'] for a in r['actors']};assert len(keys)==len(r['actors'])
        assert len(r['actors'])<=8,(code,'Actor budget')
        for a in r['actors']:assert 2<=a['x']<=17 and 3<=a['y']<=14,(code,a['key'],'Placement')
        for t in r['abilityTargets']:assert t['key'] in keys,(code,t['key'])
    adjacency={f'R{i:02}':set() for i in range(1,25)}
    for a,_,b,_,_ in EDGES:adjacency[a].add(b);adjacency[b].add(a)
    visited={'R01'};todo=['R01']
    while todo:
        room=todo.pop()
        for dest in adjacency[room]-visited:visited.add(dest);todo.append(dest)
    assert len(visited)==24
    return {'events':events,'textPages':text_pages,'connectedRooms':len(visited)}

def contracts(h,rooms):
    m=Model(h);m.put('P01',1);m.put('P02',1);m.put('RECRUITED_MOTH',1)
    # Module-owned logical transitions are checked without controller emulation.
    m.actor(rooms,'R09','downstream_gate');assert m.get('P03')==0 and m.get('REED_STAGE')==0
    m.actor(rooms,'R09','upstream_gate');m.actor(rooms,'R09','downstream_gate')
    assert m.get('P03')==1 and m.get('RECRUITED_TURTLE')==1
    m.ability(rooms,'R10','far_wave');assert m.get('P04')==0 and m.get('STONE_STAGE')==0
    for key in ['near_wave','middle_wave','far_wave']:m.ability(rooms,'R10',key)
    assert m.get('P04')==1
    m.ability(rooms,'R11','wheel_brace');assert m.get('P05')==0
    for key in ['inlet','outlet']:m.actor(rooms,'R11',key)
    m.ability(rooms,'R11','wheel_brace');assert m.get('P05')==1
    m.actor(rooms,'R12','light_crank');assert m.get('P06')==0
    m.ability(rooms,'R12','spillway_wave');m.actor(rooms,'R12','light_crank')
    assert m.get('P06')==1 and m.get('PHASE')==2
    # Completing a room twice or entering it with another companion preserves
    # the permanent flag. Native collision and visual restoration need runtime.
    m.put('ACTIVE_COMPANION',1)
    for code,flag in [('R09','P03'),('R10','P04'),('R11','P05'),('R12','P06')]:
        m.run(rooms[code]['onEnter']);assert m.get(flag)==1
    return {'creekCorrectWrongAndReentry':True}

def ridge_contracts(h,rooms,common):
    """Logical event contracts only: no controller, ROM, collision or save proof."""
    m=Model(h)
    for flag in ['P01','P02','P03','P04','P05','P06',
                 'RECRUITED_MOTH','RECRUITED_TURTLE']:
        m.put(flag,1)
    m.put('PHASE',2)
    m.put('REDUCED_SCARES',1);m.put('AUDIO_OFF',1)
    m.actor(rooms,'R14','extra_footprint');assert m.get('H3')==1
    m.actor(rooms,'R14','extra_footprint');assert m.get('H3')==1
    progression=[f'P{i:02}' for i in range(1,13)]+[
        'RECRUITED_MOTH','RECRUITED_TURTLE','RECRUITED_THUNDERBIRD',
        'ENDING_SEEN']+[f'J{i}' for i in range(1,7)]
    def snapshot():return {name:m.get(name) for name in progression}
    def wrong_companions(code,key):
        target=next(t for t in rooms[code]['abilityTargets'] if t['key']==key)
        before=dict(m.state)
        for companion in [0,1,2,3]:
            if companion==target['companion']:continue
            m.put('ACTIVE_COMPANION',companion)
            expected=dict(m.state)
            m.ability(rooms,code,key)
            assert m.state==expected,(code,key,'Wrong companion mutated state')
        m.state=before

    # P07 can be solved by either protagonist, independent of journal pages.
    m.put('PLAYER_CHARACTER',1)
    m.actor(rooms,'R15','west_vane',[1])
    m.actor(rooms,'R15','east_vane',[4])
    m.actor(rooms,'R15','central_perch')
    assert m.get('P07')==0 and m.get('RECRUITED_THUNDERBIRD')==0
    m.run(rooms['R15']['onEnter'])
    assert m.get('VANEA')==0 and m.get('VANEB')==0
    m.actor(rooms,'R15','west_vane',[2])
    m.actor(rooms,'R15','east_vane',[4])
    m.actor(rooms,'R15','central_perch')
    assert m.get('P07')==1 and m.get('RECRUITED_THUNDERBIRD')==1
    assert m.get('ACTIVE_COMPANION')==3
    before=snapshot();m.actor(rooms,'R15','central_perch')
    assert snapshot()==before

    # P08 wrong sequence clears only local relays; re-entry clears unfinished
    # arrangements. Switching to Moth/Turtle cannot operate a Spark target.
    for key in ['leaf_relay','wave_relay','star_relay']:
        wrong_companions('R16',key)
    m.put('ACTIVE_COMPANION',3)
    m.ability(rooms,'R16','wave_relay')
    assert m.get('P08')==0 and m.get('RELAY_STAGE')==0
    m.ability(rooms,'R16','leaf_relay');assert m.get('RELAY_STAGE')==1
    m.run(rooms['R16']['onEnter']);assert m.get('RELAY_STAGE')==0
    for key in ['leaf_relay','wave_relay','star_relay']:
        m.ability(rooms,'R16',key)
    assert m.get('P08')==1 and m.get('CHAPTER')==3
    m.actor(rooms,'R17','changed_sign');assert m.get('H2')==1
    m.actor(rooms,'R17','changed_sign');assert m.get('H2')==1
    before=snapshot();m.ability(rooms,'R16','star_relay')
    assert snapshot()==before

    # P09 false selections and false doors return to the real camp, preserving
    # every permanent flag. J1-J6 remain zero throughout the mandatory route.
    m.put('ACTIVE_COMPANION',1)
    for key in ['plaque_a','plaque_b','plaque_c']:
        wrong_companions('R20',key)
        m.ability(rooms,'R20',key)
    assert m.get('H4')==1
    before=snapshot();m.actor(rooms,'R20','bell_instruction',[2])
    assert m.destination==h.scenes['R19'] and snapshot()==before
    assert m.get('P09')==0
    before=snapshot();m.actor(rooms,'R20','false_door',[1])
    assert m.destination==h.scenes['R19'] and snapshot()==before
    m.run(rooms['R20']['onEnter'])
    assert all(m.get(name)==0 for name in ['PLAQUE_A','PLAQUE_B','PLAQUE_C'])
    for key in ['plaque_a','plaque_b','plaque_c']:m.ability(rooms,'R20',key)
    m.actor(rooms,'R20','bell_instruction',[1]);assert m.get('P09')==1
    before=snapshot();m.actor(rooms,'R20','bell_instruction')
    assert snapshot()==before

    # P10 requires the true inscription, both channels and Turtle at the stone.
    m.actor(rooms,'R21','left_channel',[2])
    m.actor(rooms,'R21','right_channel',[1])
    m.put('ACTIVE_COMPANION',2)
    m.ability(rooms,'R21','spring_stone');assert m.get('P10')==0
    m.run(rooms['R21']['onEnter'])
    assert m.get('CHANNEL_A')==0 and m.get('CHANNEL_B')==0
    m.actor(rooms,'R21','left_channel',[2])
    m.actor(rooms,'R21','right_channel',[4])
    wrong_companions('R21','spring_stone')
    m.ability(rooms,'R21','spring_stone');assert m.get('P10')==1

    # Every lamp order works, and repeating a charged lamp never double counts.
    lamps=['bell_lamp_a','bell_lamp_b','bell_lamp_c']
    m.put('ACTIVE_COMPANION',3)
    for key in lamps:wrong_companions('R22',key)
    for order in itertools.permutations(lamps):
        m.put('P11',0);m.put('BELL_LAMPS',0)
        for i,key in enumerate(order):
            m.ability(rooms,'R22',key)
            assert m.get('P11')==int(i==2),(order,'Premature P11')
            before=m.get('BELL_LAMPS');m.ability(rooms,'R22',key)
            assert m.get('BELL_LAMPS')==before,(order,'Repeated lamp changed bits')
        assert m.get('BELL_LAMPS')==7 and m.get('P11')==1
    m.put('P11',0);m.put('BELL_LAMPS',0)
    m.ability(rooms,'R22',lamps[0]);assert m.get('BELL_LAMPS')==1
    m.run(rooms['R22']['onEnter']);assert m.get('BELL_LAMPS')==0
    for key in lamps:m.ability(rooms,'R22',key)
    for missing in ['P02','P06','P08','P09','P10']:
        m.put(missing,0);m.put('P11',0);m.put('BELL_LAMPS',0)
        m.ability(rooms,'R22',lamps[0])
        assert m.get('BELL_LAMPS')==0 and m.get('P11')==0,missing
        m.put(missing,1)
    for key in lamps:m.ability(rooms,'R22',key)

    # Final gate checks every milestone. Wait, B-cancel (choice0), and cancelling
    # the separate confirmation preserve P12/PHASE/ENDING_SEEN. This models
    # menu return values only; a fresh physical A press is a runtime test.
    for missing in ['P02','P06','P08','P09','P10','P11']:
        m.put(missing,0);m.actor(rooms,'R22','hollow_bell')
        assert m.get('P12')==0 and m.get('PHASE')==2,missing
        m.put(missing,1)
    for choices in [[0],[2],[3],[1,0],[1,2]]:
        before=snapshot();m.actor(rooms,'R22','hollow_bell',choices)
        assert snapshot()==before and m.get('PHASE')==2,choices
    assert all(m.get('J'+str(i))==0 for i in range(1,7))
    m.put('ACTIVE_COMPANION',0)
    m.actor(rooms,'R22','hollow_bell',[1,1])
    assert m.get('P12')==1 and m.get('PHASE')==3 and m.get('CHAPTER')==4
    assert m.destination==h.scenes['R23'] and m.get('ENDING_SEEN')==0
    before=snapshot();m.actor(rooms,'R22','hollow_bell')
    assert snapshot()==before
    for code,flag in [('R15','P07'),('R16','P08'),('R20','P09'),
                      ('R21','P10'),('R22','P11')]:
        m.put('ACTIVE_COMPANION',1);m.run(rooms[code]['onEnter'])
        assert m.get(flag)==1
    # The required reunion and credits are the only tested ENDING_SEEN writer.
    # Cancelling the subsequent save is allowed; this does not prove durability.
    m.run(common['R01']['reunionScript'],[2])
    assert m.get('ENDING_SEEN')==1
    assert all(m.get('J'+str(i))==0 for i in range(1,7))
    return {'ridgeFinaleSourceModelContracts':True,'bellLampOrdersChecked':6,
            'wrongCompanionDispatchModel':True,'zeroJournalEndingModel':True,
            'falseRoutesPreserveProgressModel':True,'finalConfirmationCancelModel':True,
            'dawnBeforeCreditsModel':True}

def ridge_geometry(rooms):
    """Conservative source geometry, not the native engine collision model.

    Assume every actor and player occupies 2x2 tiles. The art generator keeps
    water on blocked scenic rims. This verifies a clear reachable below stand
    for every ridge actor and each ability target, starting at a safe landing.
    """
    art=json.loads((HERE/'art/art-manifest.json').read_text())
    manifest={r['code']:r for r in art['rooms']}
    checked=0;target_checks=0
    for code in [f'R{i:02}' for i in range(13,24)]:
        room=rooms[code];solid=manifest[code]['solid'];slots=manifest[code]['slots']
        blocks={(x,y) for y in range(18) for x in range(20) if solid[y*20+x]}
        for actor in room['actors']:
            blocks|={(actor['x']+dx,actor['y']+dy)
                     for dx in range(2) for dy in range(2)}
        def clear(x,y):
            return all(0<=x+dx<20 and 0<=y+dy<18 and
                       (x+dx,y+dy) not in blocks
                       for dx in range(2) for dy in range(2))
        start=(8,14);assert clear(*start),(code,'Blocked assumed entry landing')
        todo=[start];reached={start}
        while todo:
            x,y=todo.pop()
            for point in [(x-1,y),(x+1,y),(x,y-1),(x,y+1)]:
                if point not in reached and clear(*point):
                    reached.add(point);todo.append(point)
        for actor in room['actors']:
            stand=(actor['x'],actor['y']+2)
            assert stand in reached,(code,actor['key'],'Blocked below approach',stand)
            checked+=1
        for target in room['abilityTargets']:
            actor=next(a for a in room['actors'] if a['key']==target['key'])
            assert (actor['x'],actor['y'])==(target['x'],target['y'])
            x,y=target['x'],target['y']+2
            # Slot3 is the supplied water palette; this narrow check catches
            # accidental creek-style visual water beneath a standing station.
            assert all(slots[(y+dy)*20+x+dx]!=3
                       for dx in range(2) for dy in range(2)),(code,target['key'],'Water palette below station')
            target_checks+=1
    return {'ridgeBelowApproachSourceGeometryActors':checked,
            'ridgeAbilityStandingStationsChecked':target_checks,
            'geometryPlayerFootprintAssumption':'2x2 tiles; native behavior untested'}

if __name__=='__main__':
    for p in HERE.glob('*.py'):ast.parse(p.read_text())
    main();proposal=json.loads((HERE/'full-game-proposal.json').read_text())
    h,rooms,common=gather();result=static(proposal);result.update(contracts(h,rooms))
    result.update(ridge_contracts(h,rooms,common))
    result.update(ridge_geometry(rooms))
    result.update({'passed':True,'scope':'Staged source structure and host-side script contracts only','compiledRom':False,'emulatorTested':False,'releaseReady':False})
    (HERE/'proposal-checks.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
