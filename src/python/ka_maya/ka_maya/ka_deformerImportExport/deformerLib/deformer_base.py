#====================================================================================
#====================================================================================
#
# ka_maya.ka_deformerImportExport.deformerLib.deformer_base
#
# DESCRIPTION:
#   the base class for deformer import export classes
#
# DEPENDENCEYS:
#   ka_maya.ka_deformerImportExport
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
import ast
import pprint

import pymel.core as pymel
import maya.cmds as cmds
import maya.mel as mel

import ka_maya.ka_deformers as ka_deformers
import ka_maya.ka_pymel as ka_pymel

class Deformer(object):
    def __init__(self, **kwargs):
        self.deformer = kwargs.get('deformer', None)
        self.deformerName = kwargs.get('deformerName', None)
        self.nodeType = kwargs.get('nodeType', None)
        self.deformerSet = kwargs.get('deformerSet', None)
        self.deformedNodes = kwargs.get('deformedNodes', None)
        self.deformedComponents = kwargs.get('deformedComponents', None)

        if self.deformer:
            self.deformerName = self.deformer.nodeName(stripNamespace=True)
            self.nodeType = self.deformer.nodeType()
            self.deformerSet = ka_deformers.getDeformerSet(self.deformer)
            self.deformedNodes = ka_deformers.getDeformedComponents(self.deformer, nodesOnly=True, deformerSet=self.deformerSet)
            self.deformedComponents = ka_deformers.getDeformedComponents(self.deformer, deformerSet=self.deformerSet)
        OOOOOOO = "kwargs"; print '%s: ' % OOOOOOO, eval(OOOOOOO), ' ', type(eval(OOOOOOO))

    def getKwargs(self):
        kwargs = {}
        kwargs['deformerName'] = self.deformerName
        kwargs['deformedComponents'] = self.deformedComponents
        kwargs['deformedNodes'] = self.deformedNodes
        kwargs['nodeType'] = self.nodeType

        return kwargs



    def export(self, exportDir):
        # do automatic renames on shapes
        for deformedNode in self.deformedNodes:
            transform = deformedNode.getParent()
            transformName = transform.nodeName(stripNamespace=True)
            for shape in transform.getShapes(noIntermediate=True):
                try:
                    shape.rename('%sShape' % transformName)
                except: pass

        # do automatic renames on deformers
        if self.deformerName.startswith(self.nodeType):
            if len(self.deformedNodes) == 1:
                transformName = deformedNode.getParent().nodeName(stripNamespace=True)
                newName = '%s_%s' % (transformName, self.nodeType)
                try:
                    self.deformer.rename(newName)
                    self.deformerSet.rename('%sSet' % newName)
                except: pass


        outKwargs = self.getKwargs()
        outKwargs = ka_pymel.getAsStrings(outKwargs)

        # write kwargs file
        kwargFile = os.path.join(exportDir, 'kwargs.py')
        with open(kwargFile, 'wt') as f:
            pprint.pprint(outKwargs, stream=f)

    def import_(self, deformerPath, optimized=False):
        print 'IMPORT YEA!'


