import kwix.ui.tk.ctkwrap as tk
import kwix.ui.tk.ctkwrap.ttk as ttk

import customtkinter
from typing import Callable, Any, cast, Sequence

import pkg_resources
from PIL import Image, ImageTk

import kwix.impl
import kwix
import kwix.ui
from kwix import ItemAlt, Item
from kwix import Item, ItemSource, Conf
from kwix.impl import EmptyItemSource, BaseSelector, ok_text, cancel_text, BaseUi
from kwix.l10n import _

style_config_item_title_text = _('Theme').setup(ru_RU='Тема')


def get_logo():
	return Image.open(pkg_resources.resource_filename('kwix', 'logo.jpg'))


def run_periodically(root: tk.Tk, interval_ms: int, action):
	def on_timer():
		root.after(interval_ms, on_timer)
		action()
	on_timer()


class Ui(BaseUi):
	def __init__(self, conf: Conf):
		super().__init__()
		self.root = tk.Tk()
		self.root.wm_iconphoto(False, ImageTk.PhotoImage(get_logo()))
		self.root.title('Kwix!')
		self.root.withdraw()

		#style_conf_item = conf.scope('ui').scope('tk', 'Tk').item('theme').setup(title = str(style_config_item_title_text), default = 'ubuntu')
		#style = ThemedStyle(self.root)
		#style = ttk.Style()
		#style.theme_use(str(style_conf_item.read()))
		customtkinter.set_appearance_mode('dark')
		customtkinter.set_default_color_theme('green')
	def run(self):
		BaseUi.run(self)
		run_periodically(self.root, 10, self._process_mainloop)
		self.root.after(0, self._call_on_ready_listeners)
		self.root.mainloop()
	def _exec_in_mainloop(self, func: Callable[[], None]) -> None:
		self._thread_router.exec(func)
	def selector(self) -> kwix.Selector:
		return Selector(self)
	def dialog(self, create_dialog: Callable[[kwix.DialogBuilder], None]) -> None:
		return Dialog(self, create_dialog)
	def destroy(self):
		self._exec_in_mainloop(self._do_destroy)
	def _do_destroy(self):
		self.root.destroy()
		


class ModalWindow:
	def __init__(self, parent: Ui):
		self.parent = parent
		self.title = 'kwix'
		self._create_window()
	def _create_window(self):
		self._window = tk.Toplevel(self.parent.root)
		# self._widow.wm_iconphoto(False, ImageTk.PhotoImage(get_logo()))
		#self._window.transient(self.parent.root)
		self._window.title(self.title)
		self._window.geometry('500x500')
		self._window.columnconfigure(0, weight=1)
		self._window.rowconfigure(0, weight=1)
		self._window.bind('<Escape>', lambda _: self._do_hide())
		self._window.protocol("WM_DELETE_WINDOW", lambda: self._do_hide())
		self._window.withdraw()
	def show(self):
		self.parent._exec_in_mainloop(self._do_show)
	def _do_show(self):
		self._window.deiconify()
		self._window.title(self.title) # todo: _tkinter.TclError: bad window path name ".!toplevel"
		self._window.focus_set()
	def hide(self) -> None:
		self.parent._exec_in_mainloop(self._do_hide)
	def _do_hide(self) -> None:
		self._window.withdraw()
	def destroy(self):
		if not self._window:
			return
		def f():
			if not self._window:
				return
			self._window.destroy()
			self._window = None
		self.parent._exec_in_mainloop(f)



class Selector(ModalWindow, BaseSelector):
	actions = []

	def __init__(self, parent: Ui, item_source: ItemSource = EmptyItemSource()):
		ModalWindow.__init__(self, parent)
		kwix.impl.BaseSelector.__init__(self, item_source)
		self.result: Item | None = None
		self._init_window()

	def _init_window(self):
		self._window.bind('<Return>', cast(Any, lambda x: self._on_enter(0)))
		self._window.bind('<Alt-KeyPress-Return>', cast(Any, lambda x: self._on_enter(1)))
		for key in ['<Menu>', 'Shift-F10']: # menu key: name=menu, value=65383
			self._window.bind(key, lambda x: self._on_popup_key_press()) 
		

		self._mainframe = ttk.Frame(self._window)
		self._mainframe.grid(column=0, row=0, sticky='nsew')
		self._mainframe.rowconfigure(1, weight=1)
		self._mainframe.columnconfigure(0, weight=1)

		self._search_query = tk.StringVar()
		self._search_query.trace_add("write", lambda *_: self._on_query_entry_type())
		self._search_entry = ttk.Entry(self._mainframe, textvariable=self._search_query)
		self._search_entry.grid(column=0, row=0, sticky='ew')
		for key in ('<Up>', '<Down>', '<Control-Home>', '<Control-End>'):
			self._search_entry.bind(key, self._on_search_entry_keys) # todo bind _window and route to widgets

		result_frame = ttk.Frame(self._mainframe)
		result_frame.rowconfigure(0, weight=1)
		result_frame.columnconfigure(0, weight=1)
		result_frame.grid(column=0, row=1, sticky='nsew')

		self._result_list = tk.StringVar()
		self._result_listbox = tk.Listbox(result_frame, listvariable=self._result_list, takefocus=False, selectmode='browse')
		self._result_listbox.grid(column=0, row=0, sticky='nsew')
		self._result_listbox.bind("<Button-1>", self._on_list_left_click)
		self._result_listbox.bind("<Button-3>", self._on_list_right_click)

		scrollbar = ttk.Scrollbar(result_frame, orient='vertical')
		scrollbar.grid(column=1, row=0, sticky='nsew')

		# bind scrollbar to result list
		self._result_listbox.config(yscrollcommand=scrollbar.set)
		scrollbar.config(command = self._result_listbox.yview)


		self._on_query_entry_type()
		

	def _hide(self, event):
		self._window.withdraw()

	def _on_enter(self, alt_index: int = -1):
		item: Item | None = self._get_selected_item()
		if item:
			alts: list[ItemAlt] = item.alts
			if alt_index >= 0 and alt_index < len(alts):
				self.hide()
				alts[alt_index].execute()

	def _get_selected_item(self) -> Item | None:
		index = self._get_selected_index()
		if isinstance(index, int):
			return self._item_list[index]
		
	def _get_selected_index(self) -> int | None:
		selection = self._result_listbox.curselection()
		if not selection:
			if len(self._item_list) > 0:
				return 0
			return None
		try:
			return selection[0]
		except IndexError:
			return None

	def _on_search_entry_keys(self, event):
		if not self._result_listbox.size():
			return
		if not self._result_listbox.curselection():
			self._result_listbox.selection_set(0)
		sel: int = self._result_listbox.curselection()[0]
		newsel: int = sel
		if 'Up' == event.keysym:
			if sel > 0:
				newsel = sel - 1
		elif 'Down' == event.keysym:
			if sel + 1 < self._result_listbox.size():
				newsel = sel + 1
		elif 'Home' == event.keysym:
			newsel = 0
		elif 'End' == event.keysym:
			newsel = self._result_listbox.size() - 1
		if sel != newsel:
			sel = min(self._result_listbox.size(), max(0, sel))
			self._result_listbox.selection_clear(sel)
			self._result_listbox.selection_set(newsel)
			self._result_listbox.see(sel - 1)
			self._result_listbox.see(sel + 1)
			self._result_listbox.see(sel)

	def _on_list_left_click(self, event):
		self._select_item_at_y_pos(event.y)
		self._on_enter(0)

	def _on_list_right_click(self, event):
		self._select_item_at_y_pos(event.y)
		item: Item | None = self._get_selected_item()
		if item:
			self._show_popup_menu(item, event.x_root, event.y_root)

	def _show_popup_menu(self, item: Item, x: int, y: int) -> None:
		alts: list[ItemAlt] = item.alts
		if len(alts) >= 0:
			popup_menu = tk.Menu(self._result_listbox, tearoff=0)
			popup_menu.bind("<FocusOut>", lambda event: popup_menu.destroy())
			for alt in alts:
				def execute(alt: ItemAlt=alt):
					popup_menu.destroy()
					self.hide()						
					alt.execute()						
				popup_menu.add_command(label = str(alt), command = execute)
			popup_menu.tk_popup(x, y)

	def _on_popup_key_press(self):
		item: Item | None = self._get_selected_item()
		if item:
			x: int = int((int(self._result_listbox.winfo_rootx()) + int(self._result_listbox.winfo_width())/3))

			selected_index: int | None = self._get_selected_index()
			if isinstance(selected_index, int):
				coords: tuple[int, int, int, int] = self._result_listbox.bbox(selected_index)
				y: int = int(self._result_listbox.winfo_rooty() + (coords[1] + coords[3]/2))
			else:
				y: int = int((int(self._result_listbox.winfo_rooty()) + int(self._result_listbox.winfo_height())/3))
			self._show_popup_menu(item, x, y)


	def _select_item_at_y_pos(self, y: int):
		self._result_listbox.selection_clear(0, tk.END)
		self._result_listbox.selection_set(self._result_listbox.nearest(y))

	def go(self, on_ok: Callable[[Item, int | None], Sequence[ItemAlt]] = lambda x, y: []):
		self._on_ok = on_ok
		self.show()
		
	def _do_show(self):
		super()._do_show()
		self._search_entry.focus_set()
		self._on_query_entry_type()
		self._search_entry.select_range(0, 'end')
		
		
	def _on_query_entry_type(self) -> None:
		self._item_list = self.item_source.search(self._search_query.get())
		self._result_list.set(cast(Any, [str(item) for item in self._item_list]))
		if self._item_list:
			self._result_listbox.select_clear(0, tk.END)
			self._result_listbox.selection_set(0)
		self._result_listbox.see(0)



class Dialog(kwix.Dialog, ModalWindow):
	def __init__(self, parent: Ui, create_dialog: Callable[[kwix.DialogBuilder], None]):
		ModalWindow.__init__(self, parent)
		self.create_dialog = create_dialog
		self._init_window()
	def _init_window(self):
		self._window.bind('<Return>', cast(Any, self._ok_click))

		frame = ttk.Frame(self._window, padding=8)
		frame.grid(column=0, row=0, sticky='nsew')
		frame.columnconfigure(0, weight=1)
		frame.rowconfigure(0, weight=1)

		data_frame = ttk.Frame(frame)
		data_frame.grid(column=0, row=0, sticky='nsew')

		self.builder = DialogBuilder(data_frame)
		self.create_dialog(self.builder)
		children = data_frame.winfo_children()
		if len(children) >= 2:
			self._first_entry = children[1]
		
		control_frame = ttk.Frame(frame)
		control_frame.rowconfigure(0, weight=1)
		control_frame.columnconfigure(0, weight=1)
		control_frame.grid(column=0, row=1, sticky='nsew')

		ok_button = ttk.Button(control_frame, text=str(ok_text), command=self._ok_click)
		ok_button.grid(column=1, row=0, padx=4)

		cancel_button = ttk.Button(control_frame, text=str(cancel_text), command=self.hide)
		cancel_button.grid(column=2, row=0, padx=4)

	def _ok_click(self, *args):
		self.hide()
		self.value = self.builder.save(self.value)
		self.on_ok()
		if self.auto_destroy:
			self.destroy()
	def _cancel_click(self, *args):
		self.hide()
		self.on_cancel()
		if self.auto_destroy:
			self.destroy()
	def go(self) -> None: # todo rename to "show"
		self.builder.load(self.value)
		self.show()
	def _do_show(self):
		super()._do_show()
		self._first_entry.select_range(0, 'end')
		self._first_entry.focus_set()
	def destroy(self) -> None:
		return ModalWindow.destroy(self)
		



class DialogEntry(kwix.DialogEntry):
	def __init__(self, label: ttk.Label, string_var: tk.StringVar):
		self._label = label
		self._string_var = string_var

	def set_title(self, text: str):
		self._label.config(text=text)

	def get_value(self):
		return self._string_var.get()

	def set_value(self, value):
		self._string_var.set(value)

	def on_change(self, func: callable):
		self._string_var.trace_add(
			"write", lambda *args, **kwargs: func(self._string_var.get()))


class DialogBuilder(kwix.DialogBuilder):
	def __init__(self, root_frame: ttk.Frame):
		super().__init__()
		self._root_frame = root_frame
		self._widget_count = 0	

	def create_entry(self, id: str, title: str) -> DialogEntry:
		self._root_frame.columnconfigure(0, weight=1)

		label = ttk.Label(self._root_frame, text=title)
		label.grid(column=0, row=self._widget_count, sticky='ew')
		self._widget_count += 1

		string_var = tk.StringVar(self._root_frame)
		entry = ttk.Entry(self._root_frame, textvariable=string_var)
		entry.grid(column=0, row=self._widget_count, sticky='ew')
		self._widget_count += 1
		if self._widget_count == 2:
			entry.focus_set()

		separator = ttk.Label(self._root_frame, text='')
		separator.grid(
			column=0, row=self._widget_count, sticky='ew')
		self._widget_count += 1

		return cast(DialogEntry, self._add_widget(id, DialogEntry(label, string_var)))
