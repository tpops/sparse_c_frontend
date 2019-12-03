
void compute(int *B2_pos, int *B2_crd) {
  int A[12];
  int B[12];
  int M = 12;
  int N = 13;
  int C[12];
  for ( int i = 0; i < M; i++) {
    for (int pB = B2_pos[i]; pB < B2_pos[i + 1]; pB++) {
      int j = B2_crd[pB];
      int pC = i * N + j;
      int pA = i * N + j;
      A[pA] = B[pB] * C[pC];
    }
  }
}
