# DiffMaker: provide the result of a diff in a browseable message.
# Copyright (C) 2022 Cyrille Bougot
# This file is covered by the GNU General Public License.

"""A script providing diff information in browseable message.
"""

import globalPluginHandler
import ui
import addonHandler
import textInfos
from scriptHandler import script
import api
from logHandler import log
import gui
import core
import speech

import tempfile
import subprocess
import os
import wx
import re

# Line to uncomment in case you convert it to add-on.
# addonHandler.initTranslation()


RE_DIFF_HEADER = re.compile(r"^diff .*@@ -1 \+1 @@\n", re.DOTALL)


def textWithNoTailingNL(text):
	if text and text[-1] == '\n':
		text = text[:-1]
	return text

def diffLine(text1, text2, byCharacter):
	if not(len(textWithNoTailingNL(text1).split('\n')) == 1 and len(textWithNoTailingNL(text2).split('\n')) == 1):
		log.error('Multi-line diff not supported yet.')
		return
	d = tempfile.TemporaryDirectory()
	pathF1 = os.path.join(d.name, 'f1.txt')
	pathF2 = os.path.join(d.name, 'f2.txt')
	with open(pathF1, 'w', encoding='utf8') as f1:
		f1.write(text1)
	with open(pathF2, 'w', encoding='utf8') as f2:
		f2.write(text2)
	
	with open(os.path.join(d.name, 'out.txt'), 'w+') as fout:
		with open(os.path.join(d.name, 'err.txt'), 'w+') as ferr:
			cmdParams = ['git', 'diff', pathF1, pathF2]
			# Diff word-by-word
			cmdParams = ['git', 'diff', '-U0', '--word-diff=plain', '--minimal', '--no-index', '--', pathF1, pathF2]
			# Diff character by character
			cmdParams = ['git', 'diff', '-U0', '--word-diff=plain', '--word-diff-regex=.', '--minimal', '--no-index', '--', pathF1, pathF2]
			# Try porcelain format
			if byCharacter:
				cmdParams = ['git', 'diff', '-U0', '--word-diff=porcelain', '--word-diff-regex=.', '--minimal', '--no-index', '--', pathF1, pathF2]
			else:
				cmdParams = ['git', 'diff', '-U0', '--word-diff=porcelain', '--minimal', '--no-index', '--', pathF1, pathF2]
			out = subprocess.run(
				' '.join(cmdParams),
				stdin=subprocess.DEVNULL,
				stdout=fout,
				stderr=ferr,
				shell=True,
			)
			if out.returncode == 0:
				return False
			ferr.seek(0)
			err = ferr.read()
			if err:
				RuntimeError('Error when executing the following command:\n{cmd}\n{err}'.format(cmd=cmdParams, err=err))
			fout.seek(0)
			ui.browseableMessage(re.sub(
				RE_DIFF_HEADER,
				'',
				#out.stdout.decode('utf8'),
				#out.stdout.read(),
				fout.read()
			))
			return True


class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	
	@staticmethod
	def getCurrentLine():
		obj = api.getFocusObject()
		if obj.treeInterceptor is not None:
			obj = obj.treeInterceptor
		ti = obj.makeTextInfo(textInfos.POSITION_CARET)
		ti.collapse()
		ti.expand(textInfos.UNIT_LINE)
		return ti.text
	
	@script(
		description=_('Double-press to save the current line as first reference for the diff. Simple press to diff the previously saved text with the current line.'),
		gesture = "kb:nvda+alt+d",
	)
	def script_diffMaker(self, gesture):	
		text = self.getCurrentLine()
		wx.CallLater(0, lambda: self.popupMenu(text))
		
	def popupMenu(self, text):
		self.menu = wx.Menu()
		item = self.menu.Append(
			wx.ID_ANY,
			_("Define the &reference"),
			_("Define the reference"),
		)
		self.menu.Bind(wx.EVT_MENU, lambda evt: self.onDefineRef(text), item)
		item = self.menu.Append(
			wx.ID_ANY,
			_("Compare with reference by &character"),
			_("Compare with reference by character "),
		)
		self.menu.Bind(wx.EVT_MENU, lambda evt: self.onCompare(text, byCharacter=True), item)
		item = self.menu.Append(	
			wx.ID_ANY,
			_("Compare with reference by &word"),
			_("Compare with reference by word"),
		)
		self.menu.Bind(wx.EVT_MENU, lambda evt: self.onCompare(text, byCharacter=False), item)
		gui.mainFrame.prePopup()
		gui.mainFrame.sysTrayIcon.PopupMenu(self.menu)
		gui.mainFrame.postPopup()
		
	def onCompare(self, text, byCharacter):
		try:
			otherText = self.otherText
		except AttributeError:
			msg = _('No text previously saved')
			core.callLater(1, lambda: self.actionMessage(msg))
			return
		hasDiff = diffLine(otherText, text, byCharacter)
		if not hasDiff:
			msg = _('No difference')
			core.callLater(1, lambda: self.actionMessage(msg))
			return

	
	def onDefineRef(self, text):
		self.otherText = text
		msg = _('Text saved for diff')
		core.callLater(1, lambda: self.actionMessage(msg))
	
	@staticmethod
	def actionMessage(msg):
		speech.cancelSpeech()
		ui.message(msg)
		
				
