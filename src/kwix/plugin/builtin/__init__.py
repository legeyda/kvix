from kwix import Context
from kwix.plugin.impl import FromModules
import sys, pkgutil
from importlib import import_module
class Plugin(FromModules):
	def __init__(self, context: Context):
		FromModules.__init__(self, context, *[import_module(__name__ + '.' + m.name) for m in pkgutil.iter_modules(sys.modules[__name__].__path__)])