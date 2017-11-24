#!/usr/bin/env python3
#-*- coding: utf-8 -*-

#=======================================================================================
# Imports
#=======================================================================================

import argparse
import configparser
from lib.base import *
from lib.cappconfig import *

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

#==========================================================
class Capps(object):
	
	#=============================
	"""A collection of all the capps we manage."""
	#=============================
	
	def __init__(self, cappConfigDirPath):
		self.cappConfigDirPath = cappConfigDirPath
	def getAll(self):
		allCapps = []
		print("[DEBUG][capps.py:Capps:getAll]", "called. Going to probe for conf file: ", self.cappConfigDirPath, os.listdir(self.cappConfigDirPath))
		for configFileName in os.listdir(self.cappConfigDirPath):
			configFilePath = os.path.join(self.cappConfigDirPath, configFileName)
			print("[DEBUG][capphandler.py:Capps:getAll]", "Conf file found.")
			print("[DEBUG][capphandler.py:Capps:getAll]", "configFilePath: ", configFilePath)
			if configFilePath.rpartition(".")[2] == "conf":
				print("[DEBUG][capphandler.py:Capps:getAll]", "Conf file name ends with .conf.")
				basicConfig = BasicCappConfigSetup().getConfig(configFilePaths=[configFilePath])
				print("[DEBUG][capphandler.py:Capps:getAll]", "basicConfig anatomy", basicConfig)
				cappFlavor = CappFlavor(basicConfig.cappFlavor)
				print("[DEBUG][capphandler.py:Capps:getAll]", "Name of the chosen capp:", basicConfig.name)
				print("[DEBUG][capphandler.py:Capps:getAll]", "CappFlavor chosen:", cappFlavor.name)