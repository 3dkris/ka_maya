
#====================================================================================
#====================================================================================
#
# ka_rigAerobics
#
# DESCRIPTION:
#   Library of maps and animation to apply to different rigs
#
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
import os

import pymel.core as pymel
import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMayaUI as OpenMayaUI

import ka_maya.ka_pymel as ka_pymel                         #;reload(ka_pymel)
import ka_maya.ka_python as ka_python                       #;reload(ka_python)
import ka_maya.ka_animation as ka_animation                 #;reload(ka_animation)
import ka_maya.ka_naming as ka_naming                       #;reload(ka_naming)
import ka_maya.ka_transforms as ka_transforms               #;reload(ka_transforms)

KEY_SPACING = 20


def getAsPyNode(inputA, findOpposite=False):
    if isinstance(inputA, dict):
        newDict = {}
        for key in inputA:
            value = inputA[key]
            value = getAsPyNode(value, findOpposite=findOpposite)

        return newDict

    elif isinstance(inputA, list):
        newList = []
        for value in inputA:
            newList.append(getAsPyNode(value, findOpposite=findOpposite))

        return newList

    else:
        if findOpposite:
            inputA = ka_naming.getOppositeFromName(inputA)

        node = pymel.ls(inputA)
        if node:
            if len(node) == 1:
                node = node[0]
                return node

            else:
                pymel.error('more than 1 node matches name: '+value)

def importMapToLocals(rigMap, localsDict):
    """adds each item from the map to a local variable, who's variable
    name is the key, and who's value is a pymel object for that item"""

    for key in rigMap:
        #try:
        value = getAsPyNode(rigMap[key])
        localsDict[key] = value

        oppositeKey = ka_naming.getOppositeFromName(key)
        if oppositeKey:
            oppositeValue = getAsPyNode(rigMap[key], findOpposite=True)
            if oppositeValue:
                localsDict[oppositeKey] = oppositeValue
    OOOOOOO = 'localsDict';  print '%s = %s %s'%(str(OOOOOOO),str(eval(OOOOOOO)),str(type(eval(OOOOOOO))))
        #except:
            #printError()

    #return localsDict



def getAllControls_fromRigDict(rigDict):
    allControlls = ka_python.getItems(rigDict)
    return allControlls



RNK_BIPIED_MAP = {

# CENTER ------------------------------------------------------------------------
'hip'         : 'c_hips_ctl',
'pelvis'      : 'c_pelvis_ctl',
'spines'      : ['c_absfwdB_ctl', 'c_chestfwd_ctl', 'c_spinefwdE_ctl'],
'necks'       : ['c_neckA_ctl', 'c_neckB_ctl'],
'head'        : 'c_head_ctl',


# LEFT ------------------------------------------------------------------------
'l_clavical'    :'l_shoulderA_ctl',
'l_arm'         :'l_uparm_ctl',
'l_elbow'       :'l_forearm_ctl',
'l_wrist'       :'fk_l_hand_ctl',
'l_thumb'       :['l_handthumbA_ctl', 'l_handthumbB_ctl', 'l_handthumbC_ctl'],
'l_fingers'     :[['l_handindexA_ctl', 'l_handindexB_ctl', 'l_handindexC_ctl'],
                  ['l_handmiddleA_ctl', 'l_handmiddleB_ctl', 'l_handmiddleC_ctl'],
                  ['l_handringA_ctl', 'l_handringB_ctl', 'l_handringC_ctl'],
                  ['l_handpinkyA_ctl', 'l_handpinkyB_ctl', 'l_handpinkyC_ctl'],
                 ],
'l_metacarpals' :['l_inhandringA_ctl', 'l_inhandpinkyA_ctl'],

'l_leg'         : 'l_uplegA_ctl',
'l_knee'        : 'l_legA_ctl',
'l_ankle'       : 'l_footA_ctl',
'l_footBall'    : 'l_fulltoesA_ctl',


# RIGHT ------------------------------------------------------------------------
'r_clavical'    :'r_shoulderA_ctl',
'r_arm'         :'r_uparm_ctl',
'r_elbow'       :'r_forearm_ctl',
'r_wrist'       :'fk_r_hand_ctl',
'r_thumb'       :['r_handthumbA_ctl', 'r_handthumbB_ctl', 'r_handthumbC_ctl'],
'r_fingers'     :[['r_handindexA_ctl', 'r_handindexB_ctl', 'r_handindexC_ctl'],
                  ['r_handmiddleA_ctl', 'r_handmiddleB_ctl', 'r_handmiddleC_ctl'],
                  ['r_handringA_ctl', 'r_handringB_ctl', 'r_handringC_ctl'],
                  ['r_handpinkyA_ctl', 'r_handpinkyB_ctl', 'r_handpinkyC_ctl'],
                 ],
'r_metacarpals' :['r_inhandringA_ctl', 'r_inhandpinkyA_ctl'],

'r_leg'         : 'r_uplegA_ctl',
'r_knee'        : 'r_legA_ctl',
'r_ankle'       : 'r_footA_ctl',
'r_footBall'    : 'r_fulltoesA_ctl',

}



NITROGEN_BIPIED_MAP = {

# CENTER ------------------------------------------------------------------------
'cog'         : 'CNT_BODYROOT_01_C',
'pelvis'      : ['CNT_BODY01_REVERSE_03_C', 'CNT_BODY01_REVERSE_02_C', 'CNT_BODY01_REVERSE_01_C'],
'spines'      : ['CNT_BODY01_DIRECT_04_C', 'CNT_BODY01_DIRECT_05_C',],
'necks'       : ['CNT_BODY01_DIRECT_05_C'],
'head'        : 'CNT_BODY01_DIRECT_06_C',


# LEFT ------------------------------------------------------------------------
'l_clavical'    :'',
'l_arm'         :'CNT_FK_SHOULDER_01_L',
'l_elbow'       :'CNT_FK_ELBOW_01_L',
'l_wrist'       :'CNT_FK_WRIST_01_L',
'l_thumb'       :['CNT_FKTHUMB01_01_L', 'CNT_FKTHUMB01_02_L', 'CNT_FKTHUMB01_03_L', 'CNT_FKTHUMB01_04_L',],
'l_fingers'     :[['CNT_FKINDEX01_02_L', 'CNT_FKINDEX01_03_L', 'CNT_FKINDEX01_04_L',],
                  ['CNT_FKMIDDLE01_02_L', 'CNT_FKMIDDLE01_03_L', 'CNT_FKMIDDLE01_04_L',],
                  ['CNT_FKRING01_02_L', 'CNT_FKRING01_03_L', 'CNT_FKRING01_04_L',],
                 ],
'l_metacarpals' :['CNT_FKINDEX01_01_L', 'CNT_FKRING01_01_L'],

'l_leg'         : 'CNT_FK_LEG_01_L',
'l_knee'        : 'CNT_FK_KNEE_01_L',
'l_ankle'       : 'CNT_FK_ANKLE_01_L',
'l_footBall'    : 'CNT_FK_FOOT_03_L',


# RIGHT ------------------------------------------------------------------------
'r_clavical'    :'',
'r_arm'         :'CNT_FK_SHOULDER_01_R',
'r_elbow'       :'CNT_FK_ELBOW_01_R',
'r_wrist'       :'CNT_FK_WRIST_01_R',
'r_thumb'       :['CNT_FKTHUMB01_01_R', 'CNT_FKTHUMB01_02_R', 'CNT_FKTHUMB01_03_R', 'CNT_FKTHUMB01_04_R',],
'r_fingers'     :[['CNT_FKINDEX01_02_R', 'CNT_FKINDEX01_03_R', 'CNT_FKINDEX01_04_R',],
                  ['CNT_FKMIDDLE01_02_R', 'CNT_FKMIDDLE01_03_R', 'CNT_FKMIDDLE01_04_R',],
                  ['CNT_FKRING01_02_R', 'CNT_FKRING01_03_R', 'CNT_FKRING01_04_R',],
                 ],
'r_metacarpals' :['CNT_FKINDEX01_01_R', 'CNT_FKRING01_01_R'],

'r_leg'         : 'CNT_FK_LEG_01_R',
'r_knee'        : 'CNT_FK_KNEE_01_R',
'r_ankle'       : 'CNT_FK_ANKLE_01_R',
'r_footBall'    : 'CNT_FK_FOOT_03_R',

}

def tryToXform(*args, **kwargs):

    try:
        if args[0] != None:
            if 'mirrorTransform' in kwargs:
                mirrorTransform = kwargs.pop('mirrorTransform')
            else:
                mirrorTransform = None

            pymel.xform(*args, **kwargs)

            if mirrorTransform:
                ka_transforms.mirrorTransform(mirrorTransform, targetTransform=args[0])

    except:
        ka_python.printError()


def rnkBipiedAnimation():
    global RNK_BIPIED_MAP
    rigDict = NITROGEN_BIPIED_MAP
    rigDict = ka_pymel.getAsPyNodes(rigDict)
    OOOOOOO = 'rigDict'; print '%s: ' % OOOOOOO, eval(OOOOOOO), ' ', type(eval(OOOOOOO))
    # CENTER -----------------------------------------
    hip = rigDict.get('hip', None)
    pelvis = rigDict.get('pelvis', None)
    spines = rigDict.get('spines', None)
    necks = rigDict.get('necks', None)
    head = rigDict.get('head', None)

    # LEFT -----------------------------------------
    l_leg = rigDict.get('l_leg', None)
    l_knee = rigDict.get('l_knee', None)
    l_ankle = rigDict.get('l_ankle', None)
    l_footBall = rigDict.get('l_footBall', None)

    l_clavical = rigDict.get('l_clavical', None)
    l_arm = rigDict.get('l_arm', None)
    l_elbow = rigDict.get('l_elbow', None)
    l_wrist = rigDict.get('l_wrist', None)
    l_thumb = rigDict.get('l_thumb', None)
    l_fingers = rigDict.get('l_fingers', None)
    l_metacarpals = rigDict.get('l_metacarpals', None)

    # RIGHT -----------------------------------------
    r_leg = rigDict.get('r_leg', None)
    r_knee = rigDict.get('r_knee', None)
    r_ankle = rigDict.get('r_ankle', None)
    r_footBall = rigDict.get('r_footBall', None)

    r_clavical = rigDict.get('r_clavical', None)
    r_arm = rigDict.get('r_arm', None)
    r_elbow = rigDict.get('r_elbow', None)
    r_wrist = rigDict.get('r_wrist', None)
    r_thumb = rigDict.get('r_thumb', None)
    r_fingers = rigDict.get('r_fingers', None)
    r_metacarpals = rigDict.get('r_metacarpals', None)

    thumbCurlAxis = 'ry'
    flatThumbRotation = [0.0, -45.0, 0.0]

    pymel.currentTime( 1 )
    allControls = getAllControls_fromRigDict(rigDict)
    #for key in allControls:
        #if allControls[key] == None:
            #pymel.warning('%s has a value of None' % key)

    ka_animation.storeAllControls(allControls)
    ka_animation.deleteAnimationOnAllControls()

    # set A Pose ----------------------------------------------------------------
    ka_animation.keyAllControls()
    pymel.currentTime( 0 ) # count from zero, but first key is on frame 1

    pymel.select(clear=True)
    # set T Pose ----------------------------------------------------------------
    ka_animation.advanceNFrames(KEY_SPACING*2)

    tryToXform(l_leg, rotation=[0, 0, -90], worldSpace=True)
    ka_transforms.mirrorTransform(r_leg, targetTransform=l_leg)

    tryToXform(l_knee, rotation=[0, 0, -90], worldSpace=True)
    ka_transforms.mirrorTransform(r_knee, targetTransform=l_knee)

    tryToXform(l_ankle, rotation=[0, 0, -90], worldSpace=True)
    ka_transforms.mirrorTransform(r_ankle, targetTransform=l_ankle)

    tryToXform(l_footBall, rotation=[90, 0, -90], worldSpace=True)
    ka_transforms.mirrorTransform(r_footBall, targetTransform=l_footBall)

    tryToXform(l_arm, rotation=[-180, 0, 0], worldSpace=True)
    ka_transforms.mirrorTransform(r_arm, targetTransform=l_arm)

    tryToXform(l_elbow, rotation=[-180, 0, 0], worldSpace=True)
    ka_transforms.mirrorTransform(r_elbow, targetTransform=l_elbow)

    tryToXform(l_wrist, rotation=[-180, 0, 0], worldSpace=True)
    ka_transforms.mirrorTransform(r_wrist, targetTransform=l_wrist)


    for iA, finger in enumerate(l_fingers):
        for iB, fingerJoint in enumerate(finger):
            tryToXform(l_fingers[iA][iB], rotation=[-90, 0, 0], worldSpace=True)
            ka_transforms.mirrorTransform(r_fingers[iA][iB], targetTransform=fingerJoint)


    for iA, thumbJoint in enumerate(l_thumb):
        #worldRot = pymel.xform(l_thumb[0], q=True, ws=True, rotation=True)
        if iA != 0:
            #pymel.xform(l_thumb[iA], ws=True, rotation=worldRot)
            ka_transforms.snap(l_thumb[iA], l_thumb[0], r=1)
            ka_transforms.mirrorTransform(r_thumb[iA], targetTransform=thumbJoint)

    for spine in spines:
        tryToXform(spine, rotation=[0, 0, 0], worldSpace=True)


    for neck in necks:
        tryToXform(neck, rotation=[0, 0, 0], worldSpace=True)

    tryToXform(head, rotation=[0, 0, 0], worldSpace=True)


    ka_animation.storePose('tPose')
    ka_animation.keyAllControls()

    #pymel.error()

    # FINGER CURLS ----------------------------------------------------------------
    ka_animation.advanceNFrames(KEY_SPACING)
    ka_animation.keyAllControls()

    #pymel.error()

    for iA, finger in enumerate(reversed(l_fingers)):

        # inward curl
        curl = 0
        for iB, fingerJoint in enumerate(finger):
            ka_animation.advanceNFrames(KEY_SPACING/2)

            tryToXform(l_thumb[0], rotation=flatThumbRotation, worldSpace=True)
            ka_transforms.mirrorTransform(r_thumb[0], targetTransform=l_thumb[0])

            if iB == 0:
                curl = -75

            elif iB == 1:
                curl = -95

            else:
                curl = -65

            tryToXform(fingerJoint, rotation=[0, 0, curl], worldSpace=True, relative=True)
            ka_transforms.mirrorTransform(r_fingers[iA][iB], targetTransform=fingerJoint)

            ka_animation.keyAllControls()

        ka_animation.advanceNFrames(KEY_SPACING)
        ka_animation.applyPose('tPose')

        tryToXform(l_thumb[0], rotation=flatThumbRotation, worldSpace=True,)
        ka_transforms.mirrorTransform(r_thumb[0], targetTransform=l_thumb[0])

        ka_animation.keyAllControls()

        # upward curl
        curl = 0
        for iB, fingerJoint in enumerate(finger):
            ka_animation.advanceNFrames(KEY_SPACING/2)

            if iB == 0:
                curl = 40

            elif iB == 1:
                curl = 10

            else:
                curl = 15

            tryToXform(fingerJoint, rotation=[0, 0, curl], worldSpace=True, relative=True)
            ka_transforms.mirrorTransform(r_fingers[iA][iB], targetTransform=fingerJoint)

            ka_animation.keyAllControls()

        ka_animation.advanceNFrames(KEY_SPACING/2)
        ka_animation.applyPose('tPose')

        tryToXform(l_thumb[0], rotation=flatThumbRotation, worldSpace=True)
        ka_transforms.mirrorTransform(r_thumb[0], targetTransform=l_thumb[0])

        ka_animation.keyAllControls()

    ka_animation.advanceNFrames(KEY_SPACING/2)
    ka_animation.applyPose('tPose')

    ka_animation.keyAllControls()


    # THUMB CURLS ----------------------------------------------------------------

    # innerCurl
    for iA, thumbJoint in enumerate(l_thumb):
        if iA == 0:
            #tryToXform(thumbJoint, rotation=[-90, -40, -30], worldSpace=True,)
            #ka_transforms.mirrorTransform(r_thumb[iA], targetTransform=l_thumb[iA])
            pass

        else:
            if iA == 1:
                curl = 60

            else:
                curl = 65

            rot = thumbJoint.attr(thumbCurlAxis).get()
            thumbJoint.attr(thumbCurlAxis).set(rot+curl)
            ka_transforms.mirrorTransform(r_thumb[iA], targetTransform=l_thumb[iA])

        ka_animation.keyAllControls()
        ka_animation.advanceNFrames(KEY_SPACING/2)

    ka_animation.advanceNFrames(KEY_SPACING/2)
    ka_animation.applyPose('tPose')
    ka_animation.keyAllControls()

    # outerCurl
    for iA, thumbJoint in enumerate(l_thumb):
        if iA == 0:
            #tryToXform(thumbJoint, rotation=[-45, -45, -40], worldSpace=True)
            pass
        else:
            if iA == 1:
                curl = -20

            else:
                curl = -65

            rot = thumbJoint.attr(thumbCurlAxis).get()
            thumbJoint.attr(thumbCurlAxis).set(rot+curl)
            ka_transforms.mirrorTransform(r_thumb[iA], targetTransform=l_thumb[iA])

        ka_animation.keyAllControls()
        ka_animation.advanceNFrames(KEY_SPACING/2)

    ka_animation.advanceNFrames(KEY_SPACING/2)
    ka_animation.applyPose('tPose')
    ka_animation.keyAllControls()


    # HAND CUP ----------------------------------------------------------------
    # metacarpals
    ka_animation.advanceNFrames(KEY_SPACING)
    for iA, metacarpal in enumerate(l_metacarpals):
        if iA == 0:
            rotation = [16, 0, -7]

        else:
            rotation = [-42, 0, -16]

        tryToXform(metacarpal, rotation=[rotation[0], 0, 0], worldSpace=True, relative=True)
        tryToXform(metacarpal, rotation=[0,0,rotation[2]], worldSpace=True, relative=True)
        #metacarpal.r.set(rotation)
        ka_transforms.mirrorTransform(r_metacarpals[iA], targetTransform=l_metacarpals[iA])

    # thumb
    for iA, thumbJoint in enumerate(l_thumb):
        if iA == 0:
            tryToXform(thumbJoint, rotation=[-40, 0, -44], worldSpace=True)
            ka_transforms.mirrorTransform(r_thumb[0], targetTransform=l_thumb[0])

        else:
            if iA == 1:
                curl = 40

            else:
                curl = -57

            rotz = thumbJoint.rz.get()
            rotz = thumbJoint.rz.set(rotz+curl)
            ka_transforms.mirrorTransform(r_thumb[iA], targetTransform=l_thumb[iA])

    ka_animation.keyAllControls()

    ka_animation.advanceNFrames(KEY_SPACING)
    ka_animation.applyPose('tPose')
    ka_animation.keyAllControls()


    # HAND SPLAY ----------------------------------------------------------------
    # thumb
    tryToXform(l_thumb[0], rotation=[-95, -63, 7], worldSpace=True)
    ka_transforms.mirrorTransform(r_thumb[0], targetTransform=l_thumb[0])

    for iA, finger in enumerate(l_fingers):
        if iA == 0:
            splay = 21

        elif iA == 1:
            splay = 0

        elif iA == 2:
            splay = -15

        else:
            splay = -30

        for iB, fingerJoint in enumerate(finger):
            if iB == 0:
                ry = fingerJoint.ry.get()
                fingerJoint.ry.set(ry+splay)
                ka_transforms.mirrorTransform(r_fingers[iA][iB], targetTransform=l_fingers[iA][iB])

    for iA, metacarpal in enumerate(l_metacarpals):
        if iA == 0:
            splay = -2

        else:
            splay = -6

        ry = metacarpal.ry.get()
        metacarpal.ry.set(ry+splay)
        ka_transforms.mirrorTransform(r_metacarpals[iA], targetTransform=l_metacarpals[iA])

    ka_animation.keyAllControls()

    ka_animation.advanceNFrames(KEY_SPACING)
    ka_animation.applyPose('tPose')
    ka_animation.keyAllControls()


    # WRIST ROTATIONS ----------------------------------------------------------------
    ka_animation.advanceNFrames(KEY_SPACING)

    # forward
    tryToXform(l_wrist, rotation=[-180, -32, 0], worldSpace=True)
    ka_transforms.mirrorTransform(r_wrist, targetTransform=l_wrist)

    ka_animation.keyAllControls()
    ka_animation.advanceNFrames(KEY_SPACING)

    ka_animation.applyPose('tPose')
    ka_animation.keyAllControls()
    ka_animation.advanceNFrames(KEY_SPACING)

    # back
    tryToXform(l_wrist, rotation=[-180, 50, 0], worldSpace=True)
    ka_transforms.mirrorTransform(r_wrist, targetTransform=l_wrist)

    ka_animation.keyAllControls()
    ka_animation.advanceNFrames(KEY_SPACING)

    ka_animation.applyPose('tPose')
    ka_animation.keyAllControls()
    ka_animation.advanceNFrames(KEY_SPACING)

    # up
    tryToXform(l_wrist, rotation=[-180, 0, -268], worldSpace=True)
    ka_transforms.mirrorTransform(r_wrist, targetTransform=l_wrist)

    ka_animation.keyAllControls()
    ka_animation.advanceNFrames(KEY_SPACING)

    ka_animation.applyPose('tPose')
    ka_animation.keyAllControls()
    ka_animation.advanceNFrames(KEY_SPACING)

    # down
    tryToXform(l_wrist, rotation=[-180, 0, -90], worldSpace=True)
    ka_transforms.mirrorTransform(r_wrist, targetTransform=l_wrist)

    ka_animation.keyAllControls()
    ka_animation.advanceNFrames(KEY_SPACING)

    ka_animation.applyPose('tPose')
    ka_animation.keyAllControls()
    ka_animation.advanceNFrames(KEY_SPACING)



    # forward
    tryToXform(l_wrist, rotation=[-180, -32, 0], worldSpace=True)
    ka_transforms.mirrorTransform(r_wrist, targetTransform=l_wrist)

    ka_animation.keyAllControls()
    ka_animation.advanceNFrames(KEY_SPACING)

    # up
    tryToXform(l_wrist, rotation=[-180, 0, -268], worldSpace=True)
    ka_transforms.mirrorTransform(r_wrist, targetTransform=l_wrist)

    ka_animation.keyAllControls()
    ka_animation.advanceNFrames(KEY_SPACING)

    # back
    tryToXform(l_wrist, rotation=[-180, 50, 0], worldSpace=True)
    ka_transforms.mirrorTransform(r_wrist, targetTransform=l_wrist)

    ka_animation.keyAllControls()
    ka_animation.advanceNFrames(KEY_SPACING)

    # down
    tryToXform(l_wrist, rotation=[-180, 0, -90], worldSpace=True)
    ka_transforms.mirrorTransform(r_wrist, targetTransform=l_wrist)

    ka_animation.keyAllControls()
    ka_animation.advanceNFrames(KEY_SPACING)

    # forward
    tryToXform(l_wrist, rotation=[-180, -32, 0], worldSpace=True)
    ka_transforms.mirrorTransform(r_wrist, targetTransform=l_wrist)

    ka_animation.keyAllControls()
    ka_animation.advanceNFrames(KEY_SPACING)

    ka_animation.applyPose('tPose')
    ka_animation.keyAllControls()
    ka_animation.advanceNFrames(KEY_SPACING)


    # ARM TWIST ----------------------------------------------------------------

    # twist back
    # wrist
    tryToXform(l_wrist, rotation=[-38, 0, 0], worldSpace=True, relative=True)
    ka_transforms.mirrorTransform(r_wrist, targetTransform=l_wrist)

    ka_animation.keyAllControls()
    ka_animation.advanceNFrames(KEY_SPACING)

    # arm
    tryToXform(l_arm, rotation=[-38, 0, 0], worldSpace=True, relative=True)
    ka_transforms.mirrorTransform(r_arm, targetTransform=l_arm)

    ka_animation.keyAllControls()
    ka_animation.advanceNFrames(KEY_SPACING)


    ka_animation.applyPose('tPose')
    ka_animation.keyAllControls()
    ka_animation.advanceNFrames(KEY_SPACING)


    # twist forward
    # wrist
    tryToXform(l_wrist, rotation=[90, 0, 0], worldSpace=True, relative=True)
    ka_transforms.mirrorTransform(r_wrist, targetTransform=l_wrist)

    ka_animation.keyAllControls()
    ka_animation.advanceNFrames(KEY_SPACING)

    # arm
    tryToXform(l_arm, rotation=[38, 0, 0], worldSpace=True, relative=True)
    ka_transforms.mirrorTransform(r_arm, targetTransform=l_arm)

    ka_animation.keyAllControls()
    ka_animation.advanceNFrames(KEY_SPACING)


    ka_animation.applyPose('tPose')
    ka_animation.keyAllControls()
    ka_animation.advanceNFrames(KEY_SPACING)


    # ELBOW BEND ----------------------------------------------------------------
    tryToXform(l_elbow, rotation=[0, -135, 0], worldSpace=True, relative=True)
    ka_transforms.mirrorTransform(r_elbow, targetTransform=l_elbow)

    ka_animation.keyAllControls()
    ka_animation.advanceNFrames(KEY_SPACING)

    ka_animation.applyPose('tPose')
    ka_animation.keyAllControls()
    ka_animation.advanceNFrames(KEY_SPACING)


    # ARM ROTATIONS ----------------------------------------------------------------
    # down
    tryToXform(l_arm, rotation=[0, 0, -90], worldSpace=True, relative=True)
    ka_transforms.mirrorTransform(r_arm, targetTransform=l_arm)

    ka_animation.keyAllControls()
    ka_animation.advanceNFrames(KEY_SPACING)
    ka_animation.keyAllControls()
    ka_animation.advanceNFrames(KEY_SPACING/2)

    # forward
    tryToXform(l_arm, rotation=[-90, 0, 0], worldSpace=True, relative=True)
    ka_transforms.mirrorTransform(r_arm, targetTransform=l_arm)

    ka_animation.keyAllControls()
    ka_animation.advanceNFrames(KEY_SPACING)
    ka_animation.keyAllControls()
    ka_animation.advanceNFrames(KEY_SPACING/2)

    # flat
    ka_animation.applyPose('tPose')
    ka_transforms.mirrorTransform(r_arm, targetTransform=l_arm)

    ka_animation.keyAllControls()
    ka_animation.advanceNFrames(KEY_SPACING/2)

    tryToXform(l_arm, rotation=[0, 0, 90], worldSpace=True, relative=True)
    ka_transforms.mirrorTransform(r_arm, targetTransform=l_arm)

    ka_animation.keyAllControls()
    ka_animation.advanceNFrames(KEY_SPACING/2)

    # back
    tryToXform(l_arm, rotation=[0, 90, 0], worldSpace=True, relative=True)
    ka_transforms.mirrorTransform(r_arm, targetTransform=l_arm)

    ka_animation.keyAllControls()
    ka_animation.advanceNFrames(KEY_SPACING)
    ka_animation.keyAllControls()
    ka_animation.advanceNFrames(KEY_SPACING/2)

    # down and back
    tryToXform(l_arm, rotation=[-45, 0, 0], worldSpace=True, relative=True)
    ka_transforms.mirrorTransform(r_arm, targetTransform=l_arm)

    ka_animation.keyAllControls()
    ka_animation.advanceNFrames(KEY_SPACING/2)
    ka_animation.keyAllControls()
    ka_animation.advanceNFrames(KEY_SPACING/2)

    # down
    tryToXform(l_arm, rotation=[-90, 0, 0], worldSpace=True, relative=True)
    ka_transforms.mirrorTransform(r_arm, targetTransform=l_arm)

    ka_animation.keyAllControls()
    ka_animation.advanceNFrames(KEY_SPACING)

    ka_animation.applyPose('tPose')
    ka_animation.keyAllControls()
    ka_animation.advanceNFrames(KEY_SPACING)


    # SHOULDER ROTATIONS ISOLATED ----------------------------------------------------------------

    # up
    tryToXform(l_clavical, rotation=[0, 0, 35], worldSpace=True, relative=True)

    tryToXform(l_arm, rotation=[90, 0, -0], worldSpace=True)

    ka_animation.keyAllControls()
    ka_animation.advanceNFrames(KEY_SPACING)

    ka_animation.applyPose('tPose')
    ka_animation.keyAllControls()
    ka_animation.advanceNFrames(KEY_SPACING)

    # down
    tryToXform(l_clavical, rotation=[0, 0, -16], worldSpace=True, relative=True)

    tryToXform(l_arm, rotation=[90, 0, 0], worldSpace=True)

    ka_animation.keyAllControls()
    ka_animation.advanceNFrames(KEY_SPACING)

    ka_animation.applyPose('tPose')
    ka_animation.keyAllControls()
    ka_animation.advanceNFrames(KEY_SPACING)

    # forward
    tryToXform(l_clavical, rotation=[0, -60, 0], worldSpace=True, relative=True)

    ka_animation.keyAllControls()
    ka_animation.advanceNFrames(KEY_SPACING)

    ka_animation.applyPose('tPose')
    ka_animation.keyAllControls()
    ka_animation.advanceNFrames(KEY_SPACING)

    # back
    tryToXform(l_clavical, rotation=[0, 16, 0], worldSpace=True, relative=True)

    tryToXform(l_arm, rotation=[90, 0, 0], worldSpace=True)

    ka_animation.keyAllControls()
    ka_animation.advanceNFrames(KEY_SPACING)

    ka_animation.applyPose('tPose')
    ka_animation.keyAllControls()
    ka_animation.advanceNFrames(KEY_SPACING)

    # ARM OVER HEAD ----------------------------------------------------------------
    tryToXform(l_clavical, rotation=[0, 0, 35], worldSpace=True, relative=True)

    tryToXform(l_arm, rotation=[0, 0, 105], worldSpace=True)

    ka_animation.keyAllControls()
    ka_animation.advanceNFrames(KEY_SPACING)

    ka_animation.applyPose('tPose')
    ka_animation.keyAllControls()
    ka_animation.advanceNFrames(KEY_SPACING)

    # ARM CROSSOVER ----------------------------------------------------------------
    tryToXform(l_clavical, rotation=[0, -60, 0], worldSpace=True, relative=True)

    tryToXform(l_arm, rotation=[90, -155, 0], worldSpace=True)

    ka_animation.keyAllControls()
    ka_animation.advanceNFrames(KEY_SPACING)

    ka_animation.applyPose('tPose')
    ka_animation.keyAllControls()
    ka_animation.advanceNFrames(KEY_SPACING)

    # HEAD AND NECK ROTATIONS ----------------------------------------------------------------

    # look up
    tryToXform(head, rotation=[45, 0, 0], worldSpace=True, relative=True)

    ka_animation.keyAllControls()
    ka_animation.advanceNFrames(KEY_SPACING)

    for iA, neckJoint in enumerate(reversed(necks)):
        if iA == 0:
            tryToXform(neckJoint, rotation=[20, 0, 0], worldSpace=True, relative=True)
        else:
            tryToXform(neckJoint, rotation=[10, 0, 0], worldSpace=True, relative=True)

        ka_animation.keyAllControls()
        ka_animation.advanceNFrames(KEY_SPACING)

    ka_animation.applyPose('tPose')
    ka_animation.keyAllControls()
    ka_animation.advanceNFrames(KEY_SPACING)


    # look down
    tryToXform(head, rotation=[-35, 0, 0], worldSpace=True, relative=True)

    ka_animation.keyAllControls()
    ka_animation.advanceNFrames(KEY_SPACING)

    for iA, neckJoint in enumerate(reversed(necks)):
        if iA == 0:
            tryToXform(neckJoint, rotation=[-15, 0, 0], worldSpace=True, relative=True)
        else:
            tryToXform(neckJoint, rotation=[-7, 0, 0], worldSpace=True, relative=True)

        ka_animation.keyAllControls()
        ka_animation.advanceNFrames(KEY_SPACING)

    ka_animation.applyPose('tPose')
    ka_animation.keyAllControls()
    ka_animation.advanceNFrames(KEY_SPACING)


    # bend left
    tryToXform(head, rotation=[0, 0, 45], worldSpace=True, relative=True)

    ka_animation.keyAllControls()
    ka_animation.advanceNFrames(KEY_SPACING)

    for iA, neckJoint in enumerate(reversed(necks)):
        if iA == 0:
            tryToXform(neckJoint, rotation=[0, 0, 20], worldSpace=True, relative=True)
        else:
            tryToXform(neckJoint, rotation=[0, 0, 10], worldSpace=True, relative=True)

        ka_animation.keyAllControls()
        ka_animation.advanceNFrames(KEY_SPACING)

    ka_animation.applyPose('tPose')
    ka_animation.keyAllControls()
    ka_animation.advanceNFrames(KEY_SPACING)


    # bend right
    tryToXform(head, rotation=[0, 0, -45], worldSpace=True, relative=True)

    ka_animation.keyAllControls()
    ka_animation.advanceNFrames(KEY_SPACING)

    for iA, neckJoint in enumerate(reversed(necks)):
        if iA == 0:
            tryToXform(neckJoint, rotation=[0, 0, -20], worldSpace=True, relative=True)
        else:
            tryToXform(neckJoint, rotation=[0, 0, -10], worldSpace=True, relative=True)

        ka_animation.keyAllControls()
        ka_animation.advanceNFrames(KEY_SPACING)

    ka_animation.applyPose('tPose')
    ka_animation.keyAllControls()
    ka_animation.advanceNFrames(KEY_SPACING)


    # HEAD AND NECK TWIST ----------------------------------------------------------------
    twist = 105
    numberOfControls = 1+len(necks)
    twistPerJoint = twist*(1.0/numberOfControls)

    # twist left
    tryToXform(head, rotation=[0, twistPerJoint, 0], worldSpace=True, relative=True)

    ka_animation.keyAllControls()
    ka_animation.advanceNFrames(KEY_SPACING)

    for iA, neckJoint in enumerate(reversed(necks)):
        tryToXform(neckJoint, rotation=[0, twistPerJoint, 0], worldSpace=True, relative=True)

        ka_animation.keyAllControls()
        ka_animation.advanceNFrames(KEY_SPACING)

    ka_animation.applyPose('tPose')
    ka_animation.keyAllControls()
    ka_animation.advanceNFrames(KEY_SPACING)

    # twist right
    twistPerJoint *= -1

    tryToXform(head, rotation=[0, twistPerJoint, 0], worldSpace=True, relative=True)

    ka_animation.keyAllControls()
    ka_animation.advanceNFrames(KEY_SPACING)

    for iA, neckJoint in enumerate(reversed(necks)):
        tryToXform(neckJoint, rotation=[0, twistPerJoint, 0], worldSpace=True, relative=True)

        ka_animation.keyAllControls()
        ka_animation.advanceNFrames(KEY_SPACING)

    ka_animation.applyPose('tPose')
    ka_animation.keyAllControls()
    ka_animation.advanceNFrames(KEY_SPACING)


    # SPINE ROTATIONS ----------------------------------------------------------------

    # forward
    for iA, spineJoint in enumerate(reversed(spines)):
        if iA == 0:
            bend = -20
        else:
            bend = -30

        tryToXform(spineJoint, rotation=[bend, 0, 0], worldSpace=True, relative=True)

        ka_animation.keyAllControls()
        ka_animation.advanceNFrames(KEY_SPACING/2)

    ka_animation.advanceNFrames(KEY_SPACING/2)
    ka_animation.applyPose('tPose')
    ka_animation.keyAllControls()
    ka_animation.advanceNFrames(KEY_SPACING/2)


    # backward
    for iA, spineJoint in enumerate(reversed(spines)):
        if iA == 0:
            bend = 20
        else:
            bend = 30

        tryToXform(spineJoint, rotation=[bend, 0, 0], worldSpace=True, relative=True)

        ka_animation.keyAllControls()
        ka_animation.advanceNFrames(KEY_SPACING)

    ka_animation.advanceNFrames(KEY_SPACING/2)
    ka_animation.applyPose('tPose')
    ka_animation.keyAllControls()
    ka_animation.advanceNFrames(KEY_SPACING/2)


    # bend left
    for iA, spineJoint in enumerate(reversed(spines)):
        if iA == 0:
            bend = 20
        else:
            bend = 30

        tryToXform(spineJoint, rotation=[0, 0, bend], worldSpace=True, relative=True)

        ka_animation.keyAllControls()
        ka_animation.advanceNFrames(KEY_SPACING)

    ka_animation.advanceNFrames(KEY_SPACING/2)
    ka_animation.applyPose('tPose')
    ka_animation.keyAllControls()
    ka_animation.advanceNFrames(KEY_SPACING/2)


    # bend right
    for iA, spineJoint in enumerate(reversed(spines)):
        if iA == 0:
            bend = -20
        else:
            bend = -30

        tryToXform(spineJoint, rotation=[0, 0, bend], worldSpace=True, relative=True)

        ka_animation.keyAllControls()
        ka_animation.advanceNFrames(KEY_SPACING)

    ka_animation.advanceNFrames(KEY_SPACING/2)
    ka_animation.applyPose('tPose')
    ka_animation.keyAllControls()
    ka_animation.advanceNFrames(KEY_SPACING/2)

    # SPINE TWIST ----------------------------------------------------------------
    twist = 90
    numberOfControls = len(spines)
    twistPerJoint = twist*(1.0/numberOfControls)

    # left
    for iA, spineJoint in enumerate(reversed(spines)):
        tryToXform(spineJoint, rotation=[0, twistPerJoint, 0], worldSpace=True, relative=True)

        ka_animation.keyAllControls()
        ka_animation.advanceNFrames(KEY_SPACING/2)


    tryToXform(l_clavical, rotation=[0, 15, 0], worldSpace=True, relative=True)
    tryToXform(r_clavical, rotation=[0, 30, 0], worldSpace=True, relative=True)

    ka_animation.keyAllControls()
    ka_animation.advanceNFrames(KEY_SPACING/2)

    ka_animation.advanceNFrames(KEY_SPACING/2)
    ka_animation.applyPose('tPose')
    ka_animation.keyAllControls()
    ka_animation.advanceNFrames(KEY_SPACING/2)


    # right
    twistPerJoint *= -1

    for iA, spineJoint in enumerate(reversed(spines)):
        tryToXform(spineJoint, rotation=[0, twistPerJoint, 0], worldSpace=True, relative=True)

        ka_animation.keyAllControls()
        ka_animation.advanceNFrames(KEY_SPACING/2)

    tryToXform(l_clavical, rotation=[0, -30, 0], worldSpace=True, relative=True)
    tryToXform(r_clavical, rotation=[0, -15, 0], worldSpace=True, relative=True)

    ka_animation.keyAllControls()
    ka_animation.advanceNFrames(KEY_SPACING/2)

    ka_animation.advanceNFrames(KEY_SPACING/2)
    ka_animation.applyPose('tPose')
    ka_animation.keyAllControls()
    ka_animation.advanceNFrames(KEY_SPACING)


    # PELVIS ----------------------------------------------------------------

    # forwards
    tryToXform(pelvis, rotation=[0, 0, -45], worldSpace=True, relative=True)
    tryToXform(l_leg, rotation=[90, 0, -90], worldSpace=True,)
    tryToXform(r_leg, rotation=[-90, 0, 90], worldSpace=True,)

    ka_animation.keyAllControls()
    ka_animation.advanceNFrames(KEY_SPACING)

    ka_animation.applyPose('tPose')
    ka_animation.keyAllControls()
    ka_animation.advanceNFrames(KEY_SPACING)


    # backwards
    tryToXform(pelvis, rotation=[0, 0, 30], worldSpace=True, relative=True)
    tryToXform(l_leg, rotation=[90, 0, -90], worldSpace=True,)
    tryToXform(r_leg, rotation=[-90, 0, 90], worldSpace=True,)

    ka_animation.keyAllControls()
    ka_animation.advanceNFrames(KEY_SPACING)

    ka_animation.applyPose('tPose')
    ka_animation.keyAllControls()
    ka_animation.advanceNFrames(KEY_SPACING)


    # left
    tryToXform(pelvis, rotation=[0, 0, -20], worldSpace=True, relative=True)
    tryToXform(l_leg, rotation=[90, 0, -90], worldSpace=True,)
    tryToXform(r_leg, rotation=[-90, 0, 90], worldSpace=True,)

    ka_animation.keyAllControls()
    ka_animation.advanceNFrames(KEY_SPACING)

    ka_animation.applyPose('tPose')
    ka_animation.keyAllControls()
    ka_animation.advanceNFrames(KEY_SPACING)


    # right
    tryToXform(pelvis, rotation=[0, 0, 20], worldSpace=True, relative=True)
    tryToXform(l_leg, rotation=[90, 0, -90], worldSpace=True,)
    tryToXform(r_leg, rotation=[-90, 0, 90], worldSpace=True,)

    ka_animation.keyAllControls()
    ka_animation.advanceNFrames(KEY_SPACING)

    ka_animation.applyPose('tPose')
    ka_animation.keyAllControls()
    ka_animation.advanceNFrames(KEY_SPACING)


    # twist right
    tryToXform(pelvis, rotation=[0, 30, 0], worldSpace=True, relative=True)
    tryToXform(l_leg, rotation=[90, 0, -90], worldSpace=True,)
    tryToXform(r_leg, rotation=[-90, 0, 90], worldSpace=True,)

    ka_animation.keyAllControls()
    ka_animation.advanceNFrames(KEY_SPACING)

    ka_animation.applyPose('tPose')
    ka_animation.keyAllControls()
    ka_animation.advanceNFrames(KEY_SPACING)


    # twist left
    tryToXform(pelvis, rotation=[0, -30, 0], worldSpace=True, relative=True)
    tryToXform(l_leg, rotation=[90, 0, -90], worldSpace=True,)
    tryToXform(r_leg, rotation=[-90, 0, 90], worldSpace=True,)

    ka_animation.keyAllControls()
    ka_animation.advanceNFrames(KEY_SPACING)

    ka_animation.applyPose('tPose')
    ka_animation.keyAllControls()
    ka_animation.advanceNFrames(KEY_SPACING)


    # TOES ----------------------------------------------------------------
    # up
    tryToXform(l_footBall, rotation=[-45, 0, 0], worldSpace=True, relative=True)

    ka_animation.keyAllControls()
    ka_animation.advanceNFrames(KEY_SPACING)

    ka_animation.applyPose('tPose')
    ka_animation.keyAllControls()
    ka_animation.advanceNFrames(KEY_SPACING)


    # down
    tryToXform(l_footBall, rotation=[30, 0, 0], worldSpace=True, relative=True)

    ka_animation.keyAllControls()
    ka_animation.advanceNFrames(KEY_SPACING)

    ka_animation.applyPose('tPose')
    ka_animation.keyAllControls()
    ka_animation.advanceNFrames(KEY_SPACING)


    # ANKLE ----------------------------------------------------------------
    # up
    tryToXform(l_ankle, rotation=[-15, 0, 0], worldSpace=True, relative=True)
    ka_transforms.mirrorTransform(r_ankle, targetTransform=l_ankle)

    ka_animation.keyAllControls()
    ka_animation.advanceNFrames(KEY_SPACING)

    ka_animation.applyPose('tPose')
    ka_animation.keyAllControls()
    ka_animation.advanceNFrames(KEY_SPACING)


    # down
    tryToXform(l_ankle, rotation=[60, 0, 0], worldSpace=True, relative=True)
    ka_transforms.mirrorTransform(r_ankle, targetTransform=l_ankle)

    ka_animation.keyAllControls()
    ka_animation.advanceNFrames(KEY_SPACING)

    ka_animation.applyPose('tPose')
    ka_animation.keyAllControls()
    ka_animation.advanceNFrames(KEY_SPACING)


    # outside
    tryToXform(l_ankle, rotation=[0, 0, -40], worldSpace=True, relative=True)
    ka_transforms.mirrorTransform(r_ankle, targetTransform=l_ankle)

    ka_animation.keyAllControls()
    ka_animation.advanceNFrames(KEY_SPACING)

    ka_animation.applyPose('tPose')
    ka_animation.keyAllControls()
    ka_animation.advanceNFrames(KEY_SPACING)


    # inside
    tryToXform(l_ankle, rotation=[0, 0, 30], worldSpace=True, relative=True)
    ka_transforms.mirrorTransform(r_ankle, targetTransform=l_ankle)

    ka_animation.keyAllControls()
    ka_animation.advanceNFrames(KEY_SPACING)

    ka_animation.applyPose('tPose')
    ka_animation.keyAllControls()
    ka_animation.advanceNFrames(KEY_SPACING)


    # KNEE ----------------------------------------------------------------
    tryToXform(l_knee, rotation=[90, 0, 0], worldSpace=True, relative=True)

    ka_animation.keyAllControls()
    ka_animation.advanceNFrames(KEY_SPACING)

    ka_animation.applyPose('tPose')
    ka_animation.keyAllControls()
    ka_animation.advanceNFrames(KEY_SPACING)


    # LEG ROTATION ----------------------------------------------------------------
    # fowards
    tryToXform(l_leg, rotation=[-90, 0, 0], worldSpace=True, relative=True)

    ka_animation.keyAllControls()
    ka_animation.advanceNFrames(KEY_SPACING)

    ka_animation.applyPose('tPose')
    ka_animation.keyAllControls()
    ka_animation.advanceNFrames(KEY_SPACING)


    # backwards
    tryToXform(l_leg, rotation=[90, 0, 0], worldSpace=True, relative=True)

    ka_animation.keyAllControls()
    ka_animation.advanceNFrames(KEY_SPACING)

    ka_animation.applyPose('tPose')
    ka_animation.keyAllControls()
    ka_animation.advanceNFrames(KEY_SPACING)


    # outside
    tryToXform(l_leg, rotation=[0, 0, 30], worldSpace=True, relative=True)

    ka_animation.keyAllControls()
    ka_animation.advanceNFrames(KEY_SPACING)

    ka_animation.applyPose('tPose')
    ka_animation.keyAllControls()
    ka_animation.advanceNFrames(KEY_SPACING)


    # inside
    tryToXform(l_leg, rotation=[0, 0, -65], worldSpace=True, relative=True)
    tryToXform(r_leg, rotation=[0, 0, -65], worldSpace=True, relative=True)

    ka_animation.keyAllControls()
    ka_animation.advanceNFrames(KEY_SPACING)

    ka_animation.applyPose('tPose')
    ka_animation.keyAllControls()
    ka_animation.advanceNFrames(KEY_SPACING)

    # fowards
    tryToXform(l_leg, rotation=[-90, 0, 0], worldSpace=True, relative=True)
    ka_transforms.mirrorTransform(r_leg, targetTransform=l_leg)

    ka_animation.keyAllControls()
    ka_animation.advanceNFrames(KEY_SPACING)

    # outside
    tryToXform(l_leg, rotation=[0, 0, 30], worldSpace=True, relative=True)
    ka_transforms.mirrorTransform(r_leg, targetTransform=l_leg)

    ka_animation.keyAllControls()
    ka_animation.advanceNFrames(KEY_SPACING)

    # backwards
    tryToXform(l_leg, rotation=[90, 0, 0], worldSpace=True, relative=True)
    ka_transforms.mirrorTransform(r_leg, targetTransform=l_leg)

    ka_animation.keyAllControls()
    ka_animation.advanceNFrames(KEY_SPACING)

    # inside
    tryToXform(l_leg, rotation=[0, 0, -65], worldSpace=True, relative=True)
    tryToXform(r_leg, rotation=[0, 0, -65], worldSpace=True, relative=True)

    ka_animation.keyAllControls()
    ka_animation.advanceNFrames(KEY_SPACING)

    ka_animation.applyPose('tPose')
    ka_animation.keyAllControls()
    ka_animation.advanceNFrames(KEY_SPACING)


    # LEG TWIST ----------------------------------------------------------------

    # outside
    # ankle
    tryToXform(l_ankle, rotation=[0, -60, -0], worldSpace=True)
    ka_transforms.mirrorTransform(r_ankle, targetTransform=l_ankle)

    ka_animation.keyAllControls()
    ka_animation.advanceNFrames(KEY_SPACING)

    # leg
    tryToXform(l_leg, rotation=[-10, 0, -90], worldSpace=True)
    ka_transforms.mirrorTransform(r_leg, targetTransform=l_leg)

    ka_animation.keyAllControls()
    ka_animation.advanceNFrames(KEY_SPACING)

    ka_animation.applyPose('tPose')
    ka_animation.keyAllControls()
    ka_animation.advanceNFrames(KEY_SPACING)


    # inside
    # ankle
    tryToXform(l_ankle, rotation=[0, -135, -0], worldSpace=True)
    ka_transforms.mirrorTransform(r_ankle, targetTransform=l_ankle)

    ka_animation.keyAllControls()
    ka_animation.advanceNFrames(KEY_SPACING)

    # leg
    tryToXform(l_leg, rotation=[135, 0, -90], worldSpace=True)
    ka_transforms.mirrorTransform(r_leg, targetTransform=l_leg)

    ka_animation.keyAllControls()
    ka_animation.advanceNFrames(KEY_SPACING)

    ka_animation.applyPose('tPose')
    ka_animation.keyAllControls()
    ka_animation.advanceNFrames(KEY_SPACING)


    # Finish
    pymel.playbackOptions(min=1, max=pymel.currentTime(query=True)+50)
    pymel.currentTime( 1 )
