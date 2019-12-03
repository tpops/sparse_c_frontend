#include <stdio.h>
// main calls avgCustomOperation via a function pointer. avgCustomOperation
// takes a function pointer as an argument, and calls it.

int square(int a) {
  int b = a * a;
  return b;
}

int divide2(int a) {
  int b = a / 2;
  return b;
}

// returns a function pointer depending on sign of choose
int (*fpFactory(int choose))(int) {
  if (choose > 7) {
    return &square;
  }
  return &divide2;
}

// Takes a function pointer factory, gets two functions based on a and b,
// applies them respectively, and returns the sum
int applyFuncAdd(int a, int b, int (*funcFactory(int))(int)) {
  int (*aFunc)(int) = (*funcFactory)(a);
  int (*bFunc)(int) = (*funcFactory)(b);

  int a2 = (*aFunc)(a);
  int b2 = (*bFunc)(b);

  int sum = a2 + b2;

  return sum;
}

int main() {
  int (*(*func)(int))(int) =
      &fpFactory; // function pointer that takes an int and returns: a function
                  // pointer that takes an int and returns: an int

  int a = 7;
  int b = 40;

  int result = applyFuncAdd(a, b, func);

  printf("%d\n", result);
  return 0;
}
