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

import pymel.core as pymel
import maya.cmds as cmds
import maya.mel as mel

print 'ka_maya reloaded'
def initialize():
    print 'ka_maya initialized'

    loadPlugins()



def getPluginPaths():
    ka_mayaDir = os.path.abspath(os.path.dirname(__file__))
    pluginsDir = os.path.abspath(os.path.join(ka_mayaDir, "ka_plugins",))

    files = os.listdir(pluginsDir)

    pluginPaths = []
    for fileName in files:
        if fileName.endswith('.py'):
            pluginPaths.append(os.path.join(pluginsDir, fileName,))

    return pluginPaths

def loadPlugins():
    for pluginPath in getPluginPaths():
        print '  loading', pluginPath
        cmds.loadPlugin(pluginPath)