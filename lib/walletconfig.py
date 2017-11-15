#!/usr/bin/env python3
#-*- coding: utf-8 -*-

#=======================================================================================
# Imports
#=======================================================================================

from lib.base import *

#=======================================================================================
# Library
#=====================================================================================

#==========================================================
class BasicWalletConfigSetup(ConfigSetup):
	def __init__(self):
		super().__init__()
		self.addOption(ConfigOption(varName="walletFlavor", configName="walletflavor", category="main"))
		self.addOption(ConfigOption(varName="name", configName="name", category="main"))