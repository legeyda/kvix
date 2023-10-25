
import os.path
from pathlib import Path
import glob
import platform

pythonpath = ['src']

def find_sub_modules(parent_module_full_name: str):
	parent_module_sub_path = os.path.join(*parent_module_full_name.split('.'))
	for root in pythonpath:
		parent_module_path = os.path.join(root, parent_module_sub_path)
		for candidate in os.scandir(Path(parent_module_path)):
			file = Path(os.path.join(root, parent_module_sub_path, os.path.basename(candidate)))
			if file.is_file():
				yield parent_module_full_name + '.' + os.path.splitext(file.name)[0]

def get_project_version() -> str:
	prefix='dist/kwix-'
	suffix='.tar.gz'
	files: list[str] = glob.glob(prefix + '*' + suffix)
	if len(files) != 1:
		raise Exception('cannot get project version: expected single file matching glob {prefix}*{suffix}')
	return files[0][len(prefix):-len(suffix)]
	
project_version = get_project_version()

def get_build_os():
	if 'linux' == platform.system().lower():
		return 'linux'
	raise Exception('unknown platform.system() value: ' + platform.system())

def get_build_arch():
	if 'x86_64' == platform.machine().lower():
		return 'x64'
	raise Exception('unknown platform.machine() value: ' + platform.machine())

a = Analysis(
    ['src/kwix/app.py'],
    pathex=[],
    binaries=[('src/kwix/logo.jpg', 'kwix')],
    datas=[],
    hiddenimports=list(find_sub_modules('kwix.plugin.builtin')) + ['PIL._tkinter_finder'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

def exclusion_filter(path:str):
	return path.startswith('share/icons') or path.startswith('share/themes')
a.datas = [entry for entry in a.datas if not exclusion_filter(entry[0])]

pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='kwix-' + project_version + '-' + get_build_os() + '-' + get_build_arch(),
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
	icon = 'src/kwix/logo.jpg'
)
