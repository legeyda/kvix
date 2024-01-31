from kvix import Context
from kvix.plugin.impl import FromModules

from . import (
    add_action,
    base64decode,
    base64encode,
    calculator,
    edit_action,
    machinist,
    openurl,
    quit,
    settings,
    shell,
    websearch,
)


class Plugin(FromModules):
    def __init__(self, context: Context):
        FromModules.__init__(
            self,
            context,
            add_action,
            base64decode,
            base64encode,
            calculator,
            edit_action,
            machinist,
            openurl,
            quit,
            settings,
            shell,
            websearch,
        )
