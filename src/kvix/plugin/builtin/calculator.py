import kvix
from kvix import ActionType, Item
from kvix.impl import BaseActionType, BasePlugin, BaseItem
from kvix.plugin.builtin.machinist import BaseMachinist
from kvix.l10n import _
import re
import math
from kvix.util import apply_template
from typing import Sequence

action_type_title_text = _("Calculator").setup(ru_RU="Калькулятор", de_DE="Rechner")
action_description_text = _("Simple ariphmetic expression calculator").setup(
    ru_RU="Простой калькулятор", de_DE="Einfacher Rechner"
)
expression_error_text = _("Calculation error").setup(ru_RU="Ошибка вычисления", de_DE="Fehler")
item_title_text = _("= {{value}}")


class Action(BaseMachinist):
    def search(self, query: str) -> Sequence[Item]:
        if not query:
            return []
        if len(query) < 3:
            return []
        match = self._pattern and re.compile(self._pattern).match(query)
        result = self._evaluate(query)
        if not result:
            if match:
                result = str(expression_error_text)
            else:
                return []
        return [
            BaseItem(
                apply_template(str(item_title_text), {"value": result}),
                [
                    self._create_single_item_type_alt(lambda: result),
                    self._create_single_item_copy_alt(lambda: result),
                    self._create_single_item_paste_alt(lambda: result),
                ],
            )
        ]

    def _evaluate(self, query: str) -> str:
        math_functions = {key: getattr(math, key) for key in dir(math) if not key.startswith("_")}
        try:
            # todo work with commas instead of dots as fractional part separator
            # todo remove spaces between digits
            # todo remove commas as three digits separator
            return str(eval(query, math_functions, {}))
        except Exception:
            return ""


class Plugin(BasePlugin):
    def _create_single_action_type(self) -> ActionType:
        return BaseActionType(
            self.context,
            "kvix.plugin.builtin.calculator",
            str(action_type_title_text),  # " ".join(action_type_title.values()),
            action_factory=Action,
        )

    def get_actions(self) -> Sequence[kvix.Action]:
        return [
            Action(
                self._single_action_type,
                str(action_type_title_text),
                str(action_description_text),
                "(?i)^[0-9()\\+\\-\\*/ ]{3,}$",
            )
        ]
