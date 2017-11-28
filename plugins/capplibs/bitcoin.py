#!/usr/bin/env python3
#-*- coding: utf-8 -*-

#=======================================================================================
# Imports
#=======================================================================================

from lib.base import *
from lib.capplib import *
from lib.configutils import ConfigSetup

#=======================================================================================
# Library
#=======================================================================================

#==========================================================
class BitcoinFlavorConfigSetup(ConfigSetup):
	pass#TODO

#==========================================================
class BitcoinCappConfigSetup(FlavorConfigSetup):
	pass#TODO

#==========================================================
class BitcoinCapp(BaseCapp):
	
	#=============================
	"""Represents a Bitcoin capp."""
	#=============================
	
	def __init__(self, configSetup, flavor=None):
		super().__init__(self, configSetup, flavor, flavorConfigSetup):
		# Check path sanity.
		batchPathExistenceCheck = BatchPathExistenceCheck()
		batchPathExistenceCheck.addPath(self.config.cliBinPath, "cli-bin path: {path}".format(\
			path=self.config.cliBinPath))
		batchPathExistenceCheck.addPath(self.config.daemonBinPath, "daemon-bin path: {path}".format(\
			path=self.config.daemonBinPath))
		batchPathExistenceCheck.addPath(self.config.dataDirPath, "datadir path: {path}".format(\
			path=self.config.dataDirPath))
		if not self.config.confFilePath == None:
			# A conf file path got specified; check too.
			batchPathExistenceCheck.addPath(self.config.confFilePath, "conf-file path: {path}".format(\
				path=self.config.confFilePath))
		batchPathExistenceCheck.checkAll()
		# All paths are dandy, nice!
		
	def runCli(self, commandLine):
		
		#=============================
		"""Run the command line version of the capp with a list of command line arguments."""
		#=============================
		
		if not self.config.confFilePath == None:
			return Process([self.config.cliBinPath,\
				"-datadir={datadir}".format(datadir=self.config.dataDirPath),\
				"-conf={confFilePath}".format(confFilePath=self.config.confFilePath)] + commandLine)
		else:
			return Process([self.config.cliBinPath,\
				"-datadir={datadir}".format(datadir=self.config.dataDirPath)] + commandLine)
		

	def runDaemon(self, commandLine):
		
		#=============================
		"""Run the daemon. Takes a list for command line arguments to it."""
		#=============================
		
		if not self.config.confFilePath == None:
			return Process([self.config.daemonBinPath,\
				"-daemon",\
				"-datadir={datadir}".format(datadir=self.config.dataDirPath),\
				"-conf={confFilePath}".format(confFilePath=self.config.confFilePath)] +commandLine)
		else:
			return Process([self.config.daemonBinPath,\
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
CappConfigSetup = BitcoinCappConfigSetup
FlavorConfigSetup = BitcoinFlavorConfigSetup