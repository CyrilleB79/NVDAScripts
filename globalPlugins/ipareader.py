# -*- coding: UTF-8 -*-

import addonHandler
import api
import globalPluginHandler
from synthDriverHandler import getSynthList, getSynthInstance
from scriptHandler import script
import textInfos
from speech import PhonemeCommand, speak
import importlib
import ui

#addonHandler.initTranslation()

IPA_TO_ESPEAK = {
	' ': '||',
	u'.': ' ', #zzz check
	'a': 'a',
	'b': 'b',
	#zzz 'c': 'c',
	'd': 'd',
	'e': 'e',
	'*': 'E',
	'f': 'f',
	'g': 'g',
	'h': 'h',
	'i': 'i',
	'j': 'j',
	'k': 'k',
	'l': 'l',
	'l̩': 'l-',
	'm': 'm',
	'm̩': 'm-',
	'n': 'n',
	'n̩': 'n-',
	'o': 'o',
	'p': 'p',
	'r': 'R', #Also 'R2', 'R3'.
	'r̩': 'r-',
	#zzz 'q': 'q',
	's': 's',
	't': 't',
	'u': 'u',
	'v': 'v',
	'w': 'w',
	'x': 'x',
	'y': 'y',
	'z': 'z',
	u'æ': '&',
	'ç': 'C',
	'ð': 'D',
	u'ø': 'Y',
	u'ħ': 'H',
	'ŋ': 'N',
	'ŋ̩': 'N-',
	u'œ': 'W',
	'œ̃': 'W~',
	'ɐ': 'a#',
	u'ɑ': 'A',
	'ɑ̃': 'A~',
	u'ɚ': 'R',
	u'ɔ': 'O',
	'ɔ̃': 'O~',
	'ɕ': 'S;',
	'ə': '@',
	u'ɛ': 'E',
	'ɛ̃': 'E~',
	#'ɜ': '', #zzz check
	u'ɟ': 'J',
	'ɡ': 'g',
	u'ɢ': 'G',
	u'ɣ': 'Q',
	'ɥ': 'j.',
	u'ɪ': 'I',
	u'ɫ': 'L',
	'ɬ': 'l#',
	'ɭ': 'l.',
	u'ɱ': 'M',
	u'ɲ': '*',
	'ɲ': 'n^',
	'ɳ': 'n.',
	'ɹ': 'r',
	'ɾ': '*', # Also '**'
	'ʀ': 'r"',
	'ʁ': 'Q"',
	'ʂ': 's.',
	'ʃ': 'S',
	u'ʊ': 'U',
	'ʋ': 'v#',
	u'ʌ': 'V',
	'ʍ': 'w#',
	'ʎ': 'l^',
	'ʐ': 'z.',
	'ʑ': 'z;',
	'ʒ': 'Z',
	'ʔ': '?',
	'ʝ': 'J^',
	'ˈ': "'",
	'ˌ': ',',
	'ː': ':', #zzz check
	'ɑ̃'[1]: '~', # combining tilda (771).
	'n̩'[1]: '-', # combining subscript vertical bar (809).
	u'Φ': 'P',
	u'β': 'B',
	'θ': 'T',
	u'χ': 'X',
	'‿': '',  # Liaison # zzz to be checked if any existing translation to eSpeak phoneme notation.
}

class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	scriptCategory = _("IPA Reader")

	def __init__(self, *args, **kwargs):
		super(GlobalPlugin, self).__init__(*args, **kwargs)
		self.ipaToSynthList = {}
		self.synthList = [s[0] for s in getSynthList()]
		for name in self.synthList:
			synth = importlib.import_module("synthDrivers.%s" % name, package="synthDrivers").SynthDriver
			if name == 'espeak':
				self.ipaToSynthList[name] = synth.IPA_TO_ESPEAK
				synth.IPA_TO_ESPEAK.update(IPA_TO_ESPEAK)
				
	def terminate(self, *args, **kwargs):
		for name in self.synthList:
			if name == 'espeak':
				synth = getSynthInstance(name)
				synth.IPA_TO_ESPEAK = self.ipaToSynthList[name]
		super(GlobalPlugin, self).terminate(*args, **kwargs)
		
	@script(
		gesture = "kb:NVDA+alt+P",
		description = _("Reads the selection as IPA phonems.")
	)
	def script_translateSelection(self, gesture):
		obj=api.getFocusObject()
		treeInterceptor=obj.treeInterceptor
		if hasattr(treeInterceptor,'TextInfo') and not treeInterceptor.passThrough:
			obj=treeInterceptor
		try:
			info=obj.makeTextInfo(textInfos.POSITION_SELECTION)
		except (RuntimeError, NotImplementedError):
			info=None
		if not info or info.isCollapsed:
			# Translators: user has pressed the shortcut key for reading selected text, but no text was actually selected.
			ui.message(_("no selection"))
			return
		speechSequence = []
		speechSequence.append(PhonemeCommand(info.text, 'Phoneme translation error'))
		speak(speechSequence)
