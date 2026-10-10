"""Replay a single-boot controller journal to full-motion video and native APU.

Every retained framebuffer hash must match. No memory writes, injected save,
external music, composited game frames or cuts are accepted.
"""
from pathlib import Path
import argparse,hashlib,json,re,shutil,subprocess,tempfile,wave
import numpy as np
from pyboy import PyBoy

ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parent
WORKSPACE=REPO.parent if REPO.name=='src' else REPO
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    ap=argparse.ArgumentParser();ap.add_argument('journal',type=Path);args=ap.parse_args()
    rows=[json.loads(s) for s in args.journal.read_text().splitlines()]
    original=json.loads((args.journal.parent/'report.json').read_text())
    assert original['passed'] and original['boots']==1
    assert original['state']['P12']==1 and original['state']['ENDING_SEEN']==1
    assert len([r for r in rows if r['kind']=='boot'])==1
    rom=ROOT/'dist/PocketHoller-full.gbc';identity=sha(rom)
    receipt=json.loads((ROOT/'evidence/full-build.json').read_text())
    assert identity==rows[0]['romSha256']==original['romSha256']==receipt['rom']['sha256']
    assert receipt['debugArtifacts']['romSha256']==identity
    out=WORKSPACE/'videos';out.mkdir(exist_ok=True)
    qa=Path(tempfile.mkdtemp(prefix='full-video-render-',dir=ROOT/'evidence'))
    cart=qa/rom.name;shutil.copy2(rom,cart)
    video=qa/'picture.mp4';audio=qa/'native-audio.wav';dest=out/'PocketHoller-full-playthrough.mp4'
    log=(qa/'encoder.log').open('w')
    enc=subprocess.Popen(['ffmpeg','-hide_banner','-loglevel','warning','-y','-f','rawvideo','-pix_fmt','rgb24',
        '-s','160x144','-r','262144/4389','-i','pipe:0','-an','-vf','scale=640:576:flags=neighbor',
        '-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(video)],stdin=subprocess.PIPE,stderr=log)
    p=PyBoy(str(cart),window='null',sound_emulated=True,sound_sample_rate=48000,cgb=True);p.set_emulation_speed(0)
    wav=wave.open(str(audio),'wb');wav.setnchannels(2);wav.setsampwidth(2);wav.setframerate(48000)
    fps=4194304/70224;frame=0;samples=0;peak=0;energy=0;matched=0;held=set();pending_end=0
    def advance(target):
        nonlocal frame,samples,peak,energy
        assert frame<=target<=pending_end,('Journal interval out of order',frame,target,pending_end)
        while frame<target:
            p.tick(1,True);frame+=1;enc.stdin.write(p.screen.ndarray[:,:,:3].tobytes())
            raw=p.sound.ndarray.astype(np.float64);count=round(frame*48000/fps)-samples
            if len(raw):
                pos=np.linspace(0,len(raw)-1,count)
                pcm=np.stack([np.interp(pos,np.arange(len(raw)),raw[:,c]) for c in [0,1]],axis=1)
            else:pcm=np.zeros((count,2))
            pcm=np.clip(np.rint(pcm*256),-32768,32767).astype('<i2')
            peak=max(peak,int(np.abs(pcm.astype(np.int32)).max()));energy+=float(np.square(pcm.astype(np.float64)).sum())
            wav.writeframesraw(pcm.tobytes());samples+=count
    for row in rows[1:]:
        if row['kind']=='action':
            advance(pending_end)
            assert row['frame']==frame
            new=set(row['buttons']);assert new<={'up','down','left','right','a','b','start','select'}
            for b in held-new:p.button_release(b)
            for b in new-held:p.button_press(b)
            held=new
            pending_end=frame+row['frames']
        elif row['kind']=='frame':
            advance(row['frame'])
            assert row['frame']==frame,(row['frame'],frame)
            assert hashlib.sha256(p.screen.image.convert('RGBA').tobytes()).hexdigest()==row['rgbaSha256'],('Framebuffer differs',frame)
            matched+=1
    advance(pending_end)
    assert frame==original['frames'] and peak>0
    p.screen.image.save(out/'full-playthrough-final-frame.png')
    symbols=(ROOT/'dist/PocketHoller-full.gbc.debug/symbols.noi').read_text();glob=(ROOT/'dist/PocketHoller-full.gbc.debug/globals.i').read_text()
    base=int(re.search(r'DEF _script_memory 0x([0-9A-Fa-f]+)',symbols)[1],16);state={}
    for name in ['PLAYER_CHARACTER','ACTIVE_COMPANION','CURRENT_ROOM','PHASE','ENDING_SEEN']+[f'P{i:02}' for i in range(1,13)]:
        idx=int(re.search(r'VAR_'+name+r'\s*=\s*(\d+)',glob)[1]);a=base+2*idx;state[name]=p.memory[a]+256*p.memory[a+1]
    assert state['ENDING_SEEN']==1 and state['PHASE']==3 and all(state[f'P{i:02}']==1 for i in range(1,13))
    p.stop(save=False);enc.stdin.close();assert enc.wait()==0;wav.close();log.close()
    subprocess.run(['ffmpeg','-hide_banner','-loglevel','warning','-y','-i',str(video),'-i',str(audio),'-map','0:v:0','-map','1:a:0',
        '-c:v','copy','-c:a','aac','-b:a','160k','-af','highpass=f=20','-movflags','+faststart',
        '-metadata','title=PocketHoller: After Sundown full native playthrough',str(dest)],check=True)
    probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(dest)]))
    vs=next(s for s in probe['streams'] if s['codec_type']=='video');aas=next(s for s in probe['streams'] if s['codec_type']=='audio')
    assert vs['width']==640 and vs['height']==576 and int(vs['nb_frames'])==frame
    assert abs(float(vs['duration'])-float(aas['duration']))<0.1
    report={'romSha256':identity,'video':str(dest),'videoSha256':sha(dest),'journal':str(args.journal),'journalSha256':sha(args.journal),
        'frames':frame,'matchedFrameSamples':matched,'durationSeconds':frame/fps,'fps':fps,'nativeDimensions':[160,144],'outputDimensions':[640,576],
        'audio':'Native emulated APU, frame-aligned 48kHz PCM and 20Hz DC filter; no added music',
        'audioPeakPCM16':peak,'audioRMSPCM16':(energy/(samples*2))**0.5,'finalState':state,'singleBoot':True,'cuts':False,
        'memoryWrites':False,'audioListeningTested':False,'physicalCapture':False,'probe':probe}
    (out/'full-playthrough-report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='probe'},indent=2))
if __name__=='__main__':main()
