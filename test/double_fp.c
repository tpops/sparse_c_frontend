#include <stdio.h>
// main calls squareAverage via a function pointer. squareAverage uses a
// function pointer itself.

int average(int a, int b) {
  int c = a + b;
  int d = c / 2;
  return d;
}

int squareAverage(int a, int b) {
  static int (*avg)(int, int) = &average;
  int c = (*avg)(a, b);
  int d = c * c;
  return d;
}

int main() {
  int (*sqrAvg)(int, int) = &squareAverage;

  int a = 7;
  int b = 40;

  int result = (*sqrAvg)(a, b);

  printf("%d\n", result);

  return 0;
}
