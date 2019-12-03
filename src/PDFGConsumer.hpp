#include "Scop.hpp"
#include "ScopDetectionVisitor.hpp"
#include <clang/AST/ASTConsumer.h>
#include <clang/AST/RecursiveASTVisitor.h>
#include <clang/Frontend/CompilerInstance.h>
#include <clang/Frontend/FrontendAction.h>
#include <clang/Tooling/Tooling.h>
#ifndef PDFG_CONSUMER
#define PDFG_CONSUMER
namespace pdfg_c {
class ScopDetectionVisitor;
class FVisitor;
class PDFGConsumer : public clang::ASTConsumer {
public:
  explicit PDFGConsumer(ASTContext *Context) {
    builder = std::make_shared<pdfg_c::ScopBuilder>(Context);
    //    Visitor = PDFGVisitor(context,builder);
    fVisit = FVisitor(Context, builder);
  }

  // virtual bool HandleTopLevelDecl(DeclGroupRef DG){
  // a DeclGroupRef may have
  // multile Decls, so we iterate through each one
  //        for(DeclGroupRef::iterator i =
  //          DG.begin(), e=DG.end();i!=e; i++){
  // Decl *D=*i;
  //             fVisit.TraverseDecl(D);
  //        }
  //  return true;
  //     }
  virtual void HandleTranslationUnit(ASTContext &ctx) {

    fVisit.TraverseDecl(ctx.getTranslationUnitDecl());
    builder->genPolyComponents();
    builder->print();
    // TODO: create a class that would visit each
    // context and generate sets from them.
  }

private:
  FVisitor fVisit;
  std::shared_ptr<ScopBuilder> builder;
};

} // namespace pdfg_c
#endif
