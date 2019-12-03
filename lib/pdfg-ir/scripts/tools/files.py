__author__ = 'edavis'

import os
import csv
import shutil
import stat
import zipfile
#import xml.etree.ElementTree as ET

from tools import strings

def exists(path):
    return os.path.exists(path)


def getSize(path):
    statData = os.stat(path)
    return statData[6]


def accTime(path):
    statData = os.stat(path)
    return statData[7]


def modTime(path):
    statData = os.stat(path)
    return statData[8]


def creationTime(path):
    statData = os.stat(path)
    return statData[9]


def copy(src, dst):
    shutil.copy(src, dst)


def move(src, dst):
    shutil.move(src, dst)


def remove(file):
    os.remove(file)


def isDir(path):
    return os.path.isdir(path)


def zip(path):
    format = 'zip'
    zfPath = path + '.' + format
    zipFile = zipfile.ZipFile(zfPath, 'w', format)
    zipFile.write(path, (os.path.split(path))[1])
    zipFile.close()


def list(dir, pattern=''):
    files = os.listdir(dir)
    if len(pattern) > 0:
        subset = []
        for file in files:
            if strings.isMatch(file, pattern):
                subset.append(file)

        files = subset

    files.sort()

    fullList = []
    for file in files:
        fullList.append("%s/%s" % (dir, file))

    return fullList


def getDir(path):
    return os.path.dirname(path)


def getName(path):
    (dir, name) = os.path.split(path)

    return name


def getExt(path):
    ext = ''
    pos = path.rfind('.')
    if pos > 0:
        ext = path[pos + 1:]

    return ext


def getPathWithoutExt(path):
    pathNoExt = path
    dotIndex = path.rfind('.')
    if dotIndex >= 0:
        pathNoExt = pathNoExt[0:dotIndex]

    return pathNoExt


def getNameWithoutExt(path):
    nameNoExt = getName(path)
    dotIndex = nameNoExt.rfind('.')
    if dotIndex >= 0:
        nameNoExt = nameNoExt[0:dotIndex]
    return nameNoExt


def read(path):
    lines = []
    if exists(path):
        f = open(path, 'r')
        lines = f.readlines()
        f.close()

    return lines


def readCSV(path, delim=',', asDict=False):
    f = open(path, 'r')

    r = None
    if asDict:
        r = csv.DictReader(f, delimiter=delim)
    else:
        r = csv.reader(f, delimiter=delim)

    rows = []
    for row in r:
        rows.append(row)

    f.close()

    return rows


def write(path, lines):
    f = open(path, 'w')
    f.writelines(lines)
    f.close()


def writeCSV(path, rows):
    f = open(path, 'w')
    w = csv.writer(f)

    for row in rows:
        w.writerow(row)

    f.close()


def append(path, lines):
    f = open(path, 'a')
    f.writelines(lines)
    f.close()


def makedir(newDir):
    if not os.path.isdir(newDir):
        if not os.path.isfile(newDir):
            head, tail = os.path.split(newDir)
            if head and not os.path.isdir(head):
                makedir(head)
            if tail:
                os.mkdir(newDir)

        else:
            raise OSError("File named '%s' already exists." % newDir)


def chmod(path, mode=''):
    # TODO: Implememt mode logic...
    os.chmod(path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
