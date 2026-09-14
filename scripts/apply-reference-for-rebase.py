#!/usr/bin/env python3
from pathlib import Path
import subprocess
import json
root=Path(__file__).resolve().parent.parent
source=Path('/home/arron/projects/openjdk26-android-build/source/openjdk')
logdir=root/'logs/sequential-patch-audit'
logdir.mkdir(exist_ok=True)
results=[]
for patch in sorted((root/'recipes/openjdk-26').glob('*.patch')):
    command=['patch','--batch','--forward','--fuzz=3','-p1','-i',str(patch)]
    probe=subprocess.run(command+['--dry-run'],cwd=source,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    if probe.returncode==0:
        applied=subprocess.run(command,cwd=source,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        (logdir/(patch.name+'.log')).write_text(applied.stdout)
        if applied.returncode: raise SystemExit(applied.stdout)
        state='APPLIED_FOR_REBASE'
    else:
        (logdir/(patch.name+'.log')).write_text(probe.stdout)
        state='MANUAL_REBASE'
    results.append({'patch':patch.name,'state':state})
    print(state,patch.name)
(logdir/'summary.json').write_text(json.dumps(results,indent=2)+'\n')
