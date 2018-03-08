#!/usr/bin/env python3
#-*- coding: utf-8 -*-

#=======================================================================================
# Imports
#=======================================================================================

from lib.base import *
from lib.configutils import ConfigSetup, Config, ConfigOptionUnassignedError
from lib.localization import Lang

#=======================================================================================
# Localization
#=======================================================================================

_ = Lang( "capplib", autodetect=False).gettext

#=======================================================================================
# Library
#=======================================================================================

#==========================================================
# Exceptions
#==========================================================

class CappLibError(ErrorWithCodes):
	codes = ErrorCodes()
	codes.CONFIG_SETUP_INVALID = 0

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
	
	def __init__(self, configSetup, flavor=Config()):
		# Initialize config.
		self.configSetup = configSetup
		try:
			# [FLAVOR CONFIG DEBUG]: flavor has all the values.
			print("[DEBUG][capplib.py.BaseCapp] flavor (as given)", flavor)
			self.config = self.configSetup.getConfig(config=flavor)
			print("[DEBUG][capplib.py.BaseCapp] self.config", self.config)
			# [FLAVOR CONFIG DEBUG]: self.config has all the values.
			# [FLAVOR CONFIG DEBUG]: But it still triggers the below error.
		except ConfigOptionUnassignedError as error:
			raise CappLibError(\
				_("Capplib initialized with invalid config setup.\nCapplib info:\n{info}",\
						formatDict={"info": self.configSetup.getSynopsis(short=True)}),\
					CappLibError.codes.CONFIG_SETUP_INVALID) from error
		# Initialize flavor.
		self.flavor = flavor
	