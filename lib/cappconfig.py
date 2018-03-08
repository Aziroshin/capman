#!/usr/bin/env python3
#-*- coding: utf-8 -*-

#=======================================================================================
# Imports
#=======================================================================================

import sys
import os
from lib.configutils import *

#=======================================================================================
# Library
#=======================================================================================

#==========================================================
class DefaultsConfigSetup(ConfigSetup):
	
	#=============================
	"""'ConfigSetup' for general defaults for cappman."""
	#=============================
	
	def __init__(self):
		super().__init__()
		self.addOption(ConfigOption(varName="cappConfigDirPath", configName="cappconfigdir", optionTypes=[ConfigOptionCanonicalizedFilePathType()], enforceAssignment=True))
		self.addOption(\
			ConfigOption(varName="pluginDirPaths",\
			configName="plugindirs",\
			defaultValue="[\""+os.path.realpath(os.path.join(os.path.dirname(sys.argv[0]), "plugins")+"\"]"),\
			optionTypes=[ConfigOptionListType(merge=True),\
			ConfigOptionCanonicalizedFilePathType()]))

#==========================================================
class Defaults(Namespace):
	
	#=============================
	"""Capp Manager default config."""
	#=============================

	def __init__(self):
		super().__init__()
		# Hard coded defaults & other vital values.
		self.execPath = sys.argv[0]
		self.execDirPath = os.path.realpath(os.path.dirname(self.execPath))
		self.distConfigDirPath = os.path.join(self.execDirPath, "config")
		self.distPluginDirPath = os.path.join(self.execDirPath, "plugins")
		self.distCappmanConfigPath = os.path.join(self.distConfigDirPath, "cappman.conf")
		self.pluginDirNames = {\
			"cappExtensions": "cappextensions",\
			"callFlavors": "cappflavors",\
			"cappLibs": "capplibs",\
			"languages": "languages"}
		# Configured defaults.
		config = DefaultsConfigSetup().getConfig(configFilePaths=[self.distCappmanConfigPath])
		self.cappConfigDirPath = config.cappConfigDirPath
		#print("[DEBUG] [cappconfig.py.Defaults]"[self.distPluginDirPath]+config.pluginDirPaths)
		self.pluginDirPaths = [self.distPluginDirPath]+config.pluginDirPaths

#==========================================================
class BasicCappConfigSetup(ConfigSetup):
	
	#=============================
	"""Basic capp information needed to decide which capp flavor we're dealing with, and other
	information that's universal across all flavors."""
	#=============================
	
	def __init__(self, configFilePaths=[]):
		super().__init__(configFilePaths)
		self.addOption(ConfigOption(varName="cappFlavorName", configName="cappflavor", category="main", enforceAssignment=True))
		self.addOption(ConfigOption(varName="name", configName="name", category="main", enforceAssignment=True))

#==========================================================
class BasicFlavorConfigSetup(ConfigSetup):
	
	def __init__(self):
		super().__init__()
		self.addOption(ConfigOption(varName="cappLibName", configName="capplib", category="main", enforceAssignment=True))