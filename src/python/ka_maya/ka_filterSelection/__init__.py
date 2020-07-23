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

import re


uiFile= os.path.dirname(__file__)+'/ka_filterSelectionUI.ui'
form_class, base_class = ka_qtWidgets.loadUiType(uiFile)

scriptJobDummyWindow = 'ka_filterSelection_scriptJobWindow'

class UI(base_class, form_class):
    title = 'ka selection filter tool'



    def __init__(self, parent=ka_qtWidgets.getMayaWindow()):
        '''A custom window with a demo set of ui widgets'''
        #init our ui using the MayaWindow as parent
        super(UI, self).__init__(parent)
        #uic adds a function to our class called setupUi, calling this creates all the widgets from the .ui file
        self.setupUi(self)
        self.setObjectName('ka_renameUIWindow')
        self.setWindowTitle(self.title)



        ##name and number
        #self.connect(self.search_lineEdit, QtCore.SIGNAL('returnPressed(const QString&)'), self.update)
        self.connect(self.search_lineEdit, QtCore.SIGNAL('textChanged(const QString&)'), self.loadPreviewResults)
        #self.connect(self.search_lineEdit, QtCore.SIGNAL('returnPressed(const QString&)'), self.loadPreviewResults)
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

        self.selection = {}
        self.selectionNodeTypes = {}
        self.selectionInheritedNodeTypes = {}
        self.selectionShapeNodeTypes = {}
        self.selectedNodeNames = {}

        self.update()
        self.search_lineEdit.setFocus()

        ##script job
        #if cmds.window(scriptJobDummyWindow, exists=True):
            #cmds.deleteUI(scriptJobDummyWindow)
        #cmds.window(scriptJobDummyWindow)

        #def selectionChanged():
            #'''run if maya selection is changed, destroys self if called while window is not visisble'''
            ##import maya.cmds as cmds

            #if self.isVisible():
                #self.update()

            #else:    #self destruct
                #cmds.deleteUI(scriptJobDummyWindow)

        #jobId = cmds.scriptJob(event=['SelectionChanged', selectionChanged], parent=scriptJobDummyWindow)

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
    global ka_renameUIWindow
    try:
        ka_renameUIWindow.close()
    except:
        pass

    ka_renameUIWindow = UI()
    ka_renameUIWindow.show()
