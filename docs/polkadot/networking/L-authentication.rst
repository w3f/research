\====================================================================

**Owners**: :doc:`/team_members/Ximin`

\====================================================================

==============
Authentication
==============

In a public secure decentralised network, it’s important for some level of
service to be provided to unauthenticated users, e.g. for transparency and
auditing purposes. This however opens up avenues of attack for malicious agents
to attack the network.

Fortunately, this is straightforward to defend against at least conceptually -
simply constrain the amount of resources that are allocated to service
unauthenticated users. Extending this to a more general case, we can imagine
that, depending on the needs of the higher layer (e.g. application), there may
be several possible roles available for authentication, where some roles have
higher resource priorities than others.

In a computer system, the possible resource types are typically taken to be
CPU, memory and bandwidth. For now, we’ll only focus on the latter in this
document because it’s the simplest to control directly - and doing so should
also help to implicitly constrain the other two albeit with less accuracy than
a more direct mechanism.

To clarify our terminology, note that there are two things commonly referred to
as "authentication":

1. message authentication, where communication data are provably linked to some
   cryptographic identity such as the entity controlling a private key.
2. identity authentication, where cryptographic identities are linked to some
   other source of authority that distinguishes "good" identities from "bad" or
   "unknown" ones. Part of the linking may be cryptographic, but at some point
   there is a non-cryptographic component that asserts something is "good", e.g
   the genesis block, a certificate authority, or user-supplied credential.

(1) is straightforward and is done automatically by the networking layer via
the underlying transport protocol (e.g. TLS or QUIC) and requires no runtime
configuration to achieve. (2) is the harder problem especially because the set
of "good" identities can change over time, and the decision of "good" vs "bad"
is highly subjective and dependent on the surrounding system context.

(1) and (2) can be done separately from each other. Both must be done for
security - if (1) is done but not (2), then the actual identity supplied by (1)
may be false, since it may be controlled by an active MITM. Note also that,
even though the issues can be checked separately, something needs to bring the
results together and react to the case where either check fails, by ensuring
that no further resources are spent on the failed communication channel.


General
=======

.. _proposal-fresh-authentication-signals:

Proposal: fresh authentication signals
--------------------------------------

In well-layered protocol architectures, it's typical for the networking layer
to deal with (1). Since it's also the component that directly deals with
*resources*, it's also in charge of *taking action on* the results of (2) e.g.
disconnecting the peer. However to maintain suitable layer separation and
software composability and reusability, we'd like some other component to
*decide* the results of (2). Below is a proposal on doing this efficiently.

The networking layer receives some input data or signal from a higher layer,
which instructs it how to validate all the different roles of authenticated
peers. (For example, peers must present a certificate group-signed by a recent
set of validators, or belong to a fixed set of identities supplied by the
higher layer.)

This signal must include some period of validity, after which the networking
layer will deauthenticate (disconnect and ignore) any existing authenticated
peers, and reject any further attempts at authentication. In other words, the
higher layer must continually refresh the validity instructions for the
networking layer, otherwise it will eventually revert to only dealing with
unauthenticated peers with a very restricted resource policy.

One effect of this is that, if a node goes offline for a long-enough period of
time, the networking layer will expire its last authentication instructions.
This will result in disconnection of all authenticated peers; this is drastic
but is better than continuing in an authenticated state that is expired. The
higher layer should not let the situation reach this stage, but if it does, it
should run e.g. a synchronisation protocol to retrieve the latest version of
the authentication instructions, and signal this to the networking layer again.

Note that in practise with epoch-based authentication schemes, the higher layer
may want to send two staggered signals per epoch switch - first sending a
signal to include instructions for the next epoch, then waiting a grace period
for the external network to all switch to the next epoch, then a second signal
to exclude instructions for the previous epoch.

Proposal: bandwidth resource allocation
---------------------------------------

As mentioned in the introduction, the straightforward defence against malicious
unauthenticated peers is good resource allocation. Below is a concrete proposal
for such an algorithm, which should generalise to all foreseeable use-cases.

Given some demands on a single shared resource (e.g. all streams that demand
download bandwidth), how do we satisfy these in a fair and efficient way? For
example, if we simply say "each demand can only use up 1/N of the resource"
where N is the number of demands, this would perhaps be "fair" but it would
result in tremendous waste, since any part of each 1/N that goes unused cannot
be reused by another demand.

Here's one basic proposal. Suppose we have a set of demanders ``D``, each
associated with a ``guarantee[d]``. These values are interpreted relative to
each other, and lets the higher layer indicate which demanders are "more
important" by defining their guarantees relative to each other. Now for each
time-interval ``t`` we have some demands for each demander, ``demand[d]``, and
we want to decide how much resources to give to each demander, ``to_use[d]``
such that ``sum(to_use) < total_avail``.

Then the algorithm we propose below satisfies the following properties:

1. If ``sum(demand) < total_avail``, then ``to_use == demand``. In other words,
   if demand is lower than availability then demand is fully satisfied,
   regardless of guarantees. A good algorithm should not need to special case
   this explicitly, but simply degenerate to this when appropriate.

2. If ``all(demand[d] > guarantee[d] * total_avail for d in D)``, then
   ``all(to_use[d] == guarantee[d] * total_avail for d in D)``. That is, if
   every demander demands to use more than is available, then their actual use
   (relative to others) is simply their ``guarantee[d]``. This avoids
   higher-guarantee demanders starving lower-guarantee demanders.

The algorithm is as follows, described as executable Python:

.. include:: bw_alloc.py
   :code: py

If the application so wishes, it may divide ``guarantees`` conceptually into
further levels. For example if there are two classes of demanders, class A and
class B, it may wish to reserve 80% of resources for class A demanders, divided
equally amongst however many of them there are. In this case, every class A
demander ``a`` would have ``guarantee[a] = 80 / N_A`` where ``N_A`` is the
number of class A entities, and likewise every class B demander ``b`` would
have ``guarantee[b] = 20 / N_B``. Our algorithm will work fine for such an
arrangement, and need not be explicitly aware of the classes.

In a real networking program, ``demand`` may be estimated for a given interval,
as follows:

-  For sending streams: in order to deal with backpressure properly you should
   always have a priority-heap of things to send, as opposed to trying to send
   something as soon as it becomes available to send.

   -  (The priority-heap is populated as new things become available to
      send, and is popped when the recipient signals via some control-flow
      mechanism that they are unblocked for receiving again.)

-  For receiving streams: normal networking implementations have the kernel
   buffer stuff until the application is ready to process it, and any excess is
   dropped. It is normally possible to query how full the buffer is; if not
   then the application could implement its own receive buffer on top of the
   kernel's receive buffer, and measure that.

Overall resource allocation
---------------------------

Other resource concerns exist; general solutions for these are well-known, and
are also to be implemented. We mention them here for completeness:

- Connections use up memory, so the application should only keep a bounded
  number of connections open at any given time. Alongside this, applications
  should timeout inactive connections, since they prevent other connections
  that might be more active, and an attacker can otherwise exploit this. The
  application should be able to control this based on their own policy - e.g.,
  certain trusted and authenticated peers may be allowed to be inactive for a
  longer time, if their role is deemed important enough for the protocol.

- Connections are made pre-authentication, so all connections are initially
  in a pre- i.e. unauthenticated state. Policies based on giving extra resource
  guarantees to authenticated peers must account for this.

  For example, a policy that gives a guarantee of 40% of the connection pool to
  trusted and authenticated peers, does not prevent a DoS attack that makes
  lots of frivolous connections attempts, since they are all initially
  unauthenticated. These peers will still be forced to sit in the queue until
  the inactive connections timeout. However once they have a connection and
  successfully authenticate, they will benefit from the guarantee.

  On the other hand, QUIC supports 0-RTT (i.e. immediate) authentication for
  peers that have previously connected, and we plan to be adopting that in the
  mid-term future, so this will give more flexibility to these policies. The
  above scenario then would be much more well-protected.

Then there are DoS attacks at a lower level, consuming resources before they
even reach the application. For these cases, the protection must be implemented
elsewhere, e.g. at the OS level, at the hardware level, or at another network
location such as your router or ISP:

- Various types of packet flooding
- Breach of protocol, such as sending TCP traffic outside of the ack window for
  an already-opened connection

Solutions to these are also well-known, are not specific to Polkadot or
decentralised networks, and can be adopted by node operators at their choice.
Therefore they are outside of the scope of this document for now. Note that
conversely, these lower-level protections are not effective against attacks
that *do* reach the application - only the application has enough information
to distinguish bad open TCP connections from good open TCP connections.

Deciding resource policies
--------------------------

The above few sections describe the form in which various resource policies
should take, and how to enforce them. The actual policies are left for the
operator to decide. Often a human can set the values by hand, but this can be
tedious and inaccurate.

Automatically determining appropriate policies, in response to changing network
conditions, including attackers that might want to exploit this automation, is
a fine topic for future research.


As applied to Polkadot
======================



