"""Shared native full-game event helpers. Imports never write resources."""
from pathlib import Path
import json, textwrap, uuid

BASE=Path(__file__).resolve().parent
SOURCE=next(parent for parent in BASE.parents if (parent/'project.gbsproj').is_file())
NS=uuid.UUID('242bfbbd-8a64-480b-bc32-d59c0f24647a')
def uid(key):return str(uuid.uuid5(NS,key))
def copy_events(events):return json.loads(json.dumps(events))

NEW_VARIABLES=['REED_STAGE','STONE_STAGE','INLET','BYPASS','OUTLET','SPILLWAY_READY',
    'VANEA','VANEB','RELAY_STAGE','PLAQUE_A','PLAQUE_B','PLAQUE_C','CHANNEL_A',
    'CHANNEL_B','BELL_LAMPS','LAMP_A','LAMP_B','LAMP_C','MUSIC_OFF','EFFECTS_OFF',
    'SWAP_BUTTONS','HINT_LEVEL','LAST_CHECKPOINT','CREDITS_PAGE']

class Helpers:
    def __init__(self):
        self.counter=0
        self.variables=json.loads((SOURCE/'project/variables.gbsres').read_text())
        self.V={v['name']:v['id'] for v in self.variables['variables']}
        for name in NEW_VARIABLES:
            if name not in self.V:
                n=str(max(map(int,self.V.values()))+1)
                self.V[name]=n
                self.variables['variables'].append({'id':n,'name':name,'symbol':'var_'+name.lower()})
        self.scenes={}
        for path in (SOURCE/'project/scenes').glob('*/scene.gbsres'):
            d=json.loads(path.read_text());code=d['name'].split()[0]
            self.scenes[code]=d['id']
        for i in range(7,25):self.scenes[f'R{i:02}']=uid(f'scene-R{i:02}')
    def e(self,command,args=None,**branches):
        self.counter+=1
        event={'id':uid('event-full-'+str(self.counter)),'command':command,'args':args or {}}
        if branches:event['children']=branches
        if command=='EVENT_ACTOR_HIDE':
            # Hiding does not clear native top-down collision. Keep both
            # operations together in a supported compile-time event group.
            return self.e('EVENT_GROUP',true=[event,self.e('EVENT_ACTOR_COLLISIONS_DISABLE',{'actorId':event['args']['actorId']})])
        return event
    def num(self,n):return {'type':'number','value':n}
    def var(self,n):return {'type':'variable','value':self.V[n]}
    def setv(self,n,value):return self.e('EVENT_SET_VALUE',{'variable':self.V[n],'value':self.num(value)})
    def cond(self,n,value,true,false=None,op='eq'):
        return self.e('EVENT_IF',{'condition':{'type':op,'valueA':self.var(n),'valueB':self.num(value)}},true=true,false=false or [])
    def text(self,*pages):
        out=[]
        for page in pages:
            lines=textwrap.wrap(page.upper(),16,break_long_words=False,break_on_hyphens=False) or ['']
            for i in range(0,len(lines),3):out.append('\n'.join(lines[i:i+3]))
        return self.e('EVENT_TEXT',{'text':out[0] if len(out)==1 else out,'minHeight':4,'maxHeight':4,'textHeight':3,'closeButton':'a'})
    def actor_id(self,code,key):return uid(code+'-actor-'+key)
    def hide(self,code,key):return self.e('EVENT_ACTOR_HIDE',{'actorId':self.actor_id(code,key)})
    def show(self,code,key):return self.e('EVENT_ACTOR_SHOW',{'actorId':self.actor_id(code,key)})
    def menu(self,options,variable='SUBMENU'):
        return self.e('EVENT_MENU',{'variable':self.V[variable],'items':len(options),'layout':'menu','cancelOnB':True,'cancelOnLastOption':False,**{f'option{i+1}':v.upper() for i,v in enumerate(options)}})
    def sound(self,kind='success'):
        pitch={'success':6,'steady':3,'spark':7,'reveal':5,'click':2,'bell':5}.get(kind,4)
        effect=self.e('EVENT_SOUND_PLAY_EFFECT',{'type':'beep','pitch':pitch,'duration':0.12,'wait':False,'priority':'low'})
        return self.cond('AUDIO_OFF',0,[self.cond('EFFECTS_OFF',0,[effect])])
    def switch(self,code,x,y,direction):
        return self.e('EVENT_SWITCH_SCENE',{'sceneId':self.scenes[code],'x':self.num(x),'y':self.num(y),'direction':direction,'fadeSpeed':'2'})
    def wait(self,n=1):return self.e('EVENT_WAIT',{'units':'frames','frames':self.num(n)})
    def release(self):
        label=uid('release-'+str(self.counter))
        return [self.e('EVENT_DEFINE_LABEL',{'label':label}),self.e('EVENT_IF_INPUT',{'input':['a','b','start','select','up','down','left','right']},true=[self.wait(),self.e('EVENT_GOTO_LABEL',{'label':label})],false=[])]
    def lock(self):return self.e('EVENT_SCRIPT_LOCK')
    def unlock(self):return self.e('EVENT_SCRIPT_UNLOCK')
    def objective(self):
        goals=[('P01','Ask June. Turn the orchard screen EAST, then inspect the lantern.'),
            ('P02','Reveal the boundary plaque with Moth. Use the ray latch.'),
            ('P03','Creek reedbank: open upstream, then downstream gates.'),
            ('P04','Causeway: use Turtle at wave stones from near to far.'),
            ('P05','Wheelhouse: inlet open, bypass closed, outlet open. Steady brace.'),
            ('P06','Creek light: steady spillway, then turn its crank.'),
            ('P07','Ridge roost: turn shelter vanes toward the perch.'),
            ('P08','Relay yard: Spark leaf, wave, then star with Thunderbird.'),
            ('P09','Echo hall: Reveal three plaques. The bell calls people home.'),
            ('P10','Spring: turn both channels toward the bell, then Steady.'),
            ('P11','Bell chamber: Spark all three ceramic lamps.'),
            ('P12','At the bell, choose Ring for everyone when ready.'),
            ('ENDING_SEEN','Go home for breakfast and the dawn reunion.')]
        result=[self.text('Morning again. Explore calm rooms for any journal pages.')]
        for flag,goal in reversed(goals):result=[self.cond(flag,0,[self.text('Next: '+goal)],result)]
        return result
    def journal(self):
        pages=['Town lantern tradition. Each autumn, everyone answers with their own light.',
            'Porch note. A lamp means a place is ready to welcome you.',
            'Trail sketch. Safe camps connect the creek, ridge and roots.',
            'Bell rhyme. Water turns; lamps burn; ring and return.',
            'Caught voices. The old bell kept echoes after people went home.',
            'Dawn drawing. Three companions asleep beside the breakfast table.']
        return self.objective()+[self.cond('P02',1,[self.text('Light 1: LIT')],[self.text('Light 1: WAITING')]),self.cond('P06',1,[self.text('Light 2: LIT')],[self.text('Light 2: WAITING')]),self.cond('P08',1,[self.text('Light 3: LIT')],[self.text('Light 3: WAITING')])]+[self.cond(flag,1,[self.text(name+': '+verb)]) for flag,name,verb in [('RECRUITED_MOTH','Moth','Reveal ray marks. Living glow tells the truth.'),('RECRUITED_TURTLE','Turtle','Steady wave stones. Braces stay fixed after you leave.'),('RECRUITED_THUNDERBIRD','Thunderbird','Spark safe zigzag fixtures. No charges or fuel.')]]+[self.cond('J'+str(i),1,[self.text('Journal '+str(i)+': '+v)]) for i,v in enumerate(pages,1)]
    def companion_menu(self):
        choices=[(1,'Moth','RECRUITED_MOTH'),(2,'Turtle','RECRUITED_TURTLE'),(3,'Thunderbird','RECRUITED_THUNDERBIRD')]
        def available(recruited):
            if not recruited:return [self.text('No companions yet. A warm light waits in the orchard.')]
            result=[self.menu([name for _,name,_ in recruited]+['Travel alone','Leave'])]
            for option,(value,name,_) in enumerate(recruited,1):
                verb=['Reveal ray marks','Steady wave stones','Spark zigzag sockets'][value-1]
                result.append(self.cond('SUBMENU',option,[self.setv('ACTIVE_COMPANION',value),self.text(name+' joins you. '+verb+'.')]))
            return result+[self.cond('SUBMENU',len(recruited)+1,[self.setv('ACTIVE_COMPANION',0),self.text('Everyone rests safely. Swap freely at a lit camp.')])]
        def branch(index,recruited):
            if index==len(choices):return available(recruited)
            choice=choices[index]
            return [self.cond(choice[2],1,branch(index+1,recruited+[choice]),branch(index+1,recruited))]
        return branch(0,[])
    def return_camp(self):
        # Dawn reunion must never be skipped by returning to the final camp.
        normal=[self.switch('R01',8,12,'up')]
        for n,room in reversed([(1,'R07'),(2,'R13'),(3,'R19')]):normal=[self.cond('CAMP_ID',n,[self.switch(room,8,12,'up')],normal)]
        return [self.cond('P12',1,[self.switch('R01',8,12,'up')],normal)]
    def save(self,code,camp_id):
        load=[self.setv(n,0) for n in ['REED_STAGE','STONE_STAGE','INLET','BYPASS','OUTLET','SPILLWAY_READY','VANEA','VANEB','RELAY_STAGE','PLAQUE_A','PLAQUE_B','PLAQUE_C','CHANNEL_A','CHANNEL_B','BELL_LAMPS','LAMP_A','LAMP_B','LAMP_C','MENU','SUBMENU','TARGET_USED']]
        # Later milestones imply every earlier puzzle and recruited companion.
        for milestone,last in [('P12',12),('P08',8),('P07',7),('P06',6),('P03',3),('P02',2)]:
            repairs=[self.setv('P'+str(i).zfill(2),1) for i in range(1,last+1)]
            repairs+=[self.setv('RECRUITED_MOTH',1)]
            if last>=3:repairs+=[self.setv('RECRUITED_TURTLE',1)]
            if last>=7:repairs+=[self.setv('RECRUITED_THUNDERBIRD',1)]
            load.append(self.cond(milestone,1,repairs))
        fallback=[self.cond('RECRUITED_MOTH',1,[self.setv('ACTIVE_COMPANION',1)],[self.setv('ACTIVE_COMPANION',0)])]
        for value,flag in [(1,'RECRUITED_MOTH'),(2,'RECRUITED_TURTLE'),(3,'RECRUITED_THUNDERBIRD')]:
            load.append(self.cond('ACTIVE_COMPANION',value,[self.cond(flag,0,copy_events(fallback))]))
        load.append(self.cond('ACTIVE_COMPANION',3,copy_events(fallback),op='gt'))
        load.append(self.cond('ACTIVE_COMPANION',0,copy_events(fallback),op='lt'))
        # Permanent progression determines the recovered chapter and time.
        load += [self.cond('P12',1,[self.setv('CHAPTER',4),self.setv('PHASE',3)],[self.cond('P08',1,[self.setv('CHAPTER',3),self.setv('PHASE',2)],[self.cond('P06',1,[self.setv('CHAPTER',2),self.setv('PHASE',2)],[self.cond('P02',1,[self.setv('CHAPTER',1),self.setv('PHASE',1)],[self.setv('CHAPTER',0),self.setv('PHASE',0)])])])]),self.e('EVENT_SCENE_UPDATE_RESUME')]+self.return_camp()
        return [self.text('Save at this camp? This replaces the single save slot.'),self.menu(['Save','Cancel']),self.cond('SUBMENU',1,[self.setv('SAVE_SCHEMA',1),self.setv('BUILD_SAVE_EPOCH',2),self.setv('CAMP_ID',camp_id),self.e('EVENT_SET_VALUE',{'variable':self.V['LAST_CHECKPOINT'],'value':self.var('CHAPTER')}),self.e('EVENT_ACTOR_SET_POSITION',{'actorId':'player','x':self.num(8),'y':self.num(12),'units':'tiles'}),self.e('EVENT_SAVE_DATA',{'saveSlot':0},true=[self.setv('SESSION_REPLACES_SAVE',0),self.text('Saved at '+code+'. You may turn the game off.')],load=load)])]
    def hints(self):
        clues=[('P01','The vane shows the wind. Shelter the lantern.'),
            ('P02','Paint can point the wrong way. Trust the ray mark.'),
            ('P03','Leaves show which reed gate the water meets first.'),
            ('P04','Three safe stations follow the bank from near to far.'),
            ('P05','A branch can steal the flow before it reaches the wheel.'),
            ('P06','The crank needs water power held steady.'),
            ('P07','Both shelter vanes need to face the same perch.'),
            ('P08','The relay board shows a leaf, a wave, and a star.'),
            ('P09','Three plaques describe what the bell should do.'),
            ('P10','Both streams should turn toward the bell spring.'),
            ('P11','Every ceramic lamp needs the same living spark.'),
            ('P12','The bell can call everyone home. Save before you choose.')]
        nudge=[self.text('The real porch light will welcome you home.')]
        for flag,line in reversed(clues):nudge=[self.cond(flag,0,[self.text(line)],nudge)]
        return nudge+[self.menu(['More help','Leave']),self.cond('SUBMENU',1,self.objective())]
    def camp(self,code,camp_id):
        char=[self.menu(['Roam','Marty','Leave'])]
        for n in [1,2]:char.append(self.cond('SUBMENU',n,[self.setv('PLAYER_CHARACTER',n-1),self.text(('Roam' if n==1 else 'Marty')+' takes the trail. Progress stays with both of you.'),self.switch(code,8,12,'up')]))
        return [self.menu(['Companion','Character','Hint','Save','Leave'],'MENU'),self.cond('MENU',1,self.companion_menu()),self.cond('MENU',2,char),self.cond('MENU',3,self.hints()),self.cond('MENU',4,self.save(code,camp_id))]
    def settings(self):
        result=[self.menu(['Music','Effects','Scares','Text','Controls','Quiet preset','Leave'])]
        for n,name in [(1,'MUSIC_OFF'),(2,'EFFECTS_OFF'),(3,'REDUCED_SCARES'),(5,'SWAP_BUTTONS')]:
            on=[self.setv(name,0)]
            if name in ['MUSIC_OFF','EFFECTS_OFF']:on+=[self.setv('AUDIO_OFF',0)]
            result.append(self.cond('SUBMENU',n,[self.cond(name,0,[self.setv(name,1),self.text({'MUSIC_OFF':'Music off.','EFFECTS_OFF':'Effects off.','REDUCED_SCARES':'Reduced Scares. All clues remain.','SWAP_BUTTONS':'Actions swapped: B acts, A uses abilities. Menus: A confirms, B backs out.'}[name])],on+[self.text({'MUSIC_OFF':'Music on.','EFFECTS_OFF':'Effects on.','REDUCED_SCARES':'Standard Scares. No flashing or shake.','SWAP_BUTTONS':'Standard: A acts, B uses abilities. Menus: A confirms, B backs out.'}[name])])]))
        result += [self.cond('SUBMENU',4,[self.menu(['Normal','Fast','Instant','Leave']),self.cond('SUBMENU',1,[self.setv('FAST_TEXT',0)]),self.cond('SUBMENU',2,[self.setv('FAST_TEXT',1)]),self.cond('SUBMENU',3,[self.setv('FAST_TEXT',2)])]),self.cond('SUBMENU',6,[self.setv('MUSIC_OFF',1),self.setv('EFFECTS_OFF',1),self.setv('AUDIO_OFF',1),self.text('Quiet preset. Every clue stays visible.')])]
        from common_runtime import apply_options
        return result+apply_options(self)
    def pause(self):
        return [self.lock(),self.e('EVENT_SCENE_UPDATE_PAUSE'),self.menu(['Journal','Settings','Return to Camp','Quit','Resume'],'MENU'),self.cond('MENU',1,self.journal()),self.cond('MENU',2,self.settings()),self.cond('MENU',3,[self.text('Return to camp? Progress stays. This does not save.'),self.menu(['Return','Cancel']),self.cond('SUBMENU',1,[self.e('EVENT_SCENE_UPDATE_RESUME')]+self.return_camp())]),self.cond('MENU',4,[self.text('Quit to title? Unsaved progress will be lost.'),self.menu(['Quit','Cancel']),self.cond('SUBMENU',1,[self.e('EVENT_SCENE_UPDATE_RESUME'),self.switch('TITLE',8,12,'up')])]),self.e('EVENT_SCENE_UPDATE_RESUME')]+self.release()+[self.unlock()]

# (room A, edge, room B, return edge, permanent unlock flag). Every return
# remains open independently of the currently selected companion.
EDGES=[('R01','south','R02','north',None),('R01','west','R24','east',None),
 ('R02','south','R04','north',None),('R02','west','R03','south',None),
 ('R04','west','R05','east',None),('R04','east','R06','west',None),
 ('R06','north','R07','south','P02'),('R07','north','R08','south',None),
 ('R08','north','R09','south',None),('R09','north','R10','south','P03'),
 ('R10','north','R11','south','P04'),('R11','north','R12','south','P05'),
 ('R12','north','R13','south','P06'),('R12','west','R07','east','P06'),
 ('R13','north','R14','south',None),('R14','north','R15','south',None),
 ('R15','north','R16','south','P07'),('R16','north','R17','south','P08'),
 ('R16','west','R13','east','P08'),('R17','north','R18','south',None),
 ('R18','north','R19','south','P08'),('R19','west','R20','east',None),
 ('R19','east','R21','west',None),('R19','north','R22','south',None),
 ('R19','shortcut','R01','shortcut','VISITED_R19'),
 ('R23','south','R04','dawn','P12')]

ROOM_NAMES=['Home porch','Town lane','General store','Festival green','Orchard',
 'Boundary gate','Creek camp','Mirror pool','Reedbank','Flooded causeway',
 'Wheelhouse','Creek light','Ridge camp','Bramble stairs','Thunder roost',
 'Relay yard','Bell road','Old noticehouse','Root threshold','Echo hall',
 'Spring chamber','Bell chamber','Dawn overlook','Porch interior']
