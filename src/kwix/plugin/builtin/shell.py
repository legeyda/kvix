from kwix import ActionType, Context
from kwix.impl import BaseAction, BaseActionType, BasePlugin
from pathlib import Path
from kwix.l10n import _
import subprocess, chevron, shlex

import os

action_type_title_text = _('Run Command').setup(ru_RU='Запуск команды')
command_title_text = _('Command').setup(ru_RU='Команда')
default_action_title_text = action_type_title_text
default_action_title_description = ' '.join(default_action_title_text.values())


class Action(BaseAction):
	def _run(self) -> None:
		self.action_type.context.ui.hide()
		env = os.environ.copy()
		env['KWIX_CLIPBOARD'] = ''
		clipboard_bytes = b''
		try:
			clipboard_bytes = self.action_type.context.ui.paste_from_clipboard()
			env['KWIX_CLIPBOARD'] = str(clipboard_bytes.decode('UTF-8'))
		except:
			pass
		shell_command = chevron.render(str(self._config['command']), env)
		shell_args = shlex.split(shell_command)
		subprocess.Popen(shell_args, env=env)
	

class Plugin(BasePlugin):
	def __init__(self, context: Context):
		super().__init__(context)
	def _create_single_action_type(self) -> ActionType:
		return BaseActionType(self.context, 'kwix.plugin.builtin.shell', str(action_type_title_text), Action, {'command': command_title_text})