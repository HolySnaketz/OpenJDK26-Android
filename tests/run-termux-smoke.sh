#!/usr/bin/env bash
# Run on the target Termux environment after installing the candidate JDK and clang.
set -euo pipefail
: "${JAVA_HOME:?Set JAVA_HOME to the candidate Android JDK 26}"
testroot=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
work=$(mktemp -d "${TMPDIR:-/data/data/com.termux/files/usr/tmp}/jdk26-acceptance.XXXXXX")
echo "Evidence and generated files: $work"
exec > >(tee "$work/smoke.log") 2>&1
uname -a
getprop ro.build.version.sdk
getprop ro.product.cpu.abilist
"$JAVA_HOME/bin/java" -version
"$JAVA_HOME/bin/java" --list-modules > "$work/modules.txt"
"$JAVA_HOME/bin/javac" -h "$work" -d "$work" "$testroot/JdkSmoke.java" "$testroot/NativeSmoke.java"
for collector in UseSerialGC UseG1GC; do
    "$JAVA_HOME/bin/java" -Xms32m -Xmx96m -XX:+"$collector" -cp "$work" JdkSmoke
done
"$JAVA_HOME/bin/java" -Xms32m -Xmx96m -cp "$work" JdkSmoke
clang -shared -fPIC -Wall -Wextra -Werror -I"$JAVA_HOME/include" -I"$JAVA_HOME/include/linux" -I"$work" "$testroot/native-smoke.c" -o "$work/libjdk26smoke.so"
"$JAVA_HOME/bin/java" -Xcheck:jni --enable-native-access=ALL-UNNAMED -Djava.library.path="$work" -cp "$work" NativeSmoke
"$JAVA_HOME/bin/jar" --create --file "$work/smoke.jar" -C "$work" JdkSmoke.class
"$JAVA_HOME/bin/jdeps" "$work/smoke.jar"
"$JAVA_HOME/bin/jlink" --add-modules java.base,java.desktop,java.compiler,jdk.compiler --output "$work/linked"
"$work/linked/bin/java" -Xmx96m -cp "$work" JdkSmoke
if [[ ${1:-} == --gui ]]; then
    : "${DISPLAY:?Start Termux:X11 and set DISPLAY}"
    "$JAVA_HOME/bin/java" -Xmx128m -Djava.awt.headless=false -cp "$work" JdkSmoke --gui
fi
echo "REQUESTED_SMOKE_COMMANDS_PASSED; full acceptance and GUI visual checks remain separate."
