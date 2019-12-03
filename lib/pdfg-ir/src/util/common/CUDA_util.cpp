/*****************************************************************************
 *
 * This file contains functions that are used in CUDA benchmarks
 *
*****************************************************************************/

#include <stdio.h>
#include <stdlib.h>
#include <cuda_runtime.h>

#include "CUDA_util.h"

/*****************************************************************************
 * 
 * gpuAssert() Function 
 *
 * This function is used for error checking
 * 
*****************************************************************************/
void gpuAssert(cudaError_t code, const char *file, int line, bool abort){
  if (code != cudaSuccess){
      fprintf(stderr,"GPUassert: %s %s %d\n",
          cudaGetErrorString(code), file, line);
      if (abort) exit(code);
   }
}
