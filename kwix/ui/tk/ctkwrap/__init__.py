from tkinter import *
import typing as _typing
from customtkinter import CTkFont as _CTkFont

from CTkListbox import CTkListbox as _CTkListbox

class _Listbox(_CTkListbox):
	def __init__(self,
			     # from CTkListbox
                 master: any,
                 height: int = 100,
                 width: int = 200,
                 hightlight_color: str = "default",
                 fg_color: str = "transparent",
                 bg_color: str = None,
                 text_color: str = "default",
                 select_color: str = "default",
                 hover_color: str = "default",
                 border_width: int = 3,
                 font: tuple = "default",
                 multiple_selection: bool = False,
                 listvariable = None,
                 hover: bool = True,
                 command = None,
                 justify = "left",
				 # from CTkScrollableFrame
                 corner_radius: _typing.Optional[_typing.Union[int, str]] = None,
                 border_color: _typing.Optional[_typing.Union[str, _typing.Tuple[str, str]]] = None,
                 scrollbar_fg_color: _typing.Optional[_typing.Union[str, _typing.Tuple[str, str]]] = None,
                 scrollbar_button_color: _typing.Optional[_typing.Union[str, _typing.Tuple[str, str]]] = None,
                 scrollbar_button_hover_color: _typing.Optional[_typing.Union[str, _typing.Tuple[str, str]]] = None,
                 label_fg_color: _typing.Optional[_typing.Union[str, _typing.Tuple[str, str]]] = None,
                 label_text_color: _typing.Optional[_typing.Union[str, _typing.Tuple[str, str]]] = None,
                 label_text: str = "",
                 label_font: _typing.Optional[_typing.Union[tuple, _CTkFont]] = None,
                 label_anchor: str = "center",
                 orientation: _typing.Literal["vertical", "horizontal"] = "vertical",
				 **kwargs):
		if listvariable:
			if not listvariable.get():
				listvariable.set('[]')
		super().__init__(
			master = master,
			height = height,
			width = width,
			hightlight_color = hightlight_color,
			fg_color = fg_color,
			bg_color = bg_color,
			text_color = text_color,
			select_color = select_color,
			hover_color = hover_color,
			border_width = border_width,
			font = font,
			multiple_selection = multiple_selection,
			listvariable = listvariable,
			hover = hover,
			command = command,
			justify = justify,
			corner_radius = corner_radius,
			border_color = border_color,
			scrollbar_fg_color = scrollbar_fg_color,
			scrollbar_button_color = scrollbar_button_color,
			scrollbar_button_hover_color = scrollbar_button_hover_color,
			label_fg_color = label_fg_color,
			label_text_color = label_text_color,
			label_text = label_text,
			label_font = label_font,
			label_anchor = label_anchor,
			orientation = orientation)
	def config(self, cnf=None, **kw):
		for key in ('yscrollcommand',):
			if key in kw.keys():
				del kw[key]
		super().config(cnf, **kw)
	def yview(self, *args: _typing.Any, **kwargs: _typing.Any):
		pass
	def see(self, *args: _typing.Any, **kwargs: _typing.Any):
		pass
	def update_listvar(self):
		if not self.listvariable.get():
			self.listvariable.set('[]')
		super().update_listvar()
	def select_clear(self, *arlgs):
		pass
		# todo
	def selection_set(self, *args):
		pass # todo