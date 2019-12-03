//
// Created by edavis on 6/7/17.
//

#include "Benchmark.h"

string& Benchmark::name() {
    return _name;
}

bool Benchmark::valid() {
    return _status;
}

double Benchmark::runTime() {
    return _runTime;
}

void Benchmark::start() {
    struct timeval tval;
    gettimeofday(&tval, NULL);
    _startTime = (double) tval.tv_sec + (((double) tval.tv_usec) / 1000000);
}

void Benchmark::stop() {
    struct timeval tval;
    gettimeofday(&tval, NULL);
    _stopTime = (double) tval.tv_sec + (((double) tval.tv_usec) / 1000000);
}

double Benchmark::speedup() {
    double p = _runTime;
    double s = _evalTime;
    double r = 0.0;
    //double n = (double) _config.getInt("num_threads");

    // Amdahl's Law:
    if (s != 0.0) {
        r = (1.0 / (1.0 - p + (p/s)));
    }

    return r;
}

function<void(DType**, DType**, DType*, Configuration&)>& Benchmark::execFunction() {
    return _execFxn;
}

function<void(DType**, DType**, DType*, Configuration&)>& Benchmark::evalFunction() {
    return _evalFxn;
}

function<bool(DType**, DType**, Configuration&, vector<int>&)> Benchmark::compFunction() {
    return _compFxn;
}

bool Benchmark::setNumThreads(int nThreads) {
    bool status = true;
    if (nThreads > omp_get_max_threads()) {
        cout << "--num_threads cannot be more than \n" << omp_get_max_threads();
        status = false;
    } else if (nThreads < 1) {
        cout << "--num_threads cannot be less than 1\n";
        status = false;
    } else {
        omp_set_num_threads(nThreads);
    }

    return status;
}

void Benchmark::run() {
    init();     // Initialize data...

    if (valid()) {
        // Set number of threads...
        setNumThreads(_config.getInt("num_threads"));

        // Invoke execution function...
        start();    // Start timer...
        _execFxn(_inputData, _outputData, &_runTime, _config);
        stop();     // Stop timer...

        // If execution function did not calculate its own runtime, compute it now...
        if (_runTime == 0.0) {
            _runTime = _stopTime - _startTime;
        }

        _meas.setField("RunTime", _runTime);

        // If verification on, invoke evaluation function...
        if (_verify) {
            start();
            _evalFxn(_inputData, _verifyData, &_evalTime, _config);
            stop();

            // If evaluation function did not calculate its own runtime, compute it now...
            if (_evalTime == 0.0) {
                _evalTime = _stopTime = _startTime;
            }

            // Compare _outputData and _verifyData...
            _status = _compFxn(_outputData, _verifyData, _config, _errorLoc);

            if (_status) {
                _meas.setField("verification", "SUCCESS");
            } else {
                //cout << "Writing to CSV...\n";
                //toCSV();
                _meas.setField("verification", "FAILURE");
            }
        }

        finish();   // Perform cleanup, etc...
    } else {
        cerr << "Benchmark initialization failed!\n";
    }
}

void Benchmark::report() {
    string err = error();
    if (err.size() > 0) {
        cout << err << endl;
    }

    //get results from measurements
    string result = _meas.toLDAPString();
    string config_in = _config.toLDAPString();
    cout << config_in << result << endl;
}
