# -*- coding: UTF-8 -*-
# Matlab App Module for NVDA
# Copyright (C) 2022 Cyrille Bougot
# This file is covered by the GNU General Public License.


import appModuleHandler
from NVDAObjects.behaviors import Terminal
import controlTypes

import os
import sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
from lib.keyboard import keyboard
del sys.path[-1]

SEND_CMD = 'sendCommand'

class AppModule(appModuleHandler.AppModule):

	# Allow this to be overridden for derived applications.
	#TERMINAL_WINDOW_CLASS = "MATLAB"

	def chooseNVDAObjectOverlayClasses(self, obj, clsList):
		import NVDAObjects.behaviors, NVDAObjects.window, NVDAObjects.window.winConsole
		if obj.windowClassName == "Edit" and obj.role == controlTypes.Role.EDITABLETEXT:
			#obj.STABILIZE_DELAY = 0
			clsList[0:0] = [
				NVDAObjects.behaviors.Terminal,
				NVDAObjects.window.DisplayModelLiveText,
				NVDAObjects.window.DisplayModelEditableText,
				]
			
			
		if False and obj.windowClassName == "Edit" and obj.role == controlTypes.Role.EDITABLETEXT:
			from NVDAObjects.window import DisplayModelEditableText, DisplayModelLiveText
			from NVDAObjects.window import winConsole #.WinConsole
			try:
				clsList.remove(DisplayModelEditableText)
			except ValueError:
				pass
			#clsList[0:0] = (winConsole.WinConsole, Terminal, DisplayModelLiveText)
			clsList[0:0] = (Terminal, DisplayModelLiveText)
			
	def __init__(self, *args, **kw):
		super(AppModule, self).__init__(*args, **kw)
		self.commandTable = [
			('DbCont', 'dbcont', 'kb:F5'),
			('DbStepIn', 'dbstep in', 'kb:F8'),
			('DbStepOut', 'dbstep out', 'kb:control+shift+F8'),
			('DbStep', 'dbstep', 'kb:shift+F8'),
			('DbQuit', 'dbquit', 'kb:shift+escape'),
			('ClearSound', 'clear sound', 'kb:F7'),
			('GoToCurrentExecPoint', 'gcep', 'kb:F11'),
		]
		self.createAllScript_sendCommand()
		dicGestures = {gesture: SEND_CMD+name for name,cmd,gesture in self.commandTable}
		self.bindGestures(dicGestures)
		
	def sendCommand(self, sCmd, gesture):
		keyboard.write(sCmd)
		keyboard.send('enter')
		
	def sendCommand_oldBraille(self, sCmd, gesture):
		import brailleInput
		import inputCore
		import keyboardHandler
		#inputCore.manager.emulateGesture(keyboardHandler.KeyboardInputGesture.fromName("home"))
		#inputCore.manager.emulateGesture(keyboardHandler.KeyboardInputGesture.fromName("control+delete"))
		brailleInput.handler.sendChars(sCmd)
		inputCore.manager.emulateGesture(keyboardHandler.KeyboardInputGesture.fromName("enter"))
		
	def DISABLED_zzz_chooseNVDAObjectOverlayClasses(self, obj, clsList):
		if obj.windowClassName == "Edit" and obj.role == controlTypes.Role.EDITABLETEXT:
			#clsList.insert(0, EnhancedEditField)
			clsList.insert(0, Terminal)

	@staticmethod
	def _createScript_sendCommand(name, cmd):
		def  _genericScript_sendCommand(self, gesture):
			self.sendCommand(cmd,gesture)
		#Translators: Input help mode message pattern for the script used to send commands to Matlab.
		_genericScript_sendCommand.__doc__ = _("Send a command to Matlab: {name}").format(name=name[7:])
		return _genericScript_sendCommand
	
	
	def createAllScript_sendCommand(self):
		for name, cmd, gesture in self.commandTable:
			scriptName = 'script_' + SEND_CMD + name
			scriptFun = self._createScript_sendCommand(scriptName, cmd)
			setattr(self.__class__, scriptName, scriptFun)
	
AppModule.scriptCategory = _("Matlab")

