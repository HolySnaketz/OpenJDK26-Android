from pathlib import Path
file=Path('/home/arron/projects/openjdk26-android-build/termux-packages/build-package.sh')
text=file.read_text()
old='set -euo pipefail'
new='''set -Eeuo pipefail
trap 'echo "BUILD_ERROR at ${BASH_SOURCE[0]}:${LINENO}: ${BASH_COMMAND}" >&2' ERR'''
assert text.count(old)==1
file.write_text(text.replace(old,new))
