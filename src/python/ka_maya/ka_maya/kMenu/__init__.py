
#====================================================================================
#====================================================================================
#
# kMenu
#
# DESCRIPTION:
#   Custom Menu system
#
# DEPENDENCEYS:
#   PyQt4 or PySide
#   Maya
#
#
# AUTHOR:
#   Kris Andrews (3dkris@3dkris.com)
#
#====================================================================================
#Redistribution and use in source and binary forms, with or without
#modification, are permitted provided that the following conditions are
#met:

    #(1) Redistributions of source code must retain the above copyright
    #notice, this list of conditions and the following disclaimer.

    #(2) Redistributions in binary form must reproduce the above copyright
    #notice, this list of conditions and the following disclaimer in
    #the documentation and/or other materials provided with the
    #distribution.

    #(3)The name of the author may not be used to
    #endorse or promote products derived from this software without
    #specific prior written permission.

#THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR
#IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
#WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#DISCLAIMED. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT,
#INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
#(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
#SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
#HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
#STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING
#IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
#POSSIBILITY OF SUCH DAMAGE.
#====================================================================================


import os
#import PyQt4
#from PyQt4 import PyQt.QtGui, PyQt.QtCore, uic
import time
import inspect

import pymel.core as pymel
import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMayaUI as OpenMayaUI

import ka_maya.ka_qtWidgets as ka_qtWidgets
PyQt = ka_qtWidgets.PyQt
QtGui = ka_qtWidgets.QtGui
QtCore = ka_qtWidgets.QtCore
QtWidgets = ka_qtWidgets.QtWidgets

import ka_maya.ka_core as ka_maya
import ka_maya.ka_preference as ka_preference
import ka_maya.ka_skinCluster as ka_skinCluster
import ka_maya.ka_weightPainting as ka_weightPainting
import ka_maya.ka_attrTool.ka_attrTool_UI as ka_attrTool_UI
import ka_maya.ka_attrTool.attrCommands as attrCommands
import ka_maya.ka_context as ka_context
import ka_maya.ka_util as ka_util

QICON_DICT = {}

PARENT_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), "..",))
ICON_FOLDER = os.path.abspath(os.path.join(PARENT_FOLDER, "icons",))

TOP_BAR_HEIGHT = 12
MIN_WIDTH = 50
MIN_HEIGHT = 200
MENU_ITEM_MIN_HEIGHT = 20
MENU_ITEM_EXTRA_WIDTH = 30

ICON_BOARDER_BUFFER_PERCENT = 0.25 # percent of icon which is buffer between the icon and boarder
ICON_SIZE = int(MENU_ITEM_MIN_HEIGHT*(1-ICON_BOARDER_BUFFER_PERCENT))
ICON_BUFFER_BOARDER_PIXELS = int((MENU_ITEM_MIN_HEIGHT*ICON_BOARDER_BUFFER_PERCENT) * 0.5)

QRECTANLE_ICON_FRONT = PyQt.QtCore.QRect(ICON_BUFFER_BOARDER_PIXELS, ICON_BUFFER_BOARDER_PIXELS, ICON_SIZE, ICON_SIZE)
QRECTANLE_ICON_BACK = PyQt.QtCore.QRect(0, 0, ICON_SIZE, ICON_SIZE)

# KMENU COLORS
QCOLOR_BACKGROUND = PyQt.QtWidgets.QColor(23, 25, 27)
QCOLOR_MENU_BORDERLINES = PyQt.QtWidgets.QColor(55, 55, 55)

# MENU ITEM BRUSH
QCOLOR_MENUITEM_BACKGROUND = PyQt.QtWidgets.QColor(43, 45, 47)
QCOLOR_MENUITEM_BACKGROUND_SHADOW = PyQt.QtWidgets.QColor(30, 30, 30)
QCOLOR_MENUITEM_BACKGROUND_HILIGHT = PyQt.QtWidgets.QColor(65, 65, 65,)

gradient = PyQt.QtWidgets.QLinearGradient()
gradient.setStart(0, 0)
gradient.setFinalStop(0, MENU_ITEM_MIN_HEIGHT)
gradientEndSize = 2.0 / MENU_ITEM_MIN_HEIGHT # pixels from ends of gradient to the middles

gradient.setColorAt(0.0, QCOLOR_MENUITEM_BACKGROUND_HILIGHT)
gradient.setColorAt(gradientEndSize, QCOLOR_MENUITEM_BACKGROUND)
gradient.setColorAt(1.0-gradientEndSize, QCOLOR_MENUITEM_BACKGROUND)
gradient.setColorAt(1.0, QCOLOR_MENUITEM_BACKGROUND_SHADOW)

QBRUSH_MENUITEM = PyQt.QtWidgets.QBrush(gradient)


# MENU ITEM BRUSH ALTERNATE
QCOLOR_MENUITEM_ALTERNATE_BACKGROUND = PyQt.QtWidgets.QColor(53, 55, 57)
QCOLOR_MENUITEM_ALTERNATE_BACKGROUND_SHADOW = PyQt.QtWidgets.QColor(30, 30, 30)
QCOLOR_MENUITEM_ALTERNATE_BACKGROUND_HILIGHT = PyQt.QtWidgets.QColor(75, 75, 75)

gradient = PyQt.QtWidgets.QLinearGradient()
gradient.setStart(0, 0)
gradient.setFinalStop(0, MENU_ITEM_MIN_HEIGHT)

gradient.setColorAt(0.0, QCOLOR_MENUITEM_ALTERNATE_BACKGROUND_HILIGHT)
gradient.setColorAt(gradientEndSize, QCOLOR_MENUITEM_ALTERNATE_BACKGROUND)
gradient.setColorAt(1.0-gradientEndSize, QCOLOR_MENUITEM_ALTERNATE_BACKGROUND)
gradient.setColorAt(1.0, QCOLOR_MENUITEM_ALTERNATE_BACKGROUND_SHADOW)

QBRUSH_MENUITEM_ALTERNATE = PyQt.QtWidgets.QBrush(gradient)


# MENU ITEM HILIGHTED
QCOLOR_MENU_ITEM_UNDERMOUSE = PyQt.QtWidgets.QColor(0, 96, 179)
QCOLOR_MENU_ITEM_UNDERMOUSE_SHADOW = PyQt.QtWidgets.QColor(18, 50, 123)
QCOLOR_MENU_ITEM_UNDERMOUSE_HILIGHT = PyQt.QtWidgets.QColor(92, 137, 255)
QCOLOR_MENU_BORDERLINES_UNDERMOUSE = PyQt.QtWidgets.QColor(92, 137, 255)
QCOLOR_MENU_BORDERLINES_PINNED = PyQt.QtWidgets.QColor(5, 115, 185)

gradient = PyQt.QtWidgets.QLinearGradient()
gradient.setStart(0, 0)
gradient.setFinalStop(0, MENU_ITEM_MIN_HEIGHT)

gradient.setColorAt(0.0, QCOLOR_MENU_ITEM_UNDERMOUSE_HILIGHT)
gradient.setColorAt(gradientEndSize, QCOLOR_MENU_ITEM_UNDERMOUSE)
gradient.setColorAt(1.0-gradientEndSize, QCOLOR_MENU_ITEM_UNDERMOUSE)
gradient.setColorAt(1.0, QCOLOR_MENU_ITEM_UNDERMOUSE_SHADOW)

QBRUSH_MENUITEM_HILIGHT = PyQt.QtWidgets.QBrush(gradient)


QCOLOR_ICON_FILL = PyQt.QtWidgets.QColor(175, 175, 175)
QCOLOR_TOP_BAR = PyQt.QtWidgets.QColor(75, 75, 75)
QCOLOR_TEXT = PyQt.QtWidgets.QColor(75, 75, 75)
QCOLOR_BLACK = PyQt.QtWidgets.QColor(0, 0, 0,)
QCOLOR_WHITE = PyQt.QtWidgets.QColor(255, 255, 255,)
QCOLOR_TRANSPARENT = PyQt.QtWidgets.QColor(255, 255, 255, 255)
QCOLOR_MENU_ITEM_TEXT = PyQt.QtWidgets.QColor(205, 205, 205)
QCOLOR_MENU_ITEM_TEXT_DIM = PyQt.QtWidgets.QColor(145, 145, 145)
QCOLOR_MENU_DOCSTRING_TEXT = PyQt.QtWidgets.QColor(92, 137, 255)
QCOLOR_MENU_INPUTITEM_TEXT = PyQt.QtWidgets.QColor(132, 187, 175)
QCOLOR_MENU_INPUTITEM_BACKGROUND = PyQt.QtWidgets.QColor(72, 117, 105)
QCOLOR_MENU_SEPARATOR_TEXT = PyQt.QtWidgets.QColor(160, 160, 160)

QFONT_LABEL = PyQt.QtGui.QFont()
QFONT_LABEL.setPixelSize(12)
QPALETTE_LABEL = PyQt.QtWidgets.QPalette()
QPALETTE_LABEL.setColor(PyQt.QtWidgets.QPalette.ButtonText, QCOLOR_MENU_ITEM_TEXT)


QPALETTE_TOOLWIDGET = PyQt.QtWidgets.QPalette()
QPALETTE_TOOLWIDGET.setColor(PyQt.QtWidgets.QPalette.ButtonText, QCOLOR_WHITE)
QPALETTE_TOOLWIDGET.setColor(PyQt.QtWidgets.QPalette.Button, QCOLOR_MENUITEM_ALTERNATE_BACKGROUND)
QPALETTE_TOOLWIDGET.setColor(PyQt.QtWidgets.QPalette.Text, QCOLOR_WHITE)
QPALETTE_TOOLWIDGET.setColor(PyQt.QtWidgets.QPalette.BrightText, QCOLOR_WHITE)
QPALETTE_TOOLWIDGET.setColor(PyQt.QtWidgets.QPalette.Foreground, QCOLOR_WHITE)

QFONT_DOCSTRING = PyQt.QtGui.QFont()
QFONT_DOCSTRING.setPixelSize(12)
QPALETTE_DOCSTRING = PyQt.QtWidgets.QPalette()
QPALETTE_DOCSTRING.setColor(PyQt.QtWidgets.QPalette.ButtonText, QCOLOR_MENU_DOCSTRING_TEXT)
QPALETTE_DOCSTRING.setColor(PyQt.QtWidgets.QPalette.Text, QCOLOR_MENU_DOCSTRING_TEXT)
QPALETTE_DOCSTRING.setColor(PyQt.QtWidgets.QPalette.BrightText, QCOLOR_MENU_DOCSTRING_TEXT)
QPALETTE_DOCSTRING.setColor(PyQt.QtWidgets.QPalette.Foreground, QCOLOR_MENU_DOCSTRING_TEXT)

QFONT_SEPARATOR = PyQt.QtGui.QFont()
QFONT_SEPARATOR.setPixelSize(10)
QPALETTE_SEPARATOR = PyQt.QtWidgets.QPalette()
QPALETTE_SEPARATOR.setColor(PyQt.QtWidgets.QPalette.Foreground, QCOLOR_MENU_SEPARATOR_TEXT)

QPALETTE_INPUTITEM = PyQt.QtWidgets.QPalette()
QPALETTE_INPUTITEM.setColor(PyQt.QtWidgets.QPalette.Window, QCOLOR_MENU_INPUTITEM_BACKGROUND)
QPALETTE_INPUTITEM.setColor(PyQt.QtWidgets.QPalette.Background, QCOLOR_MENU_INPUTITEM_BACKGROUND)
QPALETTE_INPUTITEM.setColor(PyQt.QtWidgets.QPalette.Foreground, QCOLOR_MENU_INPUTITEM_TEXT)
QPALETTE_INPUTITEM.setColor(PyQt.QtWidgets.QPalette.Base, QCOLOR_MENU_INPUTITEM_BACKGROUND)
QPALETTE_INPUTITEM.setColor(PyQt.QtWidgets.QPalette.AlternateBase, QCOLOR_MENU_INPUTITEM_BACKGROUND)
QPALETTE_INPUTITEM.setColor(PyQt.QtWidgets.QPalette.ToolTipBase, QCOLOR_MENU_INPUTITEM_BACKGROUND)
QPALETTE_INPUTITEM.setColor(PyQt.QtWidgets.QPalette.ToolTipText, QCOLOR_MENU_INPUTITEM_BACKGROUND)
QPALETTE_INPUTITEM.setColor(PyQt.QtWidgets.QPalette.Text, QCOLOR_WHITE)
QPALETTE_INPUTITEM.setColor(PyQt.QtWidgets.QPalette.Button, QCOLOR_MENU_INPUTITEM_BACKGROUND)
QPALETTE_INPUTITEM.setColor(PyQt.QtWidgets.QPalette.ButtonText, QCOLOR_WHITE)
QPALETTE_INPUTITEM.setColor(PyQt.QtWidgets.QPalette.BrightText, QCOLOR_WHITE)



def getIcon(iconValue):
    iconHash = str(iconValue)
    if iconHash in QICON_DICT:
            return QICON_DICT[iconHash]

    if isinstance(iconValue, list) or isinstance(iconValue, tuple):

        QPixMap = PyQt.QtGui.QPixmap(ICON_SIZE, ICON_SIZE)
        QPixMap.fill(PyQt.QtWidgets.QColor(int(255*iconValue[0]), int(255*iconValue[1]), int(255*iconValue[2]),))
        QIcon = PyQt.QtGui.QIcon(QPixMap)
        QICON_DICT[iconHash] = QIcon
        return QIcon


    elif isinstance(iconValue, basestring):
        imageName = iconValue
        imageNameSplit = iconValue.split('.')

        QPixMap = PyQt.QtGui.QPixmap(ICON_SIZE, ICON_SIZE)

        smallFilePath = os.path.join(ICON_FOLDER, '%s_small.%s' % (imageNameSplit[0], imageNameSplit[1]))
        if os.path.exists(smallFilePath):
            filePath = smallFilePath
        else:
            filePath = os.path.join(ICON_FOLDER, imageName)

        QImage = PyQt.QtGui.QImage(filePath).scaled(ICON_SIZE, ICON_SIZE)
        QImage = QImage.scaled(ICON_SIZE, ICON_SIZE, transformMode=PyQt.QtCore.Qt.SmoothTransformation)
        QPixMap.convertFromImage(QImage)
        QIcon = PyQt.QtGui.QIcon(QPixMap)

        QICON_DICT[iconHash] = QIcon
        return QIcon


def toggleKMenu():
    if getAllKMenuWidgets():
        clearUnpinnedKMenus()
    else:
        return KMenu()


def getAllKMenuWidgets():
    allKMenuWidgets = []
    for widget in PyQt.QtWidgets.qApp.topLevelWidgets():
        if hasattr(widget, '__class__'):
            if widget.__class__.__name__ == 'KMenuWidget':
                if widget.isTopMenu:
                    allKMenuWidgets.append(widget)

    #for widget in ka_qtWidgets.getMayaWindow().children():
        #if hasattr(widget, '__class__'):
            #if widget.__class__.__name__ == 'KMenuWidget':
                #if widget.isTopMenu:
                    #allKMenuWidgets.append(widget)

    return allKMenuWidgets


def getAllUnpinnedKMenuWidgets():
    unpinnedKMenuWidgets = []
    for kMenuWidget in getAllKMenuWidgets():
        menuPinned = False
        for subMenu in kMenuWidget.allMenuWidgets:
            if subMenu.pinVisibility:
                menuPinned = True
                break
        if not menuPinned:
            unpinnedKMenuWidgets.append(kMenuWidget)

    return unpinnedKMenuWidgets

def clearUnpinnedKMenus(onlyNonPinned=True):
    if onlyNonPinned:
        for menuWidget in getAllUnpinnedKMenuWidgets():
            menuWidget.closeMenu()

    else:
        for menuWidget in getAllKMenuWidgets():
            menuWidget.closeMenu()


def raise_MenuWidgets():
    for kMenuWidget in getAllKMenuWidgets():
        for subMenu in kMenuWidget.allMenuWidgets:
            if subMenu.isVisible():
                subMenu.raise_()


def _getLabelFrom_(inputItem, kwargsDict):
    """If label as been passed in explicitly, use that. Else if
    the input item is a command, use the return of it, if that return is
    a string"""

    if 'label' in kwargsDict:
        if kwargsDict['label']:
            label = kwargsDict['label']
            #if hasattr(label, '__call__'):
                #label = label()
            kwargsDict['label'] = label

        # it is likely an empty string, replace it with the input item
        else:
            label = inputItem
            #if hasattr(inputItem, '__call__'):
                #label = inputItem()
            kwargsDict['label'] = label

    # there was never a value
    else:
        label = inputItem
        #if hasattr(inputItem, '__call__'):
            #label = inputItem()
        kwargsDict['label'] = label

    return kwargsDict['label']

class _SubMenuConstructor(object):
    """a constructor class for adding sub menus to KMenus"""

    def __init__(self, kMenu, kSubMenu,):
        self.kMenu = kMenu
        self.kSubMenu = kSubMenu

    def __enter__(self):
        self.kMenu._setCurrentMenu(self.kSubMenu)

    def __exit__(self, _type, value, traceback):
        self.kMenu._endCurrentMenu()


class KMenu(object):

    def __init__(self, *args, **kwargs):
        # get label
        #if args:
            #self.text = args[0]
        #else:
            #self.text = ''

        self.text = kwargs.get('label', '')
        self.menuWidgetInstances = []
        self.menuItemObjects = [] # objects to be represented later by menu items
        self.menuItemObjects_args = [] # args to pass to the later creation of those menu items
        self.menuItemObjects_kwargs = [] # kwargs to pass to the later creation of those menu items
        self.menuItemObjects_contexts = [] # the context commands that deside if the menu item will show

        self.currentMenu = self
        self.currentMenuHierarchy = [self]

        self.icon = kwargs.get('icon', None)

        self.menuPopulateCommand = kwargs.get('menuPopulateCommand', None)

    def _setCurrentMenu(self, kMenu):
        self.currentMenu = kMenu
        self.currentMenuHierarchy.append(kMenu)


    def _endCurrentMenu(self):
        self.currentMenuHierarchy.pop()
        self.currentMenu = self.currentMenuHierarchy[-1]

    def addSubMenu(self, *args, **kwargs):
        """Adds a submenu to the menu
        args:
            label <string> - the display label of the menu

        kwargs:
            icon <path/fileName> - the path to the icon, or the file name if it exists in
                                   ka_maya.icons
        """

        icon = kwargs.get('icon', None)
        label = kwargs.get('label', '')
        menuPopulateCommand = kwargs.get('menuPopulateCommand', None)
        kwargs['showContext'] = kwargs.get('showContext', ka_context.trueContext)

        subMenu = KMenu(label=label, icon=icon, menuPopulateCommand=menuPopulateCommand)
        self.currentMenu.add(subMenu, *args, **kwargs)

        return _SubMenuConstructor(self, subMenu)

    def addSeparator(self, *args, **kwargs):
        """Adds a separator item to the menu
        args:
            label <string> - the display label of the separator

        """
        self.currentMenu.add(KMenuItem_separator, *args, **kwargs)

    def add(self, *args, **kwargs):
        item = args[0]
        args = tuple(args[1:])

        if 'showContext' in kwargs:
            contextCommand = kwargs.pop('showContext')
        else:
            contextCommand = ka_context.trueContext

        self.currentMenu.menuItemObjects.append(item)
        self.currentMenu.menuItemObjects_args.append(args)
        self.currentMenu.menuItemObjects_kwargs.append(kwargs)
        self.currentMenu.menuItemObjects_contexts.append(contextCommand)

    def clear(self):
        self.currentMenu.menuItemObjects = [] # objects to be represented later by menu items
        self.currentMenu.menuItemObjects_args = [] # args to pass to the later creation of those menu items
        self.currentMenu.menuItemObjects_kwargs = [] # kwargs to pass to the later creation of those menu items
        self.currentMenu.menuItemObjects_contexts = [] # the context commands that deside if the menu item will show

    def pop(self, popPosition=None, parentMenu=None, parentMenuItem=None):
        kMenuWidget = KMenuWidget(kMenu=self, parentMenu=parentMenu, parent=None, parentMenuItem=parentMenuItem)

        # show
        kMenuWidget.show()

        return kMenuWidget

class KMenuWidget(PyQt.QtWidgets.QWidget):


    def __init__(self, *args, **kwargs):
        """
        args:
            label <string> - the label

        kwargs:
            parent <QWidget> - if None, then the maya window will be used as the parent

            kMenu <Kmenu> - the KMenu instance that generated the widget
        """

        # get parent
        parent = kwargs.get('parent', None)
        #if not parent:
            #parent = ka_qtWidgets.getMayaWindow()

        # init super
        super(KMenuWidget, self).__init__(parent=parent)

        self.setWindowFlags(PyQt.QtCore.Qt.FramelessWindowHint)
        self.setAttribute(PyQt.QtCore.Qt.WA_DeleteOnClose)
        #self.setFocusProxy(ka_qtWidgets.getMayaWindow())

        # create Layout
        self.vLayout = PyQt.QtWidgets.QVBoxLayout()
        self.setLayout(self.vLayout)
        self.vLayout.setSpacing(0)
        self.vLayout.setContentsMargins(QtCore.QMargins(0,0,0,0))

        # get label
        if args:
            self.label = args[0]
        else:
            self.label = ''

        self.kMenu = kwargs['kMenu']

        self.menuItems = []
        self.kMenuItems = []
        self.menuItemUnderMouse = None
        #self.nextItemPosY = 0

        # MENU HIERCHY
        # add self to subMenuWidgets of the parent menu (if there is one), and to
        # allSubMenuWidgets of all parent menus
        self.parentMenuItem = kwargs.get('parentMenuItem', None)    # the menu item that spaw
        self.parentMenu = kwargs.get('parentMenu', None)
        self.allParentMenuWidgets = []
        if self.parentMenu:
            self.parentMenu.subMenuWidgets.append(self)

            currentParentMenu = self.parentMenu
            while currentParentMenu:
                currentParentMenu.allSubMenuWidgets.append(self)
                currentParentMenu.allMenuWidgets.append(self)
                self.allParentMenuWidgets.append(currentParentMenu)

                currentParentMenu = currentParentMenu.parentMenu



        self.subMenuWidgets = []    # direct child submenus only
        self.allSubMenuWidgets = []    # all child submenus
        self.allMenuWidgets = [self]    # self, and all child submenus, only true for top menu

        self.isTopMenu = False
        if not self.parentMenu:
            self.isTopMenu = True


        # Context Object
        if self.isTopMenu:
            ka_context.newContext()

        # UNDER MOUSE
        self.subMenuWidgetUnderMouse = None
        self.widgetUnderMouse = None

        self.mouseOver_kMenuWidget = None
        self.mouseOver_previous_kMenuWidget = None
        self.mouseOver_kMenuItem = None
        self.mouseOver_previous_kMenuItem = None

        self.popped_mouseOver_submenuItem = None
        self.popped_mouseOver_submenu = None
        self.mouseOver_submenu_persists = False

        # VISIBILITY
        self.pinVisibility = False
        self.visibleSubMenus = []

        # MOVE DRAG
        self._dragMove_started = False
        self._dragMove_startCursorPosition = None
        self._dragMove_startWidgetPosition = None
        self._dragMove_mouseButton = None

        # SIZE AND POSITION
        #self.setGeometry(0, 0, MIN_WIDTH, MIN_HEIGHT)
        #self.setMinimumWidth(MIN_WIDTH)
        self.setMouseTracking(True)

        # TITLE BAR
        self.titleBarWidget = KMenuWidget_titleBar(parent=self)
        if self.parentMenuItem:
            self.titleBarWidget.qLabel.setText(self.parentMenuItem._labelText)
        self.vLayout.addWidget(self.titleBarWidget)
        #self.titleBarWidget.move(0,0)
        self.titleBarWidget.hide()
        #self.titleBarVisibility = kwargs.get('titleBarVisibility', False)

        # Populate Menu
        self.populateMenu()

        # Set Focus Policy
        #self.setFocusPolicy(PyQt.QtCore.Qt.StrongFocus)
        #self.setFocusPolicy(PyQt.QtCore.Qt.NoFocus)



        if self.parentMenu:
            self.setAttribute(PyQt.QtCore.Qt.WA_ShowWithoutActivating)



    def __repr__(self):
        labelText = 'Root'
        if self.parentMenuItem:
            if self.parentMenuItem._labelText:
                labelText = self.parentMenuItem._labelText

        return "<KMenuWidget object -%s>" % labelText

    def clearLayout(self, layout):
        if layout:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
                else:
                    self.clearLayout(item.layout())

    def show(self):

        # if menu is dynamicly populated
        if self.kMenu.menuPopulateCommand:
            self.clearLayout(self.vLayout)
            self.menuItems = []
            self.kMenuItems = []

            self.kMenu.menuPopulateCommand(self.kMenu)
            self.populateMenu()

        self.autoSize()
        if not self.pinVisibility:
            self.autoPosition()

        super(KMenuWidget, self).show()


    def autoPosition(self):
        """moves as close as possible to point without overlapping other menus, and while remaining on screen"""

        idealPosition = self._getIdealMenuPosition_(self)
        idealPositionY = idealPosition.y()

        #screenResolution = PyQt.QtWidgets.QDesktopWidget().screenGeometry()
        screenResolution = PyQt.QtWidgets.QDesktopWidget().screenGeometry(idealPosition)
        screenBottom = screenResolution.bottom()
        #screenTop = screenResolution.bottom()

        menuHeight = self.height()

        #OOOOOOO = "idealPosition"; print '%s: ' % OOOOOOO, eval(OOOOOOO), ' ', type(eval(OOOOOOO))
        #OOOOOOO = "screenResolution"; print '%s: ' % OOOOOOO, eval(OOOOOOO), ' ', type(eval(OOOOOOO))
        #OOOOOOO = "menuHeight"; print '%s: ' % OOOOOOO, eval(OOOOOOO), ' ', type(eval(OOOOOOO))
        if idealPositionY + menuHeight > screenBottom:
            adjustAmount = (idealPositionY + menuHeight) - screenBottom
            newIdealY = idealPositionY - adjustAmount - 50
            idealPosition.setY(newIdealY)
            #print 'TOO BIG'


        otherVisibibleSubMenus = []
        if self.parentMenuItem:
            for kMenuWidget in self.parentMenu.allSubMenuWidgets:
                if kMenuWidget != self:
                    if kMenuWidget.isVisible():
                        otherVisibibleSubMenus.append(kMenuWidget)

        # if other menus, solve menu collisions
        if otherVisibibleSubMenus:
            finalPositionX = None
            finalPositionY = None

            widgetWidth = self.width()
            widgetHeight = self.height()

            idealPositionY = idealPosition.y()
            idealPosition_bottomY = idealPositionY+widgetHeight
            idealPosition_midY = idealPositionY+int(widgetHeight*0.5)

            idealPositionX = idealPosition.x()

            # check for collisions
            collisionDetected = False
            for kMenuWidget in otherVisibibleSubMenus:
                kMenuWidget_Y = kMenuWidget.y()
                kMenuWidget_height = kMenuWidget.height()
                kMenuWidget_bottomY = kMenuWidget_Y+kMenuWidget_height

                ## COMPARE IDEAL GEO TO THE OTHER SUBMENUS

                # starts and ends inside
                if idealPositionY >= kMenuWidget_Y and idealPosition_bottomY <= kMenuWidget_bottomY:
                    collisionDetected = True

                # starts above, ends inside
                elif idealPositionY <= kMenuWidget_Y and idealPosition_bottomY <= kMenuWidget_bottomY and idealPosition_bottomY >= kMenuWidget_Y:
                    collisionDetected = True

                # starts inside, ends below
                elif idealPositionY >= kMenuWidget_Y and idealPositionY <= kMenuWidget_bottomY and idealPosition_bottomY >= kMenuWidget_Y:
                    collisionDetected = True

                # starts above, ends below
                elif idealPositionY <= kMenuWidget_Y and idealPosition_bottomY >= kMenuWidget_bottomY:
                    collisionDetected = True


            # If no collision is detected, move to location
            if not collisionDetected:
                self.move(idealPosition)
                return None

            # else collision has occured, determin the new placement for menu
            else:
                # sort by distance
                kMenuWidgetsByY = {}
                for kMenuWidget in otherVisibibleSubMenus:
                    kMenuWidgetsByY[kMenuWidget.y()] = kMenuWidget

                # get find large enough gaps, and arrange by distance

                # key = priorityPosition, the position used to measure distance from ideal position
                # value = position to move the menu to
                yGaps = {}

                previousWidgetBottom = None
                last = len(kMenuWidgetsByY)-1
                for i, posY in enumerate(sorted(kMenuWidgetsByY)):
                    kMenuWidget = kMenuWidgetsByY[posY]
                    kMenuWidget_Y = kMenuWidget.y()
                    kMenuWidget_height = kMenuWidget.height()
                    kMenuWidget_bottomY = kMenuWidget_Y+kMenuWidget_height

                    if i == 0 and i == last:
                        yGaps[kMenuWidget_Y] = kMenuWidget_Y-widgetHeight
                        yGaps[kMenuWidget_bottomY] = kMenuWidget_bottomY

                    elif i == 0:
                        yGaps[kMenuWidget_Y] = kMenuWidget_Y+widgetHeight
                        previousWidgetBottom = kMenuWidget_Y+kMenuWidget_height

                    elif i == last:
                        yGaps[previousWidgetBottom] = previousWidgetBottom

                    else:
                        gapHeight = kMenuWidget_Y - previousWidgetBottom
                        if gapHeight >= widgetWidth:
                            gapMid = gapHeight*0.5
                            if gapMid > idealPositionY:
                                yGaps[gapMid] = kMenuWidget_Y
                            else:
                                yGaps[gapMid] = kMenuWidget_Y+widgetHeight

                # populate dict with distance between ideal's mid, and gap's mide as the key
                yGaps_byDistance = {}
                for gapMid in yGaps:
                    distance = abs(gapMid - idealPosition_midY)
                    yGaps_byDistance[distance] = gapMid

                # set the shortest distance as the final position Y
                for gapDistance in sorted(yGaps_byDistance):
                    gapMid = yGaps_byDistance[gapDistance]
                    finalPositionY = yGaps[gapMid]
                    break

                idealPosition = PyQt.QtCore.QPoint(idealPosition.x(), finalPositionY)


        self.move(idealPosition)


    def _getIdealMenuPosition_(self, kMenuWidget):

        if kMenuWidget.parentMenuItem:
            idealPosition = kMenuWidget.parentMenuItem.mapToGlobal(PyQt.QtCore.QPoint(kMenuWidget.parentMenu.width()-2, 0))
            parent = kMenuWidget.parent()
            if parent:
                idealPosition = parent.mapFromGlobal(idealPosition)

        else:
            idealPosition = PyQt.QtWidgets.QCursor().pos()
            parent = kMenuWidget.parent()
            if parent:
                idealPosition = parent.mapFromGlobal(idealPosition)

        return idealPosition


    def autoSize(self):
        """Size the menu right before it shows based on its childrens sizes"""

        # find min width to fit all contents
        #minimumWidth = MIN_WIDTH

        for menuItem in self.menuItems:
            if hasattr(menuItem, 'autoSize'):
                menuItem.autoSize()

            #menuItemWidth = menuItem.sizeHint().width()
            #if menuItemWidth > minimumWidth:
                #minimumWidth = menuItemWidth

        #if self.titleBarVisibility:
            #currentPosY = TOP_BAR_HEIGHT
        #else:
            #currentPosY = 0

        ## set size and position of children
        #for menuItem in self.menuItems:
            #menuItem_height = menuItem.height()
            ##menuItem.setFixedWidth(minimumWidth)
            ##menuItem.move(1, currentPosY)
            #currentPosY += menuItem_height

        totalSizeHint = self.vLayout.totalSizeHint()
        #OOOOOOO = "totalSizeHint"; print '%s: ' % OOOOOOO, eval(OOOOOOO), ' ', type(eval(OOOOOOO))
        self.setFixedHeight(totalSizeHint.height())
        #self.setFixedHeight(currentPosY+1)
        #self.setFixedSize(minimumWidth+2, currentPosY+1)
        #self.titleBarWidget.setFixedWidth(self.width())

    #def setTitlebarVisibility(self, state):
        #if state:
            #self.titleBarWidget.show()
            ##self.titleBarVisibility = True
            ##self.autoSize()

        #else:
            #self.titleBarWidget.hide()
            #self.titleBarVisibility = False
            ##self.autoSize()

    def setPinnedVisibility(self, state):
        for menu in self.allMenuWidgets:

            if state:
                menu.pinVisibility = True
                self.titleBarWidget.show()
            else:
                menu.pinVisibility = False
                self.titleBarWidget.hide()

        if self.parentMenuItem:
            self.parentMenuItem.mouseOver_submenuWidgetIsPinned = self.pinVisibility

        #self.setTitlebarVisibility(state)

    def populateMenu(self):
        alternateColorOffset = 0
        if self.parentMenuItem:
            if not self.parentMenuItem.useAlternateColor:
                alternateColorOffset = 1


        i = 0
        for iA, item in enumerate(self.kMenu.menuItemObjects):
            if self.kMenu.menuItemObjects_contexts[iA]():

                if (i+alternateColorOffset)%2:
                    useAlternateColor = True
                else:
                    useAlternateColor = False

                self.makeMenuItems(iA, useAlternateColor=useAlternateColor)
                i += 1


    def makeMenuItems(self, itemIndex, useAlternateColor=False, **kwargs):
        """Make menu items from the items stored in the KMenu instance based on the type
        of those items."""

        item = self.kMenu.menuItemObjects[itemIndex]
        args = self.kMenu.menuItemObjects_args[itemIndex]
        kwargs = self.kMenu.menuItemObjects_kwargs[itemIndex]

        itemIsKMenuItemClass = False
        if inspect.isclass(item):
            if issubclass(item, KMenuItem):
                itemIsKMenuItemClass = True

        itemIsQWidgetClass = False
        if inspect.isclass(item):
            if issubclass(item, PyQt.QtWidgets.QWidget):
                itemIsQWidgetClass = True

        # if a context command was passed, use it to check whether or
        # not to show the item
        #context = kwargs.get('context', None)
        if not self.kMenu.menuItemObjects_contexts[itemIndex]():
            #if not context():
            return None

        kMenuItem_kwargs = {}
        kMenuItem_kwargs['useAlternateColor'] = useAlternateColor
        kMenuItem_kwargs['parent'] = self

        kMenuItem_kwargs['icon'] = kwargs.get('icon', None)
        kMenuItem_kwargs['label'] = kwargs.get('label', '')

        _getLabelFrom_('', kMenuItem_kwargs)


        # ToolObject
        if item.__class__.__name__ == 'ToolObject':
            tool = item

            # if there is a context requirement, check it
            if tool.context:
                if not tool.context():
                    return None

            # if no label passed in, use the tool's label
            if not kMenuItem_kwargs['label']:
                kMenuItem_kwargs['label'] = tool.label

            # if no icon passed in, use the tool's icon
            if not kMenuItem_kwargs['icon']:
                kMenuItem_kwargs['icon'] = tool.icon

            # always display a rear icon, to indicate that it is a "tool"
            kMenuItem_kwargs['rearIcon'] = 'toolSettings_small.png'

            # wrapper command, with args passed
            def menuItemCmd(*args, **kwargs):
                'do'
                OOOOOOO = "kwargs"; print '%s: ' % OOOOOOO, eval(OOOOOOO), ' ', type(eval(OOOOOOO))
                tool(*args, **kwargs)
            kMenuItem_kwargs['command'] = menuItemCmd

            itemWidget = KMenuItem(**kMenuItem_kwargs)

            if tool.settings or tool.__doc__:
                settingsMenu = KMenu(kMenu=self.kMenu,)
                itemWidget.subMenu = settingsMenu
                settingsMenu.add(ToolOptionsWidget, tool=tool)



        # KMenu
        elif item.__class__.__name__ == 'KMenu':

            kMenu = item
            if not kMenuItem_kwargs['icon']: kMenuItem_kwargs['icon'] = kMenu.icon
            _getLabelFrom_(kMenu.text, kMenuItem_kwargs)

            itemWidget = KMenuItem(subMenu=kMenu, **kMenuItem_kwargs)


        ## SettingObject
        #elif item.__class__.__name__ == 'SettingObject':
            #itemWidget = KMenuItem_toolSetting(item, **kwargs)


        # KMENUITEM
        elif itemIsKMenuItemClass:
            itemWidget = item(item, **kMenuItem_kwargs)


        # String
        elif isinstance(item, basestring):
            #kwargs['label'] = item
            #isDocString =kwargs.get('isDocString', False)

            #if isDocString:
                #itemWidget = KMenuItem_docString(**kwargs)

            #else:
            itemWidget = KLabel(item)


        # QWIDGET
        elif itemIsQWidgetClass:
            #itemWidget = KMenuItem(wrapWidget=item(**kwargs))
            itemWidget = item(**kwargs)


        # Function
        elif hasattr(item, '__call__'):

            _getLabelFrom_(item.__name__, kMenuItem_kwargs)

            #if not kwargs['label']: kwargs['label'] = item.__name__
            def menuItemCmd(*args, **kwargs):
                item(*args, **kwargs)
            kMenuItem_kwargs['command'] = menuItemCmd

            itemWidget = KMenuItem(**kMenuItem_kwargs)

        else:
            pymel.error('unable to create a menu item for type %s for item: %s' % (type(item), str(item)))


        if 'command' in kMenuItem_kwargs:
            if kMenuItem_kwargs['command']:
                #kMenuItem.signals.itemClicked.connect(kwargs['command'])
                itemWidget.clicked.connect(kMenuItem_kwargs['command'])
                itemWidget.clicked.connect(self.closeUnpinnedMenu)

        self.vLayout.addWidget(itemWidget)
        #itemWidget.move(0, self.nextItemPosY)
        #self.nextItemPosY += itemWidget.height()
        self.menuItems.append(itemWidget)

        if isinstance(itemWidget, KMenuItem):
            self.kMenuItems.append(itemWidget)

    def _updateMouseOverMenus_(self):
        """Called by the top menu, this method will update every menuItem for every child menu"""

        if self.mouseOver_kMenuItem:
            kMenuItem = self.mouseOver_kMenuItem

            # remove old popped submenus
            for otherKMenuItem in self.mouseOver_kMenuWidget.kMenuItems:
                if otherKMenuItem != kMenuItem:
                    if not otherKMenuItem.mouseOver_submenuWidgetIsPinned:
                        otherKMenuItem._unPopHoverSubMenu_()
                        kMenuItem.isHilighted = False

            # if no submenu is popped due to a mouse over
            if not kMenuItem.mouseOver_submenuWidget:
                kMenuItem._popHoverSubMenu_()

            # there is a popped submenu, but it is not visable
            elif not kMenuItem.mouseOver_submenuWidget.isVisible():
                kMenuItem._popHoverSubMenu_()

            # the submenu is already popped
            else:
                # if that submenu has a popped submenu of its own, unpop it
                if kMenuItem.mouseOver_submenuWidget.popped_mouseOver_submenuItem:
                    kMenuItem.mouseOver_submenuWidget.popped_mouseOver_submenuItem._unPopHoverSubMenu_()



        # if no menu behind mouse, and mouseOver_submenu_persists is False
        # remove any open mouseOver subMenus
        elif not self.mouseOver_kMenuWidget: # no menus behind mouse
            if not self.mouseOver_submenu_persists:
                for kMenuWidget in self.allMenuWidgets:
                    if kMenuWidget.isVisible():
                        if kMenuWidget.popped_mouseOver_submenuItem:
                            kMenuWidget.popped_mouseOver_submenuItem._unPopHoverSubMenu_()


    def _getKMenuItemUnderMouse_(self, cursorLocation=None):
        """returns the visible kMenuItem under the mouse"""

        if not globalCursorLocation:
            globalCursorLocation = PyQt.QtWidgets.QCursor().pos()

        widgetUnderMouse = self.childAt(cursorLocation)
        menuItemUnderMouse = widgetUnderMouse
        if widgetUnderMouse:
            while not isinstance(menuItemUnderMouse, KMenuItem):
                menuItemUnderMouse = menuItemUnderMouse.parent()
                if menuItemUnderMouse == self:
                    menuItemUnderMouse = None
                    break

        return menuItemUnderMouse

    def _getMouseOver_kMenuWidget_(self, globalCursorLocation=None):
        """returns the visible kMenuWidget under the mouse"""

        if not globalCursorLocation:
            globalCursorLocation = PyQt.QtWidgets.QCursor().pos()

        kMenuWidgetHierchy = [self]
        kMenuWidgetHierchy.extend(self.allSubMenuWidgets)

        for kMenuWidget in kMenuWidgetHierchy:
            if kMenuWidget.isVisible():
                menuRectangle = kMenuWidget.geometry()

                kMenuWidgetParent = kMenuWidget.parent()
                if kMenuWidgetParent:
                    localCursorLocation = kMenuWidgetParent.mapFromGlobal(globalCursorLocation)
                else:
                    localCursorLocation = globalCursorLocation

                if menuRectangle.contains(localCursorLocation):
                    return kMenuWidget


    def _getMouseOver_kMenuItem_(self, globalCursorLocation):
        """returns the visible kMenuItem under the mouse"""

        if self.mouseOver_kMenuWidget:
            for kMenuItem in self.mouseOver_kMenuWidget.kMenuItems:
                menuItemRectangle = kMenuItem.geometry()
                localCursorLocation = self.mouseOver_kMenuWidget.mapFromGlobal(globalCursorLocation)

                if menuItemRectangle.contains(localCursorLocation):
                    return kMenuItem

    def leaveEvent(self, event):
        if not self.isTopMenu:
            self.parentMenu.leaveEvent(event)

        else:
            self._updateMouseOverMenus_()

        # Do regular stuff
        PyQt.QtWidgets.QWidget.leaveEvent(self, event)

    def mouseMoveEvent(self, event):
        # because of Qt.Popup windowFlag, this event must be propigated manually to parent menus
        if not self.isTopMenu:
            self.parentMenu.mouseMoveEvent(event)

        else:
            globalCursorLocation = event.globalPos()
            globalCursorLocationX = globalCursorLocation.x()
            globalCursorLocationY = globalCursorLocation.y()

            self.mouseOver_previous_kMenuWidget = self.mouseOver_kMenuWidget
            self.mouseOver_previous_kMenuItem = self.mouseOver_kMenuItem

            self.mouseOver_kMenuWidget = self._getMouseOver_kMenuWidget_(globalCursorLocation)
            self.mouseOver_kMenuItem = self._getMouseOver_kMenuItem_(globalCursorLocation)
            if self._dragMove_started:
                self._moveDrag(globalCursorLocation)

            else:
                # Update Hover hilighting
                if self.mouseOver_kMenuWidget:
                    self._updateMouseOverMenus_()

                for kMenu in self.allMenuWidgets:
                    if kMenu.isVisible():
                        for menuItem in kMenu.kMenuItems:
                            if menuItem.isVisible():
                                if menuItem == self.mouseOver_kMenuItem:
                                    if not menuItem.isHilighted:
                                        menuItem.isHilighted = True
                                        menuItem.update()
                                else:
                                    if menuItem.isHilighted:
                                        menuItem.isHilighted = False
                                        menuItem.update()

            event.accept()

        # Do regular stuff
        PyQt.QtWidgets.QWidget.mouseMoveEvent(self, event)

    def mousePressEvent(self, event):
        if not self.isTopMenu:
            self.parentMenu.mousePressEvent(event)

        else:
            globalCursorLocation = event.globalPos()
            globalCursorLocationX = globalCursorLocation.x()
            globalCursorLocationY = globalCursorLocation.y()

            menuItemClicked = self.mouseOver_kMenuItem
            kMenuWidgetClicked = self.mouseOver_kMenuWidget

            # because the event is sometimes passed from child menus
            # we must to the following to get the local cursorLocation
            cursorLocation = kMenuWidgetClicked.mapFromGlobal(globalCursorLocation)
            cursorLocationX = cursorLocation.x()
            cursorLocationY = cursorLocation.y()

            button = event.button()
            clickedChild = kMenuWidgetClicked.childAt(cursorLocation)


            # left click
            if button == PyQt.QtCore.Qt.LeftButton:
                pass
                #if clickedChild:
                #if hasattr(clickedChild, 'command'):

                    #if clickedChild.command:
                        #clickedChild.command()

                    #if menuItemClicked:
                        #if menuItemClicked.closeMenuAfterUse:
                            #if not kMenuWidgetClicked.pinVisibility:


            # right click
            elif button == PyQt.QtCore.Qt.RightButton:
                if menuItemClicked:
                    if menuItemClicked.subMenu:
                        if menuItemClicked.mouseOver_submenuWidgetIsPinned:
                            menuItemClicked.mouseOver_submenuWidgetIsPinned = False

                        else:
                            menuItemClicked.mouseOver_submenuWidgetIsPinned = True
                        menuItemClicked.update()

            # middle click
            elif button == PyQt.QtCore.Qt.MiddleButton:
                self._moveDrag_start(globalCursorLocation)


            if kMenuWidgetClicked:
                event.accept()

        # because of Qt.Popup windowFlag, this event must be propigated manually to parent menus
        #if self.parentMenu:
            #self.parentMenu.mousePressEvent(event)

        # Do regular stuff
        PyQt.QtWidgets.QWidget.mousePressEvent(self, event)



    def mouseReleaseEvent(self, event):
        button = event.button()

        # middle release
        if button == PyQt.QtCore.Qt.MiddleButton:
            self._moveDrag_end()

        # because of Qt.Popup windowFlag, this event must be propigated manually to parent menus
        if self.parentMenu:
            self.parentMenu.mouseReleaseEvent(event)


    def _moveDrag(self, globalCursorLocation):
        if self.parentMenu:
            self.parentMenu._moveDrag(globalCursorLocation)

        else:
            moveAmount = globalCursorLocation - self._dragMove_startCursorPosition
            newLocation = self._dragMove_startWidgetPositionPosition + moveAmount
            self.move(newLocation)
            for kMenuWidget in self.allSubMenuWidgets:
                newLocation = kMenuWidget._dragMove_startWidgetPositionPosition + moveAmount
                kMenuWidget.move(newLocation)

    def _moveDrag_start(self, globalCursorLocation):
        if not self.isTopMenu:
            self.parentMenu._moveDrag_start(globalCursorLocation)

        else:
            relatedMenus = [self]
            while relatedMenus:
                currentMenu = relatedMenus.pop()

                currentMenu._dragMove_startCursorPosition = globalCursorLocation
                currentMenu._dragMove_startWidgetPositionPosition = currentMenu.pos()

                if currentMenu.subMenuWidgets:
                    relatedMenus.extend(currentMenu.subMenuWidgets)

            self._dragMove_started = True

            if self.mouseOver_kMenuWidget:
                self.mouseOver_kMenuWidget.setPinnedVisibility(True)

                #self.mouseOver_kMenuWidget.setWindowFlags(PyQt.QtCore.Qt.Window)

                if self.mouseOver_kMenuWidget.parentMenu:
                    for parentMenu in self.mouseOver_kMenuWidget.allParentMenuWidgets:
                        parentMenu.hide()

    def _moveDrag_end(self):
        if self.parentMenu:
            self.parentMenu._moveDrag_end()

        else:
            self._dragMove_started = False

    def closeMenu(self):
        if not self.isTopMenu:
            self.parentMenu.closeMenu()

        else:
            for child in reversed(self.allMenuWidgets):
                try:
                    #child.close()
                    child.deleteLater()

                except:
                    pass

    def closeUnpinnedMenu(self):
        if not self.pinVisibility:
            modifiers = PyQt.QtWidgets.QApplication.keyboardModifiers()
            if modifiers == PyQt.QtCore.Qt.NoModifier:
                self.closeMenu()


    def getTopMenu(self):
        if self.allParentMenuWidgets:
            return self.allParentMenuWidgets[-1]
        else:
            return self

    def paintEvent(self, event):

        qp = PyQt.QtWidgets.QPainter()
        qp.begin(self)
        self.drawWidget(qp)
        qp.end()

    def drawWidget(self, qp):
        #self._stayOnTop_()

        qp.setPen(QCOLOR_MENU_BORDERLINES)
        qp.setBrush(QCOLOR_BACKGROUND)

        qp.drawRect(0, 0, self.width()-1, self.height()-1)    # background


    #def _stayOnTop_(self):
        #if self.parentMenu:
            #if self.parentMenu.isVisible():
                #return None

        ##if not isinstance(self.parent().children()[-1], KMenuWidget):
            ##for kMenuWidget in self.allSubMenuWidgets:
                ##kMenuWidget.raise_()

        #topWidgets = PyQt.QtWidgets.qApp.topLevelWidgets()
        #if not isinstance(topWidgets[-1], KMenuWidget):
            #for kMenuWidget in self.allSubMenuWidgets:
                #kMenuWidget.raise_()
            #self.raise_()


#class KRegionWidget(PyQt.QtWidgets.QWidget):
class KRegionWidget(PyQt.QtWidgets.QPushButton):

    def __init__(self, *args, **kwargs):
        self.KRegionWidget__init__(*args, **kwargs)

    def KRegionWidget__init__(self, *args, **kwargs):
        #PyQt.QtWidgets.QWidget.__init__(*args, **kwargs)
        super(KRegionWidget, self).__init__(**kwargs)

        label = kwargs.get('label', None)
        if not label:
            self._labelText = ''

        self.hilightOnHover = False
    def paintEvent(self, event):
        qp = PyQt.QtWidgets.QPainter()
        qp.begin(self)
        self.draw_regionWidget(qp)
        qp.end()

    def draw_regionWidget(self, qp):
        widgetHeight = self.height()
        widgetWidth = self.width()

        qp.setPen(QCOLOR_MENU_BORDERLINES)
        qp.setBrush(QCOLOR_BACKGROUND)
        qp.drawRect(0, 0, widgetWidth-1, widgetHeight-1)

        cursorLocation = self.mapFromGlobal(PyQt.QtWidgets.QCursor().pos())
        geometry = PyQt.QtCore.QRect(1,1,widgetWidth-2, widgetHeight-2)

        # border color
        if self.hilightOnHover and geometry.contains(cursorLocation):
            qp.setPen(QCOLOR_MENU_BORDERLINES_UNDERMOUSE)
            qp.setBrush(QCOLOR_MENU_ITEM_UNDERMOUSE)

        else:
            qp.setPen(QCOLOR_MENU_BORDERLINES)
            qp.setBrush(QCOLOR_BACKGROUND)

        qp.drawRect(0, 0, widgetWidth-1, widgetHeight-1)

        #if self._labelText:

            #textBoarderPadding = widgetHeight/25

            #qp.setFont(QFONT_LABEL)
            #qp.setPen(QCOLOR_MENU_ITEM_TEXT)
            #qp.drawText(PyQt.QtCore.QRectF(6, 3, widgetWidth-6, widgetHeight-6), self._labelText)

class KLabel(PyQt.QtWidgets.QLabel):

    def __init__(self, *args, **kwargs):
        if args:
            self.labelText = args[0]
        else:
            self.labelText = args[0]

        if hasattr(self.labelText, '__call__'):
            super(KLabel, self).__init__(**kwargs)
        else:
            super(KLabel, self).__init__(self.labelText, **kwargs)

        self.setAttribute(PyQt.QtCore.Qt.WA_TransparentForMouseEvents)

    def updateLabelText(self):
        if hasattr(self.labelText, '__call__'):
            result = self.labelText()
            if isinstance(result, basestring):
                self.setText(result)
            else:
                self.setText(str(result))


#class KMenuWidget_titleBar(KRegionWidget):
class KMenuWidget_titleBar(QtWidgets.QWidget):

    def __init__(self, *args, **kwargs):
        #self.KRegionWidget__init__(self, *args, **kwargs)
        super(KMenuWidget_titleBar, self).__init__()
        #parent = kwargs.get('parent', None)

        # create Layout
        self.hLayout = PyQt.QtWidgets.QHBoxLayout()
        self.hLayout.setContentsMargins(QtCore.QMargins(1,1,1,1))
        self.setLayout(self.hLayout)

        # titleLabel
        self.qLabel = QtWidgets.QLabel()
        self.hLayout.addWidget(self.qLabel)
        self.hLayout.addStretch()

        # close button
        self.closeButton = PyQt.QtWidgets.QPushButton()
        self.closeButton.setText('x')
        self.hLayout.addWidget(self.closeButton)

        self.closeButton.clicked.connect(self.closeButtonCmd)


        # label text
        #if parent:
            #if parent.parentMenuItem:
                #if parent.parentMenuItem._labelText:
                    #self.labelWidget = KLabel(parent.parentMenuItem._labelText, parent=self)
                    #self.labelWidget.setPalette(QPALETTE_LABEL)
                    #self.labelWidget.setFixedHeight(MENU_ITEM_MIN_HEIGHT)
                    #self.labelWidgetSizeHint = self.labelWidget.sizeHint()
                    #self.labelWidgetWidthHint = self.labelWidgetSizeHint.width()
                    #self.labelWidgetHeightHint = self.labelWidgetSizeHint.height()

                    #self.labelWidget.move(MENU_ITEM_MIN_HEIGHT+1, -2)

        self.setFixedHeight(TOP_BAR_HEIGHT)
        self.closeButton.setFixedSize(TOP_BAR_HEIGHT, TOP_BAR_HEIGHT)


    def closeButtonCmd(self):
        self.parent().closeMenu()

    #def resizeEvent(self, event):
        #self.closeButton.move(self.width()-self.closeButton.width(), 0)

    #def paintEvent(self, event,):
        #qp = PyQt.QtWidgets.QPainter()
        #qp.begin(self)
        #self.draw_regionWidget(qp)
        #self.draw_titleBar(qp)
        #qp.end()

    #def draw_titleBar(self, qp):
        #widgetHeight = self.height()
        #widgetWidth = self.width()

        #qp.setBrush(QCOLOR_TOP_BAR)
        #qp.drawRect(self.geometry())    # top bar

        #qp.setPen(QCOLOR_MENU_BORDERLINES)
        #qp.setBrush(QCOLOR_ICON_FILL)

    #def mousePressEvent(self, event):
        #globalCursorLocation = event.globalPos()
        #globalCursorLocationX = globalCursorLocation.x()
        #globalCursorLocationY = globalCursorLocation.y()

        ## because the event is sometimes passed from child menus
        ## we must to the following to get the local cursorLocation
        #cursorLocation = self.mapFromGlobal(globalCursorLocation)
        #cursorLocationX = cursorLocation.x()
        #cursorLocationY = cursorLocation.y()

        #button = event.button()

        ## left click
        #if button == PyQt.QtCore.Qt.LeftButton:
            #self.parent()._moveDrag_start(globalCursorLocation)

        #else:
            ## Do regular stuff
            #PyQt.QtWidgets.QWidget.mousePressEvent(self, event)

    #def mouseReleaseEvent(self, event):
        #button = event.button()

        ## middle release
        #if button == PyQt.QtCore.Qt.LeftButton:
            #self.parent()._moveDrag_end()

    #def mouseMoveEvent(self, event):
        #globalCursorLocation = event.globalPos()
        #globalCursorLocationX = globalCursorLocation.x()
        #globalCursorLocationY = globalCursorLocation.y()

        ## because the event is sometimes passed from child menus
        ## we must to the following to get the local cursorLocation
        #cursorLocation = self.mapFromGlobal(globalCursorLocation)
        #cursorLocationX = cursorLocation.x()
        #cursorLocationY = cursorLocation.y()

        #parent = self.parent()
        #if parent._dragMove_started:
            #parent._moveDrag(globalCursorLocation)

        ## Do regular stuff
        #PyQt.QtWidgets.QWidget.mouseMoveEvent(self, event)


class KaMenu_moveWidget(KRegionWidget):

    def __init__(self, *args, **kwargs):
        self.KRegionWidget__init__(self, *args, **kwargs)
        self.hilightOnHover = kwargs.get('hilightOnHover', True)

    def paintEvent(self, event,):
        qp = PyQt.QtWidgets.QPainter()
        qp.begin(self)
        self.draw_regionWidget(qp)
        self.draw_moveWidget(qp)
        qp.end()

    def draw_moveWidget(self, qp):
        widgetHeight = self.height()
        widgetWidth = self.width()

        widthUnit = widgetWidth/6.0
        heightUnit = widgetHeight/6.0

        qp.setPen(QCOLOR_MENU_BORDERLINES)
        qp.setBrush(QCOLOR_ICON_FILL)
        polygon = PyQt.QtWidgets.QPolygon([PyQt.QtCore.QPoint(widthUnit*2, heightUnit),   PyQt.QtCore.QPoint(widthUnit*3, heightUnit*2), PyQt.QtCore.QPoint(widthUnit*4, heightUnit),
                                  PyQt.QtCore.QPoint(widthUnit*5, heightUnit*2), PyQt.QtCore.QPoint(widthUnit*4, heightUnit*3), PyQt.QtCore.QPoint(widthUnit*5, heightUnit*4),
                                  PyQt.QtCore.QPoint(widthUnit*4, heightUnit*5), PyQt.QtCore.QPoint(widthUnit*3, heightUnit*4), PyQt.QtCore.QPoint(widthUnit*2, heightUnit*5),
                                  PyQt.QtCore.QPoint(widthUnit, heightUnit*4),   PyQt.QtCore.QPoint(widthUnit*2, heightUnit*3), PyQt.QtCore.QPoint(widthUnit, heightUnit*2), PyQt.QtCore.QPoint(widthUnit*2, heightUnit),
                                  ])

        qp.drawPolygon(polygon, PyQt.QtCore.Qt.WindingFill)

    def mouseMoveEvent(self, event):
        print 'regionMove'
        pass




class KMenuItem_Signals(PyQt.QtCore.QObject):
    itemClicked = PyQt.QtCore.Signal()


class KMenuItem(PyQt.QtWidgets.QPushButton):

    def __init__(self, *args, **kwargs):
        self.__init__KMenuItem(*args, **kwargs)

    def __init__KMenuItem(self, *args, **kwargs):
        """
        kwargs:
            label (string) - the text the appears on the menu item
            command (function) - the command that runs on left click of the menu item
            subMenu (KMenu) - the Menu that is the submenu (if this is one) assosiated with this menu item
            hilightOnHover (bool) - if True, item will hilight on mouse over
        """

        self.parentMenu = kwargs.get('parent', None)
        super(KMenuItem, self).__init__(parent=self.parentMenu)

        # create layout
        self.vLayout = PyQt.QtWidgets.QVBoxLayout()
        self.setLayout(self.vLayout)
        self.vLayout.setSpacing(0)
        self.vLayout.setContentsMargins(QtCore.QMargins(ICON_SIZE+12,0,ICON_SIZE+12,0))

        # label text
        self._labelText = kwargs.get('label', '')
        self.labelWidget = KLabel(self._labelText)
        self.labelWidget.setPalette(QPALETTE_LABEL)
        self.vLayout.addWidget(self.labelWidget)

        # set min height
        self.setFixedHeight(MENU_ITEM_MIN_HEIGHT)

        # icons
        self.icon = kwargs.get('icon', None)
        if self.icon:
            self.icon = getIcon(self.icon)

        self.rearIcon = kwargs.get('rearIcon', None)
        if self.rearIcon:
            self.rearIcon = getIcon(self.rearIcon)

        # color
        self.useAlternateColor = kwargs.get('useAlternateColor', False)
        self.isHilighted = False

        # command
        self.command = kwargs.get('command', None)

        # sub menu
        self.subMenu = kwargs.get('subMenu', None)    # KMenu class  used to create menu widgets
        self.mouseOver_submenuWidget = None    # KMenu widget generated by hovering over the menu item
        self.mouseOver_submenuWidgetIsPinned = False    # is KMenu visiblity pinned to ON

        self.hilightOnHover = kwargs.get('hilightOnHover', False)
        if self.command or self.subMenu:
            self.hilightOnHover = True

        self.closeMenuAfterUse = True

        self.signals = KMenuItem_Signals()

        self.setMouseTracking(True)
        self.setFocusPolicy(PyQt.QtCore.Qt.NoFocus)
        #self.setFocusPolicy(PyQt.QtCore.Qt.ClickFocus)


    def autoSize(self):
        self.labelWidget.updateLabelText()

        # get label size hints
        labelWidgetSizeHint = self.labelWidget.sizeHint()
        labelWidgetWidthHint = labelWidgetSizeHint.width()
        #labelWidgetHeightHint = labelWidgetSizeHint.height()

        self.labelWidget.setMinimumWidth(labelWidgetWidthHint)
        #self.labelWidget.setMinimumHeight(MENU_ITEM_MIN_HEIGHT)
        #self.labelWidget.setMaximumHeight(labelWidgetHeightHint)

        # set self size based on layout
        totalSizeHint = self.vLayout.totalSizeHint()
        self.setMinimumWidth(totalSizeHint.width())
        #self.setMinimumHeight(MENU_ITEM_MIN_HEIGHT)
        #self.setMaximumHeight(totalMinimumSize.height())
        #self.setFixedHeight(totalMinimumSize.height())


    def __repr__(self):
        labelText = 'Blank'
        if self._labelText:
            labelText = self._labelText

        return "<KMenuWidget object -%s>" % labelText

    def mousePressEvent(self, event):
        button = event.button()
        if button == PyQt.QtCore.Qt.LeftButton:
            self.signals.itemClicked.emit()
            #event.accept()

            #if self.command:
                #self.command()

                #if not self.parentMenu.pinVisibility:
                    #if self.closeMenuAfterUse:
                        #PyQt.QtWidgets.QWidget.mousePressEvent(self, event)
                        #self.parent().closeMenu()
                        #return None

        # Do regular stuff
        PyQt.QtWidgets.QAbstractButton.mousePressEvent(self, event)
        #PyQt.QtWidgets.QWidget.mousePressEvent(self, event)


    def _popSubMenu_(self):
        """creates and shows an instance of the assosiated KMenu, (which creates a KMenuWidget)"""
        if self.subMenu:
            globalPosition = self.mapToGlobal(PyQt.QtCore.QPoint(0, 0))
            popPosition = (globalPosition.x()+self.width(), globalPosition.y())
            subMenu = self.subMenu.pop(popPosition=popPosition, parentMenu=self.parent(), parentMenuItem=self)
            return subMenu

    def _popHoverSubMenu_(self):
        """called when the mouse hovers over a menu item with a subMenu assosiated with it"""
        currentKMenu = self.parent()

        if self.mouseOver_submenuWidget:
            self.mouseOver_submenuWidget.show()

        else:
            self.mouseOver_submenuWidget = self._popSubMenu_()

        self.parent().popped_mouseOver_submenuItem = self


    def _unPopHoverSubMenu_(self):
        """called when the mouse hovers over some other menu item with a subMenu assosiated with it"""
        if self.mouseOver_submenuWidget:
            self.mouseOver_submenuWidget.hide()
            #self.mouseOver_submenuWidget.deleteLater()
            #self.mouseOver_submenuWidget = None

            for kMenuItem in self.mouseOver_submenuWidget.kMenuItems:
                if kMenuItem.mouseOver_submenuWidget:
                    kMenuItem._unPopHoverSubMenu_()

            #self.mouseOver_submenuWidget.deleteLater()
            #self.mouseOver_submenuWidget = None

    def paintEvent(self, event,):
        qp = PyQt.QtWidgets.QPainter()
        qp.begin(self)
        self.draw_menuItem(qp)
        qp.end()

    def draw_menuItem(self, qp):
        widgetHeight = self.height()
        widgetWidth = self.width()

        if self.hilightOnHover and self.isHilighted:
            qp.setBrush(QBRUSH_MENUITEM_HILIGHT)
            qp.setPen(QCOLOR_MENU_BORDERLINES_UNDERMOUSE)

        else:
            if self.useAlternateColor:
                qp.setBrush(QBRUSH_MENUITEM_ALTERNATE)
                qp.setPen(QCOLOR_BACKGROUND)

            else:
                qp.setBrush(QBRUSH_MENUITEM)
                qp.setPen(QCOLOR_BACKGROUND)

        # draw background rectangle
        qp.drawRect(-1, 0, widgetWidth+2, widgetHeight)

        # draw submenu indicator
        if self.subMenu:
            QRECTANLE_ICON_BACK.moveTo(widgetWidth-ICON_BUFFER_BOARDER_PIXELS-ICON_SIZE, ICON_BUFFER_BOARDER_PIXELS)
            if not self.rearIcon:
                if self.mouseOver_submenuWidgetIsPinned:
                    getIcon('subMenuArrowPinned_small.png').paint(qp, QRECTANLE_ICON_BACK)
                else:
                    getIcon('subMenuArrow_small.png').paint(qp, QRECTANLE_ICON_BACK)
            else:
                self.rearIcon.paint(qp, QRECTANLE_ICON_BACK)

        # draw icon
        if self.icon:
            self.icon.paint(qp, QRECTANLE_ICON_FRONT)

#class KMenuItem_separator(KMenuItem):
class KMenuItem_separator(QtWidgets.QWidget):

    def __init__(self, *args, **kwargs):
        """
        kwargs:
            label (string) - the text the appears on the menu item
            command (function) - the command that runs on left click of the menu item
            subMenu (KMenu) - the Menu that is the submenu (if this is one) assosiated with this menu item
        """
        #super(KMenuItem_separator, self).__init__(*args, **kwargs)
        super(KMenuItem_separator, self).__init__()

        # create layout
        self.vLayout = PyQt.QtWidgets.QVBoxLayout()
        self.setLayout(self.vLayout)
        self.vLayout.setSpacing(0)
        self.vLayout.setContentsMargins(QtCore.QMargins(ICON_SIZE+12,0,ICON_SIZE+12,0))

        # label text
        self._labelText = kwargs.get('label', '')
        self.labelWidget = KLabel(self._labelText)
        self.labelWidget.setPalette(QPALETTE_LABEL)
        self.vLayout.addWidget(self.labelWidget)

        #self.hilightOnHover = False
        self.labelWidget.setFont(QFONT_SEPARATOR)
        self.labelWidget.setPalette(QPALETTE_SEPARATOR)

        self.setMaximumHeight(MENU_ITEM_MIN_HEIGHT-7)

    #def autoSize(self):
        #self.labelWidget.updateLabelText()

        ## set size
        #labelWidgetSizeHint = self.labelWidget.sizeHint()
        #labelWidgetWidthHint = labelWidgetSizeHint.width()
        #labelWidgetHeightHint = labelWidgetSizeHint.height()

        #minWidth = labelWidgetWidthHint + MENU_ITEM_MIN_HEIGHT + 50

        ##self.labelWidget.setFixedWidth(labelWidgetWidthHint)
        #self.labelWidget.setFixedHeight(labelWidgetHeightHint)

        ##self.setFixedWidth(minWidth)
        #if self.labelWidget.text():
            #self.setFixedHeight(MENU_ITEM_MIN_HEIGHT-3)
            #self.labelWidget.move(2, (MENU_ITEM_MIN_HEIGHT-4)-labelWidgetHeightHint)

        #else:
            #self.setFixedHeight(MENU_ITEM_MIN_HEIGHT-10)


    def paintEvent(self, event,):
        qp = PyQt.QtWidgets.QPainter()
        qp.begin(self)
        self.draw_menuItem(qp)
        qp.end()


    def draw_menuItem(self, qp):
        widgetHeight = self.height()
        widgetWidth = self.width()

        # line
        qp.setPen(QCOLOR_MENU_SEPARATOR_TEXT)
        qp.drawLine(0, 0, widgetWidth, 0)
        qp.drawLine(0, widgetHeight-1, widgetWidth, widgetHeight-1)


class ToolOptionsWidget(QtWidgets.QWidget):
    """A widget that allows accsess to options and settings for a tool object. Tool Objects
    are usually created in ka_core module"""

    def __init__(self, tool=None, **kwargs):
        super(ToolOptionsWidget, self).__init__()

        self.tool = tool

        self.setPalette(QPALETTE_TOOLWIDGET)

        # create layout
        self.vLayout = PyQt.QtWidgets.QVBoxLayout()
        self.setLayout(self.vLayout)
        self.vLayout.setSpacing(0)
        self.vLayout.setContentsMargins(QtCore.QMargins(10,5,10,5))

        toolNameTextWidget = KLabel('%s:' % tool.label)
        self.vLayout.addWidget(toolNameTextWidget)
        self.vLayout.addSpacing(5)

        if hasattr(tool, '__doc__'):
            hLayout = PyQt.QtWidgets.QHBoxLayout()
            hLayout.setContentsMargins(QtCore.QMargins(10,0,0,0))
            self.vLayout.addLayout(hLayout)
            #hLayout.addSpacing(10)


            self.docStringWidget = KLabel(tool.__doc__)

            self.docStringWidget.setPalette(QPALETTE_DOCSTRING)
            hLayout.addWidget(self.docStringWidget)

            self.vLayout.addSpacing(10)


        for settingObject in tool.settings:
            # create layout
            hLayout = PyQt.QtWidgets.QHBoxLayout()
            hLayout.setSpacing(0)
            hLayout.setContentsMargins(QtCore.QMargins(10,0,0,0))
            self.vLayout.addLayout(hLayout)

            # setting label text
            settingLabel = QtWidgets.QLabel('%s:' % settingObject.settingName)
            settingLabel.setFixedWidth(settingLabel.sizeHint().width())
            settingLabel.setPalette(QPALETTE_INPUTITEM)
            hLayout.addWidget(settingLabel)
            hLayout.addSpacing(10)

            # setting widget
            self.settingWidget = self._getSettingInputWidget(settingObject)
            self.settingWidget.setFixedHeight(MENU_ITEM_MIN_HEIGHT-2)
            self.settingWidget.setPalette(QPALETTE_INPUTITEM)
            hLayout.addWidget(self.settingWidget)

            hLayout.addStretch()

        # create layout
        hLayout = PyQt.QtWidgets.QHBoxLayout()
        hLayout.setSpacing(10)
        hLayout.setContentsMargins(QtCore.QMargins(0,0,0,0))
        self.vLayout.addLayout(hLayout)
        hLayout.addStretch()

        # create buttons
        apply_pushButton = QtWidgets.QPushButton('Apply')
        apply_pushButton.setFixedHeight(20)
        hLayout.addWidget(apply_pushButton)
        apply_pushButton.clicked.connect(tool)

        echo_pushButton = QtWidgets.QPushButton('Echo Command')
        echo_pushButton.setFixedHeight(20)
        hLayout.addWidget(echo_pushButton)

        hLayout.addStretch()

    def _getSettingInputWidget(self, settingObject):
        valueType = settingObject.valueType.lower()

        defaultValue = ka_preference.get(settingObject.settingLongName, None)
        if defaultValue == None:
            defaultValue = settingObject.defaultValue

        # INT
        if valueType == 'int':
            settingInputWidget = PyQt.QtWidgets.QSpinBox(parent=self)
            settingInputWidget.setValue(defaultValue)
            #signal = PyQt.QtCore.SIGNAL('valueChanged (int)')
            signal = settingInputWidget.valueChanged

        # FLOAT
        if valueType == 'float':
            settingInputWidget = PyQt.QtWidgets.QDoubleSpinBox(defaultValue, parent=self)
            settingInputWidget.setValue(defaultValue)
            #signal = PyQt.QtCore.SIGNAL('valueChanged (double)')
            signal = settingInputWidget.valueChanged

        # STRING
        elif valueType == 'string':
            settingInputWidget = PyQt.QtWidgets.QLineEdit(defaultValue, parent=self)
            signal = PyQt.QtCore.SIGNAL('returnPressed()')
            signal = settingInputWidget.returnPressed

        # BOOL
        elif valueType == 'bool':
            settingInputWidget = PyQt.QtWidgets.QCheckBox(parent=self)
            settingInputWidget.setChecked(defaultValue)
            #signal = PyQt.QtCore.SIGNAL('stateChanged (int)')
            signal = settingInputWidget.stateChanged

        # ENUM
        elif valueType == 'enum':
            settingInputWidget = PyQt.QtWidgets.QComboBox(parent=self)
            settingInputWidget.addItems(settingObject.enumValues)
            settingInputWidget.setCurrentIndex(defaultValue)
            #signal = PyQt.QtCore.SIGNAL('currentIndexChanged (int)')
            signal = settingInputWidget.currentIndexChanged

        # hook signal to command
        def cmd(arg0, self=self, settingInputWidget=settingInputWidget, settingObject=settingObject):
            self._changeSettingValue(settingInputWidget, settingObject)

        #self.connect(settingInputWidget, signal, cmd)
        signal.connect(cmd)
        return settingInputWidget


    def _changeSettingValue(self, settingWidget, settingObject):
            # INT
            if isinstance(settingWidget, PyQt.QtWidgets.QSpinBox):
                newValue = settingWidget.value()

            # FLOAT
            if isinstance(settingWidget, PyQt.QtWidgets.QDoubleSpinBox):
                newValue = settingWidget.value()

            # STRING
            if isinstance(settingWidget, PyQt.QtWidgets.QLineEdit):
                newValue = settingWidget.text()

            # BOOL
            elif isinstance(settingWidget, PyQt.QtWidgets.QCheckBox):
                newValue = settingWidget.isChecked()

            # ENUM
            elif isinstance(settingWidget, PyQt.QtWidgets.QComboBox):
                newValue = settingWidget.currentIndex()

            OOOOOOO = "newValue"; print '%s: ' % OOOOOOO, eval(OOOOOOO), ' ', type(eval(OOOOOOO))
            ka_preference.add(settingObject.settingLongName, newValue)


#class KMenuItem_docString(QtWidgets.QWidget):

    #def __init__(self, *args, **kwargs):
        #"""
        #kwargs:
            #label (string) - the text the appears on the menu item
            #command (function) - the command that runs on left click of the menu item
            #subMenu (KMenu) - the Menu that is the submenu (if this is one) assosiated with this menu item
        #"""
        #super(KMenuItem_docString, self).__init__()

        ## create layout
        #self.vLayout = PyQt.QtWidgets.QVBoxLayout()
        #self.setLayout(self.vLayout)
        #self.vLayout.setSpacing(0)
        #self.vLayout.setContentsMargins(QtCore.QMargins(10,0,10,0))

        ## label text
        #self._labelText = kwargs.get('label', '')
        #self.labelWidget = KLabel(self._labelText)
        #self.labelWidget.setPalette(QPALETTE_LABEL)
        #self.vLayout.addWidget(self.labelWidget)

        #self.hilightOnHover = False
        #self.labelWidget.setPalette(QPALETTE_DOCSTRING)

        ## set size from size hint
        #labelWidgetSizeHint = self.labelWidget.sizeHint()
        #labelWidgetWidthHint = labelWidgetSizeHint.width()
        #labelWidgetHeightHint = labelWidgetSizeHint.height()
        #self.setMinimumWidth(labelWidgetWidthHint+20)
        #self.setMinimumHeight(labelWidgetHeightHint+10)

        ##self.vLayout.setContentsMargins(QtCore.QMargins(10,50,10,20))
        ##self.vLayout.setContentsMargins(QtCore.QMargins(0,0,0,0))

        ##self.labelWidget.move(6, 6)

    ##def autoSize(self):
        ##self.labelWidget.updateLabelText()

        ### get label size hints
        ##labelWidgetSizeHint = self.labelWidget.sizeHint()
        ##labelWidgetWidthHint = labelWidgetSizeHint.width()
        ##labelWidgetHeightHint = labelWidgetSizeHint.height()
        ##OOOOOOO = "labelWidgetHeightHint"; print '%s: ' % OOOOOOO, eval(OOOOOOO), ' ', type(eval(OOOOOOO))

        ##self.labelWidget.setMinimumWidth(labelWidgetWidthHint)
        ##self.labelWidget.setMinimumHeight(MENU_ITEM_MIN_HEIGHT)
        ###self.labelWidget.setMaximumHeight(labelWidgetHeightHint)

        ### set self size based on layout
        ##totalMinimumSize = self.vLayout.totalSizeHint()
        ##self.setMinimumWidth(totalMinimumSize.width())
        ###self.setMinimumHeight(MENU_ITEM_MIN_HEIGHT)
        ##self.setMinimumHeight(totalMinimumSize.height())
        ###self.setMaximumHeight(totalMinimumSize.height())


    ##def draw_menuItem(self, qp):
        ##pass
        ##widgetHeight = self.height()
        ##widgetWidth = self.width()

        ### line
        ##qp.setPen(QCOLOR_MENU_SEPARATOR_TEXT)
        ##qp.drawLine(0, 0, widgetWidth, 0)
        ##qp.drawLine(0, widgetHeight-1, widgetWidth, widgetHeight-1)


##class KMenuItem_toolSetting(KMenuItem):
#class KMenuItem_toolSetting(QtWidgets.QWidget):

    #def __init__(self, *args, **kwargs):
        #"""
        #kwargs:
            #label (string) - the text the appears on the menu item
            #command (function) - the command that runs on left click of the menu item
            #subMenu (KMenu) - the Menu that is the submenu (if this is one) assosiated with this menu item
        #"""

        #self.settingObject = args[0]
        #kwargs['label'] = self.settingObject.settingName + ':'
        ##super(KMenuItem_toolSetting, self).__init__(**kwargs)
        #super(KMenuItem_toolSetting, self).__init__()

        ## create layout
        #self.hLayout = PyQt.QtWidgets.QHBoxLayout()
        #self.setLayout(self.hLayout)
        #self.hLayout.setSpacing(0)
        #self.hLayout.setContentsMargins(QtCore.QMargins(10,0,10,0))

        ## label text
        #self._labelText = kwargs.get('label', '')
        #self.labelWidget = KLabel(self._labelText)
        #self.labelWidget.setPalette(QPALETTE_LABEL)
        #self.labelWidget.setFixedWidth(self.labelWidget.sizeHint().width())
        #self.labelWidget.setPalette(QPALETTE_INPUTITEM)
        #self.hLayout.addWidget(self.labelWidget)
        #self.hLayout.addSpacing(10)


        ## setting widget
        #self.settingWidget = self._getSettingInputWidget()
        #self.settingWidget.setFixedHeight(MENU_ITEM_MIN_HEIGHT-2)
        #self.settingWidget.setPalette(QPALETTE_INPUTITEM)
        #self.hLayout.addWidget(self.settingWidget)


        #self.hLayout.addStretch()
        #self.closeMenuAfterUse = False

    #def autoSize(self):
        #self.labelWidget.updateLabelText()

        ## set size
        #labelWidgetSizeHint = self.labelWidget.sizeHint()
        #labelWidgetWidthHint = labelWidgetSizeHint.width()
        #labelWidgetHeightHint = labelWidgetSizeHint.height()

        ## size and position
        #minHeight = MENU_ITEM_MIN_HEIGHT
        #minWidth = MENU_ITEM_MIN_HEIGHT + MENU_ITEM_EXTRA_WIDTH
        ##for child in self.children():
            ### width of all children
            ##if hasattr(child, 'sizeHint'):
                ##childWidth = child.sizeHint().width()
            ##else:
                ##childWidth = child.width()
            ##minWidth += childWidth


            ### height of largest child
            ##childHeight = child.height()
            ##if childHeight < minHeight:
                ##minHeight = childHeight

        ##self.settingWidget.setFixedHeight(minHeight)
        ##self.settingWidget.move(self.labelWidget.width()+40, 1,)

        ##self.setFixedWidth(minWidth)
        ##self.setFixedHeight(minHeight)


    #def _getSettingInputWidget(self):
        #valueType = self.settingObject.valueType.lower()

        #defaultValue = ka_preference.get(self.settingObject.settingLongName, None)
        #if defaultValue == None:
            #defaultValue = self.settingObject.defaultValue

        ## INT
        #if valueType == 'int':
            #settingInputWidget = PyQt.QtWidgets.QSpinBox(parent=self)
            #settingInputWidget.setValue(defaultValue)
            #self.connect(settingInputWidget, PyQt.QtCore.SIGNAL('valueChanged (int)'), self._changeSettingValue)
            #return settingInputWidget

        ## FLOAT
        #if valueType == 'float':
            #settingInputWidget = PyQt.QtWidgets.QDoubleSpinBox(defaultValue, parent=self)
            #settingInputWidget.setValue(defaultValue)
            #self.connect(settingInputWidget, PyQt.QtCore.SIGNAL('valueChanged (double)'), self._changeSettingValue)
            #return settingInputWidget

        ## STRING
        #elif valueType == 'string':
            #settingInputWidget = PyQt.QtWidgets.QLineEdit(defaultValue, parent=self)
            #self.connect(settingInputWidget, PyQt.QtCore.SIGNAL('returnPressed()'), self._changeSettingValue)
            #return settingInputWidget

        ## BOOL
        #elif valueType == 'bool':
            #settingInputWidget = PyQt.QtWidgets.QCheckBox(parent=self)
            #settingInputWidget.setChecked(defaultValue)

            #self.connect(settingInputWidget, PyQt.QtCore.SIGNAL('stateChanged (int)'), self._changeSettingValue)
            #return settingInputWidget

        ## ENUM
        #elif valueType == 'enum':
            #settingInputWidget = PyQt.QtWidgets.QComboBox(parent=self)
            #settingInputWidget.addItems(self.settingObject.enumValues)
            #settingInputWidget.setCurrentIndex(defaultValue)

            #self.connect(settingInputWidget, PyQt.QtCore.SIGNAL('currentIndexChanged (int)'), self._changeSettingValue)
            #return settingInputWidget

    #def _changeSettingValue(self):
        ## INT
        #if isinstance(self.settingWidget, PyQt.QtWidgets.QSpinBox):
            #newValue = self.settingWidget.value()

        ## FLOAT
        #if isinstance(self.settingWidget, PyQt.QtWidgets.QDoubleSpinBox):
            #newValue = self.settingWidget.value()

        ## STRING
        #if isinstance(self.settingWidget, PyQt.QtWidgets.QLineEdit):
            #newValue = self.settingWidget.text()

        ## BOOL
        #elif isinstance(self.settingWidget, PyQt.QtWidgets.QCheckBox):
            #newValue = self.settingWidget.isChecked()

        ## ENUM
        #elif isinstance(self.settingWidget, PyQt.QtWidgets.QComboBox):
            #newValue = self.settingWidget.currentIndex()

        #ka_preference.add(self.settingObject.settingLongName, newValue)

class KMenuItem_attrTool(KMenuItem):

    def __init__(self, *args, **kwargs):
        """A KmenuItem specificly for the attr tools, quick connect functionality
        """

        # selection
        context = ka_context.getCurrentContext()
        selection = context.getSelection()
        if not selection:
            selection = context.getHypershade_nodeUnderMouse()
            if selection:
                selection = [selection]

        super(KMenuItem_attrTool, self).__init__(**kwargs)
        self.closeMenuAfterUse = True

        self.attrTreeWidget = ka_attrTool_UI.AttrTreeWidget(parent=self, selection=selection, updateWithSelection=False)

        # hide header
        headerItem = self.attrTreeWidget.headerItem()
        self.attrTreeWidget.setItemHidden(headerItem, True)

        # Hide all columns except the the attrNames column
        for key in self.attrTreeWidget.columnInfoDict:
            index = self.attrTreeWidget.columnInfoDict[key]['index']

            if key != 'attrNames':
                self.attrTreeWidget.hideColumn(index)
            else:
                self.attrTreeWidget.visibleColumns[index] = None

        self.attrTreeWidget.populateAttrTree(selection=selection, mode='favorites')

        # RIGHT CLICK quick connect command
        @QtCore.Slot(QtWidgets.QTreeWidgetItem)
        def cmd(QWidgetItem, self=self):
            sourceAttrs = attrCommands.getSourceAttrs()

            if sourceAttrs:
                if len(sourceAttrs) == 1:
                    attrCommands.connectAttrs([QWidgetItem.attrObj], nodes=attrCommands.getNodeSelection())

                else:
                    attrCommands.connectAttrs([QWidgetItem.attrObj], nodes=attrCommands.getNodeSelection(), removeFromClipboard=True)

            self.attrTreeWidget.updateAttrTreeItem(QWidgetItem)
            #self.attrTreeWidget.clearSelection()

        self.attrTreeWidget.customSignals.itemRClickedSignal.connect(cmd)

        # LEFT CLICK quick connect command
        @QtCore.Slot(QtWidgets.QTreeWidgetItem)
        def cmd(QWidgetItem, self=self):
            selectedItems = self.attrTreeWidget.selectedItems()

            # add
            if QWidgetItem.isSelected():
                if len(selectedItems) == 1:
                    attrCommands.storeSourceAttrs([QWidgetItem.attrObj], nodes=attrCommands.getNodeSelection())
                else:
                    attrCommands.addToSourceAttrs([QWidgetItem.attrObj], nodes=attrCommands.getNodeSelection())
            # remove
            else:
                attrCommands.removeFromSourceAttrs([QWidgetItem.attrObj], nodes=[QWidgetItem.attrObj.node()])

        self.attrTreeWidget.customSignals.itemLClickedSignal.connect(cmd)

        # store modifiers pressed, so the release command can know if they have been released
        self.modifierWasPressed = False

        # KEY PRESS command
        @QtCore.Slot(int)
        def cmd(key, self=self):
            modifiers = PyQt.QtWidgets.QApplication.keyboardModifiers()
            if modifiers != PyQt.QtCore.Qt.NoModifier:
                self.modifierWasPressed = True

        self.attrTreeWidget.customSignals.keyPressedSignal.connect(cmd)

        # KEY RELEASE command
        @QtCore.Slot(int)
        def cmd(key, self=self):
            modifiers = PyQt.QtWidgets.QApplication.keyboardModifiers()
            if self.modifierWasPressed:
                # if no modifiers remaining held
                if modifiers == PyQt.QtCore.Qt.NoModifier:
                    self.parentMenu.closeMenu()

        self.attrTreeWidget.customSignals.keyReleasedSignal.connect(cmd)

        # item CLICK RELEASE command
        @QtCore.Slot(QtWidgets.QTreeWidgetItem)
        def cmd(QWidgetItem, self=self):
            mods = cmds.getModifiers()
            if not (mods & 1) > 0 and not (mods & 4) > 0:
                if self.attrTreeWidget.selectedItems():
                    self.parentMenu.closeMenu()

        self.attrTreeWidget.customSignals.itemRClickReleasedSignal.connect(cmd)
        self.attrTreeWidget.customSignals.itemLClickReleasedSignal.connect(cmd)

        self.attrTreeWidget.setMinimumWidth(self.attrTreeWidget.sizeHint().width())
        self.attrTreeWidget.setMinimumHeight(self.attrTreeWidget.sizeHint().height())
        #self.autoSize()

    def autoSize(self):
        indexOfAttrNames = self.attrTreeWidget.columnInfoDict['attrNames']['index']

        height = 0.0
        for attrLongName in self.attrTreeWidget.treeItemDict:
            numberOfItems = len(self.attrTreeWidget.treeItemDict)
            treeItem = self.attrTreeWidget.treeItemDict[attrLongName]
            QModelIndex = self.attrTreeWidget.indexFromItem(treeItem)
            heightPerItem = self.attrTreeWidget.indexRowSizeHint(QModelIndex)
            height = heightPerItem*(numberOfItems+1)
            break

        if height > 800:
            height = 800

        width = self.attrTreeWidget.sizeHintForColumn(indexOfAttrNames)
        self.attrTreeWidget.setColumnWidth(indexOfAttrNames, width+20)
        self.attrTreeWidget.setFixedWidth(width+40)
        self.attrTreeWidget.setFixedHeight(height+10)

        self.setFixedWidth(width+40)
        self.setFixedHeight(height+10)

