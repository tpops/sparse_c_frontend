"""
Implementation of the 'schedule tree' data structure as defined in journal paper:
Polyhedral AST Generation is More than Just Scanning Polyhedra -- Grosser et al.
"""

import sys
from codegen.visit import Visitor

CHILD_MAX = 1000000         # More than 1M children would be excessive...

class ScheduleTree(object):
    """Schedule tree is a structured representation of a schedule, assigning a recursively defined
       relative order to a set of domain elements."""
    def __init__(self, name=''):
        """The root node is always a Domain node (or Extension) and describes the (extra) domain elements to which the
           schedule applies."""
        self._name = name
        self._root = None   #DomainNode()

    @classmethod
    def from_file(cls, stfile):
        st = ScheduleTree(stfile.split('/')[-1].replace('.st', ''))
        file = open(stfile)

        node = st._root
        for line in file:
            line = line.strip()
            if line[0] != '#':
                pos = line.find(':')
                if pos > 0:
                    name = line[0:pos]
                    value = line[pos+1:].lstrip(' ').strip('"')
                    if 'domain' in name:
                        domain = DomainNode(value)
                        if node is None:
                            node = domain
                            st._root = node
                        else:
                            node = node.add(domain)
                    elif 'child' in name:
                        pass        # I think this indicates a new child is coming, not sure why it's needed yet...
                    elif 'set' in name:
                        node = node.add(SetNode())
                    elif 'sequence' in name:
                        node = node.add(SequenceNode())
                    elif 'filter' in name:
                        node = node.add(FilterNode(value))
                    elif 'context' in name:
                        node = node.add(ContextNode(value))
                    elif 'guard' in name:
                        node = node.add(GuardNode(value))
                    elif 'schedule' in name:
                        node = node.add(BandNode(value))
                    elif 'permutable' in name:
                        node.permutable = int(value) > 0
                    elif 'coincident' in name:
                        node.coincident = value
                    elif 'options' in name:
                        node.options = value
                    else:   # My hunch is this is a mark node...
                        node = node.add(MarkNode(name, value))
        return st

    @property
    def name(self):
        return self._name

    @property
    def root(self):
        return self._root

    def to_file(self):
        fname = '%s.st' % self._name
        file = open(fname, 'w')
        file.write(str(self))
        file.close()

class ScheduleNode(object):
    """Abstract class for schedule tree children."""
    def __init__(self, childmax=1, color='black'):
        self._parent = None
        self._children = []
        self._childmax = childmax
        self._color = color

    def add(self, child):
        self._children.append(child)
        if len(self._children) > self._childmax:
            raise ValueError("Node type '%s' has %d children but cannot exceed %d." %
                             (str(type(self)), len(self._children), self._childmax))
        return child

    def accept(self, visitor):
        visitor.visit(self)

    @property
    def children(self):
        return self._children

class ContextNode(ScheduleNode):
    """The context describes constraints on the parameters and the schedule dimensions of outer bands that the AST
       generator may assume to hold. It is also the only kind of node that may introduce additional parameters.
       The space of the context is that of the flat product of the outer band nodes. In particular, if there are no
       outer band nodes, then this space is the unnamed zero-dimensional space. Since a context node references the
       outer band nodes, any tree containing a context node is considered to be anchored."""
    def __init__(self, context=''):
        super().__init__()
        self._context = ''

    @property
    def context(self):
        return self._context

class DomainNode(ScheduleNode):
    """A domain node appears as the root of a schedule tree and introduces the statement instances that are scheduled
       by the descendants of the domain node. The statement instances are described by a named Presburger set."""
    def __init__(self, domain=''):
        super().__init__(color='#6B4226')
        self._domain = domain

    @property
    def domain(self):
        return self._domain

    @domain.setter
    def domain(self, domain):
        self._domain = domain

class FilterNode(ScheduleNode):
    """A filter node selects a subset of the statement instances introduced by outer domain, expansion or extension
       nodes and retained by outer filter nodes. Filter nodes are typically used as children of set and sequence nodes,
       where the siblings select the other statement instances. Filters can also be used to select the statement
       instances that are mapped to a given value of a symbolic con- stant introduced in an outer context node."""
    def __init__(self, filter=''):
        super().__init__()
        self._filter = filter

    @property
    def filter(self):
        return self._filter

    @filter.setter
    def filter(self, filter):
        self._filter = filter


class SequenceNode(ScheduleNode):
    """A sequence node expresses that its children should be executed in order. These children must be filter nodes,
       with mutually disjoint filters."""
    def __init__(self):
        super().__init__(CHILD_MAX)

class SetNode(ScheduleNode):
    """A set node is similar to a sequence node except that its children may be executed in any order."""
    def __init__(self):
        super().__init__(CHILD_MAX)

class BandNode(ScheduleNode):
    """A band node contains a partial schedule on the statement instances introduced by outer domain, expansion or
       extension nodes and retained by outer filter nodes. This partial schedule may be piecewise quasi-affine, but
       is required to be total on those statement instances. Additionally, a band node contains options that control
       the AST generation, e.g., separation, unrolling, or isolation. The ability to specify AST generation options
       for each band separately allows for great flexibility for more complicated programs with statements that,
       after scheduling, are spread over different, possibly nested, loop nests. Each band node contains an
       unstructured schedule of the type accepted by the AST generator."""
    def __init__(self, schedule=''):
        super().__init__()
        self._schedule = schedule
        self._permutable = False
        self._coincident = ''
        self._options = ''

    @property
    def schedule(self):
        return self._schedule

    @schedule.setter
    def schedule(self, schedule):
        self._schedule = schedule

    @property
    def permutable(self):
        return self._permutable

    @permutable.setter
    def permutable(self, permutable):
        self._permutable = permutable

    @property
    def coincident(self):
        return self._coincident

    @coincident.setter
    def coincident(self, coincident):
        self._coincident = coincident

    @property
    def options(self):
        return self._options

    @options.setter
    def options(self, options):
        self._options = options

class LeafNode(ScheduleNode):
    """A leaf of the schedule tree, does not impose any ordering."""
    def __init__(self):
        super().__init__(0)

class MarkNode(ScheduleNode):
    """A mark node can be used to attach any kind of information to a schedule subtree."""
    def __init__(self, name='', value=''):
        super().__init__()
        self._name = name
        self._value = value

    @property
    def name(self):
        return self._name

    @property
    def value(self):
        return self._value

class ExpansionNode(ScheduleNode):
    """An expansion node maps each of the domain elements that reach the node to one or more domain elements. The
       image of this mapping forms the set of domain elements that reach the child of the expansion node. Expansion
       nodes are useful for grouping instances of several statements into an instance of a single virtual statement
       to ensure that those instances are always executed together."""
    def __init__(self):
        super().__init__()

class ExtensionNode(ScheduleNode):
    """An extension node instructs the AST generator to add additional domain elements that need to be scheduled,
       described in terms of the outer schedule dimensions. A typical use case is the introduction of data copying
       statements for locality optimization. This is expressed as a relation between the outer schedule dimensions
       and the set of array elements accessed by the statement instances scheduled to a give value of those schedule
       dimensions. The new statement instances of extension nodes are only introduced if any of the instances
       introduced in outer nodes may still be executed at the given position of the schedule tree."""
    def __init__(self):
        super().__init__()

class GuardNode(ScheduleNode):
    """A guard node describes constraints on the symbolic constants and the schedule dimensions of outer bands that
       need to be enforced by the outer nodes in the generated AST. This allows the user to rely on a given set of
       constraints being enforced at a given point in the schedule tree, independently of the simplification of guards
       performed by the AST generator."""
    def __init__(self, guard=''):
        super().__init__()
        self._guard = guard

    @property
    def guard(self):
        return self._guard


class ScheduleTreeVisitor(Visitor):
    def visit(self, node):
        self.enter(node)
        for child in node.children:
            child.accept(self)
        self.exit(node)

class ScheduleTreePrinter(ScheduleTreeVisitor):
    def __init__(self):
        self._indent = ''

    def enter(self, node):
        print(str(node))
