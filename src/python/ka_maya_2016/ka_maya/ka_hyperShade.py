#====================================================================================
#====================================================================================
#
# ka_utils_hyperShade
#
# DESCRIPTION:
#   tools for working in the hyperShade, intended to be accessed through the ka_menu
#
# DEPENDENCEYS:
#   ka_menus
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

import maya.cmds as cmds
import maya.mel as mel
import pymel.core as pymel

import ka_maya.ka_python as ka_python
import ka_maya.ka_preference as ka_preference

HYPER_GRAPH = 'graph1HyperShadeEd'
NODE_EDITOR = 'nodeEditorPanel2NodeEditorEd'


def alignNodes(alignment):
    selection = pymel.ls(selection=True)
    hyperGraph = 'graph1HyperShadeEd'

    if len(selection) >= 2:

        posX, posY = pymel.hyperGraph(HYPER_GRAPH, query=True, getNodePosition=selection[0])

        for each in selection[1:]:

            container = pymel.container(query=True, findContainer=[each])
            if container:
                pymel.setAttr(container+'.blackBox', 0)

            if alignment == 'horizontal':
                posX += 200
            elif alignment == 'vertical':
                posY -= 200
            else:
                print 'ERROR, no alignment set'

            pymel.hyperGraph(HYPER_GRAPH, edit=True, addDependNode=each)
            pymel.hyperGraph(HYPER_GRAPH, edit=True, setNodePosition=[each, posX, posY])
            print pymel.hyperGraph(HYPER_GRAPH, query=True, look=True)

def purgeGraphOfContainers():
    hyperGraph = 'graph1HyperShadeEd'

    nodesInGraph = pymel.hyperGraph(HYPER_GRAPH, query=True, getNodeList=True)
    nodePositionDict = {}
    for node in nodesInGraph:
        node = pymel.ls(node)[0]
        if node.nodeType() != 'dagContainer':
            x, y = pymel.hyperGraph(HYPER_GRAPH, getNodePosition=node, query=True, )
            nodePositionDict[node] = (x, y)

    clear()
    for node in nodePositionDict:
        x,y = nodePositionDict[node]
        pymel.hyperGraph(HYPER_GRAPH, edit=True, addDependNode=node,)
        #pymel.select(node)
        #pymel.select(node)
        #add()
        #pymel.hyperGraph('hyperShadePanel1', edit=True, setNodePosition=[node, x, y])
        pymel.hyperGraph(HYPER_GRAPH, edit=True, setNodePosition=[node, x, y])

def isolateInGraph():
    selection = pymel.ls(selection=True)
    positions = {}

    for each in selection:
        positions[each] = pymel.hyperGraph(HYPER_GRAPH, query=True, getNodePosition=each)

    mel.eval('hyperShadePanelGraphCommand("hyperShadePanel1",  "clearGraph")')

    OOOOOOO = 'positions';  print '%s = %s %s'%(str(OOOOOOO),str(eval(OOOOOOO)),str(type(eval(OOOOOOO))))
    for each in selection:
        pymel.select(each)
        #mel.eval("ka_hgAdd")
        print each
        pymel.hyperGraph(HYPER_GRAPH, edit=True, addDependNode=each)
        pymel.hyperGraph(HYPER_GRAPH, edit=True, setNodePosition=[each, positions[each][0], positions[each][1]])

    pymel.select(selection)

def clear():
    #mel.eval('hyperShadePanelGraphCommand("hyperShadePanel1",  "clearGraph")')
    pymel.hyperGraph(HYPER_GRAPH, edit=True, clear=True)

def add():
    #mel.eval("ka_hgAdd")
    pymel.hyperGraph(HYPER_GRAPH, edit=True, addDependNode=each)


def remove():
    pymel.hyperShade(HYPER_GRAPH, edit=True, addDependNode=True)

    #selectedNodes = pymel.selected()
    #nodesInGraph = pymel.hyperGraph(HYPER_GRAPH, query=True, getNodeList=True)
    #positionDict = {}
    #for node in nodesInGraph:
        #if node not in selectedNodes:
            #position = pymel.hyperGraph(HYPER_GRAPH, query=True, getNodePosition=node)
            #positionDict[node] = position

    #clear()
    #for node in positionDict:
        #x, y = positionDict[node]
        ##pymel.select(node)
        ##add()
        #pymel.hyperGraph(HYPER_GRAPH, edit=True,  addDependNode=node, setNodePosition=[node, x, y], enableAutomaticLayout=False)

    #OOOOOOO = "nodesInGraph"; print '%s: ' % OOOOOOO, eval(OOOOOOO), ' ', type(eval(OOOOOOO))

def contain(type):
    selection = pymel.ls(selection=True)
    if type == 'dag':
        type = 'dagContainer'


    positions = {}
    for each in selection:
        positions[each] = pymel.hyperGraph(HYPER_GRAPH, query=True, getNodePosition=selection[0])

    container = pymel.container(type=type, includeHierarchyBelow=True, )
    pymel.container(addNode=selection, edit=True, includeHierarchyBelow=True, force=True)
    print container
    pymel.select( cl=True )

    #pymel.evalDeferred('pymel.select("'+container+'", replace=True,)')
    #pymel.evalDeferred('pymel.hyperGraph("'+hyperGraph+'", edit=True, expandContainer=True)')



    def deferredCauseMayaIsStupid():
        pymel.select(container, replace=True,)
        pymel.hyperGraph(HYPER_GRAPH, edit=True, expandContainer=True)

        for each in positions:
            pymel.hyperGraph(HYPER_GRAPH, edit=True, setNodePosition=[each, positions[each][0], positions[each][1]])

        posX, posY = pymel.hyperGraph(HYPER_GRAPH, query=True, getNodePosition=container)
        pymel.hyperGraph(HYPER_GRAPH, edit=True, setNodePosition=[each, posX, posY+3])


    pymel.evalDeferred( deferredCauseMayaIsStupid)
    #mel.eval('select -r "'+ container+'";')
    #pymel.pickWalk( direction='up' )

    #pymel.hyperGraph(HYPER_GRAPH, edit=True, expandContainer=True)

def selectInputOutput(mode='all', depthLimit=4):

    selection = pymel.ls(selection=True)
    hyperGraph = 'graph1HyperShadeEd'


    addList = []
    addList.extend(selection)

    if mode == 'inputs' or mode == 'all':
        inputDepth = []
        inputDepth.append(selection)

        while len(inputDepth) < depthLimit:
            newDepth = []

            for each in inputDepth[-1]:

                inputs = pymel.listConnections( each, destination=False, source=True, skipConversionNodes=False)
                if inputs:
                    newDepth.extend(inputs)

            inputDepth.append(newDepth)

        for listVar in inputDepth:
            for each in listVar:
                if not each in addList and pymel.nodeType(each) != 'hyperLayout':
                    addList.append(each)



    if mode == 'outputs' or mode == 'all':
        outputDepth = []
        outputDepth.append(selection)

        while len(outputDepth) < depthLimit:
            newDepth = []

            for each in outputDepth[-1]:
                outputs = pymel.listConnections( each, destination=True, source=False, skipConversionNodes=False)
                if outputs:
                    newDepth.extend(outputs)

            outputDepth.append(newDepth)

        for listVar in outputDepth:
            for each in listVar:
                if not each in addList and pymel.nodeType(each) != 'hyperLayout':
                    addList.append(each)


    unblackBoxList = []
    for each in addList:
        container = pymel.container(query=True, findContainer=each)
        if container:
            if not container in unblackBoxList:
                if pymel.getAttr(container+'.blackBox'):
                    unblackBoxList.append(container)

    pymel.select(addList, replace=True)




def graphInputOutput(mode='all', depthLimit=4):

    selection = pymel.ls(selection=True)
    hyperGraph = 'graph1HyperShadeEd'
    nodeDict = {}

    dataDict = {'maxNodeLimit':ka_preference.get('hyperGraph_maxGraphSize', 100),
                'numberOfNodes':0,
                'nodesToAdd':{}, # dict is for fast uniqueness checking
                'orderedNodesToAdd':[],
                'nodeCount':0,
                'totalNodeCount':0,
                'nodeLimitExeeded':False,
                'stopGraphing':False,
                }

    addList = []
    addList.extend(selection)


    def addNodesToGraphList(nodes, dataDict):
        if not dataDict['stopGraphing']:
            if not isinstance(nodes, list):
                nodes = [nodes]

            # add to data
            uniqueInputs = 0
            for node in nodes:
                if node not in dataDict['nodesToAdd']:
                    if node.nodeType() not in ['hyperLayout', 'dagContainer', 'container']:
                        dataDict['nodesToAdd'][node] = True
                        dataDict['orderedNodesToAdd'].append(node)
                        dataDict['nodeCount'] += 1
                        dataDict['totalNodeCount'] += 1


                        # check if over max
                        if dataDict['nodeCount'] >= dataDict['maxNodeLimit']:

                            if dataDict['nodeLimitExeeded']:
                                message = 'You are about to graph an additional %s items (%s total).\n This could be slow, do you want to continue?' % (str(dataDict['nodeCount']), str(dataDict['totalNodeCount']))
                            else:
                                message = 'You are about to graph %s items.\n This could be slow, do you want to continue?' % str(dataDict['nodeCount'])


                            result = cmds.confirmDialog( title='Large Graph Operation', message=message, button=['Continue', 'Stop and Graph', 'Cancel'], defaultButton='Yes', cancelButton='Cancel', dismissString='Cancel' )
                            if result == 'Stop and Graph':
                                dataDict['stopGraphing'] = True
                                dataDict['nodeLimitExeeded'] = True
                                break

                            elif result == 'Cancel':
                                pymel.error('graphing aborted by user...')

                            else:
                                dataDict['nodeCount'] = 0
                                dataDict['nodeLimitExeeded'] = True

        return dataDict


    # add selection
    dataDict = addNodesToGraphList(selection, dataDict)



    if mode == 'inputs' or mode == 'all':
        inputDepth = []
        inputDepth.append(selection)

        while len(inputDepth) < depthLimit:
            newDepth = []

            for each in inputDepth[-1]:
                inputs = pymel.listConnections( each, destination=False, source=True, skipConversionNodes=False)

                if inputs:
                    newDepth.extend(inputs)
                    dataDict = addNodesToGraphList(inputs, dataDict)
                    if dataDict['stopGraphing']:
                        break
                        break

                #if inputs:
                    #uniqueInputs = 0
                    #for eachInput in inputs:
                        #if eachInput not in nodeDict:
                            #nodeDict[eachInput.__hash__()] = True
                            #uniqueInputs += 1
                            #newDepth.append(eachInput)

                    #if uniqueInputs:
                        #numberOfNodes = addToMaxLimit(uniqueInputs, numberOfNodes)


            inputDepth.append(newDepth)

        #numberOfNodes = addToMaxLimit(len(inputDepth[-1]), numberOfNodes)
        dataDict = addNodesToGraphList(inputDepth[-1], dataDict)

        #for inputList in inputDepth:
            #for each in inputList:
                #if not each in addList and pymel.nodeType(each) != 'hyperLayout':
                    #addList.append(each)



    if mode == 'outputs' or mode == 'all':
        outputDepth = []
        outputDepth.append(selection)

        while len(outputDepth) < depthLimit:
            newDepth = []

            for each in outputDepth[-1]:
                outputs = pymel.listConnections( each, destination=True, source=False, skipConversionNodes=False)
                if outputs:
                    newDepth.extend(outputs)
                    dataDict = addNodesToGraphList(outputs, dataDict)
                    if dataDict['stopGraphing']:
                        break
                        break

            outputDepth.append(newDepth)

        #numberOfNodes = addToMaxLimit(len(outputDepth[-1]), numberOfNodes)
        dataDict = addNodesToGraphList(outputDepth[-1], dataDict)

        #for outputList in outputDepth:
            #for each in outputList:
                #if not each in addList and pymel.nodeType(each) != 'hyperLayout':
                    #addList.append(each)


    pymel.hyperGraph(HYPER_GRAPH, edit=True, clear=True)
    unblackBoxList = []

    for node in dataDict['orderedNodesToAdd']:

        container = getContainerOfNode(node)

        if container:
            if isinstance(container, list):
                container = container[0]

            if not container in unblackBoxList:
                if container.blackBox.get():
                    unblackBoxList.append(container)

    for container in unblackBoxList:
        pymel.setAttr(container+'.blackBox', 0)

    for node in dataDict['orderedNodesToAdd']:

        #if not pymel.nodeType(node) in ['dagContainer', 'container']:
        pymel.hyperGraph(HYPER_GRAPH, edit=True, setNodePosition=[node, 0, 0])


    pymel.evalDeferred('mel.eval(\'hyperShadePanelGraphCommand("hyperShadePanel1", "rearrangeGraph");\')')

    pymel.evalDeferred('import pymel.core as pymel')
    pymel.evalDeferred('pymel.hyperGraph(\'graph1HyperShadeEd\', edit=True, frameGraph=True)')
    pymel.evalDeferred('pymel.hyperGraph(\'graph1HyperShadeEd\', edit=True, frameGraph=True)')
    pymel.evalDeferred('pymel.hyperGraph(\'graph1HyperShadeEd\', edit=True, frameGraph=True)')
    pymel.evalDeferred('pymel.hyperGraph(\'graph1HyperShadeEd\', edit=True, frameGraph=True)')

    for container in unblackBoxList:
        pymel.setAttr(container+'.blackBox', 1)


def getContainerOfNode(node):
    if isinstance(node, pymel.nodetypes.DagNode):
        parent = pymel.listRelatives(node, parent=True)
        if parent:
            while parent:
                if pymel.nodeType(node) == 'dagContainer':
                    return parent[0]

                else:
                    parent = pymel.listRelatives(parent, parent=True)
                    if not parent:
                        return None

    else:
        pass

def addInputToPlusMinus(node):
    pass
    pymel.setAttr('plusMinusAverage2.input1D[1]', 0)


def addKeysToAnimCurveNode(nodes=None):
    if nodes:
        if isinstance(nodes, list) or isinstance(nodes, tuple):
            pass
        else:
            nodes = [nodes]

    else:
        nodes = pymel.ls(selection=True)

    for animCurveNode in nodes:
        pymel.setKeyframe(animCurveNode, insert=False, float=0)
        pymel.setKeyframe(animCurveNode, insert=False, value=1, float=1)









