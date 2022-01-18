#====================================================================================
#====================================================================================
#
# ka_rigQuery
#
# DESCRIPTION:
#   collection of small scripts that inspect rigs, and return information about them
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

import inspect
import math
from traceback import format_exc as printError

import pymel.core as pymel
import maya.cmds as cmds
import maya.mel as mel

import ka_math                                        #;reload(ka_math)
import ka_transforms                                  #;reload(ka_transforms)
import ka_preference                               #;reload(ka_preference)






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

def getSideFromName(node):
    """Returns 'l', 'r', or 'c' based on the nodes name"""

    nodeName = node
    sideInfo = _getSideInfo(nodeName)
    return sideInfo.get('side', 'c')


def getOppositeFromName(node):
    """Returns the name of the assumed opposite control if one can be found"""
    nodeName = node
    sideInfo = _getSideInfo(nodeName)
    side = sideInfo.get('side', None)
    if side:
        if side in ['l', 'r']:
            return sideInfo['oppositeName']

def _getSideInfo(name):
    """Returns a dictionary with the following info about side (as derrived from name)
       sideInfo = {'side':              'l'
                   'sideString':        '_l_'
                   'positionInName':    'inname'
                   'oppositeSide':      'r'
                   'oppositeSideString: '_r_'
                   'oppositeName':      'ik_arm_r_ctrl'
                  }
    """

    def _sameName(name):
        return name

    def _upperName(name):
        return name.upper()

    def _lowerName(name):
        return name.lower()

    def _upperFirstLetter(name):
        upper = name[0].upper() + name[1:]
        return upper

    sideInfo = {}

    for sideKey in sideDict:
        side = sideDict[sideKey]

        keyModifications = [_sameName, _upperName, _lowerName,]
        if len(sideKey) > 1:
            keyModifications.append(_upperFirstLetter)

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


        if len(sideKey) > 1:
            # starts with keys
            startsWithString = '%s' # format to search for

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
            endsWithString = '%s' # format to search for

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
            inNameString = '%s' # format to search for

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
