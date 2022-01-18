    #====================================================================================
#====================================================================================
#
# ka_attr
#
# DESCRIPTION:
#   Functions to manipulate maya attributes
#
# DEPENDENCEYS:
#   -Maya
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

import ka_maya.ka_pymel as ka_pymel    #;reload(ka_python)
import ka_maya.ka_python as ka_python    #;reload(ka_python)
import ka_maya.ka_context as ka_context    #;reload(ka_context)
import ka_maya.ka_attrTool.attrCommands as attrCommands

HEADER_LENGTH = 30

def addSeparatorAttr(node):
    node = ka_pymel.getAsPyNodes(node)
    attrName = '_'
    while pymel.attributeQuery(attrName, node=node, exists=True):
        attrName += '_'

    #node.addAttr(attrName, at='enum', enumName=' ', niceName='-'*HEADER_LENGTH, keyable=True)
    node.addAttr(attrName, at='enum', enumName=' ', niceName=' '*HEADER_LENGTH, keyable=True)
    #node.attr(attrName).set(lock=True)
    node.attr(attrName).set(keyable=False, channelBox=True)


def addHeaderAttr(node, header):
    node = ka_pymel.getAsPyNodes(node)

    addSeparatorAttr(node)

    #niceNameParts = ('-- ', header.replace('_', ' '), ' --')
    niceNameParts = ('------  ', header.replace('_', ' '),)
    headerNiceName = ''.join(niceNameParts)
    node.addAttr(header, at='enum', enumName='------', niceName=headerNiceName, keyable=True)
    #node.attr(header).set(lock=True)
    node.attr(header).set(keyable=False, channelBox=True)

def addEnumValue(enumAttr, enumLabel):
    attrCommands.addEnumValue(enumAttr, enumLabel)