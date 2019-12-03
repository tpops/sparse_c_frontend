__author__ = 'edavis'

import io
import xml.etree.cElementTree as et
import xml.dom.minidom as md

ENCODING = 'utf-8'

def nodeToDict(node):
    text = node.text
    if text is not None:
        text = text.strip()
    else:
        text = ''

    data = {'tag_': node.tag, 'innertext_': text}
    for (key, val) in node.attrib.items():
        data[key] = val

    for child in node.getchildren():
        tag = child.tag
        if tag not in data:
            data[tag] = []
        data[tag].append(nodeToDict(child))

    return data

class XmlObject(object):
    def __init__(self, tag='', attribs={}, text='', parent=None):
        self.tag = tag
        self.setAttribs(attribs)

        if parent is None:
            self.node = et.Element(tag, self.attribs)
        else:
            self.node = et.SubElement(parent.node, tag, self.attribs)

        self.node.text = text
        self.path = ''

    def setAttribs(self, attribs):
        newAttrs = {}
        for key in attribs.keys():
            val = attribs[key]
            newAttrs[str(key)] = str(val)       # ElementTree requires all keys and values to be strings.

        self.attribs = newAttrs

        return newAttrs

    def __str__(self):
        bio = io.BytesIO()
        et.ElementTree(self.node).write(bio)
        bytes = bio.getvalue()

        return bytes.decode(ENCODING)

    def read(self, path):
        self.path = path
        tree = et.parse(path)
        self.node = tree.getroot()
        return self.node

    def parse(self, data):
        self.node = et.fromstring(data)
        return self.node

    def write(self, path):
        self.path = path

        pathIsStr = isinstance(path, str)
        if pathIsStr:
            file = open(path, 'w')
        else:
            file = path

        xmlStr = self.prettify()

        # Turns out the antiquated ParamDataUpdater code does not like the xml version line so need to remove it.
        index = xmlStr.find('?>')
        if index > 0:
            xmlStr = xmlStr[index + 3:]

        file.write(xmlStr)

        if pathIsStr:
            file.close()

    def prettify(self):
        reparsed = md.parseString(str(self))
        return reparsed.toprettyxml(indent='')

    def toDict(self):
        aDict = {}
        if self.node is not None:
            aDict = nodeToDict(self.node)

        return aDict
