#====================================================================================
#====================================================================================
#
# hotkeys
#
# DESCRIPTION:
#   sets up named commands and hotkeys based on the classes in the class "Hotkeys"
#
# DEPENDENCEYS:
#   ka_maya
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
import sys

import maya.cmds as cmds
import pymel.core as pymel

import ka_maya.ka_hotkeys as ka_hotkeys
import ka_maya.ka_menuWidget as ka_menuWidget

import ka_maya_local.menus as menus
import ka_maya_local.core as core

class Hotkeys(ka_hotkeys.Hotkeys):

    """A collection of Classes, where each represents a hotkey and the command it should preform. While the structure of this
    class may not make much sense at first glace, it is very convenient to edit, read and define function code."""

# TILDA ########################################################################
    class tilda():#keybind------------------------------------------------------
        pushKey='`';  ctrl=False;  alt=False;

        @staticmethod
        def command():
            if ka_menuWidget.getAllUnpinnedKaMenuWidgets():
                ka_menuWidget.clearAllKaMenuWidgets(unpinnedOnly=True)

            else:
                menus.ka_menu.popMenu()

        @staticmethod
        def release_command():
            pass

    class tilda_ctrl():#keybind--------------------------------------------------
        pushKey='`';  ctrl=True;  alt=False;

        @staticmethod
        def command():
            ka_menuWidget.clearAllKaMenuWidgets(unpinnedOnly=False)

            try:
                import ka_maya_local.reload_package as reload_package; reload(reload_package)
                reload_package.reload_package()
            except:
                reload_package.reload_package()

        @staticmethod
        def release_command():
            pass

# R ############################################################################
    class r_ctrl():#keybind-----------------------------------------------------
        pushKey='r';  ctrl=True;  alt=False;

        @staticmethod
        def command():
            #import something; reload(something)
            core.exampleTool()

        @staticmethod
        def release_command():
            pass

