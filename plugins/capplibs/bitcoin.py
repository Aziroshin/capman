#!/usr/bin/env python3
#-*- coding: utf-8 -*-

#=======================================================================================
# Imports
#=======================================================================================

from lib.base import *
from lib.configutils import ConfigSetup

#=======================================================================================
# Library
#=======================================================================================

#==========================================================
class ConfigSetup(ConfigSetup):
	pass#TODO

#==========================================================
class BitcoinCapp(object):
	
	#=============================
	"""Represents a Bitcoin capp."""
	#=============================
	
	def __init__(self, configSetup):
		self.configSetup = configSetup
		self.config = configSetup.getConfig()
		self.currency = self.config.currency
		self.cliBinPath = self.config.cliBinPath
		self.daemonBinPath = self.config.daemonBinPath
		self.confFilePath = self.config.confFilePath
		self.dataDirPath = self.config.dataDirPath
		# Check path sanity.
		batchPathExistenceCheck = BatchPathExistenceCheck()
		batchPathExistenceCheck.addPath(self.cliBinPath, "cli-bin path: {path}".format(\
			path=self.cliBinPath))
		batchPathExistenceCheck.addPath(self.daemonBinPath, "daemon-bin path: {path}".format(\
			path=self.daemonBinPath))
		batchPathExistenceCheck.addPath(self.dataDirPath, "datadir path: {path}".format(\
			path=self.dataDirPath))
		if not self.confFilePath == None:
			# A conf file path got specified; check too.
			batchPathExistenceCheck.addPath(self.confFilePath, "conf-file path: {path}".format(\
				path=self.confFilePath))
		batchPathExistenceCheck.checkAll()
		# All paths are dandy, nice!

	def runCli(self, commandLine):
		
		#=============================
		"""Run the command line version of the capp with a list of command line arguments."""
		#=============================
		
		if not self.confFilePath == None:
			return Process([self.cliBinPath,\
				"-datadir={datadir}".format(datadir=self.dataDirPath),\
				"-conf={confFilePath}".format(confFilePath=self.confFilePath)] + commandLine)
		else:
			return Process([self.cliBinPath,\
				"-datadir={datadir}".format(datadir=self.dataDirPath)] + commandLine)
		

	def runDaemon(self, commandLine):
		
		#=============================
		"""Run the daemon. Takes a list for command line arguments to it."""
		#=============================
		
		if not self.confFilePath == None:
			return Process([self.daemonBinPath,\
				"-daemon",\
				"-datadir={datadir}".format(datadir=self.dataDirPath),\
				"-conf={confFilePath}".format(confFilePath=self.confFilePath)] +commandLine)
		else:
			return Process([self.daemonBinPath,\
				"-daemon",\
				"-datadir={datadir}".format(datadir=self.dataDirPath)] +commandLine)

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
		filePath = os.path.join(self.dataDirPath, fileName)
		if os.path.exists(filePath):
			if os.path.isdir(filePath):
				shutil.rmtree(filePath)
			else:
				os.remove(filePath)
	def deleteDataFiles(self, fileNameList):
		for fileName in fileNameList:
			self.deleteDataFile(fileName)
	def deleteBlockchainData(self):
		self.deleteDataFiles(["blocks", "chainstate", "database", "peers.dat", "banlist.dat"])
		

	def getBlockCount(self):
		return int(self.runCliSafe(["getblockcount"]).waitAndGetStdout(timeout=8).decode())