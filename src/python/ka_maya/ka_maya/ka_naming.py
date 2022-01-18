#====================================================================================
#====================================================================================
#
# ka_naming
#
# DESCRIPTION:
#   A module for naming nodes
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

import string

import pymel.core as pymel
import maya.cmds as cmds
import maya.mel as mel

import ka_maya.ka_pymel as ka_pymel; reload(ka_pymel)


# the get name function will be different depending on the naming convertions of
# the enviroment.
#try:

    #import common.nameUtils as nameUtils
    #def getName(node, baseName=None, index=-1, side="C", **kwargs):

        #nodeType = node.nodeType()
        #if nodeType not in nameUtils.knownNodeTypes:
            #nodeType = 'multiplyDivide'

        #if not index:
            #index = -1

        ##if name:
            ##name = name.replace('_', '')

        #if baseName:
            #baseName= baseName.replace('_', '')

        #OOOOOOO = "baseName"; print '%s: ' % OOOOOOO, eval(OOOOOOO), ' ', type(eval(OOOOOOO))
        #OOOOOOO = "nodeType"; print '%s: ' % OOOOOOO, eval(OOOOOOO), ' ', type(eval(OOOOOOO))
        #OOOOOOO = "side"; print '%s: ' % OOOOOOO, eval(OOOOOOO), ' ', type(eval(OOOOOOO))
        #OOOOOOO = "name"; print '%s: ' % OOOOOOO, eval(OOOOOOO), ' ', type(eval(OOOOOOO))
        #OOOOOOO = "index"; print '%s: ' % OOOOOOO, eval(OOOOOOO), ' ', type(eval(OOOOOOO))
        #newName = nameUtils.getName(baseName=baseName,
                                    #nodeType=nodeType,
                                    #side=side,
                                    #padding=2,
                                    ##extra=name,
                                    #index=index,
                                    #)
        #return newName

#except:
def getName(node, name='', index='', side='', grouping='', nodePurpose='', **kwargs):

    # name
    if name == '':
        name = node.nodeType()

    # index
    if index != '':
        #index = string.ascii_uppercase[index]
        index = str(index)
        while len(index) < 2:
            index = '0%s' % index
        index = '_'+index

    # side
    if side == 'l':
        side = 'l_'
    elif side == 'r':
        side = 'r_'
    else:
        side = ''

    if grouping:
        grouping = '%s_' % grouping


    # nodePurpose
    if nodePurpose:
        if nodePurpose == 'control':
            nodePurpose = '_ctl'

        if nodePurpose == 'zeroOutGroup':
            nodePurpose = '_zro'

        if nodePurpose == 'offsetGroup':
            nodePurpose = '_ofs0'

        if nodePurpose == 'group':
            nodePurpose = '_grp'

        if nodePurpose == 'joint':
            nodePurpose = '_jnt'


    # order
    newName = '%(side)s%(grouping)s%(name)s%(index)s%(nodePurpose)s' % locals()
    return newName



def setName(node, **kwargs):
    newName = getName(node, **kwargs)

    # rename
    node.rename(newName)

    # rename shapes
    try:
        shapes = node.getShapes()
        for i, shape in enumerate(shapes):
            if i == 0:
                shape.rename(newName+'Shape')
            else:
                shape.rename('%sShape%s' % (newName, str(i)))
    except:
        pass




def getOppositeNode(node):
    nodeName = ka_pymel.getAsStrings(node)
    oppositeName = getOppositeFromName(nodeName)
    if oppositeName:
        oppositeNodes = pymel.ls(oppositeName)
        if oppositeNodes:
            if len(oppositeNodes) == 1:
                return oppositeNodes[0]

            else:
                pymel.error('more than one object named: %s' % oppositeName)


def getOppositeFromName(nodeName):
    """Returns the name of the assumed opposite control if one can be found"""
    sideInfo = _getSideInfo(nodeName)
    side = sideInfo.get('side', None)
    if side:
        if side in ['l', 'r']:
            return sideInfo['oppositeName']





sideDict = {'l':'l',
            'r':'r',
            'c':'c',
            'left':'l',
            'right':'r',
            'center':'c',
           }


oppositesDict = {'l':'r',
                 'r':'l',
                 'c':'c',
                 'left':'right',
                 'right':'left',
                 'center':'center',
                }

def _getSideInfo(name):

    def _sameName(name):
        return name

    def _upperName(name):
        return name.upper()

    def _lowerName(name):
        return name.lower()

    def _upperFirstLetter(name):
        return name[0].upper() + name[1:]

    sideInfo = {}

    for sideKey in sideDict:
        side = sideDict[sideKey]

        keyModifications = [_sameName, _upperName, _lowerName,]
        if len(sideKey) > 1:
            keyModifications.append(_upperFirstLetter)

        # is a single side representation
        for keyModification in keyModifications: # check a number of possible variations of the key
            matchString = keyModification(sideKey) # string to search for in name

            if name == matchString:
                sideInfo['side'] = side
                sideInfo['sideString'] = matchString
                sideInfo['positionInName'] = 'is'

                sideInfo['oppositeSide'] = oppositesDict[side]
                sideInfo['oppositeSideString'] = keyModification(oppositesDict[sideKey])
                sideInfo['oppositeName'] = name.replace(sideInfo['sideString'], sideInfo['oppositeSideString'])

                return sideInfo

        # starts with keys
        startsWithString = '%s_' # format to search for

        for keyModification in keyModifications: # check a number of possible variations of the key
            matchString = startsWithString % keyModification(sideKey) # string to search for in name

            if name.startswith(matchString):

                sideInfo['side'] = side
                sideInfo['sideString'] = matchString
                sideInfo['positionInName'] = 'startswith'

                sideInfo['oppositeSide'] = oppositesDict[side]
                sideInfo['oppositeSideString'] = startsWithString % keyModification(oppositesDict[sideKey])
                sideInfo['oppositeName'] = name.replace(sideInfo['sideString'], sideInfo['oppositeSideString'])

                return sideInfo



        # ends with keys
        endsWithString = '_%s' # format to search for

        for keyModification in keyModifications: # check a number of possible variations of the key
            matchString = endsWithString % keyModification(sideKey) # string to search for in name

            if name.endswith(matchString):

                sideInfo['side'] = side
                sideInfo['sideString'] = matchString
                sideInfo['positionInName'] = 'endswith'

                sideInfo['oppositeSide'] = oppositesDict[side]
                sideInfo['oppositeSideString'] = endsWithString % keyModification(oppositesDict[sideKey])
                sideInfo['oppositeName'] = name.replace(sideInfo['sideString'], sideInfo['oppositeSideString'])

                return sideInfo


        # key is in name
        inNameString = '_%s_' # format to search for

        for keyModification in keyModifications: # check a number of possible variations of the key
            matchString = inNameString % keyModification(sideKey) # string to search for in name

            if matchString in name:

                sideInfo['side'] = side
                sideInfo['sideString'] = matchString
                sideInfo['positionInName'] = 'inname'

                sideInfo['oppositeSide'] = oppositesDict[side]
                sideInfo['oppositeSideString'] = inNameString % keyModification(oppositesDict[sideKey])
                sideInfo['oppositeName'] = name.replace(sideInfo['sideString'], sideInfo['oppositeSideString'])

                return sideInfo

    return sideInfo



def removeSelectedNameSpace():
    selection = cmds.ls(sl=1)
    if not selection == None:
        if selection:
            for name in selection:
                if cmds.objExists(name):
                    ns = getNamespace(name)
                    deleteNS(ns)


def deleteNS(nmSpace, removeContent = 0):
    """Find an object with the given name within a namespace

@param nmSpace : string, namespace to remove
@param removeContent : bool, whether or not to remove the content of the namespace

@return None

@code
from common import namespaceUtils
namespaceUtils.deleteNS( namespaceUtils.getNamespace(pymel.selected()[0]) )
@endcode
    """
    if len(nmSpace):
        if not removeContent: cmds.namespace(force=True,mv=(nmSpace,":"))
        c

def getNamespace(inputObj, fullPath = 0):
    """Get obj namespace

@param inputObj : string / PyNode, the object you want to get the namespace of

@return string, object namespace ("None" if root)

@code
from common import namespaceUtils
namespaceUtils.getNamespace(pymel.selected()[0])
@endcode
    """
    inputObjBK = inputObj
    try:
        inputObj = convertUnitUtils.returnPyNode(inputObj)
    except:
        pymel.system.error("[ namespaceUtils ] getNamespace - Invalid inputObj \"" + inputObjBK + "\"")

    nameSpace = None

    if len(inputObj.longName())>0:
        if not fullPath:
            namespaceList = inputObj.longName().split(":")
            if len(namespaceList) > 1:
                nameSpace = namespaceList[-2].split("|")[-1]
            else:
                nameSpace = ":"
        else:
            namespaceParts = inputObj.split(":")
            if len(namespaceParts)>1:
                namespaceParts.pop(len(namespaceParts)-1)
                fullPathNamespace = ":".join(namespaceParts)
                nameSpace = ":" + fullPathNamespace
            else:
                nameSpace = ":"

    return nameSpace