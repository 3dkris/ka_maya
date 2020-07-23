
#====================================================================================
#====================================================================================
#
# kMenu_menus
#
# DESCRIPTION:
#   a list of all the different menus created for kMenu
#
# DEPENDENCEYS:
#   kMenu
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


import ka_maya.ka_qtWidgets as ka_qtWidgets
PyQt = ka_qtWidgets.PyQt
QtGui = ka_qtWidgets.QtGui
QtCore = ka_qtWidgets.QtCore

import pymel.core as pymel
import maya.cmds as cmds
import maya.mel as mel

import ka_maya.ka_python as ka_python
import ka_maya.kMenu as kMenu
import ka_maya.ka_util as ka_util
import ka_maya.ka_core as ka_maya
import ka_maya.ka_context as ka_context
import ka_maya.ka_display as ka_display
import ka_maya.ka_rigSetups.ka_lengthBasedRibon as ka_lengthBasedRibon
import ka_maya.ka_attrTool.attrCommands as attrCommands
import ka_maya.ka_rigAerobics as ka_rigAerobics
import ka_maya.ka_advancedJoints as ka_advancedJoints
import ka_maya.ka_animation as ka_animation
import ka_maya.ka_shapes as ka_shapes
import ka_maya.ka_weightPainting as ka_weightPainting

context = ka_context.newContext()

# CREATE MENU
MENU_CREATE = kMenu.KMenu(label='Create', icon='create.png')
if MENU_CREATE:
    with MENU_CREATE.addSubMenu(label='Nurbs Curve'):
        for shapeName in ka_shapes.NURBSCURVE_SHAPES:
            def cmds(shapeName=shapeName):
                ka_shapes.createNurbsCurve(shapeName)
            MENU_CREATE.add(cmds, label=shapeName,)

        #MENU_CREATE.add(ka_maya.createShape_cube)
        #MENU_CREATE.add(ka_maya.createShape_circle)
        #MENU_CREATE.add(ka_maya.createShape_square)
        #MENU_CREATE.add(ka_maya.createShape_pyramidPointer)

    with MENU_CREATE.addSubMenu(label='Advanced Joints'):
        MENU_CREATE.add(ka_maya.createAdvanceJoint_pistonJoint)
        MENU_CREATE.add(ka_maya.createAdvanceJoint_ligamentJoint)
        MENU_CREATE.add(ka_maya.createAdvanceJoint_advancedIkSpline)
        MENU_CREATE.add(ka_lengthBasedRibon.create)
        MENU_CREATE.add(ka_maya.createVolumeRotator)
        MENU_CREATE.add(ka_maya.printAllVolumeRotators)
        MENU_CREATE.add(ka_maya.createAdvanceJoint_createJointNet)
        MENU_CREATE.add(ka_maya.createAntiTwistGroup)
        MENU_CREATE.add(ka_maya.createVolumeRotatorSet)

        with MENU_CREATE.addSubMenu(label='Surface Strand'):
            try:
                import ka_irs.irsObject.irsAdvancedJointRigs.surfaceControlStrand as surfaceControlStrand
                MENU_CREATE.add(surfaceControlStrand.SurfaceControlStrandWidget)
            except:
                ka_python.printError()


    with MENU_CREATE.addSubMenu(label='Rig Setups'):
        MENU_CREATE.add(ka_maya.rigSetup_advancedFK)


# SELECTION MENU
MENU_SELECTION = kMenu.KMenu(label='Selection', icon='Selection.png')
if MENU_SELECTION:
    MENU_SELECTION.add(ka_maya.filterTool)
    MENU_SELECTION.add(ka_maya.invertSelectionOrder)
    MENU_SELECTION.add(ka_maya.islandSelectComponents)
    MENU_SELECTION.add(ka_maya.selectAllSkinClusterInfluences)


# DISPLAY MENU
MENU_DISPLAY = kMenu.KMenu(label='Display', icon='visibility.png')
if MENU_DISPLAY:
    with MENU_DISPLAY.addSubMenu(label='Skinning Sets'):
        MENU_DISPLAY.add(ka_maya.skinningDisplaySet_createFromScene)
        #with MENU_DISPLAY.addSubMenu(label='Remove Skinning Set'):
            #pass
        #with MENU_DISPLAY.addSubMenu(label='Update Skinning Set'):
            #pass

        MENU_DISPLAY.add(ka_maya.skinningDisplaySet_printAll)

        for eachSet in ka_display.skinningDisplaySet_getAll():
            #MENU_DISPLAY.add(ka_maya.setSkinningDisplaySet(str(eachSet)), label=eachSet.nodeName())

            def cmd(skinningSet=eachSet): ka_maya.setSkinningDisplaySet(str(skinningSet))
            MENU_DISPLAY.add(cmd, label=eachSet.nodeName(), icon='isolateSelection.png')


    #for skinningSet in pymel.about:
    MENU_DISPLAY.add(ka_maya.setRigVis_rigging)
    MENU_DISPLAY.add(ka_maya.setRigVis_animation)
    MENU_DISPLAY.add(ka_maya.setIsolateSet)
    MENU_DISPLAY.add(ka_maya.clearIsolateSet)
    MENU_DISPLAY.add(ka_maya.hideRotationAxisForAll)
    MENU_DISPLAY.add(ka_maya.isolateSelection_skinningMode)
    MENU_DISPLAY.add(ka_maya.toggleColorWireframeOnSelected)
    MENU_DISPLAY.add(ka_maya.disableDrawOverrides_onSelection)
    MENU_DISPLAY.add(ka_maya.enableDrawOverrides_onSelection)


# ANIMATION MENU
MENU_ANIMATION = kMenu.KMenu(label='Animation', icon='key.png')
if MENU_ANIMATION:
    MENU_ANIMATION.addSeparator(label='Keys and Time')
    MENU_ANIMATION.add(ka_maya.keyAllControls)
    MENU_ANIMATION.add(ka_maya.advance1FrameStep)
    MENU_ANIMATION.add(ka_maya.advanceHalfFrameStep)
    MENU_ANIMATION.add(ka_maya.advanceDoubleFrameStep)
    MENU_ANIMATION.add(ka_maya.keyFrame1OnCurrentFrame)

    MENU_ANIMATION.addSeparator(label='Insert Frames')
    MENU_ANIMATION.add(ka_maya.insert1FrameStep)
    MENU_ANIMATION.add(ka_maya.insertHalfFrameStep)
    MENU_ANIMATION.add(ka_maya.insertDoubleFrameStep)

    #MENU_ANIMATION.add(ka_maya.applyTPose)

    MENU_ANIMATION.addSeparator(label='Controls Set')
    MENU_ANIMATION.add(ka_maya.storeTPose)
    MENU_ANIMATION.add(ka_maya.storeSelectionAsAllControlsSet)
    MENU_ANIMATION.add(ka_maya.addSelectionToControlsSet)
    MENU_ANIMATION.add(ka_maya.selectAllControls)

    MENU_ANIMATION.addSeparator(label='Animation Range Sets')
    MENU_ANIMATION.add(ka_maya.storeNewAnimationFrameSet)
    MENU_ANIMATION.add(ka_maya.animationFrameSet_addItemsToSet)
    MENU_ANIMATION.add(ka_maya.animationFrameSet_updateFrameRange)
    MENU_ANIMATION.add(ka_maya.animationFrameSet_setItemsOfSet)


    animationFrameSets = ka_animation.getAllAnimationFrameSets()
    with MENU_ANIMATION.addSubMenu(label='SET Current Animation Frame Sets'):
        for animFrameSet in animationFrameSets:
            def cmd(animFrameSet=animFrameSet): ka_animation.setAnimationFrameSet(animFrameSet)
            MENU_ANIMATION.add(cmd, label=animFrameSet.nodeName().replace(ka_animation.ANIMATION_FRAME_SET_PREFIX, ''))


    with MENU_ANIMATION.addSubMenu(label='ADD Selection to Animation Frame Sets'):
        for animFrameSet in animationFrameSets:
            def cmd(animFrameSet=animFrameSet): ka_animation.animationFrameSet_addItemsToSet(animFrameSet)
            MENU_ANIMATION.add(cmd, label=animFrameSet.nodeName().replace(ka_animation.ANIMATION_FRAME_SET_PREFIX, ''))


    if context.getStudioEnv() == 'rnk':
        MENU_ANIMATION.addSeparator(label='Apply RNK Bipied Rig Aerobics')
        MENU_ANIMATION.add(ka_rigAerobics.rnkBipiedAnimation)


# BLENDSHAPE MENU
MENU_BLENDSHAPES = kMenu.KMenu(label='Blendshapes')
if MENU_BLENDSHAPES:
    MENU_BLENDSHAPES.add(ka_maya.mirrorMesh)
    MENU_BLENDSHAPES.add(ka_maya.flipMesh)


# SKINNING MENU
MENU_SKINNING = kMenu.KMenu(label='Skinning: ')
if MENU_SKINNING:

    MENU_SKINNING.addSeparator(label='Joint under mouse', context=ka_context.paintableInfluenceUnderMouse_context)
    MENU_SKINNING.add(ka_maya.paintInfluenceUnderMouse)
    MENU_SKINNING.add(ka_maya.paintInfluenceUnderMouse_andHoldAllOthers)

    MENU_SKINNING.addSeparator(label='Paint Maps', context=ka_context.paintableInfluenceUnderMouse_context)

    # paint weight map selector menu ----------------------------------------------------
    def populatePaintMenu(MENU_SKINNING):

        MENU_SKINNING.clear()

        #selection = pymel.selected()
        selection = context.getSelection()
        if selection:
            paintDicts = ka_weightPainting.getPaintableAttributes(selection[-1])
            if paintDicts:
                for paintDict in paintDicts:
                    #nodeType, nodeName, attrName = paintMapString.split('.')[:3]

                    def cmd(paintDict=paintDict):
                        ka_weightPainting.paintAttribute(paintDict)

                    #MENU_SKINNING.add(cmd, label='%s - %s.%s' % (nodeType, nodeName, attrName))
                    MENU_SKINNING.add(cmd, label=paintDict['label'])

    with MENU_SKINNING.addSubMenu(label='Paint Maps:', menuPopulateCommand=populatePaintMenu):
        pass

    MENU_SKINNING.add(ka_maya.copyCurrentWeightMap)
    MENU_SKINNING.add(ka_maya.pasteOnCurrentWeightMap)
    MENU_SKINNING.add(ka_maya.flipCurrentWeightMap)
    MENU_SKINNING.add(ka_maya.mirrorCurrentWeightMap)
    MENU_SKINNING.add(ka_maya.invertCurrentWeightMap)



    MENU_SKINNING.addSeparator(label='Influence Holding')
    MENU_SKINNING.add(ka_maya.holdInfluences)
    MENU_SKINNING.add(ka_maya.unholdInfluences)

    MENU_SKINNING.addSeparator(label='Skinning Commands')
    MENU_SKINNING.add(ka_maya.mirrorWeights)
    MENU_SKINNING.add(ka_maya.mirrorWeights_onFrame1)
    MENU_SKINNING.add(ka_maya.isolateSelection_skinningMode)

    MENU_SKINNING.addSeparator(label='skinCluster Resets')
    MENU_SKINNING.add(ka_maya.resetSkinCluster)
    MENU_SKINNING.add(ka_maya.resetSkinCluster_onFrame1)
    MENU_SKINNING.add(ka_maya.bakeSkinCluster)

    with MENU_SKINNING.addSubMenu(label='Copy / Paste Weights'):

        #MENU_SKINNING.addSeparator(label='Copy Paste Weights')
        MENU_SKINNING.add(ka_maya.copySkinWeights)
        MENU_SKINNING.add(ka_maya.pasteSkinWeights)


    MENU_SKINNING.addSeparator(label='Misc')
    MENU_SKINNING.add(ka_maya.deleteAllBindPoseNodes)


# DEFORMERS MENU
MENU_DEFORMERS = kMenu.KMenu(label='Deformers', icon='deformers.png')
if MENU_DEFORMERS:
    MENU_DEFORMERS.add(ka_maya.skinCluster)
    MENU_DEFORMERS.add(MENU_SKINNING)
    MENU_DEFORMERS.add(MENU_BLENDSHAPES)
    MENU_DEFORMERS.add(ka_maya.clusterDeform_eachInSelection)
    MENU_DEFORMERS.add(ka_maya.exportDeformersOfSelectedToTempFile)
    MENU_DEFORMERS.add(ka_maya.importDeformersFromTempFileToSelected)


# TRANSFORMS MENU
MENU_TRANSFORMS = kMenu.KMenu(label='Transforms', icon='xyz.png')
if MENU_TRANSFORMS:
    MENU_TRANSFORMS.add(ka_maya.removeNonStandardTransformValues)
    MENU_TRANSFORMS.add(ka_maya.removeJointOrients)


# COPY PASTE MENU
MENU_COPYPASTE = kMenu.KMenu(label='Copy & Paste', icon='clipboard.png')
if MENU_COPYPASTE:
    MENU_COPYPASTE.add(ka_maya.copyShape)
    MENU_COPYPASTE.add(ka_maya.pasteShape)
    MENU_COPYPASTE.add(ka_maya.pasteShapeFlipped)
    MENU_COPYPASTE.add(ka_maya.pasteShapeReversed)


# TRANSFER MENU
MENU_TRANSFER = kMenu.KMenu(label='Transfer Tools', icon='transfer.png')
if MENU_TRANSFER:
    MENU_TRANSFER.add(MENU_COPYPASTE)
    MENU_TRANSFER.add(ka_maya.transferSkin)
    MENU_TRANSFER.add(ka_maya.transferSelectedWeights)
    MENU_TRANSFER.add(ka_maya.storeSelection)
    MENU_TRANSFER.add(ka_maya.xferComponentWeights_fromStoredSelection)
    MENU_TRANSFER.add(ka_maya.xferComponentWeights_fromStoredSelection_onFrame1)

# COLOR MENU
MENU_COLOR = kMenu.KMenu(label='Color', icon='colorPallet.png')
if MENU_COLOR:
    favoriteColors = [([1.0, 0.0, 0.0], 'Red'),
                      ([0.66, 0.0, 0.0], '%66 Red'),
                      ([0.0, 0.0, 1.0], 'Blue'),
                      ([0.0, 0.0, 0.66], '%66 Blue'),
                      ([1.0, 1.0, 0.0], 'Yellow'),
                      ([0.66, 0.66, 0.0], '%66 Yellow'),
                      ([0.3919999897480011, 0.86299997568130493, 1.0], 'Baby Blue'),
                      ([0.25871999323368072, 0.56957998394966125, 0.66], '%66 Baby Blue'),
                      ([1.0, 0.5, 0.0], 'Orange'),
                      ([0.5, 0.25, 0.0], '%66 Orange'),
                      ]

    # CUSTOME Colors
    for rgbColor, label in favoriteColors:
        r, g, b = rgbColor

        def cmd(rgbColor=rgbColor): ka_util.colorObjects(color=rgbColor)
        MENU_COLOR.add(cmd, label=label, icon=rgbColor)


    # MAYA Colors
    for i in range(32):
        if i == 0:
            def cmd(): mel.eval("kaRig_colourSelection \"black\";")
            MENU_COLOR.add(cmd, label='#%s None' % str(i))
        else:
            rgb = pymel.colorIndex( i, q=True )

            def cmd(i=i): ka_util.colorObjects(index=i)
            MENU_COLOR.add(cmd, label='#%s' % str(i), icon=rgb)


# LOCK / UNLOCK MENU
MENU_LOCK_UNLOCK = kMenu.KMenu(label='Lock / Unlock', icon='lock.png')
if MENU_LOCK_UNLOCK:
    with MENU_LOCK_UNLOCK.addSubMenu(label='Lock', icon='lock.png'):
        MENU_LOCK_UNLOCK.add(ka_maya.lockTranslate)
        MENU_LOCK_UNLOCK.add(ka_maya.lockRotate)
        MENU_LOCK_UNLOCK.add(ka_maya.lockScale)
        MENU_LOCK_UNLOCK.add(ka_maya.lockVis)
        MENU_LOCK_UNLOCK.add(ka_maya.lockRadius)
        MENU_LOCK_UNLOCK.add(ka_maya.lockTransformExtras)
        MENU_LOCK_UNLOCK.add(ka_maya.lockDefault)

        MENU_LOCK_UNLOCK.add(ka_maya.lockAll)

    with MENU_LOCK_UNLOCK.addSubMenu(label='Unlock', icon='unlock.png'):
        MENU_LOCK_UNLOCK.add(ka_maya.unlockTranslate)
        MENU_LOCK_UNLOCK.add(ka_maya.unlockRotate)
        MENU_LOCK_UNLOCK.add(ka_maya.unlockScale)
        MENU_LOCK_UNLOCK.add(ka_maya.unlockVis)
        MENU_LOCK_UNLOCK.add(ka_maya.unlockRadius)
        MENU_LOCK_UNLOCK.add(ka_maya.unlockTransformExtras)
        MENU_LOCK_UNLOCK.add(ka_maya.unlockDefault)
        MENU_LOCK_UNLOCK.add(ka_maya.unlockAll)


# HIERARCHY MENU
MENU_HIERARCHY = kMenu.KMenu(label='Hierarchy', icon='groups.png')
if MENU_HIERARCHY:
    MENU_HIERARCHY.add(ka_maya.addZeroOutGroup)
    MENU_HIERARCHY.add(ka_maya.parentShape)


# CONSTRAINT MENU
MENU_CONSTRAINT = kMenu.KMenu(label='Constrain', icon='pointConstraint.png')
if MENU_CONSTRAINT:
    MENU_CONSTRAINT.add(ka_maya.constrain_surfaceConstraint)
    MENU_CONSTRAINT.add(ka_maya.constrain_curveConstraint)
    MENU_CONSTRAINT.add(ka_maya.constrain_aimBetweenConstraint)
    MENU_CONSTRAINT.add(ka_maya.constrain_pointAndOrient)
    MENU_CONSTRAINT.add(ka_maya.constrain_pointOrientAndScale)
    MENU_CONSTRAINT.add(ka_maya.constrain_jointOrientContraint)
    MENU_CONSTRAINT.add(ka_maya.constrain_distanceBetween)
    MENU_CONSTRAINT.add(ka_maya.constrain_nonTwistAim)
    with MENU_CONSTRAINT.addSubMenu(label='Direct Connects'):
        MENU_CONSTRAINT.add(ka_maya.directConnect_translates)
        MENU_CONSTRAINT.add(ka_maya.directConnect_rotates)
        MENU_CONSTRAINT.add(ka_maya.directConnect_scales)




# SNAP MENU
MENU_SNAP = kMenu.KMenu(label='Snap', icon='magnet.png')
if MENU_SNAP:
    MENU_SNAP.add(ka_maya.snap_translate)
    MENU_SNAP.add(ka_maya.snap_rotate)
    MENU_SNAP.add(ka_maya.snap_scale)
    MENU_SNAP.add(ka_maya.snap_aim)
    MENU_SNAP.add(ka_maya.snap_mirror)
    MENU_SNAP.add(ka_maya.snap_rigControl)



# MISC MENU
MENU_MISC = kMenu.KMenu(label='Misc', icon='misc.png')
if MENU_MISC:
    with MENU_MISC.addSubMenu(label='Print Commands'):
        MENU_MISC.add(ka_maya.print_selection_asPythonList)
        MENU_MISC.add(ka_maya.print_curve)
        MENU_MISC.add(ka_maya.print_mesh)

    MENU_MISC.add(ka_maya.deleteAllKeyframes)
    #MENU_MISC.add(ka_maya.removeNamespacesFromSelection)
    MENU_MISC.add(ka_maya.deleteAllBindPoseNodes)
    MENU_MISC.add(ka_maya.findLatticeCageFromLatticeDeformer)
    MENU_MISC.add(ka_maya.setJointLabel)
    MENU_MISC.add(ka_maya.setJointLabel_allInfluences)
    MENU_MISC.add(ka_maya.reorderAllShapesToTopOfTheirHierchy)
    MENU_MISC.add(ka_maya.makeSurfaceConstraint_useTangetV)
    MENU_MISC.add(ka_maya.makeSurfaceConstraint_useTangetU)


# TOOL MENU
MENU_TOOL = kMenu.KMenu(label='Tools: ', icon='tools.png')
if MENU_TOOL:
    MENU_TOOL.add(ka_maya.renameTool)
    MENU_TOOL.add(ka_maya.filterTool)
    MENU_TOOL.add(ka_maya.attrTool)


# COMPONENT_SELECTION_MENU
MENU_COMPONENT = kMenu.KMenu(label='Component Selection: ')
if MENU_COMPONENT:
    MENU_COMPONENT.add(ka_maya.pasteWeightsFromInfluence)


# HYPERSHADE MENU
MENU_HYPERSHADE = kMenu.KMenu(label='HyperShade: ')
if MENU_HYPERSHADE:
    MENU_HYPERSHADE.add(ka_maya.attrTool)

    MENU_HYPERSHADE.addSeparator('') #---------------------------------------------------------

    MENU_HYPERSHADE.add(ka_maya.hyperShade_alignNodesVertical)
    MENU_HYPERSHADE.add(ka_maya.hyperShade_alignNodesHorizontal)
    MENU_HYPERSHADE.add(ka_maya.hyperShade_clear)
    MENU_HYPERSHADE.add(ka_maya.hyperShade_isolateSelection)
    MENU_HYPERSHADE.add(ka_maya.hyperShade_add)
    MENU_HYPERSHADE.add(ka_maya.hyperShade_remove)

    MENU_HYPERSHADE.addSeparator('') #---------------------------------------------------------

    MENU_HYPERSHADE.add(ka_maya.hyperShade_duplicate)
    MENU_HYPERSHADE.add(ka_maya.hyperShade_echoRecreateCommands)
    with MENU_HYPERSHADE.addSubMenu(label='Create Node', icon='create.png'):
        createNodeTypesList = ['choice', 'multiplyDivide', 'blendColors', 'condition', 'setRange', 'plusMinusAverage', 'blendTwoAttr', 'distanceBetween', 'pointOnCurveInfo', 'curveInfo', 'pointOnSurfaceInfo', 'surfaceInfo', 'closestPointOnSurface', 'angleBetween', 'vectorProduct', 'arrayMapper', 'bump2d', 'bump3d', 'heightField', 'lightInfo', 'place2dTexture', 'place3dTexture', 'projection', 'reverse', 'samplerInfo', 'stencil', 'uvChooser', 'animCurveUU', 'animCurveUA', 'animCurveUL', 'animCurveUT', 'closestPointOnMesh', 'remapValue',]
        for eachNodeType in sorted(createNodeTypesList):
            if 'animCurve' in eachNodeType:
                def cmd(nodeType=eachNodeType):
                    node = pymel.createNode(nodeType)
                    ka_hyperShade.addKeysToAnimCurveNode(node)
                    return node
            else:
                def cmd(nodeType=eachNodeType):
                    pymel.createNode(nodeType)
                    return node

            MENU_HYPERSHADE.add(cmd, label=eachNodeType)

    MENU_HYPERSHADE.addSeparator('') #---------------------------------------------------------

    MENU_HYPERSHADE.add(ka_maya.hyperShade_graphInputs)
    MENU_HYPERSHADE.add(ka_maya.hyperShade_graphOutputs)
    MENU_HYPERSHADE.add(ka_maya.hyperShade_graphInputsAndOutputs)

    MENU_HYPERSHADE.addSeparator('') #---------------------------------------------------------

    with MENU_HYPERSHADE.addSubMenu(label='Misc', icon='misc.png'):
        MENU_HYPERSHADE.add(ka_maya.hyperShade_selectInputs)
        MENU_HYPERSHADE.add(ka_maya.hyperShade_selectOutputs)
        MENU_HYPERSHADE.add(ka_maya.hyperShade_selectInputsAndOutputs)

        MENU_HYPERSHADE.addSeparator('') #---------------------------------------------------------

        MENU_HYPERSHADE.add(ka_maya.hyperShade_addKeysToAnimCurveNode)
        MENU_HYPERSHADE.add(ka_maya.hyperShade_add1DInputToPlusMinusAverageNode)

        with MENU_HYPERSHADE.addSubMenu(label='convertAnimCurvesTo:', icon='transfer.png'):
            MENU_HYPERSHADE.add(ka_maya.convertAnimCurveTo_UU)
            MENU_HYPERSHADE.add(ka_maya.convertAnimCurveTo_UA)
            MENU_HYPERSHADE.add(ka_maya.convertAnimCurveTo_UL)
            MENU_HYPERSHADE.add(ka_maya.convertAnimCurveTo_UT)




MENU_ATTR_TOOL = kMenu.KMenu()
MENU_ATTR_TOOL.add(kMenu.KMenuItem_attrTool)

ADDON_MENUS = []
try:
    import ka_maya.ka_addons.nitro.nitro_menus as nitro_menus
    ADDON_MENUS.append(nitro_menus.MENU)
except:
    pass


# ROOT MENU
MENU_ROOT = kMenu.KMenu()
if MENU_ROOT:

    MENU_ROOT.addSeparator(label='Context Actions')

    #if ka_context.weightedComponentsSelected(context=context):
    MENU_ROOT.add(ka_maya.pasteSkinWeightsAlongStrand, showContext=ka_context.weightedComponentsSelected)
    #MENU_ROOT.add(ka_maya.pasteSkinWeightsAlongStrandSoft, showContext=ka_context.weightedComponentsSelected)
    MENU_ROOT.add(ka_maya.pasteSkinWeightsFromStrandNeighbores, showContext=ka_context.weightedComponentsSelected)



    if context.userIsK():
        MENU_ROOT.add(ka_maya.createHuman)
        MENU_ROOT.add(ka_maya.createHandFoot)
        MENU_ROOT.add(ka_maya.testCommandA)
        MENU_ROOT.add(ka_maya.testCommandB)
        MENU_ROOT.add(ka_maya.testCommandC)


    MENU_ROOT.add(ka_maya.skinCluster)
    MENU_ROOT.add(ka_maya.addInfluence)
    if context.getStudioEnv() == 'rnk':
        pass


    MENU_ROOT.addSeparator(label='Root Menu')
    MENU_ROOT.add(MENU_CREATE)
    MENU_ROOT.add(MENU_SELECTION)
    MENU_ROOT.add(MENU_DISPLAY)


    MENU_ROOT.add(MENU_DEFORMERS)
    MENU_ROOT.add(MENU_ANIMATION)
    MENU_ROOT.add(MENU_TRANSFORMS)
    MENU_ROOT.add(MENU_TRANSFER)
    MENU_ROOT.add(MENU_COLOR)
    MENU_ROOT.add(MENU_LOCK_UNLOCK)
    MENU_ROOT.add(MENU_HIERARCHY)
    MENU_ROOT.add(MENU_CONSTRAINT)
    MENU_ROOT.add(MENU_SNAP)
    MENU_ROOT.add(MENU_MISC)
    MENU_ROOT.add(MENU_TOOL)

    if context.userIsK():
        for menu in ADDON_MENUS:
            MENU_ROOT.add(menu)

    MENU_ROOT.addSeparator(label='Context Menus')
    MENU_ROOT.add(MENU_SKINNING)
    MENU_ROOT.add(MENU_HYPERSHADE)






def popMenu(clearFirst=False):
    global MENU_ROOT

    context = ka_context.newContext()


    #if clearFirst:
        #if kMenu.getAllKMenuWidgets():
            #kMenu.clearUnpinnedKMenus(onlyNonPinned=False)


    if kMenu.getAllUnpinnedKMenuWidgets():
        kMenu.clearUnpinnedKMenus()

    else:
        #kMenu.clearUnpinnedKMenus()
        #kMenu.raise_MenuWidgets()

        if context.getUiTypeUnderMouse() == 'hyperShade':
            if context.getHypershade_nodeUnderMouse():
                MENU_ATTR_TOOL.pop()

            else:
                MENU_HYPERSHADE.pop()


        elif context.getUiTypeUnderMouse() == 'model':

            if context.getCurrentTool() in ('artAttrSkinContext', 'artAttrContext', 'artAttrBlendShapeContext'):
                MENU_SKINNING.pop()

            #elif context.getCurrentTool() == 'artAttrContext':
                #MENU_SKINNING.pop()

            elif ka_context.paintableInfluenceUnderMouse_and_componentsSelected_context(context=context):
                MENU_COMPONENT.pop()

            else:
                #skinningDisplaySets = ka_display.skinningDisplaySet_getAll()
                #if skinningDisplaySets:
                    #skinningDisplaySetsMenu = kMenu.KMenu(label='Skinning Sets: ')
                    #for eachSet in skinningDisplaySets:
                        #def cmd(skinningSet=eachSet): ka_maya.setSkinningDisplaySet(str(skinningSet))
                        #MENU_DISPLAY.add(cmd, label=eachSet.nodeName(), icon='isolateSelection.png')

                    #MENU_ROOT.add(skinningDisplaySetsMenu)

                MENU_ROOT.pop()


        else:
            MENU_ROOT.pop()

