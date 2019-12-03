import sys
import jsonpickle as jp
import networkx as nx
import graphviz as gv

from enum import Enum
from codegen.factory import IEGenFactory, ISLFactory
from codegen.setlib import *

_DEBUG_ = 0

class MemAlloc(Enum):
    NONE = 0,
    AUTO = 1,
    STATIC = 2,
    DYNAMIC = 3,
    STRUCT = 4

class FlowGraph(object):
    def __init__(self, name='', nodes=[], edges=[], comps=[], constants=(), parent=None, subgraphs=[]):
        self._name = name
        self._path = ''
        self._nodelist = []
        self._edgelist = []
        self._nodedict = {}
        self._comps = []
        self._nodefac = NodeFactory()
        self._setfac = IEGenFactory.instance()
        self._nx = None     # nx.DiGraph()
        self._dot = gv.Digraph()
        self._row = 0
        self._col = 0
        self._nrows = 0
        self._ncols = 0
        self._parent = parent
        self._subgraphs = subgraphs
        self._params = []
        self._includes = []
        self._returntype = 'void'
        self._symtable = {}
        self._ufregex = re.compile(r'\w+\(', re.IGNORECASE)
        self.nodes = nodes
        self.edges = edges
        self.comps = comps
        self.constants = constants

    def to_json(self):
        return jp.encode(self)

    @classmethod
    def from_json(cls, json):
        return jp.decode(json)

    def to_file(self, file=''):
        if len(file) < 1:
            file = '%s.json' % self.name
        fp = open(file, 'w')
        fp.write(self.to_json())
        fp.close()
        return file

    @classmethod
    def from_file(cls, file):
        fp = open(file, 'r')
        lines = fp.readlines()
        fp.close()
        return cls.from_json("\n".join(lines))

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def dot(self):
        return self._dot

    @property
    def nodes(self):
        return self._nodelist

    @nodes.setter
    def nodes(self, rows=[]):
        self._nrows = len(rows)
        i = 0
        for row in rows:
            self._ncols = max(self._ncols, len(row))
            j = 0
            for tuple in row:
                (type, label) = tuple
                node = self._nodefac.get(type, label)
                node['row'] = i
                node['col'] = j
                if j < len(self._comps):
                    node['comp'] = self._comps[j]
                nodekey = '%d,%d' % (i, j)
                self._nodedict[nodekey] = node
                self._nodelist.append(node)
                node.graph = self
                j += 1
            i += 1

    @property
    def edges(self):
        return self._edgelist

    @edges.setter
    def edges(self, edges=[]):
        for tuple in edges:
            (src, dest) = tuple
            if src in self and dest in self:
                edge = Edge(self[src], self[dest])
                self._edgelist.append(edge)
                edge.graph = self

    @property
    def comps(self):
        return self._comps

    @comps.setter
    def comps(self, comps):
        self._comps = comps

    @property
    def constants(self):
        return self._constants

    def addconst(self, const):
        self._constants.append(const)
        self._symtable[const.name] = const

    @constants.setter
    def constants(self, constants):
        self._constants = []
        for const in constants:
            self.addconst(const)

    @property
    def constnames(self):
        return [const.name for const in self._constants]

    @property
    def functions(self):
        funcs = []
        for symbol in self._symtable.values():
            if type(symbol) is Function:
                funcs.append(symbol)
        return funcs

    @functions.setter
    def functions(self, functions):
        for func in functions:
            self._symtable[func.name] = func

    @property
    def params(self):
        return self._params

    @params.setter
    def params(self, params):
        for param in params:
            self._symtable[param.name] = param
        self._params = params

    @property
    def paramnames(self):
        return [param.name for param in self._params]

    @property
    def includes(self):
        return self._includes

    @includes.setter
    def includes(self, includes):
        self._includes = includes

    @property
    def symtable(self):
        return self._symtable

    @symtable.setter
    def symtable(self, symbols):
        self._symtable = symbols

    @property
    def nrows(self):
        return self._nrows

    @property
    def ncols(self):
        return self._ncols

    @property
    def is_parent(self):
        return self._parent is None

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, parent):
        self._parent = parent

    @property
    def subgraphs(self):
        return self._subgraphs

    @property
    def returntype(self):
        return self._returntype

    @returntype.setter
    def returntype(self, type):
        self._returntype = type

    @property
    def node_factory(self):
        return self._nodefac

    @property
    def set_factory(self):
        return self._setfac

    def __contains__(self, key):
        if type(key) is tuple:         # Check if it's a tuple (backward compatibility)
            (x, y) = key
            return '%d,%d' % (x, y) in self._nodedict
        else:
            return key in self._symtable or key in self._nodelist

    def __getitem__(self, key):
        if type(key) is tuple:
            (x, y) = key
            key = '%d,%d' % (x, y)
            item = self._nodedict[key]
        else:
            item = self._symtable[key]
        return item

    def __setitem__(self, key, val):
        if type(key) is tuple:
            (x, y) = key
            key = '%d,%d' % (x, y)
            self._nodedict[key] = val
        else:
            self._symtable[key] = val

    def add(self, item):
        itype = type(item)
        if itype is StmtNode or itype is DataNode or itype is TempNode or itype is IterNode or itype is StructNode:
            self.addnode(item)
        elif itype is Edge:
            self.addedge(item)
        else:
            raise ValueError("Invalid FlowGraph object: '%s'" % str(item))

    def addnode(self, node):
        node['row'] = self._row
        node['col'] = self._col
        nodekey = '%d,%d' % (node['row'], node['col'])
        self._nodedict[nodekey] = node
        self._nodelist.append(node)
        self._col += 1
        node.graph = self
        self[node.label] = node

        # Add uninterpreted functions to symbol table...
        matches = set(self._ufregex.findall(str(node.domain)))
        if len(matches) > 0:
            for match in matches:
                name = match[0:len(match)-1]
                self._symtable[name] = Function(name, [''])     # Default to 1 arg for now

    def addedge(self, edge):
        (src, dest) = (edge.src, edge.dest)
        if src in self and dest in self:
            if type(src) is tuple:
                edge = Edge(self[src], self[dest])
            # TODO: This is making all lines dotted, need to resolve
            # if type(edge.src) is IterNode:
            #     edge['style'] = 'dotted'
            self._edgelist.append(edge)
            edge.graph = self
            self[edge.label] = edge

    def newrow(self):
        self._row += 1
        self._nrows = self._row
        self._ncols = max(self._col, self._ncols)
        self._col = 0

    def node(self, x, y):
        nodekey = '%d,%d' % (x, y)
        return self._nodedict[nodekey]

    def nxgraph(self):
        g = nx.DiGraph()
        for node in self._nodelist:
            g.add_node(node.label, node.attrs)
        for edge in self._edgelist:
            g.add_edge(edge.src.label, edge.dest.label, edge.attrs)
        self._nx = g

        return g

    def draw(self, view=True, nx=False):
        if nx:
            self.nxgraph()
            nx.draw_networkx(self.nxgraph())
        else:
            self._dot.render(self._name, view=view)

    def read(self, path='', nx=False):
        if len(path) < 1:
            path = '%s.dot' % self.name
        if nx:
            self._nx = nx.read_dot(path)
        else:
            self._dot = gv.Source.from_file(path)

    def save(self):
        """
        # DOT graph captions using 'xlabel' attribute:
        digraph g {
            forcelabels=true;
            a [label="Birth of George Washington", xlabel="See also: American Revolution"];
            b [label="Main label", xlabel="Additional caption"];
            a-> b;
        }
        :return:
        """
        idx = 0
        top = self._dot
        top.attr('graph', forcelabels='true')

        for i in range(self._nrows):
            cluster = gv.Digraph(name='cluster%d' % i)
            cluster.attr('graph', color='white')
            cluster.attr('graph', style='filled')
            self._dot = cluster

            for j in range(self._ncols):
                coords = (i, j)
                if coords in self:
                    node = self[coords]
                    # idx = i * self._ncols + j
                    node.name = str(idx)
                    idx += 1
                    dot = node.dot
                    if _DEBUG_:
                        sys.stderr.write("node: {name='%s', label='%s', color='%s', shape='%s', i=%d, j=%d}\n" %
                                        (node.name, node.label, node._attrs['color'], node._attrs['shape'], i, j))
            top.subgraph(self._dot)

        self._dot = top
        for edge in self.edges:
            dot = edge.dot

    def graphgen(self):
        self.save()
        return self._dot

    def codegen(self):
        from codegen.visit import FlowGraphVisitor
        v = FlowGraphVisitor(self)
        return v.code()

    def write(self, path=''):
        self.save()
        if len(path) < 1:
            path = '%s.dot' % self.name
        fp = open(path, 'w')
        fp.write(self.dot.source)
        fp.close()

    def to_pdf(self, path=''):
        if len(path) < 1:
            path = '%s.pdf' % self.name
        #curreng = self._dot.engine
        #currfmt = self._dot.format
        #self._dot.format = 'circo'
        self._dot.render(self.name) #path)
        #self._dot.engine = curreng
        #self._dot.format = currfmt

    def replaceConsts(self, code, consts=()):
        if len(consts) < 1:
            consts = self.constants
        pos = code.find('->')
        sclist = ''
        if pos > 0:
            sclist = code[0:pos]
            code = code[pos+3:].lstrip()
        for const in consts:
            code = re.sub(r"\b%s\b" % const.name, const.value, code)
        if len(sclist) > 0:
            code = '%s -> %s' % (sclist, code)
        return code

    def restoreConsts(self, code, consts=()):
        for const in consts:
            code = re.sub(r"\b%s\b" % const.value, const.name, code)
            code = re.sub(r"\b%si" % const.value, '%s*i' % const.name, code)
            intval = int(const.value)
            if intval > 0:
                code = re.sub(r"\b%s\b" % (intval-1), '(%s-1)' % const.name, code)
        return code

class Edge(object):
    def __init__(self, u=None, v=None, label='', attrs={}, directed=True, graph=None):
        self._u = u
        self._v = v
        self._label = label
        self._attrs = attrs
        self._directed = directed
        self._graph = graph
        self._dot = None

    def __contains__(self, item):
        return item in self._attrs

    def __len__(self):
        return 0

    def __getitem__(self, key):
        return self._attrs[key]

    def __setitem__(self, key, val):
        self._attrs[key] = val

    def __str__(self):
        return str(self._u) + '->' + str(self._v)

    @property
    def key(self):
        vals = [str(val) for val in sorted(self._attrs.values())]
        return '-'.join(vals)

    @property
    def attrkeys(self):
        return self._attrs.keys()

    @property
    def src(self):
        return self._u

    @src.setter
    def src(self, u=None):
        self._u = u

    @property
    def dest(self):
        return self._v

    @dest.setter
    def dest(self, v=None):
        self._v = v

    @property
    def dotlabel(self):
        return DotHelper.formatLabel(self._label)

    @property
    def label(self):
        return self._label

    @label.setter
    def label(self, label):
        self._label = label

    @property
    def attrs(self):
        return self._attrs

    @attrs.setter
    def attrs(self, attrs={}):
        self._attrs = attrs

    @property
    def directed(self):
        return self._directed

    @directed.setter
    def directed(self, directed=True):
        self._directed = directed

    @property
    def graph(self):
        return self._graph

    @graph.setter
    def graph(self, g):
        self._graph = g

    @property
    def dot(self):
        if self._dot is None:
            self._dot = self._graph.dot.edge(self.src.name, self.dest.name, self.label, DotHelper.parseAttrs(self.attrs))
        return self._dot

class Node(object):
    def __init__(self, label='', name='', attrs={}, graph=None, domain=''):
        self._label = label
        self._name = name
        self._domain = domain
        self._attrs = attrs
        self._attrs['color'] = 'white'
        self._attrs['shape'] = ''
        self._graph = graph
        self._dot = None
        self._set = None

    def __contains__(self, item):
        return item in self._attrs

    def __len__(self):
        return 0

    def __getitem__(self, key):
        return self._attrs[key]

    def __setitem__(self, key, val):
        self._attrs[key] = val

    def __str__(self):
        return  str(type(self)) + '(' + self._label + ')'

    @property
    def key(self):
        vals = [str(val) for val in sorted(self._attrs.values())]
        return '-'.join(vals)

    @property
    def attrkeys(self):
        return self._attrs.keys()

    @property
    def dotlabel(self):
        lbl = self._label
        if 'comp' in self._attrs and len(self['comp']) > 0:
            lbl = '%s (%s)' % (lbl, self['comp'])
        lbl = DotHelper.formatLabel(lbl)
        return lbl

    @property
    def label(self):
        return self._label

    @label.setter
    def label(self, label):
        self._label = label

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def domain(self):
        return self._domain

    @domain.setter
    def domain(self, domain):
        self._domain = domain

    @property
    def set(self):
        domain = self._domain
        if self._set is None and len(domain) > 0:
            self._set = self._graph._setfac.set(domain, self._label)
        return self._set

    @set.setter
    def set(self, set):
        self._set = set
        self._domain = str(set)

    @property
    def attrs(self):
        return self._attrs

    @attrs.setter
    def attrs(self, attrs={}):
        self._attrs = attrs

    @property
    def graph(self):
        return self._graph

    @graph.setter
    def graph(self, g):
        self._graph = g

    @property
    def dot(self):
        if self._dot is None:
            self._dot = self._graph.dot.node(self._name, self.label, DotHelper.parseAttrs(self._attrs))
        return self._dot

    @property
    def statement(self):
        return ''

    def accept(self, visitor):
        visitor.visit(self)

class StmtNode(Node):
    def __init__(self, label='', name='', attrs={}, domain=''):
        super().__init__(label, name, attrs.copy(), domain=domain)
        self._attrs['shape'] = 'invtriangle'
        self._statements = []
        self._datamap = ''
        self._cond = ''
        self._reads = []
        self._writes = []

    @property
    def statements(self):
        return self._statements

    @statements.setter
    def statements(self, statements):
        self._statements = statements

    def add(self, statement):
        self._statements.append(statement)

    @property
    def condition(self):
        return self._cond

    @condition.setter
    def condition(self, cond):
        self._cond = cond

    @property
    def datamap(self):
        return self._datamap

    @datamap.setter
    def datamap(self, datamap):
        self._datamap = datamap

    @property
    def reads(self):
        return self._reads

    @reads.setter
    def reads(self, reads):
        self._reads = reads

    @property
    def writes(self):
        return self._writes

    @writes.setter
    def writes(self, writes):
        self._writes = writes

    @property
    def statement(self):
        return self.label

    @property
    def dot(self):
        #    self['xlabel'] = '''<<table border="0" cellborder="0" cellspacing="0">
        #   <tr><td><strong>Domain:</strong></td><td>%s</td></tr>
        #   <tr><td><strong>Range:</strong></td><td>%s</td></tr>
        #   <tr><td><strong>Size:</strong></td><td>%s</td></tr>
        # </table>>''' % (self.domain.replace('<', '&lt').replace('>', '&gt'),
        #                 self.range.replace('<', '&lt').replace('>', '&gt'), str(self._size))
        self['xlabel'] = ("\\lDomain: %s\\l" % self._domain) + \
                         ("Statements: %s\\l" % ";\\l".join(self._statements))
        if len(self._reads) > 0:
            self['xlabel'] += ("Reads: %s\\l" % ", ".join(self._reads))
        if len(self._writes) > 0:
            self['xlabel'] += ("Writes: %s\\l" % ", ".join(self._writes))
        return super(StmtNode, self).dot

class DataNode(Node):
    def __init__(self, label='', name='', attrs={}, copy=None, domain=''):
        super().__init__(label, name, attrs.copy(), domain=domain)
        if copy is None:
            self._attrs['shape'] = 'box'    #'rect'
            self._attrs['color'] = 'gray'
            self._range = 'R'               # Default to all real #'s
            self._defval = '0'
            self._type = 'real'
            self._alloc = MemAlloc.AUTO
            if 'size' in self._attrs:
                self._size = self._attrs['size']
            else:
                self._size = '1'
        else:
            self._label = copy._label
            self._name = copy._name
            self._range = copy._range
            self._size = copy._size
            self._defval = copy._defval
            self._type = copy._type
            self._alloc = copy._alloc
            self._attrs = copy._attrs.copy()

    @property
    def domain(self):
        return self._domain

    @domain.setter
    def domain(self, domain):
        self._domain = domain
        self._size = Set.from_expr(domain).size

    @property
    def range(self):
        return self._range

    @range.setter
    def range(self, range):
        self._range = range

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, size):
        self._size = size

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, type):
        self._type = type

    @property
    def alloc(self):
        return self._alloc

    @alloc.setter
    def alloc(self, alloc):
        self._alloc = alloc

    @property
    def defval(self):
        return self._defval

    @defval.setter
    def defval(self, defval):
        self._defval = defval

    @property
    def scalar(self):
        try:
            return int(self._size) == 1
        except ValueError:
            return False

    @property
    def dot(self):
        rng = self._range
        if rng == 'R':
            rng = '|' + rng
     #    self['xlabel'] = '''<<table border="0" cellborder="0" cellspacing="0">
     #   <tr><td><strong>Domain:</strong></td><td>%s</td></tr>
     #   <tr><td><strong>Range:</strong></td><td>%s</td></tr>
     #   <tr><td><strong>Size:</strong></td><td>%s</td></tr>
     # </table>>''' % (self.domain.replace('<', '&lt').replace('>', '&gt'),
     #                 self.range.replace('<', '&lt').replace('>', '&gt'), str(self._size))
        self['xlabel'] = ("Domain: %s\\l" % self.domain) + \
                         ("Range: %s\\l" % rng) + \
                         ("Size: %s\\l" % str(self._size))
        return super(DataNode, self).dot

class TempNode(DataNode):
    def __init__(self, label='', name='', attrs={}):
        super().__init__(label, name, attrs.copy())
        self._attrs['color'] = 'white'
        self._alloc = MemAlloc.DYNAMIC

    # @property
    # def dot(self):
    #     self['xlabel'] = 'TempData'
    #     return super(TempNode, self).dot

class StructNode(DataNode):
    def __init__(self, label='', name='', attrs={}, members={}):
        super().__init__(label, name, attrs.copy())
        self._members = members

    @classmethod
    def suffix(cls):
        return '_data_t'

    @property
    def members(self):
        return self._members

    @property
    def scalar(self):       # A struct is not a scalar...
        return False

class IterNode(Node):
    def __init__(self, label='', name='', attrs={}):
        super().__init__(label, name, attrs.copy())
        self._attrs['shape'] = 'oval'
        self._relation = ''

    @property
    def relation(self):
        return self._relation

    @relation.setter
    def relation(self, relation):
        self._relation = relation

class NodeFactory(object):
    class __NodeFactory:
        def __init__(self):
            pass

    _instance = None

    def __init__(self):
        if not NodeFactory._instance:
            NodeFactory._instance = NodeFactory.__NodeFactory()

    def __getattr__(self, name):
        return getattr(self._instance, name)

    def get(self, type='', label='', attrs={}):
        if type.startswith('S'):
            node = StmtNode(label, attrs)
        elif type.startswith('D'):
            node = DataNode(label, attrs)
        elif type.startswith('T'):
            node = TempNode(label, attrs)
        elif type.startswith('I'):
            node = IterNode(label, attrs)
        else:
            raise ValueError("Invalid node label: '%s'" % type)
        return node

class IEGenGraph(FlowGraph):
    def __init__(self, name='iegen', constants=(), expressions=(), input=None):
        super().__init__(name, constants=constants)
        self._expressions = expressions
        self._input = input
        self._sets = {}
        self._maps = {}
        self._constraints = []
        self._insp_items = []
        self._setup = FlowGraph('%s_setup' % name, parent=self)
        self._exec = FlowGraph('%s_exec' % name, parent=self)
        self._insp = FlowGraph('%s_insp' % name, constants=constants, parent=self)
        self._subgraphs = [self._setup, self._exec, self._insp]

    @property
    def input(self):
        return self._input

    @property
    def setup(self):
        return self._setup

    @property
    def executor(self):
        return self._exec

    @property
    def inspector(self):
        return self._insp

    def build_sets(self):
        expressions = self._expressions
        ingraph = self._input
        factory = self._setfac
        factory.constants = self.constants
        alphare = re.compile(r'[A-Za-z_]+')
        opre = re.compile(r'\+|\/|\*|\-|\%')

        sets = {}
        maps = {}
        constraints = []
        insp_items = []          # Items that must be produced by the inspector...

        for expr in expressions:
            expr = expr.strip().rstrip(';')
            ismap = '->' in expr
            pos = expr.find(':=')
            if pos >= 0:
                name = expr[0:pos].rstrip()
                expr = expr[pos+3:].lstrip()
            else:
                if ismap:
                    name = 'T%d' % len(maps)
                else:
                    name = 'I%d' % len(sets)

            andoper = '&&'
            if ' and' in expr:
                andoper = 'and'

            if '{' in expr:
                sub = expr.lstrip('{').rstrip('}')
                pos = sub.rfind(':')
                if pos >= 0:
                    sub = sub[pos+1:].strip()
                    for constr in sub.split(andoper):
                        constr = Var.from_expr(constr)
                        bounds = [constr.lower, constr.upper]
                        if not constr.bounded:
                            bounds.append(constr.name)        # Check name if constraint is not bounded on both sides...
                        for i in range(len(bounds)):
                            id = bounds[i]
                            # TODO: Handle bounds that are complex expressions.
                            if len(id) > 0 and not opre.search(id) and alphare.search(id):
                                pos = id.find('(')
                                isfunc = pos > 0
                                if isfunc:
                                    id = id[0:pos]
                                if id not in self:
                                    if id in ingraph:
                                        self[id] = ingraph[id]
                                        if isfunc and type(self[id]) is not Function:
                                            self[id] = Function.from_expr(bounds[i])
                                    elif id not in insp_items:
                                        insp_items.append(id)  # New item: Inspector needs to build!
                                        if isfunc:
                                             self[id] = Function.from_expr(bounds[i])
                        constraints.append(constr)
                if '/' in expr or '*' in expr:      # Only replace consts if div or mul (Presburger arithmetic)
                    expr = self.replaceConsts(expr)     # Replace constants (e.g, block sizes)
                if ismap:
                    maps[name] = factory.map(expr, name)
                else:
                    sets[name] = factory.set(expr, name)

            elif '*' in expr or '(' in expr:
                pos = expr.find('*')
                if pos < 0:
                    pos = expr.find('(')
                mapid = expr[0:pos].rstrip()
                setid = expr[pos+1:].lstrip(' ').rstrip(')')
                sets[name] = sets[setid].apply(maps[mapid])

        self._sets = sets
        self._maps = maps
        self._constraints = constraints
        self._insp_items = insp_items

        return (sets, constraints, insp_items)

    def generate(self):
        (sets, constraints, insp_items) = self.build_sets()
        setup = self.build_setup()
        insp = self.build_inspector()
        exec = self.build_executor()
        # TODO: Decide how to chain graphs together, i.e., via function args...
        return (setup, insp, exec)

    def build_setup(self):
        raise NotImplementedError("IEGenGraph.build_setup is abstract, please instantiate a subclass.")

    def build_inspector(self):
        raise NotImplementedError("IEGenGraph.build_inspector is abstract, please instantiate a subclass.")

    def build_executor(self):
        raise NotImplementedError("IEGenGraph.build_executor is abstract, please instantiate a subclass.")
