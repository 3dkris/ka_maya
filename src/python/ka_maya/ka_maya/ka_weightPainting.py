#====================================================================================
#====================================================================================
#
# ka_weightPainting
#
# DESCRIPTION:
#   tools for weight painting, and general weight editing on deformers, especially skinClusters.
#   many commands intended to be accessed through the ka_menu
#
# DEPENDENCEYS:
#   ka_menus
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

from traceback import format_exc as printError
import re
import math
import time

import maya.cmds as cmds
import maya.mel as mel
import pymel.core as pymel
import maya.OpenMaya as OpenMaya
import maya.OpenMayaAnim as OpenMayaAnim

import ka_maya.ka_python as ka_python
import ka_maya.ka_pymel as ka_pymel
import ka_maya.ka_math as ka_math
import ka_maya.ka_clipBoard as ka_clipBoard
import ka_maya.ka_deformers as ka_deformers
import ka_maya.ka_selection as ka_selection
import ka_maya.ka_skinCluster as ka_skinCluster
import ka_maya.ka_preference as ka_preference
import ka_maya.ka_geometry as ka_geometry
import ka_maya.ka_mayaApi as ka_mayaApi

PRUNE_PRECISION = 0.0001

###################################################################################################################################
# GET PARALLEL WEIGHT BLENDER GLOBAL DATA
###################################################################################################################################
# parallel data
previousSelection = []

vertDict = {}    # key=vertIndex, Value=MeshVertex <pymelNode>
parallelRelationshipDict = {}    # key=vertIndex, Value={top:topVertIndex, bottom:bottomVertIndex, right:rightVertIndex, left:leftVertIndex}
vertPositionDict = {}    # key=vertIndex, Value=(worldPositionX, worldPositionY, worldPositionZ)
selectionIndices = []    # key=vertIndex, Value=MeshVertex <pymelNode>

# pair sequence
vertPairSequence = []    # key=vertIndex, Value=List of Tuples, with each tuple containing vertIndices
currentVertPairSequenceIndex = 0    # index
previousVertPairSequenceIndex = None    # index

# sphere data
rightColoredVertexSpheres = []
leftColoredVertexSpheres = []
lambertA = None
lambertB = None
lambertAIsBlack = True
lambertBIsBlack = True

# weight data
skinCluster = None
influenceDict = {} #key=vertIndex, Value={<index>:<influence>}
weightsDict = {}    #key=vertIndex, Value={<index>:<weight value>}
appliedWeightsDict = {}    #key=vertIndex, Value={<index>:<weight value>}

# weight blend undo
weightBlend_maxUndos = 10
weightBlend_weightsDictHistory = []    #[(weightDict, skinCluster), (weightDict, skinCluster)...]
weightBlend_weightsDictHistoryIndex = 0    #current position in weight dict


###################################################################################################################################
# ARTISAN PAINT FUNCTIONS
###################################################################################################################################

def paintInfluence(influence):
    oldInfluence = pymel.artAttrSkinPaintCtx('artAttrSkinContext', query=True, influence=True)
    pymel.optionVar( stringValue=("ka_weightPaintTool_oldPaintingInfluence", oldInfluence))

    mel.eval('setSmoothSkinInfluence '+influence)
    pymel.setAttr(influence+".lockInfluenceWeights", 0)

    applyJointColors()
    #refreshMayaPaintUI()

def paintAndHoldAllOthers(influence):
    holdAllInfluences()
    paintInfluence(influence)


def togglePaint():
    paintContext = pymel.currentCtx()

    if paintContext == 'artAttrSkinContext':
        oldInfluence = mel.eval('artAttrSkinPaintCtx -q -influence artAttrSkinContext')

        mel.eval('setSmoothSkinInfluence `optionVar -q ka_weightPaintTool_oldPaintingInfluence`;')

        pymel.setAttr(pymel.optionVar(query='ka_weightPaintTool_oldPaintingInfluence',)+'.lockInfluenceWeights', 0)
        pymel.optionVar(stringValue = ['ka_weightPaintTool_oldPaintingInfluence', oldInfluence])

        applyJointColors()
        #refreshMayaPaintUI()

    elif 'artAttr' in paintContext:
        value = cmds.artAttrCtx(paintContext, value=True, query=True,)
        cmds.artAttrCtx(paintContext, value=1.0-value, edit=True,)



def holdInfluence(influence):
    pymel.setAttr(influence+'.lockInfluenceWeights', 1)

    applyJointColors()
    #refreshMayaPaintUI()

def unholdInfluence(influence):
    pymel.setAttr(influence+'.lockInfluenceWeights', 0)

    applyJointColors()
    #refreshMayaPaintUI()

def holdAllInfluences():
    influenceList = getInfluences()
    for influence in influenceList:
        pymel.setAttr(influence+'.lockInfluenceWeights', 1)

def unholdAllInfluences():
    influenceList = getInfluences()
    for influence in influenceList:
        pymel.setAttr(influence+'.lockInfluenceWeights', 0)

def mirrorWeights(inverse=False):
    selection = pymel.ls(selection=True)

    if len(selection) == 1:
        #raise NameError('Too many objects selected')
        skinCluster = findRelatedSkinCluster(selection[0])
        skinCluster.envelope.set(0)

        pymel.copySkinWeights(mirrorMode='YZ', surfaceAssociation='closestPoint', influenceAssociation=['label', 'oneToOne', 'closestBone', 'name'], mirrorInverse=inverse,)

        skinCluster.envelope.set(1)

    else:
        skinClusterA = findRelatedSkinCluster(selection[0])
        skinClusterB = findRelatedSkinCluster(selection[1])
        skinClusterA.envelope.set(0)
        skinClusterB.envelope.set(0)

        pymel.copySkinWeights(sourceSkin=skinClusterA, destinationSkin=skinClusterB, mirrorMode='YZ', surfaceAssociation='closestPoint', influenceAssociation=['label', 'oneToOne', 'closestBone', 'name'], mirrorInverse=inverse,)

        skinClusterA.envelope.set(1)
        skinClusterB.envelope.set(1)

    refreshMayaPaintUI()


def toggleAddReplace():

    toolContext = pymel.currentCtx()
    if toolContext == "artAttrSkinContext":

        oldPaintTool = pymel.artAttrSkinPaintCtx(toolContext,  query=True, selectedattroper=True)
        oldPaintToolValue = pymel.artAttrSkinPaintCtx(toolContext,  query=True, value=True,)
        oldPaintToolOpacity = pymel.artAttrSkinPaintCtx(toolContext,  query=True, opacity=True,)

        #defaults

        if not pymel.optionVar(query="ka_weightPaint_oldPaintToolValue", exists=True):
            pymel.optionVar(floatValue=("ka_weightPaint_oldPaintToolValue", 1))

        if not pymel.optionVar(query="ka_weightPaint_oldPaintToolOpacity", exists=True):
            pymel.optionVar(floatValue=("ka_weightPaint_oldPaintToolOpacity", 1))

        if oldPaintTool == "smooth":
            toggleSmooth()
        else:

            if oldPaintTool == "absolute":
                pymel.artAttrSkinPaintCtx(toolContext, edit=True, selectedattroper="additive", )
                pymel.artAttrSkinPaintCtx(toolContext, edit=True, value=pymel.optionVar(query="ka_weightPaint_oldPaintToolValue",) )
                pymel.artAttrSkinPaintCtx(toolContext, edit=True, opacity=pymel.optionVar(query="ka_weightPaint_oldPaintToolOpacity",) )
                mel.eval('toolPropertyShow;')

#            elif oldPaintTool == "scale":
#                pymel.artAttrSkinPaintCtx(toolContext, edit=True, selectedattroper="additive", )
#                pymel.artAttrSkinPaintCtx(toolContext, edit=True, value=pymel.optionVar(query="ka_weightPaint_oldPaintToolValue",) )
#                pymel.artAttrSkinPaintCtx(toolContext, edit=True, opacity=pymel.optionVar(query="ka_weightPaint_oldPaintToolOpacity",) )
#                mel.eval('toolPropertyShow;')

            else:
                pymel.artAttrSkinPaintCtx(toolContext, edit=True, selectedattroper=pymel.optionVar(query="ka_weightPaint_oldPaintTool",) )
                pymel.artAttrSkinPaintCtx(toolContext, edit=True, value=pymel.optionVar(query="ka_weightPaint_oldPaintToolValue",) )
                pymel.artAttrSkinPaintCtx(toolContext, edit=True, opacity=pymel.optionVar(query="ka_weightPaint_oldPaintToolOpacity",) )
                mel.eval('toolPropertyShow;')


            if oldPaintTool in ['absolute', 'additive', 'scale']:
                pymel.optionVar(stringValue=("ka_weightPaint_oldPaintTool", oldPaintTool))
                pymel.optionVar(floatValue=("ka_weightPaint_oldPaintToolValue", oldPaintToolValue))
                pymel.optionVar(floatValue=("ka_weightPaint_oldPaintToolOpacity", oldPaintToolOpacity))

            mel.eval('artAttrSkinToolScript 4;')
            pymel.artAttrSkinPaintCtx(pymel.currentCtx(), edit=True, showactive=True)

def toggleSmooth():

    toolContext = pymel.currentCtx()
    if toolContext == "artAttrSkinContext":

        preSmoothPaintTool = pymel.artAttrSkinPaintCtx(toolContext, query=True, selectedattroper=True)
        preSmoothPaintToolValue = pymel.artAttrSkinPaintCtx(toolContext,  query=True, value=True,)
        preSmoothPaintToolOpacity = pymel.artAttrSkinPaintCtx(toolContext,  query=True, opacity=True,)

        #defaults
        if not pymel.optionVar(query="ka_weightPaint_preSmoothPaintTool", exists=True):
            pymel.optionVar(stringValue=("ka_weightPaint_preSmoothPaintTool", 'smooth'))

        if not pymel.optionVar(query="ka_weightPaint_preSmoothPaintToolValue", exists=True):
            pymel.optionVar(floatValue=("ka_weightPaint_preSmoothPaintToolValue", 1))

        if not pymel.optionVar(query="ka_weightPaint_preSmoothPaintToolOpacity", exists=True):
            pymel.optionVar(floatValue=("ka_weightPaint_preSmoothPaintToolOpacity", 1))


        if preSmoothPaintTool == "smooth":
            pymel.artAttrSkinPaintCtx(toolContext, edit=True, selectedattroper=pymel.optionVar(query="ka_weightPaint_preSmoothPaintTool",) )
            pymel.artAttrSkinPaintCtx(toolContext, edit=True, value=pymel.optionVar(query="ka_weightPaint_preSmoothPaintToolValue",) )
            pymel.artAttrSkinPaintCtx(toolContext, edit=True, opacity=pymel.optionVar(query="ka_weightPaint_preSmoothPaintToolOpacity",) )
            mel.eval('toolPropertyShow;')

        else:
            pymel.artAttrSkinPaintCtx(toolContext, edit=True, selectedattroper="smooth", )
            pymel.artAttrSkinPaintCtx(toolContext, edit=True, value=pymel.optionVar(query="ka_weightPaint_preSmoothPaintToolValue",) )
            pymel.artAttrSkinPaintCtx(toolContext, edit=True, opacity=pymel.optionVar(query="ka_weightPaint_preSmoothPaintToolOpacity",) )
            mel.eval('toolPropertyShow;')


        pymel.optionVar(stringValue=("ka_weightPaint_preSmoothPaintTool", preSmoothPaintTool))
        pymel.optionVar(floatValue=("ka_weightPaint_preSmoothPaintToolValue", preSmoothPaintToolValue))
        pymel.optionVar(floatValue=("ka_weightPaint_preSmoothPaintToolOpacity", preSmoothPaintToolOpacity))

        mel.eval('artAttrSkinToolScript 4;')
        pymel.artAttrSkinPaintCtx(pymel.currentCtx(), edit=True, showactive=True)


def resetSkin(mode):
    '''rebinds the mesh with the same weights, and without the history of the previous skin cluster'''

    deleteAllBindPoses()

    selections = pymel.ls(selection=True, objectsOnly=True, transforms=True, long=True)
    for selection in selections:

        skinCluster = findRelatedSkinCluster(selection)
        if skinCluster:
            influenceList = getInfluences(skinCluster)
            objectHistory = pymel.listHistory(selection, interestLevel=2, pruneDagObjects=True)
            if skinCluster not in objectHistory:    pymel.error('skin cluster: '+skinCluster+'was not found in '+selection+'\'s history: '+str(objectHistory))
            skinClusterIndexInHistory = objectHistory.index(skinCluster)

            obeyMaxInfluences = pymel.skinCluster(skinCluster, query=True, obeyMaxInfluences=True)
            maximumInfluences = pymel.skinCluster(skinCluster, query=True, maximumInfluences=True)

            historyParent = None
            if not skinCluster == objectHistory[0]:
                historyParent = objectHistory[skinClusterIndexInHistory-1]

            skinClusterName = skinCluster.nodeName()

            #rebind to new joint positions, no change to original geometry
            if mode == 'reset':
                pymel.setAttr(skinCluster.envelope, 0)
                duplicateSkin = pymel.duplicate( selection, returnRootsOnly=True,)[0]

                pymel.select(influenceList, duplicateSkin, replace=True,)
                duplicateSkinCluster = pymel.skinCluster(ignoreBindPose=True, toSelectedBones=True, obeyMaxInfluences=obeyMaxInfluences, maximumInfluences=maximumInfluences)

                pymel.copySkinWeights(sourceSkin=skinCluster, destinationSkin=duplicateSkinCluster, noMirror=True, influenceAssociation="oneToOne",)

                pymel.delete(skinCluster)

                pymel.select(influenceList, selection, replace=True,)
                newSkinCluster = pymel.skinCluster(name=skinCluster, ignoreBindPose=True, toSelectedBones=True, obeyMaxInfluences=obeyMaxInfluences, maximumInfluences=maximumInfluences)

                pymel.copySkinWeights(sourceSkin=duplicateSkinCluster, destinationSkin=newSkinCluster, noMirror=True, influenceAssociation="oneToOne",)

                pymel.delete(duplicateSkin)

                objectHistory[skinClusterIndexInHistory] = newSkinCluster
                if historyParent:
                    pymel.reorderDeformers( historyParent, newSkinCluster, selection )

                newSkinCluster.rename(skinClusterName)

            #bake the skin deformed mesh, and reskin as new original geometry
            elif mode == 'bake':

                duplicateSkin = pymel.duplicate( selection, returnRootsOnly=True,)[0]

                pymel.select(influenceList, duplicateSkin, replace=True,)
                duplicateSkinCluster = pymel.skinCluster(ignoreBindPose=True, toSelectedBones=True, obeyMaxInfluences=obeyMaxInfluences, maximumInfluences=maximumInfluences)

                pymel.copySkinWeights(sourceSkin=skinCluster, destinationSkin=duplicateSkinCluster, noMirror=True, influenceAssociation="oneToOne",)


                pymel.delete(selection, constructionHistory=True,)

                pymel.select(influenceList, selection, replace=True,)
                newSkinCluster = pymel.skinCluster(ignoreBindPose=True, toSelectedBones=True, obeyMaxInfluences=obeyMaxInfluences, maximumInfluences=maximumInfluences)

                pymel.copySkinWeights(sourceSkin=duplicateSkinCluster, destinationSkin=newSkinCluster, noMirror=True, influenceAssociation="oneToOne",)

                pymel.delete(duplicateSkin)

                newSkinCluster.rename(skinClusterName)

    pymel.select(selections)



###################################################################################################################################
# COPY PASTE WEIGHTS FUNCTIONS
###################################################################################################################################


#def copyWeights(verts=None, copySpecificInfluence=None):
    #'''copys skin weights from 1 or more components, if more than 1, then the weight copy is an average'''
    #print 'hiphip'
    #paintMapDict = getCurrentPaintMapDict()

    #if not verts:
        #verts = pymel.ls(selection=True, flatten=True)

    ## Skin Cluster Copy
    #if paintMapDict['nodeType'] == 'skinCluster':

        #skinCluster = findRelatedSkinCluster(verts[0])

        #if copySpecificInfluence:
            #influences = pymel.skinCluster(skinCluster, query=True, influence=True,)

            #if copySpecificInfluence in influences:

                #weights = []
                #for i, influence in enumerate(influences):

                    #if influence == copySpecificInfluence:
                        #weights.append(1)
                    #else:
                        #weights.append(0)

                #weights1 = weights
                #weights2 = weights

            #else:
                #pymel.error(copySpecificInfluence+'is not an influence of the skin cluster of the verts')

        #elif len(verts) == 1:

            #influences = pymel.skinCluster(skinCluster, query=True, influence=True,)
            #weights1 = pymel.skinPercent(skinCluster, query=True, value=True,)
            #weights2 = pymel.skinPercent(skinCluster, query=True, value=True,)

        #elif len(verts) == 2:

            #influences = pymel.skinCluster(skinCluster, query=True, influence=True,)
            #weights1 = pymel.skinPercent(skinCluster, verts[0], query=True, value=True,)
            #weights2 = pymel.skinPercent(skinCluster, verts[1],  query=True, value=True,)

        #elif len(verts) > 2:

            #listOfListOfValues = []
            #for vert in verts:

                #listOfValues = pymel.skinPercent(skinCluster, vert, query=True, value=True)
                #listOfListOfValues.append(listOfValues)

            #averagedList = []
            #for index in range(len(listOfListOfValues[0])):

                #listOfValuesToAverage = []
                #for listOfValues in listOfListOfValues:
                    #listOfValuesToAverage.append(listOfValues[index])

                #value = (math.fsum(listOfValuesToAverage) / len(listOfValuesToAverage))

                #averagedList.append(value)

            #influences = pymel.skinCluster(skinCluster, query=True, influence=True,)
            #weights1 = averagedList
            #weights2 = averagedList

        #pymel.optionVar( clearArray='copySkinWeights_clipBoard_1')
        #pymel.optionVar( clearArray='copySkinInfluences_clipBoard_1')
        #pymel.optionVar( clearArray='copySkinWeights_clipBoard_2')

        #for i, weight in enumerate(weights1):
            #if weights1[i] == 0 and weights2[i] == 0:
                #pass

            #else:
                #pymel.optionVar( floatValueAppend=['copySkinWeights_clipBoard_1', weights1[i] ])
                #pymel.optionVar( floatValueAppend=['copySkinWeights_clipBoard_2', weights2[i] ])
                #pymel.optionVar( stringValueAppend=['copySkinInfluences_clipBoard_1', influences[i] ])



    ## All Other Deformers
    #else:
        #shape = verts[0].node()
        #if len(verts) == 1:
            #weight1 = getWeights(verts[0], shape=shape, paintMapDict=paintMapDict,)[0]
            #weight2 = weight1

        #elif len(verts) == 2:
            #weight1 = getWeights(verts[0], shape=shape, paintMapDict=paintMapDict,)[0]
            #weight2 = getWeights(verts[1], shape=shape, paintMapDict=paintMapDict,)[0]

        #elif len(verts) > 2:

            #listOfValues = []
            #for vert in verts:
                #listOfValues.append(getWeights(vert, shape=shape, paintMapDict=paintMapDict,)[0])

            #averagedValue = (math.fsum(listOfValues) / len(listOfValues))

            #weight1 = averagedValue
            #weight2 = averagedValue

        #pymel.optionVar( floatValue=['copyWeights_clipBoard_1', weight1 ])
        #pymel.optionVar( floatValue=['copyWeights_clipBoard_2', weight2 ])
        #OOOOOOO = "weight1"; print '%s: ' % OOOOOOO, eval(OOOOOOO), ' ', type(eval(OOOOOOO))
        #OOOOOOO = "weight2"; print '%s: ' % OOOOOOO, eval(OOOOOOO), ' ', type(eval(OOOOOOO))

##def getWeight(component, weightMap=None, shape=None):
    ##if shape==None:
        ##shape = component.node()

    ##if isinstance(shape, pymel.nt.Mesh):
        ##index = component.index()
        ##OOOOOOO = "component"; print '%s: ' % OOOOOOO, eval(OOOOOOO), ' ', type(eval(OOOOOOO))
        ##OOOOOOO = "index"; print '%s: ' % OOOOOOO, eval(OOOOOOO), ' ', type(eval(OOOOOOO))
        ##OOOOOOO = "weightMap"; print '%s: ' % OOOOOOO, eval(OOOOOOO), ' ', type(eval(OOOOOOO))
        ##return weightMap[index].get()

    ##else:
        ##return pymel.percent(weightMap.split('.')[0], component,  query=True, value=True,)[0]

#def pasteWeights(verts=None, weightedAverage=100):

    #paintMapDict = getCurrentPaintMapDict()
    ##nodeType, deformerName, attrName = paintMapString.split('.')[:3]

    #if not verts:
        #verts = pymel.ls(selection=True, flatten=True)

    ## Skin Cluster Past
    #if paintMapDict['nodeType'] == 'skinCluster':

        #skinClusters = []
        #for vert in verts:
            #skinCluster = findRelatedSkinCluster(vert)
            #skinClusters.append(skinCluster)

        #influences = pymel.optionVar(query='copySkinInfluences_clipBoard_1')
        #weights1 =  pymel.optionVar(query='copySkinWeights_clipBoard_1')
        #weights2 =  pymel.optionVar(query='copySkinWeights_clipBoard_2')

        #lenOfInfluences = len(influences)

        #averagedWeights = []
        #for index in range(lenOfInfluences):

            #weightsA = weights2[index] * (0.01 * ((200 - weightedAverage) * 1))
            #weightsB = weights1[index] * ((weightedAverage * 1) * 0.01)

            #value = ((weightsA+weightsB) / 2)

            #averagedWeights.append(value)


        #listOfTuples = []
        #for i in range(lenOfInfluences):
            #listOfTuples.append((influences[i], averagedWeights[i]))

        #for skinCluster in skinClusters:
            #pymel.skinPercent(skinCluster, verts, normalize=False, zeroRemainingInfluences=True, transformValue=listOfTuples)


    ## All Other Deformers Paste
    #else:

        #deformedShapes = []
        #deformers = []

        #for vert in verts:
            #shape = vert.node()
            #if shape not in deformedShapes:
                #deformedShapes.append(shape)

        #if len(deformedShapes) == 1:
            #deformers = pymel.ls(paintMapDict['nodeName'])

        #else:
            #for shape in deformedShapes:
                #for deformer in ka_deformers.getDeformers(shape):
                    #if deformer not in deformers:
                        #if deformer.nodeType() == nodeType:
                            #deformers.append(deformer)


        #weight1 =  pymel.optionVar(query='copyWeights_clipBoard_1')
        #weight2 =  pymel.optionVar(query='copyWeights_clipBoard_2')


        #weightA = weight2 * (0.01 * ((200 - weightedAverage) * 1))
        #weightB = weight1 * ((weightedAverage * 1) * 0.01)

        #value = ((weightA+weightB) / 2)

        #for deformer in deformers:
            ##pymel.percent(deformer, verts, value=value)
            #setWeights(verts, values=value, paintMapDict=paintMapDict)


def assignSkinClusterInfluenceToPoint(influence, skinCluster=None):
    if skinCluster is None:
        skinCluster = ka_skinCluster.findRelatedSkinCluster()

    influenceIndexDict = getSkinClusterInfluenceIndexDict(skinCluster)
    influenceIndex = influenceIndexDict[str(influence)]

    componentInfoDict = ka_geometry.getComponentInfoDict()

    weightsDict = getWeights()

    for shapeID in weightsDict.keys():
        weightsDict
        for point in weightsDict[shapeID]['values'].keys():
            weightsDict[shapeID]['values'][point] = {influenceIndex:1.0}

    setWeights(weightInfoDict=weightsDict, componentInfoDict=componentInfoDict)


#def copyInfluence(influence, add=False, skinCluster=None):


    #if skinCluster is None:
        #skinCluster = ka_skinCluster.findRelatedSkinCluster()

    #influenceIndexDict = getSkinClusterInfluenceIndexDict(skinCluster)
    #influenceIndex = influenceIndexDict[str(influence)]

    #weightsDict = getWeights()

    #if add:
        #newWeightsDict = ka_clipBoard.get('copyWeights_weightsDict', {})

    #else:
        #newWeightsDict = {}

    #for shapeID in weightsDict.keys():
        #for point in weightsDict[shapeID]['values'].keys():
            #weightsDict[shapeID]['values'][point] = {influenceIndex:1.0}

    #setWeights(weightInfoDict=weightsDict)

#def copyWeights_fromJoint(influences=[]):
    #pass

#def pasteWeights_fromJoint(verts=None, copySpecificInfluence=None, componentInfoDict=None):
    #pass



def copyWeights(verts=None, componentInfoDict=None):
    """copies weight info to the clipboard for use later"""

    # get componentInfoDict
    if componentInfoDict is None:
        componentInfoDict = ka_geometry.getComponentInfoDict()

    weightsDict = getWeights(componentInfoDict=componentInfoDict, getAdditionalData=True)
    ka_clipBoard.add('copyWeights_weightsDict', weightsDict)


def pasteAveragedWeights(verts=None, componentInfoDict=None):
    # get componentInfoDict
    if componentInfoDict is None:
        componentInfoDict = ka_geometry.getComponentInfoDict()

    weightInfoDict = ka_clipBoard.get('copyWeights_weightsDict')

    # is this a skin weight?
    isSkinWeights = False
    for shapeID in weightInfoDict:
        for point in weightInfoDict[shapeID]['values']:
            value = weightInfoDict[shapeID]['values'][point]
            if 'influenceOfIndex' in weightInfoDict[shapeID]:
                isSkinWeights = True
            break



    valuesToAverage = []
    for shapeID in weightInfoDict:
        for point in weightInfoDict[shapeID]['values']:
            value = weightInfoDict[shapeID]['values'][point]

            # if skinweights, use joint objects as keys
            if 'influenceOfIndex' in weightInfoDict[shapeID]:
                skinValue = {}
                for index in value:
                    joint = weightInfoDict[shapeID]['influenceOfIndex'][index]
                    skinValue[joint] = value[index]
                valuesToAverage.append(skinValue)

            else:
                valuesToAverage.append(value)


    if len(valuesToAverage) == 1:
        averagedWeight = valuesToAverage[0]

    else:
        # average simple 1D weights
        if isinstance(valuesToAverage[0], float):
            averagedWeight = ka_math.average(valuesToAverage)

        # average complex weights (ie: skinCluster)
        elif isinstance(valuesToAverage[0], dict):
            # find all influence keys
            keysDict = {}
            for valueDict in valuesToAverage:
                for key in valueDict:
                    keysDict[key] = None

            averagedWeight = {}

            for key in keysDict:
                valuesOfKey = []
                for valueDict in valuesToAverage:
                    if key in valueDict:
                        valuesOfKey.append(valueDict[key])
                    else:
                        valuesOfKey.append(0.0)

                averagedWeight[key] = ka_math.average(valuesOfKey)

        # unknown weight data
        else:
            raise Exception('got unexpected weight value: %s' % str(valuesToAverage[0]))


    # make new weightsInfoDict where the values are all that of the averaged weights
    newWeightsInfoDict = {}
    targetWeightInfoDict = getWeights(componentInfoDict=componentInfoDict, getAdditionalData=True)
    for shapeID in componentInfoDict:
        newWeightsInfoDict[shapeID] = {}
        newWeightsInfoDict[shapeID]['values'] = {}

        for point in componentInfoDict[shapeID]['pointDict']:
            if isSkinWeights:
                averagedSkinWeight = {}
                for joint in averagedWeight:
                    if joint not in targetWeightInfoDict[shapeID]['indexOfInfluence']:
                        #add it
                        addedInfluenceIndicesLists = addInfluence(joints=[joint], skinClusters=[targetWeightInfoDict[shapeID]['skinCluster']])
                        index = addedInfluenceIndicesLists[0][0]
                        targetWeightInfoDict[shapeID]['indexOfInfluence'][joint] = index
                        targetWeightInfoDict[shapeID]['influenceOfIndex'][index] = joint

                    else:
                        index = targetWeightInfoDict[shapeID]['indexOfInfluence'][joint]
                        averagedSkinWeight[index] = averagedWeight[joint]

                newWeightsInfoDict[shapeID]['values'][point] = averagedSkinWeight

            else:
                newWeightsInfoDict[shapeID]['values'][point] = averagedWeight


    setWeights(weightInfoDict=newWeightsInfoDict, componentInfoDict=componentInfoDict)



#def pasteAveragedWeights(verts=None, componentInfoDict=None):

    ## get componentInfoDict
    #if componentInfoDict is None:
        #componentInfoDict = ka_geometry.getComponentInfoDict()

    #weightInfoDict = ka_clipBoard.get('copyWeights_weightsDict')

    #valuesToAverage = []

    #for shapeID in weightInfoDict:
        #for point in weightInfoDict[shapeID]['values']:
            #value = weightInfoDict[shapeID]['values'][point]
            #valuesToAverage.append(value)

    #OOOOOOO = "valuesToAverage"; print '%s= ' % OOOOOOO, eval(OOOOOOO), ' #', type(eval(OOOOOOO))

    #if len(valuesToAverage) == 1:
        #averagedWeight = valuesToAverage[0]

    #else:
        ## average simple 1D weights
        #if isinstance(valuesToAverage[0], float):
            #averagedWeight = ka_math.average(valuesToAverage)

        ## average complex weights (ie: skinCluster)
        #elif isinstance(valuesToAverage[0], dict):
            ## find all influence keys
            #keysDict = {}
            #for valueDict in valuesToAverage:
                #for key in valueDict:
                    #keysDict[key] = None

            #averagedWeight = {}

            #for key in keysDict:
                #valuesOfKey = []
                #for valueDict in valuesToAverage:
                    #if key in valueDict:
                        #valuesOfKey.append(valueDict[key])
                    #else:
                        #valuesOfKey.append(0.0)

                #averagedWeight[key] = ka_math.average(valuesOfKey)

        ## unknown weight data
        #else:
            #raise Exception('got unexpected weight value: %s' % str(valuesToAverage[0]))


    ## make new weightsInfoDict where the values are all that of the averaged weights
    #newWeightsInfoDict = {}
    #for shapeID in componentInfoDict:
        #newWeightsInfoDict[shapeID] = {}
        #newWeightsInfoDict[shapeID]['values'] = {}

        #for point in componentInfoDict[shapeID]['pointDict']:
            #newWeightsInfoDict[shapeID]['values'][point] = averagedWeight


    #setWeights(weightInfoDict=newWeightsInfoDict, componentInfoDict=componentInfoDict)



def getSkinClusterData(vertIndex):
    global skinCluster
    global vertDict
    global influenceDict
    global weightsDict

    if vertIndex not in weightsDict:
        strVertIndex = str(vertIndex)
        strSkinCluster = str(skinCluster)
        usedWeightIndices = cmds.getAttr('%s.wl[%s].weights' % (strSkinCluster, strVertIndex,), multiIndices=True)
        weightsDict[vertIndex] = {}
        for usedWeightIndex in usedWeightIndices:
            unusedWeight = False
            weight = cmds.getAttr('%s.wl[%s].weights[%s]' % (strSkinCluster, strVertIndex, str(usedWeightIndex)))

            # get influence if not already in dict
            if not usedWeightIndex in influenceDict:
                influence = skinCluster.matrix[usedWeightIndex].inputs()
                if influence:
                    influenceDict[usedWeightIndex] = influence[0]
                else:
                    unusedWeight = True

            if not unusedWeight:
                weightsDict[vertIndex][usedWeightIndex] = weight

def copyWeightsFromNeighbors():

    global ka_pasteWeightsFromNeighbors_copyWeightsSucceeded        ;ka_pasteWeightsFromNeighbors_copyWeightsSucceeded=False
    global ka_weightBlender_ignoreInfluenceHolding
    ka_weightBlender_ignoreInfluenceHolding = ka_preference.get('weightBlender_ignoreInfluenceHolding', True)
    #if not pymel.optionVar( exists='ka_weightBlender_ignoreInfluenceHolding' ):
        #pymel.optionVar( iv=('ka_weightBlender_ignoreInfluenceHolding', 1))
    #ka_weightBlender_ignoreInfluenceHolding = pymel.optionVar( query='ka_weightBlender_ignoreInfluenceHolding' )

    getParallelVertData()

    global vertDict
    global parallelRelationshipDict
    global vertPositionDict
    global selectionIndices

    global weightBlend_weightsDictHistory
    global weightBlend_maxUndos

    global skinCluster
    global influenceDict
    global weightsDict
    global appliedWeightsDict

    global vertPairSequence

    skinCluster = None
    influenceDict = {}
    weightsDict = {}

    selection = pymel.ls(selection=True, flatten=True)
    skinCluster = findRelatedSkinCluster(selection[0])

    # Get skin weights (they will be stored into global variables)
    for sequence in vertPairSequence:
        for vertPair in sequence:
            for vert in vertPair:
                getSkinClusterData(vert)


    for vertIndex in parallelRelationshipDict:

        #vertTopIndex = parallelRelationshipDict[vertIndex]['top']
        #vertBottomIndex = parallelRelationshipDict[vertIndex]['bottom']
        #vertRightIndex = parallelRelationshipDict[vertIndex]['right']
        #vertLeftIndex = parallelRelationshipDict[vertIndex]['left']

        #vert = vertDict[vertIndex]
        #vertUpperNeighbor = vertDict[vertTopIndex]
        #vertLowerNeighbor = vertDict[vertBottomIndex]
        #vertRightNeighbor = vertDict[vertRightIndex]
        #vertLeftNeighbor = vertDict[vertLeftIndex]

        # Get skin weights (they will be stored into global variables)
        getSkinClusterData(vertIndex)
        #getSkinClusterData(vertTopIndex)
        #getSkinClusterData(vertBottomIndex)
        #getSkinClusterData(vertRightIndex)
        #getSkinClusterData(vertLeftIndex)

        #vertWeights = weightsDict[vertIndex]
        #topWeights = weightsDict[vertTopIndex]
        #bottomWeights = weightsDict[vertBottomIndex]
        #rightWeights = weightsDict[vertRightIndex]
        #leftWeights = weightsDict[vertLeftIndex]

        #come up with a factor that will allow normalized blending if the ignore
        #unheld influences mode is not set.
        if not ka_weightBlender_ignoreInfluenceHolding:
            totalHeld_vertWeight = 0
            totalUnheld_vertWeight = 0

            totalHeld_topWeight = 0
            totalUnheld_topWeight = 0

            totalHeld_bottomWeight = 0
            totalUnheld_bottomWeight = 0

            totalHeld_rightWeight = 0
            totalUnheld_rightWeight = 0

            totalHeld_leftWeight = 0
            totalUnheld_leftWeight = 0

            for weightIndex in vertWeights:

                if influenceDict[weightIndex].lockInfluenceWeights.get():
                    totalHeld_vertWeight += vertWeights.get(weightIndex, 0.0)
                    totalHeld_topWeight += topWeights.get(weightIndex, 0.0)
                    totalHeld_bottomWeight += bottomWeights.get(weightIndex, 0.0)
                    totalHeld_rightWeight += rightWeights.get(weightIndex, 0.0)
                    totalHeld_leftWeight += leftWeights.get(weightIndex, 0.0)

                else:
                    totalUnheld_vertWeight += vertWeights.get(weightIndex, 0.0)
                    totalUnheld_topWeight += topWeights.get(weightIndex, 0.0)
                    totalUnheld_bottomWeight += bottomWeights.get(weightIndex, 0.0)
                    totalUnheld_rightWeight += rightWeights.get(weightIndex, 0.0)
                    totalUnheld_leftWeight += leftWeights.get(weightIndex, 0.0)


            #figure out the multiply factor if none or either of the totals equals zero
            unheldNormalizeFactor_topWeight = 0
            unheldNormalizeFactor_bottomWeight = 0
            unheldNormalizeFactor_rightWeight = 0
            unheldNormalizeFactor_leftWeight = 0

            if not totalUnheld_vertWeight == 0: #if its zero, your not going to do much...
                if totalUnheld_topWeight:    unheldNormalizeFactor_topWeight = totalUnheld_vertWeight / totalUnheld_topWeight
                if totalUnheld_bottomWeight: unheldNormalizeFactor_bottomWeight = totalUnheld_vertWeight / totalUnheld_bottomWeight
                if totalUnheld_rightWeight:  unheldNormalizeFactor_rightWeight = totalUnheld_vertWeight / totalUnheld_rightWeight
                if totalUnheld_leftWeight:   unheldNormalizeFactor_leftWeight = totalUnheld_vertWeight / totalUnheld_leftWeight


            for weightIndex in vertWeights:
                if not vertWeights.get(weightIndex, 0.0) and not topWeights.get(weightIndex, 0.0) and not bottomWeights.get(weightIndex, 0.0) and not rightWeights.get(weightIndex, 0.0) and not leftWeights.get(weightIndex, 0.0):
                    pass
                else:
                    if influenceDict[weightIndex].lockInfluenceWeights.get():
                        # If the influence is locked, manipulate the data for the top, bottom, right, and left
                        # weights to be the same as the original vert, so that blending has no effect for those
                        # influences

                        weightsDict[vertTopIndex][weightIndex] = weightsDict[vertIndex][weightIndex]
                        weightsDict[vertBottomIndex][weightIndex] = weightsDict[vertIndex][weightIndex]
                        weightsDict[vertRightIndex][weightIndex] = weightsDict[vertIndex][weightIndex]
                        weightsDict[vertLeftIndex][weightIndex] = weightsDict[vertIndex][weightIndex]

                    else:
                        # manipulate the data for the top, bottom, right, and left weights so that blending
                        # 100% to their unheld influences would leave you with a weight total of 1. This will
                        # also allow a smooth transitioning with a value of less than 1.

                        if unheldNormalizeFactor_topWeight:
                            weightsDict[vertTopIndex][weightIndex] *= unheldNormalizeFactor_topWeight
                        else: weightsDict[vertTopIndex][weightIndex] = weightsDict[vertIndex][weightIndex] #use the vert weight

                        if unheldNormalizeFactor_bottomWeight:
                            weightsDict[vertBottomIndex][weightIndex] *= unheldNormalizeFactor_bottomWeight
                        else: weightsDict[vertBottomIndex][weightIndex] = weightsDict[vertIndex][weightIndex]  #use the vert weight

                        if unheldNormalizeFactor_rightWeight:
                            weightsDict[vertRightIndex][weightIndex] *= unheldNormalizeFactor_rightWeight
                        else: weightsDict[vertRightIndex][weightIndex] = weightsDict[vertIndex][weightIndex]  #use the vert weight

                        if unheldNormalizeFactor_leftWeight:
                            weightsDict[vertLeftIndex][weightIndex] *= unheldNormalizeFactor_leftWeight
                        else: weightsDict[vertLeftIndex][weightIndex] = weightsDict[vertIndex][weightIndex]  #use the vert weight

    appliedWeightsDict = weightsDict.copy()
    addToUndoStack('weightsDict')
    ka_pasteWeightsFromNeighbors_copyWeightsSucceeded = True

def pasteWeightsFromNeighbors_changeNeighbors(reverse=False):
    global vertPairSequence
    global currentVertPairSequenceIndex
    global previousVertPairSequenceIndex

    sequenceLength = len(vertPairSequence)
    sequenceIndex = currentVertPairSequenceIndex

    if reverse:
        if sequenceIndex != 0 and sequenceLength >= 1: # not the last item in sequence or a sequence of 1
            previousVertPairSequenceIndex = currentVertPairSequenceIndex
            currentVertPairSequenceIndex = currentVertPairSequenceIndex - 1

        else:
            previousVertPairSequenceIndex = currentVertPairSequenceIndex
            currentVertPairSequenceIndex = sequenceLength - 1

    else:
        if sequenceIndex != sequenceLength-1 and sequenceLength >= 1: # not the last item in sequence or a sequence of 1
            previousVertPairSequenceIndex = currentVertPairSequenceIndex
            currentVertPairSequenceIndex = currentVertPairSequenceIndex + 1

        else:
            previousVertPairSequenceIndex = currentVertPairSequenceIndex
            currentVertPairSequenceIndex = 0

    pasteWeightsFromNeighbors_positionSpheres()

def pasteWeightsFromNeighbors_positionSpheres():
    global rightColoredVertexSpheres
    global leftColoredVertexSpheres

    global vertPositionDict

    global vertPairSequence
    global currentVertPairSequenceIndex


    sequenceIndex = currentVertPairSequenceIndex
    currentVertPairList = vertPairSequence[sequenceIndex]

    for i, each in enumerate(rightColoredVertexSpheres):
        vertA = currentVertPairList[i][0]
        vertB = currentVertPairList[i][1]
        pymel.xform(leftColoredVertexSpheres[i], translation=vertPositionDict[vertA], worldSpace=True)
        pymel.xform(rightColoredVertexSpheres[i], translation=vertPositionDict[vertB], worldSpace=True)

        setSpherePairScale_fromCameraSpace(vertPositionDict[vertB], rightColoredVertexSpheres[i], vertPositionDict[vertA], leftColoredVertexSpheres[i])

def pasteWeightsFromNeighbors(weightedAverage=100):
    #pymel.undoInfo(stateWithoutFlush=False)

    global ka_pasteWeightsFromNeighbors_copyWeightsSucceeded
    if ka_pasteWeightsFromNeighbors_copyWeightsSucceeded:
        global ka_weightBlender_ignoreInfluenceHolding

        global skinCluster
        global influenceDict
        global weightsDict
        global appliedWeightsDict
        global parallelRelationshipDict
        global vertPositionDict

        global rightColoredVertexSpheres
        global leftColoredVertexSpheres
        global lambertA
        global lambertB
        global lambertAIsBlack
        global lambertBIsBlack

        global previousSelection
        global selectionIndices

        global ka_pasteWeightsFromNeighbors_previousShiftState


        global vertPairSequence
        global currentVertPairSequenceIndex
        global previousVertPairSequenceIndex

        appliedWeightsDict = {}

        selection = previousSelection
        lenOfSelection = len(selectionIndices)
        strSkinCluster = str(skinCluster)

        #shiftState = False
        #if (cmds.getModifiers() & 1) > 0:
            #shiftState = True #Shift is down

        for i, vertIndex in enumerate(selectionIndices):
            vertLeftIndex = vertPairSequence[currentVertPairSequenceIndex][i][0]
            vertRightIndex = vertPairSequence[currentVertPairSequenceIndex][i][1]

            ## get index of our two blend verts
            #if lenOfSelection == 1:
                ##if shiftState:
                #if pasteWeightsFromNeighbors_pairIndex:
                    #vertRightIndex = parallelRelationshipDict[vertIndex]['top']
                    #vertLeftIndex = parallelRelationshipDict[vertIndex]['bottom']
                #else:
                    #vertRightIndex = parallelRelationshipDict[vertIndex]['right']
                    #vertLeftIndex = parallelRelationshipDict[vertIndex]['left']

                # is pairIndex different then its previous value? if so do not repeat the work
                #if not shiftState == ka_pasteWeightsFromNeighbors_previousShiftState:
                #if not pasteWeightsFromNeighbors_pairIndex == pasteWeightsFromNeighbors_previousPairIndex:
                    #ka_pasteWeightsFromNeighbors_previousShiftState = shiftState
                    #pasteWeightsFromNeighbors_previousPairIndex = pasteWeightsFromNeighbors_pairIndex
                    #pymel.xform(rightColoredVertexSpheres[0], translation=vertPositionDict[vertRightIndex], worldSpace=True)
                    #pymel.xform(leftColoredVertexSpheres[0], translation=vertPositionDict[vertLeftIndex], worldSpace=True)
                    #setSpherePairScale_fromCameraSpace(vertPositionDict[vertRightIndex], rightColoredVertexSpheres[0], vertPositionDict[vertLeftIndex], leftColoredVertexSpheres[0])

            #else:
                #vertRightIndex = parallelRelationshipDict[vertIndex]['right']
                #vertLeftIndex = parallelRelationshipDict[vertIndex]['left']

            # are we blending to the left or right?
            finalWeights = {}
            weightsA = weightsDict[vertIndex].copy()
            if weightedAverage < 100:
                blend = (100 - weightedAverage)
                weightsB = weightsDict[vertRightIndex].copy()

            elif weightedAverage > 100:
                blend = (weightedAverage - 100)
                weightsB = weightsDict[vertLeftIndex].copy()

            else: # is at 100, ie: inital position, with no blending
                blend = (100 - weightedAverage)
                weightsB = None
                finalWeights = weightsA

            if weightsB:
                # any indices in one list and not the other? if so, their value is 0.0
                for weightIndex in weightsB:
                    if weightIndex not in weightsA:
                        weightsA[weightIndex] = 0.0

                for weightIndex in weightsA:
                    if weightIndex not in weightsB:
                        weightsB[weightIndex] = 0.0

                # do the averaging math
                for weightIndex in weightsA:
                    weightA = weightsA[weightIndex] * (0.01 * ((100 - blend) * 2))
                    weightB = weightsB[weightIndex] * ((blend * 2) * 0.01)

                    value = ((weightA+weightB) / 2)
                    if value:
                        finalWeights[weightIndex] = value

            strVertIndex = str(vertIndex)
            cmds.removeMultiInstance('%s.wl[%s]' % (strSkinCluster, strVertIndex,))
            for weightIndex in finalWeights:
                cmds.setAttr('%s.wl[%s].w[%s]' % (strSkinCluster, strVertIndex, str(weightIndex)), finalWeights[weightIndex])

            # store final applied weight
            appliedWeightsDict[vertIndex] = finalWeights

            ###########################
            # color Spheres
            if weightedAverage < 100:
                if weightedAverage == 0: lambertA.incandescence.set( [ 1, 1, 1 ] )
                else:                    lambertA.incandescence.set( [ blend*0.01, 0.25+(blend*0.0075), blend*0.0015 ] )
                lambertAIsBlack = False

                if not lambertBIsBlack:
                    lambertB.incandescence.set( [0, 0, 0] )
                    lambertBIsBlack = True

            elif weightedAverage > 100:
                if weightedAverage == 200: lambertB.incandescence.set( [ 1, 1, 1 ] )
                else:                      lambertB.incandescence.set( [ blend*0.01, 0.25+(blend*0.0075), blend*0.0015 ] )
                lambertBIsBlack = False

                if not lambertAIsBlack:
                    lambertA.incandescence.set( [0, 0, 0] )
                    lambertAIsBlack = True

            else: #is 100 (50%)
                if not lambertBIsBlack:
                    lambertB.incandescence.set( [0, 0, 0] )
                    lambertBIsBlack = True

                if not lambertAIsBlack:
                    lambertA.incandescence.set( [0, 0, 0] )
                    lambertAIsBlack = True


            #
            ###########################

def addToUndoStack(dictToAdd):
    if dictToAdd == 'weightsDict':
        global weightsDict
        inputWeightDict = weightsDict

    if dictToAdd == 'appliedWeightsDict':
        global appliedWeightsDict
        inputWeightDict = appliedWeightsDict

    global selectionIndices
    global skinCluster
    global weightBlend_maxUndos
    global weightBlend_weightsDictHistory
    global weightBlend_weightsDictHistoryIndex

    # Does given weight data differ from the last undo?
    weightsDifferFromLastUndo = False
    if weightBlend_weightsDictHistory:
        historicalWeightDict, historicalSkinCluster = weightBlend_weightsDictHistory[weightBlend_weightsDictHistoryIndex]
        if historicalSkinCluster == skinCluster:
            for vertIndex in selectionIndices:
                if vertIndex in inputWeightDict and vertIndex in historicalWeightDict:
                    for weightIndex in inputWeightDict[vertIndex]:
                        if weightsDifferFromLastUndo:
                            break
                        else:

                            if weightIndex in historicalWeightDict[vertIndex] and weightIndex in inputWeightDict[vertIndex]:
                                if round(inputWeightDict[vertIndex][weightIndex], 3) != round(historicalWeightDict[vertIndex][weightIndex], 3):
                                    weightsDifferFromLastUndo = True
                                    break


                            else:weightsDifferFromLastUndo = True ;
                else:weightsDifferFromLastUndo = True ;
        else:weightsDifferFromLastUndo = True ;
    else:weightsDifferFromLastUndo = True ;


    # store to undo stack
    if weightsDifferFromLastUndo:

        weightsAreValid = True # are they valid (totaling 1.0)?
        for vertIndex in selectionIndices:
            weightTotal = 0.0
            for weightIndex in inputWeightDict[vertIndex]:
                weightTotal += inputWeightDict[vertIndex][weightIndex]
            if not round(weightTotal, 2) == 1.0:# > 1.001 or weightTotal < 0.999:
                weightsAreValid = False

        if weightsAreValid:
            # is current undo 0? if not this is the result of redos
            while weightBlend_weightsDictHistoryIndex != 0:
                if weightBlend_weightsDictHistoryIndex < 0:
                    pymel.error('how did that happen?')
                weightBlend_weightsDictHistoryIndex -= 1
                weightBlend_weightsDictHistory.pop(0)

            if len(weightBlend_weightsDictHistory) >= weightBlend_maxUndos:
                weightBlend_weightsDictHistory.pop(-1)

            outputWeightDict={}
            for vertIndex in selectionIndices:
                outputWeightDict[vertIndex] = {}
                weightTotal = 0.0
                for weightIndex in inputWeightDict[vertIndex]:
                    outputWeightDict[vertIndex][weightIndex] = inputWeightDict[vertIndex][weightIndex]
                    weightTotal += outputWeightDict[vertIndex][weightIndex]

            weightBlend_weightsDictHistory.insert(0, (outputWeightDict, skinCluster))


def undoWeightBlend():
    global weightsDict
    global weightBlend_weightsDictHistory
    global weightBlend_weightsDictHistoryIndex

    ## if there is something to undo
    if not len(weightBlend_weightsDictHistory)-1  <  weightBlend_weightsDictHistoryIndex+1:
        weightBlend_weightsDictHistoryIndex += 1
        historicalWeightDict, historicalSkinCluster = weightBlend_weightsDictHistory[weightBlend_weightsDictHistoryIndex]

        strSkinCluster = str(historicalSkinCluster)
        for vertIndex in historicalWeightDict:
            strVertIndex = str(vertIndex)

            cmds.removeMultiInstance('%s.wl[%s]' % (strSkinCluster, strVertIndex,))
            for weightIndex in historicalWeightDict[vertIndex]:
                cmds.setAttr('%s.wl[%s].w[%s]' % (strSkinCluster, strVertIndex, str(weightIndex)), historicalWeightDict[vertIndex][weightIndex])
    else:
        pymel.warning('weightBlender has nothing left to redo')


def redoWeightBlend():
    global weightBlend_weightsDictHistory
    global weightBlend_weightsDictHistoryIndex

    if not weightBlend_weightsDictHistoryIndex-1 < 0:
        weightBlend_weightsDictHistoryIndex -= 1
        historicalWeightDict, historicalSkinCluster = weightBlend_weightsDictHistory[weightBlend_weightsDictHistoryIndex]

        strSkinCluster = str(historicalSkinCluster)
        for vertIndex in historicalWeightDict:
            strVertIndex = str(vertIndex)

            cmds.removeMultiInstance('%s.wl[%s]' % (strSkinCluster, strVertIndex,))
            for weightIndex in historicalWeightDict[vertIndex]:
                cmds.setAttr('%s.wl[%s].w[%s]' % (strSkinCluster, strVertIndex, str(weightIndex)), historicalWeightDict[vertIndex][weightIndex])
    else:
        pymel.warning('weightBlender has nothing left to undo')


def blendWeights(weightedAverage=100):
    #pymel.undoInfo(stateWithoutFlush=False)
    global ka_pasteWeightsFromNeighbors_copyWeightsSucceeded

    if ka_pasteWeightsFromNeighbors_copyWeightsSucceeded:
        global ka_pasteWeightsFromNeighbors_pasteInfoList                 ;pasteInfoList = ka_pasteWeightsFromNeighbors_pasteInfoList
        global ka_pasteWeightsFromNeighbors_skinCluster                 ;skinCluster = ka_pasteWeightsFromNeighbors_skinCluster
        global ka_pasteWeightsFromNeighbors_influences                  ;influences = ka_pasteWeightsFromNeighbors_influences


        selection = pymel.ls(selection=True, flatten=True)

        copiedInfluences = pymel.optionVar(query='copySkinInfluences_clipBoard_1')
        copiedWeights =  pymel.optionVar(query='copySkinWeights_clipBoard_1')
        averagedWeights = []
        listOfTuples = []
        listOfListOfTuples = []
        listOfVertsPerListOfTuples = []

        for list in pasteInfoList:

            vert, vertWeight, vertUpperNeighborWeight, vertLowerNeighborWeight, vertRightNeighborWeight, vertLeftNeighborWeight, vertInfluences = list

            localCopiedWeights = []
            pasteInfluences = []
            listOfTuples = []

            for copiedWeight in copiedWeights:
                localCopiedWeights.append(copiedWeight)

            for vertInfluence in vertInfluences:
                pasteInfluences.append(vertInfluence)

            for copiedInfluence in copiedInfluences:
                if not copiedInfluence in vertInfluences:
                    pasteInfluences.append(copiedInfluence)
                    vertWeight.append(0)


            for vertInfluence in vertInfluences:
                if not vertInfluence in copiedInfluences:
                    localCopiedWeights.insert(0, 0)

            listOfTuples = []
            for i, influence in enumerate(pasteInfluences):
                weightsA = vertWeight[i]            * (0.01 * (200 - weightedAverage) * 1)
                weightsB = localCopiedWeights[i]    * ((weightedAverage * 1) * 0.01)

                value = ((weightsA+weightsB) / 2)
                listOfTuples.append((str(influence), value))

            listOfListOfTuples.append(listOfTuples)
            listOfVertsPerListOfTuples.append(vert)


            pymel.undoInfo(stateWithoutFlush=True)
            for i, listOfTuples in enumerate(listOfListOfTuples):
                #must be cmds to allow clean undo
                pymel.skinPercent(str(skinCluster), str(listOfVertsPerListOfTuples[i]), normalize=False, zeroRemainingInfluences=True, transformValue=listOfTuples)

    else:
        pass


def setSpherePairScale_fromCameraSpace(vertAPosition, sphereA, vertBPosition, sphereB):

    vertAPositionInCameraSpace = getInCameraSpace(vertAPosition)
    sphereScaleA = vertAPositionInCameraSpace[2]*-0.01

    vertBPositionInCameraSpace = getInCameraSpace(vertBPosition)
    sphereScaleB = vertBPositionInCameraSpace[2]*-0.01

    distanceBetweenPoints = ka_math.distanceBetween(vertAPositionInCameraSpace, vertBPositionInCameraSpace)

    if sphereScaleA > (distanceBetweenPoints / 5) or sphereScaleB > (distanceBetweenPoints / 5):
        sphereScaleA = (distanceBetweenPoints / 5)
        sphereScaleB = (distanceBetweenPoints / 5)

    if sphereScaleA < (distanceBetweenPoints / 30) or sphereScaleB < (distanceBetweenPoints / 30):
        sphereScaleA = (distanceBetweenPoints / 30)
        sphereScaleB = (distanceBetweenPoints / 30)

    sphereA.scale.set(sphereScaleA, sphereScaleA, sphereScaleA)
    sphereB.scale.set(sphereScaleB, sphereScaleB, sphereScaleB)



def createColoredVertexSpheres():

    global vertDict
    global parallelRelationshipDict
    global vertPositionDict
    global selectionIndices

    global rightColoredVertexSpheres
    global leftColoredVertexSpheres
    global lambertA
    global lambertB

    panel = pymel.getPanel(underPointer=True)
    panel = panel.split('|')[-1]
    selection = pymel.ls(selection=True)

    radius = 1

    rightColoredVertexSpheres = []
    leftColoredVertexSpheres = []

    # make lambert for A spheres
    lambertA = pymel.shadingNode('lambert', asShader=True, name='DELETE_ME__TEMP_rightLambert')
    lambertA.addAttr('createColoredVertexSpheres_tempType', dt='string')
    lambertA.color.set( [0,0,0] )
    lambertA.transparency.set( [0.5,0.5,0.5] )
    shadingEngineR = pymel.sets(renderable=True, noSurfaceShader=True, empty=True, name='DELETE_ME__TEMP_rightshadingEngine')
    shadingEngineR.addAttr('createColoredVertexSpheres_tempType', dt='string')
    pymel.connectAttr(lambertA+".outColor", shadingEngineR+".surfaceShader", force=True)

    # make lambert for B spheres
    lambertB = pymel.shadingNode('lambert', asShader=True, name='DELETE_ME__TEMP_rightLambert')
    lambertB.addAttr('createColoredVertexSpheres_tempType', dt='string')
    lambertB.color.set( [0,0,0] )
    lambertB.transparency.set( [0.5,0.5,0.5] )
    shadingEngineL = pymel.sets(renderable=True, noSurfaceShader=True, empty=True, name='DELETE_ME__TEMP_rightshadingEngine')
    shadingEngineL.addAttr('createColoredVertexSpheres_tempType', dt='string')
    pymel.connectAttr(lambertB+".outColor", shadingEngineL+".surfaceShader", force=True)

    isolateState = pymel.isolateSelect(panel, query=True, state=True)
    firstvertexSphereA = None
    firstvertexSphereB = None
    for i, vertIndex in enumerate(parallelRelationshipDict):
        topIndex = parallelRelationshipDict[vertIndex]['top']
        bottomIndex = parallelRelationshipDict[vertIndex]['bottom']
        rightIndex = parallelRelationshipDict[vertIndex]['right']
        leftIndex = parallelRelationshipDict[vertIndex]['left']

        if i == 0:
            vertexSphereA = pymel.sphere(name='DELETE_ME__vertexSpheres', radius=radius, sections=1, spans=2)[0]
            vertexSphereA.overrideEnabled.set(1)
            vertexSphereA.drawOverride.overrideColor.set(2)

            vertexSphereB = pymel.sphere(name='DELETE_ME__vertexSpheres', radius=radius, sections=1, spans=2)[0]
            vertexSphereB.overrideEnabled.set(1)
            vertexSphereB.drawOverride.overrideColor.set(2)


            vertexSphereA.addAttr('createColoredVertexSpheres_tempType', dt='string')
            vertexSphereB.addAttr('createColoredVertexSpheres_tempType', dt='string')

            pymel.sets( shadingEngineR, forceElement=vertexSphereA, )
            pymel.sets( shadingEngineL, forceElement=vertexSphereB, )

            firstvertexSphereA = vertexSphereA
            firstvertexSphereB = vertexSphereB
        else:
            vertexSphereA = pymel.instance(firstvertexSphereA, name='DELETE_ME__vertexSpheres',)[0]
            vertexSphereB = pymel.instance(firstvertexSphereB, name='DELETE_ME__vertexSpheres',)[0]

        rightColoredVertexSpheres.append(vertexSphereA)
        leftColoredVertexSpheres.append(vertexSphereB)

        shapeObj = selection[0].node()
        mel.eval( 'hilite '+shapeObj.name() )
        pymel.select(shapeObj)
        pymel.select(selection)



        #if len(parallelRelationshipDict) == 1:
            #vertRightNeighborPosition = vertPositionDict[rightIndex]
            #vertLeftNeighborPosition = vertPositionDict[leftIndex]
            #vertUpperNeighborPosition = vertPositionDict[topIndex]
            #vertLowerNeighborPosition = vertPositionDict[bottomIndex]
        #else:
            #vertLeftNeighborPosition = vertPositionDict[topIndex]
            #vertRightNeighborPosition = vertPositionDict[bottomIndex]

        #pymel.xform(vertexSphereA, translation=vertRightNeighborPosition, worldSpace=True)
        #pymel.xform(vertexSphereB, translation=vertLeftNeighborPosition, worldSpace=True)

        #setSpherePairScale_fromCameraSpace(vertRightNeighborPosition, vertexSphereA, vertLeftNeighborPosition, vertexSphereB)

        if isolateState:
            pymel.isolateSelect(panel, addDagObject=vertexSphereA)
            pymel.isolateSelect(panel, addDagObject=vertexSphereB)

    pasteWeightsFromNeighbors_positionSpheres()


rightColoredVertexSpheres
def colorVertexSpheres(objectList, color):

    lambert = None
    lambertMatch = pymel.ls(type='lambert')
    if lambertMatch:
        for each in lambertMatch:
            if '_'+color+'_TEMP_lambert' in each.name():
                lambert=each
                break
            elif ':'+color+'_TEMP_lambert' in each.name():
                lambert=each
                break

    if not lambert:
        lambert = pymel.shadingNode('lambert', asShader=True, name='DELETE_ME__TEMP_lambert')
        lambert.addAttr('createColoredVertexSpheres_tempType', dt='string')


    shadingEngine = None
    shadingEngineMatch = pymel.ls(type='shadingEngine')
    if shadingEngineMatch:
        for each in shadingEngineMatch:
            if '_'+color+'_TEMP_shadingEngine' in each.name():
                shadingEngine=each
                break
            elif ':'+color+'_TEMP_shadingEngine' in each.name():
                shadingEngine=each
                break

    if not shadingEngine:
        shadingEngine = pymel.sets(renderable=True, noSurfaceShader=True, empty=True, name='DELETE_ME__TEMP_shadingEngine')
        shadingEngine.addAttr('createColoredVertexSpheres_tempType', dt='string')
        pymel.connectAttr(lambert+".outColor", shadingEngine+".surfaceShader", force=True)


    colorValues = [0, 0, 0]
    if color == 'black': colorValues =          [0, 0, 0]
    if color == 'red': colorValues =            [1, 0, 0]
    if color == 'darkerRed': colorValues =      [0.75, 0, 0]
    if color == 'blue': colorValues =           [0, 0.2, 1]
    if color == 'darkBlue': colorValues =       [0, 0, .25]
    if color == 'lightBlue': colorValues =      [0.25, 0.25, 1]
    if color == 'green': colorValues =          [0, 1, 0]
    if color == 'darkGreen': colorValues =      [0, .45, 0]
    if color == 'lightGreen': colorValues =     [0.25, 1, 0.25]
    if color == 'teal': colorValues =           [0, 1, 1]

    lambert.colorR.set(colorValues[0])
    lambert.colorG.set(colorValues[1])
    lambert.colorB.set(colorValues[2])
    lambert.diffuse.set(1)

    #add color the object this color
    pymel.sets( shadingEngine, forceElement=object, )


def deleteColoredVertexSpheres():
    deleteMeObjects = pymel.ls('DELETE_ME__*')
    deleteList = []

    for each in deleteMeObjects:
        if pymel.attributeQuery('createColoredVertexSpheres_tempType', node=each, exists=True):
            deleteList.append(each)

    if deleteList:
        pymel.delete(deleteList)

def blendColoredVertexSpheres():
    pass

def averageWeights_forIslandInSelection():
    selection = pymel.ls(selection=True, flatten=True)


previousParallelSelection = []
previousDirection = None
def selectParallelVertsDict(selectGroup='top'):
    global previousParallelSelection
    global previousDirection

    mods = pymel.getModifiers()
    perpendicularMode = False
    if (mods & 1) > 0: #Shift is down
        perpendicularMode = True

    oposites = {'top':'bottom', 'bottom':'top', 'right':'left', 'left':'right', }
    parallelVertDict = getParallelVertsDict(perpendicularMode=perpendicularMode)
    previouslySelected = False

    selectList = []
    for key in parallelVertDict:
        vert, vertUpperNeighbor, vertLowerNeighbor, vertRightNeighbor, vertLeftNeighbor = parallelVertDict[key]

        if selectGroup == 'top':
            firstChoice = vertUpperNeighbor
            secondChoice = vertLowerNeighbor

        elif selectGroup == 'bottom':
            firstChoice = vertLowerNeighbor
            secondChoice = vertUpperNeighbor

        elif selectGroup == 'right':
            firstChoice = vertRightNeighbor
            secondChoice = vertLeftNeighbor

        elif selectGroup == 'left':
            firstChoice = vertLeftNeighbor
            secondChoice = vertRightNeighbor

        # has the first choice been selected immediatly before the current one?
        if previousDirection:
            if previousDirection == selectGroup:
                if firstChoice in previousParallelSelection:
                    previouslySelected = True

            #if switching direction
            elif oposites[selectGroup] == previousDirection:
                if firstChoice not in previousParallelSelection:
                    previouslySelected = True

        # if selecting our first choice would be repeating the last selection, go for the
        # second choice instead. This will keep us pickwalking in a consistant way
        if not previouslySelected:
            selectList.append(firstChoice)
        else:
            selectList.append(secondChoice)


    previousParallelSelection = pymel.ls(selection=True, flatten=True)
    previousDirection = selectGroup
    pymel.select(selectList)


def getMMatrix(object, matrixType='worldMatrix'):
    matrix = pymel.getAttr(object+".%s" % matrixType)
    matrixList = []
    for row in matrix:
        for n in row:
            matrixList.append(n)

    mMatrix = OpenMaya.MMatrix()
    OpenMaya.MScriptUtil.createMatrixFromList(matrixList, mMatrix)
    return mMatrix

def transformPoint(transformObject, point):

    objMat = getMMatrix(transformObject, matrixType='worldInverseMatrix')
    aPoint = OpenMaya.MPoint(point[0], point[1], point[2])
    result = aPoint * objMat

    return result.x, result.y, result.z

def getInCameraSpace(inputValue):
    camera = getCurrentCamera()
    if isinstance(inputValue, pymel.general.MeshVertex):
        point = inputValue.getPosition(space='world')
    else:
        point = inputValue
    cameraSpacePositionOfPoint = transformPoint(camera, point)
    return cameraSpacePositionOfPoint

def getCurrentCamera():
    panelUnderPointer = pymel.getPanel( underPointer=True )
    camera = 'persp'
    if panelUnderPointer:
        if 'modelPanel' in panelUnderPointer:
            currentPanel = pymel.getPanel(withFocus=True)
            currentPanel = currentPanel.split('|')[-1]
            camera = pymel.modelPanel(currentPanel, query=True, camera=True)

    return camera


def getParallelVertData(perpendicularMode=False):
    '''returns the verts that are parralel (like an edge ring) to the selected verts.
    returns a list of lists with each list being [selectedPoint, aboveSelectedPoint, belowSelectedPoint]'''

    global previousSelection

    selection = pymel.ls(selection=True, flatten=True)

    previousSelection = selection

    if len(selection) == 1:
        getSingleParallelVertDict(selection)
    else:
        getLineParallelVertsDict(selection)

def getSingleParallelVertDict(selection):

    global vertDict
    global parallelRelationshipDict
    global vertPositionDict
    global selectionIndices
    global vertPairSequence

    vertDict = {}    #key=vertIndex, Value=MeshVertex <pymelNode>
    parallelRelationshipDict = {}    #key=vertIndex, Value={upper:upperVertIndex, lower:lowerVertIndex, right:rightVertIndex, left:leftVertIndex}
    vertPositionDict = {}    #key=vertIndex, Value=(worldPositionX, worldPositionY, worldPositionZ)
    selectionIndices = []    #key=vertIndex, Value=MeshVertex <pymelNode>

    faceDict = {}    #key=vertIndex, Value=MeshFace <pymelNode>
    edgeDict = {}    #key=vertIndex, Value=MeshEdge <pymelNode>

    facesOfVertDict = {}    #key=vertIndex, Value=[connectedFaceIndex[0], connectedFaceIndex[1]...]
    vertsOfFaceDict = {}    #key=faceIndex, Value=[connectedVertIndex[0], connectedVertIndex[1]...]

    edgesOfVertDict = {}    #key=edgeIndex, Value=[connectedVertIndex[0], connectedVertIndex[1]...]
    vertsOfEdgeDict = {}    #key=vertIndex, Value=[connectedEdgeIndex[0], connectedEdgeIndex[1]...]

    node = selection[0].node()

    # finds nessisary component relationship data one, to prevent redundancy
    mapComponentRelationships(selection[0], node=node, faceDict=faceDict, edgeDict=edgeDict, facesOfVertDict=facesOfVertDict,
                              vertsOfFaceDict=vertsOfFaceDict,  edgesOfVertDict=edgesOfVertDict, vertsOfEdgeDict=vertsOfEdgeDict,)

    # values we are trying to find
    rightVert = None
    leftVert = None
    topVert = None
    bottomVert = None

    # the ordered pairs of verts that will be availible to blend from
    vertPairSequence = []

    # find the connected Verts
    connectedVerts = []
    for edgeIndex in edgesOfVertDict[selectionIndices[0]]:
        vertIndices = vertsOfEdgeDict[edgeIndex]
        for vertIndex in vertIndices:
            if vertIndex != selectionIndices[0]:
                connectedVerts.append(vertIndex)
    lenOfConnectedPoints = len(connectedVerts)

    # populate the dict that has the worldSpace postion of each vert
    for vertIndex in connectedVerts:
        vertPositionDict[vertIndex] = vertDict[vertIndex].getPosition(space='world')

    # make a dict that has the cameraspace position of each vert
    cameraSpaceDict = {}
    for vertIndex in connectedVerts:
        cameraSpaceDict[vertIndex] = getInCameraSpace(vertPositionDict[vertIndex])

    # Find Right
    rightVert = connectedVerts[0]
    for vertIndex in connectedVerts:
        if cameraSpaceDict[vertIndex][0] < cameraSpaceDict[rightVert][0]:
            rightVert = vertIndex


    # if there are more than 4 connected points
    if lenOfConnectedPoints > 4:
        orderedPoints = [rightVert]

        count = 0
        while len(orderedPoints) != len(connectedVerts):

            for faceIndex in facesOfVertDict[orderedPoints[-1]]:
                for vertIndex in vertsOfFaceDict[faceIndex]:
                    if vertIndex in connectedVerts:
                        if vertIndex not in orderedPoints:
                            orderedPoints.append(vertIndex)
                            break
                            break

            count += 1
            if count > 9000:
                pymel.error('way to big son')


        vertPairSequence = []
        # populate vertPairSequence
        for iA, indexA in enumerate(orderedPoints):
            for iB, indexB in enumerate(orderedPoints):
                if not iA == iB:
                    vertPairSequence.append([(orderedPoints[iA], orderedPoints[iB])])


    # if there are exactly 4 connected points
    elif lenOfConnectedPoints == 4:

        # Find Left
        facesConnectedToRight = facesOfVertDict[rightVert]
        possibleLeftVerts = []
        for vertIndex in connectedVerts:
            if vertIndex != rightVert:
                connectedFaces = facesOfVertDict[vertIndex]
                connectedToRight = False
                for faceIndex in connectedFaces:
                    if faceIndex in facesConnectedToRight:
                        connectedToRight = True
                        break
                if not connectedToRight:
                    possibleLeftVerts.append(vertIndex)

        leftVert = possibleLeftVerts[0]
        for vertIndex in possibleLeftVerts:
            if cameraSpaceDict[vertIndex][0] < cameraSpaceDict[leftVert][0]:
                leftVert = int(vertIndex)

        # Find Top
        possibleTopVerts = []
        for vertIndex in connectedVerts:
            if vertIndex not in [rightVert, leftVert]:
                possibleTopVerts.append(vertIndex)

        topVert = possibleTopVerts[0]
        for vertIndex in possibleTopVerts:
            if cameraSpaceDict[vertIndex][1] > cameraSpaceDict[topVert][1]:
                topVert = int(vertIndex)

        # Find Bottom
        possibleBottomVerts = []
        for vertIndex in connectedVerts:
            if vertIndex not in [rightVert, leftVert, topVert]:
                possibleBottomVerts.append(vertIndex)

        bottomVert = possibleBottomVerts[0]
        for vertIndex in possibleBottomVerts:
            if cameraSpaceDict[vertIndex][1] <= cameraSpaceDict[bottomVert][1]:
                bottomVert = int(vertIndex)

        # populate vertPairSequence
        vertPairSequence = [[(leftVert, rightVert)], [(topVert, bottomVert)],]


    # if there exactly 3 connected points
    elif lenOfConnectedPoints == 3:
        # Find Left
        possibleLeftVerts = []
        for vertIndex in connectedVerts:
            if vertIndex != rightVert:
                possibleLeftVerts.append(vertIndex)

        leftVert = possibleLeftVerts[0]
        for vertIndex in possibleLeftVerts:
            if cameraSpaceDict[vertIndex][0] <= cameraSpaceDict[leftVert][0]:
                leftVert = vertIndex

        # Find Top
        possibleTopVerts = []
        for vertIndex in connectedVerts:
            possibleTopVerts.append(vertIndex)

        topVert = possibleTopVerts[0]
        for vertIndex in possibleTopVerts:
            if cameraSpaceDict[vertIndex][1] >= cameraSpaceDict[topVert][1]:
                topVert = vertIndex

        # Find Bottom
        possibleBottomVerts = []
        for vertIndex in connectedVerts:
            if vertIndex != topVert:
                possibleBottomVerts.append(vertIndex)

        bottomVert = possibleBottomVerts[0]
        for vertIndex in possibleBottomVerts:
            if cameraSpaceDict[vertIndex][1] <= cameraSpaceDict[bottomVert][1]:
                bottomVert = vertIndex

        for vertIndex in possibleLeftVerts:
            if vertIndex != rightVert and vertIndex != leftVert:
                thirdVert = vertIndex
                break

        # populate vertPairSequence
        vertPairSequence = [[(leftVert, rightVert)], [(leftVert, thirdVert)], [(thirdVert, rightVert)], ]


    # if there exactly 2 connected points
    elif lenOfConnectedPoints == 2:
        # Find Left
        for vertIndex in connectedVerts:
            if vertIndex != rightVert:
                leftVert = vertIndex

        # Find Top
        topVert = connectedVerts[0]
        for vertIndex in connectedVerts:
            if cameraSpaceDict[vertIndex][1] >= cameraSpaceDict[topVert][1]:
                topVert = vertIndex

        # Find Bottom
        for vertIndex in connectedVerts:
            if vertIndex != topVert:
                bottomVert = vertIndex

        vertPairSequence = [[(leftVert, rightVert)]]


    else:
        pymel.error('how did you manage to find a point with 0 connected edges?!')



    parallelVertDict = {
        'top' :topVert,
        'bottom' :bottomVert,
        'right' :rightVert,
        'left'  :leftVert,
    }

    if topVert:
        rangeOfX = abs(cameraSpaceDict[topVert][0] - cameraSpaceDict[bottomVert][0])
        rangeOfY = abs(cameraSpaceDict[topVert][1] - cameraSpaceDict[bottomVert][1])
        if rangeOfX > rangeOfY:
            parallelVertDict['top'] = bottomVert
            parallelVertDict['bottom'] = topVert

    parallelRelationshipDict[selectionIndices[0]] = parallelVertDict


def getLineParallelVertsDict(selection):
    '''returns the verts that are parralel (like an edge ring) to the selected line of verts.
    '''

    global vertDict
    global parallelRelationshipDict
    global vertPositionDict
    global selectionIndices
    global vertPairSequence

    vertDict = {}    #key=vertIndex, Value=MeshVertex <pymelNode>
    parallelRelationshipDict = {}    #key=vertIndex, Value={upper:upperVertIndex, lower:lowerVertIndex, right:rightVertIndex, left:leftVertIndex}
    vertPositionDict = {}    #key=vertIndex, Value=(worldPositionX, worldPositionY, worldPositionZ)
    selectionIndices = []    #key=vertIndex, Value=MeshVertex <pymelNode>

    faceDict = {}    #key=vertIndex, Value=MeshFace <pymelNode>
    facesOfVertDict = {}    #key=vertIndex, Value=[connectedFaceIndex[0], connectedFaceIndex[1]...]
    vertsOfFaceDict = {}    #key=faceIndex, Value=[connectedVertIndex[0], connectedVertIndex[1]...]

    node = selection[0].node()

    for eachVert in selection:
        mapComponentRelationships(eachVert, node=node, faceDict=faceDict, facesOfVertDict=facesOfVertDict, vertsOfFaceDict=vertsOfFaceDict)

    # find an end point to use as a starting point
    endPoint = None
    for vertIndex in selectionIndices:

        connectedSelectionVerts = []
        for connectedFaceIndex in facesOfVertDict[vertIndex]:
            for connectedVertIndex in vertsOfFaceDict[connectedFaceIndex]:
                if connectedVertIndex != vertIndex:
                    if connectedVertIndex in selectionIndices:
                        if connectedVertIndex not in connectedSelectionVerts:
                            connectedSelectionVerts.append(connectedVertIndex)

        if len(connectedSelectionVerts) == 1:
            endPoint = vertIndex
            break

    if not endPoint: # selectin is continus loop
        endPoint = vertIndex

    # get ordered Selection
    orderedSelection = [endPoint]
    selectionStack = [endPoint]
    while selectionStack:
        selectionVertIndex = selectionStack.pop(0)
        selectionVert = vertDict[selectionVertIndex]

        for faceIndex in facesOfVertDict[selectionVertIndex]:
            vertIndices = vertsOfFaceDict[faceIndex]
            for vertIndex in vertIndices:
                if vertIndex != selectionVertIndex:
                    if vertIndex in selectionIndices:
                        if vertIndex not in orderedSelection:
                            orderedSelection.append(vertIndex)
                            selectionStack.append(vertIndex)
                            break
            if selectionStack:
                break

    last = len(orderedSelection)-1
    parallelSetA = []
    parallelSetB = []
    for i, vertIndex in enumerate(orderedSelection):

        requiredMatches = 2
        if i == last:
            matchIndices = [vertIndex, orderedSelection[i-1]]
        else:
            matchIndices = [vertIndex, orderedSelection[i+1]]


        # find connected faces who contain both the matchIndices
        matchingFaces = []
        faceIndices = facesOfVertDict[vertIndex]
        for faceIndex in faceIndices:

            faceVertIndices = vertsOfFaceDict[faceIndex]
            matchingFacePoints = 0
            for faceVertIndex in faceVertIndices:
                if faceVertIndex in matchIndices:
                    matchingFacePoints += 1

            if matchingFacePoints == requiredMatches:
                matchingFaces.append(faceIndex)

        for matchingFaceIndex in matchingFaces:
            facePoints = vertsOfFaceDict[matchingFaceIndex]
            lenOfFacePoints = len(facePoints)
            indexOfSelf = facePoints.index(vertIndex)

            if facePoints[indexOfSelf-1] == matchIndices[1]:
                if indexOfSelf+1 == lenOfFacePoints:
                    parallelVertIndex = facePoints[0]
                else:
                    parallelVertIndex = facePoints[indexOfSelf+1]
            else:
                parallelVertIndex = facePoints[indexOfSelf-1]

            if not parallelSetA: # if first item
                parallelSetA.append(parallelVertIndex)

            else:
                isConnectedToA = False

                # is the parallel vert connected to the last point in parallelSetA?
                for connectedFaceIndex in facesOfVertDict[parallelVertIndex]:
                    for connectedFaceVertexIndex in vertsOfFaceDict[connectedFaceIndex]:
                        if connectedFaceVertexIndex == parallelSetA[-1]:
                            parallelSetA.append(parallelVertIndex)
                            isConnectedToA = True
                            break
                    if isConnectedToA:
                        break

                if not isConnectedToA:
                    parallelSetB.append(parallelVertIndex)

    # determin which is top and which is bottom of the parallel sets
    for vertIndex in parallelSetA+parallelSetB:
        vertPositionDict[vertIndex] = vertDict[vertIndex].getPosition(space='world')

    parallelSetA_xSum = 0
    parallelSetA_ySum = 0
    parallelSetB_xSum = 0
    parallelSetB_ySum = 0

    for vertIndex in parallelSetA:
        x, y, z = getInCameraSpace(vertPositionDict[vertIndex])
        parallelSetA_xSum += x
        parallelSetA_ySum += y

    for vertIndex in parallelSetB:
        x, y, z = getInCameraSpace(vertPositionDict[vertIndex])
        parallelSetB_xSum += x
        parallelSetB_ySum += y

    rangeOfX = abs(parallelSetA_ySum - parallelSetB_ySum)
    rangeOfY = abs(parallelSetA_xSum - parallelSetB_xSum)

    verticalHorizontal = 'vertical'
    if rangeOfX > rangeOfY:
        verticalHorizontal = 'horizontal'

    if verticalHorizontal == 'vertical':
        if parallelSetA_xSum > parallelSetB_xSum:
            topVerts = parallelSetA
            bottomVerts = parallelSetB
        else:
            topVerts = parallelSetB
            bottomVerts = parallelSetA

    elif verticalHorizontal == 'horizontal':
        if parallelSetA_ySum > parallelSetB_ySum:
            topVerts = parallelSetA
            bottomVerts = parallelSetB

        else:
            topVerts = parallelSetB
            bottomVerts = parallelSetA

    vertPairSequence = []
    vertPairSequenceA = []
    for i, vertIndex in enumerate(orderedSelection):
        vertPairSequenceA.append((bottomVerts[i], topVerts[i]))
        parallelVertDict = {
            'top' :topVerts[i],
            'bottom' :bottomVerts[i],
            'right' :topVerts[i],
            'left'  :bottomVerts[i],
        }

        parallelRelationshipDict[vertIndex] = parallelVertDict
    vertPairSequence.append(vertPairSequenceA)

def mapComponentRelationships(vert, node=None, faceDict=None, edgeDict=None, facesOfVertDict=None,
                              vertsOfFaceDict=None, edgesOfVertDict=None, vertsOfEdgeDict=None,):
    global vertDict
    global selectionIndices

    vertIndex = vert.currentItemIndex()
    if not node:
        node = vert.node()

    selectionIndices.append(vertIndex)
    if vertIndex not in vertDict:
        vertDict[vertIndex] = vert

    # map connected faces
    if facesOfVertDict != None:
        connectedFaces = vert.connectedFaces()
        for connectedFace in connectedFaces:
            faceIndex = connectedFace.currentItemIndex()

            if faceIndex not in vertsOfFaceDict:
                connectedVertIndices = connectedFace.getVertices()

                vertsOfFaceDict[faceIndex] = []
                for connectedVertIndex in connectedVertIndices:

                    # add to vertsOfFaceDict
                    vertsOfFaceDict[faceIndex].append(connectedVertIndex)

                    # add to facesOfVertDict
                    if connectedVertIndex not in facesOfVertDict:
                        facesOfVertDict[connectedVertIndex] = [faceIndex]

                    if faceIndex not in facesOfVertDict[connectedVertIndex]:
                        facesOfVertDict[connectedVertIndex].append(faceIndex)

                    # add to vertDict
                    if connectedVertIndex not in vertDict:
                        vertDict[connectedVertIndex] = node.vtx[connectedVertIndex]

                # add to faceDict
                if faceIndex not in faceDict:
                    faceDict[faceIndex] = connectedFace

    # map connected edges
    if edgesOfVertDict != None:
        connectedEdges = vert.connectedEdges()
        for connectedEdge in connectedEdges:
            edgeIndex = connectedEdge.currentItemIndex()
            #if edgeIndex not in facesOfVertDict:

            connectedVertIndices = []
            for vertex in connectedEdge.connectedVertices():
                vertIndex = vertex.currentItemIndex()
                connectedVertIndices.append(vertIndex)

                # add to vertDict
                if vertIndex not in vertDict:
                    vertDict[vertIndex] = vertex

            vertsOfEdgeDict[edgeIndex] = []
            for connectedVertIndex in connectedVertIndices:

                # add to vertsOfEdgeDict
                vertsOfEdgeDict[edgeIndex].append(connectedVertIndex)

                # add to edgesOfVertDict
                if connectedVertIndex not in edgesOfVertDict:
                    edgesOfVertDict[connectedVertIndex] = [edgeIndex]

                if edgeIndex not in edgesOfVertDict[connectedVertIndex]:
                    edgesOfVertDict[connectedVertIndex].append(edgeIndex)

            # add to edgeDict
            if edgeIndex not in edgeDict:
                edgeDict[edgeIndex] = connectedEdge


#def pasteSkinWeights_fromStrandStartToEnd(verts=None, soft=False):

    #paintMapDict = getCurrentPaintMapDict()
    ##nodeType, deformerName, attrName = paintMapString.split('.')[:3]

    #components = verts
    #if not components:
        #components = pymel.ls(selection=True, flatten=True)

    #componentStrand = ka_geometry.getAsStrand(components)
    #strandStart = componentStrand[0]
    #strandEnd = componentStrand[-1]

    #strandLength = 0.0
    #shape = componentStrand[0].node()
    #origShape = ka_deformers.getOrigShape(shape)
    #previousComponentPosition = None
    #strandLength = 0.0
    #strandComponentLengths = []

    #for i, component in enumerate(componentStrand):
        #componentString = str(component).split('.')[-1]

        #component = pymel.ls('%s.%s' % (str(origShape), componentString))[0]
        #componentPosition = pymel.xform(component, query=True, translation=True, worldSpace=False)

        #if previousComponentPosition != None:
            #distance = ka_math.distanceBetween(previousComponentPosition, componentPosition)
            #strandLength += distance
            #previousComponentPosition = componentPosition

        #else:
            #previousComponentPosition = componentPosition

        #strandComponentLengths.append(strandLength)

    #copyWeights(verts=[strandEnd, strandStart])

    #ratioSegments = 200.0/(len(componentStrand)-1.0)
    #last = len(componentStrand) - 1
    #for i, component in enumerate(componentStrand):
        #if i == 0 or i == last:
            #pass
        #else:
            #if soft:
                #percentOfTotal = strandComponentLengths[i]/strandLength
                #weightedAverage = 200.0 * percentOfTotal

                #weightedAverage = ka_math.softenRange(weightedAverage, minValue=0.0, maxValue=200.0, d=200.0)

            #else:
                #percentOfTotal = strandComponentLengths[i]/strandLength
                #weightedAverage = 200.0 * percentOfTotal

            #OOOOOOO = "weightedAverage"; print '%s: ' % OOOOOOO, eval(OOOOOOO), ' ', type(eval(OOOOOOO))
            #pasteWeights(verts=[component], weightedAverage=weightedAverage)



def transferSkinOneToMany(sourceObject="", targetObjects=""):
    selectedObjects = pymel.ls(selection=True, long=True)

    if sourceObject == "":
        sourceObject = selectedObjects[0]

    if targetObjects == "":
        targetObjects = selectedObjects[1:]

    sourceSkinClusterNode = findRelatedSkinCluster(sourceObject)
    sourceSkinInfluenceList = getInfluences(sourceObject)

    skinClusterKwargs = {}
    for key in ['maximumInfluences', 'obeyMaxInfluences',]:
        kwargs = {key:True}
        skinClusterKwargs[key] = pymel.skinCluster(sourceSkinClusterNode, query=True, **kwargs)

    skinningMethod = sourceSkinClusterNode.skinningMethod.get()
    useComponents = sourceSkinClusterNode.useComponents.get()
    normalizeWeights = sourceSkinClusterNode.normalizeWeights.get()
    deformUserNormals = sourceSkinClusterNode.deformUserNormals.get()

    for targetObject in targetObjects:
        targetObjectSkinCluster = findRelatedSkinCluster(targetObject)
        if not targetObjectSkinCluster:
            pymel.select(sourceSkinInfluenceList)
            pymel.select(targetObject, add=True)
            targetObjectSkinCluster = pymel.skinCluster(removeUnusedInfluence=False, toSelectedBones=True, **skinClusterKwargs)

        targetObjectSkinCluster.skinningMethod.set(skinningMethod)
        targetObjectSkinCluster.useComponents.set(useComponents)
        targetObjectSkinCluster.normalizeWeights.set(normalizeWeights)
        targetObjectSkinCluster.deformUserNormals.set(deformUserNormals)

        pymel.copySkinWeights( sourceSkin=sourceSkinClusterNode, destinationSkin=targetObjectSkinCluster, noMirror=True, influenceAssociation = 'oneToOne', surfaceAssociation = 'closestPoint')

    pymel.select(targetObjects, replace=True)


def transferSkinManyToOne(sourceObjects=None, targetObject=None):
    selectedObjects = pymel.ls(selection=True)

    if sourceObjects == None:
        sourceObjects = selectedObjects[:-1]

    if targetObject == None:
        targetObject = selectedObjects[-1]

    sourceSkinClusterNodes = []
    sourceSkinInfluenceList = []
    for sourceObject in sourceObjects:
        skinCluster = findRelatedSkinCluster(sourceObject)
        sourceSkinClusterNodes.append(skinCluster)

        influences = getInfluences(sourceObject)
        for influence in influences:
            if influence not in sourceSkinInfluenceList:
                sourceSkinInfluenceList.append(influence)

    # figure out kwargs to recreate skin cluster with
    skinClusterKwargs = {}
    skinClusterSkinningMethod = None
    skinClusterUseComponents = None
    skinClusterNormalizeWeights = None
    skinClusterDeformUserNormals = None
    for i, sourceObject in enumerate(sourceObjects):
        for key in ['maximumInfluences', 'obeyMaxInfluences',]:
            kwargs = {key:True}
            value = pymel.skinCluster(sourceSkinClusterNodes[i], query=True, **kwargs)
            if key in skinClusterKwargs and value != skinClusterKwargs[key]:
                pymel.warning('%s flag value is inconsistant between skinClusters' % key)
            skinClusterKwargs[key] = value

        skinningMethod = sourceSkinClusterNodes[i].skinningMethod.get()
        if skinClusterSkinningMethod != None and skinningMethod != skinClusterSkinningMethod:
            pymel.warning('skinningMethod is inconsistant between skinClusters')
        skinClusterSkinningMethod = skinningMethod

        useComponents = sourceSkinClusterNodes[i].useComponents.get()
        if skinClusterUseComponents != None and useComponents != skinClusterUseComponents:
            pymel.warning('useComponents is inconsistant between skinClusters')
        skinClusterUseComponents = useComponents

        normalizeWeights = sourceSkinClusterNodes[i].normalizeWeights.get()
        if skinClusterNormalizeWeights != None and normalizeWeights != skinClusterNormalizeWeights:
            pymel.warning('normalizeWeights is inconsistant between skinClusters')
        skinClusterNormalizeWeights = normalizeWeights

        deformUserNormals = sourceSkinClusterNodes[i].deformUserNormals.get()
        if skinClusterDeformUserNormals != None and deformUserNormals != skinClusterDeformUserNormals:
            pymel.warning('deformUserNormals is inconsistant between skinClusters')
        skinClusterDeformUserNormals = deformUserNormals

    # create new skin cluster or add influences if nessisary
    targetSkinClusterNode = findRelatedSkinCluster(targetObject)
    if not targetSkinClusterNode:
        pymel.select(sourceSkinInfluenceList)
        pymel.select(targetObject, add=True)

        targetSkinClusterNode = pymel.skinCluster(removeUnusedInfluence=False, toSelectedBones=True, **skinClusterKwargs)
    else:
        targetInfluences = getInfluences(targetSkinClusterNode)
        for influence in sourceSkinInfluenceList:
            if influence not in targetInfluences:
                pymel.skinCluster(targetSkinClusterNode, edit=True, addInfluence=influence, useGeometry=False, lockWeights=True, dropoffRate=4.0, weight=0.0)

    targetSkinClusterNode.skinningMethod.set(skinClusterSkinningMethod)
    targetSkinClusterNode.useComponents.set(skinClusterUseComponents)
    targetSkinClusterNode.normalizeWeights.set(skinClusterNormalizeWeights)
    targetSkinClusterNode.deformUserNormals.set(skinClusterDeformUserNormals)

    # copy weight values
    pymel.select(sourceObjects)
    pymel.select(targetObject, add=True)

    pymel.copySkinWeights( noMirror=True, influenceAssociation='oneToOne', surfaceAssociation='closestPoint', smooth=True)

    pymel.select(targetObject, replace=True)



def transferSecondaryToPrimarySelection():

    # get source and target objects
    sourceShapes = []
    for item in ka_selection.getStoredSelection():
        node = item.node()
        if hasattr(node, 'getShape'):
            shape = node.getShape()
        else:
            shape = node

        if shape not in sourceShapes:
            sourceShapes.append(shape)

    targetItems = pymel.ls(selection=True, flatten=True)
    targetItemsDict = {}
    targetShapes = []
    for item in targetItems:
        node = item.node()
        if hasattr(node, 'getShape'):
            shape = node.getShape()
        else:
            shape = node

        if shape not in targetItemsDict:
            targetItemsDict[shape] = []

        targetItemsDict[shape].append(item)

        if shape not in targetShapes:
            targetShapes.append(shape)

    # get skinClusters and influences
    sourceSkinClusterNodes = []
    sourceSkinInfluenceList = []
    for sourceShape in sourceShapes:
        skinCluster = findRelatedSkinCluster(sourceShape)
        sourceSkinClusterNodes.append(skinCluster)

        OOOOOOO = "sourceShape"; print '%s= ' % OOOOOOO, eval(OOOOOOO), ' #', type(eval(OOOOOOO))
        OOOOOOO = "skinCluster"; print '%s= ' % OOOOOOO, eval(OOOOOOO), ' #', type(eval(OOOOOOO))
        influences = getInfluences(skinCluster=skinCluster)
        for influence in influences:
            if influence not in sourceSkinInfluenceList:
                sourceSkinInfluenceList.append(influence)

    # figure out kwargs to recreate skin cluster with
    skinClusterKwargs = {}
    skinClusterSkinningMethod = None
    skinClusterUseComponents = None
    skinClusterNormalizeWeights = None
    skinClusterDeformUserNormals = None
    for i, sourceShape in enumerate(sourceShapes):
        for key in ['maximumInfluences', 'obeyMaxInfluences',]:
            kwargs = {key:True}
            value = pymel.skinCluster(sourceSkinClusterNodes[i], query=True, **kwargs)
            if key in skinClusterKwargs and value != skinClusterKwargs[key]:
                pymel.warning('%s flag value is inconsistant between skinClusters' % key)
            skinClusterKwargs[key] = value

        skinningMethod = sourceSkinClusterNodes[i].skinningMethod.get()
        if skinClusterSkinningMethod != None and skinningMethod != skinClusterSkinningMethod:
            pymel.warning('skinningMethod is inconsistant between skinClusters')
        skinClusterSkinningMethod = skinningMethod

        useComponents = sourceSkinClusterNodes[i].useComponents.get()
        if skinClusterUseComponents != None and useComponents != skinClusterUseComponents:
            pymel.warning('useComponents is inconsistant between skinClusters')
        skinClusterUseComponents = useComponents

        normalizeWeights = sourceSkinClusterNodes[i].normalizeWeights.get()
        if skinClusterNormalizeWeights != None and normalizeWeights != skinClusterNormalizeWeights:
            pymel.warning('normalizeWeights is inconsistant between skinClusters')
        skinClusterNormalizeWeights = normalizeWeights

        deformUserNormals = sourceSkinClusterNodes[i].deformUserNormals.get()
        if skinClusterDeformUserNormals != None and deformUserNormals != skinClusterDeformUserNormals:
            pymel.warning('deformUserNormals is inconsistant between skinClusters')
        skinClusterDeformUserNormals = deformUserNormals


    for i, targetShape in enumerate(targetShapes):

        # create new skin cluster or add influences if nessisary
        targetSkinClusterNode = findRelatedSkinCluster(targetShape)
        if not targetSkinClusterNode:
            pymel.select(sourceSkinInfluenceList)
            pymel.select(targetShape, add=True)

            targetSkinClusterNode = pymel.skinCluster(removeUnusedInfluence=False, toSelectedBones=True, **skinClusterKwargs)

        else:
            targetInfluences = getInfluences(targetSkinClusterNode)
            for influence in sourceSkinInfluenceList:
                if influence not in targetInfluences:
                    pymel.skinCluster(targetSkinClusterNode, edit=True, addInfluence=influence, useGeometry=False, lockWeights=True, dropoffRate=4.0, weight=0.0)

        targetSkinClusterNode.skinningMethod.set(skinClusterSkinningMethod)
        targetSkinClusterNode.useComponents.set(skinClusterUseComponents)
        targetSkinClusterNode.normalizeWeights.set(skinClusterNormalizeWeights)
        targetSkinClusterNode.deformUserNormals.set(skinClusterDeformUserNormals)

        # copy weight values
        pymel.select(sourceShapes)
        pymel.select(targetItemsDict[targetShape], add=True)

        pymel.copySkinWeights( noMirror=True, influenceAssociation='oneToOne', surfaceAssociation='closestPoint', smooth=True)

        pymel.select(targetItems, replace=True)





def xferComponentWeights_fromStoredSelection():
    targetComponents = pymel.ls(selection=True, long=True)
    selectedObjects = ka_selection.getStoredSelection()
    xferComponentWeights(selectedObjects[0], targetComponents)


def xferComponentWeights(sourceObject=None, targetComponents=None):
    """selection A should be a point set, and it will transfer its weights to the nearest point for
    all other selected verts"""

    selectedObjects = pymel.ls(selection=True, long=True)

    if not sourceObject:
        sourceObject = selectedObjects[0].node()

    sourceSkinClusterNode = findRelatedSkinCluster(sourceObject)
    sourceSkinInfluenceList = getInfluences(sourceObject)

    destinationObjects = []
    sourceComponents = []
    targetComponents = []

    for each in selectedObjects:
        if each.node() == sourceObject:
            sourceComponents.append(each)

        else:
            if each.node() not in destinationObjects:
                destinationObjects.append(each.node())
            targetComponents.append(each)


    #find all influences that are in one skin, but not the other
    for destinationObject in destinationObjects:
        destinationSkinClusterNode = findRelatedSkinCluster(destinationObject)
        destinationSkinInfluenceList = getInfluences(destinationObject)

        missingInfuences = []
        for influence in sourceSkinInfluenceList:
            if influence not in destinationSkinInfluenceList:
                missingInfuences.append(influence)

        pymel.skinCluster(destinationSkinClusterNode, edit=True, addInfluence=missingInfuences, weight=0.0)


    #oneToOne
    for destinationObject in destinationObjects:
        pymel.select(clear=True)
        pymel.select(destinationObject, add=True)
        mel.eval('changeSelectMode -component;')
        mel.eval('setComponentPickMask "Point" true;')
        pymel.select(targetComponents, add=True)
        pymel.select(sourceObject, add=True)
        pymel.select(targetComponents, add=True)

        pymel.copySkinWeights(noMirror=True, surfaceAssociation='closestPoint', influenceAssociation=['label', 'closestBone', 'closestJoint',] )

    pymel.select(selectedObjects)
    mel.eval('changeSelectMode -component;')
    mel.eval('setComponentPickMask "Point" true;')

def _pruneSmallWeights(skinCluster, pruneMax, **kwArgs):
    verbose = kwArgs.get('verbose', False)
    influences = self.getSkinInfluences(self.mesh)
    lenOfInfluences = str(len(influences))

    #get point weights
    cmdGetString = 'cmds.getAttr(".weightList['+i+'].weights[0:'+lenOfInfluences+']")'
    values = cmds.getAttr('.weightList['+i+'].weights[0:'+lenOfInfluences+']')

def pruneSmallWeights(**kwArgs):
    kwArgs['verbose'] = True
    selection = pymel.ls(selection=True)

    for geo in selection:
        skinCluster = findRelatedSkinCluster(geo, silent=True)
        if skinCluster:
            _pruneSmallWeights(skinCluster, 0.0001 **kwArgs)


#UTILITYS#############################################################################################################################################################################
def findRelatedSkinCluster(*args, **kwArgs):
    '''return the skinCluster for the input, which will be a user selection'''
    return ka_skinCluster.findRelatedSkinCluster(*args, **kwArgs)

def getInfluences(*args, **kwArgs):
    '''return the influences attached to the skinCluster'''
    return ka_skinCluster.getInfluences(*args, **kwArgs)


def deleteAllBindPoses():
    pass

def refreshMayaPaintUI():
    mel.eval('refreshAE')
    mel.eval('artAttrSkinToolScript 4')
    mel.eval('artAttrSkinPaintCtx -e -showactive true `currentCtx`;')

def applyJointColors():
    selection = pymel.ls(selection=True, flatten=True)
    influenceList = getInfluences()
    skinCluster = findRelatedSkinCluster(selection[0])

    locked = []
    unlocked = []

    for each in influenceList:
        if pymel.getAttr(each+'.lockInfluenceWeights'):
            #pymel.color( each, userDefined=8 )
            locked.append(each)
        else:
            unlocked.append(each)

    if locked:
        pymel.color( locked, userDefined=8 )
    if unlocked:
        pymel.color( unlocked, userDefined=7 )


def createSkinCluster():
    pymel.skinCluster(obeyMaxInfluences=False, maximumInfluences=5, toSelectedBones=True, ignoreHierarchy=False, skinMethod=0, normalizeWeights=1, removeUnusedInfluence=False)

#def addInfluence():
    #selection = pymel.ls(selection=True)

    #skinClusters = []
    #influencesToAdd = []
    #for item in selection:
        #skinCluster = findRelatedSkinCluster(item)
        #if skinCluster:
            #if skinCluster not in skinClusters:
                #skinClusters.append(skinCluster)

        #else:
            #if item.nodeType() == 'joint':
                #influencesToAdd.append(item)

    #for skinCluster in skinClusters:
        #for influence in influencesToAdd:
            #skinClusterInfluences = getInfluences(skinCluster)
            #if influence not in skinClusterInfluences:
                #pymel.skinCluster(skinCluster, edit=True, addInfluence=influence, useGeometry=False, lockWeights=True, dropoffRate=4.0, weight=0.0)


def addInfluence(joints=[], skinClusters=[]):
    if not joints:
        selection = pymel.ls(selection=True)
        for item in selection:
            if item.isinstance(item, pymel.nt.Joint):
                joints.append(item)

            else:
                skinCluster = findRelatedSkinCluster(item)
                if skinCluster:
                    skinClusters.append(skinCluster)

    print 'adding:', joints, skinClusters
    addedInfluenceIndicesLists = []
    for skinCluster in skinClusters:
        multiIndices = skinCluster.matrix.get(multiIndices=True)
        if not multiIndices:
            multiIndices = [0]

        addedInfluenceIndices = []
        i = 0
        for joint in joints:
            skinClusterInfluences = getInfluences(skinCluster)
            if joint not in skinClusterInfluences:
                pymel.skinCluster(skinCluster, edit=True, addInfluence=joint, useGeometry=False, lockWeights=True, dropoffRate=4.0, weight=0.0)
                index = multiIndices[-1]+1+i
                #joint.worldMatrix >> skinCluster.matrix[index]
                #joint.lockInfluenceWeights >> skinCluster.matrix[index]
                #skinCluster.bindPreMatrix[index].set(joint.worldMatrix[0].get().inverse())
                addedInfluenceIndices.append(index)
                i += 1

        addedInfluenceIndicesLists.append(addedInfluenceIndices)
    return addedInfluenceIndicesLists


def getCurrentPaintMapDict(shape=None):
    """returns a string representing the currently set paint map for the selected geometry"""

    currentPaintMapDict = ka_clipBoard.get('currentPaintMapDict', {})

    # find the shape
    if not shape:
        shape = pymel.selected()[-1]
        if ka_pymel.isPyTransform(shape):
            shape = shape.getShape()
        elif isinstance(shape, pymel.general.Component):
            shape = shape.node()

    else:
        shape = ka_pymel.getAsShape(shape)

    shapeLongName = str(shape)
    shapeShortName = shape.nodeName()

    # try to find the current paint map from the clip board
    paintMapDict = currentPaintMapDict.get(shapeLongName, {})
    if not paintMapDict:
        paintMapDict = currentPaintMapDict.get(shapeLongName, {})

    if paintMapDict:
        if pymel.objExists(paintMapDict['nodeName']):
            return paintMapDict

    # return the first skinCluster map, or if none exist, the first deformer map
    paintDicts = getPaintableAttributes(shape=shape)
    for paintMapDict in paintDicts:
        if paintMapDict['nodeType'] == 'skinCluster':
            currentPaintMapDict[shapeLongName] = paintMapDict
            ka_clipBoard.add('currentPaintMapDict', currentPaintMapDict)
            return paintMapDict

    if paintDicts:
        currentPaintMapDict[shapeLongName] = paintDicts[0]
        ka_clipBoard.add('currentPaintMapDict', paintDicts[0])
        return paintDicts[0]


def getPaintableAttributes(shape=None):

    paintDicts = []

    # pars args
    if shape is None:
        shape = pymel.selected()[-1]

    shape = ka_pymel.getAsShape(shape)

    shapeName = shape.nodeName()
    shapePath = str(shape)


    # paintAttrKeys will determin what has allready been added to the list
    paintAttrKeys = {}


    # process known deformers
    deformers = ka_deformers.getDeformers(shape)
    for deformer in deformers:

        # SKIN CLUSTER --------------------------------------------------------------------------------------
        if isinstance(deformer, pymel.nt.SkinCluster):
            nodeName = deformer.nodeName()
            nodePath = str(deformer)
            nodeType = 'skinCluster'

            # skin weights - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            attributeName = 'paintWeights'

            # Check that deformer is not already in list
            paintAttrKey = '%s.%s.%s' % (nodeType, nodeName, attributeName)
            print 'paintAttrKey', paintAttrKey
            if paintAttrKey not in paintAttrKeys:
                paintAttrKeys[paintAttrKey] = None

                mapInfoDict = {}
                mapInfoDict['label'] = '%s.skinWeights' % nodeName
                mapInfoDict['ctx'] = 'artAttrCtx'
                mapInfoDict['nodeName'] = nodePath
                mapInfoDict['nodeType'] = nodeType
                mapInfoDict['attributeName'] = attributeName
                mapInfoDict['attributeShortName'] = attributeName
                mapInfoDict['setWeightAttribute'] = mapInfoDict['attributeName']+'[%s].weights[%s]'

                mapInfoDict['paintCommand'] = 'artSetToolAndSelectAttr("artAttrSkinPaintCtx", "%s.%s.%s" ) ;optionMenuGrp -e -sl 1 artAttrSkinWeightType; artAttrSkinWeightTypeCallback artAttrSkinPaintCtx;' % (nodeType, nodePath, 'paintWeights')

                paintDicts.append(mapInfoDict)

            # dual quaternion weights - - - - - - - - - - - - - - - - - - - - - - - -
            attributeName = 'blendWeights'

            # Check that deformer is not already in list
            paintAttrKey = '%s.%s.%s' % (nodeType, nodeName, attributeName)
            print 'paintAttrKey', paintAttrKey

            if paintAttrKey not in paintAttrKeys:
                paintAttrKeys[paintAttrKey] = None

                mapInfoDict = {}
                mapInfoDict['label'] = '%s.dualQuaternionWeights' % (nodeName)
                mapInfoDict['ctx'] = 'artAttrCtx'
                mapInfoDict['nodeName'] = nodePath
                mapInfoDict['nodeType'] = nodeType
                mapInfoDict['attributeName'] = attributeName
                mapInfoDict['attributeShortName'] = attributeName
                mapInfoDict['setWeightAttribute'] = mapInfoDict['attributeName']+'[%s]'

                mapInfoDict['paintCommand'] = 'artSetToolAndSelectAttr("artAttrSkinPaintCtx", "%s.%s.%s" ) ;artSkinSelectInfluence("artAttrSkinPaintCtx","blendWeight");' % ('skinCluster', 'skinCluster1', 'paintWeights')

                paintDicts.append(mapInfoDict)


        # BLEND SHAPE --------------------------------------------------------------------------------------
        elif isinstance(deformer, pymel.nt.BlendShape):
            nodeName = deformer.nodeName()
            nodePath = str(deformer)
            nodeType = 'blendShape'

            # base weights - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            attributeName = 'baseWeights'

            # Check that deformer is not already in list
            paintAttrKey = '%s.%s.%s' % (nodeType, nodeName, attributeName)
            print 'paintAttrKey', paintAttrKey

            if paintAttrKey not in paintAttrKeys:
                paintAttrKeys[paintAttrKey] = None

                if attributeName == 'baseWeights':
                    mapInfoDict = {}
                    mapInfoDict['label'] = '%s.%s' % (nodeName, attributeName)
                    mapInfoDict['ctx'] = 'artAttrCtx'
                    mapInfoDict['nodeName'] = nodePath
                    mapInfoDict['nodeType'] = nodeType
                    mapInfoDict['attributeName'] = 'inputTarget[0].baseWeights'
                    mapInfoDict['attributeShortName'] = attributeName
                    mapInfoDict['setWeightAttribute'] = mapInfoDict['attributeName']+'[%s]'

                    mapInfoDict['paintCommand'] = 'artSetToolAndSelectAttr("artAttrCtx", "%s.%s.%s"); artBlendShapeSelectTarget artAttrCtx "%s"' % (nodeType, nodePath, attributeName, attributeName)

                    paintDicts.append(mapInfoDict)

                #else:
                    #blendShape = pymel.PyNode(nodeName)
                    #indices = blendShape.inputTarget[0].inputTargetGroup.getArrayIndices()

                    #for i in indices:
                        #target = blendShape.inputTarget[0].inputTargetGroup[i].inputTargetItem[6000].inputGeomTarget.inputs()
                        #if target:
                            #target = target[0]
                            #targetName = target.nodeName()

                            #mapInfoDict = {}
                            #mapInfoDict['label'] = '%s.%s' % (nodeName, targetName)
                            #mapInfoDict['ctx'] = 'artAttrCtx'
                            #mapInfoDict['nodeName'] = nodePath
                            #mapInfoDict['nodeType'] = nodeType
                            #mapInfoDict['attributeName'] = 'inputTarget[0].inputTargetGroup[%s].targetWeights' % str(i)
                            #mapInfoDict['attributeShortName'] = attributeName
                            #mapInfoDict['setWeightAttribute'] = mapInfoDict['attributeName']+'[%s]'

                            #mapInfoDict['paintCommand'] = 'artSetToolAndSelectAttr("artAttrCtx", "%s.%s.paintTargetWeights"); artBlendShapeSelectTarget artAttrCtx "%s"' % (nodeType, nodePath, targetName)

                            #paintDicts.append(mapInfoDict)


    # process paintable attributes, *must be in select context for artBuildPaintMenu to work
    currentCtx = cmds.currentCtx()
    cmds.setToolTo('selectSuperContext')
    artBuildPaintMenuString = pymel.artBuildPaintMenu(shape)
    paintableAttrs = artBuildPaintMenuString.split()
    paintableAttrs.sort()
    for paintableAttr in paintableAttrs:
        nodeType, nodeName, attributeName, null = paintableAttr.split('.')
        paintAttrKey = '%s.%s.%s' % (nodeType, nodeName, attributeName)
        print 'paintAttrKey', paintAttrKey

        if paintAttrKey not in paintAttrKeys:
            if nodeName == shapeName:
                nodePath = shapePath
            else:
                nodePath = nodeName

            if nodeType == 'blendShape':    # Blend shape ------------------------------------------
                if attributeName == 'baseWeights':
                    mapInfoDict = {}
                    mapInfoDict['label'] = '%s.%s' % (nodeName, attributeName)
                    mapInfoDict['ctx'] = 'artAttrCtx'
                    mapInfoDict['nodeName'] = nodePath
                    mapInfoDict['nodeType'] = nodeType
                    mapInfoDict['attributeName'] = 'inputTarget[0].baseWeights'
                    mapInfoDict['attributeShortName'] = attributeName
                    mapInfoDict['setWeightAttribute'] = mapInfoDict['attributeName']+'[%s]'

                    mapInfoDict['paintCommand'] = 'artSetToolAndSelectAttr("artAttrCtx", "%s.%s.%s"); artBlendShapeSelectTarget artAttrCtx "%s"' % (nodeType, nodePath, attributeName, attributeName)

                    paintDicts.append(mapInfoDict)
                    paintAttrKeys[paintAttrKey] = None

                else:
                    blendShape = pymel.PyNode(nodeName)
                    indices = blendShape.inputTarget[0].inputTargetGroup.getArrayIndices()

                    for i in indices:
                        target = blendShape.inputTarget[0].inputTargetGroup[i].inputTargetItem[6000].inputGeomTarget.inputs()
                        if target:
                            target = target[0]
                            targetName = target.nodeName()

                            mapInfoDict = {}
                            mapInfoDict['label'] = '%s.%s' % (nodeName, targetName)
                            mapInfoDict['ctx'] = 'artAttrCtx'
                            mapInfoDict['nodeName'] = nodePath
                            mapInfoDict['nodeType'] = nodeType
                            mapInfoDict['attributeName'] = 'inputTarget[0].inputTargetGroup[%s].targetWeights' % str(i)
                            mapInfoDict['attributeShortName'] = attributeName
                            mapInfoDict['setWeightAttribute'] = mapInfoDict['attributeName']+'[%s]'

                            mapInfoDict['paintCommand'] = 'artSetToolAndSelectAttr("artAttrCtx", "%s.%s.paintTargetWeights"); artBlendShapeSelectTarget artAttrCtx "%s"' % (nodeType, nodePath, targetName)

                            paintDicts.append(mapInfoDict)
                            paintAttrKeys[paintAttrKey] = None

            elif nodeType == 'skinCluster':    # Skincluster ------------------------------------------
                mapInfoDictA = {}
                mapInfoDictA['label'] = '%s.skinWeights' % nodeName
                mapInfoDictA['ctx'] = 'artAttrCtx'
                mapInfoDictA['nodeName'] = nodePath
                mapInfoDictA['nodeType'] = nodeType
                mapInfoDictA['attributeName'] = attributeName
                mapInfoDictA['attributeShortName'] = attributeName
                mapInfoDictA['setWeightAttribute'] = mapInfoDictA['attributeName']+'[%s].weights[%s]'

                mapInfoDictA['paintCommand'] = 'artSetToolAndSelectAttr("artAttrSkinPaintCtx", "%s.%s.%s" ) ;optionMenuGrp -e -sl 1 artAttrSkinWeightType; artAttrSkinWeightTypeCallback artAttrSkinPaintCtx;' % (nodeType, nodePath, 'paintWeights')

                paintDicts.append(mapInfoDictA)

                mapInfoDictB = {}
                mapInfoDictB['label'] = '%s.dualQuaternionWeights' % (nodeName)
                mapInfoDictB['ctx'] = 'artAttrCtx'
                mapInfoDictB['nodeName'] = nodePath
                mapInfoDictB['nodeType'] = nodeType
                mapInfoDictB['attributeName'] = 'blendWeights'
                mapInfoDictB['attributeShortName'] = 'blendWeights'
                mapInfoDictB['setWeightAttribute'] = mapInfoDictB['attributeName']+'[%s]'

                mapInfoDictB['paintCommand'] = 'artSetToolAndSelectAttr("artAttrSkinPaintCtx", "%s.%s.%s" ) ;artSkinSelectInfluence("artAttrSkinPaintCtx","blendWeight");' % ('skinCluster', 'skinCluster1', 'paintWeights')

                paintDicts.append(mapInfoDictB)
                paintAttrKeys[paintAttrKey] = None


            else:
                # checking if attr for map actually exists due to odd result caused by 3rd party plugin
                isValidMap = False
                try:
                    node = pymel.PyNode(nodeName)
                    attr = node.attr(attributeName)
                    attrParent = attr.parent()
                    isValidMap = True
                except:
                    cmds.warning('non-existant attr returned by maya paintweights: %s.%s' % (nodeName, attributeName))

                if isValidMap:
                    if attrParent != None:
                        attrParent = attrParent.getParent(arrays=True)
                        if ka_deformers.isDeformer(node):
                            shapeIndex = node.indexForOutputShape(shape)
                            attr = attrParent[shapeIndex].attr(attributeName)

                    mapInfoDict = {}
                    mapInfoDict['label'] = '%s.%s' % (nodeName.split('|')[-1], attributeName)
                    mapInfoDict['ctx'] = 'artAttrCtx'
                    mapInfoDict['nodeName'] = nodePath
                    mapInfoDict['nodeType'] = nodeType
                    mapInfoDict['attributeName'] = attr.name(includeNode=False)
                    mapInfoDict['attributeShortName'] = attr.name(includeNode=False).split('.')[-1]
                    mapInfoDict['setWeightAttribute'] = mapInfoDict['attributeName']+'%s[%s]'

                    mapInfoDict['paintCommand'] = 'artSetToolAndSelectAttr("artAttrCtx", "%s.%s.%s" )' % (nodeType, nodePath, attributeName)

                    paintDicts.append(mapInfoDict)
                    paintAttrKeys[paintAttrKey] = None

    cmds.setToolTo(currentCtx)

    return paintDicts



def paintAttribute(paintDict, shape=None):
    """paints an attribute map based on the paint map string, usually retrieved from the
    return of getPaintableAttributes"""

    currentPaintMapDict = ka_clipBoard.get('currentPaintMapDict', {})

    # find the shape
    if shape is None:
        shape = pymel.selected()[-1]
        if ka_pymel.isPyTransform(shape):
            shape = shape.getShape()

    shapeLongName = shape.name()
    shapeShortName = shape.nodeName()

    currentPaintMapDict[shapeLongName] = paintDict
    if shapeShortName != shapeLongName:
        currentPaintMapDict[shapeShortName] = paintDict

    ka_clipBoard.add('currentPaintMapDict', currentPaintMapDict)

    try:
        mel.eval(paintDict['paintCommand'])

    except:
        ka_python.printError()
        raise Exception('mel.eval failed to eval the following text:\n%s' % paintDict['paintCommand'])


def paint(shape=None):
    """paint the current weight map"""

    # find the shape
    if not shape:
        shape = pymel.selected()[-1]
        if ka_pymel.isPyTransform(shape):
            shape = shape.getShape()

    paintMapDict = getCurrentPaintMapDict(shape)

    if paintMapDict:
        #mel.eval(paintMapDict['paintCommand'])
        paintAttribute(paintDict=paintMapDict)

def updatePaintMap():
    paint()

def getComponentArrayIndex(component, shape=None, **kwargs):
    if shape == None:
        shape = component.node()

    indices = []
    for strI in re.findall(r'\d+', str(component).split('.')[1]):
        indices.append(int(strI))

    if isinstance(shape, pymel.nodetypes.Mesh):    # POLYGONS ----------------------------------
        return indices[0]

    elif isinstance(shape, pymel.nodetypes.Subdiv):    # SUBDIVS ----------------------------------
        pass

    elif isinstance(shape, pymel.nodetypes.NurbsSurface):    # NURBS ----------------------------------
        lastV = shape.spansUV.get()[1]+3

        index = (indices[0]*lastV) + indices[1]
        return index

    elif isinstance(shape, pymel.nodetypes.NurbsCurve):    # CURVE ----------------------------------
        return indices[0]

    elif isinstance(shape, pymel.nodetypes.Lattice):    # LATTICE ----------------------------------
        sDivisions = kwargs.get('sDivisions', None)
        tDivisions = kwargs.get('tDivisions', None)

        if sDivisions == None: sDivisions = shape.sDivisions.get()
        if tDivisions == None: tDivisions = shape.tDivisions.get()

        index = indices[0] + (sDivisions*indices[1]) + ((sDivisions, tDivisions)*indices[2])
        return index


def getPaintMapAttributeDict(shapes=None, paintMapDict=None):
    """This function is important because it assosiates the many possible maps in a
    deformer with the shape they effect"""

    if paintMapDict is None:
        paintMapDict = getCurrentPaintMapDict()

    paintMapAttributesDict = {}    # {shape:paintAttr}

    nodeType = paintMapDict['nodeType']
    nodeName = paintMapDict['nodeName']
    attrPath = paintMapDict['attributeName']
    attrShortName = paintMapDict['attributeShortName']

    if attrPath:
        node = pymel.PyNode(nodeName)
        attr = node.attr(attrPath)

        if ka_deformers.isDeformer(node):

            if shapes is None:
                shapes = node.getOutputGeometry()

            for shape in shapes:
                paintMapAttributesDict[shape] = attr
        #return paintMapAttributesDict



    else:
        node = pymel.PyNode(nodeName)
        attr = node.attr(attrShortName)
        attrParent = attr.parent()

        if attrParent != None:
            attrParent = attrParent.getParent(arrays=True)
            if ka_deformers.isDeformer(node):
                if shapes is None:
                    shapes = node.getOutputGeometry()

                for shape in shapes:
                    shapeIndex = node.indexForOutputShape(shape)
                    paintMapAttributesDict[shape] = attrParent[shapeIndex].attr(attrShortName)

        else:
            paintMapAttributesDict[None] = attr

    return paintMapAttributesDict


# ---------------------------------------------------------------------------------------------------------
def pruneWeightsDict(weightsDict, prunePrecision=PRUNE_PRECISION):
    """
	Removes small values from the weights dict and redistributes them among larger values
	"""
    pass

# ---------------------------------------------------------------------------------------------------------
def getWeights(inputDict=None, paintMapDicts=None, componentInfoDict=None, getAdditionalData=False):
    """Returns a dictionary with all the nessisary information about the paintmap weights
    for the current weight map. This function does not care about things like influence objects.
    functions querying these weights are excpected to deal with any nessisary complications
    that may arise when trying to apply this map to a different node

    # note the the values subdictionary can either be and <pointIndex>:<weightValue> pair
    # or a <pointIndex>:{<influenceIndex>:<weightValue>, } as in the case of a skin cluster.
    # any exceptions need to be able to be read by the setWeight function

    Returns:
    clusterWeightsExample = {<shapeID>:{'values':{171:1.0,
    							                  172:0.87,
    							                  173:0.57,
    							                  174:0.27,
    								             },
                                       },
    		                }

    skinWeightsExample = {<shapeID>:{'values':{171:{0:1.0,},
    							               172:{0:0.75, 1:0.25},
    							               173:{0:0.33, 1:0.667},
    							               174:{1:1.0,},
    										  },

    								# keys below not implimented
    								 'indexOfInfluenceLongName':{'group7|joint2':0,
    								                             '|joint2',:1,
    								                            },

    								 'influenceNameOfInfluenceIndex':{0:'group7|joint2'
    								                                  1:'joint2',
    								                                 },
                                    },
    }

    """
    weightInfoDict = {}

    if componentInfoDict is None:
        componentInfoDict = ka_geometry.getComponentInfoDict(inputDict=inputDict)

    for shapeID in componentInfoDict:
        shape = componentInfoDict[shapeID]['pyShape']
        componentDict = componentInfoDict[shapeID]
        componentIndices = {}

        if inputDict is not None:
            for index in inputDict[shapeID]:
                componentIndices[index] = None

        else:
            for index in componentDict['pointDict']:
                componentIndices[index] = None


        weightInfoDict[shapeID] = {}
        weightDict = weightInfoDict[shapeID]
        weightDict['values'] = {}

        if paintMapDicts is None:
            paintMapDict = getCurrentPaintMapDict(shape=shape)
        else:
            paintMapDict = paintMapDicts[shapeID]

        nodeName = paintMapDict['nodeName']
        nodeType = paintMapDict['nodeType']
        attributeName = paintMapDict['attributeName']

        # SKIN CLUSTER
        if paintMapDict['nodeType'] == 'skinCluster' and paintMapDict['attributeName'] == 'paintWeights':
            if getAdditionalData:
                weightDict['values'] = _getSkinClusterWeights_(nodeName, componentIndices, additionalDataDict=weightDict)
            else:
                weightDict['values'] = _getSkinClusterWeights_(nodeName, componentIndices)


        #  OTHER DEFORMER/MAP
        else:
            weightAttr = pymel.PyNode('%s.%s' % (paintMapDict['nodeName'], paintMapDict['attributeName']))
            weightAttrType = weightAttr.type()

            for point in componentIndices:
                value = weightAttr[point].get()
                weightDict['values'][point] = value

    return weightInfoDict


def _getSkinClusterWeights_(skinCluster, componentIndices, additionalDataDict=None):
    """Takes a given skinCluster and a component Info Dict and returns the weights for
    the points in that dict. For more info on the componentInfoDict, see ka_geometry.getComponentInfoDict

    Args:
       skinCluster - <pySkinCluster>
       componentInfoDict - <ka_geometry.getComponentInfoDict()>
       additionalDataDict (dict) - if passed in, then influnce info will also be populated to that dictionary

    Returns:
       weights = {225:{2:0.7,
                       4:0.3,
                      },
                 }

    """
    if additionalDataDict != None:
        additionalDataDict['indexOfInfluence'] = {}
        additionalDataDict['influenceOfIndex'] = {}

    # get the MFnSkinCluster for clusterName
    if isinstance(skinCluster, pymel.PyNode):
        skinCluster_mfn = skinCluster.__apiobjects__['MFn']
        skinCl
    else:
        selList = OpenMaya.MSelectionList()
        selList.add(skinCluster)
        skinCluster_mObj = OpenMaya.MObject()
        selList.getDependNode(0, skinCluster_mObj)
        skinCluster_mfn = OpenMayaAnim.MFnSkinCluster(skinCluster_mObj)
        skinCluster = pymel.PyNode(skinCluster_mObj)

    # get the MDagPath for all influence
    infDags = OpenMaya.MDagPathArray()
    skinCluster_mfn.influenceObjects(infDags)

    # create a dictionary whose key is the MPlug indice id and
    # whose value is the influence list id
    infIds = {}
    infs = []
    for x in xrange(infDags.length()):
        infPath = infDags[x].fullPathName()
        infId = int(skinCluster_mfn.indexForInfluenceObject(infDags[x]))
        infIds[infId] = x
        infs.append(infPath)

    # get the MPlug for the weightList and weights attributes
    wlPlug = skinCluster_mfn.findPlug('weightList')
    wPlug = skinCluster_mfn.findPlug('weights')
    wlAttr = wlPlug.attribute()
    wAttr = wPlug.attribute()
    wInfIds = OpenMaya.MIntArray()


    if additionalDataDict:
        matrixPlug = skinCluster_mfn.findPlug('matrix')
        additionalDataDict['skinCluster'] = skinCluster

        plugIndices = OpenMaya.MIntArray()
        matrixPlug.getExistingArrayAttributeIndices(plugIndices)
        inputPlugs = OpenMaya.MPlugArray()
        for i in plugIndices:
            if matrixPlug.elementByLogicalIndex(i).isConnected():
                plugElement = matrixPlug.elementByLogicalIndex(i)
                plugElement.connectedTo(inputPlugs, True, False)
                node = pymel.PyNode(inputPlugs[0].node())
                additionalDataDict['influenceOfIndex'][i] = node
                additionalDataDict['indexOfInfluence'][node] = i


    # the weights are stored in dictionary, the key is the vertId,
    # the value is another dictionary whose key is the influence id and
    # value is the weight for that influence
    #
    weights = {}

    for vId in componentIndices:

        vWeights = {}
        # tell the weights attribute which vertex id it represents
        wPlug.selectAncestorLogicalIndex(vId, wlAttr)

        # get the indice of all non-zero weights for this vert
        wPlug.getExistingArrayAttributeIndices(wInfIds)

        # create a copy of the current wPlug
        infPlug = OpenMaya.MPlug(wPlug)
        for infId in wInfIds:
            # tell the infPlug it represents the current influence id
            infPlug.selectAncestorLogicalIndex(infId, wAttr)

            # add this influence and its weight to this verts weights
            try:
                vWeights[infIds[infId]] = infPlug.asDouble()
            except KeyError:
                # assumes a removed influence
                pass

            if additionalDataDict != None:
                if infId not in additionalDataDict['influenceOfIndex']:
                    matrixPlugItem = matrixPlug.elementByLogicalIndex(infId)
                    connections = OpenMaya.MPlugArray()
                    matrixPlugItem.connectedTo(connections, True, False)

                    for i in range(connections.length()):
                        matrixInput = connections[i].node()
                        node = pymel.PyNode(matrixInput)
                        additionalDataDict['influenceOfIndex'][infId] = node
                        additionalDataDict['indexOfInfluence'][node] = infId




        weights[vId] = vWeights

    return weights

def getSkinClusterInfluenceIndexDict(skinCluster):
    """Returns a dictionary that maps the index of each influence in that skinCluster's matrix attribute,
    to the name of the influence. This can be usefull in remapping weights from one skinCluster to another

    Returns influenceDict = {'joint2':3,
                             'joint1':2,
                             'joint3':0,
    						}
    """
    influenceIndexDict = {}

    # get the MFnSkinCluster for clusterName
    selList = OpenMaya.MSelectionList()
    selList.add(str(skinCluster))
    skinCluster_mObj = OpenMaya.MObject()
    selList.getDependNode(0, skinCluster_mObj)
    skinCluster_mfn = OpenMayaAnim.MFnSkinCluster(skinCluster_mObj)

    infDags = OpenMaya.MDagPathArray()
    skinCluster_mfn.influenceObjects(infDags)

    # create a dictionary whose key is the MPlug indice id and
    # whose value is the influence list id
    infIds = {}
    infs = []
    for x in xrange(infDags.length()):
        infPath = infDags[x].partialPathName()
        infId = int(skinCluster_mfn.indexForInfluenceObject(infDags[x]))
        infIds[infId] = x
        infs.append(infPath)
        influenceIndexDict[infPath] = infId

    return influenceIndexDict
def setSkinClusterWeights(skinCluster, weightsDict, componentInfoDict=None):
    """Takes a skinCluster, and a weights Dictionary, and sets the weights from the dictionary on
    the skinCluster

    Args:
        skinCluster - <pyNode>
    	weightsDict - dict, ie {225:{2:0.7,
                                     4:0.3,
                                    },
    						   }
    """

    t0 = time.clock()



    # get skinCluster mfn
    selList = OpenMaya.MSelectionList()
    selList.add(str(skinCluster))

    skinCluster_mObj = OpenMaya.MObject()
    selList.getDependNode(0, skinCluster_mObj)
    skinCluster_mfn = OpenMayaAnim.MFnSkinCluster(skinCluster_mObj)

    influenceObjects = OpenMaya.MDagPathArray()
    skinCluster_mfn.influenceObjects(influenceObjects)

    # get deformed geo dagPath
    deformedGeo = OpenMaya.MDagPath()
    deformedComponents_mObj = OpenMaya.MObject()
    skinCluster_mfn.getPathAtIndex(0, deformedGeo)

    # get pyShape and shapeID
    pyShape = pymel.PyNode(deformedGeo.fullPathName())
    shapeID = pyShape.__hash__()

    # get componentInfoDict
    if componentInfoDict is None:
        componentInfoDict = ka_geometry.getComponentInfoDict()

    # get components MObject
    #inputDict = {}
    #inputDict[pyShape] = []
    #for point in weightsDict:
        #inputDict[pyShape].append(componentInfoDict[shapeID]['multiIndex'][point])

    #inputDict[pyShape] = tuple(inputDict[pyShape])

    indices_mObject = ka_geometry.getIndicesOfShape_asMObject(pyShape, indices=tuple(weightsDict.keys()))

    #componentMSelectionList = ka_geometry.getMSelectionList_fromShapeAndMultiIndices(inputDict)
    #componentMSelectionList.getDagPath(0, deformedGeo, deformedComponents_mObj)

    # component print
    #mNodeIter = OpenMaya.MItSelectionList(componentMSelectionList)
    #geoIterClass = OpenMaya.MItMeshVertex
    #geoIter = geoIterClass( deformedGeo, deformedComponents_mObj )

    #form = pyShape.formV.get()
    #degree = componentInfoDict[shapeID]['degrees'][0]

    # make a list of all influence indices used by these points
    influenceIndices = {}
    for point in weightsDict:
        for index in weightsDict[point]:
            influenceIndices[index] = None

    influenceIndices = influenceIndices.keys()
    influenceIndices.sort()
    influenceIndices = tuple(influenceIndices)


    # influence array
    influences_intArray = OpenMaya.MIntArray()
    influences_intArray.setLength(len(influenceIndices))
    for i, influence in enumerate(influenceIndices):
        influences_intArray.set(influence, i)

    # create an array weight values
    weights_doubleArray = OpenMaya.MDoubleArray()
    weights_doubleArray.setLength(len(influenceIndices)*len(weightsDict))

    i = 0
    for point in ka_geometry.iterateGeo(shape=pyShape, components=tuple(weightsDict.keys()),
                                        componentInfoDict=componentInfoDict[shapeID]):


        r = 1.0
        largestInfluenceIndex = None
        largestInfluenceIndexInArray = None
        for index in influenceIndices:
            if index in weightsDict[point]:
                if largestInfluenceIndex is None:
                    largestInfluenceIndex = index
                    largestInfluenceIndexInArray = i

                # set weight value
                weight = round(weightsDict[point][index], 3)
                weights_doubleArray.set(weight, i)


                # check if the weight is the largest
                if weight > weightsDict[point][largestInfluenceIndex]:
                    largestInfluenceIndex = index
                    largestInfluenceIndexInArray = i

                r -= weight
                #print weightsDict[point][index]

            else:
                weights_doubleArray.set(0.0, i)


            i = i+1


        r = round(r, 3)
        if r:
            weight = round(weightsDict[point][largestInfluenceIndex], 3)

            weights_doubleArray.set(weight+r, largestInfluenceIndexInArray)

        cmds.removeMultiInstance(str(skinCluster)+'.wl[%s]' % str(point))

    # set Weights
    skinCluster_mfn.setWeights(deformedGeo, indices_mObject, influences_intArray, weights_doubleArray, False)




    #i = 0
    ##for point in sorted(weightsDict):
    #while not geoIter.isDone():
        ## step to next itteration
        #point = geoIter.index()

        ##print 'weightsDict[point]', weightsDict[point]
        ##total = 0.0
        #for index in influenceIndices:
            #if index in weightsDict[point]:
                #weights_doubleArray.set(weightsDict[point][index], i)

                ##total += weightsDict[point][index]
            ##else:
                ##weights_doubleArray.set(0.0, i)

            #i += 1
        #geoIter.next()

        #print 'total', total

        #if remainder != 0.0:
            #print 'remainder', round(remainder, 6)
    #OOOOOOO = "weightsDict[weightsDict.keys()[0]]"; print '%s: ' % OOOOOOO, eval(OOOOOOO), ' ', type(eval(OOOOOOO))
    #OOOOOOO = "weights_doubleArray"; print '%s: ' % OOOOOOO, eval(OOOOOOO), ' ', type(eval(OOOOOOO))



    #TTTTTTT = "  Set Weights A"; print '%s Step Took %s sec' % (TTTTTTT, str(round(time.clock()-t0, 4))) ;t0 = time.clock()

    #for point in weightsDict:
        #wlAttr = '%s.wl[%s]' % (skinCluster, str(point),)
        #cmds.removeMultiInstance(wlAttr)

        ##lenOfUsedInfluences = len(weightsDict[point])
        ##cmds.setAttr(wlAttr, size=lenOfUsedInfluences)


        ##numOfValues = len(weightsDict[point])
        ##pointsProcessed = 0
        ##currentIndex = 0
        ##currentSliceStart = None
        ##currentSliceEnd = None

        #valueStack = dict(weightsDict[point])
        #while valueStack:

            #i, value = valueStack.popitem()
            #sliceStart = i
            #sliceEnd = i

            #values = [value]

            #nextI = i+1
            #prevI = i-1

            ## look for the previous index in case we can make a slice
            #while prevI in valueStack:
                #prevValue = valueStack.pop(prevI)

                #sliceStart = prevI
                #values.append(prevValue)

                #prevI -= 1

            ## look for the next index in case we can make a slice
            #values.reverse()
            #while nextI in valueStack:
                #nextValue = valueStack.pop(nextI)

                #sliceEnd = nextI
                #values.append(nextValue)

                #nextI += 1



            #if sliceStart == sliceEnd:
                ##print 'sliceStart/end', sliceStart, sliceEnd
                #wAttr = '%s.wl[%s].w[%s]' % (skinCluster, str(point), str(sliceStart))
                #cmds.setAttr(wAttr, value)

            #else:
                #wAttr = '%s.wl[%s].w[%s:%s]' % (skinCluster, str(point), str(sliceStart), str(sliceEnd))
                ##print 'wAttr', wAttr
                #cmds.setAttr(wAttr, *values, size=len(values))

    #TTTTTTT = "  Set Weights B"; print '%s Step Took %s sec' % (TTTTTTT, str(round(time.clock()-t0, 4))) ;t0 = time.clock()
    #for vId in weightsDict:
        ## tell the weights attribute which vertex id it represents
        #wPlug.selectAncestorLogicalIndex(vId, wlAttr)

        ## clean up array
        #cmds.removeMultiInstance('%s.weightList[%s]' % (skinCluster, str(vId),))

        ## create a copy of the current wPlug
        #infPlug = OpenMaya.MPlug(wPlug)
        #for infId in weightsDict[vId]:
            #weightValue = weightsDict[vId][infId]
            #if weightValue:
                ## tell the infPlug it represents the current influence id
                #infPlug.selectAncestorLogicalIndex(infId, wAttr)

                ## set weight
                ##infPlug.setDouble(weightValue)
    #TTTTTTT = "doB"; print '%s Step Took %s sec' % (TTTTTTT, str(round(time.clock()-t0, 4))) ;t0 = time.clock()


# ---------------------------------------------------------------------------------------------------------
def setWeights(weightInfoDict=None, paintMapDicts=None, componentInfoDict=None):
    """Sets weights passed into the weightDict arg, on the map from the paintMapDict arg.
    If no paintMapDict is passed in, then the weights will be applied to the current paintmap
    for the shape

    Args:
        weightDict - weights to apply to each point    *see getWeights function for format
    	paintMapDicts (dict) - paint maps to apply the weights to. This is a dict of paint maps
            where the key is the shapeID, and the value is paintInfoDict (returned by getCurrentPaintMapDict)

    """

    ## pars args
    #if components == None:
        #components = pymel.ls(selection=True, flatten=True)

    #else:
        #if not isinstance(components, list):
            #components = [components]

    #shapes = []
    #componentsOfShapeDict = {}
    #for component in components:
        #shape = component.node()
        #if shape not in shapes:
            #shapes.append(shape)
            #componentsOfShapeDict[shape] = []

        #componentsOfShapeDict[shape].append(component)


    # Set Values ============
    #value = values
    for shapeID in weightInfoDict:

        # get paint map dict
        if paintMapDicts is None:
            if componentInfoDict:
                paintMapDict = getCurrentPaintMapDict(shape=componentInfoDict[shapeID]['pyShape'])
            else:
                paintMapDict = getCurrentPaintMapDict()
        else:
            paintMapDict = paintMapDicts[shapeID]

        # set skin weights
        if paintMapDict['nodeType'] == 'skinCluster' and paintMapDict['attributeName'] == 'paintWeights':
            setSkinClusterWeights(paintMapDict['nodeName'], weightInfoDict[shapeID]['values'], componentInfoDict=componentInfoDict)

        # or other deformer weights
        else:
            weightAttr = pymel.PyNode('%s.%s' % (paintMapDict['nodeName'], paintMapDict['attributeName']))
            weightAttrType = weightAttr.type()

            if weightAttrType == 'TdataCompound':    # ----------------------------------------------
                for point in weightInfoDict[shapeID]['values']:
                    value = weightInfoDict[shapeID]['values'][point]

                    if isinstance(value, float):
                        weightAttr[point].set(value)

                    #elif isinstance(value, dict):
                        #for key in value:
                            #subValue = value[key]
                            #setWeightsAttr = setWeightsTemplateAttr % (str(point), str(key))
                            #cmds.setAttr('%s.%s' % (paintMapDict['nodeName'], setWeightsAttr), subValue)

            elif weightAttrType == 'doubleArray':    # ----------------------------------------------
                weightList = weightAttr.get()

                for i, component in enumerate(componentsOfShapeDict[shape]):
                    arrayIndex = getComponentArrayIndex(component)

                    if isinstance(values, list):
                        value = values[i]

                    weightList[arrayIndex] = value

                weightAttr.set(weightList)

# ---------------------------------------------------------------------------------------------------------
def getWeightedAverageOfWeightValues(weightValues=None, weights=None):
    """Takes a list of given weightDicts and averages them with their corrisponding weight from
    the weights parameter.

    Args:

        weightValues - dict

    	clusterWeightsValues = (0.43,
    				            0.65,
    	                      )

        skinClusterWeightValues = ({1:0.7,
    								5:0.3,
    			    			   },

    							   {1:0.4,
    	                            7:0.6,
    				               },
    	                          )

    	weights - tuple ie:(0.35, 0.65)  The weights param is the weight each of the given weight dicts
    	                                 contribute to the averaged amount

    Return:
        averaged weights (in the same format as an item of the weightsValue tuple)

    """
    #precision = 3
    # if no weights given, then average evenly
    if weights is None:
        weights = []
        averageWeight = 1.0/len(weightValues)
        for i in range(len(weightValues)):
            weights.append(averageWeight)
        weights = tuple(weights)


    # if only 1 item is given, no averaging needed
    numOfWeightValues = len(weightValues)
    if numOfWeightValues == 1:
        return weightValues[0]

    else:
        # average simple 1D weights --------------------------------------------
        if isinstance(weightValues[0], float):
            #averagedWeight = ka_math.average(weightValues)
            averagedWeight = 0.0
            for i in range(len(weightValues)):
                weight = weights[i]
                averagedWeight += weightValues[i]*weight*numOfWeightValues

            averagedWeight = averagedWeight/numOfWeightValues
            return averagedWeight

        # average complex weights (ie: skinCluster) -----------------------------
        elif isinstance(weightValues[0], dict):

            # find all influence keys
            keysDict = {}
            for valueDict in weightValues:
                for key in valueDict:
                    keysDict[key] = None

            averagedWeight = {}

            for key in keysDict:
                valuesOfKey = []
                for valueDict in weightValues:
                    if key in valueDict:
                        valuesOfKey.append(valueDict[key])
                    else:
                        valuesOfKey.append(0.0)

                valuesOfKey = tuple(valuesOfKey)

                averagedWeight[key] = 0.0
                for i in range(len(weightValues)):
                    weight = weights[i]
                    averagedWeight[key] += valuesOfKey[i]*weight*numOfWeightValues

                #averagedWeightItem = averagedWeight[key]/numOfWeightValues
                #if averagedWeightItem > 0.00001:
                averagedWeight[key] = averagedWeight[key]/numOfWeightValues


            # assign the remainder and prune small weights
            remainder = 1.0
            total = 0.0
            for key in averagedWeight.keys():
                #value = round(averagedWeight[key], precision)
                value = averagedWeight[key]

                # prune small weights
                if value < 0.00001:
                    averagedWeight.pop(key)

                else:
                    # add rounded value
                    averagedWeight[key] = value
                    remainder -= value
                    total += value


            remainingRemainder = remainder
            largestValueKey = None
            largestValue = 0.0
            for key in averagedWeight:
                value = averagedWeight[key]
                precentOfTotal = value/total
                #percentOfRemainder = round(remainder*precentOfTotal, precision)
                percentOfRemainder = remainder*precentOfTotal
                averagedWeight[key] += percentOfRemainder
                remainingRemainder -= percentOfRemainder

                if averagedWeight[key] > largestValue:
                    largestValueKey = key
                    largestValue = averagedWeight[key]

            #averagedWeight[largestValueKey] += round(remainingRemainder, precision)
            averagedWeight[largestValueKey] += remainingRemainder

            # return the result
            return averagedWeight

        # unknown weight data
        else:
            raise Exception('got unexpected weight value: %s' % str(valuesToAverage[0]))


# ---------------------------------------------------------------------------------------------------------
def copyPaintMap(paintMapDict=None):

    # parse args
    if paintMapDict == None:
        paintMapDict = getCurrentPaintMapDict()


    # Get Map Values ============
    paintValueDict = {}

    valueDict = {}
    weightAttr = pymel.PyNode('%s.%s' % (paintMapDict['nodeName'], paintMapDict['attributeName']))
    OOOOOOO = "weightAttr"; print '%s: ' % OOOOOOO, eval(OOOOOOO), ' ', type(eval(OOOOOOO))

    weightAttrMplug = weightAttr.__apimplug__()
    weightAttrType = weightAttr.type()

    if weightAttrType == 'TdataCompound':    # ----------------------------------------------
        usedIndices = OpenMaya.MIntArray()
        weightAttrMplug.getExistingArrayAttributeIndices(usedIndices)
        for i in usedIndices:
            valueDict[i] = weightAttrMplug.elementByLogicalIndex(i).asFloat()

    elif weightAttrType == 'doubleArray':    # ----------------------------------------------
        weightList = weightAttr.get()
        for index, value in enumerate(weightList):
            valueDict[index] = weightList[index]

    else:
        raise Exception('unknown map data type: %s' % weightAttrType)


    ka_clipBoard.add('copiedPaintValueDict', valueDict)


# ---------------------------------------------------------------------------------------------------------
def pastePaintMap(paintMapDict=None, shape=None, flip=False, mirror=False, invert=False):
    """Paste copied paint map to currently set paint map"""

    # parse args
    if paintMapDict is None:
        paintMapDict = getCurrentPaintMapDict()

    # find the shape
    if not shape:
        shape = pymel.selected()[-1]
        if ka_pymel.isPyTransform(shape):
            shape = shape.getShape()

    paintValueDict = ka_clipBoard.get('copiedPaintValueDict')

    components = ka_geometry.getComponents(shape)
    valueDict = ka_clipBoard.get('copiedPaintValueDict')


    if flip or mirror:
        if flip:
            mirrorMapDict = ka_geometry.getSymmetryMapDict(shape=shape, includeNegative=False, includeMiddle=True)

        else:
            mirrorMapDict = ka_geometry.getSymmetryMapDict(shape=shape,)

    # Set Values ===========================================================================
    #weightAttr = getPaintMapAttribute(shape, paintMapDict)
    weightAttr = pymel.PyNode('%s.%s' % (paintMapDict['nodeName'], paintMapDict['attributeName']))
    OOOOOOO = "weightAttr"; print '%s: ' % OOOOOOO, eval(OOOOOOO), ' ', type(eval(OOOOOOO))

    weightAttrMplug = weightAttr.__apimplug__()
    #weightAttrType = weightAttr.type()

    #if weightAttrType == 'TdataCompound':    # ----------------------------------------------
    if True:    # ----------------------------------------------
        node = weightAttr.node()
        parentAttrs = weightAttr.getAllParents(arrays=True)
        defaultValue = ka_mayaApi.getAttrDefaultValue(weightAttr)

        for i in range(len(components)):
            cmds.removeMultiInstance('%s[%s]' % (str(weightAttr), str(i)))

        #cmds.removeMultiInstance(str(parentAttrs[-2]))

        if flip or mirror:
            for iA in range(len(components)): # flip . . . . . . . . . . . .
            #for index in pointIter:
                #print shape, index

                if flip:
                    iB = mirrorMapDict[iA]

                    if iA in valueDict:
                        valueA = valueDict[iA]
                    else:
                        valueA = defaultValue

                    if invert:
                        valueA = 1.0-valueA

                    if valueA != defaultValue:
                        weightAttrMplug.elementByLogicalIndex(iB).setFloat(valueA)


                else:# mirror . . . . . . . . . . . .
                    if iA in mirrorMapDict:

                        iB = mirrorMapDict[iA]

                        if iA in valueDict:
                            valueA = valueDict[iA]
                        else:
                            valueA = defaultValue

                        if invert:
                            valueA = 1.0-valueA

                        if valueA != defaultValue:
                            weightAttrMplug.elementByLogicalIndex(iB).setFloat(valueA)
                            weightAttrMplug.elementByLogicalIndex(iA).setFloat(valueA)


        else:    # plain paste . . . . . . . . . . . .
            for iA in range(len(components)):

                if iA in valueDict:
                    valueA = valueDict[iA]
                else:
                    valueA = defaultValue

                if invert:
                    valueA = 1.0-valueA

                if valueA != defaultValue:
                    weightAttrMplug.elementByLogicalIndex(iA).setFloat(valueA)


    elif weightAttrType == 'doubleArray':    # ----------------------------------------------
        weightList = []

        for i in sorted(valueDict):
            value = valueDict[i]

            if invert:
                valueA = 1.0-valueA

            weightList.append(value)

        if flip or mirror:
            for iA in mirrorMapDict: # flip . . . . . . . . . . . .

                iB = mirrorMapDict[iA]

                if flip:

                    if iA in valueDict:
                        valueA = valueDict[iA]
                    else:
                        valueA = defaultValue

                    if iB in valueDict:
                        valueB = valueDict[iB]
                    else:
                        valueB = defaultValue

                    #if invert:
                        #valueA = 1.0-valueA
                        #valueB = 1.0-valueB

                    weightList[iA] = valueB
                    weightList[iB] = valueA

                else: # mirror . . . . . . . . . . . .

                    if iA in valueDict:
                        valueA = valueDict[iB]
                    else:
                        valueA = defaultValue

                    #if invert:
                        #valueA = 1.0-valueA

                    weightList[iA] = valueA
                    weightList[iB] = valueA


        weightAttr.set(weightList)

    mel.eval(paintMapDict['paintCommand'])

#---------------------------------------------------------------------------------------------------------
def flipPaintMap():
    # parse args
    t0 = time.clock()
    componentInfoDict = ka_geometry.getComponentInfoDict()
    weightDict = getWeights(componentInfoDict=componentInfoDict)
    symmetryDict = ka_geometry.getSymmetryMapDict(componentInfoDict=componentInfoDict, includeNegative=True, includeMiddle=True)

    newWeightDict = {}
    for shapeID in componentInfoDict:
        newWeightDict[shapeID] = {}
        newWeightDict[shapeID]['values'] = {}

        # Flip positive point weights
        for point in symmetryDict[shapeID]['positive']:
            oppositePoint = symmetryDict[shapeID]['positive'][point]
            newWeightValue = weightDict[shapeID]['values'][oppositePoint]

            newWeightDict[shapeID]['values'][point] = newWeightValue

        # Flip negative point weights
        for point in symmetryDict[shapeID]['negative']:
            oppositePoint = symmetryDict[shapeID]['negative'][point]
            newWeightValue = weightDict[shapeID]['values'][oppositePoint]

            newWeightDict[shapeID]['values'][point] = newWeightValue

        # Copy center weights
        for point in symmetryDict[shapeID]['center']:
            newWeightValue = weightDict[shapeID]['values'][point]

            newWeightDict[shapeID]['values'][point] = newWeightValue

    setWeights(weightInfoDict=newWeightDict)
    updatePaintMap()
    return newWeightDict

#---------------------------------------------------------------------------------------------------------
def mirrorPaintMap():
    t0 = time.clock()
    componentInfoDict = ka_geometry.getComponentInfoDict()
    weightDict = getWeights(componentInfoDict=componentInfoDict)
    symmetryDict = ka_geometry.getSymmetryMapDict(componentInfoDict=componentInfoDict, includeNegative=True, includeMiddle=True)

    newWeightDict = {}
    for shapeID in componentInfoDict:
        newWeightDict[shapeID] = {}
        newWeightDict[shapeID]['values'] = {}

        # Copy positive point weights
        for point in symmetryDict[shapeID]['positive']:
            newWeightValue = weightDict[shapeID]['values'][point]
            newWeightDict[shapeID]['values'][point] = newWeightValue

        # Mirror negative point weights
        for point in symmetryDict[shapeID]['negative']:
            oppositePoint = symmetryDict[shapeID]['negative'][point]
            newWeightValue = weightDict[shapeID]['values'][oppositePoint]

            newWeightDict[shapeID]['values'][point] = newWeightValue

        # Copy center weights
        for point in symmetryDict[shapeID]['center']:
            newWeightValue = weightDict[shapeID]['values'][point]

            newWeightDict[shapeID]['values'][point] = newWeightValue

    TTTTTTT = "stepA"; print '%s Step Took %s sec' % (TTTTTTT, str(round(time.clock()-t0, 4))) ;t0 = time.clock()

    setWeights(weightInfoDict=newWeightDict)
    updatePaintMap()

    TTTTTTT = "stepB"; print '%s Step Took %s sec' % (TTTTTTT, str(round(time.clock()-t0, 4))) ;t0 = time.clock()
    return newWeightDict


#---------------------------------------------------------------------------------------------------------
def invertPaintMap():
    t0 = time.clock()
    componentInfoDict = ka_geometry.getComponentInfoDict()
    weightDict = getWeights(componentInfoDict=componentInfoDict)

    newWeightDict = {}
    for shapeID in componentInfoDict:
        newWeightDict[shapeID] = {}
        newWeightDict[shapeID]['values'] = {}

        # Invert point weights
        for point in componentInfoDict[shapeID]['pointDict']:
            newWeightValue = weightDict[shapeID]['values'][point]

            if isinstance(newWeightValue, float):
                newWeightDict[shapeID]['values'][point] = 1.0-newWeightValue

            elif isinstance(newWeightValue, int):
                newWeightDict[shapeID]['values'][point] = 1-newWeightValue

            else:
                newWeightDict[shapeID]['values'][point] = newWeightValue


    setWeights(weightInfoDict=newWeightDict)
    updatePaintMap()

    return newWeightDict

##---------------------------------------------------------------------------------------------------------
#def getMirrorMapDict(shape, includeMidPoints=True, includeNegitivePoints=False):
    #mirrorMapDict = {}
    #geometrySymmetryMap = ka_geometry.getSymmetryMapDict(shape=shape, includePositive=True, includeNegative=True, includeMiddle=True )
    #return geometrySymmetryMap

    #for component in geometrySymmetryMap:
        #symComponent = geometrySymmetryMap[component]

        #componentIndex = getComponentArrayIndex(component, shape=shape)
        #symComponentIndex = getComponentArrayIndex(symComponent, shape=shape)

        #mirrorMapDict[componentIndex] = symComponentIndex
        #mirrorMapDict[symComponentIndex] = componentIndex

    #return mirrorMapDict