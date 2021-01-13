# -*- coding: UTF-8 -*-
# visualHighlighterToggler
# A script to toggle NVDA Visual Highlighter.
# Copyright (C) 2021 Cyrille Bougot
# This file is covered by the GNU General Public License.

"""A script (unassigned by default) to toggle Visual Highlighter.
"""

import globalPluginHandler
#import config
from globalCommands import SCRCAT_VISION
from scriptHandler import script
#import logHandler
import vision
import ui
import speech

class GlobalPlugin(globalPluginHandler.GlobalPlugin):

	@script(
		# Translators: Describes a command.
		description=_("Toggles the state of the visual highlighter."),
		category=SCRCAT_VISION
	)
	def script_toggleVisualHighlighter(self, gesture):
		from visionEnhancementProviders.NVDAHighlighter import NVDAHighlighter
		nvdaHighlighterId = NVDAHighlighter.getSettings().getId()
		nvdaHighlighterInfo = vision.handler.getProviderInfo(nvdaHighlighterId)
		alreadyRunning = bool(vision.handler.getProviderInstance(nvdaHighlighterInfo))

		# Disable if running
		if alreadyRunning:
			# Translators: Reported when the visual highlighter is disabled.
			message = _("Visual highlighter disabled")
			try:
				vision.handler.terminateProvider(nvdaHighlighterInfo)
			except Exception:
				# If the visual highlighter was enabled, we do not expect exceptions.
				log.error("Visual highlighter termination error", exc_info=True)
				# Translators: Reported when the visual highlighter could not be enabled.
				message = _("Could not disable visual highlighter")
			finally:
				ui.message(message, speechPriority=speech.priorities.Spri.NOW)
				return
		else:
			# Check if visual highlighter is available, exit early if not.
			if not nvdaHighlighterInfo.providerClass.canStart():
				# Translators: Reported when the visual highlighter is not available.
				message = _("Visual highlighter not available")
				ui.message(message, speechPriority=speech.priorities.Spri.NOW)
				return

			# Translators: Reported when the visual highlighter is enabled.
			enableMessage = _("Visual highlighter enabled")
			try:
				vision.handler.initializeProvider(
					nvdaHighlighterInfo,
				)
				nvdaHighlighterInfo.providerClass.enableInConfig(True)
				providerInst = vision.handler.getProviderInstance(nvdaHighlighterInfo)
				settings = providerInst.getSettings()
				settings.highlightBrowseMode = True
				settings.highlightFocus = True
				settings.highlightNavigator = True
				settings.saveSettings()
			except Exception:
				log.error("Visual Highlighter initialization error", exc_info=True)
				# Translators: Reported when the visual highlighter could not be enabled.
				enableMessage = _("Could not enable visual highlighter")
			finally:
				ui.message(enableMessage, speechPriority=speech.priorities.Spri.NOW)

	
	