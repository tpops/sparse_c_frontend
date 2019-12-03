//
// Created by edavis on 3/21/19.
//
#pragma once
#ifndef POLYEXT_CODEGEN_HPP
#define POLYEXT_CODEGEN_HPP

#include <poly/PolyLib.hpp>
using poly::PolyLib;
#include <pdfg/GraphIL.hpp>

namespace pdfg {
    struct Codegen {
    public:
        explicit Codegen(const string& ompSched = "auto", const string& iterType = "unsigned") :
                _iterType(iterType), _ompSched(ompSched) {
        }

        string norm(const Space& space) {
            return _poly.add(space.to_iegen());
        }

        string gen(const Comp& comp) {
            vector<string> guards;
            for (const auto& guard : comp.guards()) {
                guards.push_back(stringify<Constr>(guard));
            }

            vector<string> statements;
            for (const auto& stmt : comp.statements()) {
                statements.push_back(stringify<Math>(stmt));
            }

            vector<string> schedules;
            for (const auto& schedule : comp.schedules()) {
                schedules.push_back(schedule.to_iegen());
            }

            string iegstr = Strings::replace(comp.space().to_iegen(), "N/8", "N_R");
            string norm = _poly.add(iegstr);
            string code = _poly.codegen(comp.space().name(), _iterType, _ompSched, true, statements, guards, schedules);
            return code;
        }

        string gen(const Space& space) {
            string norm = _poly.add(space.to_iegen());
            string code = _poly.codegen(space.name());
            return code;
        }

        string gen(const string& setstr) {
            string setname;
            size_t pos = setstr.find(":=");
            if (pos != string::npos) {
                setname = setstr.substr(0, pos - 1);
            }
            return _poly.codegen(setstr, setname, true);
        }

    protected:
        PolyLib _poly;
        string _iterType;
        string _ompSched;
    };
}

#endif //POLYEXT_CODEGEN_HPP
