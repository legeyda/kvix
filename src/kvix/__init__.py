from __future__ import annotations

from typing import Any, Callable, Sequence

from kvix.util import Propty
from kvix.conf import Conf


class ItemAlt:
    def execute(self) -> None:
        raise NotImplementedError()


class Item:
    priority = Propty(int)
    alts = Propty(list[ItemAlt], writeable=False)


class ItemSource:
    def search(self, query: str) -> Sequence[Item]:
        raise NotImplementedError()


class Context:
    conf = Propty(Conf, writeable=False)
    ui: Propty[Ui] = Propty(writeable=False)
    action_registry: Propty[ActionRegistry] = Propty(writeable=False)

    def quit(self) -> None:
        raise NotImplementedError()


class ActionType:
    context = Propty(type=Context)
    id = Propty(type=str)
    title = Propty(type=str)

    def action_from_config(self, value: Any) -> Action:
        raise NotImplementedError()

    def create_editor(self, builder: DialogBuilder) -> None:
        raise NotImplementedError()


class Action:
    action_type = Propty(ActionType)
    title = Propty(str)

    def search(self, query: str) -> Sequence[Item]:
        raise NotImplementedError()

    def to_config(self) -> dict[str, Any]:
        raise NotImplementedError()


class ActionRegistry(ItemSource):
    action_types = Propty(dict[str, ActionType], writeable=False)
    actions = Propty(list[Action], writeable=False)

    def load(self) -> None:
        raise NotImplementedError()

    def save(self) -> None:
        raise NotImplementedError()

    def add_action_type(self, action_type: ActionType) -> None:
        raise NotImplementedError()

    def action_from_config(self, value: Any) -> Action:
        raise NotImplementedError()

    def search(self, query: str) -> Sequence[Item]:
        raise NotImplementedError()


class Ui:
    def on_ready(self, f: Callable[[], None]) -> None:
        raise NotImplementedError()

    def run(self) -> None:
        raise NotImplementedError()

    def selector(self) -> Selector:
        raise NotImplementedError()

    def dialog(self, create_dialog: Callable[[DialogBuilder], None]) -> Dialog:
        raise NotImplementedError()

    def destroy(self) -> None:
        raise NotImplementedError()

    def copy_to_clipboard(self, data: bytes) -> None:
        raise NotImplementedError()

    def paste_from_clipboard(self) -> bytes:
        raise NotImplementedError()

    def hide(self) -> None:
        "hide and release focus"
        raise NotImplementedError()


class Window:
    title = Propty(str, default_value="kvix")

    def activate(self) -> None:
        raise NotImplementedError()

    def destroy(self) -> None:
        raise NotImplementedError()


class Selector(Window):
    item_source = Propty(ItemSource)

    def hide(self) -> None:
        raise NotImplementedError()


class Dialog(Window):
    value = Propty()
    on_ok = Propty(Callable[[], None], default_value=lambda: None)
    on_cancel = Propty(Callable[[], None], default_value=lambda: None)
    auto_destroy = Propty(bool, default_value=True)  # todo remove?


class DialogWidget:
    def get_value(self) -> str:
        raise NotImplementedError()

    def set_value(self, value: str) -> None:
        raise NotImplementedError()


class DialogEntry(DialogWidget):
    pass


class DialogBuilder:
    def __init__(self):
        self._on_load: list[Callable[[Any | None], None]] = []
        self._on_save: list[Callable[[Any | None], Any]] = []
        self._widgets: dict[str, DialogWidget] = {}

    def create_entry(self, id: str, title: str) -> DialogEntry:
        raise NotImplementedError()

    def widget(self, id: str) -> DialogWidget:
        return self._widgets[id]

    def _add_widget(self, id: str, widget: DialogWidget) -> DialogWidget:
        self._widgets[id] = widget
        return widget

    def on_load(self, func: Callable[[Any | None], None]):
        self._on_load.append(func)

    def load(self, value: Any | None):
        for func in self._on_load:
            func(value)

    def on_save(self, func: Callable[[Any | None], Any]):
        self._on_save.append(func)

    def save(self, value: Any) -> Any | None:
        for func in self._on_save:
            value = func(value)
        return value


class Plugin:
    def __init__(self, context: Context): ...

    def get_action_types(self) -> Sequence[ActionType]: ...

    def get_actions(self) -> Sequence[Action]: ...
