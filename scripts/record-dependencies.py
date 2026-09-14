from pathlib import Path
import hashlib,json,subprocess
root=Path(__file__).resolve().parent.parent
scratch=Path('/home/arron/projects/openjdk26-android-build')
for arch in ('aarch64','arm'):
    entries=[]
    for archive in sorted((scratch/f'build-{arch}/_cache-{arch}').glob('*.deb')):
        metadata=subprocess.check_output(['dpkg-deb','-f',str(archive),'Package','Version','Architecture'],text=True)
        entries.append(dict(file=archive.name,sha256=hashlib.file_digest(archive.open('rb'),'sha256').hexdigest(),metadata=metadata.strip()))
    (root/f'research/dependencies-{arch}.json').write_text(json.dumps(entries,indent=2)+'\n')
    print(arch,len(entries),'dependency archives recorded')