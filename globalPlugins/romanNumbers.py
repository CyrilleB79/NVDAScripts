# Adapt the split word rule to exclude ordinal roman number.
# Copyright (C) 2021 Cyrille Bougot
# This file is covered by the GNU General Public License.

"""This script adapts the CamelCase word split rule to exclude the cases of ordinal roman numbers used in French.
E.g. "XXIe siècle", "IIIe République", etc.
"""

import globalPluginHandler
import addonHandler
import speechDictHandler


# Store original NVDA translation function.
nvdaTranslations = _

# Line to uncomment in case you convert it to add-on.
# addonHandler.initTranslation()


class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	
	def __init__(self, *args, **kw):
		super().__init__(*args, **kw)
		self.dic = speechDictHandler.dictionaries["builtin"]
		originalPattern = '([A-Z])([A-Z][a-z])'
		self.idx = [e.pattern for e in self.dic].index(originalPattern)
		self.originalEntry = e = self.dic[self.idx]
		newPattern = '([A-Z])(?![IVXLCDM][e])([A-Z][a-z])'
		e = speechDictHandler.SpeechDictEntry(newPattern, e.replacement, e.comment, e.caseSensitive, type=e.type)
		self.dic[self.idx] = e
		
	def terminate(self):
		self.dic[self.idx] = self.originalEntry
		super().terminate()
