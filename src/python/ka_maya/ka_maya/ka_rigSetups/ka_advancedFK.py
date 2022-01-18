#====================================================================================
#====================================================================================
#
# ka_advanceFK
#
# DESCRIPTION:
#   makes a ribbon and curve to drive the position and rotation of a joint chain.
#   that joint chains position along that curve/nurb, will be detmined based on the
#   length of the full curve, not just on spans.
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

import pymel.core as pymel
import maya.cmds as cmds
import maya.mel as mel

import ka_maya.ka_util as ka_util#;reload(ka_util)
import ka_maya.ka_transforms as ka_transforms#;reload(ka_transforms)
import ka_maya.ka_naming as ka_naming#;reload(ka_naming)
import ka_maya.ka_constraints as ka_constraints    #;reload(ka_constraints)

def createFromSelection():
    buildMyTail()
    #selection = pymel.ls(selection=True)
    #_create(fkControls=selection, createGuideCurve=True)

def buildMyTail():
    filePath = '/corp/projects/scam/work/creatures/slyCooper/rigging/kandrews/hi_rig/maya/scenes/sly_tailRig_011.ma'
    cmds.file(filePath, force=True, open=True)
    fkControls = pymel.ls(['fk_tailA_ctl', 'fk_tailB_ctl', 'fk_tailC_ctl', 'fk_tailD_ctl', 'fk_tailE_ctl', 'fk_tailF_ctl', 'fk_tailG_ctl', 'fk_tailH_ctl'])
    endLocator = pymel.ls('fk_tailEnd_loc')[0]
    baseName = 'tail'
    _create(baseName, fkControls, endTransform=endLocator, createGuideCurve=True)


    for ctl in fkControls:
        ctl.rz.set(40)



def _create(baseName, fkControls=None, endTransform=None, createGuideCurve=False, ikSpline=True, ikSplineJoints=[], ikSpline_numOfJoints=60):
    """Creates an advanced FK setup.
    kwargs:
        fkControls - list of <pymel transforms> - the positioned controls
        endTransform - pymel transforms - a transform representing the end of the
                       setup

    """

    #kName = KName()


    relationshipDic = {}
    guideTransforms = fkControls + [endTransform]

    rigGroup = pymel.createNode('transform')
    rigGroup.rename(baseName+'_controlRig')

    ## CREATE BASIC CONTROLS =======================================
    relationshipDic[endTransform] = {}
    for i, fkControl in enumerate(fkControls):
        relationshipDic[fkControl] = {}

        try:
            fkControl.sx.set(lock=True, keyable=False)
            fkControl.sy.set(lock=True, keyable=False)
            fkControl.sz.set(lock=True, keyable=False)
            fkControl.v.set(lock=True, keyable=False)

        except:
            pass

        ## CREATE ZERO GROUP ---------------------------------------
        # create zero out group
        zeroGroup = pymel.createNode('transform')
        zeroGroup.rename(fkControl.nodeName()+'_zro')

        # snap zeroGroup
        ka_transforms.snap(t=1, r=1, snapTarget=fkControl, snapObjects=zeroGroup)

        # parent zeroGroup
        if i == 0:
            pymel.parent(zeroGroup, rigGroup)
        else:
            if fkControl.getParent():
                pymel.parent(zeroGroup, fkControl.getParent())


        pymel.parent(fkControl, zeroGroup)

        relationshipDic[fkControl]['zeroGroup'] = zeroGroup


        ## CREATE SHADOW GROUP ---------------------------------------
        # create shadow group
        shdwGroup = pymel.createNode('transform')
        shdwGroup.rename(fkControl.nodeName()+'_shdw')

        # snap shdwGroup
        ka_transforms.snap(t=1, r=1, snapTarget=fkControl, snapObjects=shdwGroup)

        # parent shdwGroup
        pymel.parent(shdwGroup, zeroGroup)

        pymel.orientConstraint(fkControl, shdwGroup)

        pymel.parent(fkControl.getChildren(type='transform'), shdwGroup)

        relationshipDic[fkControl]['shdwGroup'] = zeroGroup



    ## CREATE GUIDE CURVE =======================================
    if createGuideCurve:
        lastI = len(guideTransforms)-1
        for i, guideTransform in enumerate(guideTransforms):

            # create orientationLocator -------------------------
            orientationLocatorShape = pymel.createNode('locator')
            orientationLocatorShape.localScaleX.set(0.5)
            orientationLocatorShape.localScaleY.set(0.5)
            orientationLocatorShape.localScaleZ.set(0.5)
            orientationLocator = orientationLocatorShape.getParent()
            orientationLocator.rename(guideTransform.nodeName()+'_orientationLocator')
            orientationLocator.v.set(0)

            ka_transforms.snap(t=1, r=1, snapTarget=guideTransform, snapObjects=orientationLocator)
            pymel.parent(orientationLocator, guideTransform)

            relationshipDic[guideTransform]['orientationLocator'] = orientationLocator


            # create orientationLocator worldSpace position vector product
            orientationLocator_worldSpaceVectorProduct = pymel.createNode('vectorProduct')
            orientationLocator_worldSpaceVectorProduct.rename(orientationLocator.nodeName()+'_worldSpaceVectorProduct')
            orientationLocator_worldSpaceVectorProduct.operation.set(4)
            orientationLocator.worldMatrix[0] >> orientationLocator_worldSpaceVectorProduct.matrix

            relationshipDic[guideTransform]['orientationLocator_worldSpaceVectorProduct'] = orientationLocator_worldSpaceVectorProduct

            # create orientationLocator_backHandle -------------------------
            if i != 0:
                orientationLocator_backHandleShape = pymel.createNode('locator')
                orientationLocator_backHandleShape.localScaleX.set(0.2)
                orientationLocator_backHandleShape.localScaleY.set(0.2)
                orientationLocator_backHandleShape.localScaleZ.set(0.2)
                orientationLocator_backHandle = orientationLocator_backHandleShape.getParent()
                orientationLocator_backHandle.rename(guideTransform.nodeName()+'orientationLocator_backHandle')
                orientationLocator_backHandle.v.set(0)

                ka_transforms.snap(t=1, r=1, snapTarget=guideTransform, snapObjects=orientationLocator_backHandle)

                pymel.parent(orientationLocator_backHandle, orientationLocator)

                relationshipDic[guideTransform]['orientationLocator_backHandle'] = orientationLocator_backHandle


            # create orientationLocator_frontHandle -------------------------
            if i != lastI:
                orientationLocator_frontHandleShape = pymel.createNode('locator')
                orientationLocator_frontHandleShape.localScaleX.set(0.2)
                orientationLocator_frontHandleShape.localScaleY.set(0.2)
                orientationLocator_frontHandleShape.localScaleZ.set(0.2)
                orientationLocator_frontHandle = orientationLocator_frontHandleShape.getParent()
                orientationLocator_frontHandle.rename(guideTransform.nodeName()+'orientationLocator_frontHandle')
                orientationLocator_frontHandle.v.set(0)

                ka_transforms.snap(t=1, r=1, snapTarget=guideTransform, snapObjects=orientationLocator_frontHandle)

                pymel.parent(orientationLocator_frontHandle, orientationLocator)

                relationshipDic[guideTransform]['orientationLocator_frontHandle'] = orientationLocator_frontHandle




        # CREATE TIGHTNESS ATTRIBUTE ON CONTROLLERS
        for fkControl in fkControls:
            fkControl.addAttr('addLength', minValue=0.0, defaultValue=0.0)
            fkControl.addAttr('positionBetween', minValue=-1.0, maxValue=1.0, defaultValue=0.0)
            fkControl.addAttr('curveTightness', minValue=0.0, maxValue=1.0, defaultValue=0.0)

            fkControl.addLength.set(keyable=True)
            fkControl.positionBetween.set(keyable=True)
            fkControl.curveTightness.set(keyable=True)

        guideCurveCvDrivers = []

        # orient the orientation locators with aim betweens
        for i, guideTransform in enumerate(guideTransforms):
            orientationLocator = relationshipDic[guideTransform]['orientationLocator']

            if i == 0:
                nextFkControl = guideTransforms[i+1]
                previousFkControl = None

                orientationLocator_frontHandle = relationshipDic[guideTransform]['orientationLocator_frontHandle']
                orientationLocator_backHandle = None

                nextOrientationLocator = relationshipDic[nextFkControl]['orientationLocator']
                previousOrientationLocator = None

                guideCurveCvDrivers.extend([orientationLocator, orientationLocator_frontHandle])

            elif i == lastI:
                nextFkControl = None
                previousFkControl = guideTransforms[i-1]

                orientationLocator_frontHandle = None
                orientationLocator_backHandle = relationshipDic[guideTransform]['orientationLocator_backHandle']

                nextOrientationLocator = None
                previousOrientationLocator = relationshipDic[previousFkControl]['orientationLocator']

                guideCurveCvDrivers.extend([orientationLocator_backHandle, orientationLocator])

            else:
                nextFkControl = guideTransforms[i+1]
                previousFkControl = guideTransforms[i-1]

                orientationLocator_frontHandle = relationshipDic[guideTransform]['orientationLocator_frontHandle']
                orientationLocator_backHandle = relationshipDic[guideTransform]['orientationLocator_backHandle']

                nextOrientationLocator = relationshipDic[nextFkControl]['orientationLocator']
                previousOrientationLocator = relationshipDic[previousFkControl]['orientationLocator']

                guideCurveCvDrivers.extend([orientationLocator_backHandle, orientationLocator, orientationLocator_frontHandle])

            # create aim between constraints
            if i != 0 and i != lastI:
                ka_constraints.constrain([nextFkControl, previousFkControl, orientationLocator], aimBetween=True)


            # Set Driven Key
            drivenKeyX = pymel.createNode('animCurveUU', )
            drivenKeyYZ = pymel.createNode('animCurveUU', )

            pymel.setKeyframe(drivenKeyX, value=0.333, float=0.0)
            pymel.setKeyframe(drivenKeyX, value=0.0, float=1.0)
            drivenKeyX.tangentType.set(18,)
            drivenKeyX.weightedTangents.set(False,)

            pymel.setKeyframe(drivenKeyYZ, value=0.0, float=0.0)
            pymel.setKeyframe(drivenKeyYZ, value=0.0, float=1.0)
            drivenKeyYZ.tangentType.set(18,)
            drivenKeyYZ.weightedTangents.set(False,)

            if i == lastI:
                guideTransforms[-2].curveTightness >> drivenKeyX.input
                guideTransforms[-2].curveTightness >> drivenKeyYZ.input
            else:
                guideTransform.curveTightness >> drivenKeyX.input
                guideTransform.curveTightness >> drivenKeyYZ.input


            # drive orientationLocator_Handles by local distance (in 1 axis)
            if nextOrientationLocator:
                nextOrientationLocator_worldSpaceVectorProduct = relationshipDic[nextFkControl]['orientationLocator_worldSpaceVectorProduct']
                localSpace_vectorProduct = pymel.createNode('vectorProduct')
                localSpace_vectorProduct.operation.set(4)

                nextOrientationLocator_worldSpaceVectorProduct.output >> localSpace_vectorProduct.input1
                orientationLocator.worldInverseMatrix[0] >> localSpace_vectorProduct.matrix

                multiplyDivide = pymel.createNode('multiplyDivide')
                localSpace_vectorProduct.output >> multiplyDivide.input1

                drivenKeyX.output >> multiplyDivide.input2X
                drivenKeyYZ.output >> multiplyDivide.input2Y
                drivenKeyYZ.output >> multiplyDivide.input2Z

                multiplyDivide.output >> orientationLocator_frontHandle.t


            if previousOrientationLocator:
                previousOrientationLocator_worldSpaceVectorProduct = relationshipDic[previousFkControl]['orientationLocator_worldSpaceVectorProduct']
                localSpace_vectorProduct = pymel.createNode('vectorProduct')
                localSpace_vectorProduct.operation.set(4)

                previousOrientationLocator_worldSpaceVectorProduct.output >> localSpace_vectorProduct.input1
                orientationLocator.worldInverseMatrix[0] >> localSpace_vectorProduct.matrix

                multiplyDivide = pymel.createNode('multiplyDivide')
                localSpace_vectorProduct.output >> multiplyDivide.input1

                drivenKeyX.output >> multiplyDivide.input2X
                drivenKeyYZ.output >> multiplyDivide.input2Y
                drivenKeyYZ.output >> multiplyDivide.input2Z

                multiplyDivide.output >> orientationLocator_backHandle.t


        # CREATE THE ACTUAL GUIDE CURVE
        numberOfPoints = ((len(fkControls)-1) * 3) + 4

        curvePointList = []
        for driverTransform in guideCurveCvDrivers:
            position = pymel.xform(driverTransform, query=True, translation=True, worldSpace=True)
            curvePointList.append(tuple(position))

        #guideCurve = pymel.curve(degree=3, p=curvePointList)
        guideCurve = pymel.curve(degree=7, p=curvePointList)
        guideCurve.rename(baseName+'_ikCurve')
        guideCurveShape = guideCurve.getShape()
        guideCurve.inheritsTransform.set(0)

        pymel.parent(guideCurve, rigGroup)

        for i, driverTransform in enumerate(guideCurveCvDrivers):
            pymel.cluster(guideCurveShape.cv[i], wn=(driverTransform, driverTransform), bindState=True )

    if ikSpline:
        curveInfoNode = pymel.createNode('curveInfo')
        guideCurve.worldSpace[0] >> curveInfoNode.inputCurve
        curveLength = curveInfoNode.arcLength.get()

        if not ikSplineJoints:
            curveLengthSegment = curveLength / (ikSpline_numOfJoints-1)

            for i in range(ikSpline_numOfJoints):
                joint = pymel.createNode('joint')
                joint.rename(baseName+str(i)+'_ikSpline_jnt')

                if ikSplineJoints:
                    joint.tx.set(i*curveLengthSegment)
                    pymel.parent(joint, ikSplineJoints[-1])

                ikSplineJoints.append(joint)

        pymel.parent(ikSplineJoints[0], rigGroup)

        ikHandel, ikEffector = pymel.ikHandle( startJoint=ikSplineJoints[0], endEffector=ikSplineJoints[-2], solver='ikSplineSolver',
                                   curve=guideCurve, createCurve=False)

        ikHandel.dTwistControlEnable.set(1)
        ikHandel.dWorldUpType.set(4)
        ikHandel.dWorldUpAxis.set(3)
        ikHandel.dTwistValueType.set(1)
        ikHandel.v.set(0)

        pymel.parent(ikHandel, fkControls[0])

        # make a group to dictate the roll start of the ik spline
        twistGroupStart = pymel.createNode('transform')
        twistGroupStart.rename(baseName+'_twistStart')
        ka_transforms.snap(twistGroupStart, fkControls[0], t=1, r=1)
        pymel.parent(twistGroupStart, fkControls[0])
        twistGroupStart.rx.set(90)

        # make a group to dictate the roll end of the ik spline
        twistGroupEnd = pymel.createNode('transform')
        twistGroupEnd.rename(baseName+'_twistEnd')
        ka_transforms.snap(twistGroupEnd, fkControls[-1], t=1, r=1)
        pymel.parent(twistGroupEnd, fkControls[-1])
        twistGroupEnd.rx.set(90)

        twistGroupStart.worldMatrix[0] >> ikHandel.dWorldUpMatrix
        twistGroupEnd.worldMatrix[0] >> ikHandel.dWorldUpMatrixEnd

        curveLengthSegment = curveLength / (len(ikSplineJoints)-1)

        segmentMultiplyDivide = pymel.createNode('multiplyDivide')
        curveInfoNode.arcLength >> segmentMultiplyDivide.input1X
        segmentMultiplyDivide.input2X.set(1.0 / (len(ikSplineJoints)-1))

        for i, joint in enumerate(ikSplineJoints):
            if i != 0:
                jointLengthMultiplyDivide = pymel.createNode('multiplyDivide')
                segmentMultiplyDivide.outputX >> jointLengthMultiplyDivide.input1X
                jointLengthMultiplyDivide.input2X.set(curveLengthSegment / joint.tx.get())
                jointLengthMultiplyDivide.outputX >> joint.tx

                if i == len(ikSplineJoints)-1:
                    jointLengthMultiplyDivide.input2X.set(jointLengthMultiplyDivide.input2X.get()*0.75)

        pymel.aimConstraint(endTransform, ikSplineJoints[-2], worldUpType='objectrotation', worldUpObject=endTransform)
        pymel.pointConstraint(endTransform, ikSplineJoints[-1])
        #cmds.aimConstraint( 'cone1', 'surf2', 'cube2', w=.1 )


    return rigGroup