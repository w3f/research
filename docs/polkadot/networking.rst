\====================================================================

**Owners**: :doc:`/team_members/Ximin`

**Other authors**: Fatemeh Shirazi, Rob Habermeier

\====================================================================

==========
Networking
==========

.. toctree::
   :hidden:
   :glob:
   :maxdepth: 1

   networking/*

Overview
--------

To recap, :doc:`Polkadot </polkadot>` consists of a unique relay chain interacting with many different parachains and providing them with security services. These require the following network-level functionality, generally for distribution and availability:

1. As with all blockchain-like protocols, the relay chain requires:

   a. accepting transactions from users and other external data (collectively known as *extrinsic data*), and distributing them
   b. distributing artefacts of the :doc:`collation subprotocol </polkadot/block-production>`
   c. distributing artefacts of the :doc:`finalisation subprotocol </polkadot/finality>`
   d. synchronising previously-finalised state

   As an important special case, parachains may choose to implement themselves according to the above structure, perhaps even re-using the same subprotocols. Part of the Polkadot implementation is architected as a separate library called `substrate` for them to do just this.

2. For interaction between the relay chain and the parachains, we require:

   a. accepting parachain blocks from parachain collators
   b. distributing parachain block metadata including validity attestations
   c. distributing parachain block data and making these :doc:`available for a time </polkadot/Availability_and_Validity>`, for auditing purposes

3. For interaction between parachains, we require:

   a. distributing :doc:`messages between parachains </polkadot/XCMP>`, specifically from the relevant senders to the relevant recipients

For each of the above functionality requirements, we satisfy them with the following:

- 1(b), 1(c), 2(b) - artefacts are broadcast as-is (i.e. without further coding) via `Bounded gossip`_ - see also :doc:`networking/2-block-production` and :doc:`networking/5-consensus` for details specific to those protocols.
- 1(a), 1(d) - effectively, a set of nodes provide the same distributed service to clients. For accepting extrinsics or blocks, clients send these directly to the serving node; for synchronisation, clients receive verifiable data directly from the serving node.
- 2(a) - this is another type of distributed service, but is a special case from the previous type due to information travelling across a trust boundary, see :doc:`networking/1-parachains`.
- 2(c) - special case, see :doc:`networking/3-avail-valid`. Briefly, data is erasure-encoded and different recipients each receive a small part of the whole data; pieces are sent directly via QUIC over a topology custom-designed for this purpose.
- 3(a) - special case, see :doc:`networking/4-xcmp`. Briefly, messages are transferred from the sending parachain to the recipient parachain via validators who act as proxies; in the process outboxes containing messages to many recipients, are assembled into inboxes containing messages from many senders.

We go into these in more detail in the next few subpages. Finally, we talk about the lower layers underpinning all of these subprotocols, namely :doc:`networking/L-authentication` and :doc:`networking/L-discovery`.

Message keys and sizes
----------------------

The following message types are expected to be arbitrarily-large in size and not suitable to be sent directly in a single transmission:

-  P-block? (~1 MB)
-  P-block-PoV (~10 MB)
-  R-block (~1 MB)

All other message types are expected to be fairly small (<10 KB) and are suitable to be sent in a single transmission (even if the physical network performs fragmentation).

It may be beneficial to break these messages types up into chunks, or at the very least they must be sent down a different stream so that they do not block smaller message types, which tend to be more urgent.

The following message types are expected to contain an arbitrary number of members and not be keyable to an indexable structure (e.g. blocks in a chain can be keyed by height, pieces of an erasure coding can be keyed by x-coord):

-  P-transactions
-  R-transactions
-  XCMP messages

In order to deduplicate them while gossiping, a more formal or rigorous set-reconciliation protocol will be needed, perhaps involving bloom filters.

TODO: consider the above issues and propose something concrete

Bounded gossip
--------------

We treat the goals of our networking protocols as black-boxes. While gossip may not be the most efficient way to implement many of them, it will fulfill the black-box functionality.

In some cases, we will be able to gossip only among a known set of nodes, e.g., validators. In the case that we are not, the design of the gossip protocol will differ from a classical gossip protocol substantially. For these cases, we introduce the notion of a *bounded* gossip protocol.

We have the following requirements for nodes:

1. Nodes never have to consider an unbounded number of gossip messages. The gossip messages they are willing to consider should be determined by some state sent to peers.
2. The work a node has to do to figure out if one of its peers will accept a message should be relatively small

A bounded gossip system is one where nodes have a filtration mechanism for incoming packets that can be communicated to peers.

Nodes maintain a “propagation pool” of messages. When a node would like to circulate a message, it puts it into the pool until marked as expired. Every message is associated with a *topic*. Topics are used to group messages or encode metadata about them. They are not sent over the wire, but are rather determined by the contents of the message.

We define a node’s peer as any other node directly connected by an edge in the gossip graph, i.e. a node with which the node has a direct connection. The node’s peers may vary over time.

For every peer :math:`k`, the node maintains a *filtration criterion* :math:`allowed_k(m) \rightarrow bool`

Whenever a new peer :math:`k` connects, all messages from the pool (filtered according to :math:`allowed_k` ) are sent to that peer.

Whenever a peer places a new message :math:`m` in its propagation pool, it sends this message to all peers :math:`k` where :math:`allowed_k(m) \rightarrow true`.

Nodes can additionally issue a command :math:`propagateTopic(k,t)` to propagate all messages with topic :math:`t` to :math:`k` which pass :math:`allowed_k`.

Multiple bounded-gossip protocols can be safely joined by a short-circuiting binary OR over each of the :math:`allowed_k` functions, provided that they do not overlap in the topics that they claim.

Note that while we cannot stop peers from sending us disallowed messages, such behavior can be detected, considered impolite, and will lead to eventual disconnection from the peer.
