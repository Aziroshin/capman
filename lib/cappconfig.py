#!/usr/bin/env python3
#-*- coding: utf-8 -*-

#=======================================================================================
# Imports
#=======================================================================================

from lib.configutils import *

#=======================================================================================
# Library
#=======================================================================================

#==========================================================
class DefaultsConfigSetup(ConfigSetup):
	
	#=============================
	"""'ConfigSetup' for general defaults for capman."""
	#=============================
	
	def __init__(self):
		super().__init__()
		self.addOption(ConfigOption(varName="cappConfigDirPath", configName="cappconfigdir", optionTypes=[ConfigOptionCanonicalizedFilePathType()], enforceAssignment=True))
		self.addOption(ConfigOption(varName="pluginDirPaths", configName="plugindirs", optionTypes=[ConfigOptionListType(), ConfigOptionCanonicalizedFilePathType()]))

#==========================================================
class Defaults(Namespace):
	
	#=============================
	"""Capp Manager default config."""
	#=============================

	def __init__(self):
		binDir = os.path.realpath(os.path.dirname(sys.argv[0]))
		config = DefaultsConfigSetup().getConfig(configFilePaths=[os.path.join(os.path.join(binDir, "config"), "cappman.conf")])
		self.cappConfigDirPath = config.cappConfigDirPath
		self.pluginDirPaths = config.pluginDirPaths

#==========================================================
class BasicCappConfigSetup(ConfigSetup):
	
	#=============================
	"""Basic capp information needed to decide which capp flavor we're dealing with, and other
	information that's universal across all flavors."""
	#=============================
	
	def __init__(self):
		super().__init__()
		self.addOption(ConfigOption(varName="cappFlavor", configName="cappflavor", category="main"))
		self.addOption(ConfigOption(varName="name", configName="name", category="main"))