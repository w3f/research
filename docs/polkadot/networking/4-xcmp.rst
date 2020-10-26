\====================================================================

**Owners**: :doc:`/research_team_members/Ximin`

**Other authors**: Rob Habermeier, Fatemeh Shirazi

\====================================================================

=====================
Cross-chain messaging
=====================

:doc:`/polkadot/XCMP` is Polkadot's subprotocol that enables a parachain to
communicate with another. Like the :doc:`A&V protocol <3-avail-valid>`, an
instance of this subprotocol starts when the relay chain block production
protocol has :doc:`output a new candidate block <2-block-production>`.

To recap, this candidate block references a bunch of parachain blocks. As
defined by XCMP, each of those blocks might indicate that the parachain wishes
to send messages to another parachain. To save bandwidth, and since no other
parachains need to receive the data, the message bodies are not contained
within these blocks, and must be transferred separately. The purpose of XCMP
networking is to perform these transfers for the overall XCMP protocol.


Background
==========

High-level requirements
-----------------------

R1. At least one message from every (non-empty) ingress queue must be
transferred to the corresponding receiving parachain, so that they may perform
their obligation to ack at least one message.

R1a. We must distribute it to *enough* collators of the receiving parachain so
that the parachain cannot be attacked by malicious collators. (TODO: currently
"enough" is not well-defined, as Polkadot does not assume any structure in a
parachain in order to begin defining this.)

R2. Ideally, allow recipients to select which message(s) to receive first,
subject to the :ref:`XCMP fairness constraints <polkadot/XCMP/index:fairness>`.

See also `security considerations`_ below.

Out-of-scope
------------

Polkadot XCMP networking is only responsible for distributing messages from
sending to receiving parachains. It is *not* responsible for distributing
messages within parachains. This is the responsibility of each parachain,
specifically their networking layer, and may be different per parachain.

Typically at least, parachains will want to including some logic to ensure that
each node uses only a bounded (e.g. zero) amount of memory to store unverified
messages, where "unverified" means the message has not (yet) been observed on
the Polkadot relay chain to have actually been sent by the sending parachain.
The Polkadot Host software should contain a concrete reference implementation
of a gossip protocol that implements this logic.

Assumptions
-----------

Polkadot (at the time of writing) does not assume much about the structure of
parachains. The flexibility here however, means we are less flexible when
designing how Polkadot can interface with parachains. Specifically, parachains
in general do not have a list of specific peers that validators can initiate
contact with; as a consequence contact must be initiated by the parachain
collators to the Polkadot validators.

This is mainly due to the fact that Polkadot wants to support permissionless
parachains where there is no fixed membership set - it is an open research
question how to fairly & securely select a subset of peers in such a context,
and we are working on it separately.

Our initial proposal will be built on top of this lack of structure, but we
will briefly mention alternate design possibilities that require additional
networking structure, that give better properties (e.g. more efficient) and may
be feasible once we have resolved these hard questions.


Evaluation of options
=====================

Since we cannot initiate connections to collators, we need to specify some
validators that both sending collators and receiving collators can both connect
to, that stores the message temporarily for them.

The Polkadot design already assigns validator groups to parachains, and they
are used in the :doc:`block submission protocol <1-parachains>` to receive PoV
blocks sent by parachains. The PoV block includes outgoing XCMP messages, so
via this process these validators already have the messages. So using them is
"free" from the perspective of XCMP networking, and an obvious candidate. From
here on, we'll refer to these as "sending validators".

One downside of this is that receiving collators will have to connect to a
different validator for every incoming sending parachain. So another option is
to assign particular validators to store *incoming* messages for particular
collators - as opposed to outgoing messages, in the previous paragraph. From
here on, we'll refer to these as "receiving validators".

We can also combine these two structures together - i.e. sending collators pass
messages to sending validators, who pass them to receiving validators, who pass
them (upon request) to receiving collators.

These three options, are our primary options for the initial design. Of course,
there are infinite other options - but for now we'll focus on these "obvious"
ones and consider the consequences and properties of them in detail, below.

Security considerations
-----------------------

We are concerned about the following threats:

- Malicious receiving collators receiving messages (either via push or pull),
  then throwing them away. There is a sliding scale as to the severity of these
  - the attacker may be able to selectively block specific messages with high
  probability (a.k.a. a censorship attack), or they may only be able to reduce
  the effective throughput of overall incoming messages to a parachain (a.k.a
  a bandwidth-wasting attack).

  Whoever we choose to be the point-of-contact of the receiving collators, will
  be responsible for defending against these types of attacks.

- Malicious sending or receiving validators receiving messages, then throwing
  them away. That is, if we designate either sending or receiving validators to
  forward messages on behalf of a sending parachain, they must store the
  messages until the receiving parachain has acknowledged them. Due to the
  security design of Polkadot, there is a small chance that a validator group
  may be all-malicious and perform this attack, in which case we need a
  fallback retrieval mechanism.

  Note that unlike in :doc:`1-parachains`, it is not sufficient here to wait
  until the assigned group rotates into one that is good (with overwhelming
  probability) since XCMP messages are associated with specific relay-chain
  blocks, whereas the ability to submit a block is an abstract capability that
  does not change from one relay-chain block to the next.

XCMP networking is not directly concerned with the following:

- Malicious collators sending or validators forwarding invalid messages - since
  by other (non-networking) parts of XCMP, collators can verify these against
  the relay chain state.

  However the verification process needs to inform the networking layer about
  peers that send invalid messages, so that actions can be taken against them.

----

In terms of the three main options above:

- Using either sending-validators only or receiving-validators only, results in
  more collator-validator connections compared to using both: for example with
  sending-validators only, every collator (of a receiving parachain) must talk
  to a validator of every parachain sending to it; and vice-versa for
  receiving-validators only.

  This makes it harder to detect malicious collators - in general if you talk
  to lots of different peers, you observe less of their behaviour, i.e. you
  have less information to determine if they're doing the right thing or not.
  The general principle to aim for, is to limit the different number of peers
  you have to talk to - this makes it easier to build up an idea of how
  efficient each peer is. (See :ref:`net-XCMP-distinguish-malicious-collators`
  to see this applied to XCMP.)

  So from this perspective, it is better to use both sending and receiving
  validators groups.

- On the other hand, using more validator groups introduces more places at
  which messages can get lost or censored: if the entire validator group is
  malicious then the XCMP message may get lost entirely, which would freeze
  that parachain - since our fairness property blocks them from progressing
  until they have processed this message.

  Therefore, we would need to specify a backup retrieval mechanism for
  receiving collators, in the event that all assigned validators are malicious
  and block them from receiving their rightful messages.

  So from this perspective, it is better to use fewer validator groups, in
  direct opposition to the above point.

Real-world attacks
``````````````````

The caveats mentioned in :ref:`net-real-world-attacks` in the parachains
networking chapter, apply here for XCMP networking as well.

In particular, some of our suggestions below are rather heavyweight - though
they are intended to protect against the worst attacks, they also carry
additionaly development cost. Depending on the operational environment, they
may be skipped or simplified, or implemented in incrementally in stages as we
have outlined.


Pipelining
----------

As just mentioned, verifying incoming XCMP messages requires waiting for the
sent messages to appear on the relay chain, which takes time. It would save
time, if these two processes happen in parallel:

1. XCMP networking distributes message bodies from sending to receiving parachain
2. XCMP authentication includes sent messages onto the relay chain

However (1) is initially unable to use security information from (2), and so
we'll need to figure out how to buffer unverifiable message bodies in a secure
way, as we wait for the relevant security information to arrive. A future
iteration of XCMP networking may attempt to cover this.

Other considerations
--------------------

Parathreads do not have an associated validator group until after they have
produced a block. So there are no "receiving validators" in this scenario -
that is unless we modify the higher-level Polkadot protocol to associate
receiving parathreads with a validator group.

Whether we choose push vs pull primarily affects which parties must be publicly
reachable - if push then the recipients must be reachable, if pull then it is
the sender (responding to the pull request) that must be reachable.

Pull can also make it easier to protect against certain types of spam attacks,
but these are not relevant in the initial iteration of XCMP networking - since
we opted to send message bodies only after they are added to the relay chain
(i.e. forego the possibility of pipelining), which provides an anti-spam
mechanism already.


Communication complexity
------------------------

The communication complexity for our primary options listed above, can be
approximated as follows:

+---------------------+----------------+---------------+---------------------------+-----------------------------+----------------------------+
| Role                | Number in role | No validators | Sending validator         | Sending + Receiving         | Receiving validator        |
+=====================+================+===============+===========================+=============================+============================+
| Sending collator    | $$R(C+S)$$     | $$ORc$$       | $$1 v$$                   | $$1 v$$                     | $$O v$$                    |
+---------------------+----------------+---------------+---------------------------+-----------------------------+----------------------------+
| Sending validator   | $$V$$          | $$0$$         | $$\\sum_{1+J} {(1+O)Rc}$$ | $$\\sum_{1+J} {1Rc + O v}$$ | $$0$$                      |
+---------------------+----------------+---------------+---------------------------+-----------------------------+----------------------------+
| Receiving validator | $$V$$          | $$0$$         | $$0$$                     | $$\\sum_{1+K} {1Rc + I v}$$ | $$\\sum_{1+K} {(1+I)Rc}$$  |
+---------------------+----------------+---------------+---------------------------+-----------------------------+----------------------------+
| Receiving collator  | $$R(C+T)$$     | $$IRc$$       | $$I v$$                   | $$1 v$$                     | $$1 v$$                    |
+---------------------+----------------+---------------+---------------------------+-----------------------------+----------------------------+

using the following definitons:

=== =====================================================
$C$ number of parachains
$T$ number of parathreads
$S$ number of parathread slots
$V$ number of validators
$J$ $S/C$ - assuming every sending validator group "works for" 1 sending parachain and J sending parathreads
$K$ $T/C$ - assuming every receiving validator group "works for" 1 receiving parachain and K receiving parathreads
$R$ collator redundancy factor. Note that the validator redundancy factor is already built into the structure of $V$.
$O$ number of outgoing paras for the given sending para
$I$ number of incoming paras for the given receiving para
$c$ A collator
$v$ A validator
=== =====================================================

So for example, $\\sum_{1+J} {(1+O)Rc}$ is to be read as "The sum over $1$
parachain and $J$ parathread slots, of $1$ plus the number $O$ of outgoing
paras multiplied by the redundancy factor $R$ i.e. the number of collators we
must talk to for that para.

Note that $J$, $K$, $R$, $O$, and $I$ may not be constant; they may depend on
which parachain / parathread is being talked about - that is why the above
table is only an approximation. One may approximate / simplify it further by
treating e.g. $\\sum_{1+J} {(1+O)Rc}$ as $(1+J).(1+O)Rc$.

The total communication complexity cost for a given strategy (represented by a
column), can be approximated as the inner product of (a) the "number in role"
column, and (b) that given column. For example the complexity for "No
validators" is approximately:

$$\\sum_{R(C+S)}{ORc} + \\sum_{V}{0} + \\sum_{V}{0} + \\sum_{R(C+T)}{IRc}$$

The lack of structure Polkadot assumes about parachains, makes it difficult to
safely set $R$ to its minimum value of 1. For validators, we can "pair off"
validators in different groups - as we do in the :doc:`A&V <3-avail-valid>`
subprotocol - which means it is still reasonably safe to have a validator
redundancy factor of 1. However we cannot pair off collators of different
paras, or even collators and validators of the same para. So $R$ may have to be
3 or 4 or even higher, which increases the associated costs.

Comparison with A&V
-------------------

Similarities:

- Data flow pattern (qualitative), i.e. outboxes to inboxes

Differences:

- Data usage profile (quantitative) - Less overall traffic, but much greater variability
- Latency not such a big deal, can be similar to A&V, but in practise should complete quicker due to less overall traffic.


Proposal: XCMP networking, initial iteration
============================================

FIXME: this section needs to be updated & re-written

1. sending-validators-only, easy to implement

2. sending-validators with some way to reduce number of connections. TODO

3. sending and receiving validators, with some availability checks. TODO

   - Introduce the idea of receiving validator group, even for parathreads.

If watermarks do not advance for e.g. 10 blocks, then the relay chain will
accept the message body as a backup. This provides some assurance against
malicious or inefficient validators not forwarding XCMP messages. (issue #601)

Sending collators send message bodies to their sending validator group, as part
of the :doc:`parachain block submission <1-parachains>` and :doc:`A&V
<3-avail-valid>` subprotocols.

Sending validator groups send message bodies to the relevant receiving
validator groups, using a mixture of push and pull.

Receiving collators pull message bodies from their receiving validator group.
As an optimisation, receiving validators may push to any receiving collators
that they are already connected to.

Since ingress queues may be long, receiving collators should request messages
from (near) the front of the queue to ensure that their parachain can process
the messages in the correct order in a timely fashion. Validators may enforce
this at their discretion by refusing to transfer messages too far forward in
the queue; we leave the details of this open for now - but we note that the
mechanism described in the next section ought to discourage this without any
explicit enforcement at this level.

TODO: chains can only communicate when they've opened a channel to each other,
the state of which is stored on-chain. We can potentially use this information
to derive more efficient topologies for XCMP.

.. _net-XCMP-distinguish-malicious-collators:

Distinguishing honest vs malicious receiving collators
------------------------------------------------------

The lack of structure we assume about parachains, gives us fewer options to
determine if a receiving collator is "honest" vs "malicious". Despite this we
do still have some information we can make use of for this purpose, that is
related to the fundamental high-level requirement of this part of XCMP. Recall
that the purpose of having collators receive messages, is for their parachain
to act on them, and acknowledge this to the Polkadot relay chain. This is an
observable effect that can be observed by the validator, albeit indirectly and
also dependent on other factors outside of XCMP receipt, and so we can
introduce heuristics based on this to probabilistically distinguish honest vs
malicious collators.

This is analogous to the mechanism in the :doc:`block submission protocol
<1-parachains>`, where we measure bandwidth used by sending collators, vs the
actual useful throughput (of validated PoV blocks) that the bandwidth is used
for. Instead of counting the (potentially spammy) bandwidth consumed by the
sending collator, we judge the receiving collator based on how quickly their
parachain's ack-watermark advances.

There are key differences to bear in mind however: in XCMP, by its very nature
the test criteria here is more indirect and cannot be determined while the
actual data transfer happens. Also the test criteria is not solely the
responsibility of the particular recipient under test, so there is less of a
competitive mechanic that incentivises honesty [#]_ - if one malicious
recipient drops the message but another honest recipient passes it on
correctly, the test will pass for both collators. Nevertheless, in the absence
of other structures to make use of, this is the most direct test we can think
of, that begins to capture the underlying characteristic of honesty.

.. [#] If the ingress queue is long, then (as mentioned earlier) messages near
  the front of the queue will be processed by the parachain first. Receiving
  collators that behave according to protocol, i.e. choose messages near the
  front of the queue that are more likely to be processed earlier by their
  parachain, are less likely to end up on a validator's blacklist. So this
  could be said to provide a weak incentive and competitive mechanism; we do
  not rely on this fact.

The rest of our protection follows a similar high-level idea as the block
submission protocol:

1. For every collator, we track which messages we send to them, as well as the
   time it takes before we observe each message to be acknowledged on the relay
   chain via watermark advancement. From this we can build up a whitelist and
   a blacklist.

   - For the purposes of the whitelist, we count the "time taken" from the time
     we send the message to *any* recipient, to avoid malicious collators e.g.
     requesting a message just before they know it will get acked on the relay
     chain to register a low "time taken" dishonestly.

     (Honest collators may sometimes get a worse "time taken" result than they
     should have got, but this is only significant if they somehow received the
     message much later than the initial malicious collator did, which would
     suggest that they were inefficient anyhow.)

   - For the purposes of the blacklist, we count the "time taken" from the time
     we send the message to that particular recipient. This avoids penalising
     honest collators who properly distributed a message quickly, even if a
     malicious collator had previously received and dropped a message.

     (Malicious collators may sometimes get a better "time taken" result than
     they should have got, however for the purposes of the blacklist this does
     not gain them any additional benefit, so this is OK.)

     If the time taken as defined above is "too large", then we will add that
     recipient to the blacklist and disconnect from them.

2. The whitelist and blacklists are maintained and used in a similar way as in
   the block submission protocol - the whitelist helps validators from new
   groups "break the tie" regarding which collators to communicate with first,
   and the blacklist helps validators avoid potentially malicious collators,
   e.g. via usage of an IP address heat map.

   As with the block submission protocol, these whitelists and blacklists are
   not intended for use outside of this protocol, e.g. to justify rewards or
   slashing elsewhere. They are merely heuristics and are not actual hard
   evidence of any good or bad behaviour.

One outstanding question is how specifically to choose "too large" for the
purposes of the blacklist. It's possible to go into quite some depth on this,
but we suspect it is best not to overthink it: more complex ways of choosing
this limit give diminishing returns in terms of protection against attacks, the
overall protection mechanism is an heuristic anyway, and these types of attacks
are currently only theoretical.

Therefore for an initial implementation we suggest a cutoff of 5 relay chain
blocks for the blacklist - in other words, if a message does not appear acked
on the relay chain after 5 relay chain blocks after a collator receives it, we
will disconnect from that collator and choose another one to accept an incoming
connection from. This is based on the fact that 2 is the best possible case,
plus a small additional grace period in case parachains want to experiment with
receiving messages slightly out-of-order for performance under parallelism.

(TODO: 5 is probably too small for parathreads.)

If necessary, in the future we can explore further refinements
on top of this, based on real-world usage & experience of attacks:

1. based on the average ack-gap across all paras
2. based on historical ack-gap for that given para
3. allow the para to securely specify what a good cut-off should be
4. allow each validator operator to specify what the cut-off should be.

or a weighted combination of these. Of course the details of (1) and (2) have
to be chosen carefully, so as to not allow an attacker to gradually affect the
value being used in their favour.

Rotation of validator groups
----------------------------

FIXME; link with other sections

A group should be active for more than the cutoff period mentioned above,
otherwise the mechanism becomes subject to abuse by malicious validators that
give incorrect whitelist/blacklist information.

(Even with a large group rotation period, abuse is still possible but its
effect is greatly reduced as validators have enough time to reach their own
conclusions.)
