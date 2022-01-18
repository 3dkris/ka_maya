
#====================================================================================
#====================================================================================
#
# ka_menuWidget
#
# DESCRIPTION:
#   Custom Menu Widget for a custom pop up system
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
import time
import inspect

import pymel.core as pymel
import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMayaUI as OpenMayaUI
#from maya.app.general.mayaMixin import MayaQWidgetBaseMixin

import ka_maya.ka_qtWidgets as ka_qtWidgets
import ka_maya.ka_context as ka_context
import ka_maya.ka_attrTool.ka_attrTool_UI as ka_attrTool_UI
import ka_maya.ka_attrTool.attrCommands as attrCommands

PyQt = ka_qtWidgets.PyQt
QtGui = ka_qtWidgets.QtGui
QtCore = ka_qtWidgets.QtCore
QtWidgets = ka_qtWidgets.QtWidgets

PARENT_FOLDER = os.path.abspath(os.path.dirname(__file__))
ICON_FOLDER = os.path.abspath(os.path.join(PARENT_FOLDER, "icons",))

TOP_BAR_HEIGHT = 12
MIN_WIDTH = 50
MIN_HEIGHT = 200
MENU_ITEM_MIN_HEIGHT = 20
MENU_ITEM_EXTRA_WIDTH = 30
WINDOW_FRAME_THICKNESS = QtWidgets.QApplication.style().pixelMetric(QtWidgets.QStyle.PixelMetric.PM_DefaultFrameWidth)

ICON_BOARDER_BUFFER_PERCENT = 0.25 # percent of icon which is buffer between the icon and boarder
ICON_SIZE = int(MENU_ITEM_MIN_HEIGHT*(1-ICON_BOARDER_BUFFER_PERCENT))
ICON_BUFFER_BOARDER_PIXELS = int((MENU_ITEM_MIN_HEIGHT*ICON_BOARDER_BUFFER_PERCENT) * 0.5)





def getAllKaMenuWidgets():
    allKMenuWidgets = []
    #for widget in PyQt.QtWidgets.qApp.topLevelWidgets():
        #if hasattr(widget, '__class__'):
            #if widget.__class__.__name__ == 'KMenuWidget':
                #allKMenuWidgets.append(widget)

    for widget in ka_qtWidgets.getMayaWindow().children():
        if hasattr(widget, '__class__'):
            if widget.__class__.__name__ == 'Ka_menuWidget':
                allKMenuWidgets.append(widget)

    return allKMenuWidgets

def getAllUnpinnedKaMenuWidgets():
    """return all unpinned menus"""
    unPinnedKMenuWidgets = []
    for kaMenuWidget in getAllKaMenuWidgets():
        if hasattr(kaMenuWidget, 'pinState'):
            if not kaMenuWidget.pinState:
                unPinnedKMenuWidgets.append(kaMenuWidget)

    return unPinnedKMenuWidgets

def getAllPinnedKaMenuWidgets():
    """return all pinned menus"""
    pinnedKMenuWidgets = []
    for kaMenuWidget in getAllKaMenuWidgets():
        if hasattr(kaMenuWidget, 'pinState'):
            if kaMenuWidget.pinState:
                pinnedKMenuWidgets.append(kaMenuWidget)

    return pinnedKMenuWidgets



def clearAllKaMenuWidgets(unpinnedOnly=False):
    for kaMenuWidget in getAllKaMenuWidgets():
        if unpinnedOnly:
            if hasattr(kaMenuWidget, 'pinState'):
                if not kaMenuWidget.pinState:
                    kaMenuWidget.close()
                else:
                    for menuItem in kaMenuWidget.menuItems:
                        menuItem.subMenuWidget = None
            else:
                kaMenuWidget.close()
        else:
            kaMenuWidget.close()


def getIcon(iconValue):
    if isinstance(iconValue, list) or isinstance(iconValue, tuple):

        QPixMap = PyQt.QtGui.QPixmap(ICON_SIZE, ICON_SIZE)
        QPixMap.fill(PyQt.QtWidgets.QColor(int(255*iconValue[0]), int(255*iconValue[1]), int(255*iconValue[2]),))
        QIcon = PyQt.QtGui.QIcon(QPixMap)
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
        return QIcon


class _SubMenuConstructor(object):
    """a constructor class for adding sub menus to KMenus"""

    def __init__(self, kMenu, kSubMenu,):
        self.kMenu = kMenu
        self.kSubMenu = kSubMenu

    def __enter__(self):
        self.kMenu._setCurrentMenu(self.kSubMenu)

    def __exit__(self, _type, value, traceback):
        self.kMenu._endCurrentMenu()


class Ka_menu(object):

    def __init__(self, label=None, command=None, icon=None, rearIcon=None, showContext=None, menuPopulateCommand=None):
        """object which holds infomation about the structure of menu's. Menu widgets are generated
        from it.

        """

        self.label = label
        self.command = command
        self.icon = icon
        self.rearIcon = rearIcon
        self.showContext = showContext
        self.menuPopulateCommand = menuPopulateCommand

        self.menuItemObjects = [] # objects to be represented later by menu items
        self.menuItemObjects_args = [] # args to pass to the later creation of those menu items
        self.menuItemObjects_kwargs = [] # kwargs to pass to the later creation of those menu items
        self.menuItemObjects_contexts = [] # the context commands that deside if the menu item will show

        self.currentMenu = self
        self.currentMenuHierarchy = [self]


    def getAsMenuItem(self, parentMenu=None):
        kwargs = {}
        kwargs['label'] = self.label
        kwargs['icon'] = self.icon
        kwargs['subMenuObj'] = self
        kwargs['parentMenu'] = parentMenu
        kwargs['command'] = self.command

        widget = Ka_menu_item(**kwargs)
        return widget


    def getAsWindow(self, parentMenuItem=None):
        ka_menuWidget = Ka_menuWidget(parent=None, parentMenuItem=parentMenuItem)

        self.populateMenuItems(ka_menuWidget)

        # window size
        sizeHint = ka_menuWidget.sizeHint()

        ## desktop size
        #desktopWidget = QtWidgets.QDesktopWidget()
        #desktopRegion = desktopWidget.availableGeometry(idealPosition)
        #OOOOOOO = "desktopRegion"; print '%s: ' % OOOOOOO, eval(OOOOOOO), ' ', type(eval(OOOOOOO))

        # figure out windows creation position
        if parentMenuItem:
            topRight = parentMenuItem.mapToGlobal(QtCore.QPoint(parentMenuItem.width(), 0))
            topRight = parentMenuItem.parentMenu.mapFromGlobal(topRight)
            pos = parentMenuItem.parentMenu.pos()
            idealPosition = QtCore.QPoint(pos.x()+parentMenuItem.width(), pos.y()+parentMenuItem.pos().y()-(sizeHint.height()/2)+(parentMenuItem.height()/2))

        else:
            idealPosition = QtGui.QCursor().pos()
            idealPosition = ka_menuWidget.mapFromGlobal(idealPosition)
            idealPosition = ka_menuWidget.parent().mapFromGlobal(idealPosition)
            idealPosition = QtCore.QPoint(idealPosition.x(), idealPosition.y()-(sizeHint.height()/2))

        ka_menuWidget.move(idealPosition)

        return ka_menuWidget

    def addSubMenu(self, *args, **kwargs):
        """Adds a submenu to the menu
        args:
            label <string> - the display label of the menu

        kwargs:
            icon <path/fileName> - the path to the icon, or the file name if it exists in
                                   ka_maya.icons
        """

        subMenu = Ka_menu(*args, **kwargs)
        self.currentMenu.add(subMenu, *args, **kwargs)

        return _SubMenuConstructor(self, subMenu)

    def insertSubMenu(self, index, *args, **kwargs):
        """Adds a submenu to the menu
        args:
            label <string> - the display label of the menu

        kwargs:
            icon <path/fileName> - the path to the icon, or the file name if it exists in
                                   ka_maya.icons
        """

        subMenu = Ka_menu(*args, **kwargs)
        self.currentMenu.insert(index, subMenu, *args, **kwargs)

        return _SubMenuConstructor(self, subMenu)

    def _setCurrentMenu(self, kMenu):
        self.currentMenu = kMenu
        self.currentMenuHierarchy.append(kMenu)


    def _endCurrentMenu(self):
        self.currentMenuHierarchy.pop()
        self.currentMenu = self.currentMenuHierarchy[-1]


    def addSeparator(self, *args, **kwargs):
        """Adds a separator item to the menu
        args:
            label <string> - the display label of the separator

        """

        self.currentMenu.add(Ka_menu_seperator, **kwargs)


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


    def insert(self, index, *args, **kwargs):
        item = args[0]
        args = tuple(args[1:])

        if 'showContext' in kwargs:
            contextCommand = kwargs.pop('showContext')
        else:
            contextCommand = ka_context.trueContext

        self.currentMenu.menuItemObjects.insert(index, item)
        self.currentMenu.menuItemObjects_args.insert(index, args)
        self.currentMenu.menuItemObjects_kwargs.insert(index, kwargs)
        self.currentMenu.menuItemObjects_contexts.insert(index, contextCommand)


    def clear(self):
        self.currentMenu.menuItemObjects = []
        self.currentMenu.menuItemObjects_args = []
        self.currentMenu.menuItemObjects_kwargs = []
        self.currentMenu.menuItemObjects_contexts = []


    def pop(self, popPosition=None, parentMenu=None, parentMenuItem=None):
        """generate a menu under the mouse"""

        clearAllKaMenuWidgets(unpinnedOnly=True)

        ka_menuWidget = self.getAsWindow()

        # show
        ka_menuWidget.show()


    def populateMenuItems(self, ka_menuWidget):
        if self.menuPopulateCommand:
            self.menuPopulateCommand(self)

        # populate ===========================================================================
        for i, item in enumerate(self.menuItemObjects):
            itemArgs = self.menuItemObjects_args[i]
            itemKwargs = self.menuItemObjects_kwargs[i]
            itemContext = self.menuItemObjects_contexts[i]
            if itemContext():
                itemClass = item
                if not inspect.isclass(itemClass):
                    itemClass = item.__class__

                # TOOL - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
                if itemClass.__name__ == 'ToolObject':
                    tool = item

                    if 'showContext' in itemKwargs:
                        if not itemKwargs['showContext']():
                            continue

                    if tool.context is not None:
                        if not tool.context():
                            continue

                    itemKwargs['parentMenu'] = ka_menuWidget

                    # if no label passed in, use the tool's label
                    if 'label' not in itemKwargs:
                        itemKwargs['label'] = tool.label

                    # if label is a function, then it's result will function as the label
                    if hasattr(itemKwargs['label'], '__call__'):
                        itemKwargs['label'] = itemKwargs['label']()

                    # if no icon passed in, use the tool's icon
                    if 'icon' not in itemKwargs:
                        itemKwargs['icon'] = tool.icon
                    else:
                        if not itemKwargs['icon']:
                            itemKwargs['icon'] = tool.icon

                    # always display a rear icon, to indicate that it is a "tool"
                    itemKwargs['rearIcon'] = 'toolSettings_small.png'

                    # wrapper command, with args passed
                    def menuItemCmd(*args, **kwargs):
                        tool(*args, **kwargs)

                    itemKwargs['command'] = menuItemCmd

                    # create a ka_menu to generate the menu item and submenu
                    ka_menu = Ka_menu(label=itemKwargs['label'], command=tool, icon=itemKwargs['icon'], rearIcon=itemKwargs['rearIcon'])

                    if tool.__doc__:
                        ka_menu.add(ka_qtWidgets.DocStringWidget, tool)

                    if tool.settings:
                        ka_menu.add(ka_qtWidgets.ToolSettingsWidget, tool)

                    widget = ka_menu.getAsMenuItem(parentMenu=ka_menuWidget)
                    #widget = Ka_menu_item(**itemKwargs)


                # KA_MENU - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
                elif issubclass(itemClass, Ka_menu):
                    widget = item.getAsMenuItem(parentMenu=ka_menuWidget)

                elif isinstance(item, Ka_menu):
                    widget = item

                # KA_MENU_ITEM - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
                elif issubclass(itemClass, Ka_menu_item):
                    itemKwargs['parentMenu'] = ka_menuWidget
                    widget = item(*itemArgs, **itemKwargs)

                # QWIDGET - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
                elif issubclass(itemClass, QtWidgets.QWidget):
                    #widget = item(*itemArgs, **itemKwargs)
                    widget = item(parent=ka_menuWidget, *itemArgs, **itemKwargs)

                # function - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
                elif hasattr(item, '__call__'):
                    itemKwargs['parentMenu'] = ka_menuWidget
                    itemKwargs['command'] = item
                    widget = Ka_menu_item(*itemArgs, **itemKwargs)

                else:
                    #widget = QtWidgets.QTextEdit(item)
                    OOOOOOO = "item"; print '%s: ' % OOOOOOO, eval(OOOOOOO), ' ', type(eval(OOOOOOO))

                ka_menuWidget.addToMenu(widget)



class Ka_menuWidget(QtWidgets.QMainWindow):
    """
    args:
        label <string> - the label

    kwargs:
        parent <QWidget> - if None, then the maya window will be used as the parent

        kMenu <Kmenu> - the Ka_menu instance that generated the widget
    """

    STYLE_SHEET = """

    Ka_menuWidget {
        background-color: rgb(0, 0, 0);
    }

    Ka_menu_item {
        background-color: rgb(35, 35, 40);
        color: rgb(255, 35, 40);
        border-width: 1px;
        border-color: rgb(0, 0, 0);
        border-style:groove;

    }

    Ka_menu_item:hover {
        background-color: rgb(25, 70, 90);
        border-color: rgb(0, 255, 255);

    }

    Ka_menu_seperator {
        font-size: 4px;
    }

    Ka_menu_icon {
        background-color: rgb(255, 255, 255, 0);
        border-color: rgb(0, 255, 0, 0);
        border-width: 0;
        border-style: solid;
    }
    Ka_menu_icon:hover {
        background-color: rgb(255, 255, 255, 0);
        border-color: rgb(0, 255, 0, 0);
    }

    Ka_menu_titleBarWidget {
        background-color: rgb(255, 255, 255, 0);
    }

    Ka_menu_titleBarWidget:QPushButton {
        background-color: rgb(255, 0, 0);
    }
"""

    def __init__(self, *args, **kwargs):
        #parse ars
        label = kwargs.get('label', None)

        if 'parentMenuItem' in kwargs:
            self.parentMenuItem = kwargs.pop('parentMenuItem')
        else:
            self.parentMenuItem = None

        # get parent
        parent = kwargs.get('parent', None)
        if not parent:
            parent = ka_qtWidgets.getMayaWindow()

        super(Ka_menuWidget, self).__init__(parent=parent, )

        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        # style sheet
        self.setStyleSheet(self.STYLE_SHEET)

        # obj variables
        self.menuItems = []
        self.dragMoveState = False
        self.dragMoveStartCursorOffset = None
        self.pinState = False
        self.titleBar = None

        # focus
        #self.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.setFocusPolicy(QtCore.Qt.NoFocus)

        # main widget
        self.mainWidget = QtWidgets.QWidget(parent=self)
        self.setCentralWidget(self.mainWidget)

        # create Layout
        self.vLayout = QtWidgets.QVBoxLayout()
        self.vLayout.setSpacing(0)
        self.vLayout.setContentsMargins(QtCore.QMargins(0,0,0,0))

        self.mainWidget.setLayout(self.vLayout)


    def addToMenu(self, item):
        if isinstance(item, Ka_menu_item):
            self.menuItems.append(item)

        self.vLayout.addWidget(item)


    # SIZE EVENTS --------------------------------------------------------------
    def resizeEvent(self, event):
        sizeHint = self.vLayout.totalSizeHint()
        self.resize(sizeHint)
        event.accept()
        self.setMask(QtGui.QRegion(0,0, self.width(), self.height()))

        QtWidgets.QWidget.resizeEvent(self, event)

    ## FOCUS EVENTS -------------------------------------------------------------
    #def focusOutEvent(self, event):
        #if event.lostFocus():
            #print 'focus gone!'

            #if self.pinState is False:
                #event.accept()
                #self.deleteLater()


        #QtWidgets.QWidget.focusOutEvent(self, event)

    # CLOSE EVENTS -------------------------------------------------------------
    def closeEvent(self, event):
        for menuItem in self.menuItems:
            if menuItem.subMenuWidget is not None:
                if not menuItem.subMenuWidget.pinState:
                    try:
                        menuItem.subMenuWidget.close()
                    except: pass

        QtWidgets.QWidget.closeEvent(self, event)


    # MOUSE EVENTS -------------------------------------------------------------
    def mousePressEvent(self, event):
        button = event.button()
        globalCursorLocation = event.globalPos()

        ## left click
        #if button == QtCore.Qt.LeftButton:
            #pass
            ##if clickedChild:
            ##if hasattr(clickedChild, 'command'):

                ##if clickedChild.command:
                    ##clickedChild.command()

                ##if menuItemClicked:
                    ##if menuItemClicked.closeMenuAfterUse:
                        ##if not kMenuWidgetClicked.pinVisibility:


        ## right click
        #elif button == QtCore.Qt.RightButton:
            #if menuItemClicked:
                #if menuItemClicked.subMenu:
                    #if menuItemClicked.mouseOver_submenuWidgetIsPinned:
                        #menuItemClicked.mouseOver_submenuWidgetIsPinned = False

                    #else:
                        #menuItemClicked.mouseOver_submenuWidgetIsPinned = True
                    #menuItemClicked.update()

        # middle click
        if button == QtCore.Qt.MiddleButton:
            self.startDragMove(globalCursorLocation)




    def mouseReleaseEvent(self, event):
        button = event.button()

        # middle release
        if button == QtCore.Qt.MiddleButton:
            self.endDragMove()

    def mouseMoveEvent(self, event):
        globalCursorLocation = event.globalPos()

        if self.dragMoveState is True:
            self.dragMove(globalCursorLocation)

        event.accept()

        # Do regular stuff
        QtWidgets.QWidget.mouseMoveEvent(self, event)


    # DRAG METHODS -------------------------------------------------------------------
    def startDragMove(self, globalCursorLocation):
        # clear submenus before move, for visual cleaness
        self.clearSubMenuWidgets()

        self.dragMoveState = True
        dragMoveStartPosition = self.pos()
        self.dragMoveStartCursorOffset = globalCursorLocation - dragMoveStartPosition

        self.pinMenu()

    def dragMove(self, globalCursorLocation):
        newLocation = globalCursorLocation -self.dragMoveStartCursorOffset
        self.move(newLocation)

    def endDragMove(self):
        self.dragMoveState = False


    # PIN METHOD --------------------------------------------------------------------
    def pinMenu(self):
        if self.pinState is False:
            self.pinState = True
            titleBar = Ka_menu_titleBarWidget(parent=self, parentMenu=self)
            self.vLayout.insertWidget(0, titleBar)
            titleBar.show()

            clearAllKaMenuWidgets(unpinnedOnly=True)

    def clearSubMenuWidgets(self, clearPinnedMenuWidgets=False):
        # clear others
        for item in self.menuItems:
            if item.subMenuWidget:
                if not item.subMenuWidget.pinState or clearPinnedMenuWidgets:
                    try:
                        item.subMenuWidget.close()
                        item.subMenuWidget = None
                    except:
                        pass

# ==============================================================================================
#class Ka_menu_item(QtWidgets.QWidget):
class Ka_menu_item(QtWidgets.QPushButton):

    def __init__(self, *args, **kwargs):

        # parse args - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if 'label' in kwargs:
            label = kwargs.pop('label')
        else:
            label = None

        if 'icon' in kwargs:
            icon = kwargs.pop('icon')
        else:
            icon = None

        if 'parentMenu' in kwargs:
            self.parentMenu = kwargs.pop('parentMenu')
        else:
            self.parentMenu = None

        if 'subMenuObj' in kwargs:
            self.subMenuObj = kwargs.pop('subMenuObj')
        else:
            self.subMenuObj = None

        if 'rearIcon' in kwargs:
            rearIcon = kwargs.pop('rearIcon')
        else:
            if self.subMenuObj:
                rearIcon = 'subMenuArrow_small.png'
            else:
                rearIcon = None

        if 'command' in kwargs:
            self.command = kwargs.pop('command')
        else:
            self.command = None


        # init super - - - - - - - - - - - - - - - - - - - - - - - - - - -
        super(Ka_menu_item, self).__init__(*args, **kwargs)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        # instanceVariables - - - - - - - - - - - - - - - - - - - - - - - -
        self.subMenuWidget = None

        # create Layout - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.hLayout = QtWidgets.QHBoxLayout()
        self.hLayout.setContentsMargins(QtCore.QMargins(5,1,5,1))
        self.setLayout(self.hLayout)

        # icon
        self.iconWidget = Ka_menu_icon(icon=icon)
        self.hLayout.addWidget(self.iconWidget)

        # label
        if label is not None:
            self.qLabel = QtWidgets.QLabel(label)
            self.qLabel.setFixedWidth(self.qLabel.sizeHint().width())
            self.hLayout.addWidget(self.qLabel)

        self.hLayout.addStretch()

        # rearicon
        if rearIcon:
            self.rearIconWidget = Ka_menu_icon(icon=rearIcon)
            self.hLayout.addWidget(self.rearIconWidget)

        sizeHint = self.hLayout.totalSizeHint()
        self.setMinimumWidth(sizeHint.width())
        self.setMinimumHeight(sizeHint.height())


    # ENTER / LEAVE EVENTS -------------------------------------------------------------
    def enterEvent(self, event):

        if self.subMenuObj is not None and self.subMenuWidget is None:
            # clear existing menus
            self.parentMenu.clearSubMenuWidgets()

            # create subMenu
            self.subMenuWidget = self.subMenuObj.getAsWindow(parentMenuItem=self)

            # show
            self.subMenuWidget.show()

        ## clear others
        #for item in self.parentMenu.menuItems:
            #if item.subMenuWidget:
                #if item.subMenuWidget != self.subMenuWidget:
                    #if not item.subMenuWidget.pinState:
                        #try:
                            #item.subMenuWidget.close()
                            #item.subMenuWidget = None
                        #except:
                            #pass

        event.accept()
        QtWidgets.QWidget.enterEvent(self, event)

    def leaveEvent(self, event):
        event.accept()
        QtWidgets.QWidget.enterEvent(self, event)

    # MOUSE EVENTS -------------------------------------------------------------
    def mousePressEvent(self, event):
        button = event.button()
        globalCursorLocation = event.globalPos()

        # left click
        if button == QtCore.Qt.LeftButton:
            if self.command is not None:
                self.command()
                event.accept()

                modifiers = PyQt.QtWidgets.QApplication.keyboardModifiers()
                if modifiers == PyQt.QtCore.Qt.NoModifier:
                    clearAllKaMenuWidgets(unpinnedOnly=True)

        QtWidgets.QWidget.mousePressEvent(self, event)


# ==============================================================================================
class Ka_menu_icon(QtWidgets.QPushButton):

    def __init__(self, *args, **kwargs):
        super(Ka_menu_icon, self).__init__()

        self.setFixedSize(ICON_SIZE, ICON_SIZE)
        self.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)

        self.icon = kwargs.get('icon', None)
        if self.icon:
            self.setIcon(getIcon(self.icon))

    #def paintEvent(self, event):
        #if not self.icon:
            #event.accept()

        #QtWidgets.QPushButton.paintEvent(self, event)


# ==============================================================================================
class Ka_menu_titleBarWidget(Ka_menu_item):

    def __init__(self, *args, **kwargs):
        super(Ka_menu_titleBarWidget, self).__init__(*args, **kwargs)

        # close button
        self.closeButton = QtWidgets.QPushButton()
        #self.closeButton.setText('x')
        self.closeButton.setFixedHeight(ICON_SIZE)
        self.closeButton.setFixedWidth(ICON_SIZE)
        self.closeButton.setIcon(getIcon('close.png'))
        self.closeButton.setIconSize(QtCore.QSize(ICON_SIZE,ICON_SIZE))
        self.closeButton.setMask(QtGui.QRegion(0,0, ICON_SIZE-1, ICON_SIZE-1, QtGui.QRegion.Ellipse))

        #self.setFixedHeight(ICON_SIZE)
        self.hLayout.setContentsMargins(QtCore.QMargins(0,0,0,0))

        self.hLayout.addStretch()
        self.hLayout.addWidget(self.closeButton)

        self.closeButton.clicked.connect(self.parent().close)





# ==============================================================================================
#class Ka_menu_seperator(Ka_menu_item):
class Ka_menu_seperator(QtWidgets.QWidget):


    def __init__(self, *args, **kwargs):
        label = kwargs.get('label', None)
        parent = kwargs.get('parent', None)

        #super(Ka_menu_seperator, self).__init__(*args, **kwargs)
        super(Ka_menu_seperator, self).__init__(parent=parent)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        #self.setStyleSheet(self.STYLE_SHEET)

        # create Layout - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.hLayout = QtWidgets.QHBoxLayout()
        self.hLayout.setContentsMargins(QtCore.QMargins(0,1,0,1))
        self.setLayout(self.hLayout)

        # label
        if label is not None:
            #font = QtCore.QFont()
            #font.


            self.qLabel = QtWidgets.QLabel(label)
            self.qLabel.setFixedWidth(self.qLabel.sizeHint().width())
            self.hLayout.addWidget(self.qLabel)

        #self.hLayout.addStretch()


        frameWidget = QtWidgets.QFrame(parent=self)
        frameWidget.setFrameShape(QtWidgets.QFrame.HLine)
        self.hLayout.addWidget(frameWidget)

        self.setMinimumHeight((MENU_ITEM_MIN_HEIGHT/3)*2)

        sizeHint = self.hLayout.totalSizeHint()
        #self.setFixedHeight(sizeHint.height())







# ==============================================================================================
class Ka_menu_attrTool(Ka_menu_item):
#class Ka_menu_attrTool(QtWidgets.QWidget):

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

        super(Ka_menu_attrTool, self).__init__(**kwargs)

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
                    self.parentMenu.close()

        self.attrTreeWidget.customSignals.keyReleasedSignal.connect(cmd)

        # item CLICK RELEASE command
        @QtCore.Slot(QtWidgets.QTreeWidgetItem)
        def cmd(QWidgetItem, self=self):
            mods = cmds.getModifiers()
            if not (mods & 1) > 0 and not (mods & 4) > 0:
                if self.attrTreeWidget.selectedItems():
                    self.parentMenu.close()
                    OOOOOOO = "getAllKaMenuWidgets()"; print '%s: ' % OOOOOOO, eval(OOOOOOO), ' ', type(eval(OOOOOOO))

        self.attrTreeWidget.customSignals.itemRClickReleasedSignal.connect(cmd)
        self.attrTreeWidget.customSignals.itemLClickReleasedSignal.connect(cmd)

        sizeHint = self.attrTreeWidget.sizeHint()
        height = sizeHint.height()+10
        width = sizeHint.width()+40
        self.autoSize()


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