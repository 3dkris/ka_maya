#====================================================================================
#====================================================================================
#
# ka_util
#
# DESCRIPTION:
#   collection of small utility scripts that do simple yet essential tasks within maya
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

import inspect
import math
import types
from traceback import print_exc as printError

import pymel.core as pymel
import maya.cmds as cmds
import maya.mel as mel

import ka_maya.ka_math as ka_math                               #;reload(ka_math)
import ka_maya.ka_python as ka_python                           #;reload(ka_python)
import ka_maya.ka_pymel as ka_pymel                           #;reload(ka_python)
import ka_maya.ka_skinCluster as ka_skinCluster                 #;reload(ka_skinCluster)
import ka_maya.ka_transforms as ka_transforms                   #;reload(ka_transforms)
import ka_maya.ka_preference as ka_preference                   #;reload(ka_preference)
import ka_maya.ka_attrTool.attrCommands as  attrCommands        #;reload(attrCommands)



#decorators-------------------------------------------------------------------------------------------
def repeatable(function):
    '''A decorator that will make commands repeatable in maya'''
    def decoratorCode(*args, **kwargs):
        functionReturn = None
        argString = ''
        if args:
            for each in args:
                argString += str(each)+', '

        if kwargs:
            for key, item in kwargs.iteritems():
                argString += str(key)+'='+str(item)+', '

        commandToRepeat = 'python("'+__name__+'.'+function.__name__+'('+argString+')")'

        functionReturn = function(*args, **kwargs)
        try:
            cmds.repeatLast(ac=commandToRepeat, acl=function.__name__)
        except:
            printError()

        return functionReturn

    return decoratorCode



def undoable(function):
    '''A decorator that will make commands undoable in maya'''
    def decoratorCode(*args, **kwargs):
        cmds.undoInfo(openChunk=True)
        functionReturn = None
        try:
            functionReturn = function(*args, **kwargs)

        except:
            printError()

        finally:
            cmds.undoInfo(closeChunk=True)
            return functionReturn

    return decoratorCode

#decorators end-------------------------------------------------------------------------------------------

#context check utils-------------------------------------------------------------------------------------------
def selectionIsComponent():
    '''returns if selection is a component'''

    trueFalse = False
    currentSelection = cmds.ls(selection=True, shortNames=True)
    if currentSelection:
        selection = currentSelection[0]
        if '.' in selection:
            trueFalse = True

    return trueFalse

def selectionIsVertex():
    '''returns if selection is a vertex'''

    trueFalse = False
    currentSelection = cmds.ls(selection=True, shortNames=True)
    if currentSelection:
        selection = currentSelection[0]
        print 'selection:',
        print selection
        if '.vtx' in selection:
            trueFalse = True

    return trueFalse

#context check utils end-------------------------------------------------------------------------------------------
def deleteAllBindPoseNodes():
    for skinCluster in pymel.ls(type='skinCluster'):
        for inputNode in skinCluster.bindPose.inputs(type='dagPose'):
            pymel.delete(inputNode)

def cycleAttributeEditorChannelBox():

    # is attribute editor in focus?
    if mel.eval('isAttributeEditorRaised'):
        mel.eval('setAttributeEditorVisible(0);')
        mel.eval('setChannelBoxVisible(0);')

    elif mel.eval('isChannelBoxVisible'):
        mel.eval('openAEWindow;')

    else:
        if not mel.eval('isChannelBoxVisible'):
            mel.eval('setChannelBoxVisible(1);')
        else:
            mel.eval('raiseChannelBox;')

def helixParent():
    """divides the selection into 2 pairs and parents the nth item of the first set, the the nth item of the second
    set"""

    selection = pymel.ls(selection=True)
    lenOfSel = len(selection)
    if not lenOfSel%2==0:
        pymel.error('number of items selected is not divisable by 2')

    selectionSetA = selection[0:lenOfSel/2]
    selectionSetB = selection[lenOfSel/2:]

    for i, item in enumerate(selectionSetB):
        pymel.parent(selectionSetA[i], selectionSetB[i])

def helixCluster():
    """divides the selection into 2 pairs and parents the nth item of the first set, the the nth item of the second
    set"""

    selection = pymel.ls(selection=True, flatten=True)
    lenOfSel = len(selection)
    if not lenOfSel%2==0:
        pymel.error('number of items selected is not divisable by 2')

    selectionSetA = selection[0:lenOfSel/2]
    selectionSetB = selection[lenOfSel/2:]

    for i, item in enumerate(selectionSetB):
        pymel.cluster(selectionSetB[i], wn=(selectionSetA[i], selectionSetA[i]), bindState=True )

def removeJointOrients(inputJoints=None):
    if not inputJoints:
        inputJoints = pymel.ls(selection=True, type='joint')

    for joint in inputJoints:
        initialMatrix = pymel.xform(joint, query=True, matrix=True, worldSpace=True)
        joint.jointOrient.set(0,0,0)
        pymel.xform(joint, matrix=initialMatrix, worldSpace=True)


def freezePivotPosition():
    sel = cmds.ls(selection=True)
    for each in sel:
        cmds.setAttr(each+'.rotatePivotX', 0)
        cmds.setAttr(each+'.rotatePivotY', 0)
        cmds.setAttr(each+'.rotatePivotZ', 0)
        cmds.setAttr(each+'.rotatePivotTranslateX', 0)
        cmds.setAttr(each+'.rotatePivotTranslateY', 0)
        cmds.setAttr(each+'.rotatePivotTranslateZ', 0)
        cmds.setAttr(each+'.scalePivotX', 0)
        cmds.setAttr(each+'.scalePivotY', 0)
        cmds.setAttr(each+'.scalePivotZ', 0)

def snapOptions_setAimAxis(aimAxis):

    aimVector = None
    if aimAxis == 'X':
        aimVector = [1,0,0]

    elif aimAxis == '-X':
        aimVector = [-1,0,0]

    elif aimAxis == 'Y':
        aimVector = [0,1,0]

    elif aimAxis == '-Y':
        aimVector = [0,-1,0]

    elif aimAxis == 'Z':
        aimVector = [0,0,1]

    elif aimAxis == '-Z':
        aimVector = [0,0,-1]

    if aimVector:
        pymel.optionVar( clearArray='ka_transforms.snap.aimVector')
        for f in aimVector:
            pymel.optionVar( floatValueAppend=('ka_transforms.snap.aimVector', f))

#@undoable
#@repeatable


#@undoable
#@repeatable


@undoable
@repeatable
def clusterDeformSelection():
    selection = pymel.ls(selection=True)
    if not len(selection) <= 2:
        pymel.error('select am object to use as cluster, followed by points to deform')


    pymel.cluster(selection[1:], wn=(selection[0], selection[0]), bindState=True )


def lockAttr(attr):
    for node in pymel.ls(selection=True):
        try:
            node.attr(attr).lock()
            node.attr(attr).set(keyable=False)

        except: pass

        try:
            for childAttr in node.attr(attr).children():
                childAttr.unlock()
                childAttr.set(keyable=False)

        except: pass

        if not node.attr(attr).isLocked():
            print 'failed to lock %s.%s' % (str(node), attr)

def unlockAttr(attr):
    for node in pymel.ls(selection=True):
        try:
            node.attr(attr).unlock()
            node.attr(attr).set(keyable=True)

        except: pass

        try:
            for childAttr in node.attr(attr).children():
                childAttr.unlock()
                childAttr.set(keyable=True)

        except: pass


        if node.attr(attr).isLocked():
            print 'failed to unlock %s.%s' % (str(node), attr)


def setSetJointLabelFromName():
    selection = pymel.ls(selection=True)

    for sel in selection:
        _setSetJointLabelFromName(sel)

def setSetJointLabelFromNameOnAll():
    skinClusters = pymel.ls(type='skinCluster')
    jointInfluences = {}
    for skinCluster in skinClusters:
        influences = getInfluences(skinCluster)
        for influence in influences:
            if influence not in jointInfluences:
                jointInfluences[influence] = None

    for jointInfluence in jointInfluences:
        _setSetJointLabelFromName(jointInfluence)

def _setSetJointLabelFromName(node):

    if pymel.nodeType(node) == 'joint':
        baseName = None
        side = 0
        left = 1
        right = 2
        currentName = node.nodeName(stripNamespace=True)

        if currentName[0:2] == 'r_':
            side = right
            baseName = currentName[2:]
        elif currentName[0:2] == 'l_':
            side = left
            baseName = currentName[2:]
        elif currentName[0:2] == 'R_':
            side = right
            baseName = currentName[2:]
        elif currentName[0:2] == 'L_':
            side = left
            baseName = currentName[2:]

        elif '_r_' in currentName:
            side = right
            baseName = currentName.replace('_r_', '', 1)

        elif '_l_' in currentName:
            side = left
            baseName = currentName.replace('_l_', '', 1)

        elif '_R_' in currentName:
            side = right
            baseName = currentName.replace('_R_', '', 1)

        elif '_L_' in currentName:
            side = left
            baseName = currentName.replace('_L_', '', 1)

        else:
            baseName = currentName

        node.attr('type').set(18)
        node.side.set(side)
        node.otherType.set(baseName, type='string')





def makeSurfaceConstraint_useTangetV():
    """select 1 or more aim constraints created as a surface constraint by the constrain function
    in this module"""
    for each in pymel.ls(selection=True):
        for node in each.worldUpVector.inputs():
            node.tangentV >> each.worldUpVector
def makeSurfaceConstraint_useTangetU():
    """select 1 or more aim constraints created as a surface constraint by the constrain function
    in this module"""
    for each in pymel.ls(selection=True):
        for node in each.worldUpVector.inputs():
            node.tangentU >> each.worldUpVector



def shapeParent():
    selection = pymel.ls(selection=True)

    if len(selection) == 2:
        shapeObj = pymel.parent(selection[0], selection[1])
        pymel.makeIdentity(shapeObj[0], apply=True, t=1, r=1, s=1, n=1)
        shapes = pymel.listRelatives(shapeObj[0], shapes=True)

        for shape in shapes:
            pymel.parent(shape, selection[1], shape=True, add=True)

        pymel.delete(shapeObj)
        pymel.select(selection[1])

    else:
        pymel.error("script only works when 2 objects are selected")

def printSelection_asPythonList(tall=False):
    """
    Args:
        tall (bool): if true prints:
            [
            'sel1',
            'sel2',
            ]

    """
    selection = cmds.ls(selection=True)
    last = len(selection)-1

    if tall:
        printString = '[\n'
        for i, each in enumerate(selection):
            if i != last:
                printString += "'%s',\n" % each
            else:
                printString += "'%s',\n]" % each

        print printString

    else:
        printString = '['
        for i, each in enumerate(selection):
            if i != last:
                printString += "'%s', " % each
            else:
                printString += "'%s']" % each

        print printString


def xferSkin(sourceObject="", targetObjects=""):

    selectedObjects = cmds.ls(selection=True)
    if len(selectedObjects) < 2:
        cmds.error("must be at least 2 skined objects selected")

    if sourceObject == "":
        sourceObject = selectedObjects[0]

    if targetObjects == "":
        targetObjects = selectedObjects[1:]

    sourceSkinClusterNode = ka_skinCluster.findRelatedSkinCluster(sourceObject)
    sourceSkinInfluenceList = getSkinInfluences(sourceObject)

    for each in targetObjects:
        cmds.skinCluster(sourceSkinInfluenceList, each, removeUnusedInfluence=False)
        targetSkinClusterNode = ka_skinCluster.findRelatedSkinCluster(each)

        cmds.copySkinWeights( sourceSkin=sourceSkinClusterNode, destinationSkin=targetSkinClusterNode, noMirror=True, influenceAssociation = 'oneToOne', surfaceAssociation = 'closestPoint')

    cmds.select(targetObjects, replace=True)

def getEdgeLoopFromVertSelection(select=False):

    if select:  query = False
    else:       query = True
    newSelection = None
    componentSelection = cmds.ls(selection=True, flatten=True)
    meshShape = componentSelection[0].split('.')[0]
    meshShape = cmds.listRelatives(meshShape, shapes=True)[0]
    selectedVertIndexs = []

    for component in componentSelection:
        component = component.split('.')[1]
        index = component
        index = index.split('[')[1]
        index = int(index.split(']')[0])
        selectedVertIndexs.append(index)


#    print selectedVertIndexs
#    print meshShape
#    print query
#    print type(meshShape)
    if len(selectedVertIndexs) == 2:

        newSelection = mel.eval('SelectEdgeLoopSp;')
#        newSelection = cmds.polySelect(meshShape, query=query, shortestEdgePath=(selectedVertIndexs[0], selectedVertIndexs[1]))
#        print 'cmds.polySelect('+meshShape+', query='+str(query)+', shortestEdgePath=('+str(selectedVertIndexs[0])+', '+str(selectedVertIndexs[1])+'))'

#        if select: mel.eval('ConvertSelectionToVertices;')
#        if len(newSelection) == 1: #because the two points are next to each other
#            newSelection = mel.eval('SelectEdgeLoopSp;')


        print newSelection


    return newSelection


def selectEdgeLoopFromVertSelection123():
    getEdgeLoopFromVertSelection(select=True)









def editRotationAxis():
    sel = cmds.ls(selection=True)
    newSel = []
    for each in sel:
        newSel.append(each+'.rotateAxis')

    cmds.select(newSel, replace=True)
    mel.eval("buildRotateMM;")
    mel.eval("MarkingMenuPopDown;")

def setTransformManipulatorMode(mode):
    context = pymel.currentCtx()

    if context == 'RotateSuperContext':
        if mode == 'world':         mode = 1
        elif mode == 'local':       mode = 0
        elif mode == 'trueValues':  mode = 2

        pymel.manipRotateContext('Rotate', edit=True, mode=mode)

    elif context == 'moveSuperContext':
        if mode == 'world':         mode = 2
        elif mode == 'local':       mode = 0
        elif mode == 'trueValues':  mode = 1

        pymel.manipMoveContext('Move', edit=True, mode=mode)

    elif context == 'scaleSuperContext':
        if mode == 'world':         mode = 0
        elif mode == 'local':       mode = 0
        elif mode == 'trueValues':  mode = 0

        pymel.manipScaleContext('Scale', edit=True, mode=mode)


def openLastScene():
    recentFilesList = pymel.optionVar(query="RecentFilesList")
    cmds.file(recentFilesList[-1], f=True, open=True)


def componentSelectMode():
    mel.eval('changeSelectMode -component;')
    mel.eval('setComponentPickMask "Point" true;')


def objectSelectMode(release=False):
    if not release:
        mel.eval('changeSelectMode -object;')
        mel.eval('buildSelectObjectMM;')
    else:
        mel.eval('MarkingMenuPopDown;')


def getListOfComponentShells(*args):
    if not args:
        inputs = pymel.ls(selection=True)[0]

    shellListOfLists = []

    print 'inputs:',
    print inputs
    if pymel.nodeType(inputs) == 'transform':
        mesh = inputs.getShape()

    vtxDict = {}
    vtxList = list(mesh.vtx)

    vertIndices = range(len(mesh.vtx)/50)

    sortedVtxIndices = {}
    for i, vtx in enumerate(vtxList):
        if i not in sortedVtxIndices:
            print 'i:',
            print i
            shellIndices = pymel.polySelect(vtx, extendToShell=True)

            shellList = []
            for shellIndex in shellIndices:
                if shellIndex not in sortedVtxIndices:
                    print 'shellIndex:',
                    print shellIndex
                    sortedVtxIndices[shellIndex] = True
                    shellList.append(shellIndex)

        shellListOfLists.append(shellList)

    #while vertIndices:
        #vtxNum = vertIndices[0]
        #print 'len(vertIndices):',
        #print len(vertIndices)
        #shellIndices = pymel.polySelect(mesh.vtx[vtxNum], extendToShell=True)

        ##print 'shellIndices:',
        ##print shellIndices
        #shellList = []
        #for shellIndex in shellIndices:
            ##if shellIndex in vertIndices:
            #shellList.append(shellIndex)
            #vertIndices.remove(shellIndex)

        #shellListOfLists.append(shellList)

    for each in shellListOfLists:
        print each
    #print 'shellListOfLists:',
    #print shellListOfLists
    #return shellListOfLists

def reverseSelectionOrder():
    selection = pymel.ls(selection=True)
    selection.reverse()
    pymel.select(selection)

import types

def getDependencyModules(module, fromPackage=None):
    """get all modules imported within given module"""
    dependencyModules = []
    for key, item in module.__dict__.items():
        if isinstance(item, types.ModuleType):
            if fromPackage:
                if isModuleFromPackage(item, fromPackage):
                    dependencyModules.append(item)
            else:
                dependencyModules.append(item)

    return dependencyModules

def isModuleFromPackage(module, packageString):
    if module.__package__:
        if  packageString in module.__package__.split('.'):
            return True

    return False

def getReloadList(module, fromPackage=None):
    reloadList = [module]
    dependencyModules = getDependencyModules(rnkRigBuilderUI, fromPackage=fromPackage)

    while dependencyModules:
        dependencyModule = dependencyModules.pop()
        reloadList.append(dependencyModule)

        dependencyModules.extend()




def resetAttrs():
    context = cmds.currentCtx()
    selection = cmds.ls(selection=True)

    for each in selection:
        attrList = []
        if context == 'RotateSuperContext':
            attrList.append('.rotateX')
            attrList.append('.rotateY')
            attrList.append('.rotateZ')
        elif context == 'moveSuperContext':
            attrList.append('.translateX')
            attrList.append('.translateY')
            attrList.append('.translateZ')
        elif context == 'scaleSuperContext':
            attrList.append('.scaleX')
            attrList.append('.scaleY')
            attrList.append('.scaleZ')

        for attr in attrList:
            if not cmds.getAttr(each+attr, lock=True):
                if '.scale' in  attr:
                    cmds.setAttr(each+attr, 1)
                else:
                    cmds.setAttr(each+attr, 0)

def contextDuplicate():
    panelName = cmds.getPanel( underPointer=True )

    selection = cmds.ls(selection=True)[0]
    selectionComponents = selection.split('.')

    #if the split on '.' resulted in a list greater than 1, then assume its a component
    if len(selectionComponents) >= 2:
        if 'vtx[' in selectionComponents[1]:
            mel.eval('ChamferVertex;')

        if 'e[' in selectionComponents[1]:
            mel.eval('PolyExtrude;')

        if 'f' in selectionComponents[1]:
            mel.eval('PolyExtrude;')

    else:
        if 'hyperShadePanel' in panelName:
            attrCommands.duplicateSelection()
        else:
            mel.eval('performDuplicate false;')



def renameAllShapes():
    for shape in pymel.ls(shapes=True, noIntermediate=True):
        parent = shape.getParent()
        try:
            shape.rename(parent.nodeName() + 'Shape')
        except:
            printError()

@undoable
@repeatable
def jointOrientContraint(*args):

    selection = cmds.ls(selection=True)

    if not len(selection) == 2:
        cmds.error('this operation needs 2 items to be selected')
    elif cmds.nodeType(selection[-1]) != 'joint':
        cmds.error('this operation needs the target to be a joint')
    else:
        lastSelectionShortName = selection[-1].split('|')[-1]
        orientConstraint = cmds.createNode('orientConstraint', name = lastSelectionShortName+'_jointOrientContraint')
        cmds.connectAttr(selection[0]+'.rotate', orientConstraint+'.target[0].targetRotate')
        cmds.connectAttr(selection[0]+'.parentMatrix[0]', orientConstraint+'.target[0].targetParentMatrix')
        cmds.connectAttr(selection[0]+'.rotateOrder', orientConstraint+'.target[0].targetRotateOrder')

        cmds.connectAttr(selection[-1]+'.rotateOrder', orientConstraint+'.constraintRotateOrder')
        cmds.connectAttr(selection[-1]+'.parentInverseMatrix[0]', orientConstraint+'.constraintParentInverseMatrix')

        cmds.connectAttr(orientConstraint+'.constraintRotate', selection[-1]+'.jointOrient')
        cmds.parent(orientConstraint, selection[-1])

@undoable
@repeatable
def distanceBetweenToTranslateX():

    selection = cmds.ls(selection=True)


    if not len(selection) == 3:
        cmds.error('this operation needs 3 items to be selected')
    elif cmds.nodeType(selection[-1]) != 'joint':
        cmds.error('this operation needs the target to be a joint')
    else:
        lastSelectionShortName = selection[-1].split('|')[-1]
        distanceBetween = cmds.createNode('distanceBetween', name = lastSelectionShortName+'distanceBetween')

        #cmds.connectAttr(selection[0]+'.translate', distanceBetween+'.point1')
        cmds.connectAttr(selection[0]+'.worldMatrix', distanceBetween+'.inMatrix1')

        #cmds.connectAttr(selection[1]+'.translate', distanceBetween+'.point2')
        cmds.connectAttr(selection[1]+'.worldMatrix', distanceBetween+'.inMatrix2')

        cmds.connectAttr(distanceBetween+'.distance', selection[-1]+'.translateX')


def zeroOut():
    selection = cmds.ls(selection=True)
    prefix = 2

    for each in selection:

        cmds.group(empty=True)


#def setKeyframes(nodes=None):
    #"""Same as setting a keyframe regularly, but works on set driven keys as well"""

    #if not nodes:
        #nodes = pymel.ls(selection=True)

    #setDrivenFound = False
    #for node in nodes:
        #for inputNode in node.inputs():
            #if 'animCurveU' in inputNode.nodeType():
                #outputPlugs = inputNode.output.outputs(skipConversionNodes=True, plugs=True)
                #if outputPlugs:
                    #keyTime = inputNode.input.get()
                    #keyValue = outputPlugs[0].get()

                    #pymel.setKeyframe(inputNode, insert=True, float=keyTime)
                    #index = pymel.keyframe(inputNode, query=True, float=[keyTime], indexValue=True,)

                    #pymel.keyframe(inputNode, index=index, absolute=True, valueChange=keyValue)

                    #setDrivenFound = True

            #elif hasattr(inputNode, 'rigType'):
                #if inputNode.rigType.get() == 'poseDriver':
                    #ka_advance



    #if not setDrivenFound:
        #mel.eval('performSetKeyframeArgList 1 {"0", "animationList"}')


def deleteAllKeyframes():
    '''deletes all keyframes driven by time'''
    selection = cmds.ls(selection=True)

    selectionList = []
    selectionList.extend(cmds.ls(type='animCurveTU'))
    selectionList.extend(cmds.ls(type='animCurveTA'))
    selectionList.extend(cmds.ls(type='animCurveTL'))

    cmds.select(selectionList, replace=True)
    cmds.delete(selectionList)
    if selection:
        cmds.select(selection, replace=True)


    #lenOfInputs = len(inputs)
    #
    #for each in selection:
    #    currentX = 0
    #
    #
    #
    #
    #    cmds.hyperGraph(hyperGraph, edit=True, addDependNode=each)
    #    cmds.hyperGraph(hyperGraph, edit=True, setNodePosition=[each, currentX, currentY])
    #
    #    inputs = cmds.listConnections( each, destination=False, source=True )
    #
    #    if inputs:
    #        currentX += -400
    #        currentY += 250
    #        for each in inputs:
    #            if not each in cmds.hyperGraph(hyperGraph, query=True, getNodeList=True):
    #                currentY += -250
    #                cmds.hyperGraph(hyperGraph, edit=True, addDependNode=each)
    #                cmds.hyperGraph(hyperGraph, edit=True, setNodePosition=[each, currentX, currentY])
    #
    #    print inputs
    #    #if inputs:
    #    #    while inputs:
    #    #        each = inputs.pop()
    #    #
    #    #        cmds.hyperGraph('graph1HyperShadeEd', edit=True, addDependNode=each)
    #    #        cmds.hyperGraph('graph1HyperShadeEd', edit=True, setNodePosition=[each, currentX, currentY])
    #    #        currentX += 400
    #    #        inputsOfEach = cmds.listConnections( each, destination=False, source=True )
    #    #
    #    #        if inputsOfEach:
    #    #            for input in inputsOfEach:
    #    #                inputs.append(input)
    #
    #
    #    currentY += 250


#def copyAttrValues():
#    #get lead object in channel box
#    channelBoxSelection = cmds.channelBox('mainChannelBox', query=True, mainObjectList=True)
#    copyObject = channelBoxSelection[-1]
#
#    #mainChannelBox
#    mainAttrs = cmds.channelBox(mainChannelBox, query=True, selectedMainAttributes=True,)
#    if mainAttrs:
#        mainAttrs = cmds.listAttr(copyObject, keyable=True,)
#
#    cmds.optionVar(clearArray='ka_AttrClipBoard')
#
#    for attr in mainAttrs:
#        attribute = copyObject+"."+attr
#        value = cmds.getAttr(attribute)
#
#        #if attribute is the destination of a connection
#        if cmds.connectionInfo(attribute, isDestination=True):
#            connection = cmds.connectionInfo(sourceFromDestination=True
#
#            if (gmatch connection '*.rotate')
#            connection = (`match "^[^\.]*" $connection` + "." + $each)
#
#
#            if(`connectionInfo -isExactDestination ($copyObject + "." + $each)`)
#            {
#                if(`gmatch $connection "unitConversion*"`)
#                {//if connection is a unit Conversion
#                        $connection = `match "^[^\.]*" $connection`; //strip the attribute, leave object name
#                        $connection = `connectionInfo -sourceFromDestination ($connection + ".input")`;
#                }
#            }
#            optionVar -stringValueAppend "ka_AttrClipBoard" ("Connection-" + $connection);
#            print ($connection +", ");
#        }
#        else// if it is not a connection
#        {
#            optionVar -stringValueAppend "ka_AttrClipBoard" ($value);
#            print ($value +", ");
#        }
#
#    }

    #global proc ka_copyAttrValues()
#{
#    //get objects effected by the main channel box
#    string $channelBoxSelection[] = `channelBox -q -mainObjectList mainChannelBox`;
#    string $copyObject = $channelBoxSelection[(`size($channelBoxSelection)` - 1)];
#
#    //get attributes selected in the channel box, if none are selected, then record them all
#    string $mainAttrs[] = `channelBox -q -selectedMainAttributes mainChannelBox`;
#    if(`size $mainAttrs` == 0)
#    {
#        $mainAttrs = `listAttr -keyable $copyObject`;
#    }
#
#    optionVar -clearArray "ka_AttrClipBoard";
#
#    string $mainAttrsValues[];
#    string $valueType;
#    string $value;
#    string $connection;
#
#    print ("\nattributes copied to ka_clipBoard: ");
#    //copy the attribute value of the specified attributes, and store them in an option variable
#    for($each in $mainAttrs)
#    {
#        $value = `getAttr ($copyObject + "." + $each)`;
#
#        if(`connectionInfo -isDestination ($copyObject + "." + $each)`)
#        {//if attribute is the destination of a connection
#            $connection = `connectionInfo -sourceFromDestination ($copyObject + "." + $each)`;
#
#            if(`gmatch $connection "*.rotate"`){ $connection =  (`match "^[^\.]*" $connection` + "." + $each); }
#
#            if(`connectionInfo -isExactDestination ($copyObject + "." + $each)`)
#            {
#                if(`gmatch $connectimport maya.cmds as cmds
#                {//if connection is a unit Conversion
#                        $connection = `match "^[^\.]*" $connection`; //strip the attribute, leave object name
#                        $connection = `connectionInfo -sourceFromDestination ($connection + ".input")`;
#                }
#            }
#            optionVar -stringValueAppend "ka_AttrClipBoard" ("Connection-" + $connection);
#            print ($connection +", ");
#        }
#        else// if it is not a connection
#        {
#            optionVar -stringValueAppend "ka_AttrClipBoard" ($value);
#            print ($value +", ");
#        }
#
#    }
#    print ("\n");
#}
#
#global proc ka_pasteAttrValues()
#{
#    //get objects effected by the main channel box
#    string $channelBoxSelection[] = `channelBox -q -mainObjectList mainChannelBox`;
#    string $copyObject = $channelBoxSelection[(`size($channelBoxSelection)` - 1)];
#
#    //get attributes selected in the channel box, if none are selected, then record them all
#    string $mainAttrs[] = `channelBox -q -selectedMainAttributes mainChannelBox`;
#    if(`size $mainAttrs` == 0)
#    {
#        $mainAttrs = `listAttr -keyimport maya.cmds as cmds
#    }
#
#    string $value;
#    //retrieve attribute array stored by the ka_copyAttrValues command
#    string $ka_clipBoard[] = `optionVar -q "ka_AttrClipBoard"`;
#
#    print ("\nattributes pasted from ka_clipBoard: ");
#    int $i = 0;
#    //paste the attributes retrieved to the new selections (the objects effected by the channel box)
#    for($each in $ka_clipBoard)
#    {
#        for($c in $channelBoxSelection)
#        {
#            if(`getAttr -settable ($c + "." + $mainAttrs[$i] )`)//check if attribute is locked or connected
#            {
#                if(`gmatch $each "Connection-*"`)
#                {//if pasting a connection
#                    string $connectionTokens[];
#                    tokenize $each "-" $connectionTokens;
#                    connectAttr $connectionTokens[1] ($c + "." + $mainAttrs[$i]);
#                    print ($connectionTokens[1] +", ");
#                }
#                else //if is a value rather than a connection
#                {
#                    setAttr -clamp ($c + "." + $mainAttrs[$i]) (float($each));
#                    print ($each +", ");
#                }
#            }
#        }import maya.cmds as cmds
#        $i++;
#
#    }
#    print ("\n");
#}
def pasteAttrValues():
    pass



def filterSelection():
    selection = cmds.ls(selection=True)
    if cmds.optionVar( exists='ka_filterSelectionLastFilter' ):
        defaultFilter = cmds.optionVar( query='ka_filterSelectionLastFilter' )
    else:
        defaultFilter = ''

    result = cmds.promptDialog(
        title='Filter Selection by Type',
        message='Type to Filter',
        button=['OK', 'Cancel'],
        defaultButton='OK',
        cancelButton='Cancel',
        dismissString='Cancel',
        text=defaultFilter,
    )

    if result == 'OK':
        filter = cmds.promptDialog(query=True, text=True)
        cmds.optionVar( sv=('ka_filterSelectionLastFilter', filter) )

        newSelection = []
        for each in selection:
            if cmds.nodeType(each) == filter:
                newSelection.append(each)

        if newSelection:
            cmds.select(newSelection)
        else:
            cmds.select(clear=True)

@repeatable
@undoable
def getIslandComponentsDict():
    islandComponentsDict = {}
    selectedObject = pymel.ls(selection=True, flatten=True)[0]
    verts = pymel.ls(selectedObject.vtx, flatten=True)
    islands = []
    while verts:
        vert = verts.pop(0)
        island = [vert]
        newPoints = pymel.ls(vert.connectedVertices(), flatten=True)

        while newPoints:
            newPoint = newPoints.pop(0)
            connectedPoints = pymel.ls(newPoint.connectedVertices(), flatten=True)
            for connectedPoint in iter(connectedPoints):
                if connectedPoint not in island:
                    verts.remove(connectedPoint)
                    island.append(connectedPoint)
                    newPoints.append(connectedPoint)

        islands.append(tuple(island))
    return tuple(islands)



def printSelectedCurveCreationCommand():
    '''prints the maya command to rebuild the selected curve'''
    selection = pymel.ls(selection=True)

    for item in selection:
        for shape in item.getShapes():
            curvePositions = cmds.getAttr( shape+'.cv[*]' )
            curveDegree = cmds.getAttr( shape+'.degree' )

            print 'cmds.curve( p=' + str(curvePositions) + ', degree=' + str(curveDegree) + ')'




def reorderAllShapesToTopOfTheirHierchy():
    for transform in pymel.ls(type='transform'):
        shapes = pymel.listRelatives(transform, shapes=True)
        if shapes:
            for shape in reversed(shapes):
                pymel.reorder(shape, front=True)


modelEditorVisObjectTypes = ['nurbsCurves', 'nurbsSurfaces', 'polymeshes', 'subdivSurfaces', 'planes', 'lights', 'cameras', 'joints', 'ikHandles', 'deformers', 'dynamics', 'fluids', 'hairSystems', 'follicles', 'nCloths', 'nParticles', 'nRigids', 'dynamicConstraints', 'locators', 'dimensions', 'handles', 'pivots', 'textures', 'strokes',]
def toggleModelFilter(filterList=['nurbsSurfaces', 'polymeshes']):
    panelUnderPointer = cmds.getPanel( underPointer=True )

    isFiltered = True

    for filterType in modelEditorVisObjectTypes:
        if filterType in filterList:
            kwargs = {filterType:True, 'query':True}
            if not cmds.modelEditor(panelUnderPointer, **kwargs):
                isFiltered = False

        else:
            kwargs = {filterType:True, 'query':True}
            if cmds.modelEditor(panelUnderPointer, **kwargs):
                isFiltered = False

    if not isFiltered:
        cmds.modelEditor(panelUnderPointer, edit=True, allObjects=False)
        for filterType in filterList:
            kwargs = {filterType:True, 'edit':True}
            cmds.modelEditor(panelUnderPointer, **kwargs)

    else:
        cmds.modelEditor(panelUnderPointer, edit=True, allObjects=True)




def convertSelectedAnimCurveTo(targetType='animCurveUA'):
    selection = pymel.ls(selection=True)
    for node in selection:
        if node.nodeType() in ['animCurveUU', 'animCurveUA', 'animCurveUL', 'animCurveUT', 'animCurveTU', 'animCurveTA', 'animCurveTL', 'animCurveTT',]:
            convertAnimCurveTo(node, node.nodeName(), targetType=targetType)

def addKeysToAnimCurveNode(animCurveNode, frame=0, value=0, index=0,):
    import pymel.core.animation as pymel

    pymel.setKeyframe(animCurveNode, insert=True, float=frame)
    pymel.keyframe(animCurveNode,  index=(index,index), absolute=True, valueChange=value)
    #pymel.keyTangent(animCurveNode, index=(index,index), inTangentType=inTangent)

    #pymel.keyTangent(animCurveNode, index=(index,index), inTangentType=inTangent, outTangentType=outTangent)

def convertAnimCurveTo(srcCurve, targetCurve, targetType='animCurveUA'):

    newCurve = pymel.createNode(targetType, name=targetCurve)
    numKeys = pymel.getAttr(srcCurve.keyTimeValue, size=1)

    tangentType = srcCurve.tangentType.get()
    weightedTangent = srcCurve.weightedTangents.get()
    preInfinity = srcCurve.preInfinity.get()
    postInfinity = srcCurve.postInfinity.get()


def getDependencyModules(module, fromPackage=None):
    """get all modules imported within given module"""
    dependencyModules = []
    for key, item in module.__dict__.items():
        if isinstance(item, types.ModuleType):
            if fromPackage:
                if isModuleFromPackage(item, fromPackage):
                    dependencyModules.append(item)
            else:
                dependencyModules.append(item)

    return dependencyModules

def isModuleFromPackage(module, packageString):
    if module.__package__:
        if  packageString in module.__package__.split('.'):
            return True

    return False

def getModuleDict(module, exclutionList=[], fromPackage=None):
    moduleDict = {
        'module':module,
        'exclutionList':exclutionList,
        'dependencyModules':[],
        'dependencyModuleDicts':[],
    }

    if module not in exclutionList:
        exclutionList.append(module)

    dependencyModules = getDependencyModules(module, fromPackage=fromPackage)
    for dependencyModule in dependencyModules:
        moduleDict['dependencyModules'].append(dependencyModule)

        subExclutionList = list(exclutionList)

        if dependencyModule not in subExclutionList:
            dependencyModuleDict = getModuleDict(dependencyModule, exclutionList=subExclutionList, fromPackage=fromPackage)
            moduleDict['dependencyModuleDicts'].append(dependencyModuleDict)

    return moduleDict

def getReloadList(module, fromPackage=None):
    reloadList = [module]
    dependencyModules = getDependencyModules(rnkRigBuilderUI, fromPackage=fromPackage)

    while dependencyModules:
        dependencyModule = dependencyModules.pop()
        reloadList.append(dependencyModule)

        dependencyModules.extend()



#def _aimSnap(a,b, primaryAxis=[-1,0,0], secondaryAxis=[0,1,0]):

    #def crossProduct(vect1, vect2):
        #return [ vect1[1]*vect2[2] - vect1[2]*vect2[1], vect1[2]*vect2[0] - vect1[0]*vect2[2], vect1[0]*vect2[1] - vect1[1]*vect2[0] ]

    #def normalizeVector(vector):
        #return [ vector[i]/magnitudeOfVector(vector)  for i in range(len(vector)) ]

    #def magnitudeOfVector(vector):
        #return math.sqrt( sum( vector[i]*vector[i] for i in range(len(vector)) ) )

    #def multiplyVectors(vector, multi):
        #return [ vector[i] * multi for i in range(len(vector)) ]


    #posA = pymel.xform(a, query=True, translation=True, worldSpace=True)
    #posB = pymel.xform(b, query=True, translation=True, worldSpace=True)
    #primaryVector = normalizeVector([posB[0]-posA[0], posB[1]-posA[1], posB[2]-posA[2], ])

    #matrixA = pymel.xform(a, query=True, matrix=True, worldSpace=True)

    #if round(primaryAxis[0], 2):
        #primaryMatrixSlice = slice(0, 3)
        #primaryIndex = 0
    #elif round(primaryAxis[1], 2):
        #primaryMatrixSlice = slice(4, 7)
        #primaryIndex = 1
    #elif round(primaryAxis[2], 2):
        #primaryMatrixSlice = slice(8,11)
        #primaryIndex = 2


    #if round(secondaryAxis[0], 2):
        #secondaryMatrixSlice = slice(0, 3)
        #secondaryIndex = 0
    #elif round(secondaryAxis[1], 2):
        #secondaryMatrixSlice = slice(4, 7)
        #secondaryIndex = 1
    #elif round(secondaryAxis[2], 2):
        #secondaryMatrixSlice = slice(8,11)
        #secondaryIndex = 2

    #indexList = [primaryIndex, secondaryIndex]

    #if 0 not in indexList:
        #otherMatrixSlice = slice(0, 3)
        #otherIndex = 0
    #elif 1 not in indexList:
        #otherMatrixSlice = slice(4, 7)
        #otherIndex = 1
    #elif 2 not in indexList:
        #otherMatrixSlice = slice(8,11)
        #otherIndex = 2

    #secondaryVector = matrixA[secondaryMatrixSlice]

    #primaryVector = multiplyVectors(primaryVector, primaryAxis[primaryIndex])
    #secondaryVector = multiplyVectors(secondaryVector, secondaryAxis[secondaryIndex])

    #crossVector = normalizeVector( crossProduct(primaryVector, secondaryVector ) )
    #secondaryVector = crossProduct(crossVector, primaryVector)
    #otherVector = normalizeVector( crossProduct(primaryVector, secondaryVector ) )

    #newMatrix = list(matrixA)

    #newMatrix[primaryMatrixSlice] = multiplyVectors(primaryVector, magnitudeOfVector(matrixA[primaryMatrixSlice]) )
    #newMatrix[secondaryMatrixSlice] = multiplyVectors(secondaryVector, magnitudeOfVector(matrixA[secondaryMatrixSlice]) )
    #newMatrix[otherMatrixSlice] = multiplyVectors(otherVector, magnitudeOfVector(matrixA[otherMatrixSlice]) )

    #pymel.xform(a, matrix=newMatrix, worldSpace=True)


_mayaRGB_to_indexDict = {}
for i in range(32):
    if i != 0:
        r, g, b = cmds.colorIndex( i, q=True )
        _mayaRGB_to_indexDict[(r, g, b)] = i


def colorObjects(nodes=None, index=None, color=None):

    # parse args
    if color == None and index:
        color = cmds.colorIndex( index, q=True )

    if index == None and color:
        key = (color[0], color[1], color[2])
        index = _mayaRGB_to_indexDict.get(key)

    if not nodes:
        nodes = pymel.ls(selection=True)

    if not isinstance(nodes, list):
        nodes = [nodes]



    nodes = ka_pymel.getAsPyNodes(nodes)

    # Find nodes to color
    nodesToColor = []
    for node in nodes:
        shapes = node.getShapes()
        if shapes:
            for shape in shapes:
                nodesToColor.append(shape)

        else:
            nodesToColor.append(node)

    # Color Nodes
    for node in nodesToColor:
        nodeType = node.nodeType()

        if nodeType == 'rigControlsNode':
            node.lineColor.unlock()
            node.lineColorR.unlock()
            node.lineColorG.unlock()
            node.lineColorB.unlock()
            node.lineColor.set(color[0], color[1], color[2])

        else:
            try:
                node.overrideEnabled.unlock()
                node.overrideEnabled.set(1)
            except: printError()

            try:

                if index != None:
                    # set the new 2015 attribute
                    try:
                        node.overrideRGBColors.unlock()
                        if node.overrideRGBColors.isConnected():
                            node.overrideRGBColors.disconnect()
                        node.overrideRGBColors.set(0)

                    except: printError()


                    if node.overrideColor.isConnected():
                        node.overrideColor.disconnect()

                    node.overrideColor.unlock()
                    node.overrideColor.set(index)

                elif color:
                    # set the new 2015 attribute
                    try:
                        node.overrideRGBColors.unlock()
                        if node.overrideRGBColors.isConnected():
                            node.overrideRGBColors.disconnect()
                        node.overrideRGBColors.set(1)

                    except: printError()

                    if node.overrideColorRGB.isConnected():
                        node.overrideColorRGB.disconnect()

                    node.overrideColorRGB.unlock()
                    node.overrideColorRGB.set(color)

            except: printError()







def getAsPyNode(inputObject):

    if isinstance(inputObject, basestring):
        inputObject = pymel.ls(inputObject)

        if inputObject:
            return inputObject[0]

    return inputObject



sideDict = {'l':'l',
            'r':'r',
            'c':'c',
            'left':'l',
            'right':'r',
            'center':'c',
            }


oppositesDict = {'l':'r',
                 'r':'l',
                 'c':'c',
                 'left':'right',
                 'right':'left',
                 'center':'center',
                 }

def getSideFromName(node):
    """Returns 'l', 'r', or 'c' based on the nodes name"""

    nodeName = node
    sideInfo = _getSideInfo(nodeName)
    return sideInfo.get('side', 'c')


def getOppositeFromName(node):
    """Returns the name of the assumed opposite control if one can be found"""
    nodeName = node
    sideInfo = _getSideInfo(nodeName)
    side = sideInfo.get('side', None)
    if side:
        if side in ['l', 'r']:
            return sideInfo['oppositeName']

def _getSideInfo(name):
    """Returns a dictionary with the following info about side (as derrived from name)
       sideInfo = {'side':              'l'
                   'sideString':        '_l_'
                   'positionInName':    'inname'
                   'oppositeSide':      'r'
                   'oppositeSideString: '_r_'
                   'oppositeName':      'ik_arm_r_ctrl'
                  }
    """

    def _sameName(name):
        return name

    def _upperName(name):
        return name.upper()

    def _lowerName(name):
        return name.lower()

    def _upperFirstLetter(name):
        return name[0].upper() + name[1:]

    sideInfo = {}

    for sideKey in sideDict:
        side = sideDict[sideKey]

        keyModifications = [_sameName, _upperName, _lowerName,]
        if len(sideKey) > 1:
            keyModifications.append(_upperFirstLetter)

        # starts with keys
        startsWithString = '%s_' # format to search for

        for keyModification in keyModifications: # check a number of possible variations of the key
            matchString = startsWithString % keyModification(sideKey) # string to search for in name

            if name.startswith(matchString):

                sideInfo['side'] = side
                sideInfo['sideString'] = matchString
                sideInfo['positionInName'] = 'startswith'

                sideInfo['oppositeSide'] = oppositesDict[side]
                sideInfo['oppositeSideString'] = startsWithString % keyModification(oppositesDict[sideKey])
                sideInfo['oppositeName'] = name.replace(sideInfo['sideString'], sideInfo['oppositeSideString'])

                return sideInfo



        # ends with keys
        endsWithString = '_%s' # format to search for

        for keyModification in keyModifications: # check a number of possible variations of the key
            matchString = endsWithString % keyModification(sideKey) # string to search for in name

            if name.endswith(matchString):

                sideInfo['side'] = side
                sideInfo['sideString'] = matchString
                sideInfo['positionInName'] = 'endswith'

                sideInfo['oppositeSide'] = oppositesDict[side]
                sideInfo['oppositeSideString'] = endsWithString % keyModification(oppositesDict[sideKey])
                sideInfo['oppositeName'] = name.replace(sideInfo['sideString'], sideInfo['oppositeSideString'])

                return sideInfo


        # key is in name
        inNameString = '_%s_' # format to search for

        for keyModification in keyModifications: # check a number of possible variations of the key
            matchString = inNameString % keyModification(sideKey) # string to search for in name

            if matchString in name:

                sideInfo['side'] = side
                sideInfo['sideString'] = matchString
                sideInfo['positionInName'] = 'inname'

                sideInfo['oppositeSide'] = oppositesDict[side]
                sideInfo['oppositeSideString'] = inNameString % keyModification(oppositesDict[sideKey])
                sideInfo['oppositeName'] = name.replace(sideInfo['sideString'], sideInfo['oppositeSideString'])

                return sideInfo

    return sideInfo