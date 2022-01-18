import maya.cmds as cmds
import maya.mel as mel
import pymel.core as pymel

import os
import pickle
import collections


useGlobalPref = False

try:
    import getpass
    if getpass.getuser() == 'admin':
        useGlobalPref = True
except: pass

try:
    if os.getlogin() == 'kandrews':
        useGlobalPref = True
except: pass


def set(*args):
    add(*args)

def add(key, pyObject):
    prefData = _getPreferenceData()
    prefData[key] = pyObject
    if useGlobalPref:
        pickle.dump( prefData, open(_getGlobalPreferenceFile(), "wb") )
    else:
        pickle.dump( prefData, open(_getLocalPreferenceFile(), "wb") )


def get(key, defaultValue=None):
    prefData = _getPreferenceData()
    return prefData.get(key, defaultValue)

def deletePref(key):
    prefData = _getPreferenceData()
    prefData.pop(key)
    if useGlobalPref:
        pickle.dump( prefData, open(_getGlobalPreferenceFile(), "wb") )
    else:
        pickle.dump( prefData, open(_getLocalPreferenceFile(), "wb") )


def _getGlobalPreferenceFile():
    currentDir = os.path.dirname(__file__)
    return os.path.join(currentDir, 'ka_preferencesGlobal.p')

def _getLocalPreferenceFile():
    userPrefDir = pymel.internalVar(userAppDir=True)
    return os.path.join(userPrefDir, 'ka_preferencesLocal.p')

def _getPreferenceData():
    localPreferenceFile = _getLocalPreferenceFile()
    if not os.path.exists(localPreferenceFile):
        pickle.dump( {}, open( localPreferenceFile, "wb" ) )

    globalPreferenceFile = _getGlobalPreferenceFile()
    if not os.path.exists(globalPreferenceFile):
        pickle.dump( {}, open( globalPreferenceFile, "wb" ) )

    localPreferenceData = pickle.load( open(localPreferenceFile, "rb" ))
    globalPreferenceData = pickle.load( open(globalPreferenceFile, "rb" ))
    #finalData = deepMergeDict(globalPreferenceData, localPreferenceData)
    finalData = deepMergeDict(localPreferenceData, globalPreferenceData)
    return finalData

def quacks_like_dict(object):
    """Check if object is dict-like"""
    return isinstance(object, collections.Mapping)

def deepMergeDict(childDict, parentDict):
    """Merge two deep dicts non-destructively, and the resulting dictionary is b, with
    inherited keys and values from a, so long as they:
    -dont exist in b
    -the dictionary doesn't conatin an inherit:False flag
    >>> a = {'a': 1, 'b': {1: 1, 2: 2}, 'd': 6}
    >>> b = {'c': 3, 'b': {2: 7}, 'd': {'z': [1, 2, 3]}}
    >>> c = b_inheritsFrom_a_toMake_c(a, b)
    >>> from pprint import pprint; pprint(c)
    {'a': 1, 'b': {1: 1, 2: 7}, 'c': 3, 'd': {'z': [1, 2, 3]}}
    """

    assert quacks_like_dict(childDict), quacks_like_dict(parentDict)
    finalDict = childDict.copy()

    stack = [(finalDict, parentDict)]
    while stack:
        currentDict_inFinalDict, currentDict_inParentDict = stack.pop()

        #begin
        for key in currentDict_inParentDict:
                if key not in currentDict_inFinalDict:
                    currentDict_inFinalDict[key] = currentDict_inParentDict[key]

                else: #if it is a dictionary in both a and b

                    #merge dict
                    if quacks_like_dict(currentDict_inParentDict[key]) and quacks_like_dict(currentDict_inFinalDict[key]):
                        stack.append((currentDict_inFinalDict[key], currentDict_inParentDict[key],))


    return finalDict