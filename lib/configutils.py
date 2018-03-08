#!/usr/bin/env python3
#-*- coding: utf-8 -*-

#=======================================================================================
# Imports
#=======================================================================================

import os
import sys
import configparser
import json
from lib.localization import Lang
from lib.base import *

#=======================================================================================
# Localization
#=======================================================================================

_ = Lang( "cappconfigutilslib", autodetect=False).gettext

#=======================================================================================
# Library
#=======================================================================================

#==========================================================
# Exceptions
#==========================================================

#==========================================================
class ConfigFileNotFound(Error):
	pass

#==========================================================
class ConfigSetupError(Error):
	pass

#==========================================================
class ConfigOptionUnassignedError(Error):
	pass

#==========================================================
class ConfigFormatError(Error):
	pass

#==========================================================
# Config Classes
#==========================================================

#==========================================================
class NoPreviousValue(InheritableNoneType):
	
	#=============================
	"""Signifies that """
	#=============================
	
	pass

#==========================================================
class Config(Namespace):
	
	#=============================
	"""A completely parsed out namspace object that represents a configuration."""
	#=============================
	
	pass

#==========================================================
class PluginDirPaths(Namespace):
	
	#=============================
	"""Lists of pluginDirPaths with their absolute path for each baseDirPath specified.
	They are assembled by traversing each baseDirPath for the names in the pluginDirNamesDict, with each
	list being a grouping of absolute paths of each pluginDirName found at every specified
	baseDirPath."""
	#=============================
	
	def __init__(self, baseDirPaths, pluginDirNamesDict):
		for pluginDirAttributeName in pluginDirNamesDict.keys():
			pluginDirName = pluginDirNamesDict[pluginDirAttributeName]
			setattr(self, pluginDirAttributeName, [])
			for baseDirPath in baseDirPaths:
				try:
					if pluginDirName in os.listdir(baseDirPath):
						getattr(self, pluginDirAttributeName).append(os.path.join(baseDirPath, pluginDirName))
				except FileNotFoundError:
					pass#TODO: Perhaps we could do more here.

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
	
	def process(self, value, previousValue):
		if type(value) is list:
			valueItems = []
			for valueItem in value:
				valueItems.append(self.processValueItem(valueItem, previousValue))
			return valueItems
		else:
			return self.processValueItem(value, previousValue)
		
	def processValueItem(self, valueItem, previousValue):
		if self.skipNone:
			if not valueItem == None:
				processedValue = self._procedure(valueItem, previousValue)
			else:
				processedValue = valueItem # 'value' ought always to equal 'None' in this case, logically.
		else:
				processedValue = self._procedure(valueItem, previousValue)
		return processedValue

#==========================================================
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
	
	def _procedure(self, value, previousValue):
		"""Processes file path options into canonical paths, resolving the given path towards that end.
		For example: ~ gets expanded into the user home directory, redundant instances of
		"." or ".." in the file path get eliminated, etc."""
		
		#print("[DEBUG][ConfigOptionCanonicalizedFilePathType] Turning", value, "into:", os.path.normpath(os.path.expanduser(value)))
		return os.path.normpath(os.path.expanduser(value))
	
#==========================================================
class ConfigOptionListType(ConfigOptionType):
	
	#=============================
	"""A config option listing multiple values."""
	#=============================
	
	# Defaults
	listType="json"
	
	def __init__(self, *args, listType=listType, merge=False, **kwargs):
		super().__init__(*args, **kwargs)
		self.merge = merge
		self.listType = listType
	
	def _procedure(self, value, previousValue):
		if self.listType == "json":
			#print("[DEBUG][ConfigOptionListType]", value, "JSON:", json.loads(value))
			try:
				if self.merge and previousValue is type(list):
					# 'previousValue' is a list. Since we are configured to merge lists, we'll
					# prepend the new value, which is expected to have a higher priority in
					# the code that will make use of it.
					return json.loads(value)+previousValue
				else:
					# 'previousValue' is not type(list), so it's probably 'NoPreviousValue' or 'None'.
					# As a result, there is no list to prepend.
					return json.loads(value)
			except json.decoder.JSONDecodeError:
				raise ConfigFormatError(_("A malformed list configuration value has been specified.\nThe value must be a json.loads compatible list, like so: [\"valueA\", \"valueB\"]. Don't forget the quotation marks!\nValue in question: {value}",\
					formatDict={"value": value}))
		else:
			raise ConfigSetupError("Unrecognized list type specified: {listType}".format(listType=self.listType))

#==========================================================
class ConfigOptionParameter(object):
	
	#=============================
	"""An aspect to a configuration option, such as its command line argument or description.
	Each parameter is an interface to a configuration option through which they are modified
	and understood.
	The 'value' is the actual parameter string (say, a category the option is configured
	to be subject to in the context of a configuration file).
	The 'description' of it is a string used in explaining the parameter, mostly in the context
	of error messages."""
	#=============================
	
	def __init__(self, parameterValue, defaultParameterValue, shortParameterDescription, parameterExplanation):
		self.parameterValue = parameterValue
		self.defaultParameterValue = defaultParameterValue
		self.shortParameterDescription = shortParameterDescription
		self.parameterExplanation = parameterExplanation
		if self.parameterValue == self.defaultParameterValue:
			self.configured = False
		else:
			self.configured = True
		self.synposis = self.shortParameterDescription+"\n"+self.parameterExplanation

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
	
	#NOTE: This is still shaky and messy.
	
	#===============
	# Defaults
	defaultCategory = "main"
	
	#===============
	# Constructor
	def __init__(self, varName,\
	argName=None,\
	argShort=None,\
	configName=None,\
	displayName=None,\
	shortDescription=None,\
	explanation=None,\
	metaVar=None,\
	category=defaultCategory,\
	defaultValue=None,\
	optionTypes=[],\
	enforceAssignment=False,\
	validateAssignment=False):
		
		#===============
		# Parameters
		
		# varName
		self.varName = ConfigOptionParameter(parameterValue=varName, defaultParameterValue=None,\
			shortParameterDescription=_("In-code variable name"),\
			parameterExplanation=_("This is how this option is represented and accessed in the actual code"))
		# argName
		self.argName = ConfigOptionParameter(parameterValue=argName, defaultParameterValue=None,\
			shortParameterDescription=_("Command line argument (long)"),\
			parameterExplanation=_("Example: --command-line-argument"))
		# argShort
		self.argShort = ConfigOptionParameter(parameterValue=argShort, defaultParameterValue=None,\
			shortParameterDescription=_("Command line argument (short)"),\
			parameterExplanation=_("""Example: -c"""))
		# configName
		self.configName = ConfigOptionParameter(parameterValue=configName, defaultParameterValue=None,\
			shortParameterDescription=_("Name in a configuration file context"),\
			parameterExplanation=_("Example: If in a configuration file the option would look like this: \"param\"=paramvalue\"then \"param\" would be what this parameter references"))
		# displayName
		self.displayName = ConfigOptionParameter(parameterValue=displayName, defaultParameterValue=None,\
			shortParameterDescription=_("Fancy name, e.g. for GUIs"),\
			parameterExplanation=_("Example: the varName might be \"thisParameter\", but the fancy name might be: \"This Parameter\""))
		# shortDescription
		self.shortDescription = ConfigOptionParameter(parameterValue=shortDescription, defaultParameterValue=None,\
			shortParameterDescription=_("A short description, like this one"),\
			parameterExplanation=_("Describes the option in a few words. Used for compact, brief messages such as errors"))
		# explanation
		self.explanation = ConfigOptionParameter(parameterValue=explanation, defaultParameterValue=None,\
			shortParameterDescription=_("In depth explanation of the option"),\
			parameterExplanation=_("Some options might require more explanation than what the short description provides. Some might even benefit from having examples provided"))
		# metaVar
		self.metaVar = ConfigOptionParameter(parameterValue=metaVar, defaultParameterValue=None,\
			shortParameterDescription=_("Syntax variable for help text"),\
			parameterExplanation=_("Example: If the command line argument is \"--parameter=foo\", \"foo\" might be referenced as \"VALUE\" in syntax help, whereas \"VALUE\" would be the metaVar"))
		# category
		self.category = ConfigOptionParameter(parameterValue=category, defaultParameterValue=self.__class__.defaultCategory,\
			shortParameterDescription=_("Category in a configuration file context"),\
			parameterExplanation=_("For example: [Main] in an ini-style configuration file, whereas \"Main\" would be the category in this case"))
		# defaultValue
		self.defaultValue = ConfigOptionParameter(parameterValue=defaultValue, defaultParameterValue=None,\
			shortParameterDescription=_("The default value value for this option"),\
			parameterExplanation=_("If no value is assigned to it, this will be the value it's going to carry going forward"))
		# optionTypes
		self.optionTypes = ConfigOptionParameter(parameterValue=optionTypes, defaultParameterValue=[],\
			shortParameterDescription=_("A list of option types",),\
			parameterExplanation=_("These types determine how the value is going to be processed upon assignment"))
	
		
		#===============
		# Behaviour
		self.enforceAssignment = enforceAssignment
		self.validateAssignment = validateAssignment
	
	#TODO: Clean up 'parameters' and 'configuredParameters'. This just doesn't fly.
	
	@property
	def synopsis(self):
		"""Return a human readable string explaining the anatomy of this option."""
		return "\n".join(map(lambda parameter: parameter.synposis, self.parameters))
	
	@property
	def parameters(self):
		#parametersDict - What the?!
		return [self.varName, self.argName, self.argShort, self.configName, self.displayName,\
			self.shortDescription, self.explanation, self.metaVar, self.category, self.defaultValue,\
			self.optionTypes]

	@property
	def configuredParameters(self):
		"""Returns a dict with all the info variables that are not 'None'."""
		#NOTE: [Aziroshin] This is a bit hacky. x_X
		configuredParametersDict = {}
		for oneOfOurAttributes in self.__dict__.keys():
			attributeValue = self.__dict__[oneOfOurAttributes]
			if type(attributeValue) == ConfigOptionParameter:
				if attributeValue.configured:
					configuredParametersDict[oneOfOurAttributes] = attributeValue
		return configuredParametersDict

	def createConfiguredNamesErrorListing(self):
		"""Create a listing of all configured names for the purpose of using it in an error message."""
		errorListElements = []
		for configuredParameter in self.configuredParameters.values():
			errorListElements.append("- {shortDescription}: {parameterValue}".format(\
				shortDescription=configuredParameter.shortParameterDescription,\
				parameterValue=configuredParameter.parameterValue))
		return os.linesep.join(errorListElements)

	def checkEnforcedAssignment(self, value):
		"""Check whether we """
		if value == self.defaultValue.parameterValue:
			#print("[DEBUG][configutils.py:ConfigOption.checkEnforcedAssignment]", "Value:", value, "|| Default value:", self.defaultValue.parameterValue)
			raise ConfigOptionUnassignedError(_("A configuration option isn't properly configured. The configuration option in question is comprised of the following parameters, which are listed as follows according to the context they're used in to aid you in locating the source of the problem:{eol}{eol}{configInfo}",\
				formatDict={"eol": os.linesep, "configInfo": self.createConfiguredNamesErrorListing() }))

	def validateAssignment(self, value):
		"""Validate whether the assigned value is within specifications.
		This method is currently #TODO and doesn't have any code."""
		# a) Subclassing might be an option.
		# b) Another way of doing this would be to come up with a modular, class based approach,
		# like the option typing system.
		# c) Another, and perhaps the best way, would be to integrate it with the existing
		# option system. If extreme modularity was desired, modular classes according to b)
		# could be attributes of these types.
		
		pass#TODO

	def validate(self, value):
		"""Run the validation code that was written for this object.
		This method is expected to have one of two outcomes:
			- Either it returns, which means the validation procedures in place passed
			- Or the validation code it calls raises an exception"""
		#TODO: The exceptions raised in subsequent methods should probably all
		# be the same exception, but with different error codes.
		# Or there could be one exception that is supposed to immediately catch the others,
		# but that'd be kind of convoluted. =x
		# Reasoning: Once plugins start having their own validation code, cappman,
		# especially GUI frontends based on it might crash out, even though there might
		# have been a better way of dealing with the exception. There has to be a way
		# to deal with plugin failure here that's less clunky.
		if self.enforceAssignment:
			self.checkEnforcedAssignment(value)
		if self.validateAssignment:
			self.validateAssignment(value)
#==========================================================
class ConfigSetup(object):
	
	#=============================
	"""Represents a set of configuration options for a specific config setup.
	
	Instances of this take 'ConfigOption' instances which define the options
	for the config set through the 'addOption' method.
	
	In order to resolve these options into actual parameter-value pairs,
	upon instantiation we are optionally going to need parsed out argparse objects,
	or paths to configuration files. If either of that is missing,
	only the other will determine the values. If all are missing, default
	values as specified in the supplied 'ConfigOption' instances will be used."""
	#=============================
	
	def __init__(self, configFilePaths=[]):
		self.options = {}
		self.configFilePaths = configFilePaths

	def addOption(self, option):
		"""Add an instance of ConfigOption to the dict of config options."""
		self.options[option.varName.parameterValue] = option

	@property
	def configFilePathPresentation(self):
		return "\n\t".join(self.configFilePaths)

	def getSynopsis(self, short=False):
		"""Get a description of option types (not their values, mind you.)"""
		optionSynopses = []
		for varName, option in self.options.items():
			if short:
				description = _("{varName}: {description}",\
					formatDict={"varName": varName,\
						"description": option.shortDescription.parameterValue})
			else:
				description = option.synopsis
			synopsis = _("\n{description}",\
				formatDict={"varName": varName, "description": description})
			optionSynopses.append(synopsis)
		return _("\n#===============\n# Config setup options:\n\t{synopses}",\
			formatDict={"configFilePaths": self.configFilePathPresentation,\
				"synopses": "\t".join(optionSynopses)})

	@property
	def commandLineOptions(self):
		"""Get all ConfigOptions that are configured as command line parameters."""
		commandLineOptions = {}
		for varName, option in self.options.items():
			if not option.argName.parameterValue == None:
				commandLineOptions[varName] = option
		return commandLineOptions

	@property
	def configFileOptions(self):
		"""Get all ConfigOptions that are configured for a configuration file."""
		configFileOptions = {}
		for varName, option in self.options.items():
			if not option.configName.parameterValue == None:
				configFileOptions[varName] = option
		return configFileOptions
	
	def putValueIntoConfig(self, option, config, value):
		"""Add a config option and its value to a 'Config' object."""
		processedValue = value
		for optionType in option.optionTypes.parameterValue:
			if hasattr(config, option.varName.parameterValue):
				processedValue = optionType.process(\
					processedValue,\
					previousValue=getattr(config, option.varName.parameterValue))
			else:
				processedValue = optionType.process(\
					processedValue,\
					previousValue=NoPreviousValue())
		setattr(config, option.varName.parameterValue, processedValue)

	def putDefaultValueIntoConfig(self, config, option):
		"""Fill the config namespace object with default values as configured by the config options."""
		for varName, option in self.options.items():
			try:
				self.putValueIntoConfig(option=option, config=config, value=option.defaultValue.parameterValue)
			except ConfigFormatError as error:
				raise ConfigFormatError(\
					_("Whilst assigning default values, the following error occurred:\n{error}\n{optionSynopsis}",\
					formatDict={"error": error, "optionSynopsis": option.synopsis}))

	def initializeConfigWithDefaultValues(self, config):
		"""Iterate over all the configured options and initialize default values into the config as fits.
		This will not initialize default values if the 'varName' has already been associated
		with a value that doesn't match the default value of a non-configured default value
		for an option, as that means that a previous 'ConfigSetup' object working on the
		specfied 'Config' object has already initialized a value for it, which we don't want to
		override here."""
		for varName, option in self.options.items():
			if hasattr(config, varName): # If not, it's not been initialized anyway, so we'll want to.
				if getattr(config, varName) is not option.defaultValue.defaultParameterValue:
					continue # This config value's already been configured, we don't want to mess with it.
			self.putDefaultValueIntoConfig(config, option)

	def putArgsIntoConfig(self, config, argObject):
		"""Parse an argparse object and put its values into the specified 'Config' instance.
		Note: Arguments are matched using 'varName' as used in 'ConfigOption'. That's
		why 'target' has to equal 'varName' when setting up arguments with argparse, if the
		arguments are supposed to work with this here system."""
		for varName, option in self.commandLineOptions.items():
			print("[DEBUG] [configutils.py.ConfigSetup.putArgsIntoConfig]", option.parameterValue)
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
			#print("[DEBUG][configutils.py:ConfigSetup.putConfigFileValuesIntoConfig] varName: ", varName, "configName: ", option.configName.parameterValue)
			if option.category.parameterValue in fileConfig:
				if option.configName.parameterValue in fileConfig[option.category.parameterValue].keys():
					self.putValueIntoConfig(\
						option=option,\
						config=config,\
						value=fileConfig[option.category.parameterValue][option.configName.parameterValue])
	def validateConfig(self, config):
		for varName, option in sorted(self.options.items()):
			#print("[configutils.py:ConfigSetup.validateConfig], varName: ", varName, "configName: ", option.configName.parameterValue, "value: ", config.__dict__[option.varName.parameterValue])
			option.validate(getattr(config, option.varName.parameterValue))

	def getConfig(self, argObjects=[], configFilePaths=[], config=Config(), complementPaths=True):
		"""Gets a 'Config' object initialized according to the specified arguments and config files.
		The 'argObjects' and 'configFilePaths' parameters both take lists, whereas the specified items
		are parsed in list order with each item overriding the former one."""
		config = config
		#print("[DEBUG][configSetup]", configFilePaths)
		self.initializeConfigWithDefaultValues(config)
		for configFilePath in configFilePaths:
			if os.path.exists(configFilePath):
				self.putConfigFileValuesIntoConfig(config=config, configFilePath=configFilePath)
			else:
				raise ConfigFileNotFound("The following configuration file path was specified but couldn't be found: {configFilePath}"\
					.format(configFilePath=configFilePath))
		for argObject in argObjects:
			self.putArgsIntoConfig(config=config, argObject=argObject)
		try:
			self.validateConfig(config)
		except ConfigOptionUnassignedError as error:
			print("[DEBUG] configutils.py.ConfigSetup.getConfig config: ", config)
			raise type(error)("\n"+"\n".join([error.message,\
				_("# Config values found:"),\
				FormattedNamespace(config).asString]))
		return config
