//
// Created by edavis on 3/21/19.
//

#ifndef POLYEXT_ITERGRAPH_HPP
#define POLYEXT_ITERGRAPH_HPP

#include <iostream>
#include <map>
#include <string>
#include <vector>
#include <utility>

using std::ostream;
using std::map;
using std::string;
using std::vector;
using std::pair;
using std::make_pair;

typedef pair<string, string> Pair;

namespace pdfg {
    class IterGraph {
        friend ostream& operator<<(ostream& out, IterGraph& g) {
            out << "\"" << g._name << "\": { ";
            for (auto itr = g._nodes.begin(); itr != g._nodes.end(); ++itr) {
                string src = itr->first;
                int16_t ndx = itr->second;
                out << "\"" << src << "\": { ";
                for (Pair e : g._edges[ndx]) {
                    string dest = e.first;
                    string label = e.second;
                    out << "(\"" << dest << "\", \"" << label << "\"), ";
                }
                out << " } ";
            }
            out << "}";
            return out;
        }

    public:
        explicit IterGraph(const string& name = "", const unsigned size = 0) {
            _name = name;
            _edges.resize(size);
        }

        void add(const string& dest, const string& label) {
            add(_name, dest, label);
        }

        void add(const string& src, const string& dest, const string& label) {
            auto itr = _nodes.find(src);
            int16_t ndx = -1;
            if (itr == _nodes.end()) {
                ndx = _nodes.size();
                _nodes[src] = ndx;
            } else {
                ndx = itr->second;
            }
            _edges[ndx].push_back(make_pair(dest, label));
        }

    private:
        string _name;
        vector<vector<Pair>> _edges;
        map<string, int16_t> _nodes;
    };
}

#endif //POLYEXT_ITERGRAPH_HPP
