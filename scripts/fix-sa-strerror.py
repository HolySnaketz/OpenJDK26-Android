from pathlib import Path
import difflib, subprocess
root=Path(__file__).resolve().parent.parent
source=Path('/home/arron/projects/openjdk26-android-build/source/openjdk')
name='src/jdk.hotspot.agent/linux/native/libsaproc/ps_proc.c'
old=(source/name).read_text()
needle='#if defined(__GLIBC__) && defined(_GNU_SOURCE)'
assert old.count(needle)==1
new=old.replace(needle,'#if (defined(__GLIBC__) || defined(__BIONIC__)) && defined(_GNU_SOURCE)')
patch=root/'recipes/openjdk-26/0005-bionic-sa-strerror.patch'
patch.write_text(''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='a/'+name,tofile='b/'+name)))
for tree in [source,Path('/home/arron/projects/openjdk26-android-build/build-aarch64/openjdk-26/src')]:
    subprocess.run(['patch','--batch','--fuzz=0','-p1','-i',str(patch)],cwd=tree,check=True)
