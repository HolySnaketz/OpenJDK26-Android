from pathlib import Path
root=Path(__file__).resolve().parent.parent
for name in ['build-android.sh','resume-make.sh','switch-staging-arch.sh']:
    path=root/'scripts'/name
    text=path.read_text().replace('/data/data/.jdk26-build-arch','/data/TERMUX_ARCH')
    if name!='switch-staging-arch.sh':
        text=text.replace('set -euo pipefail','set -euo pipefail\nexec 9>/tmp/.jdk26-staging.lock\nflock -n 9 || { echo "Another JDK26 build owns the staging prefix" >&2; exit 2; }',1)
    else:
        text=text.replace("fi\nprintf 'Switched", "fi\nprintf '%s\\n' \"$target\" > /data/TERMUX_ARCH\nprintf 'Switched")
    path.write_text(text)