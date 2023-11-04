from kvix import Context
from kvix.plugin.impl import FromModules
from kvix.plugin import builtin, discovery


class Plugin(FromModules):
    def __init__(self, context: Context):
        FromModules.__init__(self, context, builtin, discovery)
