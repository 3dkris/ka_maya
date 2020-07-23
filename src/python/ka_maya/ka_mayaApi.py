#====================================================================================
#====================================================================================
#
# ka_mayaApi
#
# DESCRIPTION:
#   tools related to maya Api
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

from traceback import format_exc as printError

import maya.cmds as cmds
import maya.mel as mel
import pymel.core as pymel
import maya.OpenMaya as OpenMaya
import math


import ka_maya.ka_pymel as ka_pymel
import ka_maya.ka_deformers as ka_deformers


def getAttrDefaultValue(attr):
    """Returns the default value of the given compound/array attribute"""

    mobj = attr.__apimobject__()

    mFnNumericAttribute = OpenMaya.MFnNumericAttribute(mobj)
    mScriptUtil = OpenMaya.MScriptUtil()
    floatPtrA = mScriptUtil.asFloatPtr()
    mFnNumericAttribute.getDefault(floatPtrA)
    floatPtrB = OpenMaya.MScriptUtil(floatPtrA)
    defaultValue = floatPtrB.asFloat()
    return defaultValue

