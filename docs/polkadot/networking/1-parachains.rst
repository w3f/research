\====================================================================

**Owners**: :doc:`/team_members/Ximin`

\====================================================================

====================
Parachain networking
====================

As part of how parachains get their blocks finalised on the Polkadot relay
chain, each parachain's collators must send PoV block information to their
parachain validators, who process it and then pass the result onto the
:doc:`block production protocol <2-block-production>`.

We refer to this process as the **block submission protocol**; this document is
about the networking part of that. It comprises several stages:

1. `Collators find the current validator set for their parachain, and select one to connect to. <#collators-selecting-validators>`_
2. `Validators receive the PoV blocks from collators. <#collator-validator-communication>`_
3. `Validators validate the PoV blocks they receive, and send these to other parachain validators. <#validator-validator-communication>`_
4. `Validators sign proposals and attestations over the PoV blocks they have validated, and send these onto the relay chain via gossip. At least one PoV block must have a quorum of attestations for the block-producing protocol to include it. <#passing-to-the-relay-chain>`_

We go into these in more detail below. First, some background:

Background
==========

Recall that in Polkadot:

- Collators are expected to follow the relay chain and be aware of its state -
  specifically, which validators are assigned to them at a given time, and what
  their public ids are.

- Validators are semi-trusted since they are staked.

- Collators are in general untrusted & unauthenticated.

  - In future, the parachain validation function may supply an interface that
    allows the parachain to restrict its collator membership set, this will
    take a while to develop.

- Blocks are unauthenticated during distribution (whilst being transferred),
  however after distribution once a validator has received it fully, they can
  run the validation function on it to authenticate it.

  - In future, the parachain validation function may supply an interface that
    allows the parachain to specify a way to pre-validate a block, e.g. that it
    must be signed by specific keys.

  - For now, the validator must buffer potentially bad data from malicious
    nodes; we deal with this securely below.

Design considerations
=====================

Collator-validator communication (item #2 in the list above) involves
communication across a trust boundary, and is therefore a key challenge in
terms of networking.

In fact the other items on the list are quite straightforward - the data flow
is determined by the Polkadot protocol at a higher layer, and there is really
not that much room for variation at the networking layer. We include basic
suggestions in our proposal below without further comment; they should be
self-evident and unproblematic. We do have possible future improvements in mind
but they require changes at higher layers too, and for this reason we leave the
discussion of such topics to `Future additions`_.

So for the rest of this section we deal with the security issues around #2.

Malicious validators are dealt with by another part of the Polkadot protocol,
specifically the rotation of validator groups. So here we are only concerned
with malicious collators. We cover a threat model based on the real world.
Malicious collators can:

- compete with connection attempts, by regenerating a new identity
- compete with bandwidth, e.g. by sending valid but redundant / old data. This
  attack is relatively costly to pull off, however.

Using these powers, attackers can completely censor legitimate data. However,
other attacks exist that are more subtle and harder-to-detect - for example
attackers can waste bandwidth and so reduce overall throughput. Therefore, our
defensive aim is for collators to send us PoV blocks in a way that uses our
bandwidth as *efficiently* as any honest collator would - we want to make it
hard for attackers to significantly reduce the normal operating efficiency.

In terms of defense mechanisms, we assume that validators can:

- control per-peer bandwidth
- select which peers they accept connections from

and will make use of these primitives in our proposals below.

Parachain security vs Polkadot security
---------------------------------------

It should be noted that the attacks mentioned above are common concerns of p2p
networks in general, and are not unique to Polkadot. Specifically, parachains
are also concerned about these types of attacks internally - as is the Polkadot
relay chain. However, one design goal of Polkadot is to support heterogeneous
parachains - i.e. for parachains to decide their own internal structure - so
for now we do not constrain how they can provide these properties internally.

Because of this, we must *also* consider these attacks for the block submission
protocol. The reason is that, even if the parachain internally is secure
against these types of attacks, Polkadot parachain validators are not expected
to participate in their parachain's protocols [#]_ - and therefore they are not
covered by these protections.

.. [#] They rotate across parachains frequently, therefore this would require
  implementing the internal protocol details of all parachains.

So the proposals we give below are necessary to cover this angle - for the
validator to gain some confidence that it can deal with malicious collators in
an effective way, without requiring additional parachain structure.

This is a design-decision trade-off in favour of parachain flexibility - and
consequently, the proposals below have to be somewhat heavyweight. In the
future, we would like to look into possible additional but minimal networking
structure for parachains, that can achieve these protections more efficiently
whilst retaining an acceptable and maximal level of flexibility.

.. _net-real-world-attacks:

Real-world attacks
------------------

Empirically, we observe these attacks succeeding more against smaller networks.
To date, large real-world networks have not been greatly affected by these
types of attacks, even though they are theoretically possible. One major reason
is that the attacks require a continual cost to execute - use of bandwidth -
and the costs increase with the size of the victim network. Even though the
rewards are greater for attacking larger networks, it would seem that the costs
have prevented attackers from sucessfully executing them so far.

Polkadot's structure is a bit different however - although the relay chain
network will be on a similar scale as the large networks today, individual
parachains will be much smaller. Indeed, part of Polkadot's very design is to
provide better consistency guarantees for these smaller parachains even in the
presence of moderately well-resourced attackers. However these do not protect
against the network-level attacks just described.

So it's prudent to consider these attacks in advance, as we do in this section.
However, the precise incentives of attackers are hard to model and can change
over time, and so our suggestions should be considered carefully in conjunction
with operational experience of real-world attackers and how they behave. In
particular, some of our suggestions below are rather heavyweight - though they
are intended to protect against the worst attacks, they also carry additionaly
development cost. Depending on the operational environment, they may be skipped
or simplified, or implemented in incrementally in stages as we have outlined.


Proposal: parachain networking, initial iteration
=================================================

Collators selecting validators
------------------------------

Collators are expected to be full-nodes of the relay chain, so have easy access to relay chain data. Specifically, which validators are assigned to a parachain at the current block.

In order to help load-balancing, the collator should shuffle this set using their own transport (TLS or QUIC) public key as a seed. Then they can try connecting to each validator in this order, stopping when the first validator accepts the connection.

For honest collators that choose their public key randomly, this will distribute these collators evenly across the set of validators. (Malicious collators that attempt to overwhelm a single validator, are dealt with in the below section.)

Collator-validator communication
--------------------------------

This section describes collator-validator direct communication, from the perspective of validators attempting to defend against potentially-malicious collators since that is the hard part.

(An honest collator being serviced by a malicious validator is a problem, but it is largely protected by rotating the validator groups around; our 2/3-honest assumption over the validators means that the effect of a malicious validator only lasts for a short time against any parachain.)

The high-level proposal goes as follows:

1.  We track the efficiency of each peer, i.e. byte counts for:

    1. total data received
    2. data that is pending validation
    3. data that has been validated and was not already received
    4. data that has been validated but was redundant i.e. wasted bandwidth
    5. data that failed to validate

    Since identities are easy to regenerate, the data we track should include
    the peer's address, as well as the time of observation.

    To avoid peers spamming bogus or no-op requests, this should include all
    bytes received - including metadata e.g. request headers.

    As we recommend here and as a general principle, it is important to store
    **empirical observations**, and not just the conclusions derived from them.
    A key reason is that past observations are not going to change - however if
    we change the derivation algorithm, we will want to re-derive the score
    from observations. Another reason is that sometimes we cannot derive a
    score straight away, e.g. if the derivation requires other data we don't
    have yet. In such a case we will need to defer the score derivation, and
    record this fact as a "debt" so the peer can't overwhelm us with deferrable
    score derivations.

2.  From the above, we maintain a whitelist of most-efficient peers, as well as
    a blacklist of peers that send us invalid data or whose efficiency are
    below some certain threshold.

    Being added to the blacklist implies disconnection of a peer. (They may try
    to reconnect; this is dealt with by (3).)

3.  We use the whitelist and blacklist to generate an IP address "heat map",
    which affects which new peers we communicate with - i.e. connect to, or
    accept incoming connections from.

    Since IP addresses are dynamic, this heat map should fade over time - i.e.
    IP addresses we observed further back in the past should have less weight.
    (There may be other criteria we can use, IP address is the most obvious.)

4.  When rotating groups, we pass on this reputation information from the old
    group to the new group, so the new group can more quickly find good peers.
    This opens up some potential for dishonest validators to manipulate network
    behaviour, but in (3) the heatmaps fade over time, so this is limited.

We track efficiency and not just validity, which there are a whole class of
sophisticated bandwidth-wasting attacks that transmit valid-but-redundant data.
This is a straightforward way of making these attacks much harder, since the
attacker is forced to compete with actual genuine peers with regards to the end
performance that the application actually cares about.

We elaborate on the above in more detail below, with further justifications on
why they help to improve security:

0.  We need a pre-validation interface, a.k.a. incremental-validation interface. This would be in addition to the existing (full) validation function interface for parachains.

    This enables validators to receive PoV blocks from collators in smaller pieces. Otherwise each validator must buffer up to 30MB of potentially-bogus data from every collator peer it is servicing; or more, if they want to allow for the possibility of multiple competing PoV blocks. With this mechanism available, we can buffer much less data. This is the most urgent immediate priority.

    See `Pre-validation`_ for more details.

1.  Even with an incremental-validation function, collator peers can perform bandwidth-wasting attacks by sending us valid but redundant data, that can result in a parachain losing e.g. 2/3, 3/4, etc of its potential throughput. These attacks are hard to detect directly, since an attacker can always make a plausible-deniability defence "I didn't know you already had the data from someone else".

    To defeat these attacks, each validator should measure the proportion of non-redundant valid data it gets from each peer. If any peer remains in the bottom X% of peers efficiency-wise, for longer than Y time, then we will disconnect them and accept a connection from a new stranger peer. (X and Y should be chosen so that the resulting churn does not negatively affect performance too much, in the common case where there is no attack.)

    Thus attackers are forced to compete with genuine users in terms of the actual end performance that the application cares about - efficient use of bandwidth, i.e. throughput. This is more direct than "reputation scores" with vague semantics, and hopefully more effective.

    As an implementation note, received pieces may switch status after being received (e.g. be initially unvalidated, then validated later), so the measurement mechanism needs to account for this.

    As a future addition, we can reserve more buffer space for unvalidated data, for peers that have historically been more efficient. One can think of this as analogous to a "credit rating".


2.  Even with good bandwidth measurement, attackers can easily generate new identities, a new IP address (e.g. in a IPv6 block), and reconnect to us again sending us more bogus data, wasting our bandwidth.

    To protect ourselves against this scenario, we want good bandwidth control in addition to measurement. For example, 80% of our bandwidth can be reserved for the top X peers efficiency-wise. Then, newly-connected peers with no efficiency score, can only waste 20% of our bandwidth.

3.  Even with good bandwidth control, attackers can DoS other collators by competing for a validator's attention in accepting new incoming connections. We can only defend against this via heuristics, and the most obvious piece of information is the source IP address. (For example, Bitcoin does not connect to 2 peers that share the same /16).

    For parachain networking, if any peer sends us data that is eventually invalidated, their IP address and violation-time is recorded on a blacklist. Since IPv6 addresses are easy to generate, this blacklist affects not only those specific addresses, but is used to generate a "heat map", and then we prefer to accept new incoming connections from cooler parts of the heat map. Violations further back in time contribute less to the heat map, since IP address allocations change over time.

    Initially we can start with something very simple, and make this more sophisticated / flexible later. We also need to figure out how to make this work concretely; the standard C TCP API function `accept(2)` does not let the caller selectively choose which pending incoming connection to accept based on address, but we can see if QUIC can provide us with such an API.

    The security justification is heuristic - an attacker is likely to control a clustered set of IP addresses, rather than being evenly distributed across the whole IP address space. Of course it also pollutes genuine users operating under similar IP addresses; however if no other addresses want service then we will still accept connections from the affected address ranges. Thus the heuristic is based on competition from unaffected IP address ranges, rather than being a hard block.

4.  As time goes on, parachain validation groups rotate. To help the new group bootstrap to a good set of peers initially, the old group tells the new group which peers they believe were the best efficiency-wise - acting as a whitelist.

    This whitelist is only used by the new group to select their initial collator peers; after that the new group tracks efficiency and blacklist as above, i.e. by their own observations without input from the old group. [*] Generally speaking, reputation systems that rely too much on information from others, can themselves be abused more easily.

5.  Validators can tell each other about their whitelists and blacklists; this can be used to guide the acceptance of new incoming connections, including load-balancing - for example we don't want to accept a collator that is already being served by another validator.

    Since the implementation of this depends on all of the above, the details of this are left open for future elaboration, bearing in mind the point [*] above.



Validator-validator communication
---------------------------------

Since each PoV block needs a minimum number of attestations from validators, this part helps that achieve in a reasonable amount of time. (Otherwise, the parachain collators must send the same PoV block to multiple validators directly, which may be a bandwidth burden for smaller parachains.) It also adds some protection from DoS attacks against the parachain, where malicious collators compete with honest collators for attention from the validators - if at least one honest collator sends a PoV block, the validator servicing it will pass it onto the others for attestation.

This is done via a mini-overlay network over the parachain validators, structured as a d-regular random graph, generated deterministically via some seed material from the relay chain that is specific to the parachain. Whenever a validator successfully validates a PoV block, it is forwarded along these links to any other neighbour peers that do not already have the same PoV block.

As a future addition, this network can be used for metadata broadcasts along the lines of "I have successfully validated PoV block X". Other validators when seeing this, can then favour receiving X over other PoV blocks, helping to speed up the attestation process by all preferring to receive and validate the same block, rather than different blocks at the same time.


Passing to the relay chain
--------------------------

The parachain networking component is not responsible for resolving forks; however to ensure we don't overload the block production protocol with too many forks, we introduce a special type of attestation called a "proposal" that each validator is only supposed to make one of. (If they make more than one, this is grounds for slashing.)

The first PoV that a validator receives and validates, they sign a proposal for, and forward this to the relay chain gossip network.

Any subsequent PoVs that a validator receives and validates, they sign a regular attestation for, and forward this to the relay chain gossip network.

The block production protocol looks to receive a minimum quorum of attestations for each PoV block. Based on a trade-off between security and network unreliability, we set the quorum to be 2/3 of the validator set - note this is unrelated to the 2/3 consensus thresholds. 

Sentry nodes
------------

Note: sentry nodes are being deprecated soon, at which point this section will be obsolete and will be deleted.

As described elsewhere, sentry nodes are essentially proxies for their single private validator, largely for anti-DoS purposes. Note that the term "private validator" is structural rather than security-related - the limited privacy is easily broken with a modest amount of resources, so should not be relied on.

In order to support the above proposal for parachain networking, sentry nodes must perform some additional functions beyond dumb proxying, described below.

Generally, the sentry node must proxy the data transfer of the PoV block - from either a collator or another validator, to the private validator recipient. This is conceptually quite straightforward; though care should be taken to ensure that backpressure from the recipient is passed through to the sender.

If we choose a pull-based protocol with advertisements: the sentry node has to remember which collator issued which advertisement, so it can forward the pull request from its private validator to the correct collator.

If we choose a push-based protocol with multi-acks: the sentry node doesn't have to remember anything; it broadcasts the multi-ack from its private validator, to all connected collators.

Additionally, since we want validators to connect to each other, we would like the private validator to be able to control its sentries' peers. If we do not have this ability, then the multiple sentries of a private validator must co-ordinate between each other in order to avoid overloading (all connecting to) the same neighbour validator (or one of its sentry nodes). It is easier for the private validator to make this decision itself, and tell one of its sentry nodes to make the outgoing connection.

Pre-validation
--------------

A pre-validation function is defined by the parachain. Given:

- a parachain block header
- some opaque certificate data presented by the collator
- a collator's public key

together occupying no more than $reasonable KB (TBD), it returns true iff:

- the block header is valid for the parachain's current state (i.e. chain tip), and
- the collator's public key is authorized by the block header, possibly via the opaque certificate

When a validator receives such data, it runs this function. If true, this gives the collator the right to then send the larger PoV block to the validator. This provides some protection against DoS attacks by the collator, that send a large amount of data pretending to be a PoV block that does not then pass the full-validation function.

Security is based on the assumption (to be satisfied by the parachain) that the header is hard to create - e.g. a PoW or proving membership of a PoS staking set. If a parachain defines a weak pre-validation function, this will allow their parachain validators to be DoSed by malicious collators. So it is in the interests of the parachain to define a strong pre-validation function.

Future additions
================

When implementing the above proposal, please bear in mind the long-term ideas below, as to make them not too awkward to add later.

- Some way to prioritise between different proposers, for parachains that have that concept. For example, the pre-validation function could return an explicit priority number for the header; or we could have an additional comparison function over pairs of headers as an implicit priority ordering.

  Censorship attacks remain possible, with or without this comparison function. e.g. bribe validators to choose their preferred collator, ignoring the priority.

- Incremental validation, allowing collators to send small pieces of the same PoV block simultaneously. This means we can reduce the amount of unvalidated data that must be buffered, as well as helping to improve overall throughput.

  Some parts of this concept overlaps with A&V erasure-coded pieces, and we can probably re-use a bunch of logic from there. One difficulty is that A&V erasure-coded pieces include some information not known to collators, such as some state from the relay chain.


Appendix
========

Reputation systems overview
---------------------------

The term "reputation system" is commonly thrown around to refer to a few
different things:

1.  Aggregating lots of local scores by many sources about some target, into a
    single score for the target. (The aggregated score could be different from
    each source's perspective.) Examples: trust metrics (advogato), PageRank,
    sybil-detection algorithms.

    Polkadot: for parachain networking this is not a major concern since there
    are only 10 parachain validators per parachain. Any aggregation system only
    needs to not be trivially-attackable by 9 other validators. It is relevant
    for chains that want to serve lots of unauthenticated users however, such
    as the relay chain itself, so it's a topic to cover elsewhere.

    For more details see appendix, for now we skip.

2.  In (1) we didn't explain where the local scores come from. Some proposals
    have this manually input by the user, but this is inconvenient & hard to
    reason about. Other systems propose ways to automatically calculate such
    scores, based on empirical observations by the source of that target's
    behaviour.

    Polkadot has currently an ad-hoc implementation of such a system. It is not
    documented and its design decisions are unclear. For parachain networking
    we would like to derive a new system from first principles.

3.  How a source responds to future interactions with a target, depending on
    the score, either aggregate (1) or local (2) or both. This is often grouped
    together with either (1) or (2), but may be better considered separately.

    Specifically, certain responses are inherently unsafe regardless of how you
    arrived at the score driving the response. For example, it is ineffective
    to disconnect or ban a peer with low score, if all they need to do is to
    generate a new public key and IPv6 address, then reconnect you and spam
    your bandwidth again. To protect against this, you must have fine-grained
    control over your resources, and perhaps other mechanisms too.

In this rest of this document we focus primarily on (2) and (3).

Aggregating scores
------------------

The standard "universal attack" that everyone tries to defend against, is where
the attacker copies the entire topology of the genuine network, and somehow
gets a bunch of genuine nodes to peer with some of their nodes. Solutions must
break the symmetry here by assuming the source peer (doing the aggregation) is
honest, perhaps in addition to certain other user-specified nodes. Then the
aggregated score depends on these seeds of trust.

Because of this attack, solutions without a concept of trust-seeds can be
dismissed out-of-hand as being inherently insecure; Google themselves had to
add this concept into PageRank a few years after they started.
https://www.seobythesea.com/2018/04/pagerank-updated/

State-of-the-art in 2020 is generally based on random-walks / network flow
which work under the assumption that it is costly for an attacker to create
edges to genuine nodes. These algorithms are closely related to community
detection algorithms in network analysis. Some of them propose to be used on
real-world data such as social graphs. In addition to privacy concerns, we
suspect they may generate false positives when the network is genuinely divided
into subcommunities with low flow between them. However there is insufficient
research in this area currently to draw firm conclusions.

Google keep claiming they have internal work beyond PageRank, but refuse to say
publicly what it is or the ideas behind it. Possibly security by obscurity,
possibly genuinely novel & useful stuff they should publish.
