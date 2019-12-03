# CSR-SpMV
domain: "[N_R,m,n] -> {S[i]: 0 <= i < N_R; T[i]: 0 <= i < N_R; U[i,j]: 0 <= i < N_R &&  m <= j < n}"
child:
  context: "[N_R,m,n] -> {[] : N_R > 0 && m > 0 && n > m}"
  child:
    set:
    - filter: "{ S[i]; T[i]; U[i,j] }"
      child:
        schedule: "[{ S[i]->[i]; T[i]->[i]; U[i,j]->[i] }]"
          child:
            sequence:
            - filter: "{S[i]}"
            - filter: "{T[i]}"
            - filter: "{U[i,j]}"
