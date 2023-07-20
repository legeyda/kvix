from __future__ import annotations

from typing import Any, Callable, cast

from kwix.conf import Conf
from kwix.l10n import _
from kwix.util import Propty


class ItemAlt:
	def execute(self) -> None:
		raise NotImplementedError()

class Item:
	priority = Propty(default_supplier=lambda: 0)
	alts = Propty(list, type=list[ItemAlt], writeable=False)

class ItemSource:
	def search(self, query: str) -> list[Item]:
		raise NotImplementedError()



class Context:
	conf: Propty[Conf] = Propty(writeable=False)
	ui: Propty[Ui] = Propty(writeable=False)
	action_registry: Propty[ActionRegistry] = Propty(writeable=False)
	on_start = Propty(lambda: (lambda: None), type = Callable[[], None])
	def quit(self) -> None:
		raise NotImplementedError()




class ActionType:
	context = Propty(type = Context)
	id = Propty(type = str)
	title = Propty(type = str)

	def action_from_config(self, value: Any) -> Action:
		raise NotImplementedError()

	def create_editor(self, builder: DialogBuilder) -> None:
		raise NotImplementedError()

class Action:
	action_type = Propty(type = ActionType)
	title = Propty(type = str)
	description = Propty(type = str)

	def search(self, query: str) -> list[Item]:
		raise NotImplementedError()
	
	def to_config(self) -> dict[str, Any]:
		raise NotImplementedError()

class ActionRegistry(ItemSource):
	action_types: Propty[dict[str, ActionType]] = Propty(dict, writeable=False)
	actions: Propty[list[Action]] = Propty(list, writeable=False)
	
	def load(self) -> None:
		raise NotImplementedError()

	def save(self) -> None:
		raise NotImplementedError()

	def add_action_type(self, action_type: ActionType) -> None:
		raise NotImplementedError()

	def action_from_config(self, value: Any) -> Action:
		raise NotImplementedError()

	def search(self, query: str) -> list[Item]:
		raise NotImplementedError()





class Ui:
	on_start = Propty(lambda: lambda: None, type = Callable[[], None])
	def run(self) -> None:
		raise NotImplementedError()
	def selector(self) -> Selector:
		raise NotImplementedError()
	def dialog(self, create_dialog: Callable[[DialogBuilder], None]) -> Dialog:
		raise NotImplementedError()
	def destroy(self) -> None:
		raise NotImplementedError()

class Selector:
	title = Propty(type=str)
	item_source = Propty(type=ItemSource)
	def go(self) -> None:
		raise NotImplementedError()
	def destroy(self) -> None:
		raise NotImplementedError()
	
class Dialog:
	title = Propty(lambda: 'kwix', type = str)
	value = Propty(type = Any)
	on_ok = Propty(lambda: (lambda: None), type = Callable[[], None])
	on_cancel = Propty(lambda: (lambda: None), type = Callable[[], None])
	auto_destroy = Propty(lambda: True)
	def go(self) -> None:
		raise NotImplementedError()
	def destroy(self) -> None:
		raise NotImplementedError()

class DialogWidget:
	def get_value(self) -> str:
		raise NotImplementedError()

	def set_value(self, value: str) -> None:
		raise NotImplementedError()

class DialogEntry(DialogWidget):
	pass

class DialogBuilder:
	def __init__(self):
		self._on_load: list[Callable[[Any | None], None]] = []
		self._on_save: list[Callable[[Any | None], Any]] = []
		self._widgets: dict[str, DialogWidget] = {}

	def create_entry(self, id: str, title: str) -> DialogEntry:
		raise NotImplementedError()
	
	def widget(self, id: str) -> DialogWidget:
		return self._widgets[id]
	
	def _add_widget(self, id: str, widget: DialogWidget) -> DialogWidget:
		self._widgets[id] = widget
		return widget

	def on_load(self, func: Callable[[Any | None], None]):
		self._on_load.append(func)

	def load(self, value: Any | None):
		for func in self._on_load: func(value)

	def on_save(self, func: Callable[[Any | None], Any]):
		self._on_save.append(func)

	def save(self, value: Any) -> Any | None:
		for func in self._on_save: value = func(value)
		return value






class Plugin:
	def __init__(self, context: Context): ...
	def get_action_types(self) -> list[ActionType]: ...
	def get_actions(self) -> list[Action]: ...
