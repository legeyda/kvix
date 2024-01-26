import base64

from typing import Sequence
import kvix
from kvix import ActionType
from kvix.impl import BaseActionType, BasePlugin
from kvix.plugin.builtin.machinist import BaseMachinist


class Action(BaseMachinist):
    def _get_text(self, query: str) -> str:
        return base64.b64encode(self.action_type.context.ui.paste_from_clipboard()).decode("UTF-8")


class Plugin(BasePlugin):
    def _create_single_action_type(self) -> ActionType:
        return BaseActionType(
            self.context, "base64-encode", "Base64 encode", action_factory=Action
        )

    def get_actions(self) -> Sequence[kvix.Action]:
        return [Action(self._single_action_type, "Base64 encode", "encode base64")]
