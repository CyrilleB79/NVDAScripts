# Do not open a message box when no more occurrence is found during a search operation.
# Copyright (C) 2021-2024 Cyrille Bougot
# This file is covered by the GNU General Public License.

"""This script removes the dialog box that appears when no more occurrence is found during a search operation.
Only a message is reported instead.
"""

import globalPluginHandler
import ui
import addonHandler
from cursorManager import CursorManager
import speech
import gui
from logHandler import log

import wx

try:
	# Python 3
	from inspect import signature
	enableFeature = True
except:
	# Python 2
	enableFeature = False
	log.debugWarning('Global plugin Find Extended incompatible: Not supporting Python 2.')


# Store original NVDA translation function.
nvdaTranslations = _

# Line to uncomment in case you convert it to add-on.
# addonHandler.initTranslation()


originalDoFindText = CursorManager.doFindText
def newDoFindText(self, text, reverse=False, caseSensitive=False, willSayAllResume=False):	
	try:
		originalWxCallAfter = wx.CallAfter
		def newCallAfter(func, *args, **kwargs):
			if (
				func == gui.messageBox
				and args[0] == nvdaTranslations('text "%s" not found') % text
				and args[1] == nvdaTranslations("Find Error")
				and args[2] == wx.OK | wx.ICON_ERROR
			):
				speech.cancelSpeech()
				return originalWxCallAfter(lambda: ui.message(nvdaTranslations('text "%s" not found') % text))
				#return originalWxCallAfter(lambda: wx.Bell())
			else:
				return originalWxCallAfter(func, *args, **kwargs)
		wx.CallAfter = newCallAfter
		originalDoFindText(self, text, reverse, caseSensitive, willSayAllResume)
	finally:
		wx.CallAfter = originalWxCallAfter


if enableFeature and len(signature(originalDoFindText).parameters) < 5:
	# Before NVDA 2020.4 / #11564: disable the feature since the signature of the patched function is different
	enableFeature = False
	log.debugWarning('Global plugin Find Extended incompatible: NVDA < 2020.4 - the signature of DoFindText is different.')


class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	
	def __init__(self, *args, **kw):
		super(GlobalPlugin, self).__init__(*args, **kw)
		if enableFeature:
			CursorManager.doFindText = newDoFindText
		
	def terminate(self):
		if enableFeature:
			CursorManager.doFindText = originalDoFindText
		super(GlobalPlugin, self).terminate()
