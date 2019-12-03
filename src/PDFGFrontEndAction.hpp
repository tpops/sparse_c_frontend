#include "PDFGConsumer.hpp"
#include <clang/AST/ASTConsumer.h>
#include <clang/Frontend/CompilerInstance.h>
#include <clang/Frontend/FrontendAction.h>
#include <clang/Tooling/Tooling.h>
#ifndef PDFG_FRONT_END_ACTION
#define PDFG_FRONT_END_ACTION

namespace pdfg_c {
class PDFGFrontEndAction : public clang::ASTFrontendAction {
public:
  virtual std::unique_ptr<clang::ASTConsumer>
  CreateASTConsumer(clang::CompilerInstance &Compiler, llvm::StringRef InFile) {
    return std::unique_ptr<clang::ASTConsumer>(
        new PDFGConsumer(&Compiler.getASTContext()));
  }
};
} // namespace pdfg_c
#endif
