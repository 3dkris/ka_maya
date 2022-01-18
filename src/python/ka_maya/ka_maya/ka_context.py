#====================================================================================
#====================================================================================
#
# ka_context
#
# DESCRIPTION:
#   A module for finding different contexts, such as panel under mouse or active tool
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
import getpass

import maya.OpenMaya as OpenMaya
import pymel.core as pymel
import maya.cmds as cmds
import maya.mel as mel

import ka_maya.ka_clipBoard as ka_clipBoard    #;reload(ka_clipBoard)
import ka_maya.ka_skinCluster as ka_skinCluster    #;reload(ka_skinCluster)

def getCurrentContext():
    try:
        context = ka_clipBoard.get('currentContext', None)
    except:
        context = None


    if not context:
        context = newContext()

    return context

def newContext():
    context = ka_clipBoard.add('currentContext', Context())
    return context

########################################################################
class Context(object):

    def __init__(self):

        # ui under mouse
        self._uiTypeUnderMouse = None
        self._panelUnderMouse = None
        self._panelUnderMouse_type = None
        self._panelWithFocus = None
        self._panelWithFocus_type = None

        # current tool
        self._currentTool = None
        self._toolIsWeightPainting = None

        # node under mouse
        self._hypershade_NodeUnderMouse = None
        self._hypershade_NodeUnderMouseType = None

        self._dagObjectHit = None

        self._dagObjectHit_transform = None
        self._dagObjectHit_nodeType = None

        self._dagObjectHit_shape = None
        self._dagObjectHit_shapes = None
        self._dagObjectHit_shapeType = None

        # selection
        self._selection = None
        self._lenOfSelection = None
        self._selectedNodes = None
        self._selectionNodeTypes = None
        self._selectionUniqueNodeTypes = None

        self._getDagObjectHitInfo_()

        self._selectionIncludesComponents = None
        self._selectionIsComponents = None
        self._selectionIncludesNode = None
        self._selectionIncludesSkinnedGeo = None

        # misc
        self._studioEnv = None
        self._userIsK = None


    # UI UNDER MOUSE -------------------------------------------------------------------------------------
    def getUiTypeUnderMouse(self):
        """returns a predictable string for the ui type the mouse is over.
        ie: 'model' if the mouse is over the 3d view"""

        if self._uiTypeUnderMouse != None: return self._uiTypeUnderMouse

        panelName = self.getPanelUnderMouse()
        if panelName:
            if 'Panel' in panelName:
                self._uiTypeUnderMouse = panelName.split('Panel')[0] # ie: modelPanel

        return self._uiTypeUnderMouse

    def getPanelUnderMouse(self):
        if self._panelUnderMouse != None: return self._panelUnderMouse

        self._panelUnderMouse = pymel.getPanel(underPointer=True)
        return self._panelUnderMouse

    def getPanelWithFocus(self):
        if self._panelWithFocus != None: return self._panelWithFocus

        self._panelWithFocus = pymel.getPanel(withFocus=True)
        return self._panelWithFocus

    # CURRENT TOOL -------------------------------------------------------------------------------------
    def getCurrentTool(self):
        """Returns the current tool context"""
        if self._currentTool != None: return self._currentTool

        self._currentTool = cmds.currentCtx()
        return self._currentTool


    def weightPainting(self):
        """Returns bool if the current tool context is for weight painting"""
        if self._toolIsWeightPainting is not None: return self._toolIsWeightPainting

        if 'artAttr' in self.getCurrentTool():
            self._toolIsWeightPainting = True
        else:
            self._toolIsWeightPainting = False

        return self._toolIsWeightPainting


    # CURRENT STUDIO -------------------------------------------------------------------------------------
    def getStudioEnv(self):
        if self._studioEnv != None: return self._studioEnv

        if 'RNK_MAYA_VERSION' in os.environ:
            self._studioEnv = 'rnk'

        return self._studioEnv

    # CURRENT USER -------------------------------------------------------------------------------------
    def userIsK(self):
        if self._userIsK != None: return self._userIsK

        if getpass.getuser() in ['kandrews', 'admin']:
            self._userIsK = True

        return self._userIsK


    # DEFORMERS -------------------------------------------------------------------------------------


    # NODE UNDER MOUSE HYPERSHADE-------------------------------------------------------------------------------------
    def getHypershade_nodeUnderMouse(self):
        """Returns the node under the mouse in the hypershade tool context"""
        if self._hypershade_NodeUnderMouse != None: return self._hypershade_NodeUnderMouse

        hypergraph = "graph1HyperShadeEd"
        nodeUnderMouse = pymel.hyperGraph(hypergraph, query=True, feedbackNode=True,)

        if nodeUnderMouse:
            self._hypershade_NodeUnderMouse = pymel.ls(nodeUnderMouse)[0] #return pymel object

        return self._hypershade_NodeUnderMouse


    def getHypershade_nodeUnderMouseType(self):
        """Returns the node type of the node under the mouse (if there is one), in the hypershade tool context"""
        if self._hypershade_NodeUnderMouseType != None: return self._hypershade_NodeUnderMouseType

        if self._hypershade_NodeUnderMouse != None:
            node = self._hypershade_NodeUnderMouse
        else:
            node = self.getHypershade_nodeUnderMouse()

        if node != None:
            self._hypershade_NodeUnderMouseType = node.nodeType()

        return self._hypershade_NodeUnderMouseType


    # NODE UNDER MOUSE -------------------------------------------------------------------------------------
    def _getDagObjectHitInfo_(self):
        """Gets information about the objects under the mouse in the modeling
        panel"""

        mel.eval('global int $gKa_menu = 1')
        dagObjectHit = mel.eval('dagObjectHit -mn %s' % 'fakeMenu')
        mel.eval('global int $gKa_menu = 0')

        dagObjectHit_objectHit = None
        dagObjectHit_nodeType = None
        dagObjectHit_objectHitShape = None
        dagObjectHit_objectHitShapes = None
        dagObjectHit_shapeNodeType = None

        if dagObjectHit:
            dagObjectHit_objectHit = mel.eval('$gDagObjectHit_objectHit=$gDagObjectHit_objectHit')
            if pymel.objExists(dagObjectHit_objectHit):
                dagObjectHit_objectHit = pymel.ls(dagObjectHit_objectHit)[0]
                dagObjectHit_nodeType = pymel.nodeType(dagObjectHit_objectHit)

                dagObjectHit_objectHitShapes = dagObjectHit_objectHit.getShapes()
                if dagObjectHit_objectHitShapes:
                    dagObjectHit_objectHitShape = dagObjectHit_objectHitShapes[0]
                    dagObjectHit_shapeNodeType = dagObjectHit_objectHitShape.nodeType()

            dagObjectHit = True


        self._dagObjectHit = dagObjectHit

        self._dagObjectHit_transform = dagObjectHit_objectHit
        self._dagObjectHit_nodeType = dagObjectHit_nodeType

        self._dagObjectHit_shape = dagObjectHit_objectHitShape
        self._dagObjectHit_shapes = dagObjectHit_objectHitShapes
        self._dagObjectHit_shapeType = dagObjectHit_shapeNodeType


    def getTransformUnderMouse(self):
        # return if stored
        if self._currentTool != None: return self._currentTool

        if not self._dagObjectHit_transform:
            self._getDagObjectHitInfo_()
        return self._dagObjectHit_transform


    def getTransformNodeTypeUnderMouse(self):
        # return if stored
        if self._dagObjectHit_nodeType != None: return self._dagObjectHit_nodeType

        if not self._dagObjectHit_nodeType:
            self._getDagObjectHitInfo_()
        return self._dagObjectHit_nodeType


    def getShapeUnderMouse(self):
        # return if stored
        if self._dagObjectHit_shape != None: return self._dagObjectHit_shape

        if not self._dagObjectHit_shape:
            self._getDagObjectHitInfo_()
        return self._dagObjectHit_shape


    def getShapesUnderMouse(self):
        # return if stored
        if self._dagObjectHit_shapes != None: return self._dagObjectHit_shapes

        if not self._dagObjectHit_shapes:
            self._getDagObjectHitInfo_()
        return self._dagObjectHit_shapes


    def getShapeNodeTypeUnderMouse(self):
        # return if stored
        if self._dagObjectHit_shapeType != None: return self._dagObjectHit_shapeType

        if not self._dagObjectHit_shapeType:
            self._getDagObjectHitInfo_()
        return self._dagObjectHit_shapeType

    # SELECTION -------------------------------------------------------------------------------------
    def getSelection(self):
        """Gets the current selection, as well as storing various information about that selection"""

        if self._selection is not None: return self._selection

        self._selection = []
        self._selectedNodes = []
        self._selectionNodeTypes = []

        typesDict = {}

        # iter selection
        componentsMObject = OpenMaya.MObject()
        mScriptUtil = OpenMaya.MScriptUtil()
        mSelectionList = OpenMaya.MSelectionList()
        OpenMaya.MGlobal.getActiveSelectionList(mSelectionList)
        mNodeIter = OpenMaya.MItSelectionList(mSelectionList)

        while not mNodeIter.isDone():
            itemType = mNodeIter.itemType()
            self._selectionIncludesNode = True

            if itemType == OpenMaya.MItSelectionList.kDagSelectionItem:
                # get dagPath
                mDagPath = OpenMaya.MDagPath()
                mNodeIter.getDagPath( mDagPath, componentsMObject)

                # add to self._selection
                #pyNode = pymel.PyNode(mDagPath.fullPathName())
                fullPath = mDagPath.fullPathName()
                pyNode = pymel.PyNode(fullPath)
                self._selection.append(pyNode)
                self._selectedNodes.append(pyNode)

                # get mObject from dagPath
                mObject = mDagPath.node()
                mFnDependencyNode = OpenMaya.MFnDependencyNode(mObject)

                # get type
                typeName = mFnDependencyNode.typeName()
                typesDict[typeName] = None
                self._selectionNodeTypes.append(typeName)

                # get number of shapes
                ptr = mScriptUtil.asUintPtr()
                numberOfShapes = mDagPath.numberOfShapesDirectlyBelow(ptr)

                for i in range(mScriptUtil.getUint(ptr)):
                    # get dagPath
                    mShapeDagPath = OpenMaya.MDagPath(mDagPath)
                    mShapeDagPath.extendToShapeDirectlyBelow(i)

                    # get mObject from dagPath
                    mObject = mShapeDagPath.node()
                    mFnDependencyNode = OpenMaya.MFnDependencyNode(mObject)

                    # get type
                    typeName = mFnDependencyNode.typeName()
                    typesDict[typeName] = None


                # misc info
                # selection includes components
                if self._selectionIncludesComponents is None:
                    if componentsMObject.apiType() != 0:
                        self._selectionIncludesComponents = True

                # selection is exclusively components
                if self._selectionIsComponents is not False:
                    if componentsMObject.apiType() == 0:
                        self._selectionIsComponents = False
                    else:
                        self._selectionIsComponents = True
                        self._selectionIncludesNode = False


            elif itemType == OpenMaya.MItSelectionList.kDNselectionItem:
                # get mObject
                mObject = OpenMaya.MObject()
                mNodeIter.getDependNode(mObject)

                # get MFnDependencyNode
                mFnDependencyNode = OpenMaya.MFnDependencyNode(mObject)

                # add to self._selection
                #pyNode = pymel.PyNode(mFnDependencyNode.name())
                pyNode = pymel.PyNode(mFnDependencyNode.name())
                self._selection.append(pyNode)
                self._selectedNodes.append(pyNode)

                # get typeName
                typeName = mFnDependencyNode.typeName()
                typesDict[typeName] = None
                self._selectionNodeTypes.append(typeName)

                # misc info
                self._selectionIsComponents = False

            mNodeIter.next()

        self._selection = tuple(self._selection)
        self._selectedNodes = tuple(self._selectedNodes)
        self._lenOfSelection = len(self._selectedNodes)
        self._selectionNodeTypes = tuple(self._selectionNodeTypes)
        self._selectionUniqueNodeTypes = tuple(typesDict.keys())

        return self._selection

    def getLenOfSelection(self):
        if self._lenOfSelection is not None: return self._lenOfSelection

        self.getSelection()
        return self._lenOfSelection

    def getSelectedNodes(self):
        if self._selectedNodes != None: return self._selectedNodes

        self.getSelection()

        #nodes = []
        #for item in self.getSelection():
            #node = item.node()
            #if node not in nodes:
                #nodes.append(node)

        #self._selectedNodes = nodes
        return self._selectedNodes


    def getSelection_nodeTypes(self):
        if self._selectionNodeTypes != None: return self._selectionNodeTypes

        self.getSelection()

        #self._selectionNodeTypes = []
        #for node in self.getSelection():
            #self._selectionNodeTypes.append(node.nodeType())
        return self._selectionNodeTypes


    def getSelection_uniqueNodeTypes(self):
        if self._selectionUniqueNodeTypes != None: return self._selectionUniqueNodeTypes

        self.getSelection()
        #self._selectionUniqueNodeTypes = []
        #for nodeType in self.getSelection_nodeTypes():
            #if nodeType not in self._selectionUniqueNodeTypes:
                #self._selectionUniqueNodeTypes.append(nodeType)

        return self._selectionUniqueNodeTypes


    def selectionIncludesComponents(self):
        if self._selectionIncludesComponents != None: return self._selectionIncludesComponents

        self.getSelection()




        #self._selectionIncludesComponents = False
        #selection = self.getSelection()
        #for item in selection:
            #strItem = str(item)
            #if '.' in strItem:
                #self._selectionIncludesComponents = True
                #return self._selectionIncludesComponents

        return self._selectionIncludesComponents

    def selectionIsComponents(self):
        if self._selectionIsComponents != None: return self._selectionIsComponents

        self.getSelection()


        return self._selectionIsComponents

    def selectionIncludesNode(self):
        if self._selectionIncludesNode != None: return self._selectionIncludesNode

        self.getSelection()
        #OpenMaya.MGlobal.getActiveSelectionList(mSelectionList)
        #componentsMObject = OpenMaya.MObject()

        #while not mNodeIter.isDone():
            #itemType = mNodeIter.itemType()


        return self._selectionIncludesNode


    def selectionIncludesSkinnedGeo(self):
        if self._selectionIncludesSkinnedGeo != None: return self._selectionIncludesSkinnedGeo

        self._selectionIncludesSkinnedGeo = False
        for item in self.getSelectedNodes():
            skinCluster = ka_skinCluster.findRelatedSkinCluster(item)
            if skinCluster:
                self._selectionIncludesSkinnedGeo = True
                return self._selectionIncludesSkinnedGeo

        return self._selectionIncludesSkinnedGeo



# CONTEXT FUNCTIONS ----------------------------------------------------
def paintableInfluenceUnderMouse_context(context=None):
    if not context:
        context = getCurrentContext()

    selection = context.getSelection()
    nodeUnderMouse = context.getTransformUnderMouse()
    nodeUnderMouseType = context.getTransformNodeTypeUnderMouse()

    if nodeUnderMouseType == 'joint':
        skinCluster = ka_skinCluster.findRelatedSkinCluster(selection[-1])
        if skinCluster:
            return True

    return False


def paintableInfluenceUnderMouse_and_componentsSelected_context(context=None):
    if not context:
        context = getCurrentContext()

    selection = context.getSelection()
    nodeUnderMouse = context.getTransformUnderMouse()
    nodeUnderMouseType = context.getTransformNodeTypeUnderMouse()

    if context.selectionIncludesComponents():
        if nodeUnderMouseType == 'joint':
            skinCluster = ka_skinCluster.findRelatedSkinCluster(selection[-1])
            if skinCluster:
                return True

    return False


def addInfluenceContext(context=None):
    if not context:
        context = getCurrentContext()

    selection = context.getSelection()

    if context.selectionIncludesSkinnedGeo():
        if 'joint' in context.getSelection_nodeTypes():
            return True

    return False


def createSkinClusterContext(context=None):
    if not context:
        context = getCurrentContext()

    selection = context.getSelection()

    nonJoints = 0
    if selection:
        if not context.selectionIncludesSkinnedGeo():
            for nodeType in context.getSelection_nodeTypes():
                if nodeType != 'joint':
                    nonJoints += 1
                    if nonJoints == 2:
                        return False

            if nonJoints == 1:
                return True

    return False


def weightedComponentsSelected(context=None):
    if not context:
        context = getCurrentContext()

    if context.selectionIncludesSkinnedGeo():
        if context.selectionIncludesComponents():
            return True

    return False

def trueContext():
    return True