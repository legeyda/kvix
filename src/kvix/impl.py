from __future__ import annotations

from inspect import isclass
from types import ModuleType
from typing import Any, Callable, Protocol, cast

import funcy

import kvix
from kvix import Action, ActionType, Context, Item, Ui
from kvix.l10n import _
from kvix.stor import Stor
from kvix.util import Propty, query_match
from kvix.util import ThreadRouter

unnamed_text = _("Unnamed").setup(ru_RU="Без названия", de_DU="Ohne Titel")
execute_text = _("Execute").setup(ru_RU="Выполнить", de_DU="Ausführen")
title_text = _("Title").setup(ru_RU="Название", de_DE="Bezeichnung")
description_text = _("Description").setup(ru_RU="Описание", de_DE="Beschreibung")
ok_text = _("OK")
cancel_text = _("Cancel").setup(ru_RU="Отмена", de_DE="Abbrechen")


class WithTitleStr:
    def __init__(self, title: Any):
        self._title = title

    def __str__(self) -> str:
        return str(self._title)


class BaseItemAlt(kvix.ItemAlt, WithTitleStr):
    def __init__(self, title: Any, command: Callable[[], None]):
        WithTitleStr.__init__(self, title)
        self._command = command

    def execute(self):
        return self._command()


class BaseItem(kvix.Item, WithTitleStr):
    def __init__(self, title: Any, alts: list[kvix.ItemAlt]):
        WithTitleStr.__init__(self, title)
        self._alts = alts


class FuncItemSource(kvix.ItemSource):
    def __init__(self, func: Callable[[str], list[kvix.Item]]):
        self._func = func

    def search(self, query: str) -> list[Item]:
        return self._func(query)


class EmptyItemSource(kvix.ItemSource):
    def search(self, query: str) -> list[kvix.Item]:
        return []


class BaseSelector(kvix.Selector):
    title = Propty(default_value=unnamed_text)
    item_source = Propty(kvix.ItemSource, default_supplier=lambda: EmptyItemSource())

    def __init__(
        self,
        item_source: kvix.ItemSource = EmptyItemSource(),
        title: str | None = None,
    ):
        self.item_source = item_source
        if title is not None:
            self.title = title


class ActionFactory(Protocol):
    def __call__(
        self,
        action_type: ActionType,
        title: str,
        description: str | None = None,
        **config: Any,
    ) -> Action:
        ...


class BaseActionType(ActionType):
    def __init__(
        self,
        context: kvix.Context,
        id: str,
        title: str,
        action_factory: ActionFactory | None = None,
        config_entry_texts: dict[str, Any] = {},
    ):
        self.context = context
        self.id = id
        self.title = title
        self.action_factory = action_factory
        self.config_entry_texts = config_entry_texts

    def create_default_action(
        self, title: str, description: str | None = None, **config: Any
    ) -> Action:
        return cast(ActionFactory, self.action_factory)(self, title, description, **config)

    def action_from_config(self, value: Any) -> Action:
        dic = {**self._assert_config_valid(value)}
        return self.create_default_action(
            str(dic["title"]),
            str(dic.get("description", "")),
            **funcy.omit(dic, ["title", "description"]),
        )

    def _assert_config_valid(self, value: Any) -> dict[Any, Any]:
        if type(value) != dict:
            raise RuntimeError("json must be object, " + value + " given")
        value = cast(dict[Any, Any], value)
        if "type" not in value:
            raise RuntimeError('"type" must be in json object')
        if value.get("type") != self.id:
            raise RuntimeError(
                "wrong type got " + str(value.get("type")) + ", expected " + self.id
            )
        return value

    def create_editor(self, builder: kvix.DialogBuilder) -> None:
        builder.create_entry("title", str(title_text))
        builder.create_entry("description", str(description_text))
        for key, text in self.config_entry_texts.items():
            builder.create_entry(key, str(text))

        def load(value: Any | None):
            if isinstance(value, Action):
                builder.widget("title").set_value(value.title)
                builder.widget("description").set_value(value.description)
                for key in self.config_entry_texts:
                    builder.widget(key).set_value(value._config[key])

        builder.on_load(load)

        def save(value: Any | None) -> Any:
            if isinstance(value, Action):
                value.title = builder.widget("title").get_value()
                value.description = builder.widget("description").get_value()
                for key in self.config_entry_texts:
                    value._config[key] = builder.widget(key).get_value()
            elif isinstance(value, dict):
                value["title"] = builder.widget("title").get_value()
                value["description"] = builder.widget("description").get_value()
                for key in self.config_entry_texts:
                    value[key] = builder.widget(key).get_value()
            elif not value:
                value = self.create_default_action(
                    builder.widget("title").get_value(),
                    builder.widget("description").get_value(),
                    **{
                        key: builder.widget(key).get_value()
                        for key in self.config_entry_texts.keys() - {"title", "description"}
                    },
                )
            return value

        builder.on_save(save)


class BaseAction(Action):
    def __init__(
        self,
        action_type: ActionType,
        title: str,
        description: str | None = None,
        **config: Any,
    ):
        self._action_type = action_type
        self._title = title
        self._description = description or title
        self._config = {**config}

    def _match(self, query: str) -> bool:
        return query_match(query or "", *self._word_list())

    def _word_list(self) -> list[str]:
        return [self.title, self.description, *self._config.values()]

    def _create_default_items(self) -> list[Item]:
        return [BaseItem(self.title, [BaseItemAlt(execute_text, self._run)])]

    def search(self, query: str) -> list[kvix.Item]:
        if not self._match(query):
            return []
        return self._create_default_items()

    def _run(self) -> None:
        raise NotImplementedError()

    def to_config(self) -> dict[str, Any]:
        return {
            "type": self.action_type.id,
            "title": self.title,
            "description": self.description,
            **self._config,
        }


class BaseActionRegistry(kvix.ActionRegistry):
    def __init__(self, stor: Stor):
        self.stor: Stor = stor

    def load(self):
        self.stor.load()
        self._actions = []
        for action_config in self.stor.data or []:
            self._actions.append(self.action_from_config(action_config))

    def save(self) -> None:
        self.stor.data = [action.to_config() for action in self.actions]
        self.stor.save()

    def add_action_type(self, action_type: ActionType) -> None:
        if action_type.id in self.action_types:
            raise RuntimeError("duplicate action type id=" + action_type.id)
        self.action_types[action_type.id] = action_type

    def action_from_config(self, value: Any) -> Action:
        if type(value) != dict:
            raise RuntimeError("dict expected, got " + type(value))
        value = cast(dict[Any, Any], value)
        if "type" not in value:
            raise RuntimeError('"type" expected')
        type_id = value["type"]
        if type(type_id) != str:
            raise RuntimeError('"type" expected to be str, got ' + type(type_id))
        if type_id not in self.action_types:
            raise RuntimeError("uknown action type id=" + type_id)
        action_type: ActionType = self.action_types[type_id]
        return action_type.action_from_config(value)

    def search(self, query: str) -> list[kvix.Item]:
        result: list[kvix.Item] = []
        for action in self.actions:
            for item in action.search(query):
                result.append(item)
        return result


class BasePlugin(kvix.Plugin):
    def __init__(self, context: kvix.Context):
        self.context = context

    def get_action_types(self) -> list[ActionType]:
        self._single_action_type = self._create_single_action_type()
        return [self._single_action_type]

    def _create_single_action_type(self) -> ActionType:
        raise NotImplementedError()

    def get_actions(self) -> list[Action]:
        return []


class FromModule(BasePlugin):
    def __init__(self, context: Context, module: ModuleType):
        BasePlugin.__init__(self, context)
        self._wrap = self._create_plugin(module)

    def _create_plugin(self, module: ModuleType) -> kvix.Plugin | None:
        if not hasattr(module, "Plugin"):
            return None
        PluginClass = getattr(module, "Plugin")
        if not isclass(PluginClass):
            return None
        if not issubclass(PluginClass, kvix.Plugin):
            return None
        return PluginClass(self.context)

    def get_action_types(self) -> list[ActionType]:
        return self._wrap.get_action_types() if self._wrap else []

    def get_actions(self) -> list[Action]:
        return self._wrap.get_actions() if self._wrap else []


class BaseUi(Ui):
    def __init__(self):
        self._thread_router: ThreadRouter = cast(ThreadRouter, None)
        self._on_ready_listeners: list[Callable[[], None]] = []

    def on_ready(self, f: Callable[[], None]) -> None:
        self._on_ready_listeners.append(f)

    def _call_on_ready_listeners(self):
        for f in self._on_ready_listeners:
            f()

    def run(self):
        self._thread_router = ThreadRouter()

    def _exec_in_mainloop(self, func: Callable[[], None]) -> None:
        self._thread_router.exec(func)

    def _process_mainloop(self):
        self._thread_router.process()
