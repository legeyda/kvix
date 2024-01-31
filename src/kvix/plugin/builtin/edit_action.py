from __future__ import annotations
from typing import Any


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

edit_action_text = _("Edit Action").setup(
    ru_RU="Редактировать действие", de_DE="Aktion bearbeiten"
)
select_action_type_text = _("Select Action Type").setup(
    ru_RU="Выбор типа действия", de_DE="Aktionstyp auswählen"
)
select_text = _("Select").setup(ru_RU="Выбрать", de_DE="Auswählen")


class Action(BaseAction):
    def _run(self, query: str) -> None:
        action_type_selector = self.action_type.context.ui.selector()
        action_type_selector.title = str(select_action_type_text)

        def execute(action: Action) -> None:
            dialog = self.action_type.context.ui.dialog(action.action_type.create_editor)
            dialog.value = action
            dialog.auto_destroy = True

            def on_ok() -> None:
                if isinstance(dialog.value, kvix.Action):
                    self.action_type.context.action_registry.save()
                # todo refresh main selector

            dialog.on_ok = on_ok
            dialog.activate()

        def search(query: str) -> list[kvix.Item]:
            result: list[kvix.Item] = []
            for action in self.action_type.context.action_registry.actions:

                def f(action: kvix.ActionType = action):
                    if not query or query_match(query, action.title, action.action_type.title):
                        result.append(
                            BaseItem(
                                action.title,
                                [
                                    BaseItemAlt(
                                        select_text,
                                        lambda: execute(action),
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
            "kvix.plugin.builtin.edit_action",
            str(edit_action_text),
            action_factory=Action,
        )

    def get_actions(self) -> list[Action]:
        return [
            Action(
                self._single_action_type,
                str(edit_action_text) + "...",
                "/".join(edit_action_text.values()),
            )
        ]
