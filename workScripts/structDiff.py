# Structure difference
# Copyright (C) 2024 Cyrille Bougot
# This file is covered by the GNU General Public License.

"""A script to check the structure of NVDA's documentation files (either Changes of User Guide).
This script checks line by line if the locale version matches the English one.
The check of change log and versus French is hard coded in this script.
But the target language can be manually modified if needed, and only few modifications would be needed to check the User Guide instead of the Change log.
(anchor to be debugged)

To be executed, the script needs to be placed at the same level as the folder containing the screenreaderstranslations checkout, called "SRT".
"""



import os
import re

# Parameters to modify manually if needed.
CHECKOUT_FOLDER_NAME = "SRT"
LANGUAGE = "fr"
FILE = "userGuide"  # Either "changes" or "userGuide"


base = os.path.join(CHECKOUT_FOLDER_NAME, LANGUAGE)
chgFolder = os.path.join(base, 'changes-newRevisions')
chgFileName = 'changes.t2t'
chgFile = os.path.join(base, chgFileName)
ugFolder = os.path.join(base, 'userGuide-newRevisions')
ugFileName = 'userGuide.t2t'
ugFile = os.path.join(base, ugFileName)

def findLatestFolder(folder):
	latest = None
	for f in os.listdir(folder):
		num = int(f)
		if not latest or latest < num:
			latest = num
	if latest:
		return os.path.join(folder, str(latest))
	raise FileNotFoundError(f'No revision in {folder}')

def structDiff(enFile, localeFile):
	with open(enFile, encoding="utf8") as f1, open(localeFile, encoding="utf8") as f2:
		for (nLine, (enLine, locLine)) in enumerate(zip(f1, f2)):
			if nLine == 40:
				import pdb;pdb.set_trace()
				pass
			err = compareLines(enLine, locLine)
			if err is not None:
				print(f'Line {nLine+1}: {err}')
				print(f'English = {repr(enLine)}')
				print(f'Locale = {repr(locLine)}')
				#zzz import pdb;pdb.set_trace()

RE_LINE = """
	^
	(?P<headingSpaces>[ \t]*(?![ \t]))
	(
		((?P<preHeading>=+)\ [^=]+\ (?P=preHeading)(?P<anchor>\[[^]]+\])?)
		|(
			(?P<bullet>[-+]\ *)
			(.*)
		)
		|((?P<tableFirst>\|\|?)(?P<tableCells>(\ [^|]+ \|)+))
		|(?P<normalText>[^=|+-].*)
	)
	(?P<tailingSpaces>(?<![ \t])[ \t]*)
	$
"""
RE_LINE = re.compile(RE_LINE, re.VERBOSE)

def compareLines(l1, l2):
	"""Compare the structure of two lines and returns an appropriate error message if a difference is found.
	If no structural difference is found, returns None.
	"""
	if l1 == l2:
		return None
	if l1.endswith('\n'): l1 = l1[:-1]	
	if l2.endswith('\n'): l2 = l2[:-1]	
	m1 = RE_LINE.match(l1)
	m2 = RE_LINE.match(l2)
	if not m1 or not m2:
		return 'No match'
	if m1['headingSpaces'] != m2['headingSpaces']:
		return 'No same heading spaces'
	if m1['preHeading'] != m2['preHeading']:
		return 'No same pre-heading marker'
	if m1['anchor'] != m2['anchor']:
		return 'No same anchor'
		
	if m1['bullet'] != m2['bullet']:
		return 'No same bullet'
	if m1['tableFirst'] != m2['tableFirst']:
		return 'No same table first'
	nPipe1 = m1['tableCells'].count('|') if m1['tableCells'] else 0
	nPipe2 = m2['tableCells'].count('|') if m2['tableCells'] else 0
	if nPipe1 != nPipe2:
		return f'No same table celll number ({nPipe1} / {nPipe2})'
	if False and "zzz" and m1['tailingSpaces'] != m2['tailingSpaces']:
		return 'No same tailing spaces'
	
	return None

if FILE == "changes":
	enChgFile = os.path.join(findLatestFolder(chgFolder), chgFileName)
	structDiff(enChgFile, chgFile)
elif FILE == "userGuide":
	enUgFile = os.path.join(findLatestFolder(ugFolder), ugFileName)
	structDiff(enUgFile, ugFile)
else:
	print(f'Unsupported FILE: {FILE}')

