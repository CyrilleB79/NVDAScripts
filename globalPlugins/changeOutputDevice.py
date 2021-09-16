# changeInputDevice script for NVDA
# Copyright (C) 2021 Cyrille Bougot
# This file is covered by the GNU General Public License.

"""This global plugin creates a command to cycle through the audio output devices.
To use it, put it in the globalPlugins folder of the scratchpad.
"""

import globalPluginHandler
import ui
import config
import nvwave
from scriptHandler import script
import addonHandler

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
		# Reinitialize the tones and speech modules to update the audio device
		# On the contrary to what is written in onOK method of SynthesizerSelectionDialog,
		# reinitializing only tones module is not enough.
		import tones
		import speech
		speech.terminate()
		tones.terminate()
		tones.initialize()
		speech.initialize()
		ui.message(audioDevice)
	