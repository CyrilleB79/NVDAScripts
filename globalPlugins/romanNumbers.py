# -*- coding: UTF-8 -*-
# Adapt the split word rule to exclude ordinal roman number.
# Copyright (C) 2021-2026 Cyrille Bougot
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
		super(GlobalPlugin, self).__init__(*args, **kw)
		self.dic = speechDictHandler.dictionaries["builtin"]
		# Patterns for NVDA < 2026.3
		originalPattern1 = '([A-Z])([A-Z][a-z])'
		newPattern1 = '([A-Z])(?!(?<=[IVXLCDM])[IVXLCDM][e])([A-Z][a-z])'
		# Patterns for NVDA 2026.3+ (following #20433)
		originalPattern2 = "(?=[A-Z][a-z])(?<=[A-Z])"
		newPattern2 = "(?=[A-Z][a-z])(?<=[A-Z])(?!(?<=[IVXLCDM])[IVXLCDM][e])"
		try:
			# Test against originalPattern2 for NVDA 2026.3+
			self.idx = [e.pattern for e in self.dic].index(originalPattern2)
			originalPattern = originalPattern2
			newPattern = newPattern2
		except ValueError:
			# Test against originalPattern1 for NVDA < 2026.3
			self.idx = [e.pattern for e in self.dic].index(originalPattern1)
			originalPattern = originalPattern2
			newPattern = newPattern2
		self.originalEntry = e = self.dic[self.idx]
		e = speechDictHandler.SpeechDictEntry(newPattern, e.replacement, e.comment, e.caseSensitive, type=e.type)
		self.dic[self.idx] = e

	def terminate(self):
		self.dic[self.idx] = self.originalEntry
		super(GlobalPlugin, self).terminate()
