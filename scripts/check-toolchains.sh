#!/usr/bin/env bash
set -euo pipefail
taskroot=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
scratch=/home/arron/projects/openjdk26-android-build
mkdir -p "$scratch/smoke-compile"
"$scratch/toolchains/bootjdk25/bin/javac" -h "$scratch/smoke-compile" -d "$scratch/smoke-compile" "$taskroot/tests/JdkSmoke.java" "$taskroot/tests/NativeSmoke.java"
for abi in aarch64-linux-android28 armv7a-linux-androideabi28; do
    "$scratch/toolchains/android-ndk-r29/toolchains/llvm/prebuilt/linux-x86_64/bin/$abi-clang" -shared -fPIC -Wall -Wextra -Werror -I"$scratch/toolchains/bootjdk25/include" -I"$scratch/toolchains/bootjdk25/include/linux" -I"$scratch/smoke-compile" "$taskroot/tests/native-smoke.c" -o "$scratch/smoke-compile/$abi.so"
    file "$scratch/smoke-compile/$abi.so"
done
