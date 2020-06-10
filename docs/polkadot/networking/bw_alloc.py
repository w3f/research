"""
Basic bandwidth-allocation algorithm.

See bw_alloc_experiments.py in this directory for a more in-depth exploration
of the possible algorithms.
"""

from math import floor, isclose

def normalise(kv):
  """Normalise a set of values, so the sum is 1 but retain their proportions.

  Caller must ensure sum of values are non-zero.
  """
  s = sum(kv.values())
  return {k: v/s for (k, v) in kv.items()}

def allocate(total_avail, demand, guarantees):
  """Allocate resources, respecting relative guarantees.

  If any demander does not use up their guarantee, this will be allocated among
  the remainder according to their relative guarantees.
  """
  if any(not v > 0 for v in guarantees.values()):
    raise ValueError("invalid guarantees, not all +: %s" % guarantees)
  guarantees = normalise(guarantees)

  if any(v < 0 for v in demand.values()):
    raise ValueError("invalid demand, not all 0/+: %s" % demand)
  if total_avail < 0 :
    raise ValueError("invalid total_avail, not 0/+: %s" % total_avail)

  to_use = {k: 0 for k in demand}
  remaining_avail = total_avail
  remaining_demand = demand.copy()
  while remaining_avail > 0:
    used_this_round = 0
    relevant_remaining_demand = {k: d for (k, d) in remaining_demand.items() if d > 0}

    # relevant guarantees i.e. ignore roles with no remaining demand
    relevant_guarantees = normalise({k: v for (k, v) in guarantees.items()
                                     if k in relevant_remaining_demand.keys()})
    # iteration order doesn't matter due to our constraints for guarantees
    # see bw_alloc_experiments.py for details
    for k in demand:
      # remaining demand of k. we'll try to satisfy as much of this as possible
      if k not in relevant_remaining_demand: continue
      v = relevant_remaining_demand[k]
      # u is the max that can be satisfied this round, given the constraints
      u = float(remaining_avail) * relevant_guarantees[k]
      # x is what we'll actually satisfy, either u or v
      x = min(u, v)
      to_use[k] += x
      used_this_round += x
      remaining_demand[k] -= x

    remaining_avail -= used_this_round
    if used_this_round == 0: break
  # due to floating-point rounding, sometimes we are short by a few units,
  # just ignore it - if used_this_round == 0 we cannot improve any further.
  assert(sum(to_use.values()) <= total_avail)
  return to_use

def test_allocate(assert_allocate):
  ## test basic case with even guarantees
  A = 1000
  G = {0:1, 1:1, 2:1}
  assert_allocate(A, {0:900, 1:50, 2:120}, G, {0: 830, 1: 50, 2: 120})

  ## test uneven guarantees
  G = {0:8, 1:1, 2:1}
  # property 1
  assert_allocate(A, {0:500, 1:238, 2:262}, G, {0:500, 1:238, 2:262})
  # property 2
  assert_allocate(A, {0:900, 1:102, 2:102}, G, {0:800, 1:100, 2:100})
  # corner case with 0
  assert_allocate(A, {0:0, 1:0, 2:0}, G, {0:0, 1:0, 2:0})
  # more complex case
  result = assert_allocate(A, {0:900, 1:50, 2:120}, G)
  assert(result[0] > 800)
  assert(result[1] == 50)
  assert(result[2] > 100)
  print("tests passed")

if __name__ == "__main__":
  # run the test. we arrange it like this so we can run more complex tests on
  # the same test cases, in bw_alloc_experiments.py
  def assert_allocate(A, D, G, result=None):
    if result is None:
      result = allocate(A, D, G)
    assert(allocate(A, D, G) == result)
    return result
  test_allocate(assert_allocate)
