from pathlib import Path
root=Path(__file__).resolve().parent.parent
p=root/'scripts/package-image.py'
s=p.read_text().replace("'include/jni.h','include/linux/jni_md.h','jmods/java.desktop.jmod']", "'include/jni.h','include/linux/jni_md.h','jmods/java.desktop.jmod',\n          'man/man1/java.1','man/man1/javac.1','legal/java.base/LICENSE']")
s=s.replace("'androidRuntimeAcceptance':'NOT_ESTABLISHED_BY_THIS_SCRIPT'", "'androidRuntimeAcceptance':'NOT_ESTABLISHED_BY_THIS_SCRIPT',\n    'status':'candidate-awaiting-device-validation',\n    'knownIssues':(['OpenJDK 26 SA has no ARM32 backend; presence of jhsdb and libsaproc does not establish ARM32 jhsdb functionality'] if args.arch=='arm' else [])")
p.write_text(s)
p=root/'recipes/openjdk-26/build.sh'
s=p.read_text()
a=s.index('# openjdk no longer officially supports 32-bit x86')
b=s.index('TERMUX_PKG_EXCLUDED_ARCHES=',a)
s=s[:a]+'# This task targets ARM32 and ARM64 only.\n'+s[b:]
s=s.replace('termux_step_configure() {','termux_step_configure() {\n    command -v pandoc >/dev/null || { echo "Pandoc is required for complete command manuals" >&2; return 1; }',1)
p.write_text(s)