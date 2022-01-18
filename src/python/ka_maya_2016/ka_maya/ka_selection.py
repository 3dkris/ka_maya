 #====================================================================================
#====================================================================================
#
# ka_menu_weightLib
#
# DESCRIPTION:
#   functions for manipulation and query of maya selection
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
import time

import pymel.core as pymel
import maya.cmds as cmds
import maya.mel as mel

import ka_maya.ka_clipBoard as ka_clipBoard
import ka_maya.ka_pymel as ka_pymel
#import ka_maya.ka_weightBlender as ka_weightBlender
import ka_maya.ka_context as ka_context
import ka_maya.ka_geometry as ka_geometry


def storeSelection():
    selection = cmds.ls(selection=True)
    ka_clipBoard.add('storedSelection', selection)

def getStoredSelection():
    selection = ka_clipBoard.get('storedSelection', [])
    selection = ka_pymel.getAsPyNodes(selection)
    return selection


def invertSelectionOrder(selection=None):
    if not selection:
        selection = pymel.ls(selection=True)

    selection.reverse()
    pymel.select(selection)

def getSelectedShape():
    selection = pymel.ls(selection=True, objectsOnly=True)
    for node in selection:
        if ka_pymel.isPyTransform(node):
            shape = node.getShape()
            if shape:
                return shape

        elif ka_pymel.isPyShape(node):
            return node



def islandSelectComponents():
    a = pymel.ls(selection=True, flatten=True)[0]
    island = []
    newFaces = pymel.ls(a.connectedVertices(), flatten=True)
    i = 0
    while i < 999 and newFaces:
        i += 1

        newFace = newFaces.pop(0)
        connectedFaces = pymel.ls(newFace.connectedVertices(), flatten=True)
        for connectedFace in iter(connectedFaces):
            if connectedFace not in island:
                island.append(connectedFace)
                newFaces.append(connectedFace)

    pymel.select(island)




def pickWalk(direction, additive=False):

    if not cmds.ls(selection=True, dagObjects=True):
        strandInfoDict = ka_geometry.getStrandInfoDict(checkSelectionMatches=True)

        # are we additively selecting strands?
        if additive:    # ------------------------------------------------------------------------------------------
            ka_geometry.strandWalk(direction, strandInfoDict=strandInfoDict, additive=True)

        else:
            ka_geometry.strandWalk(direction, strandInfoDict=strandInfoDict)

    # Dag pick walk
    else:

        if additive:
            selection.extend(pymel.pickWalk( direction=direction ))
            cmds.select(selection)

        else:
            pymel.pickWalk( direction=direction )





