from typing import Any

import pynput

from kvix import Action, ActionType, Context, DialogBuilder, ItemAlt
from kvix.impl import (
    BaseAction,
    BaseActionType,
    BaseItem,
    BasePlugin,
    BaseItemAlt,
)
import kvix
from kvix.l10n import _
from kvix.util import query_match

text_text = _("Text").setup(ru_RU="Текст")
type_text = _("Type text").setup(ru_RU="Печатать текст", de_DE="Text eingeben")
copy_text = _("Copy to clipboard").setup(
    ru_RU="Копировать в буфер обмена", de_DE="In die Zwischenablage kopieren"
)
paste_text = _("Copy&Paste").setup(
    ru_RU="Копировать&Вставить",
    de_DE="In die Zwischenablage kopieren&einfügen",
)

_


class MachinistActionType(BaseActionType):
    def __init__(self, context: Context):
        BaseActionType.__init__(self, context, "machinist", "Machinist")

    def create_default_action(
        self,
        title: str,
        description: str | None = None,
        **config: Any,
    ) -> Action:
        return Machinist(self, "", title, description or "", **config)

    def action_from_config(self, value: Any):
        self._assert_config_valid(value)
        return Machinist(self, value["text"], value.get("title"), value.get("description"))

    def create_editor(self, builder: DialogBuilder) -> None:
        builder.create_entry("text", str(text_text))
        super().create_editor(builder)

        def load(value: Any | None):
            if isinstance(value, Machinist):
                builder.widget("text").set_value(value.text)

        builder.on_load(load)

        def save(value: Any | None = {}) -> Any:
            if isinstance(value, Machinist):
                value.text = builder.widget("text").get_value()
            else:
                value = Machinist(
                    self.context.action_registry.action_types["machinist"],
                    builder.widget("text").get_value(),
                    builder.widget("title").get_value(),
                    builder.widget("description").get_value(),
                )
            return value

        builder.on_save(save)


class BaseMachinist(BaseAction):
    def _get_text(self) -> str:
        raise NotImplementedError()

    def _type_text(self):
        self.action_type.context.ui.hide()
        pynput.keyboard.Controller().type(self._get_text())

    def _copy_text(self):
        self.action_type.context.ui.hide()
        self.action_type.context.ui.copy_to_clipboard(self._get_text().encode())

    def _paste_text(self):
        self.action_type.context.ui.hide()
        old_clipboard_content = None
        try:
            old_clipboard_content = self.action_type.context.ui.paste_from_clipboard()
        except Exception as e:
            print(e)
        self.action_type.context.ui.copy_to_clipboard(self._get_text().encode())
        from pynput.keyboard import Key, Controller

        keyboard = Controller()
        keyboard.press(str(Key.ctrl.value))
        keyboard.press("v")
        keyboard.release("v")
        keyboard.release(str(Key.ctrl.value))
        if old_clipboard_content is not None:
            try:
                self.action_type.context.ui.copy_to_clipboard(old_clipboard_content)
            except Exception as e:
                print("error copying to clipboard", e)

    def _create_default_items(self) -> list[kvix.Item]:
        type_alt: ItemAlt = BaseItemAlt(type_text, self._type_text)
        copy_alt: ItemAlt = BaseItemAlt(copy_text, self._copy_text)
        paste_alt: ItemAlt = BaseItemAlt(paste_text, self._paste_text)
        return [BaseItem(self.title, [type_alt, copy_alt, paste_alt])]


class Machinist(BaseMachinist):
    def __init__(
        self,
        action_type: ActionType,
        text: str,
        title: str | None = None,
        description: str | None = None,
    ):
        title = title or 'type text "' + text + '"'
        BaseAction.__init__(self, action_type, title, description or title)
        self.text = text

    def _get_text(self) -> str:
        return self.text

    def _match(self, query: str) -> bool:
        if query_match(query, self.text):
            return True
        return BaseAction._match(self, query)

    def to_config(self):
        result = BaseAction.to_config(self)
        result["text"] = self.text
        return result


class Plugin(BasePlugin):
    def _create_single_action_type(self) -> ActionType:
        return MachinistActionType(self.context)
