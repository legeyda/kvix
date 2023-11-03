import base64

from kwix import Action, ActionType
from kwix.impl import BaseActionType, BasePlugin
from kwix.plugin.builtin.machinist import BaseMachinist


class Action(BaseMachinist):
    def _get_text(self) -> str:
        return base64.b64decode(
            self.action_type.context.ui.paste_from_clipboard()
        ).decode("UTF-8")


class Plugin(BasePlugin):
    def _create_single_action_type(self) -> ActionType:
        return BaseActionType(
            self.context, "base64-decode", "Base64 decode", action_factory=Action
        )

    def get_actions(self) -> list[Action]:
        return [Action(self._single_action_type, "Base64 decode", "decode base64")]
