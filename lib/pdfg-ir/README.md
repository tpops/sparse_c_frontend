# Polyhedral+Dataflow eDSL and IR

This project contains an implementation of the Polyhedral+Dataflow graph intermediate representation (IR), and
corresponding embedded domain specific language (eDSL) in C++.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing
purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

The project requires Git, CMake, GCC, and Python3.

```
$ git --version
git version 2.19.1

$ cmake --version
cmake version 3.12.1

$ g++ --version
g++ (Ubuntu 8.3.0-6ubuntu1~18.10) 8.3.0

$ python3 --version
Python 3.6.7
```

### Installing

Clone the repository and enter the directory:

```
$ git clone https://github.com/BoiseState/PolyhedralDataflowIR.git
```

Enter the directory:

```
$ cd PolyhedralDataflowIR
```

Build:

```
$ cmake .
$ make
```

## Python scripts

Python scripts and Jupyter notebooks are in the `scripts` directory.

## Running the tests

Run the test executable:

```
$ ./test/edslTest
```

## Deployment

Deploy (NOT YET TESTED!!!):

```
$ make install
```

## Included Packages

* [CHiLL](https://github.com/CtopCsUtahEdu/chill-dev) - Omega+ calculator performs polyhedral code generation.
* [IEGenLib](https://github.com/CompOpt4Apps/IEGenLib) - Set and relation library with uninterpreted function symbols.
* [ISL](https://github.com/Meinersbur/isl) - Integer Set Library (required by IEGenLib).
* [GMP](https://gmplib.org) - GNU Multiple Precision Arithmetic Library (required by ISL).
* [GoogleTest](https://github.com/google/googletest) - Google Testing and Mocking Framework (for unit tests)

## Authors

* **Eddie Davis** - *Initial work* - [CompOpt4Apps](https://github.com/CompOpt4Apps/VariationsOnATheme)

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Insert NSF grant number...
