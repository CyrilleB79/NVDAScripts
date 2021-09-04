# NVDAScripts

This repo gathers various scripts for NVDA screen reader that I have not (yet?) packaged as NVDA addon.
This may include potential features in development, (to be included later in an addon), debug scripts, test scripts, etc.
It also includes some configuration files.

## Installation

* For NVDA up to 2018.4.1, copy the script you want to install in the corresponding subfolder (appModules or globalPlugins) in the user config folder of NVDA.
* For NVDA from 2019.1:
    * In the Advanced category of the settings dialog, check the "Enable loading custom code from Developer Scratchpad directory" option.
    * Press the "Open developer scratchpad directory" button
    * copy the script you want to install in the corresponding subfolder (appModules or globalPlugins) of the scratchpad folder.


## globalPlugins Scripts

### globalPlugins/autoLangSwitch.py

This script allows to cycles through speech automatic language detection modes off, language only and language+dialect with NVDA+shift+L shortcut.

### globalPlugins/langChangeRate.py

A quick and dirty script allowing to modify the speech rate when a language other than the default language is detected.
To configure the modification factor, e.g. -40%, type in the console:
`config.conf['paramChangeUponLangChange']['rateChange'] = -40`
Not tested with rate boost on.

### globalPlugins/ocrPdf.py

This script allows to OCR an opened PDF in Adobe Reader with MS word.
Before first use, open a PDF manually in MS Word. If you did not disable it before a warning dialog will appear with the following message:
"Word will now convert your PDF to an editable Word document.  This may take a while.  The resulting Word document will be optimized to allow you to edit the text, so it might not look exactly like the original PDF, especially if the original file contained lots of graphics."
Check the checkbox "Don't show this message again" and validate by clicking "OK".
If you want to restore Word's original behaviour with this dialog appearing, opan the following registry key:
HKEY_CURRENT_USER\Software\Microsoft\Office\16.0\Word\Options
And delete the delete the DisableConvertPdfWarning value or set it to 0.
Work is in course to support the conversion from a selected file in Windows Explorer but this is not yet functional.

### visualHighlighterToggler.py

This module adds script (unassigned by default) to toggle Visual Highlighter.

## appModules scripts

### appModules/matlab.py

A script to issue some commands in Matlab console by just pressing a keystroke. E.g. press F5 to issue "dbcont" command.
The lib folder contains a dependancy. Thus, it has also to be copied in the scratchpad folder.

## Configuration files

### symbols-fr.dic

My French symbol configuration file. Specifically it includes the following extra character description:
- additional latin characters with diacritics
- IPA characters
- greek characters with diacritics (the greek characters without diacritic are already included in NVDA's French symbols.dic)
- cyrillic characters
- a few musical symbols

## Removed scripts

### Debug and test scripts

The following debug and test scripts have been included in the [NVDA Dev & Test Toolbox][3] addon.
* globalPlugins/beepError.py
* globalPlugins/debugHelpMode.py
* globalPlugins/debugTool.py
* globalPlugins/windowutil.py

### globalPlugins/startupOptionWorkaround.py

This script has been packaged as an add-on: [Startup option workaround add-on][4] that is itself deprecated.

With Windows 10 1903 update, NVDA may start after logon even when this is disabled in General settings panel (cf. [#9528][1]).
This script does not fix the issue. However, as a work-around, it unloads NVDA just after startup in the case it should not have started up at all.
Of course, when [#9528][1] is fixed in NVDA (or in Windows), this script is useless and should be removed.

[1]: https://github.com/nvaccess/nvda/issues/9528

[3]: https://github.com/CyrilleB79/NVDA-Dev-Test-Toolbox

[4]: https://github.com/CyrilleB79/startupOptionWorkaround

