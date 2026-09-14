#!/usr/bin/env bash
set -euo pipefail
exec 9>/tmp/.jdk26-staging.lock
flock -n 9 || { echo "Another JDK26 build owns the staging prefix" >&2; exit 2; }
taskroot=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
scratch=/home/arron/projects/openjdk26-android-build
arch=${1:-aarch64}
case "$arch" in aarch64|arm) ;; *) echo 'Expected aarch64 or arm' >&2; exit 2;; esac
export JAVA_HOME="$scratch/toolchains/bootjdk25"
export PATH="$JAVA_HOME/bin:$PATH"
export NDK="$scratch/toolchains/android-ndk-r29"
export ANDROID_HOME="$scratch/toolchains/android-sdk"
export TERMUX_TOPDIR="$scratch/build-$arch"
export TERMUX_PKG_API_LEVEL=28
export TERMUX_PKG_MAKE_PROCESSES=8
export TERMUX_HOST_LLVM_BASE_DIR=/usr/lib/llvm-21
export TERMUX_PKGS__BUILD__RM_ALL_PKGS_BUILT_MARKER_AND_INSTALL_FILES=false
# The /data staging prefix is shared by the upstream build system: no parallel ABIs.
if [[ -f /data/TERMUX_ARCH ]] && [[ $(cat /data/TERMUX_ARCH) != "$arch" ]]; then
    echo 'Staging prefix contains another architecture; archive/switch it explicitly before building.' >&2
    exit 2
fi
printf '%s\n' "$arch" > /data/TERMUX_ARCH
mkdir -p "$scratch/recipes/openjdk-26" "$ANDROID_HOME"
cp -a "$taskroot/recipes/openjdk-26/." "$scratch/recipes/openjdk-26/"
# Use the native WSL boot JDK path for the host-build copy step.
sed -i "s|$taskroot/toolchains/bootjdk25|$JAVA_HOME|g" "$scratch/recipes/openjdk-26/build.sh"
cd "$scratch/termux-packages"
./build-package.sh -I -a "$arch" "$scratch/recipes/openjdk-26" 2>&1 | tee "$taskroot/logs/build-$arch.log"
