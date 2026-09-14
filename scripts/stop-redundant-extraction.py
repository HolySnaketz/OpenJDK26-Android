from pathlib import Path
import os, signal
base='/mnt/d/projects/arron/shuoshuo-07/openjdk26-android/'
expected={
('unzip','-q','-n',base+'downloads/android-ndk-r29-linux.zip','-d',base+'toolchains'),
('unzip','-q','-n',base+'downloads/openjdk-26+35_src.zip','-d',base+'source'),
}
for item in Path('/proc').iterdir():
    if not item.name.isdigit(): continue
    try: args=tuple((item/'cmdline').read_bytes().decode().rstrip('\0').split('\0'))
    except (FileNotFoundError, PermissionError, UnicodeDecodeError): continue
    if args in expected:
        os.kill(int(item.name),signal.SIGTERM)
        print('Stopped redundant Windows extraction',item.name)
