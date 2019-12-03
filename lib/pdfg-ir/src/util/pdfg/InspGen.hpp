//
// Created by edavis on 3/21/19.
//

#ifndef POLYEXT_INSPGEN_HPP
#define POLYEXT_INSPGEN_HPP

#include <iostream>
#include <map>
#include <string>
#include <vector>
#include <unordered_set>
#include <utility>

using std::string;
using std::vector;
using std::unordered_set;

#include <pdfg/GraphIL.hpp>
using namespace pdfg;

#include <util/Strings.hpp>

#define _IN_(elem,coll) ((coll).find((elem))!=(coll).end())
#define _NOTIN_(elem,coll) ((coll).find((elem))==(coll).end())

namespace pdfg {
    class InspGen {
    public:
        InspGen(const Space& source, const Space& dest) {
            _source = source;
            _dest = dest;
        }

        string gen() {
            enumConstraints();
            return genGraph();
        }

    private:
        void enumConstraints() {
            for (const auto& iter : _source.iterators()) {
                _iters.insert(iter.text());
            }
            for (const auto& iter : _dest.iterators()) {
                _iters.insert(iter.text());
            }

            for (const auto& constr : _source.constraints()) {
                _known.insert(constr.text());
            }

            for (const auto& constr : _dest.constraints()) {
                string ctext = constr.text();
                if (_NOTIN_(ctext, _known)) { //_known.find(ctext) == _known.end()) {
                    vector<string> elems = Strings::split(ctext);
                    string lhs = elems[0];
                    string relop = elems[1];
                    string rhs = elems[2];

                    bool hasFunc = false;
                    if (isFunc(lhs)) {
                        _ufuncs.insert(lhs);
                        hasFunc = true;
                    }
                    if (isFunc(rhs)) {
                        _ufuncs.insert(rhs);
                        hasFunc = true;
                    }
                    if (hasFunc) {
                        _unknown.insert(ctext);
                    } else {
                        _known.insert(ctext);
                    }
                }
            }
        }

        inline bool isFunc(const string& elem) {
            return _NOTIN_(elem, _iters) && Strings::digits(elem).empty();
        }

        string genGraph() {
            string code = "";
            while (_unknown.size() > 0) {
                unordered_set<string> ufcons;
                for (const auto& func : _ufuncs) {
                    for (const auto& constr : _unknown) {
                        if (constrains(constr, func)) {
                            ufcons.insert(constr);
                        }
                    }
                    code += createPDFL(ufcons);
                }
                for (const auto& constr : ufcons) {
                    _known.insert(constr);
                    _unknown.erase(constr);
                }
            }

            return code;
        }

        bool constrains(const string& constr, const string& func) {
            return true;
        }

        string createPDFL(const unordered_set<string>& ufcons) {
            string code;

            return code;
        }

        Space _source;
        Space _dest;

        unordered_set<string> _known;
        unordered_set<string> _unknown;
        unordered_set<string> _ufuncs;
        unordered_set<string> _iters;
    };
}

#endif //POLYEXT_INSPGEN_HPP
