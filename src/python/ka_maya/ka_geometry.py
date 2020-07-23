#=======================================================================================
"""
@package ka_maya.ka_geometry

Functions related to Maya geometries.

The getComponentInfo is a very usefull function that returns
information on given/selected components, regarless of what types of geometry they are. The getStrandInfo is another
usefull function that organizes components into strands (a chain of connected components forming a line or curve).


Author:
    Kris Andrews (3dkris@gmail.com)

Todo:
    None

Pre:
    All code in this module is intended to be called from the embeded python interpreter
    within Autodesk Maya

"""
#=======================================================================================

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
#=======================================================================================

import re
import time

import maya.cmds as cmds
import maya.mel as mel
import pymel.core as pymel
import maya.OpenMaya as OpenMaya
import math
import copy

import ka_maya.ka_pymel as ka_pymel
import ka_maya.ka_clipBoard as ka_clipBoard
import ka_maya.ka_math as ka_math
import ka_maya.ka_cameras as ka_cameras
import ka_maya.ka_deformers as ka_deformers
import ka_maya.ka_transforms as ka_transforms

STRAND_INFO_DICT = None

#------------------------------------------------------------------------------------------------------------------------
def getStrandID(strand=None):
    """
    makes a string which can be used to represent a strand

    Takes a list of point and creates a string which (in the context of the shape) will
    uniquely identify that strand. This will generally be used as a dictionary key.

    Args:
        strand (list): a list of 1D indices

    Returns:
        string: a string representing the given strand

    Example:
        >>> import ka_maya.ka_geometry as ka_geometry
        >>> ka_geometry.getStrandID([0,3,5,7])
        '0:7'

    """

    if len(strand) == 1:
        return '%s:%s' % (str(strand[0]), str(strand[0]), )

    else:
        return '%s:%s' % (str(strand[0]), str(strand[-1]), )


#------------------------------------------------------------------------------------------------------------------------
def _getStrandInfoDictFromClipboard_(checkSelectionMatches=False):
    """gets the last strandInfoDict from the ka_clipboard, while optionaly checking it matches selection

    Args:
        checkSelectionMatches (bool): if True, will check that the dicitonary matches the current selection

    """

    #strandInfoDict = ka_clipBoard.get('strandInfoDict', None)
    global STRAND_INFO_DICT
    strandInfoDict = STRAND_INFO_DICT

    if strandInfoDict:

        if checkSelectionMatches:

            componentInfoDict = getComponentInfoDict(positions=False, normals=False, connectedPoints=False,
                                                     worldSpace=False, objectSpace=False, origSpace=False,
                                                     cameraSpace=False, componentInfoDict={})

            for shapeID in componentInfoDict:
                # check if shapes have changed
                if shapeID not in strandInfoDict:
                    return None

                # check if points have changed
                strandInfoPointDict = strandInfoDict[shapeID]['componentInfoDict']['pointDict']
                componentInfoPointDict = componentInfoDict[shapeID]['pointDict']
                if len(componentInfoPointDict) != len(strandInfoPointDict):
                    return None

                for point in componentInfoDict[shapeID]['pointDict']:
                    if point not in strandInfoPointDict:
                        return None

            # If nothing was found dispproving that they match, use it
            return strandInfoDict

        else:
            return strandInfoDict


#------------------------------------------------------------------------------------------------------------------------
def getStrandInfoDict(new=False, checkSelectionMatches=False):
    """
    Gets a informational dictionary about components organized into strands.

    Gets or creates a dictionary usually relating to selected components. This dictionary will have all the information
    relating to the given component's organization into strands. A Strand in this context is understood to be a series of
    connected points forming a line or curve. This function is not specific to geometry type, and will organize points on
    polygons, lattices, nurbs and nurbs curves. This function is also not limited to a single shape, and may contain multiple
    components of multiple shapes. All points are represented by a 1D index, if the multi index (of a nurbs for example) is
    required, it can be found in componentInfoDict assosiated with each shape (see getComponentInfoDict).

    Args:
        new (bool): if True, the function will not try to get the previously stored strandInfoDict, and will instead create
            a new one.

        checkSelectionMatches (bool): if True, and the arg "new" is not True, then this funciton will also check
            that the current selection matches the selection of the previously stored strandInfoDict. If it does not
            then it will create a new one.


    Returns:
        a dictionary with all the information accumulated about the stored strands and their relationships.
        the dictionary will be formatted as follows:

       strandInfoDict = {<shapeID>:{'selectedStrands':{'44:22':None,
                                                       '563:563':None,
                                                      },
                                    'strandDict':{'44:22':(44, 33, 22),
                                                  '563:563':(563, 333, 234),
                                                 },

                                    'strandOfPoint':{44:'44:22',
                                                     33:'44:22',
                                                     22:'44:22',
                                                    },

                                    'strandPoints':{44:None,
                                                    33:None,
                                                    22:None,
                                                   },

                                    'pointNeighbors':{44:{'up':(563, 584),
                                                          'down':(435, 345),
                                                          'left':(345),
                                                          'right':(234, 234),
                                                         },

                                    'strandNeighbors':{44:33:{'up':'22:55',
                                                              'down':'345:578',
                                                              'left':'22:55',
                                                              'right':'345:578',
                                                             },
                                                      },

                                    'componentInfoDict':{...},    # see getComponentInfoDict function

                                   },
                        }

    """

    # return from memory
    if not new:
        strandInfoDict = _getStrandInfoDictFromClipboard_(checkSelectionMatches=checkSelectionMatches)
        if strandInfoDict:
            return strandInfoDict

    #print 'new strandInfoDict'

    componentInfoDict = getComponentInfoDict()

    strandInfoDict = {}

    for shapeID in componentInfoDict:
        shape = componentInfoDict[shapeID]['pyShape']

        strandInfoDict[shapeID] = {}
        strandInfoDict[shapeID]['selectedStrands'] = {}
        strandInfoDict[shapeID]['strandDict'] = {}
        strandInfoDict[shapeID]['strandOfPoint'] = {}
        strandInfoDict[shapeID]['strandPoints'] = {}
        strandInfoDict[shapeID]['pointNeighbors'] = {}
        strandInfoDict[shapeID]['strandNeighbors'] = {}
        strandInfoDict[shapeID]['componentInfoDict'] = componentInfoDict[shapeID]


        strands = _indicesToStrands_(indexDict=componentInfoDict[shapeID]['pointDict'], componentInfoDict=componentInfoDict[shapeID])

        for strandID in strands:
            strand = strands[strandID]

            __addStrand__(strand, strandID=strandID, strandInfoDict=strandInfoDict[shapeID])

    __findPointNeighbors__(strandInfoDict)

    storeStrandInfoDict(strandInfoDict=strandInfoDict)

    return strandInfoDict


#------------------------------------------------------------------------------------------------------------------------
def _indicesToStrands_(indexDict=None, componentInfoDict=None, strandHeadsAndTails=None):
    """
    Sorts a randomly ordered set of points into strands.

    Takes a given set of points, and split it up into connected strands, and order's those strands start to
    end. The ordering of points will largely be based on their position in camera space. This fuction usually
    is only used for sorting the first strands, since any expansion of the strand selections will likely want to
    take into account the ording of their neighbors. An example of this would be pickwalking around a sphere, camera
    space would be reversed on the back of the sphere.

    Args:
        indexDict (dict): a dict of points which should be sorted into strands. All points of this dict are assumed
            to be from a single shape.

        componentInfoDict (dict): this is a subDictionary from the return of getComponentInfoDict, where the shapeID
            has already been specified. ie: componentInfoDict[243554]

        strandHeadsAndTails (tuple): this is a list of head/tail pairs that help to order strands that do not nessisarily
            have a start and end (such as a loop).

    Returns:
        dict: a dict where they key is the strandID, and the value is a tuple of ordered indices


    """


    indexDict = indexDict.copy()
    singlePointStrands = []

    # find strand head/tails
    strandsDict = {}
    strandStarts = {}
    for index in indexDict:

        numOfConnectedIndices = 0

        for connectedIndex in componentInfoDict['connectedPointsDict'][index]:
            if connectedIndex in indexDict:
                numOfConnectedIndices += 1

        if numOfConnectedIndices == 1:
            strandStarts[index] = None

        elif numOfConnectedIndices == 2:
            pass

        elif numOfConnectedIndices == 0:
            singlePointStrands.append(index)

        else:
            raise Exception("can't make strands from selection, point[%s] is connected to more than 2 other selected points" % str(index))

    # deal with single point strands
    for index in singlePointStrands:
        indexDict.pop(index)

        strand = (index,)
        strandID = getStrandID(strand)
        strandsDict[strandID] = strand

    # deal will strands that have a start and end
    while strandStarts:
        strandStart = strandStarts.popitem()[0]

        strand = [strandStart]

        indexDict.pop(strandStart)
        nextPoint = None
        for connectedIndex in componentInfoDict['connectedPointsDict'][strandStart]:
            if connectedIndex in indexDict:
                nextPoint = connectedIndex
                break

        while nextPoint:
            thisPoint = nextPoint
            nextPoint = None

            # add index to strand
            strand.append(thisPoint)
            indexDict.pop(thisPoint)

            if thisPoint in strandStarts:
                strandStart = strandStarts.pop(thisPoint)

            # find next index
            for connectedIndex in componentInfoDict['connectedPointsDict'][thisPoint]:
                if connectedIndex in indexDict:
                    nextPoint = connectedIndex


        # order strand starting with given strand head
        if strandHeadsAndTails is not None:
            for strandHeadTail in strandHeadsAndTails:
                if strand[-1] == strandHeadTail[0]:
                    strand.reverse()
                    break

        else: # order strand camera left to right
            strandPoint0_posX = componentInfoDict['positionDict']['camera'][strand[0]][0]
            strandPointLast_posX = componentInfoDict['positionDict']['camera'][strand[-1]][0]
            if strandPoint0_posX > strandPointLast_posX:
                strand.reverse()


        # store strand
        strand = tuple(strand)
        strandID = getStrandID(strand)
        strandsDict[strandID] = strand


    # deal with loop strands
    while indexDict:
        initialIndex = indexDict.popitem()[0]

        strand = []
        smallestIndex = initialIndex

        nextIndex = initialIndex

        while nextIndex is not None:
            thisIndex = nextIndex
            nextIndex = None

            # detirmin if this is smallest index
            if thisIndex < smallestIndex:
                smallestIndex = thisIndex

            # add index to strand
            strand.append(thisIndex)

            # remove index from stack
            if thisIndex != initialIndex:
                indexDict.pop(thisIndex)

            # find next index
            for connectedIndex in componentInfoDict['connectedPointsDict'][thisIndex]:
                if connectedIndex in indexDict and connectedIndex != initialIndex:
                    nextIndex = connectedIndex

        # order strand starting with given strand head
        if strandHeadsAndTails:
            headTailPair = None
            for headTail in strandHeadsAndTails:
                if headTail[0] in strand:
                    head = headTail[0]
                    tail = headTail[1]

                    newStrand = strand[head:]
                    strandTail = strand[:tail]
                    newStrand.extend(strandTail)

                    if tail == newStrand[-1]:
                        newStrand.reverse()
                        last = newStrand.pop()
                        newStrand.insert(0, last)

        else:
            # order strand starting with lowest index
            i = strand.index(smallestIndex)
            newStrand = strand[i:]
            strandTail = strand[:i]
            newStrand.extend(strandTail)

            if newStrand[1] > newStrand[-1]:
                newStrand.reverse()
                last = newStrand.pop()
                newStrand.insert(0, last)

        # store strand
        strand = tuple(strand)
        strandID = getStrandID(strand)
        strandsDict[strandID] = strand

    return strandsDict


#------------------------------------------------------------------------------------------------------------------------
def __findPointNeighbors__(strandInfoDict):
    """
    Finds the neighboring points and their relationship to the strand point.

    This fuction takes a strandInfoDict and finds the neighboring points of the points in it's
    'strandPoints' subDictionary. After finding these neighbors, it stores that information it the
    strandInfoDict's 'pointNeighbors' subDictionary. It also populates the 'strandNeighbors' subDictionary.

    This function is usually run after the 'strandPoints' sub dictionary has had new items added to it, or during
    the creation of a new strandInfoDict.

    Args:
        strandInfoDict (dict): the standInfoDict to find Neighbors of. See getStrandInfoDict.

    Returns:
        None

    """


    for shapeID in strandInfoDict:
        componentInfoDict = strandInfoDict[shapeID]['componentInfoDict']
        shape = componentInfoDict['pyShape']

        for strandID in strandInfoDict[shapeID]['strandDict']:
            strand = strandInfoDict[shapeID]['strandDict'][strandID]

            # has this work already been done?
            neighborsAlreadyFound = (strandInfoDict[shapeID]['strandNeighbors'][strandID]['up'] and
                                     strandInfoDict[shapeID]['strandNeighbors'][strandID]['down'] and
                                     strandInfoDict[shapeID]['strandNeighbors'][strandID]['right'] and
                                     strandInfoDict[shapeID]['strandNeighbors'][strandID]['left'])

            if not neighborsAlreadyFound:
                # get parallel points
                pointNeighborDict = __getParallelStrands__(strandID, shapeID, strandInfoDict)

                # find out if there are any existing neighbors
                noNeighbors = True
                for pointID in strand:
                    if noNeighbors is False:
                        break

                    for direction in pointNeighborDict:
                        if pointID in strandInfoDict[shapeID]['pointNeighbors']:
                            if direction in strandInfoDict[shapeID]['pointNeighbors'][pointID]:
                                if strandInfoDict[shapeID]['pointNeighbors'][pointID][direction] is not None:
                                    noNeighbors = False
                                    break
                            else:
                                raise Exception("%s not in strandInfoDict[shapeID]['pointNeighbors'][%s]" % (direction, pointID))
                                #noNeighbors = False
                                #break
                        else:
                            raise Exception("%s not in strandInfoDict[shapeID]['pointNeighbors']" % pointID)
                            #noNeighbors = False
                            #break

                # If there are no neighbors then order the directions by camera space
                if noNeighbors:
                    pointNeighborDict = __sortStrandNeighborsByCamera__(shapeID=shapeID, strandID=strandID,
                                                                          pointNeighborDict=pointNeighborDict,
                                                                          strandInfoDict=strandInfoDict)

                # if there are neighbors then sort by neighbors
                else:
                    pointNeighborDict = __sortStrandNeighborsByNeighbor__(shapeID=shapeID, strandID=strandID,
                                                                          pointNeighborDict=pointNeighborDict,
                                                                          strandInfoDict=strandInfoDict)

                # store the neighbors
                for direction in pointNeighborDict:

                    for i, pointID in enumerate(strand):
                        oppositeDirection = getOppositeDirection(direction)

                        neighborPoints = pointNeighborDict[direction][i]

                        # create bland pointNeighbors dict if none exists
                        if pointID not in strandInfoDict[shapeID]['pointNeighbors']:
                            strandInfoDict[shapeID]['pointNeighbors'][pointID] = {'up':None, 'down':None, 'left':None, 'right':None, }

                        # store direction
                        if not strandInfoDict[shapeID]['pointNeighbors'][pointID][direction]:
                            strandInfoDict[shapeID]['pointNeighbors'][pointID][direction] = neighborPoints

                            # store the opposite direction for the neighborPoints to be the current point
                            if neighborPoints:
                                for neighborPoint in neighborPoints:

                                    if neighborPoint not in strandInfoDict[shapeID]['pointNeighbors']:
                                        strandInfoDict[shapeID]['pointNeighbors'][neighborPoint] = {'up':None, 'down':None, 'left':None, 'right':None, }

                                    if strandInfoDict[shapeID]['pointNeighbors'][neighborPoint][oppositeDirection] is None:

                                        # make sure there is a list to append to
                                        if strandInfoDict[shapeID]['pointNeighbors'][neighborPoint][oppositeDirection] is None:
                                            strandInfoDict[shapeID]['pointNeighbors'][neighborPoint][oppositeDirection] = []

                                        # append to that list
                                        if pointID not in strandInfoDict[shapeID]['pointNeighbors'][neighborPoint][oppositeDirection]:
                                            strandInfoDict[shapeID]['pointNeighbors'][neighborPoint][oppositeDirection].append(pointID)

                                # make the lists tuples to save memory
                                for neighborPoint in neighborPoints:
                                    strandInfoDict[shapeID]['pointNeighbors'][neighborPoint][oppositeDirection] = tuple(strandInfoDict[shapeID]['pointNeighbors'][neighborPoint][oppositeDirection])




# ----------------------------------------------------------------------------------------------------------------------------
def __getParallelStrands__(strandID, shapeID, strandInfoDict):
    """
    finds up to 2 parallel strands from neighboring points.

    This function takes a strand and from it's neighboring points, finds up to 2 more parallel strands.

    Args:
        strandID (string): the id of the strand. eg: '22:23'

        shapeID (int): the unique int that represents the shape which holds the components. This in is the
            the hash number of the shape's pymel object.

        strandInfoDict (dict): the dict holding information about strands. This dict is returned by the function
            getStrandInfoDict.

    Returns:
        (dict): returns a dictionary, of parallel strands and their directions

        The of the returned dict is a direction, these directions are not based on anything except that their
        opposite direction (left/right, up/down) would be the other parallel strand in the opposite direction.
        In most cases, up/down would be the same values as left/right. Exceptions would include lattices, and
        single points.

        The value of the return dict is a tuple of tuples. Items in the first tuple represent the points(s) neighboring
        the strand component of the same index. The tuples within are the points parallel to the strand point in that
        direction. It is a tuple because in some cases there are more than 1 neighboring point for a given direction
        (ie: non-quad polygons)

        example of the returned dict::

        {
            'up':((22,23), (23,) (24,), (25,)),
            'down':((32,33), (33,) (34,), (35,)),
            'left':((22,23), (23,) (24,), (25,)),
            'right':((32,33), (33,) (34,), (35,)),
        }


    """
    componentInfoDict = strandInfoDict[shapeID]['componentInfoDict']
    shape = componentInfoDict['pyShape']
    strand = strandInfoDict[shapeID]['strandDict'][strandID]
    strandUp = []
    strandDown = []
    strandLeft = []
    strandRight = []

    # POLYGONS ---------------------------------------------------------------------------------------------------------------------
    if isinstance(shape, pymel.nodetypes.Mesh):
        strandTargetsA = []
        strandTargetsB = []

        # SINGLE POLY VERT - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if len(strand) == 1:
            strandPosition = componentInfoDict['positionDict']['world'][strand[0]]
            strandNormal = componentInfoDict['normalDict']['world'][strand[0]]

            strandCrossVector = None
            directionDict = {} # {'left':334, 'right':234, 'up':434, 'down':323, }
            directionDictPoints = {}
            polarCoordinateDict = {}

            # Try to use the previous point as a starting point for creating a matrix with the
            # oringinal point's normal
            for direction in strandInfoDict[shapeID]['pointNeighbors'][strand[0]]:
                directionPoint = strandInfoDict[shapeID]['pointNeighbors'][strand[0]][direction]
                if directionPoint is not None:
                    directionPoint = directionPoint[0]
                    directionDict[direction] = directionPoint
                    directionDictPoints[directionPoint] = None
                    initialPoint = directionPoint
                    initialDirection = direction
                    break

            # else rely on camera position to find our cross vector
            else:
                strandCameraPosition = componentInfoDict['positionDict']['camera'][strand[0]]
                leftMostPoint = componentInfoDict['connectedPointsDict'][strand[0]][0]
                leftMostVector = ka_math.normalize(ka_math.subtract(componentInfoDict['positionDict']['camera'][leftMostPoint], componentInfoDict['positionDict']['camera'][strand[0]]))
                for i, connectedPoint in enumerate(componentInfoDict['connectedPointsDict'][strand[0]]):
                    if i != 0:
                        connectedPointPosition =  componentInfoDict['positionDict']['camera'][connectedPoint]
                        connectedPointVector = ka_math.normalize(ka_math.subtract(componentInfoDict['positionDict']['camera'][connectedPoint], strandCameraPosition))

                        if connectedPointVector[0] < leftMostVector[0]:
                            leftMostPoint = connectedPoint
                            leftMostVector = connectedPointVector

                directionDict['left'] = leftMostPoint
                directionDictPoints[leftMostPoint] = None
                initialPoint = leftMostPoint
                initialDirection = 'left'

            polarCoordinateDict[initialDirection] = 0.0

            # form matrix from normal and cross vector
            crossVectorPoint = componentInfoDict['positionDict']['world'][initialPoint]
            crossVector = ka_math.normalize(ka_math.subtract(crossVectorPoint, strandPosition))
            negativeCrossVector = ka_math.multiply(crossVector, (-1,-1,-1))
            yVector = ka_math.crossProduct(strandNormal, negativeCrossVector)
            xVector = ka_math.crossProduct(yVector, strandNormal)
            matrix = [xVector[0],xVector[1],xVector[2],0, yVector[0],yVector[1],yVector[2],0, strandNormal[0],strandNormal[1],strandNormal[2],0, strandPosition[0],strandPosition[1],strandPosition[2],1,]

            mMatrix = ka_transforms.getMMatrixFromList(matrix)
            inverseMatrix = mMatrix.inverse()


            # find opposite direction from our initial direction
            oppositeDirection = getOppositeDirection(initialDirection)
            oppositePoint = None

            # is it a quad? if so, things get much easier...
            if len(strandInfoDict[shapeID]['componentInfoDict']['connectedPointsDict'][strand[0]]) == 4:
                for connectedPoint in strandInfoDict[shapeID]['componentInfoDict']['connectedPointsDict'][strand[0]]:
                    if connectedPoint != initialPoint:

                        # the opposite of the initial point will not be sharing any polyFaces with the initial face
                        for connectedFace in strandInfoDict[shapeID]['componentInfoDict']['facesOfPoint'][connectedPoint]:
                            if connectedFace in strandInfoDict[shapeID]['componentInfoDict']['facesOfPoint'][initialPoint]:
                                break
                        else:
                            directionDict[oppositeDirection] = connectedPoint
                            directionDictPoints[connectedPoint] = None

                            # get polar coodinate
                            connectedPointPosition = componentInfoDict['positionDict']['world'][connectedPoint]
                            normalSpacePosition = OpenMaya.MPoint(connectedPointPosition[0], connectedPointPosition[1], connectedPointPosition[2])*inverseMatrix
                            normalSpaceVector = OpenMaya.MVector(normalSpacePosition)
                            #normalSpaceVector.normalize()

                            polarCoordinateDict[oppositeDirection] = ka_math.cartesianToPolarCoordinates(normalSpaceVector[0]*-1 ,normalSpaceVector[1], asDegrees=True)[1]

            # not a quad? oh well...
            else:
                directionVector = OpenMaya.MVector(1,0,0)
                for i, connectedPoint in enumerate(componentInfoDict['connectedPointsDict'][strand[0]]):
                    if connectedPoint not in directionDictPoints:
                        connectedPointPosition = componentInfoDict['positionDict']['world'][connectedPoint]
                        normalSpacePosition = OpenMaya.MPoint(connectedPointPosition[0], connectedPointPosition[1], connectedPointPosition[2])*inverseMatrix
                        normalSpaceVector = OpenMaya.MVector(normalSpacePosition)
                        normalSpaceVector.normalize()
                        polarCoordinate = ka_math.cartesianToPolarCoordinates(normalSpaceVector[0]*-1 ,normalSpaceVector[1], asDegrees=True)[1]

                        if oppositePoint is None:
                            oppositePoint = connectedPoint
                            polarCoordinateDict[oppositeDirection] = polarCoordinate

                        elif abs(180.0-polarCoordinate) < abs(180.0-polarCoordinateDict[oppositeDirection]):
                            oppositePoint = connectedPoint
                            polarCoordinateDict[oppositeDirection] = polarCoordinate

                directionDict[oppositeDirection] = oppositePoint
                directionDictPoints[oppositePoint] = None

            # find the 2 other directions
            if 'left' in directionDict:
                remainingDirections = ('up', 'down')
            else:
                remainingDirections = ('right', 'left')

            clockDirectionDict = {'left':'up', 'up':'right', 'right':'down', 'down':'left', }
            nextPoint = None
            nextDirection = clockDirectionDict[initialDirection]
            prevPoint = None
            prevDirection = clockDirectionDict[oppositeDirection]

            idealNextAngle = polarCoordinateDict[oppositeDirection]*0.5
            idealPrevAngle = 360.0-((360.0 - polarCoordinateDict[oppositeDirection])*0.5)

            for i, connectedPoint in enumerate(componentInfoDict['connectedPointsDict'][strand[0]]):
                if connectedPoint not in directionDictPoints:
                    connectedPointPosition = componentInfoDict['positionDict']['world'][connectedPoint]
                    normalSpacePosition = OpenMaya.MPoint(connectedPointPosition[0], connectedPointPosition[1], connectedPointPosition[2])*inverseMatrix
                    normalSpaceVector = OpenMaya.MVector(normalSpacePosition)
                    normalSpaceVector.normalize()
                    polarCoordinate = ka_math.cartesianToPolarCoordinates(normalSpaceVector[0]*-1 ,normalSpaceVector[1], asDegrees=True)[1]

                    # positive point
                    if nextPoint is None:
                        nextPoint = connectedPoint
                        polarCoordinateDict[nextDirection] = polarCoordinate

                    elif abs(idealNextAngle-polarCoordinate) < abs(idealNextAngle-polarCoordinateDict[nextDirection]):
                        nextPoint = connectedPoint
                        polarCoordinateDict[nextDirection] = polarCoordinate

                    # neg point
                    if prevPoint is None:
                        prevPoint = connectedPoint
                        polarCoordinateDict[prevDirection] = polarCoordinate

                    elif abs(idealPrevAngle-polarCoordinate) < abs(idealPrevAngle-polarCoordinateDict[prevDirection]):
                        prevPoint = connectedPoint
                        polarCoordinateDict[prevDirection] = polarCoordinate

            directionDict[nextDirection] = nextPoint
            directionDict[prevDirection] = prevPoint

            # create strand strandNeighborDict
            strandNeighborDict = {}
            strandNeighborDict['up'] = ((directionDict['up'],),)
            strandNeighborDict['down'] = ((directionDict['down'],),)
            strandNeighborDict['left'] = ((directionDict['left'],),)
            strandNeighborDict['right'] = ((directionDict['right'],),)

            return strandNeighborDict

        # 2 POLY VERTS - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if len(strand) == 2:
            connectingEdge = componentInfoDict['edgeFromPoints'][strand[0]][strand[1]]

            pointPriorityDict = {}    # key=pointIndex, value=dict(key=pointID, value=int representing a points priority)

            # figure out connected points
            pointsConnectedTo0 = []
            pointsConnectedTo1 = []

            for pointIndex in componentInfoDict['connectedPointsDict'][strand[0]]:
                if pointIndex != strand[1]:
                    pointsConnectedTo0.append(pointIndex)

            for pointIndex in componentInfoDict['connectedPointsDict'][strand[1]]:
                if pointIndex != strand[0]:
                    pointsConnectedTo1.append(pointIndex)

            pointsConnectedTo0 = tuple(pointsConnectedTo0)
            pointsConnectedTo1 = tuple(pointsConnectedTo1)
            connectedPoints = list(pointsConnectedTo0)

            for pointIndex in pointsConnectedTo1:
                if pointIndex not in connectedPoints:
                    connectedPoints.append(pointIndex)
            connectedPoints = tuple(connectedPoints)

            # populate priority dict
            for strandPointIndex in strand:
                pointPriorityDict[strandPointIndex] = {}

                for connectedPointIndex in connectedPoints:
                    pointPriorityDict[strandPointIndex][connectedPointIndex] = 0

            # +5 for each point connected by edge to the strand point
            for connectedPointIndex in connectedPoints:
                if connectedPointIndex in pointsConnectedTo0:
                    pointPriorityDict[strand[0]][connectedPointIndex] += 5

                if connectedPointIndex in pointsConnectedTo1:
                    pointPriorityDict[strand[1]][connectedPointIndex] += 5

            # +1 if it is connected by face to the edge between points
            for connectedFaceIndex in componentInfoDict['facesOfEdge'][connectingEdge]:
                for pointIndexOfFace in componentInfoDict['pointsOfFace'][connectedFaceIndex]:
                    if pointIndexOfFace in connectedPoints:
                        if pointIndexOfFace not in strand:
                            for strandPointIndex in strand:
                                pointPriorityDict[strandPointIndex][pointIndexOfFace] += 1

            # find 2 points for each strand point with the highest priority
            strand0Targets = []
            largetsPriority = 0
            for strandNeighborIndex in pointPriorityDict[strand[0]]:
                priorityValue = pointPriorityDict[strand[0]][strandNeighborIndex]
                if priorityValue >= largetsPriority:
                    if strand0Targets:
                        strand0Targets = [strandNeighborIndex, strand0Targets[0]]
                    else:
                        strand0Targets = [strandNeighborIndex]
                    largetsPriority = priorityValue

                # incase the first item IS the largest priority
                elif len(strand0Targets) != 2:
                    strand1Targets = [strand0Targets[0], strandNeighborIndex]

            strand1Targets = []
            largetsPriority = 0
            for strandNeighborIndex in pointPriorityDict[strand[1]]:
                priorityValue = pointPriorityDict[strand[1]][strandNeighborIndex]
                if priorityValue >= largetsPriority:
                    if strand1Targets:
                        strand1Targets = [strandNeighborIndex, strand1Targets[0]]
                    else:
                        strand1Targets = [strandNeighborIndex]
                    largetsPriority = priorityValue

                # incase the first item IS the largest priority
                elif len(strand1Targets) != 2:
                    strand1Targets = [strand1Targets[0], strandNeighborIndex]


            # add to targets A and B lists
            # find As
            strandTargetsA_firstTarget = strand0Targets.pop()
            strandTargetsA = [[strandTargetsA_firstTarget]]
            strandTargetsAShallowList = [strandTargetsA_firstTarget]


            pointsConnectedToFirstTarget = []

            for edgeIndex in componentInfoDict['edgesOfPoint'][strandTargetsA_firstTarget]:
                for pointIndex in componentInfoDict['pointsOfEdge'][edgeIndex]:
                    if pointIndex != strandTargetsA_firstTarget:
                        pointsConnectedToFirstTarget.append(pointIndex)

            for strandTarget in strand1Targets:
                if strandTarget in pointsConnectedToFirstTarget:
                    strandTargetsA.append([strandTarget])
                    strandTargetsAShallowList.append(strandTarget)
                    break


            # find Bs
            strandTargetsB = []

            for strandTarget in strand0Targets:
                if strandTarget not in strandTargetsAShallowList:
                    strandTargetsB.append((strandTarget,))
                    break

            for strandTarget in strand1Targets:
                if strandTarget not in strandTargetsAShallowList:
                    strandTargetsB.append((strandTarget,))
                    break


            # convert to tuples for memory optimization
            listOfTuples = []
            for eachList in strandTargetsA:
                listOfTuples.append(tuple(eachList))
            strandTargetsA = tuple(listOfTuples)

            listOfTuples = []
            for eachList in strandTargetsB:
                listOfTuples.append(tuple(eachList))
            strandTargetsB = tuple(listOfTuples)


            # create strand strandNeighborDict
            strandNeighborDict = {}
            strandNeighborDict['up'] = strandTargetsA
            strandNeighborDict['down'] = strandTargetsB
            strandNeighborDict['left'] = strandTargetsA
            strandNeighborDict['right'] = strandTargetsB

            return strandNeighborDict


        # 3+ POLY VERT - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if len(strand) > 2:
            strandTargetsA = []
            strandTargetsB = []

            # MID POINTS
            lastStrandIndex = len(strand)-1
            # for all but the end points
            for i, pointIndex in enumerate(strand):

                # if not and end point
                if i != 0 and i != lastStrandIndex:

                    # a unique list of points connected by edges to the this point, excluding the original strand
                    connectedPoints = []
                    #for connectedPointIndex in componentInfoDict['connectedPointsDict'][pointIndex]:
                    for connectedEdgeIndex in componentInfoDict['edgesOfPoint'][pointIndex]:
                        for connectedPointIndex in componentInfoDict['pointsOfEdge'][connectedEdgeIndex]:
                            if connectedPointIndex not in strand:
                                connectedPoints.append(connectedPointIndex)
                                #componentInfoDict['connectedPointsDict'][strand[0]]

                    if not connectedPoints:
                        pymel.error('what the heck did you select dude?')

                    # make listB contain all connected points, and move one into list A.
                    # we will move all connected points of that point to listA
                    targetListB = list(connectedPoints)
                    targetListA = [targetListB.pop(0)] # randomly take a point

                    # itterate connected faces in search of connected points on the same side of the strand
                    faceStack = list(componentInfoDict['facesOfPoint'][targetListA[0]])
                    iCheck = 0
                    while faceStack:
                        iCheck += 1
                        if iCheck == 999:
                            pymel.error('icheck failed')

                        currentFace = faceStack.pop(0)
                        pointsOfCurrentFace = componentInfoDict['pointsOfFace'][currentFace]
                        for pointOfFace in pointsOfCurrentFace:
                            if pointOfFace in targetListB:
                                #if pointOfFace in connectedPoints:
                                    #if pointOfFace not in [connectedPoints[0], connectedPoints[-1]]:
                                targetListB.remove(pointOfFace)
                                targetListA.append(pointOfFace)

                                for connectedFace in componentInfoDict['facesOfPoint'][pointOfFace]:
                                    if connectedFace != currentFace:
                                        faceStack.append(connectedFace)

                    # append targetList to the correct strand side (A or B)
                    if not strandTargetsA: # order doesn't matter on first one
                        strandTargetsA.append(targetListA)
                        strandTargetsB.append(targetListB)

                    else:
                        laststrandTargetA = strandTargetsA[-1]

                        A_to_A = False
                        for lastVert in laststrandTargetA:
                            #for connectedFace in self.facesOfPoint[lastVert]:
                            for connectedFace in componentInfoDict['facesOfPoint'][lastVert]:
                                #for faceVert in self.pointsOfFace[connectedFace]:
                                for faceVert in componentInfoDict['pointsOfFace'][connectedFace]:
                                    if faceVert in targetListA:
                                        strandTargetsA.append(targetListA)
                                        strandTargetsB.append(targetListB)
                                        A_to_A = True
                                        break

                                if A_to_A: break

                        if not A_to_A:
                            strandTargetsA.append(targetListB)
                            strandTargetsB.append(targetListA)


            ## END POINTS
            for i, pointIndex in enumerate(strand):

                # if it IS an  end point
                if i == 0 or i == lastStrandIndex:

                    if i == 0:
                        adjacentStrandIndex = 1
                        adjacentTargetIndex = 0

                    elif i == lastStrandIndex:
                        adjacentStrandIndex = -2
                        adjacentTargetIndex = -1

                    # a unique list of points connected by edges to the this point, that are not being used as targets already
                    unusedConnectedPoints = {}
                    for connectedPoint in componentInfoDict['connectedPointsDict'][pointIndex]:
                        if connectedPoint not in strand:
                            if connectedPoint not in strandTargetsA and connectedPoint not in strandTargetsB:
                                unusedConnectedPoints[connectedPoint] = None

                    # make empty lists, we will vet points to see if they are appropriate before adding them
                    targetListA = []
                    targetListB = []

                    pointsToAddToA = []
                    pointsToAddToB = []


                    # find ideal pointA to add (closest face-connected point from the adjacent mid target)
                    for strandTargetA in strandTargetsA[adjacentTargetIndex]:
                        for faceIndex in componentInfoDict['facesOfPoint'][strandTargetA]:
                            for pointIndex in componentInfoDict['pointsOfFace'][faceIndex]:
                                if pointIndex in unusedConnectedPoints:
                                    if pointIndex not in strandTargetsA[adjacentTargetIndex]:
                                        #if pointIndex not in pointsToAddToA:
                                        pointsToAddToA.append(pointIndex)
                                        break

                            if pointsToAddToA: break
                        if pointsToAddToA: break

                    # find ideal pointB to add (closest face-connected point from the adjacent mid target)
                    for strandTargetB in strandTargetsB[adjacentTargetIndex]:
                        for faceIndex in componentInfoDict['facesOfPoint'][strandTargetB]:
                            for pointIndex in componentInfoDict['pointsOfFace'][faceIndex]:
                                if pointIndex in unusedConnectedPoints:
                                    if pointIndex not in strandTargetsB[adjacentTargetIndex]:
                                        #if pointIndex not in pointsToAddToB:
                                        pointsToAddToB.append(pointIndex)
                                        break

                            if pointsToAddToB: break
                        if pointsToAddToB: break



                    pointsToRemoveFromA = []
                    for pointToAddToA in pointsToAddToA:
                        faceConnectedPoints = []
                        for faceIndex in componentInfoDict['facesOfPoint'][pointToAddToA]:
                            for pointIndex in componentInfoDict['pointsOfFace'][faceIndex]:
                                if pointIndex in strand:
                                    faceConnectedPoints.append(pointIndex)

                        if len(componentInfoDict['facesOfPoint'][pointIndex]) <= 4:

                            # if there are only 4 connected faces to the end point, we will add a special check
                            # to make sure that the proposed point is connected to the adjacent strand point
                            if strand[adjacentStrandIndex] in faceConnectedPoints:
                                break
                            else:
                                pointsToRemoveFromA.append(pointToAddToA)

                        else:
                            for connectedPoint in faceConnectedPoints:
                                # is the propose point connected to both?
                                if connectedPoint in strandTargetsB[adjacentTargetIndex]:
                                    pointsToRemoveFromA.append(pointToAddToA)    # if so, it is no good
                                    break

                    for pointToRemove in pointsToRemoveFromA:
                        pointsToAddToA.remove(pointToRemove)


                    pointsToRemoveFromB = []
                    for pointToAddToB in pointsToAddToB:
                        faceConnectedPoints = []
                        for faceIndex in componentInfoDict['facesOfPoint'][pointToAddToB]:
                            for pointIndex in componentInfoDict['pointsOfFace'][faceIndex]:
                                if pointIndex in strand:
                                    faceConnectedPoints.append(pointIndex)

                        if len(componentInfoDict['facesOfPoint'][pointIndex]) <= 4:

                            # if there are only 4 connected faces to the end point, we will add a special check
                            # to make sure that the proposed point is connected to the adjacent strand point
                            if strand[adjacentStrandIndex] in faceConnectedPoints:
                                break
                            else:
                                pointsToRemoveFromA.append(pointToAddToB)

                        else:
                            for connectedPoint in faceConnectedPoints:
                                # is the propose point connected to both?
                                if connectedPoint in strandTargetsB[adjacentTargetIndex]:
                                    pointsToRemoveFromB.append(pointToAddToB)    # if so, it is no good
                                    break

                    for pointToRemove in pointsToRemoveFromB:
                        pointsToAddToB.remove(pointToRemove)


                    # None found?
                    if not pointsToAddToA:
                        for targetPoint in strandTargetsA[adjacentTargetIndex]:
                            for connectedFace in componentInfoDict['facesOfPoint'][targetPoint]:
                                for pointOfFace in componentInfoDict['pointsOfFace'][connectedFace]:
                                    if pointOfFace == pointIndex:
                                        if not pointsToAddToA:
                                            pointsToAddToA.append(targetPoint)
                                            break


                    # None found?
                    if not pointsToAddToB:
                        for targetPoint in strandTargetsB[adjacentTargetIndex]:
                            for connectedFace in componentInfoDict['facesOfPoint'][targetPoint]:
                                for pointOfFace in componentInfoDict['pointsOfFace'][connectedFace]:
                                    if pointOfFace == pointIndex:
                                        if not pointsToAddToB:
                                            pointsToAddToB.append(targetPoint)
                                            break


                    # finnally add the two proposed points
                    if i == 0:
                        strandTargetsA.insert(0, pointsToAddToA)
                        strandTargetsB.insert(0, pointsToAddToB)
                    else:
                        strandTargetsA.append(pointsToAddToA)
                        strandTargetsB.append(pointsToAddToB)

            # convert to tuples for memory optimization
            listOfTuples = []
            for eachList in strandTargetsA:
                listOfTuples.append(tuple(eachList))
            strandTargetsA = tuple(listOfTuples)

            listOfTuples = []
            for eachList in strandTargetsB:
                listOfTuples.append(tuple(eachList))
            strandTargetsB = tuple(listOfTuples)


            # create strand strandNeighborDict
            strandNeighborDict = {}
            strandNeighborDict['up'] = strandTargetsA
            strandNeighborDict['down'] = strandTargetsB
            strandNeighborDict['left'] = strandTargetsA
            strandNeighborDict['right'] = strandTargetsB


            return strandNeighborDict


    # SURFACE -----------------------------------------------------------------------------------------------------------------
    elif isinstance(shape, pymel.nodetypes.NurbsSurface):

        # create strand strandNeighborDict
        strandNeighborDict = {}
        strandNeighborDict['up'] = []
        strandNeighborDict['down'] = []
        strandNeighborDict['left'] = []
        strandNeighborDict['right'] = []

        # SINGLE SURFACE CV - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if len(strand) == 1:
            connectedPoints = componentInfoDict['connectedPointsDict'][strand[0]]

            strandNeighborDict['up'].append((connectedPoints[0],))
            connectedPoint0MultiIndices = componentInfoDict['multiIndex'][connectedPoints[0]]

            for connectedPoint in connectedPoints[1:]:
                connectedPointMultiIndices = componentInfoDict['multiIndex'][connectedPoint]

                if connectedPointMultiIndices[0] == connectedPoint0MultiIndices[0]:
                    strandNeighborDict['down'].append((connectedPoint,))

                elif connectedPointMultiIndices[1] == connectedPoint0MultiIndices[1]:
                    strandNeighborDict['down'].append((connectedPoint,))

                elif not strandNeighborDict['left']:
                    strandNeighborDict['left'].append((connectedPoint,))

                else:
                    strandNeighborDict['right'].append((connectedPoint,))



            #directionStack = ['left', 'right', 'up', 'down']

            #while directionStack or i > len(connectedPoints):


            #for connectedPoint in connectedPoints:
                #connectedPointMultiIndices = componentInfoDict['multiIndex'][connectedPoint]


        # 2+ SURFACE CV - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        else:
            # find strand axis
            multiIndex0 = componentInfoDict['multiIndex'][strand[0]]
            multiIndex1 = componentInfoDict['multiIndex'][strand[1]]
            for i, index in enumerate(multiIndex0):
                if multiIndex1[i] == index:
                    strandDirectionIndex = i
                    break

            # find neighbores
            for index in strand:
                multiIndex = componentInfoDict['multiIndex'][index]
                connectedPoints = componentInfoDict['connectedPointsDict'][index]
                nextPoint = None
                prevPoint = None

                for connectedPoint in connectedPoints:
                    connectedPointMultiIndices = componentInfoDict['multiIndex'][connectedPoint]
                    if connectedPointMultiIndices[strandDirectionIndex] != multiIndex[strandDirectionIndex]:
                        if connectedPointMultiIndices[strandDirectionIndex] == multiIndex[strandDirectionIndex]-1:
                            prevPoint = (connectedPoint,)

                        elif connectedPointMultiIndices[strandDirectionIndex] == multiIndex[strandDirectionIndex]+1:
                            nextPoint = (connectedPoint,)

                        elif connectedPointMultiIndices[strandDirectionIndex] < multiIndex[strandDirectionIndex]:
                            nextPoint = (connectedPoint,)

                        elif connectedPointMultiIndices[strandDirectionIndex] > multiIndex[strandDirectionIndex]:
                            prevPoint = (connectedPoint,)

                strandNeighborDict['up'].append(nextPoint)
                strandNeighborDict['left'].append(nextPoint)
                strandNeighborDict['down'].append(prevPoint)
                strandNeighborDict['right'].append(prevPoint)

        # make lists into tuple to save memory
        for key in strandNeighborDict.keys():
            value = tuple(strandNeighborDict[key])
            strandNeighborDict[key] = value

        return strandNeighborDict


    # LATTICE ---------------------------------------------------------------------------------------------------------------
    elif isinstance(shape, pymel.nodetypes.Lattice):

        # create strand strandNeighborDict
        strandNeighborDict = {}
        strandNeighborDict['up'] = []
        strandNeighborDict['down'] = []
        strandNeighborDict['left'] = []
        strandNeighborDict['right'] = []

        # find strand axis
        multiIndex0 = componentInfoDict['multiIndex'][strand[0]]
        multiIndex1 = componentInfoDict['multiIndex'][strand[1]]
        strandDimension = None
        strandNeighborDimensions = []
        for i, index in enumerate(multiIndex0):
            if multiIndex1[i] != index:
                strandDimension = i

            else:
                strandNeighborDimensions.append(i)

        # find neighbores
        for index in strand:
            multiIndex = componentInfoDict['multiIndex'][index]
            connectedPoints = componentInfoDict['connectedPointsDict'][index]

            for connectedPoint in connectedPoints:
                connectedPointMultiIndices = componentInfoDict['multiIndex'][connectedPoint]

                for i, direction in enumerate(('left', 'up')):
                    oppositeDirection = getOppositeDirection(direction)

                    if connectedPointMultiIndices[strandNeighborDimensions[i]] < multiIndex[strandNeighborDimensions[i]]:
                        strandNeighborDict[direction].append((connectedPoint,))

                    elif connectedPointMultiIndices[strandNeighborDimensions[i]] > multiIndex[strandNeighborDimensions[i]]:
                        strandNeighborDict[oppositeDirection].append((connectedPoint,))

            for direction in strandNeighborDict.keys():
                if not strandNeighborDict[direction]:
                    for index in strand:
                        strandNeighborDict[direction].append((None,))

        # make lists into tuple to save memory
        for key in strandNeighborDict.keys():
            value = tuple(strandNeighborDict[key])
            if value:
                strandNeighborDict[key] = value

        return strandNeighborDict



    # NURBS CURVE -------------------------------------------------------------------------------------------------------------
    elif isinstance(shape, pymel.nodetypes.NurbsCurve):

        # SINGLE CURVE CV - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if len(strand) == 1:
            # create strand strandNeighborDict

            connectedPoints = componentInfoDict['connectedPointsDict'][strand[0]]
            if len(connectedPoints) == 1:
                # create strand strandNeighborDict
                strandNeighborDict = {}
                strandNeighborDict['up'] = ((connectedPoints[0],),)
                strandNeighborDict['down'] = ((None,),)
                strandNeighborDict['left'] = ((connectedPoints[0],),)
                strandNeighborDict['right'] = ((None,),)


            elif len(connectedPoints) == 2:
                strandNeighborDict = {}
                strandNeighborDict['up'] = ((connectedPoints[0],),)
                strandNeighborDict['down'] = ((connectedPoints[1],),)
                strandNeighborDict['left'] = ((connectedPoints[0],),)
                strandNeighborDict['right'] = ((connectedPoints[1],),)


            return strandNeighborDict


        # MULTI CURVE CVs - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        else:

            connectedPointsOfFirst = componentInfoDict['connectedPointsDict'][strand[0]]
            # create strand strandNeighborDict
            strandNeighborDict = {}
            strandNeighborDict['up'] = []
            strandNeighborDict['down'] = []
            strandNeighborDict['left'] = []
            strandNeighborDict['right'] = []

            last = len(strand) - 1
            for i, point in enumerate(strand):
                connectedPoints = componentInfoDict['connectedPointsDict'][point]
                if i == 0:
                    nextPoint = strand[i+1]
                    if len(connectedPoints) == 1:
                        prevPoint = None
                    else:
                        for connectedPoint in connectedPoints:
                            if connectedPoint != nextPoint:
                                prevPoint = connectedPoint
                                break

                elif i == last:
                    prevPoint = strand[i-1]
                    if len(connectedPoints) == 1:
                        nextPoint = None
                        for connectedPoint in connectedPoints:
                            if connectedPoint != prevPoint:
                                nextPoint = connectedPoint
                                break

                else:    # mid points
                    nextPoint = i+1
                    prevPoint = i-1

                strandNeighborDict['up'].append((nextPoint,),)
                strandNeighborDict['down'].append((prevPoint,),)
                strandNeighborDict['left'].append((nextPoint,),)
                strandNeighborDict['right'].append((prevPoint,),)


            return strandNeighborDict

        #for index in strand:
            #multiIndex = componentInfoDict['multiIndex'][index]
            #connectedPoints = componentInfoDict['connectedPointsDict'][index]

            #for connectedPoint in connectedPoints:
                #if connectedPoint not in strand:

                    #connectedPointMultiIndices = componentInfoDict['multiIndex'][connectedPoint]


# ----------------------------------------------------------------------------------------------------------------------------
def __selectPointsByIndex__(shapeIndexDict=None):
    """
    Selects components based on given dictionary(works for all geomerty types).

    The main purpose of this function is to be able to select points without knowing what type of geometry it is.
    This function also will work if there are multiple geomety types in the dictionary.

    Args:
        shapeIndexDict (dict): the dict which defines what components will selected. eg:

    Example:

        >>> import pymel.core as pymel
        >>> import ka_maya.ka_geometry as ka_geometry; reload(ka_geometry)
        >>>
        >>> sphere = pymel.sphere()[0]
        >>> sphereShape = sphere.getShape()
        >>>
        >>> shapeIndexDict = {
        ...     sphereShape:{
        ...         (3,5):None,
        ...         (4,5):None,
        ...     },
        ... }




    """
    stringItems = []
    for shape in shapeIndexDict:
        shapeString = str(shape)
        pointAttrString = getShapePointAttr(shape)
        indexDict = shapeIndexDict[shape]

        for index in indexDict:
            stringItems.append('%s.%s[%s]' % (shapeString, pointAttrString, str(index)))

    cmds.select(stringItems)



def __deselectPointsByIndex__(shapeIndexDict=None):
    """
    Deselects components based on given dictionary(works for all geomerty types).

    Args:
        shapeIndexDict (dict): the dict which defines what components will selected. eg:
            shapeIndexDict = {<pyShape>:{344:None,
                                         345:None,
                                         356:None,
                                        },
                             }
    """

    stringItems = []
    for shape in shapeIndexDict:
        shapeString = str(shape)
        pointAttrString = getShapePointAttr(shape)
        indexDict = shapeIndexDict[shape]

        for index in indexDict:
            stringItems.append('%s.%s[%s]' % (shapeString, pointAttrString, str(index)))

    if stringItems:
        cmds.select(stringItems, deselect=True)

def __sortStrandNeighborsByCamera__(shapeID=None, strandID=None, cameraMatrix=None, pointNeighborDict=None, strandInfoDict=None):
    """
    Sort the direction keys a of the pointNeighbors sub-dictionary based on position in camera space.

    Sorts the direction and items of the pointNeighbors sub-dictionary in the strandInfoDict. The sort is done based on
    average of the camera space vectors of the each neighbor point to the original point.

    Args:
        shapeID (int): the scene-unique hash index of the pymel shape object

        strandID (string): the shape-unique strand ID of the strand. ie "22:26"

        camerateMatrix (list): a list of numbers 16 items long, representing the world space pose of the current camera

        pointNeighborDict (dict): a dicitonary of unordered

        strandInfoDict (dict):

    """
    #return pointNeighborDict


    # parse args
    if cameraMatrix is None:
        cameraMatrix = ka_cameras.getCameraMatrix()


    strandVectorDict = {}    # {strandID:[strandVectorX, strandVectorY, strandVectorZ]}

    directionMap = {}
    positionInCameraSpaceDict = {}

    strand = strandInfoDict[shapeID]['strandDict'][strandID]
    componentInfoDict = strandInfoDict[shapeID]['componentInfoDict']

    # single points are already camera sorted
    if len(strand) == 1:
        return pointNeighborDict


    # get camera space positions of active strand
    for point in strandInfoDict[shapeID]['strandDict'][strandID]:
        componentPosition = componentInfoDict['positionDict']['world'][point]
        positionInCameraSpaceDict[point] = tuple(ka_cameras.getInCameraSpace(componentPosition, cameraMatrix=cameraMatrix))


    # get average vector of the strand relative to the original strand in camera space
    pointNeighborVectorDict = {}
    for direction in pointNeighborDict:

        averagedDirectionalPointVectors = []
        for i, point in enumerate(strand):
            directionPoints = pointNeighborDict[direction][i]
            directionPointVectors = []

            for directionPoint in directionPoints:
                if directionPoint is not None:
                    directionPointWorldSpace = componentInfoDict['positionDict']['world'][directionPoint]
                    directionPointCameraSpace = ka_cameras.getInCameraSpace(directionPointWorldSpace, cameraMatrix=cameraMatrix)

                    directionPointVector = ka_math.subtract(directionPointCameraSpace, positionInCameraSpaceDict[point])
                    directionPointVector = ka_math.normalize(directionPointVector)
                    directionPointVectors.append(directionPointVector)

            # average the vectors if there is more than 1
            if not directionPointVectors:
                pass

            elif len(directionPointVectors) == 1:
                averagedDirectionalPointVectors.append(directionPointVectors[0])

            else:
                averagedDirectionalPointVectors.append(ka_math.normalize(ka_math.average(directionPointVectors)))

        # get average strand vector from component vectors
        if not averagedDirectionalPointVectors:
            averageDirectionalStrandVector = (0,0,0,)

        elif len(averagedDirectionalPointVectors) == 1:
            averageDirectionalStrandVector = tuple(averagedDirectionalPointVectors)

        else:
            averageDirectionalStrandVector = tuple(ka_math.average(averagedDirectionalPointVectors))

        pointNeighborVectorDict[direction] = averageDirectionalStrandVector


    # get x, y ranges
    topBottomVectorXRange = abs(ka_math.subtract(pointNeighborVectorDict['up'][0], pointNeighborVectorDict['down'][0]))
    leftRightVectorXRange = abs(ka_math.subtract(pointNeighborVectorDict['left'][0], pointNeighborVectorDict['right'][0]))

    topBottomVectorYRange = abs(ka_math.subtract(pointNeighborVectorDict['up'][1], pointNeighborVectorDict['down'][1]))
    leftRightVectorYRange = abs(ka_math.subtract(pointNeighborVectorDict['left'][1], pointNeighborVectorDict['right'][1]))

    # detirmine propotions of vectors
    tallestRangeName = 'topBottom'
    tallestRange = topBottomVectorYRange
    if topBottomVectorYRange < leftRightVectorYRange:
        tallestRangeName = 'rightLeft'
        tallestRange = leftRightVectorYRange


    widestRangeName = 'rightLeft'
    widestRange = leftRightVectorXRange
    if leftRightVectorXRange < topBottomVectorXRange:
        widestRangeName = 'topBottom'
        widestRange = topBottomVectorXRange


    largestDimension = 'Y'
    if tallestRange < widestRange:
        largestDimension = 'X'

    # populate the direction map
    if largestDimension == 'X':    # if vector X is greater than Y
        if widestRangeName == 'rightLeft':    # and the widest range is the left and right strand
            if pointNeighborVectorDict['left'][0] > pointNeighborVectorDict['right'][0]:
                directionMap['right'] = 'left'
                directionMap['left'] = 'right'

            else:
                directionMap['right'] = 'right'
                directionMap['left'] = 'left'


            if pointNeighborVectorDict['up'][1] > pointNeighborVectorDict['down'][1]:
                directionMap['up'] = 'up'
                directionMap['down'] = 'down'

            else:
                directionMap['up'] = 'down'
                directionMap['down'] = 'up'


        elif widestRangeName == 'topBottom':
            if pointNeighborVectorDict['up'][0] > pointNeighborVectorDict['down'][0]:
                directionMap['right'] = 'up'
                directionMap['left'] = 'down'

            else:
                directionMap['right'] = 'down'
                directionMap['left'] = 'up'


            if pointNeighborVectorDict['left'][1] > pointNeighborVectorDict['right'][1]:
                directionMap['up'] = 'left'
                directionMap['down'] = 'right'

            else:
                directionMap['up'] = 'right'
                directionMap['down'] = 'left'

    elif largestDimension == 'Y':    # if vector X is greater than Y
        if tallestRangeName == 'rightLeft':    # and the widest range is the left and right strand
            if pointNeighborVectorDict['left'][1] > pointNeighborVectorDict['right'][1]:
                directionMap['up'] = 'left'
                directionMap['down'] = 'right'

            else:
                directionMap['up'] = 'right'
                directionMap['down'] = 'left'


            if pointNeighborVectorDict['up'][0] > pointNeighborVectorDict['down'][0]:
                directionMap['right'] = 'up'
                directionMap['left'] = 'down'

            else:
                directionMap['right'] = 'down'
                directionMap['left'] = 'up'


        elif tallestRangeName == 'topBottom':
            if pointNeighborVectorDict['up'][1] > pointNeighborVectorDict['down'][1]:
                directionMap['up'] = 'up'
                directionMap['down'] = 'down'

            else:
                directionMap['up'] = 'down'
                directionMap['down'] = 'up'


            if pointNeighborVectorDict['left'][0] > pointNeighborVectorDict['right'][0]:
                directionMap['right'] = 'left'
                directionMap['left'] = 'right'

            else:
                directionMap['right'] = 'right'
                directionMap['left'] = 'left'

    origPointNeighborDict = copy.deepcopy(pointNeighborDict)

    for direction in origPointNeighborDict:
        remappedDirection = directionMap[direction]
        pointNeighborDict[direction] = origPointNeighborDict[remappedDirection]

    return pointNeighborDict


def __sortStrandNeighborsByNeighbor__(shapeID=None, strandID=None, pointNeighborDict=None, strandInfoDict=None):
    """sort the directions of the pointNeighbors Dict based on their neighbors"""

    newPointNeighborDict = pointNeighborDict.copy()    # {'left':((1334, 4556), (3444), (56346))}

    strand = strandInfoDict[shapeID]['strandDict'][strandID]

    # find active directions for up/down and left/right
    directionSortDict = {}    # {'left':{1334:None, 4556:None, 3444:None, 56346:None}}


    # find direction's that are (when compaired to their opposite): ---------------------------------------------------------------------------------
    # A) not both empty
    # B) not both full
    for direction in ('up', 'left'):
        oppositeDirection = getOppositeDirection(direction)
        for point in strand:

            # are both empty?
            if strandInfoDict[shapeID]['pointNeighbors'][point][direction] is None and strandInfoDict[shapeID]['pointNeighbors'][point][oppositeDirection] is None:
                break

            # are both full?
            if strandInfoDict[shapeID]['pointNeighbors'][point][direction] is not None and strandInfoDict[shapeID]['pointNeighbors'][point][oppositeDirection] is not None:
                break

            # otherwise it is possible to sort, lets store the previous direction and it's contents
            else:
                # is it this direction or the opposite direction that is stored?
                if strandInfoDict[shapeID]['pointNeighbors'][point][direction] is not None:
                    directionSortDict[direction] = {}
                    break

                else:
                    directionSortDict[oppositeDirection] = {}
                    break

    for direction in directionSortDict.keys():
        for point in strand:
            for pointB in strandInfoDict[shapeID]['pointNeighbors'][point][direction]:
                directionSortDict[direction][pointB] = None


    # ----------------------------------------------------------------------------------------------------------------
    # for each of the unsorted previous direction, figure which of the strands from the pointNeighborDict matches,
    # and use its opposite as points for the next direction
    for direction in directionSortDict:
        previousDirection = direction
        nextDirection = getOppositeDirection(direction)
        previousStrand = directionSortDict[direction]

        # find the key/direction of the index set in the pointNeighborDict that
        # matches the previous strand
        directionOfMatchingSet = None
        for directionKey in pointNeighborDict:
            if directionOfMatchingSet: break

            for indexSet in pointNeighborDict[directionKey]:
                if directionOfMatchingSet: break

                if indexSet:
                    for point in indexSet:
                        if directionOfMatchingSet: break

                        if point in previousStrand:
                            directionOfMatchingSet = directionKey
                            break


        # store
        oppositeDirectionOfMatchingSet = getOppositeDirection(directionOfMatchingSet)

        newPointNeighborDict[nextDirection] = pointNeighborDict[oppositeDirectionOfMatchingSet]
        newPointNeighborDict[previousDirection] = pointNeighborDict[directionOfMatchingSet]

    return newPointNeighborDict



def strandWalk(direction, strandInfoDict=None, additive=False):
    """extend the current strandInfo dict by adding neighboring strands in the given direction"""

    # parse args
    if strandInfoDict is None:
        strandInfoDict = getStrandInfoDict()

    oppositeDirection = getOppositeDirection(direction)

    # pre compile list of components that will be processes, this will require a new component info dict
    shapeIndexDict = {}
    for shapeID in strandInfoDict:
        shape = strandInfoDict[shapeID]['componentInfoDict']['pyShape']
        shapeIndexDict[shape] = {}
        indexDict = shapeIndexDict[shape]

        for strandID in strandInfoDict[shapeID]['selectedStrands']:
            if strandInfoDict[shapeID]['strandNeighbors'][strandID][direction] is None:
                strand = strandInfoDict[shapeID]['strandDict'][strandID]
                for point in strand:
                    neighborPoints = strandInfoDict[shapeID]['pointNeighbors'][point][direction]
                    if neighborPoints:
                        for neighborPoint in neighborPoints:
                            if neighborPoint is not None:
                                neighborPointMultiIndex = strandInfoDict[shapeID]['componentInfoDict']['multiIndex'][neighborPoint]
                                shapeIndexDict[shape][neighborPointMultiIndex] = None

        shapeIndexDict[shape] = tuple(shapeIndexDict[shape].keys())

    # create a dict that holds all the individual componentInfoDicts
    componentInfoDict = {}
    for shapeID in strandInfoDict:
        componentInfoDict[shapeID] = strandInfoDict[shapeID]['componentInfoDict']

    # get updated componentInfoDict
    componentInfoDict = getComponentInfoDict(inputDict=shapeIndexDict, componentInfoDict=componentInfoDict)

    for shapeID in componentInfoDict:
        strandInfoDict[shapeID]['componentInfoDict'] = componentInfoDict[shapeID]


    # add new strands
    for shapeID in strandInfoDict:
        shape = strandInfoDict[shapeID]['componentInfoDict']['pyShape']

        for strandID in strandInfoDict[shapeID]['selectedStrands'].keys():

            # if a neighborStrand exists, add it to selected Strands Dict
            if strandInfoDict[shapeID]['strandNeighbors'][strandID][direction] is not None:
                neighborStrand = strandInfoDict[shapeID]['strandNeighbors'][strandID][direction]
                strandInfoDict[shapeID]['selectedStrands'][neighborStrand] = None

            # find next strand neighbor
            else:
                strand = strandInfoDict[shapeID]['strandDict'][strandID]

                # make new strand from point neighbors
                strandNeighborHeads = []
                strandPointDict = {}

                for pointID in strand:
                    neighborPoints = strandInfoDict[shapeID]['pointNeighbors'][pointID][direction]
                    for neighborPoint in neighborPoints:
                        if neighborPoint is not None:
                            if len(strandNeighborHeads) < 2:
                                strandNeighborHeads.append(neighborPoint)

                            strandPointDict[neighborPoint] = None

                # if there is a neighbor strand in the given direction
                if strandPointDict:
                    # find strand head / tail
                    head = strandInfoDict[shapeID]['pointNeighbors'][strand[0]][direction][0]

                    if len(strand) == 1:
                        tail = head

                    else:
                        tail = None
                        i = -1
                        while tail == None:
                            if i == -99:
                                raise Exception('i check failed')

                            for nextPoint in strandInfoDict[shapeID]['pointNeighbors'][strand[i]][direction]:
                                if nextPoint != head:
                                    tail = nextPoint

                            i -= 1


                    neighborStrands = _indicesToStrands_(indexDict=strandPointDict,
                                                         componentInfoDict=strandInfoDict[shapeID]['componentInfoDict'],
                                                         strandHeadsAndTails=((head, tail),))

                    if not neighborStrands:
                        pass

                    elif len(neighborStrands) > 1:
                        raise Exception('found more than 1 strand as neighboring strand in a direction')

                    else:
                        # get strand
                        neighborStrandID, neighborStrand = neighborStrands.popitem()

                        # store strand info to strandInfoDict
                        __addStrand__(neighborStrand, strandID=neighborStrandID, strandInfoDict=strandInfoDict[shapeID])

                        strandInfoDict[shapeID]['strandNeighbors'][strandID] = {'up':None, 'down':None, 'left':None, 'right':None, }
                        strandInfoDict[shapeID]['strandNeighbors'][strandID][direction] = neighborStrandID

                        strandInfoDict[shapeID]['strandNeighbors'][neighborStrandID] = {'up':None, 'down':None, 'left':None, 'right':None, }
                        strandInfoDict[shapeID]['strandNeighbors'][neighborStrandID][oppositeDirection] = strandID

                        # remove strand at the end of the opposite direction (if it is not additive)
                        if additive is False:
                            #for shapeID in strandInfoDict:
                            #shape = strandInfoDict[shapeID]['componentInfoDict']['pyShape']

                            strandsToRemove = {}
                            for strandID in strandInfoDict[shapeID]['selectedStrands'].keys():

                                # if strand has no neighbore to the opposite direction
                                if strandInfoDict[shapeID]['strandNeighbors'][strandID][oppositeDirection] is None:
                                    strandsToRemove[strandID] = None

                            for strandID in strandsToRemove:
                                __removeStrand__(strandInfoDict[shapeID]['strandDict'][strandID], strandID=strandID, strandInfoDict=strandInfoDict[shapeID])

    __findPointNeighbors__(strandInfoDict)
    storeStrandInfoDict(strandInfoDict)
    __updateStrandSelection__(strandInfoDict)

def __updateStrandSelection__(strandInfoDict):
    selectionDict = {}

    for shapeID in strandInfoDict:
        shape = strandInfoDict[shapeID]['componentInfoDict']['pyShape']
        selectionDict[shape] = {}

        for strandID in strandInfoDict[shapeID]['selectedStrands']:
            strand = strandInfoDict[shapeID]['strandDict'][strandID]
            for point in strand:
                selectionDict[shape][point] = None

    __selectPointsByIndex__(shapeIndexDict=selectionDict)



def __addStrand__(strand, strandID=None, strandInfoDict=None):

    # parse args
    if strandID is None:
        strandID = getStrandID(strand)

    if strandInfoDict is None:
        strandInfoDict = getStrandInfoDict

    # add strand
    strandInfoDict['selectedStrands'][strandID] = None
    strandInfoDict['strandDict'][strandID] = strand

    for point in strand:
        strandInfoDict['strandOfPoint'][point] = strandID
        strandInfoDict['strandPoints'][point] = None

        if point not in strandInfoDict['pointNeighbors']:
            strandInfoDict['pointNeighbors'][point] = {'up':None, 'down':None, 'left':None, 'right':None, }

    if strandID not in strandInfoDict['strandNeighbors']:
        strandInfoDict['strandNeighbors'][strandID] = {'up':None, 'down':None, 'left':None, 'right':None, }

def __removeStrand__(strand, strandID=None, strandInfoDict=None):

    # parse args
    if strandID is None:
        strandID = getStrandID(strand)

    if strandInfoDict is None:
        strandInfoDict = getStrandInfoDict

    # remove strand
    strandInfoDict['selectedStrands'].pop(strandID)
    strandInfoDict['strandDict'].pop(strandID)

    if strandID in strandInfoDict['selectedStrands']:
        strandInfoDict['selectedStrands'].pop(strandID)

    for point in strand:
        strandInfoDict['strandOfPoint'].pop(point)
        strandInfoDict['strandPoints'].pop(point)
        strandInfoDict['componentInfoDict']['pointDict'].pop(point)

    if strandID in strandInfoDict['strandNeighbors']:

        # also remove this strand, for the strandNeighbors of it's strand Neighbors
        for direction in strandInfoDict['strandNeighbors'][strandID]:
            neighborStrand = strandInfoDict['strandNeighbors'][strandID][direction]

            if neighborStrand is not None:
                for neighborDirection in strandInfoDict['strandNeighbors'][neighborStrand]:
                    neighborOfNeighborStrand = strandInfoDict['strandNeighbors'][neighborStrand][neighborDirection]

                    if neighborOfNeighborStrand == strandID:
                        strandInfoDict['strandNeighbors'][neighborStrand][neighborDirection] = None


        # remove this strand from the strandNeighbors Dict,
        strandInfoDict['strandNeighbors'].pop(strandID)


#------------------------------------------------------------------------------------------------------------------------
def clearStrandInfo():
    #ka_clipBoard.add('strandInfoDict', None)
    global STRAND_INFO_DICT
    STRAND_INFO_DICT = None
    print 'RESET'


#------------------------------------------------------------------------------------------------------------------------
def storeStrandInfoDict(strandInfoDict = {}):
    #ka_clipBoard.replace('strandInfoDict', strandInfoDict)
    global STRAND_INFO_DICT
    STRAND_INFO_DICT = strandInfoDict


#-----------------------------------------------------------------------------------------------------------------------
def addStrandInfo(strand, strandInfoDict=None):
    """adds information about the given strand to the strand dict"""


    # strand info --------------------------------------
    strandID = getStrandID(strand)

    addingToStrandDict = False
    if strandID not in strandInfoDict['strandDict']:
        strandInfoDict['strandDict'][strandID] = []
        addingToStrandDict = True

    # strand direction info --------------------------------------
    if strandID not in strandInfoDict['strandDirectionDict']:
        strandInfoDict['strandDirectionDict'][strandID] = {'up':[],
                                                           'down':[],
                                                           'left':[],
                                                           'right':[],
                                                           'prev':[],
                                                           'next':[],
                                                           }

    # shape info --------------------------------------
    shape = strand[0].node()
    shapeID = shape.__hash__()

    if shapeID not in strandInfoDict['shapesDict']:
        strandInfoDict['shapesDict'][shapeID] = shape

    # component info --------------------------------------
    for component in strand:
        componentID = component.__hash__()
        strandInfoDict['componentDict'][componentID] = component

        # strand info --------------------------------------
        if addingToStrandDict:
            strandInfoDict['strandDict'][strandID].append(componentID)

        # shape info --------------------------------------
        if shapeID not in strandInfoDict['componentsOfShapeDict']:
            strandInfoDict['componentsOfShapeDict'][shapeID] = [componentID]
        else:
            if componentID not in strandInfoDict['componentsOfShapeDict'][shapeID]:
                strandInfoDict['componentsOfShapeDict'][shapeID].append(componentID)

        strandInfoDict['shapeOfComponentDict'][componentID] = shapeID

        # direction info --------------------------------------
        if componentID not in strandInfoDict['componentDirectionDict']:
            strandInfoDict['componentDirectionDict'][componentID] = {'up':[],
                                                                     'down':[],
                                                                     'left':[],
                                                                     'right':[],
                                                                     'prev':[],
                                                                     'next':[],
                                                                     }

    return strandID


#------------------------------------------------------------------------------------------------------------------------
def addParallelStrands(strandInfoDict):

    for strandSet in strandInfoDict['strandSets']:
        for strandID in strandSet:
            # does this direction already know its next strand in that direction?
            # if all direction keys and their values are accounted for, skip unessisary look up --------------------------------------------
            if (strandInfoDict['strandDirectionDict'][strandID]['up'] and
                strandInfoDict['strandDirectionDict'][strandID]['right'] and
                strandInfoDict['strandDirectionDict'][strandID]['down'] and
                strandInfoDict['strandDirectionDict'][strandID]['left']):    # if all these things are True...
                pass

            else: # -------------------------------------------------------------------------------------------------------------------------

                strand = []
                for componentID in strandInfoDict['strandDict'][strandID]:
                    strand.append(strandInfoDict['componentDict'][componentID])

                shapeID = strandInfoDict['shapeOfComponentDict'][componentID]
                shape = strandInfoDict['shapesDict'][shapeID]

                strand_up, strand_right, strand_down, strand_left = getParalellStrands(components=strand, shape=shape)

                #directionStrandPairs = []

                directionDict = {}
                directionDict['strandID'] = {}
                directionDict['directionStrandIDs'] = {}
                directionDict['compoundDirectionStrandIDs'] = {}

                for direction, compoundDirectionStrand in (('up', strand_up), ('right', strand_right), ('down', strand_down), ('left', strand_left), ):
                    directionStrand = []

                    #directionDict['strandID'][direction] = []
                    directionDict['directionStrandIDs'][direction] = []
                    directionDict['compoundDirectionStrandIDs'][direction] = []

                    for i, componentList in enumerate(compoundDirectionStrand):
                        componentIDList = []
                        for component in componentList:
                            if component not in directionStrand:
                                componentID = component.__hash__()

                                directionStrand.append(component)
                                if componentID not in directionDict['directionStrandIDs'][direction]:
                                    directionDict['directionStrandIDs'][direction].append(componentID)

                                #directionDict['compoundDirectionStrandIDs'][direction][i].append(componentID)
                                componentIDList.append(componentID)

                        directionDict['compoundDirectionStrandIDs'][direction].append(componentIDList)
                    directionStrandID = addStrandInfo(directionStrand, strandInfoDict)

                    directionDict['strandID'][direction] = directionStrandID


                for direction in ('left', 'up'):
                    oppositeDirection = getOppositeDirection(direction)

                    # is primary And secondary directions availible?  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                    if not strandInfoDict['strandDirectionDict'][strandID][direction] and not strandInfoDict['strandDirectionDict'][strandID][oppositeDirection]:

                        # if so, just store them, they will be sorted acording to camera
                        nextStrandID = directionDict['strandID'][direction]
                        prevStrandID = directionDict['strandID'][oppositeDirection]

                        strandInfoDict['strandDirectionDict'][strandID][direction] = nextStrandID
                        strandInfoDict['strandDirectionDict'][strandID][oppositeDirection] = prevStrandID

                        # also set this strand as the reverse direction for both of the next strand directions
                        strandInfoDict['strandDirectionDict'][nextStrandID][oppositeDirection] = strandID
                        strandInfoDict['strandDirectionDict'][prevStrandID][direction] = strandID

                        for i, componentID in enumerate(strandInfoDict['strandDict'][strandID]):
                            nextComponentIDs = directionDict['compoundDirectionStrandIDs'][direction][i]
                            prevComponentIDs = directionDict['compoundDirectionStrandIDs'][oppositeDirection][i]

                            strandInfoDict['componentDirectionDict'][componentID][direction] = nextComponentIDs
                            strandInfoDict['componentDirectionDict'][componentID][oppositeDirection] = prevComponentIDs

                            # and tho complex, we need to also store the back direction for compound components
                            #for nextComponentIDs in nextCompoundComponentIDs:
                                #for nextComponentID in nextComponentIDs:
                            for nextComponentID in nextComponentIDs:
                                if componentID not in strandInfoDict['componentDirectionDict'][nextComponentID][oppositeDirection]:
                                    strandInfoDict['componentDirectionDict'][nextComponentID][oppositeDirection].append(componentID)


                            #for prevComponentIDs in prevCompoundComponentIDs:
                                #for prevComponentID in prevComponentIDs:
                            for prevComponentID in prevComponentIDs:
                                if componentID not in strandInfoDict['componentDirectionDict'][prevComponentID][direction]:
                                    strandInfoDict['componentDirectionDict'][prevComponentID][direction].append(componentID)



                    # is one direction availible? ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                    if not strandInfoDict['strandDirectionDict'][strandID][direction] or not strandInfoDict['strandDirectionDict'][strandID][oppositeDirection]:

                        # flip direction if the opposite direction is the availible one
                        if not strandInfoDict['strandDirectionDict'][strandID][oppositeDirection]:
                            direction = getOppositeDirection(direction)
                            oppositeDirection = getOppositeDirection(oppositeDirection)

                        # find next strand ID, if it is used by the opposite direction, then use the alternitive strand ID
                        nextStrandID = directionDict['strandID'][direction]
                        if nextStrandID == strandInfoDict['strandDirectionDict'][strandID][oppositeDirection]:
                            nextStrandID = directionDict['strandID'][oppositeDirection]

                        # store it
                        strandInfoDict['strandDirectionDict'][strandID][direction] = nextStrandID #<<<

                        # also set the reverse direction for the next strand to be the current strand
                        strandInfoDict['strandDirectionDict'][nextStrandID][oppositeDirection] = strandID


                        # store components
                        for i, componentID in enumerate(strandInfoDict['strandDict'][strandID]):
                            nextCompoundComponentIDs = directionDict['compoundDirectionStrandIDs'][direction]

                            strandInfoDict['componentDirectionDict'][componentID][direction] = nextCompoundComponentIDs

                            # and tho complex, we need to also store the back direction for compound components
                            for nextComponentIDs in nextCompoundComponentIDs:
                                for nextComponentID in nextComponentIDs:
                                    if componentID not in strandInfoDict['componentDirectionDict'][nextComponentID][oppositeDirection]:
                                        strandInfoDict['componentDirectionDict'][nextComponentID][oppositeDirection].append(componentID)


#------------------------------------------------------------------------------------------------------------------------
def updateStrandSelection():
    selection = []
    strandInfoDict = getStrandInfoDict()

    for strandSet in strandInfoDict['strandSets']:
        for strandID in strandSet:
            for componentID in strandInfoDict['strandDict'][strandID]:
                selection.append(strandInfoDict['componentDict'][componentID])

    pymel.select(selection, r=True)


#------------------------------------------------------------------------------------------------------------------------
def sortStrandDirectionsToCamera(strandInfoDict=None):
    cameraMatrix = ka_cameras.getCameraMatrix()
    strandVectorDict = {}    # {strandID:[strandVectorX, strandVectorY, strandVectorZ]}

    for strandSet in strandInfoDict['strandSets']:
        for strandID in strandSet:
            directionMap = {}
            positionInCameraSpaceDict = {}

            directions = ['up', 'right', 'down', 'left']

            # get camera space positions of active strand
            for componentID in strandInfoDict['strandDict'][strandID]:
                componentPosition = pymel.xform(strandInfoDict['componentDict'][componentID], query=True, translation=True, worldSpace=True)
                positionInCameraSpaceDict[componentID] = ka_cameras.getInCameraSpace(componentPosition, cameraMatrix=cameraMatrix)

            # get average vector of the strand relative to the original strand in camera space
            for direction in directions:
                directionStrandID = strandInfoDict['strandDirectionDict'][strandID][direction]

                averagedDirectionalComponentVectors = []
                for componentID in strandInfoDict['strandDict'][strandID]:
                    directionalComponentVectors = []

                    directionComponentIDs = strandInfoDict['componentDirectionDict'][componentID][direction]

                    #for directionComponentIDList in directionCompoundComponentIDList:
                    for directionalComponentID in directionComponentIDs:

                            directionalComponent = strandInfoDict['componentDict'][directionalComponentID]
                            directionalComponentPosition = pymel.xform(directionalComponent, query=True, translation=True, worldSpace=True)
                            positionInCameraSpaceDict[directionalComponentID] = ka_cameras.getInCameraSpace(directionalComponentPosition, cameraMatrix=cameraMatrix)

                            directionalComponentVector = ka_math.subtract(positionInCameraSpaceDict[directionalComponentID], positionInCameraSpaceDict[componentID])
                            directionalComponentVector = ka_math.normalize(directionalComponentVector)
                            directionalComponentVectors.append(directionalComponentVector)

                    if len(directionalComponentVectors) == 1:
                        averagedDirectionalComponentVectors.append(directionalComponentVectors[0])
                    else:
                        averagedDirectionalComponentVectors.append(ka_math.average(directionalComponentVectors))


                averageDirectionalStrandVector = ka_math.average(averagedDirectionalComponentVectors)

                strandVectorDict[directionStrandID] = averageDirectionalStrandVector

            # analize vectors to find the most apropriate for a given direction  --------------------------------------------------------------------------------
            upStrandID = strandInfoDict['strandDirectionDict'][strandID]['up']
            rightStrandID = strandInfoDict['strandDirectionDict'][strandID]['right']
            downStrandID = strandInfoDict['strandDirectionDict'][strandID]['down']
            leftStrandID = strandInfoDict['strandDirectionDict'][strandID]['left']

            # get x, y ranges
            topBottomVectorXRange = ka_math.subtract(strandVectorDict[upStrandID][0], strandVectorDict[downStrandID][0])
            leftRightVectorXRange = ka_math.subtract(strandVectorDict[leftStrandID][0], strandVectorDict[rightStrandID][0])

            topBottomVectorYRange = ka_math.subtract(strandVectorDict[upStrandID][1], strandVectorDict[downStrandID][1])
            leftRightVectorYRange = ka_math.subtract(strandVectorDict[leftStrandID][1], strandVectorDict[rightStrandID][1])

            # detirmine propotions of vectors
            tallestRangeName = 'topBottom'
            tallestRange = topBottomVectorYRange
            if topBottomVectorYRange < leftRightVectorYRange:
                tallestRangeName = 'rightLeft'
                tallestRange = leftRightVectorYRange

            widestRangeName = 'rightLeft'
            widestRange = leftRightVectorXRange
            if topBottomVectorXRange < leftRightVectorXRange:
                widestRangeName = 'topBottom'
                widestRange = topBottomVectorXRange

            largestDimension = 'Y'
            if tallestRange < widestRange:
                largestDimension = 'X'

            if largestDimension == 'X':    # if vector X is greater than Y
                if widestRangeName == 'rightLeft':    # and the widest range is the left and right strand
                    if strandVectorDict[leftStrandID][0] > strandVectorDict[rightStrandID][0]:
                        directionMap['right'] = 'left'
                        directionMap['left'] = 'right'

                    else:
                        directionMap['right'] = 'right'
                        directionMap['left'] = 'left'


                    if strandVectorDict[upStrandID][1] > strandVectorDict[downStrandID][1]:
                        directionMap['up'] = 'up'
                        directionMap['down'] = 'down'

                    else:
                        directionMap['up'] = 'down'
                        directionMap['down'] = 'up'


                elif widestRangeName == 'topBottom':
                    if strandVectorDict[upStrandID][0] > strandVectorDict[downStrandID][0]:
                        directionMap['right'] = 'up'
                        directionMap['left'] = 'down'

                    else:
                        directionMap['right'] = 'down'
                        directionMap['left'] = 'up'


                    if strandVectorDict[leftStrandID][1] > strandVectorDict[rightStrandID][1]:
                        directionMap['up'] = 'left'
                        directionMap['down'] = 'right'

                    else:
                        directionMap['up'] = 'right'
                        directionMap['down'] = 'left'

            elif largestDimension == 'Y':    # if vector X is greater than Y
                if tallestRangeName == 'rightLeft':    # and the widest range is the left and right strand
                    if strandVectorDict[leftStrandID][1] > strandVectorDict[rightStrandID][1]:
                        directionMap['up'] = 'left'
                        directionMap['down'] = 'right'

                    else:
                        directionMap['up'] = 'right'
                        directionMap['down'] = 'left'

                    if strandVectorDict[upStrandID][0] > strandVectorDict[downStrandID][0]:
                        directionMap['right'] = 'up'
                        directionMap['left'] = 'down'

                    else:
                        directionMap['right'] = 'down'
                        directionMap['left'] = 'up'


                elif tallestRangeName == 'topBottom':
                    if strandVectorDict[upStrandID][1] > strandVectorDict[downStrandID][1]:
                        directionMap['up'] = 'up'
                        directionMap['down'] = 'down'

                    else:
                        directionMap['up'] = 'down'
                        directionMap['down'] = 'up'


                    if strandVectorDict[leftStrandID][0] > strandVectorDict[rightStrandID][0]:
                        directionMap['right'] = 'left'
                        directionMap['left'] = 'right'

                    else:
                        directionMap['right'] = 'right'
                        directionMap['left'] = 'left'

            #origStrandDirectionDict = dict(strandInfoDict['strandDirectionDict'][strandID])
            origStrandInfoDict = copy.deepcopy(strandInfoDict)

            # remap strandInfoDict['strandDirectionDict']
            for direction in directions:
                oppositeDirection = getOppositeDirection(direction)

                remappedDirection = directionMap[direction]

                remappedDirectionStrandID = origStrandInfoDict['strandDirectionDict'][strandID][remappedDirection]

                # store the new ID for direction
                strandInfoDict['strandDirectionDict'][strandID][direction] = remappedDirectionStrandID

                # store the new reverse direction for the connected strand, and the new forward value too (which may be flipped)
                strandInfoDict['strandDirectionDict'][remappedDirectionStrandID][oppositeDirection] = strandID
                strandInfoDict['strandDirectionDict'][remappedDirectionStrandID][direction] = origStrandInfoDict['strandDirectionDict'][remappedDirectionStrandID][direction]



                # remap the strandInfoDict['componentDirectionDict']
                for componentID in origStrandInfoDict['strandDict'][strandID]:

                    remappedDirectionComponentIDList = origStrandInfoDict['componentDirectionDict'][componentID][remappedDirection]

                    # store the new ID for direction
                    strandInfoDict['componentDirectionDict'][componentID][direction] = remappedDirectionComponentIDList

                    # for each component in the remappedDirectionComponentIDList, make their reverse direction point back at this component
                    for remappedDirectionComponentID in remappedDirectionComponentIDList:

                        # store the new reverse direction for the connected component, and the new forward value too (which may be flipped)
                        strandInfoDict['componentDirectionDict'][remappedDirectionComponentID][oppositeDirection] = componentID
                        strandInfoDict['componentDirectionDict'][remappedDirectionComponentID][direction] = origStrandInfoDict['componentDirectionDict'][remappedDirectionComponentID][direction]




def getOppositeDirection(direction):
    if direction == 'up':
        return 'down'
    elif direction == 'down':
        return 'up'
    elif direction == 'right':
        return 'left'
    elif direction == 'left':
        return 'right'
    elif direction == 'next':
        return 'prev'
    elif direction == 'prev':
        return 'next'

    else:
        raise Exception('%s has no defined opposite' % str(direction))



def getComponents(shape):
    shapePointAttr = getShapePointAttr(shape)
    return getattr(shape, shapePointAttr)

def getShapePointAttr(shape):
    if isinstance(shape, pymel.nodetypes.Mesh):    # POLYGONS ----------------------------------
        return 'vtx'

    elif isinstance(shape, pymel.nodetypes.Subdiv):    # SUBDIVS ----------------------------------
        return 'vtx'

    elif isinstance(shape, pymel.nodetypes.NurbsSurface):    # NURBS ----------------------------------
        return 'cv'

    elif isinstance(shape, pymel.nodetypes.NurbsCurve):    # CURVE ----------------------------------
        return 'cv'

    elif isinstance(shape, pymel.nodetypes.Lattice):    # LATTICE ----------------------------------
        return 'pt'

#def getSymmetryMapDict(shape=None, includePositive=True, includeNegative=True, includeMiddle=True, precision=8, axisOfSymmetry='x'):
    ## parse args
    #if shape == None:
        #if components != None:
            #shape = components[0].node()
        #else:
            #shape = getSelectedShape()

    #else:
        #shape = ka_pymel.getAsShape(shape)

    #shapeID = shape.__hash__()

    #import ka_maya.ka_mayaApi as ka_mayaApi ;reload(ka_mayaApi)
    #componentInfoDict = getComponentInfoDict()
    #OOOOOOO = "componentInfoDict.keys()"; print '%s: ' % OOOOOOO, eval(OOOOOOO), ' ', type(eval(OOOOOOO))
    #OOOOOOO = "shape"; print '%s: ' % OOOOOOO, eval(OOOOOOO), ' ', type(eval(OOOOOOO))
    #symmetryMapDic = {}
    #positiveDict = {}
    #negativeDict = {}

    ## get axisOfSymmetry --------------------
    #if axisOfSymmetry == 'x':
        #symmetryIndex = 0
        #symmetryMultiplier = (-1,1,1)

    #elif axisOfSymmetry == 'y':
        #symmetryIndex = 1
        #symmetryMultiplier = (1,-1,1)

    #elif axisOfSymmetry == 'z':
        #symmetryIndex = 2
        #symmetryMultiplier = (1,1,-1)

    ## populate dictionary
    #for pointIndex in componentInfoDict[shapeID]['pointDict']:
        #position = componentInfoDict[shapeID]['positionDict']['orig'][pointIndex]

        ## determin if it is a positive...
        #if position[symmetryIndex] > 0.0:
            #positiveDict[position] = pointIndex

        ## ...or negitive point
        #elif position[symmetryIndex] < 0.0:
            #position = (position[0]*symmetryMultiplier[0], position[1]*symmetryMultiplier[1], position[2]*symmetryMultiplier[2], )
            #negativeDict[position] = pointIndex

        #else: # or center
            #if includeMiddle:
                #symmetryMapDic[pointIndex] = pointIndex

    #del componentInfoDict

    #currentPrecision = precision
    #nextPrecisionPositive = positiveDict.copy()
    #nextPrecisionNegative = negativeDict.copy()
    #while positiveDict and currentPrecision >= 1:
        #nextPrecisionPositive = {}
        #nextPrecisionNegative = {}

        ## try to find a mach for each item
        #while positiveDict:
            #posPosition, posIndex = positiveDict.popitem()

            #if posPosition in negativeDict:
                #negIndex = negativeDict.pop(posPosition)

                #if includePositive:
                    #symmetryMapDic[posIndex] = negIndex
                #if includeNegative:
                    #symmetryMapDic[negIndex] = posIndex

            ## round up the unmatched points
            #else:
                #nextPrecisionPositive[(round(posPosition[0], currentPrecision), round(posPosition[1], currentPrecision), round(posPosition[2], currentPrecision),) ] = posIndex

                ## round up the unmatched points

        #while negativeDict:
            #negPosition, negIndex = negativeDict.popitem()
            #nextPrecisionNegative[(round(negPosition[0], currentPrecision), round(negPosition[1], currentPrecision), round(negPosition[2], currentPrecision),) ] = negIndex

        #currentPrecision -= 1
        #positiveDict = nextPrecisionPositive.copy()
        #negativeDict = nextPrecisionNegative.copy()

    ## assume the rest are center
    #if includeMiddle:
        #for position in positiveDict:
            #index = positiveDict[position]
            #symmetryMapDic[index] = index
        #for position in negativeDict:
            #index = negativeDict[position]
            #symmetryMapDic[index] = index


    #return symmetryMapDic


def getSymmetryMapDict(componentInfoDict=None, includePositive=True, includeNegative=True, includeMiddle=True,
                       space='orig', precision=8, axisOfSymmetry='x'):
    # parse args
    if componentInfoDict is None:
        componentInfoDict = getComponentInfoDict()

    symmetryMapDic = {}



    positiveDict = {}
    negativeDict = {}

    # get axisOfSymmetry --------------------
    if axisOfSymmetry == 'x':
        symmetryIndex = 0
        symmetryMultiplier = (-1,1,1)

    elif axisOfSymmetry == 'y':
        symmetryIndex = 1
        symmetryMultiplier = (1,-1,1)

    elif axisOfSymmetry == 'z':
        symmetryIndex = 2
        symmetryMultiplier = (1,1,-1)

    # populate dictionary
    for shapeID in componentInfoDict:
        symmetryMapDic[shapeID] = {}
        symmetryMapDic[shapeID]['positive'] = {}
        symmetryMapDic[shapeID]['negative'] = {}
        symmetryMapDic[shapeID]['center'] = {}

        for pointIndex in componentInfoDict[shapeID]['pointDict']:
            position = componentInfoDict[shapeID]['positionDict'][space][pointIndex]

            # determin if it is a positive...
            if position[symmetryIndex] > 0.0:
                positiveDict[position] = pointIndex

            # ...or negitive point
            elif position[symmetryIndex] < 0.0:
                position = (position[0]*symmetryMultiplier[0], position[1]*symmetryMultiplier[1], position[2]*symmetryMultiplier[2], )
                negativeDict[position] = pointIndex

            else: # or center
                if includeMiddle:
                    symmetryMapDic[shapeID]['center'][pointIndex] = pointIndex


        currentPrecision = precision
        nextPrecisionPositive = positiveDict.copy()
        nextPrecisionNegative = negativeDict.copy()
        while positiveDict and currentPrecision >= 1:
            nextPrecisionPositive = {}
            nextPrecisionNegative = {}

            # try to find a mach for each item
            while positiveDict:
                posPosition, posIndex = positiveDict.popitem()

                if posPosition in negativeDict:
                    negIndex = negativeDict.pop(posPosition)

                    if includePositive:
                        symmetryMapDic[shapeID]['positive'][posIndex] = negIndex
                    if includeNegative:
                        symmetryMapDic[shapeID]['negative'][negIndex] = posIndex

                # round up the unmatched points
                else:
                    nextPrecisionPositive[(round(posPosition[0], currentPrecision), round(posPosition[1], currentPrecision), round(posPosition[2], currentPrecision),) ] = posIndex

                    # round up the unmatched points

            while negativeDict:
                negPosition, negIndex = negativeDict.popitem()
                nextPrecisionNegative[(round(negPosition[0], currentPrecision), round(negPosition[1], currentPrecision), round(negPosition[2], currentPrecision),) ] = negIndex

            currentPrecision -= 1
            positiveDict = nextPrecisionPositive.copy()
            negativeDict = nextPrecisionNegative.copy()

        # assume the rest are center
        if includeMiddle:
            for position in positiveDict:
                index = positiveDict[position]
                symmetryMapDic[shapeID]['center'][index] = index
            for position in negativeDict:
                index = negativeDict[position]
                symmetryMapDic[shapeID]['center'][index] = index

    return symmetryMapDic


def getAdjacentPolyStrands(strand):
    adjacentStrandA = []    # [[vert0], [vert2, vert3]...]
    adjacentStrandB = []    # [[vert0], [vert2, vert3]...]

    strandIndices = []
    for vert in strand:
        strandIndex = vert.index()
        strandIndices.append(strandIndex)

    polyInfoDict = getPolyInfoDict(strand)

def get1DComponentIndex(component, **kwargs):
    indices = []
    for strI in re.findall(r'\d+', str(component).split('.')[1]):
        indices.append(int(strI))

    # combine nD indices to get a single index
    if isinstance(shape, pymel.nodetypes.MeshVertex):    # POLYGONS ----------------------------------
        return indices[0]

    elif isinstance(shape, pymel.nodetypes.Subdiv):    # SUBDIVS ----------------------------------
        pass

    elif isinstance(shape, pymel.nodetypes.NurbsSurfaceCV):    # NURBS ----------------------------------
        lastV = shape.spansUV.get()[1]+3

        index = (indices[0]*lastV) + indices[1]
        return index

    elif isinstance(shape, pymel.nodetypes.NurbsCurveCV):    # CURVE ----------------------------------
        return indices[0]

    elif isinstance(shape, pymel.nodetypes.LatticePoint):    # LATTICE ----------------------------------
        sDivisions = kwargs.get('sDivisions', None)
        tDivisions = kwargs.get('tDivisions', None)

        if sDivisions == None: sDivisions = shape.sDivisions.get()
        if tDivisions == None: tDivisions = shape.tDivisions.get()

        index = indices[0] + (sDivisions*indices[1]) + ((sDivisions, tDivisions)*indices[2])
        return index




def particleFillSelection():

    # get the active selection
    selection = OpenMaya.MSelectionList()
    OpenMaya.MGlobal.getActiveSelectionList( selection )
    iterSel = OpenMaya.MItSelectionList(selection, OpenMaya.MFn.kMesh)

    # go througt selection
    while not iterSel.isDone():

        # get dagPath
        dagPath = OpenMaya.MDagPath()
        iterSel.getDagPath( dagPath )

        # create empty point array
        inMeshMPointArray = OpenMaya.MPointArray()

        # create function set and get points in world space
        currentInMeshMFnMesh = OpenMaya.MFnMesh(dagPath)
        currentInMeshMFnMesh.getPoints(inMeshMPointArray, OpenMaya.MSpace.kWorld)

        # put each point to a list
        pointList = []

        for i in range( inMeshMPointArray.length() ) :

            pointList.append( [inMeshMPointArray[i][0], inMeshMPointArray[i][1], inMeshMPointArray[i][2]] )

        return pointList




#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


def getMaxDimensions(shape):
    """
    Gets max dimensions of given shape.

    This is usefull for the function: getSingleIndex_fromMultiIndex

    Args:
        shape (pyShape): the shape to get the max dimensions of
    """
    if isinstance(shape, pymel.nodetypes.NurbsSurface):    # NURBS ----------------------------------
        uSpans = shape.numCVsInU()
        vSpans = shape.numCVsInV()


        return (uSpans, vSpans,)

    elif isinstance(shape, pymel.nodetypes.Lattice):    # LATTICE ----------------------------------
        return (shape.sDivisions.get(), shape.tDivisions.get(), shape.uDivisions.get())

    elif isinstance(shape, pymel.nodetypes.NurbsCurve):    # NURBS CURVE ----------------------------------
        return (len(shape.cv), )


def getDegree(shape):
    """
    Get the degree of the given shape.

    For geos like nurbsSurface and nurbs curve, this function returns their degree(s):

    Args:
        shape (pyShape): the shape

    Returns:
        (tuple/None): degree of each dimension (2 for nurbsSurface, 1 for nurbsCurve). If geometry type has
            no degree (such as polygons), returns None
    """

    if isinstance(shape, pymel.nodetypes.NurbsSurface):
        return (shape.degreeU(), shape.degreeV(),)

    elif isinstance(shape, pymel.nodetypes.NurbsCurve):
        return (shape.degree(),)

    else:
        return None


def getForm(shape):
    """
    Get the form of the given shape.

    For geos like nurbsSurface and nurbs curve, this function returns the form of each dimension.
    Form indicates things like closing of loops (sphere's, circles, torrus's ect):

    Args:
        shape (pyShape): the shape

    Returns:
        (tuple/None): form of each dimension (2 for nurbsSurface, 1 for nurbsCurve). If geometry type has
            no form (such as polygons), returns None
    """

    if isinstance(shape, pymel.nodetypes.NurbsSurface):
        return (shape.formU.get(), shape.formV.get(),)

    elif isinstance(shape, pymel.nodetypes.NurbsCurve):
        return (shape.f.get())

    else:
        return None


def _getGeoIteratorClass_(shape):
    """
    Get the assosiated geometry point itterator for the given shape

    Args:
        shape (pyShape): the shape

    Returns:
        (OpenMaya geometry iterator): The assosiated Geometry point itterator class from OpenMaya
    """
    shapeType = getShapeType(shape)

    # get assosiated geometry iterator
    if shapeType == 'mesh':
        return OpenMaya.MItMeshVertex

    elif shapeType == 'nurbsSurface':
        return OpenMaya.MItSurfaceCV

    elif shapeType == 'nurbsCurve':
        return OpenMaya.MItCurveCV

    elif shapeType == 'lattice':
        return OpenMaya.MItGeometry

    elif shapeType == 'subdiv':
        return OpenMaya.MItSubdVertex


def getShapeType(shape):
    """
    Get the type for the given shape.

    This function helps to generalize, since it recieves pyShapes and MDagPaths

    Args:
        shape (pyShape/MDagPath): the shape

    Returns:
        (string): the nodeType of the shape.
    """

    if isinstance(shape, pymel.nodetypes.Mesh):
        return 'mesh'

    elif isinstance(shape, pymel.nodetypes.NurbsSurface):
        return 'nurbsSurface'

    elif isinstance(shape, pymel.nodetypes.NurbsCurve):
        return 'nurbsCurve'

    elif isinstance(shape, pymel.nodetypes.Lattice):
        return 'lattice'

    elif isinstance(shape, pymel.nodetypes.Subdiv):
        return 'subdiv'

    elif isinstance(shape, OpenMaya.MDagPath):
        apiType = shape.apiType()

        if apiType == 296:
            return 'mesh'

        elif apiType == 294:
            return 'nurbsSurface'

        elif apiType == 267:
            return 'nurbsCurve'

        elif apiType == 279:
            return 'lattice'

        elif apiType == 671:
            return 'subdiv'

        else:
            raise Exception('unknown shape type22: %s' % str(shape))

    else:
        raise Exception('unknown shape type: %s' % str(shape))

def getMultiIndex_fromSingleIndex(index1D, maxDimensions=None, form=None, degree=None):
    """
    takes a single index (that would corrispond to it's index in an array) and converts it to a multi index (like a nurbs or lattice)

    Args:
        index1D (int): the component 1D index

        maxDimensions (tuple of ints): for multi index items (like nurbs surfaces), this represents the max length of all but
            first dimesion. in the case of a nurbs, this would be number of CVs in the V dimension.

        form (int): aadfdsf

        degree (int): passasdf

    """

    if maxDimensions is None:
        return (index1D,)
    else:
        dimensions = len(maxDimensions)

    if dimensions == 1:
        return (index1D,)

    if dimensions == 2:
        if form[1] == 2:
            return ((index1D/(maxDimensions[1]+degree[0])), (index1D % (maxDimensions[1]+degree[0])),)

        else:
            return ((index1D/maxDimensions[1]), (index1D%maxDimensions[1]),)

    if dimensions == 3:
        return (index1D%maxDimensions[0]%maxDimensions[1], index1D/maxDimensions[0]%maxDimensions[1], index1D/maxDimensions[0]/maxDimensions[1],)

def getSingleIndex_fromMultiIndex(multiIndex, maxDimensions=None, form=None, degree=None):
    """takes a multi index (like a nurbs or lattice) and converts it to a single index (that would
    corrispond to it's index in an array)

    maxDimensions - tuple of ints - for multi index items, this represents the max length of all but first dimesion.
                                   in the case of a nurbs, this would be number of CVs in the V dimension
    """
    if maxDimensions is None:
        return (multiIndex)

    else:
        dimensions = len(maxDimensions)

    if dimensions == 1:
        return multiIndex[0]

    if dimensions == 2:
        if form == 2:
            return (maxDimensions[1]+degree) * multiIndex[0] + multiIndex[1]

        else:
            return maxDimensions[1]*multiIndex[0]+multiIndex[1]

    if dimensions == 3:
        return multiIndex[0] + (maxDimensions[0]*multiIndex[1]) + ((maxDimensions[0]*maxDimensions[1])*multiIndex[2])



def getMDagPath( objectName ):
    '''given an object name string, this will return the MDagPath api handle to that object'''
    sel = OpenMaya.MSelectionList()
    sel.add( objectName )
    obj = OpenMaya.MDagPath()
    sel.getDagPath(0,obj)

    return obj


def getMfnComponent(shape):
    """
    Get the related mfnComponent and mfnComponentMObject for the given shape

    Args:
        shape (pyShape/MDagPath): the shape

    Returns:
        (tuple): (mfnComponent, mfnComponentMObject) related to the given shape


    """

    shapeType = getShapeType(shape)

    # get mfnComponent and mfnComponentMObject
    if shapeType == 'mesh':
        mfnComponent = OpenMaya.MFnSingleIndexedComponent()
        mfnComponentMObject = mfnComponent.create(OpenMaya.MFn.kMeshVertComponent)

    elif shapeType == 'nurbsSurface':
        mfnComponent = OpenMaya.MFnDoubleIndexedComponent()
        mfnComponentMObject = mfnComponent.create(OpenMaya.MFn.kSurfaceCVComponent)

    elif shapeType == 'nurbsCurve':
        mfnComponent = OpenMaya.MFnSingleIndexedComponent()
        mfnComponentMObject = mfnComponent.create(OpenMaya.MFn.kCurveCVComponent)

    elif shapeType == 'lattice':
        mfnComponent = OpenMaya.MFnTripleIndexedComponent()
        mfnComponentMObject = mfnComponent.create(OpenMaya.MFn.kLatticeComponent)

    elif shapeType == 'subdiv':
        mfnComponent = OpenMaya.MFnSingleIndexedComponent()
        mfnComponentMObject = mfnComponent.create(OpenMaya.MFn.kSubdivCVComponent)

    return mfnComponent, mfnComponentMObject


#def getMSelectionList_fromShapeAndMultiIndices(shape, multiIndices):
def getMSelectionList_fromShapeAndMultiIndices(shape, indices):
    """returns an MSelectionList from the given shape and multi indices

    Args:
        shape (pyShape/MDagPath): the shape the components are on

        multiIndices (list/tuple): a list of tuples, with the single or (preferably)
            multi indices of the components to add to the MSelection list.

    returns:
        (MSelectionList)
    """
    mSelectionList = OpenMaya.MSelectionList()

    for shape in shapeAndIndexDict:
        mfnComponent, mfnComponentMObject = getMfnComponent(shape)
        shapeMfnDagPath = shape.__apimdagpath__()

        for multiIndex in shapeAndIndexDict[shape]:
            mfnComponent.addElement(*multiIndex)

        mSelectionList.add(shapeMfnDagPath, mfnComponentMObject)

    return mSelectionList


def getIndicesOfShape_asMObject(shape, indices, componentInfoDict=None):
    """returns an MSelectionList from the given shape and multi indices

    Args:
        shape (pyShape/MDagPath): the shape the components are on

        multiIndices (list/tuple): a list of tuples, with the single or (optimally)
            multi indices of the components to add to the MSelection list.

        componentInfoDict (dict, optional): the componentInfoDict for the given shape.
            if passed in, will save time looking up certain info

    returns:
        (MObject)
    """


    # parse args
    if isinstance(shape, OpenMaya.MDagPath):
        shapeDagPath = shape

    elif ka_pymel.isPyShape(shape):
        shapeDagPath = shape.__apimdagpath__()


    mfnComponent, mfnComponentMObject = getMfnComponent(shape)

    if indices:
        if isinstance(indices[0], int):
            if componentInfoDict is not None:
                form = componentInfoDict['form']
                degree = componentInfoDict['degree']
                maxDimensions = componentInfoDict['maxDimensions']

            else:
                pyshape = ka_pymel.getAsPyNodes(shape)

                form = getForm(pyshape)
                degree = getDegree(pyshape)
                maxDimensions = getMaxDimensions(pyshape)

            for index in indices:

                multiIndex = getMultiIndex_fromSingleIndex(index, maxDimensions=maxDimensions,
                                                           form=form, degree=degree)

                mfnComponent.addElement(*multiIndex)

        else:
            for multiIndex in indices:
                mfnComponent.addElement(*multiIndex)

    components_mObject = OpenMaya.MObject()
    mSelectionList = OpenMaya.MSelectionList()

    mSelectionList.add(shapeDagPath, mfnComponentMObject)
    mSelectionList.getDagPath(0, shapeDagPath, components_mObject)

    return components_mObject


def getComponentInfoDict(inputDict=None, positions=True, normals=True, connectedPoints=True,
                         worldSpace=True, objectSpace=True, origSpace=True, cameraSpace=True,
                         componentInfoDict=None):
    """
    A highly optimized way to retrive component information.

    Args:
        inputDict (dict): A dictionary specifying which shapes, and which components (by 1D index) of those shapes
            to operate on. See example below for expected dictionary structure

        componentInfoDict (dict): The dictionary to extend. By default, a new dict will be created, but passing in an
            existing componentInfoDict will cause the values found to be added to it.

    Returns:
        dict: A dicitonary of various information about the components. The returned dict contains many subdictionaries,
            the structure of which is as follows

        componentInfoDict = {'5244353':{'pyShape':<pyShape>,

                                        'pointDict' = {0:None,    # input points
                                                       1:None,
                                                      },

                                        'positionDict':{'world':{0:(22.2, 32.2, 45.4),   # world space position'
                                                                },
                                                        'local':{0:(22.2, 32.2, 45.4),    # local space position
                                                                },
                                                        'orig':{0:(22.2, 32.2, 45.4),    # loacl space position of original mesh
                                                               },
                                                        'camera':{0:(0.5, 0.5, 0),    # position in the space of the camera
                                                                 },
                                                       },

                                        'normalDict':{'world':{0:(0.5, 0.5, 0),   # world space normal
                                                              },
                                                      'local':{0:(0.5, 0.5, 0),    # local space normal
                                                              },
                                                      'orig':{0:(0.5, 0.5, 0),    # local space normal of original mesh
                                                             },

                                                     },

                                        'connectedPointsDict:{0:(1, 2, 3)    # pointIndex:(connectedComponentIndex, ...)
                                                               },
                                        'connectedFaceDict:{0:(1, 2, 3)    # faceIndex:(connectedComponentIndex, ...)
                                                           },
                                        'connectedEdgesDict:{0:(1, 2, 3)    # edgeIndex:(connectedComponentIndex, ...)
                                                            },

                                        'edgeDict':{0:None,     # edgeIndex:None
                                                     },
                                        'faceDict':{0:None,     # faceIndex:None
                                                     },

                                        'pointsOfFace':{0:(1, 2, 3)    # faceID:(pointIndex, pointIndex...)
                                                         },
                                        'pointsOfEdge':{0:(1, 2)    # edgeID:(pointIndex, pointIndex...)
                                                         },

                                        'facesOfPoint':{0:(112344, 534666, 234244)    # pointIndex:(faceID, faceID...)
                                                         },
                                        'facesOfEdge':{0:(112344, 534666, 234244)    # edgeID:(faceID, faceID...)
                                                        },

                                        'edgesOfPoint':{2:(112344, 534666, 234244)    # pointIndex:(edgeID, edgeID...)
                                                         },
                                        'edgeFromPoints':{2:{3:5, 4:6, 5:7}    # edgeID = edgesOfPoints[indexA][indexB]
                                                           },
                                        'edgesOfFace':{1:(112344, 534666, 234244)    # faceID:(edgeID, edgeID...)
                                                        },


                                        'multiIndex':{55:(23,3),   # pointIndex:index0, index2... (nD index is used in nurbs and lattices)
                                                     },

                                        'maxDimensions':(22,15),   # indicates the number of components per dimension (ie nurbs, lattices)
                                        'wrapDimensions':(True, False),   # indicates the dimensions the wrap around (ie nurbs) (nurbs only)
                                        'degrees':(3, 3),   # nurbs degree(s) (nurbs only)
                                        'numOfCvs':(3, 3),   # number of Cvs in each direction (nurbs only)

                                       },
                            }

    Examples:
        Here is an example of how to get the dict, and use it's information

        >>> import ka_maya.ka_geometry as ka_geometry ;reload(ka_geometry)
        # create a circle
        >>> sphere = pymel.sphere()[0]
        >>> sphereShape = sphere.getShape()
        >>> pymel.select(sphereShape.cv[3:4][1])
        <BLANKLINE>
        >>> componentDict = ka_geometry.getComponentInfoDict()
        <BLANKLINE>
        # print the shape, position, 1D index and multi index of each point
        >>> for shapeID in componentDict:
        ...     print shapeID
        ...     for singleIndex in componentDict[shapeID]['pointDict']:
        ...         multiIndex = componentDict[shapeID]['multiIndex'][singleIndex]
        ...         worldSpacePosition = componentDict[shapeID]['positionDict']['world'][singleIndex]
        <BLANKLINE>
        ...         print '    ', worldSpacePosition, singleIndex, multiIndex
        <BLANKLINE>
        799298936
            (8.734899569222047e-17, -2.901104977298788e-16, -1.2264094625656803) 34 (3, 1)
            (0.7836116248912245, -2.593918494796756e-16, -0.8717636375318034) 45 (4, 1)





        inputDict={<pyShape>:(33,
                    34,
                    56,
                    ),
                  }


      >>> print [i for i in example_generator(4)]
      [0, 1, 2, 3]



    """
    selection = cmds.ls(selection=True)

    if componentInfoDict is None:
        componentInfoDict = {}


    if normals:
        mVector = OpenMaya.MVector()

    mScriptUtil = OpenMaya.MScriptUtil()
    mSelectionList = OpenMaya.MSelectionList()
    mDagPath = OpenMaya.MDagPath()
    mComponent = OpenMaya.MObject()

    # create mSelection List
    if inputDict:
        for shape in inputDict:
            indices_mObject = getIndicesOfShape_asMObject(shape, indices=inputDict[shape])
            mSelectionList.add(shape.__apimdagpath__(), indices_mObject)

        #mSelectionList = getMSelectionList_fromShapeAndMultiIndices(inputDict)

    else:
        OpenMaya.MGlobal.getActiveSelectionList(mSelectionList) # store selection to mSelectionList

    mNodeIter = OpenMaya.MItSelectionList(mSelectionList) # create iterator from mSelectionList

    # iterate mSelection List #######################################################################################
    while not mNodeIter.isDone():
        if mNodeIter.itemType() == 0:
            mNodeIter.getDagPath( mDagPath, mComponent ) # dagPath and component are passed as references; the function itself returns null, so you don't want to store its return value in dagPath

            # store shape info
            shapeName = mDagPath.partialPathName()
            #pyShape = pymel.PyNode(shapeName)
            pyShape = pymel.PyNode(mDagPath.node())

            if isinstance(pyShape, pymel.nodetypes.Transform):
                pyShape = pyShape.getShape()

            pyShapeID = pyShape.__hash__()

            shapeType = cmds.nodeType(shapeName)

            if pyShapeID in componentInfoDict:
                componentDict = componentInfoDict[pyShapeID]

            else:
                componentInfoDict[pyShapeID] = {}
                componentDict = componentInfoDict[pyShapeID]
                componentDict['pyShape'] = pyShape
                componentDict['pointDict'] = {}
                componentDict['positionDict'] = {}
                componentDict['positionDict']['world'] = {}
                componentDict['positionDict']['local'] = {}
                componentDict['positionDict']['orig'] = {}
                componentDict['positionDict']['camera'] = {}
                componentDict['normalDict'] = {}
                componentDict['normalDict']['world'] = {}
                componentDict['normalDict']['local'] = {}
                componentDict['normalDict']['orig'] = {}
                componentDict['normalDict']['camera'] = {}
                componentDict['connectedPointsDict'] = {}
                componentDict['connectedFaceDict'] = {}
                componentDict['connectedEdgesDict'] = {}
                componentDict['edgeDict'] = {}
                componentDict['faceDict'] = {}
                componentDict['pointsOfFace'] = {}
                componentDict['pointsOfEdge'] = {}
                componentDict['facesOfPoint'] = {}
                componentDict['facesOfEdge'] = {}
                componentDict['edgesOfPoint'] = {}
                componentDict['edgeFromPoints'] = {}
                componentDict['edgesOfFace'] = {}
                componentDict['index'] = {}
                componentDict['multiIndex'] = {}
                componentDict['form'] = getForm(pyShape)
                componentDict['degree'] = getDegree(pyShape)
                componentDict['maxDimensions'] = getMaxDimensions(pyShape)

            connectedItemsStack = {}
            connectedEdgesStack = {}
            connectedFacesStack = {}

            form = None
            degree = None

            # get assosiated geometry iterator
            # POLYGON -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -
            if isinstance(pyShape, pymel.nodetypes.Mesh):
                geoIterClass = OpenMaya.MItMeshVertex

                connectedPointIndicesMfnObj = OpenMaya.MFnSingleIndexedComponent()
                connectedPointsMObject = connectedPointIndicesMfnObj.create(OpenMaya.MFn.kMeshVertComponent)

                wrapDimensions = (False,)

                faceIter = OpenMaya.MItMeshPolygon( mDagPath )

            # NURBS SURFACE -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -
            elif isinstance(pyShape, pymel.nodetypes.NurbsSurface):
                geoIterClass = OpenMaya.MItSurfaceCV

                connectedPointIndicesMfnObj = OpenMaya.MFnDoubleIndexedComponent()
                connectedPointsMObject = connectedPointIndicesMfnObj.create(OpenMaya.MFn.kSurfaceCVComponent)

                if 'wrapDimensions' not in componentDict:
                    if pyShape.formU.get() == 2:
                        wrapDimensions = [True]
                    else:
                        wrapDimensions = [False]

                    if pyShape.formV.get() == 2:
                        wrapDimensions.append(True)
                    else:
                        wrapDimensions.append(False)

                    componentDict['wrapDimensions'] = tuple(wrapDimensions,)
                    componentDict['degrees'] = (pyShape.degreeU(), pyShape.degreeV(),)
                    componentDict['numCVs'] = (pyShape.numCVsInU(), pyShape.numCVsInV(),)

                numCVsInU = componentDict['numCVs'][0]
                numCVsInV = componentDict['numCVs'][1]
                form = pyShape.formV.get()
                degree = componentDict['degrees'][0]



            # NURBS CURVE -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -
            elif isinstance(pyShape, pymel.nodetypes.NurbsCurve):
                geoIterClass = OpenMaya.MItCurveCV

                connectedPointIndicesMfnObj = OpenMaya.MFnSingleIndexedComponent()
                connectedPointsMObject = connectedPointIndicesMfnObj.create(OpenMaya.MFn.kCurveCVComponent)

                if 'wrapDimensions' not in componentDict:
                    if pyShape.f.get() == 2:
                        componentDict['wrapDimensions'] = (True,)
                    else:
                        componentDict['wrapDimensions'] = (False,)

                    componentDict['degrees'] = (pyShape.degree(),)
                    componentDict['numCVs'] = (pyShape.numCVs(),)

            # LATTICE -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -
            elif isinstance(pyShape, pymel.nodetypes.Lattice):
                geoIterClass = OpenMaya.MItGeometry

                connectedPointIndicesMfnObj = OpenMaya.MFnTripleIndexedComponent()
                connectedPointsMObject = connectedPointIndicesMfnObj.create(OpenMaya.MFn.kLatticeComponent)

            # SUBDIV SURFACE -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -
            elif isinstance(pyShape, pymel.nodetypes.Subdiv):
                geoIterClass = OpenMaya.MItSubdVertex

                connectedPointIndicesMfnObj = OpenMaya.MFnSingleIndexedComponent()
                connectedPointsMObject = connectedPointIndicesMfnObj.create(OpenMaya.MFn.kSubdivCVComponent)

                if 'wrapDimensions' not in componentDict:
                    componentDict['wrapDimensions'] = (False,)


            # create the geo iter
            geoIter = geoIterClass( mDagPath, mComponent )

            if origSpace:
                origShape = ka_deformers.getOrigShape(pyShape)
                origMDagPath = getMDagPath(str(origShape))
                origGeoIter = geoIterClass( origMDagPath, mComponent )

            if cameraSpace:
                cameraMatrix = ka_cameras.getCameraMatrix()

            # iterate components ----------------------------------------------------------------------------------
            geoIter_isDone = geoIter.isDone()
            if connectedPoints:
                connectedGeoIter_isDone = False
            else:
                connectedGeoIter_isDone = True

            geoIter_isReset = False

            while not (geoIter_isDone and connectedGeoIter_isDone):

                # get/set index for connected points
                if geoIter_isDone:
                    if geoIter_isReset is False:

                        geoIter = geoIterClass( mDagPath, connectedPointsMObject )
                        if origSpace:
                            origGeoIter = geoIterClass( origMDagPath, connectedPointsMObject )

                        geoIter_isReset = True

                    pointIndex = geoIter.index()
                    multiIndex = componentDict['multiIndex'][pointIndex]

                # get index of ORIGINAL (rather than connected) points
                else:
                    # INDEX
                    pointIndex = geoIter.index()

                    componentDict['pointDict'][pointIndex] = None

                    # Get MULTI INDEX
                    # nurbs and lattice   +    +    +    +    +    +    +    +    +    +    +    +    +    +    +    +    +    +
                    if isinstance(pyShape, pymel.nodetypes.NurbsSurface) or isinstance(pyShape, pymel.nodetypes.Lattice):
                        multiIndex = getMultiIndex_fromSingleIndex(pointIndex, maxDimensions=componentDict['maxDimensions'],
                                                                   form=componentDict['form'], degree=componentDict['degree'])

                    # poly and nurbsCurve   +    +    +    +    +    +    +    +    +    +    +    +    +    +    +    +    +    +
                    else:
                        multiIndex = (pointIndex,)

                    componentDict['multiIndex'][pointIndex] = multiIndex

                ## ADD ORIGINAL (rather than connected) points +    +    +    +    +    +    +    +    +    +    +    +
                #if not geoIter_isDone:



                # GET POSITIONS +    +    +    +    +    +    +    +    +    +    +    +    +    +    +    +    +    +
                if positions:
                    if worldSpace:
                        position = geoIter.position(OpenMaya.MSpace.kWorld)
                        componentDict['positionDict']['world'][pointIndex] = (position[0], position[1], position[2],)

                    if cameraSpace:
                        if worldSpace is None:
                            position = geoIter.position(OpenMaya.MSpace.kWorld)
                        position = ka_cameras.getInCameraSpace(position, cameraMatrix)
                        componentDict['positionDict']['camera'][pointIndex] = (position[0], position[1], position[2],)

                    if objectSpace:
                        position = geoIter.position(OpenMaya.MSpace.kObject)
                        componentDict['positionDict']['local'][pointIndex] = (position[0], position[1], position[2],)

                    if origSpace:
                        position = origGeoIter.position(OpenMaya.MSpace.kObject)
                        componentDict['positionDict']['orig'][pointIndex] = (position[0], position[1], position[2],)


                if normals:
                    try:
                        if worldSpace:
                            geoIter.getNormal(mVector, OpenMaya.MSpace.kWorld)
                            componentDict['normalDict']['world'][pointIndex] = (mVector[0], mVector[1], mVector[2],)

                        if objectSpace:
                            geoIter.getNormal(mVector, OpenMaya.MSpace.kObject)
                            componentDict['normalDict']['local'][pointIndex] = (mVector[0], mVector[1], mVector[2],)

                        if origSpace:
                            origGeoIter.getNormal(mVector, OpenMaya.MSpace.kObject)
                            componentDict['normalDict']['orig'][pointIndex] = (mVector[0], mVector[1], mVector[2],)

                    except AttributeError:
                        pass


                if connectedPoints:
                    if not geoIter_isDone:
                        if isinstance(pyShape, pymel.nodetypes.Mesh): # polygon mesh - - - - - - - - - - - - - - - - - - - -
                            connectedIndices = OpenMaya.MIntArray()

                            # connected verts
                            geoIter.getConnectedVertices(connectedIndices)
                            componentDict['connectedPointsDict'][pointIndex] = tuple(connectedIndices)

                            for connectedIndex in connectedIndices:
                                #connectedItemsStack[connectedIndex] = None
                                connectedPointIndicesMfnObj.addElement(connectedIndex)
                                componentDict['multiIndex'][connectedIndex] = (connectedIndex,)

                            # connected faces
                            geoIter.getConnectedFaces(connectedIndices)
                            componentDict['connectedFaceDict'][pointIndex] = tuple(connectedIndices)

                            for faceIndex in connectedIndices:
                                connectedFacesStack[faceIndex] = None

                            # connected edges
                            geoIter.getConnectedEdges(connectedIndices)
                            componentDict['connectedEdgesDict'][pointIndex] = tuple(connectedIndices)

                            componentDict['edgesOfPoint'][pointIndex] = connectedIndices

                            for connectedIndex in connectedIndices:
                                connectedEdgesStack[connectedIndex] = None

                        elif isinstance(pyShape, pymel.nodetypes.Mesh): # subDiv mesh - - - - - - - - - - - - - - - - - - - -
                            pass

                        else:
                        #elif isinstance(pyShape, pymel.nodetypes.NurbsSurface):    # NURBS ----------------------------------
                            connectedMultiIndices = []

                            connectedPoints = []
                            for i, index in enumerate(multiIndex):

                                # are we wraping this dimension?
                                wrap = False
                                if 'wrapDimensions' in componentDict:
                                    wrap =componentDict['wrapDimensions'][i]

                                # find last index for dimension
                                lastIndex = componentDict['maxDimensions'][i]-1

                                # if FIRST
                                if index == 0:
                                    connectedPointMultiIndex = list(multiIndex)
                                    connectedPointMultiIndex[i] = index+1
                                    connectedPointIndicesMfnObj.addElement(*connectedPointMultiIndex)    # needs multi index

                                    connectedPoint = getSingleIndex_fromMultiIndex(connectedPointMultiIndex, maxDimensions=componentDict['maxDimensions'], form=form, degree=degree)
                                    connectedPoints.append(connectedPoint)
                                    componentDict['multiIndex'][connectedPoint] = tuple(connectedPointMultiIndex)

                                    if wrap:
                                        connectedPointMultiIndex = list(multiIndex)
                                        connectedPointMultiIndex[i] = lastIndex
                                        connectedPointIndicesMfnObj.addElement(*connectedPointMultiIndex)    # needs multi index

                                        connectedPoint = getSingleIndex_fromMultiIndex(connectedPointMultiIndex, maxDimensions=componentDict['maxDimensions'], form=form, degree=degree)
                                        connectedPoints.append(connectedPoint)
                                        componentDict['multiIndex'][connectedPoint] = tuple(connectedPointMultiIndex)

                                # if LAST
                                elif index == lastIndex: # last
                                    connectedPointMultiIndex = list(multiIndex)
                                    connectedPointMultiIndex[i] = index-1
                                    connectedPointIndicesMfnObj.addElement(*connectedPointMultiIndex)    # needs multi index

                                    connectedPoint = getSingleIndex_fromMultiIndex(connectedPointMultiIndex, maxDimensions=componentDict['maxDimensions'], form=form, degree=degree)
                                    connectedPoints.append(connectedPoint)
                                    componentDict['multiIndex'][connectedPoint] = tuple(connectedPointMultiIndex)

                                    if wrap:
                                        connectedPointMultiIndex = list(multiIndex)
                                        connectedPointMultiIndex[i] = 0
                                        connectedPointIndicesMfnObj.addElement(*connectedPointMultiIndex)    # needs multi index

                                        connectedPoint = getSingleIndex_fromMultiIndex(connectedPointMultiIndex, maxDimensions=componentDict['maxDimensions'], form=form, degree=degree)
                                        connectedPoints.append(connectedPoint)
                                        componentDict['multiIndex'][connectedPoint] = tuple(connectedPointMultiIndex)


                                # NOT FIRST OR LAST
                                else:
                                    connectedPointMultiIndex = list(multiIndex)
                                    connectedPointMultiIndex[i] = index+1
                                    connectedPointIndicesMfnObj.addElement(*connectedPointMultiIndex)    # needs multi index

                                    connectedPoint = getSingleIndex_fromMultiIndex(connectedPointMultiIndex, maxDimensions=componentDict['maxDimensions'], form=form, degree=degree)
                                    connectedPoints.append(connectedPoint)
                                    componentDict['multiIndex'][connectedPoint] = tuple(connectedPointMultiIndex)


                                    connectedPointMultiIndex = list(multiIndex)
                                    connectedPointMultiIndex[i] = index-1
                                    connectedPointIndicesMfnObj.addElement(*connectedPointMultiIndex)    # needs multi index

                                    connectedPoint = getSingleIndex_fromMultiIndex(connectedPointMultiIndex, maxDimensions=componentDict['maxDimensions'], form=form, degree=degree)
                                    connectedPoints.append(connectedPoint)
                                    componentDict['multiIndex'][connectedPoint] = tuple(connectedPointMultiIndex)

                            componentDict['connectedPointsDict'][pointIndex] = tuple(connectedPoints)





                # step to next itteration
                geoIter.next()
                if origSpace:
                    origGeoIter.next()

                # has the first iter completed?
                if not geoIter_isDone:
                    geoIter_isDone = geoIter.isDone()

                # has the second iterCompleted?
                else:
                    connectedGeoIter_isDone = geoIter.isDone()

                # ----------------------------------------------------------------------------------


            # get polyFace and Edge Info ~ ~ ~ ~ ~q ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
            if isinstance(pyShape, pymel.nodetypes.Mesh):
                connectedIndices = OpenMaya.MIntArray()

                # polyFaces -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -
                geoIter_isDone = faceIter.isDone()
                while connectedFacesStack:

                    # get/set index
                    faceIndex = connectedFacesStack.popitem()[0]
                    faceIter.setIndex(faceIndex, mScriptUtil.asIntPtr())

                    # face dict
                    componentDict['faceDict'][faceIndex] = None

                    # edges of face
                    faceIter.getEdges(connectedIndices)
                    componentDict['edgesOfFace'][faceIndex] = tuple(connectedIndices)
                    for edgeIndex in connectedIndices:
                        connectedEdgesStack[edgeIndex] = None

                        # populated faces of Edge
                        if edgeIndex not in componentDict['facesOfEdge']:
                            componentDict['facesOfEdge'][edgeIndex] = [faceIndex]
                        else:
                            if faceIndex not in componentDict['facesOfEdge'][edgeIndex]:
                                if isinstance(componentDict['facesOfEdge'][edgeIndex], tuple):
                                    componentDict['facesOfEdge'][edgeIndex] = list(componentDict['facesOfEdge'][edgeIndex])
                                componentDict['facesOfEdge'][edgeIndex].append(faceIndex)

                    # points of faces
                    pointIndicesOfFace = OpenMaya.MIntArray()
                    faceIter.getVertices(pointIndicesOfFace)
                    componentDict['pointsOfFace'][faceIndex] = tuple(pointIndicesOfFace)

                    # faces of point
                    for pointIndex in pointIndicesOfFace:
                        if pointIndex in componentDict['facesOfPoint']:
                            if faceIndex not in componentDict['facesOfPoint'][pointIndex]:
                                if isinstance(componentDict['facesOfPoint'][pointIndex], tuple):
                                    componentDict['facesOfPoint'][pointIndex] = list(componentDict['facesOfPoint'][pointIndex])
                                componentDict['facesOfPoint'][pointIndex].append(faceIndex)
                        else:
                            componentDict['facesOfPoint'][pointIndex] = [faceIndex]

                # polyEdges -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -
                geoIter = OpenMaya.MItMeshEdge( mDagPath )

                geoIter_isDone = geoIter.isDone()
                while connectedEdgesStack:

                    # get/set index
                    edgeIndex = connectedEdgesStack.popitem()[0]
                    geoIter.setIndex(edgeIndex, mScriptUtil.asIntPtr())

                    componentDict['edgeDict'][edgeIndex] = None

                    # points of edge
                    pointA = geoIter.index(0)
                    pointB = geoIter.index(1)

                    componentDict['pointsOfEdge'][edgeIndex] = (pointA, pointB,)


                    # edge From Points
                    if pointA not in componentDict['edgeFromPoints']:
                        componentDict['edgeFromPoints'][pointA] = {}
                    componentDict['edgeFromPoints'][pointA][pointB] = edgeIndex

                    if pointB not in componentDict['edgeFromPoints']:
                        componentDict['edgeFromPoints'][pointB] = {}
                    componentDict['edgeFromPoints'][pointB][pointA] = edgeIndex


                    # edges Of Point
                    if pointA in componentDict['edgesOfPoint']:
                        if edgeIndex not in componentDict['edgesOfPoint'][pointA]:
                            if isinstance(componentDict['edgesOfPoint'][pointA], tuple):
                                componentDict['edgesOfPoint'][pointA] = list(componentDict['edgesOfPoint'][pointA])
                            componentDict['edgesOfPoint'][pointA].append(edgeIndex)
                    else:
                        componentDict['edgesOfPoint'][pointA] = [edgeIndex]

                    if pointB in componentDict['edgesOfPoint']:
                        if edgeIndex not in componentDict['edgesOfPoint'][pointB]:
                            if isinstance(componentDict['edgesOfPoint'][pointB], tuple):
                                componentDict['edgesOfPoint'][pointB] = list(componentDict['edgesOfPoint'][pointB])
                            componentDict['edgesOfPoint'][pointB].append(edgeIndex)
                    else:
                        componentDict['edgesOfPoint'][pointB] = [edgeIndex]




                # cast all lists to tuples to save memory
                for edgeIndex in componentDict['facesOfEdge']:
                    componentDict['facesOfEdge'][edgeIndex] = tuple(componentDict['facesOfEdge'][edgeIndex])

                for pointIndex in componentDict['edgesOfPoint']:
                    componentDict['edgesOfPoint'][pointIndex] = tuple(componentDict['edgesOfPoint'][pointIndex])

                for pointIndex in componentDict['facesOfPoint']:
                    componentDict['facesOfPoint'][pointIndex] = tuple(componentDict['facesOfPoint'][pointIndex])

        mNodeIter.next()

    cmds.select(selection)
    return componentInfoDict




class iterShapes(object):
    def __init__(self, items=None):

        mSelectionList = OpenMaya.MSelectionList()

        if items is None:
            OpenMaya.MGlobal.getActiveSelectionList(mSelectionList) # store selection to mSelectionList

        elif not isinstance(components, list) and not isinstance(components, tuple):
            mSelectionList.add(str(items))

        else:
            for component in components:
                mSelectionList.add(str(items))

        self.mNodeIter = OpenMaya.MItSelectionList(mSelectionList) # create iterator from mSelectionList

    def __iter__(self):
        return self

    def next(self): # Python 3: def __next__(self)
        if self.mNodeIter.isDone():
            raise StopIteration

        else:
            mDagPath = OpenMaya.MDagPath()
            mComponent = OpenMaya.MObject()

            self.mNodeIter.getDagPath( mDagPath, mComponent ) # dagPath and component are passed as references; the function itself returns null, so you don't want to store its return value in dagPath
            mDagPath.extendToShape()
            shapeName = mDagPath.partialPathName()
            shape = pymel.PyNode(shapeName)

            self.mNodeIter.next()

            return shape

class iterateGeo(object):
    def __init__(self, shape=None, components=None, yieldInfo='index', componentInfoDict=None):
        """
        Itterates through the given components on the given geometry

        Itterates through the given components on the given geometry,
        yeilding information about the point. This function helps to
        insure that you iterate the geometry in the same order as maya
        API would (which is not alway straight forward on types like nurbs
        surfaces).

        Further information about each component can be queried from a
        componentInfoDictionary using the indices yielded.

        Args:
            shape (pyShape/MDagPath, optional): the shape the components are on

            components (list/tuple/MObject, optional): list of point indices or an MObject
                representing maya components

            componentInfoDict (dict, optional): componentInfoDict (*see getComponentInfoDict) for the given
                shape. Passing this variable will prevent unessisary calculation.

        Yields:
            (int): the index of the component

        """

        # parse args
        if shape is None and components is None:
            shape_mDagPath = OpenMaya.MDagPath()
            components_mObject = OpenMaya.MObject()
            mSelectionList = OpenMaya.MSelectionList()
            OpenMaya.MGlobal.getActiveSelectionList(mSelectionList)
            mSelectionList.getDagPath(0, shape_mDagPath, components_mObject)


        elif isinstance(shape, OpenMaya.MDagPath):
            shape_mDagPath = shape

        elif ka_pymel.isPyShape(shape):
            shape_mDagPath = shape.__apimdagpath__()

        if isinstance(components, OpenMaya.MObject):
            components_mObject = components

        elif isinstance(components, list) or isinstance(components, tuple):
            components_mObject = getIndicesOfShape_asMObject(shape_mDagPath, components,
                                                             componentInfoDict=componentInfoDict)

        # create itterator
        geoIterClass = _getGeoIteratorClass_(shape_mDagPath)
        geoIterator = geoIterClass( shape_mDagPath, components_mObject )

        # itterator attrs
        self.i = -1
        self.indices = []
        while not geoIterator.isDone():
            self.indices.append(geoIterator.index())
            geoIterator.next()

        self.indices = tuple(self.indices)
        self.lastI = len(self.indices)

    def __iter__(self):
        return self


    def next(self): # Python 3: def __next__(self)
        self.i += 1

        if self.i >= self.lastI:
            raise StopIteration

        return self.indices[self.i]



def _getPointIterator_(shape, mDagPath, mComponent):
    if isinstance(shape, pymel.nodetypes.Mesh):
        return OpenMaya.MItMeshVertex( mDagPath, mComponent )

    elif isinstance(shape, pymel.nodetypes.NurbsSurface):
        return OpenMaya.MItSurfaceCV( mDagPath, mComponent )

    elif isinstance(shape, pymel.nodetypes.NurbsCurve):
        return OpenMaya.MItCurveCV( mDagPath, mComponent )

    elif isinstance(shape, pymel.nodetypes.Lattice):
        return OpenMaya.MItGeometry( mDagPath, mComponent )

    elif isinstance(shape, pymel.nodetypes.Subdiv):
        return OpenMaya.MItSubdVertex( mDagPath, mComponent )