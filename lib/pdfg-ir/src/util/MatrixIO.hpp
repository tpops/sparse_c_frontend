#ifndef _MATRIXIO_HPP_
#define _MATRIXIO_HPP_

/*
*   Matrix Market I/O library for ANSI C
*
*   See http://math.nist.gov/MatrixMarket for details.
*/


#include <cstdio>
#include <cstring>
#include <cstdlib>
#include <cctype>
#include <string>

using std::string;

#ifndef NULL
#define NULL 0
#endif

#define MM_MAX_LINE_LENGTH 1025
#define MatrixMarketBanner "%%MatrixMarket"
#define MM_MAX_TOKEN_LENGTH 64

typedef double dtype;
typedef char MM_typecode[4];

/********************* MM_typecode query fucntions ***************************/

#define mm_is_matrix(typecode)	((typecode)[0]=='M')

#define mm_is_sparse(typecode)	((typecode)[1]=='C')
#define mm_is_coordinate(typecode)((typecode)[1]=='C')
#define mm_is_dense(typecode)	((typecode)[1]=='A')
#define mm_is_array(typecode)	((typecode)[1]=='A')

#define mm_is_complex(typecode)	((typecode)[2]=='C')
#define mm_is_real(typecode)		((typecode)[2]=='R')
#define mm_is_pattern(typecode)	((typecode)[2]=='P')
#define mm_is_integer(typecode) ((typecode)[2]=='I')

#define mm_is_symmetric(typecode)((typecode)[3]=='S')
#define mm_is_general(typecode)	((typecode)[3]=='G')
#define mm_is_skew(typecode)	((typecode)[3]=='K')
#define mm_is_hermitian(typecode)((typecode)[3]=='H')

int mm_is_valid(MM_typecode matcode);		/* too complex for a macro */


/********************* MM_typecode modify fucntions ***************************/

#define mm_set_matrix(typecode)	((*typecode)[0]='M')
#define mm_set_coordinate(typecode)	((*typecode)[1]='C')
#define mm_set_array(typecode)	((*typecode)[1]='A')
#define mm_set_dense(typecode)	mm_set_array(typecode)
#define mm_set_sparse(typecode)	mm_set_coordinate(typecode)

#define mm_set_complex(typecode)((*typecode)[2]='C')
#define mm_set_real(typecode)	((*typecode)[2]='R')
#define mm_set_pattern(typecode)((*typecode)[2]='P')
#define mm_set_integer(typecode)((*typecode)[2]='I')


#define mm_set_symmetric(typecode)((*typecode)[3]='S')
#define mm_set_general(typecode)((*typecode)[3]='G')
#define mm_set_skew(typecode)	((*typecode)[3]='K')
#define mm_set_hermitian(typecode)((*typecode)[3]='H')

#define mm_clear_typecode(typecode) ((*typecode)[0]=(*typecode)[1]= \
									(*typecode)[2]=' ',(*typecode)[3]='G')

#define mm_initialize_typecode(typecode) mm_clear_typecode(typecode)


/********************* Matrix Market error codes ***************************/


#define MM_COULD_NOT_READ_FILE	11
#define MM_PREMATURE_EOF		12
#define MM_NOT_MTX				13
#define MM_NO_HEADER			14
#define MM_UNSUPPORTED_TYPE		15
#define MM_LINE_TOO_LONG		16
#define MM_COULD_NOT_WRITE_FILE	17


/******************** Matrix Market internal definitions ********************

   MM_matrix_typecode: 4-character sequence

				    ojbect 		sparse/   	data        storage
						  		dense     	type        scheme

   string position:	 [0]        [1]			[2]         [3]

   Matrix typecode:  M(atrix)  C(oord)		R(eal)   	G(eneral)
						        A(array)	C(omplex)   H(ermitian)
											P(attern)   S(ymmetric)
								    		I(nteger)	K(kew)

 ***********************************************************************/

#define MM_MTX_STR		"matrix"
#define MM_ARRAY_STR	"array"
#define MM_DENSE_STR	"array"
#define MM_COORDINATE_STR "coordinate"
#define MM_SPARSE_STR	"coordinate"
#define MM_COMPLEX_STR	"complex"
#define MM_REAL_STR		"real"
#define MM_INT_STR		"integer"
#define MM_GENERAL_STR  "general"
#define MM_SYMM_STR		"symmetric"
#define MM_HERM_STR		"hermitian"
#define MM_SKEW_STR		"skew-symmetric"
#define MM_PATTERN_STR  "pattern"

#define MM_MAX_LINE_LENGTH 1025
#define MatrixMarketBanner "%%MatrixMarket"
#define MM_MAX_TOKEN_LENGTH 64

typedef char MM_typecode[4];

char *mm_typecode_to_str(MM_typecode matcode);

int mm_read_banner(FILE *f, MM_typecode *matcode);
int mm_read_mtx_crd_size(FILE *f, int *M, int *N, int *nz);
int mm_read_mtx_array_size(FILE *f, int *M, int *N);

int mm_write_banner(FILE *f, MM_typecode matcode);
int mm_write_mtx_crd_size(FILE *f, int M, int N, int nz);
int mm_write_mtx_array_size(FILE *f, int M, int N);


/********************* MM_typecode query fucntions ***************************/

#define mm_is_matrix(typecode)	((typecode)[0]=='M')

#define mm_is_sparse(typecode)	((typecode)[1]=='C')
#define mm_is_coordinate(typecode)((typecode)[1]=='C')
#define mm_is_dense(typecode)	((typecode)[1]=='A')
#define mm_is_array(typecode)	((typecode)[1]=='A')

#define mm_is_complex(typecode)	((typecode)[2]=='C')
#define mm_is_real(typecode)		((typecode)[2]=='R')
#define mm_is_pattern(typecode)	((typecode)[2]=='P')
#define mm_is_integer(typecode) ((typecode)[2]=='I')

#define mm_is_symmetric(typecode)((typecode)[3]=='S')
#define mm_is_general(typecode)	((typecode)[3]=='G')
#define mm_is_skew(typecode)	((typecode)[3]=='K')
#define mm_is_hermitian(typecode)((typecode)[3]=='H')

int mm_is_valid(MM_typecode matcode);		/* too complex for a macro */


/********************* MM_typecode modify fucntions ***************************/

#define mm_set_matrix(typecode)	((*typecode)[0]='M')
#define mm_set_coordinate(typecode)	((*typecode)[1]='C')
#define mm_set_array(typecode)	((*typecode)[1]='A')
#define mm_set_dense(typecode)	mm_set_array(typecode)
#define mm_set_sparse(typecode)	mm_set_coordinate(typecode)

#define mm_set_complex(typecode)((*typecode)[2]='C')
#define mm_set_real(typecode)	((*typecode)[2]='R')
#define mm_set_pattern(typecode)((*typecode)[2]='P')
#define mm_set_integer(typecode)((*typecode)[2]='I')


#define mm_set_symmetric(typecode)((*typecode)[3]='S')
#define mm_set_general(typecode)((*typecode)[3]='G')
#define mm_set_skew(typecode)	((*typecode)[3]='K')
#define mm_set_hermitian(typecode)((*typecode)[3]='H')

#define mm_clear_typecode(typecode) ((*typecode)[0]=(*typecode)[1]= \
									(*typecode)[2]=' ',(*typecode)[3]='G')

#define mm_initialize_typecode(typecode) mm_clear_typecode(typecode)


/********************* Matrix Market error codes ***************************/


#define MM_COULD_NOT_READ_FILE	11
#define MM_PREMATURE_EOF		12
#define MM_NOT_MTX				13
#define MM_NO_HEADER			14
#define MM_UNSUPPORTED_TYPE		15
#define MM_LINE_TOO_LONG		16
#define MM_COULD_NOT_WRITE_FILE	17


/******************** Matrix Market internal definitions ********************

   MM_matrix_typecode: 4-character sequence

				    ojbect 		sparse/   	data        storage
						  		dense     	type        scheme

   string position:	 [0]        [1]			[2]         [3]

   Matrix typecode:  M(atrix)  C(oord)		R(eal)   	G(eneral)
						        A(array)	C(omplex)   H(ermitian)
											P(attern)   S(ymmetric)
								    		I(nteger)	K(kew)

 ***********************************************************************/

#define MM_MTX_STR		"matrix"
#define MM_ARRAY_STR	"array"
#define MM_DENSE_STR	"array"
#define MM_COORDINATE_STR "coordinate"
#define MM_SPARSE_STR	"coordinate"
#define MM_COMPLEX_STR	"complex"
#define MM_REAL_STR		"real"
#define MM_INT_STR		"integer"
#define MM_GENERAL_STR  "general"
#define MM_SYMM_STR		"symmetric"
#define MM_HERM_STR		"hermitian"
#define MM_SKEW_STR		"skew-symmetric"
#define MM_PATTERN_STR  "pattern"


/*  high level routines */

int mm_write_mtx_crd(char fname[], int M, int N, int nz, int I[], int J[],
                     double val[], MM_typecode matcode);
int mm_read_mtx_crd_data(FILE *f, int M, int N, int nz, int I[], int J[],
                         double val[], MM_typecode matcode);
int mm_read_mtx_crd_entry(FILE *f, int *I, int *J, double *real, double *img,
                          MM_typecode matcode);

int mm_read_unsymmetric_sparse(const char *fname, int *M_, int *N_, int *nz_,
                               double **val_, int **I_, int **J_);

//unsigned _coo_order;

namespace util {
class MatrixIO {
public:
    explicit MatrixIO(const string &filename = "", unsigned order = 2, unsigned nnz = 0) {
        _filename = filename;
        _nnz = nnz;
        _order = order;
        _dims = (unsigned*) calloc(order, sizeof(unsigned));
        _indices = (unsigned**) calloc(order, sizeof(unsigned*));
        _vals = nullptr;
    }

    virtual ~MatrixIO() {
        if (_dims != nullptr) {
            free(_dims);
        }
        if (_vals != nullptr) {
            free(_vals);
        }
        if (_indices != nullptr) {
            for (unsigned i = 0; i < _order; i++) {
                free(_indices[i]);
            }
            free(_indices);
        }
    }

    virtual int read() {
        int retval = 0;
        FILE *fp = fopen(_filename.c_str(), "r");
        int nrows, ncols, nnz, row, col;

        if (fp != NULL) {
            retval = mm_read_banner(fp, &_mtxcode);
//            if (retval != 0) {
//                fprintf(stderr, "Could not process Matrix Market banner.\n");
//            }

            if (mm_is_complex(_mtxcode) && mm_is_matrix(_mtxcode) && mm_is_sparse(_mtxcode)) {
                fprintf(stderr, "This app does not support Market Market type: [%s]\n",
                        mm_typecode_to_str(_mtxcode));
                retval = 1;
            } else {
                retval = mm_read_mtx_crd_size(fp, &nrows, &ncols, &nnz);
                if (retval == 0) {
                    _dims[0] = nrows;
                    _dims[1] = ncols;
                    _nnz = nnz;

                    _indices[0] = (unsigned*) malloc(_nnz * sizeof(int));
                    _indices[1] = (unsigned*) malloc(_nnz * sizeof(int));
                    _vals = (dtype *) malloc(_nnz * sizeof(dtype));

                    int row, col;
                    for (unsigned i = 0; i < _nnz; i++) {
                        if (fscanf(fp, "%d %d %lg\n", &row, &col, &_vals[i])) {
                            _indices[0][i] = row - 1;  /* adjust from 1-based to 0-based */
                            _indices[1][i] = col - 1;
                        }
                    }

                    if (fp != stdin) {
                        fclose(fp);
                    }
                }
            }
        } else {
            retval = 1;
        }

        return retval;
    }

    int write() {
        int retval = 0;

        FILE *fp = stdout;
        mm_write_banner(fp, _mtxcode);
        mm_write_mtx_crd_size(fp, _dims[0], _dims[1], _nnz);
        for (unsigned i = 0; i < _nnz; i++) {
            fprintf(fp, "%d %d %20.19g\n", _indices[0][i] + 1, _indices[1][i] + 1, _vals[i]);
        }

        if (fp != stdout) {
            fclose(fp);
        }

        return retval;
    }

    unsigned nrows() const {
        return _dims[0];
    }

    unsigned ncols() const {
        return _dims[1];
    }

    unsigned nnz() const {
        return _nnz;
    }

    unsigned order() const {
        return _order;
    }

    unsigned *rows() const {
        return _indices[0];
    }

    unsigned *cols() const {
        return _indices[1];
    }

    dtype *vals() const {
        return _vals;
    }

    const string &filename() const {
        return _filename;
    }

protected:
    string _filename;
    unsigned _nnz;
    unsigned _order;
    unsigned* _dims;
    unsigned** _indices;
    dtype* _vals;
    MM_typecode _mtxcode;

private:
    int mm_is_valid(MM_typecode matcode) {
        if (!mm_is_matrix(matcode)) return 0;
        if (mm_is_dense(matcode) && mm_is_pattern(matcode)) return 0;
        if (mm_is_real(matcode) && mm_is_hermitian(matcode)) return 0;
        if (mm_is_pattern(matcode) && (mm_is_hermitian(matcode) ||
                                       mm_is_skew(matcode)))
            return 0;
        return 1;
    }

    int mm_read_banner(FILE *f, MM_typecode *matcode) {
        char line[MM_MAX_LINE_LENGTH];
        char banner[MM_MAX_TOKEN_LENGTH];
        char mtx[MM_MAX_TOKEN_LENGTH];
        char crd[MM_MAX_TOKEN_LENGTH];
        char data_type[MM_MAX_TOKEN_LENGTH];
        char storage_scheme[MM_MAX_TOKEN_LENGTH];
        char *p;


        mm_clear_typecode(matcode);

        if (fgets(line, MM_MAX_LINE_LENGTH, f) == NULL)
            return MM_PREMATURE_EOF;

        if (sscanf(line, "%s %s %s %s %s", banner, mtx, crd, data_type,
                   storage_scheme) != 5)
            return MM_PREMATURE_EOF;

        for (p = mtx; *p != '\0'; *p = tolower(*p), p++);  /* convert to lower case */
        for (p = crd; *p != '\0'; *p = tolower(*p), p++);
        for (p = data_type; *p != '\0'; *p = tolower(*p), p++);
        for (p = storage_scheme; *p != '\0'; *p = tolower(*p), p++);

        /* check for banner */
        if (strncmp(banner, MatrixMarketBanner, strlen(MatrixMarketBanner)) != 0)
            return MM_NO_HEADER;

        /* first field should be "mtx" */
        if (strcmp(mtx, MM_MTX_STR) != 0)
            return MM_UNSUPPORTED_TYPE;
        mm_set_matrix(matcode);


        /* second field describes whether this is a sparse matrix (in coordinate
                storgae) or a dense array */


        if (strcmp(crd, MM_SPARSE_STR) == 0)
            mm_set_sparse(matcode);
        else if (strcmp(crd, MM_DENSE_STR) == 0)
            mm_set_dense(matcode);
        else
            return MM_UNSUPPORTED_TYPE;


        /* third field */

        if (strcmp(data_type, MM_REAL_STR) == 0)
            mm_set_real(matcode);
        else if (strcmp(data_type, MM_COMPLEX_STR) == 0)
            mm_set_complex(matcode);
        else if (strcmp(data_type, MM_PATTERN_STR) == 0)
            mm_set_pattern(matcode);
        else if (strcmp(data_type, MM_INT_STR) == 0)
            mm_set_integer(matcode);
        else
            return MM_UNSUPPORTED_TYPE;


        /* fourth field */

        if (strcmp(storage_scheme, MM_GENERAL_STR) == 0)
            mm_set_general(matcode);
        else if (strcmp(storage_scheme, MM_SYMM_STR) == 0)
            mm_set_symmetric(matcode);
        else if (strcmp(storage_scheme, MM_HERM_STR) == 0)
            mm_set_hermitian(matcode);
        else if (strcmp(storage_scheme, MM_SKEW_STR) == 0)
            mm_set_skew(matcode);
        else
            return MM_UNSUPPORTED_TYPE;


        return 0;
    }

    int mm_write_mtx_crd_size(FILE *f, int M, int N, int nz) {
        if (fprintf(f, "%d %d %d\n", M, N, nz) != 3)
            return MM_COULD_NOT_WRITE_FILE;
        else
            return 0;
    }

    int mm_read_mtx_crd_size(FILE *f, int *M, int *N, int *nz) {
        char line[MM_MAX_LINE_LENGTH];
        int num_items_read;

        /* set return null parameter values, in case we exit with errors */
        *M = *N = *nz = 0;

        /* now continue scanning until you reach the end-of-comments */
        do {
            if (fgets(line, MM_MAX_LINE_LENGTH, f) == NULL)
                return MM_PREMATURE_EOF;
        } while (line[0] == '%');

        /* line[] is either blank or has M,N, nz */
        if (sscanf(line, "%d %d %d", M, N, nz) == 3)
            return 0;

        else
            do {
                num_items_read = fscanf(f, "%d %d %d", M, N, nz);
                if (num_items_read == EOF) return MM_PREMATURE_EOF;
            } while (num_items_read != 3);

        return 0;
    }

    /******************************************************************/
    /* use when I[], J[], and val[]J, and val[] are already allocated */
    /******************************************************************/

    int mm_read_mtx_crd_data(FILE *f, int M, int N, int nz, int I[], int J[],
                             double val[], MM_typecode matcode) {
        int i;
        if (mm_is_complex(matcode)) {
            for (i = 0; i < nz; i++)
                if (fscanf(f, "%d %d %lg %lg", &I[i], &J[i], &val[2 * i], &val[2 * i + 1])
                    != 4)
                    return MM_PREMATURE_EOF;
        } else if (mm_is_real(matcode)) {
            for (i = 0; i < nz; i++) {
                if (fscanf(f, "%d %d %lg\n", &I[i], &J[i], &val[i])
                    != 3)
                    return MM_PREMATURE_EOF;

            }
        } else if (mm_is_pattern(matcode)) {
            for (i = 0; i < nz; i++)
                if (fscanf(f, "%d %d", &I[i], &J[i])
                    != 2)
                    return MM_PREMATURE_EOF;
        } else
            return MM_UNSUPPORTED_TYPE;

        return 0;
    }

    char  *mm_typecode_to_str(MM_typecode matcode)
    {
        char buffer[MM_MAX_LINE_LENGTH];
        char *types[4];
        char *mm_strdup(const char *);
        int error =0;

        /* check for MTX type */
        if (mm_is_matrix(matcode))
            types[0] = (char*) MM_MTX_STR;
        else
            error=1;

        /* check for CRD or ARR matrix */
        if (mm_is_sparse(matcode))
            types[1] = (char*) MM_SPARSE_STR;
        else
        if (mm_is_dense(matcode))
            types[1] = (char*) MM_DENSE_STR;
        else
            return NULL;

        /* check for element data type */
        if (mm_is_real(matcode))
            types[2] = (char*) MM_REAL_STR;
        else
        if (mm_is_complex(matcode))
            types[2] = (char*) MM_COMPLEX_STR;
        else
        if (mm_is_pattern(matcode))
            types[2] = (char*) MM_PATTERN_STR;
        else
        if (mm_is_integer(matcode))
            types[2] = (char*) MM_INT_STR;
        else
            return NULL;


        /* check for symmetry type */
        if (mm_is_general(matcode))
            types[3] = (char*) MM_GENERAL_STR;
        else
        if (mm_is_symmetric(matcode))
            types[3] = (char*) MM_SYMM_STR;
        else
        if (mm_is_hermitian(matcode))
            types[3] = (char*) MM_HERM_STR;
        else
        if (mm_is_skew(matcode))
            types[3] = (char*) MM_SKEW_STR;
        else
            return NULL;

        sprintf(buffer,"%s %s %s %s", types[0], types[1], types[2], types[3]);
        int len = strlen(buffer);
        char *newbuff = (char *) malloc((len+1)*sizeof(char));
        return strcpy(newbuff, buffer);
    }
};

class MatlabIO : public MatrixIO {
public:
    explicit MatlabIO(const string &filename = "", int nrows = 0, int ncols = 0) :  MatrixIO(filename) {
        _dims[0] = nrows;
        _dims[1] = ncols;
    }

    int read() {
        char line[1024];
        char *pch;

        FILE *in = fopen(_filename.c_str(), "r");
        if (_dims[0] < 1) {
            // TODO: Read the file to count the number of rows...

            // TODO: Count the number of columns, from the first column

            rewind(in);
        }

        unsigned nrows = _dims[0];
        unsigned ncols = _dims[1];
        _nnz = nrows * ncols;
        _indices[0] = (unsigned*) calloc(_nnz, sizeof(int));
        _indices[1] = (unsigned*) calloc(_nnz, sizeof(int));
        _vals = (dtype*) calloc(_nnz, sizeof(dtype));

        for (unsigned i = 0; i < _dims[0] && fgets(line, sizeof(line), in) != NULL; i++) {
            // Tokenize the line...
            pch = strtok(line, " ");
            for (unsigned j = 0; j < _dims[1] && pch; j++) {
                unsigned n = i * j;
                _indices[0][n] = i;
                _indices[1][n] = j;
                _vals[n] = atof(pch);
                pch = strtok(NULL, " ");
            }
        }

        fclose(in);

        return _nnz < 1;
    }
};

class TensorIO : public MatrixIO {
protected:
    unsigned _rank;
    unsigned* _indptr;

    typedef struct _coo_tnode {
        unsigned* coords;
        unsigned order;
        dtype val;
        struct _coo_tnode *next;
    } coo_tnode;

    static int coo_tnode_comp(const void* lhs, const void* rhs) {
        int comp = 0;
        coo_tnode *tn1 = (coo_tnode*) lhs;
        coo_tnode *tn2 = (coo_tnode*) rhs;
        unsigned order = tn1->order;
        for (unsigned i = 0; i < order && !comp; i++) {
            comp = tn1->coords[i] - tn2->coords[i];
        }
        return comp;
    }

public:
    explicit TensorIO(const string &filename = "", const int rank = 0) :  MatrixIO(filename) {
        _rank = rank;
    }

    unsigned rank() const {
        return _rank;
    }

    unsigned* indices() const {
        return _indptr;
    }

    unsigned ntubes() const {
        return _dims[2];
    }

    unsigned* dims() const {
        return _dims;
    }

    int read() {
        // TNS files have no header, so this needs to be done in two passes.
        // Pass 1:
        //   1) Read first non-comment line and tokenize to get the order.
        //   2) Read to end of file to get NNZ
        // Pass 2:
        //   1) Allocate the tensor.
        //   2) Rewind the file pointer and read the indices and values.

        char line[1024];
        char *pch;
        bool found = 0;
        bool mtx = 0;
        unsigned lnum = 0;
        unsigned pos = 0;
        coo_tnode* nodes = NULL;

        FILE *in = fopen(_filename.c_str(), "r");
        while (!found && fgets(line, sizeof(line), in) != NULL) {
            found = (strlen(line) > 0 && !strchr(line, '#') && !strchr(line, '%'));
            mtx |= (strstr(line, "MatrixMarket") != NULL);
        }

        if (found) {
            /* If MTX format, skip a line */
            if (mtx) {
                pch = fgets(line, sizeof(line), in);
            }

            // Tokenize 1st line and get order
            _order = 0;
            for (pch = strtok(line, " "); pch != NULL; pch = strtok(NULL, " ")) {
                _order += 1;
            }
            _order -= 1;     // Subtract 1 for value

            // Count lines (nonzeros)
            _nnz += 1;
            while (fgets(line, sizeof(line), in) != NULL) {
                if (strlen(line) > 0 && line[0] != '#') {
                    _nnz += 1;
                }
            }

            nodes = (coo_tnode*) calloc(_nnz, sizeof(coo_tnode));
            for (unsigned i = 0; i < _nnz; i++) {
                nodes[i].coords = (unsigned*) calloc(_order, sizeof(unsigned));
                nodes[i].order = _order;
            }
            rewind(in);

            _indptr = (unsigned*) calloc(_nnz * _order, sizeof(unsigned));
            _dims = (unsigned*) calloc(_order, sizeof(unsigned));
            _vals = (dtype*) calloc(_nnz, sizeof(dtype));

            while (fgets(line, sizeof(line), in) != NULL) {
                if (strlen(line) > 0 && line[0] != '#') {
                    pos = 0;
                    for (pch = strtok(line, " "); pch != NULL; pch = strtok(NULL, " ")) {
                        if (pos < _order) {
                            // offset2(i,j,N) (i)*(N)+(j)
                            unsigned ndx = (unsigned) atol(pch);
                            if (ndx > _dims[pos]) {
                                _dims[pos] = ndx;
                            }
                            nodes[lnum].coords[pos] = ndx - 1;
                        } else {
                            nodes[lnum].val = (dtype) atof(pch);
                        }
                        pos += 1;
                    }
                    lnum += 1;
                }
            }
        }

        if (nodes != NULL) {
            qsort(nodes, _nnz, sizeof(coo_tnode), coo_tnode_comp);

            for (unsigned i = 0; i < _nnz; i++) {
                for (unsigned j = 0; j < _order; j++) {
                    _indptr[j * _nnz + i] = nodes[i].coords[j];
                }
                _vals[i] = nodes[i].val;
            }

            for (unsigned i = 0; i < _nnz; i++) {
                free(nodes[i].coords);
            }
            free(nodes);
        }

        fclose(in);

        return _nnz < 1;
    }
};
}

//unsigned TensorIO::_coo_order;

#endif    // _MATRIXIO_HPP_