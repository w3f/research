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

1. Distribute the pieces of all C blocks to all other validators

2. Ensure that ceil(N/3) of the pieces of all C blocks remains available and retrievable for a reasonable amount of time, across the N validators.

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

A3: Performance degrades reasonably under load or imperfect network conditions.

A4: TODO: Protocols should not be easily spammable, or the spammers should be easily identifiable and punishable.

### Special considerations

S1: Some validator nodes are running behind sentry nodes, who must act as their proxy. Otherwise, we can assume that all other nodes (including the sentry nodes themselves) are fully-reachable via the public internet.

To help implementation be divided into stages, the main proposal is defined without this consideration. Parts of it that will need to be changed or extended for this, are marked [[TBX S1](#sentry-node-proxies) #($ref)], TBX standing for "to be extended".

## Protocol overview

Part of this protocol relies on some pre-existing medium that allows us to broadcast various metadata to every node of the relay chain, namely:

1. receipts of specific pieces ("I have pieces X, Y and Z")
2. receipts of "enough" pieces ("I have >1/3 of pieces, I don't need more"). This could also double as an attestation to everyone else, that there is availability from the attester's position on the network.

These should be gossiped every few seconds, and allows the participants to know when the stages of the protocol begin and end, details below.

The data of the actual pieces are distributed via a topology separate from the broadcast medium:

Recall that we have a disjoint partition of N validators into C sets of parachain validators, each set having size N/C. For our purposes for this subprotocol, we will randomly assign a co-ordinate (c, i) to every validator, with c in [0, C) and i in [0, N/C). Fixing c and varying i defines a particular parachain validator set; varying c and fixing i defines what we'll call a particular validator "ring". This name is only meant to be very slightly suggestive, the precise structure and its justification will be described below.

The random assignment must be a deterministic but unpredictable assignment that every validator can calculate in the same way. For this purpose, we can use some entropy extracted from the chain at a position (height) determined by the current period, to seed a deterministic shuffle algorithm across the entire set of validators. The actual input seed must be pre-processed from the on-chain entropy, e.g. via HKDF, such that it is not re-used in any other security context.

Example:

Let's say we have 20 validators `[a, b, c, ..., t]` and 5 parachains. The co-ordinates of the validators could look like such `[a: (0, 0), b: (0, 1), c: (0, 2), d: (0, 3), e: (1, 0), ..., t: (4, 3)]`. The validator set of the first parachain would be `[a, b, c, d]`. The first validator ring would be `[a, e, i, m, q]`, the second `[b, f, j, n, r]`.

A validator ring is mostly-connected as permitted by the physical topology. Nodes within this ring talk to each other periodically via short-term and low-cost QUIC connections.

For a given parachain, the preliminary checkers are also mostly-connected, as permitted by the physical topology. Likewise the approval checkers are also mostly-connected.

These connections represent the vast majority of traffic flow in our A&V networking protocol; to improve reliability and availability there are also other lines of communication as described below.

The protocol runs in several phases and stages. Every node acts both in the distributor and distributee role, but not every role is active in every stage. A summary follows:

Phase | Distributors | Distributees
----- | ------------ | ------------
P1SA  | Y            | N
P1SB  | Y            | Y
P2SA  | Y            | N
P2SB  | N            | Y

Note that there is also background activity, as described below.

## Protocol phase 1: initial distribution

Every validator is both a distributor of C pieces and a distributee (recipient) of C pieces [TODO: correction, explanation]. Every piece has one source parachain and one main target storer, and so we can index pieces with a tuple (c_s, (c_t, i_t)) which would read as *the piece with source parachain c_s and destination validator on parachain c_t with index i_t*.

In phase 1, pieces are distributed by the source parachain validators (c_s, \*) to the main target storers. This happens in two stages. Stage A is where most of the material is distributed, and stage B acts as a backup mechanism for anything that was missed during stage A.

**Stage A**

As a distributor, each validator (c, i) attempts to send the relevant pieces for their parachain's block (c, (c', i)), to everyone else on their ring (c', i) for all c' != c. Conversely as a distributee, each validator expects to receive their relevant pieces (c', (c, i)) for other parachains' blocks, from everyone else on their ring (c', i) for all c' != c.

In more detail:

Each distributor (c, i) will, with parallelism = C / 4, for s in [0..C), try to send the relevant piece to target t = ((c+s) mod C, i). C / 4 comes from our estimate that T_b ~= 4 * T_L.

Trials are done with a timeout, slightly larger than T_l. Sending is via QUIC. In order for it to be treated as a success, it should include an acknowledgement of receipt. Note this is orthogonal from the gossiped receipts which include a validator signature; by contrast this transport-level receipt can be assumed to be already protected by QUIC [transport authentication](L-authentication.html).

If a gossiped receipt is received at any point during the whole process, for a target for a piece, then we can interpret that to mean that the target obtained the piece from a different sender in the meantime, and we should cancel the sending attempt with success.

**Stage B**

As a distributee, if after a grace period we still haven't received our piece (c', (c, i)) from a parachain validator (c', i), then we will ask the other validators (c', i') for all i' != i (from all other rings) in that parachain for the piece (c', (c, i)), load-balanced as described in more detail below.

This gives the distributee a more direct level of control over obtaining their own pieces.

As a distributor, if after our own stage A process is finished, we have received fewer than ceil(N/3) of the receipts of another ring i' - i.e. receipts for piece (c, (c', i')) from peer (c', i') for all c' - then we will begin the stage A process for the other ring i' too, load-balanced as described in more detail below.

This helps to handle cases where a distributor validator is unavailable for everyone, either due to severe network issues or due to malicious behaviour. In this case, we hope to save a bit of latency by pro-actively distributing these pieces before being asked for them.

----

In more detail, for load-balancing purposes we suggest the following:

For distributees (c, i) expecting a piece from distributor (c', i), the grace period they wait for should be 2 * T_L plus the expected slot time T_b / C * s where s = (c - c') mod C as defined in stage A, before asking other alternative distributors for the piece. When doing so, say from distributors (c', i') with fixed c', varying i', they should start with i' = (i + ((s + 1) mod (N/C - 1))) mod N/C first.

For distributors (c, i) when distributing to another ring i' that is missing too many receipts, they should prioritise rings by the directed distance d = (i' - i) mod N/C from their own ring, and start the traversal around the ring from (c + s, i') with s = C * (i' - i) / (N/C), of course skipping targets for whom a receipt has already been received.

For example, with C = 100 and N/C = 10, a distributor (57, 3) who has finished distributing to (\*, 3) and observes that rings 2, 4 and 7 are missing too many receipts, would proceed to distribute to (67, 4), (68, 4), (69, 4) and so on, skipping anyone whose receipts have already been received.

## Protocol phase 2: approval checking

In phase 2, a higher layer defines a set of approval checkers for every parachain. The size of the set starts at a given baseline N/C, the same as the parachain validators, but may be increased dynamically after the initial selection, up to potentially several times the baseline. At least ceil(N/3) of the pieces of that parachain's block must be distributed to these approval checkers.

As in phase 1, this happens in two stages. Additionally, and throughout the whole phase including both stages, checkers should connect to each other and distribute the pieces to each other via these connections. They may use the gossip protocol for this purpose, including any set reconciliation protocols. However these connections (and the bandwidth associated with them) are not intended for other uses of the main gossip protocol and are not intended to be considered "connected" to the main gossip topology, one of the reasons being that this allows us to analyse the resource usages of each subprotocol separately.

Unlike phase 1, distributees do not need to broadcast receipts for every individual piece, but only a "minimum received" receipt for parachain v, when they have received ceil(N/3) or more pieces of the block for parachain v.

**Stage A**

Stage A of phase 2 proceeds similarly to stage A of phase 1, except that:

- Each distributor only needs to distribute to the half-ring in front of it, instead of the whole ring. This is 3/2 of the minimum ceil(N/3) required, which should give a generous margin for success.
- Each distributor (c, i), when sending to target (c', i) for some given c' != c, does not send piece (c, (c', i)) as they would in phase 1, but rather the pieces (c, (v, i)) for all parachains v that c' is a approval checker for, and for which c has not received a gossiped receipt from c' for.

By re-using the basic structure from phase 1, we also automatically gain its other nice properties such as load-balancing.

**Stage B**

Stage B of phase 2 is morally similar to stage B of phase 1, but ends up being structurally quite different, due to the different high-level requirements.

Each distributee (c, i) is not expecting any specific pieces from anyone, but rather ceil(N/3) pieces of the block from every parachain v for which it is a approval checker. After a grace period of 2 * T_L, if they have not received enough pieces for any v, they will begin querying other validators for their pieces for these blocks.

For load-balancing, this querying of other validators (c', i') begins at c' = c + 1, i' = i, increasing c' then increasing i'. This means that the last validators to be queried will be (c, i - i/2) to (c, i - 1) which precisely are the ones that (are supposed to) have sent us pieces already in stage A, so we avoid duplication.

At any time, if the distributee receives ceil(N/3) or more pieces of the blocks of every parachain v for which they are a approval checker for, they can cancel the above process with success.

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

Since the private validator node may not be able to access the address book, the sentry node is the one to perform the address book lookup. As described in 1(a) above, in the general case it will get a set of addresses as the result. For better load-balancing, the sentry node should sort this set and select the jth address to connect to, where j = i mod n, n is the size of the set, and (c, i) is the co-ordinate of its validator.
