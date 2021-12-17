# -*- coding: UTF-8 -*-
# OCR scripts for NVDA
# Copyright (C) 2020 Cyrille Bougot
# This file is covered by the GNU General Public License.

# This script allows to OCR an opened PDF with MS word.
# Before first use, open a PDF manually in MS Word. If you did not disable it before a warning dialog will appear with the following message:
# "Word will now convert your PDF to an editable Word document.  This may take a while.  The resulting Word document will be optimized to allow you to edit the text, so it might not look exactly like the original PDF, especially if the original file contained lots of graphics."
# Check the checkbox "Don't show this message again" and validate by clicking "OK".
# If you want to restore Word's original behaviour with this dialog appearing, opan the following registry key:
# HKEY_CURRENT_USER\Software\Microsoft\Office\16.0\Word\Options
# And delete the delete the DisableConvertPdfWarning value or set it to 0.

import globalPluginHandler
import api
import ui
import controlTypes
from windowUtils import findDescendantWindow
from NVDAObjects.IAccessible import getNVDAObjectFromEvent
import winUser
import appModuleHandler
from scriptHandler import script
from keyboardHandler import KeyboardInputGesture
from comtypes.client import CreateObject, GetActiveObject

import os.path
try:
	# Python 3
	from urllib.parse import urlparse
except ImportError:
	# Python 2
	from urlparse import urlparse

# Strings to be translated in Adobe Reader's language. These are required by the script to get the information of these fields
# label of the 'File:' field (first field) in 'Description' pane (first pane)
FILE_LABEL_NAME = 'Fichier :'
# label of the 'Location:' field in 'Description' pane (first pane)
LOCATION_LABEL_NAME = 'Emplacement :'

class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	
	def __init__(self):
		globalPluginHandler.GlobalPlugin.__init__(self)
		
	@script(
		description = "Performs OCR on currently opened document with Microsoft Word.",
		gesture = "kb:NVDA+shift+O",
	)
	def script_ocrInMSWord(self, gesture):
		fg = api.getFocusObject()
		appName = appModuleHandler.getAppNameFromProcessID(fg.processID,True).lower()
		if appName == 'acrord32.exe':
			self.ocrInMSWordFromAdobeReader(gesture)
		elif appName == 'explorer.exe':
			self.ocrInMSWordFromExplorer(gesture)
		else:
			ui.message('OCR not supported in this application')
		
	def ocrInMSWordFromExplorer(self, gesture):
		fg = 		api.getFocusObject()
		fgHwnd = winUser.getForegroundWindow()
		import globalVars
		globalVars.dbg = fgHwnd
		shell = CreateObject("Shell.Application")
		for w in shell.Windows():
			if w.HWND == fgHwnd:
				break
		else:  # Executed if the loop ends without break
			ui.message('Explorer window not found')
			return
		pathUri = w.LocationURL
		p = urlparse(pathUri)
		pPath = p.path[1:] if p.path.startswith('/') else p.path
		if pPath == '':
			ui.message('No path')
		path = os.path.abspath(os.path.join(p.netloc, pPath))
		obj = api.getFocusObject()
		if obj.role == controlTypes.ROLE_LISTITEM:
			if obj.firstChild is not None:
				obj = obj.firstChild
		else:
			ui.message('No file selected')
			return
		filePath = os.path.join(path, obj.name)
		ui.message(filePath)
	
	def ocrInMSWordFromAdobeReader(self, gesture):
		#KeyboardInputGesture.fromName("control+D").send()
		fg = 		api.getFocusObject()
		try:
			handle = findDescendantWindow(fg.windowHandle, className='RICHEDIT50W')
		except LookupError:
			ui.message('The properties window must be opened to call this script. Press control+D to open it.')
			return
		obj = getNVDAObjectFromEvent(handle, winUser.OBJID_CLIENT, 0)
		while obj.simplePrevious:
			obj = obj.simplePrevious
		while obj:
			if obj.name == FILE_LABEL_NAME:
				obj = obj.simpleNext
				file = obj.name
			elif obj.name == LOCATION_LABEL_NAME:
				obj = obj.simpleNext
				location = obj.name
				break  # All info retrieved now
			obj = obj.simpleNext
		try:
			path = os.path.join(location, file)
		except UnboundLocalError:
			ui.message("Please select the 'Description' tab before calling the OCR command.")
			return
		KeyboardInputGesture.fromName("escape").send()
		KeyboardInputGesture.fromName("control+F4").send()
		import core
		core.callLater(1000, self.openPdfInWord, path)
		
	def openPdfInWord(self, path):
		wd = CreateObject("Word.Application", dynamic=True)
		#wd = GetActiveObject("Word.Application", dynamic=True)
		wd.Visible = True
		#Documents.Open (FileName, ConfirmConversions, ReadOnly, AddToRecentFiles, PasswordDocument, PasswordTemplate, Revert, WritePasswordDocument, WritePasswordTemplate, Format, Encoding, Visible, OpenConflictDocument, OpenAndRepair, DocumentDirection, NoEncodingDialog
		doc = wd.Documents.Open(path)
		wd.Activate()
		from time import sleep
		sleep(0.1)
		doc.Activate()
	
	