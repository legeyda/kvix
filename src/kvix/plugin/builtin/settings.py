from kvix import ActionType, Context, DialogBuilder
from kvix.impl import BaseAction, BaseActionType, BasePlugin
from kvix.l10n import _
from kvix.conf import Conf, Item
import kvix
from typing import Any, Sequence

action_type_title_text = _("Settings").setup(ru_RU="Настройки", de_DE="Einstellungen")
default_action_title_text = action_type_title_text
default_action_description = " ".join(default_action_title_text.values())


class Action(BaseAction):
    def _run(self, **args: Any) -> None:
        def create_entry(builder: DialogBuilder, key: str, item: Item, title: str):
            entry = builder.create_entry(key, title)
            builder.on_load(lambda _: entry.set_value(str(item.read())))
            builder.on_save(lambda _: item.write(str(entry.get_value())))

        def create_dialog(
            builder: DialogBuilder,
            key_prefix: str = "",
            conf: Conf = self.action_type.context.conf,
            title_prefix: str = "",
        ):
            for key, scope in conf.scopes().items():
                create_dialog(
                    builder,
                    key_prefix + key + ".",
                    scope,
                    title_prefix + (scope.title + " | " if scope.title else ""),
                )
            for key, item in conf.items().items():
                create_entry(
                    builder,
                    key_prefix + key + ".",
                    item,
                    title_prefix + (item._title or item.key),
                )

        dialog = self.action_type.context.ui.dialog(create_dialog)
        dialog.on_ok = self.action_type.context.conf.save
        dialog.activate()


class Plugin(BasePlugin):
    def __init__(self, context: Context):
        super().__init__(context)

    def _create_single_action_type(self) -> ActionType:
        return BaseActionType(
            self.context,
            "kvix.plugin.builtin.settings",
            str(action_type_title_text),
            Action,
        )

    def get_actions(self) -> Sequence[kvix.Action]:
        return [
            Action(
                self._single_action_type,
                str(default_action_title_text),
                default_action_description,
            )
        ]
