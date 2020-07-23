ka_maya
====

a collection of scripts, hotkeys, and tools to assist work done in maya.


Getting Started:
	1. Copy "ka_maya_local_template" somewhere and name it "ka_maya_local"
	2. Add the following to a shelf button with the following replacements
		-"PATH_TO_KA_MAYA" with the location of this package's "ka_maya\src\python" directory:
		-"PATH_TO_KA_MAYA_LOCAL" with the location directory copied in step 1:

"""
import sys
paths = [
    r'PATH_TO_KA_MAYA', # path to: ...\ka_maya\src\python
    r'PATH_TO_KA_MAYA_LOCAL', # path to: ...\ka_maya_local\src\python
    ]

for path in paths:
    if path not in sys.path:
        sys.path.append(path)

import ka_maya.ka_hotkeys as hotkeys; reload(hotkeys)
import ka_maya_local.hotkeys as local_hotkeys; reload(local_hotkeys)

import ka_maya_local.reload_package as reload_package; reload(reload_package) ;reload_package.reload_package()

local_hotkeys.Hotkeys.activateHotkey("all")
"""


	3. press that shelf button
	4. in maya menu Windows > settings/preferences > Hotkey Editor, Set hotkey set to kHotkeySet.
	5. close and reopen maya to save preferences.