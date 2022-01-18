#====================================================================================
#====================================================================================
#
# ka_nurbsRigging
#
# DESCRIPTION:
#   A module for rigging on nurbs surfaces
#
# DEPENDENCEYS:
#   Maya
#
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

import os

import pymel.core as pymel
import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMaya as om

import ka_maya.ka_pymel as ka_pymel
import ka_maya.ka_math as ka_math
import ka_maya.ka_transforms as ka_transforms
import ka_maya.ka_shapes as ka_shapes
import ka_maya.ka_util as ka_util

def createUvFlipKeyFrame(max=1):

    animCurveNode = pymel.createNode('animCurveUU')

    pymel.setKeyframe(animCurveNode, insert=True, float=0, outTangentType='linear')
    pymel.setKeyframe(animCurveNode, insert=True, float=max, value=float(max), inTangentType='linear', outTangentType='step')
    pymel.keyframe(animCurveNode, edit=True, float=(int(max),int(max)), absolute=True, valueChange=float(max),)
    animCurveNode.preInfinity.set(3)
    animCurveNode.postInfinity.set(3)

    pymel.keyTangent(animCurveNode, edit=True, float=(0, 0), outTangentType='linear')
    pymel.keyTangent(animCurveNode,  edit=True, float=(int(max), int(max)), inTangentType='linear', outTangentType='step')

    return animCurveNode

def createUvReverseKeyFrame(max=1):

    animCurveNode = pymel.createNode('animCurveUU')

    pymel.setKeyframe(animCurveNode, insert=True, float=0, outTangentType='linear')
    pymel.setKeyframe(animCurveNode, insert=True, float=max, value=float(max), inTangentType='linear', outTangentType='step')
    pymel.setKeyframe(animCurveNode, insert=True, float=max*-1.0, value=float(max), inTangentType='linear', outTangentType='step')
    pymel.keyframe(animCurveNode, edit=True, float=(int(max*-1),int(max*-1)), absolute=True, valueChange=float(max),)
    pymel.keyframe(animCurveNode, edit=True, float=(int(max),int(max)), absolute=True, valueChange=float(max),)
    animCurveNode.preInfinity.set(3)
    animCurveNode.postInfinity.set(3)

    pymel.keyTangent(animCurveNode, edit=True, float=(max*-1, max*-1), inTangentType='linear', outTangentType='linear')
    pymel.keyTangent(animCurveNode, edit=True, float=(0, 0), inTangentType='linear', outTangentType='linear')
    pymel.keyTangent(animCurveNode,  edit=True, float=(int(max), int(max)), inTangentType='linear', outTangentType='linear')

    return animCurveNode


def pointOnSurfaceConstraint(surface=None, nodes=None, withOffset=False, asPercent=True, wrapU=False, wrapV=False, worldSpace=True):

    selection = pymel.ls(selection=True)

    if surface == None:
        surface = ka_pymel.getAsPyNodes(selection[0])
    else:
        surface = ka_pymel.getAsPyNodes(surface)

    if nodes == None:
        nodes = ka_pymel.getAsPyNodes(selection[1:])
    else:
        nodes = ka_pymel.getAsPyNodes(nodes)

    if not isinstance(nodes, list):
        nodes = [nodes]

    if pymel.nodeType(surface) != 'nurbsSurface':
        surface = surface.getShape()

    minU, maxU = surface.minMaxRangeU.get()
    minV, maxV = surface.minMaxRangeV.get()
    spansU, spansV = surface.spansUV.get()

    aimConstraints = []
    pointOnSurfaces = []
    for each in nodes:

        baseName = each.nodeName()+'_surfaceConstraint'

        eachWorldPosition = pymel.xform(each, query=True, translation=True, worldSpace=True)
        if withOffset:
            surfaceConstraintGroup = pymel.createNode('transform',)
            surfaceConstraintGroup.rename(baseName+'Grp')
            surfaceConstraintGroup.inheritsTransform.set(0)
        else:
            surfaceConstraintGroup = each

        aimConstraint = pymel.createNode('aimConstraint',)
        aimConstraint.rename(baseName+'AimConstraint')
        aimConstraint.t.set(channelBox=False, lock=True, keyable=False)
        aimConstraint.r.set(channelBox=False, lock=True, keyable=False)
        aimConstraint.s.set(channelBox=False, lock=True, keyable=False)
        aimConstraint.v.set(channelBox=False, lock=True, keyable=False)
        aimConstraint.o.set(channelBox=False, lock=True, keyable=False)
        aimConstraint.worldUpType.set(3)

        if asPercent:
            aimConstraint.addAttr('posU', softMaxValue=1.0, softMinValue=0.0, keyable=True)
            aimConstraint.addAttr('posV', softMaxValue=1.0, softMinValue=0.0, keyable=True)
        else:
            aimConstraint.addAttr('posU', softMaxValue=surface.minMaxRangeU.get()[1], softMinValue=0.0, keyable=True)
            aimConstraint.addAttr('posV', softMaxValue=surface.minMaxRangeV.get()[1], softMinValue=0.0, keyable=True)

        if wrapU:
            aimConstraint.addAttr('uPlus1', keyable=True)
            aimConstraint.addAttr('uMinus1', keyable=True)

            uPlus1Node = pymel.createNode('plusMinusAverage')
            uPlus1Node.input1D[0].set(maxU*2)
            uPlus1Node.operation.set(2)
            aimConstraint.posU >> uPlus1Node.input1D[1]
            uPlus1Node.output1D >> aimConstraint.uPlus1

            uMinus1Node = pymel.createNode('plusMinusAverage')
            uMinus1Node.operation.set(2)
            uMinus1Node.input1D[0].set(0)
            aimConstraint.posU >> uMinus1Node.input1D[1]
            uMinus1Node.output1D >> aimConstraint.uMinus1

        if wrapV:
            aimConstraint.addAttr('vPlus1', keyable=True)
            aimConstraint.addAttr('vMinus1', keyable=True)

            vPlus1Node = pymel.createNode('plusMinusAverage')
            vPlus1Node.input1D[0].set(maxV)
            aimConstraint.posV >> vPlus1Node.input1D[1]
            vPlus1Node.output1D >> aimConstraint.vPlus1

            vMinus1Node = pymel.createNode('plusMinusAverage')
            vMinus1Node.operation.set(2)
            vMinus1Node.input1D[1].set(maxV)
            aimConstraint.posV >> vMinus1Node.input1D[0]
            vMinus1Node.output1D >> aimConstraint.vMinus1


        pymel.addAttr(aimConstraint, longName='outPosition', keyable=False, attributeType='float3')
        pymel.addAttr(aimConstraint, longName='outPositionX', keyable=False, attributeType='float', parent='outPosition')
        pymel.addAttr(aimConstraint, longName='outPositionY', keyable=False, attributeType='float', parent='outPosition')
        pymel.addAttr(aimConstraint, longName='outPositionZ', keyable=False, attributeType='float', parent='outPosition')



        closestPointOnSurface = pymel.createNode('closestPointOnSurface',)
        closestPointOnSurface.rename(baseName+'ClosestPointOnSurface')
        if worldSpace:
            surface.worldSpace[0] >> closestPointOnSurface.inputSurface
        else:
            surface.local >> closestPointOnSurface.inputSurface

        closestPointOnSurface.inPosition.set(eachWorldPosition)

        closestU = closestPointOnSurface.parameterU.get()
        maxU = surface.maxValueU.get()
        normalizedU = closestU / maxU

        closestV = closestPointOnSurface.parameterV.get()
        maxV = surface.maxValueV.get()
        normalizedV = closestV / maxV

        pymel.delete(closestPointOnSurface)

        if normalizedU > 1.0: normalizedU = 1.0
        if normalizedV > 1.0: normalizedV = 1.0
        if normalizedU < 0.0: normalizedU = 0
        if normalizedV < 0.0: normalizedV = 0

        aimConstraint.posU.set(normalizedU)
        aimConstraint.posV.set(normalizedV)



        pointOnSurfaceInfo = pymel.createNode('pointOnSurfaceInfo',)
        pointOnSurfaceInfo.rename(baseName+'PointOnSurfaceInfoA')
        pointOnSurfaceInfo.turnOnPercentage.set(asPercent)
        if worldSpace:
            surface.worldSpace[0] >> pointOnSurfaceInfo.inputSurface
        else:
            surface.local >> pointOnSurfaceInfo.inputSurface

        if wrapU:
            uvReverseKey = createUvReverseKeyFrame(maxU)
            aimConstraint.posU >> uvReverseKey.input
            uvReverseKey.output >> pointOnSurfaceInfo.parameterU
        else:
            aimConstraint.posU >> pointOnSurfaceInfo.parameterU

        if wrapV:
            uvFlipKey = createUvFlipKeyFrame(maxV)
            aimConstraint.posV >> uvFlipKey.input
            if wrapU:
                conditionA = pymel.createNode('condition')
                conditionA.operation.set(2) # greater than
                conditionA.secondTerm.set(maxU)
                conditionA.colorIfTrueB.set(-1)
                conditionA.colorIfFalseB.set(1)

                conditionB = pymel.createNode('condition')
                conditionB.operation.set(4) # less than
                conditionB.secondTerm.set(0)
                conditionA.colorIfTrueB.set(-1)

                mirroredVPlus = pymel.createNode('plusMinusAverage')
                mirroredVPlus.operation.set(2)
                mirroredVPlus.input1D[0].set(maxV)

                aimConstraint.posV >> mirroredVPlus.input1D[1]

                aimConstraint.posU >> conditionA.firstTerm
                aimConstraint.posU >> conditionB.firstTerm

                mirroredVPlus.output1D >> conditionA.colorIfTrueR
                mirroredVPlus.output1D >> conditionB.colorIfTrueR

                uvFlipKey.output >> conditionA.colorIfFalseR
                conditionA.outColorR >> conditionB.colorIfFalseR
                conditionB.outColorR >> pointOnSurfaceInfo.parameterV

                conditionA.outColorB >> conditionB.colorIfFalseB
                conditionB.outColorB >> aimConstraint.upVectorY

                # upvector flip condition
                #condition

            else:
                uvFlipKey.output >> pointOnSurfaceInfo.parameterV


        else:
            aimConstraint.posV >> pointOnSurfaceInfo.parameterV


        if worldSpace:
            pointOnSurfaceInfo.position >> aimConstraint.outPosition

            vectorProduct = pymel.createNode('vectorProduct')
            aimConstraint.outPosition >> vectorProduct.input1
            surfaceConstraintGroup.parentInverseMatrix[0] >> vectorProduct.matrix
            vectorProduct.operation.set(4)

            vectorProduct.output >> surfaceConstraintGroup.t
        else:
            pointOnSurfaceInfo.position >> surfaceConstraintGroup.t

        if pymel.nodeType(surfaceConstraintGroup) == 'joint':
            surfaceConstraintGroup.jointOrient >> aimConstraint.constraintJointOrient
        surfaceConstraintGroup.translate >> aimConstraint.constraintTranslate
        surfaceConstraintGroup.rotateOrder >> aimConstraint.constraintRotateOrder
        surfaceConstraintGroup.rotatePivot >> aimConstraint.constraintRotatePivot
        surfaceConstraintGroup.rotatePivotTranslate >> aimConstraint.constraintRotateTranslate
        if worldSpace:
            surfaceConstraintGroup.parentInverseMatrix[0] >> aimConstraint.constraintParentInverseMatrix

        plusMinusAverage = pymel.createNode('plusMinusAverage')
        pointOnSurfaceInfo.normal >> plusMinusAverage.input3D[0]
        pointOnSurfaceInfo.position >> plusMinusAverage.input3D[1]

        plusMinusAverage.output3D >> aimConstraint.target[0].targetTranslate

        pointOnSurfaceInfo.tangentU >> aimConstraint.worldUpVector
        aimConstraint.constraintRotate >> surfaceConstraintGroup.r

        pymel.parent(aimConstraint, surfaceConstraintGroup)

        if withOffset:
            pymel.parentConstraint(surfaceConstraintGroup, each, maintainOffset=True)

        aimConstraints.append(aimConstraint)
        pointOnSurfaces.append(pointOnSurfaceInfo)

    pymel.select(nodes)

    return aimConstraints, pointOnSurfaces


def createJointNetOnSurface(surface, numOfJointUV=[2,2], jointsArePerSpan=True, wrapUTop=True, wrapUBottom=True):
    jointGroup = pymel.createNode('transform')
    jointGroup.rename('jointNet')

    # parse args
    surface = ka_pymel.getAsPyNodes(surface)
    if surface.nodeType() != 'nurbsSurface':
        surface = surface.getShape()
    surfaceTransform = surface.getParent()

    pymel.parentConstraint(surface.getParent(), jointGroup, maintainOffset=False)
    pymel.scaleConstraint(surface.getParent(), jointGroup, maintainOffset=False)

    minU, maxU = surface.minMaxRangeU.get()
    minV, maxV = surface.minMaxRangeV.get()

    spansU, spansV = surface.spansUV.get()

    if jointsArePerSpan:
        jointsU = numOfJointUV[0]*spansU
        jointsV = numOfJointUV[1]*spansV

    else:
        jointsU, jointsV = numOfJointUV

    # create joints
    jointInfoDict = {}
    jointListOfLists = []
    for iU in range(jointsU):
        jointListOfLists.append([])

        for iV in range(jointsV):
            #buildJoint = True
            #if wrapU:
                #if iU == 0 or iU == jointsU-1: # first or last
                    #if iV > (jointsV / 2.0):
                        #buildJoint = False

            #if buildJoint:
            joint = pymel.createNode('joint')
            joint.rename('%s_slideJnt_u%s_v%s' % (surfaceTransform.nodeName(), str(iU), str(iV)))
            joint.setParent(jointGroup)
            aimConstraints, pointOnSurfaces = pointOnSurfaceConstraint(surface, joint, asPercent=False, wrapU=True, wrapV=True, worldSpace=False)
            aimConstraint = aimConstraints[0]
            pointOnSurface = pointOnSurfaces[0]

            uValue = (maxU/jointsU)*iU
            vValue = (maxV/jointsV)*iV

            aimConstraint.posU.set(uValue)
            aimConstraint.posV.set(vValue)

            jointInfoDict[joint] = {}
            jointInfoDict[joint]['aimConstraint'] = aimConstraint
            jointInfoDict[joint]['pointOnSurface'] = pointOnSurface
            jointInfoDict[joint]['uValue'] = uValue
            jointInfoDict[joint]['vValue'] = vValue
            jointInfoDict[joint]['uIndex'] = iU
            jointInfoDict[joint]['vIndex'] = iV

            jointListOfLists[iU].append(joint)

    # add next and previous joint info to joint info dict
    for iU in range(jointsU):
        for iV in range(jointsV):
            joint = jointListOfLists[iU][iV]

            # u --------
            if iU != jointsU-1:    # not last
                nextU = jointListOfLists[iU+1][iV]

            else:    # last row
                #if iV == 0: # then next is mid iV
                    #nextU = jointListOfLists[iU][jointsV/2]
                #elif jointsV/2 == iV: # then next is iV 0
                    #nextU = jointListOfLists[iU][0]
                #else:
                    #nextU = jointListOfLists[iU][jointsV-iV]
                #if iV == 0 or iV == jointsV-1:
                    #nextU = None
                #else:
                    #nextU = jointListOfLists[iU][int(maxV - iV)]
                nextU = None

            # --
            if iU != 0:    # not first
                prevU = jointListOfLists[iU-1][iV]

            else:    # first row
                #if iV == 0: # then next is mid iV
                    #prevU = jointListOfLists[iU][jointsV/2]
                #elif jointsV/2 == iV: # then next is iV 0
                    #prevU = jointListOfLists[iU][0]
                #else:
                    #prevU = jointListOfLists[iU][jointsV-iV]
                prevU = None
                #if iV == 0 or iV == jointsV-1:
                    #prevU = None
                #else:
                    #prevU = jointListOfLists[iU][int(maxV - iV)]

            # v --------
            if iV != jointsV-1:    # not last
                nextV = jointListOfLists[iU][iV+1]
            else:
                nextV = jointListOfLists[iU][0]

            # --
            if iV == 0:
                prevV = jointListOfLists[iU][jointsV-1]
            else:
                prevV = jointListOfLists[iU][iV-1]

            jointInfoDict[joint]['nextU'] = nextU
            jointInfoDict[joint]['prevU'] = prevU
            jointInfoDict[joint]['nextV'] = nextV
            jointInfoDict[joint]['prevV'] = prevV

    return jointInfoDict, jointListOfLists


def createSkinSlideJoints(surface, influenceTransforms, numOfJointUV=[2,2], jointsArePerSpan=True, wrapU=True):

    # parse args
    OOOOOOO = 'surface'; print '%s: ' % OOOOOOO, eval(OOOOOOO), ' ', type(eval(OOOOOOO))
    surface = ka_pymel.getAsPyNodes(surface)
    OOOOOOO = 'surface'; print '%s: ' % OOOOOOO, eval(OOOOOOO), ' ', type(eval(OOOOOOO))

    if surface.nodeType() != 'nurbsSurface':
        surface = surface.getShape()

    influenceTransforms = ka_pymel.getAsPyNodes(influenceTransforms)

    minU, maxU = surface.minMaxRangeU.get()
    minV, maxV = surface.minMaxRangeV.get()

    spansU, spansV = surface.spansUV.get()

    # create joint net
    jointInfoDict, jointListOfLists = createJointNetOnSurface(surface, numOfJointUV=numOfJointUV, jointsArePerSpan=jointsArePerSpan,)

    # create a closestPointOnSurface node for influenceTransform, and store information about it
    influenceTransformDict = {}
    for influenceTransform in influenceTransforms:
        closestPointOnSurface = pymel.createNode('closestPointOnSurface')
        surface.worldSpace >> closestPointOnSurface.inputSurface

        vectorProduct = pymel.createNode('vectorProduct')
        vectorProduct.operation.set(4)
        influenceTransform.worldMatrix[0] >> vectorProduct.matrix

        vectorProduct.output >> closestPointOnSurface.inPosition
        attachGroup = pymel.createNode('transform')

        influenceTransformDict[influenceTransform] = {}
        influenceTransformDict[influenceTransform]['closestPointOnSurface'] = closestPointOnSurface
        influenceTransformDict[influenceTransform]['closestU'] = closestPointOnSurface.parameterU.get()
        influenceTransformDict[influenceTransform]['closestV'] = closestPointOnSurface.parameterV.get()


    # find closest joint (in UV Space) to influenceTransform
    for influenceTransform in influenceTransforms:
        closestUV = [influenceTransformDict[influenceTransform]['closestU'], influenceTransformDict[influenceTransform]['closestV']]

        nearestDistance = None
        for iU, itemA in enumerate(jointListOfLists):
            for iV, joint in enumerate(jointListOfLists[iU]):
                uValue = jointInfoDict[joint]['uValue']
                vValue = jointInfoDict[joint]['vValue']

                uvDistance = ka_math.distanceBetween(closestUV, [uValue, vValue])

                if nearestDistance == None:
                    influenceTransformDict[influenceTransform]['nearestJoint'] = joint
                    nearestDistance = uvDistance

                else:
                    if uvDistance < nearestDistance:
                        influenceTransformDict[influenceTransform]['nearestJoint'] = joint
                        nearestDistance = uvDistance

    # add mirroredV attr to control joints
    for influenceTransform in influenceTransforms:
        controlJoint = influenceTransformDict[influenceTransform]['nearestJoint']
        aimConstraint = jointInfoDict[controlJoint]['aimConstraint']
        aimConstraint.addAttr('vMirrored', keyable=True)
        plusMinusAverage = pymel.createNode('plusMinusAverage')
        plusMinusAverage.input1D[0].set(maxV)
        plusMinusAverage.operation.set(2)
        aimConstraint.posV >> plusMinusAverage.input1D[1]
        plusMinusAverage.output1D >> aimConstraint.vMirrored


    controlJoints = []
    for influenceTransform in influenceTransformDict:
        controlJoints.append(influenceTransformDict[influenceTransform]['nearestJoint'])


    controlIUs = []
    controlIVs = []
    for influenceTransform in influenceTransformDict:
        controlJoint = influenceTransformDict[influenceTransform]['nearestJoint']
        controlJointIU = jointInfoDict[controlJoint]['uIndex']
        controlJointIV = jointInfoDict[controlJoint]['vIndex']

        if controlJointIU not in controlIUs:
            controlIUs.append(controlJointIU)

        if controlJointIV not in controlIVs:
            controlIVs.append(controlJointIV)


    def findNextAndPreviousUvDrivers(joint, direction='U', driverAttr='U', jointListOfLists=jointListOfLists,
                                     jointInfoDict=jointInfoDict, controlIUs=controlIUs, controlIVs=controlIVs, wrap=True):
        nextDriverAttr = None
        prevDriverAttr = None
        percentBetween = None

        # variable variables
        if direction == 'U':
            uvDirection = 'U'
            indexKey = 'uIndex'
            controlIndexList = controlIUs

        else:
            uvDirection = 'V'
            indexKey = 'vIndex'
            controlIndexList = controlIVs


        if driverAttr == 'U':
            attr = 'posU'
            attrPlus = 'uPlus1'
            attrMinus = 'uMinus1'
            secondaryAttr = 'posV'
            secondaryAttrPlus = 'vPlus1'
            secondaryAttrMinus = 'vMinus1'

        else:
            attr = 'posV'
            attrPlus = 'vPlus1'
            attrMinus = 'vMinus1'
            secondaryAttr = 'posU'
            secondaryAttrPlus = 'uPlus1'
            secondaryAttrMinus = 'uMinus1'


        nextDriver = None
        prevDriver = None

        print '-'*100
        OOOOOOO = 'joint'; print '%s: ' % OOOOOOO, eval(OOOOOOO), ' ', type(eval(OOOOOOO))
        OOOOOOO = 'direction'; print '%s: ' % OOOOOOO, eval(OOOOOOO), ' ', type(eval(OOOOOOO))

        # special cases ***************************************************
        jointIu = jointInfoDict[joint]['uIndex']
        jointIv = jointInfoDict[joint]['vIndex']
        lastU = (spansU*2)-1
        lastV = (spansV*2)-1
        midV = spansV
        if jointIu == 0 and jointIv == 0: # first U, first V
            nextDriver = jointListOfLists[0][1]
            prevDriver = jointListOfLists[0][lastV]
            nextDriverAttr = jointInfoDict[nextDriver]['aimConstraint'].attr(attr)
            prevDriverAttr = jointInfoDict[prevDriver]['aimConstraint'].attr(attr)
            percentBetween = 0.5
            return prevDriverAttr, nextDriverAttr, percentBetween

        elif jointIu == 0 and jointIv == maxV: # first U, mid V
            nextDriver = jointListOfLists[0][midV+1]
            prevDriver = jointListOfLists[0][midV-1]
            nextDriverAttr = jointInfoDict[nextDriver]['aimConstraint'].attr(attr)
            prevDriverAttr = jointInfoDict[prevDriver]['aimConstraint'].attr(attr)
            percentBetween = 0.5
            return prevDriverAttr, nextDriverAttr, percentBetween

        if jointIu == lastU and jointIv == 0: # last U, first V
            nextDriver = jointListOfLists[lastU][1]
            prevDriver = jointListOfLists[lastU][lastV]
            nextDriverAttr = jointInfoDict[nextDriver]['aimConstraint'].attr(attr)
            prevDriverAttr = jointInfoDict[prevDriver]['aimConstraint'].attr(attr)
            percentBetween = 0.5
            return prevDriverAttr, nextDriverAttr, percentBetween

        elif jointIu == lastU and jointIv == maxV: # last U, mid V
            nextDriver = jointListOfLists[lastU][midV+1]
            prevDriver = jointListOfLists[lastU][midV-1]
            nextDriverAttr = jointInfoDict[nextDriver]['aimConstraint'].attr(attr)
            prevDriverAttr = jointInfoDict[prevDriver]['aimConstraint'].attr(attr)
            percentBetween = 0.5
            return prevDriverAttr, nextDriverAttr, percentBetween

        OOOOOOO = 'jointIu'; print '%s: ' % OOOOOOO, eval(OOOOOOO), ' ', type(eval(OOOOOOO))
        OOOOOOO = 'jointIv'; print '%s: ' % OOOOOOO, eval(OOOOOOO), ' ', type(eval(OOOOOOO))
        OOOOOOO = 'lastU'; print '%s: ' % OOOOOOO, eval(OOOOOOO), ' ', type(eval(OOOOOOO))
        OOOOOOO = 'spansU'; print '%s: ' % OOOOOOO, eval(OOOOOOO), ' ', type(eval(OOOOOOO))

        # Find Next driver + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + +
        i = 0
        whileLimit = 100
        nextJoint = joint
        itterDirection = 'next'
        while not nextDriver:
            i += 1
            if i > whileLimit:
                pymel.error('whileLimit reached!')

            nextJointIu = jointInfoDict[nextJoint]['uIndex']
            nextJointIv = jointInfoDict[nextJoint]['vIndex']
            currentJoint = nextJoint
            nextJoint = jointInfoDict[nextJoint]['%s%s' % (itterDirection, uvDirection)]
            if nextJoint == None:
                if wrap: # only direction U has None values
                    oppositeV = (int(maxV)*numOfJointUV[1]) - nextJointIv
                    #jointInfoDict[currentJoint]['%s%s' % (itterDirection, uvDirection)] = jointListOfLists[nextJointIu][oppositeV]

                    print 'next ---'
                    OOOOOOO = 'oppositeV'; print '%s: ' % OOOOOOO, eval(OOOOOOO), ' ', type(eval(OOOOOOO))
                    nextJoint = jointListOfLists[nextJointIu][oppositeV]
                    itterDirection = 'prev'
                else:
                    break

            nextJointIndex = jointInfoDict[nextJoint][indexKey]
            if nextJointIndex in controlIndexList:
                nextDriver = nextJoint

            elif not jointInfoDict[nextJoint]['%s%s' % (itterDirection, uvDirection)]:
                nextDriver = nextJoint


        # Find Previous driver - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        i = 0
        whileLimit = 100
        prevJoint = joint
        itterDirection = 'prev'
        while not prevDriver:
            i += 1
            if i > whileLimit:
                pymel.error('whileLimit reached!')

            prevJointIu = jointInfoDict[prevJoint]['uIndex']
            prevJointIv = jointInfoDict[prevJoint]['vIndex']
            currentJoint = prevJoint
            prevJoint = jointInfoDict[prevJoint]['%s%s' % (itterDirection, uvDirection)]
            if prevJoint == None:
                if wrap: # only direction U has None values
                    oppositeV = (int(maxV)*numOfJointUV[1]) - prevJointIv
                    #jointInfoDict[currentJoint]['%s%s' % (itterDirection, uvDirection)] = jointListOfLists[prevJointIu][oppositeV]

                    print 'prev ---'
                    OOOOOOO = 'oppositeV'; print '%s: ' % OOOOOOO, eval(OOOOOOO), ' ', type(eval(OOOOOOO))
                    prevJoint = jointListOfLists[prevJointIu][oppositeV]
                    itterDirection = 'next'


                else:
                    break

            prevJointIndex = jointInfoDict[prevJoint][indexKey]
            if prevJointIndex in controlIndexList:
                prevDriver = prevJoint

            elif not jointInfoDict[prevJoint]['%s%s' % (itterDirection, uvDirection)]:
                prevDriver = prevJoint

        drivenValue = jointInfoDict[joint]['aimConstraint'].attr(attr).get()
        nextDriverValue = jointInfoDict[nextDriver]['aimConstraint'].attr(attr).get()
        prevDriverValue = jointInfoDict[prevDriver]['aimConstraint'].attr(attr).get()



        # decide attributes involved and their order ------------------------------------------------
        if driverAttr == 'U': # driving U attr
            nextDriverAttr = jointInfoDict[nextDriver]['aimConstraint'].attr(attr)
            prevDriverAttr = jointInfoDict[prevDriver]['aimConstraint'].attr(attr)

            # the rare case that we are wraping arount the U pole
            if direction == 'U':
                if jointIv != 0 and jointIv != midV: # not first or mid
                    nextDriverIv = jointInfoDict[nextDriver]['vIndex']
                    prevDriverIv = jointInfoDict[prevDriver]['vIndex']
                    if jointIv != nextDriverIv or jointIv != prevDriverIv: # they have different V params
                        if drivenValue > maxU*0.5:
                            nextDriverAttr = jointInfoDict[nextDriver]['aimConstraint'].attr(attrPlus)
                            prevDriverAttr = jointInfoDict[prevDriver]['aimConstraint'].attr(attr)
                        else:
                            nextDriverAttr = jointInfoDict[nextDriver]['aimConstraint'].attr(attr)
                            prevDriverAttr = jointInfoDict[prevDriver]['aimConstraint'].attr(attrMinus)

        else: # ==  V
            if nextDriverValue < drivenValue:
                nextDriverAttr = jointInfoDict[nextDriver]['aimConstraint'].attr(attrPlus)
            else:
                nextDriverAttr = jointInfoDict[nextDriver]['aimConstraint'].attr(attr)

            if prevDriverValue > drivenValue:
                prevDriverAttr = jointInfoDict[prevDriver]['aimConstraint'].attr(attrMinus)
            else:
                prevDriverAttr = jointInfoDict[prevDriver]['aimConstraint'].attr(attr)

            # rare case where the next and previous drivers are actual control points on opposite
            # sides of the mesh, wrapping the top or bottom
            if direction == 'U':
                if jointIv != 0 and jointIv != midV: # not first or mid
                    nextDriverIv = jointInfoDict[nextDriver]['vIndex']
                    prevDriverIv = jointInfoDict[prevDriver]['vIndex']
                    if jointIv != nextDriverIv:
                        nextDriverAttr = jointInfoDict[nextDriver]['aimConstraint'].attr('vMirrored')

                    if jointIv != prevDriverIv: # they have different V params
                        prevDriverAttr = jointInfoDict[prevDriver]['aimConstraint'].attr('vMirrored')


        nextDriverValue = nextDriverAttr.get()
        prevDriverValue = prevDriverAttr.get()

        OOOOOOO = 'nextDriverAttr'; print '%s: ' % OOOOOOO, eval(OOOOOOO), ' ', type(eval(OOOOOOO))
        OOOOOOO = 'prevDriverAttr'; print '%s: ' % OOOOOOO, eval(OOOOOOO), ' ', type(eval(OOOOOOO))
        OOOOOOO = 'nextDriverValue'; print '%s: ' % OOOOOOO, eval(OOOOOOO), ' ', type(eval(OOOOOOO))
        OOOOOOO = 'prevDriverValue'; print '%s: ' % OOOOOOO, eval(OOOOOOO), ' ', type(eval(OOOOOOO))



        if direction == driverAttr:
            distanceBetween = nextDriverValue - prevDriverValue
            distanceOfJoint = drivenValue - prevDriverValue
            OOOOOOO = 'distanceBetween'; print '%s: ' % OOOOOOO, eval(OOOOOOO), ' ', type(eval(OOOOOOO))
            OOOOOOO = 'distanceOfJoint'; print '%s: ' % OOOOOOO, eval(OOOOOOO), ' ', type(eval(OOOOOOO))

            percentBetween = 1.0 / (distanceBetween / distanceOfJoint)

        else: # USE SECONDARY ATTR TO PRODUCE PERCENTAGE
            secondaryDrivenValue = jointInfoDict[joint]['aimConstraint'].attr(secondaryAttr).get()
            secondaryNextDriverValue = jointInfoDict[nextDriver]['aimConstraint'].attr(secondaryAttr).get()
            secondaryPrevDriverValue = jointInfoDict[prevDriver]['aimConstraint'].attr(secondaryAttr).get()

            if secondaryNextDriverValue < secondaryDrivenValue:
                secondaryNextDriverAttr = jointInfoDict[nextDriver]['aimConstraint'].attr(secondaryAttrPlus)
            else:
                secondaryNextDriverAttr = jointInfoDict[nextDriver]['aimConstraint'].attr(secondaryAttr)

            if secondaryPrevDriverValue > secondaryDrivenValue:
                secondaryPrevDriverAttr = jointInfoDict[prevDriver]['aimConstraint'].attr(secondaryAttrMinus)
            else:
                secondaryPrevDriverAttr = jointInfoDict[prevDriver]['aimConstraint'].attr(secondaryAttr)

            secondaryNextDriverValue = secondaryNextDriverAttr.get()
            secondaryPrevDriverValue = secondaryPrevDriverAttr.get()

            distanceBetween = secondaryNextDriverValue - secondaryPrevDriverValue
            distanceOfJoint = secondaryDrivenValue - secondaryPrevDriverValue

            OOOOOOO = 'secondaryPrevDriverAttr'; print '%s: ' % OOOOOOO, eval(OOOOOOO), ' ', type(eval(OOOOOOO))
            OOOOOOO = 'secondaryNextDriverAttr'; print '%s: ' % OOOOOOO, eval(OOOOOOO), ' ', type(eval(OOOOOOO))
            OOOOOOO = 'secondaryNextDriverValue'; print '%s: ' % OOOOOOO, eval(OOOOOOO), ' ', type(eval(OOOOOOO))
            OOOOOOO = 'secondaryPrevDriverValue'; print '%s: ' % OOOOOOO, eval(OOOOOOO), ' ', type(eval(OOOOOOO))

            OOOOOOO = 'distanceBetween'; print '%s: ' % OOOOOOO, eval(OOOOOOO), ' ', type(eval(OOOOOOO))
            OOOOOOO = 'distanceOfJoint'; print '%s: ' % OOOOOOO, eval(OOOOOOO), ' ', type(eval(OOOOOOO))
            percentBetween = 1.0 / (distanceBetween / distanceOfJoint)

            OOOOOOO = 'percentBetween'; print '%s: ' % OOOOOOO, eval(OOOOOOO), ' ', type(eval(OOOOOOO))

            percentBetween = ka_math.softenRange(percentBetween)


        OOOOOOO = 'distanceBetween'; print '%s: ' % OOOOOOO, eval(OOOOOOO), ' ', type(eval(OOOOOOO))
        OOOOOOO = 'distanceOfJoint'; print '%s: ' % OOOOOOO, eval(OOOOOOO), ' ', type(eval(OOOOOOO))
        OOOOOOO = 'percentBetween'; print '%s: ' % OOOOOOO, eval(OOOOOOO), ' ', type(eval(OOOOOOO))



        return prevDriverAttr, nextDriverAttr, percentBetween


    # connect all but control joints
    for iU, itemA in enumerate(jointListOfLists):
        for iV, joint in enumerate(jointListOfLists[iU]):
            posU_relativeValue_attr = None
            posV_relativeValue_attr = None

            posU_driverA_attr = None
            posU_driverB_attr = None
            percentBetweenU = None

            posV_driverA_attr = None
            posV_driverB_attr = None
            percentBetweenV = None



            #if iU != 0 and iU != len(jointListOfLists)-1: # not top or bottom
            if not joint in controlJoints:
                # FIND U DRIVERS
                if iU in controlIUs: # IS ON A CONTROL ROW
                    # drive V directly between control points
                    posU_driverA_attr, posU_driverB_attr, percentBetweenU = findNextAndPreviousUvDrivers(joint, direction='V', driverAttr='U')

                else:
                    posU_driverA_attr, posU_driverB_attr, percentBetweenU = findNextAndPreviousUvDrivers(joint, direction='U', driverAttr='U')

                # FIND V DRIVERS
                if iV in controlIVs: # IS ON A CONTROL ROW
                    # drive V directly between control points
                    posV_driverA_attr, posV_driverB_attr, percentBetweenV = findNextAndPreviousUvDrivers(joint, direction='U', driverAttr='V')

                else:
                    posV_driverA_attr, posV_driverB_attr, percentBetweenV = findNextAndPreviousUvDrivers(joint, direction='V', driverAttr='V')


                blendColorU = pymel.createNode('blendColors')
                blendColorV = pymel.createNode('blendColors')

                posU_driverA_attr >> blendColorU.color2R
                posU_driverB_attr >> blendColorU.color1R

                posV_driverA_attr >> blendColorV.color2R
                posV_driverB_attr >> blendColorV.color1R

                blendColorU.blender.set(percentBetweenU)
                blendColorU.outputR >> jointInfoDict[joint]['aimConstraint'].posU

                blendColorV.blender.set(percentBetweenV)
                blendColorV.outputR >> jointInfoDict[joint]['aimConstraint'].posV

                ## BASE ROTATION OF NEIBOR'S POSITION
                aimConstraint = jointInfoDict[joint]['aimConstraint']

                if jointInfoDict[joint]['nextU'] and jointInfoDict[joint]['prevU']:
                    # create U average vector
                    negVector_md = pymel.createNode('multiplyDivide')
                    negVector_md.input2.set(-1,-1,-1)

                    averageVector_pma = pymel.createNode('plusMinusAverage')
                    averageVector_pma.operation.set(3)

                    next_joint = jointInfoDict[joint]['nextU']
                    next_pointOnSurface = jointInfoDict[next_joint]['pointOnSurface']
                    prev_joint = jointInfoDict[joint]['prevU']
                    prev_pointOnSurface = jointInfoDict[prev_joint]['pointOnSurface']

                    next_pointOnSurface.position >> averageVector_pma.input3D[0]
                    prev_pointOnSurface.position >> negVector_md.input1
                    negVector_md.output >> averageVector_pma.input3D[1]

                    averageVector_pma.output3Dx >> aimConstraint.worldUpVectorX
                    averageVector_pma.output3Dy >> aimConstraint.worldUpVectorY
                    averageVector_pma.output3Dz >> aimConstraint.worldUpVectorZ


    # connect closest joint to influenceTransform's closestPointOnSurface node
    for influenceTransform in influenceTransformDict:
        clostestPointNode = influenceTransformDict[influenceTransform]['closestPointOnSurface']
        closestU = influenceTransformDict[influenceTransform]['closestU']
        closestV = influenceTransformDict[influenceTransform]['closestV']

        addNode = pymel.createNode('plusMinusAverage')
        conditionA = pymel.createNode('condition')
        conditionB = pymel.createNode('condition')
        halfV = maxV*0.5
        adjacentV = maxV - closestV

        clostestPointNode.parameterV >> conditionA.firstTerm
        clostestPointNode.parameterV >> conditionB.firstTerm
        clostestPointNode.parameterV >> conditionA.colorIfFalseR
        clostestPointNode.parameterV >> conditionB.colorIfFalseR
        conditionA.outColorR >> conditionB.colorIfTrueR

        if closestV < halfV:
            conditionA.secondTerm.set(adjacentV)
            conditionB.secondTerm.set(maxV)
            addNode.input1D[1].set(maxV)
            addNode.operation.set(2)

            conditionA.operation.set(2) # greater than
            conditionB.operation.set(4) # less than

            clostestPointNode.parameterV >> addNode.input1D[0]
            addNode.output1D >> conditionA.colorIfTrueR

        else:
            conditionA.secondTerm.set(adjacentV)
            conditionB.secondTerm.set(0.0)
            addNode.input1D[0].set(maxV)
            addNode.operation.set(1)

            conditionA.operation.set(4) # less than
            conditionB.operation.set(2) # greater than

            clostestPointNode.parameterV >> addNode.input1D[1]
            addNode.output1D >> conditionA.colorIfTrueR



        followingJoint = influenceTransformDict[influenceTransform]['nearestJoint']
        followingJoint.radius.set(followingJoint.radius.get()*1.5)
        followingJoint.overrideEnabled.set(1)
        followingJoint.overrideColor.set(17)
        followingAimConstraint = jointInfoDict[followingJoint]['aimConstraint']

        clostestPointNode.parameterU >> followingAimConstraint.posU
        conditionB.outColorR >> followingAimConstraint.posV


def getNumberOfCvsInU(nurbsShape):
    if nurbsShape.formU.get() == 0:
        extraPoints = nurbsShape.degreeUV.get()[0]
    elif nurbsShape.formU.get() == 2:
        extraPoints = 0
    else:
        pymel.error('dont know how to deal with form type "closed"')

    return nurbsShape.spansU.get() + extraPoints


def getNumberOfCvsInV(nurbsShape):
    if nurbsShape.formV.get() == 0:
        extraPoints = nurbsShape.degreeUV.get()[1]
    elif nurbsShape.formV.get() == 2:
        extraPoints = 0
    else:
        pymel.error('dont know how to deal with form type "closed"')

    return nurbsShape.spansV.get() + extraPoints


def getNurbsAverageLength(nurbsShape, u=True, v=True):
    lengths = []

    numOfCvsU = getNumberOfCvsInU(nurbsShape)
    numOfCvsV = getNumberOfCvsInV(nurbsShape)
    if u:
        strandLengths = []
        for iV in range(numOfCvsV):
            strandLength = 0.0
            previousPoint = None

            for iU in range(numOfCvsU):
                cv = nurbsShape.cv[iU][iV]
                cvPos = pymel.xform(cv, query=True, translation=True, worldSpace=True)

                if previousPoint != None:
                    strandLength += ka_math.distanceBetween(previousPoint, cvPos)

                previousPoint = cvPos

            strandLengths.append(strandLength)

        lengths.append(ka_math.average(strandLengths))

    if v:
        strandLengths = []
        for iU in range(numOfCvsU):
            strandLength = 0.0
            previousPoint = None

            for iV in range(numOfCvsV):
                cv = nurbsShape.cv[iU][iV]
                cvPos = pymel.xform(cv, query=True, translation=True, worldSpace=True)

                if previousPoint != None:
                    strandLength += ka_math.distanceBetween(previousPoint, cvPos)

                previousPoint = cvPos

            strandLengths.append(strandLength)

        lengths.append(ka_math.average(strandLengths))

    return lengths



def createJointStrandOnNurbs(numberOfJoints=5, name='ribbon', nurbs=None):
    #cmds.loadPlugin('ANY_Toolset')


    if nurbs == None:
        nurbs = pymel.nurbsPlane(constructionHistory=True, object=True, u=1, v=1, axis=[0, 0, 1], width=1, lengthRatio=5)[0]
        nurbs.rename(name+'_nurbsRibbon')

    nurbsShape = nurbs.getShape()
    nurbsShape.rename('%sShape' % nurbs.nodeName(stripNamespace=True))
    controlGroup = pymel.createNode('transform')

    nurbs.t >> controlGroup.t
    nurbs.r >> controlGroup.r
    nurbs.s >> controlGroup.s

    lengthU, lengthV = getNurbsAverageLength(nurbsShape)


    joints = []
    attachedXforms = []
    jointInfo = {}
    controls = []

    infoDict = {}
    infoDict['controlGroup'] = controlGroup
    infoDict['nurbs'] = nurbs
    infoDict['jointInfoDict'] = jointInfo
    infoDict['joints'] = joints
    infoDict['attachedXforms'] = attachedXforms


    last = numberOfJoints-1
    if numberOfJoints%2: #number is odd
        half = (numberOfJoints / 2 + (numberOfJoints%2) ) - 1 # minus one at because we count form 0
    else:
        half = ((numberOfJoints / 2) + 0.5 ) - 1

    for i in range(numberOfJoints):
        attachedXform = pymel.createNode('transform')
        attachedXform.setParent(controlGroup)
        attachedXforms.append(attachedXform)

        # joint
        joint = pymel.createNode('joint')
        joint.setParent(attachedXform)
        joints.append(joint)


        aimConstraint, pointOnSurface = pointOnSurfaceConstraint(nurbs, attachedXform, asPercent=True, worldSpace=False)
        aimConstraint = aimConstraint[0]
        pointOnSurface = pointOnSurface[0]

        aimConstraint.aimVector.set(0,0,1)
        aimConstraint.upVector.set(1,0,0)


        plusMinusAverageA = pymel.createNode('plusMinusAverage')
        plusMinusAverageB = pymel.createNode('plusMinusAverage')
        plusMinusAverageA.output2D.output2Dx >> plusMinusAverageB.input2D[0].input2Dx
        plusMinusAverageA.output2D.output2Dy >> plusMinusAverageB.input2D[0].input2Dy

        plusMinusAverageB.output2D.output2Dx >> aimConstraint.posU
        plusMinusAverageB.output2D.output2Dy >> aimConstraint.posV

        jointInfo[joint] = {}
        jointInfo[joint]['aimConstraint'] = aimConstraint
        jointInfo[joint]['pointOnSurface'] = pointOnSurface
        jointInfo[joint]['plusMinusAverageA'] = plusMinusAverageA
        jointInfo[joint]['plusMinusAverageB'] = plusMinusAverageB
        jointInfo[joint]['basePercent'] = (1.0/(numberOfJoints-1.0))*i
        if i != 0:
            jointInfo[joint]['prevJoint'] = joints[-2]
            jointInfo[joints[-2]]['nextJoint'] = joint


    infoDict['jointInfoDict'][joints[0]]['plusMinusAverageA'].input2D[0].input2Dx.set(0.5)
    infoDict['jointInfoDict'][joints[1]]['plusMinusAverageA'].input2D[0].input2Dx.set(0.5)
    infoDict['jointInfoDict'][joints[1]]['plusMinusAverageA'].input2D[0].input2Dy.set(5)

    for i in range(numberOfJoints):
        if i != 0 and i != last:
            joint = joints[i]
            prevJoint = joints[0]
            nextJoint = joints[-1]

            if i == half:
                nextJoint = jointInfo[joint]['nextJoint']
                prevJoint = jointInfo[joint]['prevJoint']
                percent = 0.5

            elif i < half:
                prevJoint = jointInfo[joint]['prevJoint']
                nextJoint = joints[-1]

                percent = jointInfo[joint]['basePercent'] - jointInfo[prevJoint]['basePercent']

            elif i > half:
                prevJoint = joints[0]
                nextJoint = jointInfo[joint]['nextJoint']

                ratio = 1.0 / jointInfo[nextJoint]['basePercent']

                percent = jointInfo[joint]['basePercent'] * ratio

            blendColor = pymel.createNode('blendColors')
            #blendColorB = pymel.createNode('blendColors')
            infoDict['jointInfoDict'][joints[i]]['blendColor'] = blendColor
            #infoDict['jointInfoDict'][joints[i]]['blendColorB'] = blendColorB

            jointInfo[nextJoint]['plusMinusAverageA'].output2D.output2Dx >> blendColor.color1R
            jointInfo[prevJoint]['plusMinusAverageA'].output2D.output2Dx >> blendColor.color2R


            jointInfo[nextJoint]['plusMinusAverageA'].output2D.output2Dy >> blendColor.color1G
            jointInfo[prevJoint]['plusMinusAverageA'].output2D.output2Dy >> blendColor.color2G


            joint = joints[i]

            nextPerc = jointInfo[nextJoint]['basePercent']
            prevPerc = jointInfo[prevJoint]['basePercent']
            rangePerc = nextPerc - prevPerc
            percent = (jointInfo[joint]['basePercent']-prevPerc) / rangePerc

            blendColor.blender.set(percent)
            #blendColorB.blender.set(percent)


            blendColor.outputR >> jointInfo[joint]['plusMinusAverageA'].input2D[1].input2Dx
            blendColor.outputG >> jointInfo[joint]['plusMinusAverageA'].input2D[1].input2Dy

    return infoDict



def closestPointOnCurve(point, curve):
    """Returns the parameter and position of the clostest point to the given point, on the
    given curve"""

    if ka_pymel.isPyNode(curve):
        curve = str(curve)

    OOOOOOO = "curve"; print '%s: ' % OOOOOOO, eval(OOOOOOO), ' ', type(eval(OOOOOOO))
    # put curve into the MObject
    tempList = om.MSelectionList()
    tempList.add(curve)
    curveObj = om.MObject()
    tempList.getDependNode(0, curveObj)  # puts the 0 index of tempList's depend node into curveObj

    # get the dagpath of the object
    dagpath = om.MDagPath()
    tempList.getDagPath(0, dagpath)

    # define the curve object as type MFnNurbsCurve
    curveMF = om.MFnNurbsCurve(dagpath)

    # what's the input point (in world)
    point = om.MPoint( point[0], point[1], point[2])

    # define the parameter as a double * (pointer)
    prm = om.MScriptUtil()
    pointer = prm.asDoublePtr()
    om.MScriptUtil.setDouble (pointer, 0.0)

    # set tolerance
    tolerance = .00000001

    # set the object space
    space = om.MSpace.kObject

    # result will be the worldspace point
    result = om.MPoint()
    result = curveMF.closestPoint (point, pointer,  0.0, space)

    position = [(result.x), (result.y), (result.z)]
    curvePoint = om.MPoint ((result.x), (result.y), (result.z))

    parameter = om.MScriptUtil.getDouble (pointer)

    # just return - parameter, then world space coord.
    return [parameter, ((result.x), (result.y), (result.z))]