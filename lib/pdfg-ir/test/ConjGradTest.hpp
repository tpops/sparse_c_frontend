#ifndef _CONJGRADTEST_HPP_
#define _CONJGRADTEST_HPP_

#include <string>
using std::string;
using std::to_string;
#include <gtest/gtest.h>
using namespace testing;

#include <Eigen/Sparse>
#include <Eigen/SparseExtra>
#include <Eigen/IterativeLinearSolvers>
using Eigen::VectorXd;
using Eigen::SparseMatrix;
using Eigen::ConjugateGradient;
using Eigen::Lower;
using Eigen::Upper;
typedef Eigen::Triplet<double> Triple;

#include <util/MatrixIO.hpp>
using util::MatrixIO;
//#include "BenchmarkTest.hpp"
#include "InspExecTest.hpp"

namespace test {
    class ConjGradTest : public InspExecTest { //BenchmarkTest {

    protected:
        ConjGradTest(const string& name = "ConjGradTest") : InspExecTest(name) {
        }

        virtual ~ConjGradTest() {}

        virtual void SetUp(initializer_list<string> args) {
            // Read matrix file
            string filename = *args.begin();
            MatrixIO mtx(filename);
            mtx.read();

            _nnz = mtx.nnz();
            _nrow = mtx.nrows();
            _ncol = mtx.ncols();

            _maxiter = 500;
            _niter = _niter_ref = 0;
            _tolerance = 1e-10;
            _error = 1.0;

            // Copy arrays...
            unsigned nbytes = _nnz * sizeof(unsigned);
            _rows = (unsigned*) malloc(nbytes);
            memcpy(_rows, mtx.rows(), nbytes);
            _cols = (unsigned*) malloc(nbytes);
            memcpy(_cols, mtx.cols(), nbytes);

            nbytes = _nnz * sizeof(double);
            _vals = (double*) malloc(nbytes);
            memcpy(_vals, mtx.vals(), nbytes);

            // Initialize Eigen objects:
            _cg.setMaxIterations(_maxiter);
            _cg.setTolerance(_tolerance);

            vector<Triple> triples;
            triples.reserve(_nnz);
            for (unsigned n = 0; n < _nnz; n++) {
                triples.push_back(Triple(_rows[n], _cols[n], _vals[n]));
            }

            _Aspm.resize(_nrow, _ncol);
            _Aspm.setFromTriplets(triples.begin(), triples.end());

            _xVec.resize(_ncol);
            _bVec.resize(_nrow);

            _x = (double*) calloc(_ncol, sizeof(double));
            _b = (double*) malloc(_nrow * sizeof(double));

            // Initialize b to something more interesting than 0
            for (unsigned i = 0; i < _nrow; i++) {
                _b[i] = 1.0; //(double) (i + 1);
                _bVec(i) = _b[i];
            }
        }

        virtual void Inspect() {}

        virtual void Evaluate() {
            _cg.compute(_Aspm);
            _xVec = _cg.solve(_bVec);
            _niter_ref = _cg.iterations();
            _err_ref = _cg.error();
            _x_ref = _xVec.data();
        }

        virtual void Assert() {
            ASSERT_EQ(_niter, _niter_ref);
            ASSERT_LT(Compare(_x, _x_ref, _ncol), 0);
            ASSERT_LT(Compare(&_error, &_err_ref, 1), 0);
        }

        virtual void TearDown() {
            free(_rows);
            free(_cols);
            free(_vals);
            free(_x);
            free(_b);
        }

        unsigned _nnz, _nrow, _ncol, _maxiter;
        unsigned _niter, _niter_ref;
        unsigned* _rows;
        unsigned* _cols;

        double _error, _err_ref, _tolerance;
        double* _vals;
        double* _x;
        double* _b;
        const double* _x_ref;
        const double* _b_ref;

        // Eigen Objects:
        VectorXd _xVec, _bVec;
        SparseMatrix<double> _Aspm;
        //ConjugateGradient<SparseMatrix<double>> _cg;
        ConjugateGradient<SparseMatrix<double>, Lower|Upper> _cg;
    };
}

#endif // _CONJGRADTEST_HPP_
