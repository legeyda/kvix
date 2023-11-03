
from __future__ import annotations
from types import ModuleType
from kwix.impl import BasePlugin, FromModule
from kwix import Action, ActionType, Context


class Compound(BasePlugin):
    def __init__(self, context: Context, *wrap: kwix.Plugin):
        BasePlugin.__init__(self, context)
        self.wrap = wrap
    def get_action_types(self) -> list[ActionType]:
        return [action_type for plugin in self.wrap for action_type in plugin.get_action_types()]
    def get_actions(self) -> list[Action]:
        return [action for plugin in self.wrap for action in plugin.get_actions()]


class FromModules(Compound):
    def __init__(self, context: Context, *modules: ModuleType):
        Compound.__init__(self, context, *[FromModule(context, module) for module in modules])
        
