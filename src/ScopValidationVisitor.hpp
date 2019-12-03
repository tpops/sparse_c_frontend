#include "Scop.hpp"
#include <clang/AST/ASTConsumer.h>
#include <clang/AST/RecursiveASTVisitor.h>
#include <clang/Basic/SourceLocation.h>
#include <clang/Frontend/CompilerInstance.h>
#include <clang/Frontend/FrontendAction.h>
#include <clang/Lex/Lexer.h>
#include <clang/Rewrite/Core/Rewriter.h>
#include <clang/Tooling/Tooling.h>
#include <iterator>
#include <list>
#include <stack>
//#include <pdfg/CodeGen.hpp>
//#include <pdfg/GraphIL.hpp>
//#include <poly/PolyLib.hpp>
#ifndef PDFG_SCOP_DETECT_VISITOR
#define PDFG_SCOP_DETECT_VISITOR

using namespace clang::tooling;
using namespace clang;
using namespace std;
using namespace llvm;
class ScopBuilder;
namespace pdfg_c {

class ScopDetectionVisitor : public RecursiveASTVisitor<ScopDetectionVisitor> {
private:
  ASTContext *Context;
  pdfg_c::Context *_context;

public:
  explicit ScopDetectionVisitor(ASTContext *Context,
                                std::shared_ptr<ScopBuilder> builder)
      : Context(Context),
        rewriter(Context->getSourceManager(), Context->getLangOpts()),
        builder(builder) {}
  bool VisitStmt(clang::Stmt *st) {
    if ((isa<BinaryOperator>(st))) {
      auto binOper = dyn_cast<BinaryOperator>(st);
      // now we wanna check
      // if there is an assignment statment
      // somewhere so we can create a domain for
      // it
      // Getting the list of scops
      // bounding this
      // statement
      // cloning the list of info
      if (binOper->getOpcodeStr() == "=") {
        builder->addStmt(st);
      }
      if (binOp->isEqualityOp() && isa<DeclRefExpr>(binOp->getLHS())) {
        auto lhsDecl = dyn_cast_or_null<DeclRefExpr>(binOp->getLHS());

        if (varIterator->getDecl()->getID() == lhsDecl->getDecl()->getID()) {
          lowerBound = binOp->getRHS();
          if (isa<IntegerLiteral>(binOp->getRHS())) {
            auto intLit = dyn_cast<IntegerLiteral>(binOp->getRHS());
          } else if (isa<DeclRefExpr>(binOp->getRHS())) {
            auto declRef = dyn_cast<DeclRefExpr>(binOp->getRHS());
          } else {
            // right now we support only
            // integer initialization
            // or variable assignment
            // expressions in the init for now
            // is not supported, we can add
            // more affine information later though
            validScop = false;
          }

        } else if (isa<DeclStmt>(st) && !builder->getLoopInfoScope()->empty()) {

          builder->addStmt(st);
        }

        return true;
      }
    };
  }
#endif
