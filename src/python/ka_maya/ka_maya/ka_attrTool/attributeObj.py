import maya.cmds as cmds
import maya.mel as mel
import pymel.core as pymel
import maya.OpenMaya as OpenMaya
import traceback
import re

import os
import pickle
import time

import ka_maya.ka_python as ka_python

#import pymel.core as pymel
#import ka_maya.ka_attrTool.attributeObj as attributeObj ; reload(attributeObj)
#if not pymel.objExists('multiplyDivide1'):
    #pymel.createNode('multiplyDivide')

#node = pymel.ls('multiplyDivide1')[0]
#attrObj = attributeObj.AttributeObj(node, node.input1X.name())

#def _getattrDataBase():
    #if not os.path.exists(attrDataBaseFile):
        #pickle.dump( {}, open( attrDataBaseFile, "wb" ) )

    #try:
        #return pickle.load( open(attrDataBaseFile, "rb" ))
    #except EOFError:
        #return {}

#def _addToAttrDataBase():
    #global attrDataBase
    #try:
        #pickle.dump( attrDataBase, open( attrDataBaseFile, "wb" ) )
    #except:
        #pass

attrDataBaseDirectory = os.path.join(os.path.dirname(__file__), 'attrDataBase')
attrDatabaseStack = []
attrDatabaseDict = {}

def _getattrDataBase(nodeType):
    global attrDatabaseStack
    global attrDatabaseDict

    attrDbFile = os.path.join(attrDataBaseDirectory, '%s.p' % nodeType)
    dataDict = None

    # if dict is already the first item in the stack
    if attrDatabaseStack:
        if attrDatabaseStack[0] == nodeType:
            return attrDatabaseDict[nodeType]

    # item is already in stack, but is not the first item
    if nodeType in attrDatabaseDict:

        # move current nodeType to top of stack
        attrDatabaseStack.pop(attrDatabaseStack.index(nodeType))
        attrDatabaseStack.insert(0, nodeType)
        return attrDatabaseDict[nodeType]


    # if the attrDatabaseDict is at the max, then remove the last item
    # to make room for the new one
    if len(attrDatabaseStack) >= 10:
        attrDatabaseDict.pop(attrDatabaseStack[-1])
        attrDatabaseStack.pop()

    # load dict from file
    try:
        # create a new empty file if one does not exist
        if not os.path.exists(attrDbFile):
            pickle.dump( {}, open( attrDbFile, "wb" ) )

        dataDict = pickle.load( open(attrDbFile, "rb" ))
        attrDatabaseDict[nodeType] = dataDict
        attrDatabaseStack.insert(0, nodeType)

        return dataDict

    except EOFError:
        return {}

    except:
        return {}

def _addToAttrDataBase(nodeType, dataDict):

    attrDbFile = os.path.join(attrDataBaseDirectory, '%s.p' % nodeType)

    try:
        # save out dict
        pickle.dump( dataDict, open( attrDbFile, "wb" ) )

    except:
        pass


DATA_TYPES = {
"string" :         {'description':"string"},
"stringArray" :    {'description':"array of strings"},
"matrix" :         {'description':"4x4 double matrix"},
"reflectanceRGB" : {'description':"reflectance"},
"spectrumRGB" :    {'description':"spectrum"},
"float2" :         {'description':"2 floats"},
"float3" :         {'description':"3 floats"},
"double2" :        {'description':"2 doubles"},
"double3" :        {'description':"3 doubles"},
"long2" :          {'description':"2 32-bit integers"},
"long3" :          {'description':"3 32-bit integers"},
"short2" :         {'description':"2 16-bit integers"},
"short3" :         {'description':"3 16-bit integers"},
"doubleArray" :    {'description':"array of doubles"},
"Int32Array" :     {'description':"array of 32-bit ints"},
"vectorArray" :    {'description':"array of vectors"},
"nurbsCurve" :     {'description':"nurbs curve"},
"nurbsSurface" :   {'description':"nurbs surface"},
"mesh" :           {'description':"polygonal mesh"},
"lattice" :        {'description':"lattice"},
"pointArray" :     {'description':"array of double 4D points"},
}


ATTR_TYPES = {
"bool" :           {'description':"boolean"},
"long" :           {'description':"32 bit integer"},
"short" :          {'description':"16 bit integer"},
"byte" :           {'description':"8 bit integer"},
"char" :           {'description':"char"},
"enum" :           {'description':"enum"},
"float" :          {'description':"float"},
"double" :         {'description':"double"},
"doubleAngle" :    {'description':"angle value"},
"doubleLinear" :   {'description':"linear value"},
"compound" :       {'description':"compound"},
"message" :        {'description':"message (no data)"},
"time" :           {'description':"time"},
"fltMatrix" :      {'description':"4x4 float matrix"},
"reflectance" :    {'description':"reflectance (compound)"},
"spectrum" :       {'description':"spectrum (compound)"},
"float2" :         {'description':"2 floats (compound)"},
"float3" :         {'description':"3 floats (compound)"},
"double2" :        {'description':"2 doubles (compound)"},
"double3" :        {'description':"3 doubles (compound)"},
"long2" :          {'description':"2 32-bit integers (compound)"},
"long3" :          {'description':"3 32-bit integers (compound)"},
"short2" :         {'description':"2 16-bit integers (compound)"},
"short3" :         {'description':"3 16-bit integers (compound)"},
}

NUMERIC_TYPES = {
"bool" :None,
"long" :None,
"short" :None,
"byte" :None,
"char" :None,
"enum" :None,
"float" :None,
"double" :None,
"doubleAngle" :None,
"doubleLinear" :None,
"time" :None,
"fltMatrix" :None,
"float2" :None,
"float3" :None,
"double2" :None,
"double3" :None,
"long2" :None,
"long3" :None,
"short2" :None,
"short3" :None,
"doubleArray" :    {'description':"array of doubles"},
"Int32Array" :     {'description':"array of 32-bit ints"},
}

TRIPLE_TYPES = {
'float3':None,
'double3':None,
'long3':None,
'short3':None,
}


class AttributeObj(object):
    """object with information about the given attribute,
    differs from pymel attributes because if is built to ignore
    as many errors as possible, and return reasonable returns in cases
    that do generate errors internally. It also is very carefull not to
    generate array elements by not preforming querys (like value) to items
    which do not exist"""

    def __init__(self, node, attrName, **kwargs):
        """node - pymelNode
           attrName - name of attribute
        """

        self._node                   = node
        self._nodeType               = kwargs.get('nodeType', None)
        self._nodeTypes              = kwargs.get('nodeTypes', None)
        self._nodeName               = kwargs.get('nodeName', None)
        self._nodeLongName           = kwargs.get('nodeLongName', None)

        # determine attribute name
        # from attrName input
        if '.' in attrName:
            self._attrName           = attrName.split('.')[-1]
            self._attrLongName       = attrName

        else:
            self._attrName           = attrName
            self._attrLongName       = kwargs.get('attrLongName', None)

        self._isUserDefined          = kwargs.get('userDefined', None)

        self._attr                   = kwargs.get('attr', None)
        self._attrShortName          = kwargs.get('attrShortName', None)
        self._attrNiceName           = kwargs.get('attrNiceName', None)
        self._attrParent             = kwargs.get('attrParent', None)
        self._attrParentName         = kwargs.get('attrParentName', None)
        self._attrParentLongName     = kwargs.get('attrParentLongName', None)
        self._nonIndexedAttrName     = kwargs.get('nonIndexedAttrName', None)
        self._attrChildren           = kwargs.get('attrChildren', None)
        self._attrChildrenNames      = kwargs.get('attrChildrenNames', None)
        self._attrChildrenLongNames  = kwargs.get('attrChildrenLongNames', None)
        self._usedIndices            = kwargs.get('usedIndices', None)
        self._exists                 = kwargs.get('exists', None)
        self._value                  = kwargs.get('value', None)

        self._isArray                = kwargs.get('isArray', None)
        self._isElement              = kwargs.get('isElement', None)
        self._isInstanceAttr         = kwargs.get('isInstanceAttr', None)
        self._isCompound             = kwargs.get('isCompound', None)
        self._isMulti                = kwargs.get('isMulti', None)
        self._isSource               = kwargs.get('isSource', None)
        self._isDestination          = kwargs.get('isDestination', None)
        self._isReadable             = kwargs.get('isReadable', None)
        self._isWritable             = kwargs.get('isWritable', None)
        self._isNumeric              = kwargs.get('isNumeric', None)
        self._isDefaultValue         = kwargs.get('isDefaultValue', None)
        self._isSettable             = kwargs.get('isSettable', None)
        self._isConnected            = kwargs.get('isConnected', None)
        self._inputs                 = kwargs.get('inputs', None)
        self._outputs                = kwargs.get('outputs', None)
        self._isLocked               = kwargs.get('isLocked', None)
        self._isKeyable              = kwargs.get('isKeyable', None)
        self._isInChannelBox         = kwargs.get('isInChannelBox', None)
        self._isSimple               = kwargs.get('isSimple', None)
        self._attrType               = kwargs.get('attrType', None)
        self._isDataType             = kwargs.get('isDataType', None)
        self._isAttributeType        = kwargs.get('isAttributeType', None)
        self._isTriple               = kwargs.get('isTriple', None)

        self._enumStrings            = kwargs.get('enumStrings', None)
        self._enumString             = kwargs.get('enumString', None)
        self._hasMinValue            = kwargs.get('hasMinValue', None)
        self._hasMaxValue            = kwargs.get('hasMaxValue', None)
        self._minValue               = kwargs.get('minValue', None)
        self._maxValue               = kwargs.get('maxValue', None)
        self._hasSoftMaxValue        = kwargs.get('hasSoftMaxValue', None)
        self._hasSoftMinValue        = kwargs.get('hasSoftMinValue', None)
        self._softMaxValue           = kwargs.get('softMaxValue', None)
        self._softMinValue           = kwargs.get('softMinValue', None)

        self.tracking = False

        # userDefined must be determined early to know
        # if database look ups can be performed on certain propertys
        # of the attribute, time can be saved by passing this value in
        if self._isUserDefined == None:
            userDefinedAttrs = self.node().listAttr(userDefined=True)

            if self.attr() in userDefinedAttrs:
                self._isUserDefined = True
            else:
                self._isUserDefined = False

        self._nodeTypeDBInfo = _getattrDataBase(self.nodeType())


    def __repr__(self):
        return '<AttributeObject: %s.%s>' % (self.nodeName(), self.attrLongName())

    def _getFromDataBase(self, propertyName):
        nodeTypeDict = self._nodeTypeDBInfo

        if self.isInstanceAttr():
            attrLongName = self.attrLongName()
        else:
            attrLongName = self.nonIndexedAttrName()


        attrDict = nodeTypeDict.get(attrLongName, {})
        value = attrDict.get(propertyName, None)
        return value

    def _addToDataBase(self, propertyName, propertyValue):
        if not self.isUserDefined():

            # variables
            nodeType = self.nodeType()
            if self.isInstanceAttr():
                attrLongName = self.attrLongName()
            else:
                attrLongName = self.nonIndexedAttrName()

            if not self._nodeTypeDBInfo.has_key(attrLongName):
                self._nodeTypeDBInfo[attrLongName] = {}

            self._nodeTypeDBInfo[attrLongName][propertyName] = propertyValue

            # add to database
            _addToAttrDataBase(nodeType, self._nodeTypeDBInfo)

    def _getProperty(self, propertyName, checkDataBase=False, alternativeValue=None):
        _propertyName = '_%s' % propertyName

        # get stored Value
        propertyValue = getattr(self, _propertyName)
        if propertyValue != None:
            return propertyValue

        # get and set from dataBase Value
        if checkDataBase:
            if not self._isUserDefined:
                propertyValue = self._getFromDataBase(propertyName)

                if propertyValue != None:
                    setattr(self, _propertyName, propertyValue)
                    return propertyValue


    def node(self):
        if isinstance(self._node, basestring):
            return pymel.ls(self._node)[0]
        else:
            return self._node


    def nodeType(self):
        # Quick Query
        propertyValue = self._getProperty('nodeType')
        if propertyValue != None:
            return propertyValue

        # Regular Query
        try:
            self._nodeType = self.node().nodeType()
            return self._nodeType

        except:
            ka_python.printError()

    def nodeTypes(self):
        # Quick Query
        propertyValue = self._getProperty('nodeTypes')
        if propertyValue != None:
            return propertyValue

        # Regular Query
        try:
            self._nodeTypes = self.node().nodeType(inherited=True)
            return self._nodeTypes

        except:
            ka_python.printError()

    def attrName(self):
        return self._attrName

    def isUserDefined(self):
        return self._isUserDefined

    def nodeName(self, refresh=False):
        # Quick Query
        if not refresh:
            propertyValue = self._getProperty('nodeName')
            if propertyValue != None:
                return propertyValue

        # Regular Query
        try:
            self._nodeName = self.node().nodeName()
            return self._nodeName

        except:
            pass

    def nodeLongName(self, refresh=False):
        # Quick Query
        if not refresh:
            propertyValue = self._getProperty('nodeLongName')
            if propertyValue != None:
                return propertyValue


        try:
            return self._node.name(long=True)

        except:
            ka_python.printError()
            return self.nodeName()

    def attr(self):
        # Quick Query
        propertyValue = self._getProperty('attr')
        if propertyValue != None:
            return propertyValue

        try:
            self._attr = self.node().attr(self.attrLongName())
            return self._attr

        except:
            ka_python.printError()


    def attrShortName(self):

        # Quick Query
        propertyValue = self._getProperty('attrShortName', checkDataBase=True,)
        if propertyValue != None:
            return propertyValue

        # Regular Query
        try:
            self._attrShortName = self.attr().name(includeNode=False, longName=False, fullAttrPath=False, placeHolderIndices=False)
            self._addToDataBase('attrShortName', self._attrShortName)
            return self._attrShortName

        except:
            ka_python.printError()

        # Alternative Value
        self._attrShortName = self._attrName
        return self._attrShortName

    def attrLongName(self):
        """the attrLong name is important because it is used as a key in the dataBase.
        It therfore cannot be stored in the database"""

        # Quick Query
        propertyValue = self._getProperty('attrLongName')  # can not check DB, as it is used as key
        if propertyValue != None:
            return propertyValue

        # Regular Query
        try:
            self._attrLongName = self.node().attr(self.attrName()).name(includeNode=False, longName=True, fullAttrPath=True, placeHolderIndices=True)
            return self._attrLongName

        except:
            ka_python.printError()

        # Alternative Value
        self._attrLongName = self.attrName()
        return self._attrLongName

    def attrNiceName(self):
        # Quick Query
        propertyValue = self._getProperty('attrNiceName')  # can not check DB, as it is used as key
        if propertyValue != None:
            return propertyValue

        # Regular Query
        #try:
        self._attrNiceName = pymel.attributeQuery(self.attrLongName(), node=self.node(), niceName=True)
        return self._attrNiceName

        #except:
            #ka_python.printError()

        return self._attrNiceName



    def attrParent(self):
        # Quick Query
        propertyValue = self._getProperty('attrParent',)
        if propertyValue != None:
            return propertyValue

        # Regular Query
        #try:
        self._attrParent = self.attr().getParent(arrays=True)
        return self._attrParent
        #except: pass


    def attrParentName(self):
        # Quick Query
        propertyValue = self._getProperty('attrParentName', checkDataBase=True,)
        if propertyValue != None:
            return propertyValue

        # Regular Query
        try:
            self._attrParentName = self.attrParent().attrName(longName=True, includeNode=False)
            self._addToDataBase('attrParentName', self._attrParentName)
            return self._attrParentName
        except: pass

        # Alternative Value
        self._attrParentName = ''
        return self._attrParentName

    def attrParentLongName(self):
        # Quick Query
        propertyValue = self._getProperty('attrParentLongName', checkDataBase=True,)
        if propertyValue != None:
            return propertyValue

        # Regular Query
        try:
            self._attrParentLongName = self.attrParent().name(includeNode=False, longName=True, fullAttrPath=True, placeHolderIndices=False)
            self._addToDataBase('attrParentLongName', self._attrParentLongName)
            return self._attrParentLongName
        except: pass

        # Alternative Value
        self._attrParentLongName = ''
        return self._attrParentLongName


    def nonIndexedAttrName(self):
        # Quick Query
        propertyValue = self._getProperty('nonIndexedAttrName', checkDataBase=False,)
        if propertyValue != None:
            return propertyValue

        # Regular Query
        self._nonIndexedAttrName = re.sub('\[.\]', '', self.attrLongName())
        return self._nonIndexedAttrName


    def attrChildren(self):
        # Quick Query
        propertyValue = self._getProperty('attrChildren',)
        if propertyValue != None:
            return propertyValue

        # Regular Query
        try:
            self._attrChildren = self.attr().getChildren()
            #self._attrChildren = cmds.attributeQuery(self.attrLongName(), node=self.nodeLongName(), listChildren=True, longName=True)

            return self._attrChildren
        except: pass

        # Alternative Value
        self._attrChildren = []
        return self._attrChildren

    def attrChildrenNames(self):
        # Quick Query
        propertyValue = self._getProperty('attrChildrenNames', checkDataBase=True)
        if propertyValue != None:
            return propertyValue

        # Regular Query
        try:
            self._attrChildrenNames = []
            for childAttr in self.attrChildren():
                self._attrChildrenNames.append(childAttr.name(includeNode=False, longName=True, fullAttrPath=True, placeHolderIndices=True))

            self._addToDataBase('attrChildrenNames', self._attrChildrenNames)
            return self._attrChildrenNames
        except: pass


        # Alternative Value
        self._attrChildrenNames = []
        return self._attrChildrenNames

    def attrChildrenLongNames(self):
        # Quick Query
        propertyValue = self._getProperty('attrChildrenLongNames', checkDataBase=True)
        if propertyValue != None:
            return propertyValue

        # Regular Query
        try:
            self._attrChildrenLongNames = []
            for childAttr in self.attrChildren():
                #self._attrChildrenLongNames = cmds.attributeQuery(self.attrLongName(), node=self.nodeLongName(), listChildren=True, longName=True)
                self._attrChildrenLongNames.append(childAttr.name(includeNode=False, longName=True, fullAttrPath=True, placeHolderIndices=True))

            self._addToDataBase('attrChildrenLongNames', self._attrChildrenLongNames)
            return self._attrChildrenLongNames
        except: pass


        # Alternative Value
        self._attrChildrenLongNames = []
        return self._attrChildrenLongNames

    def isArray(self):
        # Quick Query
        propertyValue = self._getProperty('isArray', checkDataBase=True)
        if propertyValue != None:
            return propertyValue


        # Regular Query
        #try:
        self._isArray = self.attr().isArray()
        self._addToDataBase('isArray', self._isArray)
        return self._isArray
        #except: pass


        # Alternative Value
        self._isArray = False
        return self._isArray


    def isElement(self):
        # Quick Query with database
        propertyValue = self._getProperty('isElement', checkDataBase=True)
        if propertyValue != None:
            return propertyValue

        # Regular Query
        #try:
        self._isElement = self.attr().isElement()
        self._addToDataBase('isElement', self._isElement)
        return self._isElement
        #except: pass

        # Alternative Value
        self._isElement = False
        return self._isElement

    def isInstanceAttr(self):
        """returns True if this attribute is an element or child of an element of an
        array.
        """
        # Quick Query
        propertyValue = self._getProperty('isInstanceAttr', checkDataBase=False)
        if propertyValue != None:
            return propertyValue

        # check if ANY parent attr is multi
        longName = self.attrLongName()
        if '[' in longName:
            if '[-' not in longName:
                self.__isInstanceAttr = True
                return True


    def isCompound(self):
        # Quick Query
        propertyValue = self._getProperty('isCompound', checkDataBase=True)
        if propertyValue != None:
            return propertyValue

        # Regular Query
        #try:
        self._isCompound = self.attr().isCompound()
        self._addToDataBase('isCompound', self._isCompound)
        return self._isCompound
        #except: pass

        # Alternative Value
        self._isCompound = False
        return self._isCompound


    def isMulti(self):
        # Quick Query
        propertyValue = self._getProperty('isMulti', checkDataBase=True)
        if propertyValue != None:
            return propertyValue

        # Regular Query
        #try:
        self._isMulti = self.attr().isMulti()
        self._addToDataBase('isMulti', self._isMulti)
        return self._isMulti
        #except: pass

        # Alternative Value
        self._isMulti = False
        return self._isMulti

    def usedIndices(self, refresh=False):
        if self.exists():

            # Quick Query
            if not refresh:
                propertyValue = self._getProperty('usedIndices',)
                if propertyValue != None:
                    return propertyValue

            # Regular Query
            try:
                self._usedIndices = self.attr().getArrayIndices()
                return self._usedIndices
            except: pass

        # Alternative Value
        self._usedIndices = []
        return self._usedIndices

    def exists(self, refresh=False):
        # Quick Query
        if not refresh:
            propertyValue = self._getProperty('exists',)
            if propertyValue != None:
                return propertyValue

        # Regular Query
        #try:
        self._exists = self.attr().exists()
        return self._exists
        #except: pass

        # Alternative Value
        self._exists = True
        return self._exists

    def isNumeric(self, refresh=False):
        # Quick Query
        if not refresh:
            propertyValue = self._getProperty('isNumeric', checkDataBase=True)
            if propertyValue != None:
                return propertyValue

        # Regular Query
        self._isNumeric = self.attrType() in NUMERIC_TYPES
        self._addToDataBase('isNumeric', self._isNumeric)
        return self._isNumeric


    def isSource(self, refresh=False):
        if self.exists():

            # Quick Query
            if not refresh:
                propertyValue = self._getProperty('isSource',)
                if propertyValue != None:
                    return propertyValue

            # Regular Query
            #try:
            self._isSource = self.attr().isSource()
            return self._isSource
            #except: pass

        # Alternative Value
        self._isSource = False
        return self._isSource


    def isDestination(self, refresh=False):
        if self.exists():

            # Quick Query
            if not refresh:
                propertyValue = self._getProperty('isDestination',)
                if propertyValue != None:
                    return propertyValue

            # Regular Query
            #try:
            self._isDestination = self.attr().isDestination()
            return self._isDestination
            #except: pass


        # Alternative Value
        self._isDestination = False
        return self._isDestination


    def isReadable(self):
        # Quick Query
        propertyValue = self._getProperty('isReadable',)
        if propertyValue != None:
            return propertyValue


        # Regular Query
        #try:
        self._isReadable = pymel.attributeQuery(self.attrName(), node=self.node(), readable=True)
        self._addToDataBase('isReadable', self._isReadable)
        return self._isReadable
        #except: pass

        # Alternative Value
        self._isReadable = False
        return self._isReadable


    def isWritable(self):
        # Quick Query
        propertyValue = self._getProperty('isWritable',)
        if propertyValue != None:
            return propertyValue

        # Regular Query
        #try:
        self._isWritable = pymel.attributeQuery(self.attrName(), node=self.node(), writable=True)
        self._addToDataBase('isWritable', self._isWritable)
        return self._isWritable
        #except: pass

        # Alternative Value
        self._isWritable = False
        return self._isWritable

    def isSettable(self, refresh=False):
        # Quick Query
        if not refresh:
            propertyValue = self._getProperty('isSettable',)
            if propertyValue != None:
                return propertyValue

        # Regular Query
        #try:
        self._isSettable = self.attr().isSettable()
        self._addToDataBase('isSettable', self._isSettable)
        return self._isSettable
        #except: pass

        # Alternative Value
        self._isSettable = False
        return self._isSettable

    def isTriple(self):
        """returns True if this attribute is a triple attrType, ie: double3"""
        # Quick Query
        propertyValue = self._getProperty('isTriple', checkDataBase=True)
        if propertyValue != None:
            return propertyValue

        # Regular Query
        attrType = self.attrType()
        if attrType in TRIPLE_TYPES:
            self._isTriple = True
        else:
            self._isTriple = False
        return self._isTriple


    def value(self, refresh=False):
        # Quick Query
        if not refresh:
            propertyValue = self._getProperty('value',)
            if propertyValue != None:
                return propertyValue

        # Regular Query
        #try:
        if self.exists():
            if self.isTriple():
                value = pymel.getAttr(self.attr())
                self._value = pymel.getAttr(self.attr())
                return self._value

            elif not self.isMulti() and not self.isArray() and not self.isCompound():
                value = pymel.getAttr(self.attr())
                if isinstance(value, float) or isinstance(value, basestring) or isinstance(value, bool) or isinstance(value, int):
                    self._value = pymel.getAttr(self.attr())
                    return self._value

        #except: pass


    def hasMinValue(self, refresh=False):
        # Quick Query
        if not refresh:
            propertyValue = self._getProperty('hasMinValue',)
            if propertyValue != None:
                return propertyValue

        # Regular Query
        if self.exists():
            self._hasMinValue = pymel.attributeQuery(self.attrLongName(), node=self.node(), minExists=True)
            return self._hasMinValue

        # Alternative Value
        self._hasMinValue = False
        return self._hasMinValue


    def hasMaxValue(self, refresh=False):
        # Quick Query
        if not refresh:
            propertyValue = self._getProperty('hasMaxValue',)
            if propertyValue != None:
                return propertyValue

        # Regular Query
        if self.exists():
            self._hasMaxValue = pymel.attributeQuery(self.attrLongName(), node=self.node(), maxExists=True)
            return self._hasMaxValue

        # Alternative Value
        self._hasMaxValue = False
        return self._hasMaxValue


    def minValue(self, refresh=False):
        # Quick Query
        if not refresh:
            propertyValue = self._getProperty('minValue',)
            if propertyValue != None:
                return propertyValue

        # Regular Query
        if self.exists():
            if self.hasMinValue():
                self._minValue = pymel.attributeQuery(self.attrLongName(), node=self.node(), minimum=True)[0]

        return self._minValue


    def maxValue(self, refresh=False):
        # Quick Query
        if not refresh:
            propertyValue = self._getProperty('maxValue',)
            if propertyValue != None:
                return propertyValue

        # Regular Query
        if self.exists():
            if self.hasMaxValue():
                self._maxValue = pymel.attributeQuery(self.attrLongName(), node=self.node(), maximum=True)[0]

        return self._maxValue


    def hasSoftMaxValue(self, refresh=False):
        # Quick Query
        if not refresh:
            propertyValue = self._getProperty('hasSoftMaxValue',)
            if propertyValue != None:
                return propertyValue

        # Regular Query
        if self.exists():
            self._hasSoftMaxValue = pymel.attributeQuery(self.attrLongName(), node=self.node(), softMaxExists=True)
            return self._hasSoftMaxValue

        # Alternative Value
        self._hasSoftMaxValue = False
        return self._hasSoftMaxValue


    def hasSoftMinValue(self, refresh=False):
        # Quick Query
        if not refresh:
            propertyValue = self._getProperty('hasSoftMinValue',)
            if propertyValue != None:
                return propertyValue

        # Regular Query
        if self.exists():
            self._hasSoftMinValue = pymel.attributeQuery(self.attrLongName(), node=self.node(), softMinExists=True)
            return self._hasSoftMinValue

        # Alternative Value
        self._hasSoftMinValue = False
        return self._hasSoftMinValue


    def softMaxValue(self, refresh=False):
        # Quick Query
        if not refresh:
            propertyValue = self._getProperty('softMaxValue',)
            if propertyValue != None:
                return propertyValue

        # Regular Query
        if self.exists():
            if self.hasSoftMaxValue():
                self._softMaxValue = pymel.attributeQuery(self.attrLongName(), node=self.node(), softMax=True)[0]

        return self._softMaxValue


    def softMinValue(self, refresh=False):
        # Quick Query
        if not refresh:
            propertyValue = self._getProperty('softMinValue',)
            if propertyValue != None:
                return propertyValue

        # Regular Query
        if self.exists():
            if self.hasSoftMinValue():
                self._softMinValue = pymel.attributeQuery(self.attrLongName(), node=self.node(), softMax=True)[0]

        return self._softMinValue


    def isDefaultValue(self, refresh=False):
        # Quick Query
        if not refresh:
            propertyValue = self._getProperty('isDefaultValue',)
            if propertyValue != None:
                return propertyValue

        # Regular Query
        #try:
        if self.exists():


            l = []
            self.attr().__apimplug__().getSetAttrCmds(l, OpenMaya.MPlug.kNonDefault, True)
            #a.localScaleX.__apimplug__().getSetAttrCmds(l, OpenMaya.MPlug.kNonDefault, True)


            #if self.attr().getSetAttrCmds(valueSelector='nonDefault'):
            if l:
                self._isDefaultValue = False
            else:
                self._isDefaultValue = True
            return self._isDefaultValue
        #except: pass

        # Alternative Value
        self._isDefaultValue = True
        return self._isDefaultValue


    def isConnected(self, refresh=False):
        # Quick Query
        if not refresh:
            propertyValue = self._getProperty('isConnected',)
            if propertyValue != None:
                return propertyValue

        # Regular Query
        #try:
        if self.exists():
            self._isConnected = self.attr().isConnected()
            return self._isConnected
        #except: pass

        # Alternative Value
        self._isConnected = False
        return self._isConnected

    def inputs(self, refresh=False, skipConversionNodes=True):
        if self.exists():

            # Quick Query
            if not refresh:
                propertyValue = self._getProperty('inputs',)
                if propertyValue != None:
                    return propertyValue

            # Regular Query
            #try:
            if self.exists():
                self._inputs = self.attr().inputs(plugs=True, skipConversionNodes=skipConversionNodes)
                return self._inputs
            #except: pass

        # Alternative Value
        self._inputs = []
        return self._inputs

    def outputs(self, refresh=False, skipConversionNodes=True):
        if self.exists():

            # Quick Query
            if not refresh:
                propertyValue = self._getProperty('outputs')
                if propertyValue != None:
                    return propertyValue

            # Regular Query
            #try:
            if self.exists():
                self._outputs = self.attr().outputs(plugs=True, skipConversionNodes=skipConversionNodes)
                return self._outputs
            #except: pass

        # Alternative Value
        self._outputs = []
        return self._outputs

    def isLocked(self, refresh=False):
        # Quick Query
        if not refresh:
            propertyValue = self._getProperty('isLocked',)
            if propertyValue != None:
                return propertyValue

        # Regular Query
        #try:
        self._isLocked = self.attr().isLocked()
        return self._isLocked
        #except: pass

        # Alternative Value
        self._isLocked = False
        return self._isLocked

    def isKeyable(self, refresh=False):
        # Quick Query
        if not refresh:
            propertyValue = self._getProperty('isKeyable',)
            if propertyValue != None:
                return propertyValue

        # Regular Query
        #try:
        self._isKeyable = self.attr().isKeyable()
        return self._isKeyable
        #except: pass

        # Alternative Value
        self._isKeyable = False
        return self._isKeyable

    def isInChannelBox(self, refresh=False):
        # Quick Query
        if not refresh:
            propertyValue = self._getProperty('isInChannelBox',)
            if propertyValue != None:
                return propertyValue

        # Regular Query
        #try:
        self._isInChannelBox = self.attr().isInChannelBox()
        return self._isInChannelBox
        #except: pass

        # Alternative Value
        self._isInChannelBox = False
        return self._isInChannelBox

    def isSimple(self):
        """Is this a simple attribute that can be easily set, or is it an array/compound/matrix/mesh/etc"""

        # Quick Query
        propertyValue = self._getProperty('isSimple', checkDataBase=True)
        if propertyValue != None:
            return propertyValue

        # Regular Query
        #try:
        attrType = self.attrType()
        if attrType in ('bool', 'long', 'short', 'enum', 'float', 'double', 'doubleAngle', 'doubleLinear', 'string', 'time', 'double3', 'double2', 'long3', 'long2', 'short3', 'short2', ):
            self._isSimple = True
        else:
            self._isSimple = False

        self._addToDataBase('isSimple', self._isSimple)
        return self._isSimple
        #except: pass

        # Alternative Value
        self._isSimple = False
        return self._isSimple

    def attrType(self):
        # Quick Query
        propertyValue = self._getProperty('attrType', checkDataBase=True)
        if propertyValue != None:
            return propertyValue

        # Regular Query
        self._attrType = self.attr().type()
        self._addToDataBase('attrType', self._attrType)
        return self._attrType

    def isDataType(self):
        # Quick Query
        propertyValue = self._getProperty('isDataType', checkDataBase=True)
        if propertyValue != None:
            return propertyValue

        # Regular Query
        #try:
        attrType = self.attrType()
        if attrType in DATA_TYPES:
            self._isDataType = True
        self._addToDataBase('isDataType', self._isDataType)
        return self._isDataType
        #except: pass

    def isAttributeType(self):
        # Quick Query
        propertyValue = self._getProperty('isAttributeType', checkDataBase=True)
        if propertyValue != None:
            return propertyValue

        # Regular Query
        #try:
        attrType = self.attrType()
        if attrType in ATTR_TYPES:
            self._isAttributeType = True
        self._addToDataBase('isAttributeType', self._isAttributeType)
        return self._isAttributeType
        #except: pass

    def enumStrings(self):
        # Quick Query
        propertyValue = self._getProperty('enumStrings', checkDataBase=False)
        if propertyValue != None:
            return propertyValue

        # Regular Query
        if self.attrType() == 'enum':
            enumString = self.getEnumString()
            if enumString:
                self._enumStrings = enumString.split(':')

        return self._enumStrings

    def enumString(self):
        # Quick Query
        propertyValue = self._getProperty('enumString', checkDataBase=False)
        if propertyValue != None:
            return propertyValue

        # Regular Query
        if self.attrType() == 'enum':
            #enumString = pymel.attributeQuery(self.attr(), node=self.node(), listEnum=True)
            enumString = pymel.attributeQuery(self.attrLongName(), node=self.node(), listEnum=True)
            if enumString:
                enumString = enumString[0]
                self._enumString = enumString

        return self._enumString



    def recreateAttr(self):
        """recreats the attribute exactlty as it was before. The main use of this is to reorder
        the attributes"""
        kwArgs = {}

        attrLongName = self.attrLongName()
        isInChannelBox = self.isInChannelBox()
        isLocked = self.isLocked()

        attrOutputs = self.outputs()
        attrInputs = self.inputs()

        if self.attrType() == 'enum':
            kwArgs['enumName'] = self.enumString()

        if self.isAttributeType():
            kwArgs['attributeType'] = self.attrType()

        if self.isDataType():
            kwArgs['dataType'] = self.attrType()

        if self.hasMaxValue():
            kwArgs['hasMaxValue'] = self.hasMaxValue()
            kwArgs['maxValue'] = self.maxValue()

        if self.hasMinValue():
            kwArgs['hasMinValue'] = self.hasMinValue()
            kwArgs['minValue'] = self.minValue()

        if self.hasSoftMaxValue():

            kwArgs['hasSoftMaxValue'] = self.hasSoftMaxValue()
            kwArgs['softMaxValue'] = self.softMaxValue()

        if self.hasSoftMinValue():
            kwArgs['hasSoftMinValue'] = self.hasSoftMinValue()
            kwArgs['softMinValue'] = self.softMinValue()

        value = self.value()
        if value != None:
            if isinstance(value, int) or isinstance(value, float):
                kwArgs['defaultValue'] = self.value()

        kwArgs['keyable'] = self.isKeyable()
        kwArgs['shortName'] = self.attrShortName()
        kwArgs['niceName'] = self.attrNiceName()
        kwArgs['multi'] = self.isMulti()

        # unlock
        if self.isLocked():
            self.attr().unlock()

        self.attr().delete()
        self.node().addAttr(attrLongName, **kwArgs)
        self.__init__(self.node(), self.attrLongName())

        enumAttr = self.node().attr(self.attrLongName())

        if value != None:
            enumAttr.set(value)

        # reconnect
        for attrInput in attrInputs:
            attrInput >> enumAttr

        for attrOutput in attrOutputs:
            enumAttr >> attrOutput

        # relock/channel box vis
        self.attr().set(keyable=kwArgs['keyable'], channelBox=isInChannelBox, lock=isLocked)
