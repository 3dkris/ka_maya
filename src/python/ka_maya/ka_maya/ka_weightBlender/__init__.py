#====================================================================================
#====================================================================================
#
# ka_weightBlender
#
# DESCRIPTION:
#   blends between sets of weights, usually by sampling surounding components
#
# DEPENDENCEYS:
#   ka_weightUtils
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

import time

import maya.cmds as cmds
import pymel.core as pymel
import maya.mel as mel
import maya.OpenMaya as OpenMaya
import math


import ka_maya.ka_math as ka_math
import ka_maya.ka_python as ka_python
import ka_maya.ka_pymel as ka_pymel
import ka_maya.ka_preference as ka_preference
import ka_maya.ka_skinCluster as ka_skinCluster
import ka_maya.ka_geometry as ka_geometry
import ka_maya.ka_weightPainting as ka_weightPainting


# ===================================================================================================================================================
# ===================================================================================================================================================
class WeightBlenderInfo(object):

    def __init__(self, strandInfoDict=None, selection=None):
        t0 = time.clock()

        if selection is None:
            self.selection = cmds.ls(selection=True)
        else:
            self.selection = selection

        # target icons
        self.deleteTargetIcons()

        self.mode = None    # can be 'parallelBlend' or 'strandBlend'
        self.iconPointsA = {}
        self.iconPointsB = {}

        self.targetIconsADict = {}
        self.targetIconsBDict = {}

        self.targetIconsShaderA = None    # (lambertA, shadingEngineA)
        self.targetIconsShaderB = None    # (lambertB, shadingEngineB)
        self.lambertAIsBlack = True
        self.lambertBIsBlack = True

        # weight info
        self.weightDict = {}                # (key=pointID, value=dictionary (key=influenceIndex, value=weightValue))
        self.paintMapDicts = {}

        # strand length info
        self.strandLengthDict = {}
        self.strandComponentLengths = {}    # key=strandID, value=tuple(point0LengthAlongCurve, ...)
        self.strandComponentLengthRatios = {}
        # targetA/B WeightDict contains the pre averaged weights of the targetsA and B for given selected points
        # (as a point may have multiple targetsA or B)
        self.targetAWeightDict = {}    # (key=pointID(of original point, not target), value=dictionary (key=influenceIndex, value=weightValue))
        self.targetBWeightDict = {}    # (key=pointID(of original point, not target), value=dictionary (key=influenceIndex, value=weightValue))

        if strandInfoDict is None:
            self.strandInfoDict = ka_geometry.getStrandInfoDict(checkSelectionMatches=True)
        else:
            self.strandInfoDict = strandInfoDict


        for shapeID in self.strandInfoDict:
            shape = self.strandInfoDict[shapeID]['componentInfoDict']['pyShape']
            paintDict = ka_weightPainting.getCurrentPaintMapDict(shape=shape)
            self.paintMapDicts[shapeID] = paintDict



        # create strand sequences
        self.strandSequenceIndices = (0,0,0) # shapeIDIndex, strandIDIndex, sequenceIndex
        self.strandSequenceDict = {}
        # self.strandSequenceDict = {23452345:'113:116':{'targetSequences':{334:(((332,), (424,),), ((332,), (425,),),),  # <-- <point>:
        #                                                                   335:(((333,), (424,),), ((331,), (425,),),),
        #                                                                  },
        #                                                'currentSequenceIndex':0,
        #                                                'currentTargetSequence':{334:((332,), (424,),),
        #                                                                         335:((333,), (424,),)
        #                                                                        },
        #                                                'iconsA':{334:(<pyTransform>,),
        #                                                          335:(<pyTransform>,),
        #                                                         },
        #                                                'iconsB':{334:(<pyTransform>,),
        #                                                          335:(<pyTransform>,),
        #                                                         },
        #                                               },
        #                           }

        for shapeID in self.strandInfoDict:
            strandDict = self.strandInfoDict[shapeID]
            componentDict = self.strandInfoDict[shapeID]['componentInfoDict']

            self.strandSequenceDict[shapeID] = {}

            # gather possible variations of target combinations, so we can form a list
            # from that
            self.strandSequenceDict[shapeID] = {}

            for i, strandID in enumerate(self.strandInfoDict[shapeID]['strandDict']):
                strand = self.strandInfoDict[shapeID]['strandDict'][strandID]
                self.strandSequenceDict[shapeID][strandID] = {}
                self.strandSequenceDict[shapeID][strandID]['targetSequences'] = {}
                self.strandSequenceDict[shapeID][strandID]['currentTargetSequence'] = {}
                self.strandSequenceDict[shapeID][strandID]['currentSequenceIndex'] = 0
                self.strandSequenceDict[shapeID][strandID]['iconsA'] = {}
                self.strandSequenceDict[shapeID][strandID]['iconsB'] = {}

                for point in strand:

                    # Single Point Strand
                    if len(strand) == 1:
                        point = strand[0]
                        self.strandSequenceDict[shapeID][strandID]['targetSequences'][point] = (((strandDict['pointNeighbors'][point]['left']), (strandDict['pointNeighbors'][point]['right']),),
                                                                                                ((strandDict['pointNeighbors'][point]['up']), (strandDict['pointNeighbors'][point]['down']),),
                                                                                                )

                    # Multi Point Strand
                    else:
                        self.strandSequenceDict[shapeID][strandID]['targetSequences'][point] = (((strandDict['pointNeighbors'][point]['left']), (strandDict['pointNeighbors'][point]['right']),),
                                                                                                ((strandDict['pointNeighbors'][point]['up']), (strandDict['pointNeighbors'][point]['down']),),
                                                                                                )

                    self.strandSequenceDict[shapeID][strandID]['currentTargetSequence'][point] = self.strandSequenceDict[shapeID][strandID]['targetSequences'][point][0]

        TTTTTTT = "        create strand sequences"; print '%s Step Took %s sec' % (TTTTTTT, str(round(time.clock()-t0, 4))) ;t0 = time.clock()

    # START METHODS ==================================================================
    def startParallelBlend(self, createTargetIcons=True):
        self.mode = 'parallelBlend'

        if createTargetIcons:
            self.createTargetIcons()

        self.storeWeights(refresh=True)

    def startStrandBlend(self):
        self.mode = 'strandBlend'

        self.storeWeights(refresh=True)

        #skinClusterInfluences = []
        #for shapeID in self.paintMapDicts:
            #if self.paintMapDicts[shapeID]['nodeType'] == 'skinCluster':
                #skinCluster = ka_pymel.getAsPyNodes(self.paintMapDicts[shapeID]['nodeName'])
                #influences = ka_skinCluster.getInfluences(skinCluster)

                #for influence in influences:
                    #influence.lockInfluenceWeights.set(0)

    def _populateStrandLengthInfo_(self):
        """calculate and store information about the length of each strand, and the components in them"""

        for shapeID in self.strandInfoDict:
            self.strandLengthDict[shapeID] = {}
            self.strandComponentLengths[shapeID] = {}
            self.strandComponentLengthRatios[shapeID] = {}

            for strandID in self.strandInfoDict[shapeID]['strandDict']:
                strand = self.strandInfoDict[shapeID]['strandDict'][strandID]

                if len(strand) > 2:
                    geoInfoDict = self.strandInfoDict[shapeID]['componentInfoDict']

                    self.strandLengthDict[shapeID][strandID] = 0.0
                    self.strandComponentLengths[shapeID][strandID] = [0.0]
                    self.strandComponentLengthRatios[shapeID][strandID] = [0.0]

                    # get strand length
                    #strandLength = 0.0
                    #strandComponentLengths = [0.0]
                    prevPointPos = geoInfoDict['positionDict']['orig'][strand[0]]
                    for point in strand[1:]:
                        pointPos = geoInfoDict['positionDict']['orig'][point]
                        componentLength = ka_math.distanceBetween(prevPointPos, pointPos)

                        # add to strand length
                        self.strandLengthDict[shapeID][strandID] += componentLength

                        # append to component lengths
                        self.strandComponentLengths[shapeID][strandID].append(self.strandLengthDict[shapeID][strandID])

                        # store this point as previous point
                        prevPointPos = pointPos

                    for i, point in enumerate(strand[1:]):
                        ratio = self.strandComponentLengths[shapeID][strandID][i+1] / self.strandLengthDict[shapeID][strandID]
                        self.strandComponentLengthRatios[shapeID][strandID].append(ratio)


    # BLEND METHODS ==================================================================
    def blend(self, *args, **kwargs):
        """select which blend is apropriate for the mode"""

        if self.mode == 'parallelBlend':
            return self.parallelBlend(*args, **kwargs)

        elif self.mode == 'strandBlend':
            self._populateStrandLengthInfo_()
            return self.strandBlend(*args, **kwargs)


    # ----------------------------------------------------------------------------------------------------------------------
    def strandBlend(self, blendValues=[0, 30, 70, 100]):
        """main function, usually called by a change in a slider values (so potentially called often in succession)

        """
        #t0 = time.clock()
        weightInfoDict = {}

        #strength = blendValues[1]/50.0
        #strength = (strength*4.0)+1.0
        #OOOOOOO = "strength"; print '%s: ' % OOOOOOO, eval(OOOOOOO), ' ', type(eval(OOOOOOO))

        for shapeID in self.strandInfoDict:
            weightInfoDict[shapeID] = {}
            weightInfoDict[shapeID]['values'] = {}

            for strandID in self.strandInfoDict[shapeID]['strandDict']:
                strand = self.strandInfoDict[shapeID]['strandDict'][strandID]

                # can not strand blend between less than 3 points, so just copy the weights 1 to 1 if the
                # strand is too short
                if len(strand) < 3:
                    for point in strand:
                        weightInfoDict[shapeID]['values'][point] = self.weightDict[shapeID]['values'][point]

                else:
                    geoInfoDict = self.strandInfoDict[shapeID]['componentInfoDict']
                    firstPoint = strand[0]
                    lastPoint = strand[-1]

                    firstWeight = self.weightDict[shapeID]['values'][firstPoint]
                    lastWeight = self.weightDict[shapeID]['values'][lastPoint]

                    ## get strand length
                    #strandLength = 0.0
                    #strandComponentLengths = [0.0]
                    #prevPointPos = geoInfoDict['positionDict']['orig'][firstPoint]
                    #for point in strand[1:]:
                        #pointPos = geoInfoDict['positionDict']['orig'][point]
                        #componentLength = ka_math.distanceBetween(prevPointPos, pointPos)
                        #strandLength += componentLength
                        #strandComponentLengths.append(strandLength)
                        #prevPointPos = pointPos

                    #OOOOOOO = "strandLength"; print '%s: ' % OOOOOOO, eval(OOOOOOO), ' ', type(eval(OOOOOOO))

                    # find the blended value
                    ratioSegments = 100.0/(len(strand)-1)
                    previousParamT = 0.0
                    for i, point in enumerate(strand[1:-1]):
                        #percentOfTotal = strandComponentLengths[i+1]/strandLength
                        percentOfTotal = self.strandComponentLengthRatios[shapeID][strandID][i+1]
                        weightedAverage = 1.0 * percentOfTotal
                        #OOOOOOO = "percentOfTotal"; print '%s= ' % OOOOOOO, eval(OOOOOOO), ' #', type(eval(OOOOOOO))
                        #null, weightedAverage = ka_math.bezier(((float(blendValues[0] * 0.01), 0.0,), (float(blendValues[1] * 0.01), 0.0,),
                                                                #(float(blendValues[2] * 0.01), 1.0,), (float(blendValues[3] * 0.01), 1.0,),),
                                                                 #weightedAverage)
                        paramT, weightedAverageValue = ka_math.bezier(((0.0, 0.0,), (float(blendValues[1] * 0.01), 0.0,),
                                                                (float(blendValues[2] * 0.01), 1.0,), (1.0, 1.0,),),
                                                                 weightedAverage,)
                        remainder = 1.0 - weightedAverageValue

                        blendValueWeightValue = ka_weightPainting.getWeightedAverageOfWeightValues((firstWeight, lastWeight,), weights=(remainder, weightedAverageValue))

                        weightInfoDict[shapeID]['values'][point] = blendValueWeightValue

                        #previousParamT = weightedAverage
                        #OOOOOOO = "previousWeightedAverage"; print '%s: ' % OOOOOOO, eval(OOOOOOO), ' ', type(eval(OOOOOOO))
        #TTTTTTT = "    pre setWeights"; print '%s Step Took %s sec' % (TTTTTTT, str(round(time.clock()-t0, 4))) ;t0 = time.clock()

        ka_weightPainting.setWeights(weightInfoDict=weightInfoDict, paintMapDicts=self.paintMapDicts)
        #TTTTTTT = "    setWeights"; print '%s Step Took %s sec' % (TTTTTTT, str(round(time.clock()-t0, 4))) ;t0 = time.clock()




    # ----------------------------------------------------------------------------------------------------------------------
    def parallelBlend(self, blendValue=100, bothNeighbors=False):
        """main function, usually called by a change in a slider value (so potentially called often in succession)

        kwargs:
            percent - int 0-200 - a value representing the value to blend. if 100, then the weights will be the same as
                                  they started, if they are 0, then they will be 100% blended to targetA, if the value
                                  is 200, then the value will be blended 100% to targetB.
        """

        weightInfoDict = {}

        # get the percent of the blend value and it's remainder
        if blendValue < 100:
            if bothNeighbors:
                percent = (100 - blendValue)*0.005
            else:
                percent = (100 - blendValue)*0.01

        elif blendValue > 100:
            if bothNeighbors:
                percent = (blendValue - 100)*0.005
            else:
                percent = (blendValue - 100)*0.01

        else:
            percent = 0.0

        # get remainder
        if bothNeighbors:
            percentRemainder = 1.0-(percent*2)
        else:
            percentRemainder = 1.0-percent


        for shapeID in self.strandSequenceDict:
            weightInfoDict[shapeID] = {}
            weightInfoDict[shapeID]['values'] = {}

            for strandID in self.strandSequenceDict[shapeID]:
                for point in self.strandInfoDict[shapeID]['strandDict'][strandID]:
                    strandTargetSets = self.strandSequenceDict[shapeID][strandID]['currentTargetSequence'][point]

                    # get the points involved in the blendValue
                    if blendValue < 100:
                        blendValueTargets = strandTargetSets[0]

                        #for i, points in enumerate(blendValueTargets):
                            #print 'p  ', self.strandInfoDict[shapeID]['componentInfoDict']['multiIndex'][point]
                            #print 'u  ', self.strandInfoDict[shapeID]['componentInfoDict']['multiIndex'][points]
                            ##print 'd  ', strandInfoDict[shapeID]['componentInfoDict']['multiIndex'][points[0]]
                            ##print ""

                        if bothNeighbors:
                            oppositeBlendTargets = strandTargetSets[1]

                    elif blendValue > 100:
                        blendValueTargets = strandTargetSets[1]
                        if bothNeighbors:
                            oppositeBlendTargets = strandTargetSets[0]

                    else: # is at 100, ie: inital position, with no blendValueing
                        blendValueTargets = (point,)
                        if bothNeighbors:
                            oppositeBlendTargets = (point,)

                    # get Weight(s) A (weights of the original point)
                    weightsA = self.weightDict[shapeID]['values'][point]


                    # get Weight(s) B
                    if len(blendValueTargets) == 1:
                        weightsB = self.weightDict[shapeID]['values'][blendValueTargets[0]]

                    else:
                        # this would be the case if a strand point was not an end point and
                        # was connected to 5 edges or more
                        weightSetsB = []
                        for blendValueTarget in blendValueTargets:
                            weightSetsB.append(self.weightDict[shapeID]['values'][blendValueTarget])
                        weightSetsB = tuple(weightSetsB)
                        weightsB = ka_weightPainting.getWeightedAverageOfWeightValues(weightSetsB,)

                    # get Weight(s) C, but only if we are blendValueing both neighbors
                    if bothNeighbors:
                        if len(blendValueTargets) == 1:
                            weightsC = self.weightDict[shapeID]['values'][oppositeBlendTargets[0]]
                        else:
                            # this would be the case if a strand point was not an end point and
                            # was connected to 5 edges or more
                            weightSetsC = []
                            for blendValueTarget in oppositeBlendTargets:
                                weightSetsC.append(self.weightDict[shapeID]['values'][blendValueTarget])
                            weightSetsC = tuple(weightSetsC)
                            weightsC = ka_weightPainting.getWeightedAverageOfWeightValues(weightSetsC,)




                    if bothNeighbors:
                        blendValueedWeightValue = ka_weightPainting.getWeightedAverageOfWeightValues((weightsA, weightsB, weightsC), weights=(percentRemainder, percent, percent))

                    else:
                        blendValueedWeightValue = ka_weightPainting.getWeightedAverageOfWeightValues((weightsA, weightsB,), weights=(percentRemainder, percent))

                    weightInfoDict[shapeID]['values'][point] = blendValueedWeightValue

        ka_weightPainting.setWeights(weightInfoDict=weightInfoDict, paintMapDicts=self.paintMapDicts)

        ###########################
        # color Spheres
        if self.targetIconsShaderA:
            if bothNeighbors and blendValue != 100:
                if blendValue == 0 or blendValue == 200:
                    self.targetIconsShaderA[0].incandescence.set(1, 1, 1)
                    self.targetIconsShaderB[0].incandescence.set(1, 1, 1)
                else:
                    self.targetIconsShaderA[0].incandescence.set((percent*2), 0.25+((percent*2)*0.75), (percent*2)*0.15)
                    self.targetIconsShaderB[0].incandescence.set((percent*2), 0.25+((percent*2)*0.75), (percent*2)*0.15)
                self.lambertAIsBlack = False
                self.lambertBIsBlack = False


            elif blendValue < 100:
                if blendValue == 0:
                    self.targetIconsShaderA[0].incandescence.set(1, 1, 1)
                else:
                    self.targetIconsShaderA[0].incandescence.set(percent, 0.25+(percent*0.75), percent*0.15)
                self.lambertAIsBlack = False

                if not self.lambertBIsBlack:
                    self.targetIconsShaderB[0].incandescence.set(0, 0, 0)
                    self.lambertBIsBlack = True

            elif blendValue > 100:
                if blendValue == 200:
                    self.targetIconsShaderB[0].incandescence.set(1, 1, 1)
                else:
                    self.targetIconsShaderB[0].incandescence.set(percent, 0.25+(percent*0.75), percent*0.15)
                self.lambertBIsBlack = False

                if not self.lambertAIsBlack:
                    self.targetIconsShaderA[0].incandescence.set(0, 0, 0)
                    self.lambertAIsBlack = True

            else: #is 100 (50%)
                if not self.lambertBIsBlack:
                    self.targetIconsShaderB[0].incandescence.set(0, 0, 0)
                    self.lambertBIsBlack = True

                if not self.lambertAIsBlack:
                    self.targetIconsShaderA[0].incandescence.set(0, 0, 0)
                    self.lambertAIsBlack = True


    # ----------------------------------------------------------------------------------------------------------------------
    def storeWeights(self, refresh=False):
        if refresh:
            self.weightDict = {}

            inputDict = {}
            for shapeID in self.strandInfoDict:
                pyShape = self.strandInfoDict[shapeID]['componentInfoDict']['pyShape']
                inputDict[shapeID] = {}

                for strandID in self.strandSequenceDict[shapeID]:
                    for point in self.strandSequenceDict[shapeID][strandID]['currentTargetSequence']:

                        if self.mode == 'parallelBlend':
                            pointMultiIndex = self.strandInfoDict[shapeID]['componentInfoDict']['multiIndex'][point]
                            inputDict[shapeID][point] = None

                            for targetPoint in self.strandSequenceDict[shapeID][strandID]['currentTargetSequence'][point][0]:
                                targetMultiIndex = self.strandInfoDict[shapeID]['componentInfoDict']['multiIndex'][targetPoint]
                                inputDict[shapeID][targetPoint] = None

                            for targetPoint in self.strandSequenceDict[shapeID][strandID]['currentTargetSequence'][point][1]:
                                targetMultiIndex = self.strandInfoDict[shapeID]['componentInfoDict']['multiIndex'][targetPoint]
                                inputDict[shapeID][targetPoint] = None

                        elif self.mode == 'strandBlend':

                            pointMultiIndex = self.strandInfoDict[shapeID]['componentInfoDict']['multiIndex'][point]
                            inputDict[shapeID][point] = None

            componentInfoDict = {}
            for shapeID in self.strandInfoDict:
                componentInfoDict[shapeID] = self.strandInfoDict[shapeID]['componentInfoDict']

            self.weightDict = ka_weightPainting.getWeights(inputDict=inputDict, componentInfoDict=componentInfoDict, paintMapDicts=self.paintMapDicts)


    def _changeSequence(self, amount=1):
        shapeIndex, strandIndex, sequenceIndex = self.strandSequenceIndices

        shapeIDs = tuple(self.strandInfoDict.keys())
        shapeID = shapeIDs[shapeIndex]

        strandIDs = tuple(self.strandInfoDict[shapeID]['strandDict'].keys())
        strandID = strandIDs[strandIndex]

        randomPoint = self.strandSequenceDict[shapeID][strandID]['targetSequences'].keys()[0]
        lastSequenceIndex = len(self.strandSequenceDict[shapeID][strandID]['targetSequences'][randomPoint])-1

        # next sequence
        # try to jump to next strand or first strand if we've reach the end
        if amount > 0:
            if sequenceIndex == lastSequenceIndex:
                sequenceIndex = 0
            else:
                sequenceIndex += amount

        # prev sequence
        else:
            if sequenceIndex == 0:
                sequenceIndex = lastSequenceIndex
            else:
                sequenceIndex += amount

        # set the new currentSequenceIndex for the item
        self.strandSequenceDict[shapeID][strandID]['currentSequenceIndex'] = sequenceIndex
        self.strandSequenceIndices = (shapeIndex, strandIndex, sequenceIndex,)

        # set the new currentTargetSequence
        for point in self.strandSequenceDict[shapeID][strandID]['targetSequences']:
            self.strandSequenceDict[shapeID][strandID]['currentTargetSequence'][point] = self.strandSequenceDict[shapeID][strandID]['targetSequences'][point][sequenceIndex]

        self.storeWeights(refresh=True)
        self.setTargetIconPositions()

    def nextSequence(self):
        self._changeSequence()

    def previousSequence(self):
        self._changeSequence(amount=-1)

    def createTargetIcons(self):
        self.deleteTargetIcons()

        panel = getCurrentPannel()
        isolateState = pymel.isolateSelect(panel, query=True, state=True)
        radius = 1

        if not self.targetIconsShaderA:    # make lambert for A spheres
            lambertA = pymel.shadingNode('lambert', asShader=True, name='DELETE_ME__TEMP_rightLambert')
            lambertA.addAttr('createColoredVertexSpheres_tempType', dt='string')
            lambertA.color.set( [0,0,0] )
            lambertA.transparency.set( [0.5,0.5,0.5] )

            shadingEngineA = pymel.sets(renderable=True, noSurfaceShader=True, empty=True, name='DELETE_ME__TEMP_rightshadingEngine')
            shadingEngineA.addAttr('createColoredVertexSpheres_tempType', dt='string')
            pymel.connectAttr(lambertA+".outColor", shadingEngineA+".surfaceShader", force=True)
            self.targetIconsShaderA = (lambertA, shadingEngineA)


        if not self.targetIconsShaderB:    # make lambert for B spheres
            lambertB = pymel.shadingNode('lambert', asShader=True, name='DELETE_ME__TEMP_rightLambert')
            lambertB.addAttr('createColoredVertexSpheres_tempType', dt='string')
            lambertB.color.set( [0,0,0] )
            lambertB.transparency.set( [0.5,0.5,0.5] )

            shadingEngineB = pymel.sets(renderable=True, noSurfaceShader=True, empty=True, name='DELETE_ME__TEMP_rightshadingEngine')
            shadingEngineB.addAttr('createColoredVertexSpheres_tempType', dt='string')
            pymel.connectAttr(lambertB+".outColor", shadingEngineB+".surfaceShader", force=True)
            self.targetIconsShaderB = (lambertB, shadingEngineB)

        # create Icon A
        targetIconAOrig = pymel.sphere(name='DELETE_ME__targetASpheres', radius=radius, sections=1, startSweep=180, spans=2)[0]
        #targetIconAOrig = pymel.torus(axis=(0,0,-1), radius=radius*.666, heightRatio=0.33, sections=1, startSweep=20, endSweep=160, spans=4)[0]
        targetIconAOrig.rename('DELETE_ME__targetASpheres')
        targetIconAOrig.overrideEnabled.set(1)
        targetIconAOrig.drawOverride.overrideColor.set(2)

        targetIconAOrig.addAttr('createColoredVertexSpheres_tempType', dt='string')
        pymel.sets( shadingEngineA, forceElement=targetIconAOrig, )

        # create Icon B
        targetIconBOrig = pymel.sphere(name='DELETE_ME__targetBSpheres', radius=radius, sections=1, startSweep=180, spans=2)[0]
        #targetIconBOrig = pymel.torus(axis=(0,0,-1), radius=radius*.666, heightRatio=0.33, sections=1, startSweep=20, endSweep=160, spans=4)[0]
        targetIconBOrig.rename('DELETE_ME__targetBSpheres')
        targetIconBOrig.overrideEnabled.set(1)
        targetIconBOrig.drawOverride.overrideColor.set(2)

        targetIconBOrig.addAttr('createColoredVertexSpheres_tempType', dt='string')
        pymel.sets( shadingEngineB, forceElement=targetIconBOrig, )



        for shapeID in self.strandSequenceDict:
            for strandID in self.strandSequenceDict[shapeID]:

                for point in self.strandSequenceDict[shapeID][strandID]['targetSequences']:
                    targetPointSets = self.strandSequenceDict[shapeID][strandID]['currentTargetSequence'][point]
                    targetPointSetsA = targetPointSets[0]
                    targetPointSetsB = targetPointSets[1]

                    # Instance Sphere A
                    targetIcons = []
                    for targetA in targetPointSetsA:
                        if targetA is not None:
                            targetIconA = pymel.instance(targetIconAOrig,)[0]
                            targetIconA.rename('DELETE_ME__targetASpheres')

                            targetIcons.append(targetIconA)

                            if isolateState:
                                pymel.isolateSelect(panel, addDagObject=targetIconA)

                        else:
                            targetIcons.append(None)

                    self.strandSequenceDict[shapeID][strandID]['iconsA'][point] = tuple(targetIcons)

                    # Instance Sphere B
                    targetIcons = []
                    for targetB in targetPointSetsB:
                        if targetB is not None:
                            targetIconB = pymel.instance(targetIconBOrig,)[0]
                            targetIconB.rename('DELETE_ME__targetBSpheres')

                            targetIcons.append(targetIconB)

                            if isolateState:
                                pymel.isolateSelect(panel, addDagObject=targetIconB)

                        else:
                            targetIcons.append(None)

                    self.strandSequenceDict[shapeID][strandID]['iconsB'][point] = tuple(targetIcons)


        targetIconAOrig.v.set(0)
        targetIconBOrig.v.set(0)

        self.setTargetIconPositions()

        #pymel.select(self.pointsInNodesDict.keys())
        #pymel.select(clear=True)
        pymel.select(self.selection)
        for shapeID in self.strandInfoDict:
            shapeNode = self.strandInfoDict[shapeID]['componentInfoDict']['pyShape']
            mel.eval( 'hilite %s' % str(shapeNode))


    def setTargetIconPositions(self):

        for shapeID in self.strandSequenceDict:
            for strandID in self.strandSequenceDict[shapeID]:

                for point in self.strandSequenceDict[shapeID][strandID]['currentTargetSequence']:
                    pointPos = self.strandInfoDict[shapeID]['componentInfoDict']['positionDict']['world'][point]
                    if point in self.strandInfoDict[shapeID]['componentInfoDict']['normalDict']['world']:
                        pointNormal = self.strandInfoDict[shapeID]['componentInfoDict']['normalDict']['world'][point]
                    else:
                        pointNormal = (0.0, 1.0, 0.0)


                    targetPointSets = self.strandSequenceDict[shapeID][strandID]['currentTargetSequence'][point]
                    targetPointSetsA = targetPointSets[0]
                    targetPointSetsB = targetPointSets[1]

                    # targetsA
                    for i, targetPoint in enumerate(targetPointSetsA):
                        if targetPoint is not None:
                            targetIcon = self.strandSequenceDict[shapeID][strandID]['iconsA'][point][i]

                            targetPos = self.strandInfoDict[shapeID]['componentInfoDict']['positionDict']['world'][targetPoint]
                            distanceToPoint = ka_math.distanceBetween(targetPos, pointPos)

                            # figure size
                            distanceToCamera = abs(self.strandInfoDict[shapeID]['componentInfoDict']['positionDict']['camera'][targetPoint][2])
                            scale = distanceToPoint * 0.2
                            sizeMax = (distanceToCamera * 0.01)
                            sizeMin = (distanceToCamera * 0.0045)
                            if scale > sizeMax:
                                scale = sizeMax
                            elif scale < sizeMin:
                                scale = sizeMin


                            # figure trans/rot
                            vectorY = ka_math.normalize(ka_math.subtract(pointPos, targetPos))
                            vectorX = ka_math.crossProduct(vectorY, pointNormal)
                            vectorZ = ka_math.crossProduct(vectorX, vectorY)
                            vectorX = ka_math.crossProduct(vectorZ, vectorY)

                            vectorX = ka_math.multiply(vectorX, scale)
                            vectorY = ka_math.multiply(vectorY, scale)
                            vectorZ = ka_math.multiply(vectorZ, scale)

                            targetMatrix = (vectorX[0],vectorX[1],vectorX[2],0, vectorY[0],vectorY[1],vectorY[2],0, vectorZ[0],vectorZ[1],vectorZ[2],0, targetPos[0], targetPos[1], targetPos[2], 1)
                            pymel.xform(targetIcon, matrix=targetMatrix, worldSpace=True)

                    # targets B
                    for i, targetPoint in enumerate(targetPointSetsB):
                        if targetPoint is not None:
                            targetIcon = self.strandSequenceDict[shapeID][strandID]['iconsB'][point][i]

                            targetPos = self.strandInfoDict[shapeID]['componentInfoDict']['positionDict']['world'][targetPoint]
                            distanceToPoint = ka_math.distanceBetween(targetPos, pointPos)

                            # figure size
                            distanceToCamera = abs(self.strandInfoDict[shapeID]['componentInfoDict']['positionDict']['camera'][targetPoint][2])
                            scale = distanceToPoint * 0.2
                            sizeMax = (distanceToCamera * 0.01)
                            sizeMin = (distanceToCamera * 0.0025)
                            if scale > sizeMax:
                                scale = sizeMax

                            elif scale < sizeMin:
                                scale = sizeMin

                            # figure trans/rot
                            vectorY = ka_math.normalize(ka_math.subtract(pointPos, targetPos))
                            vectorX = ka_math.crossProduct(vectorY, pointNormal)
                            vectorZ = ka_math.crossProduct(vectorX, vectorY)
                            vectorX = ka_math.crossProduct(vectorZ, vectorY)

                            vectorX = ka_math.multiply(vectorX, scale)
                            vectorY = ka_math.multiply(vectorY, scale)
                            vectorZ = ka_math.multiply(vectorZ, scale)

                            targetMatrix = (vectorX[0],vectorX[1],vectorX[2],0, vectorY[0],vectorY[1],vectorY[2],0, vectorZ[0],vectorZ[1],vectorZ[2],0, targetPos[0], targetPos[1], targetPos[2], 1)
                            pymel.xform(targetIcon, matrix=targetMatrix, worldSpace=True)


    def deleteTargetIcons(self):
        deleteMeObjects = pymel.ls('DELETE_ME__*')
        deleteList = []

        for each in deleteMeObjects:
            if pymel.attributeQuery('createColoredVertexSpheres_tempType', node=each, exists=True):
                deleteList.append(each)

        if deleteList:
            pymel.delete(deleteList)

        self.targetIconsA = []
        self.targetIconsB = []


    def _orderConnectedVertsClockwise(self, shapeID, pointID):
        orderedVerts = []
        connectedPoints = self.strandInfoDict[shapeID]['componentInfoDict']['connectedPoints'][pointID]
        unOrderedVerts = list(connectedPoints)

        # find point that is fathest to camera left
        leftMostPoint = connectedPoints[0]
        for connectedPoint in connectedPoints[1:]:
            leftMostX = self.strandInfoDict[shapeID]['componentInfoDict']['positionDict']['camera'][leftMostPoint][0]
            connectedPointX = self.strandInfoDict[shapeID]['componentInfoDict']['positionDict']['camera'][connectedPointID][0]

            if leftMostX > connectedPointX:
                leftMostPoint = connectedPointID

        orderedVerts.append(leftMostPoint)
        unOrderedVerts.remove(leftMostPoint)

        count = 0
        maxCount = 999
        direction = 1
        while len(orderedVerts) != len(connectedPoints):
            count += 1

            if direction == 1:
                #faceConnectedPoints = self._getPointsConnectedByFace(shapeID, orderedVerts[-1], pointInclusionList=connectedPoints, pointExclusionList=orderedVerts)
                faceConnectedPoints = self.strandInfoDict[shapeID]['componentInfoDict']

                if not faceConnectedPoints:
                    direction = -1

                else:
                    nextPoint = None
                    for faceConnectedPoint in faceConnectedPoints:
                        if faceConnectedPoint != pointID:
                            if not nextPoint:
                                nextPoint = faceConnectedPoint

                            else:
                                if self._getCameraSpacePosition(nextPoint)[1] < self._getCameraSpacePosition(faceConnectedPoint)[1]:
                                #if self.pnt_cameraSpacePostionDict[nextPoint][1] < self.pnt_cameraSpacePostionDict[faceConnectedPoint][1]:
                                    nextPoint = faceConnectedPoint

                    orderedVerts.append(nextPoint)
                    unOrderedVerts.remove(nextPoint)


            else:   # direction is reversed
                faceConnectedPoints = self._getPointsConnectedByFace(orderedVerts[0], pointInclusionList=connectedPoints, pointExclusionList=orderedVerts)

                if not faceConnectedPoints: # well, just grab a random left over then :S
                    nextPoint = unOrderedVerts.pop()
                    orderedVerts.append(nextPoint)

                else:
                    nextPoint = None
                    for faceConnectedPoint in faceConnectedPoints:
                        if faceConnectedPoint != pointID:
                            nextPoint = faceConnectedPoint
                            break

                    orderedVerts.append(nextPoint)
                    unOrderedVerts.remove(nextPoint)

        return orderedVerts


## MAIN FUNCTIONS ----------------------------------------------------------------------------------------------------------------
weightBlenderInfo = None

def startParallelBlend():
    global weightBlenderInfo

    weightBlenderInfo = WeightBlenderInfo()
    try:
        weightBlenderInfo.startParallelBlend()
    except:
        ka_python.printError()
        finish()


def startStrandBlend():
    global weightBlenderInfo

    weightBlenderInfo = WeightBlenderInfo()
    try:
        weightBlenderInfo.startStrandBlend()
    except:
        ka_python.printError()
        finish()


def change(*args, **kwargs):
    global weightBlenderInfo

    try:
        if weightBlenderInfo:
            weightBlenderInfo.blend(*args, **kwargs)
        else:
            print 'weightBlender does not exist'

    except:
        ka_python.printError()
        finish()


def finish():
    global weightBlenderInfo

    if weightBlenderInfo:
        weightBlenderInfo.deleteTargetIcons()
        cmds.select(weightBlenderInfo.selection)
        weightBlenderInfo = None


def next():
    global weightBlenderInfo
    weightBlenderInfo.nextSequence()


def previous():
    global weightBlenderInfo
    weightBlenderInfo.previousSequence()


def blendWithBothNeighbors():
    global weightBlenderInfo
    selection = pymel.ls(selection=True)

    weightBlenderInfo = WeightBlenderInfo()
    weightBlenderInfo.start(createTargetIcons=False)

    weightBlenderInfo.averageWithBothNeighbors()


    pymel.select(selection)


# MISC
def getCurrentPannel():
    try:
        panel = pymel.getPanel(underPointer=True)
        panel = panel.split('|')[-1]
        return panel

    except:
        ka_python.printError()
        print '## Failed to find current panel, make sure you have a view port with focus'