# A part of NonVisual Desktop Access (NVDA)
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.
# Copyright (C) 2020 NV Access Limited, Cyrille Bougot

"""Color enhancer implementation based on the windows magnification API.
This implementation only works on Windows 8 and above.
"""

import vision
from vision import providerBase
import winVersion
from ctypes import Structure, windll, c_float, POINTER, WINFUNCTYPE, WinError
from ctypes.wintypes import BOOL
from autoSettingsUtils.driverSetting import BooleanDriverSetting, DriverSetting
from autoSettingsUtils.autoSettings import SupportedSettingType
from autoSettingsUtils.utils import StringParameterInfo
import wx
import gui
from logHandler import log
from typing import Optional, Type
import nvwave

# Import Magnification API stuff from screenCurtain; to be moved in a more generic module.
from visionEnhancementProviders.screenCurtain import MAGCOLOREFFECT, Magnification


# homogeneous matrix for a 4-space transformation (red, green, blue, opacity).
# https://docs.microsoft.com/en-gb/windows/win32/gdiplus/-gdiplus-using-a-color-matrix-to-transform-a-single-color-use

TRANSFORM_INVERT = MAGCOLOREFFECT()
for i in range(3):
	TRANSFORM_INVERT.transform[i][i] = -1.0
	TRANSFORM_INVERT.transform[4][i] = 1.0
TRANSFORM_INVERT.transform[3][3] = 1.0
TRANSFORM_INVERT.transform[4][4] = 1.0

TRANSFORM_TEST = MAGCOLOREFFECT()
mat = [
	[-0.3, -0.3, 0.0, 0.0, 0.0],
	[-0.3, -0.3, 0.0, 0.0, 0.0],
	[-0.3, -0.3, 0.0, 0.0, 0.0],
	[0.0, 0.0, 0.0, 1.0, 0.0],
	[1.0, 1.0, 0.0, 0.0, 1.0],
]
for i in range(5):
	for j in range(5):
		TRANSFORM_TEST.transform[i][j] = mat[i][j]



# Translators: Name for a vision enhancement provider that modifies the screen colors.
colorEnhancerTranslatedName = _("Color Enhancer")

# Translators: Description for a Color Enhancer setting that defines the color effect to apply.
colorEffectComboBoxText = _("&Color effect")


class ColorEnhancerSettings(providerBase.VisionEnhancementProviderSettings):

	#zzz colorEffect: bool
	availableColoreffects = {
		"inverseVideo": StringParameterInfo(id="inverseVideo", displayName=_("Inverse video")),
		"inverseBrightness": StringParameterInfo(id="inverseBrightness", displayName=_("Inverse brightness")),
		"blackOnWhite": StringParameterInfo(id="blackOnWhite", displayName=_("Black on white")),
		"whiteOnBlack": StringParameterInfo(id="whiteOnBlack", displayName=_("White on black")),
		"yellowOnBlack": StringParameterInfo(id="yellowOnBlack", displayName=_("Yellow on black")),
		"yellowOnBlue": StringParameterInfo(id="yellowOnBlue", displayName=_("Yellow on blue")),
	}

	@classmethod
	def getId(cls) -> str:
		return "colorEnhancer"

	@classmethod
	def getDisplayName(cls) -> str:
		return colorEnhancerTranslatedName

	def _get_supportedSettings(self) -> SupportedSettingType:
		return [
			DriverSetting(
				"colorEffect",
				colorEffectComboBoxText,
				defaultVal="inverseVideo"
			),
		]

class ColorEnhancerGuiPanel(
		gui.AutoSettingsMixin,
		gui.SettingsPanel,
):

	_enabledCheckbox: wx.CheckBox
	_enableCheckSizer: wx.BoxSizer

	from gui.settingsDialogs import VisionProviderStateControl

	def __init__(
			self,
			parent,
			providerControl: VisionProviderStateControl
	):
		self._providerControl = providerControl
		super().__init__(parent)

	def _buildGui(self):
		self.mainSizer = wx.BoxSizer(wx.VERTICAL)

		self._enabledCheckbox = wx.CheckBox(
			self,
			#  Translators: option to enable color enhancer in the vision settings panel
			label=_("Activate color enhancer")
		)
		isProviderActive = bool(self._providerControl.getProviderInstance())
		self._enabledCheckbox.SetValue(isProviderActive)

		self.mainSizer.Add(self._enabledCheckbox)
		self.mainSizer.AddSpacer(size=self.scaleSize(10))
		# this options separator is done with text rather than a group box because a groupbox is too verbose,
		# but visually some separation is helpful, since the rest of the options are really sub-settings.
		self.optionsText = wx.StaticText(
			self,
			# Translators: The label for a group box containing the color enhancer options.
			label=_("Options:")
		)
		self.mainSizer.Add(self.optionsText)
		self.lastControl = self.optionsText
		self.settingsSizer = wx.BoxSizer(wx.VERTICAL)
		self.makeSettings(self.settingsSizer)
		self.mainSizer.Add(self.settingsSizer, border=self.scaleSize(15), flag=wx.LEFT | wx.EXPAND)
		self.mainSizer.Fit(self)
		self.SetSizer(self.mainSizer)

	def getSettings(self) -> ColorEnhancerSettings:
		#zzz diff with highlighter
		return ColorEnhancerProvider.getSettings()

	def makeSettings(self, sizer: wx.BoxSizer):
		self.updateDriverSettings()
		#zzz to check
		self.Bind(wx.EVT_CHECKBOX, self._onCheckEvent)
		#zzz yyy added
		"""Evt to test
		'EVT_CHOICE',
		'EVT_COMBOBOX',
		'EVT_COMBOBOX_CLOSEUP',
		'EVT_COMBOBOX_DROPDOWN',
		
		'EVT_LISTBOX',
		'EVT_LISTBOX_DCLICK', 
		'EVT_LIST_ITEM_ACTIVATED', 
		'EVT_LIST_ITEM_FOCUSED', 
		'EVT_LIST_ITEM_SELECTED', 
		
		"""
		self.Bind(wx.EVT_CHOICE, self._onChoiceEvent)

	def onPanelActivated(self):
		#zzz diff with highlighter
		self.lastControl = self._enabledCheckbox

	def _onChoiceEvent(self, evt: wx.CommandEvent):
		import globalVars
		globalVars.dbg = self._enabledCheckbox
		if not self._enabledCheckbox.GetValue():
			return
		from tones import beep
		beep(440, 200)
		
		
	def _onCheckEvent(self, evt: wx.CommandEvent):
		from tones import beep
		beep(200, 200)
		if evt.GetEventObject() is self._enabledCheckbox:
			self._ensureEnableState(evt.IsChecked())

	def _ensureEnableState(self, shouldBeEnabled: bool):
		currentlyEnabled = bool(self._providerControl.getProviderInstance())
		if shouldBeEnabled and not currentlyEnabled:
			if not self._providerControl.startProvider():
				self._enabledCheckbox.SetValue(False)
		elif not shouldBeEnabled and currentlyEnabled:
			self._providerControl.terminateProvider()


class ColorEnhancerProvider(providerBase.VisionEnhancementProvider):
	_settings = ColorEnhancerSettings()

	@classmethod
	def canStart(cls):
		return winVersion.isFullScreenMagnificationAvailable()

	@classmethod
	def getSettingsPanelClass(cls) -> Optional[Type]:
		"""Returns the instance to be used in order to construct a settings panel for the provider.
		@return: Optional[SettingsPanel]
		@remarks: When None is returned, L{gui.settingsDialogs.VisionProviderSubPanel_Wrapper} is used.
		"""
		return ColorEnhancerGuiPanel

	@classmethod
	def getSettings(cls) -> ColorEnhancerSettings:
		return cls._settings

	def __init__(self):
		super().__init__()
		log.debug(f"Starting ColorEnhancer")
		Magnification.MagInitialize()
		try:
			#Magnification.MagSetFullscreenColorEffect(TRANSFORM_INVERT)
			Magnification.MagSetFullscreenColorEffect(TRANSFORM_TEST)
		except Exception as e:
			Magnification.MagUninitialize()
			raise e

	def terminate(self):
		log.debug(f"Terminating ColorEnhancer")
		try:
			super().terminate()
		finally:
			Magnification.MagUninitialize()

	def registerEventExtensionPoints(self, extensionPoints):
		# The color enhancer isn't interested in any events
		pass


VisionEnhancementProvider = ColorEnhancerProvider
