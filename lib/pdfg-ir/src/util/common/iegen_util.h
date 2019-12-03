#ifndef _IEGEN_UTIL_
#define _IEGEN_UTIL_

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/time.h>

// #define _NEW_ARGS(T, ...) T ## _init(malloc(sizeof(T)), __VA_ARGS__)
// #define _NEW_STRUCT(T) T ## _init(malloc(sizeof(T)))
// #define NEW_STRUCT(...) IF_1_ELSE(__VA_ARGS__)(_NEW_STRUCT(__VA_ARGS__))(_NEW_ARGS(__VA_ARGS__))

#define EPS 0.01

#define abs(x) (((x) < 0.0) ? -(x) : (x))
#define offset2(i,j,N) (i)*(N)+(j)
#define offset3(i,j,k,M,N) ((k)+(N)*((j)+(M)*(i)))
#define array_init(ptr,val,size) for(unsigned __i__=0; __i__<(size);__i__++) (ptr)[__i__]=(val)

#define GET_TIME(now) { \
   struct timeval tv; \
   gettimeofday(&tv, NULL); \
   now = tv.tv_sec + tv.tv_usec * 1E-6; \
}

void csr_init(csr_data_t *csr, int nr, int nc, int nnz) {
    csr->N_R = nr;
    csr->N_C = nc;
    csr->NNZ = nnz;

    if (nr > 0 && nnz > 0) {
        csr->index = calloc(nr + 1, sizeof(int));
        csr->col = calloc(nnz, sizeof(int));
        csr->A = calloc(nnz, sizeof(real));
    }
}

void csr_read(const char *fpath, csr_data_t *csr) {
    char buff[1024];
    char temp[64];
    unsigned row, col, nnz = 0;
    real val = 1.0;

    FILE *in = fopen(fpath, "r");

    // Read first line...
    char *ptr = fgets(buff, sizeof(buff), in);
    if (strstr(buff, "Manu_") != NULL) {
        ptr = fgets(buff, sizeof(buff), in);      // Read another...
    }

    sscanf(buff, "%u %u %u\n", &row, &col, &nnz);
    csr_init(csr, row, col, nnz);

    // Read rows...
    unsigned n = 0;
    while (n <= csr->N_R && fgets(buff, sizeof(buff), in) != NULL) {
        if (sscanf(buff, "%s\n", temp) > 0) {
            row = (unsigned) atoi(temp) - 1;
            csr->index[n++] = row;
        }
    }

    // Read cols...
    n = 0;
    while (n < nnz && fgets(buff, sizeof(buff), in) != NULL) {
        if (sscanf(buff, "%s\n", temp) > 0) {
            col = (unsigned) atoi(temp) - 1;
            csr->col[n++] = col;
        }
    }

    // Read vals...
    n = 0;
    while (n < nnz && fgets(buff, sizeof(buff), in) != NULL) {
        if (sscanf(buff, "%s\n", temp) > 0) {
            val = (real) atof(temp);
            csr->A[n++] = val;
        }
    }

    fclose(in);
}

void csr_spmv(csr_data_t const *csr, real const *x, real *y) {
  for (unsigned i = 0; i < csr->N_R; i++) {
        #pragma ivdep
        for (unsigned j = csr->index[i]; j < csr->index[i+1]; j++) {
            unsigned k = csr->col[j];
            y[i] += csr->A[j] * x[k];
        }
    }
}

int csr_bsr_verify(csr_data_t const *csr, bsr_data_t const *bsr, real const *x, real const *y) {
    real* restrict y2 = calloc(csr->N_R, sizeof(real));
    csr_spmv(csr, x, y2);

    for (unsigned i = 0; i < csr->N_R; i++) {
        if (abs((y2[i] - y[i])/y2[i]) >= EPS) {
            fprintf(stderr, "Values don't match at %u, expected %f obtained %f\n", i, y2[i], y[i]);
            return i;
        }
    }

    return -1;
} // csr_bsr_verify

#endif
