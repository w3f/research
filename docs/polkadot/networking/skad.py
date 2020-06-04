from collections import defaultdict
from copy import deepcopy
from itertools import combinations
from pprint import pprint

def pprintd(d):
  pprint({k: {k_: v for (k_, v) in kv.items() if v != 0} for (k, kv) in d.items()})

def dinic_bfs(Cap, Flow, src):
  queue = []
  queue.append(src)
  level = defaultdict(lambda: 0)
  level[src] = 1
  while queue:
    k = queue.pop(0)
    for i in Cap[k].keys():
      if Flow[k][i] < Cap[k][i] and level[i] == 0:
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
  Flow = defaultdict(lambda: defaultdict(lambda: 0)) # flow graph, successor-map
  flow = 0
  while True:
    level = dinic_bfs(Cap, Flow, src)
    if not level[dst]: break
    flow += dinic_dfs(Cap, Flow, dst, level, src, max)
    #pprintd(Flow)
  # residual graph is not explicitly expressed in this implementation of the
  # algorithm, but it can be calculated as (C - F) or residual_graph(C, F)
  #
  # note that Flow contains reverse edges with negative flows, one for every
  # forward edge in the actual flow. if you want to calculate the cost of the
  # flow against a rate graph, be sure to filter out the negative edges first.
  return (flow, Flow)

def residual_graph(Cap, Flow):
  Res = deepcopy(Cap)
  for k, kf in Flow.items():
    for i, f in kf.items():
      Res[k][i] -= f
  return Res

def residual_rates(Rates):
  # rates in a residual graph
  ResRates = defaultdict(lambda: defaultdict(lambda: 0))
  for k, kr in Rates.items():
    for i in kr.keys():
      ResRates[k][i] = Rates[k][i] - Rates[i][k]
  return ResRates

def graph_costs(G, Rates):
  Cost = defaultdict(lambda: defaultdict(lambda: 0))
  for k, kv in G.items():
    for i, v in kv.items():
      # don't create edges of cost 0 that don't exist in the input graph, which
      # breaks the negative cycle detection later
      if v != 0:
        Cost[k][i] = v * Rates[k][i]
  return Cost

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
  for _ in G.keys():
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

def max_flow_min_cost(Cap, Rates, src, dst, max=float("inf")):
  # https://courses.csail.mit.edu/6.854/06/scribe/s12-minCostFlowAlg.pdf
  (max_flow, Flow) = max_flow_dinic(Cap, src, dst)

  # to find min-cost, first convert into a circulation problem
  Cap[dst][src] = max_flow
  Rates[dst][src] = -(sum(r for kr in Rates.values() for r in kr.values()) + 1)
  Flow[dst][src] = max_flow
  Flow[src][dst] = -max_flow
  flow_cost = graph_cost(Flow, Rates)

  Res = residual_graph(Cap, Flow)
  ResRates = residual_rates(Rates)
  # keep adding negative-cost cycles to the flow, until there is none left
  while True:
    # construct residual cost graph
    ResCost = graph_costs(Res, ResRates)
    negcycle = get_negcycle(ResCost, max=max)
    if not negcycle: break

    # add the cycle to F, and update R
    edges = list(zip(negcycle[:-1], negcycle[1:]))
    flow = min(Res[u][v] for (u, v) in edges)
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

  E = defaultdict(lambda: defaultdict(lambda: 0))
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
  assert (max_flow_dinic(E, "S", "T")[0] == 23)

def tests_max_flow_min_cost():
  C = defaultdict(lambda: defaultdict(lambda: 0))
  C["S"][1] = 1
  C["S"][4] = 1
  C[1][2] = 1
  C[1][3] = 1
  C[2]["T"] = 1
  C[3]["T"] = 1
  C[4]["T"] = 1
  CR = defaultdict(lambda: defaultdict(lambda: 0))
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

  def __init__(self, init_queries, target_key, use_min_cost=True, prioritise_unique_results=False):
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

    self.target_key = target_key
    # use max-flow-min-cost, otherwise use max-flow and brute-force over the costs
    self.use_min_cost = use_min_cost
    # TODO: this could be implemented by tweaking the costs, leave it out for now
    self.prioritise_unique_results = prioritise_unique_results
    if prioritise_unique_results:
      raise NotImplementedError()

    for nodeId in init_queries:
      self.query_succ[nodeId] = {}
      self.launch_query("init %3s" % target_key, nodeId)

  def num_parallel(self):
    return len(self.query_succ[FLOW_SRC])

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

  def max_flow_min_distance(self, matching, honour_query_gap=True, ask_results=None, verbose=False):
    if ask_results is None:
      ask_results = self.num_parallel()

    use_min_cost = self.use_min_cost
    if not self.use_min_cost and ask_results != self.num_parallel():
      use_min_cost = True
      print("use_min_cost = False only supported for ask_results == num_parallel, ignoring")

    C = defaultdict(lambda: defaultdict(lambda: 0))
    for k, succs in self.query_succ.items():
      if k == FLOW_SRC:
        for succ in sorted(succs, key=self.distance_to):
          C[k][succ] = ask_results
      elif succs:
        # restrict all nodes to only being on 1 flow, by converting them into
        # two nodes (k) and (k, "out") with capacity 1 between them
        C[k][(k, "out")] = ask_results
        for succ in sorted(succs, key=self.distance_to):
          C[(k, "out")][succ] = ask_results

    candidates = list(k for k in self.query_succ.keys() if k != FLOW_SRC and matching(k))

    # honour_query_gap is True if we are using this function to select the next
    # peer to query, or False if we are using this function to give us results
    if honour_query_gap:
      # a next-peer selection previously failed, meaning we hit a bottleneck in
      # the query graph, so ensure we don't select more peers beyond it.
      wanted = self.num_parallel() - self.query_gap
    else:
      wanted = ask_results
    if verbose:
      print("candidates:", candidates, "wanted:", wanted)

    if not use_min_cost:
      # brute force version using only max-flow, also works
      # doesn't easily support ask_results != self.num_parallel(), so disable that
      for subset in combinations(sorted(candidates, key=self.distance_to), wanted):
        C_ = deepcopy(C)
        for k in subset:
          C_[k][FLOW_SINK] = self.num_parallel()
        (max_flow, max_flow_graph) = max_flow_dinic(C_, FLOW_SRC, FLOW_SINK)
        max_flow /= ask_results # normalise
        if verbose:
          print(subset)
          pprintd(C_)
          print("max flow:", max_flow)
          pprintd(max_flow_graph)
        if max_flow == wanted:
          return sorted(subset)
      return []
    else:
      # more efficient version using max-flow-min-cost just once
      Rates = defaultdict(lambda: defaultdict(lambda: 0))
      for k in candidates:
        C[k][FLOW_SINK] = self.num_parallel()
        Rates[k][FLOW_SINK] = self.distance_to(k)
      (max_flow, min_cost, F) = max_flow_min_cost(C, Rates, FLOW_SRC, FLOW_SINK)
      max_flow /= ask_results # normalise
      if max_flow < wanted and honour_query_gap: return []
      results = [k for k in candidates if F[k][FLOW_SINK] == self.num_parallel()]
      #print(max_flow, ask_results, len(results), self.num_parallel())
      assert max_flow * ask_results == len(results) * self.num_parallel()
      # if (self.query_gap == 0) then we always get exactly what we want.
      # else, we might get more results than we want, but we cut those back
      # since those are from previously-failed queries.
      if honour_query_gap:
        assert wanted <= max_flow <= wanted + self.query_gap
      return sorted(results)[:wanted]

  def select_next_query(self, verbose=False):
    next_to_query = self.max_flow_min_distance(
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

    assert (len(self.query_expect) + self.query_gap == self.num_parallel())
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
      assert (len(self.query_expect) + self.query_gap == self.num_parallel())
      return next_peer

  def current_best(self, include_waiting=False, ask_results=None, verbose=False):
    return self.max_flow_min_distance(lambda k:
        (k in self.query_result or k in self.query_expect)
        if include_waiting else
        (k in self.query_result),
        honour_query_gap=False,
        ask_results=ask_results,
        verbose=verbose)

def tests_skademlia(use_min_cost=True):
  print("----")
  q = SKadLookup([4,5,6], 0, use_min_cost=use_min_cost)
  assert(q.recv_result(4, {1,2,3}) == 1)
  assert(q.recv_result(5, {1,2,3}) == 2)
  assert(q.recv_result(6, {4,1,2}) == 3)
  # ^ corner case, correctly selects 3 even though 3 not part of 6's reply
  assert(q.current_best() == [4,5,6])
  assert(q.current_best(True) == [1,2,3]) # this assert fails if using max_flow_wrong

  print("----")
  q = SKadLookup([5,6,7,8], 0, use_min_cost=use_min_cost)
  assert(q.recv_result(5, {3,4}) == 3)
  assert(q.recv_result(6, {3,4}) == 4)
  assert(q.recv_result(7, {3,4}) == None)
  assert(q.recv_result(8, {3,4}) == None)
  assert(q.recv_result(3, {1}) == 1)
  assert(q.recv_result(4, {1}) == None)
  # ^ selects None since we actually don't have enough results
  assert(q.query_gap == 3)

  print("----")
  q = SKadLookup([5,6,7], 0, use_min_cost=use_min_cost)
  assert(q.recv_result(5, {4}) == 4)
  assert(q.recv_result(4, {1,2,3}) == 1)
  assert(q.recv_result(6, {4}) == None) # e.g. not 2
  assert(q.recv_result(7, {4}) == None)
  # this test fails if "restrict nodes to only being on 1 flow" is not implemented
  assert(q.query_gap == 2)
  assert(q.current_best() == [4,5,6])
  assert(q.current_best(ask_results=4) == [4,5,6,7])
  assert(q.current_best(True) == [1,4,5])
  assert(q.current_best(True, ask_results=4) == [1,4,5,6])

  print("----")
  q = SKadLookup([10,11,12], 0, use_min_cost=use_min_cost)
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
  tests_max_flow_min_cost()
  tests_skademlia(use_min_cost=True)
  tests_skademlia(use_min_cost=False)
