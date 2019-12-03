from abc import abstractmethod

from tools import strings
from tools import system

import copy as cp
import re
import shutil
#import z3

from codegen.helpers import *

def format_latex(formula):
    return LatexHelper.format(formula)

def replace_chars(formula):
    return VarHelper.replaceChars(formula)

def list_vars(sets):
    return VarHelper.listVars(sets)

class ISLError(Exception):
    def __init__(self, message):    # Call the base class constructor with the parameters it needs
        super(ISLError, self).__init__(message)

class Constant(object):
    def __init__(self, name, val=''):
        if ':=' in name:
            (lhs, rhs) = name.split(':=')
            self._name = lhs.rstrip()
            self._value = rhs.lstrip()
        else:
            self._name = name
            self._value = val

    def __len__(self):
        return 0

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def type(self):
        if '"' in self._value:
            type = 'char *'
        elif '.' in self.value:
            type = 'float'
        else:
            type = 'int'
        return type

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value

    def __str__(self):
        return '%s := %s;' % (self._name, self._value)

    def __repr__(self):
        return self.__str__()

    def latex(self):
        return '%s &= %s' % (LatexHelper.format(self._name), self._value)

    def omega(self):
        return 'symbolic %s;' % self._name

class Function(object):
    def __init__(self, name='', sets=[], mapping=[]):
        self._name = name
        self._sets = sets
        self._mapping = mapping
        #self._function = z3.Function(name, z3.IntSort(), z3.IntSort())

    @classmethod
    def from_expr(cls, expr):
        lpos = expr.find('(')
        if lpos > 0:
            name = expr[0:lpos]
            rpos = expr.find(')', lpos + 1)
            arg = expr[lpos+1:rpos]
            func = Function(name, (arg))
        else:
            func = Function(expr)
        return func

    def __len__(self):
        return len(self._sets)

    def add(self, space):
        self._sets.append(space)

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def mapping(self):
        return self._mapping

    @mapping.setter
    def mapping(self, mapping):
        self._mapping = mapping

    @property
    def sets(self):
        return self._sets

    @sets.setter
    def sets(self, sets):
        self._sets = sets

    def apply(self, other):
        raise(NotImplementedError("Function.apply is abstract, create subclass and impelement apply method."))

    def __mul__(self, other):       # Alias for apply...
        self.apply(other)

    def __str__(self):              # Fxn := [T,N] -> { S[t,i] -> [t,i] };
        nsets = len(self._sets)
        out = self.name + " := " + VarHelper.listVars(self._sets)
        out += " -> { "
        for i in range(nsets):
            set = self._sets[i]
            out += set.name + "["

            vars = set.vars
            nvars = len(vars)
            for j in range(nvars):
                out += vars[j].name
                if j < nvars - 1:
                    out += ","
            out += "] -> ["

            mapping = self._mapping
            for j in range(len(mapping)):
                out += mapping[j]
                if j < nvars - 1:
                    out += ","

            out += "]"
            if i < nsets - 1:
                out += ";\n"

        out += " };"

        return out

    def latex(self):
        # Fxn := [T,N] -> { S[t,i] -> [t,i] };
        nsets = len(self._sets)
        out = LatexHelper.format(self.name) + " &= " + list_vars(self._sets)

        out += r" \rightarrow \{ "
        for i in range(nsets):
            set = self._sets[i]
            out += LatexHelper.format(set.name) + "["

            vars = set.vars
            nvars = len(vars)
            for j in range(nvars):
                out += LatexHelper.format(vars[j].name)
                if j < nvars - 1:
                    out += ","

            out += r"] \rightarrow ["
            mapping = self._mapping
            for j in range(len(mapping)):
                out += mapping[j]
                if j < nvars - 1:
                    out += ", "
            out += "]"

            if i < nsets - 1:
                out += r" \\ "

        out += r" \}"

        return out

class Var(object):
    def __init__(self, name='', lower='0', upper='N', tightlow=True, tightup=True, type='int'):
        self._name = name
        self._lower = lower
        self._upper = upper
        self._tightlow = tightlow
        self._tightup = tightup
        self._type = type
        #self._int = z3.Int(name)

    @classmethod
    def from_expr(cls, expr):
        items = re.split(r'\s+', expr.strip())
        if len(items) > 3:
            try:
                (lower, lhsop, name, rhsop, upper) = items
                var = Var(name, lower, upper, '=' in lhsop, '=' in rhsop)
            except Exception as ex:
                stop=1
        else:
            (name, oper, value) = items
            if '>' in oper:
                var = Var(name, value, '', '=' in oper)
            elif '<' in oper:
                var = Var(name, upper=value, tightup='=' in oper)
            else:
                var = Var(name, value, value, True, True)
        return var

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def lower(self):
        return self._lower

    @lower.setter
    def lower(self, lower):
        self._lower = lower

    @property
    def upper(self):
        return self._upper

    @upper.setter
    def upper(self, upper):
        self._upper = upper

    @property
    def bounded(self):
        return len(self._lower) > 0 and len(self._upper) > 0

    @property
    def tightup(self):
        return self._tightup

    @tightup.setter
    def tightup(self, tightup):
        self._tightup = tightup

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, type):
        self._type = type

    def __str__(self):
        #lower = replace_chars(self._lower)
        lower = self._lower
        #upper = replace_chars(self._upper)
        upper = self._upper
        if len(lower) < 1:
            oper = "<"
            if self._tightup:
                oper += "="
            out = '%s %s %s' % (self._name, oper, upper)
        elif len(upper) < 1:
            oper = ">"
            if self._tightlow:
                oper += "="
            out = '%s %s %s' % (self._name, oper, lower)
        elif lower == upper:
            oper = '='
            out = '%s %s %s' % (self._name, oper, lower)
        else:
            leftop = '<'
            if self._tightlow:
                leftop += '='
            rightop = '<'
            if self._tightup:
                rightop += '='
            out = '%s %s %s %s %s' % (lower, leftop, self._name, rightop, upper)
        return out

    def __repr__(self):
        return self.__str__()

    def latex(self):
        lower = format_latex(self._lower)
        upper = format_latex(self._upper)
        if len(lower) < 1:
            oper = "<"
            if self._tightup:
                oper = r'\leq'
            out = '%s %s %s' % (self._name, oper, upper)
        elif len(upper) < 1:
            oper = ">"
            if self._tightlow:
                oper = r'\geq'
            out = '%s %s %s' % (self._name, oper, lower)
        elif lower == upper:
            oper = '='
            out = '%s %s %s' % (self._name, oper, lower)
        else:
            leftop = '<'
            if self._tightlow:
                leftop = r'\leq'
            rightop = '<'
            if self._tightup:
                rightop = r'\leq'
            out = '%s %s %s %s %s' % (lower, leftop, self._name, rightop, upper)
        return out

class Set(object):
    def __init__(self, name='', vars=[]):
        self._name = name
        self._vars = vars
        self._size = ''

    def add(self, var):
        self._vars.append(var)

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def vars(self):
        return self._vars

    @vars.setter
    def vars(self, vars):
        self._vars = vars

    @property
    def islset(self):
        return ISLFactory().set(str(self))

    @classmethod
    def from_expr(cls, expr):
        asgn_op = ':='
        whereop = ':'
        name = ''

        pos = expr.find(asgn_op)
        if pos > 0:
            name = expr[0:pos].rstrip()
            expr = expr[pos+len(asgn_op):].lstrip()
        set = Set(name)

        pos = expr.find(whereop)
        if pos > 0:
            condlist = expr[pos + 1:].rstrip('}')
            conds = re.split('and|&&', condlist)
            set.vars = []
            [set.vars.append(Var.from_expr(cond.strip())) for cond in conds]
        return set

    @property
    def size(self):
        if len(self._size) < 1:
            sizes = []
            for var in self._vars:
                lower = var.lower
                upper = var.upper
                hasoper = '+' in upper or '-' in upper or '*' in upper or '/' in upper
                if hasoper:
                    upper = '(%s)' % upper
                size = upper
                if len(lower) > 0 and lower != '0':
                    size += '-'
                    hasoper = '+' in upper or '-' in upper or '*' in upper or '/' in upper
                    if hasoper:
                        lower = '(%s)' % lower
                    size += lower
                if var.tightup:
                    size = '(%s+1)' % size
                sizes.append(size)
            self._size = '*'.join(sizes)
        return self._size

    def __str__(self):
        # S[t, i]: 1 <= t <= T and 1 <= i <= N
        out = self._name + "["

        nvars = len(self._vars)
        for i in range(nvars):
            out += self._vars[i]._name
            if i < nvars - 1:
                out += ","

        out += "] : "
        for i in range(nvars):
            out += str(self._vars[i])
            if i < nvars - 1:
                out += " and "

        return out

    def __repr__(self):
        return self.__str__()

    def latex(self):
        # S[t, i]: 1 <= t <= T and 1 <= i <= N
        out = format_latex(self._name) + "["

        nvars = len(self._vars)
        for i in range(nvars):
            out += format_latex(self._vars[i]._name)
            if i < nvars - 1:
                out += ","

        out += "]\;|\;"
        for i in range(nvars):
            out += self._vars[i].latex()
            if i < nvars - 1:
                out += r" \wedge "

        return out


class Domain(object):
    def __init__(self, name='', sets=[]):
        self._name = name
        self._sets = sets

    def add(self, space):
        self._sets.append(space)

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    def __add__(self, other):
        # Union -> New := Self U Other
        pass

    def __str__(self):
        # Domain := [T,N] -> { S[t,i] : 1<=t<=T and 1<=i<=N };
        out = self._name + " := ["
        expr = re.compile(r'^[0-9]+$')

        nsets = len(self._sets)
        for i in range(nsets):
            vars = self._sets[i]._vars
            nvars = len(vars)
            for j in range(nvars):
                lower = vars[j].lower
                if len(lower) > 0 and not expr.match(lower):
                    out += replace_chars(lower)
                    if j < nvars - 1:
                        out += ","
                upper = vars[j].upper
                if len(upper) > 0 and not expr.match(upper):
                    out += replace_chars(upper)
                    if j < nvars - 1:
                        out += ","

        out += "] -> { "
        for i in range(nsets):
            out += str(self._sets[i])
            if i < nsets - 1:
                out += ";\n"

        out += " };"

        return out

    def latex(self):
        # Domain := [T,N] -> { S[t,i] : 1<=t<=T and 1<=i<=N };
        nsets = len(self._sets)
        out = format_latex(self._name) + r" &= \{"
        for i in range(nsets):
            out += self._sets[i].latex()
            if i < nsets - 1:
                out += r" \\ "
        out += r" \}"

        return out

# class ISLTransform(object):
#     def __init__(self, name=''):
#         self._name = name
#
#     @property
#     def name(self):
#         return self._name
#
#     @name.setter
#     def name(self, name):
#         self._name = name
#
#     @abstractmethod
#     def transform(self, schedule):
#         pass

class Skew(Function):
    def __init__(self, name='skew', offsets=[]):
        super().__init__(name)
        self._offsets = offsets

    def apply(self, schedule):
        newSched = cp.copy(schedule)

        mapping = newSched._mapping
        vars = newSched._sets[0]._vars
        for i in range(len(self._offsets)):
            offset = self._offsets[i]
            mapStr = vars[i].name
            if len(offset) > 0:
                if offset[0] != '-' and offset[0] != '+':
                    mapStr += '+'
                mapStr = mapStr + str(offset)

            if i < len(mapping):
                mapping[i] = mapStr
            else:
                mapping.append(mapStr)

        newSched._mapping = mapping
        #newSched._name = self._name + newSched._name

        return newSched

class Apply(Function):
    def __init__(self, name='apply', lhs=None, rhs=None):
        super().__init__(name)
        self._lhs = lhs
        self._rhs = rhs

    def apply(self, rhs):
        # TODO: Apply the operation...
        self._rhs = rhs

    def __str__(self):
        return '%s := %s * %s;' % (self._name, self._lhs.name, self._rhs.name)

    def latex(self):
        return r"%s &= %s(%s)" % (format_latex(self._name), format_latex(self._lhs.name), format_latex(self._rhs.name))

class Union(Function):
    def __init__(self, name='union', lhs=None, rhs=None):
        super().__init__(name)
        self._lhs = lhs
        self._rhs = rhs

    def apply(self, rhs):
        # TODO: Merge the domains
        # [N_R, index_i_, index_ip1_, col_k_] -> {c_map[i, j = col_k_, k]: 0 <= i < N_R and index_i_ <= k < index_ip1_;
        #                                         cinv_map[i, j = col_k_, k]: 0 <= i < N_R and index_i_ <= k < index_ip1_}
        self._rhs = rhs

    def latex(self):
        return r"%s &= %s \cup %s" % (format_latex(self._name), format_latex(self._lhs.name), format_latex(self._rhs.name))

    def __str__(self):
        return '%s := %s + %s;' % (self._name, self._lhs.name, self._rhs.name)

class Call(Function):
    def __init__(self, name='print', args=[]):
        super().__init__(name)
        self._args = args

    def __str__(self):
        return '%s(%s);' % (self._name, ','.join(self._args))

    def latex(self):
        formatted = [format_latex(arg) for arg in self._args]
        return '%s(%s)' % (format_latex(self._name), ','.join(formatted))

class Fuse(Function):
    def __init__(self, name='', sets=[], index=0, ordering=[]):
        self._name = name
        self._sets = sets
        self._index = index
        if len(ordering) < 1:
            [ordering.append(i) for i in range(len(self._sets))]
        self._ordering = ordering

    def apply(self, ordering=[]):
        # TODO: Actually fuse sets rather than just building a string for ISCC to do it...
        self._ordering = ordering

    def __str__(self):
        out = "%s := %s -> {\n" % (self._name, list_vars(self._sets))
        for i in range(len(self._sets)):
            myset = self._sets[i]
            out += '    %s[' % myset.name
            for var in myset.vars:
                out += var.name
                if var.name != myset.vars[-1].name:
                    out += ','
            out += '] -> [%d,' % self._index
            for var in myset.vars:
                out += var.name + ','
            out += "%d];\n" % self._ordering[i]
        out += "};"
        return out

    def latex(self):
        out = r"%s &= \{ " % format_latex(self._name)
        for i in range(len(self._sets)):
            myset = self._sets[i]
            out += '    %s[' % format_latex(myset.name)
            for var in myset.vars:
                out += format_latex(var.name)
                if var.name != myset.vars[-1].name:
                    out += ','
            out += r"] \rightarrow [%d," % self._index
            for var in myset.vars:
                out += var.name + ','
            out += r"%d], " % self._ordering[i]
        out = out[0:len(out)-2]
        out += r" \}"
        return out

class Generator(object):
    def __init__(self, benchmark={}, out=None):
        self._benchmark = benchmark
        self._out = out
        self._isl = ''
        self._gen = ''

    def benchmark(self):
        return self._benchmark

    def code(self):
        return self._gen

    def isl(self):
        return self._isl

    def readISL(self, file=''):
        if len(file) > 0:
            code = ''
            f = open(file, 'r')
            for line in f:
                code += line
            f.close()
            self._isl = code

    def transform(self, schedule, domain):
        code = ''
        code += str(domain) + "\n"
        code += str(schedule) + "\n"
        code += "codegen(" + schedule.name + " * " + domain.name + ");\n"
        self._isl = code

        return code

    def getISL(self):
        code = self._isl
        benchmark = self._benchmark
        vars = benchmark['vars']

        for key in vars:
            val = str(vars[key])
            patt = re.compile("(\$%s)" % key)  # parentheses for capture groups
            code = re.sub(patt, val, code)

        return code

    def generate(self):
        benchmark = self._benchmark
        code = ''

        ompRegion = False
        ompLevel = -1
        ompPragma = ''
        ompLines = []

        # Start reading the template...
        template = '%s/%s' % (benchmark['path'], benchmark['template'])
        file = open(template, 'r')

        # Peak at first line to look for <Name> tag.
        line = file.readline().rstrip()

        if '<Name' in line:
            if '=' in line:
                benchmark['output'] = line.split('=')[1].replace('"', '').rstrip('>')
            else:
                code += line.replace('<Name>', benchmark['name'])

            file.close()
            file = open(template, 'r')
        else:
            code += line + "\n"

        if 'output' not in benchmark or len(benchmark['output']) < 1:
            benchmark['output'] = benchmark['name']

        if '.h' not in benchmark['output']:
            benchmark['output'] = '%s.h' % benchmark['output']

        outFile = '%s/%s' % (benchmark['path'], benchmark['output'])
        print("Creating output file '%s'..." % outFile)
        self._out = open(outFile, 'w')

        # Read the rest of the template...
        for line in file:
            line = line.rstrip()
            if '<Variables' in line and 'vars' in benchmark:
                varnames = sorted(benchmark['vars'].keys())
                for var in varnames:
                    code += '#define ' + var + ' ' + str(benchmark['vars'][var]) + "\n"
                    if var == 'TILE_SIZE':
                        code += '#define TILE_MASK ' + str(int(benchmark['vars'][var]) - 1) + "\n"
                        code += '#define TILE_SIZE2 ' + str(int(benchmark['vars'][var]) * 2) + "\n"
                        code += '#define TILE_MASK2 ' + str(int(benchmark['vars'][var]) * 2 - 1) + "\n"
            elif '<OMP' in line:
                ompRegion = True
                if 'Level' in line:
                    begin = line.find('=', line.find('Level') + 5) + 1
                    end = line.find(' ', begin)
                    if end < begin:
                        end = line.find('>', begin)
                    ompLevel = int(line[begin:end].replace('"', ''))
                if 'Pragma' in line:
                    begin = line.find('"', line.find('Pragma') + 6) + 1
                    end = line.find('"', begin)
                    if end < begin:
                        end = line.find('>', begin)
                    ompPragma = line[begin:end].replace('"', '')
            elif '</OMP' in line:
                ompRegion = False
            elif ompRegion:
                ompLines.append(line)
            elif '<ISL' in line:
                # Get ISL code...
                islFile = benchmark['isl']
                if len(islFile) < 1 and 'File' in line:
                    begin = line.find('=', line.find('File') + 4) + 1
                    end = line.find(' ', begin)
                    if end < begin:
                        end = line.find('>', begin)
                    islFile = line[begin:end].replace('"', '')

                islFile = '%s/%s' % (benchmark['path'], islFile)
                self.readISL(islFile)
                islCode = self.getISL()

                (islLines, error) = system.run([benchmark['iscc']], islCode)
                islLines = islLines.split("\n")

                if len(islLines) < 1:
                    raise ISLError("Unable to generate code from ISL file '%s'." % islFile)
                elif len(strings.grep('error', islLines, True)) > 0:
                    raise ISLError("ISL error in file '%s': %s" % islFile, "\n".join(islLines))

                if benchmark['skipguard'] and 'if (' in islLines[0]:
                    guard = islLines[0]
                    islLines = islLines[1:]
                    while len(islLines[-1]) < 1:
                        del islLines[-1]
                    if '{' in guard and '}' in islLines[-1]:
                        del islLines[-1]

                # Merge ISL code and OMP code...
                index = 0
                if ompLevel > 0 and len(ompPragma) > 0:
                    ompLevel -= 1    # This was implemented when box loop was not part of the kernel so back it up one...
                    nesting = 0
                    while index < len(islLines):
                        if 'for (' in islLines[index]:
                            if nesting == ompLevel:
                                break
                            nesting += 1
                        index += 1

                    # Insert OMP pragma before index...
                    islLines.insert(index, ompPragma)
                    index += 1

                # And any code after index...
                if len(ompLines) > 0:
                    if index > 0:
                        newLines = islLines[0:index + 1]
                        wrapped = False
                        if '{' not in newLines[-1]:
                            newLines[-1] += ' {'  # Add opening brace...
                            wrapped = True
                        newLines.extend(ompLines)
                        newLines.extend(islLines[index + 1:])
                        if wrapped:
                            #newLines[-1] += "    }\n"  # Add closing brace...
                            newLines.append('}')
                        islLines = newLines
                    else:
                        ompLines.append('')
                        ompLines.extend(islLines)
                        islLines = ompLines

                    code += "\n".join(islLines).rstrip() + "\n"

            else:
                code += line + "\n"
                if '#pragma omp' in line:
                    ompPragma = line.lstrip()

        file.close()

        self._gen = code

        if self._out is not None:
            self._out.write(code)
            self._out.close()

        # Now we have to modify the header file for the benchmark class...
        classFile = '%s/%s' % (benchmark['path'], benchmark['header'])
        tempFile = '%s~' % classFile
        print("Updating class file '%s'..." % classFile)
        fin = open(classFile, 'r')
        fout = open(tempFile, 'w')

        for line in fin:
            fout.write(line)
            if '<Include' in line:
                fout.write("#include \"%s\"\n" % benchmark['output'])
                line = fin.readline()   # Discard the next line

        fin.close()
        fout.close()

        shutil.move(tempFile, classFile)

        return code
