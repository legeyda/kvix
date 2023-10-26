


import base64
import build
import pyclip

from kwix import ActionType
from kwix.impl import BaseActionType, BasePlugin
from kwix.plugin.builtin.machinist import BaseMachinist

class Action(BaseMachinist):
	def _get_text(self) -> str:
		return base64.b64encode(pyclip.paste()).decode('UTF-8')

class Plugin(BasePlugin):
	def _create_single_action_type(self) -> ActionType:
		return BaseActionType(self.context, 'base64-encode', 'Base64 encode', action_factory=Action)
	def get_actions(self) -> list[Action]:
		return [Action(self._single_action_type, 'Base64 encode', 'encode base64')]