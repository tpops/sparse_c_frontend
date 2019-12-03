#include <stdio.h>
// main calls average via a function pointer.
int average(int a, int b) {
  int c = a + b;
  int d = c / 2;
  return d;
}

int main() {
  int (*avgPtr)(int, int) = &average;

  int a = 7;
  int b = 40;

  int result = (*avgPtr)(a, b);

  printf("%d\n", result);

  return 0;
}
