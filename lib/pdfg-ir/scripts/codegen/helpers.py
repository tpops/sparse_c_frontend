import re

class LatexHelper(object):
    @staticmethod
    def format(formula):
        formula = formula.replace("{", "\\{")
        formula = formula.replace("}", "\\}")

        # Split on underscores...
        if formula == 'R' or formula == 'Z' or formula == 'C':
            out = "\\mathbb{%s}" % formula
        elif '_' in formula:
            items = formula.split('_')
            out = items[0]
            for i in range(1, len(items)):
                out += '_{%s}' % items[i]
        else:
            out = formula

        # Replace <= with \leq...
        replacements = {
            "<=": "\\leq", ">=": "\\geq", "*": " \\times ",
            "->": " \\rightarrow ", "<-": " \\leftarrow ",
            "&&": "\\wedge", "||": "\\vee"
        }

        for key in replacements:
            out = out.replace(key, replacements[key])

        return out

class DotHelper(object):
    @staticmethod
    def formatLabel(label):
        if '^' in label or '_' in label:
            pos = label.find('^')
            while pos > 0:
                exp = label[pos+1]
                label = label.replace('^' + exp, '<sup>' + exp + '</sup>')
                pos = label.find('^')

            pos = label.find('_')
            while pos > 0:
                lhs = label[0:pos]
                rhs = label[pos + 1:]
                label = lhs + '<sub>' + rhs + '</sub>'
                pos = label.find('_')

            label = '<%s>' % label

        return label

    @staticmethod
    def parseAttrs(attrs):
        dotattrs = {'style': 'filled,solid', 'color': 'black'}
        for key in attrs:
            if key is not 'row' and key is not 'col' and key is not 'comp':
                prefix = ''
                if key == 'color':
                    prefix = 'fill'
                dotattrs[prefix + key] = attrs[key]

        return dotattrs

class VarHelper(object):
    @staticmethod
    def replaceChars(formula):
        return formula.replace(' ', '').replace('(', '_').replace(')', '_').replace('+', 'p').replace('-', 'm').replace('*', 't').replace('/', 'd')

    @staticmethod
    def restoreChars(formula):
        return formula.replace('_', '(').replace('(', '[').replace(')', ']').replace('p', '+').replace('m', '-').replace('t', '*').replace('d', '/')

    @staticmethod
    def replaceIterators(formula, newiters=()):
        olditers = formula[formula.find('->') + 3:].split('[')[1].split(']')[0].split(', ')
        for i in range(len(olditers)):
            if olditers[i][0] == 'i':
                formula = re.sub(olditers[i], newiters[i], formula)
                olditers[i] = newiters[i]
        return formula

    @staticmethod
    def listVars(sets):
        varlist = []
        nsets = len(sets)
        expr = re.compile(r'^[0-9]+$')

        for i in range(nsets):
            vars = sets[i].vars
            nvars = len(vars)
            for j in range(nvars):
                bounds = [vars[j].lower, vars[j].upper]
                for bound in bounds:
                    if len(bound) > 0 and not expr.match(bound):
                        bound = VarHelper.replaceChars(bound)
                        if bound not in varlist:
                            varlist.append(bound)

        return '[%s]' % ','.join(varlist)
