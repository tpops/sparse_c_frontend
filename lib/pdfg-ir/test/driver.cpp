#include <cassert>
#include <gtest/gtest.h>
using namespace testing;

int main(int argc, char **argv) {
    InitGoogleTest(&argc, argv);
    // Parse own command line args after GTest parses its args.
    return RUN_ALL_TESTS();
}
