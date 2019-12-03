#!/usr/bin/env python3

import os
import re
import sys
import argparse as ap
import traceback as tb

from codegen.iegenlib import IEGenLib
from iegen_to_omega import to_omega

from tools import system

# Examples:
# https://github.com/CompOpt4Apps/IEGenLib/blob/master/doc/PythonScriptExamples/DoNotDistribute/lcpc12-iegenlib-paper.py

"""
{[i,j] -> [i,k,j]: 0 <= i < N_R && 0 <= k < N_C} apply {[i,j]: 0 <= i < N_R && index(i) <= j < index(i+1) && index(i) >= 0 && index(i) <= NNZ}

{[ii,kk,i,k,j]: 0 <= i < N_R && 0 <= k < N_C && index(i) <= j < index(i+1) && exists ri,ck :0 <= ri < R && i = ii*R+ri && 0 <= ck < C && k = kk*C+ck && N_C > C && N_R > R}
"""

def execute(cmd, code, verbose=True):
    (out, err) = system.run(cmd, code)
    if verbose:
        if len(out) > 0:
            print("Output:")
            print("=========================================================================================================\n")
            print(out)

        if len(err) > 0:
            print("Error:")
            print("=========================================================================================================\n")
            print(err)
    return (out, err)

def iegenlib_test():
    # Define sets and relations...
    icsr = 'Icsr := {[i,j]: 0 <= i < N_R && index(i) <= j < index(i+1)}'
    tdense = 'Tdense := {[i,j] -> [i,k,j]: 0 <= k < N_C && k = col(j)}'
    #idense = 'Idense := {[i, k, j]: k - col(j) = 0 && i >= 0 && k >= 0 && j - index(i) >= 0 && -i + N_R - 1 >= 0 && -k + N_C - 1 >= 0 && -j + index(i + 1) - 1 >= 0 };'

    fscsc = 'D := {[In_2, In_4, Out_2] : Li(In_4) = Out_2 && 0 <= In_2 && 0 <= In_4 && 0 <= Li(In_4) && 0 <= Lp(In_2) && 0 <= Lp(In_2 + 1) && In_2 + 1 < n && In_2 < Li(In_4) && In_4 < nnz && In_4 < Lp(In_2 + 1) && Lp(In_2) < In_4 && Li(In_4) < n && Lp(In_2) < nnz && Lp(In_2 + 1) < nnz && nnz > 2}'

    ic0csc = '{ [In_2, In_4, In_6, In_8, Out_2] : colPtr(Out_2) = In_6 && rowIdx(In_4) = Out_2 && rowIdx(In_8) = rowIdx(In_6) && 0 <= In_2 && 0 <= Out_2 && In_4 <= In_8 && colPtr(rowIdx(In_4)) <= colPtr(Out_2) && rowIdx(In_8 + 1) <= rowIdx(In_6) && In_2 < Out_2 && In_2 + 1 < n && In_4 < colPtr(In_2 + 1) && colPtr(In_2) < In_4 && In_8 < colPtr(In_2 + 1) && Out_2 + 1 < n && colPtr(Out_2) < colPtr(rowIdx(In_4) + 1) }'
    omcode = to_omega(ic0csc)
    print(omcode)

    # Perform the make-dense transformation with iegenlib:
    iegen = IEGenLib()
    iegen.add(fscsc)
    omcode = iegen.to_omega('D')

    omcalc = '/usr/local/bin/omegacalc'
    (omout, omerr) = execute(omcalc, omcode)
    print(omout)

    iegen.add(icsr)
    iegen.add(tdense)
    resid = 'Idense'
    result = iegen.apply('Tdense', 'Icsr', resid)
    print("IEGenLib: " + str(result))
    omcode = iegen.to_omega(resid)

    # Now hand the resulting relation to 'oc'
    (omout, omerr) = execute(omcalc, omcode)
    print(omout)

def main():
    iegenlib_test()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt as e: # Ctrl-C
        print("Closing gracefully on keyboard interrupt...")
    except Exception as e:
        print('ERROR: ' + str(e))
        tb.print_exc()
