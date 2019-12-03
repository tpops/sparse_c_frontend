cmake_minimum_required(VERSION 3.9)
project (pdfg-c C CXX)
set (APP_NAME "pdfg-c")
#set(CMAKE_CXX_STANDARD 11)
set (CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fexceptions -fPIC -DPIC -Xpreprocessor -ftree-vectorize -funroll-all-loops ")

set (LLVM_ROOT /home/tpopoola/llvm/llvm_git CACHE PATH /home/tpopoola/llvm/llvm_build)

#llvm install sanity checkif(not exists ${LLVM_ROOT} / include / llvm)
if (NOT EXISTS ${LLVM_ROOT}/include/llvm)
endif()

if ( NOT EXISTS ${LLVM_ROOT}/tools/clang/include/clang)
  message (FATAL_ERROR "LLVM Root directory does not have clang")
endif()


list ( APPEND CMAKE_PREFIX_PATH "${LLVM_ROOT}/share/llvm/cmake")
list ( APPEND CMAKE_PREFIX_PATH "${LLVM_ROOT}/tools/clang/cmake")


find_package (LLVM REQUIRED CONFIG)

list (APPEND CMAKE_MODULE_PATH "${LLVM_CMAKE_DIR}")

find_package(Clang REQUIRED)

list (APPEND CMAKE_MODULE_PATH "${LLVM_ROOT}/tools/clang/cmake/modules")

INCLUDE (HandleLLVMOptions) #load additional configuration

option(BUILD_DOC "Build documentation" ON)

#check if Doxygen is installed
find_package(Doxygen)
if (DOXYGEN_FOUND)
#set input and output files
set(DOXYGEN_IN ${CMAKE_CURRENT_SOURCE_DIR}/docs/Doxyfile.in)
set(DOXYGEN_OUT ${CMAKE_CURRENT_BINARY_DIR}/Doxyfile)

#request to configure the file
configure_file(${DOXYGEN_IN} ${DOXYGEN_OUT} @ONLY)
	     message("Doxygen build started")


   
add_custom_target( doc_doxygen ALL
	COMMAND ${DOXYGEN_EXECUTABLE} ${DOXYGEN_OUT}
WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
COMMENT "Generating API documentation with Doxygen"
     VERBATIM )
else (DOXYGEN_FOUND)
message("Doxygen need to be installed to generate the doxygen documentation")
endif (DOXYGEN_FOUND)
include_directories(lib/pdfg-ir/src
		    lib/iegenlib/src
                    lib/isl 
		    lib/isl/imath 
		    lib/isl/include 
		    lib/isl/bld 
		    lib/isl/bld/include 
		    lib/gmp
                    lib/chill 
		    lib/chill/omega/basic/include 
		    lib/chill/omega/omega_lib/include
                    lib/chill/omega/code_gen/include 
		    lib/chill/omega/parser
                    lib/gtest  lib/gtest/include
                    lib/eigen lib/eigen/unsupported
                    lib/papi/src
                    out src
)
set (PDFG_C_FILES src/PDFGConsumer.hpp
	src/PDFGFrontEndAction.hpp
	src/ScopDetectionVisitor.hpp
	src/driver.cpp
	src/Scop.cpp
	src/Scop.hpp
	)
set(IEGEN_FILES  lib/iegenlib/src/set_relation/environment.cc
                 lib/iegenlib/src/set_relation/expression.cc
                 lib/iegenlib/src/set_relation/isl_str_manipulation.cc
                 lib/iegenlib/src/set_relation/set_relation.cc
                 lib/iegenlib/src/set_relation/SubMap.cc
                 lib/iegenlib/src/set_relation/TupleDecl.cc
                 lib/iegenlib/src/set_relation/UFCallMap.cc
                 lib/iegenlib/src/set_relation/UninterpFunc.cc
                 lib/iegenlib/src/util/util.cc
                 lib/iegenlib/src/parser/gen_scanner.cc
                 lib/iegenlib/src/parser/gen_parser.cc
                 lib/iegenlib/src/parser/parser.cc
)

set(ISL_FILES lib/isl/imath/gmp_compat.c
        lib/isl/imath/imath.c
        lib/isl/imath/imrat.c
        lib/isl/isl_map.c
        lib/isl/isl_input.c
        lib/isl/isl_output.c
        lib/isl/isl_printer.c
        lib/isl/isl_coalesce.c
        lib/isl/isl_union_map.c
        lib/isl/isl_map_simplify.c
        lib/isl/isl_map_subtract.c
        lib/isl/isl_ctx.c
        lib/isl/isl_space.c
        lib/isl/isl_mat.c
        lib/isl/isl_local_space.c
        lib/isl/isl_dim_map.c
        lib/isl/isl_map_list.c
        lib/isl/isl_map_simplify.c
        lib/isl/isl_val.c
        lib/isl/isl_int_sioimath.h
        lib/isl/isl_int_sioimath.c
        lib/isl/isl_val_sioimath.c
        lib/isl/isl_imath.c
        lib/isl/isl_obj.c
        lib/isl/isl_affine_hull.c
        lib/isl/isl_convex_hull.c
        lib/isl/isl_bernstein.c
        lib/isl/isl_blk.c
        lib/isl/isl_bound.c
        lib/isl/isl_id.c
        lib/isl/isl_id_to_ast_expr.c
        lib/isl/isl_seq.c
        lib/isl/isl_equalities.c
        lib/isl/isl_factorization.c
        lib/isl/isl_hash.c
        lib/isl/isl_tab.c
        lib/isl/isl_tab_pip.c
        lib/isl/isl_transitive_closure.c
        lib/isl/isl_vec.c
        lib/isl/isl_aff.c
        lib/isl/isl_reordering.c
        lib/isl/isl_constraint.c
        lib/isl/isl_lp.c
        lib/isl/isl_polynomial.c
        lib/isl/isl_sort.c
        lib/isl/isl_farkas.c
        lib/isl/isl_tarjan.c
        lib/isl/isl_fold.c
        lib/isl/isl_morph.c
        lib/isl/isl_arg.c
        lib/isl/isl_options.c
        lib/isl/isl_point.c
        lib/isl/isl_range.c
        lib/isl/isl_sample.c
        lib/isl/isl_scan.c
        lib/isl/isl_stream.c
        lib/isl/isl_version.c
        lib/isl/isl_vertices.c
        lib/isl/basis_reduction_tab.c
        lib/isl/isl_set_list.c
        lib/isl/isl_ast.c
        lib/isl/isl_ast_build.c
        lib/isl/isl_ast_build_expr.c
        lib/isl/isl_ast_codegen.c
        lib/isl/isl_ast_graft.c
        lib/isl/isl_band.c
        lib/isl/isl_ilp.c
        lib/isl/isl_schedule.c
        lib/isl/isl_schedule_node.c
        lib/isl/isl_schedule_tree.c
        lib/isl/isl_schedule_band.c
        lib/isl/isl_schedule_read.c
        lib/isl/print.c
)

set(EDSL_FILES   lib/pdfg-ir/src/poly/PolyLib.hpp
                 lib/pdfg-ir/src/iegenlib/IEGenLib.hpp
                 lib/pdfg-ir/src/omega/OmegaLib.hpp
                 lib/pdfg-ir/src/pdfg/GraphIL.hpp
                 lib/pdfg-ir/src/pdfg/Codegen.hpp
                 lib/pdfg-ir/src/pdfg/InspGen.hpp
                 lib/pdfg-ir/src/pdfg/FlowGraph.hpp
                 lib/pdfg-ir/src/pdfg/Visitor.hpp
)
set(OMEGA_FILES lib/chill/omega/basic/src/ConstString.cc
                lib/chill/omega/parser/parser.tab.cc
                lib/chill/omega/parser/lex.yy.cc
                lib/chill/omega/parser/AST.cc
                lib/chill/omega/omega_lib/src/closure.cc
                lib/chill/omega/omega_lib/src/farkas.cc
                lib/chill/omega/omega_lib/src/hull.cc
                lib/chill/omega/omega_lib/src/pres_beaut.cc
                lib/chill/omega/omega_lib/src/pres_col.cc
                lib/chill/omega/omega_lib/src/pres_dnf.cc
                lib/chill/omega/omega_lib/src/pres_cnstr.cc
                lib/chill/omega/omega_lib/src/pres_decl.cc
                lib/chill/omega/omega_lib/src/pres_gen.cc
                lib/chill/omega/omega_lib/src/pres_logic.cc
                lib/chill/omega/omega_lib/src/pres_form.cc
                lib/chill/omega/omega_lib/src/pres_conj.cc
                lib/chill/omega/omega_lib/src/pres_print.cc
                lib/chill/omega/omega_lib/src/pres_quant.cc
                lib/chill/omega/omega_lib/src/pres_rear.cc
                lib/chill/omega/omega_lib/src/pres_var.cc
                lib/chill/omega/omega_lib/src/reach.cc
                lib/chill/omega/omega_lib/src/hull_simple.cc
                lib/chill/omega/omega_lib/src/Relation.cc
                lib/chill/omega/omega_lib/src/RelBody.cc
                lib/chill/omega/omega_lib/src/Relations.cc
                lib/chill/omega/omega_lib/src/RelVar.cc
                lib/chill/omega/omega_lib/src/omega_core/oc.cc
                lib/chill/omega/omega_lib/src/omega_core/oc_eq.cc
                lib/chill/omega/omega_lib/src/omega_core/oc_exp_kill.cc
                lib/chill/omega/omega_lib/src/omega_core/oc_global.cc
                lib/chill/omega/omega_lib/src/omega_core/oc_print.cc
                lib/chill/omega/omega_lib/src/omega_core/oc_problems.cc
                lib/chill/omega/omega_lib/src/omega_core/oc_query.cc
                lib/chill/omega/omega_lib/src/omega_core/oc_quick_kill.cc
                lib/chill/omega/omega_lib/src/omega_core/oc_simple.cc
                lib/chill/omega/omega_lib/src/omega_core/oc_solve.cc
                lib/chill/omega/omega_lib/src/omega_core/oc_util.cc
                lib/chill/omega/code_gen/src/codegen.cc
                lib/chill/omega/code_gen/src/CG.cc
                lib/chill/omega/code_gen/src/CG_utils.cc
                lib/chill/omega/code_gen/src/CG_stringBuilder.cc
)

set (TESTING "false")
set (MAKELIB "false")
if (TESTING)
    set(GTEST_FILES lib/gtest/src/gtest.cc
                    lib/gtest/src/gtest-filepath.cc
                    lib/gtest/src/gtest-death-test.cc
                    lib/gtest/src/gtest-test-part.cc
                    lib/gtest/src/gtest-printers.cc
                    lib/gtest/src/gtest-port.cc
    )

    set(UNIT_TESTS test/driver.cpp) # test/TensorDecompTest.cpp)
    
    enable_testing()
    
    add_executable(pdfg-cTest ${UNIT_TESTS} ${GTEST_FILES} ${PDFG-C_FILES})
endif()


include (AddLLVM)
include(AddClang)

link_directories(lib)
add_definitions(${LLVM_DEFINITIONS})
include_directories(${LLVM_INCLUDE_DIRS})
include_directories(${CLANG_INCLUDE_DIRS})
set (LLVM_RUNTIME_OUTPUT_INTDIR "${CMAKE_BINARY_DIR}/bin/${CMAKE_CFG_INT_DIR}" )
set (LLVM_LIBRARY_OUTPUT_INTDIR "${CMAKE_BINARY_DIR}/lib/${CMAKE_CFG_INT_DIR}" )

get_property(dirs DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR} PROPERTY INCLUDE_DIRECTORIES)
foreach(dir ${dirs})
	  message(STATUS "dir='${dir}'")
  endforeach()
set( LLVM_LINK_COMPONENTS
    ${LLVM_TARGETS_TO_BUILD}
      Option
      Support
)
if (MAKELIB)
#installing pdfg - ir third party
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -g -O3")
add_library(polylib SHARED ${EDSL_FILES} ${IEGEN_FILES} ${ISL_FILES} ${OMEGA_FILES})

endif()

add_clang_executable(
	${APP_NAME}
      	${PDFG_C_FILES}
)

target_link_libraries(${APP_NAME}
          PRIVATE
  	  clangAST
          clangBasic
  	  clangDriver
  	  clangFrontend
  	  clangRewriteFrontend
  	  clangSerialization
  	  clangStaticAnalyzerFrontend
	  clangLex
	  clangRewrite
	  clangTooling
#polylib
) 
set_target_properties(${APP_NAME} PROPERTIES LINKER_LANGUAGE CXX)
