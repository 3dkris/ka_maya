#====================================================================================
#====================================================================================
#
# ka_utils_skinCluster
#
# DESCRIPTION:
#   library of commands for querying skinClusters
#
# DEPENDENCEYS:
#   ka_menus
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
import maya.mel as mel
import pymel.core as pymel
import maya.OpenMaya as OpenMaya

import ka_maya.ka_python as ka_python
import ka_maya.ka_pymel as ka_pymel

import ka_maya.ka_rigQuery as ka_rigQuery
import ka_maya.ka_naming as ka_naming



def findRelatedSkinCluster(*args, **kwArgs):
    '''return the skinCluster for the input, which will be a user selection

    kwArgs:
        silent - True/False if True, then no error will occure if no skinCluster is found
    '''

    silent = kwArgs.get('silent', True)

    log = 0 #log debug messages or not

    if args:
        node = ka_pymel.getAsPyNodes(args[0])

    else:
        if 'input' in kwArgs:
            node = ka_pymel.getAsPyNodes(kwArgs['input'])
        else: #then use selection
            node = pymel.ls(selection=True)[0]


    node = node.node()
    #components = input.split('.')
    transform = None
    skinCluster = None

    if log:print "input", input


    #if len(components) > 1:
        #input = components[0]

    if 'transform' in node.nodeType(inherited=True):
        transform = node

    #elif pymel.objectType(input) == 'joint':
        #transform = input

    if pymel.objectType(node) == 'skinCluster':
        return node

    elif 'deformableShape' in pymel.nodeType(node, inherited=True):
        transform = pymel.listRelatives(node, parent=True)


    if not skinCluster and transform:
        shapes = pymel.listRelatives(transform, shapes=True)
        if shapes:
            if 'deformableShape' in pymel.nodeType(shapes[0], inherited=True):
                history = pymel.listHistory(transform)

                if history:
                    for each in history:
                        if pymel.nodeType(each) == 'skinCluster':
                            shapes = pymel.listRelatives(transform, noIntermediate=True, shapes=True)
                            if shapes:
                                geos = pymel.skinCluster(each, query=True, geometry=True)
                                for geo in geos:
                                    if geo in shapes:
                                        skinCluster = each
                                        break
                                        break

                if not skinCluster:
                    if history:
                        for each in history:
                            if pymel.nodeType(each) == 'skinCluster':
                                skinCluster = each
                                break


    #if not skinCluster:
        #if not silent:
            ##raise NameError('-- A skinCluster could not be found for: '+input)
            #print '-- A skinCluster could not be found for: ', input

    return skinCluster



def getInfluences(skinCluster=None):
    '''return the influences attached to the skinCluster'''

    ka_pymel.getAsPyNodes(skinCluster)

    if skinCluster == None:    # then use selection
        selection = pymel.ls(selection=True)
        if selection:
            skinCluster = findRelatedSkinCluster(selection[0])

    elif not isinstance(skinCluster, pymel.nt.SkinCluster):
        skinCluster = findRelatedSkinCluster(skinCluster)

    if skinCluster:
        influences = pymel.listConnections(skinCluster.matrix, destination=False, source=True, skipConversionNodes=True)

    return influences


def removeUnusedForSkin(skinCluster, **kwArgs):
    verbose = kwArgs.get('verbose', False)

    influences = getInfluences(skinCluster)
    weightedInfluences = pymel.skinCluster(skinCluster, query=True, weightedInfluence=True)
    unweightedInfluences = []
    nodeState = skinCluster.nodeState.get()

    skinCluster.nodeState.set(1)
    for influence in influences:
        if influence not in weightedInfluences:
            #unweightedInfluences.append(influence)

            pymel.skinCluster(skinCluster, edit=True, removeInfluence=influence)

    if verbose:
        print 'removed %s influences from skinCluster: %s' % (str(len(unweightedInfluences)), skinCluster.name())

def removeUnusedInfluences(**kwArgs):
    kwArgs['verbose'] = True
    selection = pymel.ls(selection=True)

    for geo in selection:
        skinCluster = findRelatedSkinCluster(geo, silent=True)
        if skinCluster:
            removeUnusedForSkin(skinCluster, **kwArgs)


def setSetJointLabelFromName():
    selection = pymel.ls(selection=True)

    for sel in selection:
        _setSetJointLabelFromName(sel)

def setSetJointLabelFromNameOnAll():

    #t0 = time.clock()
    skinClusters = pymel.ls(type='skinCluster')
    #print 'A took: %s sec' % str(time.clock() - t0)

    #t0 = time.clock()
    jointInfluences = {}
    #print 'getting influences'
    #tA = 0.0
    #tB = 0.0
    for skinCluster in skinClusters:
        #t1 = time.clock()
        influences = getInfluences(skinCluster)
        #if tA > 0.03:
            #OOOOOOO = "skinCluster"; print '%s: ' % OOOOOOO, eval(OOOOOOO), ' ', type(eval(OOOOOOO))
            #OOOOOOO = "round((time.clock() - t1), 4)"; print '%s: ' % OOOOOOO, eval(OOOOOOO), ' ', type(eval(OOOOOOO))
            #print '---------------'
        #tA += time.clock() - t1


        #t2 = time.clock()
        for influence in influences:
            hash_ = influence.__hash__()
            if hash_ not in jointInfluences:
                jointInfluences[hash_] = influence


        #tB += time.clock() - t2


    #OOOOOOO = "tA"; print '%s: ' % OOOOOOO, eval(OOOOOOO), ' ', type(eval(OOOOOOO))
    #OOOOOOO = "tB"; print '%s: ' % OOOOOOO, eval(OOOOOOO), ' ', type(eval(OOOOOOO))
    #print 'B took: %s sec' % str(time.clock() - t0)

    #t0 = time.clock()
    for jointInfluence in jointInfluences:
        jointInfluence = jointInfluences[jointInfluence]
        _setSetJointLabelFromName(jointInfluence)
    #print 'C took: %s sec' % str(time.clock() - t0)

def _setSetJointLabelFromName(node):

    if pymel.nodeType(node) == 'joint':
        #baseName = None
        #side = 0
        #left = 1
        #right = 2
        #currentName = node.nodeName(stripNamespace=True)

        #if currentName[0:2] == 'r_':
            #side = right
            #baseName = currentName[2:]
        #elif currentName[0:2] == 'l_':
            #side = left
            #baseName = currentName[2:]
        #elif currentName[0:2] == 'R_':
            #side = right
            #baseName = currentName[2:]
        #elif currentName[0:2] == 'L_':
            #side = left
            #baseName = currentName[2:]

        #elif '_r_' in currentName:
            #side = right
            #baseName = currentName.replace('_r_', '', 1)

        #elif '_l_' in currentName:
            #side = left
            #baseName = currentName.replace('_l_', '', 1)

        #elif '_R_' in currentName:
            #side = right
            #baseName = currentName.replace('_R_', '', 1)

        #elif '_L_' in currentName:
            #side = left
            #baseName = currentName.replace('_L_', '', 1)

        #else:
            #baseName = currentName

        #node.attr('type').set(18)
        #node.side.set(side)
        #node.otherType.set(baseName, type='string')
        #sideInfo = ka_rigQuery._getSideInfo(node.nodeName())
        sideInfo = ka_naming._getSideInfo(node.nodeName())


        if not sideInfo:
            node.side.set(0)
            node.attr('type').set(18)
            node.otherType.set(node.nodeName(), type='string')

        else:
            if sideInfo['side'] == 'l':
                node.side.set(1)
            elif sideInfo['side'] == 'r':
                node.side.set(2)
            else:
                node.side.set(0)

            nameWithoutSide = node.nodeName().replace(sideInfo['sideString'], '', 1)

            node.attr('type').set(18)
            node.otherType.set(nameWithoutSide, type='string')


