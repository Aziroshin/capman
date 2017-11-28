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

#=======================================================================================
# Localization
#=======================================================================================

_ = Lang( "cappbaselib", autodetect=False).gettext

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
	pass

#==========================================================
class ConfigPluginError(PluginError):
	
	#=============================
	"""Errors related to the 'ConfigPlugin' class."""
	#=============================
	
	# Error codes.
	MISSING_CONFIG = 0
	MISSING_CONFIGSETUP = 1
	
	def __init__(self, message, errno):
		super().__init__(self, message, errno)

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
	
	pass

#==========================================================
class PythonLibPlugin(Plugin):
	
	#=============================
	# """Base class for plugins consisting of python libraries to be integrated and used with the runtime environment."""
	#=============================
	
	def __init__(self, dirPathToLoad, name, packageName=""):
		self.dirPathToLoad = dirPathToLoad
		self.name = name
		self.packageName = packageName
		if self.packageName:
			self.moduleNameToLoad = self.packageName+"."+self.name
		else:
			self.moduleNameToLoad = self.name
	
	def load(self):
		"""Loads the plugin with or without package (according to parameters) into sys.path and imports it."""
		if not self.dirPathToLoad in sys.path:
			sys.path.insert(1, self.dirPathToLoad)
		importlib.import_module(self.moduleNameToLoad)

#==========================================================
class ConfigPlugin(Plugin):
	
	#=============================
	"""A data based plugin that doesn't add any logic, but data through a configuration object."""
	#=============================
	
	def __init__(self, configFilePath):
		self.configFilePath = configFilePath
		self._config
		self._configSetup
		self.pluginInfoString = "ConfigPlugin of the {pluginType} plugin type from {filePath}"\
			.format(pluginType=self.__class__, filePath=self.configFilePath)

	@property
	def config(self):
		"""Return the config or raise an error if there is none."""
		if self._config is None:
			raise ConfigPluginError(_("Attempted to access the Config of {pluginInfoString}, but no config has not been initialized yet.").\
				format(pluginInfoString=self.pluginInfoString), ConfigPluginError.MISSING_CONFIG)
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
			raise ConfigPluginError(_("Attempted to access the ConfigSetup a {pluginInfoString}, but no ConfigSetup has been configured for it yet.")\
				.format(pluginInfoString=self.pluginInfoString), ConfigPluginError.MISSING_CONFIGSETUP)
		else:
			return self._configSetup
	
	@configSetup.setter
	def configSetup(self, configSetupObject):
		"""Set the ConfigSetup which this plugin is supposed to represent."""
		self._configSetup = configSetupObject
	
	def load(self):
		"""Load the config from the specified file according to the specified ConfigSetup.
		This must be called before the plugin is to be considered usable."""
		self.config = self.configSetup.getConfig(self.configFilePath)

#==========================================================
class CappLibPlugin(PythonLibPlugin):
	
	#=============================
	"""Represents a Capp library plugin.
	These libraries are the heart of cappman and contain the functionality needed to manage
	the crypto application they've been written for."""
	#=============================
	
	def __init__(self, dirPathToLoad, name):
		super().__init__(self, dirPathToLoad, name, packageName="capplibs")

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
	
	def __init__(self, flavorPluginDirPaths, name, configSetup):
		super().__init__(self, flavorFilePath)
		self.flavorFilePath = flavorFilePath
		self.configSetup = configSetup
		self.filePath = None
		for dirPath in flavorPluginDirPaths:
			if self.name in os.listdir(dirPath):
				self.filePath = os.path.join(dirPath, self.name)
				break
		if self.filePath is None:
			raise FlavorPluginNotFoundError("Flavor plugin not found.") # Needs proper error message.
		self.config = self.configSetup.getConfig(FOUNDPATH) #NOTE: Pseudocode.
	
	@property
	def flavor(self):
		return self.config

#==========================================================
class LanguagePlugin(Plugin):
	"""Represents gettext based translation files."""
	#NOTE: Low development priority.
	pass