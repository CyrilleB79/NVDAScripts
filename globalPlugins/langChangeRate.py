# -*- coding: UTF-8 -*-
# Language change scripts for NVDA
# Copyright (C) 2021-2024 Cyrille Bougot
# This file is covered by the GNU General Public License.

"""A quick and dirty script allowing to modify the speech rate when a language other than the default language is detected.
To configure the modification factor, e.g. -40%, type in the console:
`config.conf['paramChangeUponLangChange']['rateChange'] = -40`
Not tested with rate boost on.
"""

import globalPluginHandler
import config
from scriptHandler import script
from types import MethodType
from logHandler import log
import speech
try:
	from speech.commands import LangChangeCommand, RateCommand
except ImportError:
	# For older versions such as NVDA 2019.2.1
	from speech import LangChangeCommand, RateCommand
# from speech.types import SpeechSequence
# from speech.priorities import Spri

try:
	originalSpeak = speech._manager.speak
	incompatible = False
except AttributeError:
	incompatible = True
	log.debugWarning('GlobalPlugin LangChangeRate incompatible: No speech._manager.speak')
# def speakNew(self, speechSequence: SpeechSequence, priority: Spri):
def speakNew(self, speechSequence, priority):
	autoDialectSwitching = config.conf['speech']['autoDialectSwitching']
	curLanguage = defaultLanguage = speech.getCurrentLanguage()
	prevLanguage = None
	defaultLanguageRoot = defaultLanguage.split('_')[0]
	seq = []
	for item in speechSequence:
		seq.append(item)
		if isinstance(item, LangChangeCommand):
			curLanguage = item.lang
			if not curLanguage or (not autoDialectSwitching and curLanguage.split('_')[0] == defaultLanguageRoot):
				curLanguage=defaultLanguage
			if curLanguage != prevLanguage:
				seq.extend(getLangChangeSequence(curLanguage, defaultLanguage))
				prevLanguage = curLanguage
	return originalSpeak(seq, priority)


def getLangChangeSequence(curLanguage, defaultLanguage):
	seq = []
	seq.append(LangChangeCommand(curLanguage))
	if curLanguage != defaultLanguage:
		seq.append(RateCommand(offset=config.conf['paramChangeUponLangChange']['rateChange']))
	else:
		seq.append(RateCommand())
	return seq


def disableIfIncompatible(c):
	if incompatible:
		return globalPluginHandler.GlobalPlugin
	return c


@disableIfIncompatible
class GlobalPlugin(globalPluginHandler.GlobalPlugin):

	def __init__(self, *args, **kwargs):
		global originalSpeak
		super(GlobalPlugin, self).__init__(*args, **kwargs)
		confspec = {
			'rateChange': 'integer(default=-30,min=-100,max=100)',
		}
		config.conf.spec['paramChangeUponLangChange'] = confspec
				
		speech._manager.speak = MethodType(speakNew, speech._manager)
		
	def terminate(self):
		speech._manager.speak = originalSpeak
		
