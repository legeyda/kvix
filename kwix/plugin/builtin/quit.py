
from kwix import Action, ActionType
from kwix.impl import BaseAction, BaseActionType, BasePlugin
from kwix.l10n import _

quit_title_text = _('Quit Kwix').setup(ru_RU='Выключить Kwix', de_DE='Kwix ausschalten')
quit_description_text = quit_title_text


class QuitAction(BaseAction):
	def _run(self):
		self.action_type.context.quit()

class Plugin(BasePlugin):
	def _create_single_action_type(self) -> ActionType:
		return BaseActionType(self.context, 'kwix.plugin.builtin.quit', str(quit_title_text), action_factory=QuitAction)
	def _create_single_action(self) -> Action:
		return QuitAction(self._single_action_type, str(quit_title_text), str(quit_description_text))