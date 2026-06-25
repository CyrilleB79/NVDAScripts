# -*- coding: UTF-8 -*-
# Layered commands package for NVDA scratchpad.
# Copyright (C) 2026 Cyrille Bougot
# This file is covered by the GNU General Public License.

import globalPluginHandler
import globalVars
import globalCommands
import ui
from scriptHandler import script
from .layeredGestures import ScriptableObjectWithLayeredGestures

MAG_LAYERED_COMMANDS_LIST = [
	# A list of 4-tuples. Each 3-tuple contains:
	# - a gesture list
	# - a function returning the associated script
	# - if the command is available in secure mode.
	# - if the command can be repeated without exiting the layer
	(["numpadPlus"], lambda: globalCommands.commands.script_zoomIn, True, True),
	(["numpadMinus"], lambda: globalCommands.commands.script_zoomOut, True, True),
	(["leftArrow"], lambda: globalCommands.commands.script_panLeft, True, True),
	(["rightArrow"], lambda: globalCommands.commands.script_panRight, True, True),
	(["upArrow"], lambda: globalCommands.commands.script_panUp, True, True),
	(["downArrow"], lambda: globalCommands.commands.script_panDown, True, True),
	(["control+leftArrow"], lambda: globalCommands.commands.script_panToLeftEdge, True, True),
	(["control+rightArrow"], lambda: globalCommands.commands.script_panToRightEdge, True, True),
	(["control+upArrow"], lambda: globalCommands.commands.script_panToTopEdge, True, True),
	(["control+downArrow"], lambda: globalCommands.commands.script_panToBottomEdge, True, True),
	(["v"], lambda: getattr(globalCommands.commands, "script_moveMouseToView", None), True, False),
	(["i"], lambda: globalCommands.commands.script_cycleFilters, True, False),
	(["m"], lambda: globalCommands.commands.script_toggleFollowMouse, True, False),
	(["f"], lambda: globalCommands.commands.script_toggleFollowSystemFocus, True, False),
	(["r"], lambda: globalCommands.commands.script_toggleFollowReview, True, False),
	(["n"], lambda: globalCommands.commands.script_toggleFollowNavigatorObject, True, False),
	(["t"], lambda: globalCommands.commands.script_toggleAllFollow, True, False),
	(["shift+t"], lambda: globalCommands.commands.script_cycleTrackingModes, True, False),
	(["o"], lambda: globalCommands.commands.script_showEntireScreenOverview, True, False),
	(["h"], "help", False, False),
]

def getObj():
	zzz

class GlobalPlugin(
	ScriptableObjectWithLayeredGestures(
		scriptableObjectName=_("Magnifier commands"),
		entryPointGestures=["kb:NVDA+w"],
	),
	globalPluginHandler.GlobalPlugin,
):
	
	def __init__(self):
		super(GlobalPlugin, self).__init__(
			layerName="Mag_Main",
			layeredCommandsList=[
				(gestures, script, canRepeat)
				for (gestures, script, sec, canRepeat) in MAG_LAYERED_COMMANDS_LIST
				if (not globalVars.appArgs.secure) or sec
			],
		)
	