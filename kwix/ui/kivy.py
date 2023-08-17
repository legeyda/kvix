from __future__ import annotations


from kivy.config import Config
Config.set('kivy', 'exit_on_escape', '0')

from kivy.core.window import Window
Window.hide()

from kivy.app import App as KivyApp

from kivy.uix.widget import Widget
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.clock import Clock



from kwix import DialogBuilder
import kwix
from kwix.conf import Conf
from kwix.impl import BaseUi
from typing import cast, Any, Callable
from uuid import uuid4


def show_window():
	Window.show()
	Window.always_on_top = False
	Window.always_on_top = True
	Window._focus = True


def hide_window():
	Window.hide()


class NamePlusWidget:
	def __init__(self, name: str, widget: Widget):
		self.name = name
		self.widget = widget

class WindowManager:

	def __init__(self, screen_manager: ScreenManager):
		self._screen_manager = screen_manager
		self._widgets: list[NamePlusWidget] = []
		self._stack: list[NamePlusWidget] = []
	def add(self, widget: Widget) -> None:
		if self._contains_widget(widget):
			return
		name = 'window_' + str(uuid4())
		screen = Screen(name = name)
		screen.add_widget(widget)
		self._screen_manager.add_widget(screen)
		self._widgets.append(NamePlusWidget(name, widget))
	def _contains_widget(self, widget: Widget):
		return widget in [t.widget for t in self._widgets]
	def show(self, widget: Widget):
		self.add(widget)
		if widget in [t.widget for t in self._stack]:
			show_window()
			return
		for t in self._widgets:
			if t.widget == widget:
				self._stack.append(t)
				self._screen_manager.current = t.name
				show_window()
				
	def _assert_contains_widget(self, widget: Widget):
		if widget not in [t.widget for t in self._widgets]:
			raise RuntimeError('widget not created created')
	def hide(self, widget: Widget) -> None:
		self._assert_contains_widget(widget)
		if not self._stack:
			return
		if widget in [t.widget for t in self._stack[:-1]]:
			raise RuntimeError('window is blocked by child modal window')
		if widget != self._stack[-1].widget:
			return
		del self._stack[-1]
		if self._stack:
			self._screen_manager.current = self._stack[-1].name
		else:
			hide_window()
	def hide_all(self) -> None:
		self._stack.clear()
		self._screen_manager.current = None		
	def delete(self, widget: Widget):
		if not self._contains_widget(widget):
			return
		if self._stack:
			self.hide(widget)
		for i in range(len(self._widgets)):
			if self._widgets[i] == widget:
				del self._widgets[i]
				return


class KwixKivyApp(KivyApp):
	pass


class Ui(BaseUi):
	def __init__(self, conf: Conf):
		self._conf = conf
		self._init_widgets()
	def _init_widgets(self):
		screen_manager = ScreenManager()
		self._window_manager = WindowManager(screen_manager)
		self._app = KwixKivyApp()
		self._app.root = screen_manager
	def run(self) -> None:
		BaseUi.run(self)
		#Window.borderless = True
		def on_keyboard(window, key, scancode, codepoint, modifier):
			if 27 == key: # escape
				hide_window()
				pass
		def on_key_down(window, key, scancode, codepoint, modifier):
			if 27 == key: # escape
				hide_window()
				return True
			#print("got a key event: %s" % list(args))
		Window.bind(on_key_down=on_key_down, on_keyboard = on_keyboard)
		def on_request_close(*args):
			Window.hide()
			self._window_manager.hide_all()
			return True
		Window.bind(on_request_close=on_request_close)
		Clock.schedule_interval(lambda *args: self._process_mainloop(), .1)
		self._app.run()
	def selector(self) -> Selector:
		return Selector(self)
	def dialog(self, create_dialog: Callable[[DialogBuilder], None]) -> Dialog:
		raise NotImplementedError()
	def destroy(self) -> None:
		self._app.stop()


class SelectorScreen(Screen):
	def __init__(self, *args, **kwargs):
		kwargs['name'] = str(uuid4())
		Screen.__init__(*args, **kwargs)

class Selector(kwix.Selector):
	def __init__(self, parent: Ui):
		self._parent = parent
		self._init_widgets()
	def _init_widgets(self):
		self._query_text_input = TextInput(text='Hello world')

		layout = RecycleBoxLayout(orientation = 'vertical')

		self._result_view = RecycleView()
		self._result_view.add_widget(layout)
		self._result_view.data = []
		
		self._widget = BoxLayout(orientation='vertical')
		self._widget.add_widget(self._query_text_input)
		self._widget.add_widget(self._result_view)

		self._parent._window_manager.add(self._widget)

	def go(self) -> None:
		def go():
			self._parent._app.title = self.title
			self._parent._window_manager.show(self._widget)
			self._query_text_input.select_all()
			self._query_text_input.focus = True
		self._parent._exec_in_mainloop(go)
	def destroy(self) -> None:
		def go():
			self._parent._window_manager.delete(self._widget)
			self._widget = None # avoid later illegal use
		self._parent._exec_in_mainloop(go)
