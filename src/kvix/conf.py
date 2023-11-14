from __future__ import annotations

from typing import Any, Callable, Sequence, cast, TypeVar, Generic, Type

from kvix.stor import Stor


T = TypeVar("T")


class Conf:
    def __init__(self):
        self._scopes: dict[str, Scope] = {}
        self._items: dict[str, Item[Any]] = {}

    def _get_data(self) -> dict[Any, Any]:
        ...

    def load(self):
        ...

    def save(self):
        ...

    def scope(self, key: str, title: str | None = None) -> Conf:
        if key in self._items:
            raise RuntimeError('cannot create scope "' + key + '": there is item with such key')
        result = self._scopes.get(key)
        if not result:
            result = Scope(self, key, title)
            self._scopes[key] = result
        return result

    def scopes(self) -> dict[str, Scope]:
        return {**self._scopes}

    def item(self, key: str, type: Type[T] = Type[Any]) -> Item[T]:
        if key in self._scopes:
            raise RuntimeError('cannot create item "' + key + '": there is scope with such key')
        result = self._items.get(key)
        if not result:
            result = Item(self, key, type)
            self._items[key] = result
        return result

    def items(self) -> dict[str, Item[Any]]:
        return {**self._items}


class Scope(Conf):
    def __init__(self, parent: Conf, key: str, title: str | None = None):
        super().__init__()
        self.parent = parent
        self.key = key
        self.title = title

    def setup(self, title: str | None = None):
        self.title = title or self.key
        return self

    def _get_data(self) -> dict[Any, Any]:
        result: Any = self.parent._get_data().setdefault(self.key, {})
        if not isinstance(result, dict):
            raise RuntimeError(
                "dict expected at scope "
                + self.key
                + (" (" + self.title + ")" if self.title else "")
            )
        return cast(dict[Any, Any], result)

    def load(self):
        self.parent.load()

    def save(self):
        self.parent.save()


class StorConf(Conf):
    def __init__(self, stor: Stor):
        Conf.__init__(self)
        self._stor: Stor = stor

    def _get_data(self) -> dict[Any, Any]:
        result = self._stor.data
        if not isinstance(result, dict):
            raise RuntimeError("stor.data expected to be dict)")
        return cast(dict[Any, Any], result)

    def load(self):
        self._stor.load()

    def save(self):
        self._stor.save()


class Item(Generic[T]):
    def __init__(self, parent: Conf, key: str, type: Type[T] = Type[Any]):
        self.parent = parent
        self.key = key
        self.type = type
        self.setup()

    def setup(
        self,
        title: str | None = None,
        default: Any = None,
        read_mapping: Callable[[Any], Any] | None = None,
        enum: Sequence[Any] | None = None,
        on_change: Callable[[Any], None] = lambda value: None,
    ):
        self._title = title
        self._default = default
        self._read_mapping = read_mapping
        self._enum = enum
        self._on_change = on_change
        return self

    def read(self):
        result = self.parent._get_data().get(self.key)
        if self._default and not result:
            result = self._default
        if self._read_mapping:
            result = self._read_mapping(result)
        # todo handle enum somehow?
        return result

    def write(self, value: Any):
        data = self.parent._get_data()
        old_value = data.get(self.key, self._default)
        if old_value != value:
            data[self.key] = value
            if value == self._default:
                del data[self.key]
            self._on_change(value)
