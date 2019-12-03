import cgen as cg
import time as tm

# from abc import abstractmethod
from collections import deque, OrderedDict
from latex import build_pdf

from pdfg.graph import *
from codegen.ast import *
from codegen.setlib import *
from codegen.settings import *

from tools import system

DEBUG=0
WHITE = 1
GRAY = 2
BLACK = 3

class Visitor(object):
    @abstractmethod
    def visit(self, node):
        pass

    def enter(self, node):
        pass                # Default implementation: do nothing...

    def exit(self, node):
        pass                # Default implementation: do nothing...

class BFSVisitor(Visitor):
    def __init__(self, g):
        self._nVisited = 0
        self._graph = g
        self._pred = [-1] * len(g.nodes)
        self._dist = [sys.maxsize] * len(g.nodes)
        self._color = [WHITE] * len(g.nodes)

    def visit(self, node):
        color = self._color
        dist = self._dist
        pred = self._pred

        color[node] = GRAY
        dist[node] = 0

        q = deque([node])
        while len(q) > 0:
            u = q.pop()
            for v in u.neighbors():
                if color[v] == WHITE:
                    dist[v] = dist[u] + 1
                    pred[v] = u
                    color[v] = GRAY
                    q.append(v)
                    v.accept(self)
            color[u] = BLACK

class DFLRVisitor(Visitor):
    def __init__(self):
        self._nVisited = 0

    def visit(self, node):
        self.enter(node)
        for child in node.getChildren():
            self.nVisited += 1
            child.accept(self)
        self.exit(node)

    @property
    def nVisited(self):
        return self._nVisited

    @nVisited.setter
    def nVisited(self, nVisited):
        self._nVisited = nVisited

# TODO: Modify this class to use graphviz package...
class DOTVisitor(DFLRVisitor):
    def __init__(self, out=sys.stdout):
        super().__init__()
        self.out = out

    def enter(self, node):
        if node.isRoot():
            self.out.write("digraph ASTGraph {\n")

    def visit(self, node):
        self.enter(node)
        self.out.write("%d [ label=\"%s\" ];\n" % (self.nVisited, node.getLabel()))

        nodeID = self.nVisited
        for child in node.getChildren():
            self.nVisited += 1
            self.out.write("%d -> %d\n" % (nodeID, self.nVisited))
            child.accept(self)

        self.exit(node)

    def exit(self, node):
        if node.isRoot():
            self.out.write("}\n")

class PDFGVisitor(DFLRVisitor):
    def __init__(self):
        super().__init__()
        self._graphs = []
        self._g = None
        self._nodedict = {}
        self._scalar = ''
        self._fornode = None
        self._level = 0
        self._iters = []

    def enter(self, node):
        #print("Enter node '%s' at level %d" % (node.label, node.level))
        self._nodedict[node.label] = node

        ntype = type(node)
        if ntype is FunctionDecl:                # One graph per function...
            self._g = FlowGraph(node.label)     # Current graph
            self._graphs.append(self._g)

        elif ntype is ParamDecl or ntype is VarDecl:
            dsize = 1
            if node.isPointer():    # If pointer, assume size is most recent scalar...
                dsize = self._scalar
            elif len(node.children) >  0:
                dsize = node.children[0].value
            dnode = DataNode(node.value, attrs={'type': node.getType(), 'size': dsize})
            if dnode.scalar:
                self._scalar = dnode.label
            else:
                self._g.add(dnode)

        elif ntype is ForStmt:
            self._fornode = node
            self._level += 1

    def visit(self, node):
        print("Visit node '%s'" % node.label)
        self.enter(node)
        for child in node.getChildren():
            self.nVisited += 1
            child.accept(self)
        self.exit(node)

    def exit(self, node):
        print("Exit node '%s'" % node.label)
        ntype = type(node)
        if ntype is ForStmt:
            self._fornode = None
            self._level -= 1


class DFGVisitor(Visitor):
    def __init__(self):
        super().__init__()

    def walk(self, g):
        self.setup(g)
        for i in range(g.nrows):
            for j in range(g.ncols):
                if (i, j) in g:
                    node = g[(i, j)]
                    node.accept(self)
        self.finish(g)

    def visit(self, node):
        self.enter(node)
        self.exit(node)

    # Subclasses can implement to satisfy any preconditions...
    def setup(self, g):
        pass

    # Subclasses can implement to satisfy any postconditions...
    def finish(self, g):
        pass


class LatexVisitor(DFGVisitor):
    def __init__(self):
        super().__init__()
        self._header = """\\documentclass{article}
                          \\usepackage{amsmath}
                          \\usepackage{amssymb}
                          \\begin{document}"""
        self._footer = r"\end{document}"
        self._items = []

    def __repr__(self):
        ltx = self._header + "\n"
        for item in self._items:
            ltx += r"\begin{align*}" + "\n" + item + "\n" + r"\end{align*}" + "\n"
        ltx += self._footer
        return ltx

    def enter(self, node):
        #print("Enter node '%s'" % node.label)
        self._items.append(NodeVisitor.create(node).latex())

    def pdf(self, name):
        pdf = build_pdf(str(self))
        pdf.save_to('%s.pdf' % name)
        return pdf

class PolyVisitor(DFGVisitor):
    def __init__(self):
        super().__init__()
        self._items = []
        self._constants = []
        self._statements = []
        self._compiler = ''
        self._name = ''
        self._path = ''

    def __repr__(self):
        return "\n".join(self._items)

    @property
    def compiler(self):
        return self._compiler

    @compiler.setter
    def compiler(self, compiler):
        self._compiler = compiler

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, path):
        self._path = path

    def setup(self, g):
        self._name = g.name
        for const in g._constants:
            self._constants.append(const.name)

    def enter(self, node):
        if len(node.statement) > 0:
            self._statements.append(node.statement)

    def write(self, name=''):
        if len(name) < 1:
            name = self._name
        self._path = '%s/%s.in' % (os.getcwd(), name)
        file = open(self._path, 'w')
        file.write(str(self))
        file.close()
        return self._path

    def build(self):
        if os.path.isfile(self.compiler):
            (out, err) = system.run(self.compiler, str(self))
            if ' error (' in out:
                err = out
            if len(err) > 0:
                raise RuntimeError(err)
        else:
            self.write()
            lines = files.read(self._path.replace('.in', '.out'))
            out = ''.join(lines).rstrip()
        return out

class ISLVisitor(PolyVisitor):
    def __init__(self):
        super().__init__()
        self._compiler = config['iscc']
        self._factory = ISLFactory.instance()

    def enter(self, node):
        super().enter(node)
        islcode = node.domain
        if islcode[0] != '[':
            islcode = '%s -> %s' % (str(self._constants).replace('\'', ''), islcode)

        # Replace uninterpreted functions as ISL does not support them (and Omega is limited)...
        factory = self._factory
        islcode = factory.replaceUFs(islcode, node.graph.symtable)
        node.set = factory.set(islcode)

    def finish(self, g):
        nstatements = len(self._statements)
        if nstatements > 1:
            uset = self._statements[0]
            for i in range(1, nstatements):
                uset = uset.union(self._statements[i])

class OmegaVisitor(PolyVisitor):
    def __init__(self):
        super().__init__()
        self._compiler = config['omega']
        self._union = 'union'

    def setup(self, g):
        super().setup(g)
        # Add symbolics from graph symbol table...
        if len(g.symtable) > 0:
            line = 'symbolic '
            for sname in sorted(g.symtable.keys()):
                symbol = g.symtable[sname]
                line += symbol.name
                if len(symbol) > 0:
                    line += '(%d)' % len(symbol)
                line += ','
            line = line[0:len(line)-1] + ';'
            self._items.append(line)

    def enter(self, node):
        super().enter(node)
        omcode = NodeVisitor.create(node).omega()
        self._items.append(omcode)

    def finish(self, g):
        nstatements = len(self._statements)
        if nstatements > 0:
            cgname = 'union'
            if nstatements > 1:
                union_op = ' %s ' % self._union
                self._items.append('%s := %s;' % (cgname, union_op.join(self._statements)))
            else:
                cgname = self._statements[0]
            self._items.append('codegen(%s);' % cgname)

class CodeGenVisitor(DFGVisitor):
    def __init__(self, lang='C', profile=False, structname=''):
        super().__init__()
        self._lang = lang
        self._includes = ['stdio', 'stdlib', 'stdint']
        self._lines = []
        self._allocs = OrderedDict()
        self._indent = ' ' * 2
        self._path = ''
        self._structname = structname
        self._structs = OrderedDict()
        self._typedefs = [('float', 'real'), ('unsigned', 'itype')]
        # Default 'defines' needed to support polyhedral code gen...
        self._defines = [
            ('min(x,y)', '(((x)<(y))?(x):(y))'),
            ('max(x,y)', '(((x)>(y))?(x):(y))'),
            #('intdiv(x,y)', '((y)>0)?((x)/(y)):0'),
            ('intdiv(x,y)', '((x)/(y))'),
            ('floord(n,d)', 'intdiv((n),(d))'),
            ('offset2(i,j,M)', '((j)+(i)*(M))'),
            ('offset3(i,j,k,M,N)', '((k)+((j)+(i)*(M))*(N))'),
            ('offset4(i,j,k,l,M,N,P)', '((l)+((k)+((j)+(i)*(M))*(N))*(P))'),
            ('array_init(ptr,val,size)', 'for(unsigned __i__=0;__i__<(size);__i__++) (ptr)[__i__]=(val)')]
        self._functions = []
        self.profile = profile

    def __repr__(self):
        return "\n".join(self._lines)

    @property
    def includes(self):
        return self._includes

    @includes.setter
    def includes(self, includes):
        self._includes = includes

    @property
    def defines(self):
        return self._defines

    @defines.setter
    def defines(self, defines):
        self._defines = defines

    @property
    def typedefs(self):
        return self._typedefs

    @typedefs.setter
    def typedefs(self, typedefs):
        self._typedefs = typedefs

    @property
    def functions(self):
        return self._functions

    @functions.setter
    def functions(self, functions):
        self._functions = functions

    @property
    def indent(self):
        return self._indent

    @indent.setter
    def indent(self, indent):
        self._indent = indent

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, path):
        self._path = path

    @property
    def profile(self):
        return self._profile

    @profile.setter
    def profile(self, profile):
        self._profile = profile
        if profile:
            self._includes.append('sys/time')
            self._functions.append(('double get_time()', 'struct timeval tv; gettimeofday(&tv, 0); ' +
                                    'return (double) tv.tv_sec + (((double) tv.tv_usec) * 1E-6);'))

    @property
    def allocs(self):
        return self._allocs

    @property
    def structs(self):
        return self._structs

    @structs.setter
    def structs(self, structs):
        for struct in structs:
            self._structs[struct] = structs[struct]

    @property
    def structname(self):
        return self._structname

    @property
    def lines(self):
        return self._lines

    @lines.setter
    def lines(self, lines):
        self._lines = lines

    def struct_init(self, name, data=()):
        if len(data) < 1:
            data = self._structs[name]
        stype = '%s%s' % (name, StructNode.suffix())
        code = "  %s* %s = calloc(1, sizeof(%s));\n" % (stype, name, stype)
        for member in data:
            code += "  %s->%s = %s;\n" % (name, member, member)
        self.lines.insert(len(self.lines) - 2, code)

    def struct_unroll(self, structname, structdata=()):
        if len(structdata) < 1:
            structdata = self._structs[structname]
        code = ''
        for membername in structdata:
            membertype = structdata[membername]
            if '*' in membertype:
                membertype += ' restrict'
            code += "  %s %s = %s->%s;\n" % (membertype, membername, structname, membername)
        self.lines.insert(2, code)

    def setup(self, g):
        if g.is_parent:
            if len(self._path) < 1:
                self._path = '%s/%s.%s' % (os.getcwd(), g.name, self._lang.lower())

            if len(self.includes) > 0:
                for incfile in self.includes:
                    include = cg.Include('%s.h' % incfile)
                    self._lines.append(str(include))
                self._lines.append('')

            if len(self.defines) > 0:
                for tuple in self.defines:
                    (lhs, rhs) = tuple
                    define = cg.Define(lhs, rhs)
                    self._lines.append(str(define))
                self._lines.append('')

            if len(self._typedefs) > 0:
                for tuple in self._typedefs:
                    (lhs, rhs) = tuple
                    typedef = cg.Typedef(cg.Value(lhs, rhs))
                    self._lines.append(str(typedef))
                self._lines.append('')

            if len(self._functions) > 0:
                for tuple in self._functions:
                    (lhs, rhs) = tuple
                    fxndef = 'inline %s { %s }' % (lhs, rhs)
                    self._lines.append(fxndef)
                self._lines.append('')

            if len(self._structs) > 0:
                for structname in self._structs:
                    struct = self._structs[structname]
                    fields = [cg.Value(struct[name], name) for name in struct]
                    struct = cg.Struct('', fields)
                    typedef = cg.Typedef(cg.Value(struct, '%s%s' % (structname, StructNode.suffix())))
                    self._lines.append(str(typedef).replace('} ;', '}'))
                    self._lines.append('')

            if len(g.constants) > 0:
                for const in g.constants:
                    define = cg.Define(const.name, const.value)
                    self._lines.append(str(define))
                self._lines.append('')

            if len(g.includes) > 0:
                for incfile in g.includes:
                    include = cg.Include('%s.h' % incfile)
                    self._lines.append(str(include))
                self._lines.append('')

        if len(g.subgraphs) < 1:
            func = CGenHelper.functionDecl(g.returntype, g.name, g.params)
            decl = str(func)
            self._lines.append(decl)
            self._lines.append('inline %s' % decl.replace(';', ' {'))

        if len(g.constants) > 0:
            structname = self._structname
            if len(structname) < 1:
                structname = g.name.split('_')[0]
            if structname not in self._structs:
                self._structs[structname] = OrderedDict()
            for const in g.constants:
                self._structs[structname][const.name] = const.type  # Add const to struct for later use...

    def enter(self, node):
        line = NodeVisitor.create(node, self).code()
        return line

    def finish(self, g):
        indent = self._indent
        lines = self._lines

        # Prepend data allocations so that they are done first...
        nallocs = len(self._allocs)
        if nallocs > 0:
            code = "\n".join(self._allocs.values())
            # Find the header and insert after that...
            header = '%s %s' % (g.returntype, g.name)
            ndx = len(lines) - 1
            for i in range(ndx, -1, -1):
                if header in lines[i]:
                    ndx = i
                    break
            lines.insert(ndx + 1, code)

        if len(g.subgraphs) < 1:
            if nallocs > 0:
                if g.returntype == 'void':
                    for alloc in self._allocs:
                        if 'alloc' in self._allocs[alloc]:
                            lines.append('%sfree(%s);' % (indent, alloc))
                # This code is assuming allocated data is being inserted into a struct to be freed by a cleanup graph
                else:
                    alloc = list(self._allocs.items())[0]
                    lines.append('%sreturn %s;' % (indent, alloc[0]))
            lines.append("}  // %s\n" % g.name)

        if g.is_parent:
            # Define main
            params = (Var('argc', type='int'), Var('argv', type='const char **'))
            main = CGenHelper.functionDecl('int', 'main', params)
            lines.append(str(main).replace(';', ' {'))

            if self._profile:
                stmt = cg.Statement('double tstart = get_time()')
                lines.append('%s%s' % (indent, stmt))
                lines.append('')

            lines.append('%s%s();' % (indent, g.name))
            if self._profile:
                lines.append('')
                lines.append(indent + 'fprintf(stderr,"' + g.name + '::%.6lf seconds elapsed\\n", (get_time() - tstart));')
            lines.append('}%s// main\n' % indent)

        self._lines = lines
        if DEBUG:
            print("\n".join(self._lines))

    def write(self):
        file = open(self._path, 'w')
        file.write(str(self))
        file.close()
        return self._path

    def build(self):
        tstart = tm.time()          # Record start time...
        build = config['build']
        compile = '%s %s %s %s %s -o %s' % (build['CXX'], build['CFLAGS'], build['COPTS'], build['CFILES'],
                                            self._path, files.getNameWithoutExt(self._path))
        print(compile)
        (output, error) = system.run(compile)

        if len(error) > 0:
            print(error)
        elif len(output) > 0:
            print(output)
        else:
            print("Successfully built in %g sec." % (tm.time() - tstart))
        return (output, error)

class NodeVisitor(object):
    def __init__(self, node=None, outer=None):
        self._node = node
        self._outer = outer

    @property
    def node(self):
        return self._node

    @property
    def outer(self):
        return self._outer

    @classmethod
    def create(cls, node, outer=None):
        nodetype = type(node)
        if nodetype is StmtNode:
            visitor = StmtNodeVisitor(node, outer)
        elif nodetype is DataNode:
            visitor = DataNodeVisitor(node, outer)
        elif nodetype is StructNode:
            visitor = StructNodeVisitor(node, outer)
        elif nodetype is TempNode:
            visitor = TempNodeVisitor(node, outer)
        elif nodetype is IterNode:
            visitor = IterNodeVisitor(node, outer)
        elif nodetype is FlowGraph:
            visitor = FlowGraphVisitor(node, outer)
        elif nodetype is IEGenGraph:
            visitor = IEGenGraphVisitor(node, outer)
        else:
            raise ValueError("Unknown node type: '%s'" % nodetype)
        return visitor

class StmtNodeVisitor(NodeVisitor):
    def __init__(self, node, outer=None):
        super().__init__(node, outer)

    def code(self):
        iters = []
        statements = []
        node = self._node
        cond = node.condition
        domain = str(node.domain)
        if domain[0] == '[' and '->' in domain:
            domain = domain[domain.find('->') + 3:]

        is_set = '[' in domain and ']' in domain
        if is_set:
            iters = domain.split('[')[1].split(']')[0].replace(' ', '').replace('0', 'z').split(',')
            for stmt in node.statements:
                for iter in iters:
                    cond = re.sub(r"\b%s\b" % iter, '(%s)' % iter, cond)
                    stmt = re.sub(r"\b%s\b" % iter, '(%s)' % iter, stmt)
                statements.append(stmt)
        else:
            statements = node._statements

        stmtlist = ";\\\n".join(statements)
        if len(cond) > 0:
            stmtlist = 'if (%s) {  %s;  }' % (cond, stmtlist)

        define = cg.Define('%s(%s)' % (node.label, ','.join(iters)), stmtlist)
        code = "\n%s" % str(define)

        # TODO: If node reads and writes intersect, reset values. This is mostly a hack in need of refactoring...
        intersection = list(set(node.reads) & set(node.writes))
        if len(intersection) > 0:
            code += "\n"
            for item in intersection:
                name = item.split('(')[0]
                dnode = node.graph[name]
                if dnode.scalar:
                    code += "\n%s = %s;" % (name, dnode.defval)
                else:
                    code += "\nmemset(%s, %s, %s * sizeof(%s));" % (name, dnode.defval, dnode.size, dnode.type)

        if is_set and node.set:
            lines = node.graph.set_factory.codegen(node.set, [node.label]).split("\n")
            if config['skipguard'] and 'if (' in lines[0]:
                braced = (lines[0].find('{') > 0)
                lines = lines[1:]
                if braced:
                    lines = lines[0:len(lines) - 1]
            code = "%s\n\n%s" % (code, "\n".join(lines))
        else:
            code = "%s\n\n  %s();" % (code, node.label)

        code = "%s\n" % code.rstrip()
        self._outer.lines.append(code)
        return code

    def latex(self):
        # \mathbf{Iteration}:\;&I_{dense} \\
        # \mathbf{Statement}:\;&order(i,k,j)\ : c_{map}(i,j) = k \\
        # \mathbf{Mapping}:\;&c_{map}(i,j) : c[i,j] \\
        # \mathbf{Reads}:\;&col(i,k,j) \rightarrow [k] \\
        # \mathbf{Writes}:\;&c(i,k,j) \rightarrow [i,j]
        node = self._node
        ltx = r"\mathbf{Label}:\;&%s \\" % LatexHelper.format(node._label)
        ltx += "\n" + r"\mathbf{Iteration}:\;&%s \\" % LatexHelper.format(node._domain)
        if len(node._statements) > 0:
            ltx += "\n" + r"\mathbf{Statements}:\;&%s \\" % LatexHelper.format("; \\\\\n&".join(node._statements))
        if len(node._datamap) > 0:
            ltx += "\n" + r"\mathbf{DataMap}:\;&%s \\" % LatexHelper.format(node._datamap)
        if len(node._reads) > 0:
            ltx += "\n" + r"\mathbf{Reads}:\;&%s \\" % LatexHelper.format("; \\\\\n&".join(node._reads))
        if len(node._writes) > 0:
            ltx += "\n" + r"\mathbf{Writes}:\;&%s \\" % LatexHelper.format("; \\\\\n&".join(node._writes))
        return ltx

    def omega(self):
        return '%s := %s;' % (self._node._label, self._node._domain)

class DataNodeVisitor(NodeVisitor):
    def __init__(self, node, outer=None):
        super().__init__(node, outer)

    def code(self):
        node = self._node
        outer = self._outer
        indent = '  '
        line = indent
        structname = ''
        varname = node.label.replace('\'', '_prime')
        if node.alloc != MemAlloc.NONE:
            if node.alloc == MemAlloc.STRUCT:
                structname = node.graph.params[0].name
            if node.scalar:
                line += '%s %s = ' % (node.type, varname)
                if node.alloc == MemAlloc.STRUCT:
                    line += '%s->%s' % (structname, varname)
                else:
                    line += node.defval
                line += ';'
            else:
                if node.alloc == MemAlloc.DYNAMIC:
                    # Taking a page from TACO compiler and adding 'restrict' keyword to enable optimizations.
                    line += '%s* restrict %s = calloc(%s,sizeof(%s));' % (node.type, varname, node.size, node.type)
                elif node.alloc == MemAlloc.STRUCT:
                    structname = node.graph.params[0].name
                    line += '%s* restrict %s = %s->%s;' % (node.type, varname, structname, varname)
                else:
                    if node.alloc == MemAlloc.STATIC:
                        line += 'static '
                    line += '%s %s[%s];' % (node.type, varname, node.size)
                    # NOTE: array_init is defined in iegen_util.h.
                    line += "\n%sarray_init(%s, %s, %s);" % (indent, varname, node.defval, node.size)
        outer.allocs[node.label] = line
        return line

    def latex(self):
        # \mathbf{Domain}&: \{ [j_{A}]\;|\;0 \leq j_{A} < NNZ \} \\
        # \mathbf{Range}&: \mathbb{R}  \\
        # \mathbf{Size}&: NNZ
        node = self._node
        ltx = r"\mathbf{Label}:\;&%s \\" % LatexHelper.format(node._label)
        ltx += "\n" + r"\mathbf{Domain}:\;&%s \\" % LatexHelper.format(node._domain)
        ltx += "\n" + r"\mathbf{Range}:\;&%s \\" % LatexHelper.format(node._range)
        ltx += "\n" + r"\mathbf{Size}:\;&%s \\" % LatexHelper.format(node._size)
        return ltx

    def omega(self):
        return '%s := %s;' % (self._node._label, self._node._domain)

class TempNodeVisitor(DataNodeVisitor):
    def __init__(self, node, outer=None):
        super().__init__(node, outer)

    def code(self):
        line = super().code()
        node = self._node
        outer = self._outer
        if len(outer.structs) > 0:
            struct = outer.structs[list(outer.structs.keys())[0]]
            if node.scalar:
                struct[node.label] = node.type
            else: #if node.alloc == MemAlloc.DYNAMIC:
                struct[node.label] = '%s*' % node.type
            #else: # node.alloc == MemAlloc.AUTO || MemAlloc.STATIC:
            #    struct[node.label] = '%s[%s]=%s' % (node.type, node.size, node.defval)
        outer.allocs[node.label] = line
        return line

class StructNodeVisitor(DataNodeVisitor):
    def __init__(self, node, outer=None):
        super().__init__(node, outer)

    def code(self):
        line = super().code()
        self._outer.structs[self._node.label] = self._node.members
        return line

class IterNodeVisitor(NodeVisitor):
    def __init__(self, node, outer=None):
        super().__init__(node, outer)

    def code(self):
        node = self._node
        line = "// %s := %s\n" % (node.label, node.domain)
        self._outer.lines.append(line)
        return line

    def latex(self):
        ltx = "%s = &%s" % (LatexHelper.format(self._node._label), LatexHelper.format(self._node._domain))
        return ltx

    def omega(self):
        return '%s := %s;' % (self._node._label, self._node._domain)

class FlowGraphVisitor(NodeVisitor):
    def __init__(self, graph, outer=None):
        super().__init__(graph, outer)

    def code(self):
        v = CodeGenVisitor(profile=True)
        v.walk(self._node)
        v.write()
        return str(v)

    def latex(self):
        v = LatexVisitor()
        v.walk(self._node)
        v.pdf(self._node.name)
        return str(v)

    def omega(self):
        v = OmegaVisitor()
        v.walk(self._node)
        v.write(self._node.name)
        return str(v)

class IEGenGraphVisitor(FlowGraphVisitor):
    def __init__(self, graph, outer=None):
        super().__init__(graph, outer)

    def code(self):
        graph = self._node
        (srcname, destname) = graph.name.split('_')

        # Walk the setup graph
        vs = CodeGenVisitor(structname=srcname)
        vs.walk(graph.setup)

        # Walk the inspector
        vi = CodeGenVisitor(structname=destname)
        vi.walk(graph.inspector)

        # Unroll source struct so variables will be available to inspector code.
        vi.struct_unroll(srcname, graph.setup[srcname].members)

        # Initialize and return destination struct...
        vi.struct_init(destname)
        vi.lines[-2] = '  return %s;' % destname

        # Walk the executor
        ve = CodeGenVisitor()
        ve.walk(graph.executor)

        # Unroll dest struct so variables will be available to executor code.
        ve.struct_unroll(destname, vi.structs[destname])

        # Setup the main code visitor
        vg = CodeGenVisitor(profile=True)
        vg.typedefs.append(('uint_fast32_t', 'itype'))
        vg.structs = vs.structs
        vg.structs = vi.structs

        # Generate setup code (w/o constants)
        consts = graph.constants
        graph.constants = ()
        vg.setup(graph)
        graph.constants = consts

        # Merge code from all visitors...
        for lines in (vs.lines, vi.lines, ve.lines):
            for line in lines:
                vg.lines.append(line)

        self.finish(vg)
        vg.write()
        return "\n".join(vg.lines)

    def finish(self, cgvis):
        graph = self._node
        setup = graph.setup
        insp = graph.inspector
        exec = graph.executor

        cgvis.finish(graph)             # Finish up the graph (write main)

        indent = cgvis.indent
        (srcname, destname) = graph.name.split('_')

        # 1) Call the setup function (graph)
        mid = ['%s%s' % (indent, cg.LineComment('1) Call the setup function'))]
        args = ['argv[%d]' % (i + 1) for i in range(len(setup.params))]
        retval = ''
        if len(setup.returntype) > 0:
            retval = '%s %s' % (setup.returntype, srcname)
        stmt = CGenHelper.functionCall(setup.name, args, retval)
        mid.append("%s%s\n" % (indent, stmt))

        # 2) Call the inspector...
        mid.append('%s%s' % (indent, '// 2) Call the inspector'))
        retval = ''
        if len(insp.returntype) > 0:
            retval = '%s %s' % (insp.returntype, destname)

        # Time the inspector:
        if cgvis.profile:
            mid.append('%s%s' % (indent, 'double tinsp = get_time();'))

        # Assume 1st arg is struct from inspector, and remaining parameters are command line args
        args = [srcname]
        for i in range(1, len(insp.params)):
            argval = 'argv[%d]' % (i + 1)
            argtype = insp.params[i].type
            if 'char' not in argtype:
                argval = 'ato%s(%s)' % (argtype[0], argval)
            args.append(argval)
        stmt = CGenHelper.functionCall(insp.name, args, retval)
        mid.append("%s%s" % (indent, stmt))

        if cgvis.profile:
            mid.append(indent + 'fprintf(stderr,"' + insp.name + '::%.6lf seconds elapsed\\n", (get_time() - tinsp));')

        # 3) Call the executor...
        mid.append("\n%s%s" % (indent, '// 3) Call the executor'))
        # Time the executor:
        if cgvis.profile:
            mid.append('%s%s' % (indent, 'double texec = get_time();'))

        stmt = CGenHelper.functionCall(exec.name, [destname], '')
        mid.append('%s%s' % (indent, stmt))
        if cgvis.profile:
            mid.append(indent + 'fprintf(stderr,"' + exec.name + '::%.6lf seconds elapsed\\n", (get_time() - texec));')

        # Insert the middle code in between the top and bottom
        ndx = cgvis.lines.index('%s%s();' % (indent, graph.name))
        top = cgvis.lines[0:ndx]
        bot = cgvis.lines[ndx+1:]

        lines = []
        for list in (top, mid, bot):
            for line in list:
                lines.append(line)

        cgvis.lines = lines
        print(cgvis)

class CGenHelper(object):
    @staticmethod
    def assign(type, left, right):
        return cg.Assign(cg.Value(type, left), right)

    @staticmethod
    def functionDecl(type, name, params):
        fname = cg.Value(type, name)
        params = [cg.Value(param.type, param.name) for param in params]
        return cg.FunctionDeclaration(fname, params)

    @staticmethod
    def functionCall(name, args, lhs=''):
        stmt = ''
        if len(lhs) > 0:
            stmt = '%s = ' % lhs
        stmt = '%s%s(%s)' % (stmt, name, ', '.join(args))
        return cg.Statement(stmt)
