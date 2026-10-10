"""Assemble reviewable resource proposals, never write the active project.

Run only from this staging folder. The output is a patch plan requiring a
successful authorized ModRetro project selection before integration/build.
"""
from pathlib import Path
import copy,json,hashlib
from full_game_support import Helpers,SOURCE,uid,EDGES,ROOM_NAMES

HERE=Path(__file__).resolve().parent
def gather():
    from creek import build as creek
    from ridge_hollow import build as ridge
    h=Helpers();rooms=creek(h);rooms.update(ridge(h))
    rooms['R24']={'actors':[
        {'key':'porch_note','x':4,'y':8,'sprite':'sign','script':[h.cond('J2',0,[h.setv('J2',1),h.text('Journal 2: The porch note.','A lamp means a place is ready to welcome you.','We leave this one lit for whoever comes home next.')],[h.text('Your journal has the porch note.')])]},
        {'key':'breakfast','x':12,'y':8,'sprite':'lantern','script':[h.cond('P12',1,[h.text('Three empty bowls. Three sleepy companions.','Warm toast, apple jam, and a little sunlight on the table.')],[h.text('The table is ready for morning. Nobody has to earn a place here.')])]}], 'abilityTargets':[], 'onEnter':[]}
    reunion=[h.cond('ENDING_SEEN',0,[h.text('The real porch lamp burns steady. A familiar voice welcomes you.','You checked the clues, trusted your friends, and brought the light home.','Moth lands by the window. Turtle finds a sunny patch. Thunderbird steals toast.'),h.text('PocketHoller: After Sundown','An original family adventure. Built for Marty and Roam.','Native game: PocketHoller team. Engine: GB Studio. See source credits.','Morning again. Thank you for playing.'),h.setv('ENDING_SEEN',1),h.setv('CAMP_ID',0),h.text('Save now to continue from the peaceful dawn.')]+h.save('R01',0))]
    common={}
    for code,n in [('R01',0),('R07',1),('R13',2),('R19',3)]:
        checkpoint=h.e('EVENT_IF',{'condition':{'type':'gt','valueA':h.var('CHAPTER'),'valueB':h.var('LAST_CHECKPOINT')}},true=[h.text('A chapter light is repaired. Save here before the next trail.')]+h.save(code,n),false=[])
        common[code]={'onEnter':[h.setv('CAMP_ID',n),checkpoint],'campScript':h.camp(code,n)}
        if code=='R19':common[code]['onEnter']+=[h.cond('VISITED_R19',0,[h.setv('VISITED_R19',1),h.text('The roots open a dry trail back to your porch.','All three companions can help here. Save before ringing the bell.')])]
        if code=='R01':common[code]['reunionScript']=[h.cond('P12',1,reunion)]
    return h,rooms,common

def normalize_events(value,path='proposal'):
    """New proposed events get unique IDs even if a helper branch was reused."""
    if isinstance(value,dict):
        if 'command' in value:value['id']=uid('staged/'+path)
        for key,v in value.items():
            if key!='id':normalize_events(v,path+'/'+key)
    elif isinstance(value,list):
        for i,v in enumerate(value):normalize_events(v,path+'/'+str(i))

def main():
    h,rooms,common=gather()
    shared={'objective':h.objective(),'journal':h.journal(),'settings':h.settings(),'pause':h.pause()}
    proposal={'format':'pocketholler-full-game-proposal/v1','sourceRoot':str(SOURCE),
        'integrationAllowed':False,'reason':'Relocated project selection refused PATH_OUTSIDE_PROJECT; awaiting authorized plugin reconnection',
        'baseRomSha256':hashlib.sha256((SOURCE/'dist/PocketHoller-opening.gbc').read_bytes()).hexdigest(),
        'sceneIds':h.scenes,'variables':h.variables,'rooms':rooms,'common':common,'shared':shared,
        'connections':[{'from':a,'edge':ae,'to':b,'returnEdge':be,'unlock':gate} for a,ae,b,be,gate in EDGES],
        'roomNames':dict(zip([f'R{i:02}' for i in range(1,25)],ROOM_NAMES)),
        'saveEpoch':2,'oldOpeningSavesCompatible':False,'releaseReady':False}
    # A JSON round trip breaks aliases before assigning per-placement IDs.
    proposal=json.loads(json.dumps(proposal))
    normalize_events(proposal)
    (HERE/'full-game-proposal.json').write_text(json.dumps(proposal,indent=2)+'\n')
    print(json.dumps({'preparedRooms':len(rooms),'totalPlannedPlayableRooms':24,'newVariables':len(h.V)-53,'proposal':str(HERE/'full-game-proposal.json'),'integrated':False,'compiled':False}))

if __name__=='__main__':main()
