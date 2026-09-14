#!/usr/bin/env bash
set -euo pipefail
taskroot=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
mkdir -p "$taskroot/vendor/termux-packages" "$taskroot/toolchains/bootjdk25"
tar -xzf "$taskroot/downloads/termux-packages.tar.gz" --strip-components=1 -C "$taskroot/vendor/termux-packages"
tar -xzf "$taskroot/downloads/bootjdk25.tar.gz" --strip-components=1 -C "$taskroot/toolchains/bootjdk25"
find "$taskroot/vendor/termux-packages" -name AGENTS.md -print
"$taskroot/toolchains/bootjdk25/bin/java" -version
