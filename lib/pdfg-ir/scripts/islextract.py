#!/usr/bin/env python3

import sys

from codegen.cpp import CppParser
from codegen.visit import DOTVisitor, PDFGVisitor
from codegen.setlib import *
from codegen import settings

from latex import build_pdf

from tools import files

def gen_bcsr():
    items = []

    # Known constants
    N_R = Constant('N_R', '4')
    N_C = Constant('N_C', '4')
    NNZ = Constant('NNZ', '7')
    R = Constant('R', '2')
    C = Constant('C', '2')

    # Icsr: = [N_R, NNZ, index_i_, index_ip1_] -> {
    #     S[i, k_A, k_c]: 0 <= i < N_R and 0 <= k_A < NNZ and index_i_ <= k_A < index_ip1_ and k_c = k_A};

    # Vars
    i = Var('i', '0', 'N_R', tightup=False)
    jA1 = Var('j_A', '0', 'NNZ', tightup=False)
    jA2 = Var('j_A', 'index(i)', 'index(i+1)', tightup=False)
    jC = Var('j_c', 'j_A', 'j_A')
    j = Var('j', 'index(i)', 'index(i+1)', tightup=False)
    k1 = Var('k', '0', 'N_C', tightup=False)
    k2 = Var('k', 'col(j)', 'col(j)')

    set = Set("", [i, jA1, jA2, jC])
    data = Domain("I_data", [set])
    #items.append(data)

    ii = Var('ii', '0', 'N_R/R', tightup=False)
    kk = Var('kk', '0', 'N_C/C', tightup=False)
    ri = Var('ri', '0', 'R', tightup=False)
    ck = Var('ck', '0', 'C', tightup=False)
    i2 = Var('i', 'ii*R+ri', 'ii*R+ri')
    kk2 = Var('kk', 'col(j)/C', 'col(j)/C')
    ck2 = Var('ck', 'col(j)-kk*C', 'col(j)-kk*C')

    statements = []

    #makeset = Domain("I_makeset", [Set("makeset", [i, j])])
    #items.append(makeset)
    #statements.append(makeset)

    csr = Domain("I_csr", [Set("", [i, j])])
    tile = Domain("I_tile", [Set("tile", [ii, kk])])

    print(csr)
    print(tile)

    count = Domain("I_count", [Set("count", [ii, kk])])
    items.append(count)
    statements.append(count)

    order = Domain("I_order", [Set("order", [ii, kk])])
    items.append(order)
    statements.append(order)

    copy = Domain("I_copy", [Set("copy", [i, j])])
    items.append(copy)
    statements.append(copy)

    invert = Domain("I_invert", [Set("invert", [ii, kk])])
    items.append(invert)
    statements.append(invert)

    for statement in statements:
        # Print - CSR
        call = Call('print', [statement.name])
        items.append(call)

        # CodeGen - Tile
        call = Call('codegen', [statement.name])
        items.append(call)

    print("# ISL")
    for item in items:
        print(item)

    stop=1

def gen_csr():
    # Known constants
    N_R = Constant('N_R', '4')
    N_C = Constant('N_C', '4')
    NNZ = Constant('NNZ', '7')

    # Icsr: = [N_R, NNZ, index_i_, index_ip1_] -> {
    #     S[i, k_A, k_c]: 0 <= i < N_R and 0 <= k_A < NNZ and index_i_ <= k_A < index_ip1_ and k_c = k_A};

    # Vars
    i = Var('i', '0', 'N_R', tightup=False)
    kA1 = Var('k_A', '0', 'NNZ', tightup=False)
    kA2 = Var('k_A', 'index(i)', 'index(i+1)', tightup=False)
    kC = Var('k_c', 'k_A', 'k_A')

    objects = []

    set = Set("", [i, kA1, kA2, kC])
    csr = Domain("I_csr", [set])
    objects.append(csr)

    # Idense: = [N_R, index_i_, index_ip1_, col_k_] -> {
    #     S[i, k, j]: 0 <= i < N_R and index_i_ <= k < index_ip1_ and j = col_k_};

    # I_{dense} = \{ [i,k,j]\;|\; 0 \leq i < N_{R} \wedge j = col(k) \wedge index(i) \leq k < index(i+1)  \}

    j = Var('j', 'col(k)', 'col(k)')
    k = Var('k', 'index(i)', 'index(i+1)', tightup=False)
    set = Set("", [i, k, j])
    dense = Domain("I_dense", [set])
    objects.append(dense)

    # Iord: = [N_R, index_i_, index_ip1_, col_k_] -> {
    #     c_map[i, j, k]: 0 <= i < N_R and index_i_ <= k < index_ip1_ and j = col_k_};
    c_map = Set("c_map", [i, j, k])
    order = Domain("I_ord", [c_map])
    objects.append(order)

    # Iinv: = [N_R, index_i_, index_ip1_, col_k_] -> {
    #     cinv_map[i, j, k]: 0 <= i < N_R and index_i_ <= k < index_ip1_ and j = col_k_;};
    cinv_map = Set("cinv_map", [i, j, k])
    invert = Domain("I_inv", [cinv_map])
    objects.append(invert)

    # Union
    union = Union('I_insp', order, invert)
    objects.append(union)

    # Tfuse: = [N_R, index_i_, index_ip1_, col_k_] -> {
    #     c_map[i, j, k] -> [0, i, j, k, 0];
    #     cinv_map[i, j, k] -> [0, i, j, k, 1];
    # };
    # Ifuse: = Tfuse * Iinsp;

    tfuse = Fuse('T_fuse', [c_map, cinv_map])
    objects.append(tfuse)

    # Union
    apply = Apply('I_fuse', tfuse, union)
    objects.append(apply)

    # Print
    call = Call('print', [apply.name])
    objects.append(call)

    # CodeGen
    call = Call('codegen', [apply.name])
    objects.append(call)

    print("# ISL")
    for obj in objects:
        print(obj)

    latex = (r"\documentclass{article}"
             r"\usepackage{amsmath}"
             r"\begin{document}"
             r"\begin{align*}")
    for obj in objects:
        latex += obj.latex() + r"\\" + "\n"
    latex += r"\end{align*}"
    latex += r"\end{document}"
    print(latex)

    # env = make_env(loader=FileSystemLoader('.'))
    # tpl = env.get_template('doc.latex')

    # this builds a pdf-file inside a temporary directory
    pdf = build_pdf(latex)
    pdf.save_to('csr.pdf')
    stop=1

def gen_jacobi():
    #hdrFile = '%s.h' % files.getPathWithoutExt(srcFile)
    #print("Writing header file '%s'..." % hdrFile)

    t = Var("t", "1", "T")
    i = Var("i", "1", "N")
    set = Set("S", [t, i])
    domain = Domain("dom", [set])
    print(domain)

    sched = Function("sched", [set])
    skewed = (Skew(offsets=["", "t"])).apply(sched)
    print(skewed)

    stop=1

    # file = sys.stderr #open(hdrFile, 'w')
    # gen = Generator('Jacobi1D', file)
    # gen.transform(skewed, domain)
    # code = gen.generate()
    #file.close()
    #print(code)

def main():
    if len(sys.argv) < 2:
        sys.argv.append('-h')

    gen_bcsr()
    gen_csr()
    gen_jacobi()

    benchmark = sys.argv[1]
    srcFile = '%s/%s/%s' % (settings.paths['base'], benchmark, settings.benchmarks[benchmark]['source'])

    parser = CppParser(srcFile)
    ast = parser.parse();

    dotFile = '%s.ast.dot' % files.getPathWithoutExt(srcFile)
    print("Writing DOT file '%s'..." % dotFile)

    file = open(dotFile, 'w')
    visitor = DOTVisitor(file)
    visitor.visit(ast.getRoot())
    file.close()

    # Here we would use the loop visitor to find loop nests and extract their upper and lower bounds for ISL..
    # but due to time constraints, moving directly to ISL code...
    visitor = PDFGVisitor()
    visitor.visit(ast.getRoot())
    stop = 1

if __name__ == '__main__':
    try:
        main()
    except:
        print("Error: ", sys.exc_info())
        raise
