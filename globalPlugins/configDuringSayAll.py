# -*- coding: UTF-8 -*-
# Configuration change during say all - scripts for NVDA
# Copyright (C) 2020-2021 Cyrille Bougot
# This file is covered by the GNU General Public License.

# This script allows to change some configuration parameters without interrupting say all.
# Currently, the following commands are supported:
# - synth settings ring commands
# - change punctuation level
# - report CLDR
# To use it, put it in the globalPlugins folder of the scratchpad directory.

import globalPluginHandler
import ui
import scriptHandler
import config
try:
	from speech.sayAll import SayAllHandler as sayAllHandler
except ModuleNotFoundError:
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

class GlobalPlugin(globalPluginHandler.GlobalPlugin):

	# The scripts that should not interrupt during whatever type of SayAll (caret or review)
	scriptList = [
		GlobalCommands.script_increaseSynthSetting,
		GlobalCommands.script_decreaseSynthSetting,
		GlobalCommands.script_nextSynthSetting,
		GlobalCommands.script_previousSynthSetting,
		GlobalCommands.script_cycleSpeechSymbolLevel,
		GlobalCommands.script_toggleReportCLDR,
	]
	
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
		