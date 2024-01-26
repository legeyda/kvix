from __future__ import annotations
from typing import Sequence


import kvix
from kvix import ActionType
from kvix.impl import (
    BaseItem,
    BaseItemAlt,
    BaseAction,
    BaseActionType,
    BasePlugin,
    BaseItemSource,
)
from kvix.l10n import _
from kvix.util import query_match

add_action_text = _("Add Action").setup(ru_RU="Добавить действие", de_DE="Aktion hinzufuegen")
select_action_type_text = _("Select Action Type").setup(
    ru_RU="Выбор типа действия", de_DE="Aktionstyp auswählen"
)
select_text = _("Select").setup(ru_RU="Выбрать", de_DE="Auswählen")


class Action(BaseAction):
    def _run(self, query: str) -> None:
        action_type_selector = self.action_type.context.ui.selector()
        action_type_selector.title = str(select_action_type_text)

        def execute(action_type: ActionType) -> None:
            dialog = self.action_type.context.ui.dialog(action_type.create_editor)
            dialog.auto_destroy = True

            def on_ok() -> None:
                action_type_selector.destroy()
                if isinstance(dialog.value, kvix.Action):
                    self.action_type.context.action_registry.actions.append(dialog.value)
                    self.action_type.context.action_registry.save()
                # todo refresh main selector

            dialog.on_ok = on_ok
            dialog.activate()

        def search(query: str) -> Sequence[kvix.Item]:
            result: list[kvix.Item] = []
            for action_type in self.action_type.context.action_registry.action_types.values():

                def f(action_type: kvix.ActionType = action_type):
                    if not query or query_match(query, action_type.id, action_type.title):
                        result.append(
                            BaseItem(
                                action_type.title,
                                [
                                    BaseItemAlt(
                                        select_text,
                                        lambda: execute(action_type),
                                    )
                                ],
                            )
                        )

                f()
            return result

        action_type_selector.item_source = BaseItemSource(search)
        action_type_selector.activate()


class Plugin(BasePlugin):
    def _create_single_action_type(self) -> ActionType:
        return BaseActionType(
            self.context,
            "add-action",
            str(add_action_text),
            action_factory=Action,
        )

    def get_actions(self) -> Sequence[Action]:
        return [Action(self._single_action_type, str(add_action_text) + "...")]
