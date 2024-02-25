from typing import Any

import pynput
from typing import cast, Callable, Sequence

from kvix import Action, ActionType, Context, DialogBuilder, ItemAlt
from kvix.impl import (
    BaseAction,
    BaseActionType,
    BasePlugin,
    BaseItemAlt,
)
from kvix.util import apply_template

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


class MachinistActionType(BaseActionType):
    def __init__(self, context: Context):
        BaseActionType.__init__(self, context, "machinist", "Machinist")

    def create_default_action(
        self,
        title: str,
        description: str = "",
        pattern: str = "",
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
    def _create_single_item_alts(self, query: str) -> Sequence[ItemAlt]:
        return [
            self._create_single_item_type_alt(lambda: self._get_text(query)),
            self._create_single_item_copy_alt(lambda: self._get_text(query)),
            self._create_single_item_paste_alt(lambda: self._get_text(query)),
        ]

    def _create_single_item_type_alt(self, action: Callable[[], str]) -> ItemAlt:
        return BaseItemAlt(type_text, lambda: self._type_text(action()))

    def _create_single_item_copy_alt(self, action: Callable[[], str]) -> ItemAlt:
        return BaseItemAlt(copy_text, lambda: self._copy_text(action()))

    def _create_single_item_paste_alt(self, action: Callable[[], str]) -> ItemAlt:
        return BaseItemAlt(paste_text, lambda: self._paste_text(action()))

    def _get_text(self, query: str) -> str:
        raise NotImplementedError()

    def _type_text(self, text: str):
        self.action_type.context.ui.hide()
        pynput.keyboard.Controller().type(text)

    def _copy_text(self, text: str):
        self.action_type.context.ui.hide()
        self.action_type.context.ui.copy_to_clipboard(text.encode())

    def _paste_text(self, text: str):
        self.action_type.context.ui.hide()
        old_clipboard_content = None
        try:
            old_clipboard_content = self.action_type.context.ui.paste_from_clipboard()
        except Exception as e:
            print(e)
        self.action_type.context.ui.copy_to_clipboard(text.encode())
        from pynput.keyboard import Key, Controller

        keyboard = Controller()
        keyboard.press(cast(str, Key.ctrl.value))
        keyboard.press("v")
        keyboard.release("v")
        keyboard.release(cast(str, Key.ctrl.value))
        if old_clipboard_content is not None:
            try:
                self.action_type.context.ui.copy_to_clipboard(old_clipboard_content)
            except Exception as e:
                print("error copying to clipboard", e)


class Machinist(BaseMachinist):
    def __init__(
        self,
        action_type: ActionType,
        text: str,
        title: str | None = None,
        description: str = "",
    ):
        title = title or 'type text "' + text + '"'
        BaseAction.__init__(self, action_type, title, description or title)
        self.text = text

    def _get_text(self, query: str) -> str:
        return apply_template(self.text, {"query": query})

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
