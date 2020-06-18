import bw_alloc
import itertools
from math import floor, isclose

def normalise(kv):
  """Normalise a set of values, so the sum is 1 but retain their proportions.

  Caller must ensure sum of values are non-zero.
  """
  s = sum(kv.values())
  return {k: v/s for (k, v) in kv.items()}

def allocate_general(total_avail, demand, choose_new_allocations):
  """General allocation algorithm, on a custom choose_allocation"""
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

    # this is a local utility for choose_allocation to call, whenever it has
    # decided on an allocation and wants to make it effective.
    # it updates to_use and our other bookkeeping variables.
    def allocate(k, x):
      nonlocal to_use, used_this_round, remaining_demand
      to_use[k] += x
      used_this_round += x
      remaining_demand[k] -= x

    # call the custom allocation chooser
    # it can assume all values in relevant_remaining_demand are non-zero
    choose_new_allocations(relevant_remaining_demand, remaining_avail, allocate)

    remaining_avail -= used_this_round
    if used_this_round == 0: break
  # due to floating-point rounding, sometimes we are short by a few units,
  # just ignore it - if used_this_round == 0 we cannot improve any further.
  assert(sum(to_use.values()) <= total_avail)
  return to_use

def allocate_bottom_up(total_avail, demand, guarantees):
  """Allocate resources, respecting relative guarantees.

  If any demander does not use up their guarantee, this will be allocated among
  the remainder according to their relative guarantees.
  """
  if any(not v > 0 for v in guarantees.values()):
    raise ValueError("invalid guarantees, not all +: %s" % guarantees)
  guarantees = normalise(guarantees)

  def alloc_bottom_up(relevant_remaining_demand, remaining_avail, allocate):
    nonlocal guarantees
    # relevant guarantees, i.e. ignore demanders with no remaining demand
    relevant_guarantees = normalise({k: v for (k, v) in guarantees.items()
                                     if k in relevant_remaining_demand.keys()})

    # figure out everyone's "fair share"
    avail_guarantees = sorted((v * remaining_avail, k)
                              for (k, v) in relevant_guarantees.items())
    # find the smallest demand that is <= its fair share
    # when we find it, calculate p, their proportional difference
    scale = 1
    for (v, k) in avail_guarantees:
      d = relevant_remaining_demand[k]
      if d <= v:
        scale = d / v
        assert scale <= 1
        break

    # allocate everyone according to their scaled guarantees.
    # for the k we selected in the previous step, this allocates all of their
    # demand and so they won't be part of the next iteration.
    # if we didn't select a k, it means our demand is too much and scale = 1.
    for (k, v) in relevant_guarantees.items():
      allocate(k, scale * v * remaining_avail)
  return allocate_general(total_avail, demand, alloc_bottom_up)

def allocate_prio(total_avail, demand, guarantees, priorities):
  """A previous version of allocate_bottom_up that had an extraneous
  "priorities" parameter which doesn't actually affect the result.
  """
  if any(not v > 0 for v in guarantees.values()):
    raise ValueError("invalid guarantees, not all +: %s" % guarantees)
  guarantees = normalise(guarantees)

  if set(priorities) != set(demand.keys()):
    raise ValueError("invalid priorities, doesn't match demand: %s" % priorities)

  def alloc_prio(relevant_remaining_demand, remaining_avail, allocate):
    nonlocal guarantees
    # relevant guarantees i.e. ignore roles with no remaining demand
    relevant_guarantees = normalise({k: v for (k, v) in guarantees.items()
                                     if k in relevant_remaining_demand.keys()})
    for k in priorities:
      # remaining demand of k. we'll try to satisfy as much of this as possible
      if k not in relevant_remaining_demand: continue
      v = relevant_remaining_demand[k]
      # u is the max that can be satisfied this round, given the constraints
      u = float(remaining_avail) * relevant_guarantees[k]
      # x is what we'll actually satisfy, either u or v
      x = min(u, v)
      allocate(k, x)
  return allocate_general(total_avail, demand, alloc_prio)

def assert_allocate(A, D, G, result=None):
  if result is None:
    result = allocate_bottom_up(A, D, G)
  assert(allocate_bottom_up(A, D, G) == result)
  prio = sorted(D.keys())
  assert(allocate_prio(A, D, G, prio) == result)
  # prio really does nothing
  for p in itertools.permutations(prio, len(prio)):
    assert(allocate_prio(A, D, G, p) == result)
  return result

if __name__ == "__main__":
  bw_alloc.test_allocate(assert_allocate)
