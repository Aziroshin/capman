#!/usr/bin/env python3
#-*- coding: utf-8 -*-

#=======================================================================================
# Imports
#=======================================================================================

from lib.base import *
from lib.configutils import ConfigSetup

#=======================================================================================
# Library
#=======================================================================================

#==========================================================
class BaseFlavorConfigSetup(object):
	pass

#==========================================================
class BaseCappConfigSetup(object):
	pass

#==========================================================
class BaseCapp(object):
	
	#=============================
	# """Base class for capplibs, which takes care of basic initializations universal to all capplibs."""
	#=============================
	
	def __init__(self, config, flavor):
		# Initialize config.
		self.configSetup = configSetup
		self.config = self.configSetup.getConfig()
		# Initialize flavor.
		self.flavor = flavor
		self.flavor.load()
	