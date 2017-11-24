#!/usr/bin/env python3
#-*- coding: utf-8 -*-

#=======================================================================================
# Imports
#=======================================================================================

from lib.base import *

#=======================================================================================
# Library
#=======================================================================================

#==========================================================
# Masternode Classes
#==========================================================

class Masternode(object):
	
	#=============================
	"""Represents the generic concept of a masternode for further subclassing by capplibs.
	"""
	# Currently, this is planned to serve as a basis to provide basic masternode sharing logic
	# to all masternode implemenations further down the road.
	#=============================
	
	def __init__(self, shared=False):
		self.shared = shared

#=======================================================================================
# Dev Notes
#=======================================================================================
""" [Aziroshin] I'm currently playing with the idea of making this a "cappextension", 
which would make it subclassable as a "mixin" in a case of multiple inheritance for capplibs.
In any case, making this some sort of plugin or otherise distinct feature from capp libs
would make it so capplibs would have to wait with calling '.getConfig' until all plugins
added their 'ConfigOption' objects to the configuration."""