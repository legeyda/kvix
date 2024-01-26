from kvix import Action, ActionType
from kvix.impl import BaseAction, BaseActionType, BasePlugin
from kvix.l10n import _
from typing import Any, Sequence

quit_title_text = _("Quit kvix").setup(ru_RU="Выключить kvix", de_DE="kvix ausschalten")
quit_description = " | ".join([quit_title_text.default] + list(quit_title_text.l10ns.values()))


class QuitAction(BaseAction):
    def _run(self, **args: Any):
        self.action_type.context.quit()


class Plugin(BasePlugin):
    def _create_single_action_type(self) -> ActionType:
        return BaseActionType(
            self.context,
            "kvix.plugin.builtin.quit",
            str(quit_title_text),
            action_factory=QuitAction,
        )

    def get_actions(self) -> Sequence[Action]:
        return [
            QuitAction(
                self._single_action_type,
                str(quit_title_text),
                str(quit_description),
            )
        ]
