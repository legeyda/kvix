from typing import Sequence
import kvix
from kvix import ActionType
from kvix.impl import BaseActionType, BasePlugin
from kvix.plugin.builtin.machinist import BaseMachinist
from kvix.l10n import _

import uuid

action_title_text = _("Generate Random UUID").setup(ru_RU="Генерировать случайный UUID")


class Action(BaseMachinist):
    def _get_text(self, query: str) -> str:
        return str(uuid.uuid4())


class Plugin(BasePlugin):
    def _create_single_action_type(self) -> ActionType:
        return BaseActionType(
            self.context,
            "kvix.random-uuid",
            str(action_title_text),
            action_factory=Action,
        )

    def get_actions(self) -> Sequence[kvix.Action]:
        return [
            Action(
                self._single_action_type,
                str(action_title_text),
                "\n".join(action_title_text.values()),
            )
        ]
