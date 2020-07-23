
import maya.OpenMaya as OpenMaya
import maya.OpenMaya as oMaya
import maya.OpenMayaUI as OpenMayaUI
import maya.OpenMayaRender as OpenMayaRender
import maya.OpenMayaMPx as OpenMayaMPx

import math,sys

glRenderer = OpenMayaRender.MHardwareRenderer.theRenderer()
glFT = glRenderer.glFunctionTable()

ka_locatorName = "ka_locator"
ka_locatorId = OpenMaya.MTypeId(0x87006)
ka_locatorManipName = "ka_locatorManip"
ka_locatorManipId = OpenMaya.MTypeId(0x87007)

delta1 = 0.01
delta2 = 0.02
delta3 = 0.03
delta4 = 0.04

# Locator Data
centre = [    [  0.10, 0.0,  0.10 ],
            [  0.10, 0.0, -0.10 ],
            [ -0.10, 0.0, -0.10 ],
            [ -0.10, 0.0,  0.10 ], 
            [  0.10, 0.0,  0.10 ] ] 
state1 = [    [  1.00, 0.0,  1.00 ],
            [  1.00, 0.0,  0.50 ],
            [  0.50, 0.0,  0.50 ],
            [  0.50, 0.0,  1.00 ], 
            [  1.00, 0.0,  1.00 ] ] 
state2 = [    [  1.00, 0.0, -1.00 ],
            [  1.00, 0.0, -0.50 ],
            [  0.50, 0.0, -0.50 ],
            [  0.50, 0.0, -1.00 ], 
            [  1.00, 0.0, -1.00 ] ] 
state3 = [    [ -1.00, 0.0, -1.00 ],
            [ -1.00, 0.0, -0.50 ],
            [ -0.50, 0.0, -0.50 ],
            [ -0.50, 0.0, -1.00 ], 
            [ -1.00, 0.0, -1.00 ] ] 
state4 = [    [ -1.00, 0.0,  1.00 ],
            [ -1.00, 0.0,  0.50 ],
            [ -0.50, 0.0,  0.50 ],
            [ -0.50, 0.0,  1.00 ], 
            [ -1.00, 0.0,  1.00 ] ] 
arrow1 = [    [  0.00, 0.0,  1.00 ],
            [  0.10, 0.0,  0.20 ],
            [ -0.10, 0.0,  0.20 ],
            [  0.00, 0.0,  1.00 ] ] 
arrow2 = [    [  1.00, 0.0,  0.00 ],
            [  0.20, 0.0,  0.10 ],
            [  0.20, 0.0, -0.10 ],
            [  1.00, 0.0,  0.00 ] ] 
arrow3 = [    [  0.00, 0.0, -1.00 ],
            [  0.10, 0.0, -0.20 ],
            [ -0.10, 0.0, -0.20 ],
            [  0.00, 0.0, -1.00 ] ] 
arrow4 = [    [ -1.00, 0.0,  0.00 ],
            [ -0.20, 0.0,  0.10 ],
            [ -0.20, 0.0, -0.10 ],
            [ -1.00, 0.0,  0.00 ] ] 
perimeter=[    [  1.10, 0.0,  1.10 ],
            [  1.10, 0.0, -1.10 ],
            [ -1.10, 0.0, -1.10 ],
            [ -1.10, 0.0,  1.10 ], 
            [  1.10, 0.0,  1.10 ] ]

lenLocatorDrawShape = 8



kCentreCount = 5
kState1Count = 5
kState2Count = 5
kState3Count = 5
kState4Count = 5
kArrow1Count = 4
kArrow2Count = 4
kArrow3Count = 4
kArrow4Count = 4
kPerimeterCount = 5

kActive = 8
kNoStatus = 2
########################################################################
########################################################################


class ka_locatorManip(OpenMayaMPx.MPxManipContainer):
    def __init__(self):
        OpenMayaMPx.MPxManipContainer.__init__(self)

        
        self.fCircleSweepManip = OpenMaya.MDagPath()
        self.fDirectionManip = OpenMaya.MDagPath()
        self.fDiscManip = OpenMaya.MDagPath()
        self.fDistanceManip = OpenMaya.MDagPath()
        self.fFreePointTriadManip = OpenMaya.MDagPath()
        self.fStateManip = OpenMaya.MDagPath()
        self.fToggleManip = OpenMaya.MDagPath()
        self.fRotateManip = OpenMaya.MDagPath()
        self.fScaleManip = OpenMaya.MDagPath()
        self.fNodePath = OpenMaya.MDagPath()
        

class ka_locator(OpenMayaMPx.MPxLocatorNode):
    
    aShapeVisibility = OpenMaya.MObject()
    aShapeType = OpenMaya.MObject()
    
    aShapes = OpenMaya.MObject()

    aShapeTranslate = OpenMaya.MObject()
    aShapeTranslateX = OpenMaya.MObject()
    aShapeTranslateY = OpenMaya.MObject()
    aShapeTranslateZ = OpenMaya.MObject()
    
    aShapeRotate = OpenMaya.MObject()
    aShapeRotateX = OpenMaya.MObject()
    aShapeRotateY = OpenMaya.MObject()
    aShapeRotateZ = OpenMaya.MObject()
    
    aShapeScale = OpenMaya.MObject()
    aShapeScaleX = OpenMaya.MObject()
    aShapeScaleY = OpenMaya.MObject()
    aShapeScaleZ = OpenMaya.MObject()

    aLength = OpenMaya.MObject()
    aTaper = OpenMaya.MObject()
        
    aLineThickness =  OpenMaya.MObject()
    
    aColorR = OpenMaya.MObject()
    aColorG = OpenMaya.MObject()
    aColorB = OpenMaya.MObject()
    aColor = OpenMaya.MObject()
    
    
    aText = OpenMaya.MObject()
    
    aStipple = OpenMaya.MObject()
    aStippleSpacing = OpenMaya.MObject()
    aStipplePatern = OpenMaya.MObject()
    
    aLineEndMatrix = OpenMaya.MObject()
    
    #make a list that will dictate throughout the plug-in the order and total number of the attributes
    #belonging to each compound in the 'shapes' compound array. This makes adding, removing and reordering
    #attributes much simpler
    shapeAttrs = [
                    'aShapeVisibility',
                    'aShapeType',
                    'aShapeTranslate',
                    'aShapeRotate',
                    'aShapeScale',
                    'aLength',
                    'aTaper',
                    'aColor',
                    'aLineThickness',
                    'aStipple',
                    'aStippleSpacing',
                    'aStipplePatern',
                    'aLineEndMatrix',
                    'aText',
                  ]
    
    shapeTypes = {  #index  #Enum Label                  #bounding box preset
                    0:      ["locator",                  '3dBB'],
                    1:      ["text",                      None],
                    2:      ["line to lineEndMatrix",     None],
                    
                    20:     ["----------",                None],
                    21:     ["2d Circle",                '2dLengthBB'],
                    22:     ["2d Square",                '2dLengthBB'],
                    #23:     ["2d Capsule",               '2dLengthBB'],
                        
                    60:     ["----------",                 None],
                    61:     ["3d Cube",                  '3dLengthBB'],
                    62:     ["3d Sphere",                '3dLengthBB'],
                    63:     ["3d Cylinder",              '3dLengthBB'],
                    64:     ["3d arrow",                 '3dLengthBB'],
                        
                    990:    ["----------",                 None],
                    999:    ["customCurve",                None],
                 }

          
    def __init__(self):
        OpenMayaMPx.MPxLocatorNode.__init__(self)
        

    def compute(self, plug, data):
        return OpenMaya.kUnknownParameter


    def draw(self, view, path, style, status):
        view.beginGL()    #must be the first GL command
        
        #get node
        thisNode = self.thisMObject()
        fnThisNode = OpenMaya.MFnDependencyNode(thisNode)

        #local Scale of locator
        localScaleXplug = OpenMaya.MPlug( thisNode, fnThisNode.attribute( "localScaleX" ) )
        localScaleYplug = OpenMaya.MPlug( thisNode, fnThisNode.attribute( "localScaleY" ) )
        localScaleZplug = OpenMaya.MPlug( thisNode, fnThisNode.attribute( "localScaleZ" ) )
        scaleX = localScaleXplug.asMDistance().asCentimeters()
        scaleY = localScaleYplug.asMDistance().asCentimeters()
        scaleZ = localScaleZplug.asMDistance().asCentimeters()
        
        #local Position of locator
        localPositionXplug = OpenMaya.MPlug( thisNode, fnThisNode.attribute( "localPositionX" ) )
        localPositionYplug = OpenMaya.MPlug( thisNode, fnThisNode.attribute( "localPositionY" ) )
        localPositionZplug = OpenMaya.MPlug( thisNode, fnThisNode.attribute( "localPositionZ" ) )
        positionX = localPositionXplug.asMDistance().asCentimeters()
        positionY = localPositionYplug.asMDistance().asCentimeters()
        positionZ = localPositionZplug.asMDistance().asCentimeters()
        
        #shapes
        shapesPlug = OpenMaya.MPlug(thisNode, ka_locator.aShapes)
        shapeIndices = OpenMaya.MIntArray()
        shapesPlug.getExistingArrayAttributeIndices(shapeIndices)
        
        if len(shapeIndices) is 0: #create the first array item by querying it
            element0 = shapesPlug.elementByLogicalIndex(0)
            element0.asMObject()
            shapeIndices = OpenMaya.MIntArray()        
            shapesPlug.getExistingArrayAttributeIndices(shapeIndices)
            
        #for each shape
        for shapeIndice in shapeIndices:
            
            shapePlug = shapesPlug.elementByPhysicalIndex(shapeIndice)
            
            #short hand way that i find the attributes index in the compound
            findIndex = ka_locator.shapeAttrs.index
                        
            #shapeVisibility
            shapeVisibilityPlug = shapePlug.child(findIndex('aShapeVisibility'))
            shapeVisibility = shapeVisibilityPlug.asBool()
            
            if shapeVisibility:

                
                #shapeType
                shapeTypePlug = shapePlug.child(findIndex('aShapeType'))
                shapeType = shapeTypePlug.asInt()
                
                #shapeTranslate
                shapeTranslateXPlug = shapePlug.child(findIndex('aShapeTranslate')).child(0)
                shapeTranslateYPlug = shapePlug.child(findIndex('aShapeTranslate')).child(1)
                shapeTranslateZPlug = shapePlug.child(findIndex('aShapeTranslate')).child(2)
                shapeTranslateX = shapeTranslateXPlug.asMDistance().asCentimeters()+positionX
                shapeTranslateY = shapeTranslateYPlug.asMDistance().asCentimeters()+positionY
                shapeTranslateZ = shapeTranslateZPlug.asMDistance().asCentimeters()+positionZ
                
                #shapeRotate
                shapeRotateXPlug = shapePlug.child(findIndex('aShapeRotate')).child(0)
                shapeRotateYPlug = shapePlug.child(findIndex('aShapeRotate')).child(1)
                shapeRotateZPlug = shapePlug.child(findIndex('aShapeRotate')).child(2)
                shapeRotateX = degreesToRadians(shapeRotateXPlug.asDouble())
                shapeRotateY = degreesToRadians(shapeRotateYPlug.asDouble())
                shapeRotateZ = degreesToRadians(shapeRotateZPlug.asDouble())
                shapeEulerRotation = OpenMaya.MEulerRotation(shapeRotateX, shapeRotateY, shapeRotateZ)
                
                #shapeScale
                shapeScaleXPlug = shapePlug.child(findIndex('aShapeScale')).child(0)
                shapeScaleYPlug = shapePlug.child(findIndex('aShapeScale')).child(1)
                shapeScaleZPlug = shapePlug.child(findIndex('aShapeScale')).child(2)
                shapeScaleX = shapeScaleXPlug.asDouble()*scaleX
                shapeScaleY = shapeScaleYPlug.asDouble()*scaleY
                shapeScaleZ = shapeScaleZPlug.asDouble()*scaleZ

                #length
                lengthPlug = shapePlug.child(findIndex('aLength'))
                length = lengthPlug.asMDistance().asCentimeters()
    
                #color
                colorPlugR = shapePlug.child(findIndex('aColor')).child(0)
                colorPlugG = shapePlug.child(findIndex('aColor')).child(1)
                colorPlugB = shapePlug.child(findIndex('aColor')).child(2)
                colorR = colorPlugR.asDouble()
                colorG = colorPlugG.asDouble()
                colorB = colorPlugB.asDouble()
                
                #lineThickness
                lineThicknessPlug = shapePlug.child(findIndex('aLineThickness'))
                lineThickness = lineThicknessPlug.asInt()
    
                #orientation
                taperPlug = shapePlug.child(findIndex('aTaper'))
                taper = taperPlug.asDouble()
                
                #stipple
                stipplePlug = shapePlug.child(findIndex('aStipple'))
                stipple = stipplePlug.asBool()
 
                #if not one of the shapes that doesn't consider shape tranforms ie: lineBetweenObjects
                if not shapeType in [2]:
                    eulerRotate = OpenMaya.MEulerRotation(shapeRotateX, shapeRotateY, shapeRotateZ)
                    
                    shapeRotationMatrix = eulerRotate.asMatrix()
                    shapeTranslationMatrix = OpenMaya.MMatrix()
                    shapeScaleMatrix = OpenMaya.MMatrix()
                    
                    OpenMaya.MScriptUtil.createMatrixFromList( [1,0,0,0,
                                                                0,1,0,0,
                                                                0,0,1,0,
                                                                shapeTranslateX,shapeTranslateY,shapeTranslateZ,1,
                                                               ], shapeTranslationMatrix)
                    
                    OpenMaya.MScriptUtil.createMatrixFromList( [shapeScaleX,0,0,0,
                                                                0,shapeScaleY,0,0,
                                                                0,0,shapeScaleZ,0,
                                                                0,0,0,1,
                                                               ], shapeScaleMatrix)
                    
                    shapeTransformMultiplyMatrix = shapeScaleMatrix * shapeRotationMatrix * shapeTranslationMatrix
                
                
                
                
                ##DRAW               
            
                ##LINE DRAW SETTINGS
                if lineThickness > 1:
                    glFT.glPushAttrib(OpenMayaRender.MGL_LINE_BIT)
                    glFT.glLineWidth(lineThickness)
                
                #set stipple
                if stipple:        
                    stippleSpacingPlug = shapePlug.child(findIndex('aStippleSpacing'))
                    stippleSpacing = stippleSpacingPlug.asInt()  
                    
                    stipplePaternPlug = shapePlug.child(findIndex('aStipplePatern'))
                    stipplePatern = stipplePaternPlug.asInt()
                
                    glFT.glPushAttrib(OpenMayaRender.MGL_LINE_STIPPLE)
                    glFT.glPushAttrib(OpenMayaRender.MGL_LINE_STIPPLE_PATTERN)
                    glFT.glPushAttrib(OpenMayaRender.MGL_LINE_STIPPLE_REPEAT)
                
                    glFT.glLineStipple(stippleSpacing, stipplePatern)
                    glFT.glEnable(OpenMayaRender.MGL_LINE_STIPPLE)
                
                
                
                #set color
                if status == kNoStatus:    #if not being colored by maya to indicate selection, ect...
                    glFT.glPushAttrib(OpenMayaRender.MGL_CURRENT_BIT)
                    view.setDrawColor( OpenMaya.MColor(colorR, colorG, colorB) ) #set color
                    #glFT.glColor3f(colorR, colorG, colorB)    #set color OLD WAY
        
        
    
    
                ## DRAW SHAPE   
                
                ## regular locator
                if shapeType == 0: #locator
                    glFT.glBegin(OpenMayaRender.MGL_LINES)
                    drawShape=[   
                                [ [0.0, 0.0, 0.5 ], [ 0.0,  0.0, -0.5 ], ],
                                [ [0.0, 0.5, 0.0 ], [ 0.0, -0.5,  0.0 ], ],
                                [ [0.5, 0.0, 0.0 ], [-0.5,  0.0,  0.0 ], ],
                              ]
                    
                    for i, each in enumerate(drawShape):
                        pointA = OpenMaya.MPoint(drawShape[i][0][0], 
                                                 drawShape[i][0][1],
                                                 drawShape[i][0][2]) * shapeTransformMultiplyMatrix
                                                 
                        pointB = OpenMaya.MPoint(drawShape[i][1][0],
                                                 drawShape[i][1][1],
                                                 drawShape[i][1][2]) * shapeTransformMultiplyMatrix

                        glFT.glVertex3f(pointA.x, pointA.y, pointA.z)
                        glFT.glVertex3f(pointB.x, pointB.y, pointB.z)
                    glFT.glEnd()
                        
                ## text
                elif shapeType == 1: #locator
                    textPlug = shapePlug.child(findIndex('aText'))
                    text = textPlug.asString()

                    position = OpenMaya.MPoint( shapeTranslateX, shapeTranslateY, shapeTranslateZ )
                    
                    alignment = OpenMayaUI.M3dView.kCenter
                    
                    view.drawText( text, position, alignment )
                    
                ## line to lineEndMatrix
                elif shapeType == 2: #line
                    
                    lineEndMatrixPlug = shapePlug.child(findIndex('aLineEndMatrix'))
                    lineEndMatrixMObject = lineEndMatrixPlug.asMObject()
                    myMFnMatrixData = OpenMaya.MFnMatrixData(lineEndMatrixMObject)
                    lineEndMatrix = myMFnMatrixData.matrix()
                    
                    thisNodeWorldMatrix = self.getWorldMatrix(thisNode, fnThisNode)
                    thisNodeWorldInverseMatrix = thisNodeWorldMatrix.inverse()
                    
                    resultMatrix = lineEndMatrix * thisNodeWorldInverseMatrix
                    
                    thisNodeWorldPosition = self.getWorldPosition(thisNode, fnThisNode)
                    
                    glFT.glBegin(OpenMayaRender.MGL_LINES)
                    
                    glFT.glVertex3f(    shapeTranslateX,
                                        shapeTranslateY,
                                        shapeTranslateZ,
                                   )
                    
                    glFT.glVertex3f(    resultMatrix(3, 0), 
                                        resultMatrix(3, 1), 
                                        resultMatrix(3, 2), 
                                   )
                    glFT.glEnd()
        
                
                ## 2d Circle
                elif shapeType == 21:
                    glFT.glBegin(OpenMayaRender.MGL_LINE_LOOP)
                   
                    segments = 90
                    for i in range(segments):
                        if i < segments / 2 and i > 0:
                            #if taper is 0, dont bother drawing more than a single point
                            if taper:
                                angle = (2*math.pi) / segments * i
                                radiusY = math.cos(angle) * 0.5
                                radiusX =math.sin(angle) * 0.5
                                
                                pointA = OpenMaya.MPoint((radiusX * taper) + length,
                                                         radiusY * taper,
                                                         0) * shapeTransformMultiplyMatrix
                                glFT.glVertex3d(pointA.x, pointA.y, pointA.z)
                            
                            else:
                                pointA = OpenMaya.MPoint(0,0,0) * shapeTransformMultiplyMatrix
                                glFT.glVertex3d(pointA.x, pointA.y, pointA.z)
                                
                        else:   
                            angle = (2*math.pi) / segments * i
                            radiusY = math.cos(angle) * 0.5
                            radiusX =math.sin(angle) * 0.5
                            
                            pointA = OpenMaya.MPoint(radiusX,
                                                     radiusY,
                                                     0) * shapeTransformMultiplyMatrix
                            glFT.glVertex3d(pointA.x, pointA.y, pointA.z)
                    glFT.glEnd()  
        
                ## 2d Square
                elif shapeType == 22:
                    
                    glFT.glBegin(OpenMayaRender.MGL_LINES)
                    l = length
                    t = taper
                    drawShape=[   
                                [ [ 0.5+l,  0.5*t, 0.0], [-0.5  ,  0.5  , 0.0], ],
                                [ [-0.5  ,  0.5  , 0.0], [-0.5  , -0.5  , 0.0], ],
                                [ [-0.5  , -0.5  , 0.0], [ 0.5+l, -0.5*t, 0.0], ],
                                [ [ 0.5+l, -0.5*t, 0.0], [ 0.5+l,  0.5*t, 0.0], ],
                              ]

                    for i, each in enumerate(drawShape):  
                        pointA = OpenMaya.MPoint(drawShape[i][0][0],
                                                 drawShape[i][0][1],
                                                 drawShape[i][0][2]) * shapeTransformMultiplyMatrix
                        
                        pointB = OpenMaya.MPoint(drawShape[i][1][0],
                                                 drawShape[i][1][1],
                                                 drawShape[i][1][2]) * shapeTransformMultiplyMatrix
                        
                        glFT.glVertex3f(pointA.x, pointA.y, pointA.z,)
                        glFT.glVertex3f(pointB.x, pointB.y, pointB.z,)

                    glFT.glEnd()    
                
                ## 3d Cube
                elif shapeType == 61:
                    glFT.glBegin(OpenMayaRender.MGL_LINES)
                    l = length
                    t = taper
                    drawShape=[   
                               
                                [ [ 0.5+l,  0.5*t,  0.5*t], [ 0.5+l,  0.5*t, -0.5*t], ],
                                [ [ 0.5+l,  0.5*t, -0.5*t], [ 0.5+l, -0.5*t, -0.5*t], ],
                                [ [ 0.5+l, -0.5*t, -0.5*t], [ 0.5+l, -0.5*t,  0.5*t], ],
                                [ [ 0.5+l, -0.5*t,  0.5*t], [ 0.5+l,  0.5*t,  0.5*t], ],
                                
                                [ [-0.5,  0.5,  0.5], [-0.5,  0.5, -0.5], ],
                                [ [-0.5,  0.5, -0.5], [-0.5, -0.5, -0.5], ],
                                [ [-0.5, -0.5, -0.5], [-0.5, -0.5,  0.5], ],
                                [ [-0.5, -0.5,  0.5], [-0.5,  0.5,  0.5], ],
                                
                                [ [-0.5,  0.5,  0.5], [ 0.5+l,  0.5*t,  0.5*t], ],
                                [ [-0.5,  0.5, -0.5], [ 0.5+l,  0.5*t, -0.5*t], ],
                                [ [-0.5, -0.5, -0.5], [ 0.5+l, -0.5*t, -0.5*t], ],
                                [ [-0.5, -0.5,  0.5], [ 0.5+l, -0.5*t,  0.5*t], ],
                              ]
                    
                    for i, each in enumerate(drawShape):
                        pointA = OpenMaya.MPoint(drawShape[i][0][0], 
                                                 drawShape[i][0][1],
                                                 drawShape[i][0][2]) * shapeTransformMultiplyMatrix
                                                 
                        pointB = OpenMaya.MPoint(drawShape[i][1][0],
                                                 drawShape[i][1][1],
                                                 drawShape[i][1][2]) * shapeTransformMultiplyMatrix

                        glFT.glVertex3f(pointA.x, pointA.y, pointA.z)
                        glFT.glVertex3f(pointB.x, pointB.y, pointB.z)
                    glFT.glEnd()                
                
                
                ## 3d Sphere
                elif shapeType == 62:                      
                    segments = 90
                    circleAxis = ['x', 'y', 'z',]
                    if length != 0 or taper != 1:
                        circleAxis.append('x2')
                        
                    for axis in circleAxis:
                        glFT.glBegin(OpenMayaRender.MGL_LINE_LOOP)
                        
                        #draw 2d circle
                        for i in range(segments):
                            if i >= (segments/2) or i == 0:

                                angle = (2*math.pi) / segments * i
                                
                                if axis == 'x':
                                    x = 0
                                    y = math.cos(angle) * 0.5
                                    z =math.sin(angle) * 0.5
                                if axis == 'x2':
                                        x = length
                                        y = (math.cos(angle) * 0.5) * taper
                                        z =(math.sin(angle) * 0.5) * taper
                                elif axis == 'y':
                                    x = math.sin(angle) * 0.5
                                    y = 0
                                    z =math.cos(angle) * 0.5
                                elif axis == 'z':
                                    y = math.cos(angle) * 0.5
                                    x = math.sin(angle) * 0.5 #this x needs to use sin to make length split correctly
                                    z = 0
                                    
                                pointA = OpenMaya.MPoint(x,y,z) * shapeTransformMultiplyMatrix
                                glFT.glVertex3d(pointA.x, pointA.y, pointA.z,)
                                
                            if i < (segments/2) or i == segments or i == (segments/2)-1:
                                
                                if i == (segments / 2)-1: i = (segments / 2)#this double draws halfway point for a proper taper
                                
                                #if taper is 0, dont bother drawing more than a single point                                  
                                if taper:
                                    angle = (2*math.pi) / segments * i
                                    
                                    if axis == 'x':
                                        x = 0
                                        y = math.cos(angle) * 0.5
                                        z =math.sin(angle) * 0.5
                                    if axis == 'x2':
                                        x = length
                                        y = (math.cos(angle) * 0.5) * taper
                                        z =(math.sin(angle) * 0.5) * taper
                                    elif axis == 'y':
                                        x = ((math.sin(angle) * 0.5) * taper) + length
                                        y = 0
                                        z =(math.cos(angle) * 0.5) * taper
                                    elif axis == 'z':
                                        y = (math.cos(angle) * 0.5) * taper
                                        x = ((math.sin(angle) * 0.5) * taper) + length #this x needs to use sin to make length split correctly
                                        z = 0
                                        
                                    pointA = OpenMaya.MPoint(x,y,z) * shapeTransformMultiplyMatrix
                                    glFT.glVertex3d(pointA.x, pointA.y, pointA.z,)
                                    
                                else:
                                    pointA = OpenMaya.MPoint(0,0,0) * shapeTransformMultiplyMatrix
                                    glFT.glVertex3d(pointA.x, pointA.y, pointA.z)
                        glFT.glEnd()              
                
                ## 3d Cylinder
                elif shapeType == 63:
                    l = length
                    t = taper
                    
                    glFT.glBegin(OpenMayaRender.MGL_LINES)
                    drawShape=[                                  
                                [ [(0.5*t)+l,  0.0, -0.5], [(0.5*t)+l,  0.0,  0.5], ],
                                [ [-0.5     ,  0.0, -0.5], [-0.5     ,  0.0,  0.5], ],
                                [ [ 0.0     , -0.5, -0.5], [ 0.0     , -0.5,  0.5], ],
                                [ [ 0.0     ,  0.5, -0.5], [ 0.0     ,  0.5,  0.5], ],
                              ]
                    if length:
                        drawShape.append([ [(0.0*t)+l, -0.5*t, -0.5], [(0.0*t)+l, -0.5*t,  0.5], ])
                        drawShape.append([ [(0.0*t)+l,  0.5*t, -0.5], [(0.0*t)+l,  0.5*t,  0.5], ])
                        
                    for i, each in enumerate(drawShape):
                        pointA = OpenMaya.MPoint(drawShape[i][0][0], 
                                                 drawShape[i][0][1],
                                                 drawShape[i][0][2]) * shapeTransformMultiplyMatrix
                                                 
                        pointB = OpenMaya.MPoint(drawShape[i][1][0],
                                                 drawShape[i][1][1],
                                                 drawShape[i][1][2]) * shapeTransformMultiplyMatrix

                        glFT.glVertex3f(pointA.x, pointA.y, pointA.z)
                        glFT.glVertex3f(pointB.x, pointB.y, pointB.z)
                    glFT.glEnd()
                
                
                    
                    zAxisPlusMinus = [1,-1]
                    for zAxis in zAxisPlusMinus:
                        glFT.glBegin(OpenMayaRender.MGL_LINE_LOOP)

                        segments = 90
                        for i in range(segments):
                            if i >= (segments/2) or i == 0:
                                angle = (2*math.pi) / segments * i
                                radiusX = math.sin(angle) * 0.5
                                radiusY = math.cos(angle) * 0.5
                                
                                pointA = OpenMaya.MPoint(radiusX,
                                                         radiusY,
                                                         0.5*zAxis,) * shapeTransformMultiplyMatrix
                                                         
                                glFT.glVertex3d(pointA.x, pointA.y, pointA.z)
                                
                                
                            else:
                                angle = (2*math.pi) / segments * i
                                radiusX = (math.sin(angle) * 0.5) * taper
                                radiusY = (math.cos(angle) * 0.5) * taper
                                
                                pointA = OpenMaya.MPoint(radiusX+length,
                                                         radiusY,
                                                         0.5*zAxis,) * shapeTransformMultiplyMatrix
                                                         
                                glFT.glVertex3d(pointA.x, pointA.y, pointA.z)
                        glFT.glEnd()     
                    

                glFT.glPopAttrib()
            #if shape visible
        view.endGL()    #must be the last GL command
        


    def getWorldMatrix(self, thisNode, fnThisNode):
        worldMatrixAttr = fnThisNode.attribute( "worldMatrix" )
        worldMatrixAttrPlug = OpenMaya.MPlug( thisNode, worldMatrixAttr )
        worldMatrixAttrPlug = worldMatrixAttrPlug.elementByLogicalIndex( 0 )
        worldMatrixAttrMObject = worldMatrixAttrPlug.asMObject()
        myMFnMatrixData = OpenMaya.MFnMatrixData(worldMatrixAttrMObject)
        return myMFnMatrixData.matrix()
    
        
    def getWorldPosition(self, thisNode, fnThisNode):
        worldMatrix = self.getWorldMatrix(thisNode, fnThisNode)
        return [worldMatrix(3, 0), worldMatrix(3, 1), worldMatrix(3, 2)]



    def isBounded(self):
        return True

    def boundingBox(self):
        max = []
        min = []
        
        #get node
        thisNode = self.thisMObject()
        fnThisNode = OpenMaya.MFnDependencyNode(thisNode)

        #local Scale of locator
        localScaleXplug = OpenMaya.MPlug( thisNode, fnThisNode.attribute( "localScaleX" ) )
        localScaleYplug = OpenMaya.MPlug( thisNode, fnThisNode.attribute( "localScaleY" ) )
        localScaleZplug = OpenMaya.MPlug( thisNode, fnThisNode.attribute( "localScaleZ" ) )
        scaleX = localScaleXplug.asMDistance().asCentimeters()
        scaleY = localScaleYplug.asMDistance().asCentimeters()
        scaleZ = localScaleZplug.asMDistance().asCentimeters()
        
        #local Position of locator
        localPositionXplug = OpenMaya.MPlug( thisNode, fnThisNode.attribute( "localPositionX" ) )
        localPositionYplug = OpenMaya.MPlug( thisNode, fnThisNode.attribute( "localPositionY" ) )
        localPositionZplug = OpenMaya.MPlug( thisNode, fnThisNode.attribute( "localPositionZ" ) )
        positionX = localPositionXplug.asMDistance().asCentimeters()
        positionY = localPositionYplug.asMDistance().asCentimeters()
        positionZ = localPositionZplug.asMDistance().asCentimeters()
        
        #shapes
        shapesPlug = OpenMaya.MPlug(thisNode, ka_locator.aShapes)
        shapeIndices = OpenMaya.MIntArray()
        shapesPlug.getExistingArrayAttributeIndices(shapeIndices)
        
        if len(shapeIndices) is 0: #create the first array item by querying it
            element0 = shapesPlug.elementByLogicalIndex(0)
            element0.asMObject()
            shapeIndices = OpenMaya.MIntArray()        
            shapesPlug.getExistingArrayAttributeIndices(shapeIndices)
            
        #for each shape
        for shapeIndice in shapeIndices:
            
            shapePlug = shapesPlug.elementByPhysicalIndex(shapeIndice)
            
            #short hand way that i find the attributes index in the compound
            findIndex = ka_locator.shapeAttrs.index
                        
            #shapeVisibility
            shapeVisibilityPlug = shapePlug.child(findIndex('aShapeVisibility'))
            shapeVisibility = shapeVisibilityPlug.asBool()
            
            if shapeVisibility:

                
                #shapeType
                shapeTypePlug = shapePlug.child(findIndex('aShapeType'))
                shapeType = shapeTypePlug.asInt()
                
                #shapeTranslate
                shapeTranslateXPlug = shapePlug.child(findIndex('aShapeTranslate')).child(0)
                shapeTranslateYPlug = shapePlug.child(findIndex('aShapeTranslate')).child(1)
                shapeTranslateZPlug = shapePlug.child(findIndex('aShapeTranslate')).child(2)
                shapeTranslateX = shapeTranslateXPlug.asMDistance().asCentimeters()+positionX
                shapeTranslateY = shapeTranslateYPlug.asMDistance().asCentimeters()+positionY
                shapeTranslateZ = shapeTranslateZPlug.asMDistance().asCentimeters()+positionZ
                
                #shapeRotate
                shapeRotateXPlug = shapePlug.child(findIndex('aShapeRotate')).child(0)
                shapeRotateYPlug = shapePlug.child(findIndex('aShapeRotate')).child(1)
                shapeRotateZPlug = shapePlug.child(findIndex('aShapeRotate')).child(2)
                shapeRotateX = degreesToRadians(shapeRotateXPlug.asDouble())
                shapeRotateY = degreesToRadians(shapeRotateYPlug.asDouble())
                shapeRotateZ = degreesToRadians(shapeRotateZPlug.asDouble())
                shapeEulerRotation = OpenMaya.MEulerRotation(shapeRotateX, shapeRotateY, shapeRotateZ)
                
                #shapeScale
                shapeScaleXPlug = shapePlug.child(findIndex('aShapeScale')).child(0)
                shapeScaleYPlug = shapePlug.child(findIndex('aShapeScale')).child(1)
                shapeScaleZPlug = shapePlug.child(findIndex('aShapeScale')).child(2)
                shapeScaleX = shapeScaleXPlug.asDouble()*scaleX
                shapeScaleY = shapeScaleYPlug.asDouble()*scaleY
                shapeScaleZ = shapeScaleZPlug.asDouble()*scaleZ

                #length
                lengthPlug = shapePlug.child(findIndex('aLength'))
                length = lengthPlug.asMDistance().asCentimeters()

                #if not one of the shapes that doesn't consider shape tranforms ie: lineBetweenObjects
                if not shapeType in [2]:
                    eulerRotate = OpenMaya.MEulerRotation(shapeRotateX, shapeRotateY, shapeRotateZ)
                    
                    shapeRotationMatrix = eulerRotate.asMatrix()
                    shapeTranslationMatrix = OpenMaya.MMatrix()
                    shapeScaleMatrix = OpenMaya.MMatrix()
                    
                    OpenMaya.MScriptUtil.createMatrixFromList( [1,0,0,0,
                                                                0,1,0,0,
                                                                0,0,1,0,
                                                                shapeTranslateX,shapeTranslateY,shapeTranslateZ,1,
                                                               ], shapeTranslationMatrix)
                    
                    OpenMaya.MScriptUtil.createMatrixFromList( [shapeScaleX,0,0,0,
                                                                0,shapeScaleY,0,0,
                                                                0,0,shapeScaleZ,0,
                                                                0,0,0,1,
                                                               ], shapeScaleMatrix)
                    
                    shapeTransformMultiplyMatrix = shapeScaleMatrix * shapeRotationMatrix * shapeTranslationMatrix
                
                ## regular locator
#                if shapeType == 0: #locator
                    
                #if the bounding box preset defined at the top of the class with the enum
                #labels, equals the following, that use that method to figure a bounding box
                corners = []
                if ka_locator.shapeTypes[shapeType][1] == '3dBB':
                    
                     corners.append(OpenMaya.MPoint(-0.5,  0.5,  0.5,) * shapeTransformMultiplyMatrix)
                     corners.append(OpenMaya.MPoint(-0.5,  0.5, -0.5,) * shapeTransformMultiplyMatrix)
                     corners.append(OpenMaya.MPoint(-0.5, -0.5, -0.5,) * shapeTransformMultiplyMatrix)
                     corners.append(OpenMaya.MPoint(-0.5, -0.5,  0.5,) * shapeTransformMultiplyMatrix)
                     corners.append(OpenMaya.MPoint( 0.5,  0.5,  0.5,) * shapeTransformMultiplyMatrix)
                     corners.append(OpenMaya.MPoint( 0.5,  0.5, -0.5,) * shapeTransformMultiplyMatrix)
                     corners.append(OpenMaya.MPoint( 0.5, -0.5, -0.5,) * shapeTransformMultiplyMatrix)
                     corners.append(OpenMaya.MPoint( 0.5, -0.5,  0.5,) * shapeTransformMultiplyMatrix)
                                
                elif ka_locator.shapeTypes[shapeType][1] == '3dLengthBB':
                    
                     corners.append(OpenMaya.MPoint(-0.5,  0.5,  0.5,) * shapeTransformMultiplyMatrix)
                     corners.append(OpenMaya.MPoint(-0.5,  0.5, -0.5,) * shapeTransformMultiplyMatrix)
                     corners.append(OpenMaya.MPoint(-0.5, -0.5, -0.5,) * shapeTransformMultiplyMatrix)
                     corners.append(OpenMaya.MPoint(-0.5, -0.5,  0.5,) * shapeTransformMultiplyMatrix)
                     corners.append(OpenMaya.MPoint( 0.5+length,  0.5,  0.5,) * shapeTransformMultiplyMatrix)
                     corners.append(OpenMaya.MPoint( 0.5+length,  0.5, -0.5,) * shapeTransformMultiplyMatrix)
                     corners.append(OpenMaya.MPoint( 0.5+length, -0.5, -0.5,) * shapeTransformMultiplyMatrix)
                     corners.append(OpenMaya.MPoint( 0.5+length, -0.5,  0.5,) * shapeTransformMultiplyMatrix)
                     
                     
                elif ka_locator.shapeTypes[shapeType][1] == '2dBB':
                     corners.append(OpenMaya.MPoint( 0.5,  0.5,  0,) * shapeTransformMultiplyMatrix)
                     corners.append(OpenMaya.MPoint(-0.5,  0.5, -0,) * shapeTransformMultiplyMatrix)
                     corners.append(OpenMaya.MPoint(-0.5, -0.5, -0,) * shapeTransformMultiplyMatrix)
                     corners.append(OpenMaya.MPoint( 0.5, -0.5,  0,) * shapeTransformMultiplyMatrix)
                                          
                elif ka_locator.shapeTypes[shapeType][1] == '2dLengthBB':
                     corners.append(OpenMaya.MPoint( 0.5+length,  0.5,  0,) * shapeTransformMultiplyMatrix)
                     corners.append(OpenMaya.MPoint(-0.5,  0.5, -0,) * shapeTransformMultiplyMatrix)
                     corners.append(OpenMaya.MPoint(-0.5, -0.5, -0,) * shapeTransformMultiplyMatrix)
                     corners.append(OpenMaya.MPoint( 0.5+length, -0.5,  0,) * shapeTransformMultiplyMatrix)
                                          
                elif shapeType == 2: #line
                    lineEndMatrixPlug = shapePlug.child(findIndex('aLineEndMatrix'))
                    lineEndMatrixMObject = lineEndMatrixPlug.asMObject()
                    myMFnMatrixData = OpenMaya.MFnMatrixData(lineEndMatrixMObject)
                    lineEndMatrix = myMFnMatrixData.matrix()
                    
                    thisNodeWorldMatrix = self.getWorldMatrix(thisNode, fnThisNode)
                    thisNodeWorldInverseMatrix = thisNodeWorldMatrix.inverse()
                    
                    resultMatrix = lineEndMatrix * thisNodeWorldInverseMatrix
                    
                    thisNodeWorldPosition = self.getWorldPosition(thisNode, fnThisNode)
                    
                    corners.append(OpenMaya.MPoint(shapeTranslateX, shapeTranslateY, shapeTranslateZ,))
                    corners.append(OpenMaya.MPoint( resultMatrix(3, 0), resultMatrix(3, 1), resultMatrix(3, 2) ))
                                     
                else:
                     corners.append(OpenMaya.MPoint(-0.5,-0.5,-0.5,))
                     corners.append(OpenMaya.MPoint(0.5,0.5,0.5,))
                     
                #add to shape total bounding box if outside existing box
                
                #first input, set defaults

                
                #check if the corners fall outside the existing bounding box
                #if they do, add them to the bounding box
                for corner in corners:
                    if len(max) < 3:
                        max = [corner.x, corner.y, corner.z]
                    if len(min) < 3:
                        min = [corner.x, corner.y, corner.z]
                    
                    if corner.x > max[0]: max[0] = corner.x
                    if corner.y > max[1]: max[1] = corner.y
                    if corner.z > max[2]: max[2] = corner.z
                    if corner.x < min[0]: min[0] = corner.x
                    if corner.y < min[1]: min[1] = corner.y
                    if corner.z < min[2]: min[2] = corner.z
                    


#            
        #if shape visible           
        if len(max) < 3:  #will only occure if all shapes are invisible
            max = [0, 0, 0]
        if len(min) < 3:  #will only occure if all shapes are invisible
            min = [0, 0, 0]
    
        corner1MPoint = OpenMaya.MPoint( max[0], max[1], max[2] )
        corner2MPoint = OpenMaya.MPoint( min[0], min[1], min[2] )

        return OpenMaya.MBoundingBox(corner1MPoint, corner2MPoint)

    

########################################################################
########################################################################


def locatorCreator():
    return ka_locator()


def locatorInit():
    unitFn = OpenMaya.MFnUnitAttribute()
    numericFn = OpenMaya.MFnNumericAttribute()
    enumFn = OpenMaya.MFnEnumAttribute()
    matrixFn = OpenMaya.MFnMatrixAttribute()
    compoundFn = OpenMaya.MFnCompoundAttribute()
    typedFn = OpenMaya.MFnTypedAttribute()
    
    # shapeVis
    ka_locator.aShapeVisibility = numericFn.create("shapeVisibility", "shapeVis", oMaya.MFnNumericData.kBoolean, 1)

    # shapeType
    ka_locator.aShapeType = enumFn.create("shapeType", "shapeType", 0)
    for key in ka_locator.shapeTypes:
        enumFn.addField(ka_locator.shapeTypes[key][0], key)
    
    # shapeTranslate
    ka_locator.aShapeTranslateX = numericFn.create("shapeTranslateX", "shapeTX", OpenMaya.MFnNumericData.kFloat  , 0.0)
    ka_locator.aShapeTranslateY = numericFn.create("shapeTranslateY", "shapeTY", OpenMaya.MFnNumericData.kFloat  , 0.0)
    ka_locator.aShapeTranslateZ = numericFn.create("shapeTranslateZ", "shapeTZ", OpenMaya.MFnNumericData.kFloat  , 0.0)
    ka_locator.aShapeTranslate = numericFn.create("shapeTranslate", "shapeT", ka_locator.aShapeTranslateX, ka_locator.aShapeTranslateY, ka_locator.aShapeTranslateZ)
    
    # shapeRotate
    ka_locator.aShapeRotateX = numericFn.create("shapeRotateX", "shapeRX", OpenMaya.MFnNumericData.kFloat  , 0.0)
    ka_locator.aShapeRotateY = numericFn.create("shapeRotateY", "shapeRY", OpenMaya.MFnNumericData.kFloat  , 0.0)
    ka_locator.aShapeRotateZ = numericFn.create("shapeRotateZ", "shapeRZ", OpenMaya.MFnNumericData.kFloat  , 0.0)
    ka_locator.aShapeRotate = numericFn.create("shapeRotate", "shapeR", ka_locator.aShapeRotateX, ka_locator.aShapeRotateY, ka_locator.aShapeRotateZ)
    
    # shapeScale
    ka_locator.aShapeScaleX = numericFn.create("shapeScaleX", "shapeSX", OpenMaya.MFnNumericData.kFloat  , 1.0)
    ka_locator.aShapeScaleY = numericFn.create("shapeScaleY", "shapeSY", OpenMaya.MFnNumericData.kFloat  , 1.0)
    ka_locator.aShapeScaleZ = numericFn.create("shapeScaleZ", "shapeSZ", OpenMaya.MFnNumericData.kFloat  , 1.0)
    ka_locator.aShapeScale = numericFn.create("shapeScale", "shapeS", ka_locator.aShapeScaleX, ka_locator.aShapeScaleY, ka_locator.aShapeScaleZ)
    
    # lineThickness
    ka_locator.aLineThickness = numericFn.create("lineThickness", "lineThickness", oMaya.MFnNumericData.kInt, 1)
    numericFn.setSoftMax(10)
    numericFn.setSoftMin(1)

    # lineColor
    ka_locator.aColorR = numericFn.create("colorR", "cR", OpenMaya.MFnNumericData.kFloat, 1.0)
    ka_locator.aColorG = numericFn.create("colorG", "cG", OpenMaya.MFnNumericData.kFloat, 1.0)
    ka_locator.aColorB = numericFn.create("colorB", "cB", OpenMaya.MFnNumericData.kFloat, 0.0)
    ka_locator.aColor = numericFn.create("color", "color", ka_locator.aColorR, ka_locator.aColorG, ka_locator.aColorB)
    numericFn.setUsedAsColor(True)
    
    # length
    ka_locator.aLength = numericFn.create("length", "length", OpenMaya.MFnNumericData.kFloat , 0.0)
    numericFn.setSoftMax(10)
    numericFn.setSoftMin(0)
    
    # text
    ka_locator.aText = typedFn.create("textDisplayText", "text", OpenMaya.MFnData.kString,)

        
    # taper
    ka_locator.aTaper = numericFn.create("taper", "taper", OpenMaya.MFnNumericData.kFloat, 1)
    numericFn.setSoftMax(2)
    numericFn.setSoftMin(0)
    
    # stipple
    ka_locator.aStipple = numericFn.create("stiple", "stiple", oMaya.MFnNumericData.kBoolean, 0)

    # stippleSpacing
    ka_locator.aStippleSpacing = numericFn.create("stipleSpacing", "stipleSpacing", OpenMaya.MFnNumericData.kInt, 1)
    numericFn.setSoftMax(10)
    numericFn.setSoftMin(0)
    
    # stipplePattern
    ka_locator.aStipplePatern = numericFn.create("stiplePattern", "stiplePattern", OpenMaya.MFnNumericData.kInt, 508)
    numericFn.setSoftMax(1000)
    numericFn.setMin(1)
    
    # lineEndMatrix
    ka_locator.aLineEndMatrix = matrixFn.create("lineEndMatrix", "lineEndMatrix", OpenMaya.MFnNumericData.kMatrix,)


    # shapes (compound array)
    ka_locator.aShapes = compoundFn.create("shapes", "shapes",)
    compoundFn.setArray(True)
    compoundFn.setStorable(True);
    for shapeAttr in ka_locator.shapeAttrs:
        compoundFn.addChild( getattr(ka_locator, shapeAttr) )
        
        
    ka_locator.addAttribute(ka_locator.aShapes)
    
    OpenMayaMPx.MPxManipContainer.addToManipConnectTable(ka_locatorId)


def locatorManipCreator():
     return ka_locatorManip()


def locatorManipInit():
    OpenMayaMPx.MPxManipContainer.initialize()


# initialize the script plug-in
def initializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject, "Autodesk", "1.0", "Any")

    try:
        mplugin.registerNode(ka_locatorName, 
                                ka_locatorId,
                                locatorCreator,
                                locatorInit,
                                OpenMayaMPx.MPxNode.kLocatorNode)
    except:
        print "Failed to register context command: %s" % ka_locatorName
        raise

    try:
        mplugin.registerNode(ka_locatorManipName, 
                                ka_locatorManipId, 
                                locatorManipCreator, 
                                locatorManipInit,
                                OpenMayaMPx.MPxNode.kManipContainer)
    except:
        print "Failed to register node: %s" % ka_locatorManipName
        raise


# uninitialize the script plug-in
def uninitializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject)

    try:
        mplugin.deregisterNode(ka_locatorId)
    except:
        print "Failed to deregister context command: %s" % ka_locatorName
        raise

    try:
        mplugin.deregisterNode(ka_locatorManipId)
    except:
        print "Failed to deregister node: %s" % ka_locatorManipName
        raise

#UTILS
def degreesToRadians( degrees ):
    return degrees * ( math.pi / 180.0 )
     
def radiansToDegrees( radians ):
    return radians * (180.0 / math.pi)
