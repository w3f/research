
# Network randomness schemes

These are our reviews of collaborative random number generators (RNGs)
or other networked randomness schemes

## Collaborative PRNGs

There are several true collaborative PRNG schemes in which all participants obtain the same output and can then run arbitrary randomised algorithms with identical seeds and results.  As a result, we can employ more randomised algorithms that produce exact outputs like permutations of nodes, or require more complexity or tweaking.  

### Verifiable Delay Functions (VDFs)

VDFs employ a slow non-parallelizable computation and provide a PRNG with a proof that some time period elapsed between when seeds were available and when the output was available.  Right now, the best ideas for this want a group of unknown order, like maybe the class group of an imaginary quadratic number field.
https://crypto.stanford.edu/~dabo/pubs/papers/VDFsurvey.pdf

Justin Drake with Etherium research is very interested in VDFs because VDFs provide a collaborative PRNG in which one honest party suffices to produce a secure random number.  We currently fear that VDFs deployment strategies have an excessively small security margin.  An attacker might for example compute the VDF 10x faster to gains the random number early or even bias it.  ASICS might be achieve this.  At the extreme, [superconducting computing](https://en.wikipedia.org/wiki/Superconducting_computing) can achieve speeds of 100 GHz with circuits consisting of 10^5 Josephson junctions.  You’d need a rather large time window to use a VDFs, and you’d need an even larger time window to handle the highly optimised VDF node equivocating.

### DFinity style VSS + VRF

We might not fully understand the VRF's roll here because the public
key correctness ultimately depends on the VSS based DKG and this
depends upon validator nodes raising accusations.  We believe they
do this so that one DKG yields numerous VRF outputs, maybe because
the DKG is considerably more expensive, or not amenable to some
optimisations.  

Almost all the pure cryptography implementation work consists of
following the DKG design in
_Secure Distributed Key Generation for Discrete-Log Based Cryptosystems_
by Rosario Gennaro, Stanisl􏱑aw Jarecki, Hugo Krawczyk, and Tal Rabin.

There is no actual production of a BLS signature produced there
however, so one should also look over section 7 of 
_DFINITY Technology Overview Series Consensus System_ (Rev. 1)
by Timo Hanke, Mahnush Movahedi and Dominic Williams.

### Schoenmakers PVSS ala EPFL 

"A publicly verifiable secret sharing (PVSS) scheme is a verifiable
secret sharing scheme with the property that the validity of the
shares distributed by the dealer can be verified by any party; hence
verification is not limited to the respective participants receiving
the shares."

An implementation would follow 
_A Simple Publicly Verifiable Secret Sharing Scheme and its Application to Electronic Voting_
by Berry Schoenmakers,  
as well as the DEDIS group at EPFL's Kyber suite written in Go:
https://github.com/dedis/kyber/tree/master/share

As written, the resulting secret is a random curve point, not a BLS
signature or private scalar.  In comparison, DFinity's VSS + VRF
scheme produces a BLS signature, or even shared private scalar.
If the message is known in advance, then PVSS could seemingly
produce a BLS signature, although I need to think more about the
timing of protocol messages in doing so.  If correct, this might
answer an important open question of DFinity's Timo Hanke, but
maybe not the answer he wants, as PVSS probably need to be run for
every signature produced, and DFinity's solution runs the DFG 
infrequently.

Schoenmakers' PVSS avoids pairings but incorporates two rounds of
DLEQ proofs.  These are complex operations, but might prove faster
than DFinity's VSS + VRF scheme, due to pairing based curve. 
Also, ee need to verify that a type III pairing does not make the
protocol insecure and worry if components like the DLEQ proofs need
to change for my proposed PVSS + VCF variant.  We must also consider
if any attacks can influence the public key.


## Specific random results

There are various schemes that produce specific random results
without actually producing a shared random value, but the result
are necessarily inexact and may need to be simpler or complicate
the consensus process.

These are mostly applications of verifiable random functions (VRFs),
which normally consist of applying a random oracle to the output of
a deterministic signature scheme applied to a shared value. 

### Competitive VRFs

It's hard to apply VRFs competitively because attackers may delay
revealing their results, pretend not to see other's results, use
network flood attacks on winners, etc., so roughly the same problems
as simple commit and reveal.

### Ouroboros style "slot filling" VRFs

We avoid the competitive VRFs issues by using VRFs to fill slots
far more numerous than actual winning positions, say slots for block
production.  There remain related issues with timing and when block
producers may skip earlier ones, which require more thought, and may
impact other things.

Security proofs exist, but tricky UC ones.

See Ouroboros paper #2 
TODO: link

### Alistair's VRF leveraging random block selection 

If we have a network randomness scheme picking block producers or
many another specific random results, then they could include a VRF
of the block number.  As above, each node's only options are to
produce a block or not produce a block, so whatever alternatives
nodes they have who could produce a block give them influence over
the random number, but another user might produce a block first
scooping them.  

Although not a collaborative PRNG per se, this produces random
numbers we might argue can be used like collaboratively produced
ones.  Alistair says we cannot wait for finalisation here, but
disagreement results from multiple chains running in parallel.

### Algorand

Algorand has similarities to Tindermint, but selects validators
randomly from a pool, instead of using a fixed set, and does a
Byzantine agreement for each block.  All nodes produce possible
blocks and a VRFs helps choose among them.

### RANDAO

Nodes commit to a hash onion and use the layers like a local VRF,
revealing one layer whenever doing so allows them to produce a block.
RANDAO is less outright computation than local VRFs for verifiers.
Also VRFs on different seeds do not aggregate well.  RANDAO requires
verifiers verify update records for all other verifiers though,
which sounds more fragile than a VRF, meaning more sensitive code.
RANDAO producers may take a performance hit from storing intermediate
hashes, but if so Merkle trees give another similar option.

We think orphan blocks prevents us from slashing nodes for skipping
their turn, so either all nodes must have a RANDAO contribution for
each slot, or else nodes can increases their control over their
revealed values by skipping blocks.

https://ethresear.ch/t/rng-exploitability-analysis-assuming-pure-randao-based-main-chain/1825/4
https://ethresear.ch/t/randao-beacon-exploitability-analysis-round-2/1980
https://ethresear.ch/t/making-the-randao-less-influenceable-using-a-random-1-bit-clock/2566


# Network randomness uses

## Validator group assignments

We think local VRFs, either competitive or slot filling, do not
produce an even enough distribution and do not permit us to
allocate stake well across validators.  So we want a real
collaborative PRNGs here.

Relevant questions:
- Can we produce a security proof for Alistair's VRF leveraging?
- How does Ouroboros handle similar situations?
- Is PVSS + VRF better?

## Finality gadget leader assignments

Alistair thinks rotation solves everything currently.  
An alternative is Algorand's local VRF.

## Block production leader assignments

Etherium and Ouroboros handle this with RANDAO and their "slot
filling" VRF, respectively.  We think Ouroboros's VRF has
significant implementation advantages, but we may reevaluate
after we take performance more into consideration.

## Fishermen incentivization 

We envision creating a small about of random missbehavior so that
fishermen always have some missbehavior to catch.  We should do this
with local VRFs so that nobody except the missbehaving node knows in
advance, but the levels should be low enough that such missbehavior
cannot accumulate.

Are there other fishermen related uses?  Rob mentioned ordering 
fishermen, which sounds problematic.


# Timing

TODO: Comment on relative block time vs. more absolute synced clock times.
  ability to have timeout that depend on network activity?  (relative absolute time??)
  but think about the network conditions

We seemingly need a bound on clock skew between validators, which
we must enforce using the peer-to-peer network.

### RANDAO

We noticed possible timing issues with RANDAO that impact most other
schemes:  An attacker can manipulate the timing of their blocks to
help maintain a forked chain.  TODO: Add details.

### Ouroboros rate metering

Ouroboros paper 3 describes minimum rate requirement for protection
against long term attacks.  The idea goes that a long-term attacker
starts with relatively little stake, so initially they produce blocks
slower than the overall network, but as their stake increases this
rate goes up.  Ouroboros wants to prevent this initial slow start,
but this requires 



### Ideas

Unavailability game
Time or relative time signing

