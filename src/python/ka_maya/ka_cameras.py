#====================================================================================
#====================================================================================
#
# ka_cameras
#
# DESCRIPTION:
#   functions related to cameras
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

import pymel.core as pymel
import maya.cmds as cmds
import maya.mel as mel

import ka_transforms as ka_transforms


def getCurrentCamera():
    """Returns the current cammera with focus"""
    panelUnderPointer = pymel.getPanel( underPointer=True )
    camera = None
    if panelUnderPointer:
        if 'modelPanel' in panelUnderPointer:
            currentPanel = pymel.getPanel(withFocus=True)
            currentPanel = currentPanel.split('|')[-1]
            camera = pymel.modelPanel(currentPanel, query=True, camera=True)

            return pymel.ls(camera)[0]

    return pymel.ls('persp')[0]

def getCameraMatrix(camera=None):
    if camera == None:
        camera = getCurrentCamera()

    cameraMatrix = ka_transforms.getAsMatrix(camera)
    return cameraMatrix


def getInCameraSpace(inputA, cameraMatrix=None):
    if cameraMatrix == None:
        cameraMatrix = getCameraMatrix()

    return ka_transforms.getInForienSpace_point(inputA, cameraMatrix)
