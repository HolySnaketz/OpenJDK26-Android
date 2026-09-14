from pathlib import Path
import difflib
root=Path(__file__).resolve().parent.parent
source=Path('/home/arron/projects/openjdk26-android-build/source/openjdk')
changes=[]
name='src/jdk.hotspot.agent/linux/native/libsaproc/ps_core.c'
old=(source/name).read_text()
addition='''
#ifdef __ANDROID__
#include <sys/time.h>
// Bionic exposes the register sets but omits the Linux NT_PRSTATUS note type.
// Keep the kernel ELF core-note layout for each native word size.
typedef struct {
   struct elf_siginfo pr_info;
   short pr_cursig;
   unsigned long pr_sigpend;
   unsigned long pr_sighold;
   pid_t pr_pid;
   pid_t pr_ppid;
   pid_t pr_pgrp;
   pid_t pr_sid;
   struct timeval pr_utime;
   struct timeval pr_stime;
   struct timeval pr_cutime;
   struct timeval pr_cstime;
   elf_gregset_t pr_reg;
   int pr_fpvalid;
} prstatus_t;
#if defined(__aarch64__)
_Static_assert(offsetof(prstatus_t, pr_reg) == 112, "AArch64 NT_PRSTATUS register offset");
_Static_assert(sizeof(prstatus_t) == 392, "AArch64 NT_PRSTATUS note size");
#elif defined(__arm__)
_Static_assert(offsetof(prstatus_t, pr_reg) == 72, "ARM NT_PRSTATUS register offset");
_Static_assert(sizeof(prstatus_t) == 148, "ARM NT_PRSTATUS note size");
#endif
#endif
'''
new=old.replace('#include "salibelf.h"','#include "salibelf.h"\n'+addition)
new=new.replace('''   // we have to read prstatus_t from buf
   // assert(nbytes == sizeof(prstaus_t), "size mismatch on prstatus_t");''','''   if (nbytes < sizeof(prstatus_t)) {
      print_error("truncated NT_PRSTATUS core note\\n");
      return false;
   }''')
changes.append((name,old,new))
name='src/jdk.hotspot.agent/linux/native/libsaproc/elfmacros.h'
old=(source/name).read_text()
new=old.replace('#define ELF_ST_TYPE     ELF64_ST_TYPE','#ifndef ELF_ST_TYPE\n#define ELF_ST_TYPE     ELF64_ST_TYPE\n#endif').replace('#define ELF_ST_TYPE     ELF32_ST_TYPE','#ifndef ELF_ST_TYPE\n#define ELF_ST_TYPE     ELF32_ST_TYPE\n#endif')
changes.append((name,old,new))
name='src/hotspot/os/posix/os_posix.cpp'
old=(source/name).read_text()
needle='''      os::snprintf(buf, buflen, "%s", path);
      found = true;'''
assert needle in old
new=old.replace(needle,'''      found = os::snprintf(buf, buflen, "%s", path) >= 0;''')
changes.append((name,old,new))
diff=[]
for name,old,new in changes:
    diff.extend(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='a/'+name,tofile='b/'+name))
(root/'recipes/openjdk-26/0004-bionic-serviceability-core-notes.patch').write_text(''.join(diff))
print('Prepared Bionic SA core-note layout with ARM32/ARM64 compile-time layout checks')
