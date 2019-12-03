__author__ = 'edavis'

import json as js
#import jsonpickle as jp

from tools import files

def parseFile(jsonFile):
    lines = files.read(jsonFile)

    data = {}
    if len(lines) > 0:
        data = parse(("\n").join(lines))

    return data

def parse(jsonStr):
    return js.loads(jsonStr)

def writeFile(jsonFile, jsonData):
    files.write(jsonFile, write(jsonData))

def write(jsonData):
    return js.dumps(jsonData)

# def encode(obj):
#     return jp.encode(obj)
#
# def decode(data):
#     return jp.decode(data)
