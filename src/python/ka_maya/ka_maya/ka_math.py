#====================================================================================
#====================================================================================
#
# ka_math
#
# DESCRIPTION:
#   A collection of mathmatical functions
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

import math


import pymel.core as pymel
import maya.cmds as cmds
import maya.mel as mel

import ka_maya.ka_python as ka_python #;reload(ka_python)


def average(*values):
    if len(values) == 1:
        values = values[0]

    if isinstance(values, list) or isinstance(values, tuple):
        sumOfValues = sum_(values)

        lenOfValues = len(values)

        # 1D item
        if isinstance(sumOfValues, float):
            return sumOfValues / lenOfValues

        # nD items
        else:
            average = []
            for i, value in enumerate(sumOfValues):
                average.append(value / lenOfValues)

            return average


def getMidpoint(points):
    """Return Mid poitn of given points
    Args:
        points - list of lists - a list of points, with each point being a list of values (ie: 3 values
                 for a 3d point 2 values for a 2d point
    """
    numOfPoints = len(points)
    midPoint = []

    dimensions = len(points[0])
    sums = []
    for each in range(dimensions): sums.append(0.0)

    for point in points:
        for i, n in enumerate(sums):
            sums[i] += point[i]

    for i, n in enumerate(sums): sums[i] /= 2.0


    return sums



def distanceBetween(pointA, pointB):
    '''returns distance between a list of 2d or 3d coordinates'''
    sum = 0
    for i, each in enumerate(pointA):
        sum += (pointA[i] - pointB[i])**2

    return math.sqrt( sum )

def getVolumeOfTetrahedron(points):
    """takes 4 points, and returns the volume the tetrahedron it forms"""
    vectorA = subtractVectors(points[1], points[0])
    vectorB = subtractVectors(points[2], points[0])
    vectorC = subtractVectors(points[3], points[0])
    return (abs(dotProduct(vectorA, crossProduct(vectorB, vectorC))) / 6)

def getVolume(points):
    numbOfPoints = len(points)
    if numbOfPoints == 4:
        return getVolumeOfTetrahedron(points)


def crossProduct(a, b):
    c = [a[1]*b[2] - a[2]*b[1],
         a[2]*b[0] - a[0]*b[2],
         a[0]*b[1] - a[1]*b[0]]

    return c

def magnitudeOfVector(v):
    return math.sqrt(sum(v[i]*v[i] for i in range(len(v))))

def normalizeVector(v):
    '''normalize vector'''
    vmag = magnitudeOfVector(v)
    if vmag == 0:
        return [0 for i in range(len(v)) ]
    else:
        return [ v[i]/vmag  for i in range(len(v)) ]

def addVectors(u, v):
    '''add vector'''
    return [ u[i]+v[i] for i in range(len(u)) ]

def subtractVectors(u, v):
    '''subtract Vector'''
    return [ u[i]-v[i] for i in range(len(u)) ]

def multiplyVectors(u, m):
    '''multiply Vector u by value m'''
    return [ u[i]*m for i in range(len(u)) ]

def dotProduct(u, v):
    return sum(u[i]*v[i] for i in range(len(u)))

def averageVectors(u, v):
    return [ (u[i]+v[i])/2 for i in range(len(u)) ]

def sum_(*values):

    # parse args
    if len(values) == 1:
        values = values[0]

    # if values is a list of numbers
    if isinstance(values[0], float) or isinstance(values[0], int):
        return sum(values)

    # values are lists (ie vectors)
    summedValues = []
    for subValue in (values[0]):
        if isinstance(subValue, float):
            summedValues.append(0.0)

        if isinstance(subValue, int):
            summedValues.append(0)

    for value in values:
        for i, subValue in enumerate(value):
            summedValues[i] += subValue

    return summedValues

def add(a, b):
    return sum_(a, b)

def subtract(a, b):
    if isinstance(a, list) or isinstance(a, tuple): return subtractVectors(a, b)
    else: return a - b

def multiply(a, b):
    if isinstance(a, list) or isinstance(a, tuple):
        if isinstance(b, list) or isinstance(b, tuple):
            #return multiplyVectors(a, b)
            return [ (a[i]*b[i]) for i, n in enumerate(a) ]

        else:
            return [ (b*i) for i in a ]

    else:
        return a * b

def angleBetween(vector1, vector2):
    r = math.acos(dotProduct(vector1, vector2) / (magnitudeOfVector(vector1) * magnitudeOfVector(vector2)))
    return math.degrees(r)

def normalize(v):
    if isinstance(v, list) or isinstance(v, tuple): return normalizeVector(v)

#def getDeterminant(a):
    #lenA = len(a)
    #a.append(a[0])
    #a.append(a[1])
    #x = 0
    #for i in range(lenA-2):
        #y=1
        #for j in range(lenA-2):
            #y *= a[i+j][j]
        #x += y

    #p = 0
    #for i in range(lenA-2):
        #y=1;
        #z = 0;
        #for j in range(2, -1, -1):
            #y *= a[i+z][j]
            #z+=1
        #z += 1
        #p += y

    #return x - p

def getDeterminant(matrix):
    lenOfMatrix = len(matrix) # rows
    if lenOfMatrix > 2:
        factor = 1 # flips between neg and pos
        iA=0
        determinant=0

        while iA <= lenOfMatrix-1:
            d={}
            iB=1

            while iB <= lenOfMatrix-1:
                iC=0
                d[iB]=[]
                while iC<=lenOfMatrix-1:
                    if (iC==iA):
                        u=0
                    else:
                        d[iB].append(matrix[iB][iC])
                    iC+=1
                iB+=1

            matrixB=[d[x] for x in d]
            determinant = sum(determinant, (multiply(factor, multiply(matrix[0][iA], getDeterminant(matrixB), ))))

            factor *= -1
            i += 1

        return determinant


    else:
        return subtract(multiply(matrix[0][0], matrix[1][1]), multiply(matrix[0][1],matrix[1][0]))

#def getDeterminant(matrix):
    #lenOfMatrix = len(matrix) # rows
    #factor = 1
    #for i in range(lenOfMatrix):
        #pass

pass

#def dete(a):
   #x = (a[0][0] * a[1][1] * a[2][2]) + (a[1][0] * a[2][1] * a[3][2]) + (a[2][0] * a[3][1] * a[4][2])
   #y = (a[0][2] * a[1][1] * a[2][0]) + (a[1][2] * a[2][1] * a[3][0]) + (a[2][2] * a[3][1] * a[4][0])

   #return x - y

#def sum():
    #pass

#def dete(a):
    #dimentions = len(a)
    #output = []
    #for i in range(dimentions):
        #row = []
        #for i in range(dimentions):
            #row.append(None)
        #output.append(row)


    #for ia in range(dimentions):

   #x =

   #y = (a[0][2] * a[1][1] * a[2][0]) + (a[1][2] * a[2][1] * a[3][0]) + (a[2][2] * a[3][1] * a[4][0])

   #return x - y
#[0,1,2
 #0,1,2
 #0,1,2]

#def getBarycentricCoordinates(simplex, point):
    #barycentricCoordinates = []
    #dimentions = len(point)
    #pointsInSimplex = len(simplex)
    #lastSimplexIndex = pointsInSimplex-1

    #matrix = []
    #for rowIndex in range(dimentions):
        #column = []
        #for columnIndex in range(pointsInSimplex):
            #if columnIndex != lastSimplexIndex:
                #vector = subtractVectors(simplex[columnIndex], simplex[lastSimplexIndex])
                #column.append(vector)
        #matrix.append(column)

    #print matrix
    #determinant = getDeterminant(matrix)

    #return determinant

def getBarycentricCoordinates(simplex, point):
    barycentricCoordinates = []
    dimentions = len(point)
    pointsInSimplex = len(simplex)
    lastSimplexIndex = pointsInSimplex-1

    if dimentions == 3:
        total_volume = getVolumeOfTetrahedron((simplex[0], simplex[1], simplex[2], simplex[3]))
        tetraA_volume = getVolumeOfTetrahedron((simplex[1], simplex[2], simplex[3], point))
        tetraB_volume = getVolumeOfTetrahedron((simplex[0], simplex[2], simplex[3], point))
        tetraC_volume = getVolumeOfTetrahedron((simplex[0], simplex[1], simplex[3], point))
        tetraD_volume = getVolumeOfTetrahedron((simplex[0], simplex[1], simplex[2], point))

        barycentricCoordinates = ((tetraA_volume/total_volume), (tetraB_volume/total_volume), (tetraC_volume/total_volume), (tetraD_volume/total_volume), )

        return barycentricCoordinates

#def tetrahedralizePoints(points):
    #tetrahedrons = []
    #tetrahedron = []

    #solvedTetrahedrons = {}
    #unsolvedTetrahedrons = {}

    #unsolvedPoints = {}
    #solvedPoints = {}
    #pointDict = {}
    #for i, point in enumerate(points):
        #pointDict[i] = point
        #unsolvedPoints[i] = None

    #currentTetra = (0,1,2,3)
    #while currentTetra:
        #for i in unsolvedPoints:
            #barryWeights = getBarycentricCoordinates([pointDict[currentTetra[0]], pointDict[currentTetra[1]], pointDict[currentTetra[2]], pointDict[currentTetra[3]]], pointDict[i])

            ## a point is inside the current tetra
            #if barryWeight[0] + barryWeights[1] + barryWeights[2] + barryWeights[3] <= 1:
                #pass

            #else:
                #solvedTetrahedrons.append(currentTetra)

    #for i in range(4):
        #tetrahedron.append(points[i])
    #tetrahedrons.append(tetrahedron)

    #return tetrahedrons


def testA():
    cmds.file(newFile=True, force=True)
    points = [[-0.9609970484, 0.365637511932, 2.22360586626],
               [-0.674784755617, 0.125772274035, -4.97449767664],
               [2.02942906326, 5.11446127606, -4.7692572918],
               [-4.56076916929, 5.15592487068, -4.58305108432],]

    for point in points:
        loc = pymel.spaceLocator()
        loc.t.set(point)

    interiorPoint = [-1.18105510866, 1.84263103104, -2.69437256414]
    loc = pymel.spaceLocator()
    loc.t.set(interiorPoint)

    print getBarycentricCoordinates(points, interiorPoint)


def vectorProduct(input1, input2, operation, normalizeOutput=False):
    if operation in ['dotproduct', 'dotProduct', 1]:
        result = sum([ input1[i] * input2[i] for i in range(len(input1))])
    elif operation in ['crossproduct', 'crossProduct', 2]:
        a = newVector(a=input1)
        b = newVector(a=input2)
        result = a ^ b
    elif operation in ['vectormatrixproduct', 'vectorMatrixProduct', 3]:
        a = newVector(a=input1)
        mat = getWorldMat(input2)
        result = a * mat
    elif operation in ['pointmatrixproduct', 'pointMatrixProduct', 4]:
        a = newPoint(a=input1)
        mat = getWorldMat(input2)
        result = a * mat
    else:
        result = 0

    if normalizeOutput:
        if isinstance(result, float):
            result = 1.0
        else:
            result.normalize()
    if not isinstance(result, float):
        result = (result.x, result.y, result.z)
    return result


def softenRange(value, minValue=0.0, maxValue=1.0):
    """takes a range and adds an ease in and ease out to it"""

    halfRange = (maxValue - minValue) * 0.5
    newValue = (0.5 * math.sin((2.0*math.pi*value*0.5)-math.radians(90))) + halfRange
    return newValue

def softenRange(value, minValue=0.0, maxValue=1.0):
    """takes a range and adds an ease in and ease out to it"""

    halfRange = (maxValue - minValue) * 0.5
    newValue = (maxValue * math.sin((math.radians(90.0/maxValue)*value)))
    return newValue


import math
def softenRange(value, minValue=0.0, maxValue=1.0):
    """takes a range and adds an ease in and ease out to it"""

    halfRange = (maxValue - minValue) * 0.5
    newValue = (maxValue * math.sin((math.radians(180.0/maxValue)*value + halfRange)))
    newValue *= 0.5
    newValue += halfRange

    return newValue

def softenRange(value, minValue=0.0, maxValue=1.0, d=1.0):
    t = value
    b = minValue
    c = maxValue

    t /= d/2.0
    if t < 1: return c/2*t*t*t + b
    t -= 2
    return c/2*(t*t*t + 2) + b

def easeInOut(value, minValue=0.0, maxValue=1.0, strength=3.0, easeIn=True, easeOut=True):
    value = float(value)
    maxValue = float(maxValue)
    minValue = float(minValue)
    strength = float(strength)

    change = maxValue - minValue
    percentOfMax = value/maxValue

    if easeIn and not easeOut:
        return change * math.pow(percentOfMax, strength) + minValue

    elif easeOut and not easeIn:
        return maxValue - (change * math.pow(1.0-percentOfMax, strength)) + minValue


    else:
        if value - minValue < change * 0.5:
            percentOfMax = value/(maxValue*0.5)
            change = change*0.5
            return change * math.pow(percentOfMax, strength) + minValue

        else:
            percentOfMax = (value-maxValue*0.5)/(maxValue*0.5)
            change = change*0.5
            return (maxValue*1.0) - (change * math.pow(1.0-percentOfMax, strength)) + minValue

def easeInOutBezier(x, p0, p1, p2, p3, minY=0.0, maxY=1.0):
    #value = float(value)
    #maxValue = float(maxValue)
    #minValue = float(minValue)
    #strength = float(strength)

    #change = maxValue - minValue
    #percentOfMax = value/maxValue

    #if easeIn and not easeOut:
        #return change * math.pow(percentOfMax, strength) + minValue

    #elif easeOut and not easeIn:
        #return maxValue - (change * math.pow(1.0-percentOfMax, strength)) + minValue

    yRange = float(maxY - minY)
    #print 'p', p0, p1, p2, p3,
    if x < p0:
        return minValue
    elif x > p3:
        return maxValue
    else:
        xRange = float(p3-p0)
        mid = p1 + ((p2-p1)*0.5)
        midPercent = mid/xRange
        relativeX = float(x-p0)
        if x < mid:
            strengthPercent = relativeX/(p2-p0)
            strength = (4.0*strengthPercent)+1

            percentOfMax = relativeX/(xRange*0.5)
            yRange *= 0.5

            #OOOOOOO = "xRange"; print '%s: ' % OOOOOOO, eval(OOOOOOO), ' ', type(eval(OOOOOOO))
            #OOOOOOO = "relativeX"; print '%s: ' % OOOOOOO, eval(OOOOOOO), ' ', type(eval(OOOOOOO))
            #OOOOOOO = "strength"; print '%s: ' % OOOOOOO, eval(OOOOOOO), ' ', type(eval(OOOOOOO))
            #OOOOOOO = "percentOfMax"; print '%s: ' % OOOOOOO, eval(OOOOOOO), ' ', type(eval(OOOOOOO))

            return yRange * math.pow(percentOfMax, strength) + minY

        else:
            midPercent = 1.0 - midPercent
            OOOOOOO = "midPercent"; print '%s: ' % OOOOOOO, eval(OOOOOOO), ' ', type(eval(OOOOOOO))
            strengthPercent = abs(float(x)-p3) / (p3-p1)
            strength = (4.0*strengthPercent)+1
            #OOOOOOO = "strength"; print '%s: ' % OOOOOOO, eval(OOOOOOO), ' ', type(eval(OOOOOOO))

            #percentOfMax = (value-maxValue*0.5)/(maxValue*0.5)
            #percentOfMax = (relativeX-(xRange*midPercent))/(xRange*midPercent)
            percentOfMax = (relativeX-mid)/(1.0-(xRange*midPercent))
            #change = change*0.5
            yRange *= midPercent
            OOOOOOO = "percentOfMax"; print '%s: ' % OOOOOOO, eval(OOOOOOO), ' ', type(eval(OOOOOOO))
            return (xRange*1.0) - (yRange * math.pow(1.0-percentOfMax, strength)) + minY



        #if value - minValue < change * 0.5:
            #return change * math.pow(value/maxValue, strength) + minValue

        #else:
            #return change * (maxValue - math.pow(maxValue - (value/maxValue), strength)) + minValue

def bezier(n,t, arcLengthParameter=True, previousT=0.0, precision=5):
    """returns a position along a bezier curve imagined by the
    input points:

    Args:
        n = the list of points
        t = the position along the curve to return

    """
    P0 = n[0]
    P1 = n[1]
    P2 = n[2]
    P3 = n[3]

    if arcLengthParameter:
        x = round((P0[0]*(1-t)**3+P1[0]*3*t*(1-t)**2+P2[0]*3*t**2*(1-t)+P3[0]*t**3), precision)
        sampleRange = [previousT, 1.0]
        targetX = round(t, precision)
        count = 0
        while x != targetX:
            t = sampleRange[0]+((sampleRange[1]-sampleRange[0])*0.5) # GET MID U VALUE OF SAMPLE
            x = round((P0[0]*(1-t)**3+P1[0]*3*t*(1-t)**2+P2[0]*3*t**2*(1-t)+P3[0]*t**3), precision)

            if x < targetX:
                sampleRange[0] = t
            elif x > targetX:
                sampleRange[1] = t
            else:
                break

            count += 1
            if count > 1000:
                print 'fail', sampleRange
                break
    u = t
    x=(P0[0]*(1-t)**3+P1[0]*3*t*(1-t)**2+P2[0]*3*t**2*(1-t)+P3[0]*t**3)
    y=(P0[1]*(1-t)**3+P1[1]*3*t*(1-t)**2+P2[1]*3*t**2*(1-t)+P3[1]*t**3)

    return x,y


#def f(n,t, arcLengthParameter=True, previousT=0.0):
    #P0 = n[0]
    #P1 = n[1]
    #P2 = n[2]
    #P3 = n[3]

    #if arcLengthParameter:
        #x = round((P0[0]*(1-t)**3+P1[0]*3*t*(1-t)**2+P2[0]*3*t**2*(1-t)+P3[0]*t**3), 3)
        #sampleRange = [previousT, 1.0]
        #targetT = t
        #count = 0
        #while round(x, 3) != targetT:
            #t = sampleRange[0]+((sampleRange[1]-sampleRange[0])*0.5) # GET MID U VALUE OF SAMPLE
            #x = round((P0[0]*(1-t)**3+P1[0]*3*t*(1-t)**2+P2[0]*3*t**2*(1-t)+P3[0]*t**3), 3)

            #if x < targetT:
                #sampleRange[0] = t
            #elif x > targetT:
                #sampleRange[1] = t
            #else:
                #break

            #count += 1
            #if count > 1000:
                #print 'fail', sampleRange
                #break
    #u = t
    #x=(P0[0]*(1-t)**3+P1[0]*3*t*(1-t)**2+P2[0]*3*t**2*(1-t)+P3[0]*t**3)
    #y=(P0[1]*(1-t)**3+P1[1]*3*t*(1-t)**2+P2[1]*3*t**2*(1-t)+P3[1]*t**3)

    #return x,y


#locs = pymel.ls('TEMP_LOCATOR*')
#if locs:
    #pymel.delete(locs)

#def nurbsFunc(x, p0=(0,0), p1=(1,1)):
    #pass

#p0 = (0.0, 0.0)
#p1 = (0.2, 0.0)
#p2 = (0.8, 1.0)
#p3 = (1.0, 1.0)
#numOfLocs = 100
#for i in range(numOfLocs+1):
    #loc = pymel.createNode('locator')
    #loc.localScaleX.set(.0)
    #loc.localScaleY.set(.01)
    #loc.localScaleZ.set(.01)
    #loc = loc.getParent()
    #loc.rename('TEMP_LOCATOR')
    #t = i*0.01

    #x,y = f((p0, p1, p2, p3), t)
    #loc.t.set(x,y,0)


# -----------------------------------------------------------------------------------------



#locs = pymel.ls('TEMP_LOCATOR*')
#if locs:
    #pymel.delete(locs)

#def nurbsFunc(x, p0=(0,0), p1=(1,1)):
    #pass

#P0 = (0.0, 0.0)
#P1 = (0.1, 0.0)
#P2 = (0.2, 1.0)
#P3 = (1.0, 1.0)


#paramUnit = .01
#targetX = 0.0+paramUnit

#import ka_maya.ka_math as ka_math
#points = [P0, P1, P2, P3]
#hullLength = 0.0
#polyLegths = []
#for i in range(4):
    #if i == 0:
        #polyLegths.append(0.0)
    #else:
        #length = ka_math.distanceBetween(points[i], points[i-1])
        #hullLength += length
        #polyLegths.append(hullLength)

#param = 0.0
#for i in range(101):
    #loc = pymel.createNode('locator')
    #loc.localScaleX.set(.0)
    #loc.localScaleY.set(.01)
    #loc.localScaleZ.set(.01)
    #loc = loc.getParent()
    #loc.rename('TEMP_LOCATOR')
    #x = i*0.01
    #loc.tx.set(x)

    ##targetC = previousU + paramUnit


    ##while round(currentU - targetU, 3) !=
    #u = (i/100.0) # PARAMETAR FOR CURVE

    #u = param
    ##x = (P0[0]*(1-u)**3+P1[0]*3*u*(1-u)**2+P2[0]*3*u**2*(1-u)+P3[0])*u**3#BERNSTAIN    POLYNOMS FOR X AND Y
    ##y = (P0[1]*(1-u)**3+P1[1]*3*u*(1-u)**2+P2[1]*3*u**2*(1-u)+P3[1]*u**3)

    #x=round((P0[0]*(1-u)**3+P1[0]*3*u*(1-u)**2+P2[0]*3*u**2*(1-u)+P3[0]*u**3), 3)
    #targetX = (i/100.0)
    #trys = 0
    #sampleRange = [u, 1.0]
    #while round(x, 3) != targetX:
        ##u = 0.00001
        #print 'u', u,
        #u = sampleRange[0]+((sampleRange[1]-sampleRange[0])*0.5) # GET MID U VALUE OF SAMPLE
        #x=round((P0[0]*(1-u)**3+P1[0]*3*u*(1-u)**2+P2[0]*3*u**2*(1-u)+P3[0]*u**3), 3)
        #print 'u'
        #trys += 1

        #if x < targetX:
            #sampleRange[0] = u
        #elif x > targetX:
            #sampleRange[1] = u
        #else:
            #break

        #if trys > 1000:
            #print 'over 1000'
            #break

    #print x, targetX
    #print 'trys', trys
    #param = u


    #x=(P0[0]*(1-u)**3+P1[0]*3*u*(1-u)**2+P2[0]*3*u**2*(1-u)+P3[0]*u**3)
    #y=(P0[1]*(1-u)**3+P1[1]*3*u*(1-u)**2+P2[1]*3*u**2*(1-u)+P3[1]*u**3)

    ##x1 = x+1 #THIS IS END OF THE LINE
    ##y1 = y+1

    ##y = sum(x+0.01])
    #loc.tx.set(x)
    #loc.ty.set(y)


def cartesianToPolarCoordinates(x,y, asDegrees=False):
    """Takes a 2d cartesian position and returns a polar coorinate (radius, angle)"""

    r = distanceBetween((0,0), (x,y))
    o = math.atan2(y, x)

    if o < 0:
        o = math.pi + (math.pi + o)

    if asDegrees:
        o = math.degrees(o)

    return (r, o)


def sort2DPointsClockwise(points, firstPoint=None):
    if firstPoint:
        angleOfFirstPoint = cartesianToPolarCoordinates(firstPoint[0], firstPoint[1])

    angleDict = {}
    for point in points:
        radius, angle = cartesianToPolarCoordinates(point[0]*-1, point[1])

        if firstPoint:
            if angle < angleOfFirstPoint:
                angle += math.pi*2

        angleDict[angle] = point

    orderedPoints = []
    for angle in sorted(angleDict):
        orderedPoints.append(angleDict[angle])

    return tuple(orderedPoints)