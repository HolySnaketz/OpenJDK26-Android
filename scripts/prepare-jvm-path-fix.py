from pathlib import Path
import difflib
root=Path(__file__).resolve().parent.parent
source=Path('/home/arron/projects/openjdk26-android-build/source/openjdk')
changes=[]
name='src/hotspot/os/linux/os_linux.cpp'
old=(source/name).read_text()
new=old.replace('static bool read_so_path_from_maps(const char* so_name, char* buf, int buflen);\n\n','')
start=new.index('static bool read_so_path_from_maps(')
end=new.index('// Remember the stack',start)
new=new[:start]+new[end:]
start=new.index('#ifdef __ANDROID__\n  if (dli_fname[0]')
end=new.index('#else // !__ANDROID__\n',start)+len('#else // !__ANDROID__\n')
new=new[:start]+new[end:]
needle='''    }
  }
#endif

  // we miss the cpufreq entries'''
assert needle in new
new=new.replace(needle,'''    }
  }

  // we miss the cpufreq entries''',1)
changes.append((name,old,new))
name='src/hotspot/os/posix/os_posix.cpp'
old=(source/name).read_text()
helper=r'''#ifdef __ANDROID__
// Bionic may report a basename through dladdr. Resolve the mapping containing
// this function, rather than choosing an arbitrary matching library name.
static bool android_jvm_path_from_maps(char* buf, size_t buflen) {
  FILE* maps = os::fopen("/proc/self/maps", "r");
  if (maps == nullptr) {
    return false;
  }
  const uintptr_t target = reinterpret_cast<uintptr_t>(CAST_FROM_FN_PTR(address, os::jvm_path));
  char line[MAXPATHLEN + 256];
  bool found = false;
  while (fgets(line, sizeof(line), maps) != nullptr) {
    unsigned long begin, end;
    if (sscanf(line, "%lx-%lx", &begin, &end) != 2 || target < begin || target >= end) {
      continue;
    }
    char* path = strchr(line, '/');
    if (path == nullptr) {
      continue;
    }
    path[strcspn(path, "\n")] = '\0';
    if (strlen(path) < buflen) {
      os::snprintf(buf, buflen, "%s", path);
      found = true;
    }
    break;
  }
  fclose(maps);
  return found;
}
#endif

'''
new=old.replace('static char saved_jvm_path[MAXPATHLEN] = {0};',helper+'static char saved_jvm_path[MAXPATHLEN] = {0};')
needle='''  if (fname[0] != '\\0') {
    rp = os::realpath(fname, buf, buflen);
  }
  if (rp == nullptr) {'''
assert needle in new
new=new.replace(needle,'''  if (fname[0] != '\\0') {
    rp = os::realpath(fname, buf, buflen);
  }
#ifdef __ANDROID__
  if (rp == nullptr && android_jvm_path_from_maps(buf, buflen)) {
    rp = buf;
  }
#endif
  if (rp == nullptr) {''',1)
changes.append((name,old,new))
diff=[]
for name,old,new in changes:
    diff.extend(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='a/'+name,tofile='b/'+name))
(root/'recipes/openjdk-26/0003-jdk26-posix-jvm-path.patch').write_text(''.join(diff))
print('Prepared JDK 26 POSIX path-discovery repair')
