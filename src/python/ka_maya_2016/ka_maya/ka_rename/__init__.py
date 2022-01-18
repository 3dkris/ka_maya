import os
import re

import maya.cmds as cmds
import maya.mel as mel
import pymel.core as pymel
import maya.OpenMayaUI as mui

import ka_maya.ka_qtWidgets as ka_qtWidgets
PyQt = ka_qtWidgets.PyQt
QtGui = ka_qtWidgets.QtGui
QtCore = ka_qtWidgets.QtCore

class UI(QtGui.QMainWindow):
    title = 'ka rename tool'

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
        #init our ui using the MayaWindow as parent
        print("work work")

        parent = ka_qtWidgets.getMayaWindow()
        super(UI, self).__init__(parent)

        #uic adds a function to our class called setupUi, calling this creates all the widgets from the .ui file
        self.setObjectName('ka_renameUIWindow2')
        self.setWindowTitle(self.title)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setStyleSheet(self.STYLE_SHEET)

        self.centralWidget = QtGui.QWidget()
        self.setCentralWidget(self.centralWidget)

        self.verticleLayout = QtGui.QVBoxLayout()
        self.centralWidget.setLayout(self.verticleLayout)
        self.verticleLayout.setSpacing(0)

        # Search and replace widgets -------------------------------------------
        self.searchAndReplaceGroupBox = QtGui.QGroupBox(self.centralWidget)
        self.searchAndReplaceGroupBox.setTitle("Search And Replace")
        self.verticleLayout.addWidget(self.searchAndReplaceGroupBox)

        self.searchAndReplaceVLayout = QtGui.QVBoxLayout()
        self.searchAndReplaceGroupBox.setLayout(self.searchAndReplaceVLayout)

        self.searchAndReplaceHLayout = QtGui.QHBoxLayout()
        self.searchAndReplaceVLayout.addLayout(self.searchAndReplaceHLayout)

        self.searchAndReplaceVLayoutA = QtGui.QVBoxLayout()
        self.searchAndReplaceHLayout.addLayout(self.searchAndReplaceVLayoutA)
        self.searchAndReplaceVLayoutA.setSpacing(1)
        self.searchAndReplaceVLayoutB = QtGui.QVBoxLayout()
        self.searchAndReplaceHLayout.addLayout(self.searchAndReplaceVLayoutB)
        self.searchAndReplaceVLayoutB.setSpacing(1)

        # Search For:
        label = QtGui.QLabel()
        label.setText("Search For")
        self.searchAndReplaceVLayoutA.addWidget(label)

        self.searchAndReplace_search_lineEdit = QtGui.QLineEdit()
        self.searchAndReplace_search_lineEdit.setReadOnly(False)
        self.searchAndReplaceVLayoutB.addWidget(self.searchAndReplace_search_lineEdit)

        # Replace With:
        label = QtGui.QLabel()
        label.setText("Replace With:")
        self.searchAndReplaceVLayoutA.addWidget(label)

        self.searchAndReplace_replace_lineEdit = QtGui.QLineEdit()
        self.searchAndReplaceVLayoutB.addWidget(self.searchAndReplace_replace_lineEdit)

        # Case:
        label = QtGui.QLabel()
        label.setText("Case:")
        self.searchAndReplaceVLayoutA.addWidget(label)

        self.searchMode_comboBox = QtGui.QComboBox()
        self.searchMode_comboBox.setFixedWidth(200)
        self.searchAndReplaceVLayoutB.addWidget(self.searchMode_comboBox)
        self.searchMode_comboBox.addItem("case sensitive")
        self.searchMode_comboBox.addItem("ignore case")

        # Scope:
        label = QtGui.QLabel()
        label.setText("Scope:")
        self.searchAndReplaceVLayoutA.addWidget(label)

        self.searchScope_comboBox = QtGui.QComboBox()
        self.searchScope_comboBox.setFixedWidth(200)
        self.searchAndReplaceVLayoutB.addWidget(self.searchScope_comboBox)
        self.searchScope_comboBox.addItem("All Occurrences")
        self.searchScope_comboBox.addItem("ONLY Occurrence")
        self.searchScope_comboBox.addItem("First Occurrence")
        self.searchScope_comboBox.addItem("Last Occurrence")
        self.searchScope_comboBox.addItem("Starts with Occurrence")
        self.searchScope_comboBox.addItem("Ends with Occurrence")

        # Rename Button
        self.searchAndReplace_renameButton = QtGui.QPushButton()
        self.searchAndReplaceVLayout.addWidget(self.searchAndReplace_renameButton)
        self.searchAndReplace_renameButton.setText("RENAME")
        spacer = self.verticleLayout.addSpacing(10)

        # Prefix / Suffix Widgets ----------------------------------------------
        self.prefixSuffixGroupBox = QtGui.QGroupBox(self.centralWidget)
        self.prefixSuffixGroupBox.setTitle("Prefix / Suffix")
        self.verticleLayout.addWidget(self.prefixSuffixGroupBox)

        self.prefixSuffixVLayout = QtGui.QVBoxLayout()
        self.prefixSuffixGroupBox.setLayout(self.prefixSuffixVLayout)

        self.prefixSuffixHLayout = QtGui.QHBoxLayout()
        self.prefixSuffixVLayout.addLayout(self.prefixSuffixHLayout)

        self.prefixSuffixVLayoutA = QtGui.QVBoxLayout()
        self.prefixSuffixHLayout.addLayout(self.prefixSuffixVLayoutA)
        self.prefixSuffixVLayoutA.setSpacing(1)
        self.prefixSuffixVLayoutB = QtGui.QVBoxLayout()
        self.prefixSuffixHLayout.addLayout(self.prefixSuffixVLayoutB)
        self.prefixSuffixVLayoutA.setSpacing(1)

        # Add Prefix:
        label = QtGui.QLabel()
        label.setText("Add Prefix:")
        self.prefixSuffixVLayoutA.addWidget(label)

        self.prefix_lineEdit = QtGui.QLineEdit()
        self.prefixSuffixVLayoutB.addWidget(self.prefix_lineEdit)

        # Add Suffix:
        label = QtGui.QLabel()
        label.setText("Add Suffix:")
        self.prefixSuffixVLayoutA.addWidget(label)

        self.suffix_lineEdit = QtGui.QLineEdit()
        self.prefixSuffixVLayoutB.addWidget(self.suffix_lineEdit)

        # Rename Button
        self.prefixSuffix_renameButton = QtGui.QPushButton()
        self.prefixSuffixVLayout.addWidget(self.prefixSuffix_renameButton)
        self.prefixSuffix_renameButton.setText("RENAME")
        spacer = self.verticleLayout.addSpacing(10)

        # Rename And Or Number ----------------------------------------------
        self.renameAndOrNumberGroupBox = QtGui.QGroupBox(self.centralWidget)
        self.renameAndOrNumberGroupBox.setTitle("Rename And / Or Renumber")
        self.verticleLayout.addWidget(self.renameAndOrNumberGroupBox)

        self.renameAndOrNumberVLayout = QtGui.QVBoxLayout()
        self.renameAndOrNumberGroupBox.setLayout(self.renameAndOrNumberVLayout)

        self.renameAndOrNumberHLayout = QtGui.QHBoxLayout()
        self.renameAndOrNumberVLayout.addLayout(self.renameAndOrNumberHLayout)

        self.renameAndOrNumberVLayoutA = QtGui.QVBoxLayout()
        self.renameAndOrNumberHLayout.addLayout(self.renameAndOrNumberVLayoutA)
        self.renameAndOrNumberVLayoutA.setSpacing(1)
        self.renameAndOrNumberVLayoutB = QtGui.QVBoxLayout()
        self.renameAndOrNumberHLayout.addLayout(self.renameAndOrNumberVLayoutB)
        self.renameAndOrNumberVLayoutB.setSpacing(1)

        # Rename:
        label = QtGui.QLabel()
        label.setText("Rename:")
        self.renameAndOrNumberVLayoutA.addWidget(label)

        self.nameAndNumber_lineEdit = QtGui.QLineEdit()
        self.renameAndOrNumberVLayoutB.addWidget(self.nameAndNumber_lineEdit)

        # Number Placement:
        label = QtGui.QLabel()
        label.setText("Number Placement:")
        self.renameAndOrNumberVLayoutA.addWidget(label)

        self.numberBy_comboBox = QtGui.QComboBox()
        self.numberBy_comboBox.setFixedWidth(200)
        self.renameAndOrNumberVLayoutB.addWidget(self.numberBy_comboBox)
        self.numberBy_comboBox.addItem("Replacing #")
        self.numberBy_comboBox.addItem("Ending")
        self.numberBy_comboBox.addItem("Beginning")

        # Number Type:
        label = QtGui.QLabel()
        label.setText("Number Type:")
        self.renameAndOrNumberVLayoutA.addWidget(label)

        self.numberWith_comboBox = QtGui.QComboBox()
        self.numberWith_comboBox.setFixedWidth(200)
        self.renameAndOrNumberVLayoutB.addWidget(self.numberWith_comboBox)
        self.numberWith_comboBox.addItem("Letters (UPPERCASE)")
        self.numberWith_comboBox.addItem("Letters (lowercase)")
        self.numberWith_comboBox.addItem("Numbers (start at 0)")
        self.numberWith_comboBox.addItem("Numbers (start at 1)")

        # Padding:
        label = QtGui.QLabel()
        label.setText("Number Padding:")
        self.renameAndOrNumberVLayoutA.addWidget(label)

        self.padding_spinBox = QtGui.QSpinBox()
        self.padding_spinBox.setMinimum(0)
        self.padding_spinBox.setFixedWidth(50)
        self.renameAndOrNumberVLayoutB.addWidget(self.padding_spinBox)

        # Rename Button
        self.nameAndNumber_renameButton = QtGui.QPushButton()
        self.renameAndOrNumberVLayout.addWidget(self.nameAndNumber_renameButton)
        self.nameAndNumber_renameButton.setText("RENAME")
        spacer = self.verticleLayout.addSpacing(10)

        # Preview Widgets ------------------------------------------------------
        self.previewHLayout = QtGui.QHBoxLayout()
        self.verticleLayout.addLayout(self.previewHLayout)
        self.previewHLayout.setSpacing(0)
        self.previewHLayout.setContentsMargins(0,0,0,0)

        # Selection:
        self.selectionPreviewGroupBox = QtGui.QGroupBox()
        self.selectionPreviewGroupBox.setTitle("Selection:")
        self.previewHLayout.addWidget(self.selectionPreviewGroupBox)

        self.selectionPreviewLayout = QtGui.QVBoxLayout()
        self.selectionPreviewGroupBox.setLayout(self.selectionPreviewLayout)
        self.selectionPreviewLayout.setSpacing(0)
        self.selectionPreviewLayout.setContentsMargins(0,0,0,0)

        self.nameAndNumber_selection_listWidget = QtGui.QListWidget()
        self.selectionPreviewLayout.addWidget(self.nameAndNumber_selection_listWidget)

        # Preview Results
        self.resultsPreviewGroupBox = QtGui.QGroupBox()
        self.resultsPreviewGroupBox .setTitle("Preview Results:")
        self.previewHLayout.addWidget(self.resultsPreviewGroupBox )

        self.resultsPreviewLayout = QtGui.QVBoxLayout()
        self.resultsPreviewGroupBox.setLayout(self.resultsPreviewLayout)

        self.nameAndNumber_previewResults_listWidget = QtGui.QListWidget()
        self.resultsPreviewLayout.addWidget(self.nameAndNumber_previewResults_listWidget)
        self.resultsPreviewLayout.setSpacing(0)
        self.resultsPreviewLayout.setContentsMargins(0,0,0,0)

        # Connect Signals ------------------------------------------------------
        # rename buttons
        self.connect(self.searchAndReplace_renameButton, QtCore.SIGNAL('clicked()'), self.rename_searchAndReplace)
        self.connect(self.prefixSuffix_renameButton, QtCore.SIGNAL('clicked()'), self.rename_prefixSuffix)
        self.connect(self.nameAndNumber_renameButton, QtCore.SIGNAL('clicked()'), self.rename_nameAndNumber)

        # Name and Number
        self.connect(self.nameAndNumber_lineEdit, QtCore.SIGNAL('textChanged(const QString&)'), self.update)
        self.connect(self.padding_spinBox, QtCore.SIGNAL('valueChanged(int)'), self.update)
        self.connect(self.numberWith_comboBox, QtCore.SIGNAL('currentIndexChanged (int)'), self.update)
        self.connect(self.numberBy_comboBox, QtCore.SIGNAL('currentIndexChanged (int)'), self.update)

        # search and replace
        self.connect(self.searchAndReplace_search_lineEdit, QtCore.SIGNAL('returnPressed()'), self.rename_searchAndReplace)
        self.connect(self.searchAndReplace_replace_lineEdit, QtCore.SIGNAL('returnPressed()'), self.rename_searchAndReplace)
        self.connect(self.prefix_lineEdit, QtCore.SIGNAL('returnPressed()'), self.rename_prefixSuffix)
        self.connect(self.suffix_lineEdit, QtCore.SIGNAL('returnPressed()'), self.rename_prefixSuffix)
        self.connect(self.nameAndNumber_lineEdit, QtCore.SIGNAL('returnPressed()'), self.rename_nameAndNumber)

        self.connect(self.searchAndReplace_search_lineEdit, QtCore.SIGNAL('textChanged(const QString&)'), self.update)
        self.connect(self.searchAndReplace_replace_lineEdit, QtCore.SIGNAL('textChanged(const QString&)'), self.update)
        self.connect(self.prefix_lineEdit, QtCore.SIGNAL('textChanged(const QString&)'), self.update)
        self.connect(self.suffix_lineEdit, QtCore.SIGNAL('textChanged(const QString&)'), self.update)

        self.connect(self.searchMode_comboBox, QtCore.SIGNAL('currentIndexChanged (int)'), self.update)
        self.connect(self.searchScope_comboBox, QtCore.SIGNAL('currentIndexChanged (int)'), self.update)

        self.searchAndReplace_search_lineEdit.setTabOrder(self.searchAndReplace_search_lineEdit, self.searchAndReplace_replace_lineEdit)
        self.searchAndReplace_search_lineEdit.setTabOrder(self.searchAndReplace_replace_lineEdit, self.prefix_lineEdit)
        self.searchAndReplace_search_lineEdit.setTabOrder(self.prefix_lineEdit, self.suffix_lineEdit)
        self.searchAndReplace_search_lineEdit.setTabOrder(self.suffix_lineEdit, self.nameAndNumber_lineEdit)

        self.update()
        self.nameAndNumber_lineEdit.setFocus()

    def update(self):
        self.loadSelection_rename()
        self.loadPreviewResults_rename()

    ################################################################################
    #
    #    01: RENAME
    #
    ################################################################################

    def loadSelection_rename(self):
        selection = pymel.ls(selection=True)
        selectionNames = []
        for each in selection:
            if hasattr(each, 'nodeName'):
                selectionNames.append(each.nodeName())

        self.nameAndNumber_selection_listWidget.clear()
        if selectionNames:
            self.nameAndNumber_selection_listWidget.addItems(selectionNames)
        else:
            self.nameAndNumber_selection_listWidget.addItem("<Nothing Selected>")

    def loadPreviewResults_rename(self):
        selection = pymel.ls(selection=True)
        previewList = []
        nameList = []
        for each in selection:
            if hasattr(each, 'nodeName'):
                nameList.append(each.nodeName())

        self.nameAndNumber_previewResults_listWidget.clear()
        if nameList:
            if self.searchAndReplace_search_lineEdit.hasFocus(): previewList = self.figureOut_searchAndReplace(nameList)
            elif self.searchAndReplace_replace_lineEdit.hasFocus(): previewList = self.figureOut_searchAndReplace(nameList)
            elif self.searchMode_comboBox.hasFocus(): previewList = self.figureOut_searchAndReplace(nameList)
            elif self.searchScope_comboBox.hasFocus(): previewList = self.figureOut_searchAndReplace(nameList)

            elif self.prefix_lineEdit.hasFocus(): previewList = self.figureOut_prefixSuffix(nameList)
            elif self.suffix_lineEdit.hasFocus(): previewList = self.figureOut_prefixSuffix(nameList)

            elif self.nameAndNumber_lineEdit.hasFocus(): previewList = self.figureOut_nameAndNumber(nameList)
            elif self.numberBy_comboBox.hasFocus(): previewList = self.figureOut_nameAndNumber(nameList)
            elif self.numberWith_comboBox.hasFocus(): previewList = self.figureOut_nameAndNumber(nameList)
            elif self.padding_spinBox.hasFocus(): previewList = self.figureOut_nameAndNumber(nameList)


            else:
                previewList = self.figureOut_rename(nameList)

            self.nameAndNumber_previewResults_listWidget.addItems(previewList)
        else:
            self.nameAndNumber_previewResults_listWidget.addItem("<Nothing Selected>")

    def figureOut_rename(self, list):
        returnList = []
#        nameList = []
        for each in list:
#            nameList.append(each.nodeName())
            returnList.append(each)
#

        searchText = str(self.searchAndReplace_search_lineEdit.displayText())
        if searchText:
            returnList = self.figureOut_searchAndReplace(returnList)

        prefixText = str(self.prefix_lineEdit.displayText())
        suffix_Text = str(self.suffix_lineEdit.displayText())
        if prefixText or suffix_Text:
            returnList = self.figureOut_prefixSuffix(returnList,)

#        if suffix_Text:
#            print 'suf'
#            returnList = self.figureOut_prefixSuffix(returnList, mode='suffix')

        renameText = str(self.nameAndNumber_lineEdit.displayText())
        if renameText:
            returnList = self.figureOut_nameAndNumber(returnList)

        return returnList

    def figureOut_nameAndNumber(self, list):
        renameText = str(self.nameAndNumber_lineEdit.displayText())
        numberBy = self.numberBy_comboBox.currentText()
        numberWith = self.numberWith_comboBox.currentText()
        bufferLength = (self.padding_spinBox.value() + 1)
        newList = []

        for count, each in enumerate(list):

            #figure out the count string i with buffer if nessisary
            i = str(count)
            if len(i) <= bufferLength:
                diff = bufferLength - len(i)
                for each in range(diff):
                    i = '0'+i

            if numberWith == 'Numbers (start at 1)':
                i = str(count + 1)
                if len(i) <= bufferLength:
                    diff = bufferLength - len(i)
                    for each in range(diff):
                        i = '0'+i

            if numberWith == 'Letters (lowercase)':
                lowerAlphabit = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', ]
                i = lowerAlphabit[count]

                if len(i) <= bufferLength:
                    diff = bufferLength - len(i)
                    for each in range(diff):
                        i = 'a'+i
            if numberWith == 'Letters (UPPERCASE)':
                upperAlphabit = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', ]
                i = upperAlphabit[count]

                if len(i) <= bufferLength:
                    diff = bufferLength - len(i)
                    for each in range(diff):
                        i = 'A'+i


            #figure out where to put the numbers

            if numberBy == 'Replacing #':
                numberSignGroups = re.findall('#+', renameText)
                if numberSignGroups:
                    buffer = len(numberSignGroups[0])

                    if len(numberSignGroups) >= 2:
                        newList.append('<too many groups of "#"!>')
                    else:
                        newList.append(re.sub(r'#+', i, renameText))
                else:
                    newList.append(renameText)

            if numberBy == 'Ending':
                newList.append(renameText+i)
            if numberBy == 'Beginning':
                newList.append(i+renameText)

        newList = self.cleanUpList(newList)
        return newList

    def figureOut_prefixSuffix(self, list):
        prefixText = str(self.prefix_lineEdit.displayText())
        suffix_Text = str(self.suffix_lineEdit.displayText())
        newList = []

        for count, each in enumerate(list):

            if prefixText:
                each = prefixText+each


            if suffix_Text:
                each = each+suffix_Text

            newList.append(each)

        newList = self.cleanUpList(newList)
        return newList

    def figureOut_searchAndReplace(self, list):
        searchText = str(self.searchAndReplace_search_lineEdit.displayText())
        replaceText = str(self.searchAndReplace_replace_lineEdit.displayText())
        numberMode = self.searchMode_comboBox.currentText()
        numberScope = self.searchScope_comboBox.currentText()
        newList = []


        if searchText:
            for count, each in enumerate(list):

                #determine scope
                if numberMode == 'ignore case':
                    searchText = '(?i)'+searchText
                searchResults = re.findall(searchText, each)


                if numberScope == 'All Occurrences':
                    newList.append(re.sub(searchText, replaceText, each))

                elif numberScope == 'ONLY Occurrence':
                    if len(searchResults) == 1:
                        newList.append(re.sub(searchText, replaceText, each))
                    else:
                        newList.append('<more than 1 match!>')

                elif numberScope == 'First Occurrence':
                    nameSplit = re.split(searchText, each, 1)                       #search for 1 occurance of the search term
                    if len(nameSplit) > 1:                                          #if occurance is found...
                        newList.append(nameSplit[0]+replaceText+nameSplit[1])       #return string with it substituted
                    else:                                                           #else if no occurance found...
                        newList.append(each)                                        #return original name unchanged

                elif numberScope == 'Last Occurrence':
                    nameSplit = re.split(searchText[::-1], each[::-1], 1)           #do a spit of the reversed string, with a reversed search string
                    if len(nameSplit) > 1:                                          #if an occurance is found...
                        newlistItem = nameSplit[0]+replaceText[::-1]+nameSplit[1]   #build reverse string
                        newList.append(newlistItem[::-1])                           #return an unreversed string
                    else:                                                           #else if not occurance...
                        newList.append(each)                                        #return original name unchanged


                elif numberScope == 'Starts with Occurrence':
                    lenOfSearchText = len(searchText)
                    if each[:lenOfSearchText] == searchText:
                        nameSplit = re.split(searchText, each, 1)                       #search for 1 occurance of the search term
                        if len(nameSplit) > 1:                                          #if occurance is found...
                            newList.append(nameSplit[0]+replaceText+nameSplit[1])       #return string with it substituted
                        else:                                                           #else if no occurance found...
                            newList.append(each)
                    else:
                        newList.append(each)

                elif numberScope == 'Ends with Occurrence':
                    lenOfSearchText = len(searchText)
                    if each[(-1*lenOfSearchText):] == searchText:
                        nameSplit = re.split(searchText[::-1], each[::-1], 1)           #do a spit of the reversed string, with a reversed search string
                        if len(nameSplit) > 1:                                          #if an occurance is found...
                            newlistItem = nameSplit[0]+replaceText[::-1]+nameSplit[1]   #build reverse string
                            newList.append(newlistItem[::-1])                           #return an unreversed string
                        else:                                                           #else if not occurance...
                            newList.append(each)
                    else:
                        newList.append(each)

        newList = self.cleanUpList(newList)
        return newList


    def cleanUpList(self, list):
        newList = []
        for i, each in enumerate(list):

            each = re.sub(r' ', '_', each)
            each = re.sub(r'\!', '_', each)
            each = re.sub(r'\$', '_', each)
            each = re.sub(r'\|', '_', each)
            each = re.sub(r'\#', '', each)

            newList.append(each)

        return newList

    def rename_nameAndNumber(self):
        self._rename_(mode='nameAndNumber')

    def rename_prefixSuffix(self):
        self._rename_(mode='prefixSuffix')

    def rename_searchAndReplace(self):
        self._rename_(mode='searchAndReplace')


    def _rename_(self, mode=''):
        selection = pymel.ls(selection=True)
        nameList = []
        for each in selection:
            nameList.append(each.nodeName())

        if mode == 'searchAndReplace':
            renameList = self.figureOut_searchAndReplace(nameList)
        if mode == 'prefixSuffix':
            renameList = self.figureOut_prefixSuffix(nameList)
        if mode == 'nameAndNumber':
            renameList = self.figureOut_nameAndNumber(nameList)


#        renameList = self.figureOut_rename(selection)


        for i, each in enumerate(selection):
            pymel.rename( selection[i], renameList[i] )

        self.update()

        mods = cmds.getModifiers()
        if (mods & 4) > 0:    #Ctrl
            self.close()

def openUI():
    global ka_renameUIWindow
    try:
        ka_renameUIWindow.close()
    except:
        pass

    print("openUI")
    ka_renameUIWindow = UI()
    ka_renameUIWindow.show()

