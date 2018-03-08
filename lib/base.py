#!/usr/bin/env python3
#-*- coding: utf-8 -*-

#=======================================================================================
# Imports
#=======================================================================================

import os
import sys
import argparse
import importlib
import shutil
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
class FormattedNamespace(object):
	
	#=============================
	"""Provides a given namespace in various forms, such as a string or a sorted list of tuples."""
	#=============================
	
	def __init__(self, namespaceObject):
		self.namespace = namespaceObject
	
	@property
	def asDict(self):
		"""Returns the __dict__ key/value pair of the namespace object."""
		return self.namespace.__dict__
	
	@property
	def attributes(self):
		"""Returns a list of all the attributes."""
		return self.asDict.keys()
	
	@property
	def values(self):
		"""Returns a list of all the values."""
		return self.asDict.values()
	
	@property
	def asSortedListOfStrings(self):
		"""A sorted list of strings, with each string being one key/value pair of the namespace."""
		strings = []
		for keyValueTuple in self.asDict.items():
			strings.append("{key}: {value}".format(key=keyValueTuple[0], value=keyValueTuple[1]))
		return strings
	
	@property
	def asMultLineString(self):
		"""Returns a string representation of the namespace, with one line per key-value pair."""
		return "\n".join(self.asSortedListOfStrings)
	
	@property
	def asString(self):
		"""Returns a string representation of the namespace, with all key-value pairs on one line.
		The pairs are separated by commas."""
		"""Returns a list of strings, with each string holding a colon+space separated key+value pair."""
		return "\n".join(self.asSortedListOfStrings)

#==========================================================
class Singleton(type):

	#=============================
	# """This class will always return the same instance, regardless of how many times it's called."""
	#=============================

	def __init__(singletonClass, className, parentClasses, classDict):
		singletonClass.singletonObject = None
	def __call__(self, *args, **kwargs):
		if self.singletonObject is None:
			self.singletonObject = type.__call__(self, *args, **kwargs)
		return self.singletonObject

#==========================================================
class InheritableNoneType(object, metaclass=Singleton):
	
	#=============================
	# """Basically 'NoneType' that can be subclassed."""
	#=============================
	
	def __bool__(self):
		return False

#==========================================================
class Unassigned(InheritableNoneType, metaclass=Singleton):
	
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
	pass

#==========================================================
class FancyErrorMessage(object):

	#=============================
	# """Provides error messages that are a bit better formatted and visible for the end user."""
	#=============================

	def __init__(self, message, title=""):
		decorTop = "\n#=============================\n# [CAPPMAN ERROR] {title}\n".format(title=title)
		decorBottom = "\n# [CAPPMAN ERROR]\n#============================="
		self.string = "{eol}{decorTop}{eol}{message}{eol}{decorBottom}"\
			.format(eol=os.linesep, decorTop=decorTop, message=message, decorBottom=decorBottom)
		__repr__ = self.string

#==========================================================
# Exceptions
#==========================================================

#==========================================================
class Error(Exception):
	#TODO: Implement logging once there's logging functionality.
	def __init__(self, message):
		self.message = FancyErrorMessage(message, title=self.__class__.__name__).string
		super().__init__(message)

#==========================================================
class PathNotFoundError(Error):
	pass

#==========================================================
class ErrorCodes(Namespace):
	
	#=============================
	"""Namespace class to configure error codes for execeptions."""
	#=============================
	
	pass

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
	
	codes = ErrorCodes()
	
	def __init__(self, message, code):
		self.code = code
		super().__init__(message)
	
	@property
	def codeNames(self):
		"""Returns a list of all code names associated with this error."""
		return self.__dict__.keys()
	
	@property
	def codeName(self):
		"""The code name for this error."""
		self.getNameByCode(self.code)
		raise ErrorCodeError(\
			"The following error code couldn't be resolved: \"{code}\". Available error codes:\n{codeList}"\
			.format(code=code, codeList=self.codeNames))
	
	def getCodeByName(self, name):
		"""Return the error code that matches the specified code name."""
		return self.codes.__dict__[name]
	
	def getNameByCode(self, code):
		"""Takes an error code and returns its (variable) name.
		This is a reverse dictionary lookup by the code for the name of the codes namespace object.
		We expect every error code to only exist once. Break that and it'll explode in your face. :p"""
		for name in self.codes.codeNames:
			if code == self.getCodeByName(name):
				return name

#==========================================================
class ConfigFileNotFound(Error):
	pass

#==========================================================
class ConfigOptionUnassignedError(Error):
	pass

#==========================================================
class ActionResult(object):
	
	#=============================
	"""What's left after an action has completed: Its results, the state of things, etc."""
	#=============================
	
	def __init__(self, item=None, status=0, description="", jsonResult=None):
		self.item = item
		self.status = status
		self.description = description
		self.json = jsonResult # Make sure there's no collision with the json module down the road.

#==========================================================
class Action(object):
	
	#=============================
	"""Represents a command line or other API action of sorts.
	Is planned to be used in a command-matching pattern, e.g. to match actions specified on the command
	line."""
	#=============================
	
	def __init__(self, name):
		self.name = name
	def perform(self):
		"""Here goes the code in the subclassed action."""
		pass#OVERRIDE

#==========================================================
class Actions(object):
	
	#=============================
	"""A ledger of actions."""
	#=============================
	
	def __init__(self):
		self.ledger = {}
	def addAction(self, action):
		"""Add an action to the ledger, keyed with its name."""
		self.ledger[action.name] = action
	def perform(self, actionName):
		"""Perform the action specified by its name, if found in the ledger."""
		#Should perhaps raise an error if it can't find a match.
		self.ledger[actionName].perform()

#==========================================================
class BatchPathExistenceCheckPath(object):
	
	#=============================
	"""Pairs a path with an existence-check and an error message to use if it doesn't exist."""
	#=============================
	
	def __init__(self, path, errorMessage):
		self.path = path
		self.errorMessage = errorMessage

	def exists(self):
		"""Checks whether the path exists; returns 'True' if it does, 'False' if it doesn't.
		This also considers executable availability through $PATH, in case the specified
		'path' is not actually a path per se, but the name of an executable available through
		$PATH."""
		if os.path.exists(self.path):
			return True
		else:
			if shutil.which(self.path):
				return True
			else:
				return False

#==========================================================
class BatchPathExistenceCheck(object):
	
	#=============================
	"""Takes path+errorMessage pairs and checks whether they exist, with an optional error raised.
	Raising the optional error is the default behaviour and needs to be disabled if
	that is undesired."""
	#=============================
	
	def __init__(self):
		self.paths = []
		self.batchErrorMessage = ""
		self.nonExistentPathCount = 0
	
	def addPath(self, path, errorMessage):
		self.paths.append(BatchPathExistenceCheckPath(path, errorMessage))
	
	def checkAll(self, autoRaiseError=True):
		for path in self.paths:
			if not path.exists():
				self.nonExistentPathCount += 1
				self.batchErrorMessage\
					= "{batchErrorMessage}\n{errorMessage}".format(\
					batchErrorMessage=self.batchErrorMessage, errorMessage=path.errorMessage)
		if autoRaiseError:
			self.raiseErrorIfNonExistentPathFound()
	
	def raiseErrorIfNonExistentPathFound(self):
		if self.nonExistentPathCount > 0:
			self.raiseError()
	
	def raiseError(self):
		if self.batchErrorMessage == "":
			raise PathNotFoundError("Error: No non-existent paths found, but error was raised anyway.")
		elif self.nonExistentPathCount == 1:
			raise PathNotFoundError(\
				"Error: The following path doesn't exist:{batchErrorMessage}".format(\
					batchErrorMessage=self.batchErrorMessage))
		elif self.nonExistentPathCount > 1:
			raise PathNotFoundError(\
				"Error: The following paths don't exist:{batchErrorMessage}".format(\
					batchErrorMessage=self.batchErrorMessage))

#==========================================================
class BaseFile(object):
	
	#=============================
	"""Base Class for various types of fileobjects as recognized by filesystems."""
	#=============================
	
	def __init__(self, path):
		self.path = path
		
	@property
	def lastModified(self):
		return int(os.path.getmtime(self.path))

	@property
	def secondsSinceLastModification(self):
		return int(time.time()) - int(self.lastModified)

	@property
	def exists(self):
		return os.path.exists(self.path)

#==========================================================
class File(BaseFile):
	
	#=============================
	"""Basic file wrapper.
	Abstracts away basic operations such as read, write, etc."""
	#TODO: Make file operations safer and failures more verbose with some checks & exceptions.
	#=============================
	
	def __init__(self, path, make=False, makeDirs=False):
		super().__init__(path)
		self.__dirPath = os.path.dirname(self.path) # PRIVATE, because it's subject to change.
		self.existed = self.exists # Determines whether this file existed at the time of instantiation.
		if not self.exists and make:
			self.make()
		if not os.path.exists(self.__dirPath):
			self.makeDirs()
	
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
	def makeDirs(self):
		os.makedirs(self.__dirPath)

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
