
#====================================================================================
#====================================================================================
#
# ka_menu_weightLib
#
# DESCRIPTION:
#   contains custom widgets
#
# DEPENDENCEYS:
#   PyQt4 or PySide
#   Maya
#
#
# AUTHOR:
#   Kris Andrews (3dkris@3dkris.com)
#
#============   ========================================================================
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

import PySide2 as PyQt
from PySide2 import QtGui, QtCore, QtWidgets
#import shiboken as shiboken
import shiboken2 as shiboken
#from PySide2 import shiboken2
#import pysideuic
import xml.etree.ElementTree as xml
from cStringIO import StringIO

import ka_maya.ka_python as ka_python

import pymel.core as pymel
import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMayaUI as OpenMayaUI

import ka_maya.ka_preference as ka_preference
import ka_maya.ka_skinCluster as ka_skinCluster
import ka_maya.ka_weightPainting as ka_weightPainting
import ka_maya.ka_util as ka_util


## Maya 2020  =============================================================================================
#import qt as PyQt
#from qt import QtGui, QtCore

def getMayaWindow():
    """
    Get the main Maya window as a QtWidgets.QMainWindow instance
    @return: QtWidgets.QMainWindow instance of the top level Maya windows
    """
    ptr = OpenMayaUI.MQtUtil.mainWindow()
    if ptr is not None:
        return shiboken.wrapInstance(long(ptr), QtWidgets.QMainWindow)

    return omui.MQtUtil.mainWindow()


# PYSIDE FUNCTIONS AND IMPORTS  =============================================================================================



#def addQWidget_toMayaUI(qWidget, mayaUI=None):

    #if not mayaUI:
        #mayaUIPointer = long(OpenMayaUI.MQtUtil.getCurrentParent())


    #if not mayaUIPointer:
        #if not mayaUI == None:
            #raise Exception('No UI specified, and no UI set using the maya setParent command')
        #else:
            #raise Exception('specified mayaUI was not found')

    #mayaUIPointer = long(mayaUIPointer)

    #qWidgetPointer = shiboken.getCppPointer(qWidget)[0]
    #OpenMayaUI.MQtUtil.addWidgetToMayaLayout(qWidgetPointer, mayaUIPointer)


#def getMayaUI_asQT(name=None, base=None):
    #"""
    #Utility to get a maya UI item as a QT/PyQT object
    #"""

    ## get pointer
    #ptr = OpenMayaUI.MQtUtil.findControl(name)

    #if not ptr:
        #ptr = OpenMayaUI.MQtUtil.findLayout(name)

    #if not ptr:
        #ptr = OpenMayaUI.MQtUtil.findMenuItem(name)

    #if not ptr:
        #ptr = OpenMayaUI.MQtUtil.findWindow(name)

    #OOOOOOO = "ptr"; print '%s: ' % OOOOOOO, eval(OOOOOOO), ' ', type(eval(OOOOOOO))

    #if ptr is None:
        #return None

    #ptr = long(ptr) # Ensure type
    #if globals().has_key('shiboken'):
        #if base is None:
            #qObj = shiboken.wrapInstance(long(ptr), QtCore.QObject)
            #metaObj = qObj.metaObject()
            #cls = metaObj.className()
            #superCls = metaObj.superClass().className()

            #if hasattr(QtGui, cls):
                #base = getattr(QtGui, cls)
            #elif hasattr(QtGui, superCls):
                #base = getattr(QtGui, superCls)
            #else:
                #base = QtWidgets.QWidget
        #return shiboken.wrapInstance(long(ptr), base)

    ##elif globals().has_key('sip'):
        ##base = QtCore.QObject
        ##return sip.wrapinstance(long(ptr), base)
    #else:
        #return None

#def getMayaWindow():
    #"""
    #Get the main Maya window as a QtWidgets.QMainWindow instance
    #@return: QtWidgets.QMainWindow instance of the top level Maya windows
    #"""
    #ptr = OpenMayaUI.MQtUtil.mainWindow()
    #if ptr is not None:
        #return shiboken.wrapInstance(long(ptr), QtWidgets.QMainWindow)

global app
app = QtWidgets.QApplication.instance() #get the qApp instance if it exists.
if not app:
    app = QtWidgets.QApplication(sys.argv)


def getMayaMainWindow():
    mayaWin = next(w for w in app.topLevelWidgets() if w.objectName()=='MayaWindow')

    return mayaWin

print(getMayaMainWindow())

currentFolder = os.path.abspath(os.path.join(os.path.dirname(__file__), ".",))
iconFolder = os.path.abspath(os.path.join(currentFolder, "icons",))


## FUNCTIONS
def addSeparatorItem(parent, label=''):
    separator = QtWidgets.QAction(label, parent)
    separator.setSeparator(True)
    parent.addAction(separator)

    return separator


def addSubmenuItem(subMenuName, parentMenu, icon=None, tearOff=True, command=None, font=None):
    """Add a submenu to a menu item, this submenu can also trigger a command on left click
    if one is passed in"""

    #subMenu = kaQMenu(parent=parentMenu)
    subMenu = QtWidgets.QMenu(parent=parentMenu)
    subMenuAction = QtWidgets.QAction(subMenuName, parentMenu)
    subMenuAction.setMenu(subMenu)

    if icon:
        subMenuAction.setIcon(QtGui.QIcon(os.path.join(iconFolder, icon)))

    if font:
        subMenuAction.setFont(font)

    parentMenu.addAction(subMenuAction)

    if command:
        parentMenu.connect(subMenuAction, QtCore.SIGNAL('triggered()'), command)

    if tearOff:
        subMenu.setTearOffEnabled(True)

    return subMenu


def endSubmenuItem(subMenu):
    """Finishes a subMenu"""

    actions = subMenu.actions()
    hasQWidgetAction = False
    for action in actions:
        if action.__class__.__name__ == 'QWidgetAction':
            hasQWidgetAction = True
            break

    if hasQWidgetAction:

        tearOffWidgetAction =  TearOffWidgetAction(subMenu)
        subMenu.insertAction(actions[0], tearOffWidgetAction)
    else:
        subMenu.setTearOffEnabled(True)


def addWidgetMenuItem(widget, parentMenu, font=None):
    """Makes a widget into a QMenuWidgetItem and adds it to the menu"""

    QWidgetAction = QtWidgets.QWidgetAction(parentMenu)
    QWidgetAction.setDefaultWidget(widget)
    parentMenu.addAction(QWidgetAction)

    return QWidgetAction


def addMenuItem(label, menu, icon=None, command=None, colorIcon=None, font=None,):
    """adds QAction to the menu and assigns the command (which is defined 1 line above the creation of each QAction as cmd) to be the
    result of clicking the menu item
    Args:
        label - string - the label of the menu item
        menu - QMenu - the menu to add the item to
    Kwargs:
        icon - string - the file name of the icon to use for the item, must be a file existing
               in the icons directory
        command - function - the command to trigger when the item is l-clicked
        colorIcon - list - uses given rbg 0.0-1.0 values to generates an icon of solid
                    color
    """

    if colorIcon:
        pixMap = QtGui.QPixmap(100, 100)
        pixMap.fill(QtGui.QColor(255*colorIcon[0], 255*colorIcon[1], 255*colorIcon[2],))
        icon = QtGui.QIcon(pixMap)
        newQAction = QtWidgets.QAction(icon, label, menu)

    elif icon:
        newQAction = QtWidgets.QAction(QtGui.QIcon(os.path.join(iconFolder, icon)), label, menu)
    else:
        newQAction = QtWidgets.QAction(label, menu)

    if font:
        newQAction.setFont(font)

    if command:
        menu.connect(newQAction, QtCore.SIGNAL('triggered()'), command)

    menu.addAction(newQAction)

    return newQAction


## PREFRENCE MENU ITEMS

def prefMenuItem_radioButtons(preferenceName, labelList, defaultIndex, menu, command=None, font=None):
    """Adds a set of radio buttons to the menu, who's value selection gets stored as
    a preference"""

    actionGroup = QtWidgets.QActionGroup(menu)
    actionGroup.setExclusive(True)
    defaultIndex = ka_preference.get(preferenceName, defaultIndex)

    for i, label in enumerate(labelList):
        action = actionGroup.addAction(label)
        action.setCheckable(True)
        if font:
            action.setFont(font)

        if i == defaultIndex:
            action.setChecked(True)

        def cmd(i=i, preferenceName=preferenceName, command=command):
            ka_preference.set(preferenceName, i)
            if command != None:
                command()

        menu.connect(action, QtCore.SIGNAL('triggered()'), cmd)
        menu.addAction(action)

    return actionGroup


def addPrefMenuItem_bool(label, preferenceKey, defaultPreferenceValue, menu, command=None, font=None):
    action = QtWidgets.QAction(label, menu)
    if font:
        action.setFont(font)

    action.setCheckable(True)

    value = ka_preference.get(preferenceKey, defaultPreferenceValue)
    if value: action.setChecked(True)
    else: action.setChecked(False)

    def cmd(action=action, preferenceKey=preferenceKey, command=command):
        checkboxState = action.isChecked()
        if checkboxState:
            action.setChecked(2)
            ka_preference.add(preferenceKey, True)

        else:
            action.setChecked(0)
            ka_preference.add(preferenceKey, False)

        if command:
            command()

    menu.connect(action, QtCore.SIGNAL('triggered()'), cmd)
    menu.addAction(action)


class GraphWidgetSignals(QtCore.QObject):
    valueChangedSignal = QtCore.Signal(int)

class GraphWidget(QtWidgets.QWidget):
    STYLE_SHEET = """

    GraphWidget {
        background-color: rgb(0, 0, 0);
        color: rgb(0, 0, 255);
    }

"""
    def __init__(self, min=(0,0), max=(10,10), timeMarkers=None, activeTimeMarkerIndex=None,
                 drawCurve=False, curveType='Linear', curvePoints=((0.0,0.0), (0.0,10.0))):
        """draws a graph which you can plot a function curve on.

        Args:
            min (tuple): the min x,y value for the graph

            max (tuple): the max x,y value for the graph

            timeMarkers (list/tuple): a list of x values where markers will be created. marks can
                represent current time for example, it is possible to have more than one marker.

            activeTimeMarkerIndex (int): the index of the current marker. It will be colored diffrently
                than other markers

            drawCurve (bool): if True, a curve will be drawn on the graph

            curveType (string): valid types are "Linear" and "Bezier". Will define what kind of curve
                is drawn. If the type is Bezier, the curvePoints input should be exactly 4 points

            curvePoints (list/Tuple): these are the points (tuples of floats) that will define the curve
                drawn. If the type is Bezier, the curvePoints input should be exactly 4 points
        """

        super(GraphWidget, self).__init__()

        self.min = min
        self.max = max
        self.timeMarkers = timeMarkers
        self.activetimeMarkerIndex = activeTimeMarkerIndex

        # curve vars
        self.drawCurve = drawCurve
        self.curveType = curveType.lower()
        self.curvePoints = curvePoints

        # style sheet
        self.setStyleSheet(self.STYLE_SHEET)

        palette = QtGui.QPalette()
        palette.setColor(PyQt.QtGui.QPalette.Background, QtGui.QColor(0,0,25))
        palette.setColor(PyQt.QtGui.QPalette.Window, QtGui.QColor(0,0,25))
        self.setPalette(palette)

    def setTimeMarker(self, index, markerValue):
        self.timeMarkers[index] = markerValue
        self.activetimeMarkerIndex = index

        self.update()

    def setCurvePoints(self, curvePoints):
        self.curvePoints = curvePoints

    def _getPoint_fromValue_(self, x, y):
        """convert the pixel position of a value of the slider"""

        rangeX = self.max[0]-self.min[0]
        rangeY = self.max[1]-self.min[1]

        x -= float(self.min[0])
        y -= float(self.min[1])

        if x is 0:
            percX = 0.0
        else:
            percX = x/rangeX

        if y is 0:
            percY = 0.0
        else:
            percY = y/rangeY

        targRangeX = self.width()
        targRangeY = self.height()

        x = targRangeX*percX
        y = targRangeY*percY

        return x,y

    def _getValue_fromPointInPixelSpace_(self, x, y):
        """convert the pixel position of a value of the slider"""

        rangeX = self.max[0]-self.min[0]
        rangeY = self.max[1]-self.min[1]

        x -= float(self.min[0])
        y -= float(self.min[1])

        if x == 0:
            percX = 0.0
        else:
            percX = x/rangeX

        if y == 0:
            percY = 0.0
        else:
            percY = y/rangeY

        targRangeX = self.width()
        targRangeY = self.height()

        x = targRangeX*percX
        y = targRangeY*percY

        return x,y

    def paintEvent(self, event,):
        qp = PyQt.QtGui.QPainter()
        qp.setRenderHint(PyQt.QtGui.QPainter.HighQualityAntialiasing)
        #qp.setRenderHint(PyQt.QtGui.QPainter.HighQualityAntialiasing)
        qp.begin(self)
        self._draw_(event, qp)
        qp.end()

        event.accept()
        QtWidgets.QWidget.paintEvent(self, event)

    def _draw_(self, event, qp):
        # size vars
        widgetHeight = self.height()
        widgetWidth = self.width()

        # colors
        backgroundColor = QtGui.QColor(0,0,25)
        gridColor = QtGui.QColor(0,0,125)
        curveColor = QtGui.QColor(255,255,255)
        curveGridColor = QtGui.QColor(150,0,0)
        curveBackgroundColor = QtGui.QColor(75,0,0)

        # draw background rectangle
        qp.setBrush(backgroundColor)
        qp.drawRect(event.rect())

        brush = QtGui.QBrush()
        brush.setColor(gridColor)
        brush.setStyle(QtCore.Qt.BrushStyle.CrossPattern)
        qp.setBrush(brush)
        qp.drawRect(event.rect())


        # draw curve
        if self.drawCurve:
            curvePen = QtGui.QPen()
            curvePen.setColor(curveColor)
            curvePen.setWidth(1)
            qp.setPen(curvePen)

            gridBrush = QtGui.QBrush()
            gridBrush.setColor(curveGridColor)
            gridBrush.setStyle(QtCore.Qt.BrushStyle.CrossPattern)

            backgroundBrush = QtGui.QBrush(curveBackgroundColor)

            path = QtGui.QPainterPath(QtCore.QPointF(0, 0))

            if self.curveType == 'linear':
                points = []
                for point in self.curvePoints:
                    x, y = self._getPoint_fromValue_(*point)
                    point = QtCore.QPointF(x, y)
                    points.append(point)

                polygon = QtWidgets.QPolygonF(points)

                qp.setBrush(backgroundBrush)
                qp.drawPolygon(polygon )

                qp.setBrush(gridBrush)
                qp.drawPolygon(polygon )

            elif self.curveType == 'bezier':
                points = []
                for point in self.curvePoints:
                    x, y = self._getPoint_fromValue_(*point)
                    point = QtCore.QPointF(x, y)
                    points.append(point)

                path = QtGui.QPainterPath()
                path.cubicTo(*points[1:])
                path.lineTo(0.0, 0.0+float(widgetHeight))

                qp.setBrush(backgroundBrush)
                qp.drawPath(path)

                qp.setBrush(gridBrush)
                qp.drawPath(path)



        # draw time makers
        if self.timeMarkers is not None:
            activeMarkerColor1 = QtGui.QColor(0,150,150)
            activeMarkerColor2 = QtGui.QColor(0,75,75)

            inActiveMarkerColor1 = QtGui.QColor(150,150,150)
            inActiveMarkerColor2 = QtGui.QColor(75,75,75)

            qp.setPen(activeMarkerColor1)
            qp.setBrush(activeMarkerColor2)

            for i, time in enumerate(self.timeMarkers):
                if self.activetimeMarkerIndex is not None:
                    if i == self.activetimeMarkerIndex:
                        qp.setPen(activeMarkerColor1)
                        qp.setBrush(activeMarkerColor2)
                    else:
                        qp.setPen(inActiveMarkerColor1)
                        qp.setBrush(inActiveMarkerColor2)

                posX, posY = self._getPoint_fromValue_(time, 0)

                #lineStart = QtCore.QPoint(posX, 0)
                #lineEnd = QtCore.QPoint(posX, widgetHeight)
                x = posX-2
                y = 0
                w = 4
                h = widgetHeight

                if x < 0:
                    x = 0
                elif x+w > widgetWidth-1:
                    x = widgetWidth-w-1

                qp.drawRect(x, y, w, h)

                #qp.drawLine(lineStart, lineEnd)



# ==============================================================================================
class DocStringWidget(QtWidgets.QWidget):
    """A QWidget for displaying a python docstring
    """
    def __init__(self, documentedObject, *args, **kwargs):

        super(DocStringWidget, self).__init__(*args, **kwargs)

        # layout
        self.vLayout = QtWidgets.QVBoxLayout()
        self.vLayout.setContentsMargins(QtCore.QMargins(15,15,15,20))
        self.setLayout(self.vLayout)

        self.label = QtWidgets.QLabel()

        indent = '    '
        #docStringHeader = '%s:\n< %s.%s >\n\n%s' % (tool.label, tool._function.__module__, tool._function.__name__, indent)
        docString = str(documentedObject.__doc__).replace('\n', '\n%s' % indent)

        self.label.setText(docString)


        self.vLayout.addWidget(self.label)

# ==============================================================================================
class ToolSettingsWidget(QtWidgets.QWidget):
    """A QWidget for presenting the settings of a "tool" item.

    """
    def __init__(self, tool, *args, **kwargs):

        super(ToolSettingsWidget, self).__init__(*args, **kwargs)

        # layout
        self.vLayout = QtWidgets.QVBoxLayout()
        self.vLayout.setContentsMargins(QtCore.QMargins(15,15,15,20))
        self.setLayout(self.vLayout)

        if tool.settings:
            QPALETTE_INPUTITEM = PyQt.QtGui.QPalette()
            QPALETTE_INPUTITEM.setColor(PyQt.QtGui.QPalette.Text, PyQt.QtGui.QColor(255, 255, 255,))

            for settingObject in tool.settings:

                # horizontal layout
                hLayout = QtWidgets.QHBoxLayout()
                hLayout.setContentsMargins(QtCore.QMargins(0,0,0,0))
                hLayout.setSpacing(0)
                self.vLayout.addLayout(hLayout)


                # add Label
                settingLabel = QtWidgets.QLabel('%s:' % settingObject.settingName)
                settingLabel.setFixedWidth(settingLabel.sizeHint().width())
                settingLabel.setPalette(QPALETTE_INPUTITEM)
                hLayout.addWidget(settingLabel)
                hLayout.addSpacing(10)

                # setting widget
                self.settingWidget = self._getSettingInputWidget(settingObject)
                self.settingWidget.setPalette(QPALETTE_INPUTITEM)
                hLayout.addWidget(self.settingWidget)

                hLayout.addStretch()

        self.vLayout.addSpacing(10)


    def _getSettingInputWidget(self, settingObject):
        valueType = settingObject.valueType.lower()

        defaultValue = ka_preference.get(settingObject.settingLongName, None)
        if defaultValue == None:
            defaultValue = settingObject.defaultValue

        # INT
        if valueType == 'int':
            settingInputWidget = PyQt.QtWidgets.QSpinBox(parent=self)
            settingInputWidget.setValue(defaultValue)
            signal = settingInputWidget.valueChanged

            @QtCore.Slot()
            def changedCmd(value, settingObject=settingObject, settingInputWidget=settingInputWidget):
                ka_preference.add(settingObject.settingLongName, settingInputWidget.value())

        # FLOAT
        if valueType == 'float':
            settingInputWidget = PyQt.QtWidgets.QDoubleSpinBox(defaultValue, parent=self)
            settingInputWidget.setValue(defaultValue)
            signal = settingInputWidget.valueChanged

            @QtCore.Slot()
            def changedCmd(value, settingObject=settingObject, settingInputWidget=settingInputWidget):
                ka_preference.add(settingObject.settingLongName, settingInputWidget.value())

        # STRING
        elif valueType == 'string':
            settingInputWidget = PyQt.QtWidgets.QLineEdit(defaultValue, parent=self)
            signal = settingInputWidget.returnPressed

            @QtCore.Slot()
            def changedCmd(value, settingObject=settingObject, settingInputWidget=settingInputWidget):
                ka_preference.add(settingObject.settingLongName, settingInputWidget.text())

        # BOOL
        elif valueType == 'bool':
            settingInputWidget = PyQt.QtWidgets.QCheckBox(parent=self)
            settingInputWidget.setChecked(defaultValue)
            signal = settingInputWidget.stateChanged

            @QtCore.Slot()
            def changedCmd(value, settingObject=settingObject, settingInputWidget=settingInputWidget):
                ka_preference.add(settingObject.settingLongName, settingInputWidget.isChecked())

        # ENUM
        elif valueType == 'enum':
            settingInputWidget = PyQt.QtWidgets.QComboBox(parent=self)
            settingInputWidget.addItems(settingObject.enumValues)
            settingInputWidget.setCurrentIndex(defaultValue)
            signal = settingInputWidget.currentIndexChanged

            @QtCore.Slot()
            def changedCmd(value, settingObject=settingObject, settingInputWidget=settingInputWidget):
                ka_preference.add(settingObject.settingLongName, settingInputWidget.currentIndex())

        signal.connect(changedCmd)
        return settingInputWidget


# ==============================================================================================
class ColorSelectorWidget(QtWidgets.QWidget):
    """A QWidget for selecting colors

    """

    STYLE_SHEET = """

    QPushButton {
        color: rgb(255, 35, 40);
        border-width: 1px;
        border-color: rgb(55, 55, 55);
        border-style:groove;
    }
"""

    def __init__(self, columns=2, colors=((1,0,0), (1,1,0), (0,1,0), (0,1,1), (0,0,1), (1,0,1),),
                 buttonHeight=25, buttonWidth=25, function=None, **kwargs):
        """

        Kwargs:
          columns - int -default=2 -number of columns
          colors - list/tuple of list/tuples - colors to display
          buttonHeight - int - height of the buttons
          buttonWidth - int - width of the buttons
          function - function - the function to call on button press. The color value (0.0-1.0) will be passed
                                as the first arg
        """
        super(ColorSelectorWidget, self).__init__(**kwargs)

        #columns = kwargs.pop('columns', 2)
        #colors = kwargs.pop('colors', ((1,0,0), (1,1,0), (0,1,0), (0,1,1), (0,0,1), (1,0,1), ))
        #buttonHeight = kwargs.pop('buttonHeight', 25)
        #buttonWidth = kwargs.pop('buttonWidth', 25)
        #function = kwargs.pop('function', self.function)

        if function == None:
            self.function


        self.setStyleSheet(self.STYLE_SHEET)

        # layout
        self.vLayout = QtWidgets.QVBoxLayout()
        self.vLayout.setContentsMargins(QtCore.QMargins(2,2,2,2))
        self.vLayout.setSpacing(0)
        self.setLayout(self.vLayout)

        i = 0
        last = columns
        hLayout = None
        for color in colors:
            if i == last:
                i = 0

            if i == 0:
                hLayout = QtWidgets.QHBoxLayout()
                self.vLayout.addLayout(hLayout)

            i += 1

            button = QtWidgets.QPushButton()
            button.setFixedSize(buttonWidth, buttonHeight)
            hLayout.addWidget(button)

            button.setStyleSheet("background-color: rgb(%s,%s,%s)" % (str(int(color[0]*255)),
                                                                      str(int(color[1]*255)),
                                                                      str(int(color[2]*255)), ))

            def functionWrapper(function=function, color=color):
                function(color)

            button.pressed.connect(functionWrapper)


    def function(self, color):
        print 'color %s selected' % str(color)


# ==============================================================================================
class objectEditor(QtWidgets.QWidget):
    """A QWidget for editing objects. This widget will group inheriting widgets
    into the classes they belong.
    """

    STYLE_SHEET = """

    QPushButton {
        color: rgb(255, 35, 40);
        border-width: 1px;
        border-color: rgb(55, 55, 55);
        border-style:groove;
    }
"""

    def __init__(self, *args, **kwargs):
        """
        """

        super(objectEditor, self).__init__(*args, **kwargs)
