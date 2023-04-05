# -*- coding: UTF-8 -*-
# Notepad App Module for NVDA
# Copyright (C) 2023 Cyrille Bougot
# This file is covered by the GNU General Public License.


"""App module for Windows Notepad.
This module adds a script so that pressing enter reads the line before going back to newline.
"""


try:
	# Import all Notepad module in case it changes in the future.
	from nvdaBuiltin.appModules.notepad import *

	# Explicitely import what we use (even if already imported with '*')
	from nvdaBuiltin.appModules.notepad import AppModule
except ModuleNotFoundError:
	# For older NVDA versions, just import AppModule
	from appModuleHandler import AppModule
from scriptHandler import script
import api
import controlTypes
from speech import speech
import textInfos
from logHandler import log


log.debug('Loading notepad.py module')

class AppModule(AppModule):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		log.debug('Initializing Notepad appModule')

	@script(
		gesture="kb:enter",
	)
	def script_newLine(self, gesture):
		log.debug('Calling newline script')
		obj = api.getFocusObject()
		if obj.role in [controlTypes.Role.EDITABLETEXT, controlTypes.Role.DOCUMENT]:
			log.debug('Current object is editable text or document')
			info=obj.makeTextInfo(textInfos.POSITION_CARET)
			info.expand(textInfos.UNIT_LINE)
			speech.speakTextInfo(info, unit=textInfos.UNIT_LINE, reason=controlTypes.OutputReason.CARET)
		gesture.send()