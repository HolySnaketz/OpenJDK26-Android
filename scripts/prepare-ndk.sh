#!/usr/bin/env bash
set -euo pipefail
taskroot=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
unzip -q -n "$taskroot/downloads/android-ndk-r29-linux.zip" -d "$taskroot/toolchains"
"$taskroot/toolchains/android-ndk-r29/toolchains/llvm/prebuilt/linux-x86_64/bin/clang" --version
mkdir -p "$taskroot/logs/host-smoke-compile"
"$taskroot/toolchains/bootjdk25/bin/javac" -h "$taskroot/logs/host-smoke-compile" -d "$taskroot/logs/host-smoke-compile" "$taskroot/tests/JdkSmoke.java" "$taskroot/tests/NativeSmoke.java"
# Syntax/ABI toolchain check only. These binaries are not the requested JDK.
for abi in aarch64-linux-android28 armv7a-linux-androideabi28; do
    "$taskroot/toolchains/android-ndk-r29/toolchains/llvm/prebuilt/linux-x86_64/bin/$abi-clang" -shared -fPIC -Wall -Wextra -Werror -I"$taskroot/toolchains/bootjdk25/include" -I"$taskroot/toolchains/bootjdk25/include/linux" -I"$taskroot/logs/host-smoke-compile" "$taskroot/tests/native-smoke.c" -o "$taskroot/logs/host-smoke-compile/$abi.so"
    file "$taskroot/logs/host-smoke-compile/$abi.so"
done
