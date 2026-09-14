from pathlib import Path
import subprocess, tempfile, zipfile
root=Path(__file__).resolve().parent.parent
patches=sorted((root/'recipes/openjdk-26').glob('*.patch'))
proof=Path(tempfile.mkdtemp(prefix='patch-proof-',dir='/home/arron/projects/openjdk26-android-build'))
paths=sorted({line[6:] for patch in patches for line in patch.read_text().splitlines() if line.startswith('--- a/')})
with zipfile.ZipFile(root/'downloads/openjdk-26+35_src.zip') as archive:
    for name in paths:
        destination=proof/name
        destination.parent.mkdir(parents=True,exist_ok=True)
        destination.write_bytes(archive.read('openjdk/'+name))
logs=[]
for patch in patches:
    result=subprocess.run(['patch','--batch','--fuzz=0','-p1','-i',str(patch)],cwd=proof,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    logs.append(patch.name+'\n'+result.stdout)
    (root/'logs/jdk26-exact-patch-check.log').write_text('\n'.join(logs))
    if result.returncode: raise SystemExit(result.stdout)
print(f'All {len(patches)} patches applied in order to {len(paths)} original files with fuzz=0.')