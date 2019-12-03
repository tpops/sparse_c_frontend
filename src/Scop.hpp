#include "clang/Lex/Lexer.h"
#include <algorithm>
#include <assert.h>
#include <clang/AST/ASTContext.h>
#include <clang/AST/Decl.h>
#include <clang/AST/RecursiveASTVisitor.h>
#include <clang/AST/Stmt.h>
#include <clang/Basic/SourceLocation.h>
#include <iterator>
#include <list>
#include <llvm/ADT/APInt.h>
#include <llvm/ADT/StringRef.h>
#include <map>
#ifndef PDFG_SCOP
#define PDFG_SCOP
namespace pdfg_c {
template <class T> const T &max(const T &a, const T &b) {
  return (a < b) ? b : a;
}

template <class T> constexpr void append(T &a, const T &b) {
  a.insert(a.end(), b.begin(), b.end());
}
class Context;
class Stmt;
class Access;
class Schedule;
class Domain;
class Var;
class IntVar;
class IDVar;
struct Scop {
  enum IncType { UNARY, BINARY };
  enum ScopType { SINGLE, LOOP };
  IncType incType;
  std::list<clang::DeclRefExpr *> varIterators;
  bool needsVarValidation = false;
  clang::FunctionDecl *functionDecl;
  clang::Stmt *stmt;
  pdfg_c::Var *lowerBound;
  clang::Expr *condExpr;
  clang::Stmt *initStmt;
  pdfg_c::Var *condBound;
  llvm::APInt lb;
  int scheduleInfoId;
  ScopType scopType;
  Scop() {
    this->needsVarValidation = false;
    this->functionDecl = NULL;
    this->stmt = NULL;
    this->condExpr = NULL;
    this->scheduleInfoId = -1;
    this->scopType = LOOP;
    this->lowerBound = NULL;
  }
};

/**
 * Context Class has information
 * about the code section currently
 * been manipulated
 */
class Context {
private:
  pdfg_c::Scop *scop;
  llvm::StringRef name;
  clang::SourceRange range;
  bool isValid;
  int contextID;
  std::list<pdfg_c::Stmt *> statements;

public:
  Context(pdfg_c::Scop *scop, const clang::SourceRange &range, bool isValid,
          int contextID)
      : scop(scop), range(range), isValid(isValid), contextID(contextID) {}
  ~Context() {
    for (auto s : statements)
      delete s;
  }
  int getContextID() { return contextID; }
  void setValid(bool isValid) { this->isValid = isValid; }
  bool getValid() { return this->isValid; }
  std::list<pdfg_c::Stmt *> getStatements() { return statements; }
  void addStmt(pdfg_c::Stmt *stmt) { this->statements.push_back(stmt); }
  clang::SourceRange getSourceRange() const { return this->range; }
};
class Var {
public:
  virtual std::string getString() = 0;
};
class IntVar : public Var {
private:
  int value;

public:
  IntVar(int value) : value(value) {}
  std::string getString() override { return std::to_string(value); }
};
class IDVar : public Var {
private:
  /*We would put the */
  std::string id;

public:
  IDVar(std::string id) : id(id) {}
  std::string getString() override { return id; }
};

class DataMap {};
class Access {
private:
  llvm::StringRef name;
};
class Schedule {

private:
  llvm::StringRef name;
  std::list<pdfg_c::Var *> tuple;

public:
  void insertIntoTuple(pdfg_c::Var *var) { tuple.push_back(var); }
  int getLength() { return tuple.size(); }
  std::string getString() const {
    std::string res = "[";
    int i = 0;
    for (auto var : tuple) {
      res += (i++ != 0 ? "," : "") + var->getString();
    }
    res += "]";
    return res;
  }
};
class Domain {
private:
  llvm::StringRef name;
  std::list<pdfg_c::Var *> tuple;
  std::list<pdfg_c::Var *> constraints;
  std::list<pdfg_c::Var *> externs;

public:
  void insertIntoTuple(pdfg_c::Var *var) { tuple.push_back(var); }
  void insertIntoConstraints(pdfg_c::Var *var) { constraints.push_back(var); }
  void insertIntoExterns(pdfg_c::Var *var) { externs.push_back(var); }
  int getLength() { return tuple.size(); }
  bool hasIter() { return getLength() != 0; }
  bool hasExterns() { return externs.size() != 0; }
  std::string getString() const {
    std::string res = "[";
    int i = 0;
    for (auto var : tuple) {
      res += (i++ != 0 ? "," : "") + var->getString();
    }
    res += "]";
    return res;
  }
  std::string getExterns() const {
    std::string res = "[";
    int i = 0;
    for (auto var : externs) {
      res += (i++ != 0 ? "," : "") + var->getString();
    }
    res += "]";
    return res;
  }

  std::string getConstraintString() const {
    std::string res = "";
    int i = 0;
    for (auto var : constraints) {
      res += " " + var->getString() + " ";
    }
    res += "";
    return res;
  }
};
class Stmt {
private:
  llvm::StringRef name;
  pdfg_c::Domain *iterDomain;
  pdfg_c::Schedule *schedule;
  pdfg_c::Access access;
  pdfg_c::Context *context;
  pdfg_c::DataMap dataMap;
  std::list<pdfg_c::Scop *> sorroundingScops;
  clang::Stmt *stmt;
  int stmtID;

public:
  Stmt(clang::Stmt *stmt, std::list<pdfg_c::Scop *> &sorroundingScops,
       pdfg_c::Context *context, int stmtID)
      : stmt(stmt), sorroundingScops(sorroundingScops), context(context),
        stmtID(stmtID) {
    schedule = new pdfg_c::Schedule();
    iterDomain = new pdfg_c::Domain();
  }
  int getSorroundingScopsCount() { return sorroundingScops.size(); }
  clang::Stmt *getStatement() { return this->stmt; }
  std::list<pdfg_c::Scop *> getSorroundingScops() { return sorroundingScops; }
  int getStmtID() { return stmtID; }
  pdfg_c::Schedule *getSchedule() { return schedule; }
  pdfg_c::Domain *getIterDomain() { return iterDomain; }
  pdfg_c::Context *getContext() { return context; }
  bool hasContext() { return context != NULL; }
};
/*
 * This class visits the extracted
 * conditions and generates a constraints
 * */
class Func {
private:
  clang::FunctionDecl *func;
  std::list<pdfg_c::Stmt *> stmts;
  std::string funcName;

public:
  Func(clang::FunctionDecl *func, std::string funcName)
      : func(func), funcName(funcName) {}
  void add_stmt(pdfg_c::Stmt *stmt) { stmts.push_back(stmt); }
  std::list<pdfg_c::Stmt *> &getStmts() { return stmts; }
};

class PolyGenerator {
private:
  std::list<pdfg_c::Stmt *> stmts;

public:
  explicit PolyGenerator(std::list<pdfg_c::Stmt *> stmts) : stmts(stmts) {}
};
/**
 * Visitor to look for external
 * variables in conditions
 * and initializers
 */
// TODO: Try to make the extern visitor ignore
// array identifiers

class FindExternVisitor : public clang::RecursiveASTVisitor<FindExternVisitor> {
  std::list<pdfg_c::Var *> externs;
  std::list<clang::Stmt *> excludeList;
  std::list<clang::DeclRefExpr*>iterList;
public:
  explicit FindExternVisitor(std::list<clang::DeclRefExpr *> iterList)
  :iterList(iterList){
    for(auto iter:iterList){excludeList.push_back(iter);}
    
    llvm::errs()<< "iterList size "<<iterList.size() << " \n" ;
  }
  std::list<pdfg_c::Var *> getExterns() { return externs; }
  bool VisitStmt(clang::Stmt *st) {

    auto res = std::find(excludeList.begin(), excludeList.end(), st);
    if (res != excludeList.end()) {
      (*res)->dump();
      return true;
    }
    if (llvm::isa<clang::ArraySubscriptExpr>(st)) {
      auto arrExpr = llvm::dyn_cast<clang::ArraySubscriptExpr>(st);
      if (llvm::isa<clang::ImplicitCastExpr>(arrExpr->getBase())){
        auto declRefExpr = 
		(llvm::dyn_cast<clang::ImplicitCastExpr>(arrExpr->getBase()))
		->getSubExpr();

        excludeList.push_back(declRefExpr);
      }
    }
    else
    if (llvm::isa<clang::DeclRefExpr>(st)) {
      auto declE = llvm::dyn_cast<clang::DeclRefExpr>(st);
      bool found= false;
      for(auto iter:iterList){
        found = (iter->getDecl()->getID() == declE->getDecl()->getID());
      }
      if (!found){
         
	 externs.push_back(
              new pdfg_c::IDVar(declE->getNameInfo().getAsString()));
      }
    }
    return true;
  }
};

class ScopBuilder {
private:
  clang::ASTContext *context;
  pdfg_c::Context *currentContext;
  std::list<Scop *> *scopScope;
  std::list<pdfg_c::Context *> contexts;
  std::list<pdfg_c::Stmt *> stmts;
  int scopID;
  int stmtID;
  int contextID;
  pdfg_c::Func *currentFunc;
  std::list<pdfg_c::Func *> funcs;
  std::list<clang::Stmt *> visitedScops;
  std::stack<clang::FunctionDecl *> *declarationScope;
  void updateIterationDomain() {
    for (auto f : funcs) {
      for (pdfg_c::Stmt *s : f->getStmts()) {
        if (s->hasContext()) {
          int last = s->getSorroundingScops().size();
	  std::list<clang::DeclRefExpr*> allIter;
	  for (auto scop : s->getSorroundingScops()) {
            last--;
            if (scop->scopType == Scop::LOOP) {
              // get the iteration variable
              pdfg_c::Var *iterationVar = new pdfg_c::IDVar(
                  scop->varIterators.front()->getNameInfo().getAsString());

              // now we push all the information into the tuple
              s->getIterDomain()->insertIntoTuple(iterationVar);
              // inserting lower bound
              if (scop->lowerBound) {
                s->getIterDomain()->insertIntoConstraints(scop->lowerBound);
                s->getIterDomain()->insertIntoConstraints(
                    new pdfg_c::IDVar("<="));
                s->getIterDomain()->insertIntoConstraints(iterationVar);

                if (scop->condBound) {

                  s->getIterDomain()->insertIntoConstraints(
                      new pdfg_c::IDVar("and"));

                  s->getIterDomain()->insertIntoConstraints(scop->condBound);
                }

                if (last != 0) {
                  s->getIterDomain()->insertIntoConstraints(
                      new pdfg_c::IDVar("and"));
                }
              }
	      pdfg_c::append(allIter,scop->varIterators);
            }
          }
	  // this is to extract all
	  // external vvariables from 
	  // the conditions and intializtion
          for(auto scop:s->getSorroundingScops()){
	   
	     FindExternVisitor visit(allIter);
             if (scop->initStmt) {
               visit.TraverseStmt(scop->initStmt);
             }
             if (scop->condExpr) {
               visit.TraverseStmt(scop->condExpr);
             }
             // for every loop invariant
             // externals coming in from
             // outside the loop
             for (auto ext : visit.getExterns()) {
               s->getIterDomain()->insertIntoExterns(ext);
             }
	  }
	}

      }
    }
  }
  void updateScheduling() {
    // go through all func
    for (auto f : funcs) {

      int scheduleNo = 0;
      int highestLength = 0;
      std::map<pdfg_c::Scop *, int> scopScheduleMap;
      for (pdfg_c::Stmt *s : f->getStmts()) {
        if (!s->hasContext()) {
          pdfg_c::Var *var = new pdfg_c::IntVar(scheduleNo++);
          s->getSchedule()->insertIntoTuple(var);
        } else {
          // try to get its position in the context
          pdfg_c::Scop *prevScop = NULL;
          for (auto scop : s->getSorroundingScops()) {
            // SCOP that has single effect such
            // as if stmts, switch statements
            // are not included in the execution
            // schedule definition
            // they are only included as constraints
            // to the data or iteration domain
            if (scop->scopType == Scop::LOOP) {

              auto it = scopScheduleMap.find(scop);
              if (it == scopScheduleMap.end()) {
                // this gives us the number
                // for current sibling of Scop
                // int var = ++scopScheduleMap[scop];
                scopScheduleMap[scop] = 0;
              }

              // this shows that this scop
              // scheduleInfoId has not been
              // entered
              if (scop->scheduleInfoId == -1) {
                // we need to give the current
                // scop a position
                scop->scheduleInfoId =
                    (prevScop ? scopScheduleMap[prevScop]++ : scheduleNo++);
              }
              pdfg_c::Var *scopSchedule =
                  new pdfg_c::IntVar(scop->scheduleInfoId);
              // sibling schedule holds information
              // about current statements's position
              // in the SCOP
              // get the iteration variable
              pdfg_c::Var *iterationVar = new pdfg_c::IDVar(
                  scop->varIterators.front()->getNameInfo().getAsString());

              // now we push all the information into the tuple
              s->getSchedule()->insertIntoTuple(scopSchedule);
              s->getSchedule()->insertIntoTuple(iterationVar);
              prevScop = scop;
            }
          }
          // this gives the final schedule
          // location of the current statement
          // in question
          pdfg_c::Var *siblingSchedule =
              new pdfg_c::IntVar(scopScheduleMap[prevScop]++);

          s->getSchedule()->insertIntoTuple(siblingSchedule);
        }
        highestLength = max<int>(highestLength, s->getSchedule()->getLength());
      }
      // now that we have filled up our scheduling lets
      // modify scheduling and fill up the rest with zeros
      for (pdfg_c::Stmt *s : f->getStmts()) {
        for (int k = s->getSchedule()->getLength(); k <= highestLength; k++) {

          pdfg_c::Var *var = new pdfg_c::IntVar(0);
          s->getSchedule()->insertIntoTuple(var);
        }
      }
    }
  }

public:
  ScopBuilder(clang::ASTContext *context) : context(context) {
    scopID = 0;
    contextID = 0;
    stmtID = 0;
    currentContext = NULL;

    declarationScope = new std::stack<clang::FunctionDecl *>();
    scopScope = new std::list<pdfg_c::Scop *>();
  }
  std::list<pdfg_c::Scop *> *getScopScope() { return scopScope; }
  /**
   * called when entering a function
   * body
   * */
  void enterFunctionDeclaration(clang::FunctionDecl *func) {
    contextID = 0;
    declarationScope->push(func);
    currentFunc = new pdfg_c::Func(func, func->getDeclName().getAsString());
    funcs.push_back(currentFunc);
  }
  void exitFunctionDeclaration() {
    declarationScope->pop();
    currentFunc = NULL;
  }
  std::stack<clang::FunctionDecl *> *getDeclarationScope() {
    return declarationScope;
  }
  bool scopVisited(clang::Stmt *stmt) {
    std::list<clang::Stmt *>::iterator it;
    it = std::find(visitedScops.begin(), visitedScops.end(), stmt);
    return it != visitedScops.end();
  }
  std::list<clang::Stmt *> &getVisitedScops() { return visitedScops; }
  void print() {
    llvm::errs() << "\nC Front END Summary \n\n"
                 << "Located about " << contexts.size() << " contexts\n";
    for (auto c : contexts) {
      llvm::errs() << "[" << c->getValid() << "]"
                   << "Context-> Contains " << c->getStatements().size()
                   << " Statements \n";
      for (auto s : c->getStatements()) {
        llvm::StringRef state = clang::Lexer::getSourceText(
            clang::CharSourceRange::getTokenRange(
                s->getStatement()->getSourceRange()),
            context->getSourceManager(), context->getLangOpts());
        llvm::errs() << "Statement->" << state << "\n";
        llvm::errs() << s->getSorroundingScopsCount()
                     << " Sorrounding scops \n";
      }
    }
    llvm::outs() << "\n\n";
    llvm::errs() << "<--========================================-->\n\n";
    // print statements
    for (auto f : funcs) {
      for (auto sts : f->getStmts()) {

        llvm::StringRef stmtString = clang::Lexer::getSourceText(
            clang::CharSourceRange::getTokenRange(
                sts->getStatement()->getSourceRange()),
            context->getSourceManager(), context->getLangOpts());
        llvm::outs() << "S" << std::to_string(sts->getStmtID()) << ":"
                     << stmtString << "\n";
      }
    }

    llvm::outs() << "\n\n";

    // print Iteration Space
    for (auto f : funcs) {
      for (auto sts : f->getStmts()) {
        if (sts->getIterDomain()->hasIter()) {
          llvm::outs() << "S" << std::to_string(sts->getStmtID())
                       << ": "
                       /* <<(sts->getIterDomain()->hasExterns()?sts->
                                        getIterDomain()->getExterns() + " -> ":
                                        " ")*/
                       << " {" << sts->getIterDomain()->getString() << ": "
                       << sts->getIterDomain()->getConstraintString() << " }\n";
        } else {

          llvm::outs() << "S" << std::to_string(sts->getStmtID())
                       << ":  {[]}\n";
        }
      }
    }

    llvm::outs() << "\n\n";

    // print scheduling
    for (auto f : funcs) {
      for (auto sts : f->getStmts()) {
        llvm::outs() << "S" << std::to_string(sts->getStmtID()) << ":  {"
                     << sts->getIterDomain()->getString() << "->"
                     << sts->getSchedule()->getString() << "}\n";
      }
    }
    llvm::outs() << "\n\n";
  }
  void sanitizeContexts() {
    for (auto c : contexts)
      if (!c->getValid()) {
        //   contexts.remove(c);
        //   delete c;
      }
  }
  /**
   *Clears context in builder
   */
  void clearContext() { currentContext = NULL; }
  /**
   * creates new context to be
   * used
   */
  void createNewContext(const clang::SourceRange &sourceRange, Scop *info) {
    contextID++;
    currentContext = new pdfg_c::Context(info, sourceRange, true, contextID);
    contexts.push_back(currentContext);
  }

  void validateCurrentContext(bool isValid) {
    assert(currentContext != NULL && "Current context should be non null\n");
    currentContext->setValid(isValid);
  }
  void addStmt(clang::Stmt *stmt) {
    // context must not be null
    auto clonedList = std::list<pdfg_c::Scop *>(*scopScope);
    // currently haven't worked on

    // assert(currentContext!=NULL);
    pdfg_c::Stmt *s =
        new pdfg_c::Stmt(stmt, clonedList, currentContext, stmtID++);
    if (currentContext != NULL) {
      currentContext->addStmt(s);
    }
    currentFunc->add_stmt(s);
  }

  void genPolyComponents() {
    llvm::errs() << "\nUpdating Iteration Domain Information-->\n";
    updateIterationDomain();
    llvm::errs() << "\nUpdating Scheduling Information-->\n";
    updateScheduling();
  }
};

} // namespace pdfg_c
#endif
