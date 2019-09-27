====================================================================

**Authors**: Fatemeh Shirazi, Rob Habermeier

**Last updated**: 24.09.2019

**Note**: This write-up contains notes from a networking workshop 05.08.19-06.08.19 at Parity Technologies.

====================================================================
# Networking for Polkadot

## Overview

In Polkadot we need to send a number of messages to a number of entities. Below we give an overview of where and how each type of message is sent. The column *Nets* refers to the networks where a type of message is traversing and the column *Mode* refers to the type of  routing. The column *Static DHT Prefixes* refers to the DHT prefixes of the receivers if we use a one DHT for all and use prefixes to separate sub-networks.

We use gossiping mainly when the message type is small. For example, GRANDPA votes and attestation are very small. For bigger data structures we need to either use bloom filters or use direct routing.

**Nets**:

$PC$ = Parachain Collator and parachain full nodes

$PV$= Parachain Validators

$V$ = Validator and relay chain full nodes (->Validator Network ID on chain)

**Mode**:

$D$ = Direct transfer

$G$ = Gossip

$B$ = Big / Bloomfiltered

$R$ = Receving e.g., $PC_{R}$ refers to the receiving parachain's collators and full nodes

$S$ = Sending e.g., $PC_{S}$ refers to the sending parachain's collators and full nodes

\* should soon change gossiping into direct routing

| Message type              | Nets        | Mode      | Static DHT Prefixes|
| ----------------- | ----------- | --------- |-----|
| Parachain TXs     | $PC$          | $G$        |Depends on Parachain|
| PoV block         | $PC$ + $PV$    | $D$         |-|
| Parachain Block   | $PC$ + $PV$     | $G$:$PC$, $D$:$PV$  |$P_0$,...,$P_n$|
| Attestations      | $V$           | $G$        |$V$|
| Relay chain TXs   | $V$           | $G$         |$V$|
| Relay chain block | $PC$ + $V$       | $G^B$        |General|
| Messages         | $PC_{R + S}$ | $G$ (fallback->D:$PV_{R}$ request $PV_{S}$ and then uses G at $PC_{R}$ to spread them, second fallback->D: $PV_{R}$ recover messages from erasure codes obtained from V and use G at $PC_{R}$ to spread them)         |V|
| Erasure coded    | $V$           | $G^*$         |$V$|
| GRANDPA Votes     | $V$           | $G$        |$V$|


## Critical Paths for Networking

We have two important goals: a) inclusion of parachain blocks (PBlocks) in Relay chain, and b) Relay chain blocks (RBlocks) get finalized.

The critical networking for reaching these goals are in order as follows.

### a) PBlock gets included on Relay chain

1. Validators $\xrightarrow[]{\text{latest RBlock}}$ Collator: G and Syncing
2. Collator $\xrightarrow[]{\text{included PBlock}}$ Collator: G and Syncing
3. Collator/PV $\xrightarrow[]{\text{Messages}}$ Collators(of receving parachain): G and Direct requesting (see below for more details on Interchain Messaging)
4. Collator $\xrightarrow[]{\text{PoV Block}}$ PValidator(of receving parachain): Advertise and Direct sending
5. PValidator $\xrightarrow[]{\text{Attestations+PBlock Header}}$ Validators: G


### b) RBlocks get Finalized

1. Validator $\xrightarrow[]{\text{PoV Block erasure-coded pieces}}$ Validators: Direct sending
2. Collators/Fishermen/Validators $\xrightarrow[\text{Post-inclusion claims}]{\text{TXs}}$ Validators: G

3. PValidators or Validators $\xrightarrow[]{\text{PoV Blocks}}$ Validators: G, Direct sending
4. Validators$\xrightarrow[]{\text{GRANDPA Votes}}$ Validators: G


## Bounded Gossip Protocols

We treat the goals of our networking protocols as black-boxes. While gossip may not be the most efficient way to implement many of them, it will fulfill the black-box functionality.

In some cases, we will be able to gossip only among a known set of nodes, e.g., validators.
In the case that we are not, the design of the gossip protocol will differ from a classical gossip protocol substantially.
For these cases, we introduce the notion of a _bounded_ gossip protocol.

We have the following requirements for nodes:

  1. Nodes never have to consider an unbounded number of gossip messages. The gossip messages they are willing to consider should be determined by some state sent to peers.
  2. The work a node has to do to figure out if one of its peers will accept a message should be relatively small


A bounded gossip system is one where nodes have a filtration mechanism for incoming packets that can be communicated to peers.

Nodes maintain a "propagation pool" of messages. When a node would like to circulate a message, it puts it into the pool until marked as expired. Every message is associated with a _topic_. Topics are used to group messages or encode metadata about them. They are not sent over the wire, but are rather determined by the contents of the message.

We define a node's peer as any other node directly connected by an edge in the gossip graph, i.e. a node with which the node has a direct connection. The node's peers may vary over time.

For every peer $k$, the node maintains a _filtration criterion_ $allowed_k(m) \rightarrow bool$

Whenever a new peer $k$ connects, all messages from the pool (filtered according to $allowed_k$ ) are sent to that peer.

Whenever a peer places a new message $m$ in its propagation pool, it sends this message to all peers $k$ where $allowed_k(m) \rightarrow true$.

Nodes can additionally issue a command $propagateTopic(k,t)$ to propagate all messages with topic $t$ to $k$ which pass $allowed_k$.

Multiple bounded-gossip protocols can be safely joined by a short-circuiting binary OR over each of the $allowed_k$ functions, provided that they do not overlap in the topics that they claim.

Note that while we cannot stop peers from sending us disallowed messages, such behavior can be detected, considered impolite, and will lead to eventual disconnection from the peer.

## Main subprotocols

The are three main networking protocols we require for Polkadot as follows:

i) GRANDPA gossiping

ii) Parachain networking, which includes: gossiping parachain blocks (attestation gossip) and sending/ receiving erasure coded pieces

iii) Interchain message-passing

Next, the schemes will be described in detail.
