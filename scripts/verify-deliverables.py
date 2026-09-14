from pathlib import Path
import hashlib,json,tarfile
root=Path(__file__).resolve().parent.parent
results=[]
for arch in ('aarch64','arm'):
    stem='openjdk-26-android-'+arch+'-api28'
    manifest=json.loads((root/'dist'/f'{stem}.manifest.json').read_text())
    archive=root/'dist'/f'{stem}.tar'
    with archive.open('rb') as stream:
        digest=hashlib.file_digest(stream,'sha256').hexdigest()
    assert digest==manifest['sha256']
    assert (root/'dist'/f'{stem}.tar.sha256').read_text().split()[0]==digest
    verified=set()
    with tarfile.open(archive) as tar:
        for member in tar:
            relative=member.name.removeprefix('java-26-openjdk/')
            assert not member.name.startswith('/') and '..' not in Path(member.name).parts
            if member.isfile():
                with tar.extractfile(member) as stream:
                    assert hashlib.file_digest(stream,'sha256').hexdigest()==manifest['files'][relative],relative
                verified.add(relative)
                if relative.startswith('bin/'):
                    assert member.mode & 0o111,relative
    assert verified==set(manifest['files'])
    results.append(dict(arch=arch,bytes=archive.stat().st_size,sha256=digest,files=len(verified),archiveHashesVerified=True,executablePermissionsVerified=True))
(root/'dist/verification.json').write_text(json.dumps(results,indent=2)+'\n')
for row in results: print(json.dumps(row))