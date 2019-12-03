//
// Created by edavis on 6/22/19.
//

#ifndef _INSPEXECTEST_HPP_
#define _INSPEXECTEST_HPP_

#include "BenchmarkTest.hpp"

namespace test {
class InspExecTest : public BenchmarkTest {
public:
    double InspTime() const {
        return _inspTime;
    }

protected:
    InspExecTest(const string& name = "") : BenchmarkTest(name) {
        _inspTime = 0.0;
        _inspFlag = true;
    }

    virtual void Inspect() = 0;

    virtual void Run() {
        if (_inspFlag) {
            _inspTime = Now();
            Inspect();
            _inspTime = Now() - _inspTime;
        }
        BenchmarkTest::Run();
    }

    virtual void Verify() {
        if (_inspTime > 0.0) {
            GTEST_COUT << "InspTime = " << _inspTime << endl;
        }
        BenchmarkTest::Verify();
    }

    bool _inspFlag;
    double _inspTime;
};
}

#endif //_INSPEXECTEST_HPP_
