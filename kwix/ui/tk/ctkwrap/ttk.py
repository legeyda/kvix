# wrapper for migration to customtkinter without refactoring of existing code

from tkinter.ttk import *

import typing as _typing
import customtkinter as _ctk


Tk = _ctk.CTk
Button = _ctk.CTkButton
Entry = _ctk.CTkEntry
Label = _ctk.CTkLabel
#_ctk.CTk

# silently ignore unsuported ctor arguments: padding etc
class Frame(_ctk.CTkFrame):
	def __init__(self,
			  master: any, 
			  width: int = 200,
			  height: int = 200,
			  corner_radius: _typing.Optional[_typing.Union[int, str]] = None,
			  border_width: _typing.Optional[_typing.Union[int, str]] = None,
			  bg_color: _typing.Union[str, _typing.Tuple[str, str]] = "transparent",
              fg_color: _typing.Optional[_typing.Union[str, _typing.Tuple[str, str]]] = None,
              border_color: _typing.Optional[_typing.Union[str, _typing.Tuple[str, str]]] = None,
              background_corner_colors: _typing.Union[_typing.Tuple[_typing.Union[str, _typing.Tuple[str, str]]], None] = None,
              overwrite_preferred_drawing_method: _typing.Union[str, None] = None,
			  **kwargs):
		super().__init__(
			master = master,
			width = width,
			height = height,
			corner_radius = corner_radius,
			border_width = border_width,
			bg_color = bg_color,
			fg_color = fg_color,
			border_color = border_color,
			background_corner_colors = background_corner_colors,
			overwrite_preferred_drawing_method = overwrite_preferred_drawing_method)