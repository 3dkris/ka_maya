import maya.cmds as cmds
import pymel.core as pymel

import ka_maya.ka_core as core

Tool = core.Tool
Setting = core.Setting

@Setting('recipient', valueType='enum', enumValues=[' world', ' nurse', 'bud'])
@Tool(label='Example Tool')
def exampleTool(recipient=1):
    """An example of a simple tool that can be added as menu items
    """
    if recipient == 0:
        print "Hello World"

    elif recipient == 1:
        print "Hello Nurse"

    else:
        print "Hello Bud"

