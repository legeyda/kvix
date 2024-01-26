import importlib.util
import os
import sys
from pathlib import Path
from types import ModuleType
from typing import Sequence

from kvix.util import get_data_dir

from kvix import Context
from kvix.l10n import _
from kvix.plugin.impl import FromModules

plugin_dir_config_item_text = _("Plugin directory").setup(
    ru_RU="Папка для плагинов", de_DE="Plugin Ordner"
)


def scan_python_packages(root_dir: Path | str):
    if not Path(root_dir).is_dir():
        return
    for item in os.scandir(Path(root_dir)):
        if item.is_file() and item.name.endswith(".py"):
            yield (item.name, item.path)


def load_module_from_path(name: str, path: Path | str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if not spec:
        raise RuntimeError("unloadable module")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def load_plugin_modules(root_dir: Path | str) -> Sequence[ModuleType]:
    result = []
    for name, path in scan_python_packages(root_dir):
        try:
            result.append(load_module_from_path(__name__ + "." + Path(name).stem, path))
        except Exception as e:
            print(e)
    return result


def get_plugin_dir(context: Context):
    conf_item = context.conf.item("plugin_dir")
    conf_item.setup(
        title=str(plugin_dir_config_item_text),
        default=str(get_data_dir().joinpath("plugins")),
    )
    result = Path(conf_item.read())

    if not os.path.exists(result):
        os.makedirs(result)
    return result


class Plugin(FromModules):
    def __init__(self, context: Context):
        FromModules.__init__(self, context, *load_plugin_modules(get_plugin_dir(context)))
