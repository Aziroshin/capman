#!/usr/bin/env python3
#-*- coding: utf-8 -*-

#=======================================================================================
# Imports
#=======================================================================================

import argparse
import configparser
from lib.base import *
from lib.cappconfig import *
from lib.plugins import *
from lib.configutils import PluginDirPaths

#=======================================================================================
# Configuration
#=======================================================================================

defaults = Defaults()

#=======================================================================================
# Library
#=======================================================================================

#==========================================================
# Exceptions
#==========================================================

#==========================================================
class CappLibUnknown(Exception):
	def __init__(self, message):
		super().__init__(message)

#==========================================================
# Capp Classes
#==========================================================

#==========================================================
class CappLib(object):
	def __init__(self, name):
		self.name = name
		
#==========================================================
class CappFlavor(object):
	def __init__(self, name):
		self.name = name

"""So, we need to do this:
ConfigSetup needs to take initialization parameters such as directories in its constructor. The getConfig
method needs to be altered subsequently to allow either for overriding these values or complementing them.
That way, we don't have to worry about initialization and we can simply pass a ConfigSetup object
to the plugins, being compatible for all sorts of potential initialization procedures, like databases."""

#==========================================================
class Capps(object):
	
	#=============================
	"""A collection of all the capps we manage."""
	#=============================
	
	# Bugs:
	# - basicConfig has the plugin dirs, and it has them without the hard coded default.
	#   It shouldn't have them in the first place.
	#   Will move on for now by getting the data from default, as it's supposed to be.
	# Issues:
	# - [Aziroshin] I really don't like that the capp configs need to specify the capplib.
	#   I should probably load the flavor file just to get the capplib name and then pass
	#   it to the capp lib for proper loading.
	
	def __init__(self, cappConfigDirPath):
		self.cappConfigDirPath = cappConfigDirPath
	def getAll(self):
		allCapps = []
		#print("[DEBUG][capps.py:Capps:getAll]", "called. Going to probe for conf file: ", self.cappConfigDirPath, os.listdir(self.cappConfigDirPath))
		for configFileName in os.listdir(self.cappConfigDirPath):
			configFilePath = os.path.join(self.cappConfigDirPath, configFileName)
			#print("[DEBUG][capphandler.py:Capps:getAll]", "Conf file found.")
			#print("[DEBUG][capphandler.py:Capps:getAll]", "configFilePath: ", configFilePath)
			if configFilePath.rpartition(".")[2] == "conf":
				#print("[DEBUG][capphandler.py:Capps:getAll]", "Conf file name ends with .conf.")
				basicConfig = BasicCappConfigSetup().getConfig(configFilePaths=[configFilePath])
				#print("[DEBUG][capphandler.py:Capps:getAll]", "basicConfig anatomy", basicConfig)
				# Get the basic version of the flavor plugin bootstrapped, just enough to load the capplib.
				cappFlavorPlugin = CappFlavorPlugin(defaults.pluginDirPaths, basicConfig.cappFlavorName)
				cappFlavorPlugin.loadInitial(BasicFlavorConfigSetup())
				# Get the capp plugin.
				#print("[DEBUG] [capps.py.Capps.getAll]", basicConfig.__dict__, configFilePath)
				cappLibPlugin = CappLibPlugin(PluginDirPaths(\
					defaults.pluginDirPaths, defaults.pluginDirNames).cappLibs,\
					cappFlavorPlugin.flavor.cappLibName)
				cappLibPlugin.load()
				# Get the flavor plugin in its full configuration.
				cappFlavorPlugin.loadMore(cappLibPlugin.module.FlavorConfigSetup())
				print("[DEBUG][capps.py.Capps.getAll] flavor config (full):", cappFlavorPlugin.flavor)
				# Get the capp handler.
				cappLibPlugin.module.Capp(\
					configSetup=cappLibPlugin.module.CappConfigSetup(\
						configFilePaths=[basicConfig.cappConfigDirPath]),\
					flavor=cappFlavorPlugin.flavor)
				
				#print("[DEBUG][capphandler.py:Capps:getAll]", "Name of the chosen capp:", basicConfig.name)
				#print("[DEBUG][capphandler.py:Capps:getAll]", "CappFlavor chosen:", cappFlavor.name)