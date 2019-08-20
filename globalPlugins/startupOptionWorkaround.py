#startupOptionWorkaround.py
#A part of NonVisual Desktop Access (NVDA)
#Copyright (C) 2019 Cyrille Bougot
#This file is covered by the GNU General Public License.
#See the file COPYING for more details.

"""Script to work around the following issue 
With Windows 10 1903 update, NVDA may start after logon even when this is disabled in General settings panel (cf. #9528 [https://github.com/nvaccess/nvda/issues/9528]).
This script does not fix the issue. However, as a work-around, it unloads NVDA just after startup in the case it should not have started up at all.
Of course, when [#9528][1] is fixed in NVDA (or in Windows), this script is useless and should be removed.
"""

import globalPluginHandler
import config
import globalVars
import core
import wx

class GlobalPlugin(globalPluginHandler.GlobalPlugin):

	def __init__(self, *args, **kwargs):
		super(GlobalPlugin, self).__init__(*args, **kwargs)
		if ((not config.getStartAfterLogon())
		and globalVars.appArgs.easeOfAccess == True):
			core.callLater(0,wx.GetApp().ExitMainLoop)
	