
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
	return platform.system().lower()

def get_build_arch():
	return platform.machine().lower()

a = Analysis(
	['src/kvix/app.py'],
	pathex=[],
	binaries=[('src/kvix/logo.jpg', 'kvix')],
	datas=[],
	hiddenimports=[
		'PIL._tkinter_finder',

		'pynput.keyboard._base',
		'pynput.keyboard._darwin',
		'pynput.keyboard._dummy',
		'pynput.keyboard._uinput',
		'pynput.keyboard._win32',
		'pynput.keyboard._xorg',

		'pynput.mouse._base',
		'pynput.mouse._darwin',
		'pynput.mouse._dummy',
		'pynput.mouse._win32',
		'pynput.mouse._xorg',
	],
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
	name='kvix-' + get_project_version() + '-' + get_build_arch() + '-' + get_build_os() + '.exe',
	debug=False,
	bootloader_ignore_signals=False,
	strip=False,
	upx=True,
	upx_exclude=[],
	runtime_tmpdir=None,
	console=False,
	disable_windowed_traceback=False,
	argv_emulation=False,
	target_arch=None,
	codesign_identity=None,
	entitlements_file=None,
	icon = 'src/kvix/logo.jpg'
)
