====================================================================

**Authors**: Fatemeh Shirazi, Rob Habermeier

**Last updated**: 24.09.2019

**Note**: This write-up contains notes from a networking workshop 05.08.19-06.08.19 at Parity Technologies.

====================================================================
# Networking for Polkadot

## Overview

In Polkadot we need to send a number of messages to a number of entities.
First let's recap the different entity types:

- User - create and submit transactions to parachains or the relay chain.

- Collator - these belong to a specific parachain. They collate parachain
  transactions into blocks, generate proofs-of-validity and propose them to
  parachain validators as candidates for the next block. The latter two tasks
  (relating to validity) are part of Polkadot's rules, but how collation is
  done is chosen autonomously by the parachain.

- Validator - these belong to the relay chain and follow Polkadot's rules. Some
  validators are also assigned to specific parachains in order to validate
  those chains, and then we refer to them as a "parachain validator". They also
  collate transactions submitted to the relay chain.

Next, we have several subprotocols between these entities, each serving one
abstract part of the process of executing transactions:

1. Transaction submission - users find the relevant entities to contact for
   submitting a transaction, and submit them if they are reachable.

2. Parachain collation - parachain collators collect transactions into blocks,
   the internals of which are outside the scope of Polkadot, chosen by each
   parachain for themselves.

3. Parachain block attestation: collators also generate additional data and
   pass this to the parachain validators. The ultimate aim of this data is for
   the parachain validators to efficiently check that every parachain block
   satisfies the parachain validation function. To generate the data, the
   collators also need data from the relay chain, sent back by the parachain
   validators in an earlier stage of this process.

4. Relay-chain protocols: parachain validators attest to the validity of any
   parachain blocks they have been sent, and distribute these attestations to
   the other validators. Then they collate attested blocks plus relay chain
   transactions into a relay chain block, and finalise the block.

5. Inter-chain messaging: after a relay chain block is finalised and this fact
   is communicated back to the parachains, they check if these blocks contain
   new messages from other parachains, and retrieve and react them if so.

6. Parachain synchronisation: when a collator becomes connected for the first
   time or after being disconnected for a long time, it must retrieve and
   validate the latest state of the parachain, including transactions submitted
   in the interim and information about the latest state of the relay chain.

7. Relay-chain synchronisation: when validator becomes connected for the first
   time or after being disconnected for a long time, it must retrieve and
   validate the latest state of the relay chain, including transactions
   submitted in the interim.

Details have been abstracted away in the descriptions above, in an effort to
remain valid even if those details change. At the time of writing, subprotocols
(3-5) and 7 are, and are expected to remain, the largest and most complex
components that the Polkadot networking layer needs to be able to serve.

## Message types

Below we give a more precise and detailed overview of where and how each type
of message is sent, according to the subprotocol designs as of 2019 October:

TODO: convert the below into a nicer-looking table, needs conversion away from
markdown into something more powerful like reStructuredText.

- From users / light clients (subprotocol 1):
    - Users ->> Collator:
        - S  : P-transactions
    - Users ->> Validators:
        - S  : R-transactions

- Within a parachain (subprotocol 2):
    - Collators >>> Collators:
        - F  : R-blocks
        - F  : P-transactions
        - SF : P-blocks
        - SF : P-block-PoV
    - note: gossip protocol details chosen by the parachain, not polkadot

- Relay chain <-> parachain (subprotocol 3)
    - PValidators ->> Collator:
        - F  : R-blocks
    - Collator ->> PValidators:
        - SF : P-blocks
        - SF : P-block-PoV

- Within the relay chain (subprotocol 3)
    - Validators >>> Validators:
        - F  : R-transactions
        - SF : P-block-PoV-attestation-and-other-metadata ("candidate receipt")
    - Validators --> Validators: (or ->>, still open)
        - S  : PoV block, erasure coded pieces

- Within the relay chain (subprotocol 4)
    - Validators >>> Validators:
        - SF : R-blocks
        - SF : GRANDPA votes

- Between different parachains (subprotocol 5)
    - PValidator-1 ->> Collator-2:
        - F  : ICMP messages
    - Collator-1 ->> Collator-2:
        - S  : ICMP messages

Key for notation:

| symbol | meaning |
| ------ | ------- |
| --> | send, to specific recipient(s) |
| ->> | send, to non-specific recipients |
| >>> | gossip, to everyone eventually |
| S:  | sender is the source of the message (this includes new messages derived from other data) |
| F:  | sender is forwarding the message, received from someone else |

## Message keys and sizes

The following message types are expected to be arbitrary in size and not
suitable to be sent directly in a single transmission:

- P-block?
- P-block-PoV
- R-block

It may be beneficial to break these messages types up into chunks, or at the
very least they must be sent down a different stream so that they do not block
smaller message types, which tend to be more urgent.

The following message types are expected to contain an arbitrary number of
members and not be keyable to an indexable structure (e.g. blocks in a chain
can be keyed by height, pieces of an erasure coding can be keyed by x-coord):

- P-transactions
- R-transactions
- ICMP messages

In order to deduplicate them while gossiping, a more formal or rigorous
set-reconciliation protocol will be needed, perhaps involving bloom filters.

TODO: consider the above issues and propose something concrete

## Peer Discovery

TODO: entities from different sources/groups (e.g. parachain vs relay chain)
might need their own prefixes in the DHT.

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
