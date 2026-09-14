# 构建与复现

以下命令在 WSL Ubuntu-26.04 中执行。脚本中的路径针对本机固定；迁移机器需统一修改路径，不要改 Android 安装前缀。源码和下载锁在 Windows 主目录，临时树在 WSL ext4。

## 输入与工具

Windows PowerShell 执行 `scripts/fetch-sources.ps1` 可按 `downloads/sources.lock.json` 下载和验证四份固定输入，不改写锁文件。GitHub 自动生成 tar 的字节若发生变化，必须人工核实，不能自动接受新哈希。

本次构建所用主机依赖包括：build-essential、autoconf、clang/llvm/lld21、cmake、ninja-build、pkg-config、bison、flex、gawk、gettext、libtool-bin、patch、rsync、file、zstd、patchelf、gperf、texinfo、lzip、tcl、fuse-overlayfs、pandoc、unzip、curl、jq、python3。需要 FUSE 支持。

新环境才执行 `bash scripts/prepare-wsl-scratch.sh`，该脚本拒绝覆盖已有临时树。首次需创建构建用户可写的 `/data` 及 `/data/data`；若已存在其他项目数据，先核实归属，不得覆盖。NDK 工具链由固定 Termux 构建脚本按 API28 处理。

## 构建

```sh
cd /mnt/d/projects/arron/shuoshuo-07/openjdk26-android
bash scripts/build-android.sh aarch64
# 等前一个构建退出，再切换共享 staging；禁止并行两个 ABI。
bash scripts/switch-staging-arch.sh arm
bash scripts/build-android.sh arm
```

每个架构的镜像位于：

```text
/home/arron/projects/openjdk26-android-build/build-ARCH/openjdk-26/src/build/linux-ARCH-server-release/images/jdk
```

ARCH 为 aarch64 或 arm。增量源码修复后用 `bash scripts/resume-make.sh ARCH`；前提是 `/data/TERMUX_ARCH` 与 ARCH 一致。不要通过重新执行完整 build-android 丢失构建树里的尚未导出补丁。

本次首次配置未找到 Pandoc，因此 make images 不含手册。现已安装 Pandoc，未来配置会检测它；现存构建树通过以下命令补齐手册并重建镜像，日志已保留：

```sh
bash scripts/build-manuals.sh ARCH
```

`recipes/openjdk-26/build.sh` 保留 Termux 的 deb 安装步骤，但本次正式检查对象是官方 `images/jdk` 和本项目 tar。首次 ARM32 deb 后处理失败不等于 make images 失败，也未在文档中将该 deb 流水线声称为通过。

## 检查与打包

```sh
python3 scripts/verify-rebased-patch.py
python3 scripts/package-image.py ARCH /home/arron/projects/openjdk26-android-build/build-ARCH/openjdk-26/src/build/linux-ARCH-server-release/images/jdk
python3 scripts/inspect-elf.py ARCH
python3 scripts/record-dependencies.py
```

打包强制检查核心工具、GUI 原生库、JNI 头文件、java.desktop jmod、官方手册和许可证，并校验所有 ELF 的 ABI。manifest 明确记录候选状态及 ARM32 SA 已知问题。

`downloads/` 中额外的 GA tar、`.partial` 及 Windows `source/` 不用于构建。`scripts/` 中生成初始补丁的 prepare/fix 单次脚本保留作工作记录，不属于复现入口；正式补丁是 `recipes/openjdk-26/*.patch` 加路径模板 diff，按 Termux 标准步骤应用。不要重复运行单次补丁生成脚本。

依赖记录对应 WSL `build-ARCH/_cache-ARCH/*.deb`。应保存这两个缓存目录；只固定 Termux 源码提交并不能固定在线仓库未来的二进制依赖。

注：本文档由ChatGPT生成