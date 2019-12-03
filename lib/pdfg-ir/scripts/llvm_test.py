import os
import sys
import numba
from llvmlite import binding, ir
import traceback as tb
import ast
from tools import files
from collections import OrderedDict
from codegen.setlib import Var

class Tokenizer:
    def __init__(self, line):
        self._line = line
        self._token = None
        self._delims = (' ', '(')
        self._pos = -1
        if self._line[0] == self._delims[0]:
            self._pos = 0
            while self._line[self._pos] == self._delims[0]:
                self._pos += 1
            self._pos -= 1

    def __next__(self):
        if self._pos >= len(self._line):
            return None
        token = ''
        pos = self._pos
        for i in range(len(self._delims)):
            delim = self._delims[i]
            pos = self._line.find(delim, pos + 1)
            if pos > 0:
                token = self._line[self._pos+1:pos]
                if i < len(self._delims)-1 and self._delims[i+1] in token:
                    sub = token.find(self._delims[i+1])
                    token = token[0:sub]
                    pos += sub - 1
                break
        if len(token) < 1:
            token = self._line[self._pos+1:]
            pos = self._pos + len(token)
        self._token = token
        self._pos = pos
        return token.rstrip(',')

    def __iter__(self):
        return self

class Function(object):
    def __init__(self, name='', returns='', params=OrderedDict(), allocs=OrderedDict(), inits=OrderedDict(), begin='', body=''):
        self._name = name
        self._returns = returns
        self._params = params
        self._allocs = allocs
        self._inits = inits
        self._begin = begin
        self._body = body

    def __repr__(self):
        return str(self)

    def __str__(self):
        fstr = '%s %s(%s)' % (self._returns, self._name, ','.join(self._params))
        if len(self._body) > 0:
            fstr = "%s {\n%s\n}" % (fstr, self._body)
        return fstr

    @property
    def name(self):
        return self._name

    @property
    def returns(self):
        return self._returns

    @property
    def params(self):
        return self._params

    @property
    def allocs(self):
        return self._allocs

    @property
    def inits(self):
        return self._inits

    @property
    def body(self):
        return self._body

    @property
    def begin(self):
        return self._begin

    @begin.setter
    def begin(self, begin):
        self._begin = begin

    def append(self, code):
        self._body = "%s\n%s\n" % (self._body, code)

def llvm_test(irfile):
    llvmir = "\n".join(files.read(irfile))
    modref = binding.parse_assembly(llvmir)
    irname = irfile.split('/')[-1].split('.')[0]
    mod = ir.Module(irname)

    # Parsing works, now read the docs!
    # https://llvmlite.readthedocs.io/en/latest/user-guide/ir/modules.html

    for globvar in modref.global_variables:
        mod.add_global(ir.GlobalVariable(mod, globvar.type, globvar.name))

    # Uninterpreted Function Pattern:
    # 1) Load the address of the index array (e.g., rows):
    #   %2 = load i32*, i32** %rows.addr, align 8
    # 2) Load the index value (e.g., i)
    #   %3 = load i32, i32* %i, align 4
    # 3) Calculate the array offset:
    #   %idxprom = sext i32 %3 to i64
    #   %arrayidx = getelementptr inbounds i32, i32* %2, i64 %idxprom
    #   %4 = load i32, i32* %arrayidx, align 4
    # 4) Store the value in iter (e.g., j)
    #   store i32 %4, i32* %j, align 4
    func = None
    inentry = False
    infor = False
    incond = False
    inbody = False
    ininc = False
    label = ''
    iname = ''
    loops = OrderedDict()
    stack = []

    for funcref in modref.functions:
        lines = str(funcref).split("\n")
        lnum = 0
        for line in lines:
            lnum += 1

            if len(line) > 0 and line[0] != ';':
                tokenizer = Tokenizer(line)
                item = next(tokenizer)
                if item == 'define':
                    next(tokenizer)             # 'dso_local'
                    returns = next(tokenizer)
                    fname = next(tokenizer)

                    # Function definition
                    args = OrderedDict()
                    token = next(tokenizer)
                    while token != '#0' and token != '{':
                        ptype = token
                        pname = next(tokenizer).rstrip(')')
                        args[pname] = (pname, ptype)
                        token = next(tokenizer)
                    func = Function(fname, returns, args)
                    #ftype = ir.FunctionType()
                    #func = ir.Function(mod, funcref.type, )

                elif ':' in item:       # Label
                    label = item.rstrip(':')
                    inentry = (label == 'entry')
                    infor = (label.startswith('for.'))
                    if infor:
                        incond = ('.cond' in label)
                        inbody = ('.body' in label)
                        ininc = ('.inc' in label)
                        if incond:
                            iname = ''

                elif inentry:
                    if item == 'store':
                        # store i32 %N, i32* %N.addr, align 4
                        ltype = next(tokenizer)
                        lval = next(tokenizer).lstrip('%')
                        rtype = next(tokenizer)
                        rval = next(tokenizer).lstrip('%')
                        next(tokenizer)     # 'align'
                        align = next(tokenizer)
                        func.inits[rval] = (ltype, lval, rtype, rval, align)
                    elif item == 'br':
                        next(tokenizer)     # 'label'
                        func.begin = next(tokenizer)
                    else:
                        name = item        #.replace('.addr', '')
                        next(tokenizer)    # '='
                        next(tokenizer)    #  ‘alloca’ instruction allocates sizeof(<type>)*nElems bytes of memory on the runtime stack
                        dtype = next(tokenizer)
                        next(tokenizer)    # 'align'
                        align = next(tokenizer)
                        func.allocs[name] = (name, dtype, align)

                elif incond:
                    if item.startswith('br'):
                        next(tokenizer)     # i1
                        next(tokenizer)     # %cmp
                        next(tokenizer)     # label
                        loops[iname]['inlabel'] = next(tokenizer).lstrip('%')
                        next(tokenizer)  # label
                        loops[iname]['outlabel'] = next(tokenizer).lstrip('%')
                    else:
                        next(tokenizer)  # '='
                        cmd = next(tokenizer)  # 'load' or 'cmp'
                        if cmd == 'load':
                            next(tokenizer)     # ltype
                            next(tokenizer)     # rtype
                            if len(iname) < 1:
                                iname = next(tokenizer).lstrip('%')
                                if iname not in loops:
                                    loops[iname] = {'iter': Var(iname), 'body': ''}
                                    init = func.inits[iname]
                                    loops[iname]['iter'].lower = init[1]
                            else:
                                end = next(tokenizer).lstrip('%').replace('.addr', '')
                                loops[iname]['iter'].upper = end
                        elif cmd == 'icmp':
                            comp = next(tokenizer)
                            loops[iname]['iter'].tightup = ('lt' not in comp)

                elif inbody:
                    if item[0] == '%':
                        res = item
                        cmd = next(tokenizer)
                        if cmd == '=':
                            cmd = next(tokenizer)
                    else:
                        cmd = item
                    if cmd == 'load':
                        next(tokenizer)  # ltype
                        next(tokenizer)  # rtype
                        var = next(tokenizer)
                        stack.append(var)
                    elif cmd == 'sext':           # cast i32 to i64
                        pass
                    elif cmd == 'getelementptr':  # calculate array offset
                        pass
                    elif cmd == 'store':
                        ltype = next(tokenizer)
                        lval = next(tokenizer).lstrip('%')
                        rtype = next(tokenizer)
                        rval = next(tokenizer).lstrip('%')
                        next(tokenizer)  # 'align'
                        align = next(tokenizer)
                        if 'idx' in stack[-1]:
                            lval = ''
                            while len(stack) > 0:
                                arridx = stack.pop()
                                arritr = stack.pop().lstrip('%')
                                arrptr = stack.pop().lstrip('%').replace('.addr', '')
                                lval = '%s[%s]' % (arrptr, arritr)
                        func.inits[rval] = (ltype, lval, rtype, rval, align)
                    elif cmd == 'label':
                        label = next(tokenizer).lstrip('%')
                        loops[iname]['condlabel'] = label
                elif ininc:
                    stop=3


    stop=1

def main():
    llvm_test(sys.argv[1])

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt as e: # Ctrl-C
        print("Closing gracefully on keyboard interrupt...")
    except Exception as e:
        print('ERROR: ' + str(e))
        tb.print_exc()
