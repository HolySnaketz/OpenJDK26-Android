#!/usr/bin/env bash
set -euo pipefail
taskroot=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
# Keep authoritative downloads, recipes, scripts and logs in the Windows task directory.
# WSL-native scratch avoids slow per-file Windows filesystem calls during compilation.
scratch=/home/arron/projects/openjdk26-android-build
if [[ -e "$scratch" ]]; then
    echo "Scratch directory already exists; inspect before reuse: $scratch" >&2
    exit 1
fi
mkdir -p "$scratch/source" "$scratch/toolchains/bootjdk25" "$scratch/termux-packages"
unzip -q "$taskroot/downloads/openjdk-26+35_src.zip" -d "$scratch/source"
unzip -q "$taskroot/downloads/android-ndk-r29-linux.zip" -d "$scratch/toolchains"
tar -xzf "$taskroot/downloads/bootjdk25.tar.gz" --strip-components=1 -C "$scratch/toolchains/bootjdk25"
tar -xzf "$taskroot/downloads/termux-packages.tar.gz" --strip-components=1 -C "$scratch/termux-packages"
find "$scratch/source" "$scratch/termux-packages" -name AGENTS.md -print
printf '%s\n' "$scratch" > "$taskroot/research/wsl-build-root.txt"
touch "$scratch/.unpacked"
echo "WSL source/toolchain extraction complete: $scratch"
