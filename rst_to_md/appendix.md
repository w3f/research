# Diagrams

<div class="graphviz">

backtrack-1-1.dot

</div>

<div class="graphviz">

backtrack-1-2.dot

</div>

<div class="graphviz">

backtrack-1-3-bad.dot

</div>

<div class="graphviz">

backtrack-1-3-good.dot

</div>

<div class="graphviz">

backtrack-2-1.dot

</div>

<div class="graphviz">

backtrack-2-2.dot

</div>

<div class="graphviz">

backtrack-2-3-bad.dot

</div>

<div class="graphviz">

backtrack-2-3-good.dot

</div>

<div class="graphviz">

terminus-1-bad.dot

</div>

<div class="graphviz">

terminus-1-good.dot

</div>

<div class="graphviz">

results-1-bad.dot

</div>

<div class="graphviz">

results-1-good.dot

</div>

# Code listings

## S-Kademlia max-flow-min-cost algorithm

``` py
from collections import defaultdict
from copy import deepcopy
from functools import reduce
from itertools import combinations
from math import gcd
from pprint import pprint

class ddict0(dict):
  """A dict that returns 0 for missing keys BUT DOES NOT INSERT THEM.

  This means we can use [k] instead of .get(k, 0), without adding extra edges
  to the graph which would happen with defaultdict.
  """
  def __getitem__(self, key):
    if key in self:
      return super().__getitem__(key)
    else:
      return 0

def check_keys(d):
  k1 = set(d.keys())
  k2 = set(s for succ in d.values() for s in succ)
  assert k2.issubset(k1)

def ensure_keys_ddict0(d):
  k1 = set(d.keys())
  k2 = set(s for succ in d.values() for s in succ)
  for k in k2.difference(k1):
    d[k] = ddict0()

def pprintd(d):
  pprint({k: {k_: v for (k_, v) in kv.items()} for (k, kv) in d.items()})

def dinic_bfs(Cap, Flow, src):
  queue = []
  queue.append(src)
  level = ddict0()
  level[src] = 1
  while queue:
    k = queue.pop(0)
    for i in Cap.keys(): # important to visit every node, not just successors
      if Flow[k][i] < Cap[k][i] and level[i] == 0: # 0 means not-yet-visited
        level[i] = level[k] + 1
        queue.append(i)
  return level

def dinic_dfs(Cap, Flow, dst, level, k, flow):
  if k == dst:
    return flow
  for i in Cap.keys(): # important to visit every node, not just successors
    if Flow[k][i] < Cap[k][i] and level[i] == level[k] + 1:
      curr_flow = min(flow, Cap[k][i] - Flow[k][i])
      temp_flow = dinic_dfs(Cap, Flow, dst, level, i, curr_flow)
      if temp_flow > 0:
        Flow[k][i] += temp_flow
        Flow[i][k] -= temp_flow
        return temp_flow
  return 0

def max_flow_dinic(Cap, src, dst, max=float("inf")):
  # https://www.geeksforgeeks.org/dinics-algorithm-maximum-flow/
  # the algorithm has to occasionally iterate through all the nodes;
  # check that Cap.keys() does contain all the nodes so we can use it later
  check_keys(Cap)
  Flow = defaultdict(ddict0) # flow graph, successor-map
  flow = 0
  while True:
    level = dinic_bfs(Cap, Flow, src)
    if not level[dst]: break
    flow += dinic_dfs(Cap, Flow, dst, level, src, max)
  # residual graph is not explicitly expressed in this implementation of the
  # algorithm, but it can be calculated as (C - F) or residual_graph(C, F)
  #
  # note that Flow contains reverse edges with negative flows, one for every
  # forward edge in the actual flow. if you want to calculate the cost of the
  # flow against a rate graph, be sure to filter out the negative edges first.
  return (flow, Flow)

def residual_graph(Cap, Flow):
  Res = deepcopy(Cap)
  for k, kc in Cap.items():
    for i, _ in kc.items():
      Res[i][k] = Res[i][k] # ensure any 0 value exists for the opposite edge
  # perform subtraction
  for k, kf in Flow.items():
    for i, f in kf.items():
      Res[k][i] -= f
  return Res

def tests_max_flow_dinic():
  C = defaultdict(ddict0)
  C["S"][1] = 3
  C["S"][2] = 3
  C[1][2] = 2
  C[1][3] = 3
  C[2][4] = 2
  C[3][4] = 4
  C[3]["T"] = 2
  C[4]["T"] = 2
  C["T"] = ddict0()
  ensure_keys_ddict0(C)
  assert (max_flow_dinic(C, "S", "T")[0] == 4)

  D = defaultdict(ddict0)
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
  ensure_keys_ddict0(D)
  assert (max_flow_dinic(D, "S", "T")[0] == 3)

  E = defaultdict(ddict0)
  E["S"][1] = 11
  E["S"][2] = 12
  E[1][2] = 10
  E[1][3] = 12
  E[2][1] = 4
  E[2][4] = 14
  E[3][2] = 9
  E[3]["T"] = 20
  E[4][3] = 7
  E[4]["T"] = 4
  ensure_keys_ddict0(E)
  assert (max_flow_dinic(E, "S", "T")[0] == 23)

def residual_rates(Cap, Res, Rates):
  # rates in a residual graph
  ResRates = defaultdict(ddict0)
  # be very careful to match the edges in Cap
  for k, kv in Cap.items():
    for i, _ in kv.items():
      # if res is 0 we can't push flow back, so ignore it
      if Res[k][i] != 0:
        ResRates[k][i] = Rates[k][i] - Rates[i][k]
      if Res[i][k] != 0:
        ResRates[i][k] = Rates[i][k] - Rates[k][i]
  return ResRates

def graph_cost(G, Rates):
  cost = 0
  for k, kc in G.items():
    for i, c in kc.items():
      cost += c * Rates[k][i]
  return cost

def get_negcycle(G, max=float("inf")):
  # https://cp-algorithms.com/graph/finding-negative-cycle-in-graph.html
  # based on Bellman-Ford
  #pprint(G)
  D = defaultdict(lambda: 0)
  pred = defaultdict(lambda: None)

  # relaxation
  for _ in list(G.keys()):
    changed = None
    for k, kd in G.items():
      for i, d in kd.items():
        if D[i] > D[k] + d:
          D[i] = D[k] + d
          pred[i] = k
          changed = i

  if changed is None:
    return []
  for _ in G.keys():
    changed = pred[changed]

  # get the cycle. most basic implementations of Bellman-Ford don't have this
  cycle = []
  v = changed
  while True:
    cycle.append(v)
    if v == changed and len(cycle) > 1:
      break
    v = pred[v]
  #print(cycle)
  return list(reversed(cycle))

def max_flow_min_cost(Cap, Rates, src, dst, max=float("inf"), verbose=False):
  # https://courses.csail.mit.edu/6.854/06/scribe/s12-minCostFlowAlg.pdf
  (max_flow, Flow) = max_flow_dinic(Cap, src, dst)

  # to find min-cost, first convert into a circulation problem
  Cap[dst][src] = max_flow
  Rates[dst][src] = -(sum(r for kr in Rates.values() for r in kr.values()) + 1)
  Flow[dst][src] = max_flow
  Flow[src][dst] = -max_flow
  flow_cost = graph_cost(Flow, Rates)

  Res = residual_graph(Cap, Flow)
  # keep adding negative-cost cycles to the flow, until there is none left
  while True:
    # construct residual rates graph
    ResRates = residual_rates(Cap, Res, Rates)
    # note: a lot of resources will talk about finding a "negative-cost" cycle,
    # this is confusing terminology - more precisely it's a "negative-rate"
    # cycle we want, i.e. not multiplied by the residue (which is different for
    # each edge). the reason is, later we need to push flow back through this
    # cycle and of course we have to push an *equal* amount of flow per edge,
    # the cost of this flow being determined by the rate of the cycle, i.e. the
    # sum of rates across the edges in the cycle.
    negcycle = get_negcycle(ResRates, max=max)
    if not negcycle: break

    # add the cycle to F, and update R
    edges = list(zip(negcycle[:-1], negcycle[1:]))
    flow = min(Res[u][v] for (u, v) in edges)
    assert flow > 0 # fails if we didn't ignore 0-residue edges in residual_rates
    for (u, v) in edges:
      Flow[u][v] += flow
      Flow[v][u] -= flow
      Res[u][v] -= flow
      Res[v][u] += flow

    # check that new cost of F is strictly lower than previous cost
    cost = graph_cost(Flow, Rates)
    assert (cost < flow_cost)
    flow_cost = cost

  # clean up F a bit before returning it
  del Flow[src][dst]
  del Flow[dst][src]
  min_cost = graph_cost(Flow, Rates)
  # reverse our changes to Cap & Rates
  del Cap[dst][src]
  del Rates[dst][src]
  #pprintd(Cap)
  #pprintd(Flow)
  return (max_flow, min_cost, Flow)

def tests_max_flow_min_cost():
  C = defaultdict(ddict0)
  C["S"][1] = 1
  C["S"][4] = 1
  C[1][2] = 1
  C[1][3] = 1
  C[2]["T"] = 1
  C[3]["T"] = 1
  C[4]["T"] = 1
  ensure_keys_ddict0(C)
  CR = defaultdict(ddict0)
  CR[2]["T"] = 2
  CR[3]["T"] = 1
  CR[4]["T"] = 3
  assert (max_flow_min_cost(C, CR, "S", "T")[0:2] == (2, 4))


## Kademlia stuff follows

K = 20

def distance(a, b):
  return a ^ b

FLOW_SRC = "self"
FLOW_SINK = "target"

class SKadLookup(object):

  def __init__(self, init_queries, target_key, num_parallel=None, prioritise_unique_results=False):
    self.target_key = target_key

    # parallelism, the main parameter of this algorithm
    if num_parallel is None:
      num_parallel = len(init_queries)
    if len(init_queries) < num_parallel:
      raise ValueError("unsupported: len(init_queries) < num_parallel")
    self.num_parallel = num_parallel

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
    # return too-few results to sustain a max-flow of d throughout the query
    self.query_gap = 0

    for nodeId in init_queries:
      self.query_succ[nodeId] = {}
    for q in self._get_best_queries(lambda k: True):
      self.launch_query("init %3s" % target_key, q)

  def distance_to(self, n):
    return distance(n, self.target_key)

  def launch_query(self, ctx, nodeId):
    self.query_expect.add(nodeId)
    # fake send, for our testing purposes
    print(ctx, ": sending query to node %s" % nodeId)

  def warn_no_query(self, ctx):
    print(ctx, ": too-few results to select a next peer") # TODO more error detail

  def _get_best_queries(self, matching, verbose=False):
    # construct input for max-flow-min-cost, as per our security model
    C = defaultdict(ddict0)
    for k, succs in self.query_succ.items():
      if succs:
        # restrict all nodes to only being on one "disjoint path" by converting
        # them into two nodes (k) and (k, "out") with capacity 1
        # across the edge between them
        if k == FLOW_SRC:
          # source has num_parallel flow
          C[k][(k, "out")] = self.num_parallel
        else:
          C[k][(k, "out")] = 1
        for succ in sorted(succs, key=self.distance_to):
          C[(k, "out")][succ] = 1
    # every candidate has capacity := num_parallel to the sink
    candidates = list(k for k in self.query_succ.keys() if k != FLOW_SRC and matching(k))
    Rates = defaultdict(ddict0)
    for k in candidates:
      C[k][FLOW_SINK] = 1
      Rates[k][FLOW_SINK] = self.distance_to(k)
    # In summary we have:
    # - capacity num_parallel from the source
    # - capacity |candidates| to the sink
    # In the best case, a max-flow will have num_parallel flow as that is the
    # maximum capacity available from the source. We will achieve less if e.g.
    # the query graph was bottlenecked at one node.
    # The other things above encode the constraints to solve for S-Kademlia:
    # - split-nodes -> disjoint paths
    # - min-cost -> lowest distance
    # Moreover due to the min-cost constraint, it is not possible for a flow to
    # be "split" across two final nodes - all possible flows will fully-use the
    # capacity of a final node, i.e. the one that has the lower cost.

    # run max-flow-min-cost
    ensure_keys_ddict0(C)
    (max_flow, min_cost, F) = max_flow_min_cost(C, Rates, FLOW_SRC, FLOW_SINK, verbose=verbose)

    queries = [k for k in candidates if F[k][FLOW_SINK] > 0]
    # sort by flow (descending) then by distance (ascending)
    queries.sort(key=self.distance_to)
    assert all(F[q][FLOW_SINK] == 1 for q in queries)
    assert len(queries) <= self.num_parallel
    assert max_flow == len(queries)
    return queries

  def select_next_query(self, verbose=False):
    next_to_query = self._get_best_queries(
      lambda k: k not in self.query_result and
                k not in self.query_failed, verbose=verbose)
    expected = self.num_parallel - self.query_gap
    if len(next_to_query) < expected:
        # sanity check: if we got fewer than expected from max-flow-min-distance,
        # this means we've hit a(nother) bottleneck in our query graph and
        # we're actually already querying everything there is to query
        assert all(q in self.query_expect for q in next_to_query)
    # filter out stuff we're already querying. if these leaves us with nothing
    # then it means we've hit a bottleneck in the query graph
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

    assert (len(self.query_expect) + self.query_gap == self.num_parallel)
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
      assert (len(self.query_expect) + self.query_gap == self.num_parallel)
      return next_peer

  def peek_best_queries(self, verbose=False):
    return self._get_best_queries(lambda k: k not in self.query_failed, verbose=verbose)

  def _get_best_results(self, termini, matching, verbose=False):
    # filter out failed successors, add self as implicit successor
    query_succ = {k: {k} | {s for s in self.query_succ[k] if matching(s)} for k in termini}

    # every terminus is allowed to push an equal amount of flow
    # calculate normalising factors to make this effective
    lcm = reduce(lambda x, y: x*y//gcd(x,y), (len(query_succ[k]) for k in termini))
    norm = {k: lcm // len(query_succ[k]) for k in termini}
    #k not in self.query_failed

    # construct input for max-flow-min-cost
    C = defaultdict(ddict0)
    Rates = defaultdict(ddict0)
    all_succ = {s for k in termini for s in query_succ[k]}
    for k in termini:
      C[FLOW_SRC][(k, "out")] = lcm
      for s in list(query_succ[k]):
        C[(k, "out")][s] = norm[k]
    for s in all_succ:
      C[s][FLOW_SINK] = lcm * len(termini)
      Rates[s][FLOW_SINK] = self.distance_to(s)

    # run max-flow-min-cost
    ensure_keys_ddict0(C)
    (max_flow, min_cost, F) = max_flow_min_cost(C, Rates, FLOW_SRC, FLOW_SINK, verbose=verbose)

    results = [(k, F[k][FLOW_SINK]) for k in C.keys() if F[k][FLOW_SINK] > 0]
    results.sort(key=lambda v: (-v[1], self.distance_to(v[0])))
    assert max_flow == lcm * len(termini)
    return results

  def maybe_get_results(self, include_waiting=True, flows=False, verbose=False):
    """Check if the query is in a state where it can be finished."""
    queries = self.peek_best_queries(verbose=verbose)
    if any(q not in self.query_result for q in queries):
      return None # some queries are still being waited on
    matching = (lambda k:
        (k not in self.query_failed) # includes result nodes, queried nodes, and unqueried nodes
        if include_waiting else
        (k in self.query_result))
    results = self._get_best_results(queries, matching, verbose=verbose)
    return results if flows else [r[0] for r in results]

def tests_skademlia():
  print("----")
  q = SKadLookup([4,5,6], 0)
  assert(q.recv_result(4, {1,2,3}) == 1)
  assert(q.recv_result(5, {1,2,3}) == 2)
  assert(q.recv_result(6, {4,1,2}) == 3)
  # ^ corner case, correctly selects 3 even though 3 not part of 6's reply
  assert(q.peek_best_queries() == [1,2,3])
  # ^ this assert fails if using max-flow without cost considerations

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
  # ^ this test fails if "restrict nodes to only being on 1 flow" is not implemented
  assert(q.query_gap == 2)
  assert(q.peek_best_queries() == [1,4,5])

  print("----")
  q = SKadLookup([10,11,12], 0)
  assert(q.recv_result(10, {5,6}) == 5)
  assert(q.recv_result(11, {6,7}) == 6)
  assert(q.recv_result(12, {8}) == 8)
  assert(q.recv_result(5, {1,2}) == 1)
  assert(q.recv_result(1, None) == 2)
  assert(q.recv_result(2, None) == 7)
  assert(q.peek_best_queries() == [5, 6, 8])
  assert(q.maybe_get_results(True) is None)
  assert(q.recv_result(6, {}) == None)
  assert(q.recv_result(8, {}) == None)
  assert(q.maybe_get_results(True) == [5, 6, 8])
  # ^ corner case involving backtracking and failure - correctly selects 7,
  # even though it's unrelated to the "10 -> 5 -> 1" path, because 6 was
  # already selected previously

  # maybe_get_results at different times, and with overlapping results
  print("----")
  q = SKadLookup([1,2,3], 0)
  assert(q.recv_result(1, {2,3,4,5,6,7}) == 4)
  assert(q.maybe_get_results() == None)
  assert(q.recv_result(2, {1,3,5,6,7,8}) == 5)
  assert(q.maybe_get_results() == None)
  assert(q.recv_result(3, {2,9,10,11,12,13}) == 9)
  assert(q.maybe_get_results(True) == [2, 3, 1, 5, 6, 7, 4, 8, 9, 10, 11, 12, 13])

  # query where len(init_queries) != num_parallel
  print("----")
  q = SKadLookup([5,6,7,8,9], 0, num_parallel=3)
  assert(q.query_expect == set([5,6,7]))
  assert(q.recv_result(5, {1,2}) == 1)
  assert(q.recv_result(7, None) == 8)
  assert(q.recv_result(6, {10}) == 9)

if __name__ == "__main__":
  tests_max_flow_dinic()
  tests_max_flow_min_cost()
  tests_skademlia()
```
