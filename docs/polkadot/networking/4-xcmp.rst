\====================================================================

**Owners**: :doc:`/research_team_members/Ximin`

**Other authors**: Rob Habermeier, Fatemeh Shirazi

\====================================================================

=====================
Cross-chain messaging
=====================

This subprotocol runs whenever the relay chain block production protocol has output a new candidate block, similar to the A&V protocol.

This candidate block references a bunch of parachain blocks, that might indicate that those parachains wish to send messages to other parachains. To save bandwidth, and since no other parachains need to receive the data, the message bodies are not contained within these blocks, and must be transferred separately. The purpose of this subprotocol is to do that.


Background
==========

TODO: much the section below should be moved to the main XCMP document.

XCMP high-level overview
------------------------

To recap, :doc:`XCMP <../XCMP/index>` is designed to achieve ordered, reliable, and fair delivery, under the constraint of trying to minimise the data stored on the relay chain.

Terminology note: all the messages for a given (sender, block) are processed in a single batch by the recipient, so to simplify discussion without losing generality, from here on we will refer to "the" (logical) message at a given (sender, block) even though in practise this consists of multiple smaller physical messages.

(Sender, recipient) parachains that wish to communicate, register with the relay chain to open a channel. This channel comprises a bounded queue of ordered messages that have been sent but not yet acknowledged by the recipient.

The queue is maintained by the sending parachain; it tells the relay chain what the current head of the queue is, by including it in their next submission to the relay chain. Thus the relay chain only stores the current heads of the channels. [1]_ Every message is associated with a merkle co-path that proves it belongs to the channel, as defined by the head in the relay chain block. When the recipient acts on the message, they acknowledge this to the relay chain, by including the merkle co-path in their next submission to the relay chain.

.. [1] In practise this is compressed even further across multiple channels for the same sender - we omit the details here as they are not relevant to XCMP networking; the overall "shape" is similar to the oversimplified version just described.

**The main task of XCMP networking** therefore, is to distribute these messages and copaths from the senders to the recipients.

The recipient parachain collators must monitor the state of the relay chain, in order to know if it has new incoming messages, and what messages are currently in the queue (relative to a given relay chain block head). Similarly, the sending parachain collators may monitor the state of the relay chain, in order to know if its outgoing messages have been acknowledged, and what messages remain in the queue. These are also done outside of the scope of XCMP networking; however the XCMP networking relies on the former at least to be done correctly.

The relay chain & parachain validators together verify that the channel grows & is consumed, in a consistent & reliable way; this is done outside of the scope of XCMP networking. Specifically, messages must be acknowledged in the correct order for a given channel. Additionally, a recipient parachain must acknowledge at least one new message from a block, if it has any new messages (from different senders/channels) in that block. To ensure **fairness**, the order in which messages from different senders/channels must be acknowledged, is pre-determined and out of the control of the recipient parachain. In other words, multiple incoming channels for a given recipient are multiplexed into a single ingress queue, and the recipient must process this queue in the aforementioned pre-determined order.

Expected usage profile
----------------------

Every sending parachain may send up to ~1 MB per chain height in total, to all parachains. In the most unbalanced case, this will be all to a single recipient parachain.

Across all chains then, the worst case is that (C-1) parachains will each send ~1 MB to the same receiver parachain in a single block; however this need not be all distributed during the time slot for that block - see fairness below.

Fairness
--------

Fairness means that receivers must process received messages fairly across all senders, and we chose this mostly to ensure that no message will be left unprocessed for an infinite delay - the sender knows that the receiver must least ack its contents eventually, though they can drop the message after that. This is a value judgement made at the point-of-design of XCMP; we'll monitor its performance in practise.

Although different from the internet's recipient-controlled processing, fairness does not introduce much overhead since for global ordering and reliability, message-passing is co-ordinated via the relay chain anyways, and enforcing fairness on top of this is straightforward.

If recipient parachains feel that they are being spammed by certain sending parachains, they may selectively close these channels.


Requirements
============

R1. At least one message from every (non-empty) ingress queue must be transferred to the corresponding recipient parachain, so that they may perform their obligation to ack at least one message.

R1a. We must distribute it to *enough* collators of the recipient parachain so
that the parachain cannot be attacked by malicious collators. TODO: currently
"enough" is not well-defined, as Polkadot does not assume any structure in a
parachain in order to begin defining this.

R2. Ideally, allow recipients to select which message(s) to receive first, subject to the fairness constraints mentioned above.

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


Evaluation of options
=====================

We have four obvious parties in the situation, two of which are essential to
the existential goal:

[sending collators] --- [sending validators] --- [recipient validators] -- [recipient collators]

Therefore we have 4 primary options to look at, based on whether we omit or
include the {sending, recipient} validators in the data flow.

Security considerations
-----------------------

Independently of any particular design choices for XCMP networking, we have the
following security concerns.

Recall that Polkadot (at the time of writing) does not assume that parachains
have any permission system that can distinguish *at the point of initial
communication* whether a collator is honest or malicious, or indeed if it even
"actually belongs to" the parachain in any sense of that word.

Potential attacks in this scenario include:

- Malicious recipient collators receiving messages (either via push or pull),
  then throwing them away. There is a sliding scale as to the severity of these
  - the attacker may be able to selectively block specific messages with high
  probability (a.k.a. a censorship attack), or they may only be able to reduce
  the effective throughput of overall incoming messages to a parachain (a.k.a
  a bandwidth-wasting attack).

  Whoever we choose to be the point-of-contact of the recipient collators, will
  be responsible for defending against these types of attacks.

- Malicious sending or recipient validators receiving messages, then throwing
  them away - similar to the above point. This is similar to our availability
  concern in :doc:`3-avail-valid` - if we designate either sending or recipient
  validators to forward messages on behalf of a sending parachain, they must
  store the messages until the recipient parachain has acknowledged them. If a
  validator group is all-malicious then we need a fallback retrieval mechanism
  for this; unlike in :doc:`1-parachains` it is not sufficient to just wait
  until our assigned group rotates into one that is hopefully good.

XCMP networking is *not* concerned with the following:

- Malicious collators sending or validators forwarding invalid messages - since
  recipient collators :doc:`can verify these <../XCMP/index>` against the relay
  chain state.

  Performing this verification requires waiting for the sent messages to appear
  on the relay chain, which takes time. It would save time, if these two
  processes happen in parallel:

  1. XCMP networking distributes message bodies from sending to recipient parachain
  2. XCMP authentication includes sent messages onto the relay chain

  However (1) is initially unable to use security information from (2), and so
  we'll need to figure out how to buffer unverifiable message bodies in a
  secure way, as we wait for the relevant security information to arrive. A
  future iteration of XCMP networking may attempt to cover this.

Other considerations
--------------------

Sending validators already have the message bodies, since they are included in
the PoV block and distributed as part of the :doc:`A&V distribution process
<3-avail-valid>`. So making using of them is "free" from the perspective of
XCMP networking.

Parathreads do not have an associated validator group until after they have
produced a block. So there are no "recipient validators" in this scenario -
that is unless we modify the higher-level Polkadot protocol to associate
recipient parathreads with a validator group.

Whether we choose push vs pull primarily affects which parties must be publicly
reachable - if push then the recipients must be reachable, if pull then it is
the sender (responding to the pull request) that must be reachable.

- Pull can also make it easier to protect against certain types of spam
  attacks, but these are not relevant in the initial iteration of XCMP
  networking, since we opted to send message bodies only after they are added
  to the relay chain, which provides an anti-spam mechanism already.

Though Polkadot does not assume any networking structure for parachains, in the
:doc:`parachain block submission <1-parachains>` protocol we are able to
distinguish honest vs malicious sending collators by (1) checking that they
actually send us valid blocks and (2) measuring the throughput of valid blocks
being sent by different collators. However with XCMP networking, it is much
harder to distinguish honest vs malicious recipient collators, since there is
no simple way to know whether they have passed on the message body to the rest
of the parachain (honest) or if they have dropped the message (malicious). We
explore this in more detail below, including giving various concrete high-level
proposals for addressing this, with different tradeoffs.


Comparison with A&V
-------------------

Similarities:

- Data flow pattern (qualitative), i.e. outboxes to inboxes

Differences:

- Data usage profile (quantitative) - Less overall traffic, but much greater variability
- Latency not such a big deal, can be similar to A&V, but in practise should complete quicker due to less overall traffic.

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
$K$ $T/C$ - assuming every receiving validator group "works for" 1 recipient parachain and K recipient parathreads
$R$ collator redundancy factor. Note that the validator redundancy factor is already built into the structure of $V$.
$O$ number of outgoing paras for the given sending para
$I$ number of incoming paras for the given recipient para
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


Proposal: XCMP networking, initial iteration
============================================

FIXME. expand; also describe transition to this, from sending-validators-only.
describe its complexity costs regarding validator-collator connections.

FIXME: validators (and the sending parachain) should store each message until
it's been acked, but what if the receiving parachain never does this? Then
presumably the sending parachain needs to store it, and expose an interface for
the receiving parachain to retrieve it later, but we haven't specified this
anywhere as part of XCMP yet.

Introduce the idea of recipient validator group, even for parathreads.

Sending collators send message bodies to their sending validator group, as part
of the :doc:`parachain block submission <1-parachains>` and :doc:`A&V
<3-avail-valid>` subprotocols.

Sending validator groups send message bodies to the relevant recipient
validator groups, using a mixture of push and pull.

Recipient collators pull message bodies from their recipient validator group.
As an optimisation, recipient validators may push to any recipient collators
that they are already connected to.

Since ingress queues may be long, recipient collators should request messages
from (near) the front of the queue to ensure that their parachain can process
the messages in the correct order in a timely fashion. Validators may enforce
this at their discretion by refusing to transfer messages too far forward in
the queue; we leave the details of this open for now - but we note that the
mechanism described in the next section ought to discourage this without any
explicit enforcement at this level.

TODO: chains can only communicate when they've opened a channel to each other,
the state of which is stored on-chain. We can potentially use this information
to derive more efficient topologies for XCMP.

Distinguishing honest vs malicious recipient collators
------------------------------------------------------

As mentioned earlier, the lack of structure we assume about parachains, gives
us fewer options to determine if a recipient collator is "honest" vs
"malicious". Despite this we do still have some information we can make use of
for this purpose, that is related to the fundamental high-level requirement of
this part of XCMP. Recall that the purpose of having collators receive
messages, is for their parachain to act on them, and acknowledge this to the
Polkadot relay chain. This is an observable effect that can be observed by the
validator, albeit indirectly and also dependent on other factors outside of
XCMP receipt, and so we can introduce heuristics based on this to
probabilistically distinguish honest vs malicious collators.

This is analogous to the mechanism in the block submission protocol, where we
measure bandwidth used by sending collators, vs the actual useful throughput
(of validated PoV blocks) that the bandwidth is used for. Instead of counting
the (potentially spammy) bandwidth consumed by the sending collator, we judge
the receiving collator based on how quickly their parachain's ack-watermark
advances.

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

FIXME: this is fiddly to implement. discuss real-world attacks and the
possibility of omitting this protection. however future development should not
conflict with the possibility of adding it later, in response to real-world
attacks.

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
