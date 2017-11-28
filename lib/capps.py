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

raise Exception("Continue developing here.")
"""So, we need to do this:
ConfigSetup needs to take initialization parameters such as directories in its constructor. The getConfig
method needs to be altered subsequently to allow either for overriding these values or complementing them.
That way, we don't have to worry about initialization and we can simply pass a ConfigSetup object
to the plugins, being compatible for all sorts of potential initialization procedures, like databases.

As a result, we will be able to do something like the following:
CappFlavorPlugin.fl"""

#==========================================================
class Capps(object):
	
	#=============================
	"""A collection of all the capps we manage."""
	#=============================
	
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
				# Get the capp plugin.
				cappPlugin = CappLibPlugin(basicConfig.pluginDirPaths, basicConfig.name)
				# Get the flavor plugin.
				cappFlavorPlugin = CappFlavorPlugin(\
					basicConfig.pluginDirs,\
					basicConfig.CappFlavor,\
					cappPlugin.module.FlavorConfigSetup)
				# Get the capp handler.
				cappPlugin.module.Capp(\
					configSetup=cappPlugin.module.CappConfigSetup(\
						configFilePaths=basicConfig.cappConfigDirPath),\
					flavor=flavor)
				
				#print("[DEBUG][capphandler.py:Capps:getAll]", "Name of the chosen capp:", basicConfig.name)
				#print("[DEBUG][capphandler.py:Capps:getAll]", "CappFlavor chosen:", cappFlavor.name)