"""Package only the opening source, tested cartridge and selected evidence."""
from pathlib import Path
import hashlib,json,zipfile,subprocess
ROOT=Path(__file__).resolve().parents[2];native=ROOT/'native'
WORKSPACE=ROOT.parent if ROOT.name=='src' else ROOT
def evidence(name):
    local=native/'evidence'/name
    return local if local.exists() else WORKSPACE/'native/evidence'/name
def archive_path(path):
    if path.is_relative_to(ROOT):return path.relative_to(ROOT).as_posix()
    return 'native/evidence/'+path.relative_to(WORKSPACE/'native/evidence').as_posix()
files=[ROOT/'README.md',ROOT/'CONTRIBUTING.md',ROOT/'.gitignore',native/'project.gbsproj',native/'README.md',native/'LICENSE',native/'THIRD_PARTY.md']
for folder in ['project','assets','plugins','art','docs','tests','licenses','dist']:
    files.extend(p for p in (native/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts)
files.extend(native/'tools'/n for n in ['build.sh','author_opening.py','package_review.py','resources.json','art-manifest.json','prepare_characters_v2.py','characters-v2-resources.json'])
files.extend(evidence(n) for n in ['build-final.json','compiler-final.log','static-check.json','clean-build-report.json','clean-build.log','review-contact-sheet.png','review-contact-sheet.json','preview-final.json'])
for folder in ['opening-final','exits-final','characters-final','intro-final','intro-v3-final-plugin']:
    files.extend(p for p in evidence(folder).rglob('*') if p.is_file())
files.append(evidence('opening-v4/events.jsonl'))
files=sorted(set(files))
assert all(p.is_file() for p in files)
assert not any('sprite-sheet' in p.name or p.suffix in ['.ram','.rtc'] for p in files)
rom_hash=hashlib.sha256((native/'dist/PocketHoller-opening.gbc').read_bytes()).hexdigest()
try:
    commit=subprocess.check_output(['git','-C',str(ROOT),'rev-parse','HEAD'],text=True).strip()
    dirty=bool(subprocess.check_output(['git','-C',str(ROOT),'status','--porcelain'],text=True).strip())
except (OSError,subprocess.CalledProcessError):commit=None;dirty=None
manifest={'schema':'pocketholler-opening-review/v1','date':'2026-10-09','stage':'M0/M1 review candidate','romSha256':rom_hash,'gitCommit':commit,'gitDirty':dirty,'gitNote':'Per-file hashes bind the exact packaged files, including local evidence','sourceEntry':'native/project.gbsproj','physicalTested':False,'files':[{'path':archive_path(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size} for p in files]}
dest=WORKSPACE/'PocketHoller-opening-review.zip'
with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED,strict_timestamps=False) as z:
    for p in files:z.write(p,'PocketHoller-opening/'+archive_path(p))
    z.writestr('PocketHoller-opening/REVIEW-MANIFEST.json',json.dumps(manifest,indent=2))
with zipfile.ZipFile(dest) as z:
    assert z.testzip() is None
    for row in manifest['files']:
        assert hashlib.sha256(z.read('PocketHoller-opening/'+row['path'])).hexdigest()==row['sha256']
(WORKSPACE/'REVIEW-MANIFEST.json').write_text(json.dumps(manifest,indent=2))
hashes=rom_hash+'  native/dist/PocketHoller-opening.gbc\n'+hashlib.sha256(dest.read_bytes()).hexdigest()+'  '+dest.name+'\n'
(WORKSPACE/'REVIEW-SHA256SUMS').write_text(hashes)
print(json.dumps({'archive':str(dest),'bytes':dest.stat().st_size,'files':len(files),'romSha256':rom_hash,'archiveVerified':True},indent=2))
