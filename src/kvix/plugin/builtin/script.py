from kvix import ActionType, Context
from kvix.l10n import _
import subprocess
import shlex
from typing import Any
from kvix.util import apply_template
from typing import Sequence, Iterator
import os
from kvix.impl import (
    BaseAction,
    BaseActionType,
    BasePlugin,
    BaseItem,
    BaseItemAlt,
    execute_text,
)
from kvix.util import get_data_dir, compact_home

from kvix import ActionType, Context, Item, Action
from pathlib import Path
from kvix.util import query_match

action_type_title_text = _("Run Script").setup(ru_RU="Запуск скрипта")
path_config_text = _("Script or script directory path").setup(ru_RU="Путь к скрипту или к папке")
default_action_title_text = action_type_title_text
default_action_title_description = " ".join(default_action_title_text.values())
run_script_text = _("Run script {path}").setup(ru_RU="Выполнить скрипт {path}")


def get_path_type(path: str) -> str:
    """Return type of path: 'file', 'dir', 'other', or 'missing'.

    Expands user (~) and returns a simple classification useful for
    deciding whether a candidate path is a plain file or a directory.
    """
    if not path:
        return "missing"
    p = os.path.expanduser(path)
    p = os.path.abspath(p)
    if not os.path.exists(p):
        return "missing"
    if os.path.isfile(p):
        return "file"
    if os.path.isdir(p):
        return "dir"
    return "other"


def scan_dir(path: str) -> Iterator[str]:
    if not path:
        return
    p = os.path.expanduser(path)
    p = os.path.abspath(p)
    if not os.path.exists(p):
        return
    if not os.path.isdir(p):
        return
    for item in os.scandir(Path(path)):
        if item.is_file() and os.access(item, os.X_OK):
            yield item.path


class ScriptAction(BaseAction):
    def _post_init(self):
        try:
            return super()._post_init()
        finally:
            self._config.setdefault("path", str(get_data_dir().joinpath("scripts")))

    def get_env(self, query: str = "") -> dict[str, str]:
        env = os.environ.copy()
        env["KVIX_CLIPBOARD"] = ""
        clipboard_bytes = b""
        try:
            clipboard_bytes = self.action_type.context.ui.paste_from_clipboard()
            env["KVIX_CLIPBOARD"] = str(clipboard_bytes.decode("UTF-8"))
        except Exception as e:
            print("error pasting from clipboard", e)
        env["KVIX_QUERY"] = query or ""
        return env

    def search(self, query: str) -> Sequence[Item]:
        if not query:
            return []
        if 4 > len(query):
            return []
        # check whether query is a path and ensure it's a plain file (not a directory)

        path = self._config["path"]
        if not path:
            return []

        all_scripts: list[str]
        match get_path_type(path):
            case "file":
                all_scripts = [path]
            case "dir":
                all_scripts = [p for p in scan_dir(path)]
            case _:
                return []

        if not self._match(query) and not query_match(query, str(path)):
            all_scripts = [i for i in all_scripts if query_match(query, str(i))]

        return [self._create_item(script, query) for script in all_scripts]

    def _create_item(self, path: str, query: str) -> Item:

        return BaseItem(
            "▶ " + os.path.basename(path),
            [
                BaseItemAlt(
                    str(run_script_text).format(path=compact_home(path)),
                    lambda: self.run_script(path, query),
                )
            ],
        )

    def run_script(self, path: str, query: str) -> None:
        try:
            subprocess.Popen(
                [path],
                env=self.get_env(query),
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
        except Exception as e:
            print("failed to start script", path, e)


class Plugin(BasePlugin):
    def _create_single_action_type(self) -> ActionType:
        return BaseActionType(
            self.context,
            "kvix.plugin.builtin.script",
            str(action_type_title_text),
            ScriptAction,
            {
                "path": path_config_text,
            },
        )

    def get_actions(self) -> Sequence[Action]:
        return [
            ScriptAction(
                self._single_action_type,
                str(default_action_title_text),
                str(default_action_title_description),
            )
        ]
