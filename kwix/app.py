
from typing import Any, Sequence

import pynput

import kwix.impl
import kwix.plugin
import kwix.ui.tk
import kwix.ui.tray
from kwix import Action, ActionRegistry, Context, Item
from kwix.conf import Conf, StorConf
from kwix.impl import BaseItem, BaseItemAlt, FuncItemSource, BaseActionRegistry
from kwix.l10n import _
from kwix.stor import YamlFile
from kwix.util import get_config_dir, get_data_dir, get_cache_dir, ensure_type, apply_template
from kwix.plugin import Plugin as PanPlugin
from argparse import ArgumentParser
from kwix.remote import Server, Client as RemoteClient
from enum import Enum

activate_action_text = _('Activate').setup(ru_RU='Выпуолнить', de_DE='Aktivieren')
edit_action_text = _('Edit Action: {{action_title}} ({{action_type_title}})').setup(ru_RU='Редактировать действие "{{action_title}}" ({{action_type_title}})', de_DE='Aktion Bearbeiten: "{{action_title}}" ({{action_type_title}})')
delete_action_text = _('Remove Action: {{action_title}} ({{action_type_title}})').setup(ru_RU='Удалить действие "{{action_title}}" ({{action_type_title}})', de_DE='Aktion Löschen "{{action_title}}" ({{action_type_title}})')




def load_conf():
	result = StorConf(YamlFile(get_config_dir().joinpath('config.yaml')))
	result.load()
	return result

class App(Context):

	
	def __init__(self, conf: Conf | None = None):
		self._conf = conf

	def run(self):
		self.init_conf()
		self.init_action_stor()
		self.init_cache_stor()
		self.init_action_registry()
		self.load_actions()
		self.init_tray()

	def init_conf(self):
		if not self._conf:
			self._conf = self.create_conf()
	def create_conf(self) -> Conf:
		return load_conf()
		
	
	def init_action_stor(self):
		self.action_stor = self.create_action_stor()
		self.action_stor.data = []
	def create_action_stor(self):
		return YamlFile(get_data_dir().joinpath('actions.yaml'))

	def init_cache_stor(self):
		self._cache_stor = self.create_cache_stor()
		self._cache_stor.data = self._cache_stor.data or {}
	def create_cache_stor(self):
		return YamlFile(get_cache_dir().joinpath('cache.yaml'))
	
	def init_action_registry(self):
		self._action_registry = self.create_action_registry()
		self._action_registry.action_types
	def create_action_registry(self) -> ActionRegistry:
		return BaseActionRegistry(self.action_stor)
	

	def load_actions(self):
		# load action types from plugins
		pan_plugin = PanPlugin(self)
		for action_type in pan_plugin.get_action_types():
			self._action_registry.add_action_type(action_type)

		# load action from config
		self.action_registry.load()

		# load known action type ids
		self._cache_stor.load()
		self._cache_stor.data = self._cache_stor.data or {}
		cache = ensure_type(self._cache_stor.data, dict)
		known_action_types_ids = set(ensure_type(cache.get('known_action_type_ids', []), list))

		# from plugins load actions which are of unknown action types
		for action in pan_plugin.get_actions():
			if not action.action_type.id in known_action_types_ids:
				self.action_registry.actions.append(action)
		self.action_registry.save()

		# save known action type id cache
		cache['known_action_type_ids'] = list(set([id for id in self._action_registry.action_types]))
		self._cache_stor.save()

	def init_tray(self):
		self.tray = kwix.ui.tray.TrayIcon()
		self.tray.on_show = self.activate_action_selector
		self.tray.on_quit = self.quit
		self.tray.run(self.init_ui)

	def init_ui(self):
		self._ui = kwix.ui.tk.Ui()
		self.init_action_selector()
		self.register_global_hotkeys()
		self._ui.on_start = self.on_start
		self.ui.run()
		
	def init_action_selector(self):
		self.action_selector = self.ui.selector()
		self.action_selector.title = 'Kwix!!!'
		def edit_action(action: Action) -> None:
			dialog = action.action_type.context.ui.dialog(action.action_type.create_editor)
			dialog.value = action
			dialog.on_ok = lambda: self.action_registry.save()
			dialog.go()
		def delete_action(action: Action) -> None:
			self.action_registry.actions.remove(action)
			self.action_registry.save()
		def search(query: str) -> list[Item]:
			result: list[Item] = []
			for action in self.action_registry.actions:
				for item in action.search(query):
					alts = list(item.alts)
					def edit_this_action(action: Action = action):
						edit_action(action)
					alts.append(BaseItemAlt(apply_template(str(edit_action_text), action_title=action.title, action_type_title=action.action_type.title), edit_this_action))
					def delete_this_action(action: Action = action):
						delete_action(action)
					alts.append(BaseItemAlt(apply_template(str(delete_action_text), action_title=action.title, action_type_title=action.action_type.title), delete_this_action))
					result.append(BaseItem(str(item), alts))
			return result
		self.action_selector.item_source = FuncItemSource(search)

	def activate_action_selector(self):
		self.action_selector.go()

	def quit(self):
		self.conf.save()
		self.action_registry.save()
		self.ui.destroy()
		self.tray.stop()
		
		#self.server.stop()

	def register_global_hotkeys(self):
		activate_window_hotkey = self.conf.item('activate_window_hotkey').setup(title = "Activate Window Hotkey", default = '<ctrl>+;', read_mapping=str)
		pynput.keyboard.GlobalHotKeys({activate_window_hotkey.read(): self.activate_action_selector}).start()
	



class RemoteCommand(Enum):
    ping = 'ping'
    activate = 'activate'
    quit = 'quit'
    def __str__(self):
	    return self.value


def main(*args: str):
	parser = ArgumentParser(prog='kwix')
	parser.add_argument('-r', '--remote', type=RemoteCommand, choices=list(RemoteCommand), help='activate remote command')
	#parser.add_argument('-a', '--activate', action='store_true', help='show action selector immediately after start')
	#parser.add_argument('-f', '--force', action='store_true', help='skip existing running instance check')
	parsed_args = parser.parse_args(args)

	conf = load_conf()
	remote_client = RemoteClient(conf)
	if parsed_args.remote:
		if RemoteCommand.ping == parsed_args.remote:
			remote_client.ping()
		elif RemoteCommand.activate == parsed_args.remote:
			remote_client.activate()
		elif RemoteCommand.quit == parsed_args.remote:
			remote_client.quit()
	elif not remote_client.is_server_ready():
		app = App(conf)
		server = Server(app, app.activate_action_selector)
		try:
			server.start()
			app.run()
		finally:
			server.stop()
	else:
		print('already running')

if __name__ == '__main__':
	main(*sys.argv)
	