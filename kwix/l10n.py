from __future__ import annotations

import locale

from kwix.util import ensure_key


def get_current_locale() -> str:
	return locale.getlocale()[0]


class Text:
	def __init__(self, key: str, default: str | None = None, **l10ns: str):
		self._key: str = key
		self._default: str = default or key
		self._l10ns: dict[str, str] = l10ns

	def setup(self, default: str | None = None, **kwargs: str) -> Text:
		self._default = default or self._key
		self._l10ns.update(kwargs)
		return self
	
	def __str__(self) -> str:
		return self[get_current_locale()]
		
	def __getitem__(self, locale: str) -> str:
		return self._l10ns.get(locale, self._default)
	
	def values(self) -> list[str]:
		return list(self._l10ns.values())
		





_texts: dict[str, Text] = {}


def gettext(key: str, default: str | None = None, **l10ns: str) -> Text:
	return ensure_key(_texts, key, lambda: Text(key, default, **l10ns))


_ = gettext


class Scope:
	def __init__(self, key: str):
		self._key = key

	def gettext(self, key: str) -> Text:
		return gettext(self._key + '.' + key)


_scopes: dict[str, Scope] = {}


def scope(key: str) -> Scope:
	return ensure_key(_scopes, key, lambda: Scope(key))


def test():
	from kwix.l10n import _, gettext, scope
	txt = _('Hello').setup(ru_RU='Привет', de_DE='Hallo')
	print(txt)
