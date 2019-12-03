/**
 * \class DFGVisitor
 *
 * \ingroup PolyExt
 * (Note, this needs exactly one \defgroup somewhere)
 *
 * \brief Polyhedral Dataflow Graph Visitor
 *
 * C++ implementation of polyhedral dataflow graphs (PDFGs).
 *
 * \author Eddie Davis
 * \version $Revision: 0.1 $
 * \date $Date: 2018/12/03
 * Contact: eddiedavis@boisestate.edu
 */

#ifndef POLYEXT_VISITOR_H
#define POLYEXT_VISITOR_H

#include <pdfg/GraphIL.hpp>
#include <util/OS.hpp>
using util::OS;

namespace pdfg {
    struct DFGVisitor {
    public:
        virtual void visit(Node* node) {
            enter(node);
            exit(node);
        }

        virtual void enter(Node *node) {
            cerr << "Visiting node '" << node->label() << "'" << endl;
            switch (node->type()) {
                case 'D':
                    enter((DataNode *) node);
                    break;
                case 'C':
                    enter((CompNode *) node);
                    break;
                case 'R':
                    enter((RelNode *) node);
                    break;
                default:    // Throw exception, maybe?
                    break;
            }
        }

        virtual void enter(CompNode*) {}

        virtual void enter(DataNode*) {}

        virtual void exit(Node*) {}

        virtual void finish(FlowGraph* graph) {}

        virtual void setup(FlowGraph* graph) {
            _graph = graph;
        }

        virtual void walk(FlowGraph* graph) {
            setup(graph);
            for (Node* node : graph->nodes()) {
                visit(node);        //node->accept(this);
            }
//          for i in range(g.nrows):
//            for j in range(g.ncols):
//              if (i, j) in g:
//                node = g[(i, j)]
//                node.accept(self)
            finish(graph);
        }

    protected:
        FlowGraph* _graph;
    };

    struct CodeGenVisitor: DFGVisitor {
    public:
        explicit CodeGenVisitor(const string &path = "", const string &lang = "C", bool profile = false, unsigned niters = 5) :
                _path(path), _niters(niters), _lang(lang), _profile(profile) {
            init();
        }

        void include(const initializer_list<string> &libraries) {
            for (const string &library : libraries) {
                include(library);
            }
        }

        void include(const string &library) {
            _includes.push_back(library);
        }

        void define(const initializer_list<string> &defines) {
            unsigned n = 0;
            string name;
            for (const string &defn : defines) {
                if (n % 2 == 0) {
                    name = defn;
                } else {
                    define(name, defn);
                }
                n += 1;
            }
        }

        void define(const map<string, string>& defines) {
            for (const auto& iter : defines) {
                define(iter.first, iter.second);
            }
        }

        void define(const pair<string, string>& defpair) {
            define(defpair.first, defpair.second);
        }

        void define(const string &name, const string &defn = "") {
            _defines.push_back(make_pair<string, string>(string(name), string(defn)));
        }

        void function(const string &header, const string &body) {
            _functions.push_back(make_pair<string, string>(string(header), string(body)));
        }

        void typdef(const string &type, const string &alias) {
            _typedefs.push_back(make_pair<string, string>(string(type), string(alias)));
        }

        string ompSchedule() const {
            return _ompsched;
        }

        void ompSchedule(const string& schedule) {
            _ompsched = schedule;
        }

        string path() const {
            return _path;
        }

        void path(const string &p) {
            _path = p;
            if (_path.find('/') == string::npos) {
                char cwd[1024];
                getcwd(cwd, sizeof(cwd));
                _path = string(cwd) + '/' + _path;
            }
            if (_path.find('.') == string::npos) {
                _path += "." + string(tolower(_lang[0]), 1);
            }
        }

        vector<string> header() const {
            return _header;
        }

        vector<string> allocs() const {
            return _allocs;
        }

        vector<string> body() const {
            return _body;
        }

        void setup(FlowGraph* graph) override {
            _graph = graph;
            addComment();
            addIncludes();
            addTypeDefs();
            addFunctions();
        }

        void enter(DataNode* node) override {
            string label = node->label();
            string defval = node->defval();
            unsigned tilesize = _graph->tileSize();

            if (!_graph->isReturn(node) && _graph->isSource(node)) {
                // Input Data
                string param = "const " + node->datatype();
                if (!node->is_scalar()) {
                    param += "*";
                }
                param += " " + label;
                _params.push_back(param);
            } else if ((!_graph->isReturn(node) && _graph->isSink(node)) || _graph->output(label) >= 0) {
                // Output Data
                string param = node->datatype() + "* " + label;
                _params.push_back(param);
            } else if (node->alloc() != NONE) {
                // Temporary Data
                ostringstream os;
                os << _indent;
                if (node->is_scalar()) {
                    os << node->datatype() << ' ' << label;
                    if (!defval.empty()) {
                        os << " = " << defval;
                    }
                    os << ';';
                } else if (node->alloc() == DYNAMIC) {
                    os << node->datatype() << "* ";
                    bool isC = (_lang.find("+") == string::npos);
                    if (isC) {
                        os << "restrict ";
                    }
                    os << label << " = ";
                    if (!isC) {
                        os << '(' << node->datatype() << "*) ";
                    }
                    if (defval == "0") {
                        os << "calloc(" << *node->size() << ",sizeof(" << node->datatype() << "));";
                    } else {
                        if (tilesize > 0) {
                            os << "aligned_alloc(" << tilesize << ",(";
                        } else {
                            os << "malloc(";
                        }
                        os << *node->size() << "*sizeof(" << node->datatype() << "));";
                    }
                    _frees.push_back(node->label());
                } else {
                    if (node->alloc() == STATIC) {
                        os << "static ";
                    }
                    os << node->datatype() << ' ' << label << '['
                       << *node->size() << "] = {" << defval << "};";
                }
                string line = os.str();
                _allocs.push_back(line);
                if (node->alloc() == DYNAMIC && !defval.empty() && defval != "0") {
                    os.str(_indent);
                    os << "arrinit(" << label << ',' << defval << ',' << *node->size() << ");";
                    line = os.str();
                    _allocs.push_back(line);
                }
            }
        }

        void enter(CompNode* node) override {
            vector<string> names;
            map<string, vector<string> > guards;
            map<string, vector<string> > statements;
            map<string, vector<string> > schedules;

            updateComp((Comp*) node->expr(), names, statements, guards, schedules);
            addMappings(node);

            for (CompNode* child : node->children()) {
                updateComp((Comp*) child->expr(), names, statements, guards, schedules);
                addMappings(child);
            }

            string code = _poly.codegen(names, statements, guards, schedules, _ompsched, "", true);
            code = "// " + node->label() + "\n" + code;
            _body.push_back(code);
        }

        void enter(RelNode* node) {
            int stop = 4;
        }

        void finish(FlowGraph* graph) override {
            addDefines();
            addHeader();
            addFooter();

            // Undefine macros for the safety of including functions.
            undoDefines();

            if (!_path.empty()) {
                ofstream fout(_path.c_str());
                fout << str() << endl;
                fout.close();
            }

            _graph = nullptr;
        }

        string str() const {
            string out = Strings::join(_header, "\n") + "\n";
            if (!_allocs.empty()) {
                out += Strings::join(_allocs, "\n") + "\n\n";
            }
            out += Strings::join(_body, "\n") + "\n";
            return out;
        }

        friend ostream& operator<<(ostream& os, const CodeGenVisitor& cgen) {
            os << cgen.str();
            return os;
        }

    protected:
        void init() {
            // Add defines...
            define({"min(x,y)", "(((x)<(y))?(x):(y))",
                    "max(x,y)", "(((x)>(y))?(x):(y))",
                    "abs(x)", "((x)<0?-(x):(x))",
                    "absmin(x,y)", "((x)=min(abs((x)),abs((y))))",
                    "absmax(x,y)", "((x)=max(abs((x)),abs((y))))",
                    "floord(x,y)", "((x)/(y))",
                    "sgn(x)", "((x)<0?-1:1)",
                    "offset2(i,j,M)", "((j)+(i)*(M))",
                    "offset3(i,j,k,M,N)", "((k)+((j)+(i)*(M))*(N))",
                    "offset4(i,j,k,l,M,N,P)", "((l)+((k)+((j)+(i)*(M))*(N))*(P))",
                    "arrinit(ptr,val,size)", "for(unsigned __i__=0;__i__<(size);__i__++) (ptr)[__i__]=(val)",
                    "arrprnt(name,arr,size)", "{\\\nfprintf(stderr,\"%s={\",(name));\\\nfor(unsigned __i__=0;__i__<(size);__i__++) fprintf(stderr,\"%lg,\",(arr)[__i__]);\\\nfprintf(stderr,\"}\\n\");}"
                   });

            // Add includes...
            include({"stdio", "stdlib", "stdint", "math"});
            if (_profile) {
                include("sys/time");
            }

            _indent = "    ";
            //_ompsched = "runtime";
        }

        void addComment() {
            _header.push_back("// '" + _graph->name() + "' code generated by '" +
                              OS::username() + "' at " + OS::timestamp());
        }

        void addHeader() {
            string line = _graph->returnType() + " " + _graph->name() + "(";
            unsigned n = 0, nparams = _params.size();
            std::sort(_params.begin(), _params.end());
            for (const string& param : _params) {
                line += param;
                if (n < nparams - 1) {
                    line += ", ";
                } else {
                    line += ")";
                }
                n += 1;
            }
            _header.push_back(line + ";");
            _header.push_back("inline " + line + " {");

            // Define iterators.
            line = _indent + _graph->indexType() + " ";
            for (unsigned i = 1; i < _niters; i++) {
                line += "t" + to_string(i) + ",";
            }
            line += "t" + to_string(_niters) + ";";
            _header.push_back(line);
        }

        void addFooter() {
            string line;
            for (const string& free : _frees) {
                line = _indent + "free(" + free + ");";
                _body.push_back(line);
            }

            if (!_graph->returnName().empty()) {
                line = "\n" + _indent + "return (" + _graph->returnName() + ");";
                _body.push_back(line);      // Return value...
            }

            line = "}" + _indent + "// " + _graph->name();
            _body.push_back(line);      // Close the fxn
        }

        void addIncludes() {
            if (!_includes.empty()) {
                for (string& include : _includes) {
                    if (include.find(".h") == string::npos) {
                        include += ".h";
                    }
                    string line = "#include <" + include + ">";
                    _header.push_back(line);
                }
                _header.emplace_back("");
            }
        }

        void addDefines() {
            for (const auto& itr : _poly.macros()) {
                define(itr);
            }

            if (!_defines.empty()) {
                for (auto& define : _defines) {
                    string line = "#define " + define.first + " " + define.second;
                    _header.push_back(line);
                }
                _header.emplace_back("");
            }
        }

        void addTypeDefs() {
            if (!_typedefs.empty()) {
                for (auto& tdef : _typedefs) {
                    string line = "typedef " + tdef.first + " " + tdef.second + ";";
                    _header.push_back(line);
                }
                _header.emplace_back("");
            }
        }

        void addFunctions() {
            if (!_functions.empty()) {
                for (auto& fxn : _functions) {
                    string line = fxn.first + " { " + fxn.second + " }";
                    if (line.find("inline") == string::npos) {
                        line = "inline " + line;
                    }
                    _header.push_back(line);
                }
                _header.emplace_back("");
            }
        }

        void undoDefines() {
            if (!_defines.empty()) {
                _body.emplace_back("");
                for (auto& define : _defines) {
                    string undef = define.first;
                    size_t pos = undef.find('(');
                    if (pos != string::npos) {
                        undef = undef.substr(0, pos);
                    }
                    string line = "#undef " + undef;
                    _body.push_back(line);
                }
            }
        }

        void updateComp(Comp* comp, vector<string>& names,
                        map<string, vector<string> >& statements,
                        map<string, vector<string> >& guards,
                        map<string, vector<string> >& schedules) {
            //string iegstr = Strings::replace(comp.space().to_iegen(), "N/8", "N_R");
            string iegstr = comp->space().to_iegen();
            string norm = _poly.add(iegstr);
            string sname = comp->space().name();

            names.push_back(sname);
            for (const Constr& guard : comp->guards()) {
                guards[sname].emplace_back(stringify<Constr>(guard));
            }
            for (const Math& statement : comp->statements()) {
                statements[sname].emplace_back(stringify<Math>(statement));
            }
            for (const auto& schedule : comp->schedules()) {
                schedules[sname].push_back(schedule.to_iegen());
            }
        }

        void addMappings(CompNode* node) {
            // Define data mappings (one per space)
            for (Access* access : node->accesses()) {
                if (access->has_iters() && _mappings.find(access->space()) == _mappings.end()) {
                    string mapping = createMapping(access);
                    if (!mapping.empty()) {
                        string accstr = stringify<Access>(*access);
                        define(accstr, mapping);
                        _mappings[access->space()] = mapping;
                    }
                }
            }
        }

        string createMapping(const Access* access) {
            string sname = access->space();
            map<string, int> offsets = access->offset_map();

            Space space = getSpace(sname);
            Tuple tuple = space.iterators();
            unsigned size = tuple.size();

            ostringstream os;
            if (size < 1) {
                os << sname;
            } else if (tuple.at(0).type() != 'N' && access->refchar() != '[') {
                os << sname << '[';
                if (size > 1) {
                    os << "offset" << size << '(';
                }
                for (unsigned i = 0; i < size; i++) {
                    string iter = tuple.at(i).text();
                    os << '(' << iter << ')';
                    auto offset = offsets.find(iter);
                    if (offset != offsets.end() && offset->second != 0) {
                        if (offset->second > 0) {
                            os << '+';
                        }
                        os << offset->second;
                    }
                    if (size > 1) {
                        os << ',';
                    }
                }
                if (size > 1) {
                    vector<Iter> subs(tuple.begin() + 1, tuple.end());
                    string subsize = stringify<Math>(space.slice(1, size - 1).size());
                    subsize = Strings::fixParens(subsize);   // Remove redundant parens...
                    os << Strings::replace(subsize, "*", ",") << ')';
                }
                os << ']';
            }

            return os.str();
        }

        bool _profile;
        unsigned _niters;

        string _indent;
        string _lang;
        string _path;
        string _ompsched;

        map<string, string> _mappings;
        vector<pair<string, string> > _defines;
        vector<pair<string, string> > _typedefs;
        vector<pair<string, string> > _functions;

        vector<string> _includes;
        vector<string> _header;
        vector<string> _params;
        vector<string> _body;
        vector<string> _allocs;
        vector<string> _frees;

        PolyLib _poly;
    };

    struct PerfModelVisitor : public DFGVisitor {
    public:
        explicit PerfModelVisitor() {}

        /// For each computation node, compute the amount of data read (loaded), written (stored), the number
        /// of input and output streams, the number of int ops (IOPs), floating point ops (FLOPs).
        /// This leads to an estimate for the amount of memory traffic (Q) and total work (W).
        /// Arithmetic intensity can be computed as I = W/Q, the x-axis of the Roofline plot.
        /// \param node Computation node
        void enter(CompNode* node) override {
            unsigned inStreamsI = 0, outStreamsI = 0, inStreamsF = 0, outStreamsF = 0, nIOPs = 0, nFLOPs = 0;
            string inSizeExprI, outSizeExprI, inSizeExprF, outSizeExprF;

//            if (node->label() == "smul_d1") {
//                int stop = 1;
//            }

            vector<Edge*> inedges = _graph->inedges(node);
            for (Edge* edge : inedges) {
                if (edge->source()->is_data()) {
                    DataNode* source = (DataNode*) edge->source();
                    if (!source->is_scalar()) {
                        string sizeExpr = "+" + Strings::fixParens(source->size()->text());
                        if (source->is_int()) {
                            inStreamsI += 1;
                            inSizeExprI += sizeExpr;
                        } else {
                            inStreamsF += 1;
                            inSizeExprF += sizeExpr;
                        }
                    }
                }
            }

            if (!inSizeExprI.empty()) {
                inSizeExprI = inSizeExprI.substr(1);
                if (inSizeExprI.find('+') != string::npos) {
                    inSizeExprI = "(" + inSizeExprI + ")";
                }
                inSizeExprI += "*" + to_string(sizeof(int));
                node->attr("isize_in", inSizeExprI);
                node->attr("istreams_in", to_string(inStreamsI));
            }

            if (!inSizeExprF.empty()) {
                inSizeExprF = inSizeExprF.substr(1);
                if (inSizeExprF.find('+') != string::npos) {
                    inSizeExprF = "(" + inSizeExprF + ")";
                }
                inSizeExprF += "*" + to_string(sizeof(double));
                node->attr("fsize_in", inSizeExprF);
                node->attr("fstreams_in", to_string(inStreamsF));
            }

            vector<Edge*> outedges = _graph->outedges(node);
            for (Edge* edge : outedges) {
                DataNode *dest = (DataNode *) edge->dest();
                string sizeExpr;
                if (dest->is_scalar()) {
                    sizeExpr = "1";
                } else {
                    sizeExpr = "+" + Strings::fixParens(dest->size()->text());
                }
                if (dest->is_int()) {
                    outStreamsI += 1;
                    outSizeExprI += sizeExpr;
                } else {
                    outStreamsF += 1;
                    outSizeExprF += sizeExpr;
                }
            }

            if (!outSizeExprI.empty()) {
                outSizeExprI = outSizeExprI.substr(1);
                if (outSizeExprI.find('+') != string::npos) {
                    outSizeExprI = "(" + outSizeExprI + ")";
                }
                outSizeExprI += "*" + to_string(sizeof(int));
                node->attr("isize_out", outSizeExprI);
                node->attr("istreams_out", to_string(outStreamsI));
            }

            if (!outSizeExprF.empty()) {
                outSizeExprF = outSizeExprF.substr(1);
                if (outSizeExprF.find('+') != string::npos) {
                    outSizeExprF = "(" + outSizeExprF + ")";
                }
                outSizeExprF += "*" + to_string(sizeof(double));
                node->attr("fsize_out", outSizeExprF);
                node->attr("fstreams_out", to_string(outStreamsF));
            }

            nIOPs = 1;                  // TODO: count int ops later (maybe), but assume at least one
            nFLOPs = node->flops();     // Count FLOPs...

            node->attr("flops", to_string(nFLOPs));
            node->attr("iops", to_string(nIOPs));
        }
    };

    struct ScheduleVisitor : public DFGVisitor {
    public:
        explicit ScheduleVisitor() {
        }

        /// For each computation node, generate and assign a scheduling (scattering) function.
        /// \param node Computation node
        void enter(CompNode* node) override {
            unsigned i, j, n;
            unsigned level = 0;
            unsigned maxiter = 0;
            vector<Tuple> schedfxns;
            vector<int> offsets;

            // Skip if no fusion for now...
            if (node->children().size() < 1) {
                return;
            }

            Comp* comp = node->comp();

            // 0) Collect current schedules and offsets
            for (const Rel& rel : comp->schedules()) {
                Tuple sched = rel.dest().iterators();
                schedfxns.push_back(sched);
            }
            for (CompNode* child : node->children()) {
                Comp* other = child->comp();
                for (const Rel& rel : other->schedules()) {
                    Tuple sched = rel.dest().iterators();
                    schedfxns.push_back(sched);
                }
            }

            // 1) Calculate maximum # of iterators in tuples.
            unsigned nschedules = schedfxns.size();
            for (i = 0; i < nschedules; i++) {
                unsigned niter = schedfxns[i].size();
                maxiter = (niter > maxiter) ? niter : maxiter;
            }

            // 2) Determine fusion type and calculate maximum offset from each iterator.
            char fuseType = 'S';        // Simple loop-only fusion if no data dependences
            CompNode* prev = node;
            vector<CompNode*> nodes(nschedules, nullptr);
            nodes[0] = node;

            i = 1;
            for (CompNode* child : node->children()) {
//                map<string, Access*> isect = intersect(prev->writes(), child->reads());
//                if (!isect.empty()) {   // P-C Fuse
////                    maxOffsets(schedfxns[n], prev->writes(), offsets);
////                    maxOffsets(schedfxns[n], child->reads(), offsets);
//                    fuseType = 'P';
//                } else {
//                    isect = intersect(prev->reads(), child->reads());
//                    if (!isect.empty()) {   // R-R Fuse
//                        // This might be a don't-care, these are just reads so order should not matter.
////                        maxOffsets(schedfxns[n], prev->reads(), offsets);
////                        maxOffsets(schedfxns[n], child->reads(), offsets);
//                        fuseType = 'R';
//                    } else {
//                        isect = intersect(prev->writes(), child->writes());
//                        if (!isect.empty()) {   // W-W Fuse
//                            // Potential WAW hazard -- how to handle this case? Error?
////                            maxOffsets(schedfxns[n], prev->writes(), offsets);
////                            maxOffsets(schedfxns[n], child->reads(), offsets);
//                            fuseType = 'W';
//                        }
//                    }
//                }
//                prev = child;
                nodes[i++] = child;
            }

            vector<Tuple> newfxns = schedfxns;

            // 3) Find the deepest common level
            int index = -1;
            level = getCommonLevel(newfxns, &index);

            // Handle case w/o common iterators.
            Iter first;
            bool interchange = (level < 1);
            if (interchange) {
                if (newfxns[level].size() > newfxns[index].size()) {
                    index = level;
                }
                first = newfxns[index][0];
                newfxns[index].erase(newfxns[index].begin());
                level = getCommonLevel(newfxns);
            }

            for (i = 0; i < nschedules; i++) {
                if (!newfxns[i][level].is_int()) {
                    newfxns[i].insert(newfxns[i].begin() + level, Iter(i + '0'));
                    if (newfxns[i].size() > maxiter) {
                        newfxns[i].pop_back();
                    }
                }
            }

            // 4) Handle nonzero offsets...
            unsigned group = 0;
            vector<bool> shifted(maxiter, false);
            for (i = 1; i < nschedules; i++) {
                // Check whether offset exists at this level
                map<string, Access*> isect = intersect(nodes[i-1]->writes(), nodes[i]->reads());
                if (!isect.empty()) {
                    maxOffsets(schedfxns[i], nodes[i-1]->writes(), offsets);
                    maxOffsets(schedfxns[i], nodes[i]->reads(), offsets);
                }
                for (n = 0; n < offsets.size(); n++) {
                    if (offsets[n] != 0) {
                        if (!shifted[n]) {
                            // This means insert a tuple here! Or perhaps it means a shift,
                            //   need to determine when shifts are possible.
                            for (j = 0; j < nschedules; j++) {
                                newfxns[j].insert(newfxns[j].begin() + n, Iter(group + '0'));
                            }
                            group += 1;
                            maxiter += 1;
                            shifted[n] = true;
                        }
                        // If dimension is already shifted, just increment the group.
                        for (j = i; j < nschedules; j++) {
                            newfxns[j][n] = Iter(group + '0');
                        }
                        group += 1;
                        offsets[n] = 0;
                    }
                }
            }

            // 5) Increment last tuple item to ensure lexicographic ordering.
            // TODO: Ideally, the last tuple should be in group order, but the generated code should be the same.
            for (unsigned i = 0; i < nschedules; i++) {
                unsigned last = newfxns[i].size() - 1;
                if (newfxns[i][last].is_int()) {
                    newfxns[i][last] = Iter(i + '0');
                }
            }

            if (interchange) {
                newfxns[index].push_back(first);
            }

            // 6) Replace schedules with updated tuples...
            n = 0;
            for (i = 0; i < comp->nschedules(); i++) {
                comp->reschedule(i, newfxns[n]);
                n += 1;
            }
            for (CompNode* child : node->children()) {
                Comp* other = child->comp();
                for (i = 0; i < other->nschedules(); i++) {
                    other->reschedule(i, newfxns[n]);
                    n += 1;
                }
            }
        }

    protected:
        map<string, Access*> intersect(const map<string, Access*> lhs, const map<string, Access*> rhs) const {
            map<string, Access*> isect;
            for (const auto& itr : lhs) {
                auto pos = rhs.find(itr.first);
                if (pos != rhs.end()) {
                    isect[pos->first] = pos->second;
                }
            }
            return isect;
        }

        map<string, ExprTuple> absMaxDist(const map<string, Access*> accmap) const {
            map<string, ExprTuple> distmap;
            map<string, ExprTuple> maxmap;

            // Initialize distances to zero...
            ExprTuple zeros;
            for (const auto& itr : accmap) {
                Access* acc = itr.second;
                string space = acc->space();
                if (distmap.find(space) == distmap.end()) {
                    zeros = ExprTuple(acc->tuple().size(), Int(0));
                    distmap[space] = zeros;
                    ExprTuple tmax(zeros.begin(), zeros.end());
                    maxmap[space] = tmax;
                }
            }

            // Find max delta for each tuple.
            for (const auto& itr : accmap) {
                Access* acc = itr.second;
                string space = acc->space();
                ExprTuple tuple = acc->tuple();
                ExprTuple tmax = maxmap[space];

                ExprTuple diff = abs(tuple - tmax);
                if (distmap[space] < diff) {
                    distmap[space] = diff;
                    maxmap[space] = tuple;
                }
            }

            return distmap;
        }

        void maxOffsets(const Tuple& schedule, const map<string, Access*> accmap, vector<int>& max_offsets) {
            // Size up the max_offsets vector.
            for (unsigned i = 0; i < schedule.size(); i++) {
                if (max_offsets.size() <= i) {
                    max_offsets.push_back(0);
                }

                for (const auto& itr : accmap) {
                    Access *acc = itr.second;
                    string space = acc->space();
                    ExprTuple tuple = acc->tuple();

                    bool match = false;
                    for (unsigned j = 0; j < tuple.size() && !match; j++) {
                        if (!schedule[i].is_int()) {
                            string expr = tuple[j].text();
                            string iter = schedule[i].text();
                            size_t pos = expr.find(iter);
                            match = (pos != string::npos);
                            if (match && expr != iter) {
                                expr.erase(pos, iter.size());
                                int offset = unstring<int>(expr);
                                if (abs(offset) > abs(max_offsets[i])) {
                                    max_offsets[i] = offset;
                                }
                            }
                        }
                    }
                }
            }
        }

        unsigned getCommonLevel(const vector<Tuple>& tuples, int* ndx = nullptr) {
            unsigned i, n, level = 0;
            for (n = 0; n < tuples[0].size(); n++) {
                if (!tuples[0][n].is_int()) {
                    bool match = true;
                    for (i = 1; i < tuples.size() && match; i++) {
                        if (tuples[i].size() < n || !tuples[i][n].equals(tuples[0][n])) {
                            match = false;
                            if (ndx != nullptr) {
                                *ndx = i;
                            }
                        }
                    }
                    if (match) {
                        level = n + 1;
                    }
                }
            }
            return level;
        }
    };

    struct DataReduceVisitor : public DFGVisitor {
    public:
        explicit DataReduceVisitor() {
        }

        void enter(DataNode* node) override {
            vector<Edge*> ins = _graph->inedges(node);
            vector<Edge*> outs = _graph->outedges(node);

            // A node with no incoming edges is an input, and no outgoing is an output, these cannot be reduced.
            unsigned size = ins.size();
            vector<CompNode*> prodNodes(size);
            bool reducible = (size > 0 && size == outs.size());

            if (reducible) {
                for (unsigned i = 0; i < size && reducible; i++) {
                    prodNodes[i] = (CompNode*) ins[i]->source();
                    CompNode* consumer = (CompNode*) outs[i]->dest();
                    reducible = (prodNodes[i]->label() == consumer->label());
                }
            }

            if (reducible) {
                Access nodeAcc = Access::from_str(node->expr()->text());
                IntTuple intTuple = to_int(nodeAcc.tuple());

                //for (CompNode* producer : prodNodes) {
                    CompNode* producer = prodNodes[0];
                    vector<Access*> accesses = producer->accesses(node->label());
                    IntTuple maxTuple(intTuple.size(), 0);
                    for (unsigned i = 0; i < accesses.size(); i++) {
                        IntTuple accTuple = to_int(accesses[i]->tuple());
                        maxTuple = absmax(maxTuple, accTuple);
                    }

                    // Update the data space...
                    Space space = getSpace(node->label());
                    Tuple iters = space.iterators();
                    ConstrTuple constrs = space.constraints();
                    Space newspace(space.name());

                    for (unsigned i = 0; i < maxTuple.size(); i++) {
                        if (maxTuple[i] != 0) {
                            newspace.add(iters[i]);
                            for (const Constr& constr : space.constraints()) {
                                if (constr.lhs().equals(iters[i]) || constr.rhs().equals(iters[i])) {
                                    newspace.add(constr);
                                }
                            }
                        }
                    }

                    newSpace(newspace);
                    Math* resize = (Math*) getSize(*producer->comp(), Func(newspace));
                    node->size(resize);
                //}
            }
        }
    };
}

#endif  // POLYEXT_VISITOR_H
