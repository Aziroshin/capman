#!/usr/bin/env python3
#-*- coding: utf-8 -*-

#=======================================================================================
# Imports
#=======================================================================================

from lib.base import *
from lib.capplib import *
from lib.configutils import ConfigSetup, ConfigOption

#=======================================================================================
# Library
#=======================================================================================

#==========================================================
class BitcoinFlavorConfigSetup(ConfigSetup):
	"""Config options for the flavor plugin file for this crypto application.
	Flavor plugins are essentially glorified configparser (INI style) configuration files,
	which is what ConfigSetup is based on.
	When creating your own capplib based on this one here, you'd subclass this here class
	and make your own modifications as needed (or none if there are no differences).
	If you just want to change the values for your crypto application, simply make
	your own Flavor plugin. There is no need to change anything on this here level."""
	def __init__(self, configFilePaths=[]):
		super().__init__(configFilePaths)
		#=============================
		self.addOption(ConfigOption(varName="cliExecPath",\
			shortDescription="The path of the command line interface executable.",\
			configName="cli", category="paths", enforceAssignment=True))
		#=============================
		self.addOption(ConfigOption(varName="daemonExecPath",\
			shortDescription="The path of the daemon executable.",\
			configName="daemon", category="paths", enforceAssignment=True))
		#=============================
		self.addOption(ConfigOption(varName="configFileName",\
			shortDescription="The name of the wallet config file.",\
			configName="configfilename", category="names", enforceAssignment=True))
		#=============================
		self.addOption(ConfigOption(varName="dataDirPath",\
			shortDescription="The path of the datadir.",\
			configName="datadir", category="paths", enforceAssignment=True))

#==========================================================
class BitcoinCappConfigSetup(BitcoinFlavorConfigSetup):
	"""Config options for the configuration file for this capplib.
	This is the setup for the configuration file users create for their wallets.
	As they might also want to change some of the basic values inherent to the Flavor setup,
	this is supposed to be a subclass of it."""
	#=============================
	def __init__(self, configFilePaths=[]):
		super().__init__(configFilePaths)
		self.addOption(ConfigOption(varName="configFilePath",\
			shortDescription="The path of the wallet config file.",\
			configName="config", category="paths"))

#==========================================================
class BitcoinCapp(BaseCapp):
	
	#=============================
	"""Represents a Bitcoin capp."""
	#=============================
	
	def __init__(self, configSetup, flavor=None):
		print("[DEBUG] capplib_bitcoin.py BitcoinCapp.__init__ Flavor (as given)", flavor)
		super().__init__(configSetup, flavor)
		print("[DEBUG] capplib_bitcoin.py BitcoinCapp.__init__ self.flavor", self.flavor)
		# Check path sanity.
		batchPathExistenceCheck = BatchPathExistenceCheck()
		batchPathExistenceCheck.addPath(self.config.cliExecPath, "cli-bin path: {path}".format(\
			path=self.config.cliExecPath))
		batchPathExistenceCheck.addPath(self.config.daemonExecPath, "daemon-bin path: {path}".format(\
			path=self.config.daemonExecPath))
		batchPathExistenceCheck.addPath(self.config.dataDirPath, "datadir path: {path}".format(\
			path=self.config.dataDirPath))
		if not self.config.configFilePath == None:
			# A conf file path got specified; check too.
			batchPathExistenceCheck.addPath(self.config.configFilePath, "conf-file path: {path}".format(\
				path=self.config.configFilePath))
		batchPathExistenceCheck.checkAll()
		# All paths are dandy, nice!
		
	def runCli(self, commandLine):
		
		#=============================
		"""Run the command line version of the capp with a list of command line arguments."""
		#=============================
		
		if not self.config.configFilePath == None:
			return Process([self.config.cliExecPath,\
				"-datadir={datadir}".format(datadir=self.config.dataDirPath),\
				"-conf={configFilePath}".format(configFilePath=self.config.configFilePath)] + commandLine)
		else:
			return Process([self.config.cliExecPath,\
				"-datadir={datadir}".format(datadir=self.config.dataDirPath)] + commandLine)
		

	def runDaemon(self, commandLine):
		
		#=============================
		"""Run the daemon. Takes a list for command line arguments to it."""
		#=============================
		
		if not self.config.configFilePath == None:
			return Process([self.config.daemonExecPath,\
				"-daemon",\
				"-datadir={datadir}".format(datadir=self.config.dataDirPath),\
				"-conf={configFilePath}".format(configFilePath=self.config.configFilePath)] +commandLine)
		else:
			return Process([self.config.daemonExecPath,\
				"-daemon",\
				"-datadir={datadir}".format(datadir=self.config.dataDirPath)] +commandLine)

	def runCliSafe(self, commandLine, _retrying=False):
		
		#=============================
		"""A version of .runCli that checks for the capp tripping up and responds accordingly."""
		#=============================
		process = self.runCli(commandLine)
		stdoutString, stderrString = process.waitAndGetOutput()
		# Catch the capp taking the way out because the daemon isn't running.
		if stderrString.decode().strip() == "error: couldn't connect to server":
			raise CappConnectionError(\
				"Command line capp can't connect to the daemon. Is the daemon running?")
		# Catch issues caused by the capp connecting to the daemon right after the daemon started.
		# As this involves retrying, we have to make sure we don't get stuck retrying forever.
		if "error code: -28" in stdoutString.decode()\
			or "error code: -28" in stderrString.decode()\
			and not _retrying:
			# Rerun this method in intervals until it works, or we decide to give up.
			for retry in range(1,16):
				time.sleep(5)
				retriedProcess = self.runCliSafe(commandLine, _retrying=True)
				retriedStdoutString, retriedStderrString = retriedProcess.waitAndGetOutput()
				if "error code: -28" in retriedStdoutString.decode()\
					or "error code: -28" in retriedStderrString.decode():
					continue
				else:
					return retriedProcess
			raise DaemonStuckError("Daemon stuck at error -28.")
		return process

	def runDaemonSafe(self, commandLine):
		
		#=============================
		"""A version of .runDaemon that checks for the daemon tripping up and responds accordingly."""
		#=============================
		
		process = self.runDaemon(commandLine)
		stdoutString, stderrString = process.waitAndGetOutput()
		#TODO: Make running the daemon safer and failures more verbose with some checks & exceptions.
		return process

	def startDaemon(self, commandLine=[]):
		
		#=============================
		"""Start the daemon. Takes a list for command line arguments."""
		#=============================
		
		return self.runDaemon(commandLine)

	def stopDaemon(self, waitTimeout):
		
		#=============================
		"""Stop the daemon.
		The parameter 'waitTimeout' determines for how long we will wait and poll
		for stop confirmation, in seconds."""
		#=============================
		
		process = self.runCliSafe(["stop"])
		# Wait and poll every second for daemon shutdown completion.
		# Return once daemon shut down is confirmed.
		if not waitTimeout == None:
			for second in range(1,waitTimeout):
				try:
					self.getBlockCount() # We could use anything. This will do.
				except CappConnectionError:
					break
				time.sleep(1)
		return process
	def deleteDataFile(self, fileName):
		filePath = os.path.join(self.config.dataDirPath, fileName)
		if os.path.exists(filePath):
			if os.path.isdir(filePath):
				shutil.rmtree(filePath)
			else:
				os.remove(filePath)
	def deleteDataFiles(self, fileNameList):
		for fileName in fileNameList:
			self.deleteDataFile(fileName7)
	def deleteBlockchainData(self):
		self.deleteDataFiles(["blocks", "chainstate", "database", "peers.dat", "banlist.dat"])
		

	def getBlockCount(self):
		return int(self.runCliSafe(["getblockcount"]).waitAndGetStdout(timeout=8).decode())

#=======================================================================================
# Export
#=======================================================================================
# The code that's using this plugin will have to know what to call
# upon, thus you'll have to assign the 'Capp' variable the class
# that client code is supposed to access (and return a proper BaseCapp extended object.)
# Do the same for CappConfigSetup and FlavorConfigSetup
#==========================================================
Capp = BitcoinCapp
FlavorConfigSetup = BitcoinFlavorConfigSetup
CappConfigSetup = BitcoinCappConfigSetup