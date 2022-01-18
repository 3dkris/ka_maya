#====================================================================================
#====================================================================================
#
# ka_attrTool
#
# DESCRIPTION:
#   A UI and function set for dealing with maya attributes
#
# DEPENDENCEYS:
#   ka_preference
#
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
import re

import maya.cmds as cmds
import maya.mel as mel
import pymel.core as pymel
import maya.OpenMayaUI as mui

import ka_maya.ka_qtWidgets as ka_qtWidgets
PyQt = ka_qtWidgets.PyQt
QtGui = ka_qtWidgets.QtGui
QtCore = ka_qtWidgets.QtCore


import ka_maya.ka_python as ka_python #;reload(ka_python)
import ka_maya.ka_qtWidgets as ka_qtWidgets #;reload(ka_qtWidgets)
import ka_maya.ka_preference as ka_preference #;reload(ka_preference)
import ka_maya.ka_attrTool.attrCommands as attrCommands #;reload(attrCommands)
import ka_maya.ka_attrTool.attributeObj as attributeObj #;reload(attributeObj)
import ka_maya.ka_attrTool.attrFavorites as attrFavorites #;reload(attrFavorites)


# List of Attributes to always exclude
attrExclusionList = ['attributeAliasList']
acceptableAttrTypes = ['float', 'bool', 'string', 'int', 'matrix', 'vector', 'message']

### LEFT CLICK quick connect command
##@QtCore.Slot()
##def cmdBBB():
##    print 'EMIT B!!'



##class AttrTool_quickConnectPopup(QtGui.QWidgetAction): # NOT IN USE


##    def __init__(self, *args, **kwargs):
##        parent = args[0]

##        QtGui.QWidgetAction.__init__(self, parent)

##        selection = kwargs.get('selection', None)
##        if not selection:
##            selection = pymel.ls(selection=True)


##        # kwargs
##        kwargs['parent'] = parent
##        kwargs['updateWithSelection'] = False
##        kwargs['expandAll'] = True
##        kwargs['selection'] = selection

##        # Create Attr Tree
##        self.attrTreeWidget = AttrTreeWidget(**kwargs)
##        indexOfAttrNames = self.attrTreeWidget.columnInfoDict['attrNames']['index']
##        headerItem = self.attrTreeWidget.headerItem()
##        self.attrTreeWidget.setItemHidden(headerItem, True)


##        # Hide all columns except the the attrNames column
##        for key in self.attrTreeWidget.columnInfoDict:
##            index = self.attrTreeWidget.columnInfoDict[key]['index']

##            if key != 'attrNames':
##                self.attrTreeWidget.hideColumn(index)
##            else:
##                self.attrTreeWidget.visibleColumns[index] = None

##        self.attrTreeWidget.populateAttrTree(selection=selection, mode='favorites')


##        # size widget
##        height = 0.0
##        for attrLongName in self.attrTreeWidget.treeItemDict:
##            numberOfItems = len(self.attrTreeWidget.treeItemDict)
##            treeItem = self.attrTreeWidget.treeItemDict[attrLongName]
##            QModelIndex = self.attrTreeWidget.indexFromItem(treeItem)
##            heightPerItem = self.attrTreeWidget.indexRowSizeHint(QModelIndex)
##            height = heightPerItem*(numberOfItems+1)
##            break

##        width = self.attrTreeWidget.sizeHintForColumn(indexOfAttrNames)
##        self.attrTreeWidget.setColumnWidth(indexOfAttrNames, width+20)
##        self.attrTreeWidget.setFixedWidth(width+40)
##        self.attrTreeWidget.setFixedHeight(height+10)


##        # RIGHT CLICK quick connect command
##        def cmd(QWidgetItem, self=self):
##            print 'r-click'
##            sourceAttrs = attrCommands.getSourceAttrs()

##            if sourceAttrs:
##                if len(sourceAttrs) == 1:
##                    attrCommands.connectAttrs([QWidgetItem.attrObj], nodes=attrCommands.getNodeSelection())
##                    #attrCommands.connectAttrs([QWidgetItem.attrObj], nodes=[QWidgetItem.attrObj.node()])

##                else:
##                    attrCommands.connectAttrs([QWidgetItem.attrObj], nodes=attrCommands.getNodeSelection(), removeFromClipboard=True)
##                    #attrCommands.connectAttrs([QWidgetItem.attrObj], nodes=[QWidgetItem.attrObj.node()], removeFromClipboard=True)

##            self.attrTreeWidget.updateAttrTreeItem(QWidgetItem)
##            self.attrTreeWidget.clearSelection()

##        #self.connect(self.attrTreeWidget, QtCore.SIGNAL('itemRClicked(PyQt_PyObject)'), cmd)
##        self.connect(self.attrTreeWidget, itemRClickedSignal, cmd)

##        # LEFT CLICK quick connect command
##        @QtCore.Slot(QtGui.QTreeWidgetItem)
##        def cmdAAA(QWidgetItem, self=self):
##            selectedItems = self.attrTreeWidget.selectedItems()
##            print 'EMIT A!!'

##            # add
##            #if QWidgetItem in selectedItems:
##            if QWidgetItem.isSelected():
##                if len(selectedItems) == 1:
##                    attrCommands.storeSourceAttrs([QWidgetItem.attrObj], nodes=attrCommands.getNodeSelection())
##                else:
##                    attrCommands.addToSourceAttrs([QWidgetItem.attrObj], nodes=attrCommands.getNodeSelection())
##            # remove
##            else:
##                attrCommands.removeFromSourceAttrs([QWidgetItem.attrObj], nodes=[QWidgetItem.attrObj.node()])

##        #self.connect(self.attrTreeWidget, itemLClickedSignal, cmd)
##        self.attrTreeWidget.customSignals2.itemLClickedSignal.connect(cmdBBB)

##        # MODIFIER RELEASE command
##        def cmd(key, self=self):
##            modifiers = QtGui.QApplication.keyboardModifiers()

##            # if no modifiers remaining held
##            # Qt.NoModifier
##            #if modifiers != QtCore.Qt.ShiftModifier and modifiers != QtCore.Qt.ControlModifier:
##            if modifiers == QtCore.Qt.NoModifier:
##                parent.hide()
##        #self.connect(self.attrTreeWidget, QtCore.SIGNAL('keyReleased(PyQt_PyObject)'), cmd)
##        self.connect(self.attrTreeWidget, keyReleasedSignal, cmd)


##        def cmd(QWidgetItem, self=self):
##            print 'EMIT B!!'

##            mods = cmds.getModifiers()
##            if not (mods & 1) > 0 and not (mods & 4) > 0:
##                parent.hide()
##        #self.connect(self.attrTreeWidget, QtCore.SIGNAL('itemLClickReleased(PyQt_PyObject)'), cmd)
##        #self.connect(self.attrTreeWidget, itemLClickedSignal, cmd)
##        #self.attrTreeWidget.itemLClickedSignal.connect(cmd)
##        #self.connect(self.attrTreeWidget, QtCore.SIGNAL('itemRClickReleased(PyQt_PyObject)'), cmd)
##        self.connect(self.attrTreeWidget, itemRClickedSignal, cmd)


##        # set default widget
##        self.setDefaultWidget(self.attrTreeWidget)





class AttrTool_mainWindow(QtGui.QMainWindow):
    title = 'ka attrTool'

    font = QtGui.QFont('Sans Serif', 8.5)
    defaultFontSize = 8.5
    defaultFontType = 'DejaVu LGC Sans Mono'
    defaultFont = QtGui.QFont(defaultFontType, defaultFontSize)

    iconFolder = os.path.abspath( os.path.join( os.path.join( os.path.dirname(__file__), "..",), 'icons') )

    # Widget Dimentions
    windowWidth = 300
    windowHeight = 450
    treeItemHeight = 15
    defaultAttrTreeWidth = windowWidth
    defaultAttrTreeHeight = windowHeight-55
    heightOfHeaderButtons = 42


    def __init__(self,):
        windowArgs = [ka_qtWidgets.getMayaWindow()]
        if ka_preference.get('attrTool_windowOnTop', True):
            windowArgs.append(QtCore.Qt.WindowStaysOnTopHint)

        super(AttrTool_mainWindow, self).__init__(*windowArgs)

        self.setObjectName('ka_attrToolUIWindow')
        self.setWindowTitle('Attr Tool')
        self.setObjectName('windowWidget')

        menuBar = self.menuBar()
        cursorPos = QtGui.QCursor.pos()
        self.setGeometry(cursorPos.x(), cursorPos.y(), self.windowWidth+2, self.windowHeight)

        # kwargs
        kwargs = {}
        kwargs['parent'] = self
        kwargs['updateWithSelection'] = ka_preference.get('ka_attrTool_pinSelected', False)


        # Attr Tree
        self.attrTreeWidget = AttrTreeWidget(**kwargs)
        self.attrTreeWidget.setFixedSize(self.defaultAttrTreeWidth, self.defaultAttrTreeHeight)
        self.attrTreeWidget.move(0, self.heightOfHeaderButtons)
        self.connect(self.attrTreeWidget, QtCore.SIGNAL('attrTreeUpdated()'), self.updateWindowTitle)


        # Search Bar
        self.menuLineEdit = QtGui.QLineEdit(self)
        self.menuLineEdit.move(0, 2)
        self.menuLineEdit.setFixedSize((self.windowWidth*0.666), 20);
        self.connect(self.menuLineEdit, QtCore.SIGNAL('textChanged(const QString&)'), self.applyAttrTreeSearchFiler)

        # Filter Types Dropdown
        self.listFilter_comboBox = QtGui.QComboBox(self)
        self.listFilter_comboBox.move((self.windowWidth*0.666), 2)
        self.listFilter_comboBox.setFixedSize((self.windowWidth)*0.333, 18);
        self.listFilter_comboBox.addItems(['favorites', 'no filter', 'connectable', 'userDefined', 'keyable'])
        def cmd(i, self=self):
            mode = self.listFilter_comboBox.currentText()
            self.attrTreeWidget.populateAttrTree(mode=mode)
        self.connect(self.listFilter_comboBox, QtCore.SIGNAL('currentIndexChanged(int)'), cmd)

        # expandButton
        self.toggleExpandButton = QtGui.QPushButton('+', self)
        self.toggleExpandButton.move(2, 22)
        self.toggleExpandButton.setFixedSize(20, 20);
        self.connect(self.toggleExpandButton, QtCore.SIGNAL('clicked()'), self.toggleExpandButtonCmd)

        # collapseButton
        self.toggleCollapseButton = QtGui.QPushButton('-', self)
        self.toggleCollapseButton.move(22, 22)
        self.toggleCollapseButton.setFixedSize(20, 20);
        self.connect(self.toggleCollapseButton, QtCore.SIGNAL('clicked()'), self.toggleCollapseButtonCmd)

        # displayButton
        self.displayButton = QtGui.QPushButton('Display: ', self)
        self.displayButton.setObjectName('displayButton')
        self.displayButton.move(42, 22)
        self.displayButton.setFixedSize(80, 20);
        self.r_clickMenu(self.displayButton)

        # showConnectionsButton
        self.echoCmdsButton = QtGui.QPushButton('Echo Cmds:', self)
        self.echoCmdsButton.setObjectName('echoCmdsButton')
        self.echoCmdsButton.move(122, 22)
        self.echoCmdsButton.setFixedSize(90, 20);
        self.r_clickMenu(self.echoCmdsButton)

        # winodw Button
        self.windowCmdsButton = QtGui.QPushButton('Winodw:', self)
        self.windowCmdsButton.setObjectName('windowCmdsButton')
        self.windowCmdsButton.move(212, 22)
        self.windowCmdsButton.setFixedSize(90, 20);
        self.r_clickMenu(self.windowCmdsButton)

        # Misc
        self.menuHierarchy = []
        self.r_clickMenu(self.attrTreeWidget)
        self.r_clickMenu(self)


        self.updateDisplay()    # also populates AttrTree
        self.attrTreeWidget.populateAttrTree()

    def updateWindowTitle(self):
        selection = cmds.ls(selection=True)
        if selection:
            windowTitle = ''
            if len(selection) > 1:
                windowTitle += '[%s]  ' % str(len(selection))

            windowTitle += '%s' % selection[-1]

            self.setWindowTitle(windowTitle)

    def toggleExpandButtonCmd(self):
        self.updateTreeExpand(expandState=True)

    def toggleCollapseButtonCmd(self):
        self.updateTreeExpand(expandState=False)

    def updateDisplay(self):
        attrTreeWidth = 0
        activeColumns = ['attrNames']
        columnInfoDict = self.attrTreeWidget.columnInfoDict

        displayShortNames = ka_preference.get('ka_attrTool_displayShortNames', False)
        displayAliasNames = ka_preference.get('ka_attrTool_displayAliasNames', False)
        displayValues = ka_preference.get('ka_attrTool_displayValues', False)
        displayInputs = ka_preference.get('ka_attrTool_displayInputs', False)
        displayOutputs = ka_preference.get('ka_attrTool_displayOutputs', False)

        if displayShortNames:
            activeColumns.append('shortName')

        if displayAliasNames:
            activeColumns.append('aliasName')

        if displayValues:
            activeColumns.append('values')

        if displayInputs:
            activeColumns.append('inputs')

        if displayOutputs:
            activeColumns.append('outputs')


        for key in activeColumns:
            attrTreeWidth += columnInfoDict[key]['width']


        self.visibleColumns = {}
        for key in columnInfoDict:
            columnIndex = columnInfoDict[key]['index']

            if key in activeColumns:
                width = columnInfoDict[key]['width']
                self.attrTreeWidget.showColumn(columnIndex)
                self.attrTreeWidget.setColumnWidth(columnIndex, width)
                self.attrTreeWidget.visibleColumns[columnIndex] = None

            else:
                self.attrTreeWidget.hideColumn(columnIndex)
                self.attrTreeWidget.setColumnWidth(columnIndex, 0)


        self.attrTreeWidget.update(mode=self.listFilter_comboBox.currentText())


        self.attrTreeWidget.setFixedWidth(attrTreeWidth+20)
        self.setFixedWidth(attrTreeWidth+24)
        self.setFixedHeight(self.windowHeight)

        realWidth= 0
        for key in activeColumns:
            index = columnInfoDict[key]['index']
            realWidth += self.attrTreeWidget.columnWidth(index)
            print key, self.attrTreeWidget.columnWidth(index)



    def applyAttrTreeSearchFiler(self, string):
        if string:
            for attrLongName in self.treeItemDict:
                if string not in attrLongName:
                    self.attrTreeWidget.setItemHidden(self.treeItemDict[attrLongName], True)
                    self.hiddenTreeItems.append(self.treeItemDict[attrLongName])
                else:
                    self.attrTreeWidget.setItemHidden(self.treeItemDict[attrLongName], False)

        else:
            if self.hiddenTreeItems:
                for treeItemWidget in self.hiddenTreeItems:
                    self.attrTreeWidget.setItemHidden(treeItemWidget, False)


    def r_clickMenu(self, widget):
        '''add and return a QMenu that will pop when the widget is r_clicked'''

        contextMenu = QtGui.QMenu(self)

        if isinstance(widget, QtGui.QPushButton):
            def popCmd(self=self):
                self.currentMenu = contextMenu
                self.menuHierarchy = [contextMenu]

                contextMenu.clear()
                getattr(self, str(widget.objectName())+'Menu')()#(contextMenu)
                width = widget.width()
                self.emptyMenuItem()
                contextMenu.setMinimumWidth(width)
            widget.setMenu(contextMenu)
            self.connect(contextMenu, QtCore.SIGNAL('aboutToShow ()'), popCmd)

        else:
            def popCmd(QPoint, self=self):
                self.currentMenu = contextMenu
                self.menuHierarchy = [contextMenu]

                contextMenu.clear()
                getattr(self, str(widget.objectName())+'Menu')()
                height = widget.height()
                width = widget.width()
                self.emptyMenuItem()
                contextMenu.exec_(widget.mapToGlobal(QPoint))

            widget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
            self.connect(widget, QtCore.SIGNAL('customContextMenuRequested(const QPoint&)'), popCmd)

        return contextMenu

    # Menu Items ----------------------------------------------------------------------------------------------------------

    def emptyMenuItem(self,):
        return ka_qtWidgets.addMenuItem('', self.currentMenu)

    def addPrefMenuItem_bool(self, label, preferenceKey, defaultPreferenceValue, command=None):
        return ka_qtWidgets.addPrefMenuItem_bool(label, preferenceKey, defaultPreferenceValue, self.currentMenu, command=command, font=self.font)

    def addPrefMenuItem_radio(self, listOfLabels, preferenceKey, defaultPreferenceValue, command=None):
        ka_qtWidgets.prefMenuItem_radioButtons(preferenceKey, listOfLabels, defaultPreferenceValue, self.currentMenu, command=command)

    def addSeparatorItem(self, label=''):
        return ka_qtWidgets.addSeparatorItem(self.currentMenu, label=label)

    def addMenuItem(self, label, command=None, icon=None):
        """adds menu item to a Qmenu"""

        font = self.font
        font.setBold(False)

        action = ka_qtWidgets.addMenuItem(label, self.currentMenu, command=command, icon=icon, font=font)
        return action

    def startSubmenu(self, subMenuName, icon=None, tearOff=False, command=None):
        if self.currentMenu:
            currentMenuItem = self.currentMenu
        else:
            currentMenuItem = self.menu

        subMenu = ka_qtWidgets.addSubmenuItem(subMenuName, icon=icon, tearOff=tearOff, command=command, parentMenu=currentMenuItem, font=self.font)

        self.currentMenu = subMenu
        self.menuHierarchy.append(subMenu)

        return subMenu

    def endSubmenu(self,):
        self.menuHierarchy.pop()
        self.currentMenu = self.menuHierarchy[-1]

    def getSelectedAttrs(self,):
        return self.attrTreeWidget.getSelectedAttrs()

    def getAllAttrs(self):
        return self.attrTreeWidget.getAllAttrs()

    def getSelectedOrAllAttrs(self):
        attrObjs = self.attrTreeWidget.getSelectedAttrs()
        if not attrObjs:
            attrObjs = self.attrTreeWidget.getAllAttrs()

        return attrObjs


    def mainAttrTreeWidgetMenu(self):
        selection = self.getSelectedAttrs()

        def cmd():
            #selectedAttrs = attrCommands.storeSourceAttrs(self.getSelectedOrAllAttrs())
            attrCommands.copyAttrs(self.getSelectedOrAllAttrs())
        self.addMenuItem('COPY    -store sourceAttr', command=cmd, icon='copy.png')

        # Paste
        def cmd():
            attrCommands.pasteAttrs(self.getSelectedAttrs())
            self.attrTreeWidget.populateAttrTree()
            self.attrTreeWidget.clearSelection()
        self.addMenuItem('PASTE    -sourceAttr value', command=cmd, icon='paste.png')

        # Connect
        def cmd():
            attrCommands.connectAttrs(self.getSelectedAttrs())
            self.attrTreeWidget.populateAttrTree()
            self.attrTreeWidget.clearSelection()
        self.addMenuItem('CONNECT    -sourceAttr to attr', command=cmd, icon='connect.png')

        # only show dissconnect menu item if there is an input in the selected items
        for attrObject in selection:
            if attrObject.inputs():

                # disconnect attr from input
                def cmd():
                    attrCommands.disconnectAttrs(self.getSelectedAttrs())
                    self.updateSelectedTreeItems()
                    self.attrTreeWidget.clearSelection()
                self.addMenuItem('DISCONNECT    -attr', cmd, icon='disconnect.png')
                break

        self.addSeparatorItem() # --------------------------------------------

        if self.startSubmenu('CONSTRAIN    -sourceNode to node', icon='pointConstraint.png'):

            # Point Constraint
            def cmd(): attrCommands.constrainNodes(self.getSelectedAttrs(), constraintType='pointConstraint', maintainOffset=ka_preference.get('attrTool_pointConstrain_maintainOffset', False))
            if self.startSubmenu('Point Constraint', command=cmd):
                self.addMenuItem(label='options:',)
                self.addPrefMenuItem_bool('    maintain offset', 'attrTool_pointConstrain_maintainOffset', False)
                self.endSubmenu()


            # Orient Constraint
            def cmd(): attrCommands.constrainNodes(self.getSelectedAttrs(), constraintType='orientConstraint', maintainOffset=ka_preference.get('attrTool_orientConstrain_maintainOffset', False))
            if self.startSubmenu('Orient Constraint', command=cmd):
                self.addMenuItem(label='options:',)
                self.addPrefMenuItem_bool('    maintain offset', 'attrTool_orientConstrain_maintainOffset', False)
                self.endSubmenu()


            # Scale Constraint
            def cmd(): attrCommands.constrainNodes(self.getSelectedAttrs(), constraintType='scaleConstraint', maintainOffset=ka_preference.get('attrTool_scaleConstrain_maintainOffset', False))
            #self.addMenuItem('Scale Constraint', command=cmd)
            if self.startSubmenu('Scale Constraint', command=cmd):
                self.addMenuItem(label='options:',)
                self.addPrefMenuItem_bool('    maintain offset', 'attrTool_scaleConstrain_maintainOffset', False)
                self.endSubmenu()

            # Aim Constraint
            def cmd(): attrCommands.constrainNodes(self.getSelectedAttrs(), constraintType='aimConstraint', maintainOffset=ka_preference.get('attrTool_aimConstrain_maintainOffset', False))
            if self.startSubmenu('Aim Constraint', command=cmd):
                self.addMenuItem(label='options:',)
                self.addPrefMenuItem_bool('    maintain offset', 'attrTool_aimConstrain_maintainOffset', False)

                self.endSubmenu()

            self.endSubmenu()

        # Set Driven Key
        def cmd():
            attrCommands.setDrivenKey(self.getSelectedAttrs())
            self.attrTreeWidget.populateAttrTree()
            self.attrTreeWidget.clearSelection()
        self.addMenuItem('DRIVEN KEY    -sourceAttr to key to attr', command=cmd, icon='key.png')


        if self.startSubmenu('...'):
            def cmd(): attrCommands.copyAttrs(self.getSelectedOrAllAttrs(), copyConnections=False)
            self.addMenuItem('copy attr values', command=cmd)

            def cmd(): attrCommands.copyAttrs(self.getSelectedOrAllAttrs(), nonDefaultOnly=False)
            self.addMenuItem('copy all values (include non default)', command=cmd)

            def cmd(): attrCommands.copyAttrs(self.getSelectedOrAllAttrs(), copyConnections=False)
            self.addMenuItem('copy values only (no connections)', command=cmd)

            def cmd(): attrCommands.copyAttrs(self.getSelectedOrAllAttrs(), copyValues=False)
            self.addMenuItem('copy connections only (no values)', command=cmd)

            self.endSubmenu()


        self.addSeparatorItem() # --------------------------------------------

        def cmd():
            self.attrTreeWidget.addAttrsToFavorites(self.getSelectedAttrs())
            self.attrTreeWidget.populateAttrTree()
        self.addMenuItem('add attrs to favorites', command=cmd, icon='addToFavorites')

        def cmd():
            self.attrTreeWidget.removeFromFavorites(self.getSelectedAttrs())
            self.attrTreeWidget.populateAttrTree()
        self.addMenuItem('remove attrs to favorites', command=cmd, icon='removeFromFavorites')

        self.addSeparatorItem() # --------------------------------------------

        def cmd(): attrCommands.selectAttrInputsAndOutputs(self.getSelectedOrAllAttrs(), selectOutputs=False)
        self.addMenuItem('select inputs', command=cmd)

        def cmd(): attrCommands.selectAttrInputsAndOutputs(self.getSelectedOrAllAttrs(), selectInputs=False)
        self.addMenuItem('select outputs', command=cmd)

        def cmd(): attrCommands.selectAttrInputsAndOutputs(self.getSelectedOrAllAttrs())
        self.addMenuItem('select inputs & outputs', command=cmd)
        self.addMenuItem('select inputs & outputs', command=cmd)



    def displayButtonMenu(self): # ______________________________________________________________

        def cmd():
            self.updateDisplay()
        self.addPrefMenuItem_bool('Attr Values', 'ka_attrTool_displayValues', False, command=cmd)

        def cmd():
            self.updateDisplay()
        self.addPrefMenuItem_bool('Attr Inputs', 'ka_attrTool_displayInputs', False, command=cmd)

        def cmd():
            self.updateDisplay()
        self.addPrefMenuItem_bool('Attr Outputs', 'ka_attrTool_displayOutputs', False, command=cmd)

        def cmd():
            self.updateDisplay()
        self.addPrefMenuItem_bool('Attr ShortNames', 'ka_attrTool_displayShortNames', False, command=cmd)

        def cmd():
            self.updateDisplay()
        self.addPrefMenuItem_bool('Attr Alias', 'ka_attrTool_displayAliasNames', False, command=cmd)

    def echoCmdsButtonMenu(self): # ______________________________________________________________

        def cmd(): self.updateDisplay()
        self.addPrefMenuItem_bool('Echo Attr Commands', 'echoCommands', False, command=cmd)

        self.startSubmenu('echo type')     #////////////////////////

        def cmd(): pass
        self.addPrefMenuItem_radio(['Maya cmds', 'pymel cmds', 'pymel object oriented'], 'echoType', 0, command=cmd)

        self.endSubmenu()                  #\\\\\\\\\\\\\\\\\\\\\\\\

        self.addSeparatorItem() # --------------------------------------------

        def cmd():
            print attrCommands.eccoAttrs(self.getSelectedAttrs(), echoAll=True)
        self.addMenuItem('Echo Nodes    (createNodes, nonDefault-setAttrs, connections)', command=cmd)

        def cmd(): print attrCommands.eccoAttrs(self.getSelectedOrAllAttrs(), echoAll=False, echoSetAttrs=True, echoConnections=True)
        self.addMenuItem('Echo Attrs    (setAttrs, connections)', command=cmd)

        def cmd(): print attrCommands.eccoAttrs(self.getSelectedOrAllAttrs(), echoAll=False, echoSetAttrs=True)
        self.addMenuItem('Echo createNodes', command=cmd)

        def cmd(): print attrCommands.eccoAttrs(self.getSelectedOrAllAttrs(), echoAll=False, echoSetAttrs=True)
        self.addMenuItem('Echo setAttrs', command=cmd)

        def cmd(): print attrCommands.eccoAttrs(self.getSelectedOrAllAttrs(), echoAll=False, echoConnections=True)
        self.addMenuItem('Echo connections', command=cmd)

    def windowCmdsButtonMenu(self): # ______________________________________________________________

        def cmd():
            self.updateDisplay()
            self.attrTreeWidget.updateWithSelection = ka_preference.get('attrTool_windowOnTop')
        self.addPrefMenuItem_bool('Window Always On Top', 'attrTool_windowOnTop', True, command=cmd)

        def cmd():
            self.pinSelectedState = ka_preference.get('ka_attrTool_pinSelected')
        self.addPrefMenuItem_bool('Window Update on selection change', 'ka_attrTool_pinSelected', False, command=cmd)






class AttrTreeSignals(QtCore.QObject):
    itemRClickedSignal = QtCore.Signal(QtGui.QTreeWidgetItem)
    itemLClickedSignal = QtCore.Signal(QtGui.QTreeWidgetItem)
    itemRClickReleasedSignal = QtCore.Signal(QtGui.QTreeWidgetItem)
    itemLClickReleasedSignal = QtCore.Signal(QtGui.QTreeWidgetItem)
    keyPressedSignal = QtCore.Signal(int)
    keyReleasedSignal = QtCore.Signal(int)



class AttrTreeWidget(QtGui.QTreeWidget):


    columnInfoDict = { 'attrNames':{'index': 0,
                                    'width': 300,
                                    'label': 'Attribute Name:',
                                   },

                       'shortName':{'index': 1,
                                    'width': 60,
                                    'label': 'Short Name:',
                                   },

                       'aliasName':{'index': 2,
                                    'width': 100,
                                    'label': 'Alias Name:',
                                   },

                       'values':{'index': 3,
                                 'width': 60,
                                 'label': 'Value:',
                                },

                       'inputs':{'index': 4,
                                 'width': 125,
                                 'label': 'inputs:',
                                },

                       'outputs':{'index': 5,
                                  'width': 200,
                                  'label': 'outputs:',
                                 },
                     }

    defaultFontSize = 8.5
    defaultFontType = 'DejaVu LGC Sans Mono'
    defaultFont = QtGui.QFont(defaultFontType, defaultFontSize)

    def __init__(self, *args, **kwargs):
        parent=kwargs['parent']
        QtGui.QTreeWidget.__init__(self, parent=parent)



        self.customSignals = AttrTreeSignals()


        updateWithSelection = kwargs.get('updateWithSelection', True)

        # object name will be used to assosiate it with its own unique mayaUI Object which will
        # serve as a parent to the assosiated script jobs
        objectName = kwargs.get('objectName', 'mainAttrTreeWidget')
        self.setObjectName(objectName)

        # AttrTreeWidget settings
        self.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.setFont(self.defaultFont)
        self.expandedItemsDict = ka_preference.get('attrTool_expandedItems', {})
        self.setIndentation(15)


        # Vars
        selection = kwargs.get('selection', None)
        if not selection:
            selection = pymel.ls(selection=True)

        self.expandAll = kwargs.get('expandAll', False)
        self.visibleColumns = {}
        self.treeItemDict = {}
        self.attributeJobIds = {}
        self.lastSelection = []
        self.hiddenTreeItems = []
        self.attrTreeIsPopulating = False
        self.updateWithSelection = kwargs.get('updateWithSelection', True)


        # columns
        self.setColumnCount(len(self.columnInfoDict))
        for key in self.columnInfoDict:
            self.setColumnWidth(self.columnInfoDict[key]['index'], self.columnInfoDict[key]['width'])

        headerLabelList = []
        headerLabelDict = {}

        for key in self.columnInfoDict:
            headerLabelDict[self.columnInfoDict[key]['index']] = self.columnInfoDict[key]['label']

        for key in sorted(headerLabelDict):
            headerLabelList.append(headerLabelDict[key])

        self.setHeaderLabels(headerLabelList)


        # Conections
        # Connect command to memorize which items are expanded
        def cmd(widget, self=self): self.treeItemExpanded(widget, True)
        self.connect(self, QtCore.SIGNAL('itemExpanded (QTreeWidgetItem *)'), cmd)

        def cmd(widget, self=self): self.treeItemExpanded(widget, False)
        self.connect(self, QtCore.SIGNAL('itemCollapsed (QTreeWidgetItem *)'), cmd)


        # this command will be run whenever a value for an item in the UI has been
        # changed.
        def attrValueChanged(widgetItem):
            if not self.attrTreeIsPopulating:
                text = str(widgetItem.text(self.columnInfoDict['values']['index']))
                if text:
                    if text != str(widgetItem.oldValue):
                        self.attrTreeIsPopulating = True

                        attrCommands.setAttrsFromText([widgetItem.attrObj], text)
                        self.updateAttrTreeItem(widgetItem)
                        self.clearSelection()

                        self.attrTreeIsPopulating = False

        self.connect(self, QtCore.SIGNAL('itemChanged (QTreeWidgetItem *,int)'), attrValueChanged)

        # Selection Changed Script Job
        if updateWithSelection:
            #self.scriptJobWindowName = str(self.objectName())+'_scriptJobWindow'
            self.scriptJobWindowName = 'attrTool_scriptJobWindow'
            if cmds.window(self.scriptJobWindowName, exists=True):
                cmds.deleteUI(self.scriptJobWindowName)
            cmds.window(self.scriptJobWindowName)

            def selectionChanged(self=self, scriptJobWindowName=self.scriptJobWindowName, ):
                '''run if maya selection is changed, destroys scriptJobWindowName if called while window is not visisble'''
                try: self.update()

                except: # self destruct
                    pymel.warning('an error occured with update, closing attr tree thing')
                    if cmds.window(scriptJobWindowName, exists=True):
                        cmds.deleteUI(scriptJobWindowName)

            jobId = cmds.scriptJob(event=['SelectionChanged', selectionChanged], parent=self.scriptJobWindowName)


    def update(self, mode='favorites'):
        selection = pymel.ls(selection=True)
        if selection:
            if self.updateWithSelection:
                if not self.lastSelection or selection[-1] != self.lastSelection[-1]:
                    self.populateAttrTree(selection=selection, mode=mode)
                    self.lastSelection = selection
                    self.emit(QtCore.SIGNAL("attrTreeUpdated()"))

                self.raise_()

    def updateTreeExpand(self, expandState=None):

        for widget in self.treeItemDict.values():
            if expandState:
                self.expandItem(widget)

            else:
                self.collapseItem(widget)

    def populateAttrTree(self, selection=None, mode='favorites',):
        if not selection:
            selection = pymel.ls(selection=True)

        if mode == 1:
            traceback.print_stack()

        if selection:
            if not self.attrTreeIsPopulating:    # to stop this from being run again before it finishes
                t0 = time.clock()
                self.attrTreeIsPopulating = True

                self.deleteAttributeScriptJobs()
                self.clear()
                self.treeItemDict = {}

                node = selection[-1]
                nodeType = node.nodeType()

                attrs = []

                #--------------------------------------------------------
                # Come up with initial list of attrs to be proccessed
                #
                # Use favorites IF there are any for this node
                if mode == 'favorites':
                    attrFavoritesDict = ka_preference.get('attrFavorites', {})
                    # check that there are favorites saved for given nodeType
                    if not attrFavoritesDict.has_key(nodeType): mode = 'no filter'
                    elif not attrFavoritesDict[nodeType]: mode = 'no filter'

                    else:
                        attrList = attrFavoritesDict[nodeType]

                        if not attrList:
                            mode = 'no filter'
                            attrs = pymel.listAttr(node, hasData=True,)

                        else:
                            attrs.extend(attrList)
                            attrs.extend(pymel.listAttr(node, connectable=True, hasData=True, userDefined=True))

                # No Filter
                elif mode == 'no filter':
                    attrs = pymel.listAttr(node, hasData=True,)

                # Connectable
                elif mode == 'connectable':
                    attrs = pymel.listAttr(node, connectable=True, hasData=True,)

                # Other Mode
                else:
                    listAttrKwargs = {mode: True}
                    attrs = pymel.listAttr(node, connectable=True, hasData=True, **listAttrKwargs)
                print 'timerA: '+str(time.clock()-t0);t0=time.clock()

                #--------------------------------------------------------
                # Add Attrs to Tree
                #
                # validate that attribute meets all filters
                if attrs:
                    attrObjs = attrCommands.listRelevantAttrs(node, baseAttributes=attrs)
                    print 'timerB: '+str(time.clock()-t0);t0=time.clock()

                    # add a item in the tree for each object, if one already exists for an
                    # attribute of the same name, repurpose it for the new attrObject. Then
                    # clean the unused items
                    usedAttrObjDict = {}

                    for attrObj in attrObjs:
                        self.addAttrToTree(attrObj, expandAll=self.expandAll)

                self.attrTreeIsPopulating = False
                print 'timerC: '+str(time.clock()-t0);t0=time.clock()


    def addAttrToTree(self, attrObj, expandAll=False):
        # If an item was already in the menu (ie: you selected a new node of the same
        # nodeType) then reuse that QTreeWidgetItem to save time
        QTreeWidgetItem = None
        attrLongName = attrObj.attrLongName()
        if attrLongName in self.treeItemDict:
            QTreeWidgetItem = self.treeItemDict[attrLongName]

        # Expand hierchy items
        else:
            attrParentLongName = attrObj.attrParentLongName()
            if attrParentLongName:
                if attrParentLongName in self.treeItemDict:
                    parentWidget = self.treeItemDict[attrParentLongName]
                    QTreeWidgetItem = QtGui.QTreeWidgetItem(parentWidget)

                    if expandAll:
                        self.expandItem(parentWidget)

                    else:
                        expandedItemsKey = '%s.%s' % (attrObj.nodeType(), attrParentLongName)

                        if expandedItemsKey in self.expandedItemsDict:
                            self.expandItem(parentWidget)
                            self.treeItemExpanded(parentWidget, True)


            if not QTreeWidgetItem:
                QTreeWidgetItem = QtGui.QTreeWidgetItem(self,)# menuListWidget

            self.treeItemDict[attrObj.attrLongName()] = QTreeWidgetItem

        QTreeWidgetItem.attrObj = attrObj
        self.updateAttrTreeItem(QTreeWidgetItem)

        if self.columnIsVisible('values'):
            if attrObj.exists():
                if attrObj.isSimple():
                    def attributeChangedCmd(attrLongName=attrObj.attrLongName(), scriptJobWindowName=self.scriptJobWindowName):
                        if self.isVisible():
                            self.updateAttrTreeItem(self.treeItemDict[attrLongName])

                        else:
                            if cmds.window(scriptJobWindowName, exists=True):
                                cmds.deleteUI(scriptJobWindowName)

                    if attrLongName in self.attributeJobIds:
                        pymel.scriptJob(kill=self.attributeJobIds[attrLongName])

                    jobId = cmds.scriptJob(attributeChange=['%s.%s' % (attrObj.nodeLongName(), attrObj.attrLongName()), attributeChangedCmd], parent=self.scriptJobWindowName)
                    self.attributeJobIds[attrLongName] = jobId


    def updateSelectedTreeItems(self):
        selectedWidgets = self.selectedItems()
        for widget in selectedWidgets:
            self.updateAttrTreeItem(widget, refresh=True)


    def updateAttrTreeItem(self, treeWidgetItem, refresh=False):
        """changes the display name and color of the widget to indicate attitional information about
        the attribute"""

        attrObj = treeWidgetItem.attrObj

        attrNameLabel = attrObj.attrName()

        if self.columnIsVisible('shortName'):
            if attrObj.attrShortName() != attrObj.attrName():
                treeWidgetItem.setText(1, '%s' % attrObj.attrShortName())


        colorKwArgs = {
                       'color' : None,
                       'bold' : False,
                       'italic' : False,
                       'textColor' : [1, 1, 1,],
                      }

        inputs = []
        outputs = []

        if attrObj.exists():
            inputs = attrObj.inputs(refresh=True)
            #if inputs:
                #treeWidgetItem.setText(4, str(inputs[0]))
                #inputType = inputs[0].nodeType()

            #if self.columnIsVisible('outputs'):
                #outputs = attrObj.outputs()
                #if outputs:
                    #outputsDisplayString = ''
                    #for output in outputs:
                        #outputsDisplayString += ', ' + output
                    #treeWidgetItem.setText(5, outputsDisplayString)


            # Deal with the Value Column if it is being displayed
            if self.columnIsVisible('values'):
                treeWidgetItem.oldValue = None
                if not attrObj.isMulti():
                    valueColumnIndex = self.columnInfoDict['values']['index']

                    if attrObj.isSimple():
                        value = attrObj.value(refresh=True)
                        if value != None:
                            if isinstance(value, float):
                                value = round(value, 4)
                            valueString = str(value)

                            # Do Not change unless different from previous values, to avoid triggering
                            # unessisary QT signals
                            if valueString != treeWidgetItem.oldValue:
                                treeWidgetItem.oldValue = value    # must be set BEFORE actually changing the text
                                treeWidgetItem.setText(valueColumnIndex, str(value))
                                # PYSIDE FAIL
                                # treeWidgetItem.setBackgroundColor(valueColumnIndex, QtGui.QColor(int(0.7*255), int(0.7*255), int(0.7*255)))

                        if not attrObj.isLocked() or attrObj.exists() == False:
                            self.openPersistentEditor(treeWidgetItem, self.columnInfoDict['values']['index'])

        #if not attrObj.exists():
            #colorKwArgs['italic'] = True
            #colorKwArgs['textColor'] = [0.5, 0.5, 0.5,]

        #else:
            #if inputs:
                #colorKwArgs['bold'] = True

                #if 'Constraint' in inputType:
                    #colorKwArgs['color']  = [0.639215686275, 0.796078431373, 0.941176470588]
                    #colorKwArgs['textColor'] = [0, 0, 0]

                #elif 'animCurve' in inputType:
                    #colorKwArgs['color'] = [0.870588235294, 0.447058823529, 0.478431372549]
                    #colorKwArgs['textColor'] = [0, 0, 0]

                #else:
                    #colorKwArgs['color'] = [ 0.945098039216, 0.945098039216, 0.647058823529]
                    #colorKwArgs['textColor'] = [0, 0, 0]

            #elif attrObj.isLocked():
                #colorKwArgs['color'] = [ 0.408888888889, 0.462222222222, 0.515555555556]
                #colorKwArgs['textColor'] = [0, 0, 0]

            #elif attrObj.isInChannelBox():
                #if not attrObj.isKeyable():
                    #colorKwArgs['color'] = [ 0.302222222222, 0.302222222222, 0.302222222222]
                    #colorKwArgs['textColor'] = [0, 0, 0]

        # PYSIDE FAIL
        # self.colorTreeWidgetItem(treeWidgetItem, **colorKwArgs)
        treeWidgetItem.setText(0, '%s' % attrNameLabel)


    def colorTreeWidgetItem(self, widget, color=None, opacity=1, textColor=[0,0,0], bold=True, italic=False, font=None):

        # Does this item require a unique font?
        uniqueFont = None
        if bold or italic or font:
            uniqueFont = QtGui.QFont(self.defaultFontType, self.defaultFontSize)
            if bold: uniqueFont.setBold(bold)
            if italic: uniqueFont.setItalic(italic)

        # apply coloring and font to each column
        for i in self.visibleColumns.keys():
            if uniqueFont:
                widget.setFont(i, uniqueFont)

            if textColor:
                widget.setTextColor(i, QtGui.QColor(textColor[0]*255, textColor[1]*255, textColor[2]*255, opacity*255))

            if color:
                widget.setBackgroundColor(i, QtGui.QColor(int(color[0]*255), int(color[1]*255), int(color[2]*255), int(opacity*255)))
            #else:
                #widget.setBackgroundColor(i, QtGui.QColor(200, 200, 200, 0))


    def getSelectedAttrs(self,):
        selectedWidgets = self.selectedItems()

        attrs = []
        for widget in selectedWidgets:
            attrs.append(widget.attrObj)
        return attrs

    def getAllAttrs(self):
        allWidgets = self.treeItemDict.values()

        attrs = []
        for widget in allWidgets:
            attrs.append(widget.attrObj)
        return attrs

    def deleteAttributeScriptJobs(self):
        for key in self.attributeJobIds:
            pymel.scriptJob(kill=self.attributeJobIds[key])
        self.attributeJobIds = {}


    def columnIsVisible(self, columnKey):
        if self.columnInfoDict[columnKey]['index'] in self.visibleColumns:
            return True
        else:
            return False


    def treeItemExpanded(self, widget, state):
        if not self.attrTreeIsPopulating:
            expandedItemsDict = self.expandedItemsDict
            key = '%s.%s' % (widget.attrObj.nodeType(), widget.attrObj.attrLongName())
            if state:
                expandedItemsDict[key] = True
            else:
                if key in expandedItemsDict:
                    expandedItemsDict.pop(key)

            ka_preference.set('attrTool_expandedItems', expandedItemsDict)
            self.expandedItemsDict = expandedItemsDict


    def addAttrsToFavorites(self, attrObjs):
        attrFavoritesDict = ka_preference.get('attrFavorites', {})
        for attrObj in attrObjs:
            nodeType = attrObj.node().nodeType()

            if attrFavoritesDict.has_key(nodeType):
                attrs = attrFavoritesDict[nodeType]
            else:
                attrs = []

            if attrObj.attrLongName() not in attrs:
                attrs.append(attrObj.attrLongName())

            attrFavoritesDict[nodeType] = sorted(attrs)

        ka_preference.add('attrFavorites', attrFavoritesDict)


    def removeFromFavorites(self, attrObjs):
        attrFavoritesDict = ka_preference.get('attrFavorites', {})
        for attrObj in attrObjs:
            nodeType = attrObj.node().nodeType()

            if attrFavoritesDict.has_key(nodeType):
                attrs = attrFavoritesDict[nodeType]
            else:
                attrs = []

            if attrObj.attrLongName() in attrs:
                attrs.remove(attrObj.attrLongName())

            attrFavoritesDict[nodeType] = sorted(attrs)

        ka_preference.add('attrFavorites', attrFavoritesDict)



    def mousePressEvent(self, QMouseEvent):
        # default behaviour
        QtGui.QTreeWidget.mousePressEvent(self, QMouseEvent)

        # custom behaviour
        QTreeWidgetItem =  self.itemAt(QMouseEvent.pos())
        if QTreeWidgetItem:
            if QMouseEvent.button() == QtCore.Qt.RightButton:
                self.customSignals.itemRClickedSignal.emit(QTreeWidgetItem)

            elif QMouseEvent.button() == QtCore.Qt.LeftButton:
                self.customSignals.itemLClickedSignal.emit(QTreeWidgetItem)

        #super(AttrTreeWidget, self).mousePressEvent(QMouseEvent)

    def mouseReleaseEvent(self, QMouseEvent):
        QTreeWidgetItem =  self.itemAt(QMouseEvent.pos())

        if QMouseEvent.button() == QtCore.Qt.RightButton:
            self.customSignals.itemRClickReleasedSignal.emit(QTreeWidgetItem)

        elif QMouseEvent.button() == QtCore.Qt.LeftButton:
            self.customSignals.itemLClickReleasedSignal.emit(QTreeWidgetItem)

        QtGui.QTreeWidget.mouseReleaseEvent(self, QMouseEvent)
        #super(AttrTreeWidget, self).mouseReleaseEvent(QMouseEvent)


    def keyPressEvent(self, QKeyEvent):
        self.customSignals.keyPressedSignal.emit(QKeyEvent)
        super(AttrTreeWidget, self).keyPressEvent(QKeyEvent)

    def keyReleaseEvent(self, QKeyEvent):
        self.customSignals.keyReleasedSignal.emit(QKeyEvent)
        super(AttrTreeWidget, self).keyReleaseEvent(QKeyEvent)




class AttrTool_addAttrWindow(QtGui.QMainWindow):
    title = 'add Attribute'

    font = QtGui.QFont('Sans Serif', 8.5)
    defaultFontSize = 8.5
    defaultFontType = 'DejaVu LGC Sans Mono'
    defaultFont = QtGui.QFont(defaultFontType, defaultFontSize)

    # Widget Dimentions
    windowWidth = 300
    windowHeight = 450


    def __init__(self,):
        super(QtGui.QMainWindow, self).__init__(ka_qtWidgets.getMayaWindow())

        self.setObjectName('AttrTool_addAttrWindow')
        self.setWindowTitle(self.title)
        self.setFixedWidth(self.windowWidth)

        self.mainRowLayout = QtGui.QFormLayout(self)
        layout = self.mainRowLayout

        self.secondRowStart = 110
        self.currentRow = 5
        self.rowHeight = 20
        self.inputFields = {}
        def addInput(label, inputType, self=self, inputList=None):
            label = QtGui.QLabel(label+':', self)
            inputFieldWidth = self.windowWidth-self.secondRowStart-10

            if inputType == 'string':
                inputField = QtGui.QLineEdit(self)

            if inputType == 'float':
                inputField = QtGui.QLineEdit(self)
                inputFieldWidth = inputFieldWidth/2

            if inputType == 'list':
                inputField = QtGui.QComboBox(self)
                inputField.setMaxVisibleItems(100)
                for item in inputList:
                    inputField.addItem(item)

            label.setGeometry(5, self.currentRow, self.secondRowStart, self.rowHeight)
            inputField.setGeometry(self.secondRowStart, self.currentRow, inputFieldWidth, self.rowHeight)
            self.currentRow += self.rowHeight
            self.inputFields[label] = inputField


        addInput('Long Name', 'string')
        addInput('Short Name', 'string')
        addInput('Nice Name', 'string')

        attrTypeList = ['float', 'int', 'bool', 'enum', 'string', '----------']
        allTypeList = attributeObj.attrTypes.keys()
        for key in attributeObj.dataTypes.keys():
            if key not in allTypeList:
                allTypeList.append(key)

        attrTypeList.extend(allTypeList)

        addInput('attribute Type', 'list', inputList=attrTypeList)

        self.currentRow += self.rowHeight/2

        addInput('Default Value', 'float')

        self.currentRow += self.rowHeight/2

        addInput('Max Value', 'float')
        addInput('Min Value', 'float')

        self.currentRow += self.rowHeight/2

        addInput('Soft Min Value', 'float')
        addInput('Soft Max Value', 'float')

        self.currentRow += self.rowHeight/2

        self.addButton = QtGui.QPushButton('Add Attr', self)
        self.addButton.setGeometry(5, self.currentRow, self.windowWidth-10, self.rowHeight*2)
        self.currentRow += self.rowHeight*2

        self.setFixedHeight(self.currentRow+10)

        #inputField = QtGui.QLineEdit(self)




def press():
    """called by hotkeyPress"""

    global openUIToggle
    global ka_attrToolUIWindow

    if not 'ka_attrToolUIWindow' in globals():
        openUI()

    elif not ka_attrToolUIWindow.isVisible():
        openUI()

    else:
        try: ka_attrToolUIWindow.close()
        except: pass

def release():
    """called by hotkeyRelease"""
    pass


def openUI():
    """main function to launch UI"""

    global attrTool_mainWindowUI
    try: attrTool_mainWindowUI.close()
    except: pass

    attrTool_mainWindowUI = AttrTool_mainWindow()
    attrTool_mainWindowUI.show()

def attrTool_addAttrWindow_openUI():
    global attrTool_addAttrWindowUI
    try: attrTool_addAttrWindowUI.close()
    except: pass

    attrTool_addAttrWindowUI = AttrTool_addAttrWindow()
    attrTool_addAttrWindowUI.show()