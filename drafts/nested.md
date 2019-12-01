# Hierarchical Relay Chain Design

...


## Escalation

...

### Weakly escalating

Almost all sharding designs depend upon placing numerous nodes onto one shard, including both ETH 2.0 and OmniLedger.  

In principle, one might build a hierarchical relay chain design inspired by these approaches.  Right now, the best resource about these "weakly escalating" approaches remains:

[OmniLedger: A Secure, Scale-Out, Decentralized Ledger via Sharding](https://eprint.iacr.org/2017/406.pdf)

We shall focus primarily upon strongly escalating approaches in this document because naively any approached like this breaks our 2/3rd honest assumption.

### Escalating availability

We consider nested relay chains with their own grandpa finality gadget that acts like the collator for the overall relay chain.  In duch designs, availability escalation amounts to aigning the availability routing with the nesting:

Assume we have $n$ validators throughout polkadot with $m$ being assigned to each nested relay chain.  

A parachain on each nested relay chain should erasure code their PoV blocks into $n$ pieces, one for each polkadot validator, such that reconstruction remains possible with any $\lfloor n/3 \rfloor$ pieces.  Now the parachain vaidators send a disjoint set of $n/m$ pieces to each of the $m$ validtors assigned to its nested relay chain.  

At the nested relay chain level, we run some grandpa-like finality gadget in which voting requires possesion of these larger nested pieced consisting of escalated $n/m$ pieces.  We may do so because any $m/3$ of these nested pieces suffices for reconstruction.  

TODO:  How much simpler should our nested finality gadget be?  What properties do we actually want at this layer?

After our nested relay chain reaches finality, it submits its finalized blocks for inclusion in the overall relay chain.  

We now impose grid network topology upon the validators with rows corresponding to nested relay chains and columns being cliques across nested relay chains.  In other words, we name vaidators $(i,j)$ by their nested relay chain number $i$ and their sequential index $j$ on that nested relay chain.  All these cliques across nested relay chains permit efficent exchange of the escalated $n$ pieces.  

An an example, if we have three nestged relay chains, then $(1,j)$, $(2,j)$, and $(3,j)$ all exchange their pieces.  We also identify the original escalated pieces by $(i,j)$ where $i$ is a nested relay chain index, so that node $(i,j)$ recieves pieces $(1,j)$, $(2,j)$, and $(3,j)$ from its nested relay chain, and then swaps within the rows.

TODO: Formulate the networking topology better.  And comment on alowable topologies.  SlimFly?

As expected, these nested relay validators require the full $n/m$ pieces from a parachain block $B$ before voting in grandpa for any nested relay chain block containing $B$. 

### Escalating validity

We think some validity checks should come from outside the nested relay chain validators, but maybe different VRF conditions makes sense for different layer.  If so, we might require some some secondary checks from the nested relay chain before considering for polkadot.

TODO: Which VRF conditions in which layer?

Any secondary checks coming from outside the the nested relay chain might encounter more trouble reconstructing that a nested relay chain's own validators.  We suggest it first request the block from the parachain validators, then attempt a reconstruction with the groups of $n/m$ nested pieces, and finally attempt a reconstruction with the full set of $n$ escalated pieces.  


## Hierarchical vs DAG

We should investigate if DAGs present any good alternatives to a hierarchical design, likely after exploring the block DAG literature.  

In a DAG design, we have multiple relay chain blocks that form a hash DAG instead of a hash chain, but then depend upon the block validity rule to prevent conflicts.  A priori, We expect DAGs benefit from first moving all DOT transfer, staking, and voting functionality only privlidged parachains, so that the relay chain becoems as simple as possible.

If DAGs could be dynamic enough, then concievably parachains might only send ICMP messages when they land in the same DAG block, which simplifies but slows ICMP.  At first bliush however, our network topology requirements for escalating availability make DAG designs relateively statics however, which obstructs this.


## Bridge-like

At some point, any design that does not escalate availability or validity acts like a substrate-substrate bridge:

https://github.com/paritytech/substrate/pull/3703
https://github.com/paritytech/substrate/issues/1850

We previously noticed that caping transaction value gives some provable garentees for substrate-substrate bridges, but not all interchain messages have meaningful transaction values, and this does not play well with ZK schemes.


## Multi-Relay

Are there any sensible ways for chains to become parachains of multipl relay chains?  

I suppose this works if they provide their own finality and then simply buy "extra confidence" in their own finality from these relay chains.

We have no idea if ICMP makes sense under such a setup however.


