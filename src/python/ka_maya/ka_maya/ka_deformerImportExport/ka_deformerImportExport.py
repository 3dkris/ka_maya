#====================================================================================
#====================================================================================
#
# ka_maya.ka_deformerImportExport.ka_deformerImportExport
#
# DESCRIPTION:
#   a general type for deformer import export
#
# DEPENDENCEYS:
#   ka_maya.ka_deformers
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
import time
import importlib
import ast
import pprint
import shutil

import pymel.core as pymel
import maya.mel as mel
import maya.cmds as cmds

import ka_maya.ka_deformerImportExport.deformerLib.deformer_base as deformer_base

import ka_maya.ka_geometry as ka_geometry
import ka_maya.ka_deformers as ka_deformers
import ka_maya.ka_python as ka_python
import ka_maya.ka_pymel as ka_pymel

DEFORMER_SUFFIX = '____deformer'
DEFORMER_ORDER_SUFFIX = '____deformationOrder.py'

TEMP_DIR = cmds.internalVar(userTmpDir=True)
DEFORMER_LIB_DIR = os.path.join(os.path.split(__file__)[0], 'deformerLib')

log = 1
def getTempDeformersDir(emptyDir=False):
    dirPath = os.path.join(TEMP_DIR, 'TEMP_ka_deformerImportExportDir')
    OOOOOOO = "dirPath"; print '%s: ' % OOOOOOO, eval(OOOOOOO), ' ', type(eval(OOOOOOO))

    if emptyDir:
        try:
            shutil.rmtree(dirPath)
        except:
            pass

        #for item in os.listdir(dirPath):
            #try:
                #os.remove(os.path.join(dirPath, item))
            #except Exception, e:
                #print e

    try: os.mkdir(dirPath)
    except: pass

    return dirPath

def clearTempDeformersDir():
    tempDeformerDir = getTempDeformersDir(emptyDir=True)


def exportAllDeformers(saveDirectory=None, **kwargs):
    if saveDirectory is None:
        saveDirectory = getTempDeformersDir(emptyDir=True)

    allDeformedShapes = ka_deformers.getAllDeformedShapes()
    exportDeformeredObjects(allDeformedShapes, saveDirectory=saveDirectory, **kwargs)


def exportDeformersOfSelected(saveDirectory=None, **kwargs):
    """export to directory the deformers deforming the selected geometry"""
    exportDeformeredObjects(saveDirectory=saveDirectory)

def importDeformersToSelected(deformerDirectory=None, **kwargs):
    """export to directory the deformers deforming the selected geometry"""

    selection = pymel.ls(selection=True)
    deformedComponents = []
    deformedNodes = []

    for item in selection:
        if ka_pymel.isPyComponent(item):
            deformedComponents.append(item)
            deformedNodes.append(item.node())

        elif ka_pymel.isPyTransform(item):
            shape = item.getShape()
            components = ka_geometry.getComponents(shape)
            deformedComponents.extend(components)
            deformedNodes.append(shape)

        elif ka_pymel.isPyShape(item):
            shape = item
            components = ka_geometry.getComponents(shape)
            deformedComponents.extend(components)
            deformedNodes.append(shape)

    importAllDeformers(deformerDirectory=deformerDirectory, deformedComponents=deformedComponents,
                       deformedNodes=deformedNodes)
    #importDeformer(deformerPath)


def exportDeformeredObjects(deformedItems=None, saveDirectory=None, **kwargs):
    # parse args
    if saveDirectory is None:
        deformerDirectory = getTempDeformersDir()
    if deformedItems is None:
        deformedItems = pymel.ls(selection=True)

    deformerOrderDirectory = os.path.join(deformerDirectory, 'deformationOrder')

    try: os.mkdir(deformerOrderDirectory);
    except: pass

    skipDeformers = kwargs.get('skipDeformers', [])

    # export deformed items
    allDeformers = []
    for shape in deformedItems:
        deformers = ka_deformers.getDeformers(shape)

        #create deformationOrder file for each mesh with deformers
        if deformers:
            duplicateNamesCheck = pymel.ls(shape.nodeName())
            if len(duplicateNamesCheck) > 1:
                pymel.warning('DUPLICATE NAMES exist in the scene for the item (%s) being exported' % shape.nodeName())


            #string buffer to align nodeType commented column
            maxStringLen = 0
            for deformer in deformers:
                stringLen = len(deformer.nodeName())
                if stringLen > maxStringLen:
                    maxStringLen = int(stringLen)

            # write to file
            deformerOrderFilePath = os.path.abspath('%s/%s' % (deformerOrderDirectory, getDeformationOrderFileName(shape)))
            with open(deformerOrderFilePath, 'w') as f:
                f.write('[\n')
                for deformer in reversed(deformers):
                    stringLen = len(deformer.nodeName())
                    spaceBuffer = maxStringLen - stringLen + 4
                    f.write("'%s',%s# nodeType: %s\n" % (deformer.nodeName(), ' '*spaceBuffer, pymel.nodeType(deformer)))
                f.write(']')


        for deformer in deformers:
            if deformer not in allDeformers:
                allDeformers.append(deformer)


    # create deformer files
    for deformer in allDeformers:
        if skipDeformers:
            if deformer not in skipDeformers:
                exportDeformer(deformer, deformerDirectory)

        else:
            exportDeformer(deformer, deformerDirectory)



def exportDeformer(deformer, deformerDirectory):
    nodeType = deformer.nodeType()

    # get/make deformer type dir
    deformerTypeDir = os.path.join(deformerDirectory, nodeType)
    try: os.mkdir(deformerTypeDir);
    except: pass

    # get/make deformer export dir
    exportDir = os.path.join(deformerTypeDir, deformer.nodeName(stripNamespace=True))
    try: os.mkdir(exportDir);
    except: pass

    startTime = time.clock()
    deformerObj = getDeformerObj(deformer)
    deformerObj.export(exportDir)


def importAllDeformers(deformerDirectory=None, **kwargs):
    if deformerDirectory is None:
        deformerDirectory = getTempDeformersDir()

    listOfFiles = []

    for subDirName in os.listdir(deformerDirectory):
        subDirPath = os.path.join(deformerDirectory, subDirName)
        for fileName in os.listdir(subDirPath):
            filePath = os.path.join(subDirPath, fileName)
            pass

            listOfFiles.append(filePath)

    importDeformers(listOfFiles, **kwargs)

def importListOfDeformerFiles(listOfFiles, **kwargs):
    print '\n\n#- -#- -#- -#- -#- -#- -#- -#- -#- -#- -#- -#- -#- -#- -#- -#- -#- -#- -#- -#- -#- -#- -#- -#- -#- -#- -#- -#- -#- '
    print r"""   /   \___ / _| ___  _ __ _ __ ___   ___ _ __ ___  / _\ |_ __ _ _ __| |_                   #   #
  / /\ / _ \ |_ / _ \| '__| '_ ` _ \ / _ \ '__/ __| \ \| __/ _` | '__| __|                  #   #
 / /_//  __/  _| (_) | |  | | | | | |  __/ |  \__ \ _\ \ || (_| | |  | |_                   #   #
/___,' \___|_|  \___/|_|  |_| |_| |_|\___|_|  |___/ \__/\__\__,_|_|   \__|                  #   #
#- -#- -#- -#- -#- -#- -#- -#- -#- -#- -#- -#- -#- -#- -#- -#- -#- -#- -#- -#- -#- -#- -#- -#- -#- -#- -#- -#- -#-"""
    print ''

    startTime = time.clock()

    startDeferredDeformerLoadFile()

    importDeformers(listOfFiles, **kwargs)

    print '\n#- -#- -#- -#- -#- -#- -#- -#- -#- -#- -#- -#- -#- -#- -#- -#- -#- -#- -#- -#- -#- -#- -#- -#- -#- -#- -#- -#- -#- '
    print '#-  Finished loading deformers in: %s seconds   #' % str((time.clock() - startTime))
    print '#- -#- -#- -#- -#- -#- -#- -#- -#- -#- -#- -#- -#- -#- -#- -#- -#- -#- -#- -#- -#- -#- -#- -#- -#- -#- -#- -#- -#-\n\n'


def importDeformers(listOfPaths, **kwargs):
    """main call, it exports the given nodes, or if none given will export selected objects
    arg[0:-1] - nodes to export
    arg[-1]   - path to export to
    """
    pathDict = {}
    for path in listOfPaths:
        baseName = os.path.basename(path)
        pathDict[baseName] = path

    inclusionList = kwargs.get('inclusionList', [])

    allDeformerPackages = []
    allDeformationOrderFiles = []
    deformerPath_dictionary = {}

    for path in listOfPaths:

        if path.endswith(DEFORMER_ORDER_SUFFIX):
            allDeformationOrderFiles.append(path)

        #if eachFilePath.endswith(DEFORMER_SUFFIX):
        elif os.path.isdir(path):
            allDeformerPackages.append(path)

            # the keys of this dictionary are the deformer names, and the values
            # are the true file paths. This allows file lists with files from various
            # directorys to be passed in. This should be queried when opening a deformer file
            deformerName = os.path.basename(path)
            #eachDeformerName = eachFileName.split(DEFORMER_SUFFIX)[0]
            deformerPath_dictionary[deformerName] = path



    listOf_deformedObjectsInfo = []
    listOf_deformedObjectsInfo_toLoad = []
    for deformationOrderFilePath in allDeformationOrderFiles:
        deformationOrderFileName = os.path.basename(deformationOrderFilePath)
        #deformerDirectory = os.path.split(eachFilePath)[0]

        with open(deformationOrderFilePath, 'r') as f:
            dataString = f.read()
            deformationOrder = ast.literal_eval(dataString)


        # prune tweaks and other unspecified deformers and populate a list of tuples
        # where item 1 is a deformer and item 2 is a list of objects that deformer deforms
        prunedDeformationOrderPairs = []
        for deformer in deformationOrder:
            # does deformer have a deformer file in the deformer file dictionary?
            if deformer in deformerPath_dictionary:
                deformerPath = deformerPath_dictionary[deformer]

                if deformerPath in allDeformerPackages:
                    with open(os.path.join(deformerPath, 'kwargs.py'), 'r') as f:
                        dataString = f.read()
                        deformerKwargs = ast.literal_eval(dataString)
                    deformedObjects = deformerKwargs['deformedNodes']
                    prunedDeformationOrderPairs.append((deformer, deformedObjects))

        shape = deformationOrderFileName.split(DEFORMER_ORDER_SUFFIX)[0]
        dataPair = [shape, prunedDeformationOrderPairs]

        # the inclusion list if for loading a selected few deformers
        if inclusionList:
            if shape in inclusionList:
                listOf_deformedObjectsInfo_toLoad.append(tuple(dataPair))

        else:
            listOf_deformedObjectsInfo_toLoad.append(tuple(dataPair))

        listOf_deformedObjectsInfo.append(tuple(dataPair))

    OOOOOOO = "listOf_deformedObjectsInfo_toLoad"; print '%s: ' % OOOOOOO, eval(OOOOOOO), ' ', type(eval(OOOOOOO))
    cA = 0
    # WHILE THERE ARE MESHS TO LOAD DEFORMERS ON
    while listOf_deformedObjectsInfo_toLoad:
        cA += 1
        if cA > 9999:
            pymel.error('while loop A max limit hit')
            break


        deformedObjectInfo = listOf_deformedObjectsInfo_toLoad[0]
        deformedObject, listOf_deformersAndDeformedObjects = deformedObjectInfo
        if log:print '~',
        if log:print deformedObject

        cB = 0
        #WHILE THERE ARE DEFORMERS TO LOAD
        while listOf_deformersAndDeformedObjects:
            cB += 1
            if cB > 9999:
                pymel.error('while loop B  max limit hit')
                break


            deformerAndDeformedObjects = listOf_deformersAndDeformedObjects[0]
            deformer, deformedObjects = deformerAndDeformedObjects
            if log:print '    deformer:',
            if log:print deformer

            deformerPackage = deformerPath_dictionary[deformer]

            #CAN WE LOAD? CHECK HERE
            unloadableFlag = False
            for deformedObject in deformedObjects:
                if inclusionList:
                    if deformedObject not in inclusionList:
                        unloadableFlag = True

            if unloadableFlag:
                if log:print '        %s will never be ready to load because it deformes objects that are not in the selection' % deformer
                break

            if isDeformerReadyToLoad(deformer, listOf_deformedObjectsInfo):

                listOf_deformersAndDeformedObjects.pop(0)

                try:
                    importDeformer(deformerPackage, **kwargs)

                except:
                    ka_python.printError()
                    print '            failed to load deformer because of a code error (seek help) %s' % deformer

            else:
                listOf_deformersAndDeformedObjects.append(listOf_deformersAndDeformedObjects.pop(0))
                break

        listOf_deformedObjectsInfo_toLoad.pop(0)


def isDeformerReadyToLoad(deformerToLoad, listOf_deformedObjectsInfo):
    """Returns True if all conditions to load that deformer are met. This check determins the
    order that deformers are loaded (especially important in cases where a deformer has multiple objects
    in its deformer set)"""

    listOf_deformedObjectsInfo_usingDeformerToLoad = []
    for i, each in enumerate(listOf_deformedObjectsInfo):

        shape, listOf_deformerTuples = each

        listOf_deformers = []
        for deformer, deformedObjects in listOf_deformerTuples:
            listOf_deformers.append(deformer)

        if deformerToLoad in listOf_deformers:
            listOf_deformedObjectsInfo_usingDeformerToLoad.append(each)


    for shape, listOf_deformerTuples in listOf_deformedObjectsInfo_usingDeformerToLoad:


        nextDeformerToLoad = listOf_deformerTuples[0][0]
        if not nextDeformerToLoad == deformerToLoad:
            if log:print '        %s not ready to load because %s needs to load %s first' % (deformerToLoad, shape, nextDeformerToLoad,)
            return False

        if not pymel.objExists(shape):
            if log:print '        %s not ready to load because %s does not exist' % (deformerToLoad, shape,)
            return False


    return True


def importDeformer(deformerPath, **kwargs):
    optimized = kwargs.get('optimize', '')

    deformerObj = getDeformerObj(deformerPath=deformerPath, **kwargs)
    deformerObj.import_(deformerPath, optimized=optimized)

def getDeformerObj(node=None, deformerPath=None, **deformerKwargs):
    """Returns an instance of the deformer class (if there is one) associated with the
    given node or nodeType"""
    if node:
        nodeType = node.nodeType()

        if 'deformer' not in deformerKwargs:
            deformerKwargs['deformer'] = node

    elif deformerPath:
        with open(os.path.join(deformerPath, 'kwargs.py'), 'r') as f:
            dataString = f.read()
            loadedKwargs = ast.literal_eval(dataString)

        for key in loadedKwargs:
            if key not in deformerKwargs:
                deformerKwargs[key] = loadedKwargs[key]

        # check if node already exists in scene
        deformer = pymel.ls(deformerKwargs['deformerName'])
        nodeType = deformerKwargs['nodeType']
        if deformer:
            deformerKwargs['deformer'] = deformer[0]

    deformerLibFileName = 'deformer_%s.py' % nodeType
    deformerLibModuleName = 'deformer_%s' % nodeType
    deformerLibPythonPath = '.'.join([__package__, 'deformerLib', deformerLibModuleName])

    if deformerLibFileName in os.listdir(DEFORMER_LIB_DIR):
        module = importlib.import_module(deformerLibPythonPath)
        reload(module)

        className = '%s%s' % (nodeType[0].upper(), nodeType[1:])
        deformerObj = getattr(module, className)(**deformerKwargs)
        OOOOOOO = "deformerKwargs"; print '%s: ' % OOOOOOO, eval(OOOOOOO), ' ', type(eval(OOOOOOO))

        return deformerObj

    return deformer_base.Deformer(**deformerKwargs)


def getDeformationOrderFileName(node):
    # parse args
    node = ka_pymel.getAsPyNodes(node)
    nodeName = node.nodeName(stripNamespace=True)

    return '%s%s' % (nodeName, DEFORMER_ORDER_SUFFIX)
