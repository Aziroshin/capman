raise Exception("Continue developing here.")

#==========================================================
class Plugins(object):
	
	#=============================
	"""Plugin handler which allows the finding and loading of plugins from various locations."""
	#=============================
	
	def loadPlugin(self, name):
		pass
	
#==========================================================
class Plugin(object):
	pass

class PythonLibPlugin(Plugin):
	def __init__(self, dirPathToLoad, name, packageName=""):
		self.dirPathToLoad = dirPathToLoad
		self.name = name
		self.packageName = packageName
		if self.packageName:
			self.moduleNameToLoad = self.packageName+"."+self.name
		else:
			self.moduleNameToLoad = self.name
	
	def load(self):
		if not self.dirPathToLoad in sys.path:
			sys.path.insert(1, self.dirPathToLoad)
		importlib.import_module(self.moduleNameToLoad)

class ConfigPlugin(Plugin):
	pass

class CappLibPlugin(PythonLibPlugin):
	def __init__(self, dirPathToLoad, name):
		super().__init__(self, dirPathToLoad, name, packageName="capplibs")

class CappExtensionPlugin(PythonLibPlugin):
	pass

class CappFlavorPlugin(ConfigPlugin):
	pass

class LanguagePlugin(Plugin):
	pass