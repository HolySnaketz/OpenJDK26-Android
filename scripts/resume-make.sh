#!/usr/bin/env bash
set -euo pipefail
exec 9>/tmp/.jdk26-staging.lock
flock -n 9 || { echo "Another JDK26 build owns the staging prefix" >&2; exit 2; }
taskroot=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
scratch=/home/arron/projects/openjdk26-android-build
arch=${1:?Expected architecture}
case "$arch" in aarch64|arm) ;; *) exit 2;; esac
if [[ $(cat /data/TERMUX_ARCH) != "$arch" ]]; then
    echo 'Wrong architecture in shared Termux staging prefix' >&2
    exit 2
fi
export PATH="$scratch/build-$arch/_cache/android-r29-api-28-v5/bin:$scratch/toolchains/bootjdk25/bin:$PATH"
log="$taskroot/logs/make-$arch.log"
if [[ -f "$log" ]]; then cp "$log" "$log.$(date +%Y%m%d-%H%M%S)"; fi
cd "$scratch/build-$arch/openjdk-26/src/build/linux-$arch-server-release"
make images JOBS=8 2>&1 | tee "$log"
