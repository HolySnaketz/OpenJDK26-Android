from pathlib import Path
import hashlib,json,shutil,subprocess,tempfile,tarfile
root=Path(__file__).resolve().parent.parent
scratch=Path('/home/arron/projects/openjdk26-android-build')
work=Path(tempfile.mkdtemp(prefix='source-delivery-',dir=scratch))
name='openjdk-26-android-source'
bundle=work/name
bundle.mkdir()
source=bundle/'openjdk'
subprocess.run(['unzip','-q',str(root/'downloads/openjdk-26+35_src.zip'),'-d',str(bundle)],check=True)
prefix='/data/data/com.termux/files/usr'
patches=sorted((root/'recipes/openjdk-26').glob('*.patch'))+ [root/'recipes/openjdk-26/tmpdir-path-length.diff']
changed=set()
logs=[]
for patch in patches:
    content=patch.read_text().replace('@TERMUX_PREFIX@',prefix).replace('@TERMUX_TMPDIR_PATH_LENGTH@',str(len(prefix+'/tmp')))
    result=subprocess.run(['patch','--batch','--fuzz=0','-p1'],input=content,cwd=source,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    logs.append(patch.name+'\n'+result.stdout)
    if result.returncode: raise SystemExit(result.stdout)
    changed.update(line[6:] for line in content.splitlines() if line.startswith('+++ b/'))
for arch in ('aarch64','arm'):
    built=scratch/f'build-{arch}/openjdk-26/src'
    for relative in changed:
        assert (source/relative).read_bytes()==(built/relative).read_bytes(),f'{arch} build differs: {relative}'
print(f'All {len(changed)} patched files match both compiled source trees.',flush=True)
for folder in ('recipes','tests'):
    shutil.copytree(root/folder,bundle/folder,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
shutil.copytree(root/'scripts',bundle/'scripts',ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
for file in ('README.md','BUILD.zh-CN.md','INSTALL.zh-CN.md'):
    shutil.copy2(root/file,bundle/file)
(bundle/'downloads').mkdir()
shutil.copy2(root/'downloads/sources.lock.json',bundle/'downloads/sources.lock.json')
(bundle/'research').mkdir()
for path in (root/'research').glob('dependencies-*.json'):
    shutil.copy2(path,bundle/'research'/path.name)
(bundle/'SOURCE-PACKAGE.zh-CN.md').write_text('''# 源码包说明

openjdk/ 是官方 OpenJDK 26+35 RI 源码应用当前全部 Android/Termux 补丁后的完整源码。路径模板已替换为 /data/data/com.termux/files/usr，所有补丁影响的文件均与 ARM64、ARM32 实际编译树逐字节比对通过。

recipes/ 保留原始补丁与构建配方；scripts/、tests/ 和文档保留构建及验收材料。不要对 openjdk/ 再次应用这些补丁。

复现原有构建流程时，scripts/fetch-sources.ps1 根据 downloads/sources.lock.json 获取官方原始源码、NDK 和引导 JDK，随后按 BUILD.zh-CN.md 操作。已有脚本包含本机固定路径，迁移目录时需统一调整。工具链、Termux 二进制依赖及编译输出没有装入此源码包。

两个 ABI 共用此源码，不需要分成两个源码包。源码许可证保留在 openjdk/LICENSE、openjdk/ASSEMBLY_EXCEPTION 和各源文件中。当前候选状态、尚未进行的 Android 真机验收及 ARM32 SA 已知问题见 README.md。
''')
(bundle/'source-patch-verification.log').write_text('\n'.join(logs))
manifest={'base':'Official OpenJDK 26+35 RI','sourceArchiveSha256':'215fb2cc080e334538f5c57a2be3d34e64e97cf3c7655fe485b3cf13c87e1602','patchedFilesMatchedBothBuilds':len(changed),'termuxPrefix':prefix,'patches':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in patches}}
(bundle/'source-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
archive=work/(name+'.tar.xz')
print('Compressing source archive...',flush=True)
subprocess.run(['tar','--sort=name','--owner=0','--group=0','--numeric-owner','-I','xz -T4 -6','-cf',str(archive),'-C',str(work),name],check=True)
subprocess.run(['xz','-t',str(archive)],check=True)
with tarfile.open(archive,'r:xz') as tar:
    count=0
    for member in tar:
        assert not member.name.startswith('/') and '..' not in Path(member.name).parts
        count+=1
final=root/'dist'/archive.name
partial=final.with_suffix('.xz.partial')
shutil.copyfile(archive,partial)
with partial.open('rb') as stream: digest=hashlib.file_digest(stream,'sha256').hexdigest()
with archive.open('rb') as stream: assert digest==hashlib.file_digest(stream,'sha256').hexdigest()
partial.replace(final)
(final.parent/(final.name+'.sha256')).write_text(digest+'  '+final.name+'\n')
print(json.dumps({'archive':str(final),'bytes':final.stat().st_size,'sha256':digest,'archiveEntries':count}),flush=True)