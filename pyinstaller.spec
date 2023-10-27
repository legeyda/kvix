
import io
import platform
from contextlib import redirect_stdout

from setuptools_git_versioning import __main__ as print_project_version

pythonpath = ['src']

def get_project_version() -> str:
	with io.StringIO() as buf, redirect_stdout(buf):
		print_project_version()
		return buf.getvalue().strip()

def get_build_os():
	result = platform.system().lower()
	if 'linux' == result:
		return result
	raise Exception('unknown platform.system() value: ' + platform.system())

def get_build_arch():
	return platform.machine().lower()

a = Analysis(
	['src/kwix/app.py'],
	pathex=[],
	binaries=[('src/kwix/logo.jpg', 'kwix')],
	datas=[],
	hiddenimports=['PIL._tkinter_finder'],
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
