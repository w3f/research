====================================================================

**Authors**: Rob Habermeier, Fatemeh Shirazi

**Last updated**: 24.09.2019

====================================================================
## ICMP

### Inter-chain Message Passing: Egress Queue Data Fetching

Every parachain block in Polkadot produces a possible-empty list of messages to route to every other block.
These are known as "egress queues". $E^B_{x,y}$ is the egress queue from chain $x$ to $y$ at block $B$.

There is also $R(E^B_{x, y})$, which is the root hash of the Merkle-Patricia trie [] formed from mapping the index of each message in $E^B_{x,y}$ to the message data.

The pending messages to a chain should be processed in the next block for that chain.
If there are no blocks for a chain in some time, the messages can begin to pile up.

Collators and full nodes of a parachain $p$ have executed all blocks of that parachain and should have knowledge of $E^B_{p, x}$ for all $B,x$.

The _block ingress_ of a parachain $p$ at block $B$ is the set $Ingress_{B,p} = \{\forall y\neq p,  E^B_{y,p} \}$.

The _block ingress roots_ are $R(Ingress_{B,p}) = \{\forall y\neq p,  R(E^B_{y,p}) \}$

The _total accumulated ingress_ of a parachain $p$ at block $B$ is defined by the recursive function

$$T_{Ingress}(B,p) = \begin{cases}
\emptyset, & B = Genesis \\
T_{Ingress}(parent(B),p) \cup Ingress_{B,p}, & B \neq Genesis
\end{cases}$$

$$R(T_{Ingress}(B,p)) = \begin{cases}
\emptyset, & B = Genesis \\
R(T_{Ingress}(parent(B),p)) \cup R(Ingress_{B,p}), & B \neq Genesis
\end{cases}$$

This is a list containing all the ingress of every parachain to $p$ in every block from the genesis up to $B$.

Parachains must process $Ingress_{B,p}$ after $Ingress_{parent(B),p}$. Additionally, if any message from $Ingress_{B,p}$ is processed, they all must be.

Every parachain has a value $watermark_p$ which is the relay chain block hash for which it has most recently processed any ingress.
This is initially set to $Genesis$.
To define a structure containing all un-processed messages to a parachain, we introduce the _pending_ ingress, which is defined by the recursive function.

$$P_{Ingress}(B,p) = \begin{cases}
\emptyset, & Hash(B) = watermark_p \\
P_{Ingress}(parent(B),p) \cup Ingress_{B,p}, & Hash(B) \neq watermark_p
\end{cases}$$

The _pending ingress roots_ $R(P_{Ingress}(B,p))$ can be computed by a similar process to $R(T_{Ingress}(B,p))$.

A parachain candidate for $p$ building on top of relay-chain block $B$ is allowed to process any prefix of $P_{Ingress}(B,p)$.

All information the runtime has about parachains is from `CandidateReceipt`s produced by validating a parachain candidate block and included in a relay-chain block. The candidate has a number of fields. Here are some relevant ones:

  - Egress Roots: `Vec<(ParaId, Hash)>`. When included in a relay chain block $B$ for parachain $p$, each hash, paired with unique parachain $y$ is $R(E^B_{p,y})$
  - a new value for $watermark_p$ when the receipt is for parachain $p$.
  The runtime considers the value from the most recent parachain candidate it has received as current.
  It must be at least as high as the previous value of $watermark_p$ _and_ be in the ancestry of any block $B$ the candidate is included in.

(**rob**: disallow empty list where pending egress non-empty?)

The goal of a collator on $p$ building on relay chain parent $B$ is to acquire as long of a prefix of $P_{Ingress}(B, p)$ as it can.

The simplest way to do this is with a gossip protocol.
Messages are gossiped from one parachain network to another parachain network.
If there are nodes in common between these two networks gossiping the message will lead to the receiving parachain to receive its messages. .
However, if the destination parachain validators realize that the message has not been gossiped in the recipient parachain, they request the message from the parachain validator of the sending parachain and then gossip it themselves in the recipient parachain network.

At every block $B$ and parachain $p$ $R(P_{Ingress}(B, p))$ is available from the runtime.

What the runtime makes available for every parachain and block $p,B$ is a list of ingress-lists pending ingress roots at that block, each list paired with the block number the root was first meant to be routed.
$R(\emptyset)$ is omitted from ingress-lists and empty lists are omitted.
Sorted ascending by block number. All block numbers are less than `num(B)` and refer to the block in the same chain.

In Rust pseudo-code (TODO: transcribe to LaTeX)
`fn ingress(B, p) -> Vec<(BlockNumber, Vec<(ParaId, Hash)>)>`

The runtime also makes available the pending _egress_ from a given $B,p$. This follows the same constraints as the ingress list w.r.t. ordering and omission of empty lists. The `ParaId` here is the recipient chain, while in the `ingress` function it is the sending chain.

`fn egress(B, p) -> Vec<(BlockNumber, Vec<(ParaId, Hash)>)>`.

We make the following assumptions about nodes:
  1. The block-state of leaves is available but no guarantees are made about older blocks' states.
  2. The collators and full nodes of a parachain can be expected to hold onto all egress of all parachain blocks they have executed.
  3. Validators are not required to hold onto egress of any blocks.

Assuming we build on top of the attestation-gossip system, peers communicate the leaves they believe best to each other.

### Simple Gossip for ICMP queue routing: Topics based on relay-chain block where messages are issued

This section describes a _bounded_ gossip protocol (see overview for definition) for the circulation of ICMP message queues.

Recall

`fn ingress(B, p) -> Vec<(BlockNumber, Vec<(ParaId, Hash)>)>`
and
`fn egress(B, p) -> Vec<(BlockNumber, Vec<(ParaId, Hash)>)>`

Since `ingress` is invoked at a given block $B$ we can easily transform `BlockNumber` -> `BlockHash`.

Messages start un-routed and end up being routed.

We propose a gossip system where we define

$queueTopic(block\_hash: H) \rightarrow H$
Messages on this topic have the format
```rust
struct Queue {
    root: Hash,
    messages: Vec<Message>,
}
```

We maintain our local information:

  - $leaves$, a list of our best up to `MAX_CHAIN_HEADS` leaf-hashes of the block DAG
  - $leaves_k$, for each peer $k$ the latest list of their best up to `MAX_CHAIN_HEADS` leaf-hashes of the block DAG (based on what they have sent us).
  - $leafTopics(l) \rightarrow \{queueTopic(h)\}$ for each unrouted root $h$ for all parachains for a leaf $l$ in $leaves$.
  - $expectedQueues(t) \rightarrow H$: a map from topics to root hashes. Has entries for all $t\in\cup_{l \in leaves}leafTopics(l)$

---

**On new leaf $B$**

1. Update $leaves$, $leafTopics$, and $expectedQueues$. (haven't benchmarked but i would conservatively estimate 100ms operation)
2. Send peers new $leaves$.
3. If a collator on $p$, execute `egress(B,p)`.
For any message queue roots that are known and have not been propagated yet, put corresponding `Queue` message in the propagation pool.

---

**On new chain heads declaration from peer $k$**

1. Update $leaves_k$
2. $\forall H \in leaves\ \cap\ leaves_k$ do $broadcastTopic(k,t)$ for each $t$ in $leafTopics(H)$.

---

**On `Queue` message $m$ from $k$ on topic $t$**

We define `good(m)` to be a local acceptance criterion:

  - The `root` hash of the message is in $expectedQueues(t)$.
  - The trie root of given messages equals `root`.

If `good(m)`, note $k$ as beneficial and place $m$ in propagation pool. Otherwise, note $k$ as wasteful.
This is useful for peer-set cultivation.

(**rob**: if $leaves_k$ doesn't imply knowledge of $t$, should we note mistrust of the peer?)

---

**Definition of $allowed_k(m)$ for a peer $k$ and `Queue` message $m$ on topic $t$**

A message is disallowed if $k$ has sent it to us before or we have sent it to them.

Otherwise, a message is allowed if $\exists l \in leaves \cap leaves_k\ |\ t \in leafTopics(l)$ and disallowed otherwise.

---

**Periodically**

Mark all topics without entries in $expectedQueues$ as expired and purge them from the propagation pool.

Practically, once every couple of seconds. This prevents our pool from growing indefinitely.

---

The decision to only propagate unrouted messages to peers who share the same view of which leaves are current may be a bit controversial, but it is well-justified by some of the prior conditions we set out.

First, we don't want nodes to have to process an unbounded number of messages.
That means that messages for $queueTopic(H)$ where $H$ is _unknown_ to the node are unreasonable since there is an unbounded number of such $H$.

Secondly, nodes shouldn't have to do a lot of work to figure out whether to propagate a message to a specific peer or not.
Assume that $leaves \cap leaves_k = \emptyset$ _but_ that some entries of $leaves_k$ are ancestors of entries of $leaves$.
We have to do $O(n)$ work for each $l \in leaves_k$ to figure that out, though.
Then, we have to figure out if a given message is unrouted at that prior block.
Naïvely we would assume that if a message is still unrouted at a later block in the same chain that it was not routed earlier, but with chain-state reversions from fishermen this may not be true.

Since chain-state is not assumed available from prior blocks, we have no good way of determining if egress actually should be sent to peers on that earlier block. A relaxation of this by extending to a constant number of ancestors is discussed in the future improvements section.

Still, only propagating to peers that are synchronized to the same chain head is reasonable with the following assumptions (some empirical but reasonable and probably overestimated values):

 1. New valid blocks are issued on average at least 5 seconds apart (we are aiming for more like 10-15 seconds actually)
 2. Block propagation time is within 2 seconds over the "useful" portion of the gossip graph.
 3. Neighbors in the gossip graph have <=500ms latency.
 4. Meaningfully propagating messages before synchronizing to the heads of the DAG is probably not worthwhile

If we assume that no nodes broadcast updated $leaves$ until after the block has fully propagated (this is clearly not going to be the case in practice), then that leaves time after updating $leaves$ for a full 2.5 hops at 500ms latency to gossip `Queue`s until the next block.
Real values are almost certainly better.
And the good news is that not all egress has to be propagated within one block-time -- over time it is more and more likely that participants obtain earlier messages.

This is a scheme which results in all participants seeing all messages.
It almost certainly will not scale beyond a small number of initial chains but will serve functionally as a starting protocol.

 ## Interchain Messaging Routing Overview
 To send messages from one parachain (sending parachain) to another parachain (receiving parachain) depending on the setup the following steps will be carried out.

 1. When full nodes of the sending parachain are also part of the domain of the receiving parachain, gossiping the message suffices
 2. A relay chain full node is in the domain of both the sending and receiving parachain, gossiping the message suffices
 3. Parachain validator of receiving parachain does not see the message being gossiped, then it request the message directly from the parachain validator of the sending parachain (PV at the moment of sending).
 The PV of the sending parachain are responsible to keep the messages available.
 The parachain validators of the sending parachain directly send the messages to the receiving parachain PoV's.
 Finally, the PV's of the receiving parachain gossip the messages in the receiving parachain network.



**Future Improvements (roughly, from sooner to later)**:

 1. A section above describes why propagating egress to peers who are _arbitrarily_ far back is a bad idea, but we can reasonably keep track of the last $a$ ancestors of all of our leaves once we're synced and just following normal block production.
 The first reasonable choice for $a$ is 1 (keep parents). This probably gets us 90% of the gains we need, simply because there is a "stutter" when requiring leaf-sets to intersect and two peers need to update each other about the new child before sending any more messages.
 2. Extend the definition of $E^B_{x,y}$ to allow chains to censor each other. For instance, by saying that parachain $y$ can inform the relay chain not to route messages from $x$ at block $B$ (and later inform it to start routing again at block $B'$).
 Then for any block $b$ between $B$ and $B'$, we would have the runtime consider $E^b_{x,y} = \emptyset$ regardless of what the `CandidateReceipt` for $x$ at $b$ said. Actually, since the runtime deals only in trie root hashes, it would really just ignore $R(E^b_{x,y})$ from the candidate receipt and set it to $R(\emptyset)$.
 3. Extend to support a smarter topology where not everyone sees everything. Perhaps two kinds of topics, those based on $(B, Chain_{from})$ and those based on $(B, Chain_{to})$ would make this more viable.
 4. Use some kind of smart set reconciliation (e.g. https://github.com/sipa/minisketch) to minimize gossip bandwidth.
 5. Incentivize distribution with something like Probabilistic Micropayments.



 ---

 A collator or validator seeking to collect egress queues at a block $B$ and parachain $p$ simply invokes `ingress(B,p)` and searches the propagation pool for the relevant messages, waiting for any which have not been gossiped yet.


 All information that the runtime has is in the form of `CandidateReceipt`s.
 The author of a block may submit up to one `CandidateReceipt` from each parachain in the block (in practice, only those which are attested by a number of validators, although this detail is not relevant here).
 ---
