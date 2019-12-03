# Unroll & Jam (f=16)
domain: "[T,N] -> { S1[t,i]: 1 <= t <= T && 1 <= i <= N }"
child:
  context: "[N] -> {[] : N >= 32 && N % 16 = 0}"
    child:
      schedule: "[{ S1[t,i] -> [t] }, { S1[t,i] -> [i/16] }, \
                  { S1[t,i] -> [i] }]"
      options: "[N]->{ isolate[[] -> [a,b,c]]: 1 <= 16b && 16b+15 < N; \
                      [isolate[] -> unroll[2]] }"
