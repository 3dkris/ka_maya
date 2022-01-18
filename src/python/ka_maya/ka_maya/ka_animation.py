#====================================================================================
#====================================================================================
#
# ka_util
#
# DESCRIPTION:
#   collection of small utility scripts that do simple yet essential tasks within maya
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

from traceback import print_exc as printError

import pymel.core as pymel
import maya.cmds as cmds
import maya.mel as mel

import ka_maya.ka_clipBoard as ka_clipBoard
import ka_maya.ka_pymel as ka_pymel
import ka_maya.ka_display as ka_display

CONTROLS_SET_NAME = 'ka_animation_controlsSet'
ANIMATION_FRAME_SET_PREFIX = 'ka_animation_frameSet_'
CURRENT_ANIMATION_FRAME_SET_ATTR_NAME = 'currentAnimationFrameSet'
DEFAULT_FRAME_STEP = 20

def getFrameRangeStart():
	return pymel.floatField('MayaWindow|toolBar5|MainPlaybackRangeLayout|formLayout10|floatField3', query=True, value=True)

def getFrameRangeEnd():
	return pymel.floatField('MayaWindow|toolBar5|MainPlaybackRangeLayout|formLayout10|floatField4', query=True, value=True)

def setFrameRangeStart(value):
	pymel.floatField('MayaWindow|toolBar5|MainPlaybackRangeLayout|formLayout10|floatField3', edit=True, value=value)
	mel.eval('setMinPlayback MayaWindow|toolBar5|MainPlaybackRangeLayout|formLayout10|floatField3;')
	#pymel.playbackOptions(min=1, max=3)

def setFrameRangeEnd(value):
	pymel.floatField('MayaWindow|toolBar5|MainPlaybackRangeLayout|formLayout10|floatField4', edit=True, value=value)
	mel.eval('setMaxPlayback MayaWindow|toolBar5|MainPlaybackRangeLayout|formLayout10|floatField4;')
	#pymel.playbackOptions(min=1, max=3)

def advanceNFrames(numberOfFrames=DEFAULT_FRAME_STEP):
	currentTime = pymel.currentTime( query=True )
	currentTime += numberOfFrames
	pymel.currentTime( currentTime )


def storeAllControls(allControls=None):
	if not allControls:
		allControls = pymel.ls(selection=True)

	if pymel.objExists(CONTROLS_SET_NAME):

		result = cmds.confirmDialog( title='Overwrite existing controls set?', message='Overwrite existing controls set?', button=['OK','Cancel'], defaultButton='Cancel', cancelButton='Cancel', dismissString='Cancel' )
		if result == 'OK':
			pymel.delete(CONTROLS_SET_NAME)
		else:
			return None

	controlSet = pymel.sets(allControls)
	controlSet.rename(CONTROLS_SET_NAME)
	controlSet.addAttr(CURRENT_ANIMATION_FRAME_SET_ATTR_NAME, at='message')

	#ka_clipBoard.add('allControls', allControls)

def addControlsToControlsSet(itemsToAdd=None):
	if not itemsToAdd:
		itemsToAdd = pymel.ls(selection=True)

	if not pymel.objExists(CONTROLS_SET_NAME):
		controlSet = pymel.sets(itemsToAdd)
		controlSet.rename(CONTROLS_SET_NAME)

	else:
		for item in itemsToAdd:
			if isinstance(item, pymel.nt.Transform):
				controlSet = pymel.sets(CONTROLS_SET_NAME, edit=True, addElement=item)

def removeControlsFromControlsSet(itemsToRemove=None):
	if not itemsToRemove:
		itemsToRemove = pymel.ls(selection=True)

	for item in itemsToRemove:
		if isinstance(item, pymel.nt.Transform):
			controlSet = pymel.sets(CONTROLS_SET_NAME, edit=True, remove=item)




def getAllControls():
	allControls = pymel.sets(CONTROLS_SET_NAME, query=True)
	#allControls = ka_clipBoard.get('allControls', [])
	return allControls


def selectAllControls():
	return pymel.select(getAllControls())


def keyAllControls():
	for control in getAllControls():
		if control:
			pymel.setKeyframe(control, shape=False)


def keyFrame1OnCurrentFrame():
	currentTime = pymel.currentTime( query=True )
	pymel.currentTime( 1 )
	pymel.currentTime( currentTime, update=False )
	keyAllControls()
	pymel.currentTime( currentTime )


def deleteAnimationOnAllControls():
	for control in getAllControls():
		if control:
			for attr in control.listAttr(keyable=True):
				inputs = attr.inputs()
				for input in inputs:
					nodeType = input.nodeType()
					if nodeType[:-1] == 'animCurveT':
						pymel.delete(input)


def storePose(poseName='default', space='local'):
	tPoseDict = {}

	for control in getAllControls():
		if control:
			if 'transform' in control.nodeType(inherited=True):
				controlMatrix = pymel.xform(control, query=True, matrix=True, objectSpace=True)
				tPoseDict[control] = controlMatrix


	ka_clipBoard.add('tPoseData', tPoseDict)


def getTPose(space='local'):
	return ka_clipBoard.get('tPoseData', {})


def applyPose(poseName='default'):
	tPoseDict = ka_clipBoard.get('tPoseData', [])
	for control in tPoseDict:
		matrix = tPoseDict[control]
		pymel.xform(control, matrix=matrix, objectSpace=True)


def storeNewAnimationFrameSet(setBaseName=None):
	if not setBaseName:
		result = cmds.promptDialog(
			title='Name Anim Set',
			message='Name for Anim Set:',
			button=['OK', 'Cancel'],
			defaultButton='OK',
			cancelButton='Cancel',
			dismissString='Cancel')

		if result == 'OK':
			setBaseName = cmds.promptDialog(query=True, text=True)
		else:
			return None

	selection = pymel.ls(selection=True)
	animSet = pymel.sets(selection)
	animSet.rename('%s%s' % (ANIMATION_FRAME_SET_PREFIX, setBaseName))

	animSet.addAttr('frameRangeStart', at='long')
	animSet.addAttr('frameRangeEnd', at='long')
	animationFrameSet_updateFrameRange(animSet)
	setAnimationFrameSet(animSet)

def getAllAnimationFrameSets():
	return pymel.ls('%s*' % ANIMATION_FRAME_SET_PREFIX)


def setAnimationFrameSet(animationFrameSet):
	# parse args
	if animationFrameSet == None:
		animationFrameSet = animationFrameSet_getCurrent()
	else:
		animationFrameSet = ka_pymel.getAsPyNodes(animationFrameSet)

	# isolate selection
	pymel.select(animationFrameSet.members())

	#animationFrameSet_updateFrameRange(animationFrameSet)
	start = animationFrameSet.frameRangeStart.get()
	end = animationFrameSet.frameRangeEnd.get()
	setFrameRangeStart(start)
	setFrameRangeEnd(end)

	# connect current sets message, which will be used to detirmine the current set
	controlSet = pymel.ls(CONTROLS_SET_NAME)[0]
	OOOOOOO = "controlSet"; print '%s: ' % OOOOOOO, eval(OOOOOOO), ' ', type(eval(OOOOOOO))
	animationFrameSet.message >> controlSet.attr(CURRENT_ANIMATION_FRAME_SET_ATTR_NAME)


def animationFrameSet_updateFrameRange(animationFrameSet=None):
	# parse args
	if animationFrameSet == None:
		animationFrameSet = animationFrameSet_getCurrent()
	else:
		animationFrameSet = ka_pymel.getAsPyNodes(animationFrameSet)

	# set frame range
	start = getFrameRangeStart()
	end = getFrameRangeEnd()
	animationFrameSet.frameRangeStart.set(start)
	animationFrameSet.frameRangeEnd.set(end)



def animationFrameSet_addItemsToSet(animationFrameSet=None, items=None):
	# parse args
	if animationFrameSet is None:
		animationFrameSet = animationFrameSet_getCurrent()
	else:
		animationFrameSet = ka_pymel.getAsPyNodes(animationFrameSet)

	if items is None:
		items = pymel.ls(selection=True)

	# add items
	animationFrameSet.addMembers(items)


def animationFrameSet_removeItemsFromSet(animationFrameSet=None, items=None):
	# parse args
	if animationFrameSet is None:
		animationFrameSet = animationFrameSet_getCurrent()
	else:
		animationFrameSet = ka_pymel.getAsPyNodes(animationFrameSet)

	if items is None:
		items = pymel.ls(selection=True)

	# add items
	animationFrameSet.removeMembers(items)


def animationFrameSet_setItemsOfSet(animationFrameSet=None, items=None):
	# parse args
	if animationFrameSet == None:
		animationFrameSet = animationFrameSet_getCurrent()
	else:
		animationFrameSet = ka_pymel.getAsPyNodes(animationFrameSet)

	if items == None:
		items = pymel.ls(selection=True)

	# clear and add new items
	animationFrameSet.clear()
	animationFrameSet.addMembers(items)


def animationFrameSet_getCurrent():
	controlSet = pymel.ls(CONTROLS_SET_NAME)
	if controlSet:
		controlSet = controlSet[0]
		currentAnimationFrameSet = controlSet.attr(CURRENT_ANIMATION_FRAME_SET_ATTR_NAME).inputs()
		if currentAnimationFrameSet:
			return currentAnimationFrameSet[0]


def insertFrames(numberOfFrames=DEFAULT_FRAME_STEP):
	currentTime = pymel.currentTime( query=True )

	for control in getAllControls():

		for keyframe in control.inputs(type='animCurve'):
			pymel.keyframe( keyframe, edit=True, relative=True, timeChange=numberOfFrames, time=(currentTime,999999999) )

	pymel.currentTime( currentTime+numberOfFrames )
	pymel.currentTime( currentTime, update=False )
	keyAllControls()
	pymel.currentTime( currentTime )


