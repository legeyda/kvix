import logging
import os
import pathlib
import queue
import threading
import traceback
from time import sleep
from types import UnionType
from typing import Any, Callable, Generic, Type, TypeAlias, TypeVar, cast
import jinja2
import datetime


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


_thread_sentinel = threading.Thread()


class ThreadRouter:
    def __init__(self, target_thread: threading.Thread = _thread_sentinel):
        self._target_thread = (
            target_thread if target_thread is not _thread_sentinel else threading.current_thread()
        )
        self._queue = queue.Queue[Callable[[], None]]()

    def exec(self, action: Callable[[], None]):
        if threading.current_thread() == self._target_thread:
            action()
        else:
            wrap = CallableWrapper(action)
            self._queue.put(wrap)
            wrap.wait()

    def process(self):
        if threading.current_thread() != self._target_thread:
            raise RuntimeError("wrong thread")
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
    if "/" in str(home):
        return home.joinpath(".local", "share", "kvix")
    elif "\\" in str(home):
        appdata = os.getenv("APPDATA")
        if appdata:
            return pathlib.Path(appdata, "kvix")
        else:
            return home.joinpath("AppData", "kvix")
    else:
        raise RuntimeError("unexpected platform separator derived from HOME")


def get_config_dir() -> pathlib.Path:
    home = pathlib.Path.home()
    if "/" in str(home):
        return home.joinpath(".config", "kvix")
    elif "\\" in str(home):
        appdata = os.getenv("APPDATA")
        if appdata:
            return pathlib.Path(appdata, "kvix")
        else:
            return home.joinpath("AppData", "roaming", "kvix")
    else:
        raise RuntimeError("unexpected platform separator derived from HOME")


def get_cache_dir() -> pathlib.Path:
    home = pathlib.Path.home()
    if "/" in str(home):
        return home.joinpath(".cache", "kvix")
    elif "\\" in str(home):
        appdata = os.getenv("LOCALAPPDATA")
        if appdata:
            return pathlib.Path(appdata, "kvix")
        else:
            return home.joinpath("AppData", "kvix")
    else:
        raise RuntimeError("unexpected platform separator derived from HOME")


key_mappings: list[dict[str, str]] = []
key_sets: list[str] = [
    "abcdefghijklmnopqrstuvwxyz",
    "фисвуапршолдьтщзйкыегмцчня",
]
for key_set in key_sets:
    for other_key_set in key_sets:
        if key_sets is other_key_set:
            continue
        key_mappings.append(dict(zip(list(key_set), list(other_key_set))))


def query_match(query: str, *contents: str) -> str:
    if not query:
        return ""

    def normalize(x: str):
        return x.lower().replace("ё", "е")

    for word in query.split():
        word = normalize(word)
        if not word:
            continue
        for item in contents:
            if word in normalize(item.lower()):
                return word
    return ""


class Sentinel:
    pass


_sentinel = Sentinel()

T = TypeVar("T")


class Propty(Generic[T]):  # todo move to separate module
    """
    Usage variants:
    x = Propty(str) # just wrapper around self._x
    # like previous, with additional customizations
    x = Propty(dict,default_supplier=lambda: {'a':1}, private_name='_private_x_value',
            on_change='_on_change_x')
    # alternative to x = property(fget=_get_x, fset=_set_x)
    x = Propty(str, getter = _get_x, setter = _set_x)
    # just like previous but supports override of getter and setter in child classes
    x = Propty(str, getter = '_get_x', setter = '_set_x')

    """

    @staticmethod
    def create_prototype(**fix_kwargs: Any):
        def result(*args: Any, **kwargs: Any):
            kwargs.update(fix_kwargs)
            return Propty(*args, **kwargs)

        return result

    _type_default_value = cast(Type[T], None)
    _defaut_value_defalt_value = cast(T, _sentinel)
    _default_supplier_default_value = lambda: cast(T, None)

    def __init__(
        self,
        type: Type[T] = _type_default_value,
        # default value supply
        default_value: T = _defaut_value_defalt_value,
        # type default constructor by default
        default_supplier: Callable[[], T] = _default_supplier_default_value,
        value_predicate: Callable[[T], bool] = lambda x: x and True or False,
        # change notification
        on_change: str | bool | Callable[[Any, T], None] = False,
        comparator: Callable[[T, T], bool] = lambda a, b: True,
        #
        type_check: bool = False,
        writeable: bool = True,
        required: bool = False,
        # storage
        private_name: str = "",
        getter: str | Callable[[Any], T] | None = None,
        setter: str | Callable[[Any, T], None] | None = None,
    ):
        self._name = ""
        self._type = type
        if not writeable and setter:
            raise RuntimeError("Propty: not writeable and setter")
        if required and bool(default_supplier):
            raise RuntimeError("Propty: required and default_supplier")

        # default value supplier
        def get_default_supplier():
            if default_supplier != Propty._default_supplier_default_value:
                return default_supplier
            if default_value is not _sentinel:
                return lambda: default_value
            if type:
                return type
            return lambda: None

        self._default_supplier = get_default_supplier()

        self._value_predicate = value_predicate
        # change notificate
        self._on_change = on_change
        self._comparator = comparator
        # self._require_listener_exists = self._on_change
        #
        if type_check and not type:
            raise RuntimeError("Propty: type_check and not type")
        self._type_check = type_check
        self._writeable = writeable
        self._required = required
        # storage
        self._private_name = private_name
        self._getter = getter or self._builtin_getter
        self._setter = setter or self._builtin_setter

    def __set_name__(self, owner: Any, name: str):
        self._name = name
        if self._on_change is True:
            self._on_change = "_on_change_" + name
        if not self._private_name:
            self._private_name = "_" + name

    def __set__(self, obj: Any, value: T):
        if not self._writeable:
            raise AttributeError("property for " + self._name + " is not writeable")
        self._assert_type(value)
        self._maybe_notify_change_listeners(obj, value)
        self._invoke_method(self._setter, obj, value)

    def _assert_type(self, value: Any):
        if not self._type_check:
            return
        assert self._type
        if not isinstance(value, self._type):
            raise AttributeError("property " + self._name + ": unexpected type")

    def _maybe_notify_change_listeners(self, obj: Any, value: T) -> None:
        "invoke listeners, if they are configured and value really changed"
        # check if there are change listeners
        if not self._on_change:
            return
        # check if value has really changed
        self._assert_obj(obj)
        old_value: T = self.__get__(obj)
        if self._comparator(old_value, value):
            return
        # invoke listener
        self._invoke_method(self._on_change, obj, value)

    def _invoke_method(self, method: Any, obj: Any, *args: Any, **kwargs: Any):
        if isinstance(method, str) and method:
            self._assert_obj(obj)
            if not hasattr(obj, method):
                raise RuntimeError("method " + method + " not found")
            func = cast(Callable[[T], None], getattr(obj, method))
            if not callable(func):
                raise RuntimeError("attr " + method + " expected to be callable")
            return func(*args, **kwargs)
        elif callable(method):
            self._assert_obj(obj)
            return method(obj, *args, **kwargs)
        else:
            raise AssertionError("callable or non-empty string expected")

    def _builtin_setter(self, obj: Any, value: T) -> None:
        setattr(obj, self._private_name, value)

    def __get__(self, obj: Any, objtype: Any = None) -> T:
        result = self._invoke_method(self._getter, obj)
        self._assert_type(result)
        if not self._value_predicate(cast(T, result)):
            result = self._default_supplier()
            # todo maybe self._assert_type(result)
            self._invoke_method(self._setter, obj, result)
        return cast(T, result)

    def _assert_obj(self, obj: Any) -> Any:
        if not obj:
            raise AttributeError("Propty is for instances only")
        return obj

    def _builtin_getter(self, obj: Any) -> T:
        self._assert_obj(obj)
        if not hasattr(obj, self._private_name):
            # return self._default_supplier()
            return cast(T, None)
        return getattr(obj, self._private_name)


TypeKey = TypeVar("TypeKey")
TypeValue = TypeVar("TypeValue")


def ensure_key(
    dest: dict[TypeKey, TypeValue],
    key: TypeKey,
    supplier: Callable[[], TypeValue],
) -> TypeValue:
    if key in dest:
        return dest[key]
    else:
        value = supplier()
        dest[key] = value
        return value


ClassInfo: TypeAlias = type | UnionType | tuple["ClassInfo", ...]


def ensure_type(value: Any | None, type_or_tuple: ClassInfo):
    if not isinstance(value, type_or_tuple):
        raise RuntimeError("value expected to be %s" % type_or_tuple)
    return value


def apply_template(template: str, value_dict: dict[str, str] = {}, **value_kwargs: str) -> str:
    values: dict[str, Any] = {"now": datetime.datetime.now(), "today": datetime.datetime.today()}
    values.update(value_dict)
    values.update(value_kwargs)
    return jinja2.Template(template).render(**values)
