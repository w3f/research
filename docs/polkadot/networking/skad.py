from collections import defaultdict
from copy import deepcopy
from itertools import combinations
from pprint import pprint

def dinic_bfs(C, F, s, t):
  queue = []
  queue.append(s)
  level = defaultdict(lambda: 0)
  level[s] = 1
  while queue:
    k = queue.pop(0)
    for i in C[k].keys():
      if F[k][i] < C[k][i] and level[i] == 0:
        level[i] = level[k] + 1
        queue.append(i)
  return level

def dinic_dfs(C, F, t, level, k, flow):
  if k == t:
    return flow
  for i in C.keys(): # important to visit every node, not just successors
    if F[k][i] < C[k][i] and level[i] == level[k] + 1:
      curr_flow = min(flow, C[k][i] - F[k][i])
      temp_flow = dinic_dfs(C, F, t, level, i, curr_flow)
      if temp_flow > 0:
        F[k][i] = F[k][i] + temp_flow
        F[i][k] = F[i][k] - temp_flow
        return temp_flow
  return 0

def max_flow_dinic(C, s, t, max=float("inf")):
  F = defaultdict(lambda: defaultdict(lambda: 0)) # flow graph, successor-map
  flow = 0
  while True:
    level = dinic_bfs(C, F, s, t)
    if not level[t]: break
    flow += dinic_dfs(C, F, t, level, s, max)
  return (flow, F)

def tests_max_flow_dinic():
  C = defaultdict(lambda: defaultdict(lambda: 0))
  C["S"][1] = 3
  C["S"][2] = 3
  C[1][2] = 2
  C[1][3] = 3
  C[2][4] = 2
  C[3][4] = 4
  C[3]["T"] = 2
  C[4]["T"] = 2
  C["T"]["T"] = 3
  assert (max_flow_dinic(C, "S", "T")[0] == 4)

  D = defaultdict(lambda: defaultdict(lambda: 0))
  D["S"][1] = 1
  D["S"][2] = 1
  D["S"][3] = 1
  D[1][4] = 1
  D[2][5] = 1
  D[3][6] = 1
  D[4][7] = 1
  D[4][8] = 1
  D[4][9] = 1
  D[5][7] = 1
  D[5][8] = 1
  D[5][9] = 1
  D[6][7] = 1
  D[6][8] = 1
  D[6][1] = 1
  D[7]["T"] = 1
  D[8]["T"] = 1
  D[9]["T"] = 1
  assert (max_flow_dinic(D, "S", "T")[0] == 3)

## Kademlia stuff follows

K = 20

def distance(a, b):
  return a ^ b

def pprintd(d):
  pprint({k: dict(v) for (k, v) in d.items()})

FLOW_SRC = "self"
FLOW_SINK = "target"

class SKadLookup(object):

  def __init__(self, init_queries, target_key, prioritise_unique_results=False):
    # query flow graph, capacities
    self.query_succ = { FLOW_SRC: set(init_queries) }

    # nodes queried that have given a reply
    self.query_result = set()
    # nodes queried that have failed, i.e. timed out
    self.query_failed = set()
    # nodes queried that are awaiting a reply
    # this should be size (d - query_gap)
    self.query_expect = set()
    # number of queries missing. this can happen when the initial nodes all
    # return too-few results to sustain a multipath of width d
    self.query_gap = 0

    # TODO: this could be implemented by tweaking the capacities, leave it for now
    self.prioritise_unique_results = prioritise_unique_results
    if prioritise_unique_results:
      raise NotImplementedError()
    self.target_key = target_key

    for nodeId in init_queries:
      self.query_succ[nodeId] = {}
      self.launch_query("init %3s" % target_key, nodeId)

  def distance_to(self, n):
    return distance(n, self.target_key)

  def launch_query(self, ctx, nodeId):
    self.query_expect.add(nodeId)
    # fake send, for our testing purposes
    print(ctx, ": sending query to node %s" % nodeId)

  def warn_no_query(self, ctx):
    print(ctx, ": too-few results to select a next peer") # TODO more error detail

  def max_flow_wrong(self, matching, verbose=False):
    # construct the capacity graph
    # note that the order is important, we want the max_flow algorithm to
    # traverse the closest ones first.
    # FIXME: sadly this fails, including some asserts below
    # we need max-saturating-flow not max-flow
    MAX = 100000000000 # TODO: should calculate this better

    C = defaultdict(lambda: defaultdict(lambda: 0))
    for k, succs in self.query_succ.items():
      for succ in sorted(succs, key=self.distance_to):
        C[k][succ] = MAX
      if k != FLOW_SRC and matching(k):
        C[k][FLOW_SINK] = MAX - self.distance_to(k)

    # calculate max flow
    (f, max_flow) = max_flow_dinic(C, FLOW_SRC, FLOW_SINK)
    if verbose:
      print("cap & flow:")
      pprintd(C)
      pprintd(max_flow)

    # extract results
    results = set()
    for k in C.keys():
      if k not in (FLOW_SRC, FLOW_SINK) and matching(k):
        # FIXME: sadly this doesn't always work, partial flows can be maximal
        if max_flow[k][FLOW_SINK] == MAX - self.distance_to(k):
          results.add(k)

    return sorted(results, key=self.distance_to)

  def max_sat_flow(self, matching, verbose=False):
    C = defaultdict(lambda: defaultdict(lambda: 0))
    for k, succs in self.query_succ.items():
      if k == FLOW_SRC:
        for succ in sorted(succs, key=self.distance_to):
          C[k][succ] = 1
      elif succs:
        # restrict all nodes to only being on 1 flow, by converting them into
        # two nodes (k) and (k, "out") with capacity 1 between them
        C[k][(k, "out")] = 1
        for succ in sorted(succs, key=self.distance_to):
          C[(k, "out")][succ] = 1

    candidates = list(k for k in self.query_succ.keys() if k != FLOW_SRC and matching(k))
    wanted = len(self.query_succ[FLOW_SRC]) - self.query_gap
    if verbose:
      print("candidates:", candidates, "wanted:", wanted)

    for subset in combinations(sorted(candidates, key=self.distance_to), wanted):
      C_ = deepcopy(C)
      for k in subset:
        C_[k][FLOW_SINK] = 1
      (max_flow, max_flow_graph) = max_flow_dinic(C_, FLOW_SRC, FLOW_SINK)
      if verbose:
        print(subset)
        pprintd(C_)
        print("max flow:", max_flow)
        pprintd(max_flow_graph)
      if max_flow == wanted:
        return list(subset)
    return []

  def select_next_query(self, verbose=False):
    next_to_query = self.max_sat_flow(
      lambda k: k not in self.query_result and
                k not in self.query_failed, verbose=verbose)
    return [q for q in next_to_query if q not in self.query_expect]

  def recv_result(self, peer, reply, verbose=False):
    if verbose:
      print("RECV RESULT:", peer, reply)

    if peer not in self.query_expect:
      raise ValueError("unexpected reply from peer %s: %s" % (peer, reply))

    if peer in self.query_result:
      raise ValueError("duplicate reply from peer %s: %s" % (peer, reply))

    if peer in self.query_failed:
      raise ValueError("ignoring too-late reply from peer %s: %s" % (peer, reply))

    if reply is None:
      # query failed, record it as failed
      self.query_succ[peer] = set()
      self.query_failed.add(peer)

    else:
      # check that all replies are closer to the target, with exemption for
      # peers that are already very close to the target
      old_d = self.distance_to(peer)
      if any(self.distance_to(r) >= self.distance_to(peer) > K for r in reply):
        # probably malicious
        raise ValueError("divergent reply from peer %s: %s" % (peer, reply))

      # everything OK, now store the reply in the query graph
      self.query_succ[peer] = set(reply)
      for r in reply:
        self.query_succ.setdefault(r, {}) # ensure r is in query_succ.keys()

      self.query_result.add(peer)

    assert (len(self.query_expect) + self.query_gap == len(self.query_succ[FLOW_SRC]))
    self.query_expect.remove(peer)
    candidates = self.select_next_query(verbose=verbose)

    if not candidates:
      # not enough data returned by neighbours to select a next_peer.
      # record this to keep track of it, and emit a warning.
      self.warn_no_query("recv %3s" % peer)
      self.query_gap += 1
      return None
    else:
      next_peer = candidates[0]
      # make the actual query
      self.launch_query("recv %3s" % peer, next_peer)
      assert (len(self.query_expect) + self.query_gap == len(self.query_succ[FLOW_SRC]))
      return next_peer

  def current_best(self, include_waiting=False, verbose=False):
    return self.max_sat_flow(lambda k:
        (k in self.query_result or k in self.query_expect)
        if include_waiting else
        (k in self.query_result), verbose=verbose)

def tests_skademlia():
  print("----")
  q = SKadLookup([4,5,6], 0)
  assert(q.recv_result(4, {1,2,3}) == 1)
  assert(q.recv_result(5, {1,2,3}) == 2)
  assert(q.recv_result(6, {4,1,2}) == 3)
  # ^ corner case, correctly selects 3 even though 3 not part of 6's reply
  assert(q.current_best() == [4,5,6])
  assert(q.current_best(True) == [1,2,3]) # this assert fails if using max_flow_wrong

  print("----")
  q = SKadLookup([5,6,7,8], 0)
  assert(q.recv_result(5, {3,4}) == 3)
  assert(q.recv_result(6, {3,4}) == 4)
  assert(q.recv_result(7, {3,4}) == None)
  assert(q.recv_result(8, {3,4}) == None)
  assert(q.recv_result(3, {1}) == 1)
  assert(q.recv_result(4, {1}) == None)
  # ^ selects None since we actually don't have enough results
  assert(q.query_gap == 3)

  print("----")
  q = SKadLookup([5,6,7], 0)
  assert(q.recv_result(5, {4}) == 4)
  assert(q.recv_result(4, {1,2,3}) == 1)
  assert(q.recv_result(6, {4}) == None) # e.g. not 2
  assert(q.recv_result(7, {4}) == None)
  # this test fails if "restrict nodes to only being on 1 flow" is not implemented
  assert(q.query_gap == 2)
  assert(q.current_best() == [4])
  assert(q.current_best(True) == [1])

  print("----")
  q = SKadLookup([10,11,12], 0)
  assert(q.recv_result(10, {5,6}) == 5)
  assert(q.recv_result(11, {6,7}) == 6)
  assert(q.recv_result(12, {8}) == 8)
  assert(q.recv_result(5, {1,2}) == 1)
  assert(q.recv_result(1, None) == 2)
  assert(q.recv_result(2, None) == 7)
  assert(q.current_best() == [5, 11, 12])
  assert(q.current_best(True) == [5, 6, 8])
  # ^ corner case involving backtracking and failure - correctly selects 7,
  # even though it's unrelated to the "10 -> 5 -> 1" path, because 6 was
  # already selected previously

if __name__ == "__main__":
  tests_max_flow_dinic()
  tests_skademlia()
