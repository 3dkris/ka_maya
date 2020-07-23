#====================================================================================
#====================================================================================
#
# ka_deformers
#
# DESCRIPTION:
#   tools related to deformers
#
# DEPENDENCEYS:
#   Maya
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

import maya.cmds as cmds
import maya.mel as mel
import pymel.core as pymel


import ka_maya.ka_shapes as ka_shapes #;reload(ka_skinCluster)
import ka_skinCluster as ka_skinCluster #;reload(ka_skinCluster)
import ka_maya.ka_pymel as ka_pymel




def renameAllDeformers():
    """renames all deformers to be <shapeName>_<deformerNodeType>
    this allows file names to be more likely to be uniquely named and
    guessable"""

    allDeformers = getAllDeformers()
    for deformer in allDeformers:
        componentsDeformed = getDeformedComponents(deformer)
        deformedObjects = getDeformedObjects(componentsDeformed)
        if len(deformedObjects) == 1:
            if not deformer.isReferenced():
                newName = deformedObjects[0] +'_'+ pymel.nodeType(deformer)
                deformer.rename(newName)


def getDeformers(inputs):
    """returns all deformers of the given shape or shapes

    @ param inputs - can be a tran
    args:

        shapes: shape-pymelNode or list of shape-pymelNodes
            the shape or shapes to get deformers from
    """

    deformers = []
    shapes = []

    # pars args
    inputs = ka_pymel.getAsPyNodes(inputs)
    if not isinstance(inputs, list):
        inputs = [inputs]

    for node in inputs:
        nodeTypes = pymel.nodeType(node, inherited=True)
        if 'shape' in nodeTypes:
            shapes.append(node)
        elif 'transform' in nodeTypes:
            for shape in node.getShapes():
                shapes.append(shape)


    # find deformers for given shapes
    for shape in shapes:
        history = pymel.listHistory(shape, groupLevels=True, pruneDagObjects=True, leaf=False, future=False, interestLevel=1)
        for item in history:
            if 'geometryFilter' in pymel.nodeType(item, inherited=True):
                deformers.append(item)

    return deformers

def getAllDeformers():
    """returns all deformers in Scene"""
    return pymel.ls(type='geometryFilter')

def isDeformer(node):
    return isinstance(node, pymel.nt.GeometryFilter)


#def getDeformedObjects(deformedComponentSlices):
    #'''returns all shapes deformed by the given deformer
    #'''

def getAllDeformedShapes():
    allDeformedObjects = []
    for each in pymel.ls(transforms=True):
        shapes = pymel.listRelatives(each, shapes=True)

        for shape in shapes:
            if 'deformableShape' in pymel.nodeType(shape, inherited=True):
                if getDeformers(shape):
                    allDeformedObjects.append(shape)

    return allDeformedObjects


def getDeformerSet(deformerNode):
    possibleDeformerSets = deformerNode.message.outputs()
    for each in possibleDeformerSets:
        if pymel.nodeType(each) == 'objectSet':
            if pymel.isConnected(deformerNode.message, each.usedBy[0]):
                return each


def getDeformedComponents(deformerNode, flatten=False, nodesOnly=False, deformerSet=None):

    if not deformerSet:
        deformerSet = getDeformerSet(deformerNode)

    components = pymel.sets(deformerSet, q=True, nodesOnly=nodesOnly)

    if flatten:
        components = pymel.ls(components, flatten=True)

    return components


def getRange_fromString(componentString,):

    start = componentString.index('[')+1
    end = componentString.index(']')
    colon = componentString.index(':')

    start = int(componentString[start:mid])
    end = int(componentString[mid+1:end+1])

    return (start, end)


def setComponentsOfDeformersSet(deformerNode, componentSet):
    deformerSet = getDeformerSet(deformerNode)
    pymel.sets(deformerSet, clear=True,)
    pymel.sets(deformerSet, addElement=componentSet,)



def getWeightSlices(weightList):
    '''this function will take (a potentially long) list of weight values, and break it into slices
    representing the non zero values. This step will have a dramatic speed increase when it comes
    to importing them

    returns - a dictionary where the slice is the key
              ie: {'32:33' : (0.7, 0.3),}
    '''

    weightSlicesDict = {}
    sliceStart = None
    sliceEnd = None
    sliceValues = []
    lastIndex = len(weightList)-1

    for i, weightValue in enumerate(weightList):

        if weightValue:
            sliceValues.append(weightValue)

            if sliceStart == None:
                sliceStart = i
                sliceEnd = i

            else:
                sliceEnd += 1

            if i == lastIndex:
                if sliceStart == sliceEnd:
                    key = str(sliceStart)

                else:
                    key = '%s:%s' % (str(sliceStart), str(sliceEnd))

                weightSlicesDict[key] = tuple(sliceValues)
                sliceStart = None
                sliceEnd = None
                sliceValues = []

        else:
            if sliceStart != None:
                if sliceStart == sliceEnd:
                    key = str(sliceStart)

                else:
                    key = '%s:%s' % (str(sliceStart), str(sliceEnd))

                weightSlicesDict[key] = tuple(sliceValues)
                sliceStart = None
                sliceEnd = None
                sliceValues = []

    return weightSlicesDict



def makeCorrective2(items=None, name=None):
    import cvShapeInverter
    xformAttrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', ]
    xformAttrDefaults = [0,0,0,0,0,0,1,1,1]
    duplicates = []
    if name == None:
        result = cmds.promptDialog(
                title='Create Corrective Shape',
                message='Enter Corrective Name:',
                text='positionA',
                button=['Create', 'Cancel'],
                defaultButton='OK',
                cancelButton='Cancel',
                dismissString='Cancel')

        if result != 'Create':
            return None

        name = cmds.promptDialog(query=True, text=True)

    if not items:
        items = []
        for item in pymel.ls(selection=True):
            inheritedTypes = item.nodeType(inherited=True)
            if 'transform' in inheritedTypes:
                if item.getShapes():
                    items.append(item)

            elif 'shape' in inheritedTypes:
                items.append(item.getParent())


    for item in items:
        itemPosition = pymel.xform(item, query=True, translation=True, worldSpace=True)
        duplicate = pymel.duplicate(item)[0]
        duplicate.rename(name+'Corrective')
        duplicateShape = duplicate.getShape()
        duplicates.append(duplicate)

        for attr in xformAttrs:
            try:
                duplicate.attr(attr).set(lock=False)

            except:
                pass

        pymel.xform(duplicate, translation=[itemPosition[0]+5, itemPosition[1], itemPosition[2]], worldSpace=True,)

        pymel.select(item, duplicate)
        invertedItem = cvShapeInverter.invert()
        invertedItem = pymel.ls(invertedItem)[0]
        invertedItem.setParent(duplicate)
        invertedItemShape = invertedItem.getShape()
        invertedItem.v.set(0)

        for i, attr in enumerate(xformAttrs):
            invertedItem.attr(attr).set(xformAttrDefaults[i])


        blendShape = None
        for deformer in getDeformers(item):
            if deformer.nodeType() == 'blendShape':
                blendShape = deformer
                break

        if blendShape:
            index = pymel.blendShape(blendShape, query=True, weightCount=True)
            OOOOOOO = "index"; print '%s: ' % OOOOOOO, eval(OOOOOOO), ' ', type(eval(OOOOOOO))
            pymel.blendShape(blendShape, edit=True, target=(item, index, invertedItem, 1.0))
            blendShape.w[index].set(1)
            OOOOOOO = "blendShape"; print '%s: ' % OOOOOOO, eval(OOOOOOO), ' ', type(eval(OOOOOOO))
        else:
            blendShape = pymel.blendShape(invertedItem, item, frontOfChain=True,)[0]
            blendShape.rename(item.nodeName()+'_blendShape')
            blendShape.w[0].set(1)
            print 'NEW'

        #blendShapeA.w[0].set(1)
        #ka_shapes.shapeParent(invertedItem, duplicate)

        #itemBlendShape = None
        #for deformer in getDeformers(item):
            #if defomer.nodeType() == '':
                #pass
        #pymel.blendShape(bs, query=True, weightCount=True)
        #bs[0].w[0].set(2)



        OOOOOOO = "invertedItem"; print '%s: ' % OOOOOOO, eval(OOOOOOO), ' ', type(eval(OOOOOOO))



def getOrigShape(node):
    origMesh = None
    origMeshs = []
    children = node.getParent().getChildren(shapes=True, noIntermediate=False)
    for child in children:
        if hasattr(child, 'intermediateObject'):
            if child.intermediateObject.get():
                origMeshs.append(child)

    if len(origMeshs) == 1:
        return origMeshs[0]

    elif len(origMeshs) > 1:
        for origMesh in origMeshs:
            if not origMesh.inputs():
                return origMesh

        return origMeshs[0]

    return node

def makeCorrective(items=None, name=None):
    import cvShapeInverter
    xformAttrs = ['t', 'r', 's', 'tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', ]
    xformAttrDefaults = [0,0,0,0,0,0,1,1,1]
    duplicates = []
    if name == None:
        result = cmds.promptDialog(
                title='Create Corrective Shape',
                message='Enter Corrective Name:',
                text='positionA',
                button=['Create', 'Cancel'],
                defaultButton='OK',
                cancelButton='Cancel',
                dismissString='Cancel')

        if result != 'Create':
            return None

        name = cmds.promptDialog(query=True, text=True)

    if not items:
        items = []
        for item in pymel.ls(selection=True):
            inheritedTypes = item.nodeType(inherited=True)
            if 'transform' in inheritedTypes:
                if item.getShapes():
                    items.append(item)

            elif 'shape' in inheritedTypes:
                items.append(item.getParent())


    for item in items:
        itemShape = item.getShape()
        itemPosition = pymel.xform(item, query=True, translation=True, worldSpace=True)
        itemMatrix = pymel.xform(item, query=True, matrix=True, worldSpace=True)

        # get the origShape
        itemOrigShape = getOrigShape(itemShape)

        # create a duplicate
        duplicate = pymel.duplicate(item, smartTransform=False)[0]
        duplicate.rename('%s_%sCorrective' % (item.nodeName(), name,))
        duplicateShape = duplicate.getShape()
        duplicates.append(duplicate)

        ## set the duplicate's shape to match the item's orig shape
        #itemOrigShape.intermediateObject.set(0)
        #tempBlendShape = pymel.blendShape(itemOrigShape, duplicate)[0]
        #itemOrigShape.intermediateObject.set(1)

        #tempBlendShape.w[0].set(1)
        #tempBlendShape.inputTarget[0].inputTargetGroup[0].inputTargetItem[6000].inputGeomTarget.disconnect()
        #pymel.delete(duplicate, constructionHistory=True)


        # unlock translate attrs so the user can move the target
        for attr in xformAttrs:
            try:
                duplicate.attr(attr).set(lock=False)

            except:
                pass

        # create secondary blendshape node if one does not already exist
        secondaryBlendShape = None
        for deformer in getDeformers(item):
            if hasattr(deformer, 'isSecondaryBlendShape'):
                secondaryBlendShape = deformer
                break

        if not secondaryBlendShape:
            secondaryBlendShape = pymel.blendShape(item)[0]
            secondaryBlendShape.addAttr('isSecondaryBlendShape', at='bool', defaultValue=True)
            secondaryBlendShape.isSecondaryBlendShape.set(lock=True)
            secondaryBlendShape.rename(item.nodeName()+'_secondaryBlendshape')


        #duplicateOrigShape = getOrigShape(duplicateShape)
        #duplicateOrigShape.intermediateObject.set(0)
        #staticBlendShape = pymel.blendShape(item, duplicateOrigShape)[0]
        #duplicateOrigShape.intermediateObject.set(1)
        #staticBlendShape.rename(duplicate.nodeName()+'_staticBlendShape')
        #staticBlendShape.w[0].set(1)
        #pymel.delete(duplicate, constructionHistory=True)

        liveBlendShape = pymel.blendShape(item, duplicate)[0]
        liveBlendShape.rename(duplicate.nodeName()+'_liveBlendShape')
        liveBlendShape.w[0].set(1)

        tweakNode = None
        for deformer in reversed(getDeformers(duplicateShape)):
            if deformer.nodeType() == 'tweak':
                tweakNode = deformer
                break

        tweakNode.rename(duplicate.nodeName()+'_secondaryTweak')
        pymel.reorderDeformers(tweakNode, liveBlendShape)



        #pymel.reorderDeformers(tweakNode, staticBlendShape)

        # connect the input of the blendshape as a target of the live shape
        groupParts = secondaryBlendShape.input[0].inputGeometry.inputs()[0]
        groupParts.outputGeometry >> liveBlendShape.inputTarget[0].inputTargetGroup[0].inputTargetItem[6000].inputGeomTarget


        # backgroundTweak
        backgroundTweak = pymel.createNode('tweak')
        backgroundTweak.rename('backgroundTweak')
        groupParts.outputGeometry >> backgroundTweak.input[0].inputGeometry


        #groupParts.outputGeometry >> staticBlendShape.inputTarget[0].inputTargetGroup[0].inputTargetItem[6000].inputGeomTarget

        pymel.blendShape(item, duplicate)[0]
        index = pymel.blendShape(secondaryBlendShape, query=True, weightCount=True)
        pymel.blendShape(secondaryBlendShape, edit=True, target=(item, index, duplicate, 1.0))
        secondaryBlendShape.w[index].set(1)
        #backgroundTweak.outputGeometry[0] >> secondaryBlendShape.inputTarget[0].inputTargetGroup[index].inputTargetItem[6000].inputGeomTarget

        #blendShape = None
        #for deformer in getDeformers(item):
            #if deformer.nodeType() == 'blendShape':
                #blendShape = deformer
                #break

        #if blendShape:
            #index = pymel.blendShape(blendShape, query=True, weightCount=True)
            #OOOOOOO = "index"; print '%s: ' % OOOOOOO, eval(OOOOOOO), ' ', type(eval(OOOOOOO))
            #pymel.blendShape(blendShape, edit=True, target=(item, index, invertedItem, 1.0))
            #blendShape.w[index].set(1)
            #OOOOOOO = "blendShape"; print '%s: ' % OOOOOOO, eval(OOOOOOO), ' ', type(eval(OOOOOOO))
        #else:
            #blendShape = pymel.blendShape(invertedItem, item, frontOfChain=True,)[0]
            #blendShape.rename(item.nodeName()+'_blendShape')
            #blendShape.w[0].set(1)
            #print 'NEW'

        #blendShapeA.w[0].set(1)
        #ka_shapes.shapeParent(invertedItem, duplicate)

        #itemBlendShape = None
        #for deformer in getDeformers(item):
            #if defomer.nodeType() == '':
                #pass
        #pymel.blendShape(bs, query=True, weightCount=True)
        #bs[0].w[0].set(2)



        #OOOOOOO = "invertedItem"; print '%s: ' % OOOOOOO, eval(OOOOOOO), ' ', type(eval(OOOOOOO))

        #staticBlendShape.inputTarget[0].inputTargetGroup[0].inputTargetItem[6000].inputGeomTarget.disconnect()
        pymel.xform(duplicate, translation=[itemPosition[0]+5, itemPosition[1], itemPosition[2]], worldSpace=True,)
        pymel.select(duplicates)



# ========================================================================================================================================
def print_addBlendShapeFromData(inNodes=None):
    """
    Prints a string that will rebuild a blendShape with baked shapes
    """
    inBlendShapes=None
    blendShapes = []
    if not inBlendShapes:
        inBlendShapes = pymel.ls(selection=True, objectsOnly=True)
    elif not isinstance(inBlendShapes, list):
        inBlendShapes = ka_pymel.getAsPyNodes([inBlendShapes])

    for inBlendShape in inBlendShapes:
        if isinstance(inBlendShape, pymel.nt.BlendShape):
            blendShapes.append(inBlendShape)

        else:
            shapes = []
            if isinstance(inBlendShape, pymel.nt.GeometryShape):
                shapes.append(inBlendShape)

            elif ka_pymel.isPyTransform(inBlendShape):
                for shape in inBlendShape.getShapes(noIntermediate=True):
                    if isinstance(shape, pymel.nt.GeometryShape):
                        shapes.append(shape)

            for shape in shapes:
                deformers = getDeformers(shape)
                for deformer in deformers:
                    if isinstance(deformer, pymel.nt.BlendShape):
                        if deformer not in blendShapes:
                            blendShapes.append(deformer)

    for blendShape in blendShapes:
        blendShapeData = []
        for iA in blendShape.inputTarget.get(multiIndices=True):
            listA = []
            for iB in blendShape.inputTarget[iA].inputTargetGroup.get(multiIndices=True):
                listB = []
                for iC in blendShape.inputTarget[iA].inputTargetGroup[iB].inputTargetItem.get(multiIndices=True):
                    listC = []
                    inputAttr = blendShape.inputTarget[iA].inputTargetGroup[iB].inputTargetItem[iC].inputGeomTarget.inputs(plugs=True)
                    if inputAttr:
                        blendShape.inputTarget[iA].inputTargetGroup[iB].inputTargetItem[iC].inputGeomTarget.disconnect()

                    for iD, point in enumerate(blendShape.inputTarget[iA].inputTargetGroup[iB].inputTargetItem[iC].inputPointsTarget.get()):
                        #if point[0] or point[1] or point[2]:
                        listC.append((point[0], point[1], point[2], point[3],))
                    listB.append((iC, tuple(listC),))

                    if inputAttr:
                        inputAttr[0] >> blendShape.inputTarget[iA].inputTargetGroup[iB].inputTargetItem[iC].inputGeomTarget

                listA.append((iB, tuple(listB),))
            blendShapeData.append((iA, tuple(listA),))

        shapes = blendShape.getBaseObjects()
        shapeStrings = []
        for shape in shapes:
            shapeStrings.append(str(shape))
        print """
import ka_maya.ka_deformers as ka_deformers
ka_deformers.addBlendShapeFromData(%s, %s)
        """ % (str(tuple(shapeStrings)),
               str(tuple(blendShapeData)),

              )


# ========================================================================================================================================
def addBlendShapeFromData(inShape, blendShapeData):
    """
    adds a blend shape to the given transform/blendShape
    """

    inShapes = ka_pymel.getAsPyNodes(inShape)

    import time
    t0 = time.clock()
    #blendShape = None
    #for inShape in inShapes:
        #deformers = getDeformers(inShape)
        #for deformer in deformers:
            #if isinstance(deformer, pymel.nt.BlendShape):
                #blendShape = deformer
                #break
    blendShape = None
    deformers = getDeformers(inShapes[0].getParent())
    #OOOOOOO = "deformers"; print '%s= ' % OOOOOOO, eval(OOOOOOO), ' #', type(eval(OOOOOOO))
    for deformer in deformers:
        if isinstance(deformer, pymel.nt.BlendShape):
            blendShape = deformer
            break

    if not blendShape:
        #blendShape = pymel.createNode('blendShape')
        for shape in inShapes:
            transform = shape.getParent()
            break

        #dup = pymel.duplicate(transform)[0]

        cmds.select(clear=True)

        blendShape = pymel.blendShape(transform)[0]
        #print transform, blendShape
        #for transform
            #blendShape.setGeometry(shape)

        #dup = pymel.duplicate(transform)
        #blendShape = pymel.blendShape([transform, dup], ignoreSelected=True)[0]
        #pymel.delete(dup)

        #blendShape = pymel.blendShape(transform, ignoreSelected=True, exclusive=True)[0]
        #pymel.blendShape(blendShape, edit=True, geometry=transform)
        #blendShape = pymel.deformer(transform, type='blendShape', before=True)[0]


    strBlendShape = str(blendShape)
    for iA, listA in blendShapeData:
        siA = str(iA)
        for iB, listB in listA:
            siB = str(iB)
            for iC, listC in listB:
                siC = str(iC)
                cmds.setAttr('%s.inputTarget[%s].inputTargetGroup[%s].inputTargetItem[%s].inputPointsTarget' % (strBlendShape, siA, siB, siC, ), len(listC), *listC, type='pointArray')

            blendShape.weight[iB].set(keyable=True)
            blendShape.weight[iB].set(0)

    return blendShape



    pass