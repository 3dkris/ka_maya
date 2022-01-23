import sys
import os
import operator
import ast

import maya.cmds as cmds
import pymel.core as pymel

import ka_maya.ka_python as ka_python
import ka_maya.ka_preference as ka_preference
import ka_maya.ka_animation as ka_animation
import ka_maya.ka_stopwatchTool.commands as commands

import ka_maya.ka_qtWidgets as ka_qtWidgets
PyQt = ka_qtWidgets.PyQt
QtGui = ka_qtWidgets.QtGui
QtCore = ka_qtWidgets.QtCore
QtWidgets = ka_qtWidgets.QtWidgets

DEFAULT_SAVE_DIRECTORY = os.path.abspath(pymel.internalVar(userScriptDir=True))


STYLE_SHEET = """
    QWidget {
        background-color: rgb(20, 20, 20);
    }

    QTabWidget::tab-bar {
        left: 5px;
    }

    QTabBar::tab {
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                stop: 0 rgb(10, 10, 20), stop: 0.4 rgb(20, 20, 40),
                                stop: 0.5 rgb(10, 10, 20), stop: 1.0 rgb(20, 20, 40));
    border: 1px solid rgb(100, 100, 100);
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    min-width: 8ex;
    max-height: 10;
    padding: 2px;
    }

    QTabBar::tab:selected {
        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
        stop: 0 rgb(20, 40, 75), stop: 0.4 rgb(20, 40, 125),
        stop: 0.5 rgb(20, 40, 75), stop: 1.0 rgb(20, 40, 125));

        border: 1px solid rgb(200, 200, 200);
    }

    QTabBar::close-button {
        color: rgb(255, 255, 255);

    }

    QTreeView {
        background-color: rgb(0, 0, 0);
        color: rgb(0, 255, 255);
        selection-color: rgb(0, 0, 0);
        selection-background-color: rgb(200, 200, 200);
        border-width: 1px;
        border-color: rgb(100, 100, 100);
        border-style:solid;
        font-family: "Courier"
    }

    QTableView {
        background-color: rgb(10, 10, 10);
        alternate-background-color: rgb(35, 35, 35);
        color: rgb(200, 200, 200);
        selection-color: rgb(0, 0, 0);
        selection-background-color: rgb(200, 200, 200);
        border-width: 1px;
        border-color: rgb(100, 100, 100);
        border-style:solid;
        font-family: "Courier"
    }

    QHeaderView {
        background-color: rgb(20, 40, 75);
        color: rgb(200, 200, 200);
        height: 18;
    }
    QScrollBar {
        background-color: rgb(50, 50, 50);
        color: rgb(100, 100, 255);
        margin: 0px 0px 0px 0px;
        border: 1px solid rgb(170, 170, 170);
    }
    QScrollBar::add-line:horizontal{
        background-color: rgb(20, 40, 60);
        border: 1px solid rgb(170, 170, 170);
    }
    QScrollBar::sub-line:horizontal{
        background-color: rgb(20, 40, 60);
        border: 1px solid rgb(170, 170, 170);
    }
    QScrollBar::add-line:vertical{
        background-color: rgb(20, 40, 60);
        border: 1px solid rgb(170, 170, 170);
    }
    QScrollBar::sub-line:vertical{
        background-color: rgb(20, 40, 60);
        border: 1px solid rgb(170, 170, 170);
    }
    QScrollBar::handle:horizontal{
        background-color: rgb(170, 170, 170);
        min-width:25;
    }
    QScrollBar::handle:vertical{
        background-color: rgb(170, 170, 170);
        min-height:25;
    }
    QScrollBar:vertical{
        max-width: 10
    }
    QScrollBar:horizontal{
        max-height: 10
    }
    QSplitter::handle:horizontal{
        width: 1px;
    }
    QSplitter::handle:vertical {
        height: 1px;
    }


"""

class StopwatchUIWindow(QtWidgets.QMainWindow):
    """
    This UI is for viewing the results of stopwatch recordings. It is also the main UI
    of this tool
    """

    title = 'ka_stopwatch UI'

    # Widget Dimentions
    windowWidth = 1400
    windowHeight = 1000

    def __init__(self, **kwargs):
        parent = ka_qtWidgets.getMayaWindow()
        super(StopwatchUIWindow, self).__init__(parent=parent)

        self.setStyleSheet(STYLE_SHEET)
        self.setWindowTitle(self.title)
        self.resize(self.windowWidth, self.windowHeight)

        # main widget
        self.mainWidget = QtWidgets.QWidget(parent=self)
        self.setCentralWidget(self.mainWidget)

        # create Layout
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.setContentsMargins(QtCore.QMargins(0,0,0,0))
        self.layout.setSpacing(1)
        self.mainWidget.setLayout(self.layout)

        self.tabWidget = QtWidgets.QTabWidget()
        self.tabWidget.setTabsClosable(True)
        self.tabWidget.setMovable(True)
        self.tabWidget.setCurrentIndex(0)
        self.tabWidget.setTabPosition(QtWidgets.QTabWidget.North)
        self.layout.addWidget(self.tabWidget)
        self.tabWidget.tabCloseRequested.connect(self.closeTab)


        openFiles = ka_preference.get('stopwatchTool_openFiles', None)
        if not openFiles:
            self.addTab()

        else:
            for _file in openFiles:
                try:
                    self.addTab()
                    self.openRecording(_file)

                except:
                    pymel.warning('failed to load file: %s' % _file)
                    self.addTab()

        # actions -----------------------------------------------------------

        # New Stopwatch Recording Action
        runTimerAction = QtWidgets.QAction('New - Stopwatch Recording', self)
        runTimerAction.setShortcut('Ctrl+R')
        runTimerAction.setStatusTip('Launches the Timer options Window')
        runTimerAction.triggered.connect(self.newRecordingWindow)

        # Open Stopwatch Recording Action
        openAction = QtWidgets.QAction('Open - Stopwatch Recording', self)
        openAction.setShortcut('Ctrl+O')
        openAction.setStatusTip('Opens the results of a timer operation')
        openAction.triggered.connect(self.openStopwatchRecording)

        # Exit action
        exitAction = QtWidgets.QAction(QtGui.QIcon('exit24.png'), 'Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')

        # New tab Action
        newTimerInfoTabAction = QtWidgets.QAction('Add Tab - Timer Info ', self)
        newTimerInfoTabAction.setShortcut('Ctrl+T')
        newTimerInfoTabAction.setStatusTip('Adds a Tab for viewing the timing info of a recording')
        newTimerInfoTabAction.triggered.connect(self.addTab)


        # menu bar ----------------------------------------------------------
        exitAction.triggered.connect(self.close)
        menubar = self.menuBar()

        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(runTimerAction)
        fileMenu.addAction(openAction)
        fileMenu.addAction(exitAction)

        #displayMenu = menubar.addMenu('&Run Timer')

        displayMenu = menubar.addMenu('&Display')

        extrasMenu = menubar.addMenu('&Extras')

        tabsMenu = menubar.addMenu('&Tabs')
        tabsMenu.addAction(newTimerInfoTabAction)

    def addTab(self):
        stopwatchDataWidget = StopwatchDataWidget()
        self.tabWidget.addTab(stopwatchDataWidget, 'new')
        self.tabWidget.setCurrentIndex(self.tabWidget.count()-1)

    def closeTab(self, index):
        self.tabWidget.removeTab(index)
        self.savePrefs_openFiles()

    def newRecordingWindow(self):
        print 'run timer'
        window = NewStopwatchRecordingWindow(stopwatchWindow=self)
        window.show()

    def openStopwatchRecording(self):
        """
        open a stopwatch recording file
        """

        defaultSaveDirectory = ka_preference.get('stopwatchTool_defaultSaveDirectory', DEFAULT_SAVE_DIRECTORY)

        try:
            filePath = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file', defaultSaveDirectory)

        except:
            filePath = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file', DEFAULT_SAVE_DIRECTORY)

        if filePath:
            if isinstance(filePath, tuple):
                filePath = filePath[0]

            filePath = os.path.abspath(filePath)
            defaultSaveDirectory = ka_preference.set('stopwatchTool_defaultSaveDirectory', filePath)

            self.openRecording(filePath)


    def openRecording(self, filePath):

        stopwatchDataWidget = self.tabWidget.currentWidget()
        stopwatchDataWidget.loadTimerData(filePath)

        self.savePrefs_openFiles()

        title = os.path.split(os.path.split(filePath)[0])[1]
        self.tabWidget.setTabText(self.tabWidget.currentIndex(), title)

    def savePrefs(self):
        self.savePrefs_openFiles()

    def savePrefs_openFiles(self):
        openFiles = []
        for i in range(self.tabWidget.count()):
            stopwatchDataWidget = self.tabWidget.widget(i)
            if stopwatchDataWidget._file:
                openFiles.append(stopwatchDataWidget._file)

        ka_preference.set('stopwatchTool_openFiles', openFiles)


class NewStopwatchRecordingWindow(QtWidgets.QMainWindow):
    """
    A window with settings for starting a new stopwatch recording. This UI also
    launches the actual recording
    """

    title = 'Save New Stopwatch Recording'

    # Widget Dimentions
    windowWidth = 300
    windowHeight = 150

    def __init__(self, stopwatchWindow=None, **kwargs):
        parent = ka_qtWidgets.getMayaWindow()
        super(NewStopwatchRecordingWindow, self).__init__(parent=parent)

        self.stopwatchWindow = stopwatchWindow

        self.setWindowTitle(self.title)
        self.setFixedWidth(self.windowWidth)
        self.setFixedHeight(self.windowHeight)

        # main widget
        self.mainWidget = QtWidgets.QWidget(parent=self)
        self.setCentralWidget(self.mainWidget)

        # create Layout
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.setContentsMargins(QtCore.QMargins(15,15,15,15))
        self.layout.setSpacing(1)
        self.mainWidget.setLayout(self.layout)

        self.hLayoutA = QtWidgets.QHBoxLayout()
        self.hLayoutA.setContentsMargins(QtCore.QMargins(0,0,0,0))
        self.hLayoutA.setSpacing(1)
        self.layout.addLayout(self.hLayoutA)

        self.hLayoutB = QtWidgets.QHBoxLayout()
        self.hLayoutB.setContentsMargins(QtCore.QMargins(0,0,0,0))
        self.hLayoutB.setSpacing(1)
        self.layout.addLayout(self.hLayoutB)

        # frame range
        frameRangeLabel = QtWidgets.QLabel('Frame Range:')
        self.hLayoutA.addWidget(frameRangeLabel)

        self.frameRangeStartField = QtWidgets.QSpinBox()
        self.frameRangeEndField = QtWidgets.QSpinBox()
        frameRangeLayout = QtWidgets.QHBoxLayout()
        frameRangeLayout.setContentsMargins(QtCore.QMargins(0,0,0,0))
        frameRangeLayout.addWidget(self.frameRangeStartField)
        frameRangeLayout.addWidget(self.frameRangeEndField)
        self.hLayoutA.addLayout(frameRangeLayout)

        self.frameRangeStartField.setMaximum(9999999)
        self.frameRangeStartField.setMinimum(-9999999)
        self.frameRangeEndField.setMaximum(9999999)
        self.frameRangeEndField.setMinimum(-9999999)

        self.frameRangeStartField.setValue(ka_preference.get('stopwatchTool_recordingRangeStart', 0))
        self.frameRangeEndField.setValue(ka_preference.get('stopwatchTool_recordingRangeEnd', 100))

        self.frameRangeStartField.valueChanged.connect(self.changeRangeValue)
        self.frameRangeEndField.valueChanged.connect(self.changeRangeValue)

        # buttons
        button = QtWidgets.QPushButton('Start / Save')
        button.pressed.connect(self.startRecording)
        self.hLayoutB.addWidget(button)

        button = QtWidgets.QPushButton('Cancel')
        button.pressed.connect(self.close)
        self.hLayoutB.addWidget(button)

    def changeRangeValue(self, *args):
        startValue = self.frameRangeStartField.value()
        endValue = self.frameRangeEndField.value()

        ka_preference.set('stopwatchTool_recordingRangeStart', startValue)
        ka_preference.set('stopwatchTool_recordingRangeEnd', endValue)


    def startRecording(self):
        reload(commands)

        defaultSaveDirectory = ka_preference.get('stopwatchTool_defaultSaveDirectory', DEFAULT_SAVE_DIRECTORY)

        try:
            rootDir = QtWidgets.QFileDialog.getSaveFileName(self, 'Save file', defaultSaveDirectory)

        except:
            rootDir = QtWidgets.QFileDialog.getSaveFileName(self, 'Save file', DEFAULT_SAVE_DIRECTORY)

        if rootDir:
            if isinstance(rootDir, tuple):
                rootDir = rootDir[0]

            rootDir = os.path.abspath(rootDir)

            if os.path.isfile(rootDir):
                if rootDir.endswith('stopwatchFile.txt'):
                    rootDir = os.path.split(rootDir)[0]
                else:
                    raise Exception('%s is not a file name, your save name needs to be a folder name' % dirPath)

            # set framerange
            frameStartValue = self.frameRangeStartField.value()
            frameEndValue = self.frameRangeEndField.value()

            # run dg timer
            #currentFrame = cmds.currentTime(query=True)
            commands.doStopwatchRecording(rootDir, startFrame=frameStartValue, endFrame=frameEndValue)
            #cmds.currentTime(currentFrame)

            ka_preference.set('stopwatchTool_defaultSaveDirectory', os.path.split(rootDir)[0])

            if self.stopwatchWindow:
                stopWatchFilePath = os.path.join(rootDir, 'stopwatchFile.txt')
                self.stopwatchWindow.addTab()
                self.stopwatchWindow.openRecording(stopWatchFilePath)

            self.close()


class StopwatchDataWidget(QtWidgets.QWidget):
    def __init__(self, **kwargs):
        super(StopwatchDataWidget, self).__init__(**kwargs)

        self._file = None

        # get preferences
        self.hideZeroComputes =True

        # create Layout
        self.layout = QtWidgets.QHBoxLayout()
        self.layout.setContentsMargins(QtCore.QMargins(0,0,0,0))
        self.layout.setSpacing(1)
        self.setLayout(self.layout)

        self.stopwatchDataWidget_times = StopwatchDataWidget_times()
        self.stopwatchDataWidget_times.timesTabelView.clicked.connect(self.selectionUpdated)

        # Right Side ============================================================
        self.stopwatchDataWidget_traces = StopwatchDataWidget_traces()


        # Splitter ============================================================
        self.splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self.layout.addWidget(self.splitter)

        self.splitter.addWidget(self.stopwatchDataWidget_times)
        self.splitter.addWidget(self.stopwatchDataWidget_traces)


    def selectionUpdated(self, modelIndex):
        dataModel = self.stopwatchDataWidget_times.stopwatchDataModel_times
        row = modelIndex.row()

        sortedIndex = dataModel.indexOrder[row]
        node = dataModel.data_nodeNames[sortedIndex]

        self.stopwatchDataWidget_traces._loadTracerTreeForGivenNode_(node, nodeIndex=sortedIndex)

        if node and node != '-':
            try:
                cmds.select(node)
            except:
                cmds.warning('%s not found, unable to select' % node)



    def itemSelected(self, item):
        cmds.select()

    def loadTimerData(self, filePath):
        self._file = filePath

        self.stopwatchDataWidget_times.loadFile(filePath)
        self.stopwatchDataWidget_traces.loadFile(filePath)

        self.stopwatchDataWidget_times.timesTabelView.sortByColumn(0, QtCore.Qt.DescendingOrder)



class StopwatchDataWidget_times(QtWidgets.QWidget):

    def __init__(self, **kwargs):
        super(StopwatchDataWidget_times, self).__init__(**kwargs)

        # create Layout
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.setContentsMargins(QtCore.QMargins(0,0,0,0))
        self.layout.setSpacing(1)
        self.setLayout(self.layout)

        # data model
        self.stopwatchDataModel_times = StopwatchDataModel_times()

        # list View
        self.timesTabelView = QtWidgets.QTableView()
        self.timesTabelView.setModel(self.stopwatchDataModel_times)
        self.timesTabelView.setAlternatingRowColors(True)
        self.layout.addWidget(self.timesTabelView)

        horizontalHeader = self.timesTabelView.horizontalHeader()
        horizontalHeader.setStretchLastSection(True)

        verticalHeader = self.timesTabelView.verticalHeader()
        verticalHeader.setVisible(False)

        self.timesTabelView.setSortingEnabled(True)

        self.timesTabelView.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)

        # set column width to fit contents
        self.timesTabelView.resizeRowsToContents()
        self.timesTabelView.resizeColumnsToContents()

        # actions and right click menu
        self.menu = QtWidgets.QMenu(self)

        self.displayRedundantComputesAction = QtWidgets.QAction('Display Redundant Computes', self)
        self.displayPercentsAction = QtWidgets.QAction('Display Percents', self)
        self.displayCountAction = QtWidgets.QAction('Display Count', self)
        self.displayTimeAction = QtWidgets.QAction('Display Time', self)
        self.displayNodeTypeAction = QtWidgets.QAction('Display NodeType', self)
        self.displayNodeNameAction = QtWidgets.QAction('Display Node Name', self)

        self.displayRedundantComputesAction.setCheckable(True)
        self.displayPercentsAction.setCheckable(True)
        self.displayCountAction.setCheckable(True)
        self.displayTimeAction.setCheckable(True)
        self.displayNodeTypeAction.setCheckable(True)
        self.displayNodeNameAction.setCheckable(True)

        self.displayRedundantComputesAction.setChecked(True)
        self.displayPercentsAction.setChecked(True)
        self.displayCountAction.setChecked(True)
        self.displayTimeAction.setChecked(True)
        self.displayNodeTypeAction.setChecked(True)
        self.displayNodeNameAction.setChecked(True)

        self.displayRedundantComputesAction.toggled.connect(self._toggleDisplayOfColumn0_)
        self.displayPercentsAction.toggled.connect(self._toggleDisplayOfColumn1_)
        self.displayCountAction.toggled.connect(self._toggleDisplayOfColumn2_)
        self.displayTimeAction.toggled.connect(self._toggleDisplayOfColumn3_)
        self.displayNodeTypeAction.toggled.connect(self._toggleDisplayOfColumn4_)
        self.displayNodeNameAction.toggled.connect(self._toggleDisplayOfColumn5_)

        self.menu.addAction(self.displayRedundantComputesAction)
        self.menu.addAction(self.displayPercentsAction)
        self.menu.addAction(self.displayCountAction)
        self.menu.addAction(self.displayTimeAction)
        self.menu.addAction(self.displayNodeTypeAction)
        self.menu.addAction(self.displayNodeNameAction)

        # Find Node Action
        findNodeAction = QtWidgets.QAction('Find Node', self)
        findNodeAction.setShortcut('F')
        findNodeAction.setStatusTip('Finds a node in the list')
        findNodeAction.triggered.connect(self.findNode)
        self.addAction(findNodeAction)

    def _toggleDisplayOfColumn0_(self, state):
        self.toggleDisplayOfColumn(0, state)

    def _toggleDisplayOfColumn1_(self, state):
        self.toggleDisplayOfColumn(1, state)

    def _toggleDisplayOfColumn2_(self, state):
        self.toggleDisplayOfColumn(2, state)

    def _toggleDisplayOfColumn3_(self, state):
        self.toggleDisplayOfColumn(3, state)

    def _toggleDisplayOfColumn4_(self, state):
        self.toggleDisplayOfColumn(4, state)

    def _toggleDisplayOfColumn5_(self, state):
        self.toggleDisplayOfColumn(5, state)

    def toggleDisplayOfColumn(self, column, state):
        if state:
            self.timesTabelView.showColumn(column)
        else:
            self.timesTabelView.hideColumn(column)

    def findNode(self):
        """when user hits f on keyboard, will frame the node in the timer list if it exists in list
        """

        selection = pymel.ls(selection=True)
        if selection:
            selection = selection[-1]
            selection = selection.nodeName()

            dataModel = self.stopwatchDataModel_times
            if selection not in dataModel.data_nodeNames:
                raise Warning('selected node: %s not found in timer list' % selection)

            else:
                index = dataModel.data_nodeNames.index(selection)
                sortedIndex = dataModel.indexOrder[index]

                dataModel = self.timesTabelView.model()
                selectionModel = self.timesTabelView.selectionModel()
                qIndex = dataModel.index(sortedIndex, 4)
                self.timesTabelView.scrollTo(qIndex)

                for i in range(5):
                    qIndex = dataModel.index(sortedIndex, i)
                    selectionModel.setCurrentIndex(qIndex, QtWidgets.QItemSelectionModel.Select)


    def loadFile(self, filePath):
        dataDir = os.path.abspath(os.path.join(os.path.dirname(filePath), 'data'))

        self.stopwatchDataModel_times.loadData(dataDir)
        self.timesTabelView.resizeRowsToContents()

        nrows = len(self.stopwatchDataModel_times.data_nodeNames)
        for row in xrange(nrows):
            self.timesTabelView.setRowHeight(row, 14)

        self._file = filePath

        # load tracer data
        self.traceData_traceBranchesFilePath = os.path.join(dataDir, 'traceData_traceBranches.txt')
        self.traceData_branchesOfNodesFilePath = os.path.join(dataDir, 'traceData_branchesOfNodes.txt')

    def contextMenuEvent(self, event):
        self.menu.popup(QtGui.QCursor.pos())

    def getPrefDict(self):
        prefDict = {'displayColumn0':self.timesTabelView.isColumnHidden(0),
                    'displayColumn1':self.timesTabelView.isColumnHidden(1),
                    'displayColumn2':self.timesTabelView.isColumnHidden(2),
                    'displayColumn3':self.timesTabelView.isColumnHidden(3),
                    'displayColumn4':self.timesTabelView.isColumnHidden(4),
                    'displayColumn5':self.timesTabelView.isColumnHidden(5),
                   }

        return prefDict

    def setPrefsFromDict(self, prefDict):
        actions = (self.displayPercentsAction,
                   self.displayCountAction,
                   self.displayTimeAction,
                   self.displayNodeTypeAction,
                   self.displayNodeNameAction,
                   self.displayRedundantComputesAction,
                  )

        for i in range(6):
            key = 'displayColumn%s' % str(i)
            if key in prefDict:
                currentState = self.timesTabelView.isColumnHidden(i)
                if currentState != prefDict[key]:
                    actions[i].toggle()



class StopwatchDataWidget_traces(QtWidgets.QWidget):
    colorValues = {'compute':(64,12,4),
                   'draw':(0,59,76),
                   'dirty':(79,26,75),
                   'callback':(55,44,22),
                   'fetch':(10,58,10),
                   }

    selectedColorValues = {'compute':(64,12,4),
                   'draw':(0,59,76),
                   'dirty':(79,26,75),
                   'callback':(55,44,22),
                   'fetch':(10,58,10),
                   }

    def __init__(self, **kwargs):
        super(StopwatchDataWidget_traces, self).__init__(**kwargs)

        self.selectedNode = None
        self.dataDir = None
        self.traceData_branchesOfNodesFilePath = None
        self.traceData_traceBranchesFilePath = None

        # create Layout
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(QtCore.QMargins(0,0,0,0))
        layout.setSpacing(0)
        self.setLayout(layout)

        # create top bottom splitter
        self.layout = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        layout.addWidget(self.layout)

        # create metric top List Splitter
        metricSplitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self.layout.addWidget(metricSplitter)

        # create metric vertical (1 item) splitter 0
        metricSplitter0 = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        metricSplitter.addWidget(metricSplitter0)

        # create metric vertical (5 item) splitter 1
        metricSplitter1 = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        metricSplitter.addWidget(metricSplitter1)

        # all metric list
        self.allList = QtWidgets.QTreeView()
        self.allList.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

        self.allListData = QtWidgets.QStandardItemModel()
        self.allList.setModel(self.allListData)
        self.allListData.setHorizontalHeaderLabels(['All Processes'])

        self.allListSelectionModel = self.allList.selectionModel()
        self.allList.clicked.connect(self._metricListSelectionChanged_allMetric_)

        # compute metric list
        self.computeList = QtWidgets.QTreeView()
        self.computeList.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.computeList.clicked.connect(self.metricListItemSelected)

        self.computeListData = QtWidgets.QStandardItemModel()
        self.computeList.setModel(self.computeListData)
        self.computeListData.setHorizontalHeaderLabels(['compute'])

        self.computeListSelectionModel = self.computeList.selectionModel()
        #self.computeListSelectionModel.selectionChanged.connect(self._metricListSelectionChanged_computeMetric_)
        self.computeList.clicked.connect(self._metricListSelectionChanged_otherMetrics_)

        self.computeList.setStyleSheet("""
        QHeaderView {
            background-color: rgb%s;
        }
        """ % str(self.colorValues['compute']))


        # dirty metric list
        self.dirtyList = QtWidgets.QTreeView()
        self.dirtyList.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

        self.dirtyListData = QtWidgets.QStandardItemModel()
        self.dirtyList.setModel(self.dirtyListData)
        self.dirtyListData.setHorizontalHeaderLabels(['dirty'])

        self.dirtyListSelectionModel = self.dirtyList.selectionModel()
        #self.dirtyListSelectionModel.selectionChanged.connect(self._metricListSelectionChanged_dirtyMetric_)
        self.dirtyList.clicked.connect(self._metricListSelectionChanged_otherMetrics_)

        self.dirtyList.setStyleSheet("""
        QHeaderView {
            background-color: rgb%s;
        }
        """ % str(self.colorValues['dirty']))


        # fetch metric list
        self.fetchList = QtWidgets.QTreeView()
        self.fetchList.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

        self.fetchListData = QtWidgets.QStandardItemModel()
        self.fetchList.setModel(self.fetchListData)
        self.fetchListData.setHorizontalHeaderLabels(['fetch'])

        self.fetchListSelectionModel = self.fetchList.selectionModel()
        #self.fetchListSelectionModel.selectionChanged.connect(self._metricListSelectionChanged_fetchMetric_)
        self.fetchList.clicked.connect(self._metricListSelectionChanged_otherMetrics_)

        self.fetchList.setStyleSheet("""
        QHeaderView {
            background-color: rgb%s;
        }
        """ % str(self.colorValues['fetch']))


        # draw metric list
        self.drawList = QtWidgets.QTreeView()
        self.drawList.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

        self.drawListData = QtWidgets.QStandardItemModel()
        self.drawList.setModel(self.drawListData)
        self.drawListData.setHorizontalHeaderLabels(['draw'])

        self.drawListSelectionModel = self.drawList.selectionModel()
        #self.drawListSelectionModel.selectionChanged.connect(self._metricListSelectionChanged_drawMetric_)
        self.drawList.clicked.connect(self._metricListSelectionChanged_otherMetrics_)

        self.drawList.setStyleSheet("""
        QHeaderView {
            background-color: rgb%s;
        }
        """ % str(self.colorValues['draw']))


        # draw callback list
        self.callbackList = QtWidgets.QTreeView()
        self.callbackList.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

        self.callbackListData = QtWidgets.QStandardItemModel()
        self.callbackList.setModel(self.callbackListData)
        self.callbackListData.setHorizontalHeaderLabels(['callback'])

        self.callbackListSelectionModel = self.callbackList.selectionModel()
        #self.callbackListSelectionModel.selectionChanged.connect(self._metricListSelectionChanged_callbackMetric_)
        self.callbackList.clicked.connect(self._metricListSelectionChanged_otherMetrics_)

        self.callbackList.setStyleSheet("""
        QHeaderView {
            background-color: rgb%s;
        }
        """ % str(self.colorValues['callback']))


        # add metric lists to splitter
        metricSplitter0.addWidget(self.allList)

        metricSplitter1.addWidget(self.computeList)
        metricSplitter1.addWidget(self.drawList)
        metricSplitter1.addWidget(self.dirtyList)
        metricSplitter1.addWidget(self.fetchList)
        metricSplitter1.addWidget(self.callbackList)


        # create trace tree
        self.traceTreeView = QtWidgets.QTreeView()
        self.layout.addWidget(self.traceTreeView)
        self.traceTreeView.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        header = self.traceTreeView.header()
        header.setStretchLastSection(False)
        self.traceTreeView.header().setStretchLastSection(True)

        # create and add data model
        self.traceData = QtWidgets.QStandardItemModel()
        self.traceTreeView.setModel(self.traceData)
        self.traceData.setHorizontalHeaderLabels(['Trace Data Tree'])



    def loadFile(self, filePath):
        dataDir = os.path.join(os.path.dirname(filePath), 'data')
        self.dataDir = dataDir
        self.traceData_branchesOfNodesFilePath = os.path.join(dataDir, 'traceData_branchesOfNodes.txt')
        self.traceData_traceBranchesFilePath = os.path.join(dataDir, 'traceData_traceBranches.txt')

    def _loadDirtyListForGivenNode_(self, node, nodeIndex=None):
        self.selectedNode = node

    def _loadTracerTreeForGivenNode_(self, node, nodeIndex=None):
        self.selectedNode = node

        # get branch numbers
        branchNumbers = []
        with open(self.traceData_branchesOfNodesFilePath, 'r') as f:
            for i, line in enumerate(f):
                if i == nodeIndex:
                    numberStrings = line[:-1].split(',')
                    for numberString in numberStrings:
                        if numberString:
                            iB = int(numberString)
                            branchNumbers.append(iB)

        # clear metric lists
        for metricTreeData in (self.allListData,
                               self.computeListData,
                               self.dirtyListData,
                               self.fetchListData,
                               self.drawListData,
                               self.callbackListData,):
            invisibleRootItem = metricTreeData.invisibleRootItem()
            invisibleRootItem.removeRows(0, invisibleRootItem.rowCount())


        # clear tree
        rootItem = self.traceData.invisibleRootItem()
        self.currentTreeItem = rootItem
        self.currentTreeLevel = 0
        self.currentTreeItemStack = []
        rootItem.removeRows(0, rootItem.rowCount())

        # itterate branches file, and create tree items base on it's contents
        #branchesFilePath = self.traceData_traceBranchesFilePath = os.path.join(dataDir, 'traceData_branchesOfNodes.txt')
        with open(self.traceData_traceBranchesFilePath, 'r') as f:
            branchStarted = False
            for i, line in enumerate(f):
                # if branch started look for end of branch
                if branchStarted:
                    if line[0] == '0':
                        branchStarted = False

                    # this is a part of a branch, create tree item for it
                    else:
                        item = self.createTreeItemFromLine(line[:-1])    # remove \n from line


                # if branch has not been started, look for the beginning
                # if this is a begining of a branch, create a tree item
                if i in branchNumbers:
                    branchStarted = True
                    item = self.createTreeItemFromLine(line[:-1])    # remove \n from line

        self.traceTreeView.expandAll()

        # reset variables to free up memory
        self.currentTreeItem = None
        self.currentTreeLevel = None
        self.currentTreeItemStack = None

        # add a count to the headers to indicate how many of each metric
        # this node has
        self.allListData.setHorizontalHeaderLabels(['All Processes (%s)' % str(self.allListData.rowCount())])
        self.computeListData.setHorizontalHeaderLabels(['compute (%s)' % str(self.computeListData.rowCount())])
        self.dirtyListData.setHorizontalHeaderLabels(['dirty (%s)' % str(self.dirtyListData.rowCount())])
        self.fetchListData.setHorizontalHeaderLabels(['fetch (%s)' % str(self.fetchListData.rowCount())])
        self.drawListData.setHorizontalHeaderLabels(['draw (%s)' % str(self.drawListData.rowCount())])
        self.callbackListData.setHorizontalHeaderLabels(['callback (%s)' % str(self.callbackListData.rowCount())])


        # resizes
        self.traceTreeView.resizeColumnToContents(0)

        sizeHints = []
        for widget in (self.computeList,
                       self.drawList,
                       self.dirtyList,
                       self.fetchList,
                       self.callbackList,
                       ):
            sizeHint = widget.sizeHintForRow(0)
            #sizeHint = widget.indexRowSizeHint(widget.rootIndex())
            #sizeHint = widget.sizeHint()
            #sizeHints.append(sizeHint.height())
            sizeHints.append(sizeHint)


    def createTreeItemFromLine(self, line):
        lineSplit = line.split()

        # create a label
        level = int(lineSplit[0])
        metric = lineSplit[1]
        node = lineSplit[2]
        data = lineSplit[3]

        labelParts = []

        # add node to label
        if node not in data and node != '-':
            labelParts.append(node)

        # add data to label
        if metric == 'draw':
            pass

        else:
            if '.' in data:
                dataSplit = data.split('.')
                #dataSplit[1] = '<span style="color:#088A08;">%s</span>'
                #dataSplit[1] = '%s' % dataSplit[1]
                labelParts.append('.'.join(dataSplit))
            else:
                labelParts.append(data)

        label = '%s' % (' - '.join(labelParts))

        item = QtWidgets.QStandardItem(label)


        # apply colors
        if node == self.selectedNode:
            textColor = QtGui.QColor(0,255,255)
        else:
            textColor = QtGui.QColor(255,255,255)

        backgroundColor, selectedBackgroundColor = self.getColorForMetric(metric)

        brush = QtGui.QBrush()
        brush.setColor(backgroundColor)
        brush.setStyle(QtCore.Qt.SolidPattern)

        selectedBrush = QtGui.QBrush()
        selectedBrush.setColor(selectedBackgroundColor)
        selectedBrush.setStyle(QtCore.Qt.SolidPattern)

        textBrush = QtGui.QBrush()
        textBrush.setColor(textColor)

        font = QtGui.QFont()
        if node == self.selectedNode:
            font.setBold(True)
            font.setItalic(True)

        font.setFamily('Courier')

        item.setData(brush, QtCore.Qt.BackgroundRole)
        item.setData(selectedBrush, QtCore.Qt.BackgroundRole)
        item.setData(textBrush, QtCore.Qt.ForegroundRole)
        item.setData(font, QtCore.Qt.FontRole)
        item.setEditable(False)

        # do parenting
        # if item is root of a tree
        if level == 0:
            self.traceData.invisibleRootItem().appendRow(item)
            #self.traceData.invisibleRootItem().setChild (0,0, item)

        # if item is next in the current branch
        elif level == self.currentTreeLevel:
            self.currentTreeItem.appendRow(item)
            #self.currentTreeItem.setChild (0,0, item)

        # item is a child of a previous branch
        else:
            while level < self.currentTreeLevel:
                self.currentTreeLevel -= 1
                self.currentTreeItemStack.pop()

            self.currentTreeItem = self.currentTreeItemStack[-1]
            self.currentTreeItem.appendRow(item)
            #self.currentTreeItem.setChild (0,0, item)

        # finish adding
        self.currentTreeItem = item
        self.currentTreeLevel += 1
        self.currentTreeItemStack.append(item)

        # add to the metric lists
        if node == self.selectedNode:
            if metric == 'compute':
                rootItem = self.computeListData.invisibleRootItem()
                metricView = self.computeList

            elif metric == 'dirty':
                rootItem = self.dirtyListData.invisibleRootItem()
                metricView = self.dirtyList

            elif metric == 'fetch':
                rootItem = self.fetchListData.invisibleRootItem()
                metricView = self.fetchList

            elif metric == 'draw':
                rootItem = self.drawListData.invisibleRootItem()
                metricView = self.drawList

            elif metric == 'callback':
                rootItem = self.callbackListData.invisibleRootItem()
                metricView = self.callbackList

            cloneItemA = item.clone()
            cloneItemB = item.clone()

            cloneItemA.traceTreeItem = item
            cloneItemB.traceTreeItem = item

            item.allMetricItem = cloneItemA
            item.metricItem = cloneItemB
            item.metricView = metricView

            self.allListData.invisibleRootItem().appendRow(cloneItemA)
            rootItem.appendRow(cloneItemB)


        return item


    # selection changed methods ===============================================================================================
    def _metricListSelectionChanged_allMetric_(self, *args):

        allList_selectedIndices = self.allList.selectedIndexes()
        deselectList = allList_selectedIndices
        selectedList = []

        # do deselects
        for metricView in (self.computeList,
                           self.drawList,
                           self.dirtyList,
                           self.fetchList,
                           self.callbackList,
                           ):

            # deselect any items that are selected in the metric view but not the allList metricView
            selectedIndices = metricView.selectedIndexes()
            for qIndex in selectedIndices:
                item = metricView.model().itemFromIndex(qIndex)

                traceTreeItem = item.traceTreeItem
                metricItem = traceTreeItem.metricItem
                allMetricItem = traceTreeItem.allMetricItem

                allList_itemIndex = self.allListData.indexFromItem(allMetricItem)

                if allList_itemIndex not in allList_selectedIndices:
                    metricView.selectionModel().setCurrentIndex(qIndex, QtWidgets.QItemSelectionModel.Deselect)


        # do selects
        for qIndex in allList_selectedIndices:
            item = self.allListData.itemFromIndex(qIndex)

            traceTreeItem = item.traceTreeItem
            metricItem = traceTreeItem.metricItem
            metricView = traceTreeItem.metricView

            metricIndex = metricView.model().indexFromItem(metricItem)

            metricSelectedIndices = metricView.selectedIndexes()
            if metricIndex not in metricSelectedIndices:
                metricView.setCurrentIndex(metricIndex)

        self.metricListItemSelected()


    def _metricListSelectionChanged_otherMetrics_(self, *args):
        """This method links the selections make in the 5 other metic lists to that allList metric list
        """

        allList_selectedIndices = self.allList.selectedIndexes()
        deselectList = allList_selectedIndices
        selectedList = []

        for metricView in (self.computeList,
                           self.drawList,
                           self.dirtyList,
                           self.fetchList,
                           self.callbackList,
                           ):


            # select in the allList metric view, all items selected in all other metricViews
            selectedIndices = metricView.selectedIndexes()
            for qIndex in selectedIndices:
                item = metricView.model().itemFromIndex(qIndex)

                traceTreeItem = item.traceTreeItem
                allMetricItem = traceTreeItem.allMetricItem

                allList_itemIndex = self.allListData.indexFromItem(allMetricItem)


                if allList_itemIndex not in allList_selectedIndices:
                    self.allListSelectionModel.setCurrentIndex(allList_itemIndex, QtWidgets.QItemSelectionModel.Select)

                selectedList.append(allList_itemIndex)

        # deselect in the allList metric veiw all items not selected in all other metricViews
        for qIndex in deselectList:
            if qIndex not in selectedList:
                self.allListSelectionModel.setCurrentIndex(qIndex, QtWidgets.QItemSelectionModel.Deselect)

        self.metricListItemSelected()



    #def _metricListSelectionChanged_computeMetric_(self, qItemSelection, qItemDeselection):
        ##self.updateMetricSelection(self.computeList, qItemSelection, qItemDeselection)

        ## also make the selection in the other metricView that it appears in
        #selectedIndices = qItemSelection.indexes()
        #deselectedIndices = qItemDeselection.indexes()
        #newSelection = []

        #addedIndices = []
        #for qIndex in selectedIndices:
            #if qIndex not in deselectedIndices:
                #addedIndices.append(qIndex)

        #removedIndices = []
        #for qIndex in qItemDeselection:
            #if qIndex not in selectedIndices:
                #removedIndices.append(qIndex)

        ## clear lists
        ##self.computeList.clearSelection()
        ##self.dirtyList.clearSelection()
        ##self.fetchList.clearSelection()
        ##self.drawList.clearSelection()
        ##self.callbackList.clearSelection()

        ##selected_computeList = []
        ##selected_dirtyList = []
        ##selected_fetchList = []
        ##selected_drawList = []
        ##selected_callbackList = []


        #for qIndex in self.computeList.selectedIndexes():
            #item = self.computeListData.itemFromIndex(qIndex)

            #traceTreeItem = item.traceTreeItem
            #metricItem = traceTreeItem.metricItem
            ##metricView = traceTreeItem.metricView
            #metricIndex = self.allList.model().indexFromItem(metricItem)

            ##if metricView == self.computeList:
                ##selected_computeList.append(metricIndex)

            ##elif metricView == self.dirtyList:
                ##selected_dirtyList.append(metricIndex)

            ##elif metricView == self.fetchList:
                ##selected_fetchList.append(metricIndex)

            ##elif metricView == self.drawList:
                ##selected_drawList.append(metricIndex)

            ##elif metricView == self.callbackList:
                ##selected_callbackList.append(metricIndex)


            ##metricView.setCurrentIndex(metricIndex)
            #metricViewSelectedIndices = self.allList.selectedIndexes()
            #if metricIndex not in metricViewSelectedIndices:
                #self.allList.setCurrentIndex(metricIndex)

            ##self.allList.setCurrentIndex(meticIndex)



    #def _metricListSelectionChanged_dirtyMetric_(self, qItemSelection, qItemDeselection):
        #self.updateMetricSelection(self.dirtyList, qItemSelection, qItemDeselection)
        #pass
    #def _metricListSelectionChanged_fetchMetric_(self, qItemSelection, qItemDeselection):
        #self.updateMetricSelection(self.fetchList, qItemSelection, qItemDeselection)
        #pass
    #def _metricListSelectionChanged_drawMetric_(self, qItemSelection, qItemDeselection):
        #self.updateMetricSelection(self.drawList, qItemSelection, qItemDeselection)
        #pass
    #def _metricListSelectionChanged_callbackMetric_(self, qItemSelection, qItemDeselection):
        #self.updateMetricSelection(self.callbackList, qItemSelection, qItemDeselection)
        #pass


    #def updateMetricSelection(self, metricView, qItemSelection, qItemDeselection):
        #"""updates the current selection for all metricViews

        #If the selection changes in any of the metricViews, then this function updates all the metrics to
        #reflect the change.
        #"""

        #self.metricListItemSelected()


    def metricListItemSelected(self):
        #qItemSelection = self.traceTreeView.selectedIndexes()
        qItemSelection = self.allList.selectedIndexes()
        #if isinstance(qItemSelection, QtWidgets.QItemSelection):
        # convert selection from the metric list QModelIndices to treeView QModelIndices
        treeIndices = []
        for qModelIndex in qItemSelection:
            item = qModelIndex.model().item(qModelIndex.row(), qModelIndex.column())
            traceTreeIndex = self.traceData.indexFromItem(item.traceTreeItem)
            treeIndices.append(traceTreeIndex)

        self.isolateItem(treeIndices)

        if treeIndices:
            self.traceTreeView.scrollTo(treeIndices[-1])
            self.traceTreeView.setCurrentIndex(traceTreeIndex)


    def getColorForMetric(self, metric):
        """Returns background color, and selected background color
        """
        return QtGui.QColor(*self.colorValues[metric]), QtGui.QColor(*self.selectedColorValues[metric])

    def isolateItem(self, treeIndices):
        visibleIndices = []
        for qIndex in treeIndices:
            currentIndex = qIndex

            while currentIndex.isValid():
                if currentIndex not in visibleIndices:
                    visibleIndices.append(currentIndex)

                parentIndex = currentIndex.parent()
                if parentIndex.isValid():
                    parentItem = self.traceData.itemFromIndex(parentIndex)
                    currentRow = currentIndex.row()
                    for iA in range(parentItem.rowCount()):
                        rowIndex = self.traceData.index(iA, 0, parentIndex)

                        if rowIndex not in visibleIndices:
                            self.traceTreeView.setRowHidden(iA, parentIndex, True)
                        else:
                            self.traceTreeView.setRowHidden(iA, parentIndex, False)

                currentIndex = parentIndex


class StopwatchDataModel_times(QtCore.QAbstractTableModel):
    headers = ('Redun',
               'Perc',
               'Count',
               'Time',
               'NodeType',
               'Node',
              )

    def __init__(self, **kwargs):
        super(StopwatchDataModel_times, self).__init__(**kwargs)

        self.indexOrder = []
        self.data_redundancies = []
        self.data_nodeNames = []
        self.data_nodeTypes = []
        self.data_times = []
        self.data_counts = []
        self.data_percents = []

    def rowCount(self, parent):
        if self.data_nodeNames:
            return len(self.data_nodeNames)
        else:
            return 0

    def columnCount(self, parent):
        return len(self.headers)

    def headerData(self, section, orientation, role):
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                return self.headers[section]

    def sort(self, columnIndex, order):
        """Sort table by given column number.
        """
        if self.data_nodeNames:
            self.layoutAboutToBeChanged.emit()
            self.indexOrder = []

            if order == QtCore.Qt.DescendingOrder:
                reverse = True
            else:
                reverse = False

            itemTuples = []
            if columnIndex == 0:
                items = self.data_redundancies
            elif columnIndex == 1:
                items = self.data_percents
            elif columnIndex == 2:
                items = self.data_counts
            elif columnIndex == 3:
                items = self.data_times
            elif columnIndex == 4:
                items = self.data_nodeTypes
            elif columnIndex == 5:
                items = self.data_nodeNames

            for i, item in enumerate(items):
                itemTuples.append((i, item,))


            for i, percent in sorted(itemTuples, key=operator.itemgetter(1), reverse=reverse):
                self.indexOrder.append(i)

            self.layoutChanged.emit()


    def data(self, index, role):
        if role == QtCore.Qt.DisplayRole:
            if self.data_nodeNames:
                column = index.column()
                row = index.row()
                sortedIndex = self.indexOrder[row]
                if column == 0:
                    return str(self.data_redundancies[sortedIndex])
                if column == 1:
                    return str(self.data_percents[sortedIndex])
                if column == 2:
                    return str(self.data_counts[sortedIndex])
                if column == 3:
                    return str(self.data_times[sortedIndex])
                if column == 4:
                    return str(self.data_nodeTypes[sortedIndex])
                if column == 5:
                    return str(self.data_nodeNames[sortedIndex])




            else:
                return 'No timer'

    def loadData(self, dataDir):
        """
        load the output of a dgTimer operation
        """
        self.layoutAboutToBeChanged.emit()

        timeData_redundancies = os.path.join(dataDir, 'timeData_redundancies.txt')
        timeData_nodeNames = os.path.join(dataDir, 'timeData_nodeNames.txt')
        timeData_nodeTypes = os.path.join(dataDir, 'timeData_nodeTypes.txt')
        timeData_times = os.path.join(dataDir, 'timeData_times.txt')
        timeData_counts = os.path.join(dataDir, 'timeData_counts.txt')
        timeData_percents = os.path.join(dataDir, 'timeData_percents.txt')

        timeData_redundancies_file = open(timeData_redundancies, 'r')
        timeData_nodeNames_file = open(timeData_nodeNames, 'r')
        timeData_nodeTypes_file = open(timeData_nodeTypes, 'r')
        timeData_times_file = open(timeData_times, 'r')
        timeData_counts_file = open(timeData_counts, 'r')
        timeData_percents_file = open(timeData_percents, 'r')

        self.data_redundancies = []
        self.data_nodeNames = []
        self.data_nodeTypes = []
        self.data_times = []
        self.data_counts = []
        self.data_percents = []

        iB = 0
        for i, nodeName in enumerate(timeData_nodeNames_file):

            redundancies = int(timeData_redundancies_file.readline()[:-1])
            nodeName = nodeName[:-1]
            nodeType = timeData_nodeTypes_file.readline()[:-1]
            time = float(timeData_times_file.readline()[:-1])
            count = float(timeData_counts_file.readline()[:-1])
            percent = float(timeData_percents_file.readline()[:-1])

            if count >= 1.0:
                self.indexOrder.append(iB)
                self.data_redundancies.append(redundancies)
                self.data_nodeNames.append(nodeName)
                self.data_nodeTypes.append(nodeType)
                self.data_times.append(time)
                self.data_counts.append(count)
                self.data_percents.append(percent)
                iB += 1

        self.data_redundancies = tuple(self.data_redundancies)
        self.data_nodeNames = tuple(self.data_nodeNames)
        self.data_nodeTypes = tuple(self.data_nodeTypes)
        self.data_times = tuple(self.data_times)
        self.data_counts = tuple(self.data_counts)
        self.data_percents = tuple(self.data_percents)

        timeData_redundancies_file.close()
        timeData_nodeNames_file.close()
        timeData_nodeTypes_file.close()
        timeData_times_file.close()
        timeData_counts_file.close()
        timeData_percents_file.close()


        self.layoutChanged.emit()







STOPWATCH_UI = None
def openUI():
    print 'open the UIr'

    #try: STOPWATCH_UI.close()
    #except: pass

    STOPWATCH_UI = StopwatchUIWindow()
    STOPWATCH_UI.show()
