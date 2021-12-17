# changeInputDevice script for NVDA
# Copyright (C) 2021 Cyrille Bougot
# This file is covered by the GNU General Public License.

"""This global plugin creates a command to cycle through the audio output devices.
"""

import globalPluginHandler
import ui
import config
import nvwave
from scriptHandler import script
import addonHandler
import tones
from synthDriverHandler import getSynth, setSynth
import core

# Store original NVDA translation function.
nvdaTranslations = _

# Line to uncomment in case you convert it to add-on.
# addonHandler.initTranslation()


class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	
	@script(
		description = _("Cycle through audio devices"),
		gesture = "kb:NVDA+windows+D",
	)
	def script_cycleAudioOutputDevices(self, gesture):
		# Note: code mainly taken from NVDA gui/settingsDialogs.py (class SynthesizerSelectionDialog)
		deviceNames = nvwave.getOutputDeviceNames()
		# #11349: On Windows 10 20H1 and 20H2, Microsoft Sound Mapper returns an empty string.
		if deviceNames[0] in ("", "Microsoft Sound Mapper"):
			deviceNames[0] = nvdaTranslations("Microsoft Sound Mapper")
		try:
			selection = deviceNames.index(config.conf["speech"]["outputDevice"])
		except ValueError:
			selection = 0
		selection = (selection + 1) % len(deviceNames)
		audioDevice = deviceNames[selection]
		config.conf["speech"]["outputDevice"] = audioDevice
		
		# Reinitialize the tones module and the synth to update the audio device
		# On the contrary to what is written in onOK method of SynthesizerSelectionDialog,
		# reinitializing only tones module is not enough.
		# Note: we need to reinitialize synth out of a script to avoid an error if the current synth is silence.
		def runOutOfScript():
			tones.terminate()
			setSynth(getSynth().name)
			tones.initialize()
			ui.message(audioDevice)
		core.callLater(0, runOutOfScript)
		return
	