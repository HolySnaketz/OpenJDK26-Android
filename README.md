# OpenJDK 26 Android / Termux 移植

## 当前结果

ARM64 和 ARM32 的 `make images` 均已成功，且已在设备 PLC110 中验证 ARM64 版本。

| 项目 | ARM64 / aarch64 | ARM32 / arm |
|---|---|---|
| 官方 OpenJDK 26+35 RI 源码 | 已校验 | 已校验 |
| HotSpot server / C1 / C2 / G1 | 编译通过 | 编译通过，未禁用 G1 |
| AWT/X11、Swing 模块、字体原生库 | 已包含 | 已包含 |
| JDK 工具、JNI 头文件、jmods、手册、许可证 | 打包检查通过 | 打包检查通过 |
| ELF ABI、解释器、DT_NEEDED 文件检查 | 69 个通过 | 68 个通过 |
| JDK 自身 ELF 16 KiB 对齐 | 通过 | 不适用此 ARM64 检查 |
| Android API28–35 运行 | 通过 | 未验证 |
| jhsdb / Serviceability Agent | 已编译，运行未验证 | 文件已编译，但上游缺少 ARM32 后端 |

OpenJDK 26 的 SA `PlatformInfo.knownCPU` 不包含 arm，LinuxDebuggerLocal 没有 ARM32 寄存器映射。已生成 jhsdb/lib­saproc 并不代表 ARM32 调试后端可用。

## 产物

- `openjdk-26-android-aarch64-api28.tar`
- `openjdk-26-android-arm-api28.tar`
- 每个 tar 随附 `.sha256`、`.manifest.json`、`.elf-report.json`。
- 安装与真机测试见 [INSTALL.zh-CN.md](INSTALL.zh-CN.md)。（内容由ChatGPT生成）

安装目录固定为 `/data/data/com.termux/files/usr/lib/jvm/java-26-openjdk`。通过 Termux pkg 安装外部依赖；图形通过 Termux:X11。Android 运行不使用 Linux 容器或 glibc 兼容层。已验证兼容 Android 15

## 源码及构建

实际输入是官方 `openjdk-26+35_src.zip`，SHA-256 为 `215fb2cc080e334538f5c57a2be3d34e64e97cf3c7655fe485b3cf13c87e1602`。

参考 Termux packages 提交 `c0df78899f52c9905e07321c999f24dd434bb7ae` 的 JDK25 移植。五个补丁覆盖 55 个原始文件，顺序零模糊应用检查通过；另有路径长度模板补丁 `tmpdir-path-length.diff`。修复涉及 Android 路径、Bionic 声明、JDK26 的 POSIX JVM 定位和 SA ELF/strerror 接口。保留官方该架构的默认 server 功能。

实际编译使用 NDK r29、主机 OpenJDK25、Clang21 和 Pandoc。详细复现步骤见 [BUILD.zh-CN.md](BUILD.zh-CN.md)。（内容由ChatGPT生成）

`downloads/sources.lock.json` 固定源码和工具链哈希。`research/dependencies-{arch}.json` 记录每架构 167 个依赖缓存包的版本和哈希；Termux 在线仓库会变化，复现时应保留缓存并核对记录。

## 验证证据与边界

- `logs/jdk26-exact-patch-check.log`：五个补丁顺序应用成功。
- `logs/make-aarch64.log`：ARM64 make images 成功。
- `logs/build-arm.log`：ARM32 make images 成功；后续 Termux deb 手册步骤因构建机当时无 Pandoc 而失败。
- `logs/manuals-{arch}.log`：安装 Pandoc 后，两个架构再次 make images 成功，手册已进入最终 tar。
- ELF 检查验证文件层面的依赖存在、架构及对齐，不保证符号版本、运行时 dlopen、Android 权限或外部依赖的所有行为。
- `tests/` 包含 CLI/JNI/GC/GUI 冒烟程序。Java 测试源码曾用主机 JDK25 编译，两个 JNI 库曾用 API28 工具链交叉编译；均不等于目标 JDK26/Android 测试通过。

JNI 是 Java 调用 C/C++ 原生库的接口。AWT 提供窗口、图形和原生控件基础；Swing 是基于 AWT 的 Java GUI 组件库。这里的 GUI 通过 X11 显示，不是 Android 原生 View 界面。

注：本文档由ChatGPT生成

来源：[官方 RI](https://jdk.java.net/java-se-ri/26)、[官方 JDK26 源码](https://github.com/openjdk/jdk/tree/jdk-26-ga)、[Termux 参考实现](https://github.com/termux/termux-packages/tree/c0df78899f52c9905e07321c999f24dd434bb7ae/packages/openjdk-25)。