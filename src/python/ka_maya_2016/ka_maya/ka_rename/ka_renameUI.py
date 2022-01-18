import os
import sip


import maya.cmds as cmds
import maya.mel as mel
import pymel.core as pymel
import maya.OpenMayaUI as mui

from PyQt4 import QtGui, QtCore, uic

import re


def getMayaWindow():
    'Get the maya main window as a QMainWindow instance'
    ptr = mui.MQtUtil.mainWindow()
    return sip.wrapinstance(long(ptr), QtCore.QObject)

#Get the absolute path to my ui file
#uiFile = os.path.join(cmds.internalVar(upd=True), 'ui', 'demo.ui')
uiFile= os.path.dirname(__file__)+'/ka_renameUI.ui'
print 'Loading ui file:', os.path.normpath(uiFile)

#Load the ui file, and create my class
form_class, base_class = uic.loadUiType(uiFile)
print 'form_class is :', form_class
print 'base_class is :', base_class

class UI(base_class, form_class):
    title = 'ka rename tool'


    def __init__(self, parent=getMayaWindow()):
        '''A custom window with a demo set of ui widgets'''
        #init our ui using the MayaWindow as parent
        super(base_class, self).__init__(parent)
        #uic adds a function to our class called setupUi, calling this creates all the widgets from the .ui file
        self.setupUi(self)
        self.setObjectName('ka_renameUIWindow')
        self.setWindowTitle(self.title)

        print 'form_class is :', form_class
        print 'base_class is :', base_class


        self.connect(self.searchAndReplace_renameButton, QtCore.SIGNAL('clicked()'), self.rename_searchAndReplace)
        self.connect(self.prefixSuffix_renameButton, QtCore.SIGNAL('clicked()'), self.rename_prefixSuffix)
        self.connect(self.nameAndNumber_renameButton, QtCore.SIGNAL('clicked()'), self.rename_nameAndNumber)
        self.connect(self.renameMode_tabWidget, QtCore.SIGNAL('currentChanged(int)'), self.update)

        #name and number
        self.connect(self.nameAndNumber_lineEdit, QtCore.SIGNAL('textChanged(const QString&)'), self.update)
        self.connect(self.buffer_spinBox, QtCore.SIGNAL('valueChanged(int)'), self.update)
        self.connect(self.numberWith_comboBox, QtCore.SIGNAL('currentIndexChanged (int)'), self.update)
        self.connect(self.numberBy_comboBox, QtCore.SIGNAL('currentIndexChanged (int)'), self.update)

#        self.connect(self.reload_pushButton, QtCore.SIGNAL('clicked()'), self.update)

        #search and replace
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

#        self.connect(self.searchAndReplace_reload_pushButton, QtCore.SIGNAL('clicked()'), self.update)

        self.searchAndReplace_search_lineEdit.setTabOrder(self.searchAndReplace_search_lineEdit, self.searchAndReplace_replace_lineEdit)
        self.searchAndReplace_search_lineEdit.setTabOrder(self.searchAndReplace_replace_lineEdit, self.prefix_lineEdit)
        self.searchAndReplace_search_lineEdit.setTabOrder(self.prefix_lineEdit, self.suffix_lineEdit)
        self.searchAndReplace_search_lineEdit.setTabOrder(self.suffix_lineEdit, self.nameAndNumber_lineEdit)

#
        self.update()
        self.nameAndNumber_lineEdit.setFocus()

        print 'nope'
        ##script job
        #scriptJobDummyWindow = 'ka_renameUI_scriptJobWindow'
        #if cmds.window(scriptJobDummyWindow, exists=True):cmds.deleteUI(scriptJobDummyWindow)
        #cmds.window(scriptJobDummyWindow)

        #def selectionChanged():
            #'''run if maya selection is changed, destroys self if called while window is not visisble'''
            #if self.isVisible():
                #self.update()
##
            #else:    #self destruct
                #cmds.deleteUI(scriptJobDummyWindow)

        #jobId = cmds.scriptJob(event=['SelectionChanged', selectionChanged], parent=scriptJobDummyWindow)

    def update(self):
        modeIndex = self.renameMode_tabWidget.currentIndex()
        mode = self.renameMode_tabWidget.tabText(modeIndex)

        if mode == 'Rename':
            self.loadSelection_rename()
            self.loadPreviewResults_rename()

        if mode == 'Search and Replace':
            self.loadSelection_searchAndReplace()
            self.loadPreviewResults_searchAndReplace()


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

        if selectionNames:
            self.nameAndNumber_selection_listWidget.clear()
            self.nameAndNumber_selection_listWidget.addItems(selectionNames)

    def loadPreviewResults_rename(self):
        selection = pymel.ls(selection=True)
        previewList = []
        nameList = []
        for each in selection:
            if hasattr(each, 'nodeName'):
                nameList.append(each.nodeName())

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
            elif self.buffer_spinBox.hasFocus(): previewList = self.figureOut_nameAndNumber(nameList)


            else:
                previewList = self.figureOut_rename(nameList)

            self.nameAndNumber_previewResults_listWidget.clear()
            self.nameAndNumber_previewResults_listWidget.addItems(previewList)

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
        bufferLength = (self.buffer_spinBox.value() + 1)
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

return UI


def open():
    global ka_renameUIWindow
    try:
        ka_renameUIWindow.close()
    except:
        pass

    #winname = MayaCmds.window('testWin')
    #ptr = long(long(OpenMayaUI.MQtUtil.findWindow(winname)))
    #dlg = sip.wrapinstance(ptr, QtGui.QDialog)

    ka_renameUIWindow = UI()
    #cmds.scriptJob(parent=myWindow, killWithScene=True, ct= ["SomethingSelected","print moo"],)
    ka_renameUIWindow.show()
    print "OPEN"
    print "OPEN"
    print "OPEN"
    print "OPEN"
    print "OPEN"

open()