#====================================================================================
#====================================================================================
#
# ka_python
#
# DESCRIPTION:
#   general tools related to working in python
#
# DEPENDENCEYS:
#   Maya
#   Pymel
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

import traceback


def getItems(inputObject):
    """takes an object that may be a collection of collections and returns
    a list of all the sigular items within it"""
    items = []
    if isinstance(inputObject, dict):
        for key in inputObject:
            value = inputObject[key]
            items.extend(getItems(value))

    elif isinstance(inputObject, list):
        for item in inputObject:
            items.extend(getItems(item))

    else:
        items = [inputObject]

    return items


def printError():
    print '\nSCRIPT STACK------------------------------------------'
    traceback.print_stack()

    print 'ERROR ------------------------------------------------'
    traceback.print_exc()
    print '\n'


def getInput(label='Enter Text'):
    print label
    inputValue = raw_input()
    return inputValue
