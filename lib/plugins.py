#!/usr/bin/env python3
#-*- coding: utf-8 -*-

#=======================================================================================
# Imports
#=======================================================================================
import importlib
import sys
import os
import configparser 
from lib.localization import Lang
from lib.base import *
from lib.configutils import *

#=======================================================================================
# Localization
#=======================================================================================

_ = Lang( "plugins", autodetect=False).gettext

#=======================================================================================
# Library
#=======================================================================================

#==========================================================
# Exceptions
#==========================================================

#==========================================================
class PluginError(ErrorWithCodes):
	
	#=============================
	# """Base class for plugin related Exceptions."""
	#=============================
	
	# Error codes.
	NO_VALID_DIRS = 0

class PythonLibPluginError(ErrorWithCodes):
	
	#=============================
	"""Errors related to the 'PythonLibPugin' class."""
	#=============================
	
	# Error codes.
	MODULE_NOT_LOADED = 0

#==========================================================
class ConfigPluginError(ErrorWithCodes):
	
	#=============================
	"""Errors related to the 'ConfigPlugin' class."""
	#=============================
	
	# Error codes.
	MISSING_CONFIG = 0
	MISSING_CONFIGSETUP = 1

#==========================================================
# Plugin Classes
#==========================================================

#==========================================================
class Plugins(object):
	
	#=============================
	"""Plugin handler which allows the finding and loading of plugins from various locations."""
	#=============================
	#NOTE: Might go away.
	
	def loadPlugin(self, name):
		pass
	
#==========================================================
class Plugin(object):
	
	#=============================
	"""Base class for various plugin classes."""
	#=============================
	
	def __init__(self, dirPaths):
		self.dirPaths = dirPaths
	
	@property
	def existingDirPaths(self):
		"""Return a list with only those dir paths in 'self.dirPaths' that actually exist."""
		existingPaths = []
		for dirPath in self.dirPaths:
			if os.path.exists(dirPath):
				existingPaths.append(dirPath)
		if len(existingPaths) is 0:
			raise PluginError(_("No existing directory paths are configured for this plugin. The following paths are configured, but don't exist: {dirPaths}", formatDict={"dirPaths": self.dirPaths}), PluginError.NO_VALID_DIRS)
		return existingPaths

#==========================================================
class PythonLibPlugin(Plugin):
	
	#=============================
	# """Base class for plugins consisting of python libraries to be integrated and used with the runtime environment."""
	#=============================
	
	def __init__(self, dirPaths, name, packageName=None):
		super().__init__(dirPaths=dirPaths)
		self.prefix = "capplib"
		self.name = name
		self.moduleName = "{prefix}_{name}".format(prefix=self.prefix, name=self.name)
		self.packageName = packageName
	
	@property
	def module(self):
		try:
			return self._module
		except AttributeError:
			raise PythonLibPluginError(_("Attempted to access the python module of a PythonLibPlugin named {name}, but none was loaded yet.",\
				formatDict={"name": self.name}), PythonLibPluginError.MODULE_NOT_LOADED)
	
	@module.setter
	def module(self, moduleToSet):
		self._module = moduleToSet
	
	
	
	def load(self):
		"""Loads the plugin with or without package (according to parameters) into sys.path and imports it."""
		for dirPath in self.existingDirPaths:
			if not dirPath in sys.path:
				sys.path.insert(1, dirPath)
				#print("[DEBUG plugins.py.PythonLibPlugin.load] dirPath: ", dirPath, "sys.path", sys.path)
		
		self.module = __import__(name=self.moduleName, globals=globals(), locals=locals(), fromlist=[], level=0)
		#print("[DEBUG] [plugins.py.PythonLibPlugin.load] Module:", self.module, "|| Module name:", self.name)

#==========================================================
class ConfigPlugin(Plugin):
	
	#=============================
	"""A data based plugin that doesn't add any logic, but data through a configuration object.
	The ConfigSetup can be specfied at a later time, but has to be specified before 'self.load'
	is called, by assigning 'self.configSetup' with a 'ConfigSetup' object."""
	#=============================
	
	def __init__(self, dirPaths, name, configSetup=None):
		super().__init__(dirPaths=dirPaths)
		self.name = name
		self.configSetup = configSetup
		self._config = None
		self._configSetup = None
		self.pluginInfoString = _("ConfigPlugin of the {pluginType} and the name \"{name}\"",\
			formatDict={"pluginType": self.__class__, "name": self.name})

	@property
	def config(self):
		"""Return the config or raise an error if there is none."""
		if self._config is None:
			raise ConfigPluginError(_("Attempted to access the Config of {pluginInfoString}, but no config has not been initialized yet.",\
				formatDict={"pluginInfoString": self.pluginInfoString}), ConfigPluginError.MISSING_CONFIG)
		else:
			return self._config
		
	@config.setter
	def config(self, configObject):
		"""Set the config."""
		self._config = configObject
		
	@property
	def configSetup(self):
		"""Return the configured ConfigSetup or raise an error if none is configured."""
		if self._configSetup is None:
			raise ConfigPluginError(_("Attempted to access the ConfigSetup a {pluginInfoString}, but no ConfigSetup has been configured for it yet.",\
				formatDict={"pluginInfoString": self.pluginInfoString}), ConfigPluginError.MISSING_CONFIGSETUP)
		else:
			return self._configSetup
		
	@configSetup.setter
	def configSetup(self, configSetupObject):
		"""Set the ConfigSetup which this plugin is supposed to represent."""
		self._configSetup = configSetupObject
	
	def load(self, config=Config()):
		"""Load the config from the first directory in the directory list containing a file with the specified name according to the specified ConfigSetup.
		This must be called before the plugin is to be considered usable."""
		for dirPath in self.existingDirPaths:
			if self.name in os.listdir(dirPath):
				self.config = self.configSetup.getConfig(configFilePaths=[os.path.join(dirPath, self.name)], config=config)
				break
			raise ConfigPluginError(_("ConfigPlugin of the {configPluginType} type with the name \"{name}\" not found in any of the specified directories: {dirPathListing}",\
				formatDict={"configPluginType": self.__class__, "name": self.name, "dirPathListing": self.dirPaths}), 0)

#==========================================================
class CappLibPlugin(PythonLibPlugin):
	
	#=============================
	"""Represents a Capp library plugin.
	These libraries are the heart of cappman and contain the functionality needed to manage
	the crypto application they've been written for."""
	#=============================
	
	def __init__(self, dirPaths, name):
		super().__init__(dirPaths, name, packageName="capplibs")

#==========================================================
class CappExtensionPlugin(PythonLibPlugin):
	
	#=============================
	"""This type of plugin represents polymorphous mix-ins for capplibs."""
	#=============================
	pass

#==========================================================
class CappFlavorPlugin(ConfigPlugin):
	
	#=============================
	"""A flavor represents a crypto application fork in the form of what's essentially a capplib-plugin config."""
	#=============================
	
	def __init__(self, dirPaths, name):
		flavorDirPaths = []
		for dirPath in dirPaths:
			flavorDirPaths.append(os.path.join(dirPath, "cappflavors"))
		super().__init__(flavorDirPaths, name, configSetup=None)
	
	def loadInitial(self, configSetup):
		"""Loads the plugin with an initial ConfigSetup."""
		self.configSetup = configSetup
		self.load()
		
	def loadMore(self, configSetup):
		"""Subsequently loads the plugin with previous load states in mind."""
		self.configSetup = configSetup
		self.load(self.config)

	@property
	def flavor(self):
		return self.config

#==========================================================
class LanguagePlugin(Plugin):
	"""Represents gettext based translation files."""
	#NOTE: Low development priority.
	pass