#====================================================================================
#====================================================================================
#
# ka_constraints
#
# DESCRIPTION:
#   A module for creating and modifing constraints
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
import ast as ast

import pymel.core as pymel
import maya.cmds as cmds
import maya.mel as mel

import ka_maya.ka_skinCluster as ka_skinCluster
import ka_maya.ka_pymel as ka_pymel
import ka_maya.ka_weightPainting as ka_weightPainting
import ka_maya.ka_geometry as ka_geometry

def constrain(sel=None, t=0, s=0, r=0, pointOnSurface=0, aimBetween=0, withOffset=False, offsetGroup=False):
    '''snaps objects to A to object B based on translate rotate or scale'''
    if sel==None:
        sel = pymel.ls(selection=True)


    constraintObject = sel[-1]
    constraintTargets = sel[:-1]


    if t:
        constraint = pymel.pointConstraint(constraintTargets, constraintObject)

    if s:
        constraint = pymel.scaleConstraint(constraintTargets, constraintObject)

    if r:
        constraint = pymel.orientConstraint(constraintTargets, constraintObject)

    if aimBetween:
        constraintObjects = sel[2:]
        constraintTargets = sel[0:2]

        for constraintObject in constraintObjects:

            aimConstraints = []
            for i, constraintTarget in enumerate(constraintTargets):
                aimConstraint = pymel.createNode('aimConstraint')
                aimConstraint.rename(constraintObject.nodeName()+'aimBetween_aimConstraint')

                constraintTarget.translate >> aimConstraint.target[i].targetTranslate
                constraintTarget.parentMatrix >> aimConstraint.target[i].targetParentMatrix
                constraintTarget.rotatePivotTranslate >> aimConstraint.target[i].targetRotateTranslate
                constraintTarget.rotatePivot >> aimConstraint.target[i].targetRotatePivot

                constraintObject.parentInverseMatrix >> aimConstraint.constraintParentInverseMatrix
                constraintObject.rotateOrder >> aimConstraint.constraintRotateOrder
                constraintObject.rotatePivotTranslate >> aimConstraint.constraintRotateTranslate
                constraintObject.rotatePivot >> aimConstraint.constraintRotatePivot
                constraintObject.translate >> aimConstraint.constraintTranslate

                aimConstraint.upVector.set(0,0,1)
                aimConstraint.worldUpVector.set(0,0,1)
                aimConstraint.worldUpType.set(2)
                constraintTarget.worldMatrix >> aimConstraint.worldUpMatrix

                aimConstraints.append(aimConstraint)

            aimConstraints[0].aimVectorX.set(1)

            aimConstraints[1].aimVectorX.set(-1)
            #aimConstraints[1].upVector.set(0,0,1)
            #aimConstraints[1].worldUpType.set(2)

            orientConstraint = pymel.createNode('orientConstraint',)
            orientConstraint.rename(constraintObject.nodeName()+'aimBetween_orientConstraint')
            orientConstraint.interpType.set(2)

            aimConstraints[0].constraintRotate >> orientConstraint.target[0].targetRotate
            aimConstraints[1].constraintRotate >> orientConstraint.target[1].targetRotate

            constraintObject.rotateOrder >> orientConstraint.constraintRotateOrder
            constraintObject.parentInverseMatrix >> orientConstraint.constraintParentInverseMatrix
            orientConstraint.constraintRotate >> constraintObject.rotate


            #vectorProduct = pymel.createNode('vectorProduct')
            #vectorProduct.rename('aimBetween_vectorProduct')

            #vectorProduct.operation.set(3)
            #vectorProduct.input1Z.set(1)
            #constraintObject.parentMatrix >> vectorProduct.matrix
            #vectorProduct.output >> aimConstraints[0].worldUpVector
            #vectorProduct.output >> aimConstraints[1].worldUpVector

            pymel.parent(aimConstraints[0], aimConstraints[1], orientConstraint)
            pymel.parent(orientConstraint, constraintObject)



    if pointOnSurface:

        selection = pymel.ls(selection=True)
        if not pymel.nodeType(selection[0].getParent()) != 'nurbsCurve':
            pymel.warning('first selected object should be a nurbs surface')

        if pymel.nodeType(selection[0]) != 'nurbsSurface':
            nurbsSurface = selection[0].getShape()
        else:
            nurbsSurface = selection[0]


        for each in selection[1:]:

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
            aimConstraint.addAttr('posU', maxValue=1.0, minValue=0.0, keyable=True)
            aimConstraint.addAttr('posV', maxValue=1.0, minValue=0.0, keyable=True)
            pymel.addAttr(aimConstraint, longName='outPosition', keyable=False, attributeType='float3')
            pymel.addAttr(aimConstraint, longName='outPositionX', keyable=False, attributeType='float', parent='outPosition')
            pymel.addAttr(aimConstraint, longName='outPositionY', keyable=False, attributeType='float', parent='outPosition')
            pymel.addAttr(aimConstraint, longName='outPositionZ', keyable=False, attributeType='float', parent='outPosition')

            closestPointOnSurface = pymel.createNode('closestPointOnSurface',)
            closestPointOnSurface.rename(baseName+'ClosestPointOnSurface')
            nurbsSurface.worldSpace[0] >> closestPointOnSurface.inputSurface
            closestPointOnSurface.inPosition.set(eachWorldPosition)

            closestU = closestPointOnSurface.parameterU.get()
            maxU = nurbsSurface.maxValueU.get()
            normalizedU = closestU / maxU

            closestV = closestPointOnSurface.parameterV.get()
            maxV = nurbsSurface.maxValueV.get()
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
            pointOnSurfaceInfo.turnOnPercentage.set(1)
            nurbsSurface.worldSpace[0] >> pointOnSurfaceInfo.inputSurface
            aimConstraint.posU >> pointOnSurfaceInfo.parameterU
            aimConstraint.posV >> pointOnSurfaceInfo.parameterV
            pointOnSurfaceInfo.position >> aimConstraint.outPosition

            vectorProduct = pymel.createNode('vectorProduct')
            aimConstraint.outPosition >> vectorProduct.input1
            surfaceConstraintGroup.parentInverseMatrix[0] >> vectorProduct.matrix
            vectorProduct.operation.set(4)

            vectorProduct.output >> surfaceConstraintGroup.t

            if pymel.nodeType(surfaceConstraintGroup) == 'joint':
                surfaceConstraintGroup.jointOrient >> aimConstraint.constraintJointOrient
            surfaceConstraintGroup.translate >> aimConstraint.constraintTranslate
            surfaceConstraintGroup.rotateOrder >> aimConstraint.constraintRotateOrder
            surfaceConstraintGroup.parentInverseMatrix[0] >> aimConstraint.constraintParentInverseMatrix
            surfaceConstraintGroup.rotatePivot >> aimConstraint.constraintRotatePivot
            surfaceConstraintGroup.rotatePivotTranslate >> aimConstraint.constraintRotateTranslate

            plusMinusAverage = pymel.createNode('plusMinusAverage')
            pointOnSurfaceInfo.normal >> plusMinusAverage.input3D[0]
            pointOnSurfaceInfo.position >> plusMinusAverage.input3D[1]

            plusMinusAverage.output3D >> aimConstraint.target[0].targetTranslate

            pointOnSurfaceInfo.tangentU >> aimConstraint.worldUpVector
            aimConstraint.constraintRotate >> surfaceConstraintGroup.r

            pymel.parent(aimConstraint, surfaceConstraintGroup)

            if withOffset:
                pymel.parentConstraint(surfaceConstraintGroup, each, maintainOffset=True)

    pymel.select(constraintObject)


def pointOnSurfaceConstraint(surface=None, nodes=None, withOffset=False, asPercent=True, wrapU=False, wrapV=False):

    def createUvFlipKeyFrame(max=1):

        animCurveNode = pm.createNode('animCurveUU')

        pymel.setKeyframe(animCurveNode, insert=True, float=0, outTangentType='linear')
        pymel.setKeyframe(animCurveNode, insert=True, float=max, value=float(max), inTangentType='linear', outTangentType='step')
        pymel.keyframe(animCurveNode, edit=True, float=(int(max),int(max)), absolute=True, valueChange=float(max),)
        animCurveNode.preInfinity.set(3)
        animCurveNode.postInfinity.set(3)

        pymel.keyTangent(animCurveNode, edit=True, float=(0, 0), outTangentType='linear')
        pymel.keyTangent(animCurveNode,  edit=True, float=(int(max), int(max)), inTangentType='linear', outTangentType='step')

        return animCurveNode

    selection = pymel.ls(selection=True)

    if surface == None:
        surface = selection[0]

    if nodes == None:
        nodes = selection[1:]

    if not isinstance(nodes, list):
        nodes = [nodes]

    if pymel.nodeType(surface) != 'nurbsSurface':
        surface = surface.getShape()


    aimConstraints = []
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
            aimConstraint.addAttr('posU', softMaxValue=surface.minMaxRangeV.get()[1], softMinValue=0.0, keyable=True)
            aimConstraint.addAttr('posV', softMaxValue=surface.minMaxRangeV.get()[1], softMinValue=0.0, keyable=True)

        pymel.addAttr(aimConstraint, longName='outPosition', keyable=False, attributeType='float3')
        pymel.addAttr(aimConstraint, longName='outPositionX', keyable=False, attributeType='float', parent='outPosition')
        pymel.addAttr(aimConstraint, longName='outPositionY', keyable=False, attributeType='float', parent='outPosition')
        pymel.addAttr(aimConstraint, longName='outPositionZ', keyable=False, attributeType='float', parent='outPosition')

        closestPointOnSurface = pymel.createNode('closestPointOnSurface',)
        closestPointOnSurface.rename(baseName+'ClosestPointOnSurface')
        surface.worldSpace[0] >> closestPointOnSurface.inputSurface
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
        surface.worldSpace[0] >> pointOnSurfaceInfo.inputSurface

        if wrapU:
            uvFlipKey = createUvFlipKeyFrame(surface.nurbsShape.minMaxRangeU.get()[1])
            aimConstraint.posU >> uvFlipKey.input
            uvFlipKey.output >> pointOnSurfaceInfo.parameterU
        else:
            aimConstraint.posU >> pointOnSurfaceInfo.parameterU

        if wrapV:
            uvFlipKey = createUvFlipKeyFrame(surface.nurbsShape.minMaxRangeV.get()[1])
            aimConstraint.posV >> uvFlipKey.input
            uvFlipKey.output >> pointOnSurfaceInfo.parameterV
        else:
            aimConstraint.posV >> pointOnSurfaceInfo.parameterV



        pointOnSurfaceInfo.position >> aimConstraint.outPosition

        vectorProduct = pymel.createNode('vectorProduct')
        aimConstraint.outPosition >> vectorProduct.input1
        surfaceConstraintGroup.parentInverseMatrix[0] >> vectorProduct.matrix
        vectorProduct.operation.set(4)

        vectorProduct.output >> surfaceConstraintGroup.t

        if pymel.nodeType(surfaceConstraintGroup) == 'joint':
            surfaceConstraintGroup.jointOrient >> aimConstraint.constraintJointOrient
        surfaceConstraintGroup.translate >> aimConstraint.constraintTranslate
        surfaceConstraintGroup.rotateOrder >> aimConstraint.constraintRotateOrder
        surfaceConstraintGroup.parentInverseMatrix[0] >> aimConstraint.constraintParentInverseMatrix
        surfaceConstraintGroup.rotatePivot >> aimConstraint.constraintRotatePivot
        surfaceConstraintGroup.rotatePivotTranslate >> aimConstraint.constraintRotateTranslate

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

    pymel.select(nodes)

    return aimConstraints


def localizeConstraint(constraint):
    '''replace constraint with a simplified version of itself that assumes all targets and destinations
    are in the same space'''

    if pymel.objectType(constraint) == 'orientConstraint':
        newConstraint = pymel.createNode('orientConstraint', name='local_'+constraint.nodeName())
        for i in range(constraint.target.get(size=True)):
            target = constraint.target[i].targetRotate.inputs()[0]
            target.rotate >> newConstraint.target[i].targetRotate
            newConstraint.target[i].targetWeight.set(constraint.target[i].targetWeight.get())

        destination = constraint.constraintRotateX.outputs()
        if not destination:
            destination = constraint.constraintRotateY.outputs()
        if not destination:
            destination = constraint.constraintRotateZ.outputs()
        destination = destination[0]

        newConstraint.constraintRotate >> destination.rotate
        pymel.delete(constraint)
        pymel.parent(newConstraint, destination)
        newConstraint.translate.set(0,0,0)
        newConstraint.rotate.set(0,0,0)

        return newConstraint

    if pymel.objectType(constraint) == 'aimConstraint':
        newConstraint = pymel.createNode('aimConstraint', name='local_'+constraint.nodeName())
        for i in range(constraint.target.get(size=True)):
            target = constraint.target[i].targetTranslate.inputs()[0]
            target.translate >> newConstraint.target[i].targetTranslate

            newConstraint.worldUpType.set(constraint.worldUpType.get())
            newConstraint.upVector.set(constraint.upVector.get())
            newConstraint.worldUpVector.set(constraint.worldUpVector.get())
            newConstraint.aimVector.set(constraint.aimVector.get())


            targetWorldUpMatrix = constraint.worldUpMatrix.inputs()
            if targetWorldUpMatrix:
                targetWorldUpMatrix = targetWorldUpMatrix[0]
                targetWorldUpMatrix.matrix >> newConstraint.worldUpMatrix


        destination = constraint.constraintRotateX.outputs()
        if not destination:
            destination = constraint.constraintRotateY.outputs()
        if not destination:
            destination = constraint.constraintRotateZ.outputs()
        destination = destination[0]

        newConstraint.constraintRotate >> destination.rotate
        destination.translate >> newConstraint.constraintTranslate
        pymel.delete(constraint)
        pymel.parent(newConstraint, destination)
        newConstraint.translate.set(0,0,0)
        newConstraint.rotate.set(0,0,0)

        return newConstraint


def nonTwistAim(driver=None, drivens=None, aimAxis=[1,0,0]):
    if driver==None or driven == None:
        sel = pymel.ls(selection=True)
        driver = sel[0]
        drivens = sel[1:]

    elif not isinstance(drivens):
        drivens = [drivens]

    for driven in drivens:
        possibleAimAxis = [[1,0,0,], [0,1,0,], [0,0,1,]]
        drivenParent = driven.getParent()
        aimConstraint = pymel.aimConstraint(driver, driven, worldUpType='objectrotation', worldUpObject=drivenParent, aimVector=aimAxis, worldUpVector=[0,0,1], upVector=[0,0,1], maintainOffset=False)

        vectorProductAim = pymel.createNode('vectorProduct')
        vectorProductAim.operation.set(3)
        drivenParent.matrix >> vectorProductAim.matrix

        XYZ = 'XYZ'
        for vector in vectorProductAim:
            for i, axis in enumerate(vector):
                if not axis:
                    vectorProduct = pymel.createNode('vectorProduct')
                    vectorProduct.operation.set(1)
                    vectorProduct.input2.set(vector)
                    vectorProductAim.output >> vectorProduct.input1
                    vectorProduct.outputX >> aimConstraint.attr('worldUpVector'+XYZ[i])
                    vectorProduct.outputX >> aimConstraint.attr('upVector'+XYZ[i])

    pymel.select(drivens)

def aimConstraintWithObjectRotationUp(constraintTarget=None, upObject=None, transformsToConstrain=None, aimVector=(1,0,0),
                                      upVector=(0,0,1)):
    """
    aim constrains node with a rotation up object.

    """

    # parse args
    if constraintTarget is None or upObject is None or transformsToConstrain is None:
        selection = pymel.ls(selection=True)
        if not selection:
            raise Exception('Nothing is selected')

        else:
            if constraintTarget is None:
                constraintTarget = selection[0]

            if upObject is None:
                upObject = selection[1]

            if transformsToConstrain is None:
                transformsToConstrain = selection[2:]

    # make constraints
    for transform in transformsToConstrain:
        pymel.aimConstraint(constraintTarget, transform, aimVector=aimVector, upVector=upVector, worldUpType='objectrotation', worldUpObject=upObject, worldUpVector=upVector)



def skinConstraint(components, transformsToConstrain, ):
    # parse args
    if not isinstance(components, list):
        components = [components]
    components = ka_pymel.getAsPyNodes(components)

    if not isinstance(transformsToConstrain, list):
        transformsToConstrain = [transformsToConstrain]
    transformsToConstrain = ka_pymel.getAsPyNodes(transformsToConstrain)

    # make constraints
    for transformToConstrain in transformsToConstrain:
        skinConstraint = pymel.createNode('parentConstraint')
        skinConstraint.rename(transformToConstrain.nodeName()+'SkinConstraint')
        skinConstraint.setParent(transformToConstrain)

        skinConstraint.addAttr('skinConstraintData', dt='string')
        skinConstraint.addAttr('initialWorldMatrix', at='matrix')

        skinConstraintData = {'components':ka_pymel.getAsStrings(components)

                             }
        skinConstraint.skinConstraintData.set(str(skinConstraintData))
        skinConstraint.initialWorldMatrix.set(transformToConstrain.worldMatrix.get())

        updateSkinConstraintWeights(skinConstraint)

    return skinConstraints


def updateSkinConstraintWeights(skinConstraint):
    skinConstraint = ka_pymel.getAsPyNodes(skinConstraint)
    skinConstraintData = ast.literal_eval(skinConstraint.skinConstraintData.get())

    cmds.select(skinConstraintData['components'])

    skinCluster = ka_skinCluster.findRelatedSkinCluster(components[0])

    # get componentInfoDict
    cmds.select(skinConstraintData['components'])
    componentInfoDict = ka_geometry.getComponentInfoDict()
    weightsDict = getWeights(componentInfoDict=componentInfoDict, getAdditionalData=True)
    print weightsDict
    pass

def updateSkinConstraint(skinConstraint):
    pass

def getAllSkinConstraints():
    pass

def updateAllSkinConstraints():
    pass