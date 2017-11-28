#!/usr/bin/env python3
#-*- coding: utf-8 -*-

#=======================================================================================
# Imports
#=======================================================================================

import os
import sys
import argparse
import importlib
from subprocess import Popen, PIPE
from lib.localization import Lang

#=======================================================================================
# Localization
#=======================================================================================

_ = Lang( "cappbaselib", autodetect=False).gettext

#=======================================================================================
# Library
#=======================================================================================

#==========================================================
# Exceptions
#==========================================================

#==========================================================
class Error(Exception):
	#TODO: Implement logging once there's logging functionality.
	def __init__(self, message):
		super().__init__(message)

#==========================================================
class ErrorWithCodes(Error):
	
	#=============================
	"""Error with an error code for the 'errno' constructor parameter.
	The possible error numbers are to be configured as class variables of the
	appropriate subclass. Upon raising the error, one of these constants is
	supposed to be passed to 'errno'. During error handling, checks are
	supposed to use these constants as well. Never use the actual integer
	value anywhere except when defining the class variable referencing it.
	The convention is to use all upper case variable names for these."""
	#=============================
	
	def __init__(self, message, errno):
		super().__init__(message)
		self.errno = errno

#==========================================================
class ConfigFileNotFound(Error):
	pass

#==========================================================
class ConfigOptionUnassignedError(Error):
	pass

#==========================================================
# Base Classes
#==========================================================

#==========================================================
class Namespace (argparse.Namespace):
	
	#=============================
	"""Pure namespace class.
	Basically serves as a dot-notation oriented dict.
	In its current implementation, this is a simple subclass of 'argparse.Namespace'"""
	#=============================

	pass

#==========================================================
class Singleton(type):

	#=============================
	# """This class will always return the same instance, regardless of how many times it's called."""
	#=============================
	#NOTE: Currently unused. Might get deprecated in the future.

	def __init__(singletonClass, className, parentClasses, classDict):
		singletonClass.singletonObject = None
	def __call__(self, *args, **kwargs):
		if self.singletonObject is None:
			self.singletonObject = type.__call__(self, *args, **kwargs)
		return self.singletonObject

#==========================================================
class Unassigned(object, metaclass=Singleton):
	
	#=============================
	"""Anything of this type signifies a vanilla value that's supposed to be assigned at some point.
	This allows for exception checks to see whether a value is unassigned even though it ought not to be.
	
	Objects of this class will return 'False' to allow for easy checking.
	
	That job could be done by 'None', however, that also doubles for other purposes and might not be
	explicit enough in some situations, such as when parameters are assigned 'None' by default and may
	remain so to denote that the user of the software wishes there to be no assignment where that
	is applicable. For cases where other code down the line may wish to change that expectation
	on an optional basis, it is better to pass an object of this here type as the initial value instead
	of 'None'."""
	#=============================

	#NOTE: This is currently unused and might get deprecated in the future.
	
	def __bool__(self):
		return False

#==========================================================
class FancyErrorMessage(object):

	#=============================
	# """Provides error messages that are a bit better formatted and visible for the end user."""
	#=============================

	def __init__(self, message, title=""):
		decorTop = "===== [ERROR]{title}".format(title=title)
		decorBottom = "===== [ERROR]"
		self.string = "{eol}{decorTop}{message}{eol}{decorBottom}"\
			.format(eol=os.linesep, decorTop=decorTop, message=message, decorBottom=decorBottom)
		__repr__ = self.string

#==========================================================
class File(object):
	
	#=============================
	"""Basic file wrapper.
	Abstracts away basic operations such as read, write, etc."""
	#TODO: Make file operations safer and failures more verbose with some checks & exceptions.
	#=============================
	
	def __init__(self, path, make=False):
		self.path = path
		if not os.path.exists(self.path) and make:
			self.make()

	@property
	def lastModified(self):
		return int(os.path.getmtime(self.path))

	@property
	def secondsSinceLastModification(self):
		return int(time.time()) - int(self.lastModified)

	@property
	def exists(self):
		return os.path.exists(self.path)

	def write(self, data):
		with open(self.path, "w") as fileHandler:
			fileHandler.write(data)

	def read(self):
		with open(self.path, "r") as fileHandler:
			return fileHandler.read()

	def remove(self):
			os.remove(self.path)

	def make(self):
		"""Write empty file to make sure it exists."""
		self.write("")

#==========================================================
class Process(object):

	#=============================
	"""Represents a system process started by this script.
	Note: Refrain from calling .communicate() directly on the process from outside of this object."""
	#=============================

	def __init__(self, commandLine, run=True):
		self.commandLine = commandLine
		if run == True:
			self.run()
		self._communicated = False
		self._stdout = None
		self._stderr = None

	def run(self):
		self.process = Popen(self.commandLine, stdout=PIPE, stderr=PIPE)
		return self.process

	def waitAndGetOutput(self, timeout=None):
		if not self._communicated:
			self._stdout, self._stderr = self.process.communicate(timeout=timeout)
			self._communicated = True
		return (self._stdout, self._stderr)

	def waitAndGetStdout(self, timeout=None):
		return self.waitAndGetOutput(timeout)[0]

	def waitAndGetStderr(self, timeout=None):
		return self.waitAndGetOutput(timeout)[1]
