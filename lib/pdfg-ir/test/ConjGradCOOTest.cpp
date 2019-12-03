#include "InspExecTest.hpp"
#include "ConjGradTest.hpp"
// Include generated code:
#include "conjgrad_coo.h"

namespace test {
class ConjGradCOOTest : public ConjGradTest {

protected:
    ConjGradCOOTest() : ConjGradTest("ConjGradCOOTest") {
        _inspFlag = false;          // No inspector needed on this one.
    }

    virtual void Execute() {
        double* r = (double*) malloc(_nrow*sizeof(double));
        double* d = (double*) malloc(_nrow*sizeof(double));

        // copy
        for (unsigned i = 0; i < _nrow; i++) {
            r[i] = d[i] = _b[i];
        }

        // conjgrad
        unsigned t = 0;
        //for (; t < _maxiter && _error > _tolerance; t++) {
        for (; t < _maxiter; t++) {
            _error = conj_grad(_vals, _nnz, _nrow, _cols, _rows, d, r, _x);
        }

        free(r);
        free(d);

        _niter = t;
    }
};

TEST_F(ConjGradCOOTest, CG) {
    SetUp({"./data/matrix/cant.mtx"});
    //SetUp({"./data/matrix/cg.mtx"});
    Run();
    Verify();
    Assert();
    int stop = 1;
}
}