"""Create reviewable semantic-tool batches. Existing IDs are stable UUID5 values.
This writes batches, never rewrites native resource files or imports concept art.
"""
from pathlib import Path
import json, uuid, csv, textwrap
ROOT=Path(__file__).resolve().parents[1]
R=json.loads((ROOT/'tools/resources.json').read_text())
ART=json.loads((ROOT/'tools/art-manifest.json').read_text())
S={k:(v.get('scene',v))['id'] for k,v in R['scenes'].items()}
A={k:v['id'] for k,v in R['assets'].items()}
P={k:v['palette']['id'] for k,v in R['palettes'].items()}
NS=uuid.UUID('7403925b-34f1-4bfa-a188-bc3c8ea2aa2e')
def uid(s): return str(uuid.uuid5(NS,s))
counter=0
def e(cmd,args=None,**branches):
    global counter
    counter+=1
    v={'id':uid('event-'+str(counter)), 'command':cmd,'args':args or {}}
    if branches:v['children']=branches
    return v
def num(n):return {'type':'number','value':n}
VN=['SAVE_SCHEMA','BUILD_SAVE_EPOCH','CHAPTER','PHASE','CAMP_ID','VISITED_R19','ACTIVE_COMPANION',
    'RECRUITED_MOTH','RECRUITED_TURTLE','RECRUITED_THUNDERBIRD']+[f'P{i:02}' for i in range(1,13)]+[f'J{i}' for i in range(1,7)]+[f'H{i}' for i in range(1,5)]+['REDUCED_SCARES','AUDIO_OFF','FAST_TEXT','ENDING_SEEN','WINDSCREEN','BARK_REVEALED','GATE_REVEALED','INTRO_SEEN','MILESTONE_SAVED','MET_JUNE','SESSION_REPLACES_SAVE','MENU','SUBMENU','SCHEMA_PEEK','EPOCH_PEEK','TARGET_USED','NEAR_TARGET','CURRENT_ROOM','PX','PY']
V={n:str(i) for i,n in enumerate(VN)}
def var(n):return {'type':'variable','value':V[n]}
def setv(n,x):return e('EVENT_SET_VALUE',{'variable':V[n],'value':num(x)})
def cond(n,x,t,f=None,op='eq'):return e('EVENT_IF',{'condition':{'type':op,'valueA':var(n),'valueB':num(x)}},true=t,false=f or [])
def text(*pages):
    # Hand-defined page boundaries; 16 fixed-width characters / line, 3 lines.
    pp=[]
    for p in pages:
        lines=textwrap.wrap(p.upper(),16,break_long_words=False,break_on_hyphens=False)
        for j in range(0,len(lines),3):pp.append('\n'.join(lines[j:j+3]))
    return e('EVENT_TEXT',{'text':pp if len(pp)>1 else pp[0],'minHeight':4,'maxHeight':4,'textHeight':3,'closeButton':'a'})
def wait(n=1):return e('EVENT_WAIT',{'units':'frames','frames':num(n)})
def release():
    label='release-'+str(counter)
    return [e('EVENT_DEFINE_LABEL',{'label':label}),e('EVENT_IF_INPUT',{'input':['a','b','start','select','up','down','left','right']},true=[wait(),e('EVENT_GOTO_LABEL',{'label':label})],false=[])]
def lock():return e('EVENT_SCRIPT_LOCK')
def unlock():return e('EVENT_SCRIPT_UNLOCK')
def hide(a):return e('EVENT_ACTOR_HIDE',{'actorId':a})
def show(a):return e('EVENT_ACTOR_SHOW',{'actorId':a})
def pos(a,x,y):return e('EVENT_ACTOR_SET_POSITION',{'actorId':a,'x':num(x),'y':num(y),'units':'tiles'})
def switch(code,x,y,d):return e('EVENT_SWITCH_SCENE',{'sceneId':S[code],'x':num(x),'y':num(y),'direction':d,'fadeSpeed':'2'})
def menu(options,variable='MENU'):return e('EVENT_MENU',{'variable':V[variable],'items':len(options),'layout':'menu','cancelOnB':True,'cancelOnLastOption':False,**{f'option{i+1}':s.upper() for i,s in enumerate(options)}})
def sound():return cond('AUDIO_OFF',0,[e('EVENT_SOUND_PLAY_EFFECT',{'type':'beep','pitch':6,'duration':0.12,'wait':False,'priority':'low'})])
def phase():return cond('PHASE',1,[e('EVENT_PALETTE_SET_BACKGROUND',{'palette0':P['dusk'],'palette1':P['duskwood'],**{f'palette{i}':'keep' for i in range(2,8)}})])
def objective():return [cond('P02',1,[text('Next: Go home to Marty. Save at the porch.','Light 1: lit. Lights 2 and 3: waiting.','Moth: Reveal ray marks with B.')],[cond('RECRUITED_MOTH',1,[cond('GATE_REVEALED',1,[text('Next: At the boundary, use A on the ray latch.','Light 1: dark. Moth trusts the real mark.')],[text('Next: Reveal the boundary inscription with B.','Face a ray mark. Press B with Moth.')])],[text('Next: Ask June in the store. Then explore the orchard.','Turn the windscreen. Inspect the steady lantern with A.')])])]
def settings():return [menu(['Audio','Scares','Text speed','Leave'],'SUBMENU'),cond('SUBMENU',1,[cond('AUDIO_OFF',0,[setv('AUDIO_OFF',1),text('Audio off. All clues remain visible.')],[setv('AUDIO_OFF',0),text('Audio on. Gentle effect tones.')])]),cond('SUBMENU',2,[cond('REDUCED_SCARES',0,[setv('REDUCED_SCARES',1),text('Reduced Scares on. No sudden movement or stings.')],[setv('REDUCED_SCARES',0),text('Standard Scares. No flashing or loud bursts.')])]),cond('SUBMENU',3,[cond('FAST_TEXT',0,[setv('FAST_TEXT',1),text('Instant text selected.')],[setv('FAST_TEXT',0),text('Normal text selected.')])]),cond('FAST_TEXT',1,[e('EVENT_TEXT_SET_ANIMATION_SPEED',{'speedIn':0,'speedOut':0,'speed':0,'allowFastForward':True})],[e('EVENT_TEXT_SET_ANIMATION_SPEED',{'speedIn':0,'speedOut':0,'speed':1,'allowFastForward':True})])]
def hints():return [cond('P02',1,[text('The porch signal is waiting for you.')],[cond('RECRUITED_MOTH',1,[text('Paint can point the wrong way. Living light tells the truth.')],[text('The vane points east. Something needs shelter from that wind.')])]),menu(['More help','Leave'],'SUBMENU'),cond('SUBMENU',1,[cond('P02',1,[text('Start: Return to Camp. Talk to Marty and choose Save.')],[cond('RECRUITED_MOTH',1,[text('Boundary: stand below the ray plaque and press B.','Then face the small ray latch to its left and press A.')],[text('Orchard: choose EAST at the windscreen.','Then inspect the lantern above it with A.')])])])]
def save():return [text('Save here? This writes one porch checkpoint.'),menu(['Save','Cancel'],'SUBMENU'),cond('SUBMENU',1,[setv('SAVE_SCHEMA',1),setv('BUILD_SAVE_EPOCH',1),setv('CAMP_ID',0),pos('player',8,12),cond('P02',1,[setv('MILESTONE_SAVED',1)]),e('EVENT_SAVE_DATA',{'saveSlot':0},true=[setv('SESSION_REPLACES_SAVE',0),cond('P02',1,[setv('MILESTONE_SAVED',1)]),text('Saved at the porch. You may turn the game off.')],load=[cond('P02',1,[setv('RECRUITED_MOTH',1),setv('P01',1),setv('CHAPTER',1),setv('PHASE',1)]),cond('RECRUITED_MOTH',1,[setv('ACTIVE_COMPANION',1)],[setv('ACTIVE_COMPANION',0)]),setv('WINDSCREEN',0),setv('TARGET_USED',0),setv('MENU',0),setv('SUBMENU',0),e('EVENT_SCENE_UPDATE_RESUME'),switch('R01',8,12,'up')])])]
def camp():return [menu(['Companion','Hint','Save','Leave']),cond('MENU',1,[cond('RECRUITED_MOTH',1,[menu(['Moth','Travel alone','Leave'],'SUBMENU'),cond('SUBMENU',1,[setv('ACTIVE_COMPANION',1),text('LanternMoth joins you. B: Reveal ray marks.')]),cond('SUBMENU',2,[setv('ACTIVE_COMPANION',0),text('Moth rests safely. Come back any time.')])],[text('No companion yet. A little light waits in the orchard.')])]),cond('MENU',2,hints()),cond('MENU',3,save())]
def pause():return [lock(),e('EVENT_SCENE_UPDATE_PAUSE'),menu(['Journal','Settings','Return to Camp','Quit','Resume']),cond('MENU',1,objective()+[cond('J1',1,[text('Journal 1: Each autumn, the town answers the lanterns with its own light.')])]),cond('MENU',2,settings()),cond('MENU',3,[text('Return to porch? Puzzle progress stays. This does not save.'),menu(['Return','Cancel'],'SUBMENU'),cond('SUBMENU',1,[setv('WINDSCREEN',0),e('EVENT_SCENE_UPDATE_RESUME'),switch('R01',8,12,'up')])]),cond('MENU',4,[text('Quit to title? Unsaved progress will be lost.'),menu(['Quit','Cancel'],'SUBMENU'),cond('SUBMENU',1,[e('EVENT_SCENE_UPDATE_RESUME'),switch('TITLE',8,12,'up')])]),e('EVENT_SCENE_UPDATE_RESUME')]+release()+[unlock()]
def quick():return [lock()]+objective()+release()+[unlock()]
def facing_target(x,y,action):
    # Native interaction distance is one 8px gameplay tile from the 16px body.
    checks=[]
    for px,py,d in [(x,y+2,'up'),(x,y-2,'down'),(x-2,y,'right'),(x+2,y,'left'),(x-1,y,'right'),(x+1,y,'left'),(x,y+1,'up'),(x,y-1,'down')]:
        checks.append(e('EVENT_IF_ACTOR_AT_POSITION',{'actorId':'player','x':num(px),'y':num(py),'units':'tiles'},true=[e('EVENT_IF_ACTOR_DIRECTION',{'actorId':'player','direction':{'type':'direction','value':d}},true=[setv('TARGET_USED',1)]+action,false=[])],false=[]))
    return checks
def ability(code):
    body=[lock(),setv('TARGET_USED',0)]
    if code=='R05':
        body+=facing_target(12,10,[cond('ACTIVE_COMPANION',1,[cond('BARK_REVEALED',0,[setv('BARK_REVEALED',1),sound(),text('Moth reveals: Trust living light. Try this at the boundary.')],[text('The bark mark stays clear.')])],[text('A ray mark. LanternMoth can reveal it.')])])
    if code=='R06':
        body+=facing_target(8,8,[cond('ACTIVE_COMPANION',1,[cond('GATE_REVEALED',0,[setv('GATE_REVEALED',1),sound(),text('The painted arrow fades. The inscription reads:','Follow the rays. Turn the latch to the left.')],[text('Follow the ray latch to the left.')])],[text('This needs Moth. Choose Companion at the porch.')])])
    # Empty use gives a non-blocking response: brief wing blink, no text.
    moth=uid(code+'-moth')
    body+=[cond('TARGET_USED',0,[cond('ACTIVE_COMPANION',1,[hide(moth),wait(4),show(moth)])])]
    return body+release()+[unlock()]

ops={c:[] for c in S}
names={'R01':'Home porch','R02':'Town lane','R03':'General store','R04':'Festival green','R05':'Orchard','R06':'Boundary gate','TITLE':'PocketHoller / Title'}
def actor(code,key,x,y,sprite,script,**props):
    aid=uid(code+'-'+key)
    ops[code].append({'type':'actor.create','id':aid,'name':key.replace('_',' ').title(),'x':x,'y':y,'spriteSheetId':A[sprite],'direction':'down','properties':{'script':script+release() if script else [],'paletteId':P['human'] if sprite in ['marty','june'] else P['glow'],**props}})
    return aid
def transition(code,key,x,y,w,h,dest,dx,dy,d):
    ops[code].append({'type':'trigger.create','id':uid(code+'-'+key),'name':key,'x':x,'y':y,'width':w,'height':h,'properties':{'script':[lock()]+release()+[switch(dest,dx,dy,d)]}})

for i,c in enumerate(S):
    art=next(a for a in ART['rooms'] if a['code']==c)
    collision=[]
    for yy in range(18):
        start=0
        while start<20:
            val=art['solid'][yy*20+start];end=start+1
            while end<20 and art['solid'][yy*20+end]==val:end+=1
            if c=='R06' and yy==3:
                for xx in range(start,end):collision.append({'shape':'tile','x':xx,'y':yy,'value':0 if 8<=xx<12 else val})
            else:collision.append({'shape':'rectangle','x':start,'y':yy,'width':end-start,'height':1,'value':val})
            start=end
    ops[c].append({'type':'scene.update','name':c+' '+names[c],'properties':{'backgroundId':R['bgs'][c]['id'],'paletteIds':[P['foliage'],P['wood'],P['glow'],P['water']],'spritePaletteIds':[P['human'],P['glow']]}})
    ops[c].append({'type':'collision.edit','edits':collision})
    if c=='TITLE':continue
    moth=uid(c+'-moth')
    # Nearby hovering presentation: deliberately non-colliding, no pathfinding.
    update=[cond('ACTIVE_COMPANION',1,[show(moth),e('EVENT_ACTOR_GET_POSITION',{'actorId':'player','vectorX':V['PX'],'vectorY':V['PY'],'units':'pixels'}),e('EVENT_ACTOR_SET_POSITION',{'actorId':moth,'x':{'type':'max','valueA':num(8),'valueB':{'type':'sub','valueA':var('PX'),'valueB':num(12)}},'y':{'type':'max','valueA':num(8),'valueB':{'type':'sub','valueA':var('PY'),'valueB':num(10)}},'units':'pixels'})],[hide(moth)]),wait(2)]
    actor(c,'moth',4,12,'moth',[],collisionGroup='none',startScript=[e('EVENT_ACTOR_COLLISIONS_DISABLE',{'actorId':moth})],updateScript=update)
    init=[e('EVENT_SHOW_SPRITES'),setv('CURRENT_ROOM',i+1),setv('TARGET_USED',0),phase(),cond('FAST_TEXT',1,[e('EVENT_TEXT_SET_ANIMATION_SPEED',{'speedIn':0,'speedOut':0,'speed':0,'allowFastForward':True})],[e('EVENT_TEXT_SET_ANIMATION_SPEED',{'speedIn':0,'speedOut':0,'speed':1,'allowFastForward':True})]),e('EVENT_SET_INPUT_SCRIPT',{'input':['start'],'override':True},true=pause()),e('EVENT_SET_INPUT_SCRIPT',{'input':['select'],'override':True},true=quick()),e('EVENT_SET_INPUT_SCRIPT',{'input':['b'],'override':True},true=ability(c))]
    if c=='R01':
        init += [setv('CAMP_ID',0),cond('INTRO_SEEN',0,[setv('INTRO_SEEN',1),text('PocketHoller. A few hours before sundown.','Dad is checking the porch signal. The lantern walk starts tonight.','A: inspect or talk. B: companion ability. Start: pause. Select: goal.')]),cond('P02',1,[cond('MILESTONE_SAVED',0,[text('The first light is repaired. A porch checkpoint is ready.'),*save()])])]
    if c=='R05':init += [cond('P01',0,[setv('WINDSCREEN',0)])]
    if c=='R06':init += [cond('P02',1,[hide(uid('R06-gate_left')),hide(uid('R06-gate_right'))])]
    init+=release()
    ops[c].append({'type':'scene.update','properties':{'script':init}})

actor('R01','marty',8,8,'marty',[cond('P02',1,[text('Marty: There you are. One light back on.','Moth knows the way. We will handle the creek together next.','That was a good bit of noticing, Roamin.')],[text('Marty: I will keep this porch signal lit.','June has the map in the store. Take a look at the orchard.','Come home when the first light is on. I will be right here.')]),*camp()])
actor('R01','porch_signal',14,8,'lantern',[text('The porch signal burns steady. This is a safe place.')])
actor('R01','interior_notice',4,8,'sign',[text('The house is warm. Porch interior joins the full game after opening review.')])
actor('R02','directions',14,10,'sign',[text('North: home porch. South: festival green. West: June and the store.','Orchard is west of the green. Boundary is east.')])
actor('R02','distant_lights',12,8,'lantern',[cond('P02',1,[text('One warm light on the fence. Two distant lamps wait.')],[text('Three warning lights. All quiet for now.')])])
actor('R03','june',8,6,'june',[setv('MET_JUNE',1),text('June: The storm tangled our light circuit. Start at the boundary.','The orchard lantern kept flickering. The windscreen may be turned wrong.','A creature once lived in its warm light. Be gentle with it.')])
actor('R03','journal_page',4,8,'sign',[cond('J1',0,[setv('J1',1),text('Journal page 1 found. The lantern walk.','Each autumn, the town answers the lanterns with its own light.','Optional pages never block your path.')],[text('The lantern walk. Your journal already has this page.')])])
actor('R04','festival_notice',8,6,'sign',[text('Lantern walk tonight. Everyone meet here after sundown.','Original voices. Original lights. Everyone accounted for.')])
actor('R04','warm_lantern',14,8,'lantern',[text('A festival lantern. It smells like warm wax and apple leaves.')])
actor('R05','weather_vane',14,6,'vane',[text('The vane points east. The wind follows it.','Open the windscreen toward the sheltered lantern.')])
actor('R05','windscreen',8,10,'windscreen',[cond('P01',1,[text('The lantern is sheltered. Moth remembers your help.')],[text('Turn the open side of the windscreen.'),menu(['North','East','South','West'],'SUBMENU'),cond('SUBMENU',0,[],[setv('WINDSCREEN',0)]),*[cond('SUBMENU',i,[setv('WINDSCREEN',i),text('Open side: '+n+'.')]) for i,n in enumerate(['North','East','South','West'],1)]])])
actor('R05','old_lantern',8,6,'lantern',[cond('P01',1,[text('A steady little flame. LanternMoth is always welcome here.')],[cond('WINDSCREEN',2,[setv('P01',1),setv('RECRUITED_MOTH',1),setv('ACTIVE_COMPANION',1),sound(),text('The lantern stops flickering. Something opens its wings.','LanternMoth joins you. Its living glow never lies.','Practice: face the ray mark on the bark. Press B.','Then try Reveal at the boundary inscription.')],[text('The flame flickers in the wind. The vane may help.')])])])
actor('R05','bark_mark',12,10,'ray',[cond('BARK_REVEALED',1,[text('Trust living light.')],[text('Ray mark: REVEAL. Face it and press B with Moth.')])])
actor('R06','inscription',8,8,'ray',[cond('GATE_REVEALED',1,[text('Follow the rays. Turn the latch to the left.')],[text('The words look freshly painted. A ray mark waits beneath them.','Face this plaque. Moth can REVEAL it with B.')])])
actor('R06','true_latch',6,6,'ray',[cond('P02',1,[text('The latch is open. The first light stays lit.')],[cond('GATE_REVEALED',1,[setv('P02',1),setv('CHAPTER',1),setv('PHASE',1),hide(uid('R06-gate_left')),hide(uid('R06-gate_right')),phase(),sound(),text('The first warning light warms the fence. Dusk settles.','A voice in the woods: Come home, home.','Roamin: One word too many. Moth points back toward town.','Go home to Marty. Save at the porch.')],[text('Which latch is true? Reveal the inscription before choosing.')])])])
actor('R06','painted_arrow',12,10,'sign',[text('The painted arrow points into dark water.','Moth waits by the dry path. You do not have to follow a sign.')])
actor('R06','gate_left',8,2,'windscreen',[cond('P02',1,[text('The boundary is open. The creek route follows in the full game.')],[text('The warning-light gate is shut. Check the ray inscription.')])])
actor('R06','gate_right',10,2,'windscreen',[])

transition('R01','to_lane',8,16,4,2,'R02',8,3,'down')
transition('R02','to_porch',8,0,4,2,'R01',8,14,'up')
transition('R02','to_green',8,16,4,2,'R04',8,3,'down')
transition('R04','to_lane',8,0,4,2,'R02',8,14,'up')
transition('R02','to_store',0,10,2,4,'R03',8,14,'up')
transition('R03','to_lane',8,16,4,2,'R02',3,10,'right')
transition('R04','to_orchard',0,10,2,4,'R05',3,10,'right')
transition('R05','to_green',0,10,2,4,'R04',3,10,'right')
transition('R04','to_boundary',18,10,2,4,'R06',3,10,'right')
transition('R06','to_green',0,10,2,4,'R04',15,10,'left')

# Title never erases a slot. A new session keeps the old save until Save confirmation.
newgame=[*[setv(n,0) for n in VN if n not in ['AUDIO_OFF','REDUCED_SCARES','FAST_TEXT']],setv('SAVE_SCHEMA',1),setv('BUILD_SAVE_EPOCH',1),switch('R01',8,12,'up')]
loadgame=[e('EVENT_IF_SAVED_DATA',{'saveSlot':0},true=[e('EVENT_PEEK_DATA',{'saveSlot':0,'variableSource':V['SAVE_SCHEMA'],'variableDest':V['SCHEMA_PEEK']}),e('EVENT_PEEK_DATA',{'saveSlot':0,'variableSource':V['BUILD_SAVE_EPOCH'],'variableDest':V['EPOCH_PEEK']}),cond('SCHEMA_PEEK',1,[cond('EPOCH_PEEK',1,[e('EVENT_LOAD_DATA',{'saveSlot':0})],[text('Save is from another build family. It remains untouched.','Choose New Game to start a separate session.')])],[text('Save schema is incompatible. It remains untouched.','Choose New Game to start a separate session.')])],false=[text('No porch save yet. Choose New Game.')])]
title=[e('EVENT_HIDE_SPRITES'),e('EVENT_TEXT_SET_ANIMATION_SPEED',{'speedIn':0,'speedOut':0,'speed':0,'allowFastForward':True}),text('PocketHoller','After Sundown','Opening review build. Six rooms. One trusted light.'),e('EVENT_DEFINE_LABEL',{'label':'title-menu'}),menu(['New Game','Continue','Settings']),cond('MENU',1,[e('EVENT_IF_SAVED_DATA',{'saveSlot':0},true=[text('Begin a new session? The old save stays until you choose Save.'),menu(['Begin','Cancel'],'SUBMENU'),cond('SUBMENU',1,newgame)],false=newgame)]),cond('MENU',2,loadgame),cond('MENU',3,settings()),*release(),e('EVENT_GOTO_LABEL',{'label':'title-menu'})]
ops['TITLE'].append({'type':'scene.update','properties':{'script':title}})
ops['R01']=[{'type':'variable.upsert','variableId':v,'name':n,'symbol':'var_'+n.lower()} for n,v in V.items()]+ops['R01']
(ROOT/'tools/opening-batches.json').write_text(json.dumps({'scenes':S,'ops':ops,'variables':V},indent=2))
with (ROOT/'docs/variable-register.csv').open('w') as f:
    w=csv.writer(f);w.writerow(['id','name','status']);w.writerows((v,n,'reserved' if n.startswith(('P03','P04','P05','P06','P07','P08','P09','P10','P11','P12','J2','J3','J4','J5','J6','H')) or n in ['VISITED_R19','RECRUITED_TURTLE','RECRUITED_THUNDERBIRD','ENDING_SEEN'] else 'opening') for n,v in V.items())
with (ROOT/'docs/room-map.csv').open('w') as f:
    w=csv.writer(f);w.writerow(['room','native_scene_id','status','default_x','default_y']);w.writerows((c,S[c],'playable' if c!='TITLE' else 'UI',8,12) for c in S);w.writerows((f'R{i:02}','','planned',8,12) for i in range(7,25))
print({k:len(v) for k,v in ops.items()})
