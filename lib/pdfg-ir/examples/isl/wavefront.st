domain: "[n, m] -> { S1[i, j] : i >= 1 and i <= n and j >= 1 and j <= m }"
child:
  context: "[n, m] -> { [] }"
  child:
    schedule: "[n, m] -> [{ S1[i, j] -> [(i + j)] }, { S1[i, j] -> [(i)] }]"
    options: "[n, m] -> { separate[i] }"
