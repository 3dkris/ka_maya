#====================================================================================
#====================================================================================
#
# ka_hotkeys
#
# DESCRIPTION:
#   sets up named commands and hotkeys based on the classes in the class "Hotkeys"
#
# DEPENDENCEYS:
#   none
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

"""
EXAMPLE:

import sys
paths = [
    r'K:\Repo\maya\python',
    r'K:\Repo\maya\ka',
    ]
for path in paths:
    if path not in sys.path:
        sys.path.append(path)

import ka_maya.ka_hotkeys as ka_hotkeys
import ka_global.hotkeys as hotkeys
reload(hotkeys)

import ka_global.reloadPackage as reloadPackage ;reload(reloadPackage) ;reload_package.reload_package()

ka_hotkeys.activateHotkey('all', hotkeyClass=hotkeys.LocalHotkeys)

"""
import os
import sys
import inspect
import pymel.core as pymel
import maya.cmds as cmds
import maya.mel as mel

import ka_util
import ka_transforms
import ka_weightPainting


import ka_maya.ka_core as ka_core
import ka_maya.ka_attrTool.ka_attrTool_UI as ka_attrTool_UI
import ka_maya.ka_advancedJoints as ka_advancedJoints
import ka_maya.ka_scrubSlider as ka_scrubSlider
import ka_maya.ka_display as ka_display
import ka_maya.ka_selection as ka_selection
import ka_maya.ka_context as ka_context
import ka_maya.ka_menuBase as ka_menuBase
import ka_maya.ka_menuWidget as ka_menuWidget
import ka_maya.ka_preference as ka_preference
import ka_maya.ka_python as ka_python

ka_menuObj = ka_menuBase.MenuBase()

def undoHandler(object):
    '''
    This Decorator Is Used To Handle Undo Stack.

    @param object: Python Object ( Object )
    @return: Python Function. ( Function )
    '''

    def undoHandlerCall(*args, **kwargs):
        '''
        This Decorator Is Used To Handle Undo Stack.

        @return: Python Object. ( Python )
        '''

        cmds.undoInfo(openChunk=True)
        value = object(*args, **ckwargs)
        cmds.undoInfo(closeChunk=True)

        return value

    return undoHandler

def get_window_state(window_name):
    if not cmds.window(window_name, q=1, exists=1):
        return False
    return cmds.window(window_name, q=1, vis=1)


def close_window(window_name):
    try:
        cmds.window(window_name, e=1, vis=0)

    except:
        pass

class undoable(object):

    def __init__(self, f):
        self.f = f

    def __call__(self):
        print "Entering", self.f.__name__
        pymel.undoInfo(openChunk=True)

        self.f()
        pymel.undoInfo(closeChunk=True)

        print "Exited", self.f.__name__



class echo(object):

    def __init__(self, function):
        self.function = function

    def __call__(self):
        print "Entering", self.function.__name__
        self.function()
        print "Exited", self.function.__name__


def getBaseClasses(obj):
    base_classes = [obj.__class__]
    class_stack = []
    for base_class in obj.__class__.__bases__:
        if base_class is not object:
            class_stack.append(base_class)

    while class_stack:
        base_class = class_stack.pop(0)

        if base_class not in base_classes:
            base_classes.append(base_class)

            sub_base_classes = list(base_class.__bases__)
            if sub_base_classes:
                for sub_base_class in sub_base_classes:
                    if sub_base_class not in class_stack:
                        class_stack.append(sub_base_class)

    return base_classes


class Hotkeys(object):

    """A collection of Classes, where each represents a hotkey and the command it should preform. While the structure of this
    class may not make much sense at first glace, it is very convenient way to oraganize, edit, read and define function code."""

    def __init__(self):
        """ sets up all sub classes of self as named commands and hotkeys"""
        self.listOfKeyBinds = self._get_keybind_classes()
        self.base_classes = self._get_base_classes()

    def _get_keybind_classes(self):
        #create list of classes within the current class "that do not start with '_'
        membersOfClass = inspect.getmembers(self)
        listOfKeyBinds = []
        for member in membersOfClass:
            #if class does not start with a '_', member is a tuple ie: ('a', <class ka_maya.hotkeys.a at 0x00000000321292B0>)
            if not member[0][0] == '_' and inspect.isclass(member[1]):
                listOfKeyBinds.append(member[1])    #store the acual method

        return listOfKeyBinds

    def _get_base_classes(self):
        base_classes = [self.__class__]
        class_stack = []
        for base_class in self.__class__.__bases__:
            if base_class is not object:
                class_stack.append(base_class)

        while class_stack:
            base_class = class_stack.pop(0)

            if base_class not in base_classes:
                base_classes.append(base_class)

                sub_base_classes = list(base_class.__bases__)
                if sub_base_classes:
                    for sub_base_class in sub_base_classes:
                        if sub_base_class not in class_stack:
                            if isinstance(sub_base_class, Hotkeys) or sub_base_class == Hotkeys:
                                class_stack.append(sub_base_class)

        return base_classes

    #--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#
    #--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#
    #--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#--#
    @classmethod
    def activateHotkey(hotkeyClass, hotkeyList, pushKey=None, alt=None, ctrl=None):
        """sets given hotkey to use the assosiated command from the Hotkeys class

        hotkeyList -- a list of class names to activate. ie: ['v', 'tilda']

        push key=None -- if activiating commands 1 at a time, you can use the pushKey, alt and ctrl
                         flags to map your own hotkey for the command
        """

        HotkeysClassObject = hotkeyClass()
        listOfKeyBinds = HotkeysClassObject.listOfKeyBinds
        keyBindsToActivate = []
        baseClasses = []

        if hotkeyList == 'all':
            keyBindsToActivate = HotkeysClassObject.listOfKeyBinds

        elif isinstance(hotkeyList, list):
            for each in listOfKeyBinds:
                if each.__name__ in hotkeyList:
                    keyBindsToActivate.append(each)

        elif isinstance(hotkeyList, str):
            for each in listOfKeyBinds:
                if each.__name__ == hotkeyList:
                    keyBindsToActivate = [each]

        currentPackageDir = '/'.join(__file__.split('/')[:-2])+'/'
        possiblePackageLocations = [currentPackageDir]

        sys_paths_strings = []
        for base_class in HotkeysClassObject._get_base_classes():
            modulePackagePath = os.path.dirname(sys.modules[base_class.__module__].__file__)
            modulePackagePath = os.path.split(modulePackagePath)[0]
            modulePackagePath = modulePackagePath.replace('\\','\\\\')    # this formatting is nessisary
            sys_paths_strings.append("r'{}'".format(modulePackagePath))

        sys_paths_string = ", ".join(sys_paths_strings)


        for keybind in keyBindsToActivate:

            nameCommandName = 'ka_%sNameCommand_' % keybind.__name__
            runtimeCommandName = 'ka_'+keybind.__name__

            nameCommandNameRelease = 'ka_%s_releaseNameCommand_' % keybind.__name__
            runtimeCommandNameRelease = 'ka_'+keybind.__name__+'_release'

            annotation = keybind.__name__
            releaseAnnotation = keybind.__name__+'_release'

            pythonCommandString = r"import sys, os; import maya.cmds as cmds; import pymel.core as pymel\nfor directory in [{}]:\n\tif directory not in sys.path: sys.path.append(directory)\nimport {}\n{}.{}.{}.command()".format(str(sys_paths_string), hotkeyClass.__module__, hotkeyClass.__module__, hotkeyClass.__name__, keybind.__name__)
            cmdString = r'python("%s")' % pythonCommandString

            cmdReleaseString = r'python("import ka_maya.ka_hotkeys ;ka_maya.ka_hotkeys.Hotkeys.{}.release_command()")'.format(keybind.__name__)

            # create the runtimeCommands for push and release...
            #...delete pre-existing
            if cmds.runTimeCommand(runtimeCommandName, q=True, exists=True):
                cmds.runTimeCommand(runtimeCommandName, e=True, delete=True)
            if cmds.runTimeCommand(runtimeCommandNameRelease, q=True, exists=True):
                cmds.runTimeCommand(runtimeCommandNameRelease, e=True, delete=True)

            #...add as runtime commands
            cmds.runTimeCommand(runtimeCommandName,
                                annotation=nameCommandName,
                                category='ka_hotkeys',
                                commandLanguage="mel",
                                command=(cmdString),
                                )

            cmds.runTimeCommand(runtimeCommandNameRelease,
                                annotation=nameCommandNameRelease,
                                category='ka_hotkeys',
                                commandLanguage="mel",
                                command=(cmdReleaseString),
                                )

            #create the nameCommands for push and release...
            cmds.nameCommand( nameCommandName, command=runtimeCommandName , annotation=annotation,)
            cmds.nameCommand( nameCommandNameRelease, command=runtimeCommandNameRelease  , annotation=releaseAnnotation,)

            # get key press for command
            if pushKey == None:
                eachPushKey = keybind.pushKey
            else:
                eachPushKey = pushKey

            if alt == None:
                eachAlt = keybind.alt
            else:
                eachAlt = alt

            if ctrl == None:
                eachCtrl = keybind.ctrl
            else:
                eachCtrl = ctrl

            # assign the name commands to hotkeys based on the variables in their corresponding method
            if cmds.hotkeyCheck( keyString=eachPushKey, altModifier=eachAlt, ctrlModifier=eachCtrl, ):
                cmds.hotkey(keyShortcut=eachPushKey, name='', altModifier=eachAlt, ctrlModifier=eachCtrl, )

            cmds.hotkey(keyShortcut=eachPushKey, name=nameCommandName, altModifier=eachAlt, ctrlModifier=eachCtrl, )

            if cmds.hotkeyCheck( keyString=eachPushKey, altModifier=eachAlt, ctrlModifier=eachCtrl, keyUp=True):
                cmds.hotkey(keyShortcut=eachPushKey, releaseName='', altModifier=eachAlt, ctrlModifier=eachCtrl, )

            cmds.hotkey(keyShortcut=eachPushKey, releaseName=nameCommandNameRelease, altModifier=eachAlt, ctrlModifier=eachCtrl, )


# A ######################################################################################################################
    class a():#keybind--------------------------------------------------------------------------
        pushKey='a';  ctrl=False;  alt=False;


        @staticmethod
        def command():
            context = ka_context.newContext()

            if cmds.currentCtx() == 'artAttrSkinContext':
                ka_weightPainting.toggleAddReplace()

            elif context.getUiTypeUnderMouse() == 'model':
                ka_display.addToIsolateSelect()

            elif context.getUiTypeUnderMouse() == 'hyperShade':
                melCmd = 'hyperShadePanelGraphCommand("%s", "addSelected");' % context.getPanelUnderMouse()
                mel.eval(melCmd)

        @staticmethod
        def release_command():
            pass

    class a_alt():#keybind--------------------------------------------------------------------------
        pushKey='a';  ctrl=False;  alt=True;

        @staticmethod
        def command():
            import ka_maya.ka_display as ka_display    #;reload(ka_display)

            panelUnderPointer = cmds.getPanel( underPointer=True )
            toolContext = cmds.currentCtx()

            if toolContext == 'artAttrSkinContext':
                ka_display.isolateSelection(mode='skinning')

            else:
                ka_display.isolateSelection()
        @staticmethod
        def release_command():
            pass


    class A():#keybind--------------------------------------------------------------------------
        pushKey='A';  ctrl=False;  alt=False;

        @staticmethod
        def command():
            context = ka_context.newContext()

            if context.getUiTypeUnderMouse() == 'model':
                ka_display.removeFromIsolateSelect()

            elif context.getUiTypeUnderMouse() == 'hyperShade':
                mel.eval(melCmd)

        @staticmethod
        def release_command():
            pass


    class a_ctrl():#keybind--------------------------------------------------------------------------
        pushKey='a';  ctrl=True;  alt=False;

        @staticmethod
        def command():
            ka_util.cycleAttributeEditorChannelBox()

        @staticmethod
        def release_command():
            pass

    class A_ctrl_alt():#keybind--------------------------------------------------------------------------
        pushKey='A';  ctrl=True;  alt=True;

        @staticmethod
        def command():
            cmds.evalDeferred('''import pymel.core as pymel \na = pymel.ls(selection=True)[0]\ns=pymel.ls(selection=True)''')

        @staticmethod
        def release_command():
            pass

# B ######################################################################################################################
    class b():#keybind--------------------------------------------------------------------------
        pushKey='b';  ctrl=False;  alt=False;

        @staticmethod
        def command():
            mel.eval('dR_DoCmd("softSelStickyPress")')

        @staticmethod
        def release_command():
            mel.eval('dR_DoCmd("softSelStickyRelease")')

# C ######################################################################################################################
    class c():#keybind--------------------------------------------------------------------------
        pushKey='c';  ctrl=False;  alt=False;

        @staticmethod
        def command():
            if ka_util.selectionIsComponent():
                ka_weightPainting.copyWeights()

            else:
                mel.eval('snapMode -curve 1')
            #if ka_util.selectionIsComponent():
                #ka_weightPainting.copyWeights()

        @staticmethod
        def release_command():
            mel.eval('snapMode -curve 0')

    class C():#keybind--------------------------------------------------------------------------
        pushKey='C';  ctrl=False;  alt=False;

        @staticmethod
        def command():
            if ka_util.selectionIsComponent():
                ka_weightPainting.pasteWeights()
        @staticmethod
        def release_command():
            pass

    class c_ctrl():#keybind--------------------------------------------------------------------------
        pushKey='c';  ctrl=True;  alt=False;

        @staticmethod
        def command():
            if ka_util.selectionIsComponent():
                ka_weightPainting.copyWeights()
            else:
                pass

        @staticmethod
        def release_command():
            pass

    class c_alt():#keybind--------------------------------------------------------------------------
        pushKey='c';  ctrl=False;  alt=True;

        @staticmethod
        def command():
            ka_transforms.snap(r=1)
#            if ka_util.selectionIsComponent():
#                ka_weightPainting.copyWeights()

        @staticmethod
        def release_command():
            pass

# D ######################################################################################################################
    class d_ctrl():#keybind--------------------------------------------------------------------------
        pushKey='d';  ctrl=True;  alt=False;

        @staticmethod
        def command():
            reload(ka_util)
            ka_util.contextDuplicate()

        @staticmethod
        def release_command():
            pass

    class D_ctrl():#keybind--------------------------------------------------------------------------
        pushKey='D';  ctrl=True;  alt=False;

        @staticmethod
        def command():
            cmds.delete(constructionHistory=True,)

        @staticmethod
        def release_command():
            pass


# E ######################################################################################################################
    class e():#keybind--------------------------------------------------------------------------
        pushKey='e';  ctrl=False;  alt=False;

        @staticmethod
        def command():
            mel.eval('buildRotateMM')

        @staticmethod
        def release_command():
            mel.eval('destroySTRSMarkingMenu RotateTool')


    class e_alt():#keybind--------------------------------------------------------------------------
        pushKey='e';  ctrl=False;  alt=True;

        @staticmethod
        def command():
            script_editor_window = "scriptEditorPanel1Window"
            script_editor_state = get_window_state(script_editor_window)
            if script_editor_state:
                close_window(script_editor_window)
            else:
                mel.eval('tearOffPanel "Script Editor" "scriptEditorPanel" true;')

        @staticmethod
        def release_command():
            pass

    class e_ctrl_alt():#keybind--------------------------------------------------------------------------
        pushKey='e';  ctrl=True;  alt=True;

        @staticmethod
        def command():
            script_editor_window = "componentEditorPanel1Window"
            script_editor_state = get_window_state(script_editor_window)
            if script_editor_state:
                close_window(script_editor_window)
            else:
                mel.eval('tearOffPanel "Component Editor" "componentEditorPanel" true;')

        @staticmethod
        def release_command():
            pass

    class E():#keybind--------------------------------------------------------------------------
        pushKey='E';  ctrl=False;  alt=False;

        @staticmethod
        def command():
#            ka_util.selectEdgeLoopFromVertSelection()
            mel.eval('SelectEdgeLoopSp;')

        @staticmethod
        def release_command():
            pass

# F ######################################################################################################################
    class f():#keybind--------------------------------------------------------------------------
        pushKey='f';  ctrl=False;  alt=False;

        @staticmethod
        def command():
            #if cmds.currentCtx() == 'artAttrSkinContext':
                #ka_weightPainting.focusOnInfluence()
            #else:
            mel.eval('fitPanel -selected')

        @staticmethod
        def release_command():
            pass

    class f_ctrl():#keybind--------------------------------------------------------------------------
        pushKey='f';  ctrl=True;  alt=False;

        @staticmethod
        def command():
            import ka_filterSelection ;reload(ka_filterSelection)
            ka_filterSelection.openUI()

        @staticmethod
        def release_command():
            pass

# G ######################################################################################################################
    class g_alt():#keybind--------------------------------------------------------------------------
        pushKey='g';  ctrl=False;  alt=True;

        @staticmethod
        def command():
            #ka_util.modelFilterGeoOnly(filterList=['nurbsSurfaces', 'polymeshes'])
            mel.eval("SetMeshSculptTool")

        @staticmethod
        def release_command():
            pass


# H ######################################################################################################################
    class h():#keybind--------------------------------------------------------------------------
        pushKey='h';  ctrl=False;  alt=False;

        @staticmethod
        def command():
            if ka_util.selectionIsComponent():

                ka_weightPainting.copyWeights()
                ka_menu.press(buildMenuOverride='paintPallet', sliderMode='pasteWeights')


        @staticmethod
        def release_command():
            ka_menu.release(sliderMode='pasteWeights')

    class h_alt():#keybind--------------------------------------------------------------------------
        pushKey='h';  ctrl=False;  alt=True;

        @staticmethod
        def command():
            mel.eval('hotkeyEditor')

        @staticmethod
        def release_command():
            pass
# I ######################################################################################################################
    class i_alt():#keybind--------------------------------------------------------------------------
        pushKey='i';  ctrl=False;  alt=True;

        @staticmethod
        def command():
            #mel.eval('ka_invertSelectionOrder')
            ka_util.reverseSelectionOrder()
        @staticmethod
        def release_command():
            pass

    class i_ctrl():#keybind--------------------------------------------------------------------------
        pushKey='i';  ctrl=True;  alt=False;

        @staticmethod
        def command():
            mel.eval('projectViewer Import; checkForUnknownNodes()')

        @staticmethod
        def release_command():
            pass

# K ######################################################################################################################
    class k():#keybind--------------------------------------------------------------------------
        pushKey='k';  ctrl=False;  alt=False;

        @staticmethod
        def command():
            mel.eval('performSetKeyframeArgList 1 {"0", "animationList"}')
            #reload(ka_advancedJoints)
            #ka_advancedJoints.setKeyframes()

        @staticmethod
        def release_command():
            pass

    class K():#keybind--------------------------------------------------------------------------
        pushKey='K';  ctrl=False;  alt=False;

        @staticmethod
        def command():
            reload(ka_util)
            ka_util.setKeyframes()

        @staticmethod
        def release_command():
            pass

    class k_alt():#keybind--------------------------------------------------------------------------
        pushKey='k';  ctrl=False;  alt=True;

        @staticmethod
        def command():
            mel.eval('tearOffPanel "Graph Editor" "graphEditor" true;')

        @staticmethod
        def release_command():
            pass

# N ######################################################################################################################
    class n():#keybind--------------------------------------------------------------------------
        pushKey='n';  ctrl=False;  alt=False;

        @staticmethod
        def command():
##            ka_util.toggleRotationAxis()
            ka_display.toggleRotationAxis()

        @staticmethod
        def release_command():
            ka_util.objectSelectMode(release=True)

    class n_alt():#keybind--------------------------------------------------------------------------
        pushKey='n';  ctrl=False;  alt=True;

        @staticmethod
        def command():
            selection = cmds.ls(selection=True)
            shapes = cmds.listRelatives( shapes=True, path=True)

            if shapes:
                shapeType = cmds.nodeType(shapes[0])
                if shapeType == 'mesh':
                    mel.eval('ToggleFaceNormalDisplay;')


        @staticmethod
        def release_command():
            ka_util.objectSelectMode(release=True)

# M ######################################################################################################################
    class m_alt():#keybind--------------------------------------------------------------------------
        pushKey='m';  ctrl=False;  alt=True;

        @staticmethod
        def command():
            if ka_util.selectionIsComponent():
                mel.eval('polyMergeToCenter')
            else:
                reload(ka_util)
                ka_transforms.snap(m=1)

        @staticmethod
        def release_command():
            pass

# O ######################################################################################################################
    class o_alt():#keybind--------------------------------------------------------------------------
        pushKey='o';  ctrl=False;  alt=True;

        @staticmethod
        def command():
            window = "outlinerPanel1Window"
            state = get_window_state(window)
            if state:
                close_window(window)

            else:
                mel.eval('tearOffPanel "Outliner" "outlinerPanel" false;')

        @staticmethod
        def release_command():
            pass

# P ######################################################################################################################
    class p_alt():#keybind--------------------------------------------------------------------------
        pushKey='p';  ctrl=False;  alt=True;

        @staticmethod
        def command():
            print cmds.getPanel(underPointer=True)

        @staticmethod
        def release_command():
            pass




# Q ######################################################################################################################
    class q():#keybind--------------------------------------------------------------------------
        pushKey='q';  ctrl=False;  alt=False;

        @staticmethod
        def command():
            ka_util.objectSelectMode()

        @staticmethod
        def release_command():
            ka_util.objectSelectMode(release=True)

    class q_alt():#keybind--------------------------------------------------------------------------
        pushKey='q';  ctrl=False;  alt=True;

        @staticmethod
        def command():
            ka_util.componentSelectMode()
            mel.eval('global string $gSelect; setToolTo $gSelect;')
        @staticmethod
        def release_command():
            pass

    class Q_alt():#keybind--------------------------------------------------------------------------
        pushKey='Q';  ctrl=False;  alt=True;

        @staticmethod
        def command():
            selection = pymel.ls(selection=True)
            ka_util.componentSelectMode()
            mel.eval('global string $gSelect; setToolTo $gSelect;')
            pymel.select(selection)

        @staticmethod
        def release_command():
            pass

    class q_ctrl():#keybind--------------------------------------------------------------------------
        pushKey='q';  ctrl=True;  alt=False;

        @staticmethod
        def command():
            mel.eval('artSelectToolScript 4')

        @staticmethod
        def release_command():
            mel.eval('artSelectToolScript 3')

    class Q():#keybind--------------------------------------------------------------------------
        pushKey='Q';  ctrl=False;  alt=False;

        @staticmethod
        def command():
            mel.eval('artSelectToolScript 4')
            ka_display.updateIsolateSelection()

        @staticmethod
        def release_command():
            #mel.eval('artSelectToolScript 3')
            pass
# R ######################################################################################################################
    class r_ctrl():#keybind--------------------------------------------------------------------------
        pushKey='r';  ctrl=True;  alt=False;

        @staticmethod
        def command():
            import ka_maya.ka_rename; reload(ka_maya.ka_rename)
            ka_maya.ka_rename.openUI()

        @staticmethod
        def release_command():
            pass

    class r_alt():#keybind--------------------------------------------------------------------------
        pushKey='r';  ctrl=False;  alt=True;

        @staticmethod
        def command():
            mel.eval('ReferenceEditor;')

        @staticmethod
        def release_command():
            pass

    class R_ctrlAlt():#keybind--------------------------------------------------------------------------
        pushKey='R';  ctrl=True;  alt=True;

        @staticmethod
        def command():
            ka_util.openLastScene()

        @staticmethod
        def release_command():
            pass

# S ######################################################################################################################
    class s():#keybind--------------------------------------------------------------------------
        pushKey='s';  ctrl=False;  alt=False;

        @staticmethod
        def command():
            panelUnderPointer = cmds.getPanel( underPointer=True )

            #reload(ka_menu_modelEditor)
            #ka_menu.press()
            if cmds.currentCtx() == 'artAttrSkinContext':
                ka_weightPainting.toggleSmooth()
                #mel.eval('ka_MM_toggleSmooth;')

            #elif 'modelPanel' in panelUnderPointer and ka_util.selectionIsComponent():
                #ka_weightPainting.pasteWeights()

            else:
                mel.eval('ka_snapScaleAndRotate();')
                mel.eval('ka_hgInputsOutputs();')

        @staticmethod
        def release_command():
            #ka_menu.release()
            pass
            mel.eval('ka_snapScaleAndRotate_release();')


    class s_alt():#keybind--------------------------------------------------------------------------
        pushKey='s';  ctrl=False;  alt=True;

        @staticmethod
        def command():

            mel.eval('tearOffPanel "Hypershade" "hyperShadePanel" true;')
            mel.eval('hyperShadePanelMenuCommand("hyperShadePanel1", "showBottomTabsOnly");')
            mel.eval('hyperShadePanelMenuCommand("hyperShadePanel1", "toggleRenderCreateBar");')

            #mel.eval('ka_hyperGraphMM();')

        @staticmethod
        def release_command():
            pass

    class S_ctrl():#keybind--------------------------------------------------------------------------
        pushKey='S';  ctrl=True;  alt=False;

        @staticmethod
        def command():

            mel.eval('checkForUnknownNodes(); projectViewer SaveAs')

        @staticmethod
        def release_command():
            pass

# T ######################################################################################################################
    class t():#keybind--------------------------------------------------------------------------
        pushKey='t';  ctrl=False;  alt=False;

        @staticmethod
        def command():
            reload(ka_scrubSlider)
            ka_scrubSlider.timeSliderScrub()

        @staticmethod
        def release_command():
            #ka_scrubSlider.release()
            pass

    class T():#keybind--------------------------------------------------------------------------
        pushKey='T';  ctrl=False;  alt=False;

        @staticmethod
        def command():
            mel.eval('''string $sel[] = `ls -sl`; if ( size($sel) > 0 ) {
string $nodesInDAG[] = `ls -dag -shapes $sel[0]`;
if ( size($nodesInDAG) > 0 ) {
if ( `nodeType $nodesInDAG[0]` == "rnkLight" ) { select $nodesInDAG[0]; }
}
}
setToolTo ShowManips''')

        @staticmethod
        def release_command():
            pass


    class t_alt():#keybind--------------------------------------------------------------------------
        pushKey='t';  ctrl=False;  alt=True;

        @staticmethod
        def command():
            mel.eval('if (`scriptedPanel -q -exists scriptEditorPanel1`) { scriptedPanel -e -to scriptEditorPanel1; showWindow scriptEditorPanel1Window; selectCurrentExecuterControl; }else { CommandWindow; };')

        @staticmethod
        def release_command():
            pass


# V ######################################################################################################################
    class v():#keybind--------------------------------------------------------------------------
        pushKey='v';  ctrl=False;  alt=False;

        @undoable
        def command():
            context = ka_context.Context()

            if not 'moveSuperContext' == cmds.currentCtx():
                if cmds.currentCtx() == 'artAttrSkinContext':
                    ka_menu.press(buildMenuOverride='paintPallet',)

                elif context.selectionIncludesComponents() and context.selectionIncludesSkinnedGeo():
                    reload(ka_scrubSlider)
                    ka_scrubSlider.weight_parallelBlend_Scrub()

                else:
                    print '<not skinned>'
                    mel.eval('snapMode -point 1;')
            else:
                mel.eval('snapMode -point 1;')

        @staticmethod
        def release_command():
            mel.eval('snapMode -point 0;')


    class V():#keybind--------------------------------------------------------------------------
        pushKey='V';  ctrl=False;  alt=False;

        @staticmethod
        def command():
            #reload(ka_scrubSlider)
            ka_scrubSlider.weight_strandBlend_Scrub()
            #ka_menu.press(buildMenuOverride='paintPallet', sliderMode='pasteWeights')

        @staticmethod
        def release_command():
            pass
            #ka_menu.release(sliderMode='pasteWeights')


    class v_alt():#keybind--------------------------------------------------------------------------
        pushKey='v';  ctrl=False;  alt=True;

        @staticmethod
        def command():
            if ka_util.selectionIsComponent() or cmds.currentCtx() == 'artAttrSkinContext':
#                ka_menu.press(buildMenuOverride='paintPallet', sliderMode='blendWeights')
                ka_menu.press(buildMenuOverride='paintPallet', sliderMode='pasteWeights')

            else:
                ka_transforms.snap(t=1)

        @staticmethod
        def release_command():
#            ka_menu.release(sliderMode='blendWeights')
            #ka_menu.release(sliderMode='pasteWeights')
            pass

    class v_ctrl():#keybind--------------------------------------------------------------------------
        pushKey='v';  ctrl=True;  alt=False;

        @staticmethod
        def command():
            #ka_menu.press(buildMenuOverride='paintPallet', sliderMode='pasteWeights')
            #ka_weightPainting.pasteAveragedWeights()
            ka_core.pasteWeights()

        @staticmethod
        def release_command():
            pass

    class V_ctrl():#keybind--------------------------------------------------------------------------
        pushKey='V';  ctrl=True;  alt=False;

        @staticmethod
        def command():

            #ka_core.pasteSkinWeightsAlongStrand()
            scrubSlider = ka_scrubSlider.weight_strandBlend_Scrub(visible=False)
            scrubSlider.finish()


        @staticmethod
        def release_command():
            pass

# W ######################################################################################################################
    class W():#keybind--------------------------------------------------------------------------
        pushKey='W';  ctrl=False;  alt=False;

        @staticmethod
        def command():
            ka_display.toggleWireframeOnShaded()

        @staticmethod
        def release_command():
            pass

    class w_ctrl():#keybind--------------------------------------------------------------------------
        pushKey='w';  ctrl=True;  alt=False;

        @staticmethod
        def command():
            ka_core.ka_selection.pickWalk('next')

        @staticmethod
        def release_command():
            pass

    class W_ctrl():#keybind--------------------------------------------------------------------------
        pushKey='W';  ctrl=True;  alt=False;

        @staticmethod
        def command():
            ka_display.toggleWireframeOnSelected()

        @staticmethod
        def release_command():
            pass

    class w_alt():#keybind--------------------------------------------------------------------------
        pushKey='w';  ctrl=False;  alt=True;

        @staticmethod
        def command():
            #mel.eval('artAttrSkinToolScript 4')
            ka_weightPainting.paint()
            ka_display.updateIsolateSelection()

        @staticmethod
        def release_command():
            #mel.eval('artAttrSkinToolScript 3')
            pass


# X ######################################################################################################################
    class x():#keybind--------------------------------------------------------------------------
        pushKey='x';  ctrl=False;  alt=False;

        @staticmethod
        def command():
            context = ka_context.newContext()

            #if cmds.currentCtx() == 'artAttrSkinContext' or cmds.currentCtx() == 'artAttrContext':
            if context.weightPainting():
                ka_weightPainting.togglePaint()

            else:
                ka_display.xRayMode()
                mel.eval('snapMode -grid 1;')


        @staticmethod
        def release_command():
            if not cmds.currentCtx() == 'artAttrSkinContext':
                ka_display.xRayMode(False)
                ka_display.jointXRayMode(False)

            mel.eval('snapMode -grid 0;')

    class X():#keybind--------------------------------------------------------------------------
        pushKey='X';  ctrl=False;  alt=False;

        @staticmethod
        def command():
            ka_display.jointXRayMode()
            #mel.eval('string $currentPanel = `getPanel -withFocus`; modelEditor -e -jointXray (!`modelEditor -q -jointXray $currentPanel`) $currentPanel;')

        @staticmethod
        def release_command():
            pass

    class X_ctrl():#keybind--------------------------------------------------------------------------
        pushKey='X';  ctrl=True;  alt=False;

        @staticmethod
        def command():
            pass
        @staticmethod
        def release_command():
            pass

    class x_ctrl():#keybind--------------------------------------------------------------------------
        pushKey='x';  ctrl=True;  alt=False;

        @staticmethod
        def command():
            ka_display.xRayMode()


        @staticmethod
        def release_command():
            pass

    class x_alt():#keybind--------------------------------------------------------------------------
        pushKey='x';  ctrl=False;  alt=True;

        @staticmethod
        def command():
            ka_transforms.snap(s=1)

        @staticmethod
        def release_command():
            pass
# Z ######################################################################################################################
    class Z_ctrl():#keybind--------------------------------------------------------------------------
        pushKey='Z';  ctrl=True;  alt=False;

        @staticmethod
        def command():
            ka_util.resetAttrs()

        @staticmethod
        def release_command():
            pass

    class z_alt():#keybind--------------------------------------------------------------------------
        pushKey='z';  ctrl=False;  alt=True;

        @staticmethod
        def command():
            reload(ka_util)
            ka_transforms.snap(a=1)

        @staticmethod
        def release_command():
            pass
# DOWN ######################################################################################################################
    class DOWN():#keybind--------------------------------------------------------------------------
        pushKey='DOWN';  ctrl=False;  alt=False;

        @staticmethod
        def command():
            ka_selection.pickWalk('down')

        @staticmethod
        def release_command():
            pass

    class DOWN_ctrl():#keybind--------------------------------------------------------------------------
        pushKey='DOWN';  ctrl=True;  alt=False;

        @staticmethod
        def command():
            ka_selection.pickWalk('down', additive=True)

        @staticmethod
        def release_command():
            pass

    class DOWN_alt():#keybind--------------------------------------------------------------------------
        pushKey='DOWN';  ctrl=False;  alt=True;

        @staticmethod
        def command():
            cmds.select(hierarchy=True)

        @staticmethod
        def release_command():
            pass
# UP ######################################################################################################################
    class UP():#keybind--------------------------------------------------------------------------
        pushKey='UP';  ctrl=False;  alt=False;

        @staticmethod
        def command():
            ka_selection.pickWalk('up' )

        @staticmethod
        def release_command():
            pass

    class UP_ctrl():#keybind--------------------------------------------------------------------------
        pushKey='UP';  ctrl=True;  alt=False;

        @staticmethod
        def command():
            ka_selection.pickWalk('up', additive=True)

        @staticmethod
        def release_command():
            pass
# RIGHT ######################################################################################################################
    class RIGHT():#keybind--------------------------------------------------------------------------
        pushKey='RIGHT';  ctrl=False;  alt=False;

        @staticmethod
        def command():
            ka_selection.pickWalk('right' )

        @staticmethod
        def release_command():
            pass

    class RIGHT_ctrl():#keybind--------------------------------------------------------------------------
        pushKey='RIGHT';  ctrl=True;  alt=False;

        @staticmethod
        def command():
            ka_selection.pickWalk('right', additive=True)

        @staticmethod
        def release_command():
            pass

# LEFT ######################################################################################################################
    class LEFT():#keybind--------------------------------------------------------------------------
        pushKey='LEFT';  ctrl=False;  alt=False;

        @staticmethod
        def command():
            ka_selection.pickWalk('left' )

        @staticmethod
        def release_command():
            pass

    class LEFT_ctrl():#keybind--------------------------------------------------------------------------
        pushKey='LEFT';  ctrl=True;  alt=False;

        @staticmethod
        def command():
            ka_selection.pickWalk('left', additive=True)


        @staticmethod
        def release_command():
            pass

# insert ######################################################################################################################
    class insert_alt():#keybind--------------------------------------------------------------------------
        pushKey='insert';  ctrl=False;  alt=True;

        @staticmethod
        def command():
            ka_util.editRotationAxis()

        @staticmethod
        def release_command():
            pass

# tilda(`) ######################################################################################################################
    class tilda():#keybind--------------------------------------------------------------------------
        pushKey='`';  ctrl=False;  alt=False;

        @staticmethod
        def command():
            if ka_menuWidget.getAllUnpinnedKaMenuWidgets():
                ka_menuWidget.clearAllKaMenuWidgets(unpinnedOnly=True)

            else:
                ka_menuObj.popMenu()

        @staticmethod
        def release_command():
            pass
            #ka_menu.release()

    class tilda_ctrl():#keybind--------------------------------------------------------------------------
        pushKey='`';  ctrl=True;  alt=False;

        @staticmethod
        def command():
            pass

        @staticmethod
        def release_command():
            pass

    class tilda_alt():#keybind--------------------------------------------------------------------------
        pushKey='`';  ctrl=False;  alt=True;

        @staticmethod
        def command():
            ka_menuWidget.clearAllKaMenuWidgets(unpinnedOnly=False)

        @staticmethod
        def release_command():
            pass

    class tilda_ctrl_alt():#keybind--------------------------------------------------------------------------
        pushKey='`';  ctrl=True;  alt=True;

        @staticmethod
        def command():
            tweakManipState = ka_preference.get('tweakManipState', False)
            if tweakManipState:
                mel.eval('dR_DoCmd("tweakRelease")')
                ka_preference.set('tweakManipState', False)
            else:
                mel.eval('dR_DoCmd("tweakPress")')
                ka_preference.set('tweakManipState', True)

        @staticmethod
        def release_command():
            pass


# \ ######################################################################################################################
    class forwardslash_ctrl():#keybind--------------------------------------------------------------------------
        pushKey='\\';  ctrl=True;  alt=False;

        @staticmethod
        def command():
            mel.eval('setToolTo polySplitContext')

        @staticmethod
        def release_command():
            mel.eval('setToolTo polySplitContext ; toolPropertyWindow')

    class forwardslash():#keybind--------------------------------------------------------------------------
        pushKey='\\';  ctrl=False;  alt=False;

        @staticmethod
        def command():
            mel.eval('polySelectEditCtx -e -mode 1 polySelectEditContext; setToolTo polySelectEditContext')

        @staticmethod
        def release_command():
            mel.eval('polySelectEditCtx -e -mode 1 polySelectEditContext; setToolTo polySelectEditContext; toolPropertyWindow')

# 1 ######################################################################################################################
    class one():#keybind--------------------------------------------------------------------------
        pushKey='1';  ctrl=False;  alt=False;

        @staticmethod
        def command():
            ka_util.setTransformManipulatorMode('world')

        @staticmethod
        def release_command():
            pass


# 2 ######################################################################################################################
    class two():#keybind--------------------------------------------------------------------------
        pushKey='2';  ctrl=False;  alt=False;

        @staticmethod
        def command():
            ka_util.setTransformManipulatorMode('local')

        @staticmethod
        def release_command():
            pass

# 3 ######################################################################################################################
    class three():#keybind--------------------------------------------------------------------------
        pushKey='3';  ctrl=False;  alt=False;

        @staticmethod
        def command():
            ka_util.setTransformManipulatorMode('trueValues')

        @staticmethod
        def release_command():
            pass

# ! ######################################################################################################################
    class exclamation():#keybind--------------------------------------------------------------------------
        pushKey='!';  ctrl=False;  alt=False;

        @staticmethod
        def command():
            mel.eval('setDisplaySmoothness 1')

        @staticmethod
        def release_command():
            pass


# @ ######################################################################################################################
    class addressSign():#keybind--------------------------------------------------------------------------
        pushKey='@';  ctrl=False;  alt=False;

        @staticmethod
        def command():
            mel.eval('setDisplaySmoothness 2')

        @staticmethod
        def release_command():
            pass

# # ######################################################################################################################
    class pound():#keybind--------------------------------------------------------------------------
        pushKey='#';  ctrl=False;  alt=False;

        @staticmethod
        def command():
            mel.eval('setDisplaySmoothness 3')

        @staticmethod
        def release_command():
            pass

# = ######################################################################################################################
    class equals():#keybind--------------------------------------------------------------------------
        pushKey='=';  ctrl=True;  alt=False;

        @staticmethod
        def command():
            mel.eval('PolySelectTraverse 1')

        @staticmethod
        def release_command():
            pass


    class equals_ctrl():#keybind--------------------------------------------------------------------------
        pushKey='+';  ctrl=True;  alt=False;

        @staticmethod
        def command():
            import ka_maya.ka_selection as ka_selection; reload(ka_selection)
            ka_selection.islandSelectComponents()

        @staticmethod
        def release_command():
            pass








