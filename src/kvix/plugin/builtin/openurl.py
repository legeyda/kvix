from kvix import Context, ItemAlt
from kvix.impl import (
    BaseActionType,
    BasePlugin,
    BaseItemAlt
)
from kvix.l10n import _
import kvix
import webbrowser
from kvix.util import apply_template
from typing import Any, Sequence
from kvix.plugin.builtin.machinist import BaseMachinist

action_type_title_text = _("Open url").setup(ru_RU="Открыть ссылку")
item_title_text = _('Goto "{{url}}"').setup(ru_RU='Открыть "{{url}}"')
url_param_text = _("URL")

default_action_title_text = action_type_title_text
default_action_title_description = " ".join(default_action_title_text.values())


class Action(BaseMachinist):
    def _on_after_set_params(self, **params: Any) -> None:
        self._url = str(params["url"])

    def _create_single_item_alts(self, query: str) -> Sequence[ItemAlt]:
        return [
            BaseItemAlt(str(action_type_title_text), lambda: self._run(query)),
            self._create_single_item_type_alt(lambda: self._get_text(query)),
            self._create_single_item_copy_alt(lambda: self._get_text(query)),
            self._create_single_item_paste_alt(lambda: self._get_text(query)),
        ]

    def _get_text(self, query: str) -> str:
        return apply_template(self._url, {"query": query})

    def _run(self, query: str) -> None:
        self.action_type.context.ui.hide()
        webbrowser.open(self._get_text(query))


class Plugin(BasePlugin):
    def __init__(self, context: Context):
        super().__init__(context)

    def _create_single_action_type(self) -> kvix.ActionType:
        return BaseActionType(
            self.context,
            "kvix.plugin.builtin.openurl",
            str(action_type_title_text),
            Action,
            {"url": str(url_param_text)},
        )
