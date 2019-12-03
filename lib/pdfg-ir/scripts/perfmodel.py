#!/usr/bin/env python3

import sys
import traceback as tb
from argparse import ArgumentParser
from csv import DictWriter
from tools import json

def usage():
    print("perfmodel <flowgraph.json>")

def parse_dom(domain):
    iters = {}
    for clause in domain.split('^'):
        (lhs, oper, rhs) = clause.strip().split()
        iter = ''
        low = 0
        high = 0
        if lhs.isdigit() or (lhs[0] == '-' and lhs[1:].isdigit()):
            iter = rhs
            low = int(lhs)
        else:
            iter = lhs
            high = int(rhs)
        if iter not in iters:
            iters[iter] = {}
        iters[iter]['low'] = low
        iters[iter]['high'] = high

    size = ''
    if len(iters) > 0:
        for iter in sorted(iters.keys()):
            low = iters[iter]['low']
            high = iters[iter]['high']
            oper = '-'
            if low < 0:
                oper = '+'
                low = -low
            size += '(' + str(high) + oper + str(low) + '+1)*'
        size = size.rstrip('*')
    else:
        size = '1'
    return size

def main():
    if len(sys.argv) < 1:       # Read from standard in...
        usage()
        return

    js_file = sys.argv[-1]
    csv_file = open(js_file.replace('.json', '.csv'), 'w')
    writer = DictWriter(csv_file, ['Kernel', 'FLOPs', 'FLOPSize', 'ReadBytes', 'ReadSize',
                                   'WriteBytes', 'WriteSize', 'IOPs', 'StreamsIn', 'StreamsOut'])
    writer.writeheader()

    # (args, unknowns) = parse_args()
    graph = json.parseFile(js_file)
    for node in graph['nodes']:
        if 'attrs' in node:
            attrs = node['attrs']
            comp = node['space']

            # Get iteration space size to multiply by per iter FLOPs and IOPs.
            is_size = '1'
            pos = comp.find('{')
            if pos >= 0:
                is_size = parse_dom(comp[pos+1:comp.find('}', pos+1)].strip())

            fsize_out = '1'
            if 'fsize_out' in attrs:
                fsize_out = attrs['fsize_out']

            # If fsize_in missing, it is a pointwise operation, so set equal to out.
            fsize_in = fsize_out
            if 'fsize_in' in attrs:
                fsize_in = attrs['fsize_in']

            fstreams_out = ''
            if 'fstreams_out' in attrs:
                fstreams_out = attrs['fstreams_out']

            # If fsize_in missing, it is a pointwise operation, so set equal to out.
            fstreams_in = fstreams_out
            if 'fstreams_in' in attrs:
                fstreams_in = attrs['fstreams_in']

            flop_expr = '(' + is_size + ')*' + attrs['flops']

            data = {'Kernel': node['label'], 'FLOPs': eval(flop_expr), 'FLOPSize': flop_expr,
                    'ReadBytes': eval(fsize_in), 'ReadSize': fsize_in,
                    'WriteBytes': eval(fsize_out), 'WriteSize': fsize_out, 'IOPs': attrs['iops'],
                    'StreamsIn': fstreams_in, 'StreamsOut': fstreams_out}
            writer.writerow(data)

    csv_file.close()
    stop = 1

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt as e: # Ctrl-C
        print("Closing gracefully on keyboard interrupt...")
    except Exception as e:
        print('ERROR: ' + str(e))
        tb.print_exc()
