#ifndef _BENCHMARKTEST_HPP_
#define _BENCHMARKTEST_HPP_

#include <initializer_list>
using std::initializer_list;
#include <map>
using std::map;
#include <string>
using std::string;
using std::to_string;
#include <iostream>
using std::cerr;
using std::cout;
using std::endl;
#include <vector>
using std::vector;
#include <sys/time.h>
#include <gtest/gtest.h>
using namespace testing;

#ifdef _OPENMP
#include <omp.h>
#else
#define omp_get_thread_num() 0
#define omp_get_max_threads() 1
#define omp_get_num_threads() 1
#define omp_set_num_threads(n) n=n
#endif

#include <util/LIKWID.hpp>
//#define PAPI_ON 1
#ifdef PAPI_ON
#include <util/PAPI.hpp>
using util::PAPI;
#endif

#include <util/Strings.hpp>

#ifndef EPSILON
#define EPSILON 0.001
#endif

#define GTEST_COUT cout << "[   INFO   ] "
#define GTEST_CERR cerr << "[  ERROR   ] "

namespace test {
    class BenchmarkTest : public ::testing::Test {
    public:
        double EvalTime() const {
            return _evalTime;
        }

        double RunTime() const {
            return _runTime;
        }

        unsigned NumRuns() const {
            return _nRuns;
        }

        void NumRuns(unsigned nRuns) {
            _nRuns = nRuns;
        }

        double Speedup() const {
            double p = _runTime;
            double s = _evalTime;
            double r = 0.0;
            //double n = (double) GetNumThreads();

            // Amdahl's Law:
            if (s != 0.0) {
                r = (1.0 / (1.0 - p + (p/s)));
            }

            return r;
        }

        virtual int MaxThreads() const {
            return omp_get_max_threads();
        }

        virtual int NumThreads() const {
            return omp_get_num_threads();
        }

        virtual bool NumThreads(int nThreads) {
            bool result = false;
            if (nThreads > omp_get_max_threads()) {
                cerr << "--num_threads cannot be more than \n" << omp_get_max_threads();
            } else if (nThreads < 1) {
                cerr << "--num_threads cannot be less than 1\n";
            } else {
                omp_set_num_threads(nThreads);
                result = true;
                _nThreads = nThreads;
            }
            return result;
        }

    protected:
        BenchmarkTest(const string& name = "", unsigned nRuns = 1, unsigned nThreads = 1) : _name(name), _nRuns(nRuns) {
            NumThreads(nThreads);
        }

        virtual ~BenchmarkTest() {}

        virtual void SetUp(initializer_list<string> args) {
            unsigned argc = args.size();
            vector<string> argv(args.begin(), args.end());

            string key, val;
            for (unsigned i = 0; i < argc; i++) {
                string arg = argv[i];
                if (arg[0] == '-') {
                    key = Strings::ltrim(arg);
                } else {
                    val = arg;
                }
                if (!key.empty()) {
                    _args[key] = val;
                    key = "";
                }
            }
        }

        void Start() noexcept {
            _runTime = 0.0;
            _startTime = Now();
        }

        void Stop() noexcept {
            _stopTime = Now();
            _runTime = (_stopTime - _startTime);
        }

        double Now() {
            struct timeval tv;
            gettimeofday(&tv, NULL);
            return (double) tv.tv_sec + (((double) tv.tv_usec) * 1E-6);
        }

        virtual void Execute() = 0;

        virtual void Run() {
            double  timeSum = 0.0;
            for (unsigned i = 0; i < _nRuns; i++) {
#ifdef PAPI_ON
                _papi.start();
#endif
                LIKWID_MARKER_INIT;
                Start();
                LIKWID_MARKER_START("BenchmarkTest");
                Execute();
                LIKWID_MARKER_STOP("BenchmarkTest");
                Stop();
                LIKWID_MARKER_CLOSE;
#ifdef PAPI_ON
                _papi.stop();
#endif
                timeSum += _runTime;
            }
            _runTime = timeSum / (double) _nRuns;
        }

        virtual void Evaluate() = 0;

        virtual void Verify() {
            double saveTime = _runTime;
            double  timeSum = 0.0;
            for (unsigned i = 0; i < _nRuns; i++) {
                Start();
                Evaluate();
                Stop();
                timeSum += _runTime;
            }
            _evalTime = timeSum / (double) _nRuns;
            _runTime = saveTime;

            GTEST_COUT << "RunTime(" << _nRuns << ") = " << _runTime << ", EvalTime = " << _evalTime
                       << ", Ratio = " << _evalTime / _runTime << endl;
#ifdef PAPI_ON
            _papi.report();
#endif
        }

        virtual void Assert() {};

        virtual int Compare(const double* testData, const double* refData, unsigned size, double eps = EPSILON) {
            int index = -1;
            for (unsigned i = 0; i < size && index < 0; i++) {
                //if (abs((testData[i] - refData[i])/refData[i]) >= eps) {
                if (abs(testData[i] - refData[i]) >= eps) {
                    index = i;
                    GTEST_CERR << "Found " << testData[i] << ", Expected " << refData[i] << ", Position " << i << endl;
                }
            }
            return index;
        }

        template <typename T>
        static inline void Write(const vector<T>& elems, const char delim = ',') {
            Write(cerr, elems, delim);
        }

        template <typename T>
        static inline void Write(const string& file, const vector<T>& elems, const char delim = ',') {
            ofstream ofs(file.c_str());
            Write(ofs, elems, delim);
        }

        template <typename T>
        static inline void Write(ostream& os, const vector<T>& elems, const char delim = ',') {
            unsigned endpos = elems.size() - 1;
            for (unsigned i = 0; i <= endpos; i++) {
                os << elems[i];
                if (i < endpos) {
                    os << delim;
                }
            }
            os << endl;
        }

        string _name;

        unsigned _nRuns;
        unsigned _nThreads;

        double _startTime;
        double _stopTime;
        double _runTime;
        double _evalTime;

        map<string, string> _args;
#ifdef PAPI_ON
        PAPI _papi;
#endif

    };
}


#endif
