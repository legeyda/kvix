from __future__ import annotations
from types import ModuleType
from kvix.impl import BasePlugin, FromModule
from kvix import Action, ActionType, Context
from typing import Sequence


class Compound(BasePlugin):
    def __init__(self, context: Context, *wrap: kvix.Plugin):
        BasePlugin.__init__(self, context)
        self.wrap = wrap

    def get_action_types(self) -> Sequence[ActionType]:
        return [action_type for plugin in self.wrap for action_type in plugin.get_action_types()]

    def get_actions(self) -> Sequence[Action]:
        return [action for plugin in self.wrap for action in plugin.get_actions()]


class FromModules(Compound):
    def __init__(self, context: Context, *modules: ModuleType):
        Compound.__init__(self, context, *[FromModule(context, module) for module in modules])
