import os
import pprint

path = os.path.dirname(__file__)
attrFavoritesFile = path+'/'+'attrFavoritesDictionary.py'

def addAttrToFavorites(self, nodeType, attributeName, mode=None):

    favoritesDict = getAttrFavorites()

    if not isinstance(favoritesDict, dict):
        favoritesDict = {}

    if not nodeType in favoritesDict:
        favoritesDict[nodeType] = {'source':{}, 'destination':{},}

    if mode == 'source':
        attrDict = favoritesDict[nodeType]['source']

    elif mode == 'destination':
        attrDict = favoritesDict[nodeType]['destination']

    if not attributeName in attrDict:
        attrDict[attributeName] = True

    pp = pprint.PrettyPrinter(indent=4)
    writeText = pp.pformat(favoritesDict)

    f = open(filePath, 'w')
    f.write(writeText)
    f.close()


def getAttrFavorites():
    filePath = attrFavoritesFile

    try:
        if not os.path.exists(filePath):
            filePath = attrFavoritesFile
            f = open(filePath, 'w')
            f.write('{}')
            f.close()

        f = open(filePath, 'r')
        fileText = f.read()
        f.close()
        return eval(fileText)

    except:
        pymel.error('failed to read attrFavorites')
        f.close()
