# https://setuptools.pypa.io/en/latest/build_meta.html#dynamic-build-dependencies-and-other-build-meta-tweaks
# https://github.com/pypa/setuptools/blob/main/setuptools/build_meta.py
# https://peps.python.org/pep-0517/
from setuptools import build_meta as _orig
from setuptools.build_meta import *

print('==== HELLOO!!! ====')

def get_requires_for_build_wheel(self, config_settings=None):
	result = _orig.get_requires_for_build_wheel(config_settings)
	print('===========================')
	print('===========================')
	print('===========================')
	print('config_settings is ' + str(config_settings))
	print('requires is ' + str(result))
	return result