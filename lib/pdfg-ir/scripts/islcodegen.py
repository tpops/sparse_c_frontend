#!/usr/bin/env python3

import os
import sys
import time
import argparse as ap
import traceback as tb

from codegen.setlib import *
from codegen import settings

from tools import files
from tools import system

def parseArgs():
    parser = ap.ArgumentParser('islcodegen', description='Automatically generate benchmark code given a configuration file.')
    parser.add_argument('-c', '--config', default='', help='Configuration file.')
    parser.add_argument('-n', '--name', default='', help='Output name.')
    parser.add_argument('-e', '--exec', default='', help='Executable to generate.')
    parser.add_argument('-i', '--iscc', default='', help='ISCC executable path.')
    parser.add_argument('-l', '--islin', default='', help='ISL input file (overrides template).')
    parser.add_argument('-I', '--includes', default='', help='Library paths (colon separated).')
    parser.add_argument('-L', '--libs', default='', help='Library paths (colon separated).')
    parser.add_argument('-k', '--links', default='', help='Libraries to link (colon separated).')
    parser.add_argument('-m', '--main', default='', help='Source file with main method.')
    parser.add_argument('-p', '--path', default='', help='Benchmark path.')
    parser.add_argument('-H', '--header', default='', help='Benchmark header file.')
    parser.add_argument('-b', '--build', default='', help='Extra build arguments.')
    parser.add_argument('-v', '--verify', default='', help='Verify (# cells).')

    return parser.parse_known_args()

def parseVars(dct, lst):
    nVars = len(lst)
    if nVars > 0:
        for i in range(0, nVars, 2):
            j = i + 1
            var = lst[i].lstrip('-')
            val = ''
            if j < nVars:
                val = lst[j]
            dct[var] = val

    return dct

def main():
    if len(sys.argv) < 2:
        sys.argv.append('-h')
    elif not sys.argv[1].startswith('-'):
        sys.argv.insert(1, '-c')
    elif not sys.argv[-1].startswith('-'):
        sys.argv.insert(len(sys.argv)-1, '-c')

    (args, unknowns) = parseArgs()

    if '.cfg' not in args.config:
        sys.stderr.write("ERROR: Invalid config file '%s', extension must be .cfg.\n" % args.config)
        os._exit(-1)

    # Record start time...
    startTime = time.time()

    benchmark = settings.config.copy()
    benchmark['template'] = args.config

    # If no path defined, assume current working directory...
    if len(args.path) > 0:
        benchmark['path'] = args.path
    if 'path' not in benchmark or len(benchmark['path']) < 1:
        benchmark['path'] = os.getcwd()

    # If no main file specified, assume there is a main.cpp.
    if len(args.main) > 0:
        benchmark['main'] = args.main
    if 'main' not in benchmark or len(benchmark['main']) < 1:
        benchmark['main'] = 'main.cpp'

    if len(args.name) > 0:
        benchmark['name'] = args.name
    if 'name' not in benchmark or len(benchmark['name']) < 1:
        benchmark['name'] = files.getNameWithoutExt(benchmark['template'])

    # Get ISCC from environment if not specified
    if len(args.iscc) > 0:
        benchmark['iscc'] = args.iscc
    if 'iscc' not in benchmark or len(benchmark['iscc']) < 1:
        (output, error) = system.run('which iscc')
        benchmark['iscc'] = output.rstrip()
    if not os.path.isfile(benchmark['iscc']):
        sys.stderr.write("ERROR: iscc executable not found in path.\n")
        os._exit(-1)

    # Set header file that is included by the Benchmark class file.
    if len(args.header) > 0:
        benchmark['header'] = args.header
    if 'header' not in benchmark or len(benchmark['header']) < 1:
        benchmark['header'] = '%s.h' % benchmark['name']

    # All unknown command line vars become variables for the build system...
    if 'vars' not in benchmark:
        benchmark['vars'] = {}
    if len(unknowns) > 0:
        benchmark['vars'] = parseVars(benchmark['vars'], unknowns)
    elif len(benchmark['vars']) > 0:
        print("Using default vars: '%s'..." % str(benchmark['vars']))

    # Check that ISCC input file has .in extension...
    benchmark['isl'] = args.islin
    if len(benchmark['isl']) > 0 and '.in' not in args.islin:
        sys.stderr.write("ERROR: Invalid ISL input file '%s', extension must be .in.\n" % args.islin)
        os._exit(-1)

    # Ensure tile size is power of two so tile masks work...
    if 'TILE_SIZE' in benchmark['vars']:
        ts = int(benchmark['vars']['TILE_SIZE'])
        if (ts & (ts - 1)) != 0:
            sys.stderr.write("ERROR: TILE_SIZE %d must be a power of two.\n" % ts)
            os._exit(-1)

    # Generate the benchmark file...
    print("Generating benchmark '%s'..." % benchmark['name'])
    gen = Generator(benchmark)
    gen.generate()
    benchmark = gen.benchmark()

    # Set executable...
    benchmark['exec'] = args.exec
    if len(benchmark['exec']) < 1:
        benchmark['exec'] = files.getNameWithoutExt(benchmark['output'])

    # Compile the source file...
    build = benchmark['build']
    os.chdir(benchmark['path']) # Change working directory before compiling to ensure relative paths are correct!

    if len(args.includes) > 0:
        paths = args.includes.split(':')
        for path in paths:
            build['CFLAGS'] += ' -I%s' % path

    if len(args.libs) > 0:
        paths = args.libs.split(':')
        for path in paths:
            build['CFLAGS'] += ' -L%s' % path

    if len(args.links) > 0:
        paths = args.links.split(':')
        for path in paths:
            build['COPTS'] += ' -l%s' % path

    print("Compiling source file '%s' => '%s'..." % (benchmark['main'], benchmark['exec']))
    compile = '%s %s %s %s %s -o %s' % (build['CXX'], build['CFLAGS'], build['COPTS'], build['CFILES'], \
                                        benchmark['main'], benchmark['exec'])
    if len(args.build) > 0:
        compile = '%s %s' % (compile, args.build)

    print(compile)
    (output, error) = system.run(compile)

    if len(error) > 0:
        print(error)
    elif len(output) > 0:
        print(output)
    else:
        print("Successfully built in %g sec." % (time.time() - startTime))

        if len(args.verify) > 0:
            runCmd = './%s -B 1 -C %d -v' % (benchmark['exec'], int(args.verify))
            (output, error) = system.run(runCmd)
            print('Verification: %s' % output.strip())

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt as e: # Ctrl-C
        print("Closing gracefully on keyboard interrupt...")
    except Exception as e:
        print('ERROR: ' + str(e))
        tb.print_exc()
