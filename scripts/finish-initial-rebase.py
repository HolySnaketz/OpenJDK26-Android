from pathlib import Path
import subprocess, re, difflib, zipfile, json
root=Path(__file__).resolve().parent.parent
source=Path('/home/arron/projects/openjdk26-android-build/source/openjdk')
recipe=root/'recipes/openjdk-26'
# Apply the path patch after dropping only the outdated test hunk; fix that test explicitly.
patchfile=next(recipe.glob('0023-*'))
text=patchfile.read_text()
start=text.index('@@ -153,11 +153,11 @@')
end=text.index('diff --git ', start)
text=text[:start]+text[end:]
result=subprocess.run(['patch','--batch','--forward','--fuzz=3','-p1'],input=text,text=True,cwd=source,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
(root/'logs/sequential-patch-audit/0023-rebased.log').write_text(result.stdout)
if result.returncode: raise SystemExit(result.stdout)
file=source/'test/jdk/tools/jpackage/share/RuntimePackageTest.java'
text=file.read_text().replace('Path.of("/usr/share/doc",','Path.of("@TERMUX_PREFIX@/share/doc",').replace('installDir.startsWith("/usr/") || installDir.equals("/usr")','installDir.startsWith("@TERMUX_PREFIX@/") || installDir.equals("@TERMUX_PREFIX@")')
file.write_text(text)
file=source/'src/hotspot/os_cpu/linux_arm/os_linux_arm.cpp'
text=file.read_text()
assert text.count('# include <fpu_control.h>')==1
file.write_text(text.replace('# include <fpu_control.h>','#ifndef __ANDROID__\n# include <fpu_control.h>\n#endif'))
# The old x86 FPU hunk is obsolete after x86-32 removal; neither requested ABI needs it.
# JDK 26 moved the origin macros to JdkNativeCompilation.gmk.
file=source/'make/common/JdkNativeCompilation.gmk'
text=file.read_text()
clang_start=text.index('else ifeq ($(call isCompiler, clang), true)')
clang_end=text.index('else ifeq ($(call isCompiler, microsoft), true)')
clang=text[clang_start:clang_end].replace(' -Wl,--disable-new-dtags',' -Wl,--enable-new-dtags')
old='''    ifeq ($(call isTargetOs, arm), true)
      SetSharedLibraryOrigin = \\
          -Wl,-rpath,\\$(DOLLAR)ORIGIN$1
    else
      SetSharedLibraryOrigin = \\
          -Wl,-z,origin -Wl,-rpath,\\$(DOLLAR)ORIGIN$1
    endif'''
assert old in clang
clang=clang.replace(old,'''    SetSharedLibraryOrigin = \\
        -Wl,-z,origin -Wl,-rpath,\\$(DOLLAR)ORIGIN$1''')
file.write_text(text[:clang_start]+clang+text[clang_end:])
# JDK 26 uses standard uint32_t etc. so the old bionic typedef collision no longer exists.
assert 'typedef unsigned int       __uint32_t;' not in (source/'src/java.base/unix/native/libnio/fs/UnixNativeDispatcher.c').read_text()
# Retain attribution and reference patches outside the build recipe.
reference=root/'research/reference-patches'
reference.mkdir(exist_ok=True)
paths={'make/common/JdkNativeCompilation.gmk'}
for patch in sorted(recipe.glob('*.patch')):
    for line in patch.read_text().splitlines():
        if line.startswith('+++ '):
            name=line[4:].split('\t')[0].split(' ')[0]
            if name.startswith(('b/','./')): paths.add(name[2:])
    patch.rename(reference/patch.name)
diff=[]
with zipfile.ZipFile(root/'downloads/openjdk-26+35_src.zip') as archive:
    for name in sorted(paths):
        if not (source/name).is_file(): continue
        original=archive.read('openjdk/'+name).decode('utf-8')
        current=(source/name).read_text()
        if current!=original:
            diff.extend(difflib.unified_diff(original.splitlines(True),current.splitlines(True),fromfile='a/'+name,tofile='b/'+name))
header='''Android/Termux port rebased onto official OpenJDK 26+35 RI source.
Derived from the Termux OpenJDK 25 patch series at commit
c0df78899f52c9905e07321c999f24dd434bb7ae. Original patch author metadata
is retained in research/reference-patches and vendor/termux-packages.
This patch preserves G1 and libsaproc build targets. Runtime validation pending.

'''
(recipe/'0001-android-termux-jdk26.patch').write_text(header+''.join(diff))
(root/'research/rebase-notes.json').write_text(json.dumps({
'base':'Official OpenJDK 26+35 RI source zip',
'sha256':'215fb2cc080e334538f5c57a2be3d34e64e97cf3c7655fe485b3cf13c87e1602',
'excluded':['libsa removal','ASCII-only encoding workaround'],
'manual':['ARM fpu_control include guard','RuntimePackageTest path context','JdkNativeCompilation origin macros'],
'obsolete':['x86-32 FPU changes','UnixNativeDispatcher bionic typedef collision'],
'validation':'Generated exact-context patch; compilation and runtime not yet verified'
},indent=2)+'\n')
print('Generated',recipe/'0001-android-termux-jdk26.patch',len(diff),'diff lines')
