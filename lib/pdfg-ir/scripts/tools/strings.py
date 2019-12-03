__author__ = 'edavis'

import io
import re

def isMatch(inStr, pattern):
    return re.search(pattern, inStr, re.I)

def grep(pattern, list, regex=False):
    matches = None

    # Check for negation...
    negate = False
    if pattern[0] == '!':
        pattern = pattern[1:]
        negate = True

    if regex:
        expr = re.compile(pattern, re.IGNORECASE)
        if negate:
            matches = [elem for elem in list if not expr.match(elem)]
        else:
            matches = [elem for elem in list if expr.match(elem)]
    else:
        if negate:
            matches = [elem for elem in list if pattern not in elem]
        else:
            matches = [elem for elem in list if pattern in elem]

    return matches


def fastJoin(list, delim=''):
    output = io.StringIO()

    size = len(list)
    if size > 0:
        i = 0
        output.write(str(list[i]))

        while i < size:
            output.write(delim)
            output.write(str(list[i]))
            i += 1

    contents = output.getvalue()
    output.close()

    return contents


def capFirst(str):
    return ("%s%s") % (str[0:1].upper(), str[1:])
