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
from logHandler import log
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
		self.toggleVisualHighlighter()

	@script(
		# Translators: Describes a command.
		description=_("Toggles the state of the browse mode highlighter."),
		category=SCRCAT_VISION
	)
	def script_toggleBrowseModeHighlighter(self, gesture):
		self.toggleVisualHighlighter('BrowseMode')	

	@script(
		# Translators: Describes a command.
		description=_("Toggles the state of the focus highlighter."),
		category=SCRCAT_VISION
	)
	def script_toggleFocusHighlighter(self, gesture):
		self.toggleVisualHighlighter('Focus')	

	@script(
		# Translators: Describes a command.
		description=_("Toggles the state of the navigator highlighter."),
		category=SCRCAT_VISION
	)
	def script_toggleNavigatorHighlighter(self, gesture):
		self.toggleVisualHighlighter('Navigator')	
	
	def toggleHighlightSetting(self, settings, highlighter):
		import ui
		if highlighter is None:
			highlighters = ['BrowseMode', 'Focus', 'Navigator']
			enabled = not any(getattr(settings, f'highlight{h}') for h in highlighters)
		else:
			highlighters = [highlighter]
			enabled = not getattr(settings, f'highlight{highlighter}')
		for highlighter in highlighters:
			attrName = f'highlight{highlighter}'
			setattr(settings, attrName, enabled)
	
	def toggleVisualHighlighter(self, highlighter=None):
		from visionEnhancementProviders.NVDAHighlighter import NVDAHighlighter
		nvdaHighlighterId = NVDAHighlighter.getSettings().getId()
		nvdaHighlighterInfo = vision.handler.getProviderInfo(nvdaHighlighterId)
		alreadyRunning = bool(vision.handler.getProviderInstance(nvdaHighlighterInfo))
		#zzz ui.message(f'AlreadyRunning = {alreadyRunning}')

		# Enable if not running
		if not alreadyRunning:
			# Check if visual highlighter is available, exit early if not.
			if not nvdaHighlighterInfo.providerClass.canStart():
				# Translators: Reported when the visual highlighter is not available.
				message = _("Visual highlighter not available")
				ui.message(message, speechPriority=speech.priorities.Spri.NOW)
				return
			# Translators: Reported when the visual highlighter is enabled.
			try:
				vision.handler.initializeProvider(
					nvdaHighlighterInfo,
				)
				nvdaHighlighterInfo.providerClass.enableInConfig(True)
			except Exception:
				log.error("Visual Highlighter initialization error", exc_info=True)
				# Translators: Reported when the visual highlighter could not be enabled.
				ui.message(_("Could not enable visual highlighter"))
		providerInst = vision.handler.getProviderInstance(nvdaHighlighterInfo)
		settings = providerInst.getSettings()
		if True:
			self.toggleHighlightSetting(settings, highlighter)
			if highlighter is None:
				if settings.highlightBrowseMode and settings.highlightFocus and settings.highlightNavigator:
					# Translators: Reported when the visual highlighter is enabled.
					message = _("Visual highlighter enabled")
				elif not (settings.highlightBrowseMode or settings.highlightFocus or settings.highlightNavigator):
					# Translators: Reported when the visual highlighter is disabled.
					message = _("Visual highlighter disabled")
				else:
					raise RuntimeError(f'bm:{settings.highlightBrowseMode}, focus:{settings.highlightFocus}, nav:{settings.highlightNavigator}')
			else:
				if getattr(settings, f'highlight{highlighter}'):
					message = _(f"{highlighter} highlighter enabled")
				else:
					message = _(f"{highlighter} highlighter disabled")
		else:
			settings.highlightBrowseMode = True
			settings.highlightFocus = True
			settings.highlightNavigator = True
		settings.saveSettings()
			
		# Disable if running but no highlighter enabled anymore.
		if not (settings.highlightBrowseMode or settings.highlightFocus or settings.highlightNavigator):
			try:
				vision.handler.terminateProvider(nvdaHighlighterInfo)
			except Exception:
				# If the visual highlighter was enabled, we do not expect exceptions.
				log.error("Visual highlighter termination error", exc_info=True)
				# Translators: Reported when the visual highlighter could not be enabled.
				message = _("Could not disable visual highlighter")
		ui.message(message, speechPriority=speech.priorities.Spri.NOW)
