
import logging
import os
import pathlib
import queue
import threading
import traceback
from time import sleep
from types import UnionType
from typing import Any, Callable, Generic, Type, TypeAlias, TypeVar, cast

import pyclip


class CallableWrapper:
	def __init__(self, func: Callable[[], None]):
		self._func = func
		self.ready = False
	def __call__(self):
		try:
			self._func()
		finally:
			self.ready = True
	def wait(self, sleep_seconds: float = 0.001):
		while not self.ready:
			sleep(sleep_seconds)

class ThreadRouter:
	def __init__(self, target_thread: threading.Thread = threading.current_thread()):
		self._target_thread = target_thread
		self._queue = queue.Queue()
	def exec(self, action: Callable[[], None]):
		if threading.current_thread() == self._target_thread:
			action()
		else:
			wrap = CallableWrapper(action)
			self._queue.put(wrap)
			wrap.wait()
	def process(self):
		if threading.current_thread() != self._target_thread:
			raise RuntimeError('wrong thread')
		while True:
			try:
				item = self._queue.get(False)
			except queue.Empty:
				return
			try:
				item()
			except Exception:
				logging.error(traceback.format_exc())
	


	


def get_data_dir() -> pathlib.Path:
	home = pathlib.Path.home()
	if '/' in str(home):
		return home.joinpath('.local', 'share', 'kwix')
	elif '\\' in str(home):
		appdata = os.getenv('APPDATA')
		if appdata:
			return pathlib.Path(appdata, 'kwix')
		else:
			return home.joinpath('AppData', 'kwix')
		


def get_config_dir() -> pathlib.Path:
	home = pathlib.Path.home()
	if '/' in str(home):
		return home.joinpath('.config', 'kwix')
	elif '\\' in str(home):
		appdata = os.getenv('APPDATA')
		if appdata:
			return pathlib.Path(appdata, 'kwix')
		else:
			return home.joinpath('AppData', 'roaming', 'kwix')
		
def get_cache_dir() -> pathlib.Path:
	home = pathlib.Path.home()
	if '/' in str(home):
		return home.joinpath('.cache', 'kwix')
	elif '\\' in str(home):
		appdata = os.getenv('LOCALAPPDATA')
		if appdata:
			return pathlib.Path(appdata, 'kwix')
		else:
			return home.joinpath('AppData', 'kwix')
		



key_mappings: list[dict[str, str]]=[]
key_sets: list[str] = [
	'abcdefghijklmnopqrstuvwxyz',
	'фисвуапршолдьтщзйкыегмцчня']
for key_set in key_sets:
	for other_key_set in key_sets:
		if key_sets is other_key_set:
			continue
		key_mappings.append(dict(zip(list(key_set), list(other_key_set))))
		

def query_match(query: str, *contents: str) -> bool:
	if not query:
		return True
	def normalize(x: str):
		return x.lower().replace('ё', 'е')
	for word in query.split():
		if not word:
			continue
		word = normalize(word)
		for item in contents:
			if word in normalize(item.lower()):
				return True
	return False

class Sentinel():
    pass
_sentinel = Sentinel()

T = TypeVar("T")
class Propty(Generic[T]):
	def __init__(self, 
	      type: Type[T] = cast(Type[T], None),
	      default_value: T = cast(T, _sentinel),
	      default_supplier: Callable[[], T] = cast(Callable[[], T], None),
		  on_change: str | bool | Callable[[Any, T], None] = False,
		  private_name: str = '',
		  type_check: bool = False,
		  writeable: bool = True,
		  required: bool = False,
		  getter: Callable[[Any], T] | None = None,
		  setter: Callable[[Any, T], None] | None = None):
		self._name = ''
		self._type = type
		if not writeable and setter:
			raise RuntimeError('Propty: not writeable and setter')
		if required and bool(default_supplier):
			raise RuntimeError('Propty: required and default_supplier')
		self._default_supplier = default_supplier or ((lambda: default_value) if default_value is not _sentinel else None) or type or (lambda: None)
		self._on_change = on_change
		self._private_name = private_name
		if type_check and not type:
			raise RuntimeError('Propty: type_check and not type')
		self._type_check = type_check
		self._writeable = writeable
		self._required = required
		self._getter = getter or self._builtin_getter
		self._setter = setter or self._builtin_setter
	def __set_name__(self, owner: Any, name: str):
		self._name = name
		if self._on_change is True:
			self._on_change = '_on_change_' + name
		if not self._private_name:
			self._private_name = '_' + name
	def __set__(self, obj: Any, value: T):
		self._assert_obj(obj)
		if not self._writeable:
			raise AttributeError('property for ' + self._name + ' is not writeable')
		self._assert_type(value)
		if self._on_change:
			old_value: T = self._get_silent(obj, True)
			if old_value is not value:
				self._call_on_change(obj, value)
			self._setter(obj, value)
		else:
			self._setter(obj, value)
	def _assert_type(self, value: T):
		if not self._type_check:
			return
		assert self._type
		if not isinstance(value, self._type):
			raise AttributeError('property ' + self._name + ': unexpected type')
	def _call_on_change(self, obj: Any, value: T) -> None:
		if False is self._on_change:
			return
		if isinstance(self._on_change, str):
			if not hasattr(obj, self._on_change):
				raise RuntimeError('method ' + self._on_change + ' not found')
			func = cast(Callable[[T], None], getattr(obj, self._on_change))
			if not callable(func):
				raise RuntimeError('attr ' + self._on_change + ' expected to be callable')
			func(value)
		elif callable(self._on_change):
			self._on_change(obj, value)
		else:
			raise AssertionError('callable expected')
	def _builtin_setter(self, obj: Any, value: T) -> None:
		setattr(obj, self._private_name, value)
	def __get__(self, obj: Any, objtype: Any = None) -> T:
		self._assert_obj(obj)
		result = self._getter(obj)
		self._assert_type(result)
		setattr(obj, self._private_name, result)
		return result
	def _assert_obj(self, obj: Any):
		if not obj:
			raise AttributeError("Propty is for instances only")
	def _builtin_getter(self, obj: Any) -> T:
		return self._get_silent(obj)
	def _get_silent(self, obj: Any, silent: bool = False) -> T:
		self._assert_obj(obj)
		if not hasattr(obj, self._private_name):
			if self._required:
				if silent:
					return cast(T, None)
				raise RuntimeError('property is required')
			return self._default_supplier()
		return getattr(obj, self._private_name)



TypeKey = TypeVar('TypeKey')
TypeValue = TypeVar('TypeValue')
def ensure_key(dest: dict[TypeKey, TypeValue], key: TypeKey, supplier: Callable[[], TypeValue]) -> TypeValue:
	if key in dest:
		return dest[key]
	else:
		value = supplier()
		dest[key] = value
		return value


ClassInfo: TypeAlias = type | UnionType | tuple['ClassInfo', ...]
def ensure_type(value: Any | None, type_or_tuple: ClassInfo):
	if not isinstance(value, type_or_tuple):
		raise RuntimeError('value expected to be %s' % type_or_tuple)
	return value


def apply_template(template: str, **values: str) -> str:
	result = str(template)
	for key, value in values.items():
		result = result.replace('{{' + str(key) + '}}', str(value))
	return result


def paste_str() -> str:
	try:
		return pyclip.paste().decode('UTF-8')
	except Exception as e:
		print(e)
	return ''