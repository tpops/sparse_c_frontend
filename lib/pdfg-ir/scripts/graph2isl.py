#!/usr/bin/env python3

import traceback as tb

from pdfg.pdfgs import *
from codegen.visit import *
from codegen import settings

def gen_jacobi():
    # Instantiate graph
    g = Jacobi1D()
    g.write()       # Write to DOT
    # g.to_pdf()    # Write to PDF
    g.to_file()     # Write to JSON

    v = FlowGraphVisitor(g)
    print(v.latex())       # Convert to LaTeX
    v.omega()       # Generate Omega code
    v.code()     # Generate C code w/ CodeGenVisitor
    return g

def gen_mfd():
    g = MiniFluxDix()
    g.write()    # Write to DOT
    g.to_file()  # Write to JSON
    g.to_pdf()   # Write to PDF
    v = FlowGraphVisitor(g)
    v.code()  # Generate C code w/ CodeGenVisitor
    return g

def gen_csr_spmv():
    # Instantiate graph
    g = CSRSpMV()
    g.write()           # Write to DOT
    g.to_file()         # Write to JSON
    v = FlowGraphVisitor(g)
    v.code()  # Generate C code w/ CodeGenVisitor
    return g

def gen_bsr_spmv():
    # Instantiate graph
    g = BSRSpMV()
    g.write()               # Write to DOT
    g.to_file()             # Write to JSON
    v = FlowGraphVisitor(g)
    v.code()                # Generate C code w/ CodeGenVisitor
    return g

def gen_csrtobsr(nblocks=8):
    iegen = CSRToBSRGen(bsize=nblocks)
    (bsetup, binsp, bexec) = iegen.generate()
    IEGenGraphVisitor(iegen).code()
    binsp.write()
    iegen.write()
    return iegen

def gsl_test():
    spec = """
# MFD-2D Graph Spec
name("mfd-2d");
# X-Direction
fx1 := {[c,y,x]: 0 <= c < 4 && 0 <= x <= N && 0 <= y < N};
fx2 := {[c,y,x]};
dx := {[c,y,x]: 0 <= x < N};

# Y-Direction
fy1 := {[c,y,x]: 0 <= c < 4 && 0 <= x < N && 0 <= y <= N};
fy2 := {[c,y,x]};
dy := {[c,y,x]: 0 <= y < N};

# Statements
statement(fx1) := "Cx1[c,y,x] = (1./12.)*(Bin[c,y,x-2] + 7.0 * Bin[c,y,x-1] + Bin[c,y,x] + Bin[c,y,x+1])";
statement(fx2) := "Cx2[c,y,x] = Cx1[c,y,x] * 2.0 * Cx1[2,y,x]";
statement(dx) := "Bout[c,y,x] += Cx2[c,y,x+1] - Cx2[c,y,x]";
statement(fy1) := "Cy1[c,y,x] = (1./12.)*(Bin[c,y-2,x] + 7.0 * Bin[c,y-1,x] + Bin[c,y,x] + Bin[c,y+1,x])";
statement(fy2) := "Cy2[c,y,x] = Cy1[c,y,x] * 2.0 * Cy1[3,y,x]";
statement(dy) := "Bout[c,y,x] += Cy2[c,y+1,x] - Cy2[c,y,x]";
    """
    g = PDFGParser().parse(spec)
    print(g.graphgen())
    print(g.codegen())

    spec = """
# Jacobi1D Graph Spec
name("jacobi1d");
A:={[t,i]:0 <= t <= T && 0 <= i <= N+1};
A':={[i]:0 <= i <= N+1};
jacobi:={[t,i]:1 <= t <= T && 1 <= i <= N};
statement(jacobi):=A'[t,i]=A[t-1,i-1]+A[t-1,i]+A[t-1,i+1]/3.0;
    """
    g = PDFGParser().parse(spec)
    print(g.graphgen())
    print(g.codegen())

    spec = """
# CSR-SpMV Graph Spec
name('csr_spmv');
A := {[j] : 0 <= j < NNZ};
col := {[j] : 0 <= j < NNZ};
index := {[i] : 0 <= i <= N_R};
x := {[k] : 0 <= k < N_C};
y := {[i] : 0 <= i < N_R};
spmv := {[i,j]: 0 <= i < N_R && index(i) <= j < index(i+1) && j >= 0 && j < NNZ};
stmt(spmv):=y[i]+=A[j]*x[col[j]];
        """
    g = from_spec(spec)
    print(g.graphgen())
    print(g.codegen())

    spec = """
# CSR-ELL Exec Spec
name('ell_spmv');
data := {[i,k] : 0 <= i < N && 0 <= k < K};
cols := {[i,k] : 0 <= i < N && 0 <= k < K};
index := {[i] : 0 <= i <= N};
x := {[k] : 0 <= k < M};
y := {[i] : 0 <= i < N};
spmv := {[i,k] : 0 <= i < N && 0 <= k < K};
stmt(spmv):=y[i]+=data[i,k]*x[cols[i,k]];
            """
    g = from_spec(spec)
    print(g.graphgen())
    print(g.codegen())

    spec = """
# CSR-ELL Inspector Spec
name('ell_insp');
in := {[j] : 0 <= j < NNZ};
col := {[j] : 0 <= j < NNZ};
index := {[i] : 0 <= i <= N};
icsr := {[i,j]: 0 <= i < N && index(i) <= j < index(i+1) && j >= 0 && j < NNZ};
tdiff := {[i,j] -> [i,k]: k=j-index(i)};
diff := tdiff * icsr;
K := 0;
stmt(diff) := "K=max(k,K)";

data := {[k,i] : 0 <= k < K && 0 <= i < N};
cols := {[k,i] : 0 <= k < K && 0 <= i < N};

tcpy := {[i,j] -> [i,j,k]: k=j-index(i)};
copy := tcpy * icsr;
stmt(copy) := "cols[k,i] = col[j]";
stmt(copy) := "data[k,i] = in[j]";

fuse(diff, copy)
                """
    g = from_spec(spec)
    print(g.graphgen())
    print(g.codegen())

    return g

def main():
    gen_csrtobsr()
    #gen_csr_spmv()
    #gen_bsr_spmv()
    #gen_jacobi()
    #gen_mfd()
    gsl_test()

    bmark = sys.argv[1]
    graph = sys.argv[2]

    gdict = settings.graphs[graph]
    g = FlowGraph(graph, gdict['nodes'], gdict['edges'], gdict['comps'])
    g.write()

    # Output the domain definitions...
    symbol = settings.benchmarks[bmark]['symbol']
    varList = settings.benchmarks[bmark]['vars']
    domList = settings.benchmarks[bmark]['domains']

    print("# Domains")
    domNames = []
    for domain in domList:
        name = '%s_dom' % domain['name']
        domNames.append(name)

        line = '%s := [%s] -> { STM_%s' % (name, symbol, domain['name'])
        line = '%s[%s]' % (line, ','.join(varList))
        if len(domain['bounds']) > 0:
            line += ' : '
            for bound in domain['bounds']:
                (name, lower, upper) = bound
                loper = '<='
                uoper = '<='
                if '-1' in lower:
                    loper = loper.replace('=', '')
                    lower = lower.replace('-1', '')
                if '-1' in upper:
                    uoper = uoper.replace('=', '')
                    upper = upper.replace('-1', '')
                if len(lower) < 1:
                    out = '%s %s %s' % (name, loper, upper)
                elif len(upper) < 1:
                    loper = ">="
                    out = '%s %s %s' % (name, loper, lower)
                else:
                    out = '%s %s %s %s %s' % (lower, loper, name, uoper, upper)
                line += out + ' and '

            line = line[0:len(line) - 4]
        line += '};'
        print(line)

    line = 'union := %s;' % ' + '.join(domNames)
    print(line)

    print("\n# Transforms")
    print('chain: = [%s] -> {' % symbol)

    # This is the hard part... traverse the graph...

    print("};\n")
    print('# Apply')
    print("result: = chain * union;\n")

    print('# Generate')
    print('codegen(result)')


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt as e: # Ctrl-C
        print("Closing gracefully on keyboard interrupt...")
    except Exception as e:
        print('ERROR: ' + str(e))
        tb.print_exc()
