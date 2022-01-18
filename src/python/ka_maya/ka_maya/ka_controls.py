#====================================================================================
#====================================================================================
#
# ka_controls
#
# DESCRIPTION:
#   A module for creating and manipulating animaiton controls
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
import string

import pymel.core as pymel
import maya.cmds as cmds
import maya.mel as mel

import ka_maya.ka_pymel as ka_pymel
import ka_maya.ka_shapes as ka_shapes
import ka_maya.ka_naming as ka_naming
import ka_maya.ka_transforms as ka_transforms
import ka_maya.ka_attr as ka_attr
import ka_maya.ka_math as ka_math

SPACE_LABEL = 'Space'

def createControl(baseName='', shape='peg', index='', side='', size=[1,1,1], lengthAxis='y',
                       length=None, rotateOffset=[], pointAt='y', grouping=''):

    controlShape = ka_shapes.createNurbsCurve(shape=shape, scale=size, pointAt=pointAt)
    control = pymel.createNode('joint')
    ka_shapes.shapeParent(controlShape, control)
    #control.drawStyle.set(2)
    control.radius.set(0)
    control.radius.set(channelBox=False)
    #ka_naming.setName(control, baseName=baseName, index=index, side=side, nodePurpose='control',)
    control.addAttr('isControl', at='bool', defaultValue=True)
    control.isControl.set(lock=True)

    return control

def createControlStack(sizeOfStack=2, shape='peg', size=[1,1,1], lengthAxis='y',
                       length=None, rotateOffset=[], pointAt='y'):
    """returns a list of transforms, with the last being the main control, and the
    first being it's zero out group"""

    if not isinstance(size, list):
        size = [size, size, size]

    controllerStack = []

    if sizeOfStack > 1:
        zroGroup = pymel.createNode('transform')
        controllerStack.append(zroGroup)

    if sizeOfStack > 2:
        for i in range(sizeOfStack-2):
            offsetGroup = pymel.createNode('transform')
            controllerStack.append(offsetGroup)


    control = createControl(shape=shape, size=size, lengthAxis=lengthAxis,
                            length=length, rotateOffset=rotateOffset, pointAt=pointAt,)

    controllerStack.append(control)


    for i, node in enumerate(controllerStack):
        if i != 0:
            node.setParent(controllerStack[i-1])

    return controllerStack


def resizeControlShape(control, size, length=None, nextControl=None, lengthAxis='x'):

    control = ka_pymel.getAsPyNodes(control)

    if 'transform' in pymel.nodeType(control, inherits=True):
        controlShapes = control.getShapes()
        control = control

    else:
        controlShapes = control
        control = control.getParent()

    laticeDeformer, lattice, latticeBase = pymel.lattice(controlShapes)
    latticeShape = lattice.getShape()
    latticeBase.uDivisions.set(2)
    latticeBase.sDivisions.set(2)
    latticeBase.tDivisions.set(2)

    laticeDeformer.outsideLattice.set(1)


def addSpace(controlStack, spaceParent=None, worldSpaceObject=None, label=None, t=1, r=1):
    spaceXform = None
    indexOfSpaceXform = None
    for i, xForm in enumerate(controlStack):
        if hasattr(xForm, 'isSpaceXform'):
            spaceXform = xForm
            indexOfSpaceXform = i
            break

    if not spaceXform:
        indexOfSpaceXform, controlStack = _createSpaceXform(controlStack, t=t, r=r, worldSpaceObject=worldSpaceObject)
        spaceXform = controlStack[indexOfSpaceXform]

    spaceSwitchXform = controlStack[-1] # the node with the switch attributes

    if spaceParent:
        if t == 1:
            ka_attr.addEnumValue(spaceSwitchXform.attr('t%sA' % SPACE_LABEL), label)
            ka_attr.addEnumValue(spaceSwitchXform.attr('t%sB' % SPACE_LABEL), label)

        if r == 1:

            ka_attr.addEnumValue(spaceSwitchXform.attr('r%sA' % SPACE_LABEL), label)

            ka_attr.addEnumValue(spaceSwitchXform.attr('r%sB' % SPACE_LABEL), label)

        nextIndex = int(pymel.attributeQuery('t%sA' % SPACE_LABEL, node=spaceSwitchXform, maximum=True)[0])

        _createSpaceBlenderForInput(nextIndex, spaceParent, spaceXform, controlStack, worldSpaceObject=worldSpaceObject)


def _createSpaceXform(controlStack, worldSpaceObject=None, t=1, r=1):
    spaceXform = pymel.createNode('transform')
    spaceXform.rename(controlStack[-1].nodeName()+'_spaceXForm')
    spaceXform.addAttr('isSpaceXform', at='message')

    ka_transforms.snap(spaceXform, controlStack[0], t=1, r=1, s=1)

    spaceXform.setParent(controlStack[0])
    controlStack[1].setParent(spaceXform)
    indexOfSpaceXform = 1
    controlStack.insert(1, spaceXform)

    ka_transforms.snap(spaceXform, controlStack[0], t=1, r=1, s=1)


    # orientConstraint
    if r == 1:
        orientConstraint = pymel.createNode('orientConstraint')
        orientConstraint.rename(spaceXform.nodeName()+'_spaceSwitch_orientConstraint')
        orientConstraint.setParent(spaceXform)

        spaceXform.parentInverseMatrix[0] >> orientConstraint.constraintParentInverseMatrix
        spaceXform.rotateOrder >> orientConstraint.constraintRotateOrder

        orientConstraint.constraintRotateX >> spaceXform.rx
        orientConstraint.constraintRotateY >> spaceXform.ry
        orientConstraint.constraintRotateZ >> spaceXform.rz


    # pointConstraint
    if t == 1:
        pointConstraint = pymel.createNode('pointConstraint')
        pointConstraint.rename(spaceXform.nodeName()+'_spaceSwitch_pointConstraint')
        pointConstraint.setParent(spaceXform)
        spaceXform.parentInverseMatrix[0] >> pointConstraint.constraintParentInverseMatrix

        pointConstraint.constraintTranslateX >> spaceXform.tx
        pointConstraint.constraintTranslateY >> spaceXform.ty
        pointConstraint.constraintTranslateZ >> spaceXform.tz



    # space attr
    enumString = 'local:world'
    ka_attr.addHeaderAttr(controlStack[-1], '%s_SWITCHS' % SPACE_LABEL.upper())
    if t == 1:
        controlStack[-1].addAttr('t%sA' % SPACE_LABEL, at='enum', enumName=enumString, keyable=True)
        controlStack[-1].addAttr('t%sB' % SPACE_LABEL, at='enum', enumName=enumString, defaultValue=1, keyable=True)
        controlStack[-1].addAttr('t%sBlend' % SPACE_LABEL, maxValue=1.0, minValue=0.0, keyable=True)
        ka_attr.addSeparatorAttr(controlStack[-1])

    if r == 1:
        controlStack[-1].addAttr('r%sA' % SPACE_LABEL, at='enum', enumName=enumString, keyable=True)
        controlStack[-1].addAttr('r%sB' % SPACE_LABEL, at='enum', enumName=enumString, defaultValue=1, keyable=True)
        controlStack[-1].addAttr('r%sBlend' % SPACE_LABEL, maxValue=1.0, minValue=0.0, keyable=True)
        ka_attr.addSeparatorAttr(controlStack[-1])

    spaceBlenderT, spaceBlenderR = _createSpaceBlenderForInput(0, 'local', spaceXform, controlStack)
    spaceBlenderT, spaceBlenderR = _createSpaceBlenderForInput(1, 'world', spaceXform, controlStack, worldSpaceObject=worldSpaceObject)

    return indexOfSpaceXform, controlStack

def _getSpaceBlenderForInput(spaceXform, inputIndex):
    attrName = 'spaceBlender_'+str(inputIndex)
    if hasattr(spaceXform, attrName):
        return spaceXform.attr(attrName).inputs()[0]

    else:
        return _createSpaceBlenderForInput(inputIndex)

def _createSpaceBlenderForInput(inputIndex, targetXform, spaceXform, controlStack, t=1, r=1,
                                worldSpaceObject=None):
    spaceBlenderT = None
    spaceBlenderR = None

    if hasattr(controlStack[-1], 't%sBlend' % SPACE_LABEL):
        t = 1
    else:
        t = 0

    if hasattr(controlStack[-1], 'r%sBlend' % SPACE_LABEL):
        r = 1
    else:
        r = 0


    if t:
        spaceBlenderT = pymel.createNode('blendColors')
        attrName = 'spaceBlenderT_'+str(inputIndex)
        spaceXform.addAttr(attrName, at='message')
        spaceBlenderT.message >> spaceXform.attr(attrName)

        spaceACondition = pymel.createNode('condition')
        spaceACondition.secondTerm.set(inputIndex)
        spaceACondition.colorIfTrueR.set(1.0)
        spaceACondition.colorIfFalseR.set(0.0)
        controlStack[-1].attr('t%sA' % SPACE_LABEL) >> spaceACondition.firstTerm

        spaceBCondition = pymel.createNode('condition')
        spaceBCondition.secondTerm.set(inputIndex)
        spaceBCondition.colorIfTrueR.set(1.0)
        spaceBCondition.colorIfFalseR.set(0.0)
        controlStack[-1].attr('t%sB' % SPACE_LABEL) >> spaceBCondition.firstTerm

        spaceACondition.outColorR >> spaceBlenderT.color2R
        spaceBCondition.outColorR >> spaceBlenderT.color1R
        controlStack[-1].attr('t%sBlend' % SPACE_LABEL) >> spaceBlenderT.blender

        pointConstraint = None
        pointConstraints = spaceXform.tx.inputs(type='pointConstraint')
        if pointConstraints:
            pointConstraint = pointConstraints[0]

    if r:
        spaceBlenderR = pymel.createNode('blendColors')
        attrName = 'spaceBlenderR_'+str(inputIndex)
        spaceXform.addAttr(attrName, at='message')
        spaceBlenderR.message >> spaceXform.attr(attrName)

        spaceACondition = pymel.createNode('condition')
        spaceACondition.secondTerm.set(inputIndex)
        spaceACondition.colorIfTrueR.set(1.0)
        spaceACondition.colorIfFalseR.set(0.0)
        controlStack[-1].attr('r%sA' % SPACE_LABEL) >> spaceACondition.firstTerm

        spaceBCondition = pymel.createNode('condition')
        spaceBCondition.secondTerm.set(inputIndex)
        spaceBCondition.colorIfTrueR.set(1.0)
        spaceBCondition.colorIfFalseR.set(0.0)
        controlStack[-1].attr('r%sB' % SPACE_LABEL) >> spaceBCondition.firstTerm

        spaceACondition.outColorR >> spaceBlenderR.color2R
        spaceBCondition.outColorR >> spaceBlenderR.color1R
        controlStack[-1].attr('r%sBlend' % SPACE_LABEL) >> spaceBlenderR.blender

        orientConstraint = None
        orientConstraints = spaceXform.rx.inputs(type='orientConstraint')
        if orientConstraints:
            orientConstraint = orientConstraints[0]


    worldSpacePosition = pymel.xform(controlStack[0], query=True, translation=True, worldSpace=True)
    worldSpaceRotation = pymel.xform(controlStack[0], query=True, rotation=True, worldSpace=True)

    # local space
    if targetXform == 'local':
        if t:
            controlStack[0].worldMatrix[0] >> pointConstraint.target[inputIndex].targetParentMatrix

        if r:
            controlStack[0].worldMatrix[0] >> orientConstraint.target[inputIndex].targetParentMatrix


    # world space
    elif targetXform == 'world':
        parentMatrix = ka_transforms.getListFromMMatrix(spaceXform.parentMatrix[0].get())
        if t:
            pointConstraint.target[inputIndex].targetTranslate.set(worldSpacePosition)

            if worldSpaceObject:
                worldSpaceObject.worldMatrix[0] >> pointConstraint.target[inputIndex].targetParentMatrix

        if r:
            orientConstraint.target[inputIndex].targetRotate.set(worldSpaceRotation)
            if worldSpaceObject:
                worldSpaceObject.worldMatrix[0] >> orientConstraint.target[inputIndex].targetParentMatrix
            else:
                orientConstraint.target[inputIndex].targetParentMatrix.set(controlStack[0].parentMatrix.get())

    # target object space
    else:
        if t:
            worldSpacePoint = pymel.xform(spaceXform, query=True, worldSpace=True, translation=True)
            translate = ka_transforms.getInForienSpace_point(worldSpacePoint, targetXform)

            pointConstraint.target[inputIndex].targetTranslate.set(translate)
            targetXform.worldMatrix[0] >> pointConstraint.target[inputIndex].targetParentMatrix

        if r:
            rotate = ka_transforms.getInForienSpace_eularRotation(spaceXform, targetXform)

            orientConstraint.target[inputIndex].targetRotate.set(rotate)

            targetXform.worldMatrix[0] >> orientConstraint.target[inputIndex].targetParentMatrix

    if t:
        if spaceBlenderT:
            spaceBlenderT.outputR >> pointConstraint.target[inputIndex].targetWeight

    if r:
        if spaceBlenderR:
            spaceBlenderR.outputR >> orientConstraint.target[inputIndex].targetWeight


    return spaceBlenderT, spaceBlenderR


#def addSubControls(control, numberOfSubControls=1):
    #subControlSizeDiffrence = 0.8
    #subControls = []

    #KEYABLE_TRANSFORM_ATTRS = ('tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz',)
    #TRANSFORM_ATTRS = ('matrix', 'inverseMatrix', ' 'worldSpaceMatrix', 'worldInverseMatrix', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz',)


    #control_keyableAttrs = control.listAttr(keyable=True)

    #for i in range(numberOfSubControls):
        #controlDuplicate = pymel.duplicate(control)[0]
        #for attr in ('s', 'sx', 'sy', 'sz'):
            #controlDuplicate.attr(attr).set(lock=False)

        #for attr in ('sx', 'sy', 'sz'):
            #controlDuplicate.attr(attr).set(controlDuplicate.attr(attr).get()*subControlSizeDiffrence)

        #controlDuplicate.sx.set()
        #controlDuplicate.sy.set(controlDuplicate.sy.get()*subControlSizeDiffrence)
        #controlDuplicate.sz.set(controlDuplicate.sz.get()*subControlSizeDiffrence)

        #pymel.makeIdentity(controlDuplicate, apply=True, s=1)

        #subControl = createControl('subControl')
        #pymel.delete(subControl.getShape())
        #subControl.rename(control.nodeName(stripNamespace=True)+'subCtl%s' % string.ascii_uppercase[i])
        #ka_transforms.snap(subControl, control, t=1, r=1, s=1)

        #ka_shapes.shapeParent(controlDuplicate, subControl)

        #subControls.append(subControl)


    #parent = control
    #for subControl in subControls:
        #subControl.setParent(parent)
        #parent = subControl

        #subControl_keyableAttrs = subControl.listAttr(keyable=True)
        #for attr in subControl_keyableAttrs:

            #if control.attr(attr).get(lock=True):
                #subControl.attr(attr).set(lock=True)

            #if control.attr(attr).get(keyable=True):
                #subControl.attr(attr).set(keyable=True)

            #if
                #a.s.get(keyable=True)

            #if control.attr(attr).get(lock):
                #subControl.attr(attr).set(lock=True)


            #if attr not in control_keyableAttrs:
                #attr.set(keyable=False)

#def getUpVectorPosition_from3Points(pointA, pointB, pointC):
    #"""returns the ideal position for an upVector based on the 3 given points.
    #If those points are transforms, tha
    #pass

