import sys
import os.path
import opcode
from cx_Freeze import Executable, setup
from cx_Freeze.finder import ModuleFinder
import _collections
import collections
from cx_Freeze.module import ConstantsModule
from cx_Freeze import Freezer
from distutils.dist import DistributionMetadata
from cx_Freeze.finder import ModuleFinder
# base="Win32GUI" should be used only for Windows GUI app
base = "Win32GUI" if sys.platform == "win32" else None

# https://gist.github.com/nicoddemus/ca0acd93a20acbc42d1d
collections_path = os.path.join(os.path.dirname(opcode.__file__), 'collections')
build_exe_options = {}


metadata = DistributionMetadata()
metadata.name = 'kwix'
metadata.version = '0.0.1'

# class MyFreezer(Freezer):
# 	def __new__(cls, *args, **kwargs):
# 		result = Freezer.__new__(Freezer, *args, **kwargs)

# 		result._get_module_finder = _get_module_finder
# 		return result

freezer = Freezer.__new__(Freezer)
old_get_module_finder = freezer._get_module_finder
def _get_module_finder() -> ModuleFinder:
	result: ModuleFinder = old_get_module_finder()
	for name in ('collections'):
		result.add_alias(name, '_' + name)
	return result
freezer._get_module_finder = _get_module_finder

# class MyFreezerImpl(FreezerImpl):
# 	def __new__(cls):
# 		return MyFreezerImpl
# 	def __init__(self, *args, **kwargs):
# 		FreezerImpl.__init__(self, *args, **kwargs)


freezer.__init__(
	executables=[Executable("src/kwix/app.py", base=base)],
	constants_module=ConstantsModule(metadata.version, constants=[]),
	includes = [],
	excludes = [],
	packages = [],
	replace_paths = [],
	compress=True,
	optimize = 0,
	path = ['src'],
	target_dir = 'dist/kwix-exe',
	bin_includes=[],
	bin_excludes=[],
	bin_path_includes=[],
	bin_path_excludes=[],
	include_files=[],
	zip_includes=[],
	zip_include_packages=['pynput'],
	zip_exclude_packages=['*'],
	silent=0,
	metadata=metadata,
	include_msvcr=False,
)

freezer.freeze()
exit()

setup(
	executables=[Executable("src/kwix/app.py", base=base)],
	options = {
		'build_exe': {
			'path': ['src'],
			'zip_include_packages': ['pynput'],
			#'include_files': [(collections_path, 'collections')], "excludes": ["collections"]
		}
	}
)
