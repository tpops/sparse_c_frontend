import re

from codegen.ast import *
from codegen.iegenlib import IEGenLib
from codegen.setlib import Var
from codegen.helpers import VarHelper

try:
    import clang.cindex as clindex
    from clang.cindex import CursorKind
    _clangon = True
except:
    _clangon = False

try:
    import islpy as isl
    _islon = True
except:
    print("WARN: islpy package unavailable.")
    _islon = False

class ASTFactory(object):
    @staticmethod
    def getNode(kind, value='', level=0, start=(0,0), end=(0,0), type=None):
        node = None
        if kind == CursorKind.TRANSLATION_UNIT:
            node = Program()
        elif kind == CursorKind.USING_DIRECTIVE:
            node = UsingDir()
        elif kind == CursorKind.NAMESPACE_REF:
            node = NamespaceRef()
        elif kind == CursorKind.NAMESPACE:
            node = Namespace()
        elif kind == CursorKind.FUNCTION_DECL:
            node = FunctionDecl()
        elif kind == CursorKind.PARM_DECL:
            node = ParamDecl()
        elif kind == CursorKind.COMPOUND_STMT:
            node = CompoundStmt()
        elif kind == CursorKind.DECL_STMT:
            node = DeclStmt()
        elif kind == CursorKind.VAR_DECL:
            node = VarDecl()
        elif kind == CursorKind.TYPE_REF:
            node = TypeRef()
        elif kind == CursorKind.IF_STMT:
            node = IfStmt()
        elif kind == CursorKind.FOR_STMT:
            node = ForStmt()
        elif kind == CursorKind.RETURN_STMT:
            node = ReturnStmt()
        elif kind == CursorKind.NULL_STMT:
            node = NullStmt()
        elif kind == CursorKind.LABEL_STMT:
            node = LabelStmt()
        elif kind == CursorKind.FLOATING_LITERAL:
            node = FloatLiteral()
        elif kind == CursorKind.INTEGER_LITERAL:
            node = IntLiteral()
        elif kind == CursorKind.STRING_LITERAL:
            node = StringLiteral()
        elif kind == CursorKind.UNARY_OPERATOR:
            node = UnaryOper()
        elif kind == CursorKind.BINARY_OPERATOR:
            node = BinaryOper()
        elif kind == CursorKind.COMPOUND_ASSIGNMENT_OPERATOR:
            node = CompoundAssignOper()
        elif kind == CursorKind.DECL_REF_EXPR:
            node = DeclRefExpr()
        elif kind == CursorKind.STRUCT_DECL:
            node = StructDecl()
        elif kind == CursorKind.CLASS_DECL:
            node = ClassDecl()
        elif kind == CursorKind.FIELD_DECL:
            node = FieldDecl()
        elif kind == CursorKind.TYPEDEF_DECL:
            node = TypedefDecl()
        elif kind == CursorKind.CXX_ACCESS_SPEC_DECL:
            node = AccessSpecDecl()
        elif kind == CursorKind.UNEXPOSED_EXPR:
            node = None #UnexposedExpr()
        elif kind == CursorKind.ARRAY_SUBSCRIPT_EXPR:
            node = ArraySubscriptExpr()
        elif kind == CursorKind.PAREN_EXPR:
            node = ParenExpr()
        elif kind == CursorKind.CALL_EXPR:
            node = CallExpr()
        elif kind == CursorKind.GNU_NULL_EXPR:
            node = NullExpr()
        elif kind == CursorKind.CONSTRUCTOR:
            node = Constructor()
        elif kind == CursorKind.DESTRUCTOR:
            node = Destructor()
        elif kind == CursorKind.CXX_METHOD:
            node = Method()
        elif kind == CursorKind.MEMBER_REF_EXPR:
            node = MemberRefExpr()
        else:
            #raise TypeError("Invalid type '%s'." % str(kind))
            print("Invalid type '%s'." % str(kind))

        if node is not None:
            node.value = value
            node.level = level
            node.start = start
            node.end = end
            node.type = type

        return node

class SetFactory(object):
    def __init__(self):
        pass    # Nada yet

    def set(self, setstr, name=''):
        pass

    def map(self, mapstr, name=''):
        pass

    def codegen(self, schedule):
        pass

class ISLFactory(SetFactory):
    _instance = None

    def __init__(self, ctx=None):
        super().__init__()
        if _islon and ctx is None:
            ctx = isl.DEFAULT_CONTEXT
        self._context = ctx

    @classmethod
    def instance(cls):
        if ISLFactory._instance is None:
            ISLFactory._instance = ISLFactory()
        return ISLFactory._instance

    @staticmethod
    def validate(expression, name=''):
        # Ensure name is present if applicable
        pos = expression.find('{')
        stmt = expression[pos+1:expression.find('[')].strip()
        if len(name) > 0 and len(stmt) < 1:
            stmt = name
            if pos == 0:
                lhs = expression[0]
            else:
                lhs = expression[0:pos]
            expression = lhs + stmt + expression[pos+1:]

        pos = expression.find(':')
        consts = []
        operands = re.split('&&|and', expression[pos + 1:].rstrip(';').rstrip('}').strip())
        for operand in operands:
            constraint = Var.from_expr(operand)
            if re.match('[A-Za-z_]+', constraint.lower):
                consts.append(constraint.lower)
            if re.match('[A-Za-z_]+', constraint.upper):
                consts.append(constraint.upper)
        if len(consts) > 0:
            expression = '[%s] -> %s' % (','.join(consts), expression)
        return expression

    def replaceUFs(self, code, symtable):
        for symname in sorted(symtable.keys()):
            symbol = symtable[symname]
            if len(symbol) > 0:
                lpos = code.find('%s(' % symname)
                while lpos >= 0:
                    rpos = code.find(')', lpos + 1)
                    args = VarHelper.replaceChars(code[lpos+len(symname)+1:rpos])
                    newname = '%s_%s_' % (symname, args)
                    if len(symbol.sets[0]) < 1:
                        symbol.sets[0] = args  # Set the iterator
                    bpos = code.find(']')
                    npos = code.find(newname)
                    if bpos > 0 and (npos < 0 or npos > bpos):
                        code = code[0:bpos] + ',' + newname + code[bpos:lpos] + newname + code[rpos + 1:]
                    else:
                        code = code[0:lpos] + newname + code[rpos+1:]
                    lpos = code.find('%s(' % symname)
        return code

    def restoreUFs(self, code, functions, iters=()):
        for function in functions:
            funcname = function.name
            pattern = r"%s_" % funcname
            lpos = code.find(pattern)
            while lpos >= 0:
                mpos = lpos + len(funcname) + 1
                rpos = code.find('_', mpos + 1)
                lhs = code[0:lpos]
                rhs = code[rpos+1:]
                mid = code[mpos:rpos]
                arg = VarHelper.restoreChars(mid)
                items = re.split(r'[\+\-\*\/\\\%\&\|]+', arg)
                for i in range(len(items)):
                    item = items[i]
                    if item in iters:
                        arg = arg.replace(item, 'c%d' % iters.index(item))
                newname = '%s[%s]' % (funcname, arg)
                code = lhs + newname + rhs
                lpos = code.find(pattern)
        return code

    def set(self, domain, name=''):
        if domain[0] != '[':
            domain = ISLFactory.validate(domain, name)
        if '(' in domain:
            domain = self.replaceUFs(domain)

        try:
            return isl.Set(domain, self._context)
        except Exception as ex:
            print("ERROR: Set '%s' caused error '%s'" % (domain, str(ex)))
            raise ex

    def map(self, mapstr, name=''):
        try:
            return isl.Map(mapstr, self._context)
        except Exception as ex:
            print("Map '%s' caused error '%s'" % (mapstr, str(ex)))
            raise ex

    def codegen(self, sched):
        bld = isl.AstBuild.from_context(isl.Set("{:}"))
        mp = isl.Map.from_domain_and_range(sched, sched)
        mp = isl.Map.identity(mp.get_space())
        mp = isl.Map.from_domain(sched)
        ast = bld.ast_from_schedule(mp)
        ptr = isl.Printer.to_str(isl.DEFAULT_CONTEXT)
        ptr = ptr.set_output_format(isl.format.C)
        ptr.flush()
        ptr = ptr.print_ast_node(ast)

        # Restore uninterpreted functions...
        iters = sched.split('[')[1].split(']')[0].replace(' ', '').replace('0', 'z').split(',')
        code = self.restoreUFs(ptr.get_str(), iters)
        return code


class IEGenFactory(SetFactory):
    _instance = None

    def __init__(self):
        super().__init__()
        self._iegen = IEGenLib()
        self._constants = {}

    @classmethod
    def instance(cls):
        if IEGenFactory._instance is None:
            IEGenFactory._instance = IEGenFactory()
        return IEGenFactory._instance

    @property
    def constants(self):
        return self._constants.values()

    @constants.setter
    def constants(self, constants):
        for const in constants:
            self._constants[const.name] = const

    def set(self, setstr, name=''):
        return self._iegen.add(setstr, name)

    def map(self, mapstr, name=''):
        return self._iegen.add(mapstr, name)

    def codegen(self, schedule, statements=()):
        # This is where Omega comes in!
        omcode = self._iegen.to_omega(schedule.name)
        astcode = ''

        omcalc = '/usr/local/bin/omegacalc'
        if os.path.isfile(omcalc):
            from tools.system import run
            (out, err) = run(omcalc, omcode)
            if len(err) > 0:
                raise RuntimeError('Omega+ codegen failed with error: \'%s\'' % err)
            lines = list(filter(lambda line: '>>>' not in line, out.split("\n")))
            astcode = "\n".join(lines)
        else:    # Hardcode for now...
            if schedule.name == 'spmv':
                astcode = """for(t1 = 0; t1 <= N_R-1; t1++) {
  for(t2 = index(t1); t2 <= index1(t1)-1; t2++) {
    s0(t1,t2);
  }
}"""
            elif schedule.name == 'Icomp':
                astcode = """for(t1 = 0; t1 <= intFloor(N_R-1,8); t1++) {
  for(t2 = 8*t1; t2 <= min(N_R-1,8*t1+7); t2++) {
    for(t3 = index(t1,t2); t3 <= index1(t1,t2)-1; t3++) {
      t4=col(t1,t2,t3);
      s0(t1,t2,t3,t4);
    }
  }
}"""
            elif schedule.name == 'Iexec':
                astcode = """for(t1 = 0; t1 <= intFloor(N_R-1,8); t1++) {
  for(t2 = b_index(t1); t2 <= b_index1(t1)-1; t2++) {
    for(t3 = 8*t1; t3 <= min(N_R-1,8*t1+7); t3++) {
      for(t4 = 8*b_col(t1,t2); t4 <= min(8*b_col(t1,t2)+7,N_C-1); t4++) {
        s0(t1,t2,t3,t4);
      }
    }
  }
}"""

        # Reformat the code to look like ISCC output
        return self.reformat(schedule, astcode, statements)

    def reformat(self, schedule, code, statements=()):
        # Replace Omega statements (s0,...,sN) with macro names (e.g., spmv)
        for i in range(len(statements)):
            code = code.replace('s%d' % i, statements[i])

        # Replace built-in functions (e.g., min, max, etc.)
        builtins = {'intFloor': 'floord'}
        for builtin in builtins:
            code = code.replace(builtin, builtins[builtin])

        # Update iterators
        ieset = self._iegen[schedule.name]
        iters = ieset.iterators

        itype = 'itype'
        for i in range(len(iters)):
            olditer = 't%d' % (i+1)
            newiter = iters[i]
            pos = code.find(olditer)
            if pos >= 0:
                lhs = code[0:pos]
                rhs = code[pos+len(olditer):]
                code = lhs + itype + ' ' + newiter + rhs
                code = re.sub(r"\b%s\b" % olditer, newiter, code)

        # Replace uninterpreted functions...
        code = self.restoreUFs(code)

        # Finally, replace constants...
        code = self.restoreConsts(code)

        return code

    def restoreConsts(self, code):
        for const in self.constants:
            if len(const.value) > 0:
                code = re.sub(r"\b%s\b" % const.value, const.name, code)
                if re.search(r"^[0-9]+$", const.value):
                    valm1 = str(int(const.value)-1)
                    code = re.sub(r"\b%s\b" % valm1, '(%s-1)' % const.name, code)
        return code

    def restoreUFs(self, code):
        ufuncs = self._iegen.ufuncs
        for ufunc in ufuncs:
            ufname = ufunc['name']

            pos = code.find('%s(' % ufname)
            if pos >= 0:
                pos += len(ufname) + 1
                args = code[pos:code.find(')', pos + 1)]
                oldcall = '%s(%s)' % (ufname, args)
                arglist = args.split(',')

                renamed = len(ufunc['oldname']) > 0
                newargs = ufunc['arity'] > ufunc['oldarity'] and len(arglist) != ufunc['oldarity']

                if renamed:
                    newcall = ufunc['oldname']
                else:
                    newcall = ufname
                newcall += '['

                if renamed or newargs:
                    if newargs:
                        for i in range(ufunc['oldarity']):
                            oldarg = ufunc['oldargs'][-i]
                            if oldarg in ufunc['args']:
                                ndx = ufunc['args'].index(oldarg)
                                try:
                                    arg = arglist[ndx]
                                except Exception as ex:
                                    stop=1
                                newcall += arg + ','
                        newcall = newcall.rstrip(',')
                        arglist = arglist[len(arglist) - ufunc['oldarity']:]

                    if renamed:
                        for i in range(len(arglist)):
                            arglist[i] = ufunc['oldargs'][i].replace(ufunc['args'][i], arglist[i])
                        newcall += ','.join(arglist)
                else:
                    newcall += args
                newcall += ']'
                code = code.replace(oldcall, newcall)
        return code
