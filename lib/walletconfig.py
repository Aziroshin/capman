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
		self.addOption(Option(varName="walletFlavor", confName="walletflavor", category="main"))
		self.addOption(Option(varName="name", confName="name", category="main"))