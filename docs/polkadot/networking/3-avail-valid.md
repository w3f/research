====================================================================

**Authors**: Ximin Luo

**Last updated**: 2020-05-08

====================================================================

# Availability and Validity (A&V) networking

This subprotocol occurs whenever the relay chain block production protocol has output a candidate block for the current relay chain height.

This candidate block references a bunch of parachain blocks, whose data has not yet been checked (validated) by the relay chain as a whole, but rather only in a preliminary way by the respective parachain validators at that height. The purpose of this subprotocol then, is to distribute this data across the relay chain, and ensure that it is available for some time, especially to the approval checkers that will perform another round of validity checking.

These approval checkers are randomly assigned by another higher-layer protocol, in a similar way to how the parachain validators (i.e. the preliminary checkers) were randomly assigned.

Note: data from the relay chain is fully-replicated at each node, outside of this protocol. This does not need to be optimised, as there is only one relay chain and its data is not expected to be large.

## TODO

- to save time, the initial implemented version will be via gossip. Make a note of this.
- rough performance analysis & implementation notes, at the end of the doc.

## Background

For each given period (defined by higher layers), we have a disjoint partition of N validators into C sets of parachain validators, each set having size N/C.

Every parachain produces 1 block in the period, for a total of C blocks.

Every block is erasure coded across N pieces with a threshold of ceil(N/3).

### High-level requirements

At the start of the period, for every parachain, its N/C parachain validators each have all of the N pieces. In this role we call them the "preliminary checkers". The high-level purpose of A&V networking is to:

R1: Distribute the pieces of all C blocks to all other validators. A corollary of this is that every validator *must receive* at minimum (C-1) pieces - 1 from every other parachain - when operating at full capacity i.e. when every C parachain produces a block.

R2: Ensure that ceil(N/3) of the pieces of all C blocks remains available and retrievable for a reasonable amount of time, across the N validators.

Near the end of the period, for every parachain, a set of approval checkers of size > N/C will be chosen from the N validators, to actually retrieve at least ceil(N/3) pieces of the block.

### Timing model

Let T_l represent the average latency (single trip) between two peers, i.e. RTT is twice this.

Let T_B represent the average time it takes for a distributor to transfer all N pieces of a block, i.e. a single piece takes roughly T_B/N. This definition only refers to the transmission time (that uses bandwidth) and does not include the latency.

So for example, the successful direct transfer of a single piece including acknowledgement, in the context of no other transfers, takes roughly 2 * T_l (1 RTT of latency) + T_B/N (transmission time), assuming that network conditions are good and that we don't need to retransmit lost IP packets.

Let T_b be T_B divided by the number of validators per parachain, i.e. T_b = T_B/(N/C). This represents the average time it takes for a distributor to transfer the pieces of a block if this responsibility was shared equally across all validators of a parachain.

Let T_L represent the standard deviation of the distribution of when validators begin this distribution process for each period.

In practise based on some crude real-world measurements, we guess that T_l is about 150ms, T_b is about 3s, and T_L is about 750ms. In other words, T_b ~= 20 * T_l ~= 4 * T_L.

## Design considerations

### General aims

A1: Reduced redundancy & latency: pieces should (mostly) only be sent to the nodes that need it, i.e. its main storer, and the approval checkers.

A2: Constrain the use of shared OS resources, so the protocol does not interfere with other programs running at the same site.

A3: Expected work load should be as balanced as possible under ideal conditions, and degrade reasonably under imperfect conditions e.g. network congestion. For example, every sender should send approximately (C-1) pieces, rather than some senders sending twice as many as others.

A4: TODO: Protocols should not be easily spammable, or the spammers should be easily identifiable and punishable.

### Special considerations

S1: Some validator nodes are running behind sentry nodes, who must act as their proxy. Otherwise, we can assume that all other nodes (including the sentry nodes themselves) are fully-reachable via the public internet.

To help implementation be divided into stages, the main proposal is defined without this consideration. Parts of it that will need to be changed or extended for this, are marked [[TBX S1](#sentry-node-proxies) #($ref)], TBX standing for "to be extended".

## Protocol overview

We assume that all nodes can reach each other directly via the underlay topology, e.g. the internet layer. For an extension that relaxes this assumption, see [Sentry node proxies](#sentry-node-proxies).

Part of this protocol relies on some pre-existing medium that allows us to broadcast various metadata to every node of the relay chain, namely:

1. receipts of specific pieces ("I have pieces X, Y and Z")
2. receipts of "enough" pieces ("I have >1/3 of pieces, I don't need more"). This could also double as an attestation to everyone else, that there is availability from the attester's position on the network.

These should be gossiped every few seconds, and allows the participants to know when the stages of the protocol begin and end, details below.

The data of the pieces are distributed via the following communication links:

1. all validators in their in- and out-neighbour sets, as defined by in the overlay topology below
2. all other validators in the same preliminary-check set; this is the same as the parachain validator set
3. all other validators in the same approval-checking set

In addition to data, the aforementioned metadata may also be passed along links (2) and (3), to improve performance.

These links represent the majority of traffic flow in our A&V networking protocol. They are short-term [QUIC](https://quicwg.org/base-drafts/draft-ietf-quic-transport.html) connections. These have a low connection setup latency (0- or 1-RTT), and maintaining a connection also uses up no OS-level resources. So it is generally unproblematic to have a few hundred of them open at once, or to repeatedly open and close them. Empirical runtime performance data will be needed to properly choose the best approach.

The protocol runs in several phases and stages. Every node acts both in the distributor and distributee role, but not every role is active in every stage. A summary follows:

Phase | Distributors | Distributees
----- | ------------ | ------------
P1SA  | Y            | N
P1SB  | Y            | Y
P2SA  | Y            | N
P2SB  | N            | Y

Note that there is also background activity, as described below.

## Overlay topology

This section defines the topology where most of the data passes through.

Recall that we have a disjoint partition of N validators into C sets of parachain validators. In the general case, each set has size floor(N/C) or ceil(N/C), these being equal when C evenly-divides N, otherwise being 1 apart.

The topology is to be unpredictably but deterministically generated via a composition of shuffles. First we define the seeds in a secure manner. We expect that the chain provides an unpredictable value every period (chain height), the *chain seed*. The *topology master seed* should be derived from this seed via some KDF, e.g. HKDF. From this *topology master seed* we derive a *chain seed* for every chain, again via some KDF.

We then perform the following random assignments:

- Using the topology master seed, we randomly assign a *validator-index* `[0..N-1]` to every validator.
- Using the topology master seed, we randomly assign a *chain-index* `[0..C-1]` to every chain.
- Using the topology master seed, we randomly assign a *larger-chain-index* `[0..D]` to every chain of size `ceil(N/C)`, ignoring chains of size `floor(N/C)`, where `D == N mod C`.
- For every chain `c`:
    - Using the chain seed of `c`, we randomly assign a *chain-validator-index* `[0..|c|-1]` to every validator in the chain.
- For every unordered pair of chains (`a`, `b`):
    - Using (the chain seed of `a`) XOR (the chain seed of `b`), we randomly assign a matching between the chain-validator-indexes of `a` and `b`. There are two cases:
        - If `|a| == |b|` then the assignment can be performed straightforwardly, e.g. via a random shuffle on `[0..|a|-1]` interpreted as a matching (a.k.a. bipartite graph). **Example**: if `|a| == 10` then we shuffle `[0..9]` then zip the result with `[0..9]` to get a list-of-pairs to be interpreted as bidirectional matches.
        - If `|a| == |b| + 1` then we first select an index from `b` to act as the extra index. The selected index would be `larger-chain-index(a) mod |b|`. We now can perform the random matching as above, except that the match against the extra-index goes only from `b` to `a`. **Example**: if `larger-chain-index(a) == 57`, `|a| == 11`, `|b| == 10` then we would randomly assign a matching between `[0..10]` and `[0..10]`, where `10` on the RHS is later replaced by `7`, and `7 -> (some index of a)` but not `(some index of a) -> 7`. Note that `7` also has another bidirectional match with some other index of a.
        - If `|a| + 1 == |b|` then as above, but of course flipped.
    - This matching defines part of the in-neighbours and out-neighbours of the validators of a pair of chains: for everyone in the pair of chains, it adds 1 in-neighbour, and 0, 1, or 2 out-neighbours depending on the size of the chains.

The above assignment can be calculated by everyone in the same way, and gives an in-neighbour-set of `C-1` for every validator, satisfying our [requirement](#high-level-requirements) R1.

Some validators will have slightly more than `C-1` validators in their out-neighbour set, but we attempt to spread this evenly across the validators, satisfying our aim A3. This is what the indexes are for; without these we cannot attempt to spread the load. In summary, validators will either have `C-1`, `D-1`, or `C-1 + ceil-or-floor(D/floor(N/C))` out-neighbours, where `D == N mod C`. **Example**: if `N == 998`, `C == 100`, then this would be `{99, 97, 109, 110}`; and if `N == 1001`, `C == 100`, then this would be `{99, 0, 99, 100}`, with only one validator having the `0`.

Additionally, links are used in a bidirectional way as much as possible, helping to optimise the resource usage in terms of connections.

Note: in general, KDFs require an additional input, the "security context". Typically this should be a string that is not used in any other context globally. For example the string `"polkadot A&V topology master seed, generating validator-index"`, `"polkadot A&V chain seed for chain $chain-id"`, etc, will be sufficient.

### Notational definitions

In the protocol phases descriptions below, we use some shorthand notation for convenience:

When we refer to a validator `(c, i)`, we mean the validator on parachain with chain-index c and chain-validator-index i, as defined previously.

When we have to iterate through a out-neighbour-set of some validator `(c, i)`, we do this in chain-index order. That is, for all `v` in `out-neighbour(c, i)` we iterate through the `v` in increasing order of `chain-index(v)`. Recall that these chain-index values range from `[0..C-1]`; we start the iteration at `c+1` (unless otherwise stated) and go around cyclicly, wrapping back to `0` after reaching `C-1`, then proceeding onto `c-1`. For in-neighbour sets, we start the iteration at `c-1` (unless otherwise stated), go in *decreasing* order of `chain-index(v)`, and go around cyclicly eventually reaching `c+1`.

Note that for out-neighbour sets, there might be several `v` with the same `chain-index(v)`, in which case we can go through these in any order, e.g. the key-id of `v` itself.

## Protocol phase 1: initial distribution

As described in detail above, every validator is both a distributor of roughly C pieces and a distributee (recipient) of (C-1) pieces. Every piece has one source parachain and one main target-storer, and so we can index pieces with a tuple `piece(c_s, v_t)` which would read as *the piece with source parachain `c_s` and destination validator `v_t`*. `c_s` is a chain-index, and `v_t` is a validator-index as defined previously.

In phase 1, pieces are distributed by the source parachain validators to the main target-storers. This happens in two stages. Stage A is where most of the material is distributed, and stage B acts as a backup mechanism for anything that was missed during stage A.

**Stage A**

As a distributor, each validator `(c, i)` attempts to send the relevant pieces to everyone else in their out-neighbour set, i.e. `piece(c, v) for v in out-neighbour(c, i)`, iterating in order described previously. Conversely as a distributee, each validator `(c, i)` expects to receive their relevant pieces from everyone else in their in-neighbour set, i.e. `piece(chain-index(v), i) for v in in-neighbour(c, i)`.

In more detail:

Each distributor `(c, i)` will, with parallelism = C / 4, iterate through the neighbour-set, trying to send the relevant piece to each target `v`. C / 4 comes from our estimate that `T_b ~= 4 * T_L`.

Trials are done with a timeout, slightly larger than T_l. Sending is via QUIC. In order for it to be treated as a success, it should include an acknowledgement of receipt. Note this is orthogonal from the gossiped receipts which include a validator signature; by contrast this transport-level receipt can be assumed to be already protected by QUIC [transport authentication](L-authentication.html).

If a gossiped receipt is received at any point during the whole process, for a target for a piece, then we can interpret that to mean that the target obtained the piece from a different sender in the meantime, and we should cancel the sending attempt with success.

**Stage B**

As a distributee, if after a grace period we still haven't received our piece from a validator in our in-neighbour set, say from a validator on parachain `c'`, then we will ask the other validators on that parachain `c'` for the piece, load-balanced as described in more detail below.

This gives the distributee a more direct level of control over obtaining their own pieces.

As a distributor, if after our own stage A process is finished, we have received fewer than ceil(N/3) of the receipts of `out-neighbour(c, i')` for some other `i'` - then we will begin the stage A process for this out-neighbour set too, load-balanced as described in more detail below.

This helps to handle cases where a distributor validator is unavailable for everyone, either due to severe network issues or due to malicious behaviour. In this case, we hope to save a bit of latency by pro-actively distributing these pieces before being asked for them.

----

In more detail, for load-balancing purposes we suggest the following:

For distributees `(c, i)` expecting a piece from distributor `(c', i') for some i' in in-neighbour(c, i)`, the grace period they wait for should be `2 * T_L` plus the expected slot time `T_b / C * s` where `s = (c - c') mod C` as defined in stage A, before asking other alternative distributors for the piece. When doing so, say from distributors `(c', i'')` with fixed `c'`, varying `i'' != i'`, they should start with `i'' = i' + v mod chain-size(c')` first, where `v` is the distributee's validator-index, then increasing `i''` until wrapping around back to `i' + v - 1`.

For distributors `(c, i)` when distributing to another set `out-neighbour(c, i')` that is missing too many receipts, they should prioritise sets by the signed difference `d = (i' - i) mod |chain-size(c)|` between the chain-validator-indexes, and iterate through the set skipping targets for whom a receipt has already been received. The iteration should start from `c + 1 + floor(d*R)`, where `R = (|out-neighbour(c, i')| - 1) / (|chain-size(c)| - 1)`, which load-balances across any other distributor in chain `c` that might also be distributing to `out-neighbour(c, i')`.

For example, with `C == 100` and `N/C == 10`, a distributor (57, 3) who has finished distributing to `out-neighbour(57, 3)` and observes that `out-neighbour(57, 2)`, `out-neighbour(57, 4)`, `out-neighbour(57, 7)` are missing too many receipts, would proceed to distribute to validators from `out-neighbour(57, 4)` with chain-index `69 == 57 + 1 + 1*(99/9)`, then 70, 71 and so on, skipping anyone whose receipts have already been received.

## Protocol phase 2: approval checking

In phase 2, a higher layer defines a set of approval checkers for every parachain. The size of the set starts at a given baseline N/C, the same as the parachain validators, but may be increased dynamically after the initial selection, up to potentially several times the baseline. At least ceil(N/3) of the pieces of that parachain's block must be distributed to these approval checkers.

As in phase 1, this happens in two stages. Additionally, and throughout the whole phase including both stages, checkers should connect to each other and distribute the pieces to each other via these connections. They may use the gossip protocol for this purpose, including any set reconciliation protocols. However these connections (and the bandwidth associated with them) are not intended for other uses of the main gossip protocol and are not intended to be considered "connected" to the main gossip topology, one of the reasons being that this allows us to analyse the resource usages of each subprotocol separately.

Unlike phase 1, distributees do not need to broadcast receipts for every individual piece, but only a "minimum received" receipt for parachain v, when they have received ceil(N/3) or more pieces of the block for parachain v.

**Stage A**

Stage A of phase 2 proceeds similarly to stage A of phase 1, except that:

- Each distributor `(c, i)` only distributes to half of its out-neighbour set, instead of the whole set. This is 3/2 of the minimum `ceil(N/3)` required, which should give a generous margin for success. As a concrete decision, this would be the first half of the standard iteration order as described previously, of length `ceil(C/2) - 1`.

- Each distributor `(c, i)`, when sending to target `v` does not send piece `(c, v)` as they would in phase 1, but rather `piece(c, v')` for all `v'` in `out-neighbour(c, i)`) where `chain-index(v') == c_v` and `v` is an approval checker for `c_v`, and for which they have not received a gossiped receipt from `v` for. The number of parachains assigned to each approval checker will be not too much higher than 1.

By re-using the basic structure from phase 1, we also automatically gain its other nice properties such as load-balancing.

**Stage B**

Stage B of phase 2 is morally similar to stage B of phase 1, but ends up being structurally quite different, due to the different high-level requirements.

Each distributee `(c, i)` is not expecting any specific pieces from anyone, but rather `ceil(N/3)` pieces of the block from every parachain `c_v` for which it is a approval checker. After a grace period of `2 * T_L`, if they have not received enough pieces for any `c_v`, they will begin querying other validators for their pieces for these blocks.

For load-balancing, this querying of other in-neighbour sets begins at `in-neighbour(c, i')`, starting with `i' = i + 1`, increasing until it wraps around back to `i`. The iteration through each in-neighbour set starts from `c - ceil(C/2) mod C`, with decreasing chain-index as described previously. This means that the last validators to be queried will be precisely the ones that (are supposed to) have sent us pieces already in stage A, helping to avoid duplication.

At any time, if the distributee receives `ceil(N/3)` or more pieces of the blocks of every parachain `c_v` for which they are a approval checker for, they can cancel the above process with success.

Each distributor is responsible for a smaller fraction of the required pieces for each block, by design. Therefore, we don't need a separate follow-up part for distributors.

## Design explanation

We directly use the underlying network (i.e. the internet) for transport, and not an overlay network, because we considered the latter choice unsuitable for our high-level requirements:

1. Each piece is sent to a small set of specific people, rather than everyone.

2. a. People that want a specific piece of data, know where to get it - i.e. validators, for their own piece, get each piece from the preliminary checkers for that piece.

   b. Other people want non-specific pieces - i.e. approval validators, want any 1/3 of all pieces to be able to reconstruct.

Overlay topologies are generally more useful for the exact opposite of the above:

1. Each data piece is sent to nearly everyone.
2. People want a specific data piece, but don't know where (what network address) to get it from.

For example, bittorrent has similar requirements and does not use a structured overlay either. The peers there connect to other peers on a by-need basis.

The "ring" structure was chosen to make it easier to do load-balancing, as everyone can just "go around the ring" for most of these sorts of tasks, starting from their own position. The problem with (e.g.) having N clients independently randomly choose from N servers is that 1/3 of servers won't be chosen, and 1/4 of them will have multiple clients - see [N balls and N buckets](https://theartofmachinery.com/2020/01/27/systems_programming_probability.html#n-balls-in-n-buckets).

In the "ideal case", everyone starts stage A simultaneously, there is no network congestion, and all pieces are uniformly sized. Then, our stage A will have a completely evenly-distributed traffic profile, since everyone is scheduled to send a different piece to everyone else at all times. While we know that this "ideal case" will never be observed in practise, it gives us a reference point for the rest of the design.

In practise, we assume that everyone will be entering the stage at different times, normally distributed with standard deviation on the order of a few seconds. The parallel sending strategy therefore provides a good chance that there will be a "slot" available, helping to smooth out any spikes caused by multiple sources attempting to send to the same target at once.

The other details follow quite naturally from these design choices and the initial requirements. Of course there is room for further optimisation in many of the details, for the future.

## Analysis of bandwidth usage

We defined the following sources of incoming data:

- phase 1 stage A: 1 piece from every other validator in your own ring
- phase 1 stage B: several pieces

TODO

TODO discuss rate-limiting based on the expected number of piecese

## Implementation notes

TODO

Push vs pull

Rate-limiting, including for proxies [TBX S1 #3]

### Possible layers

TODO

### Erasure coding

As mentioned in the background, each block is divided into pieces which are then distributed. In practise this is done by an erasure code, but this networking layer does not need to know the details of that. The only knowledge it requires is:

- an assignment of pieces to N validators
- the threshold of the erasure code, e.g. ceil(N/3)

When receiving each piece, we also need to be able to authenticate it individually without having received any of the other pieces.

## Extensions

### Sentry node proxies

This extension deals with a scenario where we need to consider S1, i.e. where some nodes are running behind sentry nodes, who must act as their proxy. In other words, nodes have two types of reachability:

a. fully-reachable by the public internet<br/>
b. not reachable, except by their sentry nodes who are trusted

(a) was the assumption we made of all nodes in the main proposal, and now we must also account for (b). Note that this is a more restricted assumption than an arbitrary internet topology - the latter would require a fully-general NAT traversal solution, which is more complex and carries more runtime overhead.

Specifically for A&V direct sending, this translates to the following scenarios:

a. for incoming connections, the sentry node accepts these and proxies them back to the validator node<br/>
b. for outgoing connections, either the validator node makes the connection directly, or else makes it via their sentry node.

In some cases where both peers are behind their own sentries, this may be up to 2 hops. However, it is unnecessary to have special-case logic to handle this situation. The following general rules will suffice, and they can be applied even to normal validator nodes (those running without sentries):

1. For the address book, the validator should insert (or have their sentry nodes insert) the addresses of whatever nodes are acting as incoming proxies for it, what other people can reach. The following details are important:

    a. each record should include a creation date, so that later entries unambiguously obsolete earlier entries. Thus load-balancing can be done in a more predictable way, across the full set of addresses.

    b. each record should include an expiry date, so that old addresses are unambiguously avoided by readers unsure if the entry they got is "too old" or not

2. For transport session keys, any node claiming to be a validator or a proxy for one, must present a certificate proving that the validator key authorises the transport key to do so. This ties back into the [authentication proposals](#L-authentication.html#proposal-fresh-authentication-signals).

It's unnecessary to distinguish between "is a validator" and "acting as a proxy for a validator". This could be given as optional information in the certificate (e.g. so that the peer expects a higher latency), or it may be omitted if the validator wants to withhold this information from its peers. Nodes are free to guess whether their peers are proxies or not.

#### Proxy protocol

The proxying protocol is straightforward, since the private validator node and the sentry nodes trust each other.

1. Inbound, the protocol does not require any special headers (unwrapping/rewrapping of the content). Whenever a sentry node accepts an incoming connection, it forwards it directly onto the corresponding validator node.

    Justification: in our A&V direct-sending protocol, the contents are all signed by their authors, so there is no need for extra checking at the sentry node, although this may be done either to simplify the code or as extra "defense in depth". In all cases, proper exercise of flow control at the private validator node is necessary to prevent the sentry node from spamming it by mistake.

2. Outbound, the protocol needs special headers for the private validator node to tell the sentry node the outgoing destination. This is straightforward: namely the peer validator's key.

Recall that as above, there are two types of outbound connections: distributors pushing data, or distributees requesting data.

Since the private validator node may not be able to access the address book (e.g. one implemented via Kademlia DHT), the sentry node is the one to perform the address book lookup. As described in 1(a) above, in the general case it will get a set of addresses as the result. For better load-balancing, the sentry node should sort this set and select the jth address to connect to, where j = i mod n, n is the size of the set, and (c, i) is the co-ordinate of its validator.
