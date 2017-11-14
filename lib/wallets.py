#!/usr/bin/env python3
#-*- coding: utf-8 -*-

#=======================================================================================
# Imports
#=======================================================================================

import argparse
import configparser
from lib.base import *
from lib.walletconfig import *

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
class WalletLibUnknown(Exception):
	def __init__(self, message):
		super().__init__(message)

#==========================================================
# Wallet Classes
#==========================================================

#==========================================================
class WalletLib(object):
	def __init__(self, name):
		self.name = name
		
#==========================================================
class WalletFlavor(object):
	def __init__(self):
		self.name = name

#==========================================================
class Wallets(object):
	
	#=============================
	"""A collection of all the wallets we manage."""
	#=============================
	
	def __init__(self, walletConfigDirPath):
		self.walletConfigDirPath = walletConfigDirPath
	def getAll(self):
		print("[DEBUG][wallethandler.py:Wallets:getAll]", "called. Going to probe for conf file: ", self.walletConfigDirPath, os.listdir(self.walletConfigDirPath))
		for configFilePath in os.listdir(self.walletConfigDirPath):
			print("[DEBUG][wallethandler.py:Wallets:getAll]", "Conf file found.")
			if configFilePath.rpartition["."][2] == "conf":
				print("[DEBUG][wallethandler.py:Wallets:getAll]", "Conf file name ends with .conf.")
				basicConfig = BasicWalletConfigSetup().getConfig(configFilePaths=[configFilePath])
				walletLib = WalletLib(basicConfig.walletlib)
				print("[DEBUG][wallethandler.py:Wallets:getAll]", "WalletLib chosen:", walletLib, ".")