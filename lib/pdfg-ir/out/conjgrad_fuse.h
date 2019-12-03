#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <math.h>

#define min(x,y) (((x)<(y))?(x):(y))
#define max(x,y) (((x)>(y))?(x):(y))
#define abs(x) ((x)<0?-(x):(x))
#define absmin(x,y) ((x)=min(abs((x)),abs((y))))
#define absmax(x,y) ((x)=max(abs((x)),abs((y))))
#define floord(x,y) ((x)/(y))
#define sgn(x) ((x)<0?-1:1)
#define offset2(i,j,M) ((j)+(i)*(M))
#define offset3(i,j,k,M,N) ((k)+((j)+(i)*(M))*(N))
#define offset4(i,j,k,l,M,N,P) ((l)+((k)+((j)+(i)*(M))*(N))*(P))
#define arrinit(ptr,val,size) for(unsigned __i__=0;__i__<(size);__i__++) (ptr)[__i__]=(val)
#define arrprnt(name,arr,size) {\
fprintf(stderr,"%s={",(name));\
for(unsigned __i__=0;__i__<(size);__i__++) fprintf(stderr,"%lg,",(arr)[__i__]);\
fprintf(stderr,"}\n");}
#define col(i) col[(i)]
#define row(i) row[(i)]
#define rp(i) rp[(i)]

double conj_grad(const unsigned M, const unsigned* row, const unsigned* col, const double* A, const unsigned N, double* d, double* r, double* x);
inline double conj_grad(const unsigned M, const unsigned* row, const unsigned* col, const double* A, const unsigned N, double* d, double* r, double* x) {
    unsigned t1,t2,t3,t4,t5;
    double* s = (double*) calloc((N),sizeof(double));
    double ds = 0;
    double rs0 = 0;
    double alpha = 0;
    double rs = 0;
    double beta = 0;

// spmv
#undef s0
#define s0(n,i,j) s[(i)]+=A[(n)]*d[(j)]

#pragma omp parallel for schedule(auto) private(t1)
for(t1 = 0; t1 <= M-1; t1++) {
  t2=row(t1);
  t3=col(t1);
  s0(t1,t2,t3);
}

// ddot+rdot0
#undef s0
#define s0(i) ds+=d[(i)]*s[(i)]
#undef s1
#define s1(i) rs0+=r[(i)]*r[(i)]

#pragma omp parallel for schedule(auto) private(t1)
for(t1 = 0; t1 <= N-1; t1++) {
  s0(t1);
  s1(t1);
}

// adiv+xadd+rsub+rdot
#undef s0
#define s0() alpha=rs0/ds
#undef s1
#define s1(i) x[(i)]+=alpha*d[(i)]
#undef s2
#define s2(i) r[(i)]-=alpha*s[(i)]
#undef s3
#define s3(i) rs+=r[(i)]*r[(i)]

s0();
#pragma omp parallel for schedule(auto) private(t1)
for(t1 = 0; t1 <= N-1; t1++) {
  s1(t1);
  s2(t1);
  s3(t1);
}

// bdiv+bmul+dadd
#undef s0
#define s0() beta=rs/rs0
#undef s1
#define s1(i) d[(i)]*=beta
#undef s2
#define s2(i) d[(i)]+=r[(i)]

s0();
#pragma omp parallel for schedule(auto) private(t1)
for(t1 = 0; t1 <= N-1; t1++) {
  s1(t1);
  s2(t1);
}

    free(s);

    return (rs);
}    // conj_grad

#undef min
#undef max
#undef abs
#undef absmin
#undef absmax
#undef floord
#undef sgn
#undef offset2
#undef offset3
#undef offset4
#undef arrinit
#undef arrprnt
#undef col
#undef row
#undef rp

