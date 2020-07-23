#====================================================================================
#====================================================================================
#
# ka_shapes
#
# DESCRIPTION:
#   a module for creating and manipulating maya shapes
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

import maya.OpenMaya as OpenMaya
import pymel.core as pymel
import maya.cmds as cmds
import maya.mel as mel

import ka_maya.ka_pymel as ka_pymel
import ka_maya.ka_math as ka_math

NURBSCURVE_SHAPES = ('cube',
                     'circle',
                     'square',
                     'cube',
                     'pyramidPointer',
                     'left',
                     'right',
                     'center',
                     'peg',
                     'wrench',
                     'house',
                     'fourCorners')


# ========================================================================================================================================
def createNurbsCurve(shape, name=None, pointAt='y', size=1, scale=None):

    if shape == "cube":
        transform = pymel.curve( p=[(-0.5, -0.5, 0.5), (-0.5, -0.5, -0.5), (0.5, -0.5, -0.5), (0.5, -0.5, 0.5), (-0.5, -0.5, 0.5), (-0.5, 0.5, 0.5), (0.5, 0.5, 0.5), (0.5, -0.5, 0.5), (0.5, 0.5, 0.5), (0.5, 0.5, -0.5), (-0.5, 0.5, -0.5), (-0.5, 0.5, 0.5), (-0.5, 0.5, -0.5), (-0.5, -0.5, -0.5), (0.5, -0.5, -0.5), (0.5, 0.5, -0.5)], degree=1)

    elif shape == "circle":
        transform = pymel.curve( p=[(2.3991186704999999e-17, 0.39180581245000001, -0.39180581245000001), (-3.8708546040000001e-33, 0.55409709399999996, 6.321585305e-17), (-2.3991186704999999e-17, 0.39180581245000001, 0.39180581245000001), (-3.3928661614999998e-17, 1.6056347535000001e-16, 0.55409709399999996), (-2.3991186704999999e-17, -0.39180581245000001, 0.39180581245000001), (-1.02233679e-32, -0.55409709399999996, 1.669602682e-16), (2.3991186704999999e-17, -0.39180581245000001, -0.39180581245000001), (3.3928661614999998e-17, -2.9760662995000001e-16, -0.55409709399999996)], degree=3)
        closeCurve = True

    elif shape == "square":
        transform = pymel.curve( p=[(0.0, -0.5, 0.5), (0.0, -0.5, -0.5), (0.0, 0.5, -0.5), (0.0, 0.5, 0.5), (0.0, -0.5, 0.5)], degree=1)

    elif shape == "pyramidPointer":
        transform = pymel.curve( p=[(0.5, -1.0, 0.0), (0.0, -1.0, -0.5), (-0.5, -1.0, 0.0), (0.0, -1.0, 0.5), (0.5, -1.0, 0.0), (0.0, 0.0, 0.0), (-0.5, -1.0, 0.0), (0.0, -1.0, -0.5), (0.0, 0.0, 0.0), (0.0, -1.0, 0.5)], degree=1)

    elif shape == 'left':
        transform = pymel.curve( p=[(0.0, 0.50000000000000011, 0.27409390948864532), (0.0, -0.50000000000000011, 0.27409390948864532), (0.0, -0.50000000000000011, -0.36169014866651744), (0.0, -0.25147407344080469, -0.36169014866651744), (0.0, -0.25147407344080469, 0.015250915494142647), (0.0, 0.50000000000000011, 0.015250915494142647), (0.0, 0.50000000000000011, 0.27409390948864532)], degree=1)

    elif shape == 'right':
        transform = pymel.curve( p=[(0.0, -0.50000000000000011, 0.34701017465534501), (0.0, 0.50000000000000011, 0.34701017465534501), (0.0, 0.50000000000000011, -0.15298982534465544), (0.0, 0.3450397241816891, -0.29255616902419646), (0.0, 0.092304523700337093, -0.29255616902419646), (0.0, -0.086315998719090292, -0.15298982534465544), (0.0, -0.50000000000000011, -0.39534458727270605), (0.0, -0.50000000000000011, -0.15298982534465544), (0.0, -0.086315998719090292, 0.098623991834074776), (0.0, -0.50000000000000011, 0.098623991834074665), (0.0, -0.50000000000000011, 0.34701017465534501)], degree=1)

    elif shape == 'center':
        transform = pymel.curve( p=[(0.0, 0.15262777599595378, -0.50000000000000044), (0.0, 0.5, -0.50000000000000044), (0.0, 0.5, 0.0), (0.0, 0.15262777599595378, 0.26231195721027145), (0.0, -0.18544782982303926, 0.26231195721027145), (0.0, -0.5, 0.0), (0.0, -0.5, -0.50000000000000044), (0.0, -0.18544782982303926, -0.50000000000000044), (0.0, -0.18544782982303926, -0.086059463768694888), (0.0, 0.15262777599595378, -0.086059463768694888), (0.0, 0.15262777599595378, -0.50000000000000044)], degree=1)

    elif shape == 'wrench':
        transform = pymel.curve( p=[(0.4554875238899897, -0.060676712358602558, 1.3877787807814457e-16), (0.33413409917278608, -0.060676712358602558, 2.7755575615628914e-17), (0.33413409917278608, 0.060676712358601476, 2.7755575615628914e-17), (0.4554875238899897, 0.060676712358601476, 1.3877787807814457e-16), (0.4554875238899897, 0.12135342471720351, 1.3877787807814457e-16), (0.39481081153138703, 0.18203013707580476, 8.3266726846886741e-17), (0.27345738681418469, 0.18203013707580476, 0.0), (0.21278067445558399, 0.062477221441455788, 0.0), (-0.21278067445558158, 0.062477221441455788, -5.5511151231257827e-17), (-0.27345738681418374, 0.18203013707580473, -1.1102230246251565e-16), (-0.39481081153138731, 0.18203013707580476, 0.0), (-0.45548752388998981, 0.12135342471720353, 8.3266726846886741e-17), (-0.45548752388998981, 0.060676712358601476, 5.5511151231257827e-17), (-0.33413409917278569, 0.060676712358601503, 8.3266726846886741e-17), (-0.33413409917278569, -0.060676712358602558, 8.3266726846886741e-17), (-0.45548752388998981, -0.060676712358602558, 5.5511151231257827e-17), (-0.45548752388998981, -0.12135342471720456, 8.3266726846886741e-17), (-0.39481081153138731, -0.1820301370758059, -5.5511151231257827e-17), (-0.27345738681418374, -0.18203013707580584, -1.1102230246251565e-16), (-0.21278067445558158, -0.062477221441456898, -5.5511151231257827e-17), (0.21278067445558399, -0.062477221441456898, 0.0), (0.27345738681418469, -0.1820301370758059, -5.5511151231257827e-17), (0.39481081153138703, -0.18203013707580595, 8.3266726846886741e-17), (0.4554875238899897, -0.12135342471720456, 1.3877787807814457e-16), (0.4554875238899897, -0.060676712358602558, 1.3877787807814457e-16)], degree=1)

    elif shape == 'peg':
        transform = pymel.curve( p=[(0.0, -0.5, 0.5), (0.0, -0.5, -0.5), (1.0, -0.30902348578491962, -0.30902348578491962), (1.0, -0.30902348578491962, 0.30902348578491962), (0.0, -0.5, 0.5), (0.0, 0.5, 0.5), (1.0, 0.30902348578491962, 0.30902348578491962), (1.0, -0.30902348578491962, 0.30902348578491962), (1.0, 0.30902348578491962, 0.30902348578491962), (1.0, 0.30902348578491962, -0.30902348578491962), (0.0, 0.5, -0.5), (0.0, 0.5, 0.5), (0.0, 0.5, -0.5), (0.0, -0.5, -0.5), (1.0, -0.30902348578491962, -0.30902348578491962), (1.0, 0.30902348578491962, -0.30902348578491962)], degree=1)

    elif shape == 'cubePeg':
        transform = pymel.curve( p=[(0.0, -0.5, 0.5), (0.0, -0.5, -0.5), (1.0, -0.5, -0.5), (1.0, -0.5, 0.5), (0.0, -0.5, 0.5), (0.0, 0.5, 0.5), (1.0, 0.5, 0.5), (1.0, -0.5, 0.5), (1.0, 0.5, 0.5), (1.0, 0.5, -0.5), (0.0, 0.5, -0.5), (0.0, 0.5, 0.5), (0.0, 0.5, -0.5), (0.0, -0.5, -0.5), (1.0, -0.5, -0.5), (1.0, 0.5, -0.5)], degree=1)

    elif shape == 'house':
        transform = pymel.curve( p=[(0.0, -0.5, 0.5), (0.0, 0.375, 0.5), (0.0, 0.625, 0.0), (0.0, 0.375, -0.5), (0.0, -0.5, -0.5), (0.0, -0.5, 0.5)], degree=1)

    elif shape == 'fourCorners':
        transform = pymel.curve( p=[(-4.000000000000001, -0.1359356208343714, 3.0000000000000036), (-4.0, -0.13593562083437133, 4.000000000000004), (-3.0, -0.13593562083437133, 4.000000000000004), (-3.0, 0.13593562083437133, 4.000000000000004), (-4.0, 0.13593562083437133, 4.000000000000004), (-3.999999999999999, 0.13593562083437133, 3.0000000000000036), (-4.000000000000001, -0.1359356208343714, 3.0000000000000036)], degree=1)
        transformB = pymel.curve( p=[(-3.000000000000002, -0.1359356208343714, -4.000000000000002), (-4.000000000000003, -0.13593562083437133, -4.000000000000002), (-4.0000000000000036, -0.13593562083437133, -3.0000000000000013), (-4.0000000000000036, 0.13593562083437133, -3.0000000000000013), (-4.000000000000003, 0.13593562083437133, -4.000000000000002), (-3.000000000000002, 0.13593562083437133, -4.000000000000001), (-3.000000000000002, -0.1359356208343714, -4.000000000000002)], degree=1)
        transformC = pymel.curve( p=[(4.000000000000003, -0.1359356208343714, -3.0000000000000018), (4.000000000000002, -0.13593562083437133, -4.000000000000003), (3.0000000000000018, -0.13593562083437133, -4.000000000000003), (3.0000000000000018, 0.13593562083437133, -4.000000000000003), (4.000000000000002, 0.13593562083437133, -4.000000000000003), (4.000000000000002, 0.13593562083437133, -3.0000000000000018), (4.000000000000003, -0.1359356208343714, -3.0000000000000018)], degree=1)
        transformD = pymel.curve( p=[(3.0000000000000027, -0.1359356208343714, 4.000000000000002), (4.0000000000000036, -0.13593562083437133, 4.000000000000001), (4.0000000000000036, -0.13593562083437133, 3.000000000000001), (4.0000000000000036, 0.13593562083437133, 3.000000000000001), (4.0000000000000036, 0.13593562083437133, 4.000000000000001), (3.0000000000000027, 0.13593562083437133, 4.000000000000001), (3.0000000000000027, -0.1359356208343714, 4.000000000000002)], degree=1)
        shapeParent(transformB, transform)
        shapeParent(transformC, transform)
        shapeParent(transformD, transform)




    if pointAt == '-y' or pointAt == [0,-1, 0]:
        transform.rx.set(180)

    elif pointAt == 'z' or pointAt == [0, 0, 1]:
        transform.rx.set(90)

    elif pointAt == '-z' or pointAt == [0, 0, -1]:
        transform.rx.set(-90)

    elif pointAt == 'x' or pointAt == [1, 0, 0]:
        transform.rz.set(-90)

    elif pointAt == '-x' or pointAt == [-1, 0, 0]:
        transform.rz.set(90)

    if size:
        transform.s.set(size, size, size)
        pymel.makeIdentity(transform, apply=True, t=0, r=1, s=1)

    if scale:
        transform.s.set(scale[0], scale[1], scale[2])
        pymel.makeIdentity(transform, apply=True, t=0, r=1, s=1)

    if not name:
        name = shape
    transform.rename(name)

    return transform


# ========================================================================================================================================
def polyTetrahedron(pointPositions=[[-1.0, 0.0, 0.0], [0.73444569110870361, 0.0, 1.0], [0.13706603646278381, 1.0, -0.0041212271898984909], [0.73444569110870361, 0.0, -1.0]]):

    numFaces = 4
    numVertices = 4

    faceCounts = OpenMaya.MIntArray()
    for i in [3, 3, 3, 3]: faceCounts.append(i)

    faceConnects = OpenMaya.MIntArray()
    for i in [0, 1, 2, 0, 2, 3, 0, 3, 1, 1, 3, 2]:
        faceConnects.append(i)

    points = OpenMaya.MFloatPointArray()
    for pointPosition in pointPositions:
        points.append(OpenMaya.MFloatPoint( *pointPosition ))

    meshFS = OpenMaya.MFnMesh()
    newMesh = meshFS.create(numVertices, numFaces, points, faceCounts, faceConnects, OpenMaya.MObject())
    meshFS.updateSurface()
    nodeName = meshFS.name()
    cmds.sets (nodeName, e=True, fe='initialShadingGroup')


# ========================================================================================================================================
def shapeParent(objectA, objectB):

    shapeObj = pymel.parent(objectA, objectB)
    pymel.makeIdentity(shapeObj[0], apply=True, t=1, r=1, s=1, n=1)
    shapes = pymel.listRelatives(shapeObj[0], shapes=True)

    for shape in shapes:
        pymel.parent(shape, objectB, shape=True, add=True)

    pymel.delete(shapeObj)
    pymel.select(objectB)


# ========================================================================================================================================
def shrinkWrapShape(shapesToShrink=None, shapeToCollide=None):
    print 'shrink it'

    if shapesToShrink == None or shapeToCollide == None:
        selection = pymel.ls(selection=True)
        shapesToShrink = []
        for item in selection[:-1]:
            shapesToShrink.append(ka_pymel.getAsShape(item))

        shapeToCollide = ka_pymel.getAsShape(selection[-1])

    for shape in shapesToShrink:
        positions = []

        for cv in shape.cv:
            print cv
            position = cv.getPosition(space='world')
            positions.append(position)

        averagePositon = ka_math.average(positions)

        for i, cv in enumerate(shape.cv):
            direction = averagePositon - positions[i]
            didHit, pointsOfCollision, facesOfCollision = shapeToCollide.intersect(positions[i], direction, tolerance=.0001, space='world')

            if pointsOfCollision:
                cv.setPosition(pointsOfCollision[0], space='world')



# ========================================================================================================================================
def print_createShape_nurbsCurve(inCurves=None, shortVersion=False):
    curves = []
    if not inCurves:
        inCurves = pymel.ls(selection=True, objectsOnly=True)
    elif not isinstance(inCurves, list):
        inCurves = [inCurves]

    for inCurve in inCurves:
        if isinstance(inCurve, pymel.nt.NurbsCurve):
            curves.append(inCurve)
        elif ka_pymel.isPyTransform(inCurve):
            for shape in inCurve.getShapes():
                if isinstance(shape, pymel.nt.NurbsCurve):
                    curves.append(shape)

    printString = "import ka_maya.ka_shapes as ka_shapes\n"

    for curve in curves:
        name = curve.nodeName()
        parent = None

        points = []
        for cv in curve.cv:
            point = cv.getPosition()
            points.append((round(point[0], 6), round(point[1], 6), round(point[2], 6),))

        points = tuple(points)

        knots = tuple(curve.getKnots())

        degree = curve.degree()

        form = curve.form().index

        printString += """
ka_shapes.createShape_nurbsCurve(%s, %s, %s, %s, False, False,
                                 name='%s', parent=%s)
""" % (str(points), str(knots), str(degree), str(form), name, str(parent))
        print printString

    return printString


# ========================================================================================================================================
def createShape_nurbsCurve(points, knots, degree, form, create2D, createRational, name=None, parent=None,):
    """
    Creates a curve from the given parameters. These inputs are usually generated from the print_createShape_curve function.
    """

    if not parent:
        parentMObject = OpenMaya.MObject()
    else:
        if not ka_pymel.isPyTransform(parent):
            parent=pymel.PyNode(parent)

        parentMObject = parent.__apimobject__()

    if not name and parent:
        name = parent.nodeName()+'Shape'

    knots_MDoubleArray = OpenMaya.MDoubleArray()
    for i in knots: knots_MDoubleArray.append(i)

    points_MPointArray = OpenMaya.MPointArray ()
    for point in points: points_MPointArray.append(OpenMaya.MPoint(point[0], point[1], point[2], 0.0))

    nurbsFS = OpenMaya.MFnNurbsCurve()
    newMesh = nurbsFS.create(points_MPointArray, knots_MDoubleArray, degree, OpenMaya.MFnNurbsCurve.kOpen, create2D, createRational, parentMObject)
    nurbsFS.updateCurve()

    if name:
        curve = cmds.rename(nurbsFS.name(), name)
    else:
        curve = nurbsFS.name()

    return curve


# ========================================================================================================================================
def print_createShape_mesh(inMeshs=None, shortVersion=False):
    """
    Prints the code nessisary to recreate the given polygon
    """

    meshes = []
    if not inMeshs:
        inMeshs = pymel.ls(selection=True, objectsOnly=True)
    elif not isinstance(inMeshs, list):
        inMeshs = [inMeshs]

    for inMesh in inMeshs:
        if isinstance(inMesh, pymel.nt.Mesh):
            meshes.append(inMesh)
        elif ka_pymel.isPyTransform(inMesh):
            for shape in inMesh.getShapes():
                if isinstance(shape, pymel.nt.Mesh):
                    meshes.append(shape)

    printString = "import ka_maya.ka_shapes as ka_shapes\n"

    for mesh in meshes:
        name = mesh.nodeName()
        parent = None

        points = []
        for point in mesh.getPoints():
            points.append((point[0], point[1], point[2],))
        points = tuple(points)

        numVertices = len(points)

        numFaces = len(mesh.f.indices())

        faceCounts = []
        faceConnects = []
        for i, face in enumerate(mesh.f):
            verts = face.getVertices()
            faceCounts.append(len(verts))
            faceConnects.extend(verts)
        faceCounts = tuple(faceCounts)
        faceConnects = tuple(faceConnects)


        hardEdges = []
        for edge in mesh.e:
            if not edge.isSmooth():
                hardEdges.append(edge.index())
        hardEdges = tuple(hardEdges)

        if shortVersion:
            printString += """
ka_shapes.createShape_mesh(%s, %s, %s, %s, %s, %s,
                           name='%s', parent=%s)
""" % (str(numVertices), str(numFaces), str(faceCounts), str(faceConnects), str(points), str(hardEdges), name, str(parent))
            print printString
            return printString

        else:
            printString = """
# Create Mesh ------------------------
import maya.OpenMaya as OpenMaya

numFaces = %s
numVertices = %s

faceCounts = OpenMaya.MIntArray()
for i in %s: faceCounts.append(i)

faceConnects = OpenMaya.MIntArray()
for i in %s: faceConnects.append(i)

points = OpenMaya.MFloatPointArray()
for point in %s: points.append(OpenMaya.MFloatPoint( *point ))

meshFS = OpenMaya.MFnMesh()
newMesh = meshFS.create(numVertices, numFaces, points, faceCounts, faceConnects, OpenMaya.MObject())
for edge in %s:
    meshFS.setEdgeSmoothing(edge, False)
meshFS.updateSurface()
nodeName = meshFS.name()
maya.cmds.sets (nodeName, e=True, fe='initialShadingGroup')
# -----------------------------------
            """ % (str(numFaces), str(numVertices), str(faceCounts), str(faceConnects), str(points), str(hardEdges))
            print printString
            return printString


# ========================================================================================================================================
def createShape_mesh(numVertices, numFaces, faceCounts, faceConnects, points, hardEdges, name=None, parent=None):
    """
    Creates a mesh from the given parameters. These inputs are usually generated from the print_createShape_mesh function.
    """

    if not parent:
        parentMObject = OpenMaya.MObject()
    else:
        if not ka_pymel.isPyTransform(parent):
            parent=pymel.PyNode(parent)

        parentMObject = parent.__apimobject__()

    if not name and parent:
        name = parent.nodeName()+'Shape'

    faceCounts_MintArray = OpenMaya.MIntArray()
    for i in faceCounts: faceCounts_MintArray.append(i)

    faceConnects_MIntArray = OpenMaya.MIntArray()
    for i in faceConnects: faceConnects_MIntArray.append(i)

    points_MFloatPointArray = OpenMaya.MFloatPointArray()
    for point in points: points_MFloatPointArray.append(OpenMaya.MFloatPoint( *point ))

    meshFS = OpenMaya.MFnMesh()
    newMesh = meshFS.create(numVertices, numFaces, points_MFloatPointArray, faceCounts_MintArray, faceConnects_MIntArray, parentMObject)
    #for edge in hardEdges:

        #meshFS.setEdgeSmoothing(edge, False)
    meshFS.updateSurface()

    if name:
        mesh = cmds.rename(meshFS.name(), name)
    else:
        mesh = meshFS.name()

    hardEdgesStrings = []
    for edge in hardEdges:
        hardEdgesStrings.append('%s.e[%s]' % (mesh, str(edge)))

    cmds.sets(mesh, e=True, fe='initialShadingGroup')
    cmds.polySoftEdge(*hardEdgesStrings, ch=0, a=0)

    return pymel.PyNode(mesh)







# -----------------------------------------------------------------------
browAttrs = ('brow', (('UD', ('UD', 'UD_#',)),
                      ('LR', ('LR', 'LR_#',)),
                      ('FB', ('FB', 'FB_#',)),
                      ('TW', ('TW', 'TW_#',)),
                      ),
             )


# -----------------------------------------------------------------------
eyeAttrs = ('eyelids', ('UD',
                        'LR',
                        'TW',
                        ('upperLid', ('UD',
                                      'UD_#',
                                      'LR',
                                      'LR_#',
                                      'TW',
                                      'TW_#',
                                      ),
                         ),
                        ('lowerLid', ('UD',
                                      'UD_#',
                                      'LR',
                                      'LR_#',
                                      'TW',
                                      'TW_#',
                                      ),
                         ),
                        ('squint', ('UD',
                                    'UD_#',
                                    'LR',
                                    'LR_#',
                                    'FB',
                                    'FB_#',
                                    'TW',
                                    'TW_#',
                                    ),
                         ),
                        ),
            )


# -----------------------------------------------------------------------
noseAttrs = ('nose', ('UD',
                      'LR',
                      'FB',
                      'TW',
                      'bend_UD',
                      'bend_LR',
                      'bend_FB',
                      'bend_TW',
                      'sneer_L',
                      'sneer_R',
                      'flair_L',
                      'flair_R',
                      ),
             )


# -----------------------------------------------------------------------
lipAttrs = ('lips', ('upper', (('UD', ('UD', 'UD_#',)),
                               ('LR', ('LR', 'LR_#',)),
                               ('FB', ('FB', 'FB_#',)),
                               ),
                     ),
            ('lower', (('UD', ('UD', 'UD_#',)),
                       ('LR', ('LR', 'LR_#',)),
                       ('FB', ('FB', 'FB_#',)),
                       ),
             ),
            )

mouthAttrs = ('mouth', ('jaw_UD',
                        'jaw_LR',
                        'jaw_FB',
                        'jaw_TW',
                        'jaw_jutt',
                        'jaw_drop',
                        'mouth_UD',
                        'mouth_LR',
                        'mouth_FB',
                        'mouth_TW',
                        'corner_L_UD',
                        'corner_R_UD',
                        'corner_L_LR',
                        'corner_R_LR',
                        'corner_L_FB',
                        'corner_R_FB',
                        'corner_L_TW',
                        'corner_R_TW',
                        ),
              )







