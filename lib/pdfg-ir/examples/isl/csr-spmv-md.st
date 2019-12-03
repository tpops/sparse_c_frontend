# CSR-SpMV (make-dense)
domain: "[N_R,N_C,m,n,c] -> {S[i]: 0 <= i < N_R; T[i]: 0 <= i < N_R; P[i,k,j]: 0 <= i < N_R && 0 <= k < N_C && m <= j < n; U[i,k,j]: 0 <= i < N_R && 0 <= k < N_C && m <= j < n}"
child:
  context: "[N_R,N_C,m,n,c] -> {[]: N_R > 0 && N_C > 0 && m > 0 && n > m && 0 <= c < N_C}"
  child:
    set:
    - filter: "{S[i]; T[i]; P[i,k,j]; U[i,k,j]}"
      child:
        schedule: "[{S[i]->[i]; T[i]->[i]; P[i,k,j]->[i]; U[i,k,j]->[i]}]"
          child:
            sequence:
            - filter: "{S[i]}"
            - filter: "{T[i]}"
            - filter: "{P[i,k,j]; U[i,k,j]}"
              child:
                schedule: "[{P[i,k,j]->[k]; U[i,k,j]->[k]}]"
                  child:
                    sequence:
                    - filter: "{P[i,k,j]; U[i,k,j]}"
                      child:
                        schedule: "[{P[i,k,j]->[j]; U[i,k,j]->[j]}]"
                        child:
                          sequence:
                          - filter: "{P[i,k,j]}"
                          - filter: "[c]->{U[i,k,j]: k=c}"
