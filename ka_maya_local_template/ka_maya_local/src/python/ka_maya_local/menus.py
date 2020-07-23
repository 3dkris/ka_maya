import ka_maya.ka_menuWidget as ka_menuWidget
import ka_maya.ka_menuBase as ka_menuBase

import ka_maya_local.core as core

# add the the root menu ------------------------------------------------------
MENU_ROOT = ka_menuBase.MENU_ROOT

# EXAMPLE add menu item to existing menu
MENU_CREATE = ka_menuBase.MENU_CREATE
with MENU_CREATE.insertSubMenu(1, label='Example Submenu'):
    MENU_CREATE.add(core.exampleTool)

# EXAMPLE add menu item to a new submenu
MENU_EXAMPLE = ka_menuWidget.Ka_menu(label='EXAMPLE MENU', icon='visibility.png')
if MENU_EXAMPLE:
    MENU_EXAMPLE.add(core.exampleTool)

ka_menu = ka_menuBase.MenuBase()





