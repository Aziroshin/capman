#!/usr/bin/env python3
#-*- coding: utf-8 -*-

#=======================================================================================
# Imports
#=======================================================================================

import gettext

#=======================================================================================
# Library
#=======================================================================================

#==========================================================
class Local(object):
	
	
	"""Represents a translation based on gettext."""
	def __init__(self, domain, localeDir, language=None, autodetect=False):
		self.translation = None
		try:
			self.translation = gettext.translation(domain, localeDir)
			self.gettext = translation.gettext
		except FileNotFoundError:
			pass
		self.domain = domain
		self.localeDir = localeDir
		self.language = language

	def gettext(self, string):
		"""Wraps around gettext to provide additional features."""
		if self.translation is None:
			return string
		return self.gettext(string)