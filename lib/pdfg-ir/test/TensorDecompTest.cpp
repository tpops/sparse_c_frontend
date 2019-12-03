#include <string>
using std::string;
using std::to_string;
#include <gtest/gtest.h>
using namespace testing;

#ifdef SPLATT_ENABLED
#include <splatt.h>
#endif

#include <util/MatrixIO.hpp>
using util::MatlabIO;
using util::TensorIO;

#include "BenchmarkTest.hpp"

namespace test {
    class TensorDecompTest : public ::testing::Test {

    protected:
        TensorDecompTest() {}

        virtual ~TensorDecompTest() {}

        void SetUp(const string& filename, const int rank = 10) {
            _rank = rank;

            // Read tensor file
            TensorIO tns(filename, rank);
            tns.read();
            _nnz = tns.nnz();
            _order = tns.order();

            unsigned nbytes = _order * _nnz * sizeof(unsigned);
            _indices = (unsigned*) malloc(nbytes);
            memcpy(_indices, tns.indices(), nbytes);

            nbytes = _order * sizeof(unsigned);
            _dims = (unsigned*) malloc(nbytes);
            memcpy(_dims, tns.dims(), nbytes);

            nbytes = _nnz * sizeof(real);
            _vals = (real*) malloc(nbytes);
            memcpy(_vals, tns.vals(), nbytes);

            // Get file prefix
            string prefix = filename;
            size_t pos = prefix.rfind('.');
            if (pos != string::npos) {
                prefix = prefix.substr(0, pos);
            }
            prefix += "_r" + to_string(_rank) + "_";

            // Lambda is an Rx1 vector.
            string lambda_file = prefix + "lambda.mat";
            MatlabIO lam(lambda_file, rank, 1);
            lam.read();

            // Need to do a copy, 'mat' object will go out of scope.
            nbytes = rank * sizeof(real);
            _lambda = (real*) malloc(nbytes);
            memcpy(_lambda, lam.vals(), nbytes);

            // Read factor matrices
            _factors = (real**) calloc(_order, sizeof(real*));
            for (unsigned d = 0; d < _order; d++) {
                unsigned dim = _dims[d];
                string factor_file = prefix + "mode" + to_string(d+1) + ".mat";
                MatlabIO fac(factor_file, dim, rank);
                fac.read();

                nbytes = dim * rank * sizeof(real);
                _factors[d] = (real*) malloc(nbytes);
                memcpy(_factors[d], fac.vals(), nbytes);
            }
        }

        virtual void TearDown() {
            free(_indices);
            free(_dims);
            free(_vals);
            free(_lambda);

            for (unsigned d = 0; d < _order; d++) {
                free(_factors[d]);
            }
            free(_factors);

            /* cleanup */
//            splatt_free_csf(_tns, _opts);
//            splatt_free_kruskal(&_fac);
//            splatt_free_opts(_opts);
        }

        unsigned _nnz;
        unsigned _rank;
        unsigned _order;
        unsigned* _indices;
        unsigned* _dims;

        real* _vals;
        real* _lambda;
        real** _factors;

//        double* _opts;
//        splatt_idx_t _dim;
//        splatt_csf* _tns;
//        splatt_kruskal _fac;
    };

    TEST_F(TensorDecompTest, SplattCPD) {
        SetUp("../../tensors/matmul_5-5-5.tns", 10);
        /* do the factorization! */
//        int ret = splatt_cpd_als(_tns, _rank, _opts, &_fac);
//
//        /* do some processing */
//        for(splatt_idx_t m = 0; m < _dim; ++m) {
//            /* access factored.lambda and factored.factors[m] */
//        }
    }

    TEST_F(TensorDecompTest, CPD_ALS) {
        SetUp("./data/tensor/matmul_5-5-5.tns", 10);

        int stop = 1;
    }
}
