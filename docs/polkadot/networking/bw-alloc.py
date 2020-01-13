from math import floor, isclose

def calculate_to_use(R, use_limit, total_avail, demand):
  if not isclose(sum(use_limit.values()), 1.0):
    raise ValueError("invalid use_limit, sum not 1: %s" % use_limit)
  if any(not v > 0 for v in use_limit.values()):
    raise ValueError("invalid use_limit, not all +: %s" % use_limit)
  to_use = {r: 0 for r in R}
  remaining_avail = total_avail
  remaining_demand = demand.copy()
  while remaining_avail > 0:
    # normalise use_limits i.e. ignore roles with no remaining demand
    relevant_use_limits = sum(v for (r, v) in use_limit.items() if remaining_demand[r] > 0)
    # division below is safe; relevant_use_limits can only be 0 if normalised_use_limit is an empty dict
    normalised_use_limit = {r: (v / relevant_use_limits) for (r, v) in use_limit.items() if remaining_demand[r] > 0}
    used_this_round = 0
    for r in R:
      # remaining demand of r. we'll try to satisfy as much of this as possible
      v = remaining_demand[r]
      if v == 0: continue
      # u is the max that can be satisfied this round, given the constraints
      u = floor(float(remaining_avail) * normalised_use_limit[r])
      # x is what we'll actually satisfy, either u or v
      x = min(u, v)
      to_use[r] += x
      used_this_round += x
      remaining_demand[r] -= x
    remaining_avail -= used_this_round
    # due to floor() sometimes we are short by a few bytes, just ignore it and prevent infinite loop
    if used_this_round == 0: break
    # now we loop back.
    # if any r didn't use up its use_limit in this iteration (i.e. v < u) then
    # this is now available for another r to use up in the next iteration
  assert(sum(to_use.values()) <= total_avail)
  return to_use

R = [0,1,2]
U = {0:0.8, 1:0.1, 2:0.1}
A = 1000

# property 1
assert(calculate_to_use(R, U, A, {0:500, 1:238, 2:262}) == {0:500, 1:238, 2:262})
# property 2
assert(calculate_to_use(R, U, A, {0:900, 1:102, 2:102}) == {0:800, 1:100, 2:100})
# corner case with 0
assert(calculate_to_use(R, U, A, {0:0, 1:0, 2:0}) == {0:0, 1:0, 2:0})
# more complex case
assert(calculate_to_use(R, U, A, {0:900, 1:50, 2:120})[0] > 800)
assert(calculate_to_use(R, U, A, {0:900, 1:50, 2:120})[1] == 50)
assert(calculate_to_use(R, U, A, {0:900, 1:50, 2:120})[2] > 100)
