#!/usr/bin/env bash
set -euo pipefail
taskroot=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
scratch=/home/arron/projects/openjdk26-android-build
arch=${1:?Expected architecture}
case "$arch" in arm|aarch64) ;; *) exit 2;; esac
exec 9>/tmp/.jdk26-staging.lock
flock -n 9 || exit 2
[[ $(cat /data/TERMUX_ARCH) == "$arch" ]] || exit 2
export PATH="$scratch/build-$arch/_cache/android-r29-api-28-v5/bin:$scratch/toolchains/bootjdk25/bin:$PATH"
cd "$scratch/build-$arch/openjdk-26/src/build/linux-$arch-server-release"
make images JOBS=8 ENABLE_PANDOC=true PANDOC=/usr/bin/pandoc PANDOC_MARKDOWN_FLAG=markdown-smart-tex_math_dollars > "$taskroot/logs/manuals-$arch.log" 2>&1
printf '%s official manual rebuild completed\n' "$arch"