import math

import pymel.core as pymel

import ka_maya.ka_math as ka_math #;reload(ka_math)
import ka_maya.ka_transforms as ka_transforms #;reload(ka_transforms)
import ka_maya.ka_python as ka_python #;reload(ka_python)

def distanceBetween(pointA, pointB):
    '''returns distance between a list of 2d or 3d coordinates'''
    sum = 0
    for i, each in enumerate(pointA):
        sum += (pointA[i] - pointB[i])**2

    return math.sqrt( sum )

def shapeParent(objectA, objectB):

    shapeObj = pymel.parent(objectA, objectB)
    pymel.makeIdentity(shapeObj[0], apply=True, t=1, r=1, s=1, n=1)
    shapes = pymel.listRelatives(shapeObj[0], shapes=True)

    for shape in shapes:
        pymel.parent(shape, objectB, shape=True, add=True)

    pymel.delete(shapeObj)
    pymel.select(objectB)

def makeControl():
    pass



def create_pistonMuscle():
    text=None
    result = cmds.promptDialog(
                    title='Name Muscle',
                    message='Enter a Base Name:',
                    button=['OK', 'Cancel'],
                    defaultButton='OK',
                    cancelButton='Cancel',
                    dismissString='Cancel')

    if result == 'OK':
        text = cmds.promptDialog(query=True, text=True)

        if text:
            _createBendMuscle(baseName)
        else:
            _createBendMuscle()


def _create_pistonMuscle(baseName):
    pass

def print_pistonMuscle():
    pass




def makeRibonFromTransforms(transformList=None, secondaryAxis=1):
    if not transformList:
        transformList = pymel.ls(selection=True)
    if not hasattr(transformList, '__iter__'):
        list(transformList)

    lenOfTransformList = len(transformList)
    if lenOfTransformList < len(transformList):
        pymel.error('must select at least 4 transforms to build ribon')

    ribon, makeNurbPlane = pymel.nurbsPlane( d=3, u=1, v=lenOfTransformList-3 )
    ribonShape = ribon.getShape()

    for i, transform in enumerate(transformList):
        cvRow = ribonShape.cv[0:3][i]
        ribonVector = [0.0, 0.0, 0.0]

        for ib, cv in enumerate(cvRow):
            if ib == 0: ribonVector[secondaryAxis] = 1.0
            if ib == 1: ribonVector[secondaryAxis] = 0.0
            if ib == 2: ribonVector[secondaryAxis] = -1.0
            ka_transforms.translate_inTargetObjectsSpace([ribonShape.cv[ib][i]], ribonVector, transform)

        # create a control locator for row
        controlLocatorShape = pymel.createNode('locator')
        controlLocator = controlLocatorShape.getParent()

        guideLocatorWorldMatrix = pymel.xform(transform, query=True, matrix=True, worldSpace=True)
        pymel.xform(controlLocator, matrix=guideLocatorWorldMatrix, worldSpace=True)


    pymel.delete(ribonShape, constructionHistory=True)
            ##transform cvRow i*0.333 in transforms y-axis
            #utils
            #pass



def makeAdvancedIkSplineUI():
    '''Simple UI to create an ik spline with strech and upvectors from the start and end joint (selected in that order.
    The strech will preserve the ratio of the inital joint lengths, though the scale of the chain may change to fit the
    newly created chain. If more than 2 joints are selected, the joints inbetween the first and last will be an additional twist point,
    and also be the connecting point between the multiple overlapping ik splines'''

    if cmds.windowPref( 'makeAdvancedIkSplineWindow', exists=True ):
        cmds.windowPref( 'makeAdvancedIkSplineWindow', remove=True )


    if cmds.window('makeAdvancedIkSplineWindow', exists=True):
        cmds.deleteUI('makeAdvancedIkSplineWindow', window=True)

    windowH = 100
    windowW = 350
    windowUI = cmds.window('makeAdvancedIkSplineWindow', title="makeAdvancedIkSplineWindow", iconName='make Advanced Ik Spline', widthHeight=(windowW, windowH,) )
    cmds.rowColumnLayout(columnWidth=[1, windowW])
    cmds.text("Rig IK Spline")

    cmds.separator(vis=0, h=5)
    cmds.separator()
    cmds.separator(vis=0, h=5)

    cmds.text("Base Name:")
    nameField = cmds.textField()

    cmds.separator(vis=0, h=5)
    cmds.separator()
    cmds.separator(vis=0, h=5)

    cmds.text("Number Of Spans")
    numbOfSpansField = cmds.intField(v=2, minValue=1, width=50)

    cmds.separator(vis=0, h=5)
    cmds.separator()
    cmds.separator(vis=0, h=5)

    def cmd(*args, **kwargs):
        baseName = cmds.textField(nameField, q=True, text=True)
        numbOfSpans = cmds.intField(numbOfSpansField, q=True, value=True)
        makeAdvancedIkSplineFromSelection(baseName, numbOfSpans)

    cmds.button( label='Create', command=cmd)

    cmds.setParent( '..' )
    cmds.window(windowUI, edit=True, width=windowW, height=windowH )
    cmds.showWindow( windowUI )

def makeAdvancedIkSplineFromSelection(baseName, numbOfCvs):
    '''makes an ikSpline from selection'''

    selection = pymel.ls(selection=True)



    if len(selection) > 2:
        twistControlJoints = selection[1:-1]

    else:
        twistControlJoints = []

    rootJoint = selection[0]
    endJoint = selection[-1]


    makeAdvancedIkSpline(baseName, rootJoint, endJoint, numbOfCvs=numbOfCvs, twistControlJoints=twistControlJoints)


def makeAdvancedIkSpline(baseName, rootJoint, endJoint, numbOfCvs=2, twistControlJoints=[], closedCurve=False):

    #make a list of the points of the joints so we can make a linear point per joint curve with it later
    #this will serve as the curve we can build our iks on to start
    chainWorldSpacePointList = []
    jointList = []
    parent = [endJoint]


    while parent:

        joint = parent
        position = tuple(pymel.xform(joint, query=True, translation=True, worldSpace=True))
        jointList.append(joint)
        chainWorldSpacePointList.append(position)

        if parent[0] != rootJoint:
            parent = pymel.listRelatives(parent, parent=True)

        else:
            parent = []

    chainWorldSpacePointList.reverse()
    totalJointLength = 0
    for i, point in enumerate(chainWorldSpacePointList):
        if i != 0:
            totalJointLength += ka_math.distanceBetween( chainWorldSpacePointList[i-1], chainWorldSpacePointList[i] )


    jointLinearCurve = pymel.curve( p=chainWorldSpacePointList, degree=1)
    curveInfo = pymel.createNode('curveInfo')
    multiplyDivideLength = pymel.createNode('multiplyDivide',)
    curveInfo.arcLength >> multiplyDivideLength.input1X

    jointLinearCurve.getShape().worldSpace[0] >> curveInfo.inputCurve

    #numbOfSpans = (len(twistControlJoints)*(numbOfCvs+1))+1
    numbOfSpans = ( (len(twistControlJoints)+1) * numbOfCvs ) + len(twistControlJoints) -1

    if closedCurve:
        numbOfSpans -= 1
    niceCurve = pymel.rebuildCurve(jointLinearCurve, replaceOriginal=False, degree=3, spans=numbOfSpans, constructionHistory=False)[0]
    niceCurve.rename(baseName+'_ikCurve')
    niceCurve.inheritsTransform.set(0)
    niceCurveCvs = list(niceCurve.getShape().cv)

    if closedCurve:
        pymel.closeCurve(niceCurve, replaceOriginal=True)


    chainStartEnds = []
    if twistControlJoints:
        #rootParent = rootJoint.getParent()

        twistControlJoints.append(endJoint)
        localStartJoint = rootJoint
        for twistControlJoint in twistControlJoints:
            if twistControlJoint == twistControlJoints[-1]:
                localEndJoint = endJoint

            else:
                twistControlJointName = twistControlJoint.nodeName()
                localEndJoint = pymel.duplicate(twistControlJoint,)[0]
                localEndJoint.rename(twistControlJointName+'EndJoint')
                endJointChildren = pymel.listRelatives(localEndJoint)
                pymel.delete(endJointChildren)
                pymel.parent(twistControlJoint, localEndJoint)
                localEndJoint.radius.set(0)

            chainStartEnds.append((localStartJoint, localEndJoint))
            localStartJoint = twistControlJoint


    else:
        chainStartEnds.append((rootJoint, endJoint))


    ikHandles = []
    locators = []
    firstControlBuilt = True
    for chain_i, chainStartEnd in enumerate(chainStartEnds):

        chainStart, chainEnd = chainStartEnd

        ikHandle = pymel.ikHandle(startJoint=chainStart, endEffector=chainEnd, solver='ikSplineSolver', rootOnCurve=False)[0]

        ikHandles.append(ikHandle)
        jointChain = pymel.ikHandle(ikHandle, query=True, jointList=True)
        jointChain.append(chainEnd)


        if chain_i == 0:
            ikHandle.rootOnCurve.set(1)

        ikHandle.rename(baseName+'_ikHandle'+str(chain_i))

        pymel.delete(ikHandle.inCurve.inputs(plugs=True)[0].node().getParent())
        ikCurveShape = jointLinearCurve.getShape()
        ikCurveShape.worldSpace[0] >> ikHandle.inCurve

        #ikCurveShape = ikHandle.inCurve.inputs(plugs=True)[0].node()


        ikCurve = pymel.listRelatives(ikCurveShape, parent=True)[0]
        ikCurve.rename(baseName+'_unSmoothedIkSplineCurve')
        ikCurve.inheritsTransform.set(0)
        ikCurve.translate.lock()
        ikCurve.rotate.lock()
        ikCurve.scale.lock()
        ikEndEffector = pymel.ikHandle(ikHandle, query=True, endEffector=True)
        ikEndEffector.rename(baseName+'_ikEndEffector')

        #if chain_i != 0:
            #multiplyDivide = pymel.createNode('multiplyDivide')
            #curveInfoNode.arcLength >> multiplyDivide.input1X
            #multiplyDivide.input2X.set(ChainLengthCount / jointLinearCurve.getShape().length())
            #multiplyDivide.outputX >> ikHandle.offset
            ##multiplyDivide.operation.set(2)

        if chain_i == 0:
            controllersToMake = numbOfCvs+2
        else:
            controllersToMake = numbOfCvs+1

        chain_midLocators = []
        for i in range(controllersToMake):

            #if last twist control in the closed curve ikChain
            if closedCurve and chain_i == len(chainStartEnds)-1 and i == controllersToMake-1:
                locators.append(locators[0])

            else:
                curveCv = niceCurveCvs.pop(0)
                isATwistControl = False
                if firstControlBuilt or i == controllersToMake-1:
                    locator = pymel.curve( p=[(0.0, 2.2204460492503131e-16, 3.0000000000000009), (0.0, 0.0, 0.0), (0.0, 1.0, -1.6653345369377348e-16), (3.3306690738754696e-16, 3.3306690738754696e-16, 2.0), (0.0, -1.0, 1.6653345369377348e-16), (0.0, 0.0, 0.0)], degree=1)
                    isATwistControl = True
                else:
                    locator = pymel.spaceLocator()

                locator.rename(baseName+'_ikCluster'+str(curveCv.currentItemIndex()))
                locatorShape = locator.getShapes()[0]
                locator.translate.set(curveCv.getPosition())
                pymel.cluster(curveCv, wn=(locator, locator), bindState=True )
                locators.append(locator)

                if isATwistControl:
                    if firstControlBuilt:
                        chainStartPosition = pymel.xform(chainStart, query=True, translation=True, worldSpace=True)
                        pymel.xform(locator, translation=chainStartPosition, worldSpace=True)
                        firstControlBuilt=False
                    else:
                        chainEndPosition = pymel.xform(chainEnd, query=True, translation=True, worldSpace=True)
                        pymel.xform(locator, translation=chainEndPosition, worldSpace=True)

                else:
                    chain_midLocators.append(locator)




        if chain_i == 0:
            chain_startLocatorIndex = 0
            chain_endLocatorIndex = -1

        else:
            chain_startLocatorIndex = (controllersToMake*-1)-1
            chain_endLocatorIndex = -1

        chain_startLocator = locators[chain_startLocatorIndex]
        chain_endLocator = locators[chain_endLocatorIndex]


        for locator in chain_midLocators:
            ka_math.distanceBetween(chain_startLocator.translate.get(), chain_endLocator.translate.get())

        pymel.parent(ikHandle, locators[0])


        ikHandle.dTwistControlEnable.set(1)
        ikHandle.dWorldUpType.set(4)
        ikHandle.dWorldUpAxis.set(3)
        ikHandle.dWorldUpVector.set([0,0,1])
        ikHandle.dWorldUpVectorEnd.set([0,0,1])

        chain_startLocator.worldMatrix >> ikHandle.dWorldUpMatrix
        chain_endLocator.worldMatrix >> ikHandle.dWorldUpMatrixEnd

        if chain_i == 0:
            ikHandle.addAttr('currentLength', keyable=True, defaultValue=1)
            ikHandle.addAttr('currentScale', keyable=True, defaultValue=1)
            ikHandle.addAttr('goalLength', keyable=True, defaultValue=1)
            ikHandle.addAttr('percentLength', keyable=True, defaultValue=1)
            ikHandle.addAttr('goalPercentBlend', keyable=True, defaultValue=1, maxValue=1, minValue=0)

        jointList = pymel.ikHandle(ikHandle, query=True, jointList=True,)
        jointList.append(endJoint)
        for i, joint in enumerate(jointList):
            if not i == 0:
                distance = ka_math.distanceBetween( [0,0,0], joint.translate.get() )
                joint.jointOrient.set(0,0,0)
                joint.translateX.set(distance)
                joint.translateY.set(0)
                joint.translateZ.set(0)

            else:
                joint.jointOrient.set(0,0,0)




        #curveInfo = pymel.createNode('curveInfo',)
        #ikCurveShape.worldSpace[0] >> curveInfo.inputCurve

        curveLength = curveInfo.arcLength.get()
        numberOfJoints = len(chainWorldSpacePointList)
        curveLengthEqualSegment = curveLength / ( numberOfJoints-1 )

        if chain_i == 0:
            ikHandle.goalLength >> multiplyDivideLength.input1Y
            ikHandle.percentLength >> multiplyDivideLength.input2X
            ikHandle.currentScale >> multiplyDivideLength.input2Y
            multiplyDivideLength.outputX >> ikHandle.currentLength
            ikHandle.goalLength.set( ikHandle.currentLength.get() )

            blendColorGoalPercentBlend = pymel.createNode('blendColors',)
            blendColorGoalPercentBlend.rename('blendColorGoalPercentBlend')
            multiplyDivideLength.outputX >> blendColorGoalPercentBlend.color1R
            multiplyDivideLength.outputY >> blendColorGoalPercentBlend.color2R
            ikHandle.goalPercentBlend >> blendColorGoalPercentBlend.blender

            multiplyDivideLengthPerJoint = pymel.createNode('multiplyDivide')
            multiplyDivideLengthPerJoint.rename('multiplyDivideLengthPerJoint')
            blendColorGoalPercentBlend.outputR >> multiplyDivideLengthPerJoint.input1X
            multiplyDivideLengthPerJoint.input2X.set(1.0 / ( numberOfJoints-1 ))

            curveInfo.arcLength >> ikHandle.currentLength

            multiplyDivideScale = pymel.createNode('multiplyDivide')
            multiplyDivideScale.rename('multiplyDivideScale')
            multiplyDivideLengthPerJoint.outputX >> multiplyDivideScale.input1X
            multiplyDivideScale.operation.set(2)
            ikHandle.currentScale >> multiplyDivideScale.input2X


        for i, joint in enumerate(jointChain):
            if i != 0:
                initialJointLength = ka_math.distanceBetween( [0,0,0], joint.translate.get() )
                percentOfJointTotal = initialJointLength / totalJointLength

                lengthOfCurveSegmanet = percentOfJointTotal * curveLength
                percentOfEqualSegment = lengthOfCurveSegmanet / curveLengthEqualSegment

                multiplyDivide = pymel.createNode('multiplyDivide')
                multiplyDivide.rename('multiplyDivideJointLengthRatio')
                multiplyDivide.input2X.set(percentOfEqualSegment)
                multiplyDivideScale.outputX >> multiplyDivide.input1X
                multiplyDivide.outputX >> joint.tx

        if chain_i == 0:
            scaleConstraint = pymel.createNode('scaleConstraint')
            pymel.parent(scaleConstraint, ikHandle)
            ikHandle.scale >> scaleConstraint.target[0].targetScale
            ikHandle.parentMatrix >> scaleConstraint.target[0].targetParentMatrix
            scaleConstraint.constraintScaleX >> ikHandle.currentScale

            ikHandle.currentLength.lock()
            ikHandle.currentScale.lock()
        ikHandle.visibility.set(0)
        ikCurve.template.set(1)

    connectionPlugs = jointLinearCurve.getShape().worldSpace[0].outputs(plugs=True)
    for plug in connectionPlugs:
        niceCurve.worldSpace[0] >> plug

    pymel.delete(jointLinearCurve)

    OOOOOOO = 'ikCurve';  print '%s = %s %s'%(str(OOOOOOO),str(eval(OOOOOOO)),str(type(eval(OOOOOOO))))
    infoDict = {'ikCurve':niceCurve,
                'jointList':jointList,
                'locators':locators,
    }

    return infoDict

def createBendMuscle():
    text=None
    result = cmds.promptDialog(
                    title='Name Muscle',
                    message='Enter a Base Name:',
                    button=['OK', 'Cancel'],
                    defaultButton='OK',
                    cancelButton='Cancel',
                    dismissString='Cancel')

    if result == 'OK':
        text = cmds.promptDialog(query=True, text=True)

        if text:
            _createBendMuscle(name=text)
        else:
            _createBendMuscle()


def procedurallyCreateBendMuscle(baseName=None, numberOfJoints=[3,3], radius=1, insertionParent=None, originParent=None, pivotIndicatorZroParent=None, insertionMatrix=[], originMatrix=[], pivotIndicatorZroMatrix=[], pivotPositionMatrix=[], jointPercents=[]):

#    pivotIndicator = _createBendMuscle(name=baseName, numberOfInbetweenJoints=numberOfJoints, radius=radius)
    pivotIndicator = _createBendMuscle(name=baseName, numberOfInbetweenJoints=[3,3], radius=radius)
    #pivotIndicatorZro = pymel.listRelatives(pivotIndicator, parent=True)[0]
    insertionNull = pivotIndicator.insertion.inputs()[0]
    originNull = pivotIndicator.origin.inputs()[0]

    if originParent:
        pymel.parent(originNull, originParent)

    if insertionParent:
        pymel.parent(insertionNull, insertionParent)

    #if pivotIndicatorZroParent:
        #pymel.parent(pivotIndicatorZro, pivotIndicatorZroParent)

    if originMatrix:
        pymel.xform(originNull, ws=True, m=originMatrix)
    if insertionMatrix:
        pymel.xform(insertionNull, ws=True, m=insertionMatrix)
    #if pivotIndicatorZroMatrix:
        #pymel.xform(pivotIndicatorZro, ws=True, m=pivotIndicatorZroMatrix)
    if pivotPositionMatrix:
        pymel.xform(pivotIndicator, ws=True, m=pivotPositionMatrix)

    bendyJoints = getBendyJoints(pivotIndicator)
    for iA, listOfJoints in enumerate(bendyJoints):
        for iB, joint in enumerate(listOfJoints):
            joint.constraintPercent.set(float(jointPercents[iA][iB]))

    return pivotIndicator

def getBendyJoints(pivotIndicator):
    muscleMidPointJoint = []

    originJointsDict = {}
    originJointsList = []

    insertionJointsDict = {}
    insertionJointsList = []

    joints = pymel.listRelatives(pivotIndicator, type='joint', children=True)

    if not joints:
        transforms = pymel.listRelatives(pivotIndicator, type='transform', children=True)
        for transform in transforms:
            if pymel.attributeQuery('rigType', node=transform, exists=True):
                rigType = transform.rigType.get()
                if rigType == 'jointsGroup':
                    joints = pymel.listRelatives(transform, type='joint', children=True)


    if joints:
        for joint in joints:
            if pymel.attributeQuery('baseName', node=joint, exists=True):
                jointBaseName = joint.baseName.get()

                if 'muscleOriginInbetweenJoint' in jointBaseName:
                    originJointsDict[jointBaseName] = joint

                if 'muscleInsertionInbetweenJoint' in jointBaseName:
                    insertionJointsDict[jointBaseName] = joint

                if jointBaseName == 'muscleMidPointJoint':
                    muscleMidPointJoint = [joint]


    for key in sorted(originJointsDict):
        originJointsList.append(originJointsDict[key])

    for key in sorted(insertionJointsDict):
        insertionJointsList.append(insertionJointsDict[key])

    return [originJointsList, insertionJointsList, muscleMidPointJoint]


def printCommand_procedurallyCreateBendMuscleJoint():
    allBendMuscleJoints = getAllBendMuscleJoints()

    for pivotIndicator in allBendMuscleJoints:
        pivotIndicatorZro = pymel.listRelatives(pivotIndicator, parent=True)[0]

        baseName = pivotIndicator.nodeName()
        baseName = baseName.replace('_pivotPosition', '', 1)

        radius = str(pivotIndicator.radius.get())

        insertionNull = pivotIndicator.insertion.inputs()[0]
        originNull = pivotIndicator.origin.inputs()[0]

        insertionParent = insertionNull.getParent()
        if insertionParent:
            insertionParent = str(insertionParent)
        else:
            insertionParent = ''

        originParent = originNull.getParent()
        if originParent:
            originParent = str(originParent)
        else:
            originParent = ''

        #pivotIndicatorParent = pivotIndicatorZro.getParent()
        #if pivotIndicatorParent:
            #pivotIndicatorParent = str(pivotIndicatorParent)
        #else:
            #pivotIndicatorParent = ''


        insertionMatrix = str( pymel.xform(insertionNull, query=True, ws=True, m=True) )
        originMatrix = str( pymel.xform(originNull, query=True, ws=True, m=True) )
        #pivotIndicatorMatrix = str( pymel.xform(pivotIndicatorZro, query=True, ws=True, m=True) )
        pivotPositionMatrix = str( pymel.xform(pivotIndicator, query=True, ws=True, m=True) )


        muscleOriginInbetweenJoints = []
        muscleInsertionInbetweenJoints = []

        newListOfJointLists = []
        listOfJointLists = getBendyJoints(pivotIndicator)

        for list in listOfJointLists:

            newList = []
            for joint in list:
                newList.append( joint.constraintPercent.get() )

            newListOfJointLists.append(newList)


        jointPercents = str(newListOfJointLists)

        numberOfJoints = '['+str(len(newListOfJointLists[0]))+','+str(len(newListOfJointLists[1]))+']'


#        insertionMatrix = str(muscleJoint.worldMatrix.get())
#        originMatrix = str(muscleJoint.worldMatrix.get())

        #print 'userMethods.procedurallyCreateBendMuscle(baseName="'+baseName+'", numberOfJoints='+numberOfJoints+', radius='+radius+', insertionParent="'+insertionParent+'", originParent="'+originParent+'", pivotIndicatorZroParent="'+pivotIndicatorParent+'", insertionMatrix='+insertionMatrix+', originMatrix='+originMatrix+', pivotIndicatorZroMatrix='+pivotIndicatorMatrix+', pivotPositionMatrix='+pivotPositionMatrix+', jointPercents='+str(jointPercents)+')'
        print 'userMethods.procedurallyCreateBendMuscle(baseName="'+baseName+'", numberOfJoints='+numberOfJoints+', radius='+radius+', insertionParent="'+insertionParent+'", originParent="'+originParent+'", pivotIndicatorZroParent="'+pivotIndicatorParent+'", insertionMatrix='+insertionMatrix+', originMatrix='+originMatrix+', pivotPositionMatrix='+pivotPositionMatrix+', jointPercents='+str(jointPercents)+')'



#def printCommand_procedurallyCreateBendMuscleJoint():
    #allBendMuscleJoints = getAllBendMuscleJoints()

    #for pivotIndicator in allBendMuscleJoints:
        #pivotIndicatorZro = pymel.listRelatives(pivotIndicator, parent=True)[0]

        #baseName = pivotIndicator.nodeName()
        #baseName = baseName.replace('_pivotPosition', '', 1)

        #radius = str(pivotIndicator.radius.get())

        #insertionNull = pivotIndicator.insertion.inputs()[0]
        #originNull = pivotIndicator.origin.inputs()[0]

        #insertionParent = insertionNull.getParent()
        #if insertionParent:
            #insertionParent = str(insertionParent)
        #else:
            #insertionParent = ''

        #originParent = originNull.getParent()
        #if originParent:
            #originParent = str(originParent)
        #else:
            #originParent = ''

        #pivotIndicatorParent = pivotIndicatorZro.getParent()
        #if pivotIndicatorParent:
            #pivotIndicatorParent = str(pivotIndicatorParent)
        #else:
            #pivotIndicatorParent = ''


        #insertionMatrix = str( pymel.xform(insertionNull, query=True, ws=True, m=True) )
        #originMatrix = str( pymel.xform(originNull, query=True, ws=True, m=True) )
        #pivotIndicatorMatrix = str( pymel.xform(pivotIndicatorZro, query=True, ws=True, m=True) )
        #pivotPositionMatrix = str( pymel.xform(pivotIndicator, query=True, ws=True, m=True) )


        #muscleOriginInbetweenJoints = []
        #muscleInsertionInbetweenJoints = []

        #newListOfJointLists = []
        #listOfJointLists = getBendyJoints(pivotIndicator)

        #for list in listOfJointLists:

            #newList = []
            #for joint in list:
                #newList.append( joint.constraintPercent.get() )

            #newListOfJointLists.append(newList)


        #jointPercents = str(newListOfJointLists)

        #numberOfJoints = '['+str(len(newListOfJointLists[0]))+','+str(len(newListOfJointLists[1]))+']'


##        insertionMatrix = str(muscleJoint.worldMatrix.get())
##        originMatrix = str(muscleJoint.worldMatrix.get())

        #print 'userMethods.procedurallyCreateBendMuscle(baseName="'+baseName+'", numberOfJoints='+numberOfJoints+', radius='+radius+', insertionParent="'+insertionParent+'", originParent="'+originParent+'", pivotIndicatorZroParent="'+pivotIndicatorParent+'", insertionMatrix='+insertionMatrix+', originMatrix='+originMatrix+', pivotIndicatorZroMatrix='+pivotIndicatorMatrix+', pivotPositionMatrix='+pivotPositionMatrix+', jointPercents='+str(jointPercents)+')'

##        print 'baseName:',baseName
##        print 'initialLength:',initialLength
##        print 'initialLength:',radius
##        print 'squashAndStretchStrength:',squashAndStretchStrength
##        print 'insertionParent:',insertionParent
##        print 'originParent:',originParent
##        print 'insertionMatrix:',insertionMatrix
##        print 'originMatrix:',originMatrix


def modifyBendMuscle(position, mode):
    '''
    position - tuple of 2 ints - first number is 0 or 1, indicating it is effecting the origin or insertion joints
    mode - string - either 'add' or 'delete' are appropriate flags
    '''
    selection = pymel.ls(selection=True)
    pivotIndicator = selection[0]
    if pymel.attributeQuery('rigType', node=pivotIndicator, exists=True):
        rigType = pivotIndicator.rigType.get()
        if rigType != 'muscleBendPivotPosition':
            pymel.error('selection must be a single pivotPosition of a bend muscle')
    else:
        pymel.error('selection must be a single pivotPosition of a bend muscle')

    pivotIndicatorChildren = pymel.listRelatives(pivotIndicator, shapes=False)

#    jointsGroup = None
    muscleOriginInbetweenLocators = []
    muscleInsertionInbetweenLocators = []
    muscleOriginInbetweenJoints = []
    muscleInsertionInbetweenJoints = []

    for child in pivotIndicatorChildren:
       if pymel.attributeQuery('rigType', node=child, exists=True):
           rigType = child.rigType.get()

#           if rigType == 'jointsGroup':
#               jointsGroup = child

           if rigType == 'muscleMidPointLocatorB':
               muscleMidPointLocatorB = child

           if rigType == 'muscleOriginInbetweenLocator':
               muscleOriginInbetweenLocators.append(child)

           if rigType == 'muscleInsertionInbetweenLocator':
               muscleInsertionInbetweenLocators.append(child)

           if rigType == 'muscleMidPointLocatorB':
               muscleMidPointLocatorB = child

           if 'muscleOriginInbetweenJoint' in baseName:
               muscleOriginInbetweenJoints.append(joint)

           if 'muscleInsertionInbetweenJoint' in baseName:
               muscleInsertionInbetweenJoints.append(joint)

#    muscleOriginInbetweenJoints = []
#    muscleInsertionInbetweenJoints = []
#    if jointsGroup:
#        joints = pymel.listRelatives(jointsGroup, shapes=False, type='joint')
#        if joints:
#            for joint in joints:
#                if pymel.attributeQuery('baseName', node=joint, exists=True):
#                    print 'chea!'
#                    baseName = joint.baseName.get()
#
#                    if 'muscleOriginInbetweenJoint' in baseName:
#                        muscleOriginInbetweenJoints.append(joint)
#
#                    if 'muscleInsertionInbetweenJoint' in baseName:
#                        muscleInsertionInbetweenJoints.append(joint)

    baseName = pivotIndicator.baseName.get()
    userDefinedName = pivotIndicator.nodeName()[0:(-1*(len(baseName)+1))]

    if position[0] == 0:
        numberOfOriginJoints = len(muscleOriginInbetweenJoints)
        muscleInbetweenJoints = muscleOriginInbetweenJoints
        muscleInbetweenLocators = muscleOriginInbetweenLocators
        type = 'origin'
        muscleEndLocator = pivotIndicator.origin.inputs()[0]

    elif position[0] == 1:
        numberOfOriginJoints = len(muscleInsertionInbetweenJoints)
        muscleInbetweenJoints = muscleInsertionInbetweenJoints
        muscleInbetweenLocators = muscleInsertionInbetweenLocators
        type = 'insertion'
        muscleEndLocator = pivotIndicator.insertion.inputs()[0]

    print 'muscleOriginInbetweenJoints: ',
    print muscleOriginInbetweenJoints
    print 'muscleInsertionInbetweenJoints: ',
    print muscleInsertionInbetweenJoints
    print 'userDefinedName: ',
    print userDefinedName
    print 'numberOfOriginJoints: ',
    print numberOfOriginJoints
    print 'pivotIndicator: ',
    print pivotIndicator
    print 'jointsGroup: ',
    print jointsGroup
    print 'muscleInbetweenJoints: ',
    print muscleInbetweenJoints
    print 'muscleEndLocator: ',
    print muscleEndLocator

    _addJointToBendOriginMuscle(type, userDefinedName, numberOfOriginJoints, pivotIndicator, muscleInbetweenJoints, muscleInbetweenLocators, muscleMidPointLocatorB, muscleEndLocator,)

    pymel.select(selection)

def _modifyBendMuscle(bendMuscle, position, mode):
    pass

def _addJointToBendOriginMuscle(type, name, numberOfInbetweenJoints, pivotIndicator, muscleInbetweenJointsA, muscleInbetweenLocatorsA, muscleMidPointLocatorB, muscleOriginLocator, jointPercents=[]):
    total = numberOfInbetweenJoints+2
    i = numberOfInbetweenJoints
    Type = type[0].upper() + type[1:] #uppercased first letter
#    muscleInbetweenLocatorsA = []
#    muscleInbetweenJointsA = []
#    for i in range(numberOfInbetweenJoints[0]):

    muscleInbetweenLocator = pymel.spaceLocator(name=name+'muscle'+Type+'InbetweenLocator'+str(chain_i))
    muscleInbetweenLocatorShape = pymel.listRelatives(muscleInbetweenLocator, shapes=True)[0]
    pymel.addAttr(muscleInbetweenLocator, longName='rigType', dataType='string', keyable=True)
    muscleInbetweenLocator.rigType.set('muscle'+Type+'InbetweenLocator', lock=True)
    muscleInbetweenLocatorShape.localScale.set([0.2,0.2,0.2])
    pymel.parent(muscleInbetweenLocator, pivotIndicator)
    muscleInbetweenLocator.visibility.set(0)

#    if not muscleInbetweenLocatorsA:
#        muscleInbetweenLocatorPointConstraint = pymel.pointConstraint(muscleOriginLocator, muscleMidPointLocatorB, muscleInbetweenLocator)
#        muscleInbetweenLocatorOrientConstraint = pymel.orientConstraint(muscleOriginLocator, muscleMidPointLocatorB, muscleInbetweenLocator)
#        muscleInbetweenLocatorOrientConstraint.interpType.set(2)
#    else:
    muscleInbetweenLocatorPointConstraint = pymel.pointConstraint(muscleOriginLocator, muscleInbetweenJointsA[-1], muscleInbetweenLocator)
    muscleInbetweenLocatorOrientConstraint = pymel.orientConstraint(muscleOriginLocator, muscleInbetweenLocatorsA[-1], muscleInbetweenLocator)
    muscleInbetweenLocatorOrientConstraint.interpType.set(2)

    muscleInbetweenLocatorPointConstraint.w0.set(1)
    muscleInbetweenLocatorPointConstraint.w1.set(total-2)

    muscleInbetweenLocatorOrientConstraint.w0.set(1)
    muscleInbetweenLocatorOrientConstraint.w1.set(total-2)

    muscleInbetweenLocatorsA.append(muscleInbetweenLocator)


    muscleInbetweenJoint = pymel.createNode('joint', name=name+'muscle'+Type+'InbetweenJoint'+str(i))
    muscleInbetweenJoint.radius.set(0.2)
    muscleInbetweenJoint.addAttr('constraintPercent', defaultValue=1.0/(total-1.0), keyable=True)
    muscleInbetweenJointsA.append(muscleInbetweenJoint)
    pymel.addAttr(muscleInbetweenJoint, longName='rigType', dataType='string', keyable=True)
    muscleInbetweenJoint.rigType.set('muscleBendJoint', lock=True)
    pymel.addAttr(muscleInbetweenJoint, longName='baseName', dataType='string', keyable=True)
    muscleInbetweenJoint.baseName.set('muscle'+Type+'InbetweenJoint'+str(i), lock=True)
    pymel.parent(muscleInbetweenJoint, jointsGroup)


    plusMinusAverage = pymel.createNode('plusMinusAverage', name=name+'muscle'+Type+'InbetweenJoint'+str(i)+'_plusMinusAverage')
    plusMinusAverage.input1D[0].set(1)
    plusMinusAverage.operation.set(2)
    muscleInbetweenJoint.constraintPercent >> plusMinusAverage.input1D[1]

    muscleInbetweenJoint.constraintPercent >> muscleInbetweenLocatorPointConstraint.w0
    plusMinusAverage.output1D >> muscleInbetweenLocatorPointConstraint.w1

    muscleInbetweenJoint.constraintPercent >> muscleInbetweenLocatorOrientConstraint.w0
    plusMinusAverage.output1D >> muscleInbetweenLocatorOrientConstraint.w1

    muscleOriginInbetweenJoint_vectorProductA = pymel.createNode('vectorProduct', name=name+'muscle'+Type+'InbetweenJoint'+str(i)+'_vectorProductA')
    muscleInbetweenLocator.translate >> muscleOriginInbetweenJoint_vectorProductA.input1
    muscleInbetweenLocator.translate >> muscleOriginInbetweenJoint_vectorProductA.input2

    muscleOriginInbetweenJoint_vectorProductB = pymel.createNode('vectorProduct', name=name+'muscle'+Type+'InbetweenJoint'+str(i)+'_vectorProductB')
    muscleInbetweenLocator.translate >> muscleOriginInbetweenJoint_vectorProductB.input1
    muscleInbetweenLocator.translate >> muscleOriginInbetweenJoint_vectorProductB.input2
    muscleOriginInbetweenJoint_vectorProductB.normalizeOutput.set(1)
    muscleOriginInbetweenJoint_vectorProductB.operation.set(3)

    condition = pymel.createNode('condition', name=name+'muscle'+Type+'InbetweenJoint'+str(i)+'_condition')
    muscleOriginInbetweenJoint_vectorProductA.outputX >> condition.firstTerm
    condition.operation.set(2)
    condition.secondTerm.set(1)
    muscleInbetweenLocator.translate >> condition.colorIfTrue
    muscleOriginInbetweenJoint_vectorProductB.output >> condition.colorIfFalse
    condition.outColor >> muscleInbetweenJoint.translate

    total -= 1

    jointBefore = muscleInbetweenJointsA[-1]
    jointAfter = muscleInbetweenJointsA[0]

    aimConstraint = pymel.listRelatives(jointAfter, type='aimConstraint')[0]
    muscleUpVector_vectorProductC = aimConstraint.worldUpVectorY.inputs()[0]
    muscleUpVector_animCurveUU = aimConstraint.worldUpVectorZ.inputs()[0]
#    muscleUpVector_vectorProductC.outputX >> aimConstraint.worldUpVectorY
#    muscleUpVector_vectorProductC.outputX >> aimConstraint.upVectorY
#    muscleUpVector_animCurveUU.output >> aimConstraint.worldUpVectorZ
#    muscleUpVector_animCurveUU.output >> aimConstraint.upVectorZ

    if type == 'origin':
        aimVector = [1,0,0]
    else:
        aimVector = [-1,0,0]
    aimConstraint = pymel.aimConstraint(jointAfter, muscleInbetweenJoint, worldUpType='objectrotation', worldUpObject=muscleInbetweenLocator, aimVector=aimVector, worldUpVector=[0,0,1], upVector=[0,0,1])
    muscleUpVector_vectorProductC.outputX >> aimConstraint.worldUpVectorY
    muscleUpVector_vectorProductC.outputX >> aimConstraint.upVectorY
    muscleUpVector_animCurveUU.output >> aimConstraint.worldUpVectorZ
    muscleUpVector_animCurveUU.output >> aimConstraint.upVectorZ

#    for i, joint in enumerate(muscleInbetweenJointsA):
#        if joint == muscleInbetweenJointsA[0]:
#            pymel.aimConstraint(muscleMidPointLocatorB, joint, worldUpType='objectrotation', worldUpObject=muscleInbetweenLocatorsA[i], aimVector=[1,0,0], worldUpVector=[0,0,1], upVector=[0,0,1])
#        else:
#            pymel.aimConstraint(muscleInbetweenJointsA[i-1], joint, worldUpType='objectrotation', worldUpObject=muscleInbetweenLocatorsA[i], aimVector=[1,0,0], worldUpVector=[0,0,1], upVector=[0,0,1])

    colorAllMuscleJoints()

#----------------------------------------------------------------------
def globalizeConstraint(constraint):
    """replace constraint with a simplified version of itself that uses globalSpace"""

    if pymel.objectType(constraint) == 'orientConstraint':
        newConstraint = pymel.createNode('orientConstraint', name='local_'+constraint.nodeName())

        for i in range(constraint.target.get(size=True)):
            target = constraint.target[i].targetRotate.inputs()[0]
            target.worldMatrix[0] >> newConstraint.target[i].targetParentMatrix
            newConstraint.target[i].targetWeight.set(constraint.target[i].targetWeight.get())

        destination = constraint.constraintRotateX.outputs()
        if not destination:
            destination = constraint.constraintRotateY.outputs()
        if not destination:
            destination = constraint.constraintRotateZ.outputs()
        destination = destination[0]

        newConstraint.constraintRotate >> destination.rotate
        destination.parentInverseMatrix[0] >> newConstraint.constraintParentInverseMatrix
        destination.rotateOrder >> newConstraint.constraintRotateOrder
        pymel.delete(constraint)
        pymel.parent(newConstraint, destination)
        newConstraint.translate.set(0,0,0)
        newConstraint.rotate.set(0,0,0)

    return newConstraint




def localizeConstraint(constraint):
    '''replace constraint with a simplified version of itself that assumes all targets and destinations are in the same space'''

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


def _createBendMuscle(name='', radius=1, numberOfInbetweenJoints=[3,3]):

    if name:
        name = name+'_'

    # create pivotIndicatorZro control
    pivotIndicatorZro = pymel.circle(sweep=180, radius=1, name=name+'pivotPosition_zro')[0]
    pivotIndicatorZro.rotateZ.set(-90)
    pymel.delete(pivotIndicatorZro, constructionHistory=True)
    pymel.makeIdentity(pivotIndicatorZro, apply=True, rotate=True)
    pymel.addAttr(pivotIndicatorZro, longName='rigType', dataType='string', keyable=True)
    pivotIndicatorZro.rigType.set('muscleBendPivotPositionZro', lock=True)


    # create pivotIndicatorOri
    pivotIndicatorOri = pymel.group(world=True, empty=True, name=name+'pivotIndicatorOri')
    pymel.addAttr(pivotIndicatorOri, longName='rigType', dataType='string', keyable=True)
    pivotIndicatorOri.rigType.set('muscleBendPivotPositionOri', lock=True)
    pymel.parent(pivotIndicatorOri, pivotIndicatorZro)
    pivotIndicatorOri.translate.lock()
    pivotIndicatorOri.scale.lock()

    # create pivotIndicatorAimTarget control
    pivotIndicatorAimTargetShape = pymel.createNode('locator')
    pivotIndicatorAimTarget = pivotIndicatorAimTargetShape.getParent()
    pivotIndicatorAimTarget.rename(name+'pivotIndicatorAimTarget')
    pymel.addAttr(pivotIndicatorAimTarget, longName='rigType', dataType='string', keyable=True)
    pivotIndicatorAimTarget.rigType.set('muscleBendPivotPositionOri', lock=True)
    pymel.parent(pivotIndicatorAimTarget, pivotIndicatorOri)
    pivotIndicatorAimTarget.translate.set(0,1,0)
    pivotIndicatorAimTargetShape.localScale.set([0.2,0.5,0.2])
    pivotIndicatorAimTargetShape.visibility.set(0)
    pivotIndicatorAimTarget.translateZ.lock()

    # create shape of pivotIndicator
    pivotIndicator = pymel.circle(sweep=180, radius=1, name=name+'pivotPosition')[0]
    pivotIndicator.rotateZ.set(-90)
    pymel.makeIdentity(pivotIndicator, apply=True, rotate=True)
    pivotIndicator.rotateY.set(-90)
    pymel.makeIdentity(pivotIndicator, apply=True, rotate=True)
    pymel.delete(pivotIndicator, constructionHistory=True)
    pivotIndicator.translate.lock()

    pivotIndicatorShapeC = pymel.circle(sweep=360, radius=1,)[0]
    pivotIndicatorShapeC.rotateX.set(-90)
    pymel.makeIdentity(pivotIndicatorShapeC, apply=True, rotate=True)
    pymel.delete(pivotIndicatorShapeC, constructionHistory=True)
    shapeParent(pivotIndicatorShapeC, pivotIndicator)

    curveShape = pymel.curve( p=[(0.0, 0.0, 0.0), (0.0, 1.2, 0.0)], degree=1,)
    shapeParent(curveShape, pivotIndicator)
    pymel.parent(pivotIndicator, pivotIndicatorZro)

    pivotIndicatorShapes = pymel.listRelatives(pivotIndicator, shapes=True)
    for i, shape in enumerate(pivotIndicatorShapes):
        if i == 0:
            shape.rename(pivotIndicator.name()+'Shape')
        else:
            shape.rename(pivotIndicator.name()+'Shape'+str(i))

    pivotIndicator.addAttr('pullWeight', defaultValue=0, keyable=True, minValue=0)
    pivotIndicator.addAttr('radius', defaultValue=radius, keyable=True)
    pymel.addAttr(pivotIndicator, longName='rigType', dataType='string', keyable=True)
    pivotIndicator.rigType.set('muscleBendPivotPosition', lock=True)
    pymel.addAttr(pivotIndicator, longName='baseName', dataType='string', keyable=True)
    pivotIndicator.baseName.set('pivotPosition', lock=True)
    pymel.addAttr(pivotIndicator, longName='origin', attributeType='message', keyable=True)
    pymel.addAttr(pivotIndicator, longName='insertion', attributeType='message', keyable=True)

    jointsGroup = pivotIndicator

    pivotIndicatorOriCounterScale_multiplyDivide = pymel.createNode('multiplyDivide')
    pivotIndicatorAimTarget.rename(name+'pivotIndicatorOriCounterScale_multiplyDivide')
    pivotIndicatorOriCounterScale_multiplyDivide.input1.set(1.0, 1.0, 1.0,)

    pivotIndicator.s >> pivotIndicatorOriCounterScale_multiplyDivide.input2
    pivotIndicatorOriCounterScale_multiplyDivide.operation.set(2)



    # create muscleOriginLocator
    muscleOriginLocator = pymel.spaceLocator(name=name+'muscleOriginLocator')
    muscleOriginLocatorShape = pymel.listRelatives(muscleOriginLocator, shapes=True)[0]
    muscleOriginLocatorShape.localScale.set([0.2,0.5,0.2])
    muscleOriginLocator.translateX.set(-2)
    pymel.addAttr(muscleOriginLocator, longName='rigType', dataType='string', keyable=True)
    muscleOriginLocator.rigType.set('muscleBendOrigin', lock=True)
    muscleOriginLocator.message >> pivotIndicator.origin

    muscleOriginLocatorShdw = pymel.group(name=name+'muscleOriginLocatorShdw', empty=True, world=True)
    pymel.addAttr(muscleOriginLocatorShdw, longName='rigType', dataType='string', keyable=True)
    muscleOriginLocatorShdw.rigType.set('muscleBendOriginShdw', lock=True)
    pymel.parent(muscleOriginLocatorShdw, pivotIndicator)
    pointConstraint = pymel.pointConstraint(muscleOriginLocator, muscleOriginLocatorShdw)
    orientConstraint = pymel.orientConstraint(muscleOriginLocator, muscleOriginLocatorShdw,)


    # create muscleInsertLocator
    muscleInsertLocator = pymel.spaceLocator(name=name+'muscleInsertLocator')
    muscleInsertLocatorShape = pymel.listRelatives(muscleInsertLocator, shapes=True)[0]
    muscleInsertLocatorShape.localScale.set([0.2,0.5,0.2])
    muscleInsertLocator.translateX.set(2)
    pymel.addAttr(muscleInsertLocator, longName='rigType', dataType='string', keyable=True)
    muscleInsertLocator.rigType.set('muscleBendInsertion', lock=True)
    muscleInsertLocator.message >> pivotIndicator.insertion

    muscleInsertLocatorShdw = pymel.group(name=name+'muscleInsertLocatorShdw', empty=True, world=True)
    pymel.addAttr(muscleInsertLocatorShdw, longName='rigType', dataType='string', keyable=True)
    muscleInsertLocatorShdw.rigType.set('muscleInsertLocatorShdw', lock=True)
    pymel.parent(muscleInsertLocatorShdw, pivotIndicator)
    pointConstraint = pymel.pointConstraint(muscleInsertLocator, muscleInsertLocatorShdw)
    orientConstraint = pymel.orientConstraint(muscleInsertLocator, muscleInsertLocatorShdw,)


    # constrain pivotIndicatorAimTarget between origin and insertion locators
    pointConstraint = pymel.pointConstraint(muscleOriginLocator, muscleInsertLocator, pivotIndicatorAimTarget, skip=['z',])
    pivotIndicatorAimTargetPointConstraint = pointConstraint
    yInput = pivotIndicatorAimTarget.translateY.inputs()[0]
    condition = pymel.createNode('condition')
    pointConstraint.constraintTranslateY >> condition.firstTerm
    pointConstraint.constraintTranslateY >> condition.colorIfTrueR
    condition.outColorR >> pivotIndicatorAimTarget.translateY
    condition.secondTerm.set(1)
    condition.colorIfFalseR.set(1)
    condition.operation.set(2)

    orientConstraint = pymel.orientConstraint(muscleOriginLocator, muscleInsertLocator, pivotIndicatorOri)
    orientConstraint = globalizeConstraint(orientConstraint)
    orientConstraint.interpType.set(2)
    aimConstraint = pymel.aimConstraint(pivotIndicatorAimTarget, pivotIndicator, worldUpType='objectrotation', worldUpObject=pivotIndicatorOri, aimVector=[0,1,0], worldUpVector=[0,0,1], upVector=[0,0,1])


    # create mid point locators
    muscleMidPointLocator = pymel.spaceLocator(name=name+'muscleMidPointLocator')
    muscleMidPointLocatorShape = pymel.listRelatives(muscleMidPointLocator, shapes=True)[0]
    muscleMidPointLocatorShape.localScale.set([0.2,0.2,0.2])
    pymel.parent(muscleMidPointLocator, pivotIndicator)
    pymel.addAttr(muscleMidPointLocator, longName='rigType', dataType='string', keyable=True)
    muscleMidPointLocator.rigType.set('muscleMidPointLocator', lock=True)
    muscleMidPointLocator_blendPosition = pymel.createNode('blendColors', name=name+'muscleMidPointLocator_blendPosition')
    muscleMidPointLocator_blendPosition.blender.set(0.5)
    muscleOriginLocatorShdw.translateY >> muscleMidPointLocator_blendPosition.color1G
    muscleInsertLocatorShdw.translateY >> muscleMidPointLocator_blendPosition.color2G
    muscleMidPointLocator.visibility.set(0)

    blendColor = pymel.createNode('blendColors', name=name+'muscleMidPointLocator')
    pivotIndicator.pullWeight >> blendColor.blender
    muscleMidPointLocator_blendPosition.outputG >> blendColor.color2G
    blendColor.color1.set(0,1,0)
    blendColor.outputG >> muscleMidPointLocator.translateY


    muscleMidPointLocatorB = pymel.spaceLocator(name=name+'muscleMidPointLocatorB')
    muscleMidPointLocatorBShape = pymel.listRelatives(muscleMidPointLocatorB, shapes=True)[0]
    muscleMidPointLocatorBShape.localScale.set([0.2,0.2,0.2])
    pymel.parent(muscleMidPointLocatorB, pivotIndicator)
    pymel.addAttr(muscleMidPointLocatorB, longName='rigType', dataType='string', keyable=True)
    muscleMidPointLocatorB.rigType.set('muscleMidPointLocatorB', lock=True)
    muscleMidPointLocatorB.visibility.set(0)

    muscleMidPointLocatorC = pymel.spaceLocator(name=name+'muscleMidPointLocatorC')
    muscleMidPointLocatorCShape = pymel.listRelatives(muscleMidPointLocatorC, shapes=True)[0]
    muscleMidPointLocatorCShape.localScale.set([0.2,0.2,0.2])
    pymel.parent(muscleMidPointLocatorC, pivotIndicator)
    pymel.addAttr(muscleMidPointLocatorC, longName='rigType', dataType='string', keyable=True)
    muscleMidPointLocatorC.rigType.set('muscleMidPointLocatorC', lock=True)
    muscleMidPointLocatorC.visibility.set(0)
    condition = pymel.createNode('condition', name=name+'midPointCollide_condition')
    muscleMidPointLocator.translateY >> condition.firstTerm
    condition.secondTerm.set(1)
    condition.operation.set(2)
    muscleMidPointLocator.translateY >> condition.colorIfTrueG
    condition.colorIfFalseR.set(0)
    condition.colorIfFalseB.set(0)
    condition.outColor >> muscleMidPointLocatorB.translate




    vectorProductA = pymel.createNode('vectorProduct', name=name+'vectorProductA')

    vectorProductB = pymel.createNode('vectorProduct', name=name+'vectorProductB')
    muscleMidPointLocatorC.translate >> vectorProductB.input1
    muscleMidPointLocatorC.translate >> vectorProductB.input2

    vectorProductC = pymel.createNode('vectorProduct', name=name+'vectorProductC')
    muscleMidPointLocatorC.translate >> vectorProductC.input1
    vectorProductC.normalizeOutput.set(1)
    vectorProductC.operation.set(3)



    joints = []

    muscleOriginJoint = pymel.createNode('joint', name=name+'muscleOriginJoint')
    muscleOriginJoint.radius.set(0.2)
    muscleOriginLocatorShdw.translate >> muscleOriginJoint.translate
    pymel.parent(muscleOriginJoint, jointsGroup)
    pymel.addAttr(muscleOriginJoint, longName='rigType', dataType='string', keyable=True)
    muscleOriginJoint.rigType.set('muscleBendJoint', lock=True)
    pymel.addAttr(muscleOriginJoint, longName='indexNum', dataType='string', keyable=True)
    muscleOriginJoint.indexNum.set(str(0), lock=True)

    muscleMidPointJoint = pymel.createNode('joint', name=name+'muscleMidPointJoint')
    muscleMidPointJoint.radius.set(0.2)
    muscleMidPointJoint.addAttr('constraintPercent', defaultValue=0.5, keyable=True, maxValue=1, minValue=0)
    pymel.parent(muscleMidPointJoint, jointsGroup)
    pymel.addAttr(muscleMidPointJoint, longName='rigType', dataType='string', keyable=True)
    muscleMidPointJoint.rigType.set('muscleBendJoint', lock=True)
    pymel.addAttr(muscleMidPointJoint, longName='baseName', dataType='string', keyable=True)
    muscleMidPointJoint.baseName.set('muscleMidPointJoint', lock=True)

    #hook up the percent blend of the mid joint to the point constraint of the pivotIndicatorAimTarget
    plusMinusAverage = pymel.createNode('plusMinusAverage')
    plusMinusAverage.input1D[0].set(1)
    plusMinusAverage.operation.set(2)
    muscleMidPointJoint.constraintPercent >> plusMinusAverage.input1D[1]
    muscleMidPointJoint.constraintPercent >> pivotIndicatorAimTargetPointConstraint.w0
    plusMinusAverage.output1D >> pivotIndicatorAimTargetPointConstraint.w1
    muscleMidPointJoint.constraintPercent >> muscleMidPointLocator_blendPosition.blender
    pivotIndicatorOriCounterScale_multiplyDivide.output >> muscleMidPointJoint.s

    muscleInsertJoint = pymel.createNode('joint', name=name+'muscleInsertJoint')
    muscleInsertJoint.radius.set(0.2)
    muscleInsertLocatorShdw.translate >> muscleInsertJoint.translate
    pymel.parent(muscleInsertJoint, jointsGroup)
    pymel.addAttr(muscleInsertJoint, longName='rigType', dataType='string', keyable=True)
    muscleInsertJoint.rigType.set('muscleBendJoint', lock=True)
    pymel.addAttr(muscleInsertJoint, longName='indexNum', dataType='string', keyable=True)
    muscleInsertJoint.indexNum.set(str(numberOfInbetweenJoints[0]+numberOfInbetweenJoints[1]+2), lock=True)

    conditionB = pymel.createNode('condition', name=name+'midPointCollide_conditionB')
    vectorProductB.outputX >> conditionB.firstTerm
    conditionB.secondTerm.set(1)
    conditionB.operation.set(2)
    muscleMidPointLocatorC.translate >> conditionB.colorIfTrue
    vectorProductC.output >> conditionB.colorIfFalse
    conditionB.outColor >> muscleMidPointJoint.translate


    total = numberOfInbetweenJoints[0]+2
    muscleInbetweenLocatorsA = []
    muscleInbetweenJointsA = []
    for i in range(numberOfInbetweenJoints[0]):
        muscleInbetweenLocator = pymel.spaceLocator(name=name+'muscleOriginInbetweenLocator'+str(i))
        muscleInbetweenLocatorShape = pymel.listRelatives(muscleInbetweenLocator, shapes=True)[0]
        muscleInbetweenLocatorShape.localScale.set([0.2,0.2,0.2])
        pymel.addAttr(muscleInbetweenLocator, longName='rigType', dataType='string', keyable=True)
        muscleInbetweenLocator.rigType.set('muscleOriginInbetweenLocator', lock=True)
        pymel.parent(muscleInbetweenLocator, pivotIndicator)
        muscleInbetweenLocatorShape.visibility.set(0)

        if not muscleInbetweenLocatorsA:
            muscleInbetweenJoint_blendPosition = pymel.createNode('blendColors', name=name+'muscleInbetweenJoint_blendPosition'+str(i))
            muscleOriginLocatorShdw.translate >> muscleInbetweenJoint_blendPosition.color1
            muscleMidPointLocatorB.translate >> muscleInbetweenJoint_blendPosition.color2


            muscleInbetweenLocatorOrientConstraint = pymel.orientConstraint(muscleOriginLocatorShdw, muscleMidPointLocatorB, muscleInbetweenLocator)
            muscleInbetweenLocatorOrientConstraint.interpType.set(2)
        else:
            muscleInbetweenJoint_blendPosition = pymel.createNode('blendColors', name=name+'muscleInbetweenJoint_blendPosition'+str(i))
            muscleOriginLocatorShdw.translate >> muscleInbetweenJoint_blendPosition.color1
            muscleInbetweenJointsA[-1].translate >> muscleInbetweenJoint_blendPosition.color2

            muscleInbetweenLocatorOrientConstraint = pymel.orientConstraint(muscleOriginLocatorShdw, muscleInbetweenLocatorsA[-1], muscleInbetweenLocator)
            muscleInbetweenLocatorOrientConstraint.interpType.set(2)

        muscleInbetweenJoint_blendPosition.output >> muscleInbetweenLocator.translate
        muscleInbetweenLocatorOrientConstraint = ka_constraints.localizeConstraint(muscleInbetweenLocatorOrientConstraint)
        muscleInbetweenLocatorOrientConstraint.interpType.set(2)

        muscleInbetweenLocatorOrientConstraint.target[0].targetWeight.set(1)
        muscleInbetweenLocatorOrientConstraint.target[0].targetWeight.set(total-2)

        muscleInbetweenLocatorsA.append(muscleInbetweenLocator)


        muscleInbetweenJoint = pymel.createNode('joint', name=name+'muscleOriginInbetweenJoint'+str(i))
        pymel.parent(muscleInbetweenJoint, jointsGroup)
        muscleInbetweenJoint.radius.set(0.2)
        muscleInbetweenJoint.addAttr('constraintPercent', defaultValue=1.0/(total-1.0), keyable=True, maxValue=1, minValue=0)
        muscleInbetweenJointsA.append(muscleInbetweenJoint)
        pymel.addAttr(muscleInbetweenJoint, longName='rigType', dataType='string', keyable=True)
        muscleInbetweenJoint.rigType.set('muscleBendJoint', lock=True)
        pymel.addAttr(muscleInbetweenJoint, longName='baseName', dataType='string', keyable=True)
        muscleInbetweenJoint.baseName.set('muscleOriginInbetweenJoint'+str(i), lock=True)


        plusMinusAverage = pymel.createNode('plusMinusAverage', name=name+'muscleOriginInbetweenJoint'+str(i)+'_plusMinusAverage')
        plusMinusAverage.input1D[0].set(1)
        plusMinusAverage.operation.set(2)
        muscleInbetweenJoint.constraintPercent >> plusMinusAverage.input1D[1]

        muscleInbetweenJoint.constraintPercent >> muscleInbetweenJoint_blendPosition.blender

        muscleInbetweenJoint.constraintPercent >> muscleInbetweenLocatorOrientConstraint.target[0].targetWeight
        plusMinusAverage.output1D >> muscleInbetweenLocatorOrientConstraint.target[1].targetWeight

        muscleOriginInbetweenJoint_vectorProductA = pymel.createNode('vectorProduct', name=name+'muscleOriginInbetweenJoint'+str(i)+'_vectorProductA')
        muscleInbetweenLocator.translate >> muscleOriginInbetweenJoint_vectorProductA.input1
        muscleInbetweenLocator.translate >> muscleOriginInbetweenJoint_vectorProductA.input2

        muscleOriginInbetweenJoint_vectorProductB = pymel.createNode('vectorProduct', name=name+'muscleOriginInbetweenJoint'+str(i)+'_vectorProductB')
        muscleInbetweenLocator.translate >> muscleOriginInbetweenJoint_vectorProductB.input1
        muscleInbetweenLocator.translate >> muscleOriginInbetweenJoint_vectorProductB.input2
        muscleOriginInbetweenJoint_vectorProductB.normalizeOutput.set(1)
        muscleOriginInbetweenJoint_vectorProductB.operation.set(3)

        condition = pymel.createNode('condition', name=name+'muscleOriginInbetweenJoint'+str(i)+'_condition')
        muscleOriginInbetweenJoint_vectorProductA.outputX >> condition.firstTerm
        condition.operation.set(2)
        condition.secondTerm.set(1)
        muscleInbetweenLocator.translate >> condition.colorIfTrue
        muscleOriginInbetweenJoint_vectorProductB.output >> condition.colorIfFalse
        condition.outColor >> muscleInbetweenJoint.translate
        pivotIndicatorOriCounterScale_multiplyDivide.output >> muscleInbetweenJoint.s
        total -= 1


    muscleUpVector_vectorProductC = pymel.createNode('vectorProduct', name=name+'muscleUpVector_vectorProductC')
    muscleUpVector_vectorProductC.operation.set(1)
    muscleUpVector_vectorProductC.normalizeOutput.set(1)
    muscleOriginLocatorShdw.translate >> muscleUpVector_vectorProductC.input1
    muscleUpVector_vectorProductC.input2.set(0,0,1)

    muscleUpVector_animCurveUU = pymel.createNode('animCurveUU', name=name+'muscleUpVector_plusMinusAverage')
    muscleUpVector_vectorProductC.outputX >> muscleUpVector_animCurveUU.input
    pymel.setKeyframe(muscleUpVector_animCurveUU, float=1, value=0, inTangentType='linear', outTangentType='linear',)
    pymel.setKeyframe(muscleUpVector_animCurveUU, float=0, value=1, inTangentType='linear', outTangentType='linear',)
    pymel.setKeyframe(muscleUpVector_animCurveUU, float=-1, value=0, inTangentType='linear', outTangentType='linear',)

    aimConstraint = pymel.aimConstraint(muscleInbetweenJointsA[-1], muscleOriginJoint, worldUpType='objectrotation', worldUpObject=muscleOriginLocatorShdw, aimVector=[1,0,0], worldUpVector=[0,0,1], upVector=[0,0,1])
    aimConstraint = ka_constraints.localizeConstraint(aimConstraint)
    muscleUpVector_vectorProductC.outputX >> aimConstraint.worldUpVectorY
    muscleUpVector_vectorProductC.outputX >> aimConstraint.upVectorY
    muscleUpVector_animCurveUU.output >> aimConstraint.worldUpVectorZ
    muscleUpVector_animCurveUU.output >> aimConstraint.upVectorZ
    for i, joint in enumerate(muscleInbetweenJointsA):
        if joint == muscleInbetweenJointsA[0]:
            aimConstraint = pymel.aimConstraint(muscleMidPointLocatorB, joint, worldUpType='objectrotation', worldUpObject=muscleInbetweenLocatorsA[i], aimVector=[1,0,0], worldUpVector=[0,0,1], upVector=[0,0,1])
        else:
            aimConstraint = pymel.aimConstraint(muscleInbetweenJointsA[i-1], joint, worldUpType='objectrotation', worldUpObject=muscleInbetweenLocatorsA[i], aimVector=[1,0,0], worldUpVector=[0,0,1], upVector=[0,0,1])

        aimConstraint = ka_constraints.localizeConstraint(aimConstraint)
        muscleUpVector_vectorProductC.outputX >> aimConstraint.worldUpVectorY
        muscleUpVector_vectorProductC.outputX >> aimConstraint.upVectorY
        muscleUpVector_animCurveUU.output >> aimConstraint.worldUpVectorZ
        muscleUpVector_animCurveUU.output >> aimConstraint.upVectorZ


    total = numberOfInbetweenJoints[1]+2
    muscleInbetweenLocatorsB = []
    muscleInbetweenJointsB = []
    for i in range(numberOfInbetweenJoints[1]):
        muscleInbetweenLocator = pymel.spaceLocator(name=name+'muscleInsertionInbetweenLocator'+str(i))
        muscleInbetweenLocatorShape = pymel.listRelatives(muscleInbetweenLocator, shapes=True)[0]
        muscleInbetweenLocatorShape.localScale.set([0.2,0.2,0.2])
        pymel.addAttr(muscleInbetweenLocator, longName='rigType', dataType='string', keyable=True)
        muscleInbetweenLocator.rigType.set('muscleInsertionInbetweenLocator', lock=True)
        pymel.parent(muscleInbetweenLocator, pivotIndicator)
        muscleInbetweenLocatorShape.visibility.set(0)

        if not muscleInbetweenLocatorsB:
            muscleInbetweenJoint_blendPosition = pymel.createNode('blendColors', name=name+'muscleInbetweenJoint_blendPosition'+str(i))
            muscleInsertLocatorShdw.translate >> muscleInbetweenJoint_blendPosition.color1
            muscleMidPointLocatorB.translate >> muscleInbetweenJoint_blendPosition.color2

            muscleInbetweenLocatorOrientConstraint = pymel.orientConstraint(muscleInsertLocatorShdw, muscleMidPointLocatorB, muscleInbetweenLocator)
            muscleInbetweenLocatorOrientConstraint.interpType.set(2)
        else:
            muscleInbetweenJoint_blendPosition = pymel.createNode('blendColors', name=name+'muscleInbetweenJoint_blendPosition'+str(i))
            muscleInsertLocatorShdw.translate >> muscleInbetweenJoint_blendPosition.color1
            muscleInbetweenJointsB[-1].translate >> muscleInbetweenJoint_blendPosition.color2

            muscleInbetweenLocatorOrientConstraint = pymel.orientConstraint(muscleInsertLocatorShdw, muscleInbetweenLocatorsB[-1], muscleInbetweenLocator)
            muscleInbetweenLocatorOrientConstraint.interpType.set(2)

        muscleInbetweenJoint_blendPosition.output >> muscleInbetweenLocator.translate
        muscleInbetweenLocatorOrientConstraint = ka_constraints.localizeConstraint(muscleInbetweenLocatorOrientConstraint)
        muscleInbetweenLocatorOrientConstraint.interpType.set(2)

        muscleInbetweenJoint = pymel.createNode('joint', name=name+'muscleInsertionInbetweenJoint'+str(i))
        pymel.parent(muscleInbetweenJoint, jointsGroup)
        muscleInbetweenJoint.radius.set(0.2)
        muscleInbetweenJoint.addAttr('constraintPercent', defaultValue=1.0/(total-1.0), keyable=True, maxValue=1, minValue=0)
        muscleInbetweenJointsB.append(muscleInbetweenJoint)
        pymel.addAttr(muscleInbetweenJoint, longName='rigType', dataType='string', keyable=True)
        muscleInbetweenJoint.rigType.set('muscleBendJoint', lock=True)
        pymel.addAttr(muscleInbetweenJoint, longName='baseName', dataType='string', keyable=True)
        muscleInbetweenJoint.baseName.set('muscleInsertionInbetweenJoint'+str(i), lock=True)
        muscleInbetweenLocatorsB.append(muscleInbetweenLocator)
        pymel.addAttr(muscleInbetweenJoint, longName='indexNum', dataType='string', keyable=True)
        muscleInbetweenJoint.indexNum.set(str(numberOfInbetweenJoints[0]+i+2), lock=True)

        plusMinusAverage = pymel.createNode('plusMinusAverage', name=name+'muscleInsertionInbetweenJoint'+str(i)+'_plusMinusAverage')
        plusMinusAverage.input1D[0].set(1)
        plusMinusAverage.operation.set(2)
        muscleInbetweenJoint.constraintPercent >> plusMinusAverage.input1D[1]

        muscleInbetweenJoint.constraintPercent >> muscleInbetweenJoint_blendPosition.blender

        muscleInbetweenJoint.constraintPercent >> muscleInbetweenLocatorOrientConstraint.target[0].targetWeight
        plusMinusAverage.output1D >> muscleInbetweenLocatorOrientConstraint.target[1].targetWeight

        muscleOriginInbetweenJoint_vectorProductA = pymel.createNode('vectorProduct', name=name+'muscleInsertionInbetweenJoint'+str(i)+'_vectorProductA')
        muscleInbetweenLocator.translate >> muscleOriginInbetweenJoint_vectorProductA.input1
        muscleInbetweenLocator.translate >> muscleOriginInbetweenJoint_vectorProductA.input2

        muscleOriginInbetweenJoint_vectorProductB = pymel.createNode('vectorProduct', name=name+'muscleInsertionInbetweenJoint'+str(i)+'_vectorProductB')
        muscleInbetweenLocator.translate >> muscleOriginInbetweenJoint_vectorProductB.input1
        muscleInbetweenLocator.translate >> muscleOriginInbetweenJoint_vectorProductB.input2
        muscleOriginInbetweenJoint_vectorProductB.normalizeOutput.set(1)
        muscleOriginInbetweenJoint_vectorProductB.operation.set(3)

        condition = pymel.createNode('condition', name=name+'muscleInsertionInbetweenJoint'+str(i)+'_condition')
        muscleOriginInbetweenJoint_vectorProductA.outputX >> condition.firstTerm
        condition.secondTerm.set(1)
        condition.operation.set(2)
        muscleInbetweenLocator.translate >> condition.colorIfTrue
        muscleOriginInbetweenJoint_vectorProductB.output >> condition.colorIfFalse
        condition.outColor >> muscleInbetweenJoint.translate
        pivotIndicatorOriCounterScale_multiplyDivide.output >> muscleInbetweenJoint.s

        total -= 1


    muscleUpVector_vectorProductC = pymel.createNode('vectorProduct', name=name+'muscleUpVector_vectorProductC')
    muscleUpVector_vectorProductC.operation.set(1)
    muscleUpVector_vectorProductC.normalizeOutput.set(1)
    muscleInsertLocatorShdw.translate >> muscleUpVector_vectorProductC.input1
    muscleUpVector_vectorProductC.input2.set(0,0,1)

    muscleUpVector_animCurveUU = pymel.createNode('animCurveUU', name=name+'muscleUpVector_plusMinusAverage')
    muscleUpVector_vectorProductC.outputX >> muscleUpVector_animCurveUU.input
    pymel.setKeyframe(muscleUpVector_animCurveUU, float=1, value=0, inTangentType='linear', outTangentType='linear',)
    pymel.setKeyframe(muscleUpVector_animCurveUU, float=0, value=1, inTangentType='linear', outTangentType='linear',)
    pymel.setKeyframe(muscleUpVector_animCurveUU, float=-1, value=0, inTangentType='linear', outTangentType='linear',)


    aimConstraint = pymel.aimConstraint(muscleInbetweenJointsB[-1], muscleInsertJoint, worldUpType='objectrotation', worldUpObject=muscleInsertLocatorShdw, aimVector=[-1,0,0], worldUpVector=[0,0,1], upVector=[0,0,1])
    aimConstraint = ka_constraints.localizeConstraint(aimConstraint)
    muscleUpVector_vectorProductC.outputX >> aimConstraint.worldUpVectorY
    muscleUpVector_vectorProductC.outputX >> aimConstraint.upVectorY
    muscleUpVector_animCurveUU.output >> aimConstraint.worldUpVectorZ
    muscleUpVector_animCurveUU.output >> aimConstraint.upVectorZ
    for i, joint in enumerate(muscleInbetweenJointsB):
        if joint == muscleInbetweenJointsB[0]:
            aimConstraint = pymel.aimConstraint(muscleMidPointLocatorB, joint, worldUpType='objectrotation', worldUpObject=muscleInbetweenLocatorsB[i], aimVector=[-1,0,0], worldUpVector=[0,0,1], upVector=[0,0,1])
        else:
            aimConstraint = pymel.aimConstraint(muscleInbetweenJointsB[i-1], joint, worldUpType='objectrotation', worldUpObject=muscleInbetweenLocatorsB[i], aimVector=[-1,0,0], worldUpVector=[0,0,1], upVector=[0,0,1])

        aimConstraint = ka_constraints.localizeConstraint(aimConstraint)
        muscleUpVector_vectorProductC.outputX >> aimConstraint.worldUpVectorY
        muscleUpVector_vectorProductC.outputX >> aimConstraint.upVectorY
        muscleUpVector_animCurveUU.output >> aimConstraint.worldUpVectorZ
        muscleUpVector_animCurveUU.output >> aimConstraint.upVectorZ

    muscleMidPointLocatorC_averagePosition = pymel.createNode('plusMinusAverage', name=name+'muscleMidPointLocatorC_averagePosition')
    muscleMidPointLocatorC_averagePosition.operation.set(3)
    muscleInbetweenJointsB[0].translate >> muscleMidPointLocatorC_averagePosition.input3D[0]
    muscleInbetweenJointsA[0].translate >> muscleMidPointLocatorC_averagePosition.input3D[1]
    muscleMidPointLocatorB.translate >> muscleMidPointLocatorC_averagePosition.input3D[2]
    muscleMidPointLocatorC_averagePosition.output3D >> muscleMidPointLocatorC.translate

    muscleMidPointJointC_orientConstraint = pymel.orientConstraint(muscleInbetweenJointsB[0], muscleInbetweenJointsA[0], muscleMidPointJoint)
    muscleMidPointJointC_orientConstraint = ka_constraints.localizeConstraint(muscleMidPointJointC_orientConstraint)
    muscleMidPointJointC_orientConstraint.interpType.set(2)

    pivotIndicator.radius >> pivotIndicatorZro.scaleX
    pivotIndicator.radius >> pivotIndicatorZro.scaleY
    pivotIndicator.radius >> pivotIndicatorZro.scaleZ

    colorAllMuscleJoints()
    return pivotIndicator

def muscleJoint():
    text=None
    result = cmds.promptDialog(
                    title='Name Muscle',
                    message='Enter a Base Name:',
                    button=['OK', 'Cancel'],
                    defaultButton='OK',
                    cancelButton='Cancel',
                    dismissString='Cancel')

    if result == 'OK':
        text = cmds.promptDialog(query=True, text=True)

        if text:
            _muscleJoint(name=text)
        else:
            _muscleJoint

def printCommand_procedurallyCreateMuscleJoint():
    allMuscleJoints = getAllMuscleJoints()
    for muscleJoint in allMuscleJoints:
        baseName = muscleJoint.nodeName()
        baseName = baseName.replace('_muscleJoint', '', 1)

        initialLength = str(muscleJoint.initialLength.get())
        radius = str(muscleJoint.radius.get())
        if pymel.attributeQuery('squashAndStretchStrength', node=muscleJoint, exists=True):
            squashAndStretchStrength = str(muscleJoint.squashAndStretchStrength.get())
        else: #attribute has been spelt wrong initially by kris (me)
            squashAndStretchStrength = str(muscleJoint.squashAndStrechStrength.get())

        insertionNull = muscleJoint.insertion.inputs()[0]
        originNull = muscleJoint.origin.inputs()[0]

        insertionParent = str(insertionNull.getParent())
        originParent = str(originNull.getParent())

        insertionMatrix = str( pymel.xform(insertionNull, query=True, ws=True, m=True) )
        originMatrix = str( pymel.xform(originNull, query=True, ws=True, m=True) )

#        insertionMatrix = str(muscleJoint.worldMatrix.get())
#        originMatrix = str(muscleJoint.worldMatrix.get())

        print 'userMethods.procedurallyCreateMuscleJoint("'+baseName+'", '+initialLength+', '+radius+', '+squashAndStretchStrength+', "'+insertionParent+'", "'+originParent+'", '+insertionMatrix+', '+originMatrix+')'

#        print 'baseName:',baseName
#        print 'initialLength:',initialLength
#        print 'initialLength:',radius
#        print 'squashAndStretchStrength:',squashAndStretchStrength
#        print 'insertionParent:',insertionParent
#        print 'originParent:',originParent
#        print 'insertionMatrix:',insertionMatrix
#        print 'originMatrix:',originMatrix

def procedurallyCreateMuscleJoint(baseName, initialLength, radius, squashAndStretchStrength, insertionParent, originParent, insertionMatrix, originMatrix):

    muscleJoint = _muscleJoint(name=baseName, initialLength=initialLength, radius=radius, squashAndStretchStrength=squashAndStretchStrength)
    insertionNull = muscleJoint.insertion.inputs()[0]
    originNull = muscleJoint.origin.inputs()[0]

    pymel.parent(originNull, originParent)
    pymel.parent(insertionNull, insertionParent)

    pymel.xform(originNull, ws=True, m=originMatrix)
    pymel.xform(insertionNull, ws=True, m=insertionMatrix)


def _muscleJoint(name='', initialLength=1.5, radius=0.4, squashAndStretchStrength=0):

    if name:
        name = name+'_'
    rootLocatorShape = pymel.createNode('locator',)
    rootLocator = pymel.listRelatives(rootLocatorShape, parent=True)[0]
    pymel.rename(rootLocator, name+'muscleOrigin')
    pymel.addAttr(rootLocator, longName='rigType', dataType='string', keyable=True)
    rootLocator.rigType.set('muscleOrigin')

    rootLocator.translateX.set(1)
    rootLocator.localScaleX.set(0.3)
    rootLocator.localScaleY.set(0.5)
    rootLocator.localScaleZ.set(0.3)

    endLocatorShape = pymel.createNode('locator',)
    endLocator = pymel.listRelatives(endLocatorShape, parent=True)[0]
    pymel.rename(endLocator, name+'muscleInsertion')
    pymel.addAttr(endLocator, longName='rigType', dataType='string', keyable=True)
    endLocator.rigType.set('muscleInsertion')

#    pymel.parent(endLocator, rootLocator)

    endLocator.translateX.set(3)
    endLocator.localScaleX.set(0.3)
    endLocator.localScaleY.set(0.5)
    endLocator.localScaleZ.set(0.3)


    midPositionGroup = pymel.group( empty=True, name=name+'muscleMidPoint')
    pymel.parent(midPositionGroup, rootLocator)
    pymel.pointConstraint(rootLocator, endLocator, midPositionGroup)

    muscleJoint = pymel.joint(name=name+'muscleJoint', position=(2, 0, 0))
    pymel.addAttr(muscleJoint, longName='initialLength', defaultValue=initialLength, minValue=0.001, keyable=True)
    pymel.addAttr(muscleJoint, longName='squashAndStretchStrength', defaultValue=squashAndStretchStrength, minValue=0., keyable=True)
    pymel.addAttr(muscleJoint, longName='rigType', dataType='string', keyable=True)
    pymel.addAttr(muscleJoint, longName='origin', attributeType='message', keyable=True)
    pymel.addAttr(muscleJoint, longName='insertion', attributeType='message', keyable=True)
    muscleJoint.rigType.set('muscleJoint')
    muscleJoint.rigType.lock()
    rootLocator.message >> muscleJoint.origin
    endLocator.message >> muscleJoint.insertion
    muscleJoint.radius.set(radius)
    muscleJoint.translateX.set(0)

    pymel.select(clear=True)

    muscleEnd = pymel.joint(name=name+'muscleInsertionJoint', position=(3, 0, 0))
    pymel.parent(muscleEnd, muscleJoint)
    muscleEnd.radius.set(radius*0.75)
    pymel.select(clear=True)
    pymel.addAttr(muscleEnd, longName='rigType', dataType='string', keyable=True)
    muscleEnd.rigType.set('muscleInsertionJoint')
    muscleEnd.rigType.lock()

    muscleStart = pymel.joint(name=name+'muscleOriginJoint', position=(1, 0, 0))
    pymel.parent(muscleStart, muscleJoint)
    muscleStart.radius.set(radius*0.75)
    pymel.select(clear=True)
    pymel.addAttr(muscleStart, longName='rigType', dataType='string', keyable=True)
    muscleStart.rigType.set('muscleOriginJoint')
    muscleEnd.rigType.lock()

    pymel.pointConstraint(rootLocator, endLocator, midPositionGroup)
    pymel.pointConstraint(rootLocator, muscleStart)
    pymel.pointConstraint(endLocator, muscleEnd)
    pymel.aimConstraint(rootLocator, midPositionGroup, worldUpObject=rootLocator, worldUpType='objectrotation', aimVector=[-1,0,0], upVector=[0,0,1], worldUpVector=[0,0,1])

    worldSpaceToLocalSpace_vectorProduct2 = pymel.createNode('vectorProduct', name=name+'worldSpaceToLocalSpace')
    worldSpaceToLocalSpace_vectorProduct2.operation.set(4)
    endLocatorShape.worldPosition >> worldSpaceToLocalSpace_vectorProduct2.input1
    midPositionGroup.worldInverseMatrix >> worldSpaceToLocalSpace_vectorProduct2.matrix

    scale_multiplyDivide = pymel.createNode('multiplyDivide', name=name+'scale_multiplyDivide')
    scale_multiplyDivide.operation.set(2)

    worldSpaceToLocalSpace_vectorProduct2.outputX >> scale_multiplyDivide.input1X
    worldSpaceToLocalSpace_vectorProduct2.outputX >> scale_multiplyDivide.input2Y
    muscleJoint.initialLength >> scale_multiplyDivide.input2X
    muscleJoint.initialLength >> scale_multiplyDivide.input1Y

    scaleFactor_blendColor = pymel.createNode('blendColors', name=name+'scale_blendColors')
    scaleFactor_blendColor.color2.set(1,1,1)

    scale_multiplyDivide.output >> scaleFactor_blendColor.color1

    muscleJoint.squashAndStretchStrength >> scaleFactor_blendColor.blender

    scaleFactor_blendColor.outputR >> muscleJoint.scaleX
    scaleFactor_blendColor.outputG >> muscleJoint.scaleY
    scaleFactor_blendColor.outputG >> muscleJoint.scaleZ

    pymel.select(rootLocator)

    colorAllMuscleJoints()

    return muscleJoint

def getRelatedMuscleJoint(input):
    muscleJoint = None
    if pymel.attributeQuery('rigType', node=input, exists=True):
        rigType = input.rigType.get()
        possibleMuscleJoint = None
        possibleBendMuscle = None

        if rigType == 'muscleJoint':
            muscleJoint = input
        elif rigType == 'muscleOriginJoint':
            possibleMuscleJoint = input.inverseScale.inputs()[0]
        elif rigType == 'muscleInsertionJoint':
            possibleMuscleJoint = input.inverseScale.inputs()[0]

        if rigType == 'muscleBendPivotPosition':
            muscleJoint = input

        elif rigType == 'muscleBendPivotPositionZro':
            for child in pymel.listRelatives(input, children=True):
                if pymel.attributeQuery('rigType', node=child, exists=True):
                    childRigType = child.rigType.get()
                    if childRigType == 'muscleBendPivotPosition':
                        muscleJoint = child

        elif rigType == 'muscleBendJoint':
            possibleBendMuscle = pymel.listRelatives(input, parent=True)[0]
            possibleBendMuscle = pymel.listRelatives(possibleBendMuscle, parent=True)[0]

        elif rigType == 'muscleBendOrigin':
            outputs = input.message.outputs()
            for each in outputs:
                if pymel.attributeQuery('rigType', node=each, exists=True):
                    eachRigType = each.rigType.get()
                    if rigType == 'muscleBendPivotPosition':
                        muscleJoint = input

        elif rigType == 'muscleBendInsertion':
            outputs = input.message.outputs()
            for each in outputs:
                if pymel.attributeQuery('rigType', node=each, exists=True):
                    eachRigType = each.rigType.get()
                    if rigType == 'muscleBendPivotPosition':
                        muscleJoint = input


        if possibleMuscleJoint:
            if pymel.attributeQuery('rigType', node=possibleMuscleJoint, exists=True):
                rigType = possibleMuscleJoint.rigType.get()
                if rigType == 'muscleJoint':
                    muscleJoint = possibleMuscleJoint

    return muscleJoint

def getRelatedBendMuscleJoint(input):
    muscleJoint = None
    if pymel.attributeQuery('rigType', node=input, exists=True):
        rigType = input.rigType.get()
        possibleMuscleJoint = None
        possibleBendMuscle = None

        if rigType == 'muscleBendPivotPosition':
            muscleJoint = input
        #elif rigType == 'muscleOriginJoint':
            #possibleMuscleJoint = input.inverseScale.inputs()[0]
        #elif rigType == 'muscleInsertionJoint':
            #possibleMuscleJoint = input.inverseScale.inputs()[0]

        #if rigType == 'muscleBendPivotPosition':
            #muscleJoint = input

        #elif rigType == 'muscleBendJoint':
            #possibleBendMuscle = pymel.listRelatives(input, parent=True)[0]
            #possibleBendMuscle = pymel.listRelatives(possibleBendMuscle, parent=True)[0]

        #elif rigType == 'muscleBendOrigin':
            #outputs = input.message.outputs()
            #for each in outputs:
                #if pymel.attributeQuery('rigType', node=each, exists=True):
                    #eachRigType = each.rigType.get()
                    #if rigType == 'muscleBendPivotPosition':
                        #muscleJoint = input

        #elif rigType == 'muscleBendInsertion':
            #outputs = input.message.outputs()
            #for each in outputs:
                #if pymel.attributeQuery('rigType', node=each, exists=True):
                    #eachRigType = each.rigType.get()
                    #if rigType == 'muscleBendPivotPosition':
                        #muscleJoint = input

        #if possibleMuscleJoint:
            #if pymel.attributeQuery('rigType', node=possibleMuscleJoint, exists=True):
                #rigType = possibleMuscleJoint.rigType.get()
                #if rigType == 'muscleJoint':
                    #muscleJoint = possibleMuscleJoint

    return muscleJoint

def getAllMuscleJoints():
    muscleJoints = []
    selection = pymel.ls(selection=True)
    joints = pymel.ls(type='joint')

    for joint in joints:
       if pymel.attributeQuery('rigType', node=joint, exists=True):
           rigType = joint.rigType.get()

           if rigType == 'muscleJoint':
               muscleJoints.append(joint)

    return muscleJoints

def getAllBendMuscleJoints():
    muscleBendJoints = []
    selection = pymel.ls(selection=True)
    curves = pymel.ls(type='nurbsCurve')

    for curve in curves:
        curve = pymel.listRelatives(curve, parent=True)[0]
        if pymel.attributeQuery('rigType', node=curve, exists=True):
           rigType = curve.rigType.get()
           if rigType == 'muscleBendPivotPosition':
               if curve not in muscleBendJoints:
                   muscleBendJoints.append(curve)

    return muscleBendJoints

def getAllMuscleSkinningJoints():
    muscleJoints = []
    selection = pymel.ls(selection=True)
    joints = pymel.ls(type='joint')

    for joint in joints:
       if pymel.attributeQuery('rigType', node=joint, exists=True):
           rigType = joint.rigType.get()
           if rigType == 'muscleJoint':
               muscleJoints.append(joint)
           elif rigType == 'muscleOriginJoint':
               muscleJoints.append(joint)
           elif rigType == 'muscleInsertionJoint':
               muscleJoints.append(joint)
           elif rigType == 'muscleBendJoint':
               muscleJoints.append(joint)

    return muscleJoints

def selectAllMuscleJoints():
    pymel.select(getAllMuscleSkinningJoints() )

def colorAllMuscleJoints():
    muscleJoints = []
    selection = pymel.ls(selection=True)
    joints = pymel.ls(type='joint')
    curves = pymel.ls(type='nurbsCurve')
    curves.extend(pymel.ls(type='locator'))

    for joint in joints:
       if pymel.attributeQuery('rigType', node=joint, exists=True):
           rigType = joint.rigType.get()

           if rigType == 'muscleBendJoint':
               joint.overrideEnabled.set(1)
               joint.overrideColor.set(29)

               if pymel.attributeQuery('baseName', node=joint, exists=True):
                   baseName = joint.baseName.get()
                   if baseName == 'muscleMidPointJoint':
                       joint.overrideEnabled.set(1)
                       joint.overrideColor.set(15)

           elif rigType == 'muscleOriginJoint':
               joint.overrideEnabled.set(1)
               joint.overrideColor.set(20)

           elif rigType in ['muscleJoint','muscleInsertionJoint']:
               joint.overrideEnabled.set(1)
               joint.overrideColor.set(4)



    for curve in curves:
        curve = pymel.listRelatives(curve, parent=True)[0]
        if pymel.attributeQuery('rigType', node=curve, exists=True):
           rigType = curve.rigType.get()
           if rigType in ['muscleBendPivotPosition','muscleBendOrigin','muscleBendInsertion','muscleInsertion','muscleOrigin']:
               curve.overrideEnabled.set(1)
               curve.overrideColor.set(22)

           elif rigType in ['muscleBendPivotPositionZro',]:
               curve.overrideEnabled.set(1)
               curve.overrideColor.set(26)


    return muscleJoints


def getMirroredObject(object):

        newName = None
        currentName = object.nodeName()
        if currentName[0:2] == 'r_':
            newName = 'l_'+ currentName[2:]
        elif currentName[0:2] == 'l_':
            newName = 'r_'+ currentName[2:]
        elif currentName[0:2] == 'R_':
            nameName = 'L_'+ currentName[2:]
        elif currentName[0:2] == 'L_':
            newName = 'R_'+ currentName[2:]

        elif '_r_' in currentName:
            newName = currentName.replace('_r_', '_l_', 1)
        elif '_l_' in currentName:
            newName = currentName.replace('_l_', '_r_', 1)
        elif '_R_' in currentName:
            newName = currentName.replace('R_', '_L_', 1)
        elif '_L_' in currentName:
            newName = currentName.replace('_L_', '_R_', 1)

        else:
            newName = currentName

        if pymel.objExists(newName):
            newObject = pymel.ls(newName)[0]
            return newObject


def mirrorMuscleJoint():
    selection = pymel.ls(selection=True)
    selectedMuscleJoints = [getRelatedMuscleJoint(each) for each in selection]
    fails = 0
    failStrings = []

    for originalMuscleJoint in selectedMuscleJoints:

#        try:
        newName = None
        currentName = originalMuscleJoint.nodeName()

        if currentName[0:2] == 'r_':
            newName = 'l_'+ currentName[2:]
        elif currentName[0:2] == 'l_':
            newName = 'r_'+ currentName[2:]
        elif currentName[0:2] == 'R_':
            nameName = 'L_'+ currentName[2:]
        elif currentName[0:2] == 'L_':
            newName = 'R_'+ currentName[2:]
        else:
            failStrings.append('%s naming prefix does not indicate side, So mirroring was skipped' % (str(originalMuscleJoint)))

        if newName:
           if pymel.attributeQuery('rigType', node=originalMuscleJoint, exists=True):
               rigType = originalMuscleJoint.rigType.get()

               if rigType == 'muscleJoint':
                   newbaseName = newName.split('_muscleJoint')[0]
                   initialLength = originalMuscleJoint.initialLength.get()
                   radius = originalMuscleJoint.radius.get()
                #            squashAndStretchStrength = originalMuscleJoint.squashAndStretchStrength.get()
                   if pymel.attributeQuery('squashAndStretchStrength', node=originalMuscleJoint, exists=True):
                       squashAndStretchStrength = originalMuscleJoint.squashAndStretchStrength.get()
                   else: #attribute has been spelt wrong initially by kris (me)
                       squashAndStretchStrength = originalMuscleJoint.squashAndStrechStrength.get()

                   mirroredJoint = _muscleJoint(name=newbaseName, initialLength=1.5, radius=0.4, squashAndStretchStrength=0)

                   originalMuscleOrigin = originalMuscleJoint.origin.inputs()[0]
                   originalMuscleOriginParent = pymel.listRelatives(originalMuscleOrigin, parent=True)[0]
                   originalMuscleInsertion = originalMuscleJoint.insertion.inputs()[0]
                   originalMuscleInsertionParent = pymel.listRelatives(originalMuscleInsertion, parent=True)[0]

                   newMuscleOrigin = mirroredJoint.origin.inputs()[0]
                   newMuscleOriginParent = getMirroredObject(originalMuscleOriginParent)
                   pymel.parent(newMuscleOrigin, newMuscleOriginParent)

                   newMuscleInsertion = mirroredJoint.insertion.inputs()[0]
                   newMuscleInsertionParent = getMirroredObject(originalMuscleInsertionParent)
                   pymel.parent(newMuscleInsertion, newMuscleInsertionParent)

                   snapMirrored(snapTarget=originalMuscleOrigin, snapObjects=[newMuscleOrigin])
                   snapMirrored(snapTarget=originalMuscleInsertion, snapObjects=[newMuscleInsertion])

               elif rigType == 'muscleBendPivotPosition':
                   newbaseName = newName.split('_pivotPosition')[0]
                   radius = originalMuscleJoint.radius.get()

                   newListOfJointLists = []
                   listOfJointLists = getBendyJoints(originalMuscleJoint)

                   for list in listOfJointLists:

                       newList = []
                       for joint in list:
                           newList.append( joint.constraintPercent.get() )

                       newListOfJointLists.append(newList)


                   jointPercents = newListOfJointLists

                   numberOfJoints = [len(newListOfJointLists[0]), len(newListOfJointLists[1])]


                   originalMuscleOrigin = originalMuscleJoint.origin.inputs()[0]
                   originalMuscleOriginParent = pymel.listRelatives(originalMuscleOrigin, parent=True)[0]
                   originalMuscleInsertion = originalMuscleJoint.insertion.inputs()[0]
                   originalMuscleInsertionParent = pymel.listRelatives(originalMuscleInsertion, parent=True)[0]
                   originalPivotPosition = originalMuscleJoint
                   originalPivotPositionZro = pymel.listRelatives(originalPivotPosition, parent=True)[0]
                   originalPivotPositionZroParent = pymel.listRelatives(originalPivotPositionZro, parent=True)[0]

                   #mirroredJoint = procedurallyCreateBendMuscle(baseName=newbaseName, radius=radius, jointPercents=jointPercents)
                   mirroredJoint = procedurallyCreateBendMuscle(baseName=newbaseName, numberOfJoints=numberOfJoints, radius=radius, insertionParent=None, originParent=None, pivotIndicatorZroParent=None, insertionMatrix=[], originMatrix=[], pivotIndicatorZroMatrix=[], jointPercents=jointPercents)



                   newMuscleOrigin = mirroredJoint.origin.inputs()[0]
                   newMuscleOriginParent = getMirroredObject(originalMuscleOriginParent)
                   pymel.parent(newMuscleOrigin, newMuscleOriginParent)

                   newMuscleInsertion = mirroredJoint.insertion.inputs()[0]
                   newMuscleInsertionParent = getMirroredObject(originalMuscleInsertionParent)
                   pymel.parent(newMuscleInsertion, newMuscleInsertionParent)

                   newPivotPosition = mirroredJoint
                   newPivotPositionZro = pymel.listRelatives(newPivotPosition, parent=True)[0]
                   newPivotPositionZroParent = getMirroredObject(originalPivotPositionZroParent)
                   pymel.parent(newPivotPositionZro, newPivotPositionZroParent)


                   snapMirrored(snapTarget=originalMuscleOrigin, snapObjects=[newMuscleOrigin])
                   snapMirrored(snapTarget=originalMuscleInsertion, snapObjects=[newMuscleInsertion])
                   snapMirrored(snapTarget=originalPivotPositionZro, snapObjects=[newPivotPositionZro])

                   pymel.xform(newMuscleOrigin, rotation=[0,180,0], relative=True, objectSpace=True)
                   pymel.xform(newMuscleInsertion, rotation=[0,180,0], relative=True, objectSpace=True)
                   pymel.xform(newPivotPositionZro, rotation=[0,180,0], relative=True, objectSpace=True)


#
#    print '\n\n'
#    print '% s out of %s mirrored successfully ' % (str(len(selectedMuscleJoints)-fails), str(len(selectedMuscleJoints)))
#    for failString in failStrings:
#        print failString
def mirrorBendMuscleJoint():
    selection = pymel.ls(selection=True)
    selectedMuscleJoints = [getRelatedBendMuscleJoint(each) for each in selection]
    fails = 0
    failStrings = []

    for originalMuscleJoint in selectedMuscleJoints:

#        try:
        newName = None
        currentName = originalMuscleJoint.nodeName()

        if currentName[0:2] == 'r_':
            newName = 'l_'+ currentName[2:]
        elif currentName[0:2] == 'l_':
            newName = 'r_'+ currentName[2:]
        elif currentName[0:2] == 'R_':
            nameName = 'L_'+ currentName[2:]
        elif currentName[0:2] == 'L_':
            newName = 'R_'+ currentName[2:]
        else:
            failStrings.append('%s naming prefix does not indicate side, So mirroring was skipped' % (str(originalMuscleJoint)))

        if newName:
            if pymel.attributeQuery('rigType', node=originalMuscleJoint, exists=True):
                rigType = originalMuscleJoint.rigType.get()

               #if rigType == 'muscleJoint':
                   #newbaseName = newName.split('_muscleJoint')[0]
                   #initialLength = originalMuscleJoint.initialLength.get()
                   #radius = originalMuscleJoint.radius.get()
                ##            squashAndStretchStrength = originalMuscleJoint.squashAndStretchStrength.get()
                   #if pymel.attributeQuery('squashAndStretchStrength', node=originalMuscleJoint, exists=True):
                       #squashAndStretchStrength = originalMuscleJoint.squashAndStretchStrength.get()
                   #else: #attribute has been spelt wrong initially by kris (me)
                       #squashAndStretchStrength = originalMuscleJoint.squashAndStrechStrength.get()
                       #mirroredJoint = _muscleJoint(name=newbaseName, initialLength=1.5, radius=0.4, squashAndStretchStrength=0)

                   #originalMuscleOrigin = originalMuscleJoint.origin.inputs()[0]
                   #originalMuscleOriginParent = pymel.listRelatives(originalMuscleOrigin, parent=True)[0]
                   #originalMuscleInsertion = originalMuscleJoint.insertion.inputs()[0]
                   #originalMuscleInsertionParent = pymel.listRelatives(originalMuscleInsertion, parent=True)[0]

                   #newMuscleOrigin = mirroredJoint.origin.inputs()[0]
                   #newMuscleOriginParent = getMirroredObject(originalMuscleOriginParent)
                   #pymel.parent(newMuscleOrigin, newMuscleOriginParent)

                   #newMuscleInsertion = mirroredJoint.insertion.inputs()[0]
                   #newMuscleInsertionParent = getMirroredObject(originalMuscleInsertionParent)
                   #pymel.parent(newMuscleInsertion, newMuscleInsertionParent)

                   #snapMirrored(snapTarget=originalMuscleOrigin, snapObjects=[newMuscleOrigin])
                   #snapMirrored(snapTarget=originalMuscleInsertion, snapObjects=[newMuscleInsertion])

               #elif rigType == 'muscleBendPivotPosition':
                   #newbaseName = newName.split('_pivotPosition')[0]
                   #radius = originalMuscleJoint.radius.get()

                   #mirroredJoint = _createBendMuscle(name=newbaseName, radius=radius)

                   #originalMuscleOrigin = originalMuscleJoint.origin.inputs()[0]
                   #originalMuscleOriginParent = pymel.listRelatives(originalMuscleOrigin, parent=True)[0]
                   #originalMuscleInsertion = originalMuscleJoint.insertion.inputs()[0]
                   #originalMuscleInsertionParent = pymel.listRelatives(originalMuscleInsertion, parent=True)[0]
                   #originalPivotPosition = originalMuscleJoint
                   #originalPivotPositionParent = pymel.listRelatives(originalPivotPosition, parent=True)[0]

                   #newMuscleOrigin = mirroredJoint.origin.inputs()[0]
                   #newMuscleOriginParent = getMirroredObject(originalMuscleOriginParent)
                   #pymel.parent(newMuscleOrigin, newMuscleOriginParent)

                   #newMuscleInsertion = mirroredJoint.insertion.inputs()[0]
                   #newMuscleInsertionParent = getMirroredObject(originalMuscleInsertionParent)
                   #pymel.parent(newMuscleInsertion, newMuscleInsertionParent)

                   #newPivotPosition = mirroredJoint
                   #newPivotPositionParent = getMirroredObject(originalPivotPositionParent)
                   #pymel.parent(newPivotPosition, newPivotPositionParent)

                   #snapMirrored(snapTarget=originalMuscleOrigin, snapObjects=[newMuscleOrigin])
                   #snapMirrored(snapTarget=originalMuscleInsertion, snapObjects=[newMuscleInsertion])
                   #snapMirrored(snapTarget=originalPivotPosition, snapObjects=[newPivotPosition])



def alignAllMuscleOrigin():
    muscleOrigins = []
    selection = pymel.ls(selection=True)
    joints = pymel.ls(type='joint')

    for joint in joints:
       if pymel.attributeQuery('rigType', node=joint, exists=True):
           rigType = joint.rigType.get()
           if rigType == 'muscleJoint':
               muscleOrigins.append(joint)

    if muscleOrigins:
        for muscleOrigin in muscleOrigins:
            alignMuscleOrigin(muscleJoints=[muscleOrigin])

    pymel.select(selection)

def alignMuscleOrigin(muscleJoints=None):

    muscleJoints = []
    muscleBendJoints = []
    selection = pymel.ls(selection=True)
    joints = pymel.ls(type='joint')
    curves = pymel.ls(type='nurbsCurve')
    curves.extend(pymel.ls(type='locator'))

    for joint in joints:
       if pymel.attributeQuery('rigType', node=joint, exists=True):
           rigType = joint.rigType.get()

           if rigType == 'muscleJoint':
               muscleJoints.append(joint)

    for curve in curves:
       if pymel.attributeQuery('rigType', node=joint, exists=True):
           rigType = joint.rigType.get()

           if rigType == 'muscleBendJoint':
               muscleBendJoints.append(each)

#    if muscleJoints == None:
#        muscleJoints = []
#        for each in selection:
#            if pymel.attributeQuery('rigType', node=each, exists=True):
#                rigType = each.rigType.get()
#                if rigType == 'muscleJoint':
#                    muscleJoints.append(each)
#
#        muscleJoints = pymel.ls(selection=True)

    if muscleJoints:
        for muscleJoint in muscleJoints:
            originLocator = muscleJoint.origin.inputs()[0]
            insertionLocator = muscleJoint.insertion.inputs()[0]
            insertionMatrix = pymel.xform(insertionLocator, q=True, ws=True, m=True)
            snap(r=True, snapTarget=muscleJoint.name(), snapObjects=[originLocator.name()])
            pymel.xform(insertionLocator, ws=True, m=insertionMatrix)
            snap(r=True, snapTarget=muscleJoint.name(), snapObjects=[insertionLocator.name()])

            pointA = pymel.xform(originLocator, query=True, ws=True, translation=True)
            pointB = pymel.xform(insertionLocator, query=True, ws=True, translation=True)
            initialDistance = distanceBetween(pointA, pointB)
            muscleJoint.initialLength.set(initialDistance*0.5)

    if muscleBendJoints:
        for muscleBendJoint in muscleBendJoints:
            originLocator = muscleBendJoint.origin.inputs()[0]
            insertionLocator = muscleBendJoint.insertion.inputs()[0]

            insertionMatrix = pymel.xform(insertionLocator, q=True, ws=True, m=True)
            snap(r=True, snapTarget=muscleJoint.name(), snapObjects=[originLocator.name()])
            pymel.xform(insertionLocator, ws=True, m=insertionMatrix)
            snap(r=True, snapTarget=muscleJoint.name(), snapObjects=[insertionLocator.name()])

#            pointA = pymel.xform(originLocator, query=True, ws=True, translation=True)
#            pointB = pymel.xform(insertionLocator, query=True, ws=True, translation=True)
#            initialDistance = distanceBetween(pointA, pointB)
#            muscleJoint.initialLength.set(initialDistance*0.5)

    pymel.select(selection)


def snap(t=0, s=0, r=0, snapTarget=None, snapObjects=None):
    '''snaps objects to A to object B based on translate rotate or scale'''
    sel = cmds.ls(selection=True)

    if not snapObjects:
        snapObjects = sel[:-1]

    if not snapTarget:
        snapTarget = sel[-1:]

    if t == 1:
        for each in snapObjects:
#            tempConstraint = pointConstraint(snapTarget, each)
#            delete(tempConstraint)

#            matrix = cmds.xform(snapTarget, q=True, ws=True, m=True)
#            origMatrix = cmds.xform(each, q=True, ws=True, m=True)
#
#            origMatrix[12] = matrix[12]
#            origMatrix[13] = matrix[13]
#            origMatrix[14] = matrix[14]
#
#            cmds.xform(each, ws=True, m=origMatrix)
#
            worldTrans = cmds.xform(snapTarget, q=True, ws=True, translation=True)
            cmds.xform(each, ws=True, translation=worldTrans)

    if s == 1:
        for each in snapObjects:
            tempConstraint = cmds.scaleConstraint(snapTarget, each)
            delete(tempConstraint)
#            worldScale = cmds.xform(snapTarget, q=True, scale=True)
#            cmds.xform(each, ws=True, scale=worldScale)

    if r == 1:
        for each in snapObjects:

            worldRot = cmds.xform(snapTarget, q=True, ws=True, rotation=True)
            cmds.xform(each, ws=True, rotation=worldRot)

    cmds.select(snapObjects)

def snapMirrored(snapTarget=None, snapObjects=None):

    sel = pymel.ls(sl=True)
    if not snapObjects:
        snapObjects = sel[:-1]

    if not snapTarget:
        snapTarget = sel[-1]

    for each in snapObjects:
        mmat = trh.getMirrorTransform(snapTarget)
        dst = snapObjects

        pymel.xform(dst,ws=True, m=trh.getMatrixAsList(mmat))

    cmds.select(snapObjects)
