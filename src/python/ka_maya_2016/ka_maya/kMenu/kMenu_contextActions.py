
#====================================================================================
#====================================================================================
#
# kMenu_contextActions
#
# DESCRIPTION:
#   actions which are highly variable based on the context in which they are called
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


import pymel.core as pymel
import maya.cmds as cmds
import maya.mel as mel

import ka_maya.ka_context as ka_context    #;reload(ka_context)

#class ContextActionObject(object):
    #"""A decorator that creates a ContextAction from a function"""

    #def __init__(self, label='', icon=None, docFunc=None):
        #self.label = label
        #self.icon = icon
        #self.docFunc = docFunc

    #def __call__(self, f):
        ##print 'tool __call__'

        #toolObject = ToolObject(label=self.label, function=f, icon=self.icon, docFunc=self.docFunc)
        #return toolObject

#class ContextAction(object):
    #"""A decorator that creates a ContextAction from a function"""

    #def __init__(self, label='', icon=None, docFunc=None):
        #self.label = label
        #self.icon = icon
        #self.docFunc = docFunc

    #def __call__(self, f):
        #contextActionObject = ContextActionObject(label=self.label, function=f, icon=self.icon, docFunc=self.docFunc)
        #return contextActionObject

##def context_objectUnderMouse()

#@ContextAction(visibleContext=None):
#def printObjUnderMouse():
    #print ka_context.Context().getPanelUnderMouse()