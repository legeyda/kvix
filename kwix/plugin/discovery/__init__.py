from kwix import Context
from kwix.plugin.impl import FromModules

class Plugin(FromModules):
	def __init__(self, context: Context):
		FromModules.__init__(self, context)