from kvix import ActionType, Context, Item
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
import urllib.parse as urlparse
from typing import Sequence

action_type_title_text = _("Google Search").setup(ru_RU="Поиск в google")
search_google_text = _('Google for "{query}"').setup(ru_RU='Загуглить "{query}"')
search_duck_text = _('DuckDuckGo for "{query}"').setup(ru_RU='Найти в DuckDuckGo "{query}"')

command_title_text = _("Command").setup(ru_RU="Команда")
default_action_title_text = action_type_title_text
default_action_title_description = " ".join(default_action_title_text.values())


class Action(BaseAction):
    def _search_google(self, query: str) -> None:
        self.action_type.context.ui.hide()
        webbrowser.open("https://www.google.com/search?btnI=1&q=" + urlparse.quote(query))

    def _search_duck(self, query: str) -> None:
        self.action_type.context.ui.hide()
        webbrowser.open("https://duckduckgo.com/?q=" + urlparse.quote("\\ " + query))

    def search(self, query: str) -> Sequence[Item]:
        if not query:
            return []
        if 4 > len(query):
            return []
        return [
            BaseItem(
                str(search_google_text).format(query=query),
                [BaseItemAlt(str(execute_text), lambda: self._search_google(query))],
            ),
            BaseItem(
                str(search_duck_text).format(query=query),
                [BaseItemAlt(str(execute_text), lambda: self._search_duck(query))],
            ),
        ]


class Plugin(BasePlugin):
    def __init__(self, context: Context):
        super().__init__(context)

    def _create_single_action_type(self) -> ActionType:
        return BaseActionType(
            self.context,
            "kvix.plugin.builtin.websearch",
            str(action_type_title_text),
            Action,
        )

    def get_actions(self) -> Sequence[kvix.Action]:
        return [Action(self._single_action_type, str(action_type_title_text))]
