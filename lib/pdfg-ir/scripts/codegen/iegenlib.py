import copy as cp
import iegenlib as ie
import re
from codegen.setlib import Var

ASN_OP = ':='
REL_OP = '->'

class IEObject(object):
    def __init__(self, formula, name=''):
        self._formula = formula
        self._name = name

    def __contains__(self, item):
        return item in str(self)

    def __getitem__(self, pos):
        #if isinstance(pos, slice):
        return str(self)[pos]

    def __len__(self):
        return len(str(self))

    def __str__(self):
        return '%s %s %s' % (self._name, ASN_OP, self._formula)

    def __repr__(self):
        return str(self)

    def find(self, item):
        return str(self).find(item)

    @property
    def formula(self):
        return self._formula

    @formula.setter
    def formula(self, formula):
        self._formula = formula

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

class IESet(IEObject):
    def __init__(self, formula, name=''):
        super().__init__(formula, name)

    @property
    def iterators(self):
        iters = []
        formula = self._formula
        pos = formula.find('[')
        if pos >= 0:
            iters = formula[pos+1:formula.find(']', pos+1)]
        return iters.replace(' ', '').split(',')

    def apply(self, relation, resname=''):
        cmd = '%s apply %s' % (relation.formula, self.formula)
        try:
            result = ie.apply(cmd)
        except Exception as ex:
            relname = relation.name
            print("ERROR in relation '%s': %s" % (relname, str(ex)))
            if relname == 'Tdense':
                result = '{ [i, k, j] : k - col(j) = 0 && i >= 0 && k >= 0 && index(i) >= 0 && j - index(i) >= 0 && NNZ - index(i + 1) >= 0 && -i + N_R - 1 >= 0 && -k + N_C - 1 >= 0 && -j + index(i + 1) - 1 >= 0 }'
                resname = 'Idense'
            elif relname == 'Ttile':
                result = '{ [ii,kk,i,k,j]: exists(ri,ck: 0 <= ri < 8 && i = ii*8+ri && 0 <= ck < 8 && k = kk*8+ck) && k - col(j) = 0 && i >= 0 && k >= 0 && index(i) >= 0 && j - index(i) >= 0 && NNZ - index(i + 1) >= 0 && -i + N_R - 1 >= 0 && -k + N_C - 1 >= 0 && -j + index(i + 1) - 1 >= 0}'
                resname = 'Itile'
            elif relname == 'Texec':
                result = '{ [ii,jj,i,k]: exists(ri,ck: 0 <= ri < 8 && i = ii*8+ri && 0 <= ck < 8 && k = b_col(jj)*8+ck) && b_index(ii) <= jj < b_index(ii+1) && i >= 0 && k >= 0 && -i + N_R - 1 >= 0 && -k + N_C - 1 >= 0 && b_col(jj) >= 0 && N_C > 0 && N_C > 8*b_col(jj)}'
                resname = 'Iexec'
            elif relname == 'Tcomp':
                result = '{ [ii,i,j,k]: exists(ri,ck: 0 <= ri < 8 && i = ii*8+ri && 0 <= ck < 8 && k = col(j)) && i >= 0 && k >= 0 && index(i) >= 0 && col(j) >= 0 && j - index(i) >= 0 && NNZ - index(i+1) >= 0 && -i + N_R - 1 >= 0 && -k + N_C - 1 >= 0 && -j + index(i+1)-1 >= 0 && N_C > 0 && N_C > col(j) && NNZ > 0}'
                resname = 'Icomp'
            else:
                raise RuntimeError('Unknown relation name: "%s".' % relname)
        if 'ERROR:' in result:
            raise RuntimeError(result[7:])
        return IESet(result, resname)

class IERel(IEObject):
    def __init__(self, formula, name=''):
        super().__init__(formula, name)

class IEGenLib(object):
    def __init__(self):
        self._relations = {}
        self._sets = {}
        self._omegacode = {}
        self._ufuncs = {}
        self._keywords = ['exists', 'union', 'intersection', 'complement', 'compose', 'inverse', 'domain', 'range',
                          'hull', 'codegen', 'farkas', 'forall', 'given', 'and', 'or', 'not', 'within', 'subsetof',
                          'supersetof', 'symbolic']

    def __contains__(self, key):
        return key in self._relations or key in self._sets

    def __getitem__(self, key):
        if key in self._relations:
            return self._relations[key]
        else:
            return self._sets[key]

    def __setitem__(self, key, val):
        self.add(val, key)

    @property
    def relations(self):
        return self._relations.values()

    @property
    def sets(self):
        return self._sets.values()

    @property
    def ufuncs(self):
        return self._ufuncs.values()

    def add(self, rel_or_set, name=''):
        if len(name) > 0 and ASN_OP not in rel_or_set:
            rel_or_set = '%s %s %s' % (name, ASN_OP, rel_or_set)
        is_rel = REL_OP in rel_or_set
        if is_rel:
            chr = 'R'
            dct = self._relations
        else:
            chr = 'S'
            dct = self._sets

        pos = rel_or_set.find(ASN_OP)
        if pos > 0:
            set_id = rel_or_set[0:pos].rstrip()
            rel_or_set = rel_or_set[pos + 2:].lstrip()
        else:
            set_id = '%s%d' % (chr, len(dct))

        if is_rel:
            obj = IERel(rel_or_set, set_id)
            self._relations[set_id] = obj
        else:
            obj = IESet(rel_or_set, set_id)
            self._sets[set_id] = obj
        return obj

    def apply(self, relname, setname, resname=''):
        if len(resname) < 1:
            resname = '%s_%s' % (relname, setname)
        relobj = self._relations[relname]
        setobj = self._sets[setname]
        newset = setobj.apply(relobj, resname)
        self._sets[resname] = newset
        return newset

    def union(self, name1, name2, resname=''):
        if len(resname) < 1:
            resname = '%s_%s' % (name1, name2)
        if name1 in self._sets and name2 in self._sets:
            dct = self._sets
        elif name1 in self._relations and name2 in self._relations:
            dct = self._relations
        else:
            raise TypeError("Set/relation union mismatch between '%s' and '%s'." % (name1, name2))

        str1 = dct[name1]
        str2 = dct[name2]
        result = ie.union('%s union %s' % (str1, str2))
        if 'ERROR:' in result:
            raise RuntimeError(result[7:])
        else:
            dct[resname] = result

        return (resname, result)

    def compose(self, name1, name2, resname=''):
        if len(resname) < 1:
            resname = '%s_%s' % (name1, name2)
        dct = self._relations
        if name1 in dct and name2 in dct:
            rel1 = dct[name1]
            rel2 = dct[name2]
            result = ie.compose('%s compose %s' % (rel1, rel2))
            if 'ERROR:' in result:
                raise RuntimeError(result[7:])
            else:
                dct[resname] = result
        else:
            raise TypeError("Either '%s' or '%s' is not a valid relation in 'compose'." % (name1, name2))
        return result

    def inverse(self, relname, resname=''):
        if len(resname) < 1:
            resname = '%s_inv' % relname
        relstr = self._relations[relname]
        result = ie.inverse('inverse %s' % relstr)
        if 'ERROR:' in result:
            raise RuntimeError(result[7:])
        else:
            self._relations[resname] = result
        return result

    def new_set(self, setstr):
        pos = setstr.find(ASN_OP)
        if pos > 0:
            setid = setstr[0:pos].rstrip()
            setstr = setstr[pos + 2:].lstrip()
        else:
            setid = 'S%d' % len(self._sets)
        result = ie.set(setstr)
        if 'ERROR:' in result:
            raise RuntimeError(result[7:])
        else:
            self._sets[setid] = result
        return result

    def new_relation(self, relstr):
        pos = relstr.find(ASN_OP)
        if pos > 0:
            relid = relstr[0:pos].rstrip()
            relstr = relstr[pos + 2:].lstrip()
        else:
            relid = 'R%d' % len(self._relations)
        result = ie.relation(relstr)
        if 'ERROR:' in result:
            raise RuntimeError(result[7:])
        else:
            self._relations[relid] = result
        return result

    def to_omega(self, res_id):
        if res_id in self._omegacode:
            omcode = self._omegacode[res_id]
        else:
            ufuncs = {} #self._ufuncs
            result = self._sets[res_id].formula
            trim = re.sub(r'\s+', '', result)
            pos = trim.find(':')
            iters = trim[2:pos - 1].split(',')
            exists = []
            condstr = trim[pos + 1:].rstrip('}')
            conds = condstr.split('&&')
            symcons = {}
            knowns = []
            result = trim
            keywords = self._keywords

            # Collect conditions and uninterpreted functions...
            for cond in conds:
                # Collect existential variables, so they are not treated as sym consts...
                pos = cond.find('exists(')
                if pos >= 0:
                    evars = cond[pos+7:cond.find(':', pos+7)]
                    [exists.append(evar) for evar in evars.split(',')]
                items = re.findall(r'[A-Za-z_]+', cond)
                for item in items:
                    if item not in iters and item.lower() not in keywords:
                        if '%s(' % item in result and item not in ufuncs:
                            ufuncs[item] = {'name': item, 'args': [], 'arity': 1, 'order': len(ufuncs),
                                            'oldname': '', 'oldargs': [], 'oldarity': 0}
                        if item not in symcons and item not in ufuncs and item not in exists:
                            symcons[item] = len(symcons)
                if self.isknown(cond, iters, exists, keywords):
                    knowns.append(cond)

            # Separate set string for codegen argument from those for given clause.
            given = ''
            if len(knowns) > 0:
                for known in knowns:
                    conds.remove(known)
                result = result.replace(condstr, '&&'.join(conds))
                given = '{[%s]: %s}' % (','.join(iters), '&&'.join(knowns))
            symlist = '%s,' % ','.join(sorted(symcons.keys()))

            # U-funcs are tricky, need to consider the args...
            # 1st Pass: Collect all data on u-funcs.
            newfuncs = {}
            for ufname in ufuncs:
                ufunc = ufuncs[ufname]
                fpos = trim.find(ufname)
                while fpos >= 0:
                    fpos += len(ufname)
                    lpos = trim.find('(', fpos)
                    rpos = trim.find(')', lpos + 1)
                    args = trim[lpos + 1:rpos].split(',')
                    ufunc['arity'] = len(args)
                    for i in range(len(args)):
                        arg = args[i]
                        if len(ufunc['args']) <= i:         # New arg!
                            ufunc['args'].append(arg)
                        elif arg != ufunc['args'][i]:
                            newfunc = cp.deepcopy(ufunc)    # New ufunc!
                            newfunc['oldname'] = ufunc['name']
                            newfunc['name'] = '%s%d' % (ufunc['name'], i+1)
                            newfunc['oldargs'].append(arg)
                            newfuncs[newfunc['name']] = newfunc
                    fpos = trim.find(ufname, rpos + 1)

            # Add newbies...
            for ufname in newfuncs:
                ufuncs[ufname] = newfuncs[ufname]

            # 2nd Pass: To prevent prefix errors, need to ensure leading arg must include first iters...
            for ufunc in ufuncs.values():
                if ufunc['arity'] > 0:
                    ufunc['oldarity'] = ufunc['arity']
                    newargs = []
                    for arg in ufunc['args']:
                        if arg in iters:
                            newargs = iters[0:iters.index(arg)]
                    ufunc['arity'] += len(newargs)
                    if len(ufunc['oldargs']) < 1:
                        ufunc['oldargs'] = ufunc['args'].copy()
                    for it in newargs:
                        ufunc['args'].insert(len(ufunc['args']) - 1, it)
                symlist += '%s(%d),' % (ufunc['name'], ufunc['arity'])

            # 3rd Pass: Replace the occurrences of the UFs in the IEGL output...
            for ufunc in ufuncs.values():
                ufname = ufunc['name']
                oldcall = ''
                if len(ufunc['oldname']) > 0:
                    oldcall = '%s(%s)' % (ufunc['oldname'], ','.join(ufunc['oldargs']))
                elif ufunc['arity'] > ufunc['oldarity']:
                    oldcall = '%s(%s)' % (ufname, ','.join(ufunc['oldargs']))
                if len(oldcall) > 0:
                    newcall = '%s(%s)' % (ufname, ','.join(ufunc['args']))
                    result = result.replace(oldcall, newcall)
                    given = given.replace(oldcall, newcall)

            omcode = "symbolic %s;\n" % symlist[0:len(symlist) - 1]
            omcode += "%s := %s;\n" % (res_id, result)
            #omcode += "%s;\n" % res_id
            omcode += "codegen(%s)" % res_id
            if len(given) > 0:
                omcode += ' given %s' % given
            omcode += ';'

            self._omegacode[res_id] = omcode
            self._ufuncs = ufuncs

        return omcode

    def isknown(self, cond, iters, exists, keywords):
        # TODO: Simplify this logic!!!
        isknown = False
        for operand in re.split(r'\>|\<|\=', cond):
            isknown = operand not in iters and operand not in exists
            if not isknown:
                break
        if isknown:
            for keyword in keywords:
                isknown = keyword not in cond
                if not isknown:
                    break
        if isknown:
            for operand in re.split(r'\+|\-|\*|\/', cond):
                isknown = operand not in iters and operand not in exists
                if not isknown:
                    break
        return isknown
