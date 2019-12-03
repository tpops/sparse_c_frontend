//
// Created by edavis on 6/18/19.
//

#ifndef _PAPI_HPP_
#define _PAPI_HPP_

#include <iostream>
using std::cerr;
using std::cout;
using std::endl;
#include <map>
using std::map;
#include <string>
using std::string;
#include <vector>
using std::vector;
#include <papi.h>

namespace util {
class PAPI {
public:
    explicit PAPI() {
        _eventSet = PAPI_NULL;
        _event = 0x0;
        _num_events = 0;
    }

    int init() {
        /* Initialize the PAPI library */
        int retval = PAPI_library_init(PAPI_VER_CURRENT);
        if (retval > 0 && retval != PAPI_VER_CURRENT) {
            error("Library version mismatch", retval);
        } else {
            retval = PAPI_create_eventset(&_eventSet);
            if (retval != PAPI_OK) {
                error("Create EventSet", retval);
            } else {
                _num_events = PAPI_num_counters();
                if (_num_events < _papi_count) {
                    error("PAPI hardware counters not supported");
                } else {
                    for (int i = 0; i < _papi_count; i++) {
                        add(_papi_events[i]);
                    }
                }
            }
        }
        return retval;
    }

    void error(const string& errstr, int code = PAPI_OK) {
        cerr << "[ PAPI-ERR ] " << errstr;
        if (code != PAPI_OK) {
            cerr << ": " << PAPI_strerror(code);
        }
        cerr << endl;
    }

    int add(int event) {
        int retval = PAPI_add_event(_eventSet, event);
        if (retval != PAPI_OK) {
            error("Add event " + to_string(event), retval);
        } else {
            _event_codes.push_back(event);
        }
        return retval;
    }

    int add(const string& name) {
        int event;
        int retval = PAPI_event_name_to_code(name.c_str(), &event);
        if (retval != PAPI_OK) {
            error("Add event " + name, retval);
        } else {
            retval = add(event);
        }
        return retval;
    }

    int start() {
        if (_num_events < 1) {
            init();
        }

        //int retval = PAPI_start_counters(_papi_events, _papi_count);
        int retval = PAPI_start(_eventSet);
        if (retval != PAPI_OK) {
            error("Counter start failed", retval);
        }

        return retval;
    }

    int stop() {
        long_long* values = (long_long*) calloc(_event_codes.size(), sizeof(long_long));
        //int retval = PAPI_stop_counters(_papi_values, _papi_count);
        int retval = PAPI_stop(_eventSet, values);
        if (retval != PAPI_OK) {
            error("Counter stop failed", retval);
        } else {
            char event_name[50];
            for (int i = 0; i < _event_codes.size(); i++) {
                retval = PAPI_event_code_to_name(_event_codes[i], event_name);
                if (retval == PAPI_OK) {
                    _papi_data[string(event_name)] = values[i];
                }
            }
        }
        return retval;
    }

    void report() {
        for (const auto& iter : _papi_data) {
            cout << iter.first << " = " << iter.second << endl;
        }
    }

private:
    bool _initialized;

    int _event;
    int _eventSet;

    // PAPI Events
    const int _papi_count = 7;
    int _papi_events[7] = {PAPI_L1_DCM, PAPI_L2_DCM, PAPI_PRF_DM, // PAPI_CA_SHR, PAPI_CA_CLN };
                           PAPI_SP_OPS, PAPI_DP_OPS, PAPI_VEC_SP, PAPI_VEC_DP};
    int _num_events;

    // PAPI Values
    map<string, long_long> _papi_data;
    vector<int> _event_codes;
};
}

#endif // _PAPI_HPP_
