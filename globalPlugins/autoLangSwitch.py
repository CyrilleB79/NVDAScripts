# -*- coding: UTF-8 -*-
#Auto-language switching command scripts for NVDA
#Copyright (C) 2019 Cyrille Bougot
#This file is covered by the GNU General Public License.

#This script allows to cycles through speech automatic language detection modes off, language only and language+dialect with NVDA+shift+L shortcut.

import globalPluginHandler
import ui
import config
from globalCommands import SCRCAT_SPEECH

class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	
	def script_cycleSpeechAutomaticLanguageSwitching(self,gesture):
		if config.conf["speech"]["autoLanguageSwitching"]:
			if config.conf["speech"]["autoDialectSwitching"]:
				# Translators: The message announced when toggling the auto language switching speech setting.
				state = _("Automatic language switching off")
				config.conf["speech"]["autoLanguageSwitching"]=False
				config.conf["speech"]["autoDialectSwitching"] = False
			else:
				state = _("Automatic language and dialect switching on")
				config.conf["speech"]["autoDialectSwitching"] = True
		else:
			# Translators: The message announced when toggling the auto language switching speech setting.
			state = _("Automatic language switching on")
			config.conf["speech"]["autoLanguageSwitching"]=True
			config.conf["speech"]["autoDialectSwitching"] = False
		ui.message(state)
	# Translators: Input help mode message for toggle automatic language switching command.
	script_cycleSpeechAutomaticLanguageSwitching.__doc__=_("Cycles through speech automatic language detection modes off, language only and language and dialect.")
	script_cycleSpeechAutomaticLanguageSwitching.category=SCRCAT_SPEECH
	
	__gestures = {
		"kb:NVDA+shift+L": "cycleSpeechAutomaticLanguageSwitching"
		}
		