#include <stdio.h>
// main calls outerFunc, which calls the global funcPtr, changes funcPtr via
// innerFunc, and then calls funcPtr again.

int average(int a, int b) {
  int c = a + b;
  int d = c / 2;
  return d;
}

int sub(int a, int b) {
  int c = a - b;
  return c;
}

int (*funcPtr)(int, int) = &average;

void innerFunc(void) { funcPtr = &sub; }

int outerFunc(int a, int b) {
  int c = (*funcPtr)(a, b);
  innerFunc();
  int d = (*funcPtr)(a, b);
  int result = c + d;
  return result;
}

int main() {
  int (*func)(int, int) = &outerFunc;

  int a = 7;
  int b = 40;

  int result = (*func)(a, b);

  printf("%d\n", result);

  return 0;
}
