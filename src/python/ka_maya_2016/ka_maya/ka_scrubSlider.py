#====================================================================================
#====================================================================================
#
# ka_scrubUtils
#
# DESCRIPTION:
#   a series of fuctions triggered by dragging the mouse
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
import time

import maya.cmds as cmds
import pymel.core as pymel
import maya.mel as mel
import maya.OpenMayaUI as OpenMayaUI

import ka_maya.ka_qtWidgets as ka_qtWidgets
PyQt = ka_qtWidgets.PyQt
QtGui = ka_qtWidgets.QtGui
QtCore = ka_qtWidgets.QtCore

import ka_maya.ka_python as ka_python   #;reload(ka_weightPainting)
import ka_maya.ka_math as ka_math   #;reload(ka_weightPainting)
import ka_maya.ka_weightPainting as ka_weightPainting   #;reload(ka_weightPainting)
import ka_maya.ka_preference as ka_preference        #;reload(ka_preference)
import ka_maya.ka_weightBlender as ka_weightBlender         #;reload(ka_weightBlender)


#class ScrubSlider(QtGui.QSlider):

    #def __init__(self, sliderRange=[0, 100], defaultValue=0, width=500, step=1.0, shiftStep=25, mode='toggle',
                    #startCommand=None, changeCommand=None, finishCommand=None, hotkeyDict={}, rightClickCommand=None):
        #"""
        #constructor of scrubSlider.

        #Kwargs:
            #sliderRange (start int, end int): The slider range

            #defaultValue (int): the value to start the slider at

            #width (int in pixels): the width of the slider (this also effects the sensitivity of it indirectly)

            #step (int): not yet impimented

            #mode (string): acceptable values are "clickDrag", and "toggle".

            #startCommand (function): a passed in function to run at the start of the scrub

            #changeCommand (function): a passed in function to run when the slider changes. The current Value of the slider will be
                                        #the first argument passed to the function

            #finishCommand (function): a passed in function to run at the end of the scrub (right before the mouse is released
                                        #back to the user)

            #hotkeyDict (dictionary of string(key) function(value) pairs): This dictionary gives the slider functions to assign to
                                                                            #keypresses that will override maya hotkeys while the slider
                                                                            #is in use.

        #"""
        #self.mayaWindow = ka_qtWidgets.getMayaWindow()
        #super(ScrubSlider, self).__init__(self.mayaWindow)


        #self.mode = mode
        #cursorPos = QtGui.QCursor().pos()
        #cursorPos = self.mayaWindow.mapFromGlobal(cursorPos)
        #self.extraWidgets = []
        #self.finished = False

        ## slider setup math
        #self.defaultValue = float(defaultValue)
        #self.previousValue = float(defaultValue)
        #self.mouseInitialPositionX = cursorPos.x()
        #self.mouseGrabOffset = 0.0
        #self.step = step
        #self.shiftStep = shiftStep

        #self.sliderMax = float(sliderRange[1])
        #self.sliderMin = float(sliderRange[0])
        #self.sliderRange = float(self.sliderMax - self.sliderMin)

        #defaultPercentOfSliderRange = (float(defaultValue) - self.sliderMin) / float(self.sliderRange)

        #self.pixelMin = self.mouseInitialPositionX - (width * defaultPercentOfSliderRange)
        #self.pixelMax = self.pixelMin + width
        #self.pixelRange = self.pixelMax - self.pixelMin


        ## QSlider
        #sliderOffset = 105
        #self.move(self.pixelMin, cursorPos.y()+sliderOffset)
        #self.setOrientation(QtCore.Qt.Horizontal)
        #self.setSingleStep(1)
        #self.setFixedSize(width, 4)
        #self.setValue(defaultValue)
        #self.setMaximum(self.sliderMax)
        #self.setMinimum(self.sliderMin)

        ## value spin box
        #valueBoxWidth = 40
        #self.sliderValueBox = QtGui.QSpinBox(self.mayaWindow)
        #self.sliderValueBox.move(((self.pixelMin+((self.pixelMax-self.pixelMin)*0.5) - (valueBoxWidth*0.5))),
                                    #cursorPos.y()+sliderOffset+6)
        #self.sliderValueBox.setFixedSize(valueBoxWidth, 15)
        ##self.sliderValueBox.setButtonSymbols(2)
        #self.sliderValueBox.setButtonSymbols(QtGui.QAbstractSpinBox.NoButtons)


        #self.sliderValueBox.setRange(self.sliderMin, self.sliderMax)
        #self.extraWidgets.append(self.sliderValueBox)


        ## passed commandeds
        #self.startCommand = startCommand
        #self.changeCommand = changeCommand
        #self.finishCommand = finishCommand

        #if mode == "clickDrag":
            #self.startScrub = False

        #if mode == "toggle":
            #self.startScrub = True

        #self.connect(self, QtCore.SIGNAL('sliderReleased()'), self.finish)

        #self.hotkeyDict = hotkeyDict
        #self.lastPressedKeyID = None

    #def mousePressEvent(self, event):
        #print event.button()

        #if event == QtCore.Qt.LeftButton:
            #self.finish()
            #event.accept()

        #elif event == QtCore.Qt.RightButton:
            #self.finish()
            #event.accept()

        #QtGui.QSlider.mousePressEvent(self, event)


    #def mouseMoveEvent(self, mouseEvent):
        #mouseX = self.mayaWindow.mapFromGlobal(mouseEvent.globalPos()).x()
        #scrubValue = int(round(self.getScrubValue(mouseX)))
        #if (scrubValue - self.previousValue):
            #self.scubValueChanged(scrubValue)
        #mouseEvent.accept()

    #def keyPressEvent(self, keyEvent):
        ##keyID = keyEvent.key()
        #keyID = keyEvent.text()
        #if keyID in self.hotkeyDict:
            #subDict = self.hotkeyDict[keyID]
            #if subDict['press']:

                #modifiers = int(keyEvent.modifiers())
                #modifierDown = True
                #if subDict['shift'] and modifiers not in [33554432, 100663296, 369098752, 301989888]:
                    #modifierDown = False
                    #print 'not shift'

                #if subDict['alt'] and modifiers not in [134217728, 201326592, 167772160, 234881024]:
                    #modifierDown = False
                    #print 'not alt'

                #if subDict['ctrl'] and modifiers not in [67108864, 100663296, 201326592, 234881024]:
                    #modifierDown = False
                    #print 'not ctrl'

                #if modifierDown:
                    #if subDict['hold']:
                        #if not keyEvent.isAutoRepeat():
                            #subDict['command']()
                            #keyEvent.accept()

                    #else:
                        #subDict['command']()
                        #keyEvent.accept()
                        #return None

        #QtGui.QSlider.keyPressEvent(self, keyEvent)


    #def keyReleaseEvent(self, keyEvent):

        #if not keyEvent.isAutoRepeat():
            #keyID = keyEvent.key()
            #if keyID in self.hotkeyDict:
                #subDict = self.hotkeyDict[keyID]
                #if subDict['release']:
                    #subDict['command']()
                    #keyEvent.accept()

        #QtGui.QSlider.keyReleaseEvent(self, keyEvent)


    #def getScrubValue(self, mouseX):

        #if mouseX <= self.pixelMin:
            #return self.sliderMin

        #elif mouseX >= self.pixelMax:
            #return self.sliderMax

        #else:
            #relativeX = float(mouseX-self.pixelMin)
            #percent = relativeX / float(self.pixelRange)
            #return self.sliderMin + (self.sliderRange * percent)


    #def getSteppedValue(self, x, base=1):
        #return int(base * round(float(x)/base))


    ## VALUE CHANGED ---------------------------------------------------------------
    #def scubValueChanged(self, value):
        #try:
            #self._scubValueChanged(value)
        #except:
            #ka_python.printError()
            #self.finish()

    #def _scubValueChanged(self, value):
        #self.previousValue = value

        ## check if modifier should change step value
        #modifiers = QtGui.QApplication.keyboardModifiers()
        #if modifiers == QtCore.Qt.ShiftModifier:
            #value = self.getSteppedValue(value, self.shiftStep)

        #self.setValue(value)
        #self.setFocus(QtCore.Qt.MouseFocusReason)

        #if self.sliderValueBox.isVisible:
            #self.sliderValueBox.setValue(value)

        #if self.changeCommand:
            #self.changeCommand(value)

    ## VALUE START ---------------------------------------------------------------
    #def start(self):
        #try:
            #self._start()
        #except:
            #ka_python.printError()
            #self.finish()

    #def _start(self):

        #sliderVis = ka_preference.get('scrubSlider_sliderVisable', True)
        #sliderValueVis = ka_preference.get('scrubSlider_sliderValueVisable', True)
        #if self.startCommand:
            #self.startCommand()

        #self.setTracking(True)
        #self.setMouseTracking(True)
        ##self.setFocus(QtCore.Qt.MouseFocusReason)
        #self.show()
        #self.grabMouse()
        #self.grabKeyboard()
        #self.setSliderDown(True)

        ##if not sliderVis:
            ##self.hide()

        #if sliderValueVis:
            #self.sliderValueBox.show()

        ##self.setFocus(QtCore.Qt.MouseFocusReason)

    ## VALUE FINISH ---------------------------------------------------------------
    #def finish(self):
        #if not self.finished: # only finish once
            #print 'finish'

            #if self.finishCommand:
                #self.finishCommand()

            #self.releaseMouse()
            #self.releaseKeyboard()

            #for extraWidget in self.extraWidgets:
                #extraWidget.deleteLater()

            #self.sliderValueBox.deleteLater()
            #self.deleteLater()

            #self.finished = True




def getScrubSlider():
    mayaWindow = ka_qtWidgets.getMayaWindow()
    for child in mayaWindow.children():
        if hasattr(child, 'objectName'):
            if child.objectName() == 'ka_scrubSlider':
                return child

#scrubSlider = getScrubSlider()
#if scrubSlider:
    #scrubSlider.finish()



#def createScrubSlider(*args, **kwargs):
    #"""Returns scrubSlider. This is the main function to create the scrub slider"""

    ## get mode
    #mode = ka_preference.get('snapToolPrimaryAxis', 0)
    #if mode == 1: mode = 'clickDrag'
    #else:         mode = 'toggle'
    #kwargs['mode'] = mode

    #if mode == 'toggle':
        #scrubSlider = getScrubSlider()
        #if scrubSlider:
            #count = 0
            #while scrubSlider and count < 25:
                #count += 1

                #try:
                    #scrubSlider.finish()
                #except:
                    #ka_python.printError()
                    #if hasattr(scrubSlider, 'extraWidgets'):
                        #for extraWidget in scrubSlider.extraWidgets:
                            #extraWidget.deleteLater()

                        #scrubSlider.deleteLater()

                #scrubSlider = getScrubSlider()

        #else:
            #scrubSlider = ScrubSlider(*args, **kwargs)
            #scrubSlider.setObjectName('ka_scrubSlider')
            #scrubSlider.start()


    #elif mode == 'clickDrag':
        #scrubSlider = ScrubSlider(*args, **kwargs)
        #scrubSlider.setObjectName('ka_scrubSlider')
        #scrubSlider.start()


    #return scrubSlider

def addHotkeyToDict(keyString, command, hotkeyDict, press=True, release=False, hold=False):
    keyString = keyString.upper()
    keyString.replace('ALT', 'Alt')
    keyString.replace('SHIFT', 'Shift')
    keyString.replace('CTRL', 'Ctrl')

    QKeySeq = QtGui.QKeySequence(keyString)

    #keyID = int(QKeySeq)
    keyID = QKeySeq.toString()
    hotkeyDict[keyID] = {}
    subDict = hotkeyDict[keyID]
    subDict['QKeySequence'] = QKeySeq
    subDict['command'] = command
    subDict['press'] = press
    subDict['release'] = release
    subDict['hold'] = hold

    if 'Shift' in keyString:
        subDict['shift'] = True
    else:
        subDict['shift'] = False

    if 'Alt'   in keyString:
        subDict['alt']   = True
    else:
        subDict['alt']   = False

    if 'Ctrl'  in keyString:
        subDict['ctrl']  = True
    else:
        subDict['ctrl']   = False


def timeSliderScrub():
    rangeMin = int(pymel.floatField('MayaWindow|toolBar5|MainPlaybackRangeLayout|formLayout10|floatField3', query=True, value=True))
    rangeMax = int(pymel.floatField('MayaWindow|toolBar5|MainPlaybackRangeLayout|formLayout10|floatField4', query=True, value=True))
    currentTime = pymel.currentTime(query=True)

    def sliderCmd(scrubWidget, values):
        time = values[0]
        cmds.currentTime(time)

    scrubSlider = createScrubSlider(sliderRange=(rangeMin, rangeMax), changeCommand=sliderCmd,
                                    defaultValues=[currentTime,], visible=False)

    return scrubSlider

def weight_parallelBlend_Scrub():
    """Activates weight blender to blend weights from the neighbors of the selected points"""

    # Check if there is a selection
    selection = cmds.ls(selection=True)
    if not selection:
        pymel.warning('Nothing Selected')
        return None

    hotkeyDict = {}

    def startCommand(scrubWidget):
        ka_weightBlender.startParallelBlend()

    def changeCommand(scrubWidget, values):
        modifiers = cmds.getModifiers()
        if (modifiers & 4) > 0:
            ctrlDown = True
        else:
            ctrlDown = False

        ka_weightBlender.change(blendValue=values[0], bothNeighbors=ctrlDown)

    def finishCommand(scrubWidget):
        ka_weightBlender.finish()


    def c_pressed(scrubWidget):
        ka_weightBlender.next()
    addHotkeyToDict('c', c_pressed, hotkeyDict, press=True, release=False, hold=False)

    def b_pressed(scrubWidget):
        ka_weightBlender.previous()
    addHotkeyToDict('b', b_pressed, hotkeyDict, press=True, release=False, hold=False)

    graphKwargs = {}
    graphKwargs['drawCurve'] = True
    graphKwargs['curveType'] = 'Linear'
    graphKwargs['curvePoints'] = ((0.0, 0.0), (100, 1.0), (200, 0.0),)

    scrubSlider = createScrubSlider(sliderRange=[0, 200], startCommand=startCommand, changeCommand=changeCommand,
                                    finishCommand=finishCommand, defaultValues=[100], hotkeyDict=hotkeyDict,
                                    visible=True, graphKwargs=graphKwargs)

    scrubSlider.setFixedSize(400, 35)

    return scrubSlider

def weight_strandBlend_Scrub(visible=True):
    """Activates weight blender to blend weights from the start and the end of the strand"""

    # Check if there is a selection
    selection = cmds.ls(selection=True)
    if not selection:
        pymel.warning('Nothing Selected')
        return None

    hotkeyDict = {}

    def startCommand(scrubWidget):
        t0 = time.clock()
        ka_weightBlender.startStrandBlend()

    def changeCommand(scrubWidget, values):
        curvePoints = list(values)
        curvePoints.sort()

        curvePoints = [(curvePoints[0], 0.0), (curvePoints[1], 0.0), (curvePoints[2], 1.0), (curvePoints[3], 1.0), ]

        scrubWidget.graphWidget.setCurvePoints(curvePoints)

        ka_weightBlender.change(blendValues=values)

    def finishCommand(scrubWidget):
        ka_preference.add('strandBlendDefaultValues', scrubWidget.currentValues)
        ka_weightBlender.finish()


    def c_pressed(scrubWidget):
        scrubWidget.editNextValue()

    addHotkeyToDict('c', c_pressed, hotkeyDict, press=True, release=False, hold=False)

    def b_pressed(scrubWidget):
        scrubWidget.editPreviousValue()

    addHotkeyToDict('b', b_pressed, hotkeyDict, press=True, release=False, hold=False)

    graphKwargs = {}
    graphKwargs['drawCurve'] = True
    graphKwargs['curveType'] = 'Bezier'
    graphKwargs['curvePoints'] = ((0,1), (.5,0), (0,1))

    defaultValues = ka_preference.get('strandBlendDefaultValues', [30, 70, 0, 100])

    scrubSlider = createScrubSlider(sliderRange=[0, 100], startCommand=startCommand, changeCommand=changeCommand,
                                    finishCommand=finishCommand, defaultValues=defaultValues, hotkeyDict=hotkeyDict,
                                    visible=True, shiftStep=20, graphKwargs=graphKwargs)

    scrubSlider.setFixedSize(200, 200)

    return scrubSlider

class ScrubWidgetSignals(QtCore.QObject):
    valueChangedSignal = QtCore.Signal(int)
    finishSignal = QtCore.Signal()

class ScrubWidget(QtGui.QMainWindow):
    """
    A UI that when poped, will map the mouse position to a given command.

    """

    valueChanged = QtCore.Signal(int)

    def __init__(self, sliderRange=[-100, 100], defaultValues=[0], width=500, step=1.0, shiftStep=25,
                 startCommand=None, changeCommand=None, finishCommand=None, hotkeyDict={},
                 rightClickCommand=None, visible=True, graphKwargs={}):
        """
        constructor of scrubSlider.

        Kwargs:
            sliderRange (start int, end int): The slider range

            defaultValues (tuple of ints): the values to start the slider at. The number of default values will
                                           detirmin how many values the slider has. These values also do not need
                                           to be passed in order of value. The first item will be the value being
                                           edited by default

            width (int in pixels): the width of the slider (this also effects the sensitivity of it indirectly)

            step (int): not yet impimented

            mode (string): acceptable values are "clickDrag", and "toggle".

            startCommand (function): a passed in function to run at the start of the scrub

            changeCommand (function): a passed in function to run when the slider changes. The current Value of the slider will be
                                      the first argument passed to the function

            finishCommand (function): a passed in function to run at the end of the scrub (right before the mouse is released
                                       back to the user)

            hotkeyDict (dictionary of string(key) function(value) pairs): This dictionary gives the slider functions to assign to
                                                                          keypresses that will override maya hotkeys while the slider
                                                                          is in use.

            visible: bool - if False, will not show the slider bar on screen

            graphKwargs (dict) - args to be passed when creating the ka_qtWidgets.GraphWidget widget

        """
        super(ScrubWidget, self).__init__(parent=ka_qtWidgets.getMayaWindow())

        self.setFocusPolicy(QtCore.Qt.StrongFocus)

        # store signals
        self.scrubWidgetSignals = ScrubWidgetSignals()

        # vars
        width = 400
        height = 400
        offsetFromMouse = 100

        # get cursor pos
        cursorPos = QtGui.QCursor().pos()

        # size window
        self.setFixedSize(width,height)
        #self.setMask(QtGui.QRegion(-1,-1, self.width()+2, self.height()+2))

        # posistion window
        self.move(cursorPos.x()-(self.width()*0.5), cursorPos.y()+offsetFromMouse)

        cursorPos = self.mapFromGlobal(cursorPos)

        # slider setup math
        self.previousValue = defaultValues[0]
        self.currentValues = defaultValues
        #self.startValues = tuple(defaultValues)
        self.currentValueIndex = 0

        mouseInitialPositionX = cursorPos.x()
        #self.mouseGrabOffset = 0.0
        self.step = step
        self.shiftStep = shiftStep

        self.sliderMax = sliderRange[1]
        self.sliderMin = sliderRange[0]
        self.sliderRange = self.sliderMax - self.sliderMin

        #defaultPercentOfSliderRange = (float(defaultValues[0]) - self.sliderMin) / float(self.sliderRange)

        #self.pixelMin = mouseInitialPositionX - (width * defaultPercentOfSliderRange)
        #self.pixelMax = self.pixelMin + width
        #self.pixelRange = self.pixelMax - self.pixelMin
        self.setMouseMapping()

        # main widget
        self.mainWidget = QtGui.QWidget(parent=self)
        self.setCentralWidget(self.mainWidget)

        # create Layout
        self.vLayout = QtGui.QVBoxLayout()
        self.vLayout.setSpacing(0)
        self.vLayout.setContentsMargins(QtCore.QMargins(0,0,0,0))
        self.mainWidget.setLayout(self.vLayout)

        #if curveFunction:
            #def curveFunctionWrapper(x, curveFunction=curveFunction, scrubWidget=self):
                #"""This funciton's only purpose is so make this object availible to the original function command"""
                #return curveFunction(scrubWidget, x)

            #curveFunction = curveFunctionWrapper

        graphKwargs['min'] = (self.sliderMin, 0)
        graphKwargs['max'] = (self.sliderMax, 1)
        graphKwargs['timeMarkers'] = defaultValues

        self.graphWidget = ka_qtWidgets.GraphWidget(**graphKwargs)
        #self.graphWidget.setFixedSize(width,height)

        self.vLayout.addWidget(self.graphWidget)


        # ACTIONS ---------------------------------------------------------------
        # store input commands
        self.hotkeyDict = hotkeyDict
        self.changeCommand = changeCommand
        self.finishCommand = finishCommand

        @QtCore.Slot(int)
        def scubValueChangedCmd(value, self=self):
            """commands to run when the value of the slider has changed"""
            try:
                #print value

                # get stepped value if SHIFT modifier is down
                modifiers = QtGui.QApplication.keyboardModifiers()
                if modifiers == QtCore.Qt.ShiftModifier:
                    value = self.getSteppedValue(value, self.shiftStep)
                    print 'shift down'
                # update internal variables
                self.previousValue = value
                self.currentValues[self.currentValueIndex]  = value

                # update the marker lines in the graph widget if it is visible
                if self.isVisible():
                    self.graphWidget.setTimeMarker(self.currentValueIndex, value)

                # run the change command with the given value
                if changeCommand is not None:
                    values = list(self.currentValues)
                    values.sort()
                    self.changeCommand(self, values)

            except:
                ka_python.printError()
                self.finish()

        @QtCore.Slot(int)
        def scrubFinishedCmd(self=self):
            """commands to run as finishing"""
            print 'finish22'

            self.releaseMouse()
            self.releaseKeyboard()

            if self.finishCommand is not None:
                self.finishCommand(self)

            self.close()

        self.scrubWidgetSignals.valueChangedSignal.connect(scubValueChangedCmd)
        self.scrubWidgetSignals.finishSignal.connect(scrubFinishedCmd)

        # track mouse and keyboard
        self.setMouseTracking(True)
        self.grabMouse()
        self.grabKeyboard()

        # start command
        if startCommand is not None:
            startCommand(self)

        # popWindow
        self.activateWindow()
        self.setFocus()

        if visible:
            self.show()

        # emit first changed signal
        scrubValue = int(round(self.getScrubValue(mouseInitialPositionX)))
        self.scrubWidgetSignals.valueChangedSignal.emit(scrubValue)

    # event overrides ============================================
    def resizeEvent(self, event):
        sizeHint = self.vLayout.totalSizeHint()
        self.resize(sizeHint)
        event.accept()
        self.setMask(QtGui.QRegion(0,0, self.width(), self.height()))

        QtGui.QWidget.resizeEvent(self, event)


    def mousePressEvent(self, event):
        event.accept()
        QtGui.QWidget.mousePressEvent(self, event)
        self.finish()

    def mouseMoveEvent(self, event):
        mouseX = event.pos().x()
        scrubValue = int(round(self.getScrubValue(mouseX)))
        if scrubValue != self.previousValue:
            self.scrubWidgetSignals.valueChangedSignal.emit(scrubValue)

        event.accept()
        QtGui.QWidget.mouseMoveEvent(self, event)

    def focusOutEvent(self, event):
        print 'focus lost'
        event.accept()
        QtGui.QWidget.focusOutEvent(self, event)
        self.finish()

    def keyPressEvent(self, keyEvent):
        keyID = keyEvent.text()
        if keyID in self.hotkeyDict:
            subDict = self.hotkeyDict[keyID]
            if subDict['press']:

                modifiers = int(keyEvent.modifiers())
                modifierDown = True
                if subDict['shift'] and modifiers not in [33554432, 100663296, 369098752, 301989888]:
                    modifierDown = False
                    print 'not shift'

                if subDict['alt'] and modifiers not in [134217728, 201326592, 167772160, 234881024]:
                    modifierDown = False
                    print 'not alt'

                if subDict['ctrl'] and modifiers not in [67108864, 100663296, 201326592, 234881024]:
                    modifierDown = False
                    print 'not ctrl'

                if modifierDown:
                    if subDict['hold']:
                        if not keyEvent.isAutoRepeat():
                            subDict['command'](self)
                            keyEvent.accept()

                    else:
                        subDict['command'](self)
                        keyEvent.accept()
                        return None


        QtGui.QWidget.keyPressEvent(self, keyEvent)


    def keyReleaseEvent(self, keyEvent):

        if not keyEvent.isAutoRepeat():
            keyID = keyEvent.key()
            if keyID in self.hotkeyDict:
                subDict = self.hotkeyDict[keyID]
                if subDict['release']:
                    subDict['command']()
                    keyEvent.accept()

        QtGui.QWidget.keyReleaseEvent(self, keyEvent)


    # custome methods =============================================
    def finish(self):
        self.scrubWidgetSignals.finishSignal.emit()

    def editNextValue(self):
        lastIndex = len(self.currentValues)-1
        if self.currentValueIndex == lastIndex:
            self.currentValueIndex = 0
        else:
            self.currentValueIndex += 1

        self.setMouseMapping()
        self.graphWidget.update()

    def editPreviousValue(self):
        lastIndex = len(self.currentValues)-1
        if self.currentValueIndex == 0:
            self.currentValueIndex = lastIndex
        else:
            self.currentValueIndex -= 1

        self.setMouseMapping()
        self.graphWidget.update()

    def setMouseMapping(self):
        """maps in pixels how the mouse's position will translate into a value. This is important in cases
        where there are more than 1 value, to keep those values from jumping as you switch which value you are
        editing. This is because as you switch to a new value, you mouse has not moved and there will now be a hidden
        offset"""

        cursorPosX = self.mapFromGlobal(QtGui.QCursor().pos()).x()
        width = self.width()
        defaultValue = self.currentValues[self.currentValueIndex]

        defaultPercentOfSliderRange = (float(defaultValue) - self.sliderMin) / float(self.sliderRange)
        self.pixelMin = cursorPosX - (width * defaultPercentOfSliderRange)
        self.pixelMax = self.pixelMin + width
        self.pixelRange = self.pixelMax - self.pixelMin

    def getSteppedValue(self, x, base=1):
        """Returns the stepped value of the slider"""
        return int(base * round(float(x)/base))



    def getScrubValue(self, mouseX):
        """Gets the mouse x position and maps it to the slider's value"""
        if mouseX <= self.pixelMin:
            return self.sliderMin

        elif mouseX >= self.pixelMax:
            return self.sliderMax

        else:
            relativeX = mouseX-self.pixelMin
            percent = relativeX / float(self.pixelRange)
            return self.sliderMin + int(round(self.sliderRange * percent))


def getScrubSlider():
    mayaWindow = ka_qtWidgets.getMayaWindow()
    for child in mayaWindow.children():
        if hasattr(child, 'objectName'):
            if child.objectName() == 'ka_scrubSlider':
                return child

#scrubSlider = getScrubSlider()
#if scrubSlider:
    #scrubSlider.finish()



def createScrubSlider(*args, **kwargs):
    """Returns scrubSlider. This is the main function to create the scrub slider"""
    print 'make'
    scrubSlider = getScrubSlider()
    if scrubSlider:
        try:
            scrubSlider.finish()
        except:
            ka_python.printError()

    else:
        scrubSlider = ScrubWidget(*args, **kwargs)
        scrubSlider.setObjectName('scrubSlider')

    return scrubSlider
