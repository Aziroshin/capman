#!/usr/bin/env python3
#-*- coding: utf-8 -*-

#=======================================================================================
# Imports
#=======================================================================================

import unittest
import os
import shutil
import configparser
import argparse
from lib.base import *


#=======================================================================================
# Configuration
#=======================================================================================

testDirPath=os.path.join(os.path.join(os.path.expanduser("~"), ".cache"), "walman")

#=======================================================================================
# Library
#=======================================================================================

#==========================================================
class ConfigTest(unittest.TestCase):
	def setUp(self):
		self.configFilePath = os.path.join(testDirPath, "test.conf")
		try:
			os.makedirs(testDirPath)
		except FileExistsError:
			pass
		fileConfig = configparser.ConfigParser()
		fileConfig["Test"] = {}
		fileConfig["Test"]["testconfigkey"] = "testconfigvalue"
		with open(self.configFilePath, "w") as configFile:
			fileConfig.write(configFile)
		self.configSetup = ConfigSetup()
		self.configSetup.addOption(ConfigOption("test", argName="--test", argShort="-t", configName="testconfigkey", defaultValue="testdefaultvalue", category="Test"))
	def testConfigArgOverride(self):
		args = argparse.Namespace()
		args.test = "testargvalue"
		self.config = self.configSetup.getConfig(argObjects=[args], configFilePaths=[self.configFilePath])
		self.assertEqual(self.config.test, "testargvalue")
	def testArgAbsence(self):
		self.config = self.configSetup.getConfig(argObjects=[], configFilePaths=[self.configFilePath])
		self.assertEqual(self.config.test, "testconfigvalue")
	def testAllAbsence(self):
		self.config = self.configSetup.getConfig()
		self.assertEqual(self.config.test, "testdefaultvalue")

if __name__ == "__main__":
	unittest.main()