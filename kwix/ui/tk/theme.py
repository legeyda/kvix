
from tkinter import ttk



darcula_name = 'kwix.darcula'


def init(style: ttk.Style) -> None:
	text_color = "#adadad"
	face_back_color = "#3c3f41"
	edit_back_color = "#282829"
	highlight_color = "#375a96"

	darcula_theme = {
		".": { 
			"configure": {
				'foreground': text_color,
				"background": face_back_color,
				"fieldbackground": edit_back_color,
				#"foreground": text_color,
				"highlightbackground": highlight_color,
				"highlightcolor": highlight_color,

			}
		},
		"TLabel": {
			"configure": {
				"foreground": "white",
				"background": face_back_color
			}
		},
		"TButton": {
			"configure": {
				"background": face_back_color,
				"foreground": "white",
			}
		},
		'TEntry': {
			"configure": {
			}
		},
		'TListbox': {
			'configure': {
				'background': edit_back_color
			}
		}
	}
	style.theme_create(darcula_name, parent="clam", settings=darcula_theme)