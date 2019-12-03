#include "Scop.hpp"
#include <algorithm>
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
#include <string>
//#include <pdfg/CodeGen.hpp>
//#include <pdfg/GraphIL.hpp>
//#include <poly/PolyLib.hpp>
#ifndef PDFG_SCOP_DETECT_VISITOR
#define PDFG_SCOP_DETECT_VISITOR

using namespace clang::tooling;
using namespace clang;
using namespace std;
using namespace llvm;
namespace pdfg_c {
class ScopBuilder;
/**
 * description: This class is useful for looking
 * for lower bounds for iteration variables
 * that do not exist in the Scop information
 * */
class FindIterAssignVisitor
    : public RecursiveASTVisitor<FindIterAssignVisitor> {
  clang::Stmt *lastAssign;
  pdfg_c::Var *lowerBound;
  clang::Stmt *termStmt; /*This is useful cos we dont want to go past
  the looped scop, it is believed the initilization and assignment
  should be done before the loop statement body is called */
  clang::DeclRefExpr *iter;

public:
  explicit FindIterAssignVisitor(clang::DeclRefExpr *iter,
                                 clang::Stmt *termStmt)
      : iter(iter), lastAssign(NULL) {}
  clang::Stmt *getAssignStmt() { return lastAssign; }
  pdfg_c::Var *getlowerBound() { return lowerBound; }
  bool VisitStmt(clang::Stmt *st) {
    if (termStmt == st) {
      return false;
    }
    if ((isa<BinaryOperator>(st))) {
      auto binOper = dyn_cast<BinaryOperator>(st);
      if (binOper->getOpcodeStr() == "=") {
        // let us check if the left side
        // of this operation is a var iterator
        if (isa<DeclRefExpr>(binOper->getLHS())) {
          auto declE = dyn_cast<DeclRefExpr>(binOper->getLHS());
          if (iter->getDecl()->getID() == declE->getDecl()->getID()) {
            if (isa<DeclRefExpr>(binOper->getRHS())) {
              auto declR = dyn_cast<DeclRefExpr>(binOper->getRHS());
              lowerBound =
                  new pdfg_c::IDVar(declR->getNameInfo().getAsString());

            } else if (isa<IntegerLiteral>(binOper->getRHS())) {
              auto intR = dyn_cast<IntegerLiteral>(binOper->getRHS());
              lowerBound =
                  new pdfg_c::IntVar((int)intR->getValue().getLimitedValue());
            }
          }
        }
      }

    } else if (isa<DeclStmt>(st)) {
      auto init = dyn_cast_or_null<DeclStmt>(st);
      // for now we only support
      // single declaration
      if (init->isSingleDecl()) {
        auto decl = init->getSingleDecl();
        if (iter->getDecl()->getID() == decl->getID()) {
          // TODO: Work on a way of
          // finding out the RHS of declare statement
          // so that we can know the initial value
        }
      }
    }
    return true; /*Keep traversing the tree*/
  }
};

class ASTListVisitor : public RecursiveASTVisitor<ASTListVisitor> {
  std::list<clang::Stmt *> stmtList;

public:
  bool VisitStmt(clang::Stmt *stmt) { stmtList.push_back(stmt); }
  std::list<clang::Stmt *> getList() { return stmtList; }
};

class ScopDetectionVisitor : public RecursiveASTVisitor<ScopDetectionVisitor> {
private:
  ASTContext *Context;
  Rewriter rewriter;
  std::shared_ptr<ScopBuilder> builder;
  std::list<clang::Stmt *> excludeList;
  std::string GetCleanString(const clang::SourceRange &loc) {
    std::string exprString = clang::Lexer::getSourceText(
        clang::CharSourceRange::getTokenRange(loc), Context->getSourceManager(),
        Context->getLangOpts());
    // replace [] for ()
    std::replace(exprString.begin(), exprString.end(), '[', '(');
    std::replace(exprString.begin(), exprString.end(), ']', ')');
    // remove possible ;
    std::replace(exprString.begin(), exprString.end(), ';', ' ');
    return exprString;
  }

public:
  explicit ScopDetectionVisitor(ASTContext *Context,
                                std::shared_ptr<ScopBuilder> builder)
      : Context(Context),
        rewriter(Context->getSourceManager(), Context->getLangOpts()),
        builder(builder) {}
  ScopDetectionVisitor() {}
  void EndSourceFileAction() {
    SourceManager &SM = rewriter.getSourceMgr();
    // << SM.getFileEntryForID(SM.getMainFileID())->getName() << "\n";
    // rewriter.getEditBuffer(
    // SM.getMainFileID()).write(errs());
  }

  bool VisitStmt(clang::Stmt *st) {
    // check if stmt is part of
    // exclude List
    auto res = std::find(excludeList.begin(), excludeList.end(), st);
    /**
     * This skips statements we are not
     * interested in
     * */
    if (res != excludeList.end()) {
      return true;
    }
    // TODO: work on if statement's body
    //
    if (isa<IfStmt>(st)) {
      IfStmt *ifStmt = dyn_cast<IfStmt>(st);
    } else if (isa<ForStmt>(st)) {
      // at this stage we found a static control part
      // TODO: Examine this scop and check if it is
      // affine a nd every other check
      // 1. Must be affine
      // if it is add it to the scope
      // if not contiune trasversing
      // i
      //

      ForStmt *forStmt = dyn_cast<ForStmt>(st);
      // check if has been visited already
      if (builder->scopVisited(forStmt)) {
        return true;
      }
      // get the init statement
      clang::Stmt *initStmt = forStmt->getInit();
      Expr *incExpr = forStmt->getInc();
      bool validScop = true;
      bool requiresRescan = false;
      DeclRefExpr *varIterator = NULL;
      pdfg_c::Var *lowerBound = NULL;

      pdfg_c::Var *condBound = new pdfg_c::IDVar(
          GetCleanString(forStmt->getCond()->getSourceRange()));

      if (isa<UnaryOperator>(incExpr)) {
        auto uExpr = dyn_cast<UnaryOperator>(incExpr);
        varIterator = dyn_cast<DeclRefExpr>(uExpr->getSubExpr());
      } else
        validScop = false;

      if (initStmt != NULL) {
        // flaten the initstmt in
        // a list
        pdfg_c::ASTListVisitor listVisit;
        listVisit.TraverseStmt(initStmt);
        pdfg_c::append<std::list<clang::Stmt *>>(excludeList,
                                                 listVisit.getList());
        if (isa<DeclStmt>(initStmt)) {
          auto init = dyn_cast_or_null<DeclStmt>(initStmt);
          // for now we only support
          // single declaration

          if (init->isSingleDecl() && isa<VarDecl>(init->getSingleDecl())) {
            auto decl = dyn_cast<VarDecl>(init->getSingleDecl());
            if (varIterator->getDecl()->getID() != decl->getID()) {

              // this means we do not have access to
              // the lower bounds so we need to rescan
              // function declaration
              requiresRescan = true;
            } else {
              // here we have access to lower bound
              if (decl->getInit() != NULL) {
                if (isa<IntegerLiteral>(decl->getInit())) {
                  auto intR = dyn_cast<IntegerLiteral>(decl->getInit());
                  lowerBound = new pdfg_c::IntVar(
                      (int)intR->getValue().getLimitedValue());

                } else if (isa<DeclRefExpr>(decl->getInit())) {
                  auto declR = dyn_cast<DeclRefExpr>(decl->getInit());
                  lowerBound =
                      new pdfg_c::IDVar(declR->getNameInfo().getAsString());

                }

                else if (isa<ImplicitCastExpr>(decl->getInit())) {
                  auto declR = (dyn_cast<ImplicitCastExpr>(decl->getInit()))
                                   ->getSubExpr();
                  std::string exprString =
                      GetCleanString(decl->getInit()->getSourceRange());
                  lowerBound = new pdfg_c::IDVar(exprString);

                } else {
                  validScop = false;
                }
              }
            }
          } else {
            validScop = false;
          }
        } else if (isa<BinaryOperator>(initStmt)) {
          auto binOp = dyn_cast<BinaryOperator>(initStmt);
          // checking if the operation is
          // an equality expression that could
          // give us information about the lower
          // bounds
          if (binOp->isEqualityOp() && isa<DeclRefExpr>(binOp->getLHS())) {
            auto lhsDecl = dyn_cast_or_null<DeclRefExpr>(binOp->getLHS());

            if (varIterator->getDecl()->getID() ==
                lhsDecl->getDecl()->getID()) {
              if (isa<DeclRefExpr>(binOp->getRHS())) {
                auto declR = dyn_cast<DeclRefExpr>(binOp->getRHS());
                lowerBound =
                    new pdfg_c::IDVar(declR->getNameInfo().getAsString());

              } else if (isa<IntegerLiteral>(binOp->getRHS())) {
                auto intR = dyn_cast<IntegerLiteral>(binOp->getRHS());
                lowerBound =
                    new pdfg_c::IntVar((int)intR->getValue().getLimitedValue());

              } else if (isa<ImplicitCastExpr>(binOp->getRHS())) {
                auto declR =
                    (dyn_cast<ImplicitCastExpr>(binOp->getRHS()))->getSubExpr();
                std::string exprString =
                    GetCleanString(binOp->getRHS()->getSourceRange());
                lowerBound = new pdfg_c::IDVar(exprString);

              } else {
                llvm::errs() << "scop was invalid\n";
                // right now we support only
                // integer initialization
                // or variable assignment
                // expressions in the init for now
                // is not supported, we can add
                // more affine information later though
                validScop = false;
              }
            }
          } else {
            requiresRescan = true;
          }
        } else {

          requiresRescan = true;
        }
      } else {
        requiresRescan = true;
      }
      if (validScop) {
        // if we have to look for
        // lower bounds
        Scop *info = new Scop();
        info->incType = Scop::UNARY;
        info->varIterators.push_back(varIterator);
        info->needsVarValidation = requiresRescan;
        info->scopType = Scop::LOOP;
        // get the function declaration we currently are

        info->functionDecl = builder->getDeclarationScope()->top();
        info->lowerBound = lowerBound;
        info->stmt = forStmt;
        info->condBound = condBound;
        info->condExpr = forStmt->getCond();
        info->initStmt = initStmt;
        if (lowerBound == NULL) {
          FindIterAssignVisitor visit(varIterator, forStmt);
          // now we traverse current function
          // to look for the initStmt
          visit.TraverseDecl(builder->getDeclarationScope()->top());
          pdfg_c::Var *lb = visit.getlowerBound();
          info->lowerBound = lb;
        }
        if (builder->getScopScope()->empty()) {
          // if this loop info is not a
          // in a nest, then we want
          // to create a new context
          // with the builder
          builder->createNewContext(forStmt->getBody()->getSourceRange(), info);
        }
        // now let us push the loop info we have
        // extracted into the stack
        // and visit the contents of the for loop
        if (forStmt->getBody() != NULL) {
          auto body = forStmt->getBody();
          builder->getScopScope()->push_back(info);
          builder->getVisitedScops().push_back(forStmt);
          this->TraverseStmt(body);
          builder->getScopScope()->pop_back();
          // TODO have to find a way to store information
          // not to visit

          /*Make the trasversal keep going
           * if we are in a scope*/
          /*!builder->getScopScope()->empty();*/
        }
        // making sure the context is
        // cleared after we leave
        if (builder->getScopScope()->empty()) {
          builder->clearContext();
        }
        return true;
      }
    } else
        // this happens if there
        // is an assignment operation and
        // we are currently in a loop scope
        if ((isa<BinaryOperator>(st) && !builder->getScopScope()->empty())) {
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
        // let us check if the left side
        // of this operation is a var iterator
        if (isa<DeclRefExpr>(binOper->getLHS())) {
          auto declE = dyn_cast<DeclRefExpr>(binOper->getLHS());
          for (auto scop : *builder->getScopScope()) {
            for (auto iter : scop->varIterators) {
              if (iter->getDecl()->getID() == declE->getDecl()->getID()) {
                // we invalidate this context;
                builder->validateCurrentContext(false);
                llvm::errs() << "Detected modification of iterator \n";
              }
            }
          }
        }

        builder->addStmt(st);
      }

    }
    // rest of supported statements
    else if (isa<DeclStmt>(st) || isa<CompoundAssignOperator>(st))

    {

      builder->addStmt(st);
    }
    // this is a hack to
    // prevent rescanning
    excludeList.push_back(st);
    return true;
  }
};

class FVisitor : public RecursiveASTVisitor<FVisitor> {
private:
  ASTContext *Context;
  Rewriter rewriter;
  std::shared_ptr<ScopBuilder> builder;

public:
  explicit FVisitor(ASTContext *Context, std::shared_ptr<ScopBuilder> builder)
      : Context(Context),
        rewriter(Context->getSourceManager(), Context->getLangOpts()),
        builder(builder) {}
  FVisitor() {}
  bool VisitFunctionDecl(clang::FunctionDecl *Decl) {
    if (Decl->hasBody()) {
      builder->enterFunctionDeclaration(Decl);
      ScopDetectionVisitor scVisit(Context, builder);

      scVisit.TraverseStmt(Decl->getBody());
      builder->exitFunctionDeclaration();
    }
    // return false to prevent the visitor
    // from going deeper
    return false;
  }
};

} // namespace pdfg_c
#endif
