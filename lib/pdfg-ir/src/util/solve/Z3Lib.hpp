#ifndef Z3LIB_HPP
#define Z3LIB_HPP

#include <map>
#include <string>
#include <vector>
#include <z3++.h>

#include <util/Strings.hpp>

#define IN(str,sub) ((str).find((sub)) != string::npos)

using std::map;
using std::string;
using std::vector;
using namespace z3;

namespace {
struct Z3Lib {
private:
    context _ctx;
    map<string, solver> _solvers;

public:
    string add(const string& setstr) {
        solver solve(_ctx);
        map<string, size_t> iters;
        map<string, size_t> funcs;

        vector<string> items = Strings::split(setstr);
        string last;
        string name;
        string constr;
        string iter;
        bool intuple = false;
        bool endtuple = false;
        bool inconstr = false;

        for (unsigned i = 0; i < items.size(); i++) {
            string item = items[i];
            if (item == ":=") {
                name = last;
            } else if (IN(item, '[')) {
                intuple = true;
                item = Strings::replace(item, "[", "");
            } else if (IN(item, ']')) {
                endtuple = true;
            } else if (item == ":") {
                inconstr = true;
                constr = "";
                item = "";
            } else if (iters.find(item) != iters.end()) {
                iter = item;
            } else if (IN(item, '(')) {
                size_t pos = item.find('(');
                string fname = item.substr(0, pos - 1);
                funcs[fname] = funcs.size();
            } else if (item == "&&" || item == "and") {
                int stop = 1;
            }
            if (intuple) {
                item = Strings::replace(item, ",", "");
                iters[item] = iters.size();
                if (endtuple) {
                    intuple = false;
                }
            } else if (inconstr) {
                constr += item;
            }
            last = item;
        }

        return solve.to_smt2();
    }

    short check(const string& name) {
        short result = 0;

        auto itr = _solvers.find(name);
        if (itr != _solvers.end()) {
            solver solve = itr->second;
            switch (solve.check()) {
                case unsat:
                    result = 0;
                    break;
                case sat:
                    result = 1;
                    break;
                case unknown:
                    result = -1;
                    break;
            }
        }

        return result;
    }
};
}


#endif      // Z3LIB_HPP
