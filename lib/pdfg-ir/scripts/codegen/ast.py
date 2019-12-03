import os
try:
    import clang.cindex as clindex
except:
    print("WARN: clang module NOT loaded.")

from graphviz import *
from tools import files

class Node(object):
    def __init__(self, value='', start=(0,0), end=(0,0), level=0, label='Node'):
        self.value = value
        self.start = start
        self.end = end
        self.level = level
        self.label = label
        self.parent = None
        self.type = None
        self.children = []
        self.attributes = {}

    def getChildren(self):
        return self.children

    def addChild(self, child):
        if (self != child):     # Prevent cycles...
            child.setParent(self)
            self.children.append(child)

    def insertChild(self, child, index):
        child.setParent(self)
        self.children.insert(index, child)

    def getParent(self):
        return self.parent

    def setParent(self, parent):
        self.parent = parent

    def getValue(self):
        return self.value

    def setValue(self, value):
        self.value = value

    def getAttr(self, key):
        return self.attributes[key]

    def setAttr(self, key, value):
        self.attributes[key] = value

    def getLabel(self):
        label = self.label
        if len(self.value) > 0:
            label += "\\n" + self.value.replace('"','\\"')
        return label

    def getType(self):
        type = ''
        if self.type is not None and self.type.kind != clindex.TypeKind.INVALID:
             type = self.type.spelling
        return type

    def isPointer(self):
        return self.type.kind == clindex.TypeKind.POINTER

    def isRoot(self):
        return self.parent is None

    def isLeaf(self):
        return len(self.children) == 0

    def accept(self, visitor):
        visitor.visit(self)

class Program(Node):
    def __init__(self, value='', start=(0,0), end=(0,0), level=0, label='Program'):
        super().__init__(value, start, end, level, label)

class UsingDir(Node):
    def __init__(self, value='', start=(0,0), end=(0,0), level=0, label='UsingDir'):
        super().__init__(value, start, end, level, label)

class Namespace(Node):
    def __init__(self, value='', start=(0,0), end=(0,0), level=0, label='Namespace'):
        super().__init__(value, start, end, level, label)

class NamespaceRef(Node):
    def __init__(self, value='', start=(0,0), end=(0,0), level=0, label='NamespaceRef'):
        super().__init__(value, start, end, level, label)

class TypeRef(Node):
    def __init__(self, value='', start=(0,0), end=(0,0), level=0, label='TypeRef'):
        super().__init__(value, start, end, level, label)

class Statement(Node):
    def __init__(self, value='', start=(0,0), end=(0,0), level=0, label='Statement'):
        super().__init__(value, start, end, level, label)

class CompoundStmt(Statement):
    def __init__(self, value='', start=(0,0), end=(0,0), level=0, label='CompoundStmt'):
        super().__init__(value, start, end, level, label)

class DeclStmt(Statement):
    def __init__(self, value='', start=(0,0), end=(0,0), level=0, label='DeclStmt'):
        super().__init__(value, start, end, level, label)

class IfStmt(Statement):
    def __init__(self, value='', start=(0,0), end=(0,0), level=0, label='IfStmt'):
        super().__init__(value, start, end, level, label)

class ForStmt(Statement):
    def __init__(self, value='', start=(0,0), end=(0,0), level=0, label='ForStmt'):
        super().__init__(value, start, end, level, label)

class ReturnStmt(Statement):
    def __init__(self, value='', start=(0,0), end=(0,0), level=0, label='ReturnStmt'):
        super().__init__(value, start, end, level, label)

class NullStmt(Statement):
    def __init__(self, value='', start=(0,0), end=(0,0), level=0, label='NullStmt'):
        super().__init__(value, start, end, level, label)

class LabelStmt(Statement):
    def __init__(self, value='', start=(0,0), end=(0,0), level=0, label='LabelStmt'):
        super().__init__(value, start, end, level, label)

class Literal(Node):
    def __init__(self, value='', start=(0,0), end=(0,0), level=0, label='Literal'):
        super().__init__(value, start, end, level, label)

class FloatLiteral(Literal):
    def __init__(self, value='', start=(0,0), end=(0,0), level=0, label='FloatLiteral'):
        super().__init__(value, start, end, level, label)

class IntLiteral(Literal):
    def __init__(self, value='', start=(0,0), end=(0,0), level=0, label='IntLiteral'):
        super().__init__(value, start, end, level, label)

class StringLiteral(Literal):
    def __init__(self, value='', start=(0,0), end=(0,0), level=0, label='StringLiteral'):
        super().__init__(value, start, end, level, label)

class Operator(Node):
    def __init__(self, value='', start=(0,0), end=(0,0), level=0, label='Operator'):
        super().__init__(value, start, end, level, label)

class UnaryOper(Operator):
    def __init__(self, value='', start=(0,0), end=(0,0), level=0, label='UnaryOper'):
        super().__init__(value, start, end, level, label)

class BinaryOper(Operator):
    def __init__(self, value='', start=(0,0), end=(0,0), level=0, label='BinaryOper'):
        super().__init__(value, start, end, level, label)

class CompoundAssignOper(Operator):
    def __init__(self, value='', start=(0,0), end=(0,0), level=0, label='CompoundAssignOper'):
        super().__init__(value, start, end, level, label)

class Declaration(Node):
    def __init__(self, value='', start=(0,0), end=(0,0), level=0, label='Declaration'):
        super().__init__(value, start, end, level, label)

class FunctionDecl(Declaration):
    def __init__(self, value='', start=(0,0), end=(0,0), level=0, label='FunctionDecl'):
        super().__init__(value, start, end, level, label)

class ParamDecl(Declaration):
    def __init__(self, value='', start=(0,0), end=(0,0), level=0, label='ParamDecl'):
        super().__init__(value, start, end, level, label)

class VarDecl(Declaration):
    def __init__(self, value='', start=(0,0), end=(0,0), level=0, label='VarDecl'):
        super().__init__(value, start, end, level, label)

class StructDecl(Declaration):
    def __init__(self, value='', start=(0,0), end=(0,0), level=0, label='StructDecl'):
        super().__init__(value, start, end, level, label)

class ClassDecl(Declaration):
    def __init__(self, value='', start=(0,0), end=(0,0), level=0, label='ClassDecl'):
        super().__init__(value, start, end, level, label)

class FieldDecl(Declaration):
    def __init__(self, value='', start=(0,0), end=(0,0), level=0, label='FieldDecl'):
        super().__init__(value, start, end, level, label)

class TypedefDecl(Declaration):
    def __init__(self, value='', start=(0,0), end=(0,0), level=0, label='TypedefDecl'):
        super().__init__(value, start, end, level, label)

class AccessSpecDecl(Declaration):
    def __init__(self, value='', start=(0,0), end=(0,0), level=0, label='AccessSpecDecl'):
        super().__init__(value, start, end, level, label)

class Expression(Node):
    def __init__(self, value='', start=(0,0), end=(0,0), level=0, label='Expression'):
        super().__init__(value, start, end, level, label)

class Condition(Expression):
    def __init__(self, value='', start=(0,0), end=(0,0), level=0, label='Condition'):
        super().__init__(value, start, end, level, label)

class DeclRefExpr(Expression):
    def __init__(self, value='', start=(0,0), end=(0,0), level=0, label='DeclRefExpr'):
        super().__init__(value, start, end, level, label)

class UnexposedExpr(Expression):
    def __init__(self, value='', start=(0,0), end=(0,0), level=0, label='UnexposedExpr'):
        super().__init__(value, start, end, level, label)

class ArraySubscriptExpr(Expression):
    def __init__(self, value='', start=(0,0), end=(0,0), level=0, label='ArraySubscriptExpr'):
        super().__init__(value, start, end, level, label)

class ParenExpr(Expression):
    def __init__(self, value='', start=(0,0), end=(0,0), level=0, label='ParenExpr'):
        super().__init__(value, start, end, level, label)

class CallExpr(Expression):
    def __init__(self, value='', start=(0,0), end=(0,0), level=0, label='CallExpr'):
        super().__init__(value, start, end, level, label)

class NullExpr(Expression):
    def __init__(self, value='', start=(0,0), end=(0,0), level=0, label='NullExpr'):
        super().__init__(value, start, end, level, label)

class MemberRefExpr(Expression):
    def __init__(self, value='', start=(0,0), end=(0,0), level=0, label='MemberRefExpr'):
        super().__init__(value, start, end, level, label)

class Method(Node):
    def __init__(self, value='', start=(0,0), end=(0,0), level=0, label='Method'):
        super().__init__(value, start, end, level, label)

class Constructor(Method):
    def __init__(self, value='', start=(0,0), end=(0,0), level=0, label='Constructor'):
        super().__init__(value, start, end, level, label)

class Destructor(Method):
    def __init__(self, value='', start=(0,0), end=(0,0), level=0, label='Destructor'):
        super().__init__(value, start, end, level, label)

class Tree(object):
    @staticmethod
    def fromDOT(path):
        tree = None
        if files.exists(path):
            lines = files.read(path)
            src = ''.join(lines)
            dot = Source(src)
            name = files.getNameWithoutExt(path)
            tree = Tree(name, dot=dot)
        else:
            raise FileNotFoundError(path)

        return tree

    def __init__(self, name='', root=Node(), dot=None):
        self.name = name
        self.root = root
        self.dot = dot

    def getName(self):
        return self.name

    def getRoot(self):
        return self.root
