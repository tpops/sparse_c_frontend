#include <stdio.h>
// main calls avgCustomOperation via a function pointer. avgCustomOperation
// takes a function pointer as an argument, and calls it.

int average(int a, int b) {
  int c = a + b;
  int d = c / 2;
  return d;
}

int avgCustomOperation(int a, int b, int (*fp)(int)) {
  static int (*avg)(int, int) = &average;

  int c = (*avg)(a, b);
  int d = (*fp)(c);
  return d;
}

int square(int a) {
  int b = a * a;
  return b;
}

int divide2(int a) {
  int b = a / 2;
  return b;
}

int main() {
  int (*sqr)(int) = &square;
  int (*div2)(int) = &divide2;

  int (*avgCustOp)(int, int, int (*)(int)) = &avgCustomOperation;

  int a = 7;
  int b = 40;

  int result1 = (*avgCustOp)(a, b, sqr);
  int result2 = (*avgCustOp)(a, b, div2);

  printf("%d\n", result1);
  printf("%d\n", result2);

  return 0;
}
