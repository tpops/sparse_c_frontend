void foo() {
  for (int i = 0; i < 8; i++) {
    int j = i * i;
  }
}
int main(int argc, char **argv) {
  int i;
  int A[20];
  for (i = 0; i < 10 && 4 < 10; i++) {
    A[i] = 5 * A[i + 1];
    for (int j = 0; j < 10; j++) {
      int y = i + j;
      j = 10;
    }
  }

  for (i = 10; i < 12; i++) {
    int k = i;
    i = 3;
  }
}
