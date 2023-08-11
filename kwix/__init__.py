from __future__ import annotations

from typing import Any, Callable

from kwix.conf import Conf
from kwix.l10n import _
from kwix.util import Propty


class ItemAlt:
	def execute(self) -> None:
		raise NotImplementedError()

class Item:
	priority = Propty(int)
	alts = Propty(list[ItemAlt], writeable=False)

class ItemSource:
	def search(self, query: str) -> list[Item]:
		raise NotImplementedError()



class Context:
	conf = Propty(writeable=False)
	ui: Propty[Ui] = Propty(writeable=False)
	action_registry: Propty[ActionRegistry] = Propty(writeable=False)
	on_start = Propty(Callable[[], None], default_value=lambda: None)
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
	action_type = Propty(ActionType)
	title = Propty(str)
	description = Propty(str)

	def search(self, query: str) -> list[Item]:
		raise NotImplementedError()
	
	def to_config(self) -> dict[str, Any]:
		raise NotImplementedError()

class ActionRegistry(ItemSource):
	action_types = Propty(dict[str, ActionType], writeable=False)
	actions = Propty(list[Action], writeable=False)
	
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
	on_start = Propty(Callable[[], None], default_value=lambda: None)
	def run(self) -> None:
		raise NotImplementedError()
	def selector(self) -> Selector:
		raise NotImplementedError()
	def dialog(self, create_dialog: Callable[[DialogBuilder], None]) -> Dialog:
		raise NotImplementedError()
	def destroy(self) -> None:
		raise NotImplementedError()

class Selector:
	title = Propty(str)
	item_source = Propty(ItemSource)
	def go(self) -> None:
		raise NotImplementedError()
	def destroy(self) -> None:
		raise NotImplementedError()
	
class Dialog:
	title = Propty(str, default_value='kwix')
	value = Propty()
	on_ok = Propty(Callable[[], None], default_value=lambda: None)
	on_cancel = Propty(Callable[[], None], default_value = lambda: None)
	auto_destroy = Propty(bool, default_value=True)
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
