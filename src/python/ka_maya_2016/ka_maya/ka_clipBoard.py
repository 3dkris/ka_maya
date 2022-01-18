import maya.cmds as cmds
import maya.mel as mel
import pymel.core as pymel

import os
import pickle

CLIPBOARD_FILE = os.path.join(cmds.internalVar(userPrefDir=True), 'ka_clipBoard.p')

def add(key, pyObject):
    """
    Adds item to the clipboard.

    Args:
        key (string): the key for the item being added to the clipBoardDict

        pyObject (object): item to be stored
    """

    clipBoardData = _getClipBoardData()
    clipBoardData[key] = pyObject
    pickle.dump( clipBoardData, open(_getClipBoardFile(), "wb") )
    return pyObject

def get(key, defaultValue=None):
    """
    Gets item from the clipboard.

    Args:
        key (string): the key for the item being retrieved from the clipBoardDict

        defaultValue (object): item to be returned if key does not exist in the clipBoardDict

    Returns:
        (object): object found for given key. if no object found, than the defaultValue parameter is returned
    """

    clipBoardData = _getClipBoardData()
    return clipBoardData.get(key, defaultValue)

def replace(key, pyObject):
    """
    similar to the add command, except that it will reset the clip board and add the item.

    This function is faster than add

    Args:
        key (string): the key for the item being added to the clipBoardDict

        pyObject (object): item to be stored
    """

    pickle.dump( {key:pyObject}, open(_getClipBoardFile(), "wb") )


def _getClipBoardFile():
    userPrefDir = cmds.internalVar(userPrefDir=True)
    return os.path.join(userPrefDir, 'ka_clipBoard.p')

def _getClipBoardData():
    #clipBoardFile = _getClipBoardFile()

    try:
        clipBoardData = pickle.load( open( CLIPBOARD_FILE, "rb" ) )
    except:
        pymel.warning('clipBoard experienced an error, and has been reset')
        clipBoardData = {}
        pickle.dump( {}, open( CLIPBOARD_FILE, "wb" ) )

    return clipBoardData