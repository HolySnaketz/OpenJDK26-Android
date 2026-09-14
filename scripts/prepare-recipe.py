#!/usr/bin/env python3
"""Prepare a JDK 26 recipe from a pinned Termux reference, without running it."""
from pathlib import Path
import re
import shutil

root = Path(__file__).resolve().parent.parent
reference = root / 'vendor/termux-packages/packages/openjdk-25'
destination = root / 'recipes/openjdk-26'
if destination.exists():
    raise SystemExit('Recipe already exists; inspect it rather than overwriting local edits.')
destination.mkdir(parents=True)
# Do not import a feature-removal patch or an old ASCII-only locale workaround.
excluded = {'0005-android-prevent-build-of-libsa.patch', '0010-Use-ASCII-codeset-on-android.patch'}
for source in reference.iterdir():
    if source.is_file() and source.name not in excluded and source.name != 'build.sh':
        target = destination / source.name.replace('openjdk-25', 'openjdk-26')
        target.write_text(source.read_text().replace('java-25-openjdk', 'java-26-openjdk').replace('openjdk-25', 'openjdk-26'))
recipe = (reference / 'build.sh').read_text()
recipe = recipe.replace('openjdk-25', 'openjdk-26').replace('java-25-openjdk', 'java-26-openjdk')
recipe = re.sub(r'^TERMUX_PKG_VERSION=.*$', 'TERMUX_PKG_VERSION="26"', recipe, flags=re.M)
recipe = re.sub(r'^TERMUX_PKG_SRCURL=.*$', 'TERMUX_PKG_SRCURL="file://' + str(root / 'downloads/openjdk-26+35_src.zip') + '"', recipe, flags=re.M)
recipe = re.sub(r'^TERMUX_PKG_SHA256=.*$', 'TERMUX_PKG_SHA256=215fb2cc080e334538f5c57a2be3d34e64e97cf3c7655fe485b3cf13c87e1602', recipe, flags=re.M)
recipe = re.sub(r'^TERMUX_PKG_AUTO_UPDATE=.*$', 'TERMUX_PKG_AUTO_UPDATE=false', recipe, flags=re.M)
recipe = re.sub(r'^TERMUX_PKG_UPDATE_VERSION_REGEXP=.*\n', '', recipe, flags=re.M)
recipe = recipe.replace('TERMUX_PKG_MAINTAINER="@termux"', 'TERMUX_PKG_MAINTAINER="Local Android JDK build"')
recipe = recipe.replace('--with-vendor-name="Termux"', '--with-vendor-name="Local OpenJDK Android Port"')
# Include GUI/runtime dependencies explicitly and preserve libsaproc support.
recipe = recipe.replace('littlecms, alsa-plugins"', 'littlecms, alsa-plugins, freetype, giflib, libpng, libx11, libxext, libxi, libxrender, libxtst, libelf"')
recipe = recipe.replace('xorgproto, alsa-lib"', 'xorgproto, alsa-lib, libelf"')
recipe = recipe.replace('# enable lto\n__jvm_features="link-time-opt"', '# Use upstream server defaults, including G1 on ARM32; investigate failures instead of disabling it.\n__jvm_features=""')
start = recipe.index('termux_step_host_build() {')
end = recipe.index('\ntermux_step_pre_configure()', start)
recipe = recipe[:start] + '''termux_step_host_build() {
    cp -a "''' + str(root / 'toolchains/bootjdk25') + '''/." "$TERMUX_PKG_HOSTBUILD_DIR/"
}
''' + recipe[end:]
start = recipe.index('\n\t# g1gc causes')
end = recipe.index('\n}\n', start)
recipe = recipe[:start] + '\n\t# Keep G1 and the upstream architecture feature set enabled.\n' + recipe[end:]
recipe = recipe.replace(' --with-jvm-features="${__jvm_features}"', '')
# Empty JVM features are unnecessary; avoid a configure argument with ambiguous semantics.
recipe = re.sub(r'^\s*--with-jvm-features=.*\\\n', '', recipe, flags=re.M)
recipe = recipe.replace('\n__jvm_features=""', '')
(destination / 'build.sh').write_text(recipe)
print(destination)
