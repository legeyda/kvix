from __future__ import annotations

import tkinter as tk
from tkinter import (
    Misc as _TkMisc,
    Tk as _Tk,
    Listbox as _TkListbox,
    Entry as _TkEntry,
    Button as _TkButton,
    Scrollbar as _TkScrollbar,
    INSERT,
)
from tkinter.ttk import Style as _TkStyle
from typing import Any as _Any, cast as _cast, Generator as _Generator
from .util import find_all_children

from kvix.l10n import _

copy_text = _("Copy").setup(ru_RU="Копировать", de_DE="Kopieren")
cut_text = _("Cut").setup(ru_RU="Вырезать", de_DE="Ausschneiden")
del_text = _("Delete").setup(ru_RU="Удалить", de_DE="Entfernen")
paste_text = _("Paste").setup(ru_RU="Вставить", de_DE="Einfügen")

_style_singleton: BaseStylePlus = None


def _apply_widget_style(widget: _TkMisc):
    if _style_singleton:
        _style_singleton.configure_widgets(widget)


class Listbox(_TkListbox):
    def __init__(self, master=None, cnf={}, **kw):
        _TkListbox.__init__(self, master, cnf, **kw)
        _apply_widget_style(self)


class Menu(tk.Menu):
    def __init__(
        self,
        master: tk.Tk | None = None,
        cnf: dict[str, _Any] = {},
        **kw: _Any,
    ):
        tk.Menu.__init__(self, master, cnf, **kw)
        _apply_widget_style(self)


class Entry(_TkEntry):
    def __init__(
        self,
        master: tk.Tk | None = None,
        cnf: dict[str, _Any] = {},
        **kw: _Any,
    ):
        _TkEntry.__init__(self, master, cnf, **kw)
        _apply_widget_style(self)
        self._init_menu()
        self.bind("<<Paste>>", lambda _: self._delete())

    def _init_menu(self):
        self._popup_menu = Menu(self, tearoff=False)
        self._add_popup_menu_item(copy_text, lambda: self.event_generate("<<Copy>>"))
        self._add_popup_menu_item(cut_text, lambda: self.event_generate("<<Cut>>"))
        self._add_popup_menu_item(del_text, lambda: self._delete())
        self._popup_menu.add_separator()
        self._add_popup_menu_item(paste_text, lambda: self.event_generate("<<Paste>>"))
        self.bind(
            "<Button-3>",
            lambda event: self._popup_menu.tk_popup(event.x_root, event.y_root),
        )

    def _add_popup_menu_item(self, text, command):
        self._popup_menu.add_command(label=str(text), command=command)

    def _delete(self):
        if not self.selection_present():
            return
        self.delete(self.index("sel.first"), self.index("sel.last"))


class Button(_TkButton):
    def __init__(self, master=None, cnf={}, **kw):
        _TkButton.__init__(self, master, cnf, **kw)
        _apply_widget_style(self)


class Scrollbar(_TkScrollbar):
    def __init__(self, master=None, cnf={}, **kw):
        _TkScrollbar.__init__(self, master, cnf, **kw)
        _apply_widget_style(self)


class ThemePlus:
    def __init__(
        self,
        frame_back_color: str = "",
        button_back_color: str = "",
        edit_back_color: str = "",
        back_color: str = "",
        button_text_color: str = "",
        edit_text_color: str = "",
        text_color: str = "",
        select_back_color: str = "",
    ):
        self.frame_back_color = frame_back_color or back_color
        self.button_back_color = button_back_color or frame_back_color or back_color
        self.edit_back_color = edit_back_color or back_color

        self.button_text_color = button_text_color or edit_text_color or text_color
        self.edit_text_color = edit_text_color or button_text_color or text_color
        self.select_back_color = select_back_color

    def create_settings(self) -> dict[str, _Any]:
        return {
            ".": {
                "configure": {
                    "background": self.frame_back_color,
                    "foreground": self.button_text_color,
                    "insertbackground": self.edit_text_color,  # insert blinking cursor color
                    "fieldbackground": self.edit_back_color,
                    "selectbackground": self.select_back_color,
                    "selectforeground": self.edit_text_color,
                    "highlightthickness": "0"
                    # 'highlightcolor': self.highlight_color,
                }
            }
        }

    def configure_widget(self, widget: _TkMisc):
        if "Listbox" == widget.winfo_class():
            _cast(_TkListbox, widget).configure(
                background=self.edit_back_color,
                foreground=self.edit_text_color,
                selectbackground=self.select_back_color,
                selectforeground=self.edit_text_color,
                highlightthickness="0",
            )
        elif "Entry" == widget.winfo_class():
            _cast(_TkEntry, widget).configure(
                background=self.edit_back_color,
                foreground=self.edit_text_color,
                insertbackground=self.edit_text_color,
                highlightthickness="0",
                selectbackground=self.select_back_color,
                selectforeground=self.edit_text_color,
            )
        elif "Button" == widget.winfo_class():
            _cast(_TkButton, widget).configure(
                bg=self.button_back_color, fg=self.button_text_color
            )
        elif "Scrollbar" == widget.winfo_class():
            _cast(_TkScrollbar, widget).configure(background=self.button_back_color)
        elif "Menu" == widget.winfo_class():
            _cast(tk.Menu, widget).configure(
                background=self.button_back_color,
                foreground=self.button_text_color,
                activebackground=self.select_back_color,
                activeforeground=self.button_text_color,
            )


class BaseStylePlus:
    def __init__(self):
        global _style_singleton
        if _style_singleton:
            raise Exception("kvix.ui.tk.plus:Style should be singleton")
        _style_singleton = self
        self._themes: dict[str, ThemePlus] = {}
        self._current_theme_name: str = ""

    def theme_plus_register(self, theme_name: str, theme: ThemePlus) -> None:
        if theme_name in self._themes:
            raise Exception("duplicate theme: " + theme_name)
        self._themes[theme_name] = theme

    def theme_plus_use(self, theme_name: str, root_widget: _TkMisc):
        if not theme_name:
            return self._current_theme_name
        if theme_name not in self._themes:
            return
        self._current_theme_name = theme_name
        self.configure_widgets(root_widget)
        return theme_name

    def configure_widgets(self, root: _TkMisc):
        if not self._current_theme_name:
            return
        current_theme = self._themes[self._current_theme_name]
        if not current_theme:
            return
        for widget in find_all_children(root):
            current_theme.configure_widget(widget)


class Style(BaseStylePlus, _TkStyle):
    def __init__(self, master: _Tk | None = None):
        _TkStyle.__init__(self, master)
        BaseStylePlus.__init__(self)
        self.theme_register(
            "dark",
            "clam",
            ThemePlus(
                frame_back_color="#3c3f41",
                button_back_color="#333333",
                edit_back_color="#282829",
                text_color="#adadad",
                select_back_color="#173a7b",
            ),
        )
        self.theme_register(
            "light",
            "clam",
            ThemePlus(
                frame_back_color="#dddddd",
                button_back_color="#cccccc",
                edit_back_color="#ffffff",
                text_color="#000000",
                select_back_color="#aaaaff",
            ),
        )

    def theme_register(self, theme_name: str, parent: str | None, theme: ThemePlus) -> None:
        BaseStylePlus.theme_plus_register(self, theme_name, theme)
        _TkStyle.theme_create(self, theme_name, parent, theme.create_settings())

    def theme_use(self, themename: str | None) -> str | None:
        if themename is None:
            return _TkStyle.theme_use(self)
        _TkStyle.theme_use(self, themename)
        if self.master:
            BaseStylePlus.theme_plus_use(self, str(themename), self.master)
