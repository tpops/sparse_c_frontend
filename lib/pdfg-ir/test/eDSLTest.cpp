#include <cmath>
#include <gtest/gtest.h>
#include <iostream>
#include <map>
#include <sstream>
#include <pdfg/Codegen.hpp>
#include <pdfg/GraphIL.hpp>
#include <poly/PolyLib.hpp>
//#include <pdfg/FlowGraph.hpp>
//#include <isl/IntSetLib.hpp>
//#include <solve/Z3Lib.hpp>

using namespace pdfg;
using namespace poly;
using namespace std;

TEST(eDSLTest, Dense) {
    Iter i("i"), j("j");
    Const N("N"), M("M");
    Space dns("Idns", 0 <= i < N ^ 0 <= j < M);
    string result = Codegen().gen(dns);
    string expected = "for(t1 = 0; t1 <= N-1; t1++) {\n  for(t2 = 0; t2 <= M-1; t2++) {\n    s0(t1,t2);\n  }\n}\n";
    //cerr << result << endl;
    ASSERT_EQ(result, expected);
}

TEST(eDSLTest, COO) {
    Iter i("i"), n("n"), j("j");
    Func row("row"), col("col");
    Const NNZ("NNZ");
    Space coo("Icoo", 0 <= n < NNZ ^ i==row(n) ^ j==col(n));
    string result = Codegen().gen(coo);
    string expected = "for(t1 = 0; t1 <= NNZ-1; t1++) {\n"
                      "  t2=row(t1);\n"
                      "  t3=col(t1);\n"
                      "  s0(t1,t2,t3);\n"
                      "}\n";
    //cerr << result << endl;
    ASSERT_EQ(result, expected);
}

TEST(eDSLTest, CSR) {
    Iter i("i"), j("j"), n("n");
    Const N("N"), NNZ("NNZ");
    Func rp("rp"), col("col");
    Space csr("Icsr", 0 <= i < N ^ rp(i) <= n < rp(i+1) ^ j==col(n));
    string result = Codegen().gen(csr);
    string expected = "for(t1 = 0; t1 <= N-1; t1++) {\n  for(t2 = rp(t1); t2 <= rp1(t1)-1; t2++) {\n    t3=col(t1,t2);\n    s0(t1,t2,t3);\n  }\n}\n";
    //cerr << result << endl;
    ASSERT_EQ(result, expected);
}

TEST(eDSLTest, DSR) {
    Iter i("i"), n("n"), j("j"), m("m");
    Func crp("crp"), crow("crow"), col("col");
    Const N("N"), NZR("NZR");
    Space dsr("Idsr", 0 <= m < NZR ^ i==crow(m) ^ crp(m) <= n < crp(m+1) ^ j==col(n));
    string result = Codegen().gen(dsr);
    //cerr << result;
    string expected = "for(t1 = 0; t1 <= NZR-1; t1++) {\n  t2=crow(t1);\n  for(t3 = crp(t1); t3 <= crp1(t1)-1; t3++) {\n    t4=col(t1,t2,t3);\n    s0(t1,t2,t3,t4);\n  }\n}\n";
    ASSERT_EQ(result, expected);
}

TEST(eDSLTest, ELL) {
    Iter i("i"), j("j"), k("k");
    Const N("N"), K("K");
    Func rp("rp"), ecol("ecol");
    Space ell("Iell", 0 <= i < N ^ 0 <= k < K ^ j==ecol(i,k));
    string result = Codegen().gen(ell);
    string expected = "for(t1 = 0; t1 <= N-1; t1++) {\n  for(t2 = 0; t2 <= K-1; t2++) {\n    t3=ecol(t1,t2);\n    s0(t1,t2,t3);\n  }\n}\n";
    //cerr << result << endl;
    ASSERT_EQ(result, expected);
}

TEST(eDSLTest, Lset) {
    Iter l("l"), s("s"), i("i"), n("n"), j("j");
    Func lp("lp"), lrow("lrow"), rp("rp"), col("col");
    Const L("L");
    Space lev("Ilev", 0 <= l < L ^ lp(l) <= s < lp(l+1) ^ i==lrow(s) ^ rp(i) <= n < rp(i+1) ^ j==col(n));
    string result = Codegen().gen(lev);
    string expected = "for(t1 = 0; t1 <= L-1; t1++) {\n  for(t2 = lp(t1); t2 <= lp1(t1)-1; t2++) {\n    t3=lrow(t1,t2);\n    for(t4 = rp(t1,t2,t3); t4 <= rp1(t1,t2,t3)-1; t4++) {\n      t5=col(t1,t2,t3,t4);\n      s0(t1,t2,t3,t4,t5);\n    }\n  }\n}\n";
    //cerr << result << endl;
    ASSERT_EQ(result, expected);
}

TEST(eDSLTest, CSC) {
    Iter i("i"), j("j"), n("n");
    Const M("M"), NNZ("NNZ");
    Func cp("cp"), row("row");
    Space csc("Icsc", 0 <= j < M ^ cp(j) <= n < cp(j+1) ^ i==row(n));
    string result = Codegen().gen(csc);
    string expected = "for(t1 = 0; t1 <= M-1; t1++) {\n  for(t2 = cp(t1); t2 <= cp1(t1)-1; t2++) {\n    t3=row(t1,t2);\n    s0(t1,t2,t3);\n  }\n}\n";
    //cerr << result << endl;
    ASSERT_EQ(result, expected);
}

TEST(eDSLTest, TCOO) {
    Iter i("i"), n("n"), j("j"),  k("k");
    Func ind0("ind0"), ind1("ind1"),ind2("ind2");
    Const NNZ("NNZ");
    Space coo("Icoo", 0 <= n < NNZ ^ i==ind0(n) ^ j==ind1(n) ^ k==ind2(n));
    string result = Codegen().gen(coo);
    string expected = "for(t1 = 0; t1 <= NNZ-1; t1++) {\n  t2=ind0(t1);\n  t3=ind1(t1);\n  t4=ind2(t1);\n  s0(t1,t2,t3,t4);\n}\n";
    //cerr << result << endl;
    ASSERT_EQ(result, expected);
}

TEST(eDSLTest, HiCOO) {
    Iter i("i"), j("j"), k("k"), n("n"), b("b");
    Const B("B", 8), NB("NB");
    //Func bp("bp"), bind("bind", 2), eind("eind", 2);
    Func bp("bp"), bind0("bind0"), bind1("bind1"), bind2("bind2"), eind0("eind0"), eind1("eind1"), eind2("eind2");
    Space hic("Ihic", 0 <= b < NB ^ bp(b) <= n < bp(b+1) ^ i==bind0(b)*B+eind0(n) ^
                      j==bind1(b)*B+eind1(n) ^ k==bind2(b)*B+eind2(n));
    string result = Codegen().gen(hic);
    string expected = "for(t1 = 0; t1 <= NB-1; t1++) {\n  for(t2 = bp(t1); t2 <= bp1(t1)-1; t2++) {\n    t3=eind0(t1,t2)+8*bind0(t1);\n    t4=8*bind1(t1)+eind1(t1,t2);\n    t5=8*bind2(t1)+eind2(t1,t2);\n    s0(t1,t2,t3,t4,t5);\n  }\n}\n";
    //cerr << result << endl;
    ASSERT_EQ(result, expected);
}

TEST(eDSLTest, CSF) {
    Iter i("i"), j("j"), k("k"), p("p"), m("m"), n("n");
    Func ind0("ind0"), ind1("ind1"), ind2("ind2");
    Func pos0("pos0"), pos1("pos1");
    Const NZF("NZF");
    Space csf("Icsf", 0 <= p < NZF ^ i==ind0(p) ^ pos0(p) <= m < pos0(p+1) ^ j==ind1(m) ^ pos1(m) <= n < pos1(m+1) ^ k==ind2(n));
    string result = Codegen().gen(csf);
    string expected = "for(t1 = 0; t1 <= NZF-1; t1++) {\n  t2=ind0(t1);\n  for(t3 = pos0(t1); t3 <= pos0_1(t1)-1; t3++) {\n    t4=ind1(t1,t2,t3);\n    for(t5 = pos1(t1,t2,t3); t5 <= pos1_1(t1,t2,t3)-1; t5++) {\n      t6=ind2(t1,t2,t3,t4,t5);\n      s0(t1,t2,t3,t4,t5,t6);\n    }\n  }\n}\n";
    ASSERT_EQ(result, expected);
}

TEST(eDSLTest, DSR_SpMV) {
    Iter i("i"), n("n"), j("j"), m("m");
    Func crp("crp"), crow("crow"), col("col");
    Const N("N"), M("M"), NZR("NZR"), NNZ("NNZ");
    //Space dsr("spmv", 0 <= m < NZR ^ i==crow(m) ^ crp(m) <= n < crp(m+1) ^ 0 <= n < NNZ ^ j==col(n));
    Space dsr("spmv", 0 <= m < NZR ^ i==crow(m) ^ crp(m) <= n < crp(m+1) ^ j==col(n));

    string name = "dsr_spmv";
    init(name);
    Space val("val", NNZ), x("x", M), y("y", N);
    Comp spmv = dsr + (y[i] += val[n] * x[j]);
    //cerr << codegen() << endl;

    string result = stringify<Comp>(spmv);
    string expected = "spmv(m,i,n,j) = { 0 <= m ^ m < NZR ^ 0 < NZR ^ i = crow(m) ^ crp(m) <= n ^ n < crp(m+1) ^ crp(m) < crp(m+1) ^ j = col(n) } : { y[i]+=val[n]*x[j] }";
    ASSERT_EQ(result, expected);

    result = codegen(name);
    //cerr << result << endl;
    expected = "#include <stdio.h>\n"
               "#include <stdlib.h>\n"
               "#include <stdint.h>\n"
               "#include <sys/time.h>\n\n"
               "#define min(x,y) (((x)<(y))?(x):(y))\n"
               "#define max(x,y) (((x)>(y))?(x):(y))\n"
               "#define floord(x,y) ((x)/(y))\n"
               "#define offset2(i,j,M) ((j)+(i)*(M))\n"
               "#define offset3(i,j,k,M,N) ((k)+((j)+(i)*(M))*(N))\n"
               "#define offset4(i,j,k,l,M,N,P) ((l)+((k)+((j)+(i)*(M))*(N))*(P))\n"
               "#define arrinit(ptr,val,size) for(unsigned __i__=0;__i__<(size);__i__++) (ptr)[__i__]=(val)\n\n"
               "void dsr_spmv(const unsigned NZR, const unsigned* crow, const unsigned* crp, const unsigned* col, const float* val, const float* x, float* y);\n"
               "inline void dsr_spmv(const unsigned NZR, const unsigned* crow, const unsigned* crp, const unsigned* col, const float* val, const float* x, float* y) {\n"
               "    unsigned t1,t2,t3,t4,t5;\n"
               "// spmv\n"
               "#define col(m,i,n) col[(n)]\n"
               "#define crow(m) crow[(m)]\n"
               "#define crp(m) crp[(m)]\n"
               "#define crp1(m) crp[(m+1)]\n\n"
               "#undef s0\n"
               "#define s0(m,i,n,j) y[(i)]+=val[(n)]*x[(j)]\n\n"
               "for(t1 = 0; t1 <= NZR-1; t1++) {\n"
               "  t2=crow(t1);\n"
               "  for(t3 = crp(t1); t3 <= crp1(t1)-1; t3++) {\n"
               "    t4=col(t1,t2,t3);\n"
               "    s0(t1,t2,t3,t4);\n"
               "  }\n"
               "}\n"
               "\n"
               "}    // dsr_spmv\n";
    ASSERT_EQ(result, expected);
}

TEST(eDSLTest, COO_MTTKRP) {
    Iter n("n"), i("i"), j("j"),  k("k"), l("l");
    Func ind0("ind0"), ind1("ind1"),ind2("ind2");
    Const NNZ("NNZ"),  I("I"), J("J"), K("K"), L("L");
    Space coo("Icoo", 0 <= n < NNZ ^ i==ind0(n) ^ j==ind1(n) ^ k==ind2(n)); // ^ 0 <= l < L);
    coo ^= 0 <= l < L;

    Space val("val", NNZ), A("A",I,J), B("B",NNZ), C("C",K,J), D("D",L,J);
    Comp mttkrp = coo + (A(i,j) += B(n) * C(k,j) * D(l,j));

    string result = Codegen().gen(mttkrp);
    //cerr << result << endl;
    string expected = "#define ind0(n) ind0[(n)]\n#define ind1(n) ind1[(n)]\n#define ind2(n) ind2[(n)]\n\n#undef s0\n#define s0(n,i,j,k,l) A[offset2((i),(j),(J))]+=B[(n)]*C[offset2((k),(j),(J))]*D[offset2((l),(j),(J))]\n\nunsigned t1,t2,t3,t4,t5;\n#pragma omp parallel for schedule(auto) private(t1,t2,t3,t4,t5)\nfor(t1 = 0; t1 <= NNZ-1; t1++) {\n  t2=ind0(t1);\n  t3=ind1(t1);\n  t4=ind2(t1);\n  for(t5 = 0; t5 <= L-1; t5++) {\n    s0(t1,t2,t3,t4,t5);\n  }\n}\n";
    ASSERT_EQ(result, expected);
}

TEST(eDSLTest, CSF_MTTKRP) {
    Iter i("i"), j("j"), k("k"), l("l"), p("p"), m("m"), n("n");
    Func ind0("ind0"), ind1("ind1"), ind2("ind2");
    Func pos0("pos0"), pos1("pos1");
    Const NZF("NZF"), NNZ("NNZ"), I("I"), J("J"), K("K"), L("L");
    Space csf("Icsf", 0 <= p < NZF ^ i==ind0(p) ^ pos0(p) <= m < pos0(p+1) ^ j==ind1(m) ^ pos1(m) <= n < pos1(m+1) ^ k==ind2(n) ^ 0 <= l < L);

    Space val("val", NNZ), A("A",I,J), B("B",NNZ), C("C",K,J), D("D",L,J);
    Comp mttkrp = csf + (A(i,j) += B(n) * C(k,j) * D(l,j));

    string result = Codegen().gen(mttkrp);
    //cerr << result << endl;
    string expected = "#define ind0(p) ind0[(p)]\n#define ind1(p,i,m) ind1[(m)]\n#define ind2(p,i,m,j,n) ind2[(n)]\n#define pos0(p) pos0[(p)]\n#define pos0_1(p) pos0[(p+1)]\n#define pos1(p,i,m) pos1[(m)]\n#define pos1_1(p,i,m) pos1[(m+1)]\n\n#undef s0\n#define s0(p,i,m,j,n,k,l) A[offset2((i),(j),(J))]+=B[(n)]*C[offset2((k),(j),(J))]*D[offset2((l),(j),(J))]\n\nunsigned t1,t2,t3,t4,t5,t6,t7;\n#pragma omp parallel for schedule(auto) private(t1,t2,t3,t4,t5,t6,t7)\nfor(t1 = 0; t1 <= NZF-1; t1++) {\n  t2=ind0(t1);\n  for(t3 = pos0(t1); t3 <= pos0_1(t1)-1; t3++) {\n    t4=ind1(t1,t2,t3);\n    for(t5 = pos1(t1,t2,t3); t5 <= pos1_1(t1,t2,t3)-1; t5++) {\n      t6=ind2(t1,t2,t3,t4,t5);\n      for(t7 = 0; t7 <= L-1; t7++) {\n        s0(t1,t2,t3,t4,t5,t6,t7);\n      }\n    }\n  }\n}\n";
    ASSERT_EQ(result, expected);
}

TEST(eDSLTest, MFD_2D) {
    /**
    # slice(Fx1, c=2)
    Fx1 := [N]->{fx1[c,y,x]: 0<=c<4 and 0<=y<N and 0<=x<=N};
    Fx2 := [N]->{fx2[c,y,x] : 0<=c<4 and 0<=x<=N and 0<=y<N};
    Dx := [N]->{dx[c,y,x] : 0<=c<4 and 0<=x<N and 0<=y<N};

    # slice(Fy1, c=3)
    Fy1 := [N]->{fy1[c,y,x]: 0<=c<4 and 0<=y<=N and 0<=x<N};
    Fy2 := [N]->{fy2[c,y,x] : 0<=c<4 and 0<=y<=N and 0<=x<N};
    Dy := [N]->{dy[c,y,x] : 0<=c<4 and 0<=y<N and 0<=x<N};

    # Statements
    #statement(Fx1) := "Cx1[c,y,x] = (1./12.)*(Bin[c,y,x-2] + 7.0 * Bin[c,y,x-1] +
    #                                          Bin[c,y,x] + Bin[c,y,x+1])";
    #statement(Fx2) := "Cx2[c,y,x] = Cx1[c,y,x] * 2.0 * Cx1[2,y,x]";
    #statement(Dx) := "Bout[c,y,x] += Cx2[c,y,+1] - Cx2[c,y,x]";
    #statement(Fy1) := "Cy1[c,y,x] = (1./12.)*(Bin[c,y-2,x] + 7.0 * Bin[c,y-1,x] +
    #                                          Bin[c,y,x] + Bin[c,y+1,x])";
    #statement(Fy2) := "Cy2[c,y,x] = Cy1[c,y,x] * 2.0 * Cy1[3,y,x]";
    #statement(Dy) := "Bout[c,y,x] += Cy2[c,y+1,x] - Cy2[c,y,x]";

    D := Fx1 + Fx2 + Dx + Fy1 + Fy2 + Dy;
     */
    Iter c("c"), y("y"), x("x");
    Const C("C", 4), N("N");
    Space fx("fx", 0 <= c < C ^ 0 <= y < N ^ 0 <= x <= N);
    Space df("df", 0 <= c < C ^ 0 <= y < N ^ 0 <= x < N);
    //Comp fx1 = fx + (Cx1[c,y,x] = (1./12.)*(Bin[c,y,x-2] + 7.0 * Bin[c,y,x-1] + Bin[c,y,x] + Bin[c,y,x+1]));
    //Comp fx2 = fx + (Cx2[c,y,x] = Cx1[c,y,x] * 2.0 * Cx1[2,y,x]);
    //Comp dx = df + (Cx2[c,y,x] = Cx1[c,y,x] * 2.0 * Cx1[2,y,x]);
}

TEST(eDSLTest, COO_CSR_Insp) {
    Iter i("i"), n("n"), j("j");
    Func rp("rp"), row("row"), col("col");
    Const N("N"), NNZ("NNZ");

    // COO->CSR Inspector:
    Space insp1("I_N", 0 <= n < NNZ ^ i==row(n));
    Comp inspN = insp1 + (i >= N) + (N=i+1);
    string result = Codegen("").gen(inspN);
//    cerr << inspN << endl;
//    cerr << result << endl;
    string expected = "#define row(n) row[(n)]\n\n#undef s0\n#define s0(n,i) if ((i) >= N) N=(i)+1\n\nunsigned t1,t2;\nfor(t1 = 0; t1 <= NNZ-1; t1++) {\n  t2=row(t1);\n  s0(t1,t2);\n}\n";
    ASSERT_EQ(result, expected);

    Space insp2("I_rp", 0 <= n < NNZ ^ i==row(n) ^ n >= rp(i+1));
    Comp insp_rp = insp2 + (rp(i+1) = n+1);
    result = Codegen("").gen(insp_rp);
//    cerr << insp_rp << endl;
//    cerr << result << endl;
    expected = "#define row(n) row[(n)]\n"
               "#define rp(n,i) rp[(i+1)]\n\n"
               "#undef s0\n"
               "#define s0(n,i) rp((i)+1)=(n)+1\n\n"
               "unsigned t1,t2;\n"
               "for(t1 = 0; t1 <= NNZ-1; t1++) {\n"
               "  t2=row(t1);\n"
               "  if (t1 >= rp(t1,t2)) {\n"
               "    s0(t1,t2);\n"
               "  }\n"
               "}\n";

    ASSERT_EQ(result, expected);
}

TEST(eDSLTest, COO_CSR_Insp_Opt) {
    Iter i("i"), n("n"), j("j"), m("m");
    Func rp("rp"), row("row"), col("col");
    Const N("N"), NNZ("NNZ");

    // Here we add the constraint: row(i-1) <= row(i), 1 <= i < N (i.e., row is sorted)

    // COO->CSR Inspector:
    Space insp1("I_N"); //, 0 <= n < NNZ ^ i==row(n) ^ i >= N);
    //Math expr = (N=row(NNZ-1));
    Comp inspN = insp1 + (N=row(NNZ-1)+1);
    string result = Codegen("").gen(inspN);
    cerr << inspN << endl;
    cerr << result << endl;
    string expected = "#undef s0\n"
                      "#define s0() N=row(NNZ-1)+1\n\n"
                      "s0();\n";
    ASSERT_EQ(result, expected);

    Space insp2("I_rp", 0 <= n < NNZ ^ i==row(n) ^ n >= rp(i+1));
    Comp insp_rp = insp2 + (rp(i+1) = n+1);
    result = Codegen("").gen(insp_rp);
    cerr << insp_rp << endl;
    cerr << result << endl;
    expected = "#define row(n) row[(n)]\n"
               "#define rp(n,i) rp[(i+1)]\n\n"
               "#undef s0\n"
               "#define s0(n,i) rp((i)+1)=(n)+1\n\n"
               "unsigned t1,t2;\n"
               "for(t1 = 0; t1 <= NNZ-1; t1++) {\n"
               "  t2=row(t1);\n"
               "  if (t1 >= rp(t1,t2)) {\n"
               "    s0(t1,t2);\n"
               "  }\n"
               "}\n";

    ASSERT_EQ(result, expected);
}

TEST(eDSLTest, Jacobi2D) {
    Iter t('t'), i('i'), j('j');
    Const T('T'), N('N');   // N=#rows/cols, M=#nnz, K=#iterations
    Space jac("jac", 1 <= t <= T ^ 1 <= i <= N ^ 1 <= j <= N);
    Space A("A", T, N, N);
    init("jacobi2d");
    Comp stencil = jac + (A(t,i,j) = (A(t-1,i,j) + A(t-1,i,j-1) + A(t-1,i,j+1) + A(t-1,i+1,j) + A(t-1,i-1,j)) * 0.2);
    print("out/jacobi2d.json");
    string result = codegen("out/jacobi2d.o");
    //cerr << result << endl;
    ASSERT_TRUE(!result.empty());
}

TEST(eDSLTest, Jac2D) {
    init("jacobi2d");
    Iter t('t'), i('i'), j('j');
    Const M('M'), N('N');
    Space jac("jac", 1 <= i <= M ^ 1 <= j <= N);
    Space A("A", M+2, N+2);
    Space B("B", M+2, N+2);
    Comp stencil = jac + (A(i,j) = (A(i,j) + A(i,j-1) + A(i,j+1) + A(i-1,j) + A(i+1,j))*0.2);
    print("out/jacobi2d.json");
    string result = codegen("out/jacobi2d.o");
    //cerr << result << endl;
    ASSERT_TRUE(!result.empty());
}

TEST(eDSLTest, COO_CSR_Insp_Fuse) {
    // COO->CSR Inspector:
    // Here we assume the constraint: row(i-1) <= row(i), 1 <= i < N (i.e., row is sorted)
    Iter i('i'), n('n'), j('j'), m('m');
    Func rp("rp"), row("row"), col("col");
    Const N("N"), NNZ("NNZ");
    Space insp1("I_N");
    Space insp2("Irp", 0 <= n < NNZ ^ i==row(n));

    pdfg::init("coo_csr_insp", "N", "d", "u", {"rp"});
    Comp inspN("inspN", insp1, (N=row(NNZ-1)+1));
    Comp insp_rp("insp_rp", insp2, (n >= rp(i+1)), (rp(i+1) = n+1));
    Comp insp_rp2("insp_rp2", insp2, (rp(i) > rp(i+1)), (rp(i+1) = rp(i)+0));

    pdfg::fuse(insp_rp, insp_rp2);
    print("out/coo_csr_insp.json");
    string result = codegen("out/coo_csr_insp.h", "", "C++", "simd");
    ASSERT_TRUE(!result.empty());
}

TEST(eDSLTest, ConjGrad) {
    Iter t('t'), i('i'), j('j'), n('n');
    Const N('N'), M('M'), K('K');   // N=#rows/cols, M=#nnz, K=#iterations
    Func rp("rp"), row("row"), col("col");

    // Iteration spaces:
    Space sca("sca");
    Space vec("vec", 0 <= i < N);
    Space csr("csr", 0 <= i < N ^ rp(i) <= n < rp(i+1) ^ j==col(n));
    //Space coo("coo", 0 <= n < M ^ i==row(n) ^ j==col(n));
    //Space spv("spv", 0 <= n < M ^ i==row(n));   // Sparse vector, to enable fusion of dot products with SpMV.
    //Space mtx = coo;
    Space mtx = csr;

    // Data spaces:
    Space A("A", M), x("x", N), b("b", N), r("r", N), s("s", N), d("d", N);
    Space v1("v1", N), v2("v2", N), v3("v3", N);
    Space alpha("alpha"), beta("beta"), ds("ds"), rs("rs"), rs0("rs0");

    string name = "conjgrad_csr";
    //string name = "conjgrad_coo";
    init(name, "rs", "d", "", {"d", "r"}, to_string(0));

    //Comp copy("copy", vec, ((r[i]=b[i]+0) ^ (d[i]=b[i]+0)));
    Comp spmv("spmv", mtx, (s[i] += A[n] * d[j]));
    Comp ddot("ddot", vec, (ds += d[i]*s[i]));
    //Comp ddot("ddot", spv, (ds += d[i]*s[i]));
    Comp rdot0("rdot0", vec, (rs0 += r[i]*r[i]));
    //Comp rdot0("rdot0", spv, (rs0 += r[i]*r[i]));
    Comp adiv("adiv", sca, (alpha = rs0/ds));
    Comp xadd("xadd", vec, (x[i] += alpha * d[i]));
    Comp rsub("rsub", vec, (r[i] -= alpha*s[i]));
    Comp rdot("rdot", vec, (rs += r[i]*r[i]));
    Comp bdiv("bdiv", sca, (beta = rs / rs0));
    Comp bmul("bmul", vec, (d[i] *= beta));
    Comp dadd("dadd", vec, (d[i] += r[i]));

    // Perform fusions
    fuse("spmv", "ddot", "rdot0");
    fuse("xadd", "rsub", "rdot");
    fuse("bmul", "dadd");

    perfmodel();        // perfmodel annotates graph with performance attributes.
    print("out/" + name + ".json");
    string result = codegen("out/" + name + ".o", "", "C++", "auto");
    //cerr << result << endl;
    ASSERT_TRUE(!result.empty());
}

TEST(eDSLTest, ConjGradTime) {
    Iter t('t'), i('i'), j('j'), n('n');
    Const N('N'), M('M'), K('K');   // N=#rows/cols, M=#nnz, K=#iterations
    Func rp("rp"), row("row"), col("col");

    // Iteration spaces:
    Space sca("sca");
    Space vec("vec", 0 <= i < N);
    Space csr("csr", 0 <= i < N ^ rp(i) <= n < rp(i+1) ^ j==col(n));
    //Space coo("coo", 0 <= n < M ^ i==row(n) ^ j==col(n));
    //Space spv("spv", 0 <= n < M ^ i==row(n));   // Sparse vector, to enable fusion of dot products with SpMV.
    //Space mtx = coo;
    Space mtx = csr;

    // Data spaces:
    Space A("A", M), x("x", N), b("b", N), r("r", N), s("s", N), d("d", N);
    Space v1("v1", N), v2("v2", N), v3("v3", N);
    Space alpha("alpha"), beta("beta"), ds("ds"), rs("rs"), rs0("rs0");

    string name = "conjgrad_csr";
    //string name = "conjgrad_coo";
    init(name, "rs", "d", "", {"d", "r"}, to_string(0));

    //Comp copy("copy", vec, ((r[i]=b[i]+0) ^ (d[i]=b[i]+0)));
    Comp spmv("spmv", mtx, (s[i] += A[n] * d[j]));
    Comp ddot("ddot", vec, (ds += d[i]*s[i]));
    //Comp ddot("ddot", spv, (ds += d[i]*s[i]));
    Comp rdot0("rdot0", vec, (rs0 += r[i]*r[i]));
    //Comp rdot0("rdot0", spv, (rs0 += r[i]*r[i]));
    Comp adiv("adiv", sca, (alpha = rs0/ds));
    Comp xadd("xadd", vec, (x[i] += alpha * d[i]));
    Comp rsub("rsub", vec, (r[i] -= alpha*s[i]));
    Comp rdot("rdot", vec, (rs += r[i]*r[i]));
    Comp bdiv("bdiv", sca, (beta = rs / rs0));
    Comp bmul("bmul", vec, (d[i] *= beta));
    Comp dadd("dadd", vec, (d[i] += r[i]));

    // Perform fusions
    fuse("spmv", "ddot", "rdot0");
    fuse("xadd", "rsub", "rdot");
    fuse("bmul", "dadd");

    perfmodel();        // perfmodel annotates graph with performance attributes.
    print("out/" + name + ".json");
    string result = codegen("out/" + name + ".o", "", "C++", "auto");
    //cerr << result << endl;
    ASSERT_TRUE(!result.empty());
}

TEST(eDSLTest, ConjGrad2) {
    Iter t('t'), i('i'), j('j'), n('n');
    Const N('N'), M('M'), T('T');   // N=#rows/cols, M=#nnz, K=#iterations
    Func rp("rp"), row("row"), col("col");

    // Iteration spaces:
    Space cpy("cpy", t==0 ^ 0 <= i < N);
    Space sca("sca", 1 <= t <= T);
    Space vec("vec", 1 <= t <= T ^ 0 <= i < N);
    Space csr("csr", 1 <= t <= T ^ 0 <= i < N ^ rp(i) <= n < rp(i+1) ^ j==col(n));
    Space coo("coo", 1 <= t <= T ^ 0 <= n < M ^ i==row(n) ^ j==col(n));
    Space mtx = coo;

    // Data spaces:
    Space A("A", M), x("x", T, N), b("b", N), d("d", T, N), r("r", T, N), s("s", N);
    Space alpha("alpha"), beta("beta"), ds("ds"), rs("rs", T);

    init("conjgrad2");
    Comp copy("copy", cpy, ((r(t,i)=b(i)+0) ^ (d(t,i)=b(i)+0)));
    Comp spmv("spmv", mtx, (s(i) += A(n) * d(t-1,j)));
    Comp ddot("ddot", vec, (ds+=d(t-1,i)*s(i)));
    Comp rdot0("rdot0", vec, (rs(t-1)+=r(t-1,i)*r(t-1,i)));
    Comp adiv("adiv", sca, (alpha=rs(t-1)/ds));
    Comp xadd("xadd", vec, (x(t,i)=x(t-1,i)+alpha*d(t-1,i)));
    Comp rsub("rsub", vec, (r(t,i)-=alpha*s(i)));
    // Add exit predicate for tolerance check here...
    Comp rdot("rdot", vec, (rs(t)+=r(t,i)*r(t,i)));
    Comp bdiv("bdiv", sca, (beta=rs(t)/rs(t-1)));
    Comp dadd("dadd", vec, (d(t,i)=r(t,i)+beta*d(t-1,i)));
    print("out/conjgrad2.json");
    string result = codegen("out/conjgrad2.o");
    //cerr << result << endl;
    ASSERT_TRUE(!result.empty());
}

TEST(eDSLTest, JacobiMethod) {
    Iter t('t'), s('s'), i('i'), j('j'), n('n');
    Const N('N'), M('M'), T('T');

    // Data spaces:
    Space A("A", N, N), x("x", T, N), b("b", N), err("err", 1.0), tol("tol", 1E-6);
    // UFs:
    Func rp("rp"), row("row"), col("col");
    Macro check("check", {t}, {Constr(tol, err, "<")});
    // Iteration space
    Space sca("sca", {0 <= t < T ^ check(t) > 0});
    Space vec("vec", {0 <= t < T ^ check(t) > 0 ^ 0 <= i < N});
    Space mtx("mtx", 0 <= t < T ^ check(t) > 0 ^ 0 <= i < N ^ 0 <= j < N ^ i != j);
    //Comp jac("jac", mtx, ((x(t,i) = b(i)+0) ^ (x(t,i) += -A(i,j) * x(t-1,j)) ^ (x(t,i) /= A(i,j))));
    Comp init("init", vec, (x(t,i) = b(i)+0));
    Comp dot("dot", mtx, (x(t,i) += -A(i,j) * x(t-1,j)));
    Comp div("div", vec, (x(t,i) /= A(i,i)));
    Comp ssq("ssq", vec, (err += (x(t,i) - x(t-1,i)) * (x(t,i) - x(t-1,i))));
    Comp norm("norm", sca, err = sqrt(err));
    // Perform fusions
    fuse({"init", "dot", "div", "ssq", "norm"});

    print("out/jacobi.json");
    string result = codegen("out/jacobi.h");
    //cerr << result << endl;
    ASSERT_TRUE(!result.empty());
}

TEST(eDSLTest, CP_ALS) {
    // TODO: Figure out how to do transpose and norm...

    // TACO-MTTKRP output for reference:
//    for (int32_t pX1 = X1_pos[0]; pX1 < X1_pos[1]; pX1++) {
//        int32_t iX = X1_coord[pX1];
//        for (int32_t pX2 = X2_pos[pX1]; pX2 < X2_pos[(pX1 + 1)]; pX2++) {
//            int32_t jX = X2_coord[pX2];
//            for (int32_t pX3 = X3_pos[pX2]; pX3 < X3_pos[(pX2 + 1)]; pX3++) {
//                int32_t kX = X3_coord[pX3];
//                double tk = X_vals[pX3];
//                for (int32_t rC = 0; rC < C2_dimension; rC++) {
//                    int32_t pC2 = kX * C2_dimension + rC;
//                    int32_t pB2 = jX * B2_dimension + rC;
//                    int32_t pA2 = iX * A2_dimension + rC;
//                    A_vals[pA2] = A_vals[pA2] + tk * C_vals[pC2] * B_vals[pB2];
//                }
//            }
//        }
//    }

    // TODO: These are transposes, figure out if can be handled by changing the data mapping, matrices are
    //   linearized, so should be possible.
    // MxN*NxP -> RxK*KxR
//    Space mm("mm", 0 <= i < I ^ 0 <= k < K ^ 0 <= j < J);
//    Comp mtm = mm + (C(i,k) += A(i,j) * B(j,k));
//    int i, j, k;
//    for (i = 0; i < N; i++)
//        for (j = 0; j < N; j++)
//            for (k = 0; k < N; k++)
//                res[i][j] += mat1[i][k] *
//                             mat2[k][j];

    Iter m("m"), i("i"), j("j"),  k("k"), q("q"), r("r");
    Func ind0("ind0"), ind1("ind1"),ind2("ind2");
    Const I("I"), J("J"), K("K"), M("M"), R("R");
    Real one(1.0);

    Space coo("coo", 0 <= m < M ^ i==ind0(m) ^ j==ind1(m) ^ k==ind2(m));
    Space krp = coo ^ 0 <= r < R;
    Space mtx("mtx", 0 <= i < I ^ 0 <= j < J ^ 0 <= k < K ^ 0 <= r < R);
    Space A("A",I,R), B("B",J,R), C("C",K,R), X("X",M);
    Space Akr("Akr",I,R), Bkr("Bkr",J,R), Ckr("Ckr",K,R);
    Space Asq("Asq",R,R), Bsq("Bsq",R,R), Csq("Csq",R,R);
    Space Ahp("Ahp",R,R), Bhp("Bhp",R,R), Chp("Chp",R,R);
    Space Ainv("Ainv",R,R), Binv("Binv",R,R), Cinv("Cinv",R,R);
    Space sums("sums",R), lmbda("lmbda",R);

    Space vecR("vecR", 0 <= r < R);
    Space hadR("hadR", 0 <= q < R ^ 0 <= r < R);
    Space mtxA("mtxA", 0 <= i < I ^ 0 <= r < R);
    Space mtxB("mtxB", 0 <= j < J ^ 0 <= q < R);
    Space mtxC("mtxC", 0 <= k < K ^ 0 <= r < R);
    Space mulA("mulA", 0 <= q < R ^ 0 <= r < R ^ 0 <= i < I);
    Space mulB("mulB", 0 <= q < R ^ 0 <= r < R ^ 0 <= j < J);
    Space mulC("mulC", 0 <= q < R ^ 0 <= r < R ^ 0 <= k < K);
    Space pmmA("pmmA", 0 <= i < I ^ 0 <= q < R ^ 0 <= r < R);
    Space pmmB("pmmB", 0 <= j < J ^ 0 <= q < R ^ 0 <= r < R);
    Space pmmC("pmmC", 0 <= k < K ^ 0 <= q < R ^ 0 <= r < R);

    init("cp_als");

    // Randomize factor matrices...
    Comp initA("Ainit", mtxA, (A(i,r) = urand()));
    Comp initB("Binit", mtxB, (B(j,r) = urand()));
    Comp initC("Cinit", mtxC, (C(k,r) = urand()));

    Comp mmC("Cmm", mulC, (Csq(q,r) += C(q,k) * C(k,r)));
    Comp mmB("Bmm", mulB, (Bsq(q,r) += B(q,j) * B(j,r)));
    // Hadamard (component-wise) product on RxR square matrices.
    Comp hadA("Ahad", hadR, (Ahp(q,r) = Csq(q,r) * Bsq(q,r)));
    // Now the M-P pseudoinverse (using SVD: A=USV* => A+ = VS+U*).
    Comp pinvA("Apinv", hadR, Ainv(q,r) = one / Ahp(q,r)); //pinv(Ahp));
    Comp krpA("Akrp", krp, (Akr(i,r) += X(m) * C(k,r) * B(j,r)));
    Comp mmAp("Apmm", pmmA, (A(i,q) += Akr(i,r) * Ainv(q,r)));
    // Norm A columns and store in \vec{\lambda}
    Comp ssqA("Assq", mtxA, (sums(r) += A(i,r) * A(i,r)));
    //Comp normA = vecR + (lmbda(r) = sqrt(lmbda(r)));

    Comp mmA("Amm", mulA, (Asq(q,r) += A(q,i) * A(i,r)));
    // Hadamard (component-wise) product on RxR square matrices.
    Comp hadB("Bhad", hadR, (Bhp(q,r) = Csq(q,r) * Asq(q,r)));
    // Now the M-P pseudoinverse.
    Comp pinvB("Bpinv", hadR, Binv(q,r) = one / Bhp(q,r)); //pinv(Bhp));
    Comp krpB("Bkrp", krp, (Bkr(j,r) += X(m) * C(k,r) * A(i,r)));
    Comp mmBp("Bpmm", pmmB, (B(j,q) += Bkr(j,r) * Binv(q,r)));
    // Norm B columns and store in \vec{\lambda}
    Comp ssqB("Bssq", mtxB, (sums(r) += B(j,r) * B(j,r)));
    //Comp normB = vecR + (lmbda(r) = sqrt(lmbda(r)));

    // Hadamard (component-wise) product on RxR square matrices.
    Comp hadC("Chad", hadR, (Chp(q,r) = Bsq(q,r) * Asq(q,r)));
    // Now the M-P pseudoinverse.
    Comp pinvC("Cpinv", hadR, Cinv(q,r) = one / Chp(q,r)); //pinv(Chp));
    Comp krpC("Ckrp", krp, (Ckr(k,r) += X(m) * B(j,r) * A(i,r)));
    Comp mmCp("Cpmm", pmmC, (C(k,q) += Ckr(k,r) * Cinv(r,r)));
    // Norm C columns and store in \vec{\lambda}
    Comp ssqC("Cssq", mtxC, (sums(r) += C(k,r) * C(k,r)));
    Comp norm("norm", vecR, (lmbda(r) = sqrt(sums(r))));

    print("out/cp_als.json");
    string result = codegen("out/cp_als.h");

    //cerr << result << endl;
    ASSERT_TRUE(!result.empty());
}

TEST(eDSLTest, SGeMM) {
    // C(i,j) = C(i,j) * beta + alpha * A(i,k) * B(k,j)
//    for (i = 0; i < N; i++) {
//        for (j = 0; j < M; j++) {
//            C[i][j] *= beta;
//            for (k = 0; k < K; k++)
//                C[i][j] += alpha * A[i][k] * B[k][j];
//        }
//    }

    Iter i('i'), j('j'), k('k');
    Const N('N'), M('M'), P('P');
    Space A("A", N, P), B("B", P, M), C("C", N, M), D("D", N, M);
    Space a("a"), b("b");

    auto sub = a * A(i,k);
    init("sgemm");
    Comp init("init", (0 <= i < N ^ 0 <= j < M), (C(i,j) *= b));
    Comp gemm("gemm", (0 <= i < N ^ 0 <= j < M ^ 0 <= k < P), (C(i,j) += a * A(i,k) * B(k,j)));

    // This makes an excellent opportunity to implement fusion!
    pdfg::fuse(init, gemm);
    print("out/sgemm.json");
    string result = codegen("out/sgemm.o");
    //cerr << result << endl;
    ASSERT_TRUE(!result.empty());
}

TEST(eDSLTest, SDDMM) {
    // A(i,j) = B(i,j) * C(i,k) * D(k,j)
    // A=B*CD, wher
    //
    //
    //
    // e A and B are sparse matrices, C and D are dense matrices, * denotes component-wise multiplication
//    int A1_pos = A.d1.pos[0];
//    int A2_pos = A.d2.pos[A1_pos];
//    for (int B1_pos = B.d1.pos[0]; B1_pos < B.d1.pos[1]; B1_pos++) {
//        int iB = B.d1.idx[B1_pos];
//        for (int B2_pos = B.d2.pos[B1_pos]; B2_pos < B.d2.pos[B1_pos + 1]; B2_pos++) {
//            int jB = B.d2.idx[B2_pos];
//            for (int kC = 0; kC < K; kC++) {
//                int C2_pos = (iB * I) + kC;
//                int D2_pos = (jB * J) + kC;
//                A_val[A2_pos] += (B.vals[B2_pos] * C.vals[C2_pos]) * D.vals[D2_pos];
//            }
//            A2_pos++;
//        }
//        if (A.d2.pos[A1_pos + 1] > A.d2.pos[A1_pos]) {
//            A1_pos++;
//        }
//    }

    Iter i('i'), j('j'), k('k');
    Const I('I'), J('J'), K('K');
    Space sddm("sddm", 0 <= i < I ^ 0 <= j < J ^ 0 <= k < K);
    Space A("A", I, J), B("B", I, J), C("C", I, K), D("D", K, J);

    init("sddm");
    Comp comp = sddm + (A(i,j) += B(i,j) * C(i,k) * D(k,j));
    print("out/sddm.json");
    string result = codegen("out/sddm.o");
    //cerr << result << endl;
    ASSERT_TRUE(!result.empty());
}

TEST(eDSLTest, CSR_ELL_Insp) {
    Iter i('i'), j('j'), k('k'), n('n');
    Const N("N"), NNZ("NNZ"), K("K");
    Func rp("rp"), row("row"), col("col"), ecol("ecol");
    Space csr("Icsr", 0 <= i < N ^ rp(i) <= n < rp(i+1) ^ j==col(n));
    Space ell("Iell", 0 <= i < N ^ 0 <= k < K ^ j==ecol(i,k));

    // CSR->COO Inspector:
    init("csr_ell_insp");
    Space insp("kmax", 0 <= i < N ^ rp(i) <= n < rp(i+1) ^ k==n-rp(i) ^ j==col(n));
    Comp kmax = insp + (K=max(k,K));
    Math asn = (ecol(i,k)=j+0);
    kmax += asn;
    cerr << kmax << endl;

    string result = Codegen().gen(ell);
    string expected = "for(t1 = 0; t1 <= N-1; t1++) {\n  for(t2 = 0; t2 <= K-1; t2++) {\n    t3=ecol(t1,t2);\n    s0(t1,t2,t3);\n  }\n}\n";
    //cerr << result << endl;
    ASSERT_EQ(result, expected);
}

TEST(eDSLTest, CSR_COO_Insp) {
    Iter i("i"), j("j"), n("n");
    Const N("N"), NNZ("NNZ");
    Func rp("rp"), row("row"), col("col");
    Space csr("Icsr", 0 <= i < N ^ rp(i) <= n < rp(i+1) ^ j==col(n));

    // CSR->COO Inspector:
    init("csr_coo_insp");
    //Comp insp_cnt = csr + (NNZ+=1);
    Space snnz("nnz");
    Comp insp_nnz = snnz + (NNZ=rp(N)+0);
    Space insp("coal", 0 <= i < N ^ rp(i) <= n < rp(i+1));
    Comp insp_row = insp + (row(n)=i+0);
    string result = codegen();
    //cerr << result << endl;
    string expected = "#include <stdio.h>\n"
                      "#include <stdlib.h>\n"
                      "#include <stdint.h>\n"
                      "#include <sys/time.h>\n\n"
                      "#define min(x,y) (((x)<(y))?(x):(y))\n"
                      "#define max(x,y) (((x)>(y))?(x):(y))\n"
                      "#define floord(x,y) ((x)/(y))\n"
                      "#define offset2(i,j,M) ((j)+(i)*(M))\n"
                      "#define offset3(i,j,k,M,N) ((k)+((j)+(i)*(M))*(N))\n"
                      "#define offset4(i,j,k,l,M,N,P) ((l)+((k)+((j)+(i)*(M))*(N))*(P))\n"
                      "#define arrinit(ptr,val,size) for(unsigned __i__=0;__i__<(size);__i__++) (ptr)[__i__]=(val)\n\n"
                      "void csr_coo_insp(const unsigned N, const unsigned* rp, unsigned* NNZ, unsigned* row);\n"
                      "inline void csr_coo_insp(const unsigned N, const unsigned* rp, unsigned* NNZ, unsigned* row) {\n\n"
                      "#undef s0\n"
                      "#define s0() NNZ=rp(N)\n\n"
                      "s0();\n\n"
                      "#define rp(i) rp[(i)]\n"
                      "#define rp1(i) rp[(i+1)]\n\n"
                      "#undef s0\n"
                      "#define s0(i,n) row((n))=(i)\n\n"
                      "unsigned t1,t2;\n"
                      "for(t1 = 0; t1 <= N-1; t1++) {\n"
                      "  for(t2 = rp(t1); t2 <= rp1(t1)-1; t2++) {\n"
                      "    s0(t1,t2);\n"
                      "  }\n"
                      "}\n"
                      "\n"
                      "}    // csr_coo_insp\n";
    ASSERT_EQ(result, expected);
}

TEST(eDSLTest, CSR_BSR_Insp) {
    Iter i('i'), j('j'), n('n');
    Const N("N"), M("M"), NNZ("NNZ"), NB("NB");
    Const R("R", 8), C("C", 8);
    Iter b("b"), ii("ii"), jj("jj"), ri("ri"), cj("cj");
    Func rp("rp"), col("col"), bp("bp"), bcol("bcol"); //, min("min", 2);
    Space icsr("Icsr", 0 <= i < N ^ rp(i) <= n < rp(i+1) ^ j==col(n));
    Space val("val", NNZ), x("x", N), y("y", N), bval("bval"); //, NB, R, C);
    Comp csr = icsr + (y[i] += val[n] * x[j]);
    cerr << csr << endl;

    Space ibsr("Ibsr", 0 <= ii < N/R ^ bp(ii) <= b < bp(ii+1) ^ jj==bcol(b) ^ 0 <= ri < R ^ 0 <= cj < C ^ i==ii*R+ri ^ j==jj*C+cj);
    Comp bsr = ibsr + (y[i] += bval(b,ri,cj) * x[j]);
    cerr << bsr << endl;
    string result = Codegen().gen(bsr);
    cerr << result << endl;

    Comp count = csr + (NB += 1);
    result = count.tile(i, R, ii);
    //Space insp("Iin", 0 <= ii < N/R ^ ii*R <= i < R*ii+R ^ rp(i) <= n < rp(i+1) ^ j==col(n));
    cerr << result << endl;
    result = Codegen("").gen(result);
    cerr << result << endl;

    // make-dense 1st:
    result = csr.make_dense(0 <= j < M);
    cerr << result << endl;
    result = csr.tile(i, j, R, C, ii, jj);
    cerr << result << endl;

    ASSERT_TRUE(!result.empty());
}