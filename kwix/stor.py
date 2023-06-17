from __future__ import annotations

import os.path
import pathlib
from typing import Any

import yaml


class Stor:
	def __init__(self, data: Any = None):
		self.data = data
	def load(self) -> None: ...
	def save(self) -> None: ...



class YamlFile(Stor):
	def __init__(self, file_path: pathlib.Path):
		super().__init__({})
		self._file_path = file_path
	def load(self) -> None:
		if not os.path.exists(self._file_path):
			self.data = None
			return
		with open(self._file_path, "r") as stream:
			self.data = yaml.safe_load(stream)
	def save(self) -> None:
		dir_path = os.path.dirname(self._file_path)
		if not os.path.exists(dir_path):
			os.makedirs(dir_path)
		with open(self._file_path, 'w') as out:
			yaml.dump(self.data, out, default_flow_style=False)