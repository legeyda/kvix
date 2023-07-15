
from __future__ import annotations

from typing import Any

import kwix
from kwix import ActionType
from kwix.impl import BaseItem, BaseItemAlt, BaseAction, BaseActionType, BasePlugin, FuncItemSource
from kwix.l10n import _
from kwix.util import query_match

add_action_text = _('Add Action').setup(ru_RU='Добавить действие', de_DE='Aktion hinzufuegen')
select_action_type_text = _('Select Action Type').setup(ru_RU='Выбор типа действия', de_DE='Aktionstyp auswählen')
select_text = _('Select').setup(ru_RU='Выбрать', de_DE='Auswählen')

class Action(BaseAction):
	def _run(self):
		selector = self.action_type.context.ui.selector()
		selector.title = str(select_action_type_text)
		def execute(action_type: ActionType) -> None:
			selector.destroy()
			dialog = self.action_type.context.ui.dialog(action_type.create_editor)
			def on_dialog_ready(value: Any | None) -> None:
				dialog.destroy()
				if isinstance(value, kwix.Action):
					self.action_type.context.action_registry.actions.append(value)
					self.action_type.context.action_registry.save()
			dialog.go(None, on_dialog_ready)		
		def search(query: str) -> list[kwix.Item]:
			result: list[kwix.Item] = []
			for action_type in self.action_type.context.action_registry.action_types.values():
				def f(action_type: kwix.ActionType = action_type):
					if query_match(query, action_type.id, action_type.title):
						result.append(BaseItem(action_type.title, [BaseItemAlt(select_text, lambda: execute(action_type))]))
				f()
			return result
		selector.item_source = FuncItemSource(search)
		selector.go()

class Plugin(BasePlugin):
	def _create_single_action_type(self) -> ActionType:
		return BaseActionType(self.context, 'add-action', str(add_action_text), action_factory=Action)
	def get_actions(self) -> list[Action]:
		return [Action(self._single_action_type, str(add_action_text) + '...')]