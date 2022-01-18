#====================================================================================
#====================================================================================
#
# utils_transform
#
# DESCRIPTION:
#   tools for working with transforms
#
# DEPENDENCEYS:
#   None
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

import math

import pymel.core as pymel
import maya.OpenMaya as OpenMaya

import ka_maya.ka_pymel as ka_pymel
import ka_maya.ka_python as ka_python
import ka_maya.ka_preference as ka_preference
import ka_maya.ka_math as ka_math


def distanceBetween(pointA, pointB):
    points = []
    for point in [pointA, pointB]:
        if isinstance(pointA, basestring): # then it represents a maya node
            points.append(pymel.xform(point, query=True, translation=True, worldSpace=True))

        elif isinstance(point, list): # is alread a list of floats
            points.append(point)

        else: # pymel transform
            points.append(pymel.xform(point, query=True, translation=True, worldSpace=True))

    return ka_math.distanceBetween(points[0], points[1])

#----------------------------------------------------------------------
def getAsPyNode(inputObject):
    """if inputObject is a string, convert it to a pynode"""

    if isinstance(inputObject, list):
        if inputObject:
            if isinstance(inputObject[0], basestring):
                return pymel.ls(inputObject)

    elif isinstance(inputObject, basestring):
        inputObject = pymel.ls(inputObject)
        if inputObject:
            return inputObject[0]

    return inputObject

#----------------------------------------------------------------------
def getAsPoint(arg):
    """returns arg as a point (list of floats)"""

    # list of numbers
    if isinstance(arg, list):

        if arg:
            if isinstance(arg[0], float) or isinstance(arg[0], int):
                if len(arg) == 3:
                    return arg

                elif len(arg) == 16:
                    return arg[12:15]

    # transform
    elif ka_pymel.isPyTransform(arg):
        point = pymel.xform(arg, query=True, translation=True, worldSpace=True)
        return point

    elif isinstance(arg, basestring): # transform
        transforms = ka_pymel.getAsPyNodes(arg)

        if transforms:
            if len(transforms) > 1:
                pymel.error('more than 1 transform matched arg: %s of type: %s' % (str(arg), str(type(arg))))

            else:
                point = pymel.xform(transforms, query=True, translation=True, worldSpace=True)
                return point
        else:
            pymel.error('no transform matched arg: %s of type: %s' % (str(arg), str(type(arg))))

    pymel.error('unable to get a POINT from the input arg: %s of type: %s' % (str(arg), str(type(arg))))

#----------------------------------------------------------------------
def getAsMatrix(arg):
    """returns arg as a point (list of floats)"""

    # list of numbers
    if isinstance(arg, list):
        if arg:
            if isinstance(arg[0], float) or isinstance(arg[0], int):
                if len(arg) == 3:
                    return [1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, arg[0], arg[1], arg[2], 1.0]

                elif len(arg) == 16:
                    return arg

    # transform
    elif ka_pymel.isPyTransform(arg):
        point = pymel.xform(arg, query=True, matrix=True, worldSpace=True)
        return point

    elif isinstance(arg, basestring): # transform
        transforms = ka_pymel.getAsPyNodes(arg)
        if transforms:
            if len(transforms) > 1:
                pymel.error('more than 1 transform matched arg: %s of type: %s' % (str(arg), str(type(arg))))
            else:
                point = pymel.xform(transforms, query=True, matrix=True, worldSpace=True)
                return point
        else:
            pymel.error('no transform matched arg: %s of type: %s' % (str(arg), str(type(arg))))

    pymel.error('unable to get a MATRIX from the input arg: %s of type: %s' % (str(arg), str(type(arg))))

#----------------------------------------------------------------------
def getVectorFromMatrix(matrix, axis='x'):
    """
    returns the vector of the given axis

    Args:
        axis: string value of x, y, z, -x, -y or -z.

    Returns:
        a vector representing that axis direction
    """
    matrix = getAsMatrix(matrix)

    if axis == 'x':
        return matrix[0:3]
    elif axis == 'y':
        return matrix[4:7]
    elif axis == 'z':
        return matrix[8:11]

    elif axis == '-x':
        return [matrix[0]*-1, matrix[1]*-1, matrix[2]*-1, ]
    elif axis == '-y':
        return [matrix[4]*-1, matrix[5]*-1, matrix[6]*-1, ]
    elif axis == '-z':
        return [matrix[8]*-1, matrix[9]*-1, matrix[10]*-1, ]




#----------------------------------------------------------------------
def getListFromMMatrix(MMatrix):
    """"""
    matrixList = []
    for row in MMatrix:
        matrixList.extend(row)

    return matrixList

#----------------------------------------------------------------------
def getMMatrixFromList(matrixList):
    """"""
    MMatrix = OpenMaya.MMatrix()
    OpenMaya.MScriptUtil.createMatrixFromList( matrixList, MMatrix)

    return MMatrix

#----------------------------------------------------------------------
def getMMatrixFromAttr(attribute):
    """"""
    matrixValues = attribute.get()
    matrixList = []
    for row in matrixValues:
        matrixList.extend(row)

    matrixObj = getMMatrixFromList(matrixList)
    return matrixObj

#----------------------------------------------------------------------
def setMatrix(transfrom, matrix, worldSpace=False):
    """"""
    matrixList = getListFromMMatrix(matrix)
    pymel.xform(transfrom, worldSpace=worldSpace, matrix=matrixList)

#----------------------------------------------------------------------
#def mirrorMatrix(matrix, behavior=True):
    #""""""
    #if behavior:
        #matrixList = getListFromMMatrix(matrix)
        #for i in [4,5,6, 8,9,10,]:
            #matrixList[i] = matrixList[i]*-1
        #matrix = getMMatrixFromList(matrixList)

    #mirrorOp = getMMatrixFromList( [ -1.0, 0.0, 0.0, 0.0,
                                      #0.0, 1.0, 0.0, 0.0,
                                      #0.0, 0.0, 1.0, 0.0,
                                      #0.0, 0.0, 0.0, 1.0] )

    #if behavior:
        #mirrorBehaveOp = OpenMaya.MMatrix()
        #OpenMaya.MScriptUtil.createMatrixFromList( [ 1.0, 0.0, 0.0, 0.0,
                                                     #0.0, 1.0, 0.0, 0.0,
                                                     #0.0, 0.0, 1.0, 0.0,
                                                     #0.0, 0.0, 0.0, 1.0], mirrorOp)

    ##mirroredMatrix = OpenMaya.MMatrix()
    #mirroredMatrix = mirrorOp * matrix * mirrorOp

    #return mirroredMatrix

def mirrorMatrix(matrix, behavior=False):
    """Mirrors an MMatrix"""
    if behavior:
        matrixList = getListFromMMatrix(matrix)
        for i in [4,5,6, 8,9,10,]:
            matrixList[i] = matrixList[i]*-1
        matrix = getMMatrixFromList(matrixList)

    mirrorOp = getMMatrixFromList( [ -1.0, 0.0, 0.0, 0.0,
                                      0.0, 1.0, 0.0, 0.0,
                                      0.0, 0.0, 1.0, 0.0,
                                      0.0, 0.0, 0.0, 1.0] )


    mirroredMatrix = mirrorOp * matrix * mirrorOp

    return mirroredMatrix

#----------------------------------------------------------------------
def mirrorMatrixList(matrixList, behavior=False):
    """"""
    matrix = getMMatrixFromList(matrixList)
    mirroredMatrix = mirrorMatrix(matrix, behavior=behavior)
    mirroredMatrixList = getListFromMMatrix(mirroredMatrix)

    return mirroredMatrixList

#----------------------------------------------------------------------
def mirrorTransform(transform, targetTransform=None, behavior=True):
    """mirrors given transform by itself, or optionally to a target"""

    targetTransform
    if not targetTransform:
        targetTransform = transform

    worldMatrix = getMMatrixFromAttr(targetTransform.worldMatrix[0])
    mirroredMatrix = mirrorMatrix(worldMatrix, behavior=behavior)
    setMatrix(transform, mirroredMatrix, worldSpace=True)

    # if joint, subtract the joint orient from the result
    if transform.nodeType() == 'joint':
        for axis in ['X', 'Y', 'Z', ]:
            jointOrient = transform.attr('jointOrient%s' % axis).get()
            transform.attr('rotate%s' % axis).set(transform.attr('rotate%s' % axis).get()-jointOrient)

def snapToMirroredPositionOfTransform(transformTarget, transform, behavior=True):
    """"""
    worldMatrix = getMMatrixFromAttr(transformTarget.worldMatrix[0])
    mirroredMatrix = mirrorMatrix(worldMatrix, behavior=behavior)
    setMatrix(transform, mirroredMatrix, worldSpace=True)


def getInWorldSpace_point(point, space):
    """Returns a point [x,y,z] that represents what the input point in the given space
    would be in world space

    args:
        point - list of floats [x,y,z] - a point in space
        space - matrix (list of 16 floats) - represents the space we are moving the point into or..
              - pyMel node or string - a transform node representing the space we are moving the point into
    """

    # parse point arg
    if isinstance(point, list):
        mPoint = OpenMaya.MPoint(*point)
    else:
        point = pymel.xform(point, query=True, translation=True, worldSpace=True)
        mPoint = OpenMaya.MPoint(*point)

    # parse space arg
    if isinstance(space, list):
        targetMMatrix = getMMatrixFromList(space)
    else:
        targetMMatrix = getMMatrixFromAttr(space.worldMatrix[0])

    # do math
    result = mPoint * targetMMatrix
    return [result[0], result[1], result[2], ]

def getInForienSpace_point(point, space):
    """Returns a point [x,y,z] that represents what the input point would be
    if it where in the given space

    args:
        point - list of floats [x,y,z] - a point in space
              - MPoint
        space - matrix (list of 16 floats) - represents the space we are moving the point into or..
              - pyMel node or string - a transform node representing the space we are moving the point into
    """

    # parse point arg
    if isinstance(point, list) or isinstance(point, tuple):
        mPoint = OpenMaya.MPoint(*point)
    elif isinstance(point, OpenMaya.MPoint):
        mPoint = point
    else:
        point = pymel.xform(point, query=True, translation=True, worldSpace=True)
        mPoint = OpenMaya.MPoint(*point)

    # parse space arg
    if isinstance(space, list) or isinstance(space, tuple):
        targetMMatrix = getMMatrixFromList(space)
        targetMMatrix = targetMMatrix.inverse()
    else:
        targetMMatrix = getMMatrixFromAttr(space.worldInverseMatrix[0])

    # do math
    result = mPoint * targetMMatrix
    return [result[0], result[1], result[2], ]


def getInWorldSpace_matrix(matrix, space):
    """Returns a point [x,y,z] that represents what the input point in the given space
    would be in world space

    args:
        point - list of floats [x,y,z] - a point in space
        space - matrix (list of 16 floats) - represents the space we are moving the point into or..
              - pyMel node or string - a transform node representing the space we are moving the point into
    """

    # parse point arg
    if isinstance(matrix, list):
        mMatrix = getMMatrixFromList(matrix)
    else:
        matrix = pymel.xform(matrix, query=True, matrix=True, worldSpace=True)
        mMatrix = getMMatrixFromList(matrix)

    # parse space arg
    if isinstance(space, list):
        targetMMatrix = getMMatrixFromList(space)
    else:
        targetMMatrix = getMMatrixFromAttr(space.worldMatrix[0])

    # parse space arg
    if isinstance(space, list):
        targetMMatrix = getMMatrixFromList(space)
    else:
        targetMMatrix = getMMatrixFromAttr(space.worldMatrix[0])

    # do math
    result = getListFromMMatrix(mMatrix * targetMMatrix)
    return result

def getInForienSpace_matrix(matrix, space):
    """Returns a point [x,y,z] that represents what the input point would be
    if it where in the given space

    args:
        point - list of floats [x,y,z] - a point in space
        space - matrix (list of 16 floats) - represents the space we are moving the point into or..
              - pyMel node or string - a transform node representing the space we are moving the point into
    """

    # parse point arg
    if isinstance(matrix, list):
        mMatrix = getMMatrixFromList(matrix)
    else:
        matrix = pymel.xform(matrix, query=True, matrix=True, worldSpace=True)
        mMatrix = getMMatrixFromList(matrix)

    # parse space arg
    if isinstance(space, list):
        targetMMatrix = getMMatrixFromList(space)
        targetMMatrix = targetMMatrix.inverse()
    else:
        targetMMatrix = getMMatrixFromAttr(space.worldInverseMatrix[0])

    # do math
    result = getListFromMMatrix(mMatrix * targetMMatrix)
    return result

def getInWorldSpace_eularRotation(transform, space):
    """Returns a Eular Rotation [xAngle, yAngle, zAngle] that represents what the input transform would be
    if it where in the given space

    args:
        transform - list of floats - a transform matrix or...
                  - pyMel node or string - a transform node
        space - matrix (list of 16 floats) - represents the space we are moving the rotate into or..
              - pyMel node or string - a transform node representing the space we are moving the rotate into

    """

    # parse transform arg
    if isinstance(transform, list):
        targetMMatrix = getMMatrixFromList(transform)
    else:
        m1 = getMMatrixFromAttr(transform.worldMatrix[0])

    # parse space arg
    if isinstance(space, list):
        m2 = getMMatrixFromList(space)
    else:
        m2 = getMMatrixFromAttr(space.worldInverseMatrix[0])

    # do math
    r = m1 * m2
    tm = OpenMaya.MTransformationMatrix(r)
    r = tm.eulerRotation()

    return math.degrees(r[0]), math.degrees(r[1]), math.degrees(r[2])

def getInForienSpace_eularRotation(transform, space):
    """Returns a Eular Rotation [xAngle, yAngle, zAngle] that represents what the input transform would be
    if it where in the given space

    args:
        transform - list of floats - a transform matrix or...
                  - pyMel node or string - a transform node
        space - matrix (list of 16 floats) - represents the space we are moving the rotate into or..
              - pyMel node or string - a transform node representing the space we are moving the rotate into

    """

    # parse transform arg
    if isinstance(transform, list):
        targetMMatrix = getMMatrixFromList(transform)
    else:
        m1 = getMMatrixFromAttr(transform.worldMatrix[0])

    # parse space arg
    if isinstance(space, list):
        m2 = getMMatrixFromList(space)
        m2 = m2.inverse()
    else:
        m2 = getMMatrixFromAttr(space.worldInverseMatrix[0])

    # do math
    r = m1 * m2
    tm = OpenMaya.MTransformationMatrix(r)
    r = tm.eulerRotation()

    return math.degrees(r[0]), math.degrees(r[1]), math.degrees(r[2])


def removeNonStandardTransformValues(nodes=None):
    """reset attributes such as scale pivot, and shear, so that only scale rotate and translate modify the transforms position"""

    # parse args
    if nodes == None:
        nodes = pymel.ls(selection=True)
    else:
        nodes = ka_pymel.getAsPyNodes(nodes)
        if not isinstance(nodes, list):
            nodes = [nodes]

    # define sub command
    def setAttr(node, attrName, value):
        if pymel.objExists(node):
            if pymel.attributeQuery(attrName, node=node, exists=True):
                lockedAttrs = []
                attrsToCheck = [node.attr(attrName)]
                childAttrs = pymel.attributeQuery(attrName, node=node, listChildren=True)
                if childAttrs:
                    for childAttr in childAttrs:
                        attrsToCheck.append(node.attr(childAttr))

                for attrToCheck in attrsToCheck:
                    if attrToCheck.get(lock=True):
                        lockedAttrs.append(attrToCheck)
                        attrToCheck.set(lock=False)

                node.attr(attrName).set(value)

                if lockedAttrs:
                    for lockedAttr in lockedAttrs:
                        lockedAttr.set(lock=True)



    reset_attrList = {
        'rotatePivotTranslate':[0,0,0],
        'rotateTranslate':[0,0,0],
        'scalePivotTranslate':[0,0,0],
        'scalePivot':[0,0,0],
        'scale':[1,1,1],
        'rotatePivot':[0,0,0],
        'rotateAxis':[0,0,0],
        'shear':[0,0,0],
        'jointOrient':[0,0,0],
        }

    # do work
    for each in nodes:
        for attr in reset_attrList:
            setAttr(each, attr, reset_attrList[attr])


def removeJointOrients(inputJoints=None):
    if not inputJoints:
        inputJoints = pymel.ls(selection=True, type='joint')

    for joint in inputJoints:
        initialMatrix = pymel.xform(joint, query=True, matrix=True, worldSpace=True)
        joint.jointOrient.set(0,0,0)
        pymel.xform(joint, matrix=initialMatrix, worldSpace=True)


ALL_TRANSFORM_ATTRS = ('t', 'r', 's', 'v', 'radius', 'jointOrient', 'rotateAxis', 'rotateOrder', 'rotatePivot',
                       'rotatePivotTranslate', 'scalePivot', 'scalePivotTranslate' )
DEFAULT_TRANSFORM_ATTRS = ('t', 'r', 's', 'v', 'radius')

def lockTransformAttrs(nodes=None, t=True, r=True, s=True, radius=True, v=True, transformExtras=True):
    """Locks and makes non keyable, the given attributes (which are by default keyable on a transform).

    args:
        nodes  - list of nodes - List of objects to lock, if none are given, then use current selection
        t      - bool - if True, Locks Translate
        r      - bool - if True, Locks Rotate
        s      - bool - if True, Locks Scale
        v      - bool - if True, Locks Visibility
        radius - bool - if True, Locks Radius
    """


    if not nodes:
        pymel.error('no nodes specified to lock attrs on')

    if not isinstance(nodes, list) or isinstance(nodes, tuple):
        nodes = [nodes]

    attrs = []
    if t: attrs.extend('t')
    if r: attrs.append('r')
    if s: attrs.append('s')
    if v: attrs.append('v')
    if radius: attrs.append('radius')
    if transformExtras: attrs.extend(['shear', 'jointOrient', 'rotateAxis', 'rotateOrder', 'rotatePivot', 'rotatePivotTranslate',
                                     'scalePivot', 'scalePivotTranslate'])


    for node in nodes:
        for attrName in attrs:
            if hasattr(node, attrName):
                attr = node.attr(attrName)
                try:
                    attr.lock()
                    attr.set(keyable=False)

                    for childAttr in attr.getChildren():
                        childAttr.set(keyable=False)
                        childAttr.set(lock=True)

                except: pass


def unlockTransformAttrs(nodes=None, t=False, r=False, s=False, radius=False, v=False, transformExtras=False):
    """Locks and makes non keyable, the given attributes (which are by default keyable on a transform).

    args:
        nodes  - list of nodes - List of objects to unlock, if none are given, then use current selection
        t      - bool - if True, Unlocks Translate
        r      - bool - if True, Unlocks Rotate
        s      - bool - if True, Unlocks Scale
        v      - bool - if True, Unlocks Visibility
        radius - bool - if True, Unlocks Radius
    """

    attrs = []
    if t: attrs.append('t')
    if r: attrs.append('r')
    if s: attrs.append('s')
    if v: attrs.append('v')
    if radius: attrs.append('radius')
    if transformExtras: attrs.extend(['shear', 'jointOrient', 'rotateAxis', 'rotateOrder', 'rotatePivot', 'rotatePivotTranslate',
                                     'scalePivot', 'scalePivotTranslate'])

    if not nodes:
        nodes = pymel.ls(selection=True)

    for node in nodes:
        for attrName in attrs:
            if hasattr(node, attrName):
                attr = node.attr(attrName)
                try:
                    attr.unlock()
                    attr.set(keyable=True)

                    for childAttr in attr.getChildren():
                        try:
                            childAttr.unlock()
                            childAttr.set(keyable=True)
                        except: pass

                except: pass


def snap(snapObjects=None, snapTarget=None, t=0, s=0, r=0, a=0, m=0, jo=0):
    '''snaps objects to A to object B based on translate rotate or scale'''

    if t==0 and r==0 and s==0 and a==0 and m==0 and jo==0:
        pymel.error('snap recieved no arguments for which snap operation!')

    sel = pymel.ls(selection=True)

    if not snapObjects:
        snapObjects = sel[:-1]

    elif not isinstance(snapObjects, list):
        snapObjects = [snapObjects]

    if not snapTarget:
        snapTarget = sel[-1]

    elif isinstance(snapTarget, list):
        snapTarget = snapTarget[0]


    if t:
        for each in snapObjects:
            worldTrans = pymel.xform(snapTarget, q=True, ws=True, translation=True)
            pymel.xform(each, ws=True, translation=worldTrans)

    if s:
        for each in snapObjects:

            tempConstraint = pymel.scaleConstraint(snapTarget, each)
            pymel.delete(tempConstraint)
#            worldScale = pymel.xform(snapTarget, q=True, scale=True)
#            pymel.xform(each, ws=True, scale=worldScale)

    if r:
        for each in snapObjects:
            worldRot = pymel.xform(snapTarget, q=True, ws=True, rotation=True)
            pymel.xform(each, ws=True, rotation=worldRot)


    if jo:
        for each in snapObjects:
            worldRot = pymel.xform(snapTarget, q=True, ws=True, rotation=True)
            if hasattr(each, 'jointOrient'):
                each.jointOrient.set(0,0,0)

            pymel.xform(each, ws=True, rotation=worldRot)

            if hasattr(each, 'jointOrient'):
                each.jointOrient.set(each.r.get())
                each.r.set(0,0,0)


    if a:
        if isinstance(a, list):
            primaryAxis = a[0]
            secondaryAxis = a[1]

        else:
            axisList = ['x', '-x', 'y', '-y', 'z', '-z', ]
            primaryAxis = axisList[ka_preference.get('snapToolPrimaryAxis', 0)]
            secondaryAxis = axisList[ka_preference.get('snapToolSecondaryAxis', 4)]

        for each in snapObjects:
            aimSnap(each, snapTarget, primaryAxis=primaryAxis, secondaryAxis=secondaryAxis)


    if m:
        for each in snapObjects:

            if pymel.nodeType(each) == 'joint':
                snapToMirroredPositionOfTransform(snapTarget, each, behavior=True)
            else:
                snapToMirroredPositionOfTransform(snapTarget, each, behavior=True)

    pymel.select(snapObjects)


def aimSnap(a=None, b=None, primaryAxis='x', secondaryAxis='z'):
    """snaps an object to point its primary axis towards the target
    and to twist its secondary axis to point as near as posible (while
    still pointing its primary axis at the target)"""
    if a == None:
        a = pymel.ls(selection=True)[0]
    if b == None:
        b = pymel.ls(selection=True)[1]


    if   primaryAxis ==  'x': primaryAxis = [ 1, 0, 0]
    elif primaryAxis == '-x': primaryAxis = [-1, 0, 0]
    elif primaryAxis ==  'y': primaryAxis = [ 0, 1, 0]
    elif primaryAxis == '-y': primaryAxis = [ 0,-1, 0]
    elif primaryAxis ==  'z': primaryAxis = [ 0, 0, 1]
    elif primaryAxis == '-z': primaryAxis = [ 0, 0,-1]

    if   secondaryAxis ==  'x': secondaryAxis = [ 1, 0, 0]
    elif secondaryAxis == '-x': secondaryAxis = [-1, 0, 0]
    elif secondaryAxis ==  'y': secondaryAxis = [ 0, 1, 0]
    elif secondaryAxis == '-y': secondaryAxis = [ 0,-1, 0]
    elif secondaryAxis ==  'z': secondaryAxis = [ 0, 0, 1]
    elif secondaryAxis == '-z': secondaryAxis = [ 0, 0,-1]


    _aimSnap(a, b, primaryAxis=primaryAxis, secondaryAxis=secondaryAxis)

def _aimSnap(a, b, primaryAxis=(1,0,0), secondaryAxis=(0,0,1)):

    def crossProduct(vect1, vect2):
        return [ vect1[1]*vect2[2] - vect1[2]*vect2[1], vect1[2]*vect2[0] - vect1[0]*vect2[2], vect1[0]*vect2[1] - vect1[1]*vect2[0] ]

    def normalizeVector(vector):
        return [ vector[i]/magnitudeOfVector(vector)  for i in range(len(vector)) ]

    def magnitudeOfVector(vector):
        return math.sqrt( sum( vector[i]*vector[i] for i in range(len(vector)) ) )

    # get positions
    posA = pymel.xform(a, query=True, translation=True, worldSpace=True)
    posB = pymel.xform(b, query=True, translation=True, worldSpace=True)

    # normalized vector from A to B
    primaryVector = normalizeVector([posB[0]-posA[0], posB[1]-posA[1], posB[2]-posA[2], ])

    # initial matrix
    matrixA = pymel.xform(a, query=True, matrix=True, worldSpace=True)

    # sort out the details of which axis are being used
    # matrixSlice (primary/secondary) is the slice in the matrix of that axis
    # index (primary/secondary) is the index in a tuple of (x,y,z) that represents the axis
    if primaryAxis[0]:
        primaryMatrixSlice = slice(0, 3)
        primaryIndex = 0
    elif primaryAxis[1]:
        primaryMatrixSlice = slice(4, 7)
        primaryIndex = 1
    elif primaryAxis[2]:
        primaryMatrixSlice = slice(8,11)
        primaryIndex = 2


    if secondaryAxis[0]:
        secondaryMatrixSlice = slice(0, 3)
        secondaryIndex = 0
    elif secondaryAxis[1]:
        secondaryMatrixSlice = slice(4, 7)
        secondaryIndex = 1
    elif secondaryAxis[2]:
        secondaryMatrixSlice = slice(8,11)
        secondaryIndex = 2

    # secondaryVector is the axis vector from the initial matrix
    secondaryVector = normalizeVector(matrixA[secondaryMatrixSlice])

    # in case of negitive axis
    primaryVector[0] *= primaryAxis[primaryIndex]
    primaryVector[1] *= primaryAxis[primaryIndex]
    primaryVector[2] *= primaryAxis[primaryIndex]
    secondaryVector[0] *= secondaryAxis[secondaryIndex]
    secondaryVector[1] *= secondaryAxis[secondaryIndex]
    secondaryVector[2] *= secondaryAxis[secondaryIndex]

    if not primaryAxis[0] and not secondaryAxis[0]:
        otherMatrixSlice = slice(0, 3)
        otherIndex = 0
        if primaryIndex == 1: invertOrder = False
        else: invertOrder = True

    elif not primaryAxis[1] and not secondaryAxis[1]:
        otherMatrixSlice = slice(4, 7)
        otherIndex = 1
        if primaryIndex == 2: invertOrder = False
        else: invertOrder = True

    elif not primaryAxis[2] and not secondaryAxis[2]:
        otherMatrixSlice = slice(8,11)
        otherIndex = 2
        if primaryIndex == 0: invertOrder = False
        else: invertOrder = True

    if not invertOrder:
        crossVector = normalizeVector( crossProduct(primaryVector, secondaryVector) )
        secondaryVector = crossProduct(crossVector, primaryVector)
        otherVector = normalizeVector( crossProduct(primaryVector, secondaryVector) )
    else:
        crossVector = normalizeVector( crossProduct(secondaryVector, primaryVector) )
        secondaryVector = crossProduct(primaryVector, crossVector)
        otherVector = normalizeVector( crossProduct(secondaryVector, primaryVector) )

    newMatrix = [0,0,0,0,0,0,0,0,0,0,0,0,matrixA[12],matrixA[13],matrixA[14],1]
    newMatrix[primaryMatrixSlice] = primaryVector
    newMatrix[secondaryMatrixSlice] = secondaryVector
    newMatrix[otherMatrixSlice] = otherVector
    newMatrix[3] = 0
    newMatrix[7] = 0
    newMatrix[11] = 0
    newMatrix[15] = 1
    pymel.xform(a, matrix=newMatrix, worldSpace=True)



def makeZroGroup(*inputObjects):
    selection = pymel.ls(selection=True)
    if inputObjects:
        selection = inputObjects

    for each in selection:
        nodeName = each.nodeName()
        newNodeName = each.nodeName()
        parent = each.getParent()

        if parent:
            parentNodeName = parent.nodeName()

            if len(parentNodeName) > 4:

                if parentNodeName[-4:] == '_zro':
                    newNodeName = parentNodeName.split('_zro')[0]
                    newNodeName += '_ofsA'

                elif parentNodeName[-5:] == '_ofsA':
                    newNodeName = parentNodeName.split('_ofsA')[0]
                    newNodeName += '_ofsB'

                elif parentNodeName[-5:] == '_ofsB':
                    newNodeName = parentNodeName.split('_ofsB')[0]
                    newNodeName += '_ofsC'

                else:
                    newNodeName += '_zro'

        # get new name
        suffixFound = False
        possibleControlSuffix = ['_ctl', '_ctrl', '_cnt','_Ctl', '_Ctrl', '_Cnt',]
        for suffix in possibleControlSuffix:
            if suffix in nodeName:
                newNodeName = newNodeName.split(suffix)[0]
                newNodeName += '_zro'
                suffixFound = True

        if not suffixFound:
            newNodeName += '_zro'

        zroGroup = pymel.createNode('transform')
        zroGroup.rename(newNodeName)
        snap(t=1, s=1, r=1, snapTarget=each, snapObjects=[zroGroup])

        if parent:
            pymel.parent(zroGroup, parent)

        pymel.parent(each, zroGroup)

    pymel.select(selection)


def getIkUpVector_position(inputA, inputB, inputC, ikPlaneAxis='z'):
    """
    Get ideal position for an ik upvector

    Takes 3 inputs and returns a position that is ideal for an ik upvector. The
    ideal position will cause the ik chain to be in the same position as the inputs.
    The inputs can be either transforms, points, or matrices.

    Args:
        inputA: first transform in chain. Can be a transform, point, or matrix
        inputB: second transform in chain. Can be a transform, or matrix
        inputC: thrid transform in chain. Can be a transform, point, or matrix

    Returns:
        a point representing the ideal position for an upvector.
        example:

        [0, 9.0, 3.5]
    """

    # pars args
    pointA = getAsPoint(inputA)
    pointB = getAsPoint(inputB)
    pointC = getAsPoint(inputC)

    # do math
    matrixB = getAsMatrix(inputB)

    ikPlaneUpVector = getVectorFromMatrix(matrixB, axis=ikPlaneAxis)
    vectorCA = ka_math.normalize(ka_math.subtract(pointC, pointA))
    #vectorCB = ka_math.normalize(ka_math.subtract(pointC, pointB))

    crossVector = ka_math.crossProduct(vectorCA, ikPlaneUpVector)
    #crossVector = ka_math.crossProduct(vectorCA, vectorCB)
    #crossVector = ka_math.crossProduct(vectorCA, crossVector)

    distanceAB = ka_math.distanceBetween(pointA, pointB)
    distanceBC = ka_math.distanceBetween(pointA, pointB)

    moveVector = ka_math.multiply(crossVector, (distanceAB+distanceBC))
    position = ka_math.add(pointB, moveVector)

    return position


def snapRigControl(nodes=None, targetNode=None):
    if nodes == None:
        sel = pymel.ls(selection=True)
        nodes = sel[:-1]
        targetNode = sel[-1]

    globalPosOfTarg = pymel.xform(targetNode, query=True, translation=True, worldSpace=True)
    for node in nodes:
        #if hasattr(node, 'tipOffset'):
        snap(node, targetNode, r=True, t=True)

        tipOffsetAttr = None
        tipOffsetParent = node.getParent()
        for i in range(5):
            inputs = tipOffsetParent.tx.inputs(plugs=True)
            if inputs:
                inputAttr = inputs[0]
                if inputAttr.name(includeNode=False) == 'tipOffset':
                    tipOffsetAttr = inputAttr
                    break

            tipOffsetParent = tipOffsetParent.getParent()

        OOOOOOO = 'tipOffsetAttr'; print '%s: ' % OOOOOOO, eval(OOOOOOO), ' ', type(eval(OOOOOOO))
        OOOOOOO = 'tipOffsetParent'; print '%s: ' % OOOOOOO, eval(OOOOOOO), ' ', type(eval(OOOOOOO))

        if tipOffsetAttr:
            inputs = tipOffsetAttr.inputs(plugs=True)
            while inputs:
                tipOffsetAttr = inputs[0]
                inputs = tipOffsetAttr.inputs(plugs=True)


            point = getInForienSpace_point(globalPosOfTarg, tipOffsetParent.getParent())
            OOOOOOO = 'point'; print '%s: ' % OOOOOOO, eval(OOOOOOO), ' ', type(eval(OOOOOOO))
            tipOffsetAttr.set(point[0])

            #recievingTransform = node.tipOffset.outputs()[0]
            #point = ka_transforms.getInForienSpace_point(globalPosOfTarg, recievingTransform.getParent())
            #node.tipOffset.set(point[0])

