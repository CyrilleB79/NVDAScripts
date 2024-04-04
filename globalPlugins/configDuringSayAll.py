# -*- coding: UTF-8 -*-
# Configuration change during say all - scripts for NVDA
# Copyright (C) 2020-2024 Cyrille Bougot
# This file is covered by the GNU General Public License.

# This script allows to change some configuration parameters without interrupting say all.
# Currently, the following commands are supported:
# - synth settings ring commands
# - change punctuation level
# - report CLDR

import globalPluginHandler
import ui
import scriptHandler
import config
try:
	from speech.sayAll import SayAllHandler as sayAllHandler
except ImportError:  # Python 3: raises ModuleNotFoundError (a subclass from ImportError); Python 2: raises ImportError
	import sayAllHandler
from globalCommands import commands, GlobalCommands
from types import MethodType


def willSayAllResumeNew(gesture):
	return (
		config.conf['keyboard']['allowSkimReadingInSayAll']
		and gesture.wasInSayAll
		and getattr(
			gesture.script,
			'resumeSayAllMode',
			None
		) in [sayAllHandler.lastSayAllMode, sayAllHandler.CURSOR_ANY]
	)
def disableWithPython2(c):
	import sys
	if sys.version_info.major <= 2:
		from logHandler import log
		log.debugWarning('GlobalPlugin configDuringSayAll incompatible: Does not support Python 2')
		return globalPluginHandler.GlobalPlugin
	return c


@disableWithPython2
class GlobalPlugin(globalPluginHandler.GlobalPlugin):

	# The scripts that should not interrupt during whatever type of SayAll (caret or review)
	scriptList = [
		GlobalCommands.script_increaseSynthSetting,
		GlobalCommands.script_decreaseSynthSetting,
		GlobalCommands.script_nextSynthSetting,
		GlobalCommands.script_previousSynthSetting,
		GlobalCommands.script_cycleSpeechSymbolLevel,
	]
	try:
		scriptList.append(GlobalCommands.script_toggleReportCLDR)
	except AttributeError:
		# Older NVDA versions such as NVDA 2019.2.1 : script_toggleReportCLDR not present
		pass
	
	def __init__(self):
		super().__init__()
		self.willSayAllResumeOriginal = scriptHandler.willSayAllResume
		scriptHandler.willSayAllResume = willSayAllResumeNew
		sayAllHandler.CURSOR_ANY = -1
		for scr in self.scriptList:
			func = scr
			func.resumeSayAllMode = sayAllHandler.CURSOR_ANY
			setattr(GlobalCommands, func.__name__, func)

	def terminate(self):
		super().terminate()
		del sayAllHandler.CURSOR_ANY
		for scr in self.scriptList:
			del scr.resumeSayAllMode
		scriptHandler.willSayAllResume = self.willSayAllResumeOriginal
