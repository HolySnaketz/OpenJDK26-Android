#!/usr/bin/env python3
"""Package a built image. Structural checks are not Android runtime acceptance."""
from pathlib import Path
import argparse, hashlib, json, struct, tarfile
parser=argparse.ArgumentParser()
parser.add_argument('arch',choices=['aarch64','arm'])
parser.add_argument('image',type=Path)
args=parser.parse_args()
root=Path(__file__).resolve().parent.parent
image=args.image.resolve(strict=True)
required=['release','lib/modules','lib/server/libjvm.so','lib/libsaproc.so',
          'lib/libawt_xawt.so','lib/libfontmanager.so','lib/libjawt.so',
          'include/jni.h','include/linux/jni_md.h','jmods/java.desktop.jmod',
          'man/man1/java.1','man/man1/javac.1','legal/java.base/LICENSE']
required += ['bin/'+name for name in ['java','javac','jar','javap','javadoc','jshell','jlink','jmod','jdeps','jcmd','jstack','jmap','jhsdb','keytool']]
for name in required:
    if not (image/name).is_file(): raise SystemExit('Missing required JDK component: '+name)
release=(image/'release').read_text()
if 'JAVA_VERSION="26' not in release: raise SystemExit('Image is not JDK 26')
expected_class,expected_machine=(2,183) if args.arch=='aarch64' else (1,40)
hashes={}
for path in sorted(image.rglob('*')):
    if path.is_symlink():
        if not path.resolve().is_relative_to(image): raise SystemExit('External symlink requires packaging decision: '+str(path))
        continue
    if not path.is_file(): continue
    data=path.read_bytes()
    if data.startswith(b'\x7fELF'):
        if data[5]!=1: raise SystemExit('Unexpected ELF byte order: '+str(path))
        machine=struct.unpack_from('<H',data,18)[0]
        if data[4]!=expected_class or machine!=expected_machine: raise SystemExit('Wrong ELF ABI: '+str(path))
    hashes[str(path.relative_to(image))]=hashlib.sha256(data).hexdigest()
dist=root/'dist'
dist.mkdir(exist_ok=True)
name='openjdk-26-android-'+args.arch+'-api28'
partial=dist/(name+'.tar.partial')
with tarfile.open(partial,'w',format=tarfile.PAX_FORMAT) as archive:
    archive.add(image,arcname='java-26-openjdk')
with tarfile.open(partial,'r') as archive:
    names=set(archive.getnames())
    for member in required:
        if 'java-26-openjdk/'+member not in names: raise SystemExit('Archive missing '+member)
final=dist/(name+'.tar')
partial.replace(final)
checksum=hashlib.sha256(final.read_bytes()).hexdigest()
(final.with_suffix('.tar.sha256')).write_text(checksum+'  '+final.name+'\n')
(dist/(name+'.manifest.json')).write_text(json.dumps({
    'architecture':args.arch,'minimumAndroidApi':28,'archive':final.name,'sha256':checksum,
    'release':release,'files':hashes,
    'checks':{'requiredComponents':'passed','elfArchitecture':'passed','tarContents':'passed'},
    'androidRuntimeAcceptance':'NOT_ESTABLISHED_BY_THIS_SCRIPT',
    'status':'candidate-awaiting-device-validation',
    'knownIssues':(['OpenJDK 26 SA has no ARM32 backend; presence of jhsdb and libsaproc does not establish ARM32 jhsdb functionality'] if args.arch=='arm' else [])
},indent=2)+'\n')
print(final)
print('Structural checks passed; verify dynamic dependencies, API compatibility and Android runtime separately.')
