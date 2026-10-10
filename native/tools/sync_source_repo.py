"""Copy the tested native working source into the sibling src Git checkout.

Only managed source folders and named release receipts/cartridges are copied.
The baseline detects repository-side edits before overwriting; saves, active
preview builds and full recordings stay in the working workspace.
"""
from pathlib import Path
import argparse,hashlib,json,shutil

NATIVE=Path(__file__).resolve().parents[1]
WORKSPACE=NATIVE.parent
REPO=WORKSPACE/'src'
BASELINE=WORKSPACE/'working-copy-source-manifest.json'
FOLDERS=['project','assets','plugins','art','docs','tools','tests','licenses']
ROOT_FILES=['project.gbsproj','README.md','LICENSE','THIRD_PARTY.md','requirements-dev.txt']
RECEIPTS=['build-final.json','static-check.json','full-build.json','full-static.json','full-world-map.json','full-game-report.json','full-save-report.json','full-clean-build.json','full-release-manifest.json','full-browser-report.json','full-video-report.json','full-capture-report.json','full-audio-report.json','full-oam-report.json','clean-full-source-manifest.json']
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def candidates():
    paths=[NATIVE/name for name in ROOT_FILES if (NATIVE/name).is_file()]
    for name in FOLDERS:
        paths += [p for p in (NATIVE/name).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix not in ['.ram','.rtc','.pyc'] and not (p.suffix=='.wav' and 'art' in p.relative_to(NATIVE).parts)]
    paths += [NATIVE/'evidence'/name for name in RECEIPTS if (NATIVE/'evidence'/name).is_file()]
    for name in ['PocketHoller-opening.gbc','PocketHoller-full.gbc','SHA256SUMS']:
        path=NATIVE/'dist'/name
        if path.is_file():paths.append(path)
    for name in ['PocketHoller-opening.gbc.debug','PocketHoller-full.gbc.debug']:
        paths += [p for p in (NATIVE/'dist'/name).rglob('*') if p.is_file()]
    return sorted(set(paths))
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--apply',action='store_true');args=ap.parse_args()
    assert (REPO/'.git').exists() and BASELINE.is_file(), 'Run this utility from the authorized sibling native working copy, with its source baseline present; it is not a clone build command.'
    baseline=json.loads(BASELINE.read_text())['files'];paths=candidates();conflicts=[]
    for path in paths:
        rel='native/'+path.relative_to(NATIVE).as_posix();dest=REPO/rel
        if dest.is_file() and sha(dest)!=sha(path) and (rel not in baseline or sha(dest)!=baseline[rel]):conflicts.append(rel)
    assert not conflicts,'Repository-side changes need review before synchronization: '+', '.join(conflicts)
    removed=[rel for rel in baseline if not (WORKSPACE/rel).exists() and (REPO/rel).is_file()]
    for rel in removed:assert sha(REPO/rel)==baseline[rel], 'Modified removed source must be preserved: '+rel
    if args.apply:
        for path in paths:
            dest=REPO/'native'/path.relative_to(NATIVE);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(path,dest);assert sha(dest)==sha(path)
        for rel in removed:(REPO/rel).unlink()
        baseline.update({'native/'+p.relative_to(NATIVE).as_posix():sha(p) for p in paths})
        for rel in removed:baseline.pop(rel,None)
        document=json.loads(BASELINE.read_text());document['files']=baseline;BASELINE.write_text(json.dumps(document,indent=2)+'\n')
    print(json.dumps({'files':len(paths),'removedManagedFiles':len(removed),'applied':args.apply,'repository':str(REPO),'recordingsAndSavesCopied':False}))
if __name__=='__main__':main()
