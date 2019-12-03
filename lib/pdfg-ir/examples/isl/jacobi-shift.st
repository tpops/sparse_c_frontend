# [domain is the set that we want to genrate code for]:
# schedule looks like a union map with some restrictions
domain: "[T,N] -> { S1[t,i] : 1 <= t <= T && 1 <= i <= N }"
child:
  schedule: "[{ S1[t,i] -> [t] }]"
  child:
    schedule: "[{ S1[t,i] -> [t+i] }]"

