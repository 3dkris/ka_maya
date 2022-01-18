#====================================================================================
#====================================================================================
#
# ka_maya.ka_deformerImportExport.deformerLib.deformer_skinCluster
#
# DESCRIPTION:
#   a general type for deformer import export
#
# DEPENDENCEYS:
#   ka_maya.ka_deformerImportExport
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
import ast

import pymel.core as pymel
import maya.mel as mel
import maya.cmds as cmds

from . import deformer_base

class SkinCluster(deformer_base.Deformer):
    userPaintedAttributes = ('weightList', 'blendWeights')

    def __init__(self, **kwargs):
        super(SkinCluster, self).__init__(**kwargs)

        self.influences = kwargs.get('influences', None)
        self.optimizedInfluences = kwargs.get('influences', None)


        # get info
        if self.deformer:
            self.influences = self.getSkinClusterInfluences()



    def getKwargs(self):
        kwargs = super(SkinCluster, self).getKwargs()
        kwargs['influences'] = self.influences
        kwargs['optimizedInfluences'] = self.optimizedInfluences
        kwargs['deformedComponents'] = self.deformedComponents
        kwargs['deformedNodes'] = self.deformedNodes
        kwargs['nodeType'] = self.nodeType

        return kwargs

    def export(self, exportDir):
        self.exportSkinWeights_asFile(exportDir) # must happen before super so it can populate self.optimizedInfluences
        super(SkinCluster, self).export(exportDir)


    def import_(self, deformerPath, optimized=False):
        super(SkinCluster, self).import_(deformerPath, optimized=optimized)

        initialSelection = cmds.ls(selection=True)

        # choose set of influences
        if optimized:
            influences = self.optimizedinfluences
        else:
            influences = self.influences

        for deformedNode in self.deformedNodes:
            pymel.select(clear=True)

            # Are there missing influences?
            try:
                pymel.select(influences)
            except:
                missingInfluencesString = ''
                missingInfluencesCount = 0
                duplicateNamesString = ''
                duplicateNamesCount = 0

                for each in influences:
                    if not cmds.objExists(each):
                        missingInfluencesString += '        %s\n' % each
                        missingInfluencesCount += 1

                    elif len(pymel.ls(each)) > 1:
                        for each in pymel.ls(each):
                            duplicateNamesString += '        %s\n' % str(each)
                            duplicateNamesCount += 1

                if missingInfluencesCount:
                    pymel.error('\n    SKINCLUSTER FAILED TO LOAD on %s because %s influences DO NOT EXIST in the scene:\n' % (deformedObject, str(missingInfluencesCount)) + missingInfluencesString)

                if duplicateNamesCount:
                    pymel.error('\n    SKINCLUSTER FAILED TO LOAD on %s because %s there are DUPLICATE NAMES for the following influences:\n' % (deformedObject, str(duplicateNamesCount)) + duplicateNamesString)

            # create new skin cluster
            if not self.deformer:
                pymel.select(self.deformedComponents, add=True)
                self.deformer = pymel.skinCluster(toSelectedBones=True, removeUnusedInfluence=False, normalizeWeights=0)
                self.deformer.rename(self.deformerName)

            # clear data from existing skinCluster
            else:
                #bindPreMatrixInputs = NOne
                for i in self.deformer.matrix.get(multiIndices=True):
                    for arrayAttr in ('matrix', 'influenceColor', 'lockWeights', 'weightList',):
                        pymel.removeMultiInstance(self.deformer.attr(arrayAttr)[i], b=True)

                    try:
                        pymel.removeMultiInstance(self.deformer.bindPreMatrix[i], b=False)
                    except:
                        pass

                for i, joint in enumerate(influences):
                    joint.worldMatrix[0] >> self.deformer.matrix[i]
                    joint.objectColorRGB >> self.deformer.influenceColor[i]
                    joint.lockInfluenceWeights >> self.deformer.lockWeights[i]

                    try:
                        self.deformer.bindPreMatrix[i].set(joint.worldInverseMatrix.get())

                    except:
                        pass


            self.deformer.normalizeWeights.set(0)
            pymel.skinPercent(self.deformer, self.deformedComponents, nrm=False, prw=100)

            if optimized:
                weightsFile = os.path.join(deformerPath, 'optimizedSkinWeights.txt')
            else:
                weightsFile = os.path.join(deformerPath, 'skinWeights.txt')

            self.importSkinWeights_fromFile(weightsFile)


            self.deformer.normalizeWeights.set(1)

        pymel.select(initialSelection)


    def getSkinClusterInfluences(self):
        influences = pymel.listConnections(self.deformer.matrix, skipConversionNodes=True, d=False, s=True )
        if not influences:
            pymel.error('skin Cluster: %s has no influences!'% self.deformerName)

        return influences

    def importSkinWeights_fromFile(self, weightFile):
        with open(weightFile, 'r') as f:

        #f = open(weightsFile, 'r')
        #deformerNodeName = deformerNode.nodeName()


            ia = 0
            for line in f:
                strIA = str(ia)
                weightSubDict = ast.literal_eval(line)
                for ib in weightSubDict:
                    strIB = str(ib)
                    cmds.setAttr('%s.wl[%s].w[%s]' % (self.deformerName, strIA, strIB), weightSubDict[ib])
                ia += 1

            #f.close()

    def exportSkinWeights_asFile(self, exportDir, createOptimizedWeightsFile=True):
        """Writes a formated weight dict to a file, in human readable and code parseable format

        args:
            fileName - the file to write to
        kwArgs:
            weightsDict - a dictionary of weights, usually returned by getSkinWeights_asDict function
        }
        """

        # write regular weight file
        filePath = os.path.join(exportDir, 'skinWeights.txt')
        try: os.remove(filePath)
        except: pass
        with open(filePath, 'w+') as deformerFile:

            deformerName = str(self.deformer)
            pointRange = cmds.getAttr('%s.wl' % (deformerName, ), multiIndices=True)[-1]
            strPointRange = str(pointRange)
            cmds.progressWindow(title='Saving DEFORMERS', min=0, max=pointRange, progress=0, status='saving...: ', isInterruptable=False )


            # determine if any of the array items are not in use (usually because that influence has been removed)
            # we will used the realIndexDict to later when we want to write weights to the index it would have been
            realIndexDict = {}
            usedInfluenceIndices = pymel.getAttr(self.deformer.matrix, multiIndices=True)

            for count, plugIndex in enumerate(usedInfluenceIndices):
                realIndexDict[count] = str(plugIndex) #string because this be used directly in a file write


            unusedInfluences = realIndexDict.copy()

            toggle = 0
            for ia in range(pointRange+1):
                strIA = str(ia)

                #save time by only updating progress window every other iteration
                toggle = 1 - toggle
                if toggle:
                    cmds.progressWindow(edit=True, progress=ia,)


                pointWeightsList = []
                usedIndices = cmds.getAttr('%s.wl[%s].weights' % (deformerName, strIA,), multiIndices=True)

                if usedIndices:
                    for ib in usedIndices:
                        strIB = str(ib)

                        weight = cmds.getAttr('%s.wl[%s].weights[%s]' % (deformerName, strIA, strIB))

                        if weight:
                            #pretty format
                            if ib in realIndexDict:
                                pointWeightsList.append('%s:%s, ' % (realIndexDict[ib], str(weight)))

                            if ib in unusedInfluences:
                                unusedInfluences.pop(ib)

                deformerFile.write('{%s}\n' % ''.join(pointWeightsList))

            deformerFile.close()
            cmds.progressWindow(endProgress=1)



        # Create optimised weights file ----------------------------------------
        if createOptimizedWeightsFile:
            optimizedFilePath = os.path.join(exportDir, 'optimizedSkinWeights.txt')
            with open(optimizedFilePath, 'w+') as optimizedDeformerFile:

                # convert to new dict where the keys are the index they where output as
                newUnusedInfluences = {}
                for oldIndex, realIndex in unusedInfluences.items():
                    newUnusedInfluences[int(realIndex)] = True

                # remove unused influences from optimized list of influences
                optimizedinfluences = []
                for i, influence in enumerate(self.influences):
                    if i not in newUnusedInfluences:
                        optimizedinfluences.append(influence)

                self.optimizedInfluences = optimizedinfluences


                # Make a new dictionary to make the indecies to their new index if the
                # influences are removed
                newRealIndexDict = {}
                newRealIndexList = []
                for oldIndex, realIndex in realIndexDict.items():
                    realIndex = int(realIndex)
                    if realIndex not in newUnusedInfluences:
                        newRealIndexList.append(realIndex)

                for i, item in enumerate(newRealIndexList):
                    newRealIndexDict[item] = str(i)


                # write the new optimized file
                #deformerFile = open(filePath, 'r')
                with open(filePath, 'r') as deformerFile:

                    #optimizedDeformerFile = open(optimizedFilePath, 'w')

                    # prune small weights, and redistibute the weight proportionaly
                    # to the remaining weights. If their is a remainder, assign that
                    # to the largest weight. ALSO assign the proper new index
                    # for weights effected by the removal of unused influences
                    pruneBelow = 0.001
                    for line in deformerFile:
                        weightsDict = eval(line)

                        # prune small weights
                        prunedWeightsPool = 0.0
                        activeWeightsPool = 0.0
                        largestInfluenceIndex = None
                        for i in iter(weightsDict.copy()):
                            weight = weightsDict[i]

                            if weight < pruneBelow:
                                prunedWeightsPool += weight
                                weightsDict.pop(i)
                            else:
                                activeWeightsPool += weight

                                #is the weight the largest?
                                if largestInfluenceIndex == None:
                                    largestInfluenceIndex = i
                                else:
                                    if weight > weightsDict[i]:
                                        largestInfluenceIndex = i

                        # redistribute pruned weights and normilize (in case it was exported using post normalisation)
                        totalWeightsPool = prunedWeightsPool + activeWeightsPool
                        newTotalWeightsPool = 0.0
                        if prunedWeightsPool:
                            for i in iter(weightsDict.copy()):
                                weight = weightsDict[i]

                                ratioOfTotal = weight / totalWeightsPool
                                weight += (prunedWeightsPool*ratioOfTotal)
                                normalizedWeight = weight / totalWeightsPool

                                newTotalWeightsPool += normalizedWeight
                                weightsDict[i] = normalizedWeight

                            remainder = 1-newTotalWeightsPool
                            weightsDict[largestInfluenceIndex] += remainder


                        # write to file
                        weightsStringList = []
                        for i in sorted(weightsDict):
                            weightsStringList.append('%s:%s, ' % (newRealIndexDict[i], str(weightsDict[i])))

                        lineToWrite = '{%s}\n' % ''.join(weightsStringList)
                        optimizedDeformerFile.write('{%s}\n' % ''.join(weightsStringList))

