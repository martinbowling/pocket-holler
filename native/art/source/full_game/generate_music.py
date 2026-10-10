"""Original compact PocketHoller soundtrack; no bundled song/template bytes.

The UGE v6 layout is derived from the installed official GB Studio
src/shared/lib/uge/ugeHelper.ts loadUGESong/saveUGESong implementation.
All note sequences, instruments, and wave samples below are original.
Output stays in this standalone art directory. Optional WAVs are compositional
previews, not Game Boy APU or built-ROM recordings.
"""
from pathlib import Path
import hashlib, json, math, struct, wave, uuid

HERE=Path(__file__).resolve().parent
U32=lambda n:struct.pack('<I',n)
U8=lambda n:struct.pack('B',n)
def text(s):
    data=s.encode('utf8');assert len(data)<256
    return U8(len(data))+data+bytes(255-len(data))

# Tracker note 0 is C3, not MIDI zero. None emits sentinel 90.
PITCH={'C':0,'Cs':1,'D':2,'Ds':3,'E':4,'F':5,'Fs':6,'G':7,'Gs':8,'A':9,'As':10,'B':11}
def note(s):
    if s is None:return 90
    return (int(s[-1])-3)*12+PITCH[s[:-1]]

# Sixteen notes per phrase, two phrases form the eight-bar loop.
# One melodic attack every four tracker rows; walking pulse is deliberately quiet.
SONGS={
'porch':{'title':'Porch lanterns','ticks':8,'key':'C major','chords':['C3','A3','F3','G3','C3','F3','G3','C3'],
    'melody':['E5','G5','A5','G5','E5','D5','C5',None,'F5','A5','G5','E5','D5','E5','G5',None,
              'E5','G5','C6','A5','G5','E5','F5',None,'D5','G5','A5','G5','E5','D5','C5',None]},
'creek':{'title':'Leaves on the creek','ticks':9,'key':'D Dorian','chords':['D3','G3','D3','C3','F3','G3','C3','D3'],
    'melody':['D5','F5','A5','G5','F5','E5','D5',None,'C5','D5','F5','E5','D5','A4','C5',None,
              'F5','A5','G5','F5','E5','D5','C5',None,'G5','E5','D5','C5','A4','C5','D5',None]},
'ridge':{'title':'Three ridge lamps','ticks':8,'key':'G major','chords':['G3','E3','C3','D3','G3','C3','D3','G3'],
    'melody':['G5','A5','B5','D6','B5','A5','G5',None,'E5','G5','A5','B5','A5','Fs5','D5',None,
              'B5','D6','E6','D6','B5','A5','G5',None,'A5','B5','D6','B5','A5','Fs5','G5',None]},
'hollow':{'title':'The spring remembers','ticks':10,'key':'A minor','chords':['A3','F3','D3','E3','A3','D3','F3','E3'],
    'melody':['A4',None,'E5',None,'C5',None,'B4',None,'A4',None,'D5',None,'C5',None,'B4',None,
              'C5',None,'E5',None,'D5',None,'C5',None,'B4',None,'E5',None,'B4',None,'A4',None]},
'dawn':{'title':'Breakfast after sundown','ticks':7,'key':'C major','chords':['C3','G3','A3','F3','C3','F3','G3','C3'],
    'melody':['C5','E5','G5','C6','B5','G5','E5',None,'A5','G5','E5','F5','G5','A5','G5',None,
              'E5','G5','C6','E6','D6','C6','A5',None,'F5','A5','G5','E5','D5','E5','C5',None]},
}

# Authored answering phrases lengthen the loops without repeating the same verse.
# Each list is an explicit melody; only the quiet accompaniment is patterned.
RESPONSES={
'porch':{'chords':['A3','F3','C3','G3','F3','G3','C3','C3'],
 'melody':['A5','C6','B5','A5','G5','F5','E5',None,'G5','A5','C6','B5','G5','E5','D5',None,
           'F5','E5','D5','C5','D5','E5','G5',None,'E5','D5','G5','E5','D5','C5','C5',None]},
'creek':{'chords':['G3','F3','D3','A3','C3','G3','A3','D3'],
 'melody':['A5','G5','F5','D5','E5','G5','F5',None,'E5','D5','C5','A4','C5','D5','F5',None,
           'G5','A5','C6','A5','G5','E5','F5',None,'E5','C5','A4','D5','F5','E5','D5',None]},
'ridge':{'chords':['E3','C3','A3','D3','C3','D3','G3','G3'],
 'melody':['E6','D6','B5','G5','A5','B5','D6',None,'E5','G5','B5','A5','G5','Fs5','E5',None,
           'C6','B5','A5','G5','A5','B5','D6',None,'B5','A5','Fs5','D5','G5','B5','G5',None]},
'hollow':{'chords':['D3','A3','F3','E3','D3','F3','E3','A3'],
 'melody':['D5',None,'F5',None,'E5',None,'C5',None,'D5',None,'A4',None,'B4',None,'E5',None,
           'F5',None,'E5',None,'D5',None,'C5',None,'B4',None,'C5',None,'E5',None,'A4',None]},
'dawn':{'chords':['A3','E3','F3','G3','F3','G3','C3','C3','C3','A3','F3','G3',
                 'A3','F3','C3','G3','F3','G3','C3','C3'],
 'melody':['A5','C6','E6','D6','C6','B5','A5',None,'G5','B5','E6','D6','B5','A5','G5',None,
           'F5','A5','C6','A5','G5','E5','D5',None,'E5','G5','C6','G5','E5','D5','C5',None,
           'C6','D6','E6','G6','E6','D6','C6',None,'B5','C6','E6','C6','A5','G5','E5',None,
           'F5','G5','A5','C6','A5','G5','F5',None,'E5','G5','C6','B5','A5','G5','E5',None,
           'F5','E5','D5','E5','G5','A5','G5',None,'E5','D5','G5','E5','D5','C5','C5',None]},
}
for song_name,response in RESPONSES.items():
    SONGS[song_name]['melody']+=response['melody']
    SONGS[song_name]['chords']+=response['chords']
    assert len(SONGS[song_name]['melody'])==len(SONGS[song_name]['chords'])*4

def instrument(kind,index):
    # Exactly 45 records: 15 pulse, 15 wave, 15 noise. Silent unused slots.
    selected=index==0 or (kind==0 and index==1)
    names={0:['Soft lantern pluck','Warm walking pulse'],1:['Round creek bass'],2:['Soft leaf brush']}
    name=names[kind][index] if selected else ''
    length=None if kind!=2 else 12
    volume=(5 if index==0 else 3) if kind==0 else (1 if kind==2 else 0)
    if not selected:volume=0
    duty=2 if index==0 else 1
    # Envelope falls slowly. Noise uses hardware length to avoid any hiss bed.
    envelope_step=7 if kind==0 and selected else 0
    out=U32(kind)+text(name)+U32((256 if kind==1 else 64)-length if length is not None else 0)
    out+=U8(length is not None)+U8(volume)+U32(1 if envelope_step else 0)+U8(envelope_step)
    out+=U32(0)+U32(0)+U32(0)+U8(duty if kind==0 else 0)
    out+=U32(3 if kind==1 and selected else 0)+U32(0)+U32(0)+U8(0)
    for _ in range(64):out+=U32(90)+U32(0)+U32(0)+U32(0)+U8(0)
    return out

def sequences(name,song):
    patterns=[];orders=[[],[],[],[]]
    for section in range(len(song['melody'])//16):
        channel_rows=[[[90,0,0,0] for _ in range(64)] for _ in range(4)]
        for row in range(64):
            global_row=section*64+row
            chord=song['chords'][global_row//16]
            bass=note(chord)
            if row%4==0:
                pitch=note(song['melody'][global_row//4])
                if pitch!=90:channel_rows[0][row]=[pitch,1,0,0]
            if row%8==0:
                # Fifths give gentle support without competing with the clue text.
                offset=12+(7 if (global_row//8)%2 else 0)
                channel_rows[1][row]=[bass+offset,2,0,0]
            if row%16==0:channel_rows[2][row]=[bass,1,0,0]
            if row%16==8:channel_rows[3][row]=[42,1,0,0]
        for channel in range(4):
            orders[channel].append(len(patterns));patterns.append(channel_rows[channel])
    return patterns,orders

def save_uge(name,song):
    patterns,orders=sequences(name,song)
    out=U32(6)+text(song['title'])+text('PocketHoller original soundtrack')+text('Original notes and instruments; edit freely in GB Studio music editor. No copied song data.')
    for kind in range(3):
        for n in range(15):out+=instrument(kind,n)
    # A soft asymmetric triangle waveform, 32 four-bit samples, not packed here.
    waveform=[4,4,5,5,6,7,8,9,10,11,12,12,11,10,9,8,7,6,5,4,3,3,2,2,3,3,4,4,4,4,4,4]
    out+=bytes(waveform)+bytes(32*15)
    out+=U32(song['ticks'])+U8(0)+U32(0)+U32(len(patterns))
    for pattern_id,pattern in enumerate(patterns):
        out+=U32(pattern_id)
        for pitch,instr,effect,param in pattern:
            out+=U32(pitch)+U32(instr)+U32(0)+U32(effect)+U8(param)
    for channel in range(4):
        out+=U32(len(orders[channel])+1)
        for p in orders[channel]:out+=U32(p)
        out+=U32(0)
    out+=bytes(16*4)
    path=HERE/'music'/f'{name}.uge';path.write_bytes(out)
    sequence={'name':name,'title':song['title'],'key':song['key'],'ticksPerRow':song['ticks'],
              'channels':['Pulse melody','Pulse supporting fifths','Wave bass','Noise brush'],
              'instrumentVolumes':{'pulse1':5,'pulse2':3,'waveLevel':3,'noise':1},
              'patterns':patterns,'orders':orders,'melody':song['melody'],'chords':song['chords'],
              'waveform':waveform,'approximateLoopSeconds':len(orders[0])*64*song['ticks']/59.7275,
              'sha256':hashlib.sha256(out).hexdigest(),'bytes':len(out),'ugeVersion':6}
    (HERE/'music'/f'{name}.sequence.json').write_text(json.dumps(sequence,indent=2)+'\n')
    sidecar={'_resourceType':'music','id':str(uuid.uuid5(uuid.NAMESPACE_URL,'PocketHoller/full-game/music/'+name)),
             'name':'PocketHoller '+song['title'],'symbol':'song_pocketholler_'+name,'settings':{},
             'filename':name+'.uge','type':'uge'}
    (HERE/'music'/f'{name}.uge.gbsres').write_text(json.dumps(sidecar,indent=2)+'\n')
    return sequence

def preview_wav(seq):
    """Readable composition preview only; actual playback must be verified in ROM."""
    sr=22050;seconds_per_row=seq['ticksPerRow']/59.7275
    samples=int(len(seq['orders'][0])*64*seconds_per_row*sr);audio=[0.0]*samples
    gains=[0.11,0.055,0.065,0.009]
    for channel in range(4):
        state=None
        for order,pattern_id in enumerate(seq['orders'][channel]):
            pattern=seq['patterns'][pattern_id]
            for row,cell in enumerate(pattern):
                pitch,instr,_,_=cell;start=int((order*64+row)*seconds_per_row*sr)
                end=min(samples,int((order*64+row+1)*seconds_per_row*sr))
                if pitch!=90:state=(pitch,start)
                if not state:continue
                freq=130.81278265*2**(state[0]/12)
                for t in range(start,end):
                    elapsed=(t-state[1])/sr
                    if channel==3:
                        if elapsed>12/256:continue
                        # Deterministic low-volume brush, no external sample.
                        signal=(1 if ((t*1103515245+12345)&0x10000) else -1)*math.exp(-elapsed*60)
                    else:
                        phase=elapsed*freq%1
                        if channel==2:signal=(1-4*abs(phase-.5))*.75
                        else:signal=(1 if phase<(0.5 if channel==0 else .25) else -1)*math.exp(-elapsed*1.8)
                        # Short attack avoids audible clicks in this approximate synth.
                        signal*=min(1,elapsed/.006)
                    audio[t]+=signal*gains[channel]
    peak=max(abs(v) for v in audio)
    pcm=b''.join(struct.pack('<h',int(max(-1,min(1,v))*32767)) for v in audio)
    with wave.open(str(HERE/'music'/f'{seq["name"]}-composition-preview.wav'),'wb') as f:
        f.setnchannels(1);f.setsampwidth(2);f.setframerate(sr);f.writeframes(pcm)
    return {'sampleRate':sr,'samples':samples,'peak':peak,'renderType':'Approximate composition synthesizer; not Game Boy APU capture'}

def main():
    (HERE/'music').mkdir(exist_ok=True)
    songs=[]
    for name,song in SONGS.items():
        seq=save_uge(name,song);seq['compositionPreview']=preview_wav(seq)
        songs.append({k:v for k,v in seq.items() if k not in ('patterns','orders','melody','chords','waveform')})
    manifest={'provenance':'Original composition, instruments and waveform; no template song or external audio sampled.',
              'formatReference':'Official installed GB Studio src/shared/lib/uge/ugeHelper.ts, version-6 save/load layout.',
              'validation':'Standalone proposals; parser/ROM playback checks reported separately.',
              'songs':songs,'recommendedRoomMusic':{'R01-R06':'porch','R07-R12':'creek','R13-R18':'ridge','R19-R22':'hollow','DAWN':'dawn','R24':'porch'}}
    (HERE/'music-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({'songs':len(songs),'bytes':sum(s['bytes'] for s in songs),'maxPreviewPeak':max(s['compositionPreview']['peak'] for s in songs)}))

if __name__=='__main__':main()
