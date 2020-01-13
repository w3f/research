k = 20

def distance(a, b):
  return a ^ b

class SKadLookup(object):

  def __init__(self, init_queries, target_node):
    self.queries = [{}] # query nodes per hop, [{nodeId: replied or not}]
    self.results = [{}] # result sets per hop, [{nodeId: set(predecessor nodeId)}]
    # queries[n+1] is selected from results[n] under the fat-multipath constraints

    self.queries_per_hop = len(init_queries)
    # "d" parameter as mentioned in the paper
    self.target_node = target_node
    self.ensure_hop(1)
    for nodeId in init_queries:
      self.launch_query("init %3s" % target_node, 1, nodeId)

  def distance_to(self, n):
    return distance(n, self.target_node)

  def ensure_hop(self, n):
    if len(self.queries) <= n:
      self.queries.append({})
    if len(self.results) <= n:
      self.results.append({})

  def launch_query(self, ctx, n, nodeId):
    self.queries[n][nodeId] = False
    # fake send, for our testing purposes
    print(ctx, ": sending hop-%s query to node %s" % (n, nodeId))

  def find_query_hop(self, peer):
    for hop, queries in enumerate(self.queries):
      if peer in queries:
        return hop
    return None

  def get_hop_replied(self, hop):
    return set(peer for (peer, replied) in self.queries[hop].items() if replied)

  def get_hop_preds(self, hop):
    return set(pred for peer in self.queries[hop].keys()
                    for pred in self.results[hop-1][peer])

  def check_query_fatness(self, n):
    # check that queries[n] "comes from" an expected number of queries[n-1] peers
    preds = self.get_hop_preds(n)
    #print("preds:", preds)
    #print("queries:", self.queries[n])
    #print("replied:", self.get_hop_replied(n-1))
    assert(len(preds) == len(self.queries[n]))
    assert(len(preds) == len(self.get_hop_replied(n-1)))

  def recv_result(self, peer, reply):
    hop = self.find_query_hop(peer)
    if not hop:
      raise ValueError("unexpected reply from peer %s: %s" % (peer, reply))
    #print("hop:", hop)

    if self.queries[hop][peer]:
      raise ValueError("duplicate reply from peer %s: %s" % (peer, reply))

    # check that all replies are closer to the target, with exemption for
    # peers that are already very close to the target
    old_d = self.distance_to(peer)
    if any(self.distance_to(r) >= self.distance_to(peer) > k for r in reply):
      # probably malicious
      raise ValueError("divergent reply from peer %s: %s" % (peer, reply))

    # drop replies that were already queried in previous hops
    reply = [r for r in reply if not any(r in self.queries[h] for h in range(hop+1))]
    #print("remaining replies:", reply)

    # everything OK, now store the reply details including its predecessor
    self.ensure_hop(hop)
    self.queries[hop][peer] = True
    for r in reply:
      self.results[hop].setdefault(r, set()).add(peer)

    # select another next-hop peer
    self.ensure_hop(hop+1)
    preds = self.get_hop_preds(hop+1)
    replied = self.get_hop_replied(hop)
    if len(replied) > len(preds):
      # no existing next-hop query came from $peer, so choose a peer from
      # $reply (which clearly does come from $peer)
      candidates = reply
    else:
      # an existing next-hop query already came from $peer, so any other result
      # that was not already chosen, can be chosen as a next-hop query. this
      # covers the "corner case" we mentioned involving backtracking.
      candidates = [r for r in self.results[hop].keys() if r not in self.queries[hop+1]]
    candidates.sort(key=self.distance_to)
    next_peer = candidates[0]

    # make the actual query
    self.launch_query("recv %3s" % peer, hop+1, next_peer)
    # check our stated invariants
    self.check_query_fatness(hop+1)
    return next_peer


if __name__ == "__main__":
  q = SKadLookup([1,2,3], 10)
  assert(q.recv_result(1, {4,5,6}) == 6)
  assert(q.recv_result(2, {4,5,6}) == 4)
  assert(q.recv_result(3, {1,4,6}) == 5)
  # ^ corner case, correctly selects 5 even though 5 not part of 3's reply
