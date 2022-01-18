import os
import shutil
import pymel.core as pymel

import maya.cmds as cmds

import ka_maya.ka_python as ka_python
import ka_maya.ka_animation as ka_animation

def doStopwatchRecording(rootDir, startFrame=None, endFrame=None):

    # create root directory ----------------------------------------------------------
    if not os.path.exists(rootDir):
        os.makedirs(rootDir)

    # get output paths ---------------------------------------------------------------
    stopwatchFile = os.path.join(rootDir, 'stopwatchFile.txt')
    dataDir = os.path.join(rootDir, 'data')

    nodesOfBranchTempDir = os.path.join(dataDir, 'nodesOfBranchTempDir')

    timeData_redundancies = os.path.join(dataDir, 'timeData_redundancies.txt')
    timeData_nodeNames = os.path.join(dataDir, 'timeData_nodeNames.txt')
    timeData_nodeTypes = os.path.join(dataDir, 'timeData_nodeTypes.txt')
    timeData_times = os.path.join(dataDir, 'timeData_times.txt')
    timeData_counts = os.path.join(dataDir, 'timeData_counts.txt')
    timeData_percents = os.path.join(dataDir, 'timeData_percents.txt')

    traceData_traceBranches = os.path.join(dataDir, 'traceData_traceBranches.txt')
    traceData_branchesOfNodes = os.path.join(dataDir, 'traceData_branchesOfNodes.txt')
    traceData_metricTypes = os.path.join(dataDir, 'traceData_metricTypes.txt')
    traceData_metricInfo = os.path.join(dataDir, 'traceData_metricInfo.txt')
    traceData_nodeName = os.path.join(dataDir, 'traceData_nodeName.txt')
    traceData_times = os.path.join(dataDir, 'traceData_times.txt')

    time_raw_filePath = os.path.join(dataDir, 'time_raw.txt')
    trace_raw_filePath = os.path.join(dataDir, 'trace_raw.txt')

    # set desired frame range -------------------------------------------------------
    oldStartFrame = None
    oldEndFrame = None
    if startFrame != None:
        oldStartFrame = ka_animation.getFrameRangeStart()
        oldEndFrame = ka_animation.getFrameRangeEnd()

        ka_animation.setFrameRangeStart(startFrame)
        ka_animation.setFrameRangeEnd(endFrame)

        pymel.currentTime(startFrame)

    numOfFrames = float(endFrame-startFrame)

    # run dg timer ----------------------------------------------------------------------
    cmds.dgtimer(reset=True)
    cmds.dgtimer(reset=True, trace=True)

    cmds.dgtimer(on=True)
    cmds.dgtimer(trace=True, outputFile=trace_raw_filePath)

    cmds.play(wait=True)

    cmds.dgtimer(on=False)
    cmds.dgtimer(trace=True, outputFile='/tmp/trace.txt')
    cmds.dgtimer(query=True, outputFile=time_raw_filePath)

    os.makedirs(nodesOfBranchTempDir)


    # process timer files ---------------------------------------------------------------
    timeData_nodeNames_file = open(timeData_nodeNames, 'w')
    timeData_nodeTypes_file = open(timeData_nodeTypes, 'w')
    timeData_times_file = open(timeData_times, 'w')
    timeData_counts_file = open(timeData_counts, 'w')
    timeData_percents_file = open(timeData_percents, 'w')
    time_raw_file = open(time_raw_filePath, "r")

    branchesOfNodeDict = {}
    dataStarted = False
    dataFinished = False
    for i, line in enumerate(time_raw_file):

        if dataStarted == False:
            if line.startswith('----'):
                dataStarted = True

        elif dataStarted == True:
            if 'DELETED NODE TOTAL' in line:
                dataFinished = True
                break

            elif dataFinished == False:
                nodeTimeDataSplit = line.split()

                time = float(nodeTimeDataSplit[2]) / numOfFrames
                percent = float(nodeTimeDataSplit[3][:-1])
                count = float(nodeTimeDataSplit[6]) / numOfFrames
                nodeType = nodeTimeDataSplit[7]
                nodeName = nodeTimeDataSplit[8]

                branchesOfNodeDict[nodeName] = ''

                nodeTempPath = os.path.join(nodesOfBranchTempDir, '%s.txt' % nodeName.replace(':', '-'))
                with open(nodeTempPath, 'w') as nodeTempFile:
                    pass

                timeData_nodeNames_file.write('%s\n' % nodeName)
                timeData_nodeTypes_file.write('%s\n' % nodeType)
                timeData_times_file.write('%s\n' % str(time))
                timeData_counts_file.write('%s\n' % str(count))
                timeData_percents_file.write('%s\n' % str(percent))

    time_raw_file.close()
    timeData_nodeNames_file.close()
    timeData_nodeTypes_file.close()
    timeData_times_file.close()
    timeData_counts_file.close()
    timeData_percents_file.close()

    # process tracer files ---------------------------------------------------------------
    traceData_traceBranches_file = open(traceData_traceBranches, 'w')
    trace_raw_file = open(trace_raw_filePath, "r")

    currentLineNumber = 0
    lineStack = []
    lineIndexStack = []
    branchSubIndex = 0
    isFirstFrame = None
    for i, line in enumerate(trace_raw_file):
        # is this the second frame? if so, don't write trace info
        if 'DGpreTimeChangeMsg' in line:
            if isFirstFrame == None:
                isFirstFrame = True
            else:
                break


        lineSplit = line.split()

        if i > 50 and i < 75:
            print i, lineSplit

        # if line is a START -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -
        if line.startswith('dgtimer:begin:'):

            metric = lineSplit[1][:-1]
            data = lineSplit[4][:-1]

            if lineSplit[3] == ',':
                node = "-"
            else:
                node = "%s" % lineSplit[3][:-1]

                nodeTempPath = os.path.join(nodesOfBranchTempDir, '%s.txt' % node.replace(':', '-'))
                nodeTempLine = None
                with open(nodeTempPath, 'r') as nodeTempFile:
                    nodeTempLine = nodeTempFile.readline()

                strCurrentLineNumber = '%s,' % str(currentLineNumber)
                if strCurrentLineNumber not in nodeTempLine:
                    with open(nodeTempPath, 'a') as nodeTempFile:
                        nodeTempFile.write(strCurrentLineNumber)

            unfinishedLine = "%s %s %s" % (metric, node, data)
            lineStack.append(unfinishedLine)
            lineIndexStack.append(branchSubIndex)
            branchSubIndex += 1


        # if line is a End -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -
        elif line.startswith('dgtimer:end:'):

            level = lineSplit[2][:-1]
            selfTime = lineSplit[3][:-1]
            inclusiveTime = lineSplit[4][:-1]

            lineIndex = lineIndexStack.pop()
            unfinishedLine = lineStack[lineIndex]

            finishedLine = '%s %s %s %s\n' % (level, unfinishedLine, selfTime, inclusiveTime)

            lineStack[lineIndex] = finishedLine

            if level == '0':
                for finishedLine in lineStack:
                    traceData_traceBranches_file.write(finishedLine)
                    currentLineNumber += 1

                # reset branch variables
                lineStack = []
                branchSubIndex = 0

    currentLineNumber = None
    lineStack = None
    lineIndexStack = None
    branchSubIndex = None
    trace_raw_file.close()
    traceData_traceBranches_file.close()

    # figure out the line numbers of each branch containing each node ---------------
    traceData_branchesOfNodes_file = open(traceData_branchesOfNodes, 'w')
    timeData_nodeNames_file = open(timeData_nodeNames, 'r')

    for iA, lineA in enumerate(timeData_nodeNames_file):
        nodeName = lineA[:-1]

        nodeTempPath = os.path.join(nodesOfBranchTempDir, '%s.txt' % nodeName.replace(':', '-'))
        nodeTempLine = None
        with open(nodeTempPath, 'r') as nodeTempFile:
            nodeTempLine = nodeTempFile.readline()

        traceData_branchesOfNodes_file.write('%s\n' % nodeTempLine)



    traceData_branchesOfNodes_file.close()
    timeData_nodeNames_file.close()

    # delete the temp file ---------------------------------------------------------
    shutil.rmtree(nodesOfBranchTempDir)

    # write the stopwatch.txt file -------------------------------------------------
    with open(stopwatchFile, "w") as _file:
        _file.write("{numOfFrames:%s}" % str(numOfFrames))

    print 'stopwatch recording saved to: %s' % rootDir


    # reset the timeline framerange -------------------------------------------------
    if oldStartFrame != None:
        ka_animation.setFrameRangeStart(oldStartFrame)

    if oldEndFrame != None:
        ka_animation.setFrameRangeEnd(oldEndFrame)
