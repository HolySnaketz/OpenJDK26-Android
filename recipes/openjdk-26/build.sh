TERMUX_PKG_HOMEPAGE=https://openjdk.java.net
TERMUX_PKG_DESCRIPTION="Java development kit and runtime"
TERMUX_PKG_LICENSE="GPL-2.0"
TERMUX_PKG_MAINTAINER="Local Android JDK build"
TERMUX_PKG_VERSION="26"
TERMUX_PKG_SRCURL="file:///mnt/d/projects/arron/shuoshuo-07/openjdk26-android/downloads/openjdk-26+35_src.zip"
TERMUX_PKG_SHA256=215fb2cc080e334538f5c57a2be3d34e64e97cf3c7655fe485b3cf13c87e1602
TERMUX_PKG_AUTO_UPDATE=false
TERMUX_PKG_DEPENDS="libandroid-shmem, libandroid-spawn, libiconv, libjpeg-turbo, zlib, littlecms, alsa-plugins, freetype, giflib, libpng, libx11, libxext, libxi, libxrender, libxtst, libelf"
TERMUX_PKG_BUILD_DEPENDS="cups, fontconfig, libxrandr, libxt, xorgproto, alsa-lib, libelf"
# openjdk-26-x is recommended because X11 separation is still very experimental.
TERMUX_PKG_RECOMMENDS="ca-certificates-java, openjdk-26-x, resolv-conf"
# This task targets ARM32 and ARM64 only.
TERMUX_PKG_EXCLUDED_ARCHES="i686"
TERMUX_PKG_SUGGESTS="cups"
TERMUX_PKG_BUILD_IN_SRC=true
TERMUX_PKG_HAS_DEBUG=false
TERMUX_PKG_HOSTBUILD=true
# Use upstream server defaults, including G1 on ARM32; investigate failures instead of disabling it.

termux_step_get_source() {
    termux_download_src_archive
    local archive="$TERMUX_PKG_CACHEDIR/$(basename "$TERMUX_PKG_SRCURL")"
    # Official RI ZIP begins with openjdk/.editorconfig, not a directory entry.
    # The generic Termux ZIP extractor assumes its first entry is the root directory.
    local unpack="$TERMUX_PKG_TMPDIR/official-ri-source"
    mkdir -p "$unpack"
    unzip -q "$archive" -d "$unpack"
    test -f "$unpack/openjdk/configure"
    mv "$unpack/openjdk" "$TERMUX_PKG_SRCDIR"
}

termux_step_host_build() {
    cp -a "/mnt/d/projects/arron/shuoshuo-07/openjdk26-android/toolchains/bootjdk25/." "$TERMUX_PKG_HOSTBUILD_DIR/"
}

termux_step_pre_configure() {
	unset JAVA_HOME

	local patch="$TERMUX_PKG_BUILDER_DIR/tmpdir-path-length.diff"
	local tmpdir_path="$TERMUX_PREFIX/tmp"
	echo "Applying patch: $(basename "$patch")"
	test -f "$patch" && sed \
		-e "s%\@TERMUX_PREFIX\@%${TERMUX_PREFIX}%g" \
		-e "s%\@TERMUX_TMPDIR_PATH_LENGTH\@%${#tmpdir_path}%g" \
		"$patch" | patch --silent -p1

	# Keep G1 and the upstream architecture feature set enabled.

}

termux_step_configure() {
    command -v pandoc >/dev/null || { echo "Pandoc is required for complete command manuals" >&2; return 1; }
	local jdk_ldflags="-L${TERMUX_PREFIX}/lib \
		-Wl,-rpath=$TERMUX_PREFIX/lib/jvm/java-26-openjdk/lib \
		-Wl,-rpath=${TERMUX_PREFIX}/lib -Wl,--enable-new-dtags"
	bash ./configure \
		--with-boot-jdk="$TERMUX_PKG_HOSTBUILD_DIR" \
		--disable-precompiled-headers \
		--disable-warnings-as-errors \
		--enable-option-checking=fatal \
		--with-version-pre="" \
		--with-version-opt="" \
		--with-jvm-variants=server \
		--with-debug-level=release \
		--openjdk-target=$TERMUX_HOST_PLATFORM \
		--with-toolchain-type=clang \
		--with-extra-cflags="$CFLAGS $CPPFLAGS -DLE_STANDALONE -D__ANDROID__=1 -D__TERMUX__=1" \
		--with-extra-cxxflags="$CXXFLAGS $CPPFLAGS -DLE_STANDALONE -D__ANDROID__=1 -D__TERMUX__=1" \
		--with-extra-ldflags="${jdk_ldflags} -Wl,--as-needed -landroid-shmem -landroid-spawn" \
		--with-cups-include="$TERMUX_PREFIX/include" \
		--with-fontconfig-include="$TERMUX_PREFIX/include" \
		--with-freetype-include="$TERMUX_PREFIX/include/freetype2" \
		--with-freetype-lib="$TERMUX_PREFIX/lib" \
		--with-alsa="$TERMUX_PREFIX" \
		--with-alsa-include="$TERMUX_PREFIX/include/alsa" \
		--with-alsa-lib="$TERMUX_PREFIX/lib" \
		--with-x="$TERMUX_PREFIX/include/X11" \
		--x-includes="$TERMUX_PREFIX/include/X11" \
		--x-libraries="$TERMUX_PREFIX/lib" \
		--with-giflib=system \
		--with-lcms=system \
		--with-libjpeg=system \
		--with-libpng=system \
		--with-zlib=system \
		--with-vendor-name="Local OpenJDK Android Port" \
		AR="$AR" \
		NM="$NM" \
		OBJCOPY="$OBJCOPY" \
		OBJDUMP="$OBJDUMP" \
		STRIP="$STRIP" \
		CXXFILT="llvm-cxxfilt" \
		BUILD_CC="$TERMUX_HOST_LLVM_BASE_DIR/bin/clang" \
		BUILD_CXX="$TERMUX_HOST_LLVM_BASE_DIR/bin/clang++" \
		BUILD_NM="$TERMUX_HOST_LLVM_BASE_DIR/bin/llvm-nm" \
		BUILD_AR="$TERMUX_HOST_LLVM_BASE_DIR/bin/llvm-ar" \
		BUILD_OBJCOPY="$TERMUX_HOST_LLVM_BASE_DIR/bin/llvm-objcopy" \
		BUILD_STRIP="$TERMUX_HOST_LLVM_BASE_DIR/bin/llvm-strip" \
		--with-jobs=$TERMUX_PKG_MAKE_PROCESSES
}

termux_step_make() {
	cd build/linux-${TERMUX_ARCH/i686/x86}-server-release
	make images
}

termux_step_make_install() {
	rm -rf  $TERMUX_PREFIX/lib/jvm/java-26-openjdk
	mkdir -p $TERMUX_PREFIX/lib/jvm/java-26-openjdk
	cp -r build/linux-${TERMUX_ARCH/i686/x86}-server-release/images/jdk/* \
		$TERMUX_PREFIX/lib/jvm/java-26-openjdk/
	find $TERMUX_PREFIX/lib/jvm/java-26-openjdk/ -name "*.debuginfo" -delete

	# Dependent projects may need JAVA_HOME.
	mkdir -p $TERMUX_PREFIX/lib/jvm/java-26-openjdk/etc/profile.d
	echo "export JAVA_HOME=$TERMUX_PREFIX/lib/jvm/java-26-openjdk/" > \
		$TERMUX_PREFIX/lib/jvm/java-26-openjdk/etc/profile.d/java.sh
}

termux_step_post_make_install() {
	cd $TERMUX_PREFIX/lib/jvm/java-26-openjdk/man/man1
	for manpage in *.1; do
		gzip "$manpage"
	done

	# Make sure that our alternatives file is up to date.
	binaries="$(find $TERMUX_PREFIX/lib/jvm/java-26-openjdk/bin -executable -type f | xargs -I{} basename "{}" | xargs echo)"
	manpages="$(find $TERMUX_PREFIX/lib/jvm/java-26-openjdk/man/man1 -name "*.1.gz" | xargs -I{} basename "{}" | xargs echo)"

	local failure=false
	for binary in $binaries; do
		grep -q "lib/jvm/java-26-openjdk/bin/${binary}$" "$TERMUX_PKG_BUILDER_DIR"/openjdk-26.alternatives || {
			echo "ERROR: Missing entry for binary: $binary in openjdk-26.alternatives"
			failure=true
		}
	done

	for manpage in $manpages; do
		grep -q "lib/jvm/java-26-openjdk/man/man1/${manpage}$" "$TERMUX_PKG_BUILDER_DIR"/openjdk-26.alternatives || {
			echo "ERROR: Missing entry for manpage: $manpage in openjdk-26.alternatives"
			failure=true
		}
	done
	if [[ "$failure" = true ]]; then
		termux_error_exit "ERROR: openjdk-26.alternatives is not up to date, please update it."
	fi
}
