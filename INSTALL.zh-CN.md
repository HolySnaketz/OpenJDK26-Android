# 安装与验收（构建产物尚待 Android 真机验证）

适用默认包名 com.termux 的 Termux，固定前缀 /data/data/com.termux/files/usr。ARM64 与 ARM32 必须选择各自架构的 tar，不能根据 CPU 支持 ARM64 就推断系统支持 32 位进程。先在 Termux 执行 `dpkg --print-architecture`，结果 aarch64 或 arm 对应同名产物。

## 安装依赖

```sh
pkg update
pkg install x11-repo
pkg install termux-x11-nightly clang fontconfig libandroid-shmem libandroid-spawn libiconv libjpeg-turbo zlib littlecms alsa-plugins freetype giflib libpng libx11 libxext libxi libxrender libxtst libelf cups
```

Termux:X11 需要同时安装 Android APK 与 Termux companion 包。APK 从官方 [Termux:X11 nightly](https://github.com/termux/termux-x11/releases/tag/nightly) 获取；具体使用要求见 [官方说明](https://github.com/termux/termux-x11)。安装包含中文字符的字体到 ~/.local/share/fonts 后运行 `fc-cache -f`。中文显示需要实际检查所装字体覆盖范围。

## 解压

先用随附 .sha256 校验 tar。以下示例为 ARM64，ARM32 将 aarch64 改为 arm；在 tar 所在目录执行。

```sh
sha256sum -c openjdk-26-android-aarch64-api28.tar.sha256
mkdir -p "$PREFIX/lib/jvm"
# 若目录已存在，先自行备份并移开；不要覆盖正在使用的 JDK。
test ! -e "$PREFIX/lib/jvm/java-26-openjdk" || exit 1
tar -xf openjdk-26-android-aarch64-api28.tar -C "$PREFIX/lib/jvm"
export JAVA_HOME="$PREFIX/lib/jvm/java-26-openjdk"
export PATH="$JAVA_HOME/bin:$PATH"
export TMPDIR="$PREFIX/tmp"
java -version
javac -version
```

## 图形与验证

```sh
termux-x11 :1 &
export DISPLAY=:1
# 进入本项目 tests 目录（将整个目录复制到设备）
bash run-termux-smoke.sh --gui
```

打开 Termux:X11 Android 应用观察窗口。检查 AWT/Swing 两种按钮、文本输入和中文显示。脚本包含 javac、JNI、Serial/G1、文件、图片和 jlink 冒烟检查；并不覆盖完整的 JDK 行为。

还需验证 jcmd/jstack/jmap/jhsdb、剪贴板、Robot、打印与音频，以及 ARM32 JIT/G1 压力测试。记录设备、Android API、ABI、Termux 版本和错误日志。API28 与 API35 端点及中间版本均未取得真机结果。

不得将静态 ELF 检查当作 AWT/Swing 已实际可用的证明。Android 15 的 16 KiB 页兼容也需要系统及外部依赖共同满足条件；本项目报告仅核验 JDK 自身 ELF。