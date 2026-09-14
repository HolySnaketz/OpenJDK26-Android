# 源码包说明

openjdk/ 是官方 OpenJDK 26+35 RI 源码应用当前全部 Android/Termux 补丁后的完整源码。路径模板已替换为 /data/data/com.termux/files/usr，所有补丁影响的文件均与 ARM64、ARM32 实际编译树逐字节比对通过。

recipes/ 保留原始补丁与构建配方；scripts/、tests/ 和文档保留构建及验收材料。不要对 openjdk/ 再次应用这些补丁。

复现原有构建流程时，scripts/fetch-sources.ps1 根据 downloads/sources.lock.json 获取官方原始源码、NDK 和引导 JDK，随后按 BUILD.zh-CN.md 操作。已有脚本包含本机固定路径，迁移目录时需统一调整。工具链、Termux 二进制依赖及编译输出没有装入此源码包。

两个 ABI 共用此源码，不需要分成两个源码包。源码许可证保留在 openjdk/LICENSE、openjdk/ASSEMBLY_EXCEPTION 和各源文件中。当前候选状态、尚未进行的 Android 真机验收及 ARM32 SA 已知问题见 README.md。
