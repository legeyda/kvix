
import logging
import os.path
import platform
import sys
from pathlib import Path

import setuptools_git_versioning

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
	parser = setuptools_git_versioning._parser()
	namespace = parser.parse_args()
	log_level = setuptools_git_versioning.VERBOSITY_LEVELS.get(namespace.verbose, logging.DEBUG)
	logging.basicConfig(level=log_level, format=setuptools_git_versioning.LOG_FORMAT, stream=sys.stderr)
	return str(setuptools_git_versioning.get_version(root=namespace.root))
	
def get_build_os():
	result = platform.system().lower()
	if 'linux' == result:
		return result
	raise Exception('unknown platform.system() value: ' + platform.system())

def get_build_arch():
	result = platform.machine().lower()
	if 'x86_64' == result:
		return result
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
	name='kwix-' + get_project_version() + '-' + get_build_arch() + '-' + get_build_os() + '.exe',
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
