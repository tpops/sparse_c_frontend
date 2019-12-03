#include "InspExecTest.hpp"
#include "ConjGradTest.hpp"
// Include generated code:
#include "coo_csr_insp.h"
#include "conjgrad_csr.h"

namespace test {
class ConjGradCSRTest : public ConjGradTest {

protected:
    ConjGradCSRTest() : ConjGradTest("ConjGradCSRTest") {
        _rowptr = nullptr;
    }

    virtual ~ConjGradCSRTest() {
        if (_rowptr != nullptr) {
            free(_rowptr);
        }
    }

    virtual void Inspect() {
        // Run COO->CSR Inspector!
        _rowptr = (unsigned*) calloc(_nrow + 1, sizeof(unsigned));
        coo_csr_insp(_nnz, _rows, _rowptr);
    }

    virtual void Execute() {
        unsigned nbytes = _nrow * sizeof(double);
        double* r = (double*) malloc(nbytes);
        double* d = (double*) malloc(nbytes);

        // copy
        memcpy(r, _b, nbytes);
        memcpy(d, r, nbytes);

        // conjgrad
        unsigned t = 0;
        //for (; t < _maxiter && _error > _tolerance; t++) {
        for (; t < _maxiter; t++) {
            _error = conjgrad_csr(_vals, _nrow, _cols, _rowptr, d, r, _x);
        }
        _niter = t;

        free(r);
        free(d);
    }

    virtual void Evaluate() {
// TODO: Call ConjGradCOOTest::Execute.
    }

    unsigned* _rowptr;
};

TEST_F(ConjGradCSRTest, CG) {
    ConjGradTest::SetUp({"./data/matrix/cant.mtx"});
    ConjGradTest::Run();
    ConjGradTest::Verify();
    ConjGradTest::Assert();
    int stop = 1;
}
}
