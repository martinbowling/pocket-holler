"""Prepare semantic native edits; review output before applying to selected project."""
from pathlib import Path
import json,uuid,copy
ROOT=Path(__file__).resolve().parents[1]
r=json.loads((ROOT/'tools/characters-v2-resources.json').read_text())
A={k:v['id'] for k,v in r['assets'].items()};P={k:v['palette']['id'] for k,v in r['palettes'].items()}
namespace=uuid.UUID('1a53e8f5-fb71-49be-8294-8027599c5157');counter=0
def uid(key):return str(uuid.uuid5(namespace,key))
def e(cmd,args=None,**children):
    global counter
    counter+=1;v={'id':uid('event-'+str(counter)),'command':cmd,'args':args or {}}
    if children:v['children']=children
    return v
def cond(var,value,yes,no=None):return e('EVENT_IF',{'condition':{'type':'eq','valueA':{'type':'variable','value':str(var)},'valueB':{'type':'number','value':value}}},true=yes,false=no or [])
def text(s):return e('EVENT_TEXT',{'text':s,'minHeight':4,'maxHeight':4,'textHeight':3,'closeButton':'a'})
def setchar(n):return e('EVENT_SET_VALUE',{'variable':'52','value':{'type':'number','value':n}})
def visible(actor,on):return [e('EVENT_ACTOR_ACTIVATE' if on else 'EVENT_ACTOR_DEACTIVATE',{'actorId':actor}),e('EVENT_ACTOR_SHOW' if on else 'EVENT_ACTOR_HIDE',{'actorId':actor}),e('EVENT_ACTOR_COLLISIONS_ENABLE' if on else 'EVENT_ACTOR_COLLISIONS_DISABLE',{'actorId':actor})]
M='795d548a-b918-5d0a-bcea-399f69dfb5ee';R=uid('roam-porch-actor')
def apply_char(porch=False):
    def branch(name,palette):
        return [e('EVENT_PLAYER_SET_SPRITE',{'spriteSheetId':A[name]}),e('EVENT_PALETTE_SET_SPRITE',{'palette0':P[palette],**{f'palette{i}':'keep' for i in range(1,8)}})]
    m=branch('marty','Marty orange');ro=branch('roam','Roam green')
    if porch:m+=visible(M,False)+visible(R,True);ro+=visible(R,False)+visible(M,True)
    return cond(52,1,m,ro)
def select_char():
    return [e('EVENT_MENU',{'variable':'44','items':3,'layout':'menu','cancelOnB':True,'cancelOnLastOption':False,'option1':'ROAM','option2':'MARTY','option3':'BACK'}),cond(44,1,[setchar(0),apply_char(True),text('ROAM IS READY.\nGREEN JACKET,\nCURIOUS EYES.')]),cond(44,2,[setchar(1),apply_char(True),text('MARTY IS READY.\nORANGE JACKET,\nSTEADY STEPS.')])]
ops=[];porch=json.loads((ROOT/'project/scenes/start/scene.gbsres').read_text())['id']
ops.append({'sceneId':porch,'operations':[{'type':'variable.upsert','variableId':'52','name':'PLAYER_CHARACTER','properties':{'symbol':'var_player_character'}}]})
# Preserve all existing gameplay IDs; replace only displayed name text.
for p in sorted((ROOT/'project/scenes').rglob('*.gbsres')):
    d=json.loads(p.read_text());scene_id=json.loads((p.parent/'scene.gbsres' if p.name=='scene.gbsres' else p.parent.parent/'scene.gbsres').read_text())['id']
    target={'sceneId':scene_id,'scriptKey':'script'}
    if d['_resourceType']=='actor':target['actorId']=d['id']
    if d['_resourceType']=='trigger':target['triggerId']=d['id']
    def walk(x,path=[]):
        if isinstance(x,list):
            for event in x:
                if not isinstance(event,dict):continue
                a=event.get('args',{})
                if event.get('command')=='EVENT_TEXT' and 'ROAMIN' in str(a.get('text','')):
                    value=a['text'];value=[t.replace('ROAMIN','ROAM') for t in value] if isinstance(value,list) else value.replace('ROAMIN','ROAM')
                    ops.append({'sceneId':scene_id,'operations':[{'type':'event.edit','action':'update','eventId':event['id'],'target':{**target,'branchPath':path},'patch':{'args':{**a,'text':value}}}]})
                for name,branch in event.get('children',{}).items():walk(branch,path+[{'eventId':event['id'],'branch':name}])
    walk(d.get('script',[]))
    if d['_resourceType']=='scene' and not d['name'].startswith('TITLE'):
        ops.append({'sceneId':scene_id,'operations':[{'type':'scene.update','properties':{'spritePaletteIds':[P['Roam green'],P['Moth orange']]}},{'type':'event.edit','action':'insert','index':1,'target':{'sceneId':scene_id,'scriptKey':'script'},'event':apply_char(scene_id==porch)}]})
    if d['_resourceType']=='actor' and d['name']=='Moth':ops.append({'sceneId':scene_id,'operations':[{'type':'actor.update','actorId':d['id'],'spriteSheetId':A['moth'],'properties':{'paletteId':P['Moth orange']}}]})
    if d['_resourceType']=='actor' and d['name']=='Marty':
        script=d['script'];menu=script[1];menu['args'].update(items=5,option5='CHARACTER')
        script.insert(5,cond(43,5,select_char()))
        ops.append({'sceneId':porch,'operations':[{'type':'actor.update','actorId':M,'spriteSheetId':A['marty'],'properties':{'paletteId':P['Marty orange'],'script':script}}]})
        clone=copy.deepcopy(script)
        def rekey(x,path=''):
            if isinstance(x,dict):
                if 'command' in x:x['id']=uid('roam-guide'+path)
                for k,v in x.items():rekey(v,path+'/'+k)
            elif isinstance(x,list):
                for i,v in enumerate(x):rekey(v,path+'/'+str(i))
        rekey(clone)
        clone[0]=text('ROAM: I WILL\nWATCH THE PORCH.\nCAMP IS SAFE.')
        ops.append({'sceneId':porch,'operations':[{'type':'actor.create','id':R,'name':'Roam at porch','x':8,'y':8,'spriteSheetId':A['roam'],'direction':'down','properties':{'paletteId':P['Roam green'],'script':clone,'collisionGroup':''}}]})
(ROOT/'tools/characters-v2-operations.json').write_text(json.dumps(ops))
print(json.dumps({'batches':len(ops),'roamPorchActorId':R}))
