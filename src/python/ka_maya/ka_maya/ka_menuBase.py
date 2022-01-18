#====================================================================================
#====================================================================================
#
# ka_menuWidget_menus
#
# DESCRIPTION:
#   a list of all the different menus created for ka_menuWidget
#
# DEPENDENCEYS:
#   ka_menuWidget
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

import ka_maya.ka_qtWidgets as ka_qtWidgets
PyQt = ka_qtWidgets.PyQt
QtGui = ka_qtWidgets.QtGui
QtCore = ka_qtWidgets.QtCore

import pymel.core as pymel
import maya.cmds as cmds
import maya.mel as mel

import ka_maya.ka_context as ka_context
import ka_maya.ka_menuWidget as ka_menuWidget

import ka_maya.ka_python as ka_python
import ka_maya.ka_menuWidget as ka_menuWidget
import ka_maya.ka_util as ka_util
import ka_maya.ka_display as ka_display
import ka_maya.ka_rigSetups.ka_lengthBasedRibon as ka_lengthBasedRibon
import ka_maya.ka_attrTool.attrCommands as attrCommands
import ka_maya.ka_rigAerobics as ka_rigAerobics
import ka_maya.ka_advancedJoints as ka_advancedJoints
import ka_maya.ka_animation as ka_animation
import ka_maya.ka_shapes as ka_shapes
import ka_maya.ka_weightPainting as ka_weightPainting

import ka_maya.ka_core as ka_core

context = ka_context.newContext()

MENU_ROOT = ka_menuWidget.Ka_menu()

# NAME SELECTION ----------------------------------------------
#def nameSelection(menu):
    #menu.clear()
    #selection = cmds.ls(selection=True)
    #if selection:
        #for item in selection:
            #label = str(item)
            #menu.add(cmd, label=label)

#with MENU_ROOT.addSubMenu(label='selection:', menuPopulateCommand=nameSelection):
    #pass


# CREATE MENU
MENU_CREATE = ka_menuWidget.Ka_menu(label='Create', icon='create.png')
if MENU_CREATE:
    with MENU_CREATE.addSubMenu(label='Nurbs Curve'):
        for shapeName in ka_shapes.NURBSCURVE_SHAPES:
            def cmd(shapeName=shapeName):
                ka_shapes.createNurbsCurve(shapeName)
            MENU_CREATE.add(cmd, label=shapeName,)

        #MENU_CREATE.add(ka_core.createShape_cube)
        #MENU_CREATE.add(ka_core.createShape_circle)
        #MENU_CREATE.add(ka_core.createShape_square)
        #MENU_CREATE.add(ka_core.createShape_pyramidPointer)


    with MENU_CREATE.addSubMenu(label='Advanced Joints'):
        MENU_CREATE.add(ka_core.createAdvanceJoint_pistonJoint)
        MENU_CREATE.add(ka_core.createAdvanceJoint_ligamentJoint)
        MENU_CREATE.add(ka_core.createAdvanceJoint_advancedIkSpline)
        MENU_CREATE.add(ka_lengthBasedRibon.create)
        MENU_CREATE.add(ka_core.createAdvanceJoint_createJointNet)

        #with MENU_CREATE.addSubMenu(label='Surface Strand'):
            ###try:
            #import ka_irs.irsObject.irsAdvancedJointRigs.surfaceControlStrand as surfaceControlStrand
            #MENU_CREATE.add(surfaceControlStrand.SurfaceControlStrandWidget)
            ###except:
                ###ka_python.printError()

    with MENU_CREATE.addSubMenu(label='Irs Limbs'):
        MENU_CREATE.add(ka_core.createAdvanceJoint_pistonJoint)


    with MENU_CREATE.addSubMenu(label='Rig Setups'):
        MENU_CREATE.add(ka_core.rigSetup_advancedFK)


# SELECTION MENU
MENU_SELECTION = ka_menuWidget.Ka_menu(label='Selection', icon='Selection.png')
if MENU_SELECTION:
    MENU_SELECTION.add(ka_core.filterTool)
    MENU_SELECTION.add(ka_core.invertSelectionOrder)
    MENU_SELECTION.add(ka_core.islandSelectComponents)
    MENU_SELECTION.add(ka_core.selectAllSkinClusterInfluences)


# DISPLAY MENU
MENU_DISPLAY = ka_menuWidget.Ka_menu(label='Display', icon='visibility.png')
if MENU_DISPLAY:
    with MENU_DISPLAY.addSubMenu(label='Skinning Sets'):
        MENU_DISPLAY.add(ka_core.skinningDisplaySet_createFromScene)
        #with MENU_DISPLAY.addSubMenu(label='Remove Skinning Set'):
            #pass
        #with MENU_DISPLAY.addSubMenu(label='Update Skinning Set'):
            #pass

        MENU_DISPLAY.add(ka_core.skinningDisplaySet_printAll)

        for eachSet in ka_display.skinningDisplaySet_getAll():
            #MENU_DISPLAY.add(ka_core.setSkinningDisplaySet(str(eachSet)), label=eachSet.nodeName())

            def cmd(skinningSet=eachSet): ka_core.setSkinningDisplaySet(str(skinningSet))
            MENU_DISPLAY.add(cmd, label=eachSet.nodeName(), icon='isolateSelection.png')


    #for skinningSet in pymel.about:
    MENU_DISPLAY.add(ka_core.setRigVis_rigging)
    MENU_DISPLAY.add(ka_core.setRigVis_animation)
    MENU_DISPLAY.add(ka_core.setIsolateSet)
    MENU_DISPLAY.add(ka_core.clearIsolateSet)
    MENU_DISPLAY.add(ka_core.hideRotationAxisForAll, icon='xyz.png')
    MENU_DISPLAY.add(ka_core.taperJointRadiusAlongChain)
    MENU_DISPLAY.add(ka_core.isolateSelection_skinningMode)
    MENU_DISPLAY.add(ka_core.toggleColorWireframeOnSelected)
    MENU_DISPLAY.add(ka_core.enableDrawOverrides_onSelection)
    MENU_DISPLAY.add(ka_core.disableDrawOverrides_onSelection)

# SHAPES MENU
MENU_SHAPES = ka_menuWidget.Ka_menu(label='Shapes')
if MENU_SHAPES:

    # COPY PASTE MENU
    with MENU_SHAPES.addSubMenu(label='Copy & Paste', icon='clipboard.png'):
        MENU_SHAPES.add(ka_core.copyShape)
        MENU_SHAPES.add(ka_core.pasteShape)
        MENU_SHAPES.add(ka_core.pasteShapeFlipped)
        MENU_SHAPES.add(ka_core.pasteShapeReversed)

    MENU_SHAPES.add(ka_core.shrinkWrapShape)



# ANIMATION MENU
MENU_ANIMATION = ka_menuWidget.Ka_menu(label='Animation', icon='key.png')
if MENU_ANIMATION:
    MENU_ANIMATION.addSeparator(label='Keys and Time')
    MENU_ANIMATION.add(ka_core.keyAllControls)
    MENU_ANIMATION.add(ka_core.advance1FrameStep)
    MENU_ANIMATION.add(ka_core.advanceHalfFrameStep)
    MENU_ANIMATION.add(ka_core.advanceDoubleFrameStep)
    MENU_ANIMATION.add(ka_core.keyFrame1OnCurrentFrame)

    MENU_ANIMATION.addSeparator(label='Insert Frames')
    MENU_ANIMATION.add(ka_core.insert1FrameStep)
    MENU_ANIMATION.add(ka_core.insertHalfFrameStep)
    MENU_ANIMATION.add(ka_core.insertDoubleFrameStep)

    #MENU_ANIMATION.add(ka_core.applyTPose)

    MENU_ANIMATION.addSeparator(label='Controls Set')
    MENU_ANIMATION.add(ka_core.storeTPose)
    MENU_ANIMATION.add(ka_core.storeSelectionAsAllControlsSet)
    MENU_ANIMATION.add(ka_core.addSelectionToControlsSet)
    MENU_ANIMATION.add(ka_core.removeSelectionFromControlSet)

    MENU_ANIMATION.add(ka_core.selectAllControls)

    MENU_ANIMATION.addSeparator(label='Animation Range Sets')
    MENU_ANIMATION.add(ka_core.storeNewAnimationFrameSet)
    MENU_ANIMATION.add(ka_core.animationFrameSet_addItemsToSet)
    MENU_ANIMATION.add(ka_core.animationFrameSet_updateFrameRange)
    MENU_ANIMATION.add(ka_core.animationFrameSet_setItemsOfSet)


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


    MENU_ANIMATION.addSeparator()
    MENU_ANIMATION.add(ka_core.deleteAllKeyframes)



# BLENDSHAPE MENU
MENU_BLENDSHAPES = ka_menuWidget.Ka_menu(label='Blendshapes')
if MENU_BLENDSHAPES:
    MENU_BLENDSHAPES.add(ka_core.mirrorMesh)
    MENU_BLENDSHAPES.add(ka_core.flipMesh)


# SKINNING MENU
MENU_SKINNING = ka_menuWidget.Ka_menu(label='Skinning: ')
if MENU_SKINNING:

    MENU_SKINNING.addSeparator(label='Joint under mouse', showContext=ka_context.paintableInfluenceUnderMouse_context)
    MENU_SKINNING.add(ka_core.paintInfluenceUnderMouse)
    MENU_SKINNING.add(ka_core.paintInfluenceUnderMouse_andHoldAllOthers)

    MENU_SKINNING.addSeparator(label='Paint Maps', showContext=ka_context.paintableInfluenceUnderMouse_context)

    # paint weight map selector menu ----------------------------------------------------
    def populatePaintMenu(MENU_SKINNING):

        MENU_SKINNING.clear()

        selection = pymel.selected()
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

    MENU_SKINNING.add(ka_core.copyCurrentWeightMap)
    MENU_SKINNING.add(ka_core.pasteOnCurrentWeightMap)
    MENU_SKINNING.add(ka_core.flipCurrentWeightMap)
    MENU_SKINNING.add(ka_core.mirrorCurrentWeightMap)
    MENU_SKINNING.add(ka_core.invertCurrentWeightMap)



    MENU_SKINNING.addSeparator(label='Influence Holding')
    MENU_SKINNING.add(ka_core.holdInfluences)
    MENU_SKINNING.add(ka_core.unholdInfluences)

    MENU_SKINNING.addSeparator(label='Skinning Commands')
    MENU_SKINNING.add(ka_core.mirrorWeights)
    MENU_SKINNING.add(ka_core.mirrorWeights_onFrame1)
    MENU_SKINNING.add(ka_core.isolateSelection_skinningMode)

    MENU_SKINNING.addSeparator(label='skinCluster Resets')
    MENU_SKINNING.add(ka_core.resetSkinCluster)
    MENU_SKINNING.add(ka_core.resetSkinCluster_onFrame1)
    MENU_SKINNING.add(ka_core.bakeSkinCluster)

    with MENU_SKINNING.addSubMenu(label='Copy / Paste Weights'):

        #MENU_SKINNING.addSeparator(label='Copy Paste Weights')
        MENU_SKINNING.add(ka_core.copySkinWeights)
        MENU_SKINNING.add(ka_core.pasteWeights)


    MENU_SKINNING.addSeparator(label='Misc')
    MENU_SKINNING.add(ka_core.deleteAllBindPoseNodes)


# DEFORMERS MENU
MENU_DEFORMERS = ka_menuWidget.Ka_menu(label='Deformers', icon='deformers.png')
if MENU_DEFORMERS:
    MENU_DEFORMERS.add(ka_core.skinCluster)
    MENU_DEFORMERS.add(MENU_SKINNING)
    MENU_DEFORMERS.add(MENU_BLENDSHAPES)
    MENU_DEFORMERS.add(ka_core.clusterDeform_eachInSelection)
    MENU_DEFORMERS.add(ka_core.exportDeformersOfSelectedToTempFile)
    MENU_DEFORMERS.add(ka_core.importDeformersFromTempFileToSelected)


# TRANSFORMS MENU
MENU_TRANSFORMS = ka_menuWidget.Ka_menu(label='Transforms', icon='xyz.png')
if MENU_TRANSFORMS:
    MENU_TRANSFORMS.add(ka_core.removeNonStandardTransformValues)
    MENU_TRANSFORMS.add(ka_core.removeJointOrients)

# TRANSFER MENU
MENU_TRANSFER = ka_menuWidget.Ka_menu(label='Transfer Tools', icon='transfer.png')
if MENU_TRANSFER:
    #MENU_TRANSFER.add(MENU_COPYPASTE)

    # transfer skins
    MENU_TRANSFER.addSeparator(label='Transfer Skins')
    MENU_TRANSFER.add(ka_core.transferSkin)
    MENU_TRANSFER.add(ka_core.transferSkinFromMultiSkins)

    MENU_TRANSFER.addSeparator(label='Transfer Skins From Secondary Selection')
    MENU_TRANSFER.add(ka_core.storeSelection)
    MENU_TRANSFER.add(ka_core.transferSkin_secondaryToPrimarySelection)
    #MENU_TRANSFER.add(ka_core.transferSkin_manyToOne_FromSecondarySelection)


    #MENU_TRANSFER.add(ka_core.transferSelectedWeights)
    #MENU_TRANSFER.add(ka_core.xferComponentWeights_fromStoredSelection)
    #MENU_TRANSFER.add(ka_core.xferComponentWeights_fromStoredSelection_onFrame1)

# COLOR MENU
MENU_COLOR = ka_menuWidget.Ka_menu(label='Color', icon='colorPalletRGB.png')
if MENU_COLOR:
    BASIC_RGB_COLORS = ((1,1,1,), (1,0,0), (1,.5,0), (1,1,0), (.5,1,0), (0,1,0), (0,1,.5), (0,1,1), (0,.5,1), (0,0,1), (.5,0,1), (1,0,1), (1,0,.5),)

    def function(color):
        print 'I R SETTING COLOR %s' % str(color)
        ka_util.colorObjects(color=color)


    # COLOR BASICS ---------------------------
    with MENU_COLOR.addSubMenu(label='Color RGB -basics', icon='colorPalletRGB.png'):
        colors = []
        shades = 5

        # blacks
        for color in BASIC_RGB_COLORS:
            colors.append((0,0,0,))

        # dark shades
        for i in range(shades):
            for color in BASIC_RGB_COLORS:
                    multiplyValue = 1.0/((shades+1)-i)
                    shadeColor = []
                    for value in color:
                        shadeColor.append(value*multiplyValue)
                    colors.append(shadeColor)

        # full color
        for color in BASIC_RGB_COLORS:
            colors.append(color)

        # light shades
        for i in range(shades):
            for color in BASIC_RGB_COLORS:
                addValue = ((1.0/shades)*(i+1))
                shadeColor = []
                for value in color:
                    if value < addValue:
                        newValue = value+addValue
                        if newValue > 1.0:
                            newValue = 1.0
                        shadeColor.append(newValue)
                    else:
                        shadeColor.append(value)

                colors.append(shadeColor)

        MENU_COLOR.add(ka_qtWidgets.ColorSelectorWidget, columns=len(BASIC_RGB_COLORS), buttonHeight=20,
                       buttonWidth=20, colors=colors, function=function)


    # COLOR SHADES ---------------------------
    with MENU_COLOR.addSubMenu(label='Color RGB -shades', icon='colorPalletRGB.png'):
        SHADES_RGB_COLORS = ((0,0,1), (.24,.47,1),  (.18,.5,.7),  (.3,.27,1),    (.44,.37,.8), (.55,.29,.95), (.69,.66,1),
                             (1,0,0), (.73,.22,.5), (.9,.46,.11), (.96,.22,.41), (.95,0,.47),  (.94,.32,.32), (1,.63,.63),
                             (1,1,0), (.82,1,0),    (.69,1,.2),   (.8,.76,.12),  (.8,.58,.12), (.73,.74,.19), (1,.98,.53),)

        colors = []

        MENU_COLOR.add(ka_qtWidgets.ColorSelectorWidget, columns=7, buttonHeight=80, buttonWidth=17,
                       colors=SHADES_RGB_COLORS, function=function)

    # COLOR INDICES ---------------------------
    with MENU_COLOR.addSubMenu(label='Color Index', icon='colorPallet.png'):
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
MENU_LOCK_UNLOCK = ka_menuWidget.Ka_menu(label='Lock / Unlock', icon='lock.png')
if MENU_LOCK_UNLOCK:
    with MENU_LOCK_UNLOCK.addSubMenu(label='Lock', icon='lock.png'):
        MENU_LOCK_UNLOCK.add(ka_core.lockTranslate)
        MENU_LOCK_UNLOCK.add(ka_core.lockRotate)
        MENU_LOCK_UNLOCK.add(ka_core.lockScale)
        MENU_LOCK_UNLOCK.add(ka_core.lockVis)
        MENU_LOCK_UNLOCK.add(ka_core.lockRadius)
        MENU_LOCK_UNLOCK.add(ka_core.lockTransformExtras)
        MENU_LOCK_UNLOCK.add(ka_core.lockDefault)

        MENU_LOCK_UNLOCK.add(ka_core.lockAll)

    with MENU_LOCK_UNLOCK.addSubMenu(label='Unlock', icon='unlock.png'):
        MENU_LOCK_UNLOCK.add(ka_core.unlockTranslate)
        MENU_LOCK_UNLOCK.add(ka_core.unlockRotate)
        MENU_LOCK_UNLOCK.add(ka_core.unlockScale)
        MENU_LOCK_UNLOCK.add(ka_core.unlockVis)
        MENU_LOCK_UNLOCK.add(ka_core.unlockRadius)
        MENU_LOCK_UNLOCK.add(ka_core.unlockTransformExtras)
        MENU_LOCK_UNLOCK.add(ka_core.unlockDefault)
        MENU_LOCK_UNLOCK.add(ka_core.unlockAll)


# HIERARCHY MENU
MENU_HIERARCHY = ka_menuWidget.Ka_menu(label='Hierarchy', icon='groups.png')
if MENU_HIERARCHY:
    MENU_HIERARCHY.add(ka_core.addZeroOutGroup)
    MENU_HIERARCHY.add(ka_core.parentShape)


# CONSTRAINT MENU
MENU_CONSTRAINT = ka_menuWidget.Ka_menu(label='Constrain', icon='pointConstraint.png')
if MENU_CONSTRAINT:
    MENU_CONSTRAINT.add(ka_core.constrain_surfaceConstraint)
    MENU_CONSTRAINT.add(ka_core.constrain_curveConstraint)
    MENU_CONSTRAINT.add(ka_core.constrain_aimBetweenConstraint)
    MENU_CONSTRAINT.add(ka_core.constrain_pointAndOrient)
    MENU_CONSTRAINT.add(ka_core.constrain_pointOrientAndScale)
    MENU_CONSTRAINT.add(ka_core.constrain_jointOrientContraint)
    MENU_CONSTRAINT.add(ka_core.constrain_distanceBetween)
    MENU_CONSTRAINT.add(ka_core.constrain_nonTwistAim)
    MENU_CONSTRAINT.add(ka_core.constrainAimWithObjectRotUp)
    with MENU_CONSTRAINT.addSubMenu(label='Direct Connects'):
        MENU_CONSTRAINT.add(ka_core.directConnect_translates)
        MENU_CONSTRAINT.add(ka_core.directConnect_rotates)
        MENU_CONSTRAINT.add(ka_core.directConnect_scales)




# SNAP MENU
MENU_SNAP = ka_menuWidget.Ka_menu(label='Snap', icon='magnet.png')
if MENU_SNAP:
    MENU_SNAP.add(ka_core.snap_translate)
    MENU_SNAP.add(ka_core.snap_rotate)
    MENU_SNAP.add(ka_core.snap_scale)
    MENU_SNAP.add(ka_core.snap_aim)
    MENU_SNAP.add(ka_core.snap_mirror)
    MENU_SNAP.add(ka_core.snap_rigControl)



# MISC MENU
MENU_MISC = ka_menuWidget.Ka_menu(label='Misc', icon='misc.png')
if MENU_MISC:
    with MENU_MISC.addSubMenu(label='Print Commands'):
        MENU_MISC.add(ka_core.print_selection_asPythonList)
        MENU_MISC.add(ka_core.print_selection_asTallPythonList)
        MENU_MISC.add(ka_core.print_selection_asPythonTuple)
        MENU_MISC.add(ka_core.print_selection_asTupleOfMatrices)

        MENU_MISC.add(ka_core.print_curve)
        MENU_MISC.add(ka_core.print_mesh)
        MENU_MISC.add(ka_core.print_curveShort)
        MENU_MISC.add(ka_core.print_meshShort)
        MENU_MISC.add(ka_core.print_BlendShapeShort)

    #MENU_MISC.add(ka_core.removeNamespacesFromSelection)
    MENU_MISC.add(ka_core.deleteAllBindPoseNodes)
    MENU_MISC.add(ka_core.findLatticeCageFromLatticeDeformer)
    MENU_MISC.add(ka_core.setJointLabel)
    MENU_MISC.add(ka_core.setJointLabel_allInfluences)
    MENU_MISC.add(ka_core.reorderAllShapesToTopOfTheirHierchy)
    MENU_MISC.add(ka_core.makeSurfaceConstraint_useTangetV)
    MENU_MISC.add(ka_core.makeSurfaceConstraint_useTangetU)


# TOOL MENU
MENU_TOOL = ka_menuWidget.Ka_menu(label='Tools: ', icon='tools.png')
if MENU_TOOL:
    MENU_TOOL.add(ka_core.renameTool)
    MENU_TOOL.add(ka_core.filterTool)
    MENU_TOOL.add(ka_core.attrTool)
    MENU_TOOL.add(ka_core.stopwatchTool, icon='stopwatch.png')


# COMPONENT_SELECTION_MENU
MENU_COMPONENT = ka_menuWidget.Ka_menu(label='Component Selection: ')
if MENU_COMPONENT:
    MENU_COMPONENT.add(ka_core.pasteWeightsFromInfluence)
    MENU_COMPONENT.addSeparator()
    #MENU_COMPONENT.add(ka_core.pasteWeightsFromInfluence)
    #MENU_COMPONENT.add(ka_core.pasteWeightsFromInfluence)


# HYPERSHADE MENU
MENU_HYPERSHADE = ka_menuWidget.Ka_menu(label='HyperShade: ')
if MENU_HYPERSHADE:
    MENU_HYPERSHADE.add(ka_core.attrTool)

    MENU_HYPERSHADE.addSeparator('') #---------------------------------------------------------

    # SELECT INPUTS ----------------------------------------------
    def defPopulateNodeInputs(MENU_HYPERSHADE):
        MENU_HYPERSHADE.clear()

        selection = pymel.ls(selection=True)
        if selection:
            connections = selection[-1].inputs(plugs=True, connections=True)
            if connections:
                for connection in connections:
                    connectedNode = connection[1].node()
                    def cmd(selection=selection, connection=connection):
                        connectedNode = connection[1].node()
                        connectedNodeType = connectedNode.type()

                        for node in selection:
                            if hasattr(node, connection[0].name(includeNode=False)):
                                for inputNode in node.inputs():
                                    if inputNode.nodeType() == connectedNodeType:
                                        pymel.select(inputNode, add=True)
                            pymel.select(node, deselect=True)

                        melCmd = 'hyperShadePanelGraphCommand("%s", "addSelected");' % context.getPanelUnderMouse()
                        mel.eval(melCmd)

                    label = '%s.%s >> .%s' % (connectedNode.nodeType(), connection[1].name(includeNode=False), connection[0].name(includeNode=False))
                    MENU_HYPERSHADE.add(cmd, label=label)

    with MENU_HYPERSHADE.addSubMenu(label='Select Inputs', menuPopulateCommand=defPopulateNodeInputs):
        pass

    # SELECT OUTPUTS ----------------------------------------------
    def defPopulateNodeOutputs(MENU_HYPERSHADE):
        MENU_HYPERSHADE.clear()

        selection = pymel.ls(selection=True)
        if selection:
            connections = selection[-1].outputs(plugs=True, connections=True)
            if connections:
                for connection in connections:
                    connectedNode = connection[1].node()
                    def cmd(selection=selection, connection=connection):
                        connectedNode = connection[1].node()
                        connectedNodeType = connectedNode.type()

                        for node in selection:
                            if hasattr(node, connection[0].name(includeNode=False)):
                                for outputNode in node.outputs():
                                    if outputNode.nodeType() == connectedNodeType:
                                        pymel.select(outputNode, add=True)

                            pymel.select(node, deselect=True)

                        melCmd = 'hyperShadePanelGraphCommand("%s", "addSelected");' % context.getPanelUnderMouse()
                        mel.eval(melCmd)

                    label = '.%s >> %s.%s' % (connection[0].name(includeNode=False), connectedNode.nodeType(), connection[1].name(includeNode=False),)
                    MENU_HYPERSHADE.add(cmd, label=label)

    with MENU_HYPERSHADE.addSubMenu(label='Select Outputs', menuPopulateCommand=defPopulateNodeOutputs):
        pass

    MENU_HYPERSHADE.addSeparator('transfer attrs') #---------------------------------------------------------


    # COPY INPUTS ----------------------------------------------
    def defPopulateNodeInputs(MENU_HYPERSHADE):
        MENU_HYPERSHADE.clear()

        selection = pymel.ls(selection=True)
        if selection:
            connections = selection[0].inputs(plugs=True, connections=True)
            if connections:
                for connection in connections:
                    connectedNode = connection[1].node()
                    def cmd(connection=connection):
                        connectedNode = connection[1].node()
                        attrName = connection[0].name(includeNode=False)
                        for eachNode in pymel.ls(selection)[1:]:
                            if hasattr(eachNode, attrName):
                                connection[1] >> eachNode.attr(attrName)

                    label = '%s.%s >> .%s' % (connectedNode.nodeType(), connection[1].name(includeNode=False), connection[0].name(includeNode=False))
                    MENU_HYPERSHADE.add(cmd, label=label)

    with MENU_HYPERSHADE.addSubMenu(label='Copy Inputs', menuPopulateCommand=defPopulateNodeInputs):
        pass


    # TRANSFER INPUTS ----------------------------------------------
    def defPopulateNodeInputs(MENU_HYPERSHADE):
        MENU_HYPERSHADE.clear()

        selection = pymel.ls(selection=True)
        if selection:
            connections = selection[0].inputs(plugs=True, connections=True)
            if connections:
                for connection in connections:
                    connectedNode = connection[1].node()
                    def cmd(connection=connection):
                        connectedNode = connection[1].node()
                        attrName = connection[0].name(includeNode=False)
                        for eachNode in pymel.ls(selection)[1:]:
                            if hasattr(eachNode, attrName):
                                connection[1] >> eachNode.attr(attrName)
                                connection[1] // connection[0]

                    label = '%s.%s >> .%s' % (connectedNode.nodeType(), connection[1].name(includeNode=False), connection[0].name(includeNode=False))
                    MENU_HYPERSHADE.add(cmd, label=label)

    with MENU_HYPERSHADE.addSubMenu(label='Transfer Inputs', menuPopulateCommand=defPopulateNodeInputs):
        pass

    # TRANSFER OUTPUTS ----------------------------------------------
    def defPopulateNodeOutputs(MENU_HYPERSHADE):
        MENU_HYPERSHADE.clear()

        selection = pymel.ls(selection=True)
        if selection:
            connections = selection[0].outputs(plugs=True, connections=True)
            if connections:
                for connection in connections:
                    connectedNode = connection[1].node()
                    def cmd(connection=connection):
                        connectedNode = connection[1].node()
                        attrName = connection[0].name(includeNode=False)
                        for eachNode in pymel.ls(selection)[1:]:
                            if hasattr(eachNode, attrName):
                                eachNode.attr(attrName) >> connection[1]

                    label = '.%s >> %s.%s' % (connection[0].name(includeNode=False), connectedNode.nodeType(), connection[1].name(includeNode=False),)
                    MENU_HYPERSHADE.add(cmd, label=label)

    with MENU_HYPERSHADE.addSubMenu(label='Transfer Outputs', menuPopulateCommand=defPopulateNodeOutputs):
        pass



    MENU_HYPERSHADE.addSeparator('') #---------------------------------------------------------

    MENU_HYPERSHADE.add(ka_core.hyperShade_alignNodesVertical)
    MENU_HYPERSHADE.add(ka_core.hyperShade_alignNodesHorizontal)
    MENU_HYPERSHADE.add(ka_core.hyperShade_clear)
    MENU_HYPERSHADE.add(ka_core.hyperShade_isolateSelection)
    MENU_HYPERSHADE.add(ka_core.hyperShade_add)
    MENU_HYPERSHADE.add(ka_core.hyperShade_remove)

    MENU_HYPERSHADE.addSeparator('') #---------------------------------------------------------

    MENU_HYPERSHADE.add(ka_core.hyperShade_duplicate)
    MENU_HYPERSHADE.add(ka_core.hyperShade_echoRecreateCommandsPymelObjectOriented)
    MENU_HYPERSHADE.add(ka_core.hyperShade_echoRecreateCommandsPymel)
    MENU_HYPERSHADE.add(ka_core.hyperShade_echoRecreateCommandsCmds)

    with MENU_HYPERSHADE.addSubMenu(label='Create Node', icon='create.png'):
        createNodeTypesList = ('choice', 'multiplyDivide', 'blendColors', 'condition', 'setRange', 'plusMinusAverage', 'blendTwoAttr', 'distanceBetween', 'angleBetween', 'vectorProduct', 'arrayMapper', 'bump2d', 'bump3d', 'heightField', 'lightInfo', 'place2dTexture', 'place3dTexture', 'projection', 'reverse', 'samplerInfo', 'stencil', 'uvChooser', 'animCurveUU', 'animCurveUA', 'animCurveUL', 'animCurveUT', 'remapValue',  )
        createNodeTypesConstraintsList = (u'aimConstraint', u'cMuscleSmartConstraint', u'constraint (abstract)', u'dynamicConstraint', u'geometryConstraint', u'hairConstraint', u'normalConstraint', u'oldGeometryConstraint', u'oldNormalConstraint', u'oldTangentConstraint', u'orientConstraint', u'parentConstraint', u'pointConstraint', u'pointOnPolyConstraint', u'poleVectorConstraint', u'rigidConstraint', u'scaleConstraint', u'symmetryConstraint', u'tangentConstraint')
        createNodeTypesGeometryList = ('closestPointOnMesh', 'pointOnCurveInfo', 'pointOnSurfaceInfo', 'curveInfo', 'surfaceInfo', 'nearestPointOnCurve', 'closestPointOnSurface', 'arcLengthDimension', )
        createNodeTypesMatricesList = (u'addMatrix', u'composeMatrix', u'decomposeMatrix', u'fourByFourMatrix', u'holdMatrix', u'inverseMatrix', u'multMatrix', u'passMatrix', u'pointMatrixMult', u'transposeMatrix', u'wtAddMatrix')
        createNodeTypesQuaternionsList = (u'eulerToQuat', u'quatAdd', u'quatConjugate', u'quatInvert', u'quatNegate', u'quatNormalize', u'quatProd', u'quatSub', u'quatToEuler')


        def addCreateNodeItem(eachNodeType, MENU_HYPERSHADE=MENU_HYPERSHADE):
            nodeTypeIconFolder = os.path.join(ka_menuWidget.ICON_FOLDER, 'nodeTypes')
            nodeTypeIcons = []
            for iconFile in os.listdir(nodeTypeIconFolder):
                nodeTypeIcons.append(iconFile.split('.')[0])

            if eachNodeType in nodeTypeIcons:
                icon = os.path.join('nodeTypes', '%s.png' % eachNodeType)
            else:
                icon = os.path.join('nodeTypes', 'unknownNode.png')

            if 'animCurve' in eachNodeType:
                def cmd(nodeType=eachNodeType):
                    node = pymel.createNode(nodeType)
                    ka_core.hyperShade_addKeysToAnimCurveNode()
                    return node
            else:
                def cmd(nodeType=eachNodeType):
                    node = pymel.createNode(nodeType)
                    return node

            MENU_HYPERSHADE.add(cmd, label=eachNodeType, icon=icon)


        with MENU_HYPERSHADE.addSubMenu(label='Constraints'):
            for eachNodeType in sorted(createNodeTypesConstraintsList):
                addCreateNodeItem(eachNodeType)

        with MENU_HYPERSHADE.addSubMenu(label='Curves/Nurbs/Geo'):
            for eachNodeType in sorted(createNodeTypesGeometryList):
                addCreateNodeItem(eachNodeType)

        with MENU_HYPERSHADE.addSubMenu(label='Matrices'):
            for eachNodeType in sorted(createNodeTypesMatricesList):
                addCreateNodeItem(eachNodeType)

        with MENU_HYPERSHADE.addSubMenu(label='Quaternions'):
            for eachNodeType in sorted(createNodeTypesQuaternionsList):
                addCreateNodeItem(eachNodeType)


        for eachNodeType in sorted(createNodeTypesList):
            addCreateNodeItem(eachNodeType)



    MENU_HYPERSHADE.addSeparator('') #---------------------------------------------------------

    MENU_HYPERSHADE.add(ka_core.hyperShade_graphInputs)
    MENU_HYPERSHADE.add(ka_core.hyperShade_graphOutputs)
    MENU_HYPERSHADE.add(ka_core.hyperShade_graphInputsAndOutputs)

    MENU_HYPERSHADE.addSeparator('') #---------------------------------------------------------

    with MENU_HYPERSHADE.addSubMenu(label='Misc', icon='misc.png'):
        MENU_HYPERSHADE.add(ka_core.hyperShade_selectInputs)
        MENU_HYPERSHADE.add(ka_core.hyperShade_selectOutputs)
        MENU_HYPERSHADE.add(ka_core.hyperShade_selectInputsAndOutputs)

        MENU_HYPERSHADE.addSeparator('') #---------------------------------------------------------

        MENU_HYPERSHADE.add(ka_core.hyperShade_addKeysToAnimCurveNode)
        MENU_HYPERSHADE.add(ka_core.hyperShade_add1DInputToPlusMinusAverageNode)

        with MENU_HYPERSHADE.addSubMenu(label='convertAnimCurvesTo:', icon='transfer.png'):
            MENU_HYPERSHADE.add(ka_core.convertAnimCurveTo_UU)
            MENU_HYPERSHADE.add(ka_core.convertAnimCurveTo_UA)
            MENU_HYPERSHADE.add(ka_core.convertAnimCurveTo_UL)
            MENU_HYPERSHADE.add(ka_core.convertAnimCurveTo_UT)




MENU_ATTR_TOOL = ka_menuWidget.Ka_menu()
MENU_ATTR_TOOL.add(ka_menuWidget.Ka_menu_attrTool)

ADDON_MENUS = []
try:
    import ka_maya.ka_addons.nitro.nitro_menus as nitro_menus
    ADDON_MENUS.append(nitro_menus.MENU)
except:
    pass



# ROOT MENU #####################################################################################################################
if MENU_ROOT:


    MENU_ROOT.add(ka_core.pasteSkinWeightsAlongStrand, showContext=ka_context.weightedComponentsSelected)
    MENU_ROOT.add(ka_core.pasteSkinWeightsFromStrandNeighbores, showContext=ka_context.weightedComponentsSelected)



    # FILTER SELECTION -------------------------------------------------------------------------------------------------
    def menuPopCmd(MENU_ROOT):
        MENU_ROOT.clear() # clear current subMenu

        selection = context.getSelection()
        for nodeType in sorted(context._selectionUniqueNodeTypes):
            def cmd(nodeType=nodeType, selection=selection):
                newSelection = pymel.select(pymel.ls(selection, type=nodeType))

            MENU_ROOT.add(cmd, label=nodeType)

    def contextCommand():
        context = ka_context.newContext()
        if context._selectionIncludesComponents == True:
            return False
        return True

    with MENU_ROOT.addSubMenu(label='Filter Selection', menuPopulateCommand=menuPopCmd, showContext=contextCommand):
        pass
    # ------------------------------------------------------------------------------------------------------------------

    # PASTE FROM BOTH NEIGHBORS
    MENU_ROOT.add(ka_core.pasteSkinWeightsFromStrandNeighbores, showContext=ka_context.weightedComponentsSelected)

    MENU_ROOT.add(ka_core.skinCluster)
    MENU_ROOT.add(ka_core.addInfluence)
    if context.getStudioEnv() == 'rnk':
        pass


    MENU_ROOT.addSeparator(label='Root Menu')
    MENU_ROOT.add(MENU_CREATE)
    MENU_ROOT.add(MENU_SELECTION)
    MENU_ROOT.add(MENU_DISPLAY)


    MENU_ROOT.add(MENU_DEFORMERS)
    MENU_ROOT.add(MENU_SHAPES)
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

    MENU_ROOT.addSeparator(label='Context Menus')
    MENU_ROOT.add(MENU_SKINNING)
    MENU_ROOT.add(MENU_HYPERSHADE)


class MenuBase(object):
    """
    This class is meant as a class for producing and object with a method (popMenu)
    which can be called to produce a ka_menu. This class can be inherited and its method
    copied or overriden with a super call to its parent to produce a similar menu with
    specific additions/subtractions.

    The whole reason for this class is to be able to make varients of the menu.
    """

    def __init__(self):
        self.context = None


    def popMenu(self):
        self.context = ka_context.newContext()
        self.generateMenu()
        self.context = None

    def generateMenu(self):
        """
        This method is used to determin which menu should be popped up at the time of the request. This
        method will typically use methods and functions of the ka_context object to decide which menu to
        show. Reimplement this function to change it behaviour in varient menus.
        """

        # if mouse over Hyper shade...
        if self.context.getUiTypeUnderMouse() == 'hyperShade':

            # if mouse over node in hypershade use attr tool menu
            if self.context.getHypershade_nodeUnderMouse():
                MENU_ATTR_TOOL.pop()

            # else use regular hypershade menu
            else:
                MENU_HYPERSHADE.pop()


        # if mouse over the 3dView...
        elif self.context.getUiTypeUnderMouse() == 'model':
            print "A"
            # if using paint tools show skinning/painting menu
            if self.context.getCurrentTool() in ('artAttrSkinContext', 'artAttrContext', 'artAttrBlendShapeContext'):
                MENU_SKINNING.pop()

            # if paintable influence is under mouse, show the custome menu for assigning weights to it
            elif ka_context.paintableInfluenceUnderMouse_and_componentsSelected_context(context=self.context):
                MENU_COMPONENT.pop()

            # else use the regular menu
            else:
                MENU_ROOT.pop()

        # else use the regular menu
        else:
            MENU_ROOT.pop()


ka_menu = MenuBase()

#def popMenu(clearFirst=False):

    #context = ka_context.newContext()

    #if context.getUiTypeUnderMouse() == 'hyperShade':
        #if context.getHypershade_nodeUnderMouse():
            #MENU_ATTR_TOOL.pop()

        #else:
            #MENU_HYPERSHADE.pop()


    #elif context.getUiTypeUnderMouse() == 'model':

        #if context.getCurrentTool() in ('artAttrSkinContext', 'artAttrContext', 'artAttrBlendShapeContext'):
            #MENU_SKINNING.pop()

        #elif ka_context.paintableInfluenceUnderMouse_and_componentsSelected_context(context=context):
            #MENU_COMPONENT.pop()

        #else:
            #MENU_ROOT.pop()


    #else:
        #MENU_ROOT.pop()

