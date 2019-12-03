#include "PDFGFrontEndAction.hpp"
#include <clang/Tooling/CommonOptionsParser.h>
// declares llvm::cl:: extrhelp
#include "llvm/Support/CommandLine.h"
#include <string>
#include <vector>
using namespace clang::tooling;
using namespace pdfg_c;

// Apply a custom category to all command line options so that they
// they are the only ones displayed

static llvm::cl::OptionCategory MyToolCategory("pdfg-tool options");

// CommonOptionsParser declares HelpMessage with a description of the common
// command-line options related to the compilation database and input files.
// It's nice to have this help message in all tools
static cl::extrahelp CommonHelp(CommonOptionsParser::HelpMessage);

// extra help for inline functionn

static cl::extrahelp
    MoreHelp("\n PDFG standalone tool to generate PDFG-IR from C\n ");

int main(int argc, const char **argv) {
  // commonOptions Parser constructor will parse arguments and create
  // a compilaton database. In case of error it will terminate the program
  CommonOptionsParser OptionsParser(argc, argv, MyToolCategory);

  ClangTool tool(OptionsParser.getCompilations(),
                 OptionsParser.getSourcePathList());

  // The clang tool needs a new frontendaction for each translation unit we run
  // on. Thus, it takes a front end factory as parameter. to create a
  // frontendactionfactory from a given Frontendactiontype, we all
  // newFrontendActionFactory<clang::SyntaxOnlyAction>()
  int result = tool.run(newFrontendActionFactory<PDFGFrontEndAction>().get());

  // print out the rwritten source code

  return 0;
}
