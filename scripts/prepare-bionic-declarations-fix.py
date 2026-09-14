from pathlib import Path
import difflib
root=Path(__file__).resolve().parent.parent
source=Path('/home/arron/projects/openjdk26-android-build/source/openjdk')
name='src/hotspot/share/utilities/compilerWarnings.hpp'
old=(source/name).read_text()
needle='#define FORBIDDEN_FUNCTION_COND_NOEXCEPT_noexcept NOT_WINDOWS(NOT_BSD(noexcept))'
replacement='''// Android Bionic declarations do not use the glibc noexcept specification.
#ifdef __ANDROID__
#define FORBIDDEN_FUNCTION_COND_NOEXCEPT_noexcept
#else
#define FORBIDDEN_FUNCTION_COND_NOEXCEPT_noexcept NOT_WINDOWS(NOT_BSD(noexcept))
#endif'''
assert old.count(needle)==1
new=old.replace(needle,replacement)
patch=''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='a/'+name,tofile='b/'+name))
(root/'recipes/openjdk-26/0002-bionic-forbidden-function-declarations.patch').write_text(patch)
print('Prepared Bionic declaration fix; forbidden-function diagnostics remain enabled.')
