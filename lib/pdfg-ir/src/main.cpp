#include <iostream>
#include <pdfg/GraphIL.hpp>
#include <pdfg/InspGen.hpp>
#include <pdfg/Codegen.hpp>

using namespace pdfg;
using namespace std;

int main() {
    Iter i("i"), n("n"), j("j"), m("m");
    Func rp("rp"), row("row"), col("col"), crow("crow"), crp("crp");
    Const N("N"), M("M"), NNZ("NNZ"), NZR("NZR");

    Space dns("Idns", 0 <= i < N ^ 0 <= j < M);
    Space csr("Icsr", 0 <= i < N ^ rp(i) <= n < rp(i+1) ^ j==col(n));
    Space coo("Icoo", 0 <= n < NNZ ^ i==row(n) ^ j==col(n));
    Space dsr("Idsr", 0 <= m < NZR ^ i==crow(m) ^ crp(m) <= n < crp(m+1) ^ j==col(n));

    //Space ocsr = csr.to_omega();

    Iter k("k");
    Const K("K");
    Func ecol("ecol");
    Space ell("Iell", 0 <= i < N ^ 0 <= k < K ^ j==ecol(i,k));

    Iter b("b");
    Const B("B"), NB("NB");
    Func bp("bp"), bind("bind", 2), eind("eind", 2);
    Space hic("Ihic", 0 <= b < NB ^ bp(b) <= n < bp(b+1) ^ i==bind(b,0)*B+eind(n,0) ^
                      j==bind(b,1)*B+eind(n,1) ^ k==bind(b,2)*B+eind(n,2));

    //Relation rel("Tcoo_csr", coo, csr);
    //cout << Codegen().gen(coo) << endl;
    //InspGen(coo, csr).gen();

    Space val("val", NNZ), x("x", N), y("y", N);
    Comp spmv = csr + (y(i) += val(n) * x(j));

    // Let's switch to inspectors!
    // COO->CSR Inspector:
    Space insp1("I_N", 0 <= n < NNZ ^ i==row(n) ^ i >= N);
    //auto sum = N+1;
    Comp inspN = insp1 + (N=N+1);
    cerr << inspN << endl;
    cerr << Codegen("").gen(inspN) << endl;

    //Space insp2("I_rp", 0 <= n < NNZ ^ 0 <= i < N ^ i==row(n) ^ n >= rp(i+1));
    Space insp2("I_rp", 0 <= n < NNZ ^ i==row(n) ^ n >= rp(i+1));
    Comp insp_rp = insp2 + (rp(i+1) = n+1);
    cerr << insp_rp << endl;
    cerr << Codegen("").gen(insp_rp) << endl;

    // How do we turn these expressions into graphs?
    // 1) We'll want to extend Access as Read and Write, depending on whether Space is Lhs or Rhs.
    // 2) Space can be extended as IterSpace or DataSpace.
    // 3) DataSpaces become DataNodes, Comps become StmtNodes, Relations TransNodes.
    // 4) Figure out how to express inspectors, and multi-part computations like CG.
    // 5) Need a timing inspector (like OSKI) to determine which format is fastest on each dataset, and use it.
    // 6) Also want to gather performance information during execution (timing, input streams, storage sizes,
    //    and counters like PAPI to build and validate the performance model (power consumption too!).
    // 7) Port over as much Python code as possible!

    return 0;
}
