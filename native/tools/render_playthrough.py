"""Encode a genuine input-driven emulator recording as full-motion H.264/AAC.
Replays the retained ordinary controller journal, verifies every sampled RGBA
hash, and captures every framebuffer plus the native APU output. No save or
emulator memory writes, artificial backgrounds, commentary, music or cuts.
"""
from pathlib import Path
import hashlib,json,subprocess,tempfile,shutil,wave,re
import numpy as np
from pyboy import PyBoy
ROOT=Path(__file__).resolve().parents[1]
RECORD=ROOT/'evidence/video-playthrough-20261009'
OUT=ROOT.parent/'videos';OUT.mkdir(exist_ok=True)
rows=[json.loads(x) for x in (RECORD/'events.jsonl').read_text().splitlines()]
rom=ROOT/'dist/PocketHoller-opening.gbc'
identity=hashlib.sha256(rom.read_bytes()).hexdigest()
assert identity==rows[0]['rom']['sha256']
qa=Path(tempfile.mkdtemp(prefix='video-render-',dir=ROOT/'evidence'))
cart=qa/rom.name;shutil.copy2(rom,cart)
fps=4194304/70224;rate=48000
video=qa/'video-only.mp4';audio=qa/'game-audio.wav';dest=OUT/'PocketHoller-opening-playthrough.mp4'
log=(qa/'encoder.log').open('w')
enc=subprocess.Popen(['ffmpeg','-hide_banner','-loglevel','warning','-y','-f','rawvideo','-pix_fmt','rgb24',
    '-s','160x144','-r','262144/4389','-i','pipe:0','-an','-vf','scale=640:576:flags=neighbor',
    '-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(video)],
    stdin=subprocess.PIPE,stderr=log)
p=PyBoy(str(cart),window='null',sound_emulated=True,sound_sample_rate=rate,cgb=True)
p.set_emulation_speed(0)
wav=wave.open(str(audio),'wb');wav.setnchannels(2);wav.setsampwidth(2);wav.setframerate(rate)
frame=0;held=set();matched=0;audio_samples=0;source_audio_samples=0;audio_peak=0
def tick(n):
    global frame,audio_samples,source_audio_samples,audio_peak
    for _ in range(n):
        p.tick(1,True);frame+=1
        enc.stdin.write(p.screen.ndarray[:,:,:3].tobytes())
        raw=p.sound.ndarray.astype(np.float64)
        source_audio_samples+=len(raw)
        # Align each original APU buffer to this frame's exact hardware-clock
        # duration. Small sample-count fluctuations do not accumulate A/V drift.
        count=round(frame*rate/fps)-audio_samples
        if len(raw):
            pos=np.linspace(0,len(raw)-1,count)
            pcm=np.stack([np.interp(pos,np.arange(len(raw)),raw[:,c]) for c in [0,1]],axis=1)
        else:pcm=np.zeros((count,2))
        pcm=np.clip(np.rint(pcm*256),-32768,32767).astype('<i2')
        audio_peak=max(audio_peak,int(np.abs(pcm.astype(np.int32)).max()))
        wav.writeframesraw(pcm.tobytes());audio_samples+=count
tick(rows[0]['startingCondition']['initialFrames'])
for row in rows[1:]:
    if row['kind']=='action':
        action=row['action']
        if action['type']=='set_buttons':
            new=set(action['buttons'])
            for b in held-new:p.button_release(b)
            for b in new-held:p.button_press(b)
            held=new
        elif action['type']=='step':tick(action['frames'])
        else:raise AssertionError(('Non-controller action in recording',action))
    elif row['kind']=='frame':
        if row['frame']<rows[0]['startingCondition']['initialFrames']:
            continue  # Boot samples preceded the explicit controller journal.
        assert frame==row['frame'],(frame,row['frame'])
        digest=hashlib.sha256(p.screen.image.convert('RGBA').tobytes()).hexdigest()
        assert digest==row['rgbaSha256'],('Framebuffer differs',frame,digest,row['rgbaSha256'])
        matched+=1
assert frame==rows[-1]['totalFrames']
assert audio_peak>0,'Expected native game effects in APU capture'
p.screen.image.save(OUT/'playthrough-final-frame.png')
symbols=(ROOT/'dist/PocketHoller-opening.gbc.debug/symbols.noi').read_text()
glob=(ROOT/'dist/PocketHoller-opening.gbc.debug/globals.i').read_text()
base=int(re.search(r'DEF _script_memory 0x([0-9A-Fa-f]+)',symbols)[1],16)
state={}
for n in ['PLAYER_CHARACTER','CURRENT_ROOM','P01','P02','J1','RECRUITED_MOTH','MILESTONE_SAVED']:
    idx=int(re.search(r'VAR_'+n+r'\s*=\s*(\d+)',glob)[1]);a=base+2*idx
    state[n]=p.memory[a]+256*p.memory[a+1]
assert all(state[n]==1 for n in state),state
p.stop(save=False);enc.stdin.close();assert enc.wait()==0
wav.close();log.close()
subprocess.run(['ffmpeg','-hide_banner','-loglevel','warning','-y','-i',str(video),'-i',str(audio),
    '-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','160k','-af','highpass=f=20,volume=4',
    '-movflags','+faststart','-metadata','title=PocketHoller - After Sundown opening playthrough',str(dest)],check=True)
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(dest)]))
vs=next(s for s in probe['streams'] if s['codec_type']=='video');aas=next(s for s in probe['streams'] if s['codec_type']=='audio')
assert vs['width']==640 and vs['height']==576 and int(vs['nb_frames'])==frame
assert abs(float(vs['duration'])-float(aas['duration']))<0.1
report={'romSha256':identity,'recording':str(RECORD),'recordingJournalSha256':hashlib.sha256((RECORD/'events.jsonl').read_bytes()).hexdigest(),
    'video':str(dest),'videoSha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'runtime':'PyBoy 2.7.0',
    'sourceFrames':frame,'sampledFramesVerified':matched,'durationSeconds':frame/fps,'nativeSize':[160,144],
    'outputSize':[640,576],'scale':'4x nearest neighbor','fps':fps,'audio':'Original emulated game APU; frame-aligned PCM, 20 Hz DC filter, 12 dB playback gain, AAC',
    'audioSampleRate':rate,'sourceAudioSamples':source_audio_samples,'encodedAudioSamples':audio_samples,'audioPeakPCM16':audio_peak,
    'finalState':state,'memoryWrites':False,'cuts':False,'physicalCapture':False,'probe':probe}
(OUT/'playthrough-report.json').write_text(json.dumps(report,indent=2))
print(json.dumps({k:v for k,v in report.items() if k!='probe'},indent=2))
