#
# General Settings
#

# Colors:
RED = 'rgb(213, 72, 87)'
BLUE = 'rgb(64, 111, 223)'
GREEN = 'rgb(57, 177, 67)'
ORANGE = 'rgb(207, 121, 38)'
VIOLET = 'rgb(209, 66, 244)'
TEAL = 'rgb(33,190,148)'

config = {
    #'header': 'miniFluxDiv-gen.h',
    'header': 'MiniFluxBenchmark.h',
    'skipguard': True,
    'vars': {'TILE_SIZE': 8},
    'build': {
        'CC': 'gcc',
        'CXX': 'g++',
        'CFLAGS': '-std=c++11 -g -I../common -I../common/Benchmark -I../common/ISLInt -I/usr/include -I/usr/local/include',
        'COPTS': '-fopenmp -O3 -lpthread', # -DTILE_SIZE=16',
        'CFILES': '../common/Measurements.cpp ../common/Configuration.cpp ../common/Benchmark/Benchmark.cpp MiniFluxBenchmark.cpp'
    },
    'iscc': '/usr/local/bin/iscc',
    'omega': '/usr/local/bin/oc'
}

#
# Jacobi1D Benchmark
#

benchmarks = {
    'Jacobi1D': {
        'header':
'''// Jacobi1D-gen.h
#include \"util.h\"

#define N Nx
#define Ts 8
#define S(t,i) stencil(data,t,i)
#define S0(i) S(t,i)
#define S1(i) S(t+1,i)

inline void jacobi1D(real* data, int T, int Nx) {''',
        'body': '',
        'footer': '}	// Jacobi1D',
        'path': '',
        'source': 'Jacobi1D-NaiveParallel-OMP.cpp',
        'vars': {}
    },

#
# MiniFluxDiv Benchmark
#

'MiniFluxDiv': {
    'template': 'miniFluxDiv-template.h',
        'header':
'''// miniFluxDiv_kernel.h
#include \"ISLFunctions.h\"
''',
    'body':
'''inline void miniFluxdiv_kernel(Real *old_box, Real *new_box, int numCell,\
int full_numCell, int full_numCell2, int full_numCell3, int nGhost,\
Real **gx_caches, Real **gy_caches, Real **gz_caches, bool debug) { //, Real **gx2_caches, Real **gy2_caches, Real **gz2_caches) {''',
        'footer': '}	// miniFluxdiv_kernel',
        'path': '',
        'source': 'miniFluxDiv-gen.cpp',
        'isl': 'miniFluxDiv-gen.in',
        'skipguard': True,
        'omp': {
            'code': '''     int tid = omp_get_thread_num();
     Real *gx_cache = gx_caches[tid];
     Real *gy_cache = gy_caches[tid];
     Real *gz_cache = gz_caches[tid];

     //Real *gx2_cache = gx2_caches[tid];
     //Real *gy2_cache = gy2_caches[tid];
     //Real *gz2_cache = gz2_caches[tid];
    },
}

''',
        'pragma': '#pragma omp parallel for default(shared)',
        'level': 0
    },
    'vars': {
        'TILE_SIZE': 2
    },

    'build': {
        'CC': 'gcc',
        'CXX': 'g++',
        'CFLAGS': '-std=c++11 -g -I../common -I../ISLInt -I/usr/include -I/usr/local/include',
        'COPTS': '-fopenmp -O3', # -DTILE_SIZE=16',
        'CFILES': '../common/Measurements.cpp ../common/Configuration.cpp Benchmark.cpp MiniFluxBenchmark.cpp'
    }
},

    'miniFluxDiv-overlap-tiling': {
        'name': 'miniFluxDiv-overlap-tiling',
        'template': 'miniFluxDiv-overlap-tiling-template.h',
    },

    'miniFluxDiv': {
        'symbol': 'numCell',
        'vars': ['c', 'z', 'y', 'x'],
        'domains': [
            {
                'label': 'Fx1',
                'name': 'FLUX1X',
                'bounds': [
                    ['c', '0', '4'],
                    ['z', '0', 'numCell-1'],
                    ['y', '0', 'numCell-1'],
                    ['x', '0', 'numCell'],
                    ['numCell', '2', '']
                ]
            },
            {
                'label': 'Fx2',
                'name': 'FLUX2X',
                'bounds': [
                    ['c', '0', '4'],
                    ['z', '0', 'numCell-1'],
                    ['y', '0', 'numCell-1'],
                    ['x', '0', 'numCell'],
                    ['numCell', '2', '']
                ]
            },
            {
                'label': 'Dx',
                'name': 'DIFFX',
                'bounds': [
                    ['c', '0', '4'],
                    ['z', '0', 'numCell-1'],
                    ['y', '0', 'numCell-1'],
                    ['x', '0', 'numCell-1'],
                    ['numCell', '2', '']
                ]
            },
            {
                'label': 'Fy1',
                'name': 'FLUX1Y',
                'bounds': [
                    ['c', '0', '4'],
                    ['z', '0', 'numCell-1'],
                    ['y', '0', 'numCell'],
                    ['x', '0', 'numCell-1'],
                    ['numCell', '2', '']
                ]
            },
            {
                'label': 'Fy2',
                'name': 'FLUX2Y',
                'bounds': [
                    ['c', '0', '4'],
                    ['z', '0', 'numCell-1'],
                    ['y', '0', 'numCell'],
                    ['x', '0', 'numCell-1'],
                    ['numCell', '2', '']
                ]
            },
            {
                'label': 'Dy',
                'name': 'DIFFY',
                'bounds': [
                    ['c', '0', '4'],
                    ['z', '0', 'numCell-1'],
                    ['y', '0', 'numCell-1'],
                    ['x', '0', 'numCell-1'],
                    ['numCell', '2', '']
                ]
            },
            {
                'label': 'Fz1',
                'name': 'FLUX1Z',
                'bounds': [
                    ['c', '0', '4'],
                    ['z', '0', 'numCell'],
                    ['y', '0', 'numCell-1'],
                    ['x', '0', 'numCell-1'],
                    ['numCell', '2', '']
                ]
            },
            {
                'label': 'Fz2',
                'name': 'FLUX2Z',
                'bounds': [
                    ['c', '0', '4'],
                    ['z', '0', 'numCell'],
                    ['y', '0', 'numCell-1'],
                    ['x', '0', 'numCell-1'],
                    ['numCell', '2', '']
                ]
            },
            {
                'label': 'Dz',
                'name': 'DIFFZ',
                'bounds': [
                    ['c', '0', '4'],
                    ['z', '0', 'numCell-1'],
                    ['y', '0', 'numCell-1'],
                    ['x', '0', 'numCell-1'],
                    ['numCell', '2', '']
                ]
            }
        ]
    }
}

# Fig 6
charts = {
    'mfd-fusion': {
        'data': '/home/edavis/Work/VarDevEddie/scripts/data/miniFluxDiv-latest.csv',
        # 6a
        #'order': [4, 3, 6, 5, 1, 0, 2],
        #'legends': ['Series-SSA-CLO', 'Series-Reduce-CLO', 'Fuse-Among-Dirs-SSA', 'Fuse-All-SSA-CLO',
        #           'Fuse-All-Redux-CLO', 'Fuse-Within-Dirs-SSA-CLO', 'Fuse-Within-Dirs-Redux-CLO'], #, 'FuseAll-CLO-Redux-Overlap-TS8-PB'],
        #'figures': ['Series of Loops (SA)', 'Series of Loops (Reduced)', 'Fuse Among Directions',
        #           'Fuse All Levels (SA)', 'Fuse All Levels (Reduced)', 'Fuse Within Directions (SA)',
        #           'Fuse Within Directions (Reduced)'], #, '  Overlapped Tiling'],
        #'colors': [RED, RED, GREEN, BLUE, BLUE, ORANGE, ORANGE], #, VIOLET],
        #'symbols': ['circle', 'diamond', 'square', 'circle', 'diamond', 'circle', 'diamond', 'square'], #, 'cross'],
        #'dashes': ['', 'dash', '', '', 'dash', '', 'dash', ''], #, ''],
        #'legendpos': (0.6, 1.1),
        # 6b
        # 'order': [2, 0, 1, 5, 3, 4, 6, 7],
        # 'legends': ['Series-SSA-CLO', 'Series-Reduce-CLO', 'Fuse-Among-Dirs-SSA', 'Fuse-All-SSA-CLO',
        #            'Fuse-All-Redux-CLO', 'Fuse-Within-Dirs-SSA-CLO', 'Fuse-Within-Dirs-Redux-CLO',
        #            'FuseAll-CLO-Redux-Overlap-TS8-PB'],
        # 'figures': ['Series of Loops (SA)', 'Series of Loops (Reduced)', 'Fuse Among Directions',
        #            'Fuse All Levels (SA)', 'Fuse All Levels (Reduced)', 'Fuse Within Directions (SA)',
        #            'Fuse Within Directions (Reduced)', 'Overlapped Tiling'],
        # 'colors': [RED, RED, GREEN, BLUE, BLUE, ORANGE, ORANGE, VIOLET],
        # 'symbols': ['circle', 'diamond', 'square', 'circle', 'diamond', 'circle', 'diamond', 'square', 'cross'],
        # 'dashes': ['', 'dash', '', '', 'dash', '', 'dash', 'dashdot'], #, ''],
        # 'legendpos': (0.6, 1.2),
        # Reduced Variants
        'order': [2, 3, 4, 0, 1],
        'legends': ['Series-Reduce-CLO', 'Fuse-Among-Dirs-SSA', 'Fuse-All-Redux-CLO',
                    'Fuse-Within-Dirs-Redux-CLO', 'FuseAll-CLO-Redux-Overlap-TS8-PB'],
        'figures': ['Series of Loops', 'Fuse Among Directions',
                   'Fuse All Levels', 'Fuse Within Directions', 'Overlapped Tiling'],
        'colors': [RED, GREEN, BLUE, ORANGE, VIOLET],
        'symbols': ['diamond', 'square', 'cross', 'circle', 'square'],
        'dashes': ['dash', '', 'dash', '', 'dashdot'], #, ''],
        'legendpos': (0.6, 1.0),
        # Pres...
        # 'order': [0, 1, 2],
        # 'legends': ['Series-Reduce-CLO', 'FuseAll-CLO-Redux-Overlap-TS8-PB', 'Ideal-Scaling'],
        # 'figures': ['Series of Loops (Reduced)', 'Overlapped Tiling', 'Ideal Scaling'],
        # 'colors': [RED, VIOLET, 'black'],
        # 'symbols': ['circle', 'cross', 'diamond'],
        # 'dashes': ['', '', ''],
        # 'legendpos': (0.6, 1.0),
        # Others...
        'xcol': 'nThreads',
        'ycol': 'MinTime',  #'MeanTime'
        'markerSize': 24,
        'lineSize': 6,
        'fontName': 'Arial',
        'fontSize': 30,
        'fontColor': 'black'
    },
    # 'mfd-redux': {
    #     'data': '/home/edavis/Work/VarDevEddie/scripts/data/miniFluxDiv-diff.csv',
    #     # Reduced Variants
    #     'order': [0,1,2],
    #     'legends': ['Series-Diff-CLO', 'Fuse-Within-Dirs-Diff-CLO', 'Fuse-All-Diff-CLO'],
    #     'figures': ['Series of Loops', 'Fuse Within Directions', 'Fuse All Levels'],
    #     'colors': [RED, ORANGE, BLUE],
    #     'symbols': ['diamond', 'circle', 'cross'],
    #     'dashes': ['', '', ''],
    #     'legendpos': (0.6, 1.0),
    #     'xcol': 'nThreads',
    #     'ycol': 'MedianTime',  #'MeanTime'
    #     'markerSize': 24,
    #     'lineSize': 6,
    #     'fontName': 'Arial',
    #     'fontSize': 30,
    #     'fontColor': 'black'
    # },
    'mfd-overlap': {
        'data': '/home/edavis/Work/VarDevEddie/scripts/data/miniFluxDiv-filter.csv',
        # Reduced Variants
        'order': [0,1,2],
        'legends': ['Series-Reduce-CLO', 'Series-CLO-Redux-Overlap-TS8-PB', 'FuseAll-CLO-Redux-Overlap-TS8-PB'],
        'figures': ['Series of Loops', 'Vectorized Overlapped Tiling', 'Shift-Fused Overlapped Tiling'],
        'colors': [RED, TEAL, VIOLET],
        'symbols': ['diamond', 'circle', 'square'],
        'dashes': ['', '', ''],
        'legendpos': (0.57, 1.0),
        'xcol': 'nThreads',
        'ycol': 'MinTime',  #'MeanTime'
        'markerSize': 24,
        'lineSize': 6,
        'fontName': 'Arial',
        'fontSize': 30,
        'fontColor': 'black'
    },
    # Fig 12
    'mfd-halide': {
        'data': '/home/edavis/Work/VarDevEddie/scripts/data/miniFluxDiv-latest.csv',
        #12a
        #'order': [2, 3, 0, 1],
        #'legends': ['Series-Reduce-CLO', 'Fuse-Among-Dirs-SSA', 'Halide2', 'PolyMage'],
        #'figures': ['Series of Loops', 'Fuse Among Directions', 'Halide Auto-Schedule', 'PolyMage Auto-Tuned'],
        #'colors': [RED, GREEN, TEAL, VIOLET],
        #'symbols': ['circle', 'square', 'diamond', 'cross'],
        #'dashes': ['', 'dash', 'dash', 'dashdot'],
        #'legendpos': (0.68, 0.8),
        # 12b
        'order': [4, 0, 3, 2, 1],
        'legends': ['Series-Reduce-CLO', 'FuseAll-CLO-Redux-Overlap-TS8-PB', 'FuseAll-CLO-Redux-Overlap-TS8-PT', 'Halide-NoOMP', 'PolyMage'],
        'figures': ['Series of Loops', 'Overlapped Tiling (Parallel over Boxes)', 'Overlapped Tiling (Parallel within Boxes)', 'Halide Auto-Schedule', 'PolyMage Auto-Tuned'],
        'colors': [RED, BLUE, ORANGE, TEAL, VIOLET],
        'symbols': ['circle', 'square', 'diamond', 'cross', 'diamond'],
        'dashes': ['', '', 'dash', 'dash', 'dashdot'],
        'legendpos': (0.5, 1.05),
        # Others...
        'xcol': 'nThreads',
        'ycol': 'MinTime', #'MeanTime',
        'markerSize': 24,
        'lineSize': 6,
        'fontName': 'Arial',
        'fontSize': 32,
        'fontColor': 'black'
    },

    'mfd-polymage': {
        'data': '/home/edavis/Work/VarDevEddie/scripts/data/miniFluxDiv-latest.csv',
        #'legends': ['Series-SSA-CLO', 'FuseAll-CLO-Redux-Overlap-TS8-PT', 'Halide-NoOMP', 'PolyMage'],
        'legends': ['FuseAll-CLO-Redux-Overlap-TS8-PT', 'Halide-NoOMP', 'PolyMage'],
        #'figures': ['1) Series of Loops', '2) Fuse All Rows', '3) Halide Auto-Schedule', '4) PolyMage Auto-Tuned'],
        'figures': ['1) Fuse All Rows', '2) Halide Auto-Schedule', '3) PolyMage Auto-Tuned'],
        'colors': [RED, BLUE, GREEN],
        'symbols': ['circle', 'diamond', 'square'],
        'dashes': ['', '', ''],
        'xcol': 'nThreads',
        'ycol': 'MeanTime',
        'legendpos': (0.65, 1.0),
        'markerSize': 8,
        'lineSize': 4,
        'fontName': 'Arial',
        'fontSize': 32,
        'fontColor': 'black'
    },

    'mfd-overlap-old': {
        'data': '/home/edavis/Work/VarDevEddie/scripts/data/miniFluxDiv-fuseAllCLOReduxOver.csv',
        'legends': [#'Fuse-All-CLO-Redux-Overlap', 'Fuse-All-CLO-Redux-Overlap16', 'Fuse-All-CLO-Redux-Overlap32',
                    'Fuse-All-CLO-Redux-Overlap8PT', 'Fuse-All-CLO-Redux-Overlap16PT', 'Fuse-All-CLO-Redux-Overlap32PT'],
                    #'Fuse-All-CLO-Redux-Overlap8Nest', 'Fuse-All-CLO-Redux-Overlap16Nest', 'Fuse-All-CLO-Redux-Overlap32Nest'],
        'figures': [#'1a) OT Per Box (Size=8)', '1b) OT Per Box (Size=16)', ' 1c) OT Per Box (Size=32)',
                    ' a) OT Per Tile (Size=8)', ' b) OT Per Tile (Size=16)', ' c) OT Per Tile (Size=32)'],
                    #'3a) OT Nested (Size=8)', '3b) OT Nested (Size=16)', ' 3c) OT Nested (Size=32)'],
        'colors': [#RED, GREEN, RED,
                   RED, GREEN, BLUE,],
                   #BLUE, BLUE, BLUE],
                   #ORANGE],
        'symbols': [#'circle', 'diamond', 'square',
                    'circle', 'diamond', 'square',],
                    #'circle', 'diamond', 'square'],
        'dashes': [#'', 'dash', 'dot',
                   '', 'dash', 'dot',],
                    #'', 'dash', 'dot',],
        'xcol': 'nThreads',
        'ycol': 'MinTime',
        'legendpos': (0.8, 1.0)
    }
}

graphs = {
    'seriesSSACLO': {
        'comps': ['p', 'e', 'u', 'v', 'w'],
        'nodes': [
            [('D','N^3'), ('D','N^3'), ('D','N^3'), ('D','N^3'), ('D','N^3')],                                  #  0
            [('S','Fx1'), ('S','Fx1'), ('S','Fx1'), ('S','Fx1'), ('S','Fx1')],                                  #  1
            [('T','N^3+N^2'), ('T','N^3+N^2'), ('T','N^3+N^2'), ('T','N^3+N^2'), ('T','N^3+N^2')],    #  2
            [('S','Fx2'), ('S','Fx2'), ('S','Fx2'), ('S','Fx2'), ('S','Fx2')],                                  #  3
            [('T','N^3+N^2'), ('T','N^3+N^2'), ('T','N^3+N^2'), ('T','N^3+N^2'), ('T','N^3+N^2')],    #  4
            [('S','Dx'), ('S','Dx'), ('S','Dx'), ('S','Dx'), ('S','Dx')],                                       #  5
            [('S','Fy1'), ('S','Fy1'), ('S','Fy1'), ('S','Fy1'), ('S','Fy1')],                                  #  6
            [('T','N^3+N^2'), ('T','N^3+N^2'), ('T','N^3+N^2'), ('T','N^3+N^2'), ('T','N^3+N^2')],    #  7
            [('S','Fy2'), ('S','Fy2'), ('S','Fy2'), ('S','Fy2'), ('S','Fy2')],                                  #  8
            [('T','N^3+N^2'), ('T','N^3+N^2'), ('T','N^3+N^2'), ('T','N^3+N^2'), ('T','N^3+N^2')],    #  9
            [('S','Dy'), ('S','Dy'), ('S','Dy'), ('S','Dy'), ('S','Dy')],                                       # 10
            [('S','Fz1'), ('S','Fz1'), ('S','Fz1'), ('S','Fz1'), ('S','Fz1')],                                  # 11
            [('T','N^3+N^2'), ('T','N^3+N^2'), ('T','N^3+N^2'), ('T','N^3+N^2'), ('T','N^3+N^2')],    # 12
            [('S','Fz2'), ('S','Fz2'), ('S','Fz2'), ('S','Fz2'), ('S','Fz2')],                                  # 13
            [('T','N^3+N^2'), ('T','N^3+N^2'), ('T','N^3+N^2'), ('T','N^3+N^2'), ('T','N^3+N^2')],    # 14
            [('S','Dz'), ('S','Dz'), ('S','Dz'), ('S','Dz'), ('S','Dy')],                                       # 15
            [('D','N^3'), ('D','N^3'), ('D','N^3'), ('D','N^3'), ('D','N^3')]                                   # 16
        ],

        'edges': [
            # old_box => Fx1
            ((0,0), (1,0)), ((0,1), (1,1)), ((0,2), (1,2)), ((0,3), (1,3)), ((0,4), (1,4)),
            # Fx1 => N^3+N^2
            ((1,0), (2,0)), ((1,1), (2,1)), ((1,2), (2,2)), ((1,3), (2,3)), ((1,4), (2,4)),
            # N^3+N^2 => Fx2
            ((2,0), (3,0)), ((2,1), (3,1)), ((2,2), (3,2)), ((2,3), (3,3)), ((2,4), (3,4)),
            # Fx1(u)[N^3+N^2] => Fx2
            ((2,2), (3,0)), ((2,2), (3,1)), ((2,2), (3,3)), ((2,2), (3,4)),
            # Fx2 => N^3+N^2
            ((3,0), (4,0)), ((3,1), (4,1)), ((3,2), (4,2)), ((3,3), (4,3)), ((3,4), (4,4)),
            # N^3+N^2=> Dx
            ((4,0), (5,0)), ((4,1), (5,1)), ((4,2), (5,2)), ((4,3), (5,3)), ((4,4), (5,4)),
            # Dx => new_box
            #('Dx(p)', 'p1'), ('Dx(e)', 'e1'), ('Dx(u)', 'u1'), ('Dx(v)', 'v1'), ('Dx(w)', 'w1'),
            ((5,0), (16,0)), ((5,1), (16,1)), ((5,2), (16,2)), ((5,3), (16,3)), ((5,4), (16,4)),

            # old_box => Fy1
            #('p0', 'Fy1(p)'), ('e0', 'Fy1(e)'), ('u0', 'Fy1(u)'), ('v0', 'Fy1(v)'), ('w0', 'Fy1(w)'),
            ((0,0), (6,0)), ((0,1), (6,1)), ((0,2), (6,2)), ((0,3), (6,3)), ((0,4), (6,4)),
            # Fy1 => N^3+N^2
            ((6,0), (7,0)), ((6,1), (7,1)), ((6,2), (7,2)), ((6,3), (7,3)), ((6,4), (7,4)),
            # N^3+N^2 => Fy2
            #('Fy1(p)', 'Fy2(p)'), ('Fy1(e)', 'Fy2(e)'), ('Fy1(u)', 'Fy2(u)'), ('Fy1(v)', 'Fy2(v)'), ('Fy1(w)', 'Fy2(w)'),
            ((7,0), (8,0)), ((7,1), (8,1)), ((7,2), (8,2)), ((7,3), (8,3)), ((7,4), (8,4)),
            # Fy2 => N^3+N^2
            ((8,0), (9,0)), ((8,1), (9,1)), ((8,2), (9,2)), ((8,3), (9,3)), ((8,4), (9,4)),
            # Fy1(v)[N^3+N^2] => Fy2
            #('Fy1(v)', 'Fy2(p)'), ('Fy1(v)', 'Fy2(e)'), ('Fy1(v)', 'Fy2(u)'), ('Fy1(v)', 'Fy2(w)'),
            ((8,3), (9,0)), ((8,3), (9,1)), ((8,3), (9,2)), ((8,3), (9,4)),
            # N^3+N^2 => Dy
            #('Fy2(p)', 'Dy(p)'), ('Fy2(e)', 'Dy(e)'), ('Fy2(u)', 'Dy(u)'), ('Fy2(v)', 'Dy(v)'), ('Fy2(w)', 'Dy(w)'),
            ((9,0), (10,0)), ((9,1), (10,1)), ((9,2), (10,2)), ((9,3), (10,3)), ((9,4), (10,4)),
            # Dy => new_box
            #('Dy(p)', 'p1'), ('Dy(e)', 'e1'), ('Dy(u)', 'u1'), ('Dy(v)', 'v1'), ('Dy(w)', 'w1'),
            ((10,0), (16,0)), ((10,1), (16,1)), ((10,2), (16,2)), ((10,3), (16,3)), ((10,4), (16,4)),

            # old_box => Fz1
            #('p0', 'Fz1(p)'), ('e0', 'Fz1(e)'), ('u0', 'Fz1(u)'), ('v0', 'Fz1(v)'), ('w0', 'Fz1(w)'),
            ((0,0), (11,0)), ((0,1), (11,1)), ((0,2), (11,2)), ((0,3), (11,3)), ((0,4), (11,4)),
            # Fz1 => N^3+N^2
            ((11,0), (12,0)), ((11,1), (12,1)), ((11,2), (12,2)), ((11,3), (12,3)), ((11,4), (12,4)),
            # N^3+N^2 => Fz2
            #('Fz1(p)', 'Fz2(p)'), ('Fz1(e)', 'Fz2(e)'), ('Fz1(u)', 'Fz2(u)'), ('Fz1(v)', 'Fz2(v)'), ('Fz1(w)', 'Fz2(w)'),
            ((12,0), (13,0)), ((12,1), (13,1)), ((12,2), (13,2)), ((12,3), (13,3)), ((12,4), (13,4)),
            # Fz1(w)[N^3+N^2] => Fz2
            #('Fz1(w)', 'Fz2(p)'), ('Fz1(w)', 'Fz2(e)'), ('Fz1(w)', 'Fz2(u)'), ('Fz1(w)', 'Fz2(v)'),
            ((12,4), (13,0)), ((12,4), (13,1)), ((12,4), (13,2)), ((12,4), (13,3)),
            # Fz2 => N^3+N^2
            ((13,0), (14,0)), ((13,1), (14,1)), ((13,2), (14,2)), ((13,3), (14,3)), ((13,4), (14,4)),
            # N^3+N^2 => Dz
            #('Fz2(p)', 'Dz(p)'), ('Fz2(e)', 'Dz(e)'), ('Fz2(u)', 'Dz(u)'), ('Fz2(v)', 'Dz(v)'), ('Fz2(w)', 'Dz(w)'),
            ((14,0), (15,0)), ((14,1), (15,1)), ((14,2), (15,2)), ((14,3), (15,3)), ((14,4), (15,4)),
            # Dz => new_box
            #('Dz(p)', 'p1'), ('Dz(e)', 'e1'), ('Dz(u)', 'u1'), ('Dz(v)', 'v1'), ('Dz(w)', 'w1')
            ((15,0), (16,0)), ((15,1), (16,1)), ((15,2), (16,2)), ((15,3), (16,3)), ((15,4), (16,4)),
        ]
    }
}
