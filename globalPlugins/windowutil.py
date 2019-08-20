# -*- coding: UTF-8 -*-
#Window util  scripts for NVDA
#Copyright (C) 2019 Cyrille Bougot
#This file is covered by the GNU General Public License.

#This debug script allows to get various information on the current navigator object or associated window. It is an improvement of NVDA developer guide [https://www.nvaccess.org/files/nvda/documentation/developerGuide.html] example 3
#To use it, put it in the globalPlugins folder.

#Usage:
#NVDA+LeftArrow : Announce the navigator object's currently selected property.
#NVDA+Shift+LeftArrow or NVDA+Shift+RightArrow: select previous or next property and announce it for the navigator object.
#The list of supported properties is the following:
#name, role, state, value, windowClassName, windowControlID, windowHandle, pythonClass, pythonClassMRO
#If you have installed Speech history review and copying [https://addons.nvda-project.org/addons/speech_history.en.html] addon from Tyler Spivey and James Scholes, you may use it to copy and paste the announced property to review it;
#review via copy/paste is especially useful for pythonClassMRO since it may be long.


import globalPluginHandler
import ui
import api
import controlTypes

def _createDicControlTypesConstantes(prefix):
	dic = {}
	attributes = dir(controlTypes)
	for name in attributes:
		if name.startswith(prefix):
			dic[getattr(controlTypes, name)] = name[len(prefix):]
	#from logHandler import log
	#log.debug(dic)
	return dic
_DIC_ROLES = _createDicControlTypesConstantes('ROLE_')
_DIC_STATES = _createDicControlTypesConstantes('STATE_')

def getStateInfos(o):
	info = sorted(o.states)
	names = ', '.join([_DIC_STATES[i] for i in info])
	info = unicode(names) + u' (' + unicode(info) + u')'
	return info
			
	
class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	
	_INFO_TYPES = ['name',
		('role', lambda o: _DIC_ROLES[o.role] + u' (' + unicode(o.role) + u')'),
		('states', getStateInfos),
		'value',
		'windowClassName',
		'windowControlID',
		'windowHandle',
		('pythonClass', lambda o: type(o)),
		('pythonClassMRO', lambda o: str(type(o).mro()).replace('>, <', ',\r\n').replace('[<', '\r\n', 1).replace('>]',''))]
	
	def __init__(self):
		globalPluginHandler.GlobalPlugin.__init__(self)
		self.index = 0
		
	def script_announceObjectInfo(self, gesture):
		self.announceCurrentInfo()
	script_announceObjectInfo.__doc__=_("Announce current object property.")
	script_announceObjectInfo.category=_("WindowsUtil")
		
	def script_nextObjectInfo(self, gesture):
		self.index = (self.index + 1) % len(self._INFO_TYPES)
		self.announceCurrentInfo()
	script_nextObjectInfo.__doc__=_("Select next object property and announce it.")
	script_nextObjectInfo.category=_("WindowsUtil")
		
	def script_priorObjectInfo(self, gesture):
		self.index = (self.index - 1) % len(self._INFO_TYPES)
		self.announceCurrentInfo()
	script_priorObjectInfo.__doc__=_("Select prior object property and announce it.")
	script_priorObjectInfo.category=_("WindowsUtil")	
	
	def announceCurrentInfo(self):
		infoType = self._INFO_TYPES[self.index]
		nav = api.getNavigatorObject()
		if isinstance(infoType, str):
			info = getattr(nav, infoType)
		else:
			infoType, fun = infoType
			info = fun(nav)
		ui.message(infoType + u': ' + unicode(info))
		return
		if infoType == 'role':
			name = self._DIC_ROLES[info]
			info = name + u' (' + unicode(info) + u')'
		elif infoType == 'states':
			info = sorted(info)
			names = ', '.join([self._DIC_STATES[i] for i in info])
			info = unicode(names) + u' (' + unicode(info) + u')'
		ui.message(infoType + u': ' + unicode(info))
		
	
	__gestures = {
		"kb:NVDA+rightArrow": "announceObjectInfo",
		"kb:NVDA+shift+leftArrow": "priorObjectInfo",
		"kb:NVDA+shift+rightArrow": "nextObjectInfo",
		}