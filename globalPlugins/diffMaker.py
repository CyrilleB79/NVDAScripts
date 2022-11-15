# DiffMaker: provide the result of a diff in a browseable message.
# Copyright (C) 2022 Cyrille Bougot
# This file is covered by the GNU General Public License.

"""A script providing diff information in browseable message.
"""

import globalPluginHandler
import ui
import addonHandler
import textInfos
import scriptHandler
import api
from logHandler import log

import tempfile
#import shellapi
#from winUser import SW_SHOWNORMAL
import subprocess
import os



# Store original NVDA translation function.
nvdaTranslations = _

# Line to uncomment in case you convert it to add-on.
# addonHandler.initTranslation()


def diffLine(text1, text2):
	class D:
		name = ''
	d = D()
	d.name = r"C:\Users\CB232690\Documents\tmp\Toto"
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
			cmdParams = ['git', 'diff', '-U0', '--word-diff=plain', '--minimal', '--no-index', '--', pathF1, pathF2]
			out = subprocess.run(
				' '.join(cmdParams),
				stdout=subprocess.PIPE,
				stderr=ferr,
				shell=True,
			)
			ferr.seek(0)
			err = ferr.read()
			if err:
				log.error(f'Error when executing the following command:\n{cmdParams}\n{err}')
				return
			
			ui.browseableMessage(out.stdout.decode('utf8'))
	
	

class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	
	@scriptHandler.script(
		description=_('Double-press to save the current line as first reference for the diff. Simple press to diff the previously saved text with the current line.'),
		gesture = "kb:nvda+shift+control+d",
	)
	def script_diffMaker(self, gesture):
		obj = api.getFocusObject()
		if obj.treeInterceptor is not None:
			obj = obj.treeInterceptor
		ti = obj.makeTextInfo(textInfos.POSITION_CARET)
		ti.collapse()
		ti.expand(textInfos.UNIT_LINE)
		text = ti.text
		nRepeat = scriptHandler.getLastScriptRepeatCount()
		if nRepeat == 0:
			try:
				otherText = self.otherText
			except AttributeError:
				ui.message('No text previously saved')
				return
			diffLine(otherText, text)
		elif nRepeat == 1:
			self.otherText = text
			ui.message(_('Text saved for diff'))
		else:
			pass
		
				
