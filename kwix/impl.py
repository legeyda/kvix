
from __future__ import annotations

from typing import Any, Callable, Sequence, cast
from types import ModuleType
from inspect import isclass

import kwix
from kwix import Action, ActionType, Item, Context
from kwix.l10n import _
from kwix.util import Propty, query_match
from kwix.stor import Stor

unnamed_text = _('Unnamed').setup(ru_RU='Без названия', de_DU='Ohne Titel')
execute_text = _('Execute').setup(ru_RU='Выполнить', de_DU='Ausführen')
title_text = _('Title').setup(ru_RU = 'Название', de_DE='Bezeichnung')
description_text = _('Description').setup(ru_RU = 'Описание', de_DE = 'Beschreibung')
ok_text = _('OK')
cancel_text = _('Cancel').setup(ru_RU='Отмена', de_DE='Abbrechen')



class WithTitleStr:
	def __init__(self, title: Any):
		self._title = title
	def __str__(self) -> str:
		return str(self._title)


class BaseItemAlt(kwix.ItemAlt, WithTitleStr):
	def __init__(self, title: Any, command: Callable[[], None]):
		WithTitleStr.__init__(self, title)
		self._command = command
	def execute(self):
		return self._command()

class BaseItem(kwix.Item, WithTitleStr):
	def __init__(self, title: Any, alts: list[kwix.ItemAlt]):
		WithTitleStr.__init__(self, title)
		self._alts = alts

class FuncItemSource(kwix.ItemSource):
	def __init__(self, func: Callable[[str], list[kwix.Item]]):
		self._func = func
	def search(self, query: str) -> list[Item]:
		return self._func(query)

class EmptyItemSource(kwix.ItemSource):
	def search(self, query: str) -> list[kwix.Item]:
		return []





class BaseSelector(kwix.Selector):
	title = Propty(lambda: unnamed_text)
	item_source: Propty[kwix.ItemSource] = cast(Propty[kwix.ItemSource], Propty(EmptyItemSource()))
	def __init__(self, item_source: kwix.ItemSource = EmptyItemSource(), title: str | None = None):
		self.item_source = item_source
		if title is not None:
			self.title = title


	
class BaseActionType(ActionType):
	def __init__(self, context: kwix.Context, id: str, title: str, action_factory: Callable[[ActionType, str, str], Action] | None = None):
		self.context = context
		self.id = id
		self.title = title
		self.action_factory = action_factory

	def create_default_action(self, title: str, description: str | None = None) -> Action:
		return self.action_factory(self, title, description)

	def action_from_config(self, value: Any) -> Action:
		dic = self._assert_config_valid(value)
		return self.create_default_action(dic['title'], dic.get('description'))

	def _assert_config_valid(self, value: Any) -> dict[Any, Any]:
		if type(value) != dict:
			raise RuntimeError('json must be object, ' + value + ' given')
		value = cast(dict[Any, Any], value)
		if 'type' not in value:
			raise RuntimeError('"type" must be in json object')
		if value.get('type') != self.id:
			raise RuntimeError('wrong type got ' +
							   str(value.get('type')) + ', expected ' + self.id)
		return value
	
	def create_editor(self, builder: kwix.DialogBuilder) -> None:
		builder.create_entry('title', str(title_text))
		builder.create_entry('description', str(description_text))
		def load(value: Any | None):
			if isinstance(value, Action):
				builder.widget('title').set_value(value.title)
				builder.widget('description').set_value(value.description)	
		builder.on_load(load)

		def save(value: Any | None) -> Any:
			value = value or {}
			if isinstance(value, Action):
				value.title = builder.widget('title').get_value()
				value.description = builder.widget('description').get_value()
			if isinstance(value, dict):
				value['title'] = builder.widget('title').get_value()
				value['description'] = builder.widget('description').get_value()
			return value
		builder.on_save(save)

class BaseAction(Action):
	def __init__(self, action_type: ActionType, title: str, description: str | None = None):
		self._action_type = action_type
		self._title = title
		self._description = description or title

	def _match(self, query: str) -> bool:
		return query_match(query or '', self.title, self.description)

	def _create_default_items(self) -> list[Item]:
		return [BaseItem(self.title, [BaseItemAlt(execute_text, self._run)])]

	def search(self, query: str) -> list[kwix.Item]:
		if not self._match(query):
			return []
		return self._create_default_items()

	def _run(self) -> None:
		raise NotImplementedError()
	
	def to_config(self) -> dict[str, Any]:
		return {
			'type': self.action_type.id,
			'title': self.title,
			'description': self.description
		}

class BaseActionRegistry(kwix.ActionRegistry):

	def __init__(self, stor: Stor):
		self.stor: Stor = stor

	def load(self):
		self.stor.load()
		self._actions = [self.action_from_config(x) for x in (self.stor.data or [])]

	def save(self) -> None:
		self.stor.data = [action.to_config() for action in self.actions]
		self.stor.save()

	def add_action_type(self, action_type: ActionType) -> None:
		if action_type.id in self.action_types:
			raise RuntimeError('duplicate action type id=' + action_type.id)
		self.action_types[action_type.id] = action_type

	def action_from_config(self, value: Any) -> Action:
		if type(value) != dict:
			raise RuntimeError('dict expected, got ' + type(value))
		value = cast(dict[Any, Any], value)
		if 'type' not in value:
			raise RuntimeError('"type" expected')
		type_id = value['type']
		if type(type_id) != str:
			raise RuntimeError('"type" expected to be str, got ' + type(type_id))
		if type_id not in self.action_types:
			raise RuntimeError('uknown action type id=' + type_id)
		action_type: ActionType = self.action_types[type_id]
		return action_type.action_from_config(value)

	def search(self, query: str) -> list[kwix.Item]:
		result: list[kwix.Item] = []
		for action in self.actions:
			for item in action.search(query):
				result.append(item)
		return result







class BasePlugin(kwix.Plugin):
	def __init__(self, context: kwix.Context):
		self.context = context
	def get_action_types(self) -> list[ActionType]:
		self._single_action_type = self._create_single_action_type()
		return [self._single_action_type]
	def _create_single_action_type(self) -> ActionType:
		raise NotImplementedError()
	def get_actions(self) -> list[Action]:
		return []

class FromModule(BasePlugin):
	def __init__(self, context: Context, module: ModuleType):
		BasePlugin.__init__(self, context)
		self._wrap = self._create_plugin(module)
	def _create_plugin(self, module: ModuleType) -> kwix.Plugin | None:
		if not hasattr(module, 'Plugin'):
			return None
		PluginClass = getattr(module, 'Plugin')
		if not isclass(PluginClass):
			return None
		if not issubclass(PluginClass, kwix.Plugin):
			return None
		return PluginClass(self.context)
	def get_action_types(self) -> list[ActionType]:
		return self._wrap.get_action_types() if self._wrap else []
	def get_actions(self) -> list[Action]:
		return self._wrap.get_actions() if self._wrap else []