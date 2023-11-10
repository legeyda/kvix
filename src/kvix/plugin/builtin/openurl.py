from kvix import Context, Item, ItemAlt
from kvix.impl import (
    BaseAction,
    BaseActionType,
    BasePlugin,
    BaseItem,
    BaseItemAlt,
    execute_text,
)
from kvix.l10n import _
import kvix
import webbrowser
from kvix.util import apply_template
from typing import Any

action_type_title_text = _("Open url").setup(ru_RU="Открыть ссылку")
item_title_text = _('Goto "{{url}}"').setup(ru_RU='Открыть "{{url}}"')
url_param_text = _("URL")

default_action_title_text = action_type_title_text
default_action_title_description = " ".join(default_action_title_text.values())


class Action(BaseAction):
    def _on_after_set_params(self, **params: Any) -> None:
        self._url = str(params["url"])

    def _run(self, query: str) -> None:
        self.action_type.context.ui.hide()
        webbrowser.open(apply_template(self._url, {"query": query}))


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
