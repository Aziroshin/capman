#!/usr/bin/env python3
#-*- coding: utf-8 -*-

#=======================================================================================
# Imports
#=======================================================================================

from plugins.walletlibs.bitcoin import *

#=======================================================================================
# Library
#=======================================================================================

#==========================================================
class DashWallet(BitcoinWallet):
	
	#=============================
	"""Represents a Dash wallet."""
	#=============================
	
	def deleteBlockchainData(self):
		self.deleteDataFiles["blocks", "chainstate", "database", "mncache.dat", "peers.dat", "mnpayments.dat", "banlist.dat"]