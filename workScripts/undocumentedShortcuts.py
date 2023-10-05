# Check shortcuts
# Copyright (C) 2023 Cyrille Bougot
# This file is covered by the GNU General Public License.

"""A script to check NVDA's shortcuts between doc and code.
This script list all the shortcuts defined in NVDA's code which are not listed in NVDA's user guide.
"""

import os
import re

# locale folder
pathRoot = os.path.join(
	os.getenv('homepath'),
	r"Documents\DevP\GIT\nvda",
)
pathSource = os.path.join(pathRoot, 'source')
pathDoc = os.path.join(pathRoot, 'user_docs', 'en', 'userGuide.t2t')

def pythonFilesGenerator(pathRoot):
	for path, folders, files in os.walk(pathRoot):
		for name in files:
			if not (name.endswith('.py') or name.endswith('.pyw')):
				continue
			yield os.path.join(path, name)

RE_SHORTCUT = r'(?:(?:nvda|alt|control|shift|windows)\+)+[a-z0-9]+'
RE_SHORTCUT_IN_CODE = r'kb(?:\(\desktop|laptop\))?:' + RE_SHORTCUT
REC_SHORTCUT = re.compile(RE_SHORTCUT, re.I)
REC_SHORTCUT_IN_CODE = re.compile(RE_SHORTCUT_IN_CODE, re.I)


def getSourceShortcuts(path):
	shortcuts = set()
	for file in pythonFilesGenerator(path):
		shortcuts.update(getSourceShortcutsInFile(file, inCode=True))
	return shortcuts

def getSourceShortcutsInFile(path, inCode):
	shortcuts = set()
	with open(path, 'r', encoding='utf8') as f:
		for line in f:
			line = line.lower().strip()
			if line.startswith('#'):
				continue
			recShortcut = REC_SHORTCUT_IN_CODE if inCode else REC_SHORTCUT
			shortcuts.update(recShortcut.findall(line))
	if inCode:
		shortcuts = [s.split(':', 1)[1] for s in shortcuts]
	return shortcuts


shortcutsInSource = getSourceShortcuts(pathSource)
shortcutsInDoc = getSourceShortcutsInFile(pathDoc, inCode=False)

srcNotDoc = '\n'.join(sorted(shortcutsInSource - shortcutsInDoc))
print('In source, not in doc:\n{}'.format(srcNotDoc))
