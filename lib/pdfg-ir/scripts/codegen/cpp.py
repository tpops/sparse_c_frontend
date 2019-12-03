import os
import sys
import clang.cindex as clindex

from codegen.ast import *
from codegen.factory import ASTFactory

from tools import files


def verbose(*args, **kwargs):
    # filter predicate for show_ast: show all
    return True

def noSystemIncludes(cursor, level):
    # filter predicate for show_ast: filter out verbose stuff from system include files
    curFile = cursor.location.file
    return (level != 1) or (curFile is not None and not curFile.name.startswith('/usr')) #/include'))

def mainFileOnly(cursor, level):
    # filter predicate for show_ast: filter out verbose stuff from system include files
    curFile = cursor.location.file
    return (level != 1) or (curFile is not None and not curFile.name.startswith('/usr')) #/include'))

def isValidType(type):
    # used to check if a cursor has a type
    isValid = True

    try:
        isValid = (type.kind != clindex.TypeKind.INVALID)
    except ValueError as ve:
        stop=1
    except AttributeError as ae:
        if 'struct' in type.spelling:
            type.kind = clindex.CursorKind.STRUCT_DECL
        isValid = False

    return isValid

def qualifiers(type):
    # set of qualifiers of a type
    qualSet = set()
    if type.is_const_qualified():
        qualSet.add('const')
    if type.is_volatile_qualified():
        qualSet.add('volatile')
    if type.is_restrict_qualified():
        qualSet.add('restrict')

    return qualSet

def showLevel(level, *args):
    # pretty print an indented line
    print('\t' * level + ' '.join(map(str, args)))

def showType(type, level, title):
    # pretty print type AST
    showLevel(level, title, str(type.kind), ' '.join(qualifiers(type)))
    if isValidType(type.get_pointee()):
        showType(type.get_pointee(), level + 1, 'points to:')

# Defaulting level to zero first, but will change to 1 if does not work.
def showAST(cursor, filterPred=verbose, level=0):
    # pretty print cursor AST
    if filterPred(cursor, level):
        showLevel(level, cursor.kind, cursor.spelling, cursor.displayname, cursor.location)
        if isValidType(cursor.type):
            showType(cursor.type, level + 1, 'type:')
            showType(cursor.type.get_canonical(), level + 1, 'canonical type:')

        for child in cursor.get_children():
            showAST(child, filterPred, level + 1)


# Defaulting level to zero first, but will change to 1 if does not work.
def getAST(parser, cursor, filterPred=verbose, level=0, node=None):
    if filterPred(cursor, level):
        showLevel(level, cursor.kind, cursor.spelling, cursor.displayname, cursor.location)
        if isValidType(cursor.type):
            showType(cursor.type, level + 1, 'type:')
            #showType(cursor.type.get_canonical(), level + 1, 'canonical type:')

        # Convert AST to something I can use...
        val = cursor.spelling
        ext = cursor.extent
        start = (ext.start.line, ext.start.column)
        stop = (ext.end.line, ext.end.column)

        # Only extract values for nodes that start and stop on the same line for now...
        if len(val) < 1 and start[0] > 0 and start[0] == stop[0]:
            lines = parser.read(cursor.location.file.name)
            line = (lines[start[0] - 1:stop[0]])[0]
            val = line[start[1] - 1:stop[1] - 1]

        newNode = ASTFactory.getNode(cursor.kind, val, level, start, stop, cursor.type)
        if newNode is not None:
            node = newNode

        for curChild in cursor.get_children():
            astChild = getAST(parser, curChild, filterPred, level + 1, node)
            if astChild is not None:
                node.addChild(astChild)

        if node.label.startswith('ForStmt') and len(node.children) < 4:
            fixForNode(parser, node)
    else:
        sys.stderr.write("Skipping node '%s' at %s.\n" % (cursor.kind, cursor.location.file.name))

    return node

def fixForNode(parser, node):
    # For some reason, Clang skips the loop condition...
    child1 = node.children[0]
    child2 = node.children[1]
    start = (child1.end[0], child1.end[1] + 1)
    stop = (child2.start[0], child2.start[1] - 1)
    line = (parser.lines[start[0] - 1:stop[0]])[0]
    val = line[start[1] - 1:stop[1] - 1]

    newChild = Condition()
    newChild.value = val
    newChild.level = child1.level
    newChild.start = start
    newChild.end = stop
    newChild.type = child1.type

    node.insertChild(newChild, 1)


class CppParser(object):
    def __init__(self, path=''):
        self.index = None
        self.unit = None
        self.ast = None
        self.includes = []
        self.lines = []
        self.files = {}

        clindex.Config.set_library_path('%s/lib' % os.environ['LLVMHOME'])

        self.path = path
        if os.path.exists(path):
            self.parse()
        else:
            raise FileNotFoundError(self.path)

    def read(self, path):
        if path not in self.files:
            self.files[path] = files.read(path)

        return self.files[path]

    def parse(self):
        print('Parsing "%s"...' % self.path)
        self.read(self.path)
        self.index = clindex.Index.create()
        self.unit = self.index.parse(self.path)

        for incudeFile in self.unit.get_includes():
            self.includes.append(incudeFile)

        cursor = self.unit.cursor
        root = getAST(self, cursor, noSystemIncludes)
        #clindex.Cursor_visit(self.unit.cursor, clindex.Cursor_visit_callback(codeVisitor), None)

        name = files.getNameWithoutExt(self.unit.spelling)
        self.ast = Tree(name, root)

        return self.ast
