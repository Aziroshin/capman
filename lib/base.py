#!/usr/bin/env python3
#-*- coding: utf-8 -*-

#=======================================================================================
# Imports
#=======================================================================================

import os
import sys
from subprocess import Popen, PIPE
import argparse
import configparser

#=======================================================================================
# Library
#=======================================================================================

#==========================================================
# Exceptions
#==========================================================

#==========================================================
class ConfigFileNotFound(Exception):
	def __init__(self, message):
		super().__init__(message)

#==========================================================
# Base Classes
#==========================================================

class Namespace (argparse.Namespace):
	"""Pure namespace class.
	Basically serves as a dot-notation oriented dict.
	In its current implementation, this is a simple subclass of 'argparse.Namespace'"""
	pass

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
class Config(Namespace):
	
	#=============================
	"""A completely parsed out namspace object that represents a configuration."""
	#=============================
	def __init__(self):
		pass#TODO

#==========================================================
class ConfigOptionType(object):
	
	#=============================
	"""A 'ConfigOption' parsing & checking base class.
	This is used by 'ConfigOption' objects to perform certain actions on the options' value
	once it is initialized from its source (e.g. path sanity checking or expanding).
	Subclasses of this may be specified when instantiating 'ConfigOption' to have such
	procedures applied to the associated option and its value."""
	#=============================
	
	# Default behaviour
	skipNone=True
	
	def __init__(self, skipNone=skipNone):
		"""Please always specify keyword parameters to this method explicitely, their order might change."""
		self.skipNone=skipNone
	
	def _procedure(self, value):
		pass#OVERRIDE
	
	def process(self, value):
		if self.skipNone:
			if not value == None:
				processedValue = self._procedure(value)
			else:
				processedValue = value # 'value' ought always to equal 'None' in this case, logically.
		else:
				processedValue = self._procedure(value)
		return processedValue

class ConfigOptionFilePathType(ConfigOptionType):

	#=============================
	"""A basic class for various file path options."""
	#=============================
	
	pass

#==========================================================
class ConfigOptionCanonicalizedFilePathType(ConfigOptionFilePathType):
	
	#=============================
	"""A file path option that is supposed to end up with a canonical path."""
	#=============================
	
	def _procedure(self, value):
		"""Processes file path options into canonical paths, resolving the given path towards that end.
		For example: ~ gets expanded into the user home directory, redundant instances of
		"." or ".." in the file path get eliminated, etc."""
		
		return os.path.normpath(os.path.expanduser(value))
		

#==========================================================
class ConfigOption(object):
	
	#=============================
	"""Represents a config option for a configuration setup.
	
	Parameter break down:
	- varName: The nameof the variable. The code handles this option by that name.
	- argName: The command line argument for this option.
	    If absent, it's assumed this isn't a command line option.
	- configName: How this option is called in a config file.
	    If not specified, it's assumed this option won't show up in config files.
	- displayName: What this option will be called in "fancy" environments, such as a GUI.
	- description: A description of this option used in help texts.
	metaVar: A string used to represent the option in syntax help bits, preferably upper case (e.g. PATH).
	- category: A category in a configuration file.
	- defaultValue: If no value for the option is specified anywhere, this will be it instead.
	- optionType: Certain options may need some processing (e.g. checking for path sanity).
	    For such options, a subclass of 'ConfigOptionType' with an overridden 'process' method
	    can be instantiated right when we are called
	    For example: 'ConfigOption(varName=test, optionType=ConfigOptionTestType())
	    
	    Dev note: The reason for instantiating it at that point is to keep the door open for 
	    possible customization parameters of 'ConfigOptionType' subclasses down the road
	    without compromising API compatibility."""
	#=============================
	
	# Defaults
	defaultCategory = "main"
	
	def __init__(self, varName, argName=None, argShort=None, configName=None, displayName=None, description=None, metaVar=None, category=defaultCategory, defaultValue=None, optionType=None):
		self.varName = varName
		self.argName = argName
		self.argShort = argShort
		self.configName = configName
		self.displayName = displayName
		self.description = description
		self.metaVar = metaVar
		self.category = category
		self.defaultValue = defaultValue
		self.optionType = optionType

#==========================================================
class ConfigSetup(object):
	
	#=============================
	"""Represents a set of configuration options for a specific config setup.
	
	Instances of this take 'ConfigOption' instances which define the options
	for the config set through the 'addOption' method.
	
	In order to resolve these options into actual parameter-value pairs,
	upon instantiation we are optionally going to need a parsed out argparse object,
	or a path to a configuration file. If either of them is missing,
	only the other will determine the values. If all are missing, default
	values as specified in the supplied 'ConfigOption' instances will be used."""
	
	#=============================
	
	def __init__(self):
		self.options = {}

	def addOption(self, option):
		"""Add an instance of ConfigOption to the dict of config options."""
		self.options[option.varName] = option

	@property
	def commandLineOptions(self):
		"""Get all ConfigOptions that are configured as command line parameters."""
		commandLineOptions = {}
		for varName, option in self.options.items():
			if not option.argName == None:
				commandLineOptions[varName] = option
		return commandLineOptions

	@property
	def configFileOptions(self):
		"""Get all ConfigOptions that are configured for a configuration file."""
		configFileOptions = {}
		for varName, option in self.options.items():
			if not option.configName == None:
				configFileOptions[varName] = option
		return configFileOptions
	
	def putValueIntoConfig(self, option, config, value):
		"""Add a config option and its value to a 'Config' object."""
		if option.optionType == None:
			processedValue = value
		else:
			processedValue = option.optionType.process(value)
		config.__dict__[option.varName] = processedValue

	def putDefaultValuesIntoConfig(self, config):
		for varName, option in self.options.items():
			self.putValueIntoConfig(option=option, config=config, value=option.defaultValue)

	def putArgsIntoConfig(self, config, argObject):
		"""Parse an argparse object and put its values into the specified 'Config' instance.
		Note: Arguments are matched using 'varName' as used in 'ConfigOption'. That's
		why 'target' has to equal 'varName' when setting up arguments with argparse, if the
		arguments are supposed to work with this here system."""
		for varName, option in self.commandLineOptions.items():
			if varName in argObject.__dict__.keys():
				self.putValueIntoConfig(\
					option=option,\
					config=config,\
					value=argObject.__dict__[varName])

	def putConfigFileValuesIntoConfig(self, config, configFilePath):
		"""Parse the specified config file and put its values into the specified 'Config' instance."""
		fileConfig = configparser.ConfigParser()
		fileConfig.read(configFilePath)
		for varName, option in self.configFileOptions.items():
			if option.category in fileConfig:
				if option.configName in fileConfig[option.category].keys():
					self.putValueIntoConfig(\
						option=option,\
						config=config,\
						value=fileConfig[option.category][option.configName])
	def getConfig(self, argObjects=[], configFilePaths=[], config=Config()):
		"""Gets a 'Config' object initialized according to the specified arguments and config files.
		The 'argObjects' and 'configFilePaths' parameters both take lists, whereas the specified items
		are parsed in list order with each item overriding the former one."""
		config = config
		print("[DEBUG][configSetup]", configFilePaths)
		self.putDefaultValuesIntoConfig(config)
		for configFilePath in configFilePaths:
			if os.path.exists(configFilePath):
				self.putConfigFileValuesIntoConfig(config=config, configFilePath=configFilePath)
			else:
				raise ConfigFileNotFound("The following configuration file path was specified but couldn't be found: {configFilePath}"\
					.format(configFilePath=configFilePath))
		for argObject in argObjects:
			self.putArgsIntoConfig(config=config, argObject=argObject)
		return config

class DefaultsConfigSetup(ConfigSetup):
	"""'ConfigSetup' for general defaults for wallet manager."""
	def __init__(self):
		super().__init__()
		self.addOption(ConfigOption(varName="walletConfigDirPath", configName="walletconfigdir", optionType=ConfigOptionCanonicalizedFilePathType()))

class Defaults(Namespace):
	"""Wallet Manager default config."""
	def __init__(self):
		binDir = os.path.realpath(os.path.dirname(sys.argv[0]))
		config = DefaultsConfigSetup().getConfig(configFilePaths=[os.path.join(os.path.join(binDir, "config"), "capman.conf")])
		self.walletConfigDirPath = config.walletConfigDirPath

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