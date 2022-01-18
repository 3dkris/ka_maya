#====================================================================================
#====================================================================================
#
# ka_hyperShade
#
# DESCRIPTION:
#   tools for filtering current selection based on UI inputs
#
# DEPENDENCEYS:
#   None
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


import maya.cmds as cmds
import maya.mel as mel
import pymel.core as pymel

import ka_maya.ka_qtWidgets as ka_qtWidgets
PyQt = ka_qtWidgets.PyQt
QtGui = ka_qtWidgets.QtGui
QtCore = ka_qtWidgets.QtCore
QtWidgets = ka_qtWidgets.QtWidgets

import re

class UI(QtWidgets.QMainWindow):
    title = 'ka selection filter tool'

    STYLE_SHEET = """
    QPushButton {
        background-color: rgb(180, 90, 0);
    }
    QComboBox {
        background-color: rgb(68, 107, 163);
    }
    QSpinBox {
        background-color: rgb(68, 107, 163);
    }
"""

    def __init__(self):
        '''A custom window with a demo set of ui widgets'''

        parent = ka_qtWidgets.getMayaWindow()
        super(UI2, self).__init__(parent)

        self.setWindowTitle(self.title)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setStyleSheet(self.STYLE_SHEET)


        self.centralWidget = QtWidgets.QWidget()
        self.setCentralWidget(self.centralWidget)

        self.verticleLayout = QtWidgets.QVBoxLayout()
        self.centralWidget.setLayout(self.verticleLayout)
        self.verticleLayout.setSpacing(0)

        # Search Filter Widgets ------------------------------------------------
        self.searchFilterGroupBox = QtWidgets.QGroupBox(self.centralWidget)
        self.searchFilterGroupBox.setTitle("Filter by name")
        self.verticleLayout.addWidget(self.searchFilterGroupBox)

        self.searchFilterVLayout = QtWidgets.QVBoxLayout()
        self.searchFilterGroupBox.setLayout(self.searchFilterVLayout)

        self.searchFilterHLayout = QtWidgets.QHBoxLayout()
        self.searchFilterVLayout.addLayout(self.searchFilterHLayout)

        self.searchFilterVLayoutA = QtWidgets.QVBoxLayout()
        self.searchFilterHLayout.addLayout(self.searchFilterVLayoutA)
        self.searchFilterVLayoutA.setSpacing(1)
        self.searchFilterVLayoutB = QtWidgets.QVBoxLayout()
        self.searchFilterHLayout.addLayout(self.searchFilterVLayoutB)
        self.searchFilterVLayoutB.setSpacing(1)

        # Search For:
        label = QtWidgets.QLabel()
        label.setText("Filter by name")
        self.searchFilterVLayoutA.addWidget(label)

        self.search_lineEdit = QtWidgets.QLineEdit()
        self.search_lineEdit.setReadOnly(False)
        self.searchFilterVLayoutB.addWidget(self.search_lineEdit)

        # Case:
        label = QtWidgets.QLabel()
        label.setText("Case:")
        self.searchFilterVLayoutA.addWidget(label)

        self.searchCaseSensitive_comboBox = QtWidgets.QComboBox()
        self.searchCaseSensitive_comboBox.setFixedWidth(200)
        self.searchFilterVLayoutB.addWidget(self.searchCaseSensitive_comboBox)
        self.searchCaseSensitive_comboBox.addItem("case sensitive")
        self.searchCaseSensitive_comboBox.addItem("ignore case")

        # Scope:
        label = QtWidgets.QLabel()
        label.setText("Scope:")
        self.searchFilterVLayoutA.addWidget(label)

        self.scopeHLayout = QtWidgets.QHBoxLayout()
        self.searchFilterVLayoutB.addLayout(self.scopeHLayout)

        self.scopeKeepPrune_comboBox = QtWidgets.QComboBox()
        self.scopeHLayout.addWidget(self.scopeKeepPrune_comboBox)
        self.scopeKeepPrune_comboBox.addItem("Keep")
        self.scopeKeepPrune_comboBox.addItem("Prune")

        self.searchScope_comboBox = QtWidgets.QComboBox()
        self.scopeHLayout.addWidget(self.searchScope_comboBox)
        self.searchScope_comboBox.addItem("Only those with Occurrence")
        self.searchScope_comboBox.addItem("Only those Starting with")
        self.searchScope_comboBox.addItem("Only those Ending with")

        self.scopeHLayout.addStretch()

        # Filter Button
        self.filter_button = QtWidgets.QPushButton()
        self.searchFilterVLayout.addWidget(self.filter_button)
        self.filter_button.setText("Filter")
        spacer = self.verticleLayout.addSpacing(10)


        # Filter By Type -------------------------------------------------------
        self.filterByTypeGroupBox = QtWidgets.QGroupBox()
        self.filterByTypeGroupBox .setTitle("Filter By Type")
        self.verticleLayout.addWidget(self.filterByTypeGroupBox)

        self.filterByTypeVLayout = QtWidgets.QVBoxLayout()
        self.filterByTypeGroupBox.setLayout(self.filterByTypeVLayout)

        self.filterByTypeHLayout = QtWidgets.QHBoxLayout()
        self.filterByTypeVLayout.addLayout(self.filterByTypeHLayout)

        self.filterByTypeVLayoutA = QtWidgets.QVBoxLayout()
        self.filterByTypeHLayout.addLayout(self.filterByTypeVLayoutA)
        self.filterByTypeVLayoutA.setSpacing(1)
        self.filterByTypeVLayoutB = QtWidgets.QVBoxLayout()
        self.filterByTypeHLayout.addLayout(self.filterByTypeVLayoutB)
        self.filterByTypeVLayoutB.setSpacing(1)
        self.filterByTypeVLayoutC = QtWidgets.QVBoxLayout()
        self.filterByTypeHLayout.addLayout(self.filterByTypeVLayoutC)
        self.filterByTypeVLayoutC.setSpacing(1)

        # Filter by Node Type selector
        self.filterByTypeVLayoutA.addSpacing(1)

        self.rule1_comboBoxKeepPrune_comboBox = QtWidgets.QComboBox()
        self.filterByTypeVLayoutA.addWidget(self.rule1_comboBoxKeepPrune_comboBox)
        self.rule1_comboBoxKeepPrune_comboBox.addItem("keep")
        self.rule1_comboBoxKeepPrune_comboBox.addItem("prune")
        self.rule1_comboBoxKeepPrune_comboBox.setFixedWidth(100)

        self.rule1_comboBox = QtWidgets.QComboBox()
        self.filterByTypeVLayoutB.addWidget(self.rule1_comboBox)

        self.rule2_comboBoxKeepPrune_comboBox = QtWidgets.QComboBox()
        self.filterByTypeVLayoutA.addWidget(self.rule2_comboBoxKeepPrune_comboBox)
        self.rule2_comboBoxKeepPrune_comboBox.addItem("keep")
        self.rule2_comboBoxKeepPrune_comboBox.addItem("prune")
        self.rule2_comboBoxKeepPrune_comboBox.setFixedWidth(100)

        self.rule2_comboBox = QtWidgets.QComboBox()
        self.filterByTypeVLayoutB.addWidget(self.rule2_comboBox)

        # Include shapes option
        label = QtWidgets.QLabel()
        label.setText("Inlcude Shapes:")
        label.setFixedWidth(100)
        self.filterByTypeVLayoutC.addWidget(label)

        self.rule1_considerShapecheckBox = QtWidgets.QCheckBox()
        self.filterByTypeVLayoutC.addWidget(self.rule1_considerShapecheckBox)

        label = QtWidgets.QLabel()
        label.setText("Inlcude Shapes:")
        label.setFixedWidth(100)
        self.filterByTypeVLayoutC.addWidget(label)

        self.rule2_considerShapecheckBox = QtWidgets.QCheckBox()
        self.filterByTypeVLayoutC.addWidget(self.rule2_considerShapecheckBox)

        # Preview Widgets ------------------------------------------------------
        self.previewHLayout = QtWidgets.QHBoxLayout()
        self.verticleLayout.addLayout(self.previewHLayout)
        self.previewHLayout.setSpacing(0)
        self.previewHLayout.setContentsMargins(0,0,0,0)

        # Selection:
        self.selectionPreviewGroupBox = QtWidgets.QGroupBox()
        self.selectionPreviewGroupBox.setTitle("Selection:")
        self.previewHLayout.addWidget(self.selectionPreviewGroupBox)

        self.selectionPreviewLayout = QtWidgets.QVBoxLayout()
        self.selectionPreviewGroupBox.setLayout(self.selectionPreviewLayout)
        self.selectionPreviewLayout.setSpacing(0)
        self.selectionPreviewLayout.setContentsMargins(0,0,0,0)

        self.nameAndNumber_selection_listWidget = QtWidgets.QListWidget()
        self.selectionPreviewLayout.addWidget(self.nameAndNumber_selection_listWidget)

        # Preview Results
        self.resultsPreviewGroupBox = QtWidgets.QGroupBox()
        self.resultsPreviewGroupBox .setTitle("Preview Results:")
        self.previewHLayout.addWidget(self.resultsPreviewGroupBox )

        self.resultsPreviewLayout = QtWidgets.QVBoxLayout()
        self.resultsPreviewGroupBox.setLayout(self.resultsPreviewLayout)

        self.previewResults_listWidget = QtWidgets.QListWidget()
        self.resultsPreviewLayout.addWidget(self.previewResults_listWidget)
        self.resultsPreviewLayout.setSpacing(0)
        self.resultsPreviewLayout.setContentsMargins(0,0,0,0)

        # Filter Button
        self.filterByType_button = QtWidgets.QPushButton()
        self.filterByTypeVLayout.addWidget(self.filterByType_button)
        self.filterByType_button.setText("Filter By Type")
        spacer = self.verticleLayout.addSpacing(10)


        ##name and number
        self.connect(self.search_lineEdit, QtCore.SIGNAL('textChanged(const QString&)'), self.loadPreviewResults)
        self.connect(self.searchCaseSensitive_comboBox, QtCore.SIGNAL('currentIndexChanged (int)'), self.loadPreviewResults)
        self.connect(self.scopeKeepPrune_comboBox, QtCore.SIGNAL('currentIndexChanged (int)'), self.loadPreviewResults)
        self.connect(self.searchScope_comboBox, QtCore.SIGNAL('currentIndexChanged (int)'), self.loadPreviewResults)
        self.connect(self.rule1_comboBoxKeepPrune_comboBox, QtCore.SIGNAL('currentIndexChanged (int)'), self.loadPreviewResults)
        self.connect(self.rule1_comboBox, QtCore.SIGNAL('currentIndexChanged (int)'), self.loadPreviewResults)
        self.connect(self.rule1_considerShapecheckBox, QtCore.SIGNAL('stateChanged (int)'), self.loadPreviewResults)
        self.connect(self.rule2_comboBoxKeepPrune_comboBox, QtCore.SIGNAL('currentIndexChanged (int)'), self.loadPreviewResults)
        self.connect(self.rule2_comboBox, QtCore.SIGNAL('currentIndexChanged (int)'), self.loadPreviewResults)
        self.connect(self.rule2_considerShapecheckBox, QtCore.SIGNAL('stateChanged (int)'), self.loadPreviewResults)

        self.connect(self.filter_button, QtCore.SIGNAL('clicked()'), self.filter)
        self.connect(self.filterByType_button, QtCore.SIGNAL('clicked()'), self.filter)

        self.selection = {}
        self.selectionNodeTypes = {}
        self.selectionInheritedNodeTypes = {}
        self.selectionShapeNodeTypes = {}
        self.selectedNodeNames = {}

        self.update()
        self.search_lineEdit.setFocus()

    def storeSelectionInfo(self):
        selection = pymel.ls(selection=True, dependencyNodes=True)

        self.selectionIds = []
        nodeIdsUsed = {}
        for each in iter(selection):
            nodeId = each.__hash__()
            self.selectionIds.append(nodeId)

            if nodeId not in self.selection:
                nodeTypes = each.nodeType(inherited=True)
                shapes = pymel.listRelatives(each, shapes=True)

                #nodes
                self.selection[nodeId] = each

                # types
                self.selectionNodeTypes[nodeId] = nodeTypes[-1]
                self.selectionInheritedNodeTypes[nodeId] = nodeTypes

                # shape types
                self.selectionShapeNodeTypes[nodeId] = []
                if shapes:
                    for shape in shapes:
                        shapeNodeType = shape.nodeType()
                        self.selectionShapeNodeTypes[nodeId].append(shapeNodeType)

                # node names
                self.selectedNodeNames[nodeId] = each.nodeName()

                nodeIdsUsed[nodeId] = True

            else:
                nodeIdsUsed[nodeId] = True

        for nodeId in iter(self.selectionIds):
            if nodeId not in nodeIdsUsed:
                self.selection.pop(nodeId)
                self.selectionNodeTypes.pop(nodeId)
                self.selectionInheritedNodeTypes.pop(nodeId)
                self.selectedNodeNames.pop(nodeId)
                self.selectionShapeNodeTypes.pop(nodeId)

    def update(self):
        self.storeSelectionInfo()
        self.loadSelection()
        self.loadPreviewResults()
        pass

    def closeEvent(self, event):
        if cmds.window(scriptJobDummyWindow, exists=True):
            cmds.deleteUI(scriptJobDummyWindow)
        event.accept() # let the window close

    def filter(self):
        """filter selection"""

        filteredNodeIds = self.processFilter()
        selection = []
        for nodeId in iter(filteredNodeIds):
            selection.append(self.selection[nodeId])
        pymel.select(selection, replace=True)


    def loadPreviewResults(self):
        """preview filter selection"""
        previewNodeIds = self.processFilter()
        self.previewResults_listWidget.clear()
        for nodeId in iter(previewNodeIds):
            self.previewResults_listWidget.addItem(self.selectedNodeNames[nodeId])

    #################################################################################
    ##
    ##    01: loadSelection
    ##
    #################################################################################
    def loadSelection(self):

        selectionNames = []

        nodeTypes = []
        givenrule1 = str(self.rule1_comboBox.currentText())
        givenrule2 = str(self.rule2_comboBox.currentText())

        # clear type comboBoxs and add the '' Value
        self.rule1_comboBox.clear()
        self.rule2_comboBox.clear()
        self.rule1_comboBox.addItem('')
        self.rule2_comboBox.addItem('')

        # if there was a value selected before for either type, preserve it
        if givenrule1:
            nodeTypes.append(givenrule1)
        if givenrule2:
            nodeTypes.append(givenrule2)


        # iterate through selection
        for nodeId in iter(self.selectionIds):

            selectionNames.append(self.selectedNodeNames[nodeId])

            # add objects type to the list of types to filter comboBox
            nodeType = self.selectionNodeTypes[nodeId]
            if nodeType not in nodeTypes:
                nodeTypes.append(nodeType)

            # do the same for its shapes
            if 'transform' in self.selectionInheritedNodeTypes[nodeId]:
                for shapeNodeType in self.selectionShapeNodeTypes[nodeId]:
                    if shapeNodeType not in nodeTypes:
                        nodeTypes.append(shapeNodeType)

        # add names to list widget
        if selectionNames:
            self.selection_listWidget.clear()
            self.selection_listWidget.addItems(selectionNames)

        for nodeType in sorted(nodeTypes):
            self.rule1_comboBox.addItem(nodeType)
            self.rule2_comboBox.addItem(nodeType)

        #if there was a value selected before, set it as current value
        if givenrule1 in nodeTypes:
            index = self.rule1_comboBox.findText(givenrule1)
            self.rule1_comboBox.setCurrentIndex(index)

        if givenrule2 in nodeTypes:
            index = self.rule2_comboBox.findText(givenrule2)
            self.rule2_comboBox.setCurrentIndex(index)


    def processFilter(self):
        returnList = []

        searchText = str(self.search_lineEdit.displayText())
        scopeKeepPrune = str(self.scopeKeepPrune_comboBox.currentText())
        scopeMode = str(self.searchScope_comboBox.currentText())

        rule1KeepPrune = str(self.rule1_comboBoxKeepPrune_comboBox.currentText())
        rule1 = str(self.rule1_comboBox.currentText())
        rule1_considerShapecheckBox = self.rule1_considerShapecheckBox.checkState()

        rule2KeepPrune = str(self.rule2_comboBoxKeepPrune_comboBox.currentText())
        rule2 = str(self.rule2_comboBox.currentText())
        rule2_considerShapecheckBox = self.rule2_considerShapecheckBox.checkState()

        returnList = list(self.selectionIds)
        itemIdList = list(self.selectionIds)

        #filter by search text
        if searchText:

            matches = []
            for nodeId in iter(itemIdList):
                nodeName = self.selectedNodeNames[nodeId]

                if scopeMode == 'Only those with Occurrence':
                    if searchText in nodeName:
                        matches.append(nodeId)

                elif scopeMode == 'Only those Starting with':
                    if nodeName.startswith(searchText):
                        matches.append(nodeId)

                elif scopeMode == 'Only those Ending with':
                    if nodeName.endswith(searchText):
                        matches.append(nodeId)


            for nodeId in iter(itemIdList):
                if nodeId in returnList:
                    if scopeKeepPrune == 'keep':
                        if nodeId not in matches:
                            returnList.remove(nodeId)

                    elif scopeKeepPrune == 'prune':
                        if nodeId in matches:
                            returnList.remove(nodeId)


        rules = (rule1, rule2)
        typeKeepPrune = (rule1KeepPrune, rule2KeepPrune)
        considerShapes = (rule1_considerShapecheckBox, rule1_considerShapecheckBox)

        #Filter by rule1
        #if rule1:

        for i, rule in enumerate(rules):
            if rule:
                matches = []
                for nodeId in iter(returnList):

                    #if each in returnList:
                        #if pymel.nodeType(each) == rule1:
                    if self.selectionNodeTypes[nodeId] == rule:
                        matches.append(nodeId)

                    #if it didnt match, check if any of its shapes matach
                    #elif 'transform' in pymel.nodeType(each, inherited=True):
                    elif considerShapes[i]:
                        if 'transform' in self.selectionInheritedNodeTypes[nodeId]:
                            #for shape in pymel.listRelatives(each, shapes=True):
                            if rule in self.selectionShapeNodeTypes[nodeId]:
                                #if pymel.nodeType(shape) == rule1:
                                matches.append(nodeId)


                for nodeId in iter(itemIdList):
                    if nodeId in returnList:
                        if typeKeepPrune[i] == 'keep':
                            if nodeId not in matches:
                                returnList.remove(nodeId)

                        elif typeKeepPrune[i] == 'prune':
                            if nodeId in matches:
                                returnList.remove(nodeId)


        return returnList



def openUI():
    global ka_filterSelectionUIWindow
    try:
        ka_filterSelectionUIWindow.close()
    except:
        pass

    ka_filterSelectionUIWindow = UI2()
    ka_filterSelectionUIWindow.show()
