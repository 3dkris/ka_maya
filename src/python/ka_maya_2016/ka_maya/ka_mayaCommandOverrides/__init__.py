#====================================================================================
#====================================================================================
#
# __init__ of mayaCommandOverrides
#
# DESCRIPTION:
#   will source all mel scripts in the version subfolders, overriding the original
#   maya mel command
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

import os
import maya.cmds as cmds
import maya.mel as mel
import re

import ka_maya.ka_python as ka_python


def cleanPath(path):
    normalPath = os.path.normpath(path)
    fowardSlashPath = re.sub(r'\\', '/', normalPath)
    return fowardSlashPath



currentDirectory = cleanPath(os.path.dirname(__file__))
subfolders = os.walk(currentDirectory).next()[1]
version = cmds.about(version=True)

#get the folder that represents the current version
currentVersionFolder = []
for folder in subfolders:
    if str(folder) in version:
        currentVersionFolder.append(cleanPath(os.path.join(currentDirectory, folder)))

#make sure that there is only 1 folder for current version
if not len(currentVersionFolder) == 1:
    if len(currentVersionFolder) == 0:
        print '!! Warning no version folder found for current version of maya in ka_maya/ka_mayaCommandOverrides'
    else:
        print '!! Warning too many version folders found for current version of maya in ka_maya/ka_mayaCommandOverrides'


else:
    #get list of file which are .mel
    melScriptFiles = []
    for file in os.listdir(currentVersionFolder[0]):
        if file[-4:] == '.mel':
            melScriptFiles.append(cleanPath(os.path.join(currentVersionFolder[0], file)))

    #and finally source them
    for filePath in melScriptFiles:
        try:
            mel.eval('source "'+filePath+'"')

        except:
            print "FAILED TO LOAD MEL FILE: %s" % filePath
            ka_python.printError()




