#!/usr/bin/env python3
from pathlib import Path
import argparse, json, re, struct, subprocess
parser=argparse.ArgumentParser()
parser.add_argument('arch',choices=['aarch64','arm'])
args=parser.parse_args()
root=Path(__file__).resolve().parent.parent
scratch=Path('/home/arron/projects/openjdk26-android-build')
image=scratch/f'build-{args.arch}/openjdk-26/src/build/linux-{args.arch}-server-release/images/jdk'
ndk=scratch/'toolchains/android-ndk-r29/toolchains/llvm/prebuilt/linux-x86_64'
current=Path('/data/TERMUX_ARCH').read_text().strip()
staging=Path('/data/data') if current==args.arch else scratch/f'staging/{args.arch}-data'
triple='aarch64-linux-android' if args.arch=='aarch64' else 'arm-linux-androideabi'
provided={file.name for directory in [image/'lib', staging/'com.termux/files/usr/lib',ndk/f'sysroot/usr/lib/{triple}/28'] for file in directory.rglob('*') if file.is_file() or file.is_symlink()}
rows=[]
errors=[]
for path in sorted(image.rglob('*')):
    if path.is_symlink() or not path.is_file(): continue
    with path.open('rb') as stream:
        if stream.read(4)!=b'\x7fELF': continue
        stream.seek(0)
        data=stream.read()
    bits=data[4]
    phoff=struct.unpack_from('<Q' if bits==2 else '<I',data,32 if bits==2 else 28)[0]
    phentsize,phnum=struct.unpack_from('<HH',data,54 if bits==2 else 42)
    alignments=[]
    interpreter=None
    for index in range(phnum):
        fields=struct.unpack_from('<IIQQQQQQ' if bits==2 else '<IIIIIIII',data,phoff+index*phentsize)
        if fields[0]==1: alignments.append(fields[7])
        if fields[0]==3:
            offset,size=(fields[2],fields[5]) if bits==2 else (fields[1],fields[4])
            interpreter=data[offset:offset+size].rstrip(b'\0').decode()
    dynamic=subprocess.run([str(ndk/'bin/llvm-readelf'),'-d',str(path)],check=True,text=True,stdout=subprocess.PIPE).stdout
    needed=re.findall(r'\(NEEDED\).*?\[(.*?)\]',dynamic)
    runpath=re.findall(r'\((?:RUNPATH|RPATH)\).*?\[(.*?)\]',dynamic)
    name=str(path.relative_to(image))
    if interpreter and interpreter!=('/system/bin/linker64' if bits==2 else '/system/bin/linker'):
        errors.append(name+': unexpected interpreter '+interpreter)
    if args.arch=='aarch64' and any(alignment<16384 for alignment in alignments):
        errors.append(name+': PT_LOAD alignment below 16 KiB')
    for library in needed:
        if library not in provided: errors.append(name+': unresolved DT_NEEDED '+library)
        if library in {'libc.so.6','libpthread.so.0','libdl.so.2','libm.so.6'}:
            errors.append(name+': glibc dependency '+library)
    rows.append({'file':name,'interpreter':interpreter,'loadAlignments':alignments,'needed':needed,'runpaths':runpath})
result={'architecture':args.arch,'elfFiles':rows,'errors':errors,'runtimeAcceptance':'not performed','note':'Checks DT_NEEDED file availability, interpreter and alignment; does not prove symbol or dlopen compatibility.'}
output=root/f'dist/openjdk-26-android-{args.arch}-api28.elf-report.json'
output.write_text(json.dumps(result,indent=2)+'\n')
print(f'{len(rows)} ELF files checked; {len(errors)} errors; {output}')
if errors: raise SystemExit('\n'.join(errors))
