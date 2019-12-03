#define NULL 0

int sumList(int *numbers, int len) {
  int nSum = 0;

  for (int i = 0; i < len; i++) {
    nSum = numbers[i];
    numbers[i] = numbers[i - 1] + nSum;
    for (int j = 0; j < len; j++) {
      numbers[j + 1] = numbers[j + 1];
      numbers[j] = numbers[j - 1];
      for (int k = 0; k < j; k++) {
        numbers[k] = nSum + numbers[j];
      }
      numbers[j] = numbers[j + 1];
    }
  }
  int A[2999];
  int B[12];
  int kl = 12;
  for (int i = 0; i < len; i++) {
    nSum = numbers[i];
    numbers[i] = numbers[i - 1] + nSum;
    for (int j = B[A[i]]; j < len; j++) {
      numbers[j + 1] = numbers[j + 1];
      numbers[j] = numbers[j - 1];
      for (int k = 0; k < j; k++) {
        numbers[k] = nSum + numbers[j];
      }
      numbers[j] = numbers[j + 1];
    }
  }
  int kt = 12;
  kt += 12;
  kl -= 10;
  return nSum;
}
