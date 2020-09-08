\====================================================================

**Authors**: Ximin Luo, Rob Habermeier, Fatemeh Shirazi

**Last updated**: 2020-06-04

\====================================================================

====
XCMP
====

This subprotocol runs whenever the relay chain block production protocol has output a new candidate block, similar to the A&V protocol.

This candidate block references a bunch of parachain blocks, that might indicate that those parachains wish to send messages to other parachains. To save bandwidth, and since no other parachains need to receive the data, the message bodies are not contained within these blocks, and must be transferred separately. The purpose of this subprotocol is to do that.

Background
==========

XCMP high-level overview
------------------------

To recap, :doc:`XCMP <../XCMP/index>` is designed to achieve ordered, reliable, and fair delivery, under the constraint of trying to minimise the data stored on the relay chain.

Terminology note: all the messages for a given (sender, block) are processed in a single batch by the recipient, so to simplify discussion without losing generality, from here on we will refer to "the" (logical) message at a given (sender, block) even though in practise this consists of multiple smaller physical messages.

(Sender, recipient) parachains that wish to communicate, register with the relay chain to open a channel. This channel comprises a bounded queue of ordered messages that have been sent but not yet acknowledged by the recipient.

The queue is maintained by the sending parachain; it tells the relay chain what the current head of the queue is, by including it in their next submission to the relay chain. Thus the relay chain only stores the current heads of the channels. [1]_ Every message is associated with a merkle co-path that proves it belongs to the channel, as defined by the head in the relay chain block. When the recipient acts on the message, they acknowledge this to the relay chain, by including the merkle co-path in their next submission to the relay chain.

.. [1] In practise this is compressed even further across multiple channels for the same sender - we omit the details here as they are not relevant to XCMP networking; the overall "shape" is similar to the oversimplified version just described.

**The main task of XCMP networking** therefore, is to distribute these messages and copaths from the senders to the recipients.

The recipient parachain collators must monitor the state of the relay chain, in order to know if it has new incoming messages, and what messages are currently in the queue (relative to a given relay chain block head). Similarly, the sending parachain collators may monitor the state of the relay chain, in order to know if its outgoing messages have been acknowledged, and what messages remain in the queue. These are also done outside of the scope of XCMP networking; however the XCMP networking relies on the former at least to be done correctly.

The relay chain & parachain validators together verify that the channel grows & is consumed, in a consistent & reliable way; this is done outside of the scope of XCMP networking. Specifically, messages must be acknowledged in the correct order for a given channel. Additionally, a recipient parachain must acknowledge at least one new message from a block, if it has any new messages (from different senders) in that block. To ensure fairness, the order in which messages from different senders are acknowledged, is pre-determined and out of the control of the recipient parachain.

Expected usage
--------------

Every sending parachain may send up to ~1 MB per chain height in total, to all parachains. In the most unbalanced case, this will be to a single recipient parachain.

TODO: in the worst case, (C-1) parachains will each send ~1 MB to the same victim receiver parachain. We could attempt to limit this.

TODO: chains can only communicate when they've opened a channel to each other, the state of which is stored on-chain. We can potentially use this information to derive more efficient topologies for XCMP.

Fairness
--------

A small digression: fairness means that receivers must process received messages fairly across all senders, and is mostly to ensure that no message will be left unprocessed for an infinite delay - the sender knows that the receiver must least ack its contents eventually, though they can drop the message after that. This is a value judgement made at the point-of-design of XCMP; we'll monitor its performance in practise.

Although different from the internet's recipient-controlled processing, fairness does not introduce much overhead since for global ordering and reliability, message-passing is co-ordinated via the relay chain anyways, and enforcing fairness on top of this is straightforward.


Requirements
============

R1. At least one message from every (non-empty) ingress queue must be transferred to the corresponding recipient, so that they may perform their obligation to ack at least one message.

R2. Ideally, allow recipients to select which message(s) to receive first, subject to the fairness constraints mentioned above.


Comparison with A&V
===================

Similarities
------------

Data flow pattern, i.e. outboxes to inboxes

Differences
-----------

Data usage profile

Less overall traffic, but much greater variability

Latency not such a big deal, can be similar to A&V, but in practise should complete quicker due to less overall traffic.

More notes in https://hackmd.io/9JvbSmiNTiGUqEjQiPWtKQ?both


Evaluation of options
=====================

We have four obvious parties in the situation, two of which are essential to the existential goal:

[sending collators] --- [sending validators] --- [recipient validators] -- [recipient collators]

Therefore we have 4 primary options to look at, based on whether we omit or include the {sending, recipient} validators in the data flow.

First, we note that parathreads do not have an associated validator group until after they have produced a block. So there are no "recipient validators" in this scenario, unless we modify the higher-level Polkadot protocol to associate recipient parathreads with a validator group.
