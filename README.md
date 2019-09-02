# NVDAScripts

This repo gathers various scripts for NVDA screen reader that I have not (yet?) packaged as NVDA addon.
This may include potential features in development, (to be included later in an addon), debug scripts, test scripts, etc.

## Installation

* For NVDA up to 2018.4.1, copy the script you want to install in the corresponding subfolder (appModules or globalPlugins) in the user config folder of NVDA.
* For NVDA from 2019.1:
    * In the Advanced category of the settings dialog, check the "Enable loading custom code from Developer Scratchpad directory" option.
    * Press the "Open developer scratchpad directory" button
    * copy the script you want to install in the corresponding subfolder (appModules or globalPlugins) of the scratchpad folder.


## Scripts

### globalPlugins/autoLangSwitch.py

This script allows to cycles through speech automatic language detection modes off, language only and language+dialect with NVDA+shift+L shortcut.

### globalPlugins/beepError.py

This script allows NVDA to beep on error even in NVDA non-test versions.
To activate or de-activate beep error feature, press NVDA+control+alt+B

### globalPlugins/debugTool.py

This script allows to enable the stack trace logging of the speech function when pressing NVDA+control+alt+S. You may modify this file to pathc another function.
See all instructions in the file for details on usage.

### globalPlugins/windowutil.py

This debug script allows to get various information on the current navigator object or associated window. It is an improvement of [NVDA developer guide][2] example 3

Usage:

* NVDA+LeftArrow : Announce the navigator object's currently selected property.
* NVDA+Shift+LeftArrow or NVDA+Shift+RightArrow: select previous or next property and announce it for the navigator object.

The list of supported properties is the following:
name, role, state, value, windowClassName, windowControlID, windowHandle, pythonClass, pythonClassMRO

If you have installed [Speech history review and copying][3]  addon from Tyler Spivey and James Scholes, you may use it to copy and paste the announced property to review it;
review via copy/paste is especially useful for pythonClassMRO since it may be long.

## Removed scripts

### globalPlugins/startupOptionWorkaround.py

This script has been package as an add-on: [Startup option workaround add-on][4]

With Windows 10 1903 update, NVDA may start after logon even when this is disabled in General settings panel (cf. [#9528][1]).
This script does not fix the issue. However, as a work-around, it unloads NVDA just after startup in the case it should not have started up at all.
Of course, when [#9528][1] is fixed in NVDA (or in Windows), this script is useless and should be removed.

[1]: https://github.com/nvaccess/nvda/issues/9528

[2]: https://www.nvaccess.org/files/nvda/documentation/developerGuide.html

[3]: https://addons.nvda-project.org/addons/speech_history.en.html

[4]: https://github.com/CyrilleB79/startupOptionWorkaround

