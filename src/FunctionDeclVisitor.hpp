#include "ScopDetectionVisitor.hpp"
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
#ifndef PDFG_VISITOR
#define PDFG_VISITOR
using namespace clang::tooling;
using namespace clang;
using namespace std;
using namespace llvm;
class ScopBuilder;
namespace pdfg_c {

class PDFGVisitor : public RecursiveASTVisitor<PDFGVisitor> {
private:
  ASTContext *Context;
  Rewriter rewriter;
  std::stack<ForStmt *> ForStmtScope;
  std::shared_ptr<ScopBuilder> builder;
  ScopDetectionVisitor visit;

public:
  explicit PDFGVisitor(ASTContext *Context,
                       std::shared_ptr<ScopBuilder> builder)
      : Context(Context),
        rewriter(Context->getSourceManager(), Context->getLangOpts()),
        builder(builder), visit(Context, builder) {}
  bool VisitFunctionDecl(clang::FunctionDecl *Decl) {
    llvm::outs() << "Currently in Function" << Decl->getName()
                 << "\n"; // this part visibly work
    if (Decl->hasBody()) {
      llvm::outs() << "Has Body, trying to visit it\n";
      builder->getDeclarationScope().push(Decl);
      visit.Visit(Decl);
      builder->getDeclarationScope().pop();
    }
    // return false to prevent the visitor
    // from going deeper
    return false;
  }
}
}; // namespace pdfg_c
}
#endif
