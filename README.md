## SPARSE POLYHEDRAL MODEL FRONT END COMPILER

Name: Tobi Goodness Popoola
Class: Comprehensive exam artifact

# Features / Overview
A compiler that detects Static Control Parts (SCoPs) in a C program and generates Sparse Polyhedral Model

1. Parses C program 
2. Generates the Iteration Domain component of Sparse Polyhedral Framework.
3. Generates the Execution Schedule component of the Sparse Polyhedral Framework.


### Documentation

Generate Documentation to see source manifest


```sh
OUTPUT_DIRECTORY       = @CMAKE_CURRENT_BINARY_DIR@/doc_doxygen/
INPUT                  = @CMAKE_CURRENT_SOURCE_DIR@/src/ @CMAKE_CURRENT_SOURCE_DIR@/docs
```
To specify the location for documentation edit OUTPUT_DIRECTORY in the docs/ folder.


### Dependencies
Clang/LLVM

Clang/LLVM: Clang installation is needed

Follow installation information [here](https://clang.llvm.org/get_started.html)



### Build / Install

```sh
$ mkdir build
$ cd build
```

You can specify documentation option with the -DBUILD_DOC=ON and the llvm/clang route -DLLVM_ROOT=

```sh
$ cmake -DLLVM_ROOT=~/ -DBUILD_DOC=ON ../path-to-source/
```

### Usage

```sh
 $./build/bin/sparse-c -h=1 /filepath -- -std=c++11

```


### Publications Used 

[Strout, Michelle & Lamielle, Alan & Carter, Larry & Ferrante, Jeanne & Kreaseck, Barbara & Olschanowksy, Catherine. (2013). An Approach for Code Generation in the Sparse Polyhedral Framework. Parallel Computing. 53. 10.1016/j.parco.2016.02.004.] (https://www.researchgate.net/publication/259497067_An_Approach_for_Code_Generation_in_the_Sparse_Polyhedral_Framework) 


[ENABLING POLYHEDRAL OPTIMIZATIONS IN LLVM. Tobias Christian Grosser](https://polly.llvm.org/publications/grosser-diploma-thesis.pdf)
