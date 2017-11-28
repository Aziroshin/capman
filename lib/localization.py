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
class Lang(object):
	
	# Defaults
	
	# This default may be messy, but it's still preferable over having to define
	# and maintain it in all those multiples of files this class will be used in
	# before proper language plugin procedures are available to the runtime environment.
	defaultLocaleDirPath = os.path.realpath(\
	os.path.join(os.path.join(\
		os.path.join(os.path.dirname(sys.argv[0]), "plugins"), "languages")))
	
	#=============================
	"""Represents a translation based on gettext."""
	#=============================
	
	def __init__(self, domain, localeDirPath=defaultLocaleDirPath, language=None, autodetect=False):
		self.translation = None
		try:
			self.translation = gettext.translation(domain, localeDirPath)
			self.gettext = translation.gettext
		except FileNotFoundError:
			pass
		self.domain = domain
		self.localeDirPath = localeDirPath
		self.language = language

	def gettext(self, string):
		"""Wraps around gettext to provide additional features."""
		if self.translation is None:
			return string
		return self.gettext(string)