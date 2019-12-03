from io import StringIO
from codegen.iegenlib import *
from codegen.visit import *

def from_spec(spec):
    # Lazy approach today:
    if 'Jacobi1' in spec:
        return Jacobi1D()
    elif 'Jacobi2' in spec:
        return Jacobi2D()
    elif 'CSR' in spec:
        return CSRSpMV()
    else:
        raise NotImplementedError('Arbitrary graph specification not yet implemented')

class PDFGParser(object):
    def __init__(self, file='', name=''):
        self._iegen = IEGenLib()
        self._file = file
        self._iters = {}
        self._lineno = 0
        if len(file) > 0 and len(name) < 1:
            name = file.split('/')[-1].split('.')[0]
        self._graph = FlowGraph(name)

    def parse(self, spec=''):
        if len(spec) > 0:
            handle = StringIO(spec)
        else:
            handle = open(self._file)
        for line in handle:
            self._lineno += 1
            line = line.strip().rstrip(';')
            if len(line) > 0 and line[0] != '#':
                pos = line.find(':=')
                if pos > 0:
                    self.assign(line, pos)
                else:
                    self.expression(line)
        handle.close()
        return self._graph

    def assign(self, line, pos):
        lhs = line[0:pos].rstrip()
        rhs = line[pos + 2:].lstrip()
        relop = '->'
        pos = lhs.find('(')
        if pos > 0:  # It's a built-in fxn
            kword = lhs[0:pos]
            args = lhs[pos + 1:].rstrip(')')
            self.function(kword, args, rhs)
        elif rhs[0] == '[':
            pos = rhs.find(relop)
            if pos > 0:
                self.constants(rhs[0:pos])
                self.relation(lhs, rhs[pos+1])
        elif rhs[0] == '{':
            self.relation(lhs, rhs)      # Set or relation

    def constants(self, constlist):
        constants = constlist[1:len(constlist)-1].split(',')
        [self._graph.addconst(const.strip()) for const in constants]

    def relation(self, name, relstr):
        pos = relstr.find('[')
        iterlist = relstr[pos+1:relstr.find(']', pos+1)]
        iters = [itr.strip() for itr in iterlist.split(',')]
        iterdefs = {}

        whereop = ':'
        pos = relstr.find(whereop)
        if pos > 0:
            condlist = relstr[pos+1:].rstrip('}')
            andpatt = 'and|&&'
            conds = re.split(andpatt, condlist)

            for cond in conds:
                cond = cond.strip()
                var = Var.from_expr(cond)
                iterdefs[var.name] = var
                self.bound(var.lower)
                self.bound(var.upper)

        # Check whether iterator needs to be added to current expression...
        for itr in iters:
            if itr in iterdefs:
                self._iters[itr] = iterdefs[itr]
            elif itr in self._iters:
                if ':' not in relstr:
                    insert = ' : '
                else:
                    insert = ' && '
                insert += str(self._iters[itr])
                pos = relstr.rfind('}')
                relstr = relstr[0:pos] + insert + relstr[pos:]
            else:   # Undefined iterator
                raise(SyntaxError("Undefined iterator '%s' in expression '%s' at line %d." %
                                  (itr, relstr, self._lineno)))
        self._iegen.add(relstr, name)

    def expression(self, line):
        pos = line.find('(')
        if pos > 0:  # It's a built-in fxn
            kword = line[0:pos]
            args = line[pos + 1:].rstrip(')')
            if kword == 'name':
                self._graph.name = args.strip("\"")

    def function(self, name, args, rhs):
        if name == 'statement' or name == 'stmt':
            self.statement(args, rhs.strip('"'))
        else:
            print("Function '%s' not yet supported." % name)

    def updaterefs(self, stmt):
        # Update multi-dimensional array accesses in expression
        graph = self._graph
        expr = ''
        id = ''
        insub = False

        newstmt = stmt
        for chr in stmt:
            if not chr.isspace():
                if chr == '[':
                    insub = True
                elif chr == ']':
                    count = expr.count(',')+1
                    if count > 0 and 'offset' not in expr:
                        dnode = graph[id]
                        sizes = dnode.size.split('*')
                        oldexpr = '%s[%s]' % (id, expr)
                        # offset3(i,j,k,M,N) (k+N*(j+M*i))
                        newexpr = '%s[offset%d(%s,%s)]' % (id, count, expr, ','.join(sizes[0:len(sizes)-1]))
                        newstmt = newstmt.replace(oldexpr, newexpr)
                    insub = False
                    expr = id = ''
                elif insub:
                    expr += chr
                elif not self.isoper(chr) and not (len(id) < 1 and self.isnumeric(chr)):
                    id += chr
        return newstmt

    def statement(self, name, stmt):
        # This is a statement node, fetch the domain from IEGen object.
        if name in self._graph:
            snode = self._graph[name]
        else:
            snode = StmtNode(name, domain=self._iegen[name])

        # Split statement on assignment
        pos = stmt.find('=')
        if pos > 0:     # RHS are reads, LHS are writes
            wnodes = self.writes(snode, stmt[0:pos].rstrip())
            rnodes = self.reads(snode, stmt[pos+1:].lstrip())
        else:
            rnodes = []
            wnodes = []

        # Add read nodes to graph
        [self._graph.add(rnode) for rnode in rnodes]
        self._graph.newrow()

        # Add statement node to graph
        self._graph.add(snode)
        self._graph.newrow()

        # Add write nodes to graph
        [self._graph.add(wnode) for wnode in wnodes]
        self._graph.newrow()

        # Add read edges
        [self._graph.add(Edge(rnode, snode)) for rnode in rnodes]

        # Add write edges
        [self._graph.add(Edge(snode, wnode)) for wnode in wnodes]

        stmt = self.updaterefs(stmt)
        snode.statements.append(stmt)

    def reads(self, node, expr):
        self.accesses(expr, node.reads)
        return self.datanodes(node, node.reads)

    def writes(self, node, expr):
        self.accesses(expr, node.writes)
        return self.datanodes(node, node.writes)

    def accesses(self, expr, alist):
        item = ''
        insub = False
        for chr in expr:
            if not chr.isspace():
                item += chr
                if chr == '[':
                    insub = True
                elif chr == ']':
                    insub = False
                elif not insub and self.isoper(chr):
                    item = item[0:len(item) - 1]
                    if len(item) > 0 and not self.isnumeric(item):
                        alist.append(item)
                    item = ''
        if len(item) > 0 and not self.isnumeric(item):
            alist.append(item)

    def datanodes(self, snode, accesses):
        dnodes = []
        marked = {}
        for expr in accesses:
            pos = expr.find('[')
            if pos > 0:
                id = expr[0:pos]
            else:
                id = expr
            if id not in marked:
                marked[id] = True
                if id not in self._graph:
                    dnode = DataNode(id)
                    if id not in self._iegen:
                        self._iegen.add(snode.domain.formula, id)
                    dnode.domain = self._iegen[id]
                else:
                    dnode = self._graph[id]
                dnodes.append(dnode)
        return dnodes

    def bound(self, bound):
        if len(bound) > 0 and not self.isnumeric(bound):
            if '(' in bound or '[' in bound:
                stop=1      # UF
            else:
                for item in bound.split():
                    if not self.isoper(item) and not self.isnumeric(item) and item not in self._graph:
                        self._graph.addconst(Constant(bound))

    @property
    def operators(self):
        return ['*', '/', '%', '+', '-', '&', '|', '(', ')', '=', '.']

    def isoper(self, chr):
        return chr in self.operators

    def isnumeric(self, expr):
        return re.match(r'[+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?', expr)

class Jacobi1D(FlowGraph):
    def __init__(self, name='jacobi1d', n=100000, t=100000):
        super().__init__(name)

        # Add constants
        self.constants = [Constant('N', str(n)), Constant('T', str(t))]

        # Input: only need space for t-1, and t.
        a = DataNode('A')
        a.domain = '{[t,i] : 0 <= t <= T && 0 <= i <= N+1}'
        a.size = 'T*(N+2)'
        self.add(a)
        self.newrow()

        # jacobi
        jacobi = StmtNode('jacobi1d')
        jacobi.domain = '{[t,i] : 1 <= t <= T && 1 <= i <= N}'
        jacobi.statements = ['A[t,i] = (A[t-1,i-1] + A[t-1,i] + A[t-1,i+1]) / 3.0']
        jacobi.datamap = a.domain
        jacobi.reads = ['A[t-1,i-1]', 'A[t-1,i]', 'A[t-1,i+1]']
        jacobi.writes = ['A[t,i]']
        self.add(jacobi)
        self.newrow()

        # Output: only report last time step, t==T
        out = DataNode('A\'')
        out.domain = '{[i] : 0 <= i <= N+1}'
        out.range = 'R'  # r'\mathbb{R}'
        out.size = 'N+2'
        self.add(out)
        self.newrow()

        # A => stencil edge
        self.add(Edge(a, jacobi))
        # stencil => out edge
        self.add(Edge(jacobi, out))

    def codegen(self):          # Generate C code w/ CodeGenVisitor
        v = CodeGenVisitor(profile=True)
        v.defines.append(('index(t,i)', '((t)&1)*(N+2)+(i)'))
        v.walk(self)
        v.write()
        return str(v)

class Jacobi2D(FlowGraph):
    def __init__(self, name='jacobi2d', m=4096, n=4096, t=100):
        super().__init__(name)

        # Add constants
        self.constants = [Constant('M', str(m)), Constant('N', str(n)), Constant('T', str(t))]

        # Input: only need space for t-1, and t.
        a = DataNode('A')
        a.domain = '{[t,i] : 0 <= t <= T && 0 <= i <= N+1}'
        a.size = '2*(M+2)*(N+2)'
        self.add(a)
        self.newrow()

        # jacobi
        jacobi = StmtNode('stencil')
        jacobi.domain = '{[t,i,j] : 1 <= t <= T && 1 <= i <= M && 1 <= j <= N}'
        jacobi.statements = ['A[t,i,j] = (A[t-1,i,j-1] + A[t-1,i,j] + A[t-1,i,j+1] + A[t-1,i-1,j] + A[t-1,i+1,j]) * 0.2']
        jacobi.datamap = a.domain
        jacobi.reads = ['A[t-1,i,j-1]', 'A[t-1,i,j]', 'A[t-1,i,j+1]', 'A[t-1,i-1,j]', 'A[t-1,i+1,j]']
        jacobi.writes = ['A[t,i,j]']
        self.add(jacobi)
        self.newrow()

        # Output: only report last time step, t==T
        out = DataNode('out')
        out.domain = '{[i,j] : 0 <= i <= M+1 && 0 <= j <= N+1}'
        out.range = 'R'  # r'\mathbb{R}'
        out.size = '(M+2)*(N+2)'
        self.add(out)
        self.newrow()

        # A => stencil edge
        self.add(Edge(a, jacobi))
        # stencil => out edge
        self.add(Edge(jacobi, out))

class MiniFluxDix(FlowGraph):
    def __init__(self, name='miniFluxDiv', variant='seriesSSACLO', nboxes=28, ncells=128, nghost=2, ncomp=5):
        super().__init__('%s-%s' % (name, variant))

        gdict = graphs[variant]
        self.nodes = gdict['nodes']
        self.edges = gdict['edges']
        self.comps = gdict['comps']

        # Add constants
        self.constants = [Constant('N', str(ncells))]#, Constant('C', str(ncomp))]#,
                          #Constant('B', str(nboxes)), Constant('G', str(nghost))]

        vars = benchmarks[name]['vars']
        varnames = ','.join(vars)
        dims = 'xyz'
        vels = {}
        for i in range(len(dims)):
            vels[dims[i]] = self.comps[i + 2]

        # 1st Pass: Set domains, ranges, and sizes...
        for i in range(self.nrows):
            for j in range(self.ncols):
                if (i, j) in self:
                    node = self[(i, j)]
                    ntype = type(node)

                    child = None
                    tuple = (i + 1, j)
                    if tuple in self:
                        child = self[tuple]

                    varnames = ','.join(vars[1:])

                    if ntype is DataNode or ntype is TempNode:
                        domain = '{[%s] : ' % varnames
                        for var in vars[1:]:
                            endoper = '<'
                            if '+' in node.label and child.label[0] == 'F' and child.label[1] == var:
                                endoper += '='
                            domain += '0 <= ' + var + ' ' + endoper + ' N && '
                        domain += 'N > 1}'

                        node.domain = domain
                        node.range = 'R'
                        node.size = node.label
                        node.label = '%s_old' % self.comps[j]
                    elif ntype is StmtNode:
                        # 0 <= 0 <= c < C && z < N && 0 <= y < N && 0 <= x <= N
                        #domain = '{[%s] : 0 <= %s < C && ' % (varnames, vars[0])
                        domain = '{[%s] : ' % varnames
                        for var in vars[1:]:
                            endoper = '<'
                            if node.label[0] == 'F' and node.label[1] == var:
                                endoper += '='
                            domain += '0 <= ' + var + ' ' + endoper + ' N && '
                        #domain += 'N > 1 && C > 1}'
                        domain += 'N > 1}'
                        node.domain = domain

                        statement = node.label.upper().replace('F', 'FLUX').replace('D', 'DIFF')
                        statement = statement[0:len(statement)-2] + statement[-1] + statement[-2]
                        statement = '%s(%s)' % (statement, varnames)
                        node.statements = [statement]
                    else:
                        raise TypeError('Unrecognized node type: %s' % str(node))
                    #node.label = '%s (%s)' % (node._label, self.comps[j])

        # 2nd Pass: Set datamaps, reads, and writes...
        for i in range(self.nrows):
            for j in range(self.ncols):
                if (i, j) in self:
                    node = self[(i, j)]
                    ntype = type(node)

                    if ntype is StmtNode:
                        child = None
                        tuple = (i + 1, j)
                        if tuple in self:
                            child = self[tuple]

                        if child is not None:
                            node.datamap = child.domain

                        label = node.label
                        dim = label[1]
                        comp = self.comps[j]
                        varnames = ','.join(vars[1:])

                        if label[0] == 'F':
                            if label[2] == '1':
                                for i in range(-2, 2):
                                    read = '%s(' % comp
                                    for var in vars[1:]:
                                        read += var
                                        if var == dim and i != 0:
                                            read += '%+d' % i
                                        read += ','
                                    read = '%s)' % read[0:len(read)-1]
                                    node.reads.append(read)
                                child.label = '%s1_cache' % comp
                                node.writes.append('%s(%s)' % (child.label, varnames))
                            else:   # FLUX2(X|Y|Z)
                                node.reads.append('%s1_cache(%s)' % (comp, varnames))
                                node.reads.append('%s1_cache(%s)' % (vels[dim], varnames))
                                child.label = '%s2_cache' % comp
                                node.writes.append('%s(%s)' % (child.label, varnames))
                        else:   # DIFF(X|Y|Z)
                            prefix = '%s2_cache' % comp
                            node.reads.append('%s(%s)' % (prefix, varnames))

                            read = '%s(' % prefix
                            for var in vars[1:]:
                                read += var
                                if var == dim:
                                    read += '+1'
                                read += ','
                            node.reads.append('%s)' % read[0:len(read) - 1])

                            node.reads.append('%s(%s)' % (comp, varnames))
                            node.writes.append(node.reads[-1])
                            child.label = '%s_new' % comp


class CSRSpMV(FlowGraph):
    def __init__(self, name='csr_spmv', n=100000, nnz=100000):
        super().__init__(name)

        # Add constants
        self.constants = [Constant('N_R', str(n)), Constant('N_C', str(n)), Constant('NNZ', str(nnz))]

        # I_csr
        #icsr = IterNode('I_csr')
        # k = col(j)
        #icsr.domain = '{[i,j] : 0 <= i < N_R && index(i) <= j < index(i+1) && index(i) >= 0 && index(i) <= NNZ}'
        #icsr.domain = '{[i,j] : 0 <= i < N_R && index(i) <= j < index(i+1) && 0 <= j < NNZ}'
        #self.add(icsr)

        a = TempNode('A')
        a.domain = '{[j] : 0 <= j < NNZ}'
        a.range = 'R'  # r'\mathbb{R}'
        a.size = 'NNZ'
        a.alloc = MemAlloc.DYNAMIC
        self.add(a)

        col = TempNode('col')
        col.domain = '{[j] : 0 <= j < NNZ}'
        col.range = '{[k] : 0 <= k < N_C}'
        col.size = 'NNZ'
        col.type = 'itype'
        col.alloc = MemAlloc.DYNAMIC
        self.add(col)

        ndx = TempNode('index')
        ndx.domain = '{[i] : 0 <= i <= N_R}'
        ndx.range = '{[j] : 0 <= j <= NNZ}'
        ndx.size = 'N_R+1'
        ndx.type = 'itype'
        ndx.alloc = MemAlloc.DYNAMIC
        self.add(ndx)

        x = DataNode('x')
        x.domain = '{[k] : 0 <= k < N_C}'
        x.range = 'R'
        x.size = 'N_C'
        self.add(x)

        # self.add(Edge(ndx, icsr))           # index => Icsr edge
        # self.add(Edge(col, icsr))           # col => Icsr edge
        self.newrow()

        # make_blocks
        spmv = StmtNode('spmv')
        spmv.domain = '{[i,j] : 0 <= i < N_R && index(i) <= j < index(i+1) && index(i) >= 0 && NNZ > 0 && NNZ >= index(i+1)}'
        spmv.statements = ['y[i]+=A[j]*x[col[j]]']
        spmv.datamap = '{[i] : 0 <= i < N_R}'
        spmv.reads = ['A[j]', 'col[j]', 'x[col[j]]']
        spmv.writes = ['y[i]']
        self.add(spmv)

        #self.add(Edge(icsr, spmv))              # Icsr => spmv edge
        self.add(Edge(ndx, spmv))  # index => spmv edge
        self.add(Edge(col, spmv))  # col => spmv edge
        self.add(Edge(a, spmv))                 # A => spmv edge
        self.add(Edge(x, spmv))                 # x => spmv edge
        self.newrow()

        y = DataNode('y')
        y.domain = spmv.datamap
        y.range = 'R'
        y.size = 'N_R'
        self.add(y)

        # A => spmv edge
        self.add(Edge(spmv, y))
        self.newrow()

class BSRSpMV(FlowGraph):
    def __init__(self, name='bsr_spmv', n=62451, nnz=2034917, blocksize=(9,9)):
        super().__init__(name)

        # Add constants
        self.constants = [Constant('N_R', str(n)), Constant('N_C', str(n)), Constant('NNZ', str(nnz)),
                          Constant('R', str(blocksize[0])), Constant('C', str(blocksize[1]))]

        # I_bsr
        ibsr = IterNode('I_bsr')
        ibsr.domain = '{[ii,jj,ri,ck] : 0 <= ii < N_R/R && b_index(ii) <= jj < b_index(ii+1) && ' + \
                      '0 <= ri < R && 0 <= ck < C && kk = b_col(jj) && index(ii) >= 0 && index(ii) <= NB}'
        self.add(ibsr)

        a = DataNode('A_prime')
        a.domain = '{[jj,ri,ck] : 0 <= jj < NB && 0 <= ri < R && 0 <= ck < C}'
        a.range = 'R'  # r'\mathbb{R}'
        a.size = 'NB*R*C'
        self.add(a)

        col = DataNode('b_col')
        col.domain = '{[jj] : 0 <= jj < NB}'
        col.range = '{[kk] : 0 <= kk < N_C/C}'
        col.size = 'N_C/C'
        col.type = 'int'
        self.add(col)

        ndx = DataNode('b_index')
        ndx.domain = '{[ii] : 0 <= ii <= N_R/R}'
        ndx.range = '{[jj] : 0 <= jj <= NB}'
        ndx.size = 'N_R/R+1'
        ndx.type = 'int'
        self.add(ndx)

        x = DataNode('x')
        x.domain = '{[k] : 0 <= k < N_C}'
        x.range = 'R'
        x.size = 'N_C'
        self.add(x)

        self.add(Edge(ndx, ibsr))           # index => Icsr edge
        self.add(Edge(col, ibsr))           # col => Icsr edge
        self.newrow()

        # spmv
        spmv = StmtNode('spmv')
        spmv.domain = ibsr.domain
        spmv.statements = ['i=ii*R+ri', 'k=b_col[jj]*C+ck', 'm=jj*R+ri*C+ck', 'y[i]+=A_prime[m]*x[k]']
        spmv.datamap = '{[i] : 0 <= i < N_R}'
        spmv.reads = ['A(jj,ri,ck)', 'x(k)']
        spmv.writes = ['y(i)']
        self.add(spmv)

        self.add(Edge(ibsr, spmv))              # Icsr => spmv edge
        self.add(Edge(a, spmv))                 # A => spmv edge
        self.add(Edge(x, spmv))                 # x => spmv edge
        self.newrow()

        y = DataNode('y')
        y.domain = spmv.datamap
        y.range = 'R'
        y.size = 'N_R'
        self.add(y)

        # A => spmv edge
        self.add(Edge(spmv, y))
        self.newrow()

class CSRToBSRGen(IEGenGraph):
    # TODO: Devise a means to add missing constraints to expressions automatically (e.g, from Idense to Itile, adding manually for now...
    #Itile := {spmv[ii,kk,i,k,j]: exists ri,ck :0 <= ri < R && i = ii*R+ri && 0 <= ck < C && k = kk*C+ck && N_C > C && N_R > R};
    _code = """
        Icsr := {[i,j]: 0 <= i < N_R && index(i) <= j < index(i+1) && index(i) >= 0 && index(i+1) <= NNZ && NNZ > 0 && col(j) >= 0 && N_C > 0};
        Tdense := {[i,j] -> [i,k,j]: 0 <= k < N_C && k = col(j)};
        Ttile := {[i,k,j] -> [ii,kk,i,k,j]: exists(ri,ck :0 <= ri < R && i = ii*R+ri && 0 <= ck < C && k = kk*C+ck)};
        #Itile := {[ii,kk,i,k,j]: 0 <= i < N_R && 0 <= k < N_C && index(i) <= j < index(i+1) && exists ri,ck :0 <= ri < R && i = ii*R+ri && 0 <= ck < C && k = kk*C+ck};
        Texec := {[ii,kk,i,k,j] -> [ii,jj,i,k,j]: b_index(ii) <= jj < b_index(ii+1) && kk = b_col(jj) && b_index(i) <= NB};
        Tcomp := {[ii,kk,i,k,j] -> [ii,kk,i,k,j]: k = col(j) && kk = k/C};
        Idense := Tdense * Icsr;
        Itile := Ttile * Idense;
        Iexec := Texec * Itile;
        Icomp := Tcomp * Itile;
        """

    def __init__(self, name='csr_bsr', bsize=8):
        super().__init__(name, [Constant('R', str(bsize)), Constant('C', str(bsize))],
                         CSRToBSRGen._code.strip().split("\n"), CSRSpMV())
        self.includes.append('iegen_util')

    def build_setup(self):
        # Run CodeGenVisitor on input graph to generate the initial struct...
        input = self.input
        vi = CodeGenVisitor()
        vi.walk(input)

        setup = self._setup
        setup.params.append(Var('path', type='const char*'))

        # struct
        struct = StructNode('csr', members=vi.structs['csr'])
        struct.size = '1'
        struct.type = '%s%s' % (struct.label, StructNode.suffix())
        struct.alloc = MemAlloc.DYNAMIC
        setup.add(struct)

        # read
        read = StmtNode('read')
        read.domain = '1'
        read.statements = ['csr_read(path,csr)']
        read.datamap = r'[0]'
        setup.add(read)

        # struct -> read
        setup.add(Edge(struct, read))
        setup.newrow()

        setup.returntype = '%s*' % struct.type
        return setup

    def build_inspector(self):
        insp = self._insp
        insp.functions = self.functions
        insp.returntype = 'bsr%s*' % StructNode.suffix()
        insp.params = [Var('csr', type='csr%s*' % StructNode.suffix())]
        for const in insp.constants:
            insp.params.append(Var(const.name, type=const.type))

        # Add N_R and N_C to inspector constants so they will find their way into the BSR structure:
        insp.constants.append(Constant('N_R'))
        insp.constants.append(Constant('N_C'))

        # TODO: This is another ISL-ism, do not need for IEGenLib, comment but fix later!
        #icomp = self._sets['Icomp']
        #idom = VarHelper.replaceIterators(str(icomp), ['ii','kk','i','k','j'])
        idom = str(self._sets['Icomp'])

        # Bset
        bset = TempNode('bset')
        bset.domain = '[0,N_R/R*N_C/C]'
        bset.range = '[0,1]'
        bset.type = 'itype'
        bset.size = 'N_R/R*N_C/C'
        insp.add(bset)

        # count
        count = StmtNode('count')
        count.domain = idom.replace('insp', count.label)
        count.condition = '!bset[ii*(N_C/C)+(k/C)]'
        count.statements = ['bset[ii*(N_C/C)+(k/C)]=++nb']
        count.datamap = r'[0]'
        count.writes = ['bset', 'nb']
        insp.add(count)

        # NB
        nb = TempNode('nb')
        nb.domain = '[0]'
        nb.range = '[0,N_R/R*N_C/C]'
        nb.size = '1'
        nb.type = 'itype'
        insp.add(nb)

        # count -> bset
        insp.add(Edge(bset, count))

        # count -> nb
        insp.add(Edge(count, nb))

        # offsets
        offsets = StmtNode('offsets')
        offsets.domain = idom.replace('insp', 'offsets')
        offsets.condition = '!bset[ii*(N_C/C)+(k/C)]'
        offsets.statements = ['b_index[ii+1] = ++nb', 'bset[ii*(N_C/C)+(k/C)]=nb']
        offsets.datamap = 'b_index(ii+1)'
        offsets.reads = ['bset', 'nb']
        offsets.writes = ['bset', 'nb', 'b_index']
        insp.add(offsets)

        # b_index
        b_index = TempNode('b_index')
        b_index.domain = r'[0,N_R/R]'
        b_index.range = r'[0,NB]'
        b_index.type = 'itype'
        b_index.size = 'N_R/R+1'
        insp.add(b_index)

        # bset -> offsets
        insp.add(Edge(bset, offsets))

        # offsets -> b_index
        insp.add(Edge(offsets, b_index))

        # extract
        extract = StmtNode('extract')
        extract.domain = idom.replace('insp', extract.label)
        extract.condition = '!bset[ii*(N_C/C)+(k/C)]'
        extract.statements = ['b_col[nb++] = k/C', 'bset[ii*(N_C/C)+(k/C)]=nb']
        extract.reads = ['bset', 'nb']
        extract.writes = ['nb', 'bset', 'b_col']
        insp.add(extract)

        # b_col
        b_col = TempNode('b_col')
        b_col.domain = '[0,NB)'
        b_col.range = '[0,N_C/C)'
        b_col.type = 'itype'
        b_col.size = nb.label
        insp.add(b_col)

        # bset -> extract
        insp.add(Edge(bset, extract))

        # extract -> nb
        insp.add(Edge(nb, extract))

        # extract -> b_col
        insp.add(Edge(extract, b_col))

        # R_A->A'
        r_map = IterNode('R_A->A')
        r_map.domain = r'\{[i,j] -> [ii,i,j,k] : ri=i-ii*R && ck=k-(k/C)*C && A_prime(k/C,ri,ck)=A(j)\}'
        insp.add(r_map)

        # copy
        copy = StmtNode('copy')
        copy.domain = idom.replace('insp', copy.label)
        copy.statements = ['A_prime[offset3(k/C,(i-ii*R),(k-(k/C)*C),R,C)] = A[j]']
        copy.datamap = '{[jj,ri,ck] : 0 <= jj < nb && 0 <= ri < R && 0 <= ck < C}'
        copy.reads = ['A(j)']
        copy.writes = ['A_prime(k/C,i-ii*R,k-(k/C)*C)']
        insp.add(copy)

        # r_map -> copy
        insp.add(Edge(r_map, copy))

        # offsets -> nb
        insp.add(Edge(nb, copy))

        # A_prime
        aprime = TempNode('A_prime')
        aprime.domain = copy.datamap
        aprime.range = 'R'
        aprime.size = 'nb*R*C'
        insp.add(aprime)

        # copy -> A_prime
        insp.add(Edge(copy, aprime))
        insp.newrow()
        return insp

    def build_executor(self):
        ###
        # Generate executor graph...
        ###
        exec = self._exec
        exec.params.append(Var('bsr', type='bsr_data_t*'))

        # Connect inspector data to executor...
        aprime = DataNode(copy=self._insp['A_prime'])
        aprime.alloc = MemAlloc.NONE

        # Dense 'x' column vector
        x = DataNode('x')
        x.domain = '{[k] : 0 <= k < N_C}'
        x.range = 'R'
        x.size = 'N_C'
        x.defval = 1.0
        exec.add(x)

        # spmv
        iexec = self._sets['Iexec']

        # TODO: Egads, another ISL leftover, put this code somewhere else!
        #edom = VarHelper.replaceIterators(str(iexec), 'ii,jj,i,k,j'.split(','))

        spmv = StmtNode('spmv')
        spmv.domain = str(iexec)
        spmv.statements = ['y[i]+=A_prime[jj*R+(i-R*ii)*C+(k-C*b_col[jj])]*x[k]']
        spmv.datamap = '{[i] : 0 <= i < N_R}'
        spmv.reads = ['A(jj,ri,ck)', 'x(k)']
        spmv.writes = ['y(i)']

        # Dense 'y' row vector
        y = DataNode('y')
        y.domain = spmv.datamap
        y.range = 'R'
        y.size = 'N_R'
        exec.add(y)

        exec.add(spmv)

        exec.add(Edge(aprime, spmv))  # A' => spmv edge
        exec.newrow()

        exec.add(Edge(x, spmv))  # x => spmv edge
        exec.newrow()

        exec.add(Edge(spmv, y))  # x => spmv edge
        exec.newrow()

        exec.functions = self.functions
        return exec

class CSRToBSR(FlowGraph):
    def __init__(self, name='csr_to_bsr', nrows=62451, ncols=62451, nnz=2034917, blocksize=(8,8)):
        super().__init__(name)
        N_R = Constant('N_R', str(nrows))
        N_C = Constant('N_C', str(ncols))
        NNZ = Constant('NNZ', str(nnz))
        R = Constant('R', str(blocksize[0]))
        C = Constant('C', str(blocksize[1]))
        self.constants = [N_R, N_C, NNZ, R, C]
        self._exec = FlowGraph('bsr_exec', constants=self.constants)
        self._insp = FlowGraph('bsr_insp', constants=self.constants)

    def convert(self, csr):
        stmt = csr['spmv']
        sname = stmt.label
        pos = sname.find('_')
        if pos > 0:
            sname = sname[pos + 1:]
        omcode = StmtNodeVisitor(stmt).omega()
        assign = ':='
        pos = omcode.index(assign)

        csrf = omcode[0:pos] + assign + ' ' + str(csr.constnames).replace('\'', '') + \
                  ' -> {' + sname + omcode[pos + 4:]
        # Replace uninterpreted functions as ISL does not support them (and Omega is limited)...
        csrf = stmt.graph.set_factory.replaceUFs(csrf, stmt.graph.symtable)
        csrf = csrf[pos+2:]

        # csrfuncs = (csr['index'], csr['col'])
        # bsrfuncs = (Function('b_index', ['ii']), Function('b_col', ['jj']))

        # Iterators...
        # ii = Var('ii', upper='N_R/R', tightup=False)
        # kk = Var('kk', upper='N_C/C', tightup=False)
        # jj = Var('jj', 'b_index(ii)', 'b_index(ii+1)', tightup=False)
        # i = Var('i', upper='N_R', tightup=False)
        # k = Var('k', upper='N_C', tightup=False)
        # j = Var('j', 'index(i)', 'index(i+1)', tightup=False)

        densef = "[N_R, N_C, NNZ, index_i_, index_ip1_] -> {spmv[i,j] -> spmv[i,k,j]: 0 <= i < N_R && 0 <= k < N_C && index_i_ <= j < index_ip1_ && 0 <= index_i_ < NNZ && 0 <= index_ip1_ <= NNZ}"

        # tilef = """[N_R, N_C, index_i_, index_ip1_] -> {spmv[i,k,j] -> [ii,kk,i,k,j]: 0 <= i < N_R && 0 <= k < N_C &&
        #            exists ri, ck: 0 <= ri < R && i = ii * R + ri && 0 <= ck < C && k = kk * C + ck &&
        #            index_i_ <= j < index_ip1_ && N_R > R && N_C > C}"""

        tilef = "[N_R,N_C,index_i_,index_ip1_] -> { spmv[ii,kk,i,k,j] : 0 <= i < N_R && 0 <= k < N_C && exists ri,ck :" + \
                "0 <= ri < R && i=ii*R+ri && 0 <= ck < C && k=kk*C+ck && index_i_ <= j < index_ip1_ && N_C > C && N_R > R}"

        rblock = self['R']
        cblock = self['C']
        tilef = csr.replaceConsts(tilef, (rblock, cblock))

        execf = "[N_R, N_C, R, C, NB, b_index_ii_, b_index_iip1_, b_col_jj_] -> {spmv[ii,kk,i,k,j] -> spmv[ii,jj,i,k,j]: " + \
                "b_index_ii_ <= jj < b_index_iip1_ && kk = b_col_jj_ && j = 0}"

        compf = "[N_R,N_C,index_i_,index_ip1_,col_j_] -> {spmv[ii,kk,i,k,j] -> insp[ii,kk,i,k,j]: k = col_j_ && kk = k/C}"
        compf = csr.replaceConsts(compf, (rblock, cblock))

        fac = ISLFactory.instance()
        icsr = fac.set(csrf)

        print("/* I_csr: %s */" % str(icsr))
        print(fac.codegen(icsr))

        mkdense = fac.map(densef)
        print("/* T_md: %s */" % str(mkdense))
        idense = icsr.apply(mkdense)
        print("/* I_dense: %s */" % str(idense))
        print(fac.codegen(idense))

        #ttile = fac.map(tilef)
        #itile = idense.apply(ttile)
        itile = fac.set(tilef)
        print("/* I_tile: %s */" % itile)
        print(fac.codegen(itile))

        texec = fac.map(execf)
        iexec = itile.apply(texec)
        print("/* I_exec: %s */" % iexec)
        print(fac.codegen(iexec))
        tcomp = fac.map(compf)
        icomp = itile.apply(tcomp)
        print("/* I_comp: %s */" % icomp)
        print(fac.codegen(icomp))

class CSRToBSRInsp(FlowGraph):
    def __init__(self, name='csr-to-bcsr-insp', nrows=62451, ncols=62451, nnz=2034917, blocksize=(9,9)):
        super().__init__(name)

        # Add constants
        N_R = Constant('N_R', str(nrows))
        N_C = Constant('N_C', str(ncols))
        NNZ = Constant('NNZ', str(nnz))
        R = Constant('R', str(blocksize[0]))
        C = Constant('C', str(blocksize[1]))
        self.constants = [N_R, N_C, NNZ, R, C]

        # I_csr
        icsr = IterNode('I_csr')
        icsr.relation = r'\{[i,j] : 0 <= i < N_R && 0 <= j < NNZ && index(i) <= j < index(i+1)\}'
        self.add(icsr)

        # Create top layer of data nodes
        a = DataNode('A')
        a.domain = r'\{[j_A] : 0 <= j_A < NNZ\}'
        a.range = 'R'  # r'\mathbb{R}'
        a.size = 'NNZ'
        self.add(a)

        col = DataNode('col')
        col.domain = r'\{[j_c] : 0 <= j_c < NNZ\}'
        col.range = r'\{[k] : 0 <= k < N_C\}'
        col.size = 'NNZ'
        col.type = 'int'
        self.add(col)

        ndx = DataNode('index')
        ndx.domain = r'\{[i] : 0 <= i < N_R\}'
        ndx.range = r'\{[j_i] : 0 <= j_i < NNZ\}'
        ndx.size = 'N_R + 1'
        ndx.type = 'int'
        self.add(ndx)

        # index => Icsr edge
        self.add(Edge(ndx, icsr))
        self.newrow()

        # T_tile
        itile = IterNode('T_tile')
        itile.relation = r'\{[ii,kk] : 0 <= i < N_R && exists(j,k : k = col(j)) && ii = floor(i/R) && kk = floor(k/C)\}'
        self.add(itile)

        # Icsr => Itile edge
        self.add(Edge(icsr, itile))

        # col => Itile edge
        self.add(Edge(col, itile))

        # make_blocks
        # mb = StmtNode('make_blocks')
        # mb.domain = itile.label
        # mb.statements = ['bset(ii,kk) = 1']
        # mb.datamap = r'\{[ii,kk] : 0 <= ii < ceil(N_R/R) && 0 <= kk < ceil(N_C/C)\}'
        # mb.writes.append('bset(ii,kk)')
        # self.add(mb)
        #
        # # Itile => make_blocks edge
        # self.add(Edge(itile, mb))
        # self.newrow()

        # bset
        # bset = TempNode('bset')
        # self.add(bset)
        #
        # # make_blocks => bset
        # self.add(Edge(mb, bset))
        # self.newrow()

        # count
        count = StmtNode('count')
        count.domain = itile.label
        count.statements = ['count++']
        count.datamap = r'[0]'
        count.writes.append('NB')
        self.add(count)

        # Itile => count
        self.add(Edge(itile, count))

        # order
        order = StmtNode('order')
        order.domain = itile.label
        order.statements = ['ordered_set(ii,kk) = p++']
        order.datamap = r'\{[ii,kk] : 0 <= ii < ceil(N_R/R) && 0 <= kk < ceil(N_C/C)\}'
        order.writes.append('ordered_bset(ii,kk)')
        self.add(order)

        # Itile => order
        self.add(Edge(itile, order))
        self.newrow()

        # NB
        nb = TempNode('NB')
        nb.domain = '[0]'
        nb.range = r'Z>=0'  # r'mathbb{Z}_{\geq 0}'
        self.add(nb)

        # count -> NB
        self.add(Edge(count, nb))

        # ordered_bset
        ord_bset = TempNode('ordered_bset')
        self.add(ord_bset)

        # order -> ordered_bset
        self.add(Edge(order, ord_bset))
        self.newrow()

        # invert
        invert = StmtNode('invert')
        invert.domain = 'I_tile'
        invert.statements = ['b_row[p] = ii', 'b_col[p] = kk', 'p++']
        invert.datamap = r'\{[p,d] : 0 <= p < NB && 0 <= d < 2\}'
        invert.writes = ('b_row(p)', 'b_col(p)')
        self.add(invert)

        # Itile => invert
        self.add(Edge(itile, invert))

        # R_A->A'
        r_map = IterNode('map: R_A->A\'')
        r_map.relation = r'\{[i,j] -> [b,ri,ck] : ii=floor(i/R) && kk=floor(k/C) && ri=i-ii*R && ck=col(j)-kk*C && b=ordered_bset(ii,kk) && A_prime(b,ri,ck)=A(j)\}'
        self.add(r_map)

        # copy
        copy = StmtNode('copy')
        copy.domain = icsr.label
        copy.statements = [r_map.relation]
        copy.datamap = r'\{[b,ri,ck] : 0 <= b < NB && 0 <= ri < R && 0 <= ck < C\}'
        copy.reads = ['A(j)', 'ordered_bset(ii,kk)']
        copy.writes = ['A_prime(b,ri,ck)']
        self.add(copy)

        # I_csr -> copy
        self.add(Edge(icsr, copy))

        # r_map -> copy
        self.add(Edge(r_map, copy))

        # A -> copy
        self.add(Edge(a, copy))

        # NB -> copy
        self.add(Edge(nb, copy))

        # ordered_bset -> copy
        self.add(Edge(ord_bset, copy))

        self.newrow()

        # A_prime
        aprime = DataNode('A_prime')
        aprime.domain = copy.datamap
        aprime.range = 'R'  # r'mathbb{R}'
        aprime.size = 'NB*R*C'
        self.add(aprime)

        # copy -> A_prime
        self.add(Edge(copy, aprime))

        # b_row
        b_row = DataNode('b_row')
        b_row.domain = invert.datamap
        b_row.range = order.datamap
        b_row.size = 'NB'
        self.add(b_row)

        # invert -> b_row
        self.add(Edge(invert, b_row))
        self.newrow()

        # b_col
        b_col = DataNode('b_col')
        b_col.domain = invert.datamap
        b_col.range = order.datamap
        b_col.size = 'NB'
        self.add(b_col)

        # invert -> b_col
        self.add(Edge(invert, b_col))
        self.newrow()
