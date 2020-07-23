#====================================================================================
#====================================================================================
#
# ka_reload
#
# DESCRIPTION:
#   reloads all modules in ka_maya
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
import sys

import pymel.core as pymel
import maya.cmds as cmds
import maya.mel as mel


# PYTHON MODULES (IN ORDER) ####################################################
PACKAGE_RELOADERS = []
MODULES = []
add = MODULES.append

# low level ------------------------------------------------------------------------------------------------------------------------------
import ka_maya                                                                                       ;add(ka_maya)
import ka_maya.ka_python as ka_python                                                                ;add(ka_python)
import ka_maya.ka_pymel as ka_pymel                                                                  ;add(ka_pymel)
import ka_maya.ka_mayaCommandOverrides as ka_mayaCommandOverrides                                    ;add(ka_mayaCommandOverrides)
import ka_maya.ka_mayaApi as ka_mayaApi                                                              ;add(ka_mayaApi)
import ka_maya.ka_preference as ka_preference                                                        ;add(ka_preference)
import ka_maya.ka_context as ka_context                                                              ;add(ka_context)


# mid level ------------------------------------------------------------------------------------------------------------------------------
import ka_maya.ka_math as ka_math                                                                    ;add(ka_math)
import ka_maya.ka_naming as ka_naming                                                                ;add(ka_naming)


# standard level -------------------------------------------------------------------------------------------------------------------------
import ka_maya.ka_animation as ka_animation                                                          ;add(ka_animation)
import ka_maya.ka_attrTool.attrCommands as attrCommands                                              ;add(attrCommands)
import ka_maya.ka_attrTool.attrFavorites as attrFavorites                                            ;add(attrFavorites)
import ka_maya.ka_attrTool.attributeObj as attributeObj                                              ;add(attributeObj)
import ka_maya.ka_attr as ka_attr                                                                    ;add(ka_attr)
import ka_maya.ka_deformers as ka_deformers                                                          ;add(ka_deformers)
import ka_maya.ka_deformerImportExport.ka_deformerImportExport as ka_deformerImportExport            ;add(ka_deformerImportExport)
import ka_maya.ka_deformerImportExport.deformerLib.deformer_base as ka_deformer_base                 ;add(ka_deformer_base)
import ka_maya.ka_deformerImportExport.deformerLib.deformer_skinCluster as ka_deformer_skinCluster   ;add(ka_deformer_skinCluster)

import ka_maya.ka_clipBoard as ka_clipBoard                                                          ;add(ka_clipBoard)
import ka_maya.ka_controls as ka_controls                                                            ;add(ka_controls)
import ka_maya.ka_display as ka_display                                                              ;add(ka_display)
import ka_maya.ka_cameras as ka_cameras                                                              ;add(ka_cameras)
import ka_maya.ka_rigAerobics as ka_rigAerobics                                                      ;add(ka_rigAerobics)
import ka_maya.ka_rigQuery as ka_rigQuery                                                            ;add(ka_rigQuery)
import ka_maya.ka_rigSetups.ka_advancedFK as ka_advancedFK                                           ;add(ka_advancedFK)
import ka_maya.ka_selection as ka_selection                                                          ;add(ka_selection)
import ka_maya.ka_shapes as ka_shapes                                                                ;add(ka_shapes)
import ka_maya.ka_skinCluster as ka_skinCluster                                                      ;add(ka_skinCluster)
import ka_maya.ka_transforms as ka_transforms                                                        ;add(ka_transforms)
import ka_maya.ka_util as ka_util                                                                    ;add(ka_util)
import ka_maya.ka_weightBlender as ka_weightBlender                                                  ;add(ka_weightBlender)
import ka_maya.ka_weightPainting as ka_weightPainting                                                ;add(ka_weightPainting)
import ka_maya.ka_nurbsRigging as ka_nurbsRigging                                                    ;add(ka_nurbsRigging)
import ka_maya.ka_geometry as ka_geometry                                                            ;add(ka_geometry)
import ka_maya.ka_rename as ka_rename                                                                ;add(ka_rename)

import ka_maya.ka_psd as ka_psd
import ka_maya.ka_filterSelection as ka_filterSelection                                              ;add(ka_filterSelection)


# UI Modules ------------------------------------------------------------------------------------------------------------------------------
import ka_maya.ka_qtWidgets as ka_qtWidgets                                                          ;add(ka_qtWidgets)
import ka_maya.ka_attrTool.ka_attrTool_UI as ka_attrTool_UI                                          ;add(ka_attrTool_UI)
import ka_maya.ka_stopwatchTool.commands as ka_stopwatchToolCommands                                 ;add(ka_stopwatchToolCommands)
import ka_maya.ka_stopwatchTool.ui as ka_stopwatchToolUi                                             ;add(ka_stopwatchToolUi)
import ka_maya.ka_scrubSlider as ka_scrubSlider                                                      ;add(ka_scrubSlider)
import ka_maya.ka_menuWidget as ka_menuWidget                                                        ;add(ka_menuWidget)


import ka_maya.ka_core as ka_core                                                                    ;add(ka_core)
import ka_maya.ka_menuBase as ka_menuBase                                                            ;add(ka_menuBase)
import ka_maya.ka_hotkeys as ka_hotkeys                                                              ;add(ka_hotkeys)


def reload_package():
    """Call this function to reload package"""
    for package_reloader in PACKAGE_RELOADERS:
        reload(package_reloader)
        package_reloader.reload_package()

    message = '>> Reloading KA_MAYA'
    print message, '='*(80-len(message))

    for module in MODULES:
        reload(module)

def get_previous_modified_time():
    previous_modified_time = 0
    for module in MODULES:
        modified_time = os.stat(module.__file__)[8]
        if modified_time > previous_modified_time:
            previous_modified_time = modified_time
    return previous_modified_time


def has_changed(previous_modified_time):
    result = False
    for module in MODULES:
        modified_time = os.stat(module.__file__)[8]
        result = result or ( modified_date <= previous_lastest_change )
    return result