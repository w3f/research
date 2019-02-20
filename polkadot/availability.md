# Availability

## Motivation

In Polkadot parachain collators are responsible for creating parachain blocks and sending them to parachain validators. These parachain validators must validate the block and submit summaries (called headers) to all validators of the relay chain. One of these validators is going to add this parachain header in form of a relay chain block to the relay chain. Parachain fishermen verify the validation process carried out by the parachain validators. 

**Definition**: Let us define a parachain blob as a tuple containing a light client proof of validity (PoV) for a parachain block, the parachain block itself, and the outgoing messages from that parachain. 

Note that we are not trusting the parachain collators or validators necessarily, but instead we rely on a number of light clients called fishermen. Fishermen are responsibile to check the validation process carried out by parachain validators. However, fishermen do not have access to all the parachain blobs since they are not full nodes of the parachain necessarily. Hence, if parachain blobs are not available fishermen would not be able to detect faulty proofs and raise any concern.

Hence, if dishonest parachain validators collude with collators and create parachain headers for non-existing blobs, other relay chain blocks might be built upon non-existing parachain blobs.

Therefore, once a block is created it is important that the parachain blob is available for a while. The naive solution for this would be broadcasting/gossip the parachain blobs to all, which is not a feasible option because the parachain blobs are big. We want to find an efficient solution to ensure parachain blobs from any recently created parachain block are available. 

## Availability via Erasure Coding

Let us assume we have $n=3f+1$ validators and at least $n-f$ of those are honest and online.

## Availability Protocol

1. A collator sends a parachain block, its outgoing messages and  a light-client proof of correctness of these to parachain validators (a parachain blob) to the parachain validators
2. Once the parachain validators have validated it, they create an erasure coded version with an optimal $(n,k)$ block code of this blob, where $k=f+1$.
They also calculate a Merkle tree for this erasure coded version and add the Merkle root to the things they sign about the block for inclusion on the relay chain. 
3.  The parachain validators send out these pieces along with a Merkle proof to all validators
4.  The parachain block header gets included on the relay chain
5. If a validator has not received an erasure coded piece for every parachain blob that has a header in a relay chain block it request it. The piece they should ask for is different for each validator. Along with the piece, the parachain validator needs to provide the Merkle proof that it comes from the Merkle root on the relay chain.
6. Validators only prevote in Grandpa for a (descendant of a) relay chain block if they have all these erasure coded pieces. They only build on blocks if they have just seen it very recently (e.g., last block) or they have all the pieces. We do not want to build on a block that has an unavailable ancestor block. 
7. The request for missing erasure coded pieces is first sent to the rest of the parachain validators and then the other full nodes of the parachain. If full nodes of the parachain don't have the parachain block available, a randomly selected validator (called assigned validator) asks all validators for their erasure coded piece of the block. When he receives $k=f+1$ pieces, the assigned validator attempts to reconstruct it.
8. If a parachain fisherman publishes a proof that the block is invalid or if an intermediate validator or the validator holding the erasure coded piece refuse to hand over the piece we slash them. Moreover, if the assigned validator publishes that $f+1$ pieces cannot be decoded into a blob, then we slash the parachain validators and declare that relay chain block invalid.
9. To agree on non-availability we carry out an attestation game described below. We require any one of the  validators to start the attestion game by claiming that their erasure coded piece of the blob is unavailable. Now the other validators need only ask for the pieces that are claimed to be unavailable, rather than the whole blob. The initiator of the attestion game should already have asked full nodes of the parachain if the parachain validators disappeared for their piece.

The idea here is that we do not finalise a block until sometime after $f+1$ honest validators prevote for it. But if that's the case, then 6 should succeed, which means that we only finalise available blocks. If 7 happens fast enough, then we only finalise valid and available blocks. As before, we'll need to plan for when we finalise an invalid block.

The Merkle root commitment means that all parachain validators who signed off on the blob must provide the same erasure coded version. It also means that the erasure code only needs to deal with missing, rather than corrupted pieces, even if one of the guys is Byzantine, because any piece with a valid Merkle proof is the one that all the guys committed to. Now we know that if we see f+1 pieces with proof that they came from the same Merkle root in the block header, that if they don't assemble to something then all the parachain validators who signed the block header did so knowing that it didn't contain the Merkle root of a valid erasure code. So if we cannot reconstruct the blob from $f+1$ pieces, we can slash everyone who signed off on the Merkle root.


Note: We are not going to do the 2D Reed-Solomon approach from https://arxiv.org/abs/1809.09044. If we did, it would give us smaller proofs of non-decodability. This is only worth it if proofs of invalidity of parachain blocks are likely to be smaller than the blocks themselves. So we will stick to 1D codes here. Since we know exactly how many validators we have, we can do a deterministic scheme.

## Attestation Game: Agreeing on non-availability

How do we agree that a piece of the erasure code of a parachain blob is not available? 

We can have some sort of a petition (set of attestations) that can be triggered by any one of the validators for an erasure coded piece of a parachain blob when its header is on the relay chain and when they cannot retrieve the piece otherwise. This petition is broadcasted or sent around to all validators who confirm that the piece is not available and sign the petition. Once the petition is confirmed/signed by $\frac{2}{3}$ of the validators the collators of that parachain and the parachain validators are going to be slashed. 

We only need the attestation game for liveness, and we might not even need it then, so it doesn't have to be fast. The issue is that if $f$ honest validators have a piece then that is not enough to reconstruct the blob, but as far as they know, they can still vote for it. If there are any Byzantine or offline validators, then this might stop us getting the $n-f$ votes needed to finalise something else. In this case we might get two forks, one including the blob and one without it. If the one including the blob is longer, we need the attestation game for everyone to agree that it is invalid.

In the case when $f+1$ validators are Byzantine and claim an unavailable blob is available, they can finalise it with the help of $f$ validators, who have the only $f$ pieces, and we have no way of uniquely attributing this fault. But this is also a problem for other schemes. (ask AL about it!)

The data stored by each validator is actually smaller to the previous scheme we considered. If there are $m$ parachains with parachain blocks of size $s$ bytes, then each validator stores $s/k$ bytes for each parachain and so $ms/k < 3ms/n$ bytes total for this availability. The previous scheme called for like 10 additional validators per parachain to guarantee availabilty, which would result in $10ms/n$ extra bytes for availabilty per validator.


### How are missing parachain blob (pieces) retrieved?

If a validators in not receiving an erasure coded piece of a parachain blob from a certain parachain validator after he has seen the header in the relay chain, it can request the missing piece from the remainder parachain validators. If those validators are also AWOL, then she can request ot from full nodes of the parachain. 


How do full nodes of the parachains (including collators) talk to all validators when the parachain validators, who should be the guys on both networks, are AWOL? 

We don't want people to be able to flood the network by asking for stuff (parachain blobs?). We could ask only one validator to collect all the pieces of a blob, assemble the blob, and forward it to the parachain light clients. The AWOLing validators would only be AWOL a parachain blob if they can go undetected, otherwise they will be slashed. Therefore, it should not be known to anyone who is going to be asked by parachain light clients in advance. Otherwise the adversary can corrupt/DoS that validator. We should ask a validator at random. We need to use a randomness that cannot be significantly biased by an adversary, e.g., randomness used to choose the validator that adds the next relay chain block. 

There is a low probability that the parachain validators, who are AWOLing the light nodes of the parachain, do know in advance whether they are going to be selected as an assigned validator who reconstructs the missing parachain blob. Moreover, they do not know if there is not any other validator who has the same output for their VRF, and that their AWOLing would go undetected. We could even XOR some randomnes of the VRFs of the last blocks for this? To make the it very difficult for adversary to bias the randomness.

## Backing up

Note that an honest parachain validator can back up the pieces, before she sends them out to validators, at a (random or preferably trusted) full node of the parachain before sending them out to the validators. If the parachain validator is AWOL that parachain full node can distribute that piece to all full nodes of the parachain who can respond to requests from validators that are requesting missing erasure coded pieces. 

## Current implementation in Polkodot PoC-4

Polkadot is currently using Reed-Solomon encoding of $(n, f+1)$ over Finite Field of $2^{16}$ elements where $n$ is the number of relay chain validators and $f=\lfloor\frac{n-1}{3}\rfloor$ to implement the availability scheme. Every parachain block is encoded by SCALE codec and is possibly padded to make sure that the encoded data is of even length. The block then is seen as a sequence of two-byte chunks each representing an element of $GF(2^{16})$. The sequence is broken into $f+1$-length subsequences where the final subsequence is also padded by 0 to make it of consistent length with the other subsequences. Each subsequence is treated as a message word and is encoded using Reed-Solomon $(n,f+1)$ encoding into an n-tuple codeword vector whose elements are distributed between the validators. In this way, each subset of $f+1$ validators can reconstruct all of the $f+1$ subsequences and hence reconstruct the original parachain block.

## Notes from the ICMP workshop

Let us assume an availability guarantor is a validator that has received an erasure coded piece according to the availabilty scheme. 

We use [n, f+1] erasure coding where n=3f+1 and is the number of pieces and corresponding AGs. We can tolerate slightly under a third of validators being malicious. Each AG will store 1/(f+1) erasure coded pieces of each blob.

AG (validators that hold a erasured coded piece) are also GRANDPA validators.

Terminology:
AG: Availability guarantor
PV: Parachain validator
BA: Block author
PoV: Proof of Validity (a block candidate plus all witness data in order to let a stateless (light) client execute it)
RC: Relay chain

1. Parachain validators or collator do the deterministic coding of the data (PoV ++ Outgoing Messages) and combine into a merkle tree, whose root is committed to in the PoV candidate and block
2. BA authors a block with various attested-to candidates (see above steps)
3. Each AG asks for their piece of the erasure coding from the PVs or the collator. In practice, the PVs may send them out pre-emptively.
4. AGs, when acting as GRANDPA voters, do not vote for a block unless they have ensured availability of their piece. This guarantees that we never finalize anything which is unavailable.
5. BAs, when authoring, should not build on chains where they do not have their piece of data available in each unfinalized block (perhaps excepting recent blocks).
     * If BAs are unpredictable then this should help ensure that the longest chain tends to have available data.
     * If BAs are not AGs they should be requesting random pieces of the coding.

The difficulty lies in step 3; distributing the correct pieces to all correct AGs will be difficult and will require targeted messaging infrastructure.

Fishermen requesting f+1 pieces in order to check the constructed data is valid will be similarly difficult.

We may still need the attestation game for liveness.

This scheme is inspired by the less GRANDPA specific Fraud Proofs paper.

Unlike the fraud proofs paper, we don’t currently make use of a 2-dimensional coding. The 2-dimensional coding gives small fraud proof transactions from a small fraction of the shares, while our variant requires reconstructing the whole data. It’s impossible to verify the block’s correctness without reconstruction though anyways. Also, the Fraud Proofs paper is randomized which unties them from our f+1 paramater. We could devise a deterministic variant of the Fraud Proofs paper.

We expect these fraud proof transactions to be very unlikely (especially with rule #5). As an alternative optimization, we could employ a zero-knowledge proof that some f+1 erasure coded pieces reconstructs to something different than the attested-to data hash. With SNARKS, if the codes are instantiated with polynomials over the right field, they can be efficiently evaluated within a proof circuit.
