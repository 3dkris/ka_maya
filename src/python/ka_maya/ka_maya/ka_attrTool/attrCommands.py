import os
import pickle
import math
import time
import random
import string
import re

import maya.cmds as cmds
import maya.mel as mel
import pymel.core as pymel

import ka_maya.ka_python as ka_python    #;reload(ka_clipBoard)
import ka_maya.ka_clipBoard as ka_clipBoard    #;reload(ka_clipBoard)
import ka_maya.ka_preference as ka_preference    #;reload(ka_preference)
import ka_maya.ka_math as ka_math    #;reload(ka_math)
import ka_maya.ka_attrTool.attributeObj as attributeObj    #;reload(attributeObj)

attrObjectDict = {}

def inHypherShade():
    """Returns True if the user has focus on the hyperShade"""
    panels = cmds.getPanel(visiblePanels=True)
    for panelName in panels:
        if 'hyperShadePanel' in panelName:
            return True

    return False

def getNodeSelection():
    """Returns selection. If that selection exists in the hypershade, than
    it is returned acording to their height in the hypershade"""

    hyperGraph = 'graph1HyperShadeEd'

    visiblePanels = pymel.getPanel( visiblePanels=True )
    hyperShadePanel = None
    for eachPanel in visiblePanels:
        if 'hyperShadePanel' in eachPanel:
            hyperShadePanel = eachPanel
            break

    if hyperShadePanel:
        nodesInGraph = pymel.hyperGraph(hyperGraph, query=True, getNodeList=True)
        selectionInGraph = True
        selection = pymel.ls(selection=True)
        for each in selection:
            if each not in nodesInGraph:
                selectionInGraph = False
                break

        # Sort by pos Y in hypershade
        if selectionInGraph:
            if len(selection) == 1:
                return selection
            elif len(selection) == 0:
                return []

            xDict = {}
            yDict = {}
            for each in selection:
                x, y = pymel.hyperGraph(hyperGraph, getNodePosition=each, query=True, )
                xDict[x] = each
                yDict[y] = each

            sortedX = sorted(xDict)
            sortedY = sorted(yDict)
            nodeList_width = sortedX[-1]-sortedX[0]
            nodeList_height = sortedY[-1]-sortedY[0]

            if nodeList_width > nodeList_height:
                dictOfChoice = xDict
            else:
                dictOfChoice = yDict

            nodeList = []
            for key in sorted(dictOfChoice):
                nodeList.append(dictOfChoice[key])

            return nodeList

    return selection

def getNodeHypershadePosition(node):
    hyperGraph = 'graph1HyperShadeEd'
    x, y = pymel.hyperGraph(hyperGraph, getNodePosition=node, query=True, )
    return (x, y)


def addNodeToHyperShade(node):
    hyperGraph = 'graph1HyperShadeEd'
    pymel.hyperGraph(hyperGraph, addDependNode=node, edit=True, )

def getNodesInHyperShade():
    """Returns a list of nodes in the hypershade"""
    hyperGraph = 'graph1HyperShadeEd'
    return pymel.ls(pymel.hyperGraph(hyperGraph, query=True, getNodeList=True, ))

def guessNiceName(longName):
    niceName = re.sub("([a-z])([A-Z])","\g<1> \g<2>", longName)
    niceName = '%s%s' % (niceName[0].upper(), niceName[1:])
    return niceName

lastSetHypershadePosition = (0.0, 0.0)
def positionNodeInHyperShade(node, x, y):
    global lastSetHypershadePosition

    #x += random.randrange(-10, 10)
    #y += random.randrange(-10, 10)

    hyperGraph = 'graph1HyperShadeEd'
    pymel.hyperGraph(hyperGraph, setNodePosition=[node, x, y], edit=True, )

def positionNodeInbetweenNodesInHyperShade(targetNode1, targetNode2, node):
    addNodeToHyperShade(node)
    point1 = getNodeHypershadePosition(targetNode1)
    point2 = getNodeHypershadePosition(targetNode2)
    midPoint = ka_math.getMidpoint([point1, point2])
    positionNodeInHyperShade(node, midPoint[0], midPoint[1])

def storeAttrValues(attrObjs, storeConnections=True):
    values = []

    for attrObj in attrObjs:
        if attrObj.exists():
            value = attrObj.value(refresh=True)

            if storeConnections:
                inputs = attrObj.inputs(refresh=True)
                if inputs:
                    for plug in inputs:
                        value = (str(plug), str(attrObj.attr()))

        else:
            value = None

        values.append(value)

    return ka_clipBoard.add('ka_attrTool_attrValues', values)

def getAttrValues():
    return ka_clipBoard.get('ka_attrTool_attrValues',)


def copyAttrs(attrObjs, nonDefaultOnly=True, copyValues=True, copyConnections=True):
    filteredAttrObjs = []
    for node in getNodeSelection():
        for attrObj in attrObjs:
            eachAttrObj = getAsAttrObject(node, attrObj.attrLongName())

            if eachAttrObj.exists():
                if attrObj.inputs() and copyConnections:
                    filteredAttrObjs.append(eachAttrObj)

                elif nonDefaultOnly and copyValues:
                    if not eachAttrObj.isWritable():
                        filteredAttrObjs.append(eachAttrObj)

                    elif not eachAttrObj.isDefaultValue():
                        filteredAttrObjs.append(eachAttrObj)

                    elif eachAttrObj.inputs():
                        filteredAttrObjs.append(eachAttrObj)

                elif copyValues:
                    filteredAttrObjs.append(eachAttrObj)

    storeAttrValues(filteredAttrObjs, storeConnections=copyConnections)
    storeSourceAttrs(attrObjs)

def pasteAttrs(attrObjs=None):
    values = getAttrValues()

    # get source Nodes
    sourceNodes = []
    sourceAttrObjs = getSourceAttrs()
    for sourceAttrObj in sourceAttrObjs:
        if sourceAttrObj.node() not in sourceNodes:
            sourceNodes.append(sourceAttrObj.node())

    targetAttrObjs = []
    # get targetAttrs
    for node in getNodeSelection():
        if attrObjs:
            for attrObj in attrObjs:
                targetAttrObj = attributeObj.AttributeObj(node, attrObj.attrLongName())
                targetAttrObjs.append(targetAttrObj)

        else:
            sourceAttrObjs = getSourceAttrs()
            for attrObj in sourceAttrObjs:
                targetAttrObj = attributeObj.AttributeObj(node, attrObj.attrLongName())
                if targetAttrObj.exists():
                    targetAttrObjs.append(targetAttrObj)

    if len(values) != len(targetAttrObjs):
        pymel.error('The number of copied attrs (%s) is diffrent from the number of target attrs (%s). Cannot Paste Attr' % (len(values), len(targetAttrObjs)))

    for i, targetAttrObj in enumerate(targetAttrObjs):
        if isinstance(values[i], tuple):
            if isinstance(values[i][0], basestring) and isinstance(values[i][1], basestring):
                pymel.connectAttr(values[i][0], targetAttrObj.attr(), force=True)
                continue

        targetAttrObj.attr().set(values[i])

def setAttrsFromText(attrObjs, text):
        #text = inputText
        value = None
        operator = None
        if text:
            if len(text) > 2:
                if text[0:2] in ['*=', '/=', '-=', '+=',]:
                    operatorSplit = text.split('=')
                    operator = ' '.join(operatorSplit)
                    operator = 'value '+ operator

            elif 'value' in text:
                operator = text

            if value == None and operator == None:
                if text != '':
                    try: value = eval(text)
                    except:
                        ka_python.printError()
                        value = None

            if value != None:
                for node in pymel.ls(selection=True):
                    for attrObj in attrObjs:
                        eachAttrObj = getAsAttrObject(node, attrObj.attrLongName())
                        if value != eachAttrObj.value(refresh=True):
                            eachAttrObj.attr().set(value)

            elif operator != None:
                for node in pymel.ls(selection=True):
                    for attrObj in attrObjs:
                        eachAttrObj = getAsAttrObject(node, attrObj.attrLongName())

                        eachOperator = operator.replace('value', str(eachAttrObj.value(refresh=True)))

                        newValue = eval(eachOperator)

                        if isinstance(newValue, float) or isinstance(newValue, int):
                            if newValue != eachAttrObj.value(refresh=True):
                                eachAttrObj.attr.set(newValue)


def selectAttrInputsAndOutputs(attrObjs, selectInputs=True, selectOutputs=True):

    newSelection = []
    for node in getNodeSelection():
        for attrObj in attrObjs:
            #eachAttrObj = attributeObj.AttributeObj(node, attrObj.attrLongName())
            eachAttrObj = getAsAttrObject(node, attrObj.attrLongName())

            if selectInputs:
                if eachAttrObj.inputs():
                    for eachInput in eachAttrObj.inputs():
                        newSelection.append(eachInput.node())

            if selectOutputs:
                if eachAttrObj.outputs():
                    for eachOutput in eachAttrObj.outputs():
                        newSelection.append(eachOutput.node())

    pymel.select(clear=True)
    pymel.select(newSelection)


def storeSourceAttrs(attrObjs, nodes=None):
    """stores source attrs for every node. The result for tx, ty, on 2 nodes would be:
    [nodeA.tx, nodeA.ty, nodeB.tx, nodeB.ty,]
    """

    sourceAttrObjs_asStrings = []

    if not nodes:
        nodes = getNodeSelection()

    for node in nodes:
        for attrObj in attrObjs:
            sourceAttrObj_asString = (str(node), attrObj.attrLongName())
            if sourceAttrObj_asString not in sourceAttrObjs_asStrings:
                sourceAttrObjs_asStrings.append(sourceAttrObj_asString)

    return ka_clipBoard.add('ka_attrTool_sourceAttrs', sourceAttrObjs_asStrings)


def addToSourceAttrs(attrObjs, nodes=None):
    """stores source attrs for every node. The result for tx, ty, on 2 nodes would be:
    [nodeA.tx, nodeA.ty, nodeB.tx, nodeB.ty,]
    """
    sourceAttrObjs_asStrings = ka_clipBoard.get('ka_attrTool_sourceAttrs',)

    if not nodes:
        nodes = getNodeSelection()

    for node in nodes:
        for attrObj in attrObjs:
            sourceAttrObj_asString = (str(node), attrObj.attrLongName())
            if sourceAttrObj_asString not in sourceAttrObjs_asStrings:
                sourceAttrObjs_asStrings.append(sourceAttrObj_asString)

    return ka_clipBoard.add('ka_attrTool_sourceAttrs', sourceAttrObjs_asStrings)

def removeFromSourceAttrs(attrObjs, nodes=None):
    """stores source attrs for every node. The result for tx, ty, on 2 nodes would be:
    [nodeA.tx, nodeA.ty, nodeB.tx, nodeB.ty,]
    """

    sourceAttrObjs_asStrings = ka_clipBoard.get('ka_attrTool_sourceAttrs',)
    if not nodes:
        nodes = getNodeSelection()

    for node in nodes:
        for attrObj in attrObjs:
            sourceAttrObj_asString = (str(node), attrObj.attrLongName())
            if sourceAttrObj_asString in sourceAttrObjs_asStrings:
                sourceAttrObjs_asStrings.remove(sourceAttrObj_asString)

    return ka_clipBoard.add('ka_attrTool_sourceAttrs', sourceAttrObjs_asStrings)



def getSourceAttrs():
    """Returns a list of attrObjects previously stored by the storeSourceAttrs. attrObjs
    are instantiated from stored strings, so they can be of different scenes"""

    sourceAttrObjs_asStrings = ka_clipBoard.get('ka_attrTool_sourceAttrs',)
    sourceAttrObjs = []
    for nodeString, attrString in sourceAttrObjs_asStrings:
        sourceAttrObj = attributeObj.AttributeObj(nodeString, attrString)
        sourceAttrObjs.append(sourceAttrObj)

    return sourceAttrObjs

def popConnectAttrs(attrObjs, nodes=None):
    """This command wraps the connectAttrs command, except that it removes the
    sourceAttr from the clipboard after if connects"""

    connectAttrs(attrObjs, nodes=nodes)


def connectAttrs(attrObjs, nodes=None, removeFromClipboard=False):
    sourceAttrObjs = getSourceAttrs()
    if not sourceAttrObjs:
        pymel.error('no source attributes stored, cannot connect')

    targetAttrObjs = []
    if not nodes:
        nodes = getNodeSelection()

    for node in nodes:
        for attrObj in attrObjs:
            targetAttrObj = attributeObj.AttributeObj(node, attrObj.attrLongName())
            targetAttrObjs.append(targetAttrObj)

    lenOfSources = len(sourceAttrObjs)
    lenOfTargets = len(targetAttrObjs)

    # determine the list to iterate
    if lenOfSources == 1:
        iterList = targetAttrObjs
        sourceAttrObj = sourceAttrObjs[0]
        sourceAttrObjs = []

        for i in range(lenOfTargets):
            sourceAttrObjs.append(sourceAttrObj)

    elif lenOfSources == lenOfTargets:
        iterList = targetAttrObjs

    elif lenOfSources > lenOfTargets:
        iterList = targetAttrObjs

    elif lenOfSources < lenOfTargets:
        iterList = sourceAttrObjs

    # do connections
    for i, each in enumerate(iterList):
        _safeConnect(sourceAttrObjs[i], targetAttrObjs[i])

        if removeFromClipboard:
            removeFromSourceAttrs([sourceAttrObjs[i]], [sourceAttrObjs[i].node()])


def constrainNodes(attrObjs, constraintType='pointConstraint', maintainOffset=False):
    sourceNodes = []
    targetNodes = []

    sourceAttrObjs = getSourceAttrs()
    if not sourceAttrObjs:
        pymel.error('no source attributes stored, cannot connect')

    for sourceAttrObj in sourceAttrObjs:
        node = sourceAttrObj.node()
        if node not in sourceNodes:
            sourceNodes.append(node)

    for node in getNodeSelection():
        targetNodes.append(node)

    lenOfSources = len(sourceNodes)
    lenOfTargets = len(targetNodes)

    constrainCmd = getattr(pymel, constraintType)

    constraints = []
    targetSourcePairs = []

    if lenOfSources == 1:
        for i, each in enumerate(targetNodes):
            constraints.append(constrainCmd(sourceNodes[0], targetNodes[i], maintainOffset=maintainOffset))
            targetSourcePairs.append((sourceNodes[0], targetNodes[i]))

    elif lenOfSources == lenOfTargets:
        for i, each in enumerate(targetNodes):
            constraints.append(constrainCmd(sourceNodes[i], targetNodes[i], maintainOffset=maintainOffset))
            targetSourcePairs.append((sourceNodes[i], targetNodes[i]))

    elif lenOfSources > lenOfTargets:
        for i, each in enumerate(sourceAttrObjs):
            constraints.append(constrainCmd(sourceNodes[i], targetNodes[i], maintainOffset=maintainOffset))
            targetSourcePairs.append((sourceNodes[i], targetNodes[i]))

    elif lenOfSources < lenOfTargets:
        for i, each in enumerate(targetNodes):
            constraints.append(constrainCmd(sourceNodes[i],targetNodes[i],  maintainOffset=maintainOffset))
            targetSourcePairs.append((sourceNodes[i], targetNodes[i]))

    # position inbetween source and target node
    for i, constraint in enumerate(constraints):
        positionNodeInbetweenNodesInHyperShade(targetSourcePairs[i][0], targetSourcePairs[i][1], constraint)

def setDrivenKey(attrObjs, nodes=None):
    selection = pymel.ls(selection=True)

    sourceAttrObjs = getSourceAttrs()
    if not sourceAttrObjs:
        pymel.error('no source attributes stored, cannot connect')

    targetAttrObjs = []
    if not nodes:
        nodes = getNodeSelection()

    for node in nodes:
        for attrObj in attrObjs:
            targetAttrObj = attributeObj.AttributeObj(node, attrObj.attrLongName())
            targetAttrObjs.append(targetAttrObj)

    lenOfSources = len(sourceAttrObjs)
    lenOfTargets = len(targetAttrObjs)

    if lenOfSources == 1:
        for i, each in enumerate(targetAttrObjs):
            _connectWithSetDrivenKey(sourceAttrObjs[0], targetAttrObjs[i])

    elif lenOfSources == lenOfTargets:
        for i, each in enumerate(targetAttrObjs):
            _connectWithSetDrivenKey(sourceAttrObjs[i], targetAttrObjs[i])

    elif lenOfSources > lenOfTargets:
        for i, each in enumerate(sourceAttrObjs):
            _connectWithSetDrivenKey(sourceAttrObjs[i], targetAttrObjs[i])

    elif lenOfSources < lenOfTargets:
        for i, each in enumerate(targetAttrObjs):
            _connectWithSetDrivenKey(sourceAttrObjs[i], targetAttrObjs[i])

    pymel.select(selection)

def getConnections(nodes):
    connectionsDict = {}

    for node in nodes:
        attrTuples = []

        for attrTuple in node.outputs(connections=True, plugs=True,):
            attrTuples.append(attrTuple)

        for attrTuple in node.inputs(connections=True, plugs=True,):
            attrTuples.append((attrTuple[1], attrTuple[0]))

        for attrTuple in attrTuples:
            sourceAttrObj = getAsAttrObject(attrTuple[0].node(), attrTuple[0].name(includeNode=False, longName=True, fullAttrPath=True, placeHolderIndices=True))
            destinationAttrObj = getAsAttrObject(attrTuple[1].node(), attrTuple[1].name(includeNode=False, longName=True, fullAttrPath=True, placeHolderIndices=True))

            if sourceAttrObj.node() in nodes and destinationAttrObj.node() in nodes:
                connectionsDict[attrTuple[1]] = (sourceAttrObj, destinationAttrObj)

    return connectionsDict.values()

def duplicateSelection():

    #panelName = cmds.getPanel( underPointer=True )
    #duplicateInHypershade = False
    #if 'hyperShadePanel' in panelName:
        #duplicateInHypershade = True
        #nodesInHyperShade = pymel.hyperGraph('graph1HyperShadeEd', getNodeList=True, query=True, )

    duplicateInHypershade = inHypherShade()
    nodesInHyperShade = getNodesInHyperShade()

    selection = pymel.ls(selection=True)
    selectionDict = {}            # key = node, value = None
    duplicits = []
    nodeIndexDict = {}

    connectionsDict = {}     # key = inputPlug, value = outputPlug
    relationshipDict = {}    # key = node object, value = dict{'duplicatedFromNode':None, 'duplicitsOfNode':[]}

    for each in selection:
        selectionDict[each] = None

    # Duplicate Nodes
    selectedDagObjects = []
    for i, each in enumerate(selection):

        # Duplicate shape's parents, not the shapes
        redundantDuplicate = False
        if 'shape' in each.nodeType(inherited=True):
            shapeParent = each.getParent()
            if shapeParent in selectionDict:
                redundantDuplicate = True
            else:
                each = shapeParent
                selectionDict[each]

        # Do the actual Duplicating
        if not redundantDuplicate:
            duplicate = pymel.duplicate(each)[0]
            duplicits.append(duplicate)
            nodeIndexDict[each] = i

            relationshipDict[each] = {'duplicitsOfNode':[duplicate], 'duplicatedFromNode':None}
            relationshipDict[duplicate] = {'duplicitsOfNode':[], 'duplicatedFromNode':each}

            if 'transform' in duplicate.nodeType(inherited=True):
                originalShapes = each.getShapes()
                duplicitShapes = duplicate.getShapes()

                # Delete non shape children of the duplicated node
                duplicitChildren = duplicate.listRelatives()
                duplicitChildren_toDelete = []
                for duplicitChild in duplicitChildren:
                    if duplicitChild not in duplicitShapes:
                        duplicitChildren_toDelete.append(duplicitChild)
                pymel.delete(duplicitChildren_toDelete)

                # record relationship data for the shapes
                for i, shape in enumerate(duplicitShapes):
                    duplicits.append(shape)
                    relationshipDict[originalShapes[i]] = {'duplicitsOfNode':[duplicitShapes[i]], 'duplicatedFromNode':None}
                    relationshipDict[duplicitShapes[i]] = {'duplicitsOfNode':[], 'duplicatedFromNode':originalShapes[i]}


    # record connections
    for i, each in enumerate(selection):
        attrTuples = []


        for attrTuple in each.outputs(connections=True, plugs=True,):
            attrTuples.append(attrTuple)
            #connectionsDict[attrTuple[1]] = attrTuple[0]

        for attrTuple in each.inputs(connections=True, plugs=True,):
            attrTuples.append((attrTuple[1], attrTuple[0]))
            #connectionsDict[attrTuple[0]] = attrTuple[1]

        for attrTuple in attrTuples:
            sourceAttrObj = getAsAttrObject(attrTuple[0].node(), attrTuple[0].name(includeNode=False, longName=True, fullAttrPath=True, placeHolderIndices=True))
            destinationAttrObj = getAsAttrObject(attrTuple[1].node(), attrTuple[1].name(includeNode=False, longName=True, fullAttrPath=True, placeHolderIndices=True))

            # if in hypershade, also connect nodes that are where not selected to the new
            # duplicated nodes, but only if the are visible in the hypershade
            if duplicateInHypershade:
                if sourceAttrObj.node() in nodesInHyperShade and destinationAttrObj.node() in nodeIndexDict:
                    connectionsDict[attrTuple[1]] = (sourceAttrObj, destinationAttrObj)


            # else, only remember connections where both nodes involved where selected
            else:
                if sourceAttrObj.node() in nodeIndexDict and destinationAttrObj.node() in nodeIndexDict:
                    connectionsDict[attrTuple[1]] = (sourceAttrObj, destinationAttrObj)

    # apply connections
    for sourceAttrObj, destinationAttrObj in connectionsDict.values():
        sourceNode = sourceAttrObj.node()
        destinationNode = destinationAttrObj.node()

        # if source was duplicated
        #if sourceNode in nodeIndexDict:
        if sourceNode in relationshipDict:
            if relationshipDict[sourceNode]['duplicitsOfNode']:
                #sourceNodeIndex = nodeIndexDict[sourceAttrObj.node()]
                #dupSourceAttrObj = getAsAttrObject(duplicits[sourceNodeIndex], sourceAttrObj.attrLongName())
                duplicateOfSource = relationshipDict[sourceNode]['duplicitsOfNode'][0]
                dupSourceAttrObj = getAsAttrObject(duplicateOfSource, sourceAttrObj.attrLongName())

        else: # use the same one
            dupSourceAttrObj = sourceAttrObj


        #if destinationAttrObj.node() in nodeIndexDict:
        if destinationNode in relationshipDict:
            if relationshipDict[destinationNode]['duplicitsOfNode']:
                #destinationNodeIndex = nodeIndexDict[destinationAttrObj.node()]
                duplicateOfDestination = relationshipDict[destinationNode]['duplicitsOfNode'][0]
                dupDestinationAttrObj = getAsAttrObject(duplicateOfDestination, destinationAttrObj.attrLongName())

        else: # use the same one
            dupDestinationAttrObj = destinationAttrObj


        dupSourceAttrObj.attr() >> dupDestinationAttrObj.attr()


    # reposition Nodes in hypershade
    if inHypherShade:
        nodesInHyperShade = getNodesInHyperShade()

        selectionPositionDict = {}
        for each in selection:
            if each in nodesInHyperShade:
                selectionPositionDict[each] = getNodeHypershadePosition(each)
                duplicitNode = relationshipDict[each]['duplicitsOfNode'][0]
                if duplicitNode not in nodesInHyperShade:
                    print 'duplicitNode:',
                    print duplicitNode

                    addNodeToHyperShade(duplicitNode)
                positionNodeInHyperShade(duplicitNode, selectionPositionDict[each][0] + 160, selectionPositionDict[each][1] - 180)

        #for i, each in enumerate(duplicits):
            #positionNodeInHyperShade(each, selectionPositionDict[selection[i]][0] + 160, selectionPositionDict[selection[i]][1] - 180)


    # reparent duplicated items
    for duplicate in duplicits:
        nodeTypes = duplicate.nodeType(inherited=True)
        if 'transform' in nodeTypes:
            originalNode = relationshipDict[duplicate]['duplicatedFromNode']
            originalParent = originalNode.getParent()

            if originalParent in relationshipDict:
                duplicitsOfParent = relationshipDict[originalParent]['duplicitsOfNode']
                if duplicitsOfParent:
                    pymel.parent(duplicate, duplicitsOfParent[0])


    pymel.select(duplicits)
    return duplicits


def substituteNode(originalNode=None, substituteNode=None, nodes=None):
    selection = pymel.ls(selection=True)

    if not originalNode:
        originalNode = selection[0]

    if not substituteNode:
        substituteNode = selection[1]

    if not nodes:
        nodes = selection[2:]

    connections = getConnections(selection)
    for sourceAttrObj, destinationAttrObj in connections:

        if sourceAttrObj.node() == originalNode:
            substituteAttrObj = getAsAttrObject(substituteNode, sourceAttrObj.attrLongName())
            substituteAttrObj.attr() >> destinationAttrObj.attr()

        elif destinationAttrObj.node() == originalNode:
            substituteAttrObj = getAsAttrObject(substituteNode, destinationAttrObj.attrLongName())
            sourceAttrObj.attr() >> substituteAttrObj.attr()


def disconnectAttrs(attrObjs):
    for node in getNodeSelection():
        for attrObj in attrObjs:
            eachAttrObj = attributeObj.AttributeObj(node, attrObj.attrLongName())
            _safeDisconnect(eachAttrObj)


def _safeDisconnect(attrObj):
    """does a connection from source to target, with added fail safty"""
    value = None
    try:
        value = attrObj.value()
    except: pass

    attrObj.attr().disconnect()

    if value != None:
        try: attrObj.attr().set(value)
        except: pass


def _connectWithSetDrivenKey(sourceAttrObj, targetAttrObj):
    if targetAttrObj.isMulti():
        pymel.error()

    curveType = 'animCurveUU'
    typeLower = targetAttrObj.attrType().lower()
    if 'angle' in typeLower:
        curveType = 'animCurveUA'
    elif 'linear' in typeLower:
        curveType = 'animCurveUL'
    elif 'time' in typeLower:
        curveType = 'animCurveUT'

    keyframe = pymel.createNode(curveType)
    keyframe.rename('%s_%s' % (targetAttrObj.nodeName(), targetAttrObj.attrName()))
    #pymel.setKeyframe(keyframe, insert=True, float=0)
    #pymel.setKeyframe(keyframe, insert=True, float=1)
    #pymel.keyframe(keyframe, index=1, absolute=True, valueChange=1)
    #pymel.keyTangent(keyframe, index=(0, 1), inTangentType='spline', outTangentType='spline')

    pymel.setKeyframe(keyframe, insert=True, float=sourceAttrObj.value(refresh=True))
    #pymel.setKeyframe(keyframe, insert=True, float=sourceAttrObj.value()+1)
    pymel.keyframe(keyframe, index=0, absolute=True, valueChange=targetAttrObj.value(refresh=True))
    #pymel.keyframe(keyframe, index=1, absolute=True, valueChange=targetAttrObj.value())
    #pymel.keyTangent(keyframe, index=(0, 1), inTangentType='spline', outTangentType='spline')
    pymel.keyTangent(keyframe, index=(0), inTangentType='spline', outTangentType='spline')

    sourceAttrObj.attr() >> keyframe.input

    keyframeOutputAttrObj = getAsAttrObject(keyframe, 'output')
    _safeConnect(keyframeOutputAttrObj, targetAttrObj)

    if inHypherShade():
        positionNodeInbetweenNodesInHyperShade(sourceAttrObj.node(), targetAttrObj.node(), keyframe)

def _safeConnect(sourceAttrObj, targetAttrObj):
    """does a connection from source to target, with added fail safty"""
    eccoCommands = ka_preference.get('echoCommands', False)


    sourceAttrObj.attr() >> targetAttrObj.attr()

    if eccoCommands:
        print """cmds.connectAttr('%s.%s', '%s.%s')""" % (str(sourceAttrObj.node()), sourceAttrObj.attrLongName(), str(targetAttrObj.node()), targetAttrObj.attrLongName(), )


def baseconvert(n, base):
    """convert positive decimal integer n to equivalent in another base (2-36)"""

    digits = "0123456789abcdefghijklmnopqrstuvwxyz"

    try:
        n = int(n)
        base = int(base)
    except:
        return ""

    if n < 0 or base < 2 or base > 36:
        return ""

    s = ""
    while 1:
        r = n % base
        s = digits[r] + s
        n = n / base
        if n == 0:
            break

    return s

def getHashEncodedNodeName(node):
    return '%s__%s__' % (node.nodeName(), baseconvert(str(node.__hash__()), 36))




def _getEccoSetAttrException(attrObj, mode='pymel_objects'):
    setAttrExceptionsDict = {
    'animCurveUU':{'keyTime':_eccoSetAttrException_animCurve_keyTime,
                   'keyValue':None,
                  },
    'animCurveUA':{'keyTime':_eccoSetAttrException_animCurve_keyTime,
                   'keyValue':None,
                  },
    'animCurveUL':{'keyTime':_eccoSetAttrException_animCurve_keyTime,
                   'keyValue':None,
                  },
    'animCurveUT':{'keyTime':_eccoSetAttrException_animCurve_keyTime,
                   'keyValue':None,
                  },
    'animCurveTU':{'keyTime':_eccoSetAttrException_animCurve_keyTime,
                   'keyValue':None,
                  },
    'animCurveTA':{'keyTime':_eccoSetAttrException_animCurve_keyTime,
                   'keyValue':None,
                  },
    'animCurveTL':{'keyTime':_eccoSetAttrException_animCurve_keyTime,
                   'keyValue':None,
                  },
    'animCurveTT':{'keyTime':_eccoSetAttrException_animCurve_keyTime,
                   'keyValue':None,
                  },

    'dagNode':{'boundingBox':None,
               'boundingBoxMin':None,
               'boundingBoxMinX':None,
               'boundingBoxMinY':None,
               'boundingBoxMinZ':None,
               'boundingBoxMax':None,
               'boundingBoxMaxX':None,
               'boundingBoxMaxY':None,
               'boundingBoxMaxZ':None,
               'boundingBoxSize':None,
               'boundingBoxSizeX':None,
               'boundingBoxSizeY':None,
               'boundingBoxSizeZ':None,

              },

    'allNodes':{'output':None,
                'outputX':None,
                'outputY':None,
                'outputZ':None,
                'outputR':None,
                'outputG':None,
                'outputB':None,
                'outColor':None,
                'outColorR':None,
                'outColorG':None,
                'outColorB':None,
                'outAlpha':None,
                'colorOut':None,
                'colorOutR':None,
                'colorOutG':None,
                'colorOutB':None,
                'outputColor':None,
                'outputColorR':None,
                'outputColorG':None,
                'outputColorB':None,
               }

    }

    nodeTypes = attrObj.nodeTypes()
    attrName = attrObj.attrName()
    function = None
    functionFound = False

    for nodeType in nodeTypes:
        if nodeType in setAttrExceptionsDict:
            if attrName in setAttrExceptionsDict[nodeType]:
                function = setAttrExceptionsDict[nodeType][attrName]
                functionFound = True

    if setAttrExceptionsDict['allNodes'].has_key(attrName):
        if setAttrExceptionsDict['allNodes'].has_key(attrName):
            function = setAttrExceptionsDict['allNodes'][attrName]
            functionFound = True

    if functionFound:
        if function:
            return function(attrObj, mode=mode)
        else:
            # if it has a key, and that key is None, then it is an
            # indication to skip that attribute
            return True

    return False


def _eccoSetAttrException_animCurve_keyTime(attrObj, mode='pymel_objects'):

    node = attrObj.node()
    attrLongName = attrObj.attrLongName()

    # keyValue Attr
    keyValueAttrName = attrLongName.split('.')[:-1]
    keyValueAttrName.append('keyValue')
    keyValueAttrName = '.'.join(keyValueAttrName)

    keyValueAttr = getAsAttrObject(node, keyValueAttrName)
    index = keyValueAttr.attr().parent().index()
    inTangentType = pymel.keyTangent(node, q=True, index=(index,), inTangentType=True)
    outTangentType = pymel.keyTangent(node, q=True, index=(index,), outTangentType=True)

    kwargsString = "value=%s, float=%s" % (str(keyValueAttr.value(refresh=True)), str(attrObj.value(refresh=True)),)

    if mode == 'pymel_objects':
        return "pymel.setKeyframe(%s, %s)\n" % (getHashEncodedNodeName(node), kwargsString)

    elif mode == 'pymel_commands':
        return "pymel.setKeyframe(%s, %s,)\n" % (getHashEncodedNodeName(node), kwargsString)

    elif mode == 'cmds_commands':
        return 'cmds.setKeyframe(%s, %s,)\n' % (str(node), kwargsString)


def eccoAttrs(nodes=None, attrObjs=None, mode='pymel_objects', echoAll=True,
                                 createNode=False, echoConnections=False, skipExternalConnections=True, echoSetAttrs=False, nonDefaultsOnly=True,
                                 limitToHypershadeWorkspace=False):

    """Returns a string that can be evaluated to recreate the given nodes, with their attribute settings, and
    connections. Can Return 3 modes, maya.cmds, pymel, or object oriented pymel

    Kwargs:
        nodes - list of nodes - if passed in, will return ecco for those nodes, otherwise it will use selection

        attrObjs - list of attrObjs - if passed then ecco will only be preformed on those attributes

        mode - string - determins if the return should be in regular maya commands, or pymel commands or object oriented
                               pymel. Valid values are 'pymel_objects', 'pymel_commands' or 'cmds_commands'

        createNode -

    """



    if echoAll:
        echoConnections=True
        echoSetAttrs=True
        createNode = True

    connectionStrings = ''
    setAttrStrings = ''
    createNodeString = ''
    addAttrStrings = ''

    createdNodes = []
    releventNonCreatedNodes = []  # ie, an incommingConnection is recieved from node, but node is not created
    releventNonCreatedNodesString = ''

    if nodes == None:
        nodes = pymel.ls(selection=True)
    createdNodes = []

    def getVarName(node):
        if node not in createdNodes:
            if node not in releventNonCreatedNodes:
                releventNonCreatedNodes.append(node)

        #return getHashEncodedNodeName(node)
        return str(node)

    ## CREATE NODES
    nodesToCreateStack = []
    nodeParentDict = {}
    if createNode:
        for node in nodes:
            if node.canBeWritten():
                if 'dagNode' in node.nodeType(inherited=True):
                    parent = node.getParent()
                    if parent:
                        if parent not in nodes:
                            parentVarName = getVarName(parent) # adds to releventNonCreatedNodes list

                    nodeParentDict[node] = node.getParent()
                    nodesToCreateStack.append(node)

                else:
                    nodeParentDict[node] = None
                    nodesToCreateStack.append(node)

    nodesToCreate = []
    whileCount = 0
    whileMax = 200
    # order create nodes so that their parent is created first, so that they can be created as a child
    while nodesToCreateStack:
        node = nodesToCreateStack.pop(0)
        nodeParent = nodeParentDict[node]

        if not nodeParent or nodeParent in nodesToCreate or nodeParent in releventNonCreatedNodes:
            nodesToCreate.append(node)

        else:
            nodesToCreateStack.append(node)

        whileCount += 1
        if whileCount >= whileMax:
            pymel.error('whileMax reached')


    for node in nodesToCreate:
        nodeVarName = getVarName(node)
        argsString = "'%s', " % node.nodeType()
        kwargsString = ''

        if 'dagNode' in node.nodeType(inherited=True):
            parent = node.getParent()
            if parent:
                if mode == 'pymel_objects':
                    kwargsString += "parent=%s,  " % getVarName(parent)
                else:
                    kwargsString += "parent='%s', " % str(parent)

        if mode == 'pymel_objects':
            createNodeString += """%s = pymel.createNode(%s).rename('%s')\n""" % (nodeVarName, argsString+kwargsString, node.nodeName())

        elif mode == 'pymel_commands':
            createNodeString += """%s = pymel.createNode(%s).rename('%s')\n""" % (nodeVarName, argsString+kwargsString, node.nodeName())

        elif mode == 'cmds_commands':
            kwargsString += "name='%s', " % str(node)
            createNodeString += """%s = cmds.createNode(%s)\n""" % (nodeVarName, argsString+kwargsString)

        createdNodes.append(node)


    ## SET ATTRS
    attrFavoritesDict = ka_preference.get('attrFavorites', {})
    for node in nodes:
        nodeType = node.nodeType()
        nodeVarName = getVarName(node)
        setAttrStringsAddition = ''
        addAttrStringsAddition = ''

        attrs = []
        usedAttrs = {}
        standardAttrs = pymel.listAttr(node, hasData=True, userDefined=False, visible=True)

        # always include userDefined
        userDefinedAttrs = pymel.listAttr(node, userDefined=True, settable=True)

        for attr in standardAttrs+userDefinedAttrs:
            if attr not in usedAttrs:
                usedAttrs[attr] = None
                attrs.append(attr)

        tripleAttrs = []
        if attrs:
            for attrObj in listRelevantAttrs(node, baseAttributes=attrs):

                if attrObj.isSimple() or attrObj.isTriple():
                    if not attrObj.isDefaultValue() and not attrObj.attrParentLongName() in tripleAttrs:
                        value = attrObj.value(refresh=True)
                        if value != None:

                            if isinstance(value, basestring):
                                value = '\'%s\'' % value

                            elif attrObj.isTriple():
                                tripleAttrs.append(attrObj.attrLongName())
                                value = '%s, %s, %s' % (value[0], value[1], value[2], )

                            argsString = ''

                            keyable = attrObj.isKeyable()
                            channelBox = attrObj.isInChannelBox()
                            locked = attrObj.isLocked()

                            kwargsString = ''

                            if keyable:
                                kwargsString += ' k=%s' % str(keyable)

                            if not keyable and channelBox:
                                kwargsString += ' k=False, cb=%s,' % str(channelBox)

                            if locked:
                                kwargsString += ' lock=%s, ' % str(locked)

                            if mode == 'cmds_commands':
                                if not attrObj.isNumeric():
                                    kwargsString += "type='%s', " % attrObj.attrType()

                            # find out if this attribute is execptional
                            exceptionSetAttrString = _getEccoSetAttrException(attrObj, mode=mode)
                            if exceptionSetAttrString:
                                if isinstance(exceptionSetAttrString, basestring):
                                    setAttrStringsAddition += exceptionSetAttrString


                            else:
                                if mode == 'pymel_objects':
                                    argsString = '%s,' % str(value)
                                    setAttrStringsAddition += '%s.%s.set(%s)\n' % (getVarName(node), attrObj.attrLongName(), argsString+kwargsString)

                                elif mode == 'pymel_commands':
                                    argsString = '%s.%s, %s,' % (nodeVarName, attrObj.attrLongName(), str(value))
                                    setAttrStringsAddition += 'pymel.setAttr(%s)\n' % (argsString+kwargsString)

                                elif mode == 'cmds_commands':
                                    argsString = "%s+'.%s', %s," % (nodeVarName, attrObj.attrLongName(), str(value))
                                    setAttrStringsAddition += 'cmds.setAttr(%s)\n' % (argsString+kwargsString)

        if setAttrStringsAddition:
            setAttrStrings += setAttrStringsAddition+'\n'


        # ADD ATTRS
        for attrName in userDefinedAttrs:
            attrObj = getAsAttrObject(node, attrName)
            if attrObj.isAttributeType():
                plugType = 'at'

            elif attrObj.isDataType():
                plugType = 'dt'

            attrLongName = attrObj.attrLongName()
            attrShortName = attrObj.attrShortName()
            attrNiceName = attrObj.attrNiceName()
            attrNiceNameGuess = guessNiceName(attrLongName)

            kwargsString = ''
            if mode != 'pymel_objects':
                kwargsString += "longName='%s', " % attrLongName
            kwargsString +=  "%s='%s', " % (plugType, attrObj.attrType())

            if attrShortName != attrLongName:
                kwargsString += "shortName='%s', " % attrShortName

            if attrNiceName != attrNiceNameGuess:
                kwargsString += "niceName='%s', " % attrNiceName

            minValue = attrObj.attr().getMin()
            if minValue != None:
                kwargsString += 'hasMinValue=True, '
                kwargsString += 'minValue=%s, ' % str(minValue)

            maxValue = attrObj.attr().getMax()
            if maxValue != None:
                kwargsString += 'hasMaxValue=True, '
                kwargsString += 'maxValue=%s, ' % str(maxValue)

            softMinValue = attrObj.attr().getSoftMin()
            if softMinValue != None:
                kwargsString += 'hasSoftMinValue=True, '
                kwargsString += 'softMinValue=%s, ' % str(softMinValue)

            softMaxValue = attrObj.attr().getSoftMax()
            if softMaxValue != None:
                kwargsString += 'hasSoftMaxValue=True, '
                kwargsString += 'softMaxValue=%s, ' % str(softMaxValue)

            if attrObj.attrType() == 'enum':
                enumNames = pymel.attributeQuery(attrObj.attrLongName(), node=node, listEnum=True)
                if enumNames:
                    kwargsString += "enumName='%s', " % enumNames[0]

            if mode == 'pymel_objects':
                argsString = "'%s', " % attrName
                addAttrStringsAddition += "%s.addAttr(%s)\n" % (getVarName(node), argsString+kwargsString)

            elif mode == 'pymel_commands':
                argsString = "%s, " % nodeVarName
                addAttrStringsAddition += "pymel.addAttr(%s)\n" % (argsString+kwargsString)

            elif mode == 'cmds_commands':
                argsString = "%s, " % nodeVarName
                addAttrStringsAddition += 'cmds.addAttr(%s)\n' % (argsString+kwargsString)

        if addAttrStringsAddition:
            addAttrStrings += addAttrStringsAddition+'\n'

    ## CONNECT NODES
    connectionsDict = {}

    # record connections
    for i, node in enumerate(nodes):
        uniqueConnectionsDict = {}
        attrTuples = []

        #for attrTuple in node.outputs(connections=True, plugs=True,):
            #attrTuples.append(attrTuple)

        for attrTuple in node.inputs(connections=True, plugs=True, skipConversionNodes=True):
            attrTuples.append((attrTuple[1], attrTuple[0]))

        for attrTuple in attrTuples:
            sourceNode = attrTuple[0].node()
            destinationNode = attrTuple[1].node()
            sourceAttrObj = getAsAttrObject(sourceNode, attrTuple[0].name(includeNode=False, longName=True, fullAttrPath=True, placeHolderIndices=True))
            destinationAttrObj = getAsAttrObject(destinationNode, attrTuple[1].name(includeNode=False, longName=True, fullAttrPath=True, placeHolderIndices=True))

            # if in hypershade, also connect nodes that are where not selected to the new
            # duplicated nodes, but only if the are visible in the hypershade
            if limitToHypershadeWorkspace:
                nodesInHyperShade = getNodesInHyperShade()
                if sourceAttrObj.node() in nodesInHyperShade and destinationAttrObj.node() in nodesInHyperShade:
                    uniqueConnectionsDict[attrTuple[1]] = (sourceAttrObj, destinationAttrObj)

            # else if the skipExternalConnections is true, only remember connections where both nodes
            # involved where selected/input
            elif skipExternalConnections:
                if destinationAttrObj.node() in nodes:
                    uniqueConnectionsDict[attrTuple[1]] = (sourceAttrObj, destinationAttrObj)

            # else record all connections
            else:
                uniqueConnectionsDict[attrTuple[1]] = (sourceAttrObj, destinationAttrObj)

        if uniqueConnectionsDict:
            connectionsDict[node] = uniqueConnectionsDict

    # generate connection strings
    for node in connectionsDict:
        connectionRows = []
        connectionStringsAddition = ''
        connectionStringsAdditionAMaxLength = 0

        if mode == 'pymel_objects':

            for sourceAttrObj, destinationAttrObj in connectionsDict[node].values():

                connectionStringsAdditionA = '%s.%s ' % (getVarName(sourceAttrObj.node()), sourceAttrObj.attrLongName(),)
                connectionStringsAdditionB = '>> %s.%s\n' % (getVarName(destinationAttrObj.node()), destinationAttrObj.attrLongName(),)
                connectionRows.append((connectionStringsAdditionA, connectionStringsAdditionB))

                lenOfConnectionStringsAdditionA = len(connectionStringsAdditionA)
                if lenOfConnectionStringsAdditionA > connectionStringsAdditionAMaxLength:
                    connectionStringsAdditionAMaxLength = lenOfConnectionStringsAdditionA

            if connectionRows:
                for connectionRow in connectionRows:
                    connectionStringsAdditionA, connectionStringsAdditionB = connectionRow
                    spaceBuffer = ' '*(connectionStringsAdditionAMaxLength-len(connectionStringsAdditionA))
                    connectionStrings += connectionStringsAdditionA+spaceBuffer+connectionStringsAdditionB

                connectionStrings += '\n'

        elif mode == 'pymel_commands':
            for sourceAttrObj, destinationAttrObj in connectionsDict[node].values():
                connectionStrings += "pymel.connectAttr(%s.%s, %s.%s, f=True)\n" % (getVarName(sourceAttrObj.node()), sourceAttrObj.attrLongName(),
                                                                                         getVarName(destinationAttrObj.node()), destinationAttrObj.attrLongName(),
                                                                                         )

            connectionStrings += '\n'

        elif mode == 'cmds_commands':
            for sourceAttrObj, destinationAttrObj in connectionsDict[node].values():
                connectionStrings += "cmds.connectAttr(%s+'.%s', %s+'.%s', f=True)\n" % (getVarName(sourceAttrObj.node()), sourceAttrObj.attrLongName(),
                                                                                         getVarName(destinationAttrObj.node()), destinationAttrObj.attrLongName(),
                                                                                         )

            connectionStrings += '\n'

    # ls Relevent Non-Created Nodes
    for node in list(releventNonCreatedNodes):
        if node not in createdNodes:
            releventNonCreatedNodesString += "%s = pymel.ls('%s')[0]\n" % (getVarName(node), str(node))


    print '\n\n## ----------------------------------------------------------------------------------------------------'

    if mode == 'pymel_objects' or mode == 'pymel_commands':
        print 'import pymel.core as pymel'

    elif mode == 'cmds_commands':
        print 'import maya.cmds as cmds'

    if releventNonCreatedNodesString:
        print '\n# GET RELATED NODES:  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  \n', releventNonCreatedNodesString

    if createNodeString:
        print '\n## CREATE NODES:  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  - \n', createNodeString

    if addAttrStrings:
        print '\n## ADD ATTRS:  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -   \n', addAttrStrings

    if setAttrStrings:
        print '\n## SET ATTRS:  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -   \n', setAttrStrings

    if connectionStrings:
        print '\n## CONNECT ATTRS:  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -   \n', connectionStrings


def listRelevantAttrs(node, baseAttributes=[], **kwArgs):
    """Returns a list of attibuteObjects based on the given baseAttributes. If baseAttributes are not
    specified, then all top level attributes will be used. From the base attributes, child, instance, etc
    attributes will be added to the return list"""

    exclusionList = ['attributeAliasList',]
    attrObjs = []
    #nodeTypes = node.nodeType(inherited=True)
    nodeName = node.nodeName()

    #if 'dagNode' in nodeTypes:
    if isinstance(node, pymel.nt.DagNode):
        nodeLongName = node.name(long=True)

        #if 'transform' in nodeTypes:
        exclusionList.extend(['boundingBox', 'center', 'isIKDirtyFlag',])
    else:
        nodeLongName = nodeName

    # make a dict of user defined attribute strings
    userDefinedAttributes = cmds.listAttr(nodeLongName, userDefined=True)
    userDefinedAttributesDict = {}
    if userDefinedAttributes:
        for userDefinedAttribute in userDefinedAttributes:
            userDefinedAttributesDict[userDefinedAttribute] = None

    if not baseAttributes:
        baseAttributes = pymel.listAttr(node, connectable=True, hasData=True,)
        baseAttributes.append('message')

    baseAttributes.sort()

    ## do any additional special sorting
    #if isinstance(node, pymel.nt.AnimCurve):
        #baseAttributes.pop(baseAttributes.index('keyTimeValue'))
        #baseAttributes.pop(baseAttributes.index('keyTimeValue.keyTime'))
        #baseAttributes.pop(baseAttributes.index('keyTimeValue.keyValue'))

        #baseAttributes.insert(0, 'keyTimeValue')
        #baseAttributes.insert(1, 'keyTimeValue.keyTime')
        #baseAttributes.insert(2, 'keyTimeValue.keyValue')

    # do any additional special sorting
    if isinstance(node, pymel.nt.AnimCurve):
        if 'keyTimeValue' in baseAttributes:
            baseAttributes.pop(baseAttributes.index('keyTimeValue'))
        if 'keyTimeValue.keyTime' in baseAttributes:
            baseAttributes.pop(baseAttributes.index('keyTimeValue.keyTime'))
        if 'keyTimeValue.keyValue' in baseAttributes:
            baseAttributes.pop(baseAttributes.index('keyTimeValue.keyValue'))

        baseAttributes.insert(0, 'keyTimeValue')
        baseAttributes.insert(1, 'keyTimeValue.keyTime')
        baseAttributes.insert(2, 'keyTimeValue.keyValue')



    # instance attr objects
    for attrName in baseAttributes:
        if attrName not in exclusionList:
            # get propertys of attributes/node to pass in to the creation of attrObjects
            # so that they do not need to be queried on a per attribute
            # basis
            attrObjKwargs = {}

            if attrName in userDefinedAttributesDict:
                attrObjKwargs['userDefined'] = True
            else:
                attrObjKwargs['userDefined'] = False

            #attrObjKwargs['nodeType'] = nodeTypes[-1]
            attrObjKwargs['nodeName'] = nodeName
            attrObjKwargs['exists'] = True

            #if 'dagNode' in nodeTypes:
            if isinstance(node, pymel.nt.DagNode):
                attrObjKwargs['nodeLongName'] = nodeLongName
            else:
                attrObjKwargs['nodeLongName'] = nodeName

            attrObj = getAsAttrObject(node, attrName, **attrObjKwargs) # returns None if attr is filtered

            # Only Top level attrs, children will be dealt with seperatly
            if attrObj.attrParentLongName() == '':
                if isinstance(attrObj.attr(), pymel.general.Attribute):
                    attrObjs.append(attrObj)
                    attrDecendentsStack = addAttrDecendentsToStack(attrObj, [], **attrObjKwargs)

                    while attrDecendentsStack:
                        decendentAttrObj = attrDecendentsStack.pop(0)

                        attrObjs.append(decendentAttrObj)
                        attrDecendentsStack = addAttrDecendentsToStack(decendentAttrObj, attrDecendentsStack, **attrObjKwargs)

    return attrObjs


def getAsAttrObject(node, attrName, **kwargs):
    """checks validity of attribute, and then returns and instantiates an attrObject for it."""

    global attrObjectDict

    if not isinstance(attrName, basestring):
        attrName = attrName.name(includeNode=False, longName=True, fullAttrPath=True, placeHolderIndices=True)
    #print attrName, type(attrName)


    if node.attr(attrName).__hash__() not in attrObjectDict:
        attrObj = attributeObj.AttributeObj(node, attrName, **kwargs)
        attrObjectDict[node.attr(attrName).__hash__()] = attrObj
        return attrObj

    else:
        return attrObjectDict[node.attr(attrName).__hash__()]


def addAttrDecendentsToStack(attrObj, stack, **kwargs):

    kwargs['attrParentLongName'] = attrObj.attrLongName()

    # Deal with Array Items
    if attrObj.isArray():
        usedIndices = attrObj.usedIndices()    ####
        indexDict = {}
        indexDict[0] = None
        indexDict[1] = None

        if usedIndices:

            for index in usedIndices:
                indexDict[index] = None

            indexDict[usedIndices[-1]+1] = None
            indexDict[usedIndices[-1]+2] = None


        # make array items
        for i in sorted(indexDict):

            # assume some propertys of the element to save time
            strI = str(i)
            attrName = '%s[%s]' % (attrObj.attrName(), strI)
            attrLongName = '%s[%s]' % (attrObj.attrLongName(), strI)

            childKwargs = dict(kwargs)
            childKwargs['attrLongName'] = attrLongName
            childKwargs['isElement'] = True
            if not attrObj.exists():
                childKwargs['exists'] = False
            else:
                if i in usedIndices:
                    childKwargs['exists'] = True
                else:
                    childKwargs['exists'] = False

            arrayAttrObj = getAsAttrObject(attrObj.node(), attrName, **childKwargs)

            stack.append(arrayAttrObj)

    else:

        # Deal With Children
        attrChildren = attrObj.attrChildrenLongNames()
        if attrChildren:
            for attrName in attrChildren:

                # assume some propertys of the child to save time
                childKwargs = dict(kwargs)
                childKwargs['attrLongName'] = attrName
                if not attrObj.exists():
                    childKwargs['exists'] = False

                childAttrObj = getAsAttrObject(attrObj.node(), childKwargs['attrLongName'], **childKwargs)
                stack.append(childAttrObj)


    return stack


def reorderAttribute(attribute, newIndex):

    pass

def addEnumValue(enumAttr, enumLabel):
    """Adds an enume label to the given enum attribute"""

    node = enumAttr.node()
    userDefinedAttrs = node.listAttr(userDefined=True)
    indexOfAttr = 0
    for i, attr in enumerate(userDefinedAttrs):
        if attr == enumAttr:
            indexOfAttr = i
            break

    # add enum
    enumDict = enumAttr.getEnums()
    orderedEnumDict = {}
    for key in enumDict:
        orderedEnumDict[enumDict[key]] = key

    enumList = []
    for key in sorted(orderedEnumDict):
        enumList.append(orderedEnumDict[key])
    enumList.append(enumLabel)

    enumString = ':'.join(enumList)
    attrOutputs = enumAttr.outputs(plugs=True)
    attrInputs = enumAttr.inputs(plugs=True)

    enumAttrObj = getAsAttrObject(node, enumAttr)
    keyable = enumAttrObj.isKeyable()
    shortName = enumAttrObj.attrShortName()
    longName = enumAttrObj.attrLongName()
    defaultValue = enumAttrObj.value()
    isInChannelBox = enumAttrObj.isInChannelBox()

    enumAttr.delete()
    node.addAttr(longName, at='enum', shortName=shortName, enumName=enumString, defaultValue=defaultValue, keyable=keyable)

    enumAttr = node.attr(longName)
    if isInChannelBox:
        enumAttr.set(keyable=keyable, channelBox=isInChannelBox)

    # reconnect
    for attrInput in attrInputs:
        attrInput >> enumAttr

    for attrOutput in attrOutputs:
        enumAttr >> attrOutput

    # recreate all attrs after i
    if indexOfAttr < len(userDefinedAttrs):
        for attr in userDefinedAttrs[indexOfAttr+1:]:
            attrObj = getAsAttrObject(node, attr)
            attrObj.recreateAttr()


def add1DInputToPlusMinusAverage(nodes=None):
    if nodes == None:
        nodes = pymel.ls(selection=True)

    for node in nodes:
        inputAttrs = node.input1D.elements()
        for i in range(len(inputAttrs)+1):
            if 'input1D[%s]'%str(i) in node.input1D.elements():
                pass

            else:
                node.caching >> node.input1D[i]
                node.caching // node.input1D[i]

    pymel.select(nodes)
