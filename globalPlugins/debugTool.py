# -*- coding: UTF-8 -*-
#Stack trace log script for NVDA
#Copyright (C) 2019 Cyrille Bougot
#This file is covered by the GNU General Public License.

#This script allows to enable the stack trace logging of the speech function when pressing NVDA+control+alt+S. You may modify this file to pathc another function.
#To use it, put it in the globalPlugins folder.

#INSTRUCTIONS:
#- Put this file in the globalPlugins subfolder of NVDA user config folder.
#- Reload NVDA's pllugins (NVDA+Control+F3)
#- Press NVDA+control+alt+S to enable stack trace log
#A stack trace wille be logged each time the speak function will be called.
#- Press again NVDA+control+alt+S to disable stack trace log when you do not need it anymore.

#To change the trigger function search this file for "ToBeCustomized" strings.
#E.g. to trigger stack trace log on braille.BrailleHandler.update
#- import braille instead of speech
#- replace speech.speak function by braille.BrailleHandler.update function
#Good candidate functions may be the ones found in NVDA's journal on lines beginning with 'IO - ', e.g. braille.update, braille.BrailleBuffer.update, tones.beep, etc.


import globalPluginHandler
import ui
import traceback
from logHandler import log
from scriptHandler import script

#ToBeCustomized: import here the module containing the function you want the stacktrace to be logged
import speech
_originalFunction = speech.speak
#import braille
#_originalFunction = braille.BrailleHandler.update



def functionWithStackTraceLog(*args, **kwargs):
	res = _originalFunction(*args, **kwargs)
	GlobalPlugin.logStackTrace()
	return res
		
	
class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	
	def __init__(self):
		globalPluginHandler.GlobalPlugin.__init__(self)
		self.logEnabled = False
		
	@script(
		description = "Toggle stack trace log on the defined function.",
		gesture = "kb:nvda+control+alt+S"
		)
	def script_toggleStackTraceLog(self, gesture):
		global _originalFunction
		self.logEnabled = not self.logEnabled
		if self.logEnabled:
			newFun = functionWithStackTraceLog
			msg = 'Stacktrace log enabled'
		else:
			newFun = _originalFunction
			msg = 'Stacktrace log disabled'
		#ToBeCustomized: the function from which you want the stack trace
		speech.speak = newFun
		#braille.BrailleHandler.update = newFun
		ui.message(msg)
		
	@staticmethod
	def logStackTrace():
	    stack = [line.strip() for line in traceback.format_stack()]
	    msgStackTrace = (
	    	'=== Stack trace log ===\n' +
	    	'\n'.join(stack[:-1]) + '\n'
	    	'=== End stack trace log ===')
	    log.debug(msgStackTrace)
	
	