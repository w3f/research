====================================================================

**Authors**: Rob Habermeier

**Last updated**: 12.09.2019

====================================================================
## Parachain networking

### Attestation Gossip: gossiping parachain blocks

We have an attestation-gossip scheme such that nodes can potentially have earliest access to see misbehavior, which means a fisherman reward is open to them. In the attestation gossip the latest block is distributed.

A new attestation topic is started for each new block.
A topic expires when the block to which it refers to is no longer a _viable leaf_: either some competing fork has finalized, or some new block has been built on top of this.

`fn topic_for(header_hash) = H('parachain_attestation' ++ header_hash)`

Because there are going to be many blocks in the chain, and different peers will have different views of which topics are expired, we will want to limit the messages a peer can receive to only messages it perceives as _live_.

We say that a topic is _live_ to a node if the node is currently at a view with a viable leaf with that topic.

The main means by which we limit gossip to _live_ messages is the same as in GRANDPA, by view co-ordination. Nodes will periodically send their neighbors in the gossip graph a message notifying them of their latest view. It is protocol misbehavior to send messages which would not be considered _live_ under the latest view received.

Full nodes don't need to see these in order to reach consensus, but it is safer for them to relay those which are recent.
Erasure-coded availability pieces are meant to be propagated, but we are ignoring those for the moment.

**Neighbor View Updates:**
- Chain Heads: `Vec<Hash>` up to arbitrary constant N of viable leaves according to that peer. in practice there will only be 1 or 2 but let's say N=5. None of the chain heads may be descendants of each other or ancestors of any chain heads sent in the prior packet. Doing this check for all chain heads in all prior updates is not tractable, but it's possible this could be left open to a "flip-flop" attack of some kind.

**Gossip Messages:**
- **Candidate:**
    - Members
        - Parachain candidate
        - Validator public key
        - Signature
        - Relay Parent
    - This is an announcement of a parachain candidate to the network. Only one announcement may be made by each validator per relay parent hash. Receiving this message from a peer indicates that the peer is aware of the candidate. Sending this message to a peer will make the peer aware of the statement, and should be done only if there is no prior indication of awareness.
- **Valid:**
    - Members
        - Candidate Hash
        - Validator public key
        - Signature
        - Relay Chain Parent Hash
    - This is an attestation on the candidate with given hash, that indicates the candidate is both valid and has block data available. May only be sent to peers who are aware of the `Candidate`.
- **Invalid:**
    - Members
        - Candidate Hash
        - Validator public key
        - Signature
        - Relay Chain Parent Hash
    - This is an attestation against the candidate with given hash. May only be sent to peers who are aware of the `Candidate`.

### Direct Routing: sending/ receiving erasure coded pieces
