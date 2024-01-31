from __future__ import annotations

from inspect import isclass
from types import ModuleType
from typing import Any, Callable, Protocol, cast, Sequence

import funcy
import re

import kvix
from kvix import Action, ActionType, Context, Item, ItemAlt, Ui
from kvix.l10n import _
from kvix.stor import Stor
from kvix.util import Propty, query_match, apply_template
from kvix.util import ThreadRouter

unnamed_text = _("Unnamed").setup(ru_RU="Без названия", de_DE="Ohne Titel")
execute_text = _("Execute").setup(ru_RU="Выполнить", de_DE="Ausführen")
title_text = _("Title").setup(ru_RU="Название", de_DE="Bezeichnung")
description_text = _("Description").setup(ru_RU="Описание", de_DE="Beschreibung")
pattern_text = _("Regular expression").setup(
    ru_RU="Регулярное выражение", de_DE="Regular expression"
)
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
    def __init__(self, title: Any, alts: Sequence[kvix.ItemAlt]):
        WithTitleStr.__init__(self, title)
        self._alts = alts


class BaseItemSource(kvix.ItemSource):
    def __init__(self, func: Callable[[str], list[kvix.Item]]):
        self._func = func

    def search(self, query: str) -> Sequence[Item]:
        return self._func(query)


class EmptyItemSource(kvix.ItemSource):
    def search(self, query: str) -> Sequence[kvix.Item]:
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
        description: str = "",
        pattern: str = "",
        **config: Any,
    ) -> Action:
        ...


class BaseActionType(ActionType):
    BUILTIN_PARAMS = ["title", "description", "pattern"]

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
        self, title: str, description: str = "", pattern: str = "", **params: Any
    ) -> Action:
        return cast(ActionFactory, self.action_factory)(
            self, title=title, description=description, pattern=pattern, **params
        )

    def action_from_config(self, value: Any) -> Action:
        dic = {**self._assert_config_valid(value)}
        return self.create_default_action(
            title=str(dic["title"]),
            description=str(dic.get("description", "")),
            pattern=str(dic.get("pattern", "")),
            **funcy.omit(dic, ["action_type"] + BaseActionType.BUILTIN_PARAMS),
        )

    def _assert_config_valid(self, value: Any) -> dict[Any, Any]:
        if not isinstance(value, dict):
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
        builder.create_entry("pattern", str(pattern_text))
        for key, text in self.config_entry_texts.items():
            builder.create_entry(key, str(text))

        def load(value: Any | None):
            if isinstance(value, Action):
                builder.widget("title").set_value(value.title)
                builder.widget("description").set_value(value._description)
                builder.widget("pattern").set_value(value._pattern)
                for key in self.config_entry_texts:
                    builder.widget(key).set_value(value._config[key])

        builder.on_load(load)

        def save(value: Any | None) -> Any:
            if isinstance(value, Action):
                value.title = builder.widget("title").get_value()
                value._description = builder.widget("description").get_value()
                value._pattern = builder.widget("pattern").get_value()
                for key in self.config_entry_texts:
                    value._config[key] = builder.widget(key).get_value()
            elif isinstance(value, dict):
                value["title"] = builder.widget("title").get_value()
                value["description"] = builder.widget("description").get_value()
                value["pattern"] = builder.widget("pattern").get_value()
                for key in self.config_entry_texts:
                    value[key] = builder.widget(key).get_value()
            elif not value:
                value = self.create_default_action(
                    builder.widget("title").get_value(),
                    builder.widget("description").get_value(),
                    builder.widget("pattern").get_value(),
                    **{
                        key: builder.widget(key).get_value()
                        for key in self.config_entry_texts.keys() - BaseActionType.BUILTIN_PARAMS
                    },
                )
            return value

        builder.on_save(save)


class BaseAction(Action):
    def __init__(
        self,
        action_type: ActionType,
        title: str,
        description: str = "",
        pattern: str = "",
        **params: Any,
    ):
        self._action_type = action_type
        self._title = title
        self._description = description or title
        self._pattern = pattern
        self._set_params(**params)

    def _set_params(self, **params: Any) -> None:
        self._config = {**params}  # todo rename to params
        self._on_after_set_params(**params)

    def _on_after_set_params(self, **params: Any) -> None:
        pass

    def search(self, query: str) -> Sequence[kvix.Item]:
        if not self._match(query):
            return []
        return self._create_items(query)

    def _match(self, query: str) -> bool:
        if not query:
            return True
        if self._pattern:
            return re.compile(self._pattern).match(query) and True or False
        return query_match(query or "", *self._word_list()) and True or False

    def _word_list(self) -> Sequence[str]:
        return [self.title, self._description, *self._config.values()]

    def _create_items(self, query: str) -> Sequence[Item]:
        return (self._create_single_item(query),)

    def _create_single_item(self, query: str) -> Item:
        return BaseItem(self._get_single_item_title(query), self._create_single_item_alts(query))

    def _get_single_item_title(self, query: str) -> str:
        return apply_template(self._title, query=query)

    def _create_single_item_alts(self, query: str) -> Sequence[ItemAlt]:
        return (self._create_single_item_single_alt(query),)

    def _create_single_item_single_alt(self, query: str) -> ItemAlt:
        return BaseItemAlt(execute_text, lambda: self._run(query=query))

    def _run(self, query: str) -> None:
        raise NotImplementedError()

    def to_config(self) -> dict[str, Any]:
        return {
            "type": self.action_type.id,
            "title": self.title,
            "description": self._description,
            "pattern": self._pattern,
            **self._config,
        }


class BaseActionRegistry(kvix.ActionRegistry):
    def __init__(self, stor: Stor):
        self.stor: Stor = stor

    def load(self):
        self.stor.load()
        self._actions: list[Action] = []
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
        if not isinstance(value, dict):
            raise RuntimeError("dict expected, got " + type(value))
        value = cast(dict[Any, Any], value)
        if "type" not in value:
            raise RuntimeError('"type" expected')
        type_id = value["type"]
        if not isinstance(type_id, str):
            raise RuntimeError('"type" expected to be str, got ' + type(type_id))
        if type_id not in self.action_types:
            raise RuntimeError("uknown action type id=" + type_id)
        action_type: ActionType = self.action_types[type_id]
        return action_type.action_from_config(value)

    def search(self, query: str) -> Sequence[kvix.Item]:
        result: list[kvix.Item] = []
        for action in self.actions:
            for item in action.search(query):
                result.append(item)
        return result


class BasePlugin(kvix.Plugin):
    def __init__(self, context: kvix.Context):
        self.context = context

    def get_action_types(self) -> Sequence[ActionType]:
        self._single_action_type = self._create_single_action_type()
        return [self._single_action_type]

    def _create_single_action_type(self) -> ActionType:
        raise NotImplementedError()

    def get_actions(self) -> Sequence[Action]:
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

    def get_action_types(self) -> Sequence[ActionType]:
        return self._wrap.get_action_types() if self._wrap else []

    def get_actions(self) -> Sequence[Action]:
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
