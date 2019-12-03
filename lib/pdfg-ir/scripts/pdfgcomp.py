#!/usr/bin/env python3

import traceback as tb
from argparse import ArgumentParser

from pdfg.pdfgs import *
from codegen.visit import *

def parse_args():
    parser = ArgumentParser('pdfgcomp', description='Command line compiler for the Graph Specification Language (GSL).')
    parser.add_argument('-i', '--input', default='', help='Input file.')
    parser.add_argument('-c', '--cfile', default='', help='Output C file name.')
    parser.add_argument('-o', '--output', default='', help='Output executable.')
    parser.add_argument('-d', '--dot', default='', help='Graphviz DOT file.')
    parser.add_argument('-I', '--includes', default='', help='Library paths (colon separated).')
    parser.add_argument('-L', '--libs', default='', help='Library paths (colon separated).')
    parser.add_argument('-p', '--path', default='', help='Benchmark path.')
    parser.add_argument('-H', '--header', default='', help='Benchmark header file.')
    parser.add_argument('-b', '--build', default='', help='Extra build arguments.')
    parser.add_argument('-v', '--verify', default='', help='Verify (# cells).')
    return parser.parse_known_args()

def main():
    if len(sys.argv) < 1:       # Read from standard in...
        gslfile = ''
        infile = sys.stdin
    else:
        gslfile = sys.argv[-1]
        infile = open(gslfile)

    (args, unknowns) = parse_args()

    spec = "\n".join(infile.readlines())
    parser = PDFGParser()
    dfg = parser.parse(spec)

    if len(args.dot) > 0:
        dot = open(args.dot, 'w')
        dot.write(dfg.graphgen())

    if len(args.cfile) > 0:
        outfile = open(args.cfile, 'w')
    else:
        outfile = sys.stdout
    outfile.write(dfg.codegen())

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt as e: # Ctrl-C
        print("Closing gracefully on keyboard interrupt...")
    except Exception as e:
        print('ERROR: ' + str(e))
        tb.print_exc()
