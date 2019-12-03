/*****************************************************************************
 *
 * This file contains function headers and related macros for debugging 
 * purposes in CUDA benchmarks
 *
*****************************************************************************/

/*****************************************************************************
 *  These macros:
 *
 *  #define gpuErrchk(ans)
 *
 *  #define gpuErrchkSync(ans)
 *
******************************************************************************/
#define gpuErrchk(ans) { gpuAssert((ans), __FILE__, __LINE__); }

#ifdef CUDADEBUG
#define gpuErrchkSync(ans) { gpuAssert((ans), __FILE__, __LINE__); }
#else
#define gpuErrchkSync(ans)
#endif

/*****************************************************************************
 * 
 * The function headers
 * 
*****************************************************************************/
void gpuAssert(cudaError_t code, const char *file, int line, bool abort=true);
