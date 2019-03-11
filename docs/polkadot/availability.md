# Availability

## Motivation

In Polkadot parachain, collators are responsible for creating parachain blocks and sending them to parachain validators. These parachain validators, which are a subset of all relay chain validators, must validate the blocks and submit summaries (called headers) to all the validators of the relay chain. One of the relay chain validators is going to add this parachain header in the form of a relay chain block to the relay chain. 

**Definition**: Let us define a *parachain blob* as a tuple $(PoV, B, M)$ where $PoV$ is the light client proof of validity for a parachain block, representing all witness data in order to let a light (stateless) client execute it, $B$ is the parachain block itself, and $M$ is the outgoing messages from that parachain.

Fishermen are light clients that are responsible to check the validation process carried out by parachain validators. However, fishermen do not have access to all the parachain blobs since they are not full nodes of the parachain necessarily. Hence, if parachain blobs are not available, fishermen would not be able to detect faulty proofs and raise any concerns. Moreover, if dishonest parachain validators create parachain headers for non-existing blobs, other relay chain blocks might be built upon non-existing parachain blobs.

Therefore, once a block is created, it is important that the parachain blob is available for a while. The naïve solution for this would be broadcasting/gossiping the parachain blobs to all full nodes, which is not a feasible option because the parachain blobs are big. We want to find an efficient solution to ensure parachain blobs from any recently created parachain block are available. 


## Availability via Erasure Coding

Let us assume that $V$ is the set of all the relay chain validators such that $n=3f+1=|V|$ be the total number of the relay chain validators. Let $PV \subset V$ be the subset of $V$ containing all parachain validators and $HV \subset V$ is the subset containing the honest and online relay chain validators. We assume that $HV \geq n-f$. We assume reliable networking for now and consider networks attacks out of scope at this moment, where an intermediate validator blocks communication amoung two other validators. Such attacks will be addressed later. 


### Availability Protocol

1. A collator sends a parachain block, its outgoing messages and a light-client proof of correctness of these (a parachain blob) to the parachain validators.
2. Once the parachain validators have validated it, they create an erasure coded version with an optimal $(n,k)$ block code of this blob, where $k=f+1$.
They also calculate a Merkle tree for this erasure coded version and add the Merkle root to the sets of values they sign about the block for inclusion on the relay chain. 
3. The parachain validators send out these pieces along with a Merkle proof to all relay chain validators. To distribute erasure coded pieces, validators are divided among parachain validators who agree on the validity of the parachain blob to avoid repetition.
4. The parachain block header gets included on the relay chain. Note that the header includes signatures from all parachain validators who successfully validated the blob.
5. If a validator has not received an erasure coded piece for every parachain blob that has a header in a relay chain block, it requests it from the parachain validators. The piece they should ask for is different for each relay chain validator. Along with the piece, a parachain validator needs to provide the Merkle proof corresponding to the Merkle root on the relay chain.
6. During the execution of GRANDPA protocol, a relay chain validator only prevotes for a (descendant of a) relay chain block if it has received an erasure coded piece for each parachain block header included in that relay chain block. Validators only build on blocks if they have just seen it very recently (e.g., last block) or they have all the pieces. We do not want to build on a block that has an unavailable ancestor block. 
7. A validator who has not received an erasure coded piece for a blob header in a relay chain block needs to requests for the missing erasure coded piece. It sends the request first to the parachain validators who also signed off on the validaity of the blob, but were not the parachain validator who was supposed to send the erasure coded piece. Afterwards, the validator requests the erasure coded piece from the other full nodes of the parachain. If full nodes of the parachain are not able to provide the missing pieces, the relay chain validator whose piece is missing does not validate the corresponding relay chain block.

The idea here is that we do not finalize a block until sometime after $f+1$ honest validators prevote for it. But if that's the case, then 6. should succeed, which means that we only finalize available blocks. If 7. happens fast enough, then we only finalize valid and available blocks. As before, we will need to plan for when we finalize an invalid block.

### Backing up erasure-coded pieces

Note that an honest parachain validator can back up the pieces at a (random or preferably trusted) full node of the parachain before it sends them out to relay chain validators. Subsequently, that parachain full node can distribute those pieces to all full nodes of the parachain who can respond to requests from validators that are requesting missing erasure-coded pieces.


## Agreeing on non-availability and reconstructing parachain blobs

In this section, we describe how we agree that a piece of the erasure code of a parachain blob is not available. 

We require any one of the relay chain validators to announce that their erasure-coded piece of the blob is unavailable if a grace period (see definition below) has passed and they have not received their piece on for a parachain block included in a relay chain block on the longest subchain. It is assumed that the validators who announce unavailbility, should already have asked the collators (full nodes) of the parachain for the missing piece.

**Definition**: *Availability grace period* $\Delta T$ be the period of time passed after production of block $B$ on the best subchain $C$, of the relay chain, which a validator waits before validator $v$ announces unavailability for the parachain block $PB$ such that $Head_{PB} \in B$, if it has not received their erasure-coded piece for block $BP$.

1. Upon receiving an unavailability claim for a parachain block, an assigned validator (e.g., randomly assigned) tries to reconstruct the partially unavailable block first by asking the collators of the parachain and eventually by requesting other validators for their erasure-coded piece, and try to reconstruct the contested parachain blob. If succeeded, they re-compute the erasure coded pieces sending them to the validators claiming unavailability and the collators of the parachain.

2. Once a validator receives at least $f$ unavailability announcements for a parachain block whose header is included in block $B$, it will not vote to finalize $B$ or any of its descendants in GRANDPA.

3. Once $\frac{2}{3}$ of the validators claims unavailability, the collators of that parachain and the parachain validators who have signed the unavailable block are going to be slashed.

The availability procedure is only required for liveness, so it does not have to be fast. The issue is that if $f$ honest validators have a piece, then that is not enough to reconstruct the blob, but as far as they know, they can still vote for it. 

If there are any Byzantine or offline validators, then this might stop us from getting the $n-f$ votes needed to finalize another subchain. In this case, we might get two forks, one including the blob and one without it. If the one including the blob is longer, we need the availability procedure for everyone to agree that it is invalid.

Note that in the case when $f+1$ validators are Byzantine and the claim for an unavailable blob is available, they can finalize it with the help of $f$ validators who have the only $f$ pieces, and we have no way to uniquely attributing this fault. But this is also a problem for other schemes.


## Challenging a parachain block validity

If a parachain fisherman publishes a proof stating that the block is invalid, the validators which have signed off on the relay chain block containing the parachain block header must hand over the erasure-coded piece associated to that parachain block. If a validator refuses to hand over the piece, we slash them. Moreover, if the assigned validator publishes the proof that $f+1$ pieces cannot be decoded into a blob, then we slash the parachain validators and declare that relay chain block as invalid.

The Merkle root commitment means that all parachain validators who signed off on the blob must provide the same erasure-coded version. As a result, the erasure code is only used to recover from missing, rather than corrupted pieces. This is true even if some of the parachain validators are Byzantine, because any piece with a valid Merkle proof is the one that *all* the validators committed to. 

Accordingly, suppose there are $f+1$ pieces alongside the proof that they all belong to the same Merkle root in the block header. If they do not assemble to a valid decoded message (block), then all the parachain validators who signed the block header did so, knowing that it did not contain the Merkle root of a valid erasure code. So if the original block cannot be reconstructed from $f+1$ pieces, it is safe to slash every parachain validator who signed off on the Merkle root.
 
## Post-checking
Agreeing on unavailability might take a long time, particularly, if all parachain validators are malicious i might take a while for invalid/unavailable blocks to be detected. For adversary, this delay might be enough. We propose post-checking scheme, where availability and validity of parachain blobs is check as soon as they are added to a relay chain block. Note, that this scheme might not detect all unavailability/invalidity issues, hence, we keep the previous "agreeing on availability" as a fall back guarantee. 

Once a relay chain block has been added to the relay chain, validators need to randomly be self-assigned to parachains to check whether the parachain is still available and valid. Once, a validator is self-assigned to a parachain, it will check all none checked blob of that parachain. A list of checked parachain blobs is kept on the relay chain. 

## Storage efficiency
If there are $m$ parachains with parachain blocks of size $s$ bytes, then each validator stores $s/k$ bytes for each parachain and hence the total storage requirement is equal to $ms/k < 3ms/n$ as $k > n/3$.

In that regard, the amount of storage for the proposed availability scheme is less than a naïve scheme where $c$ randomly chosen validators store the same copy of a block for $c > 3$. In such a scheme, each validator requires $cms/n$ bytes on average to store a block. At the same time, the proposed scheme has more resilience against Byzantine validators.


## Current implementation in Polkadot PoC-4

Polkadot is currently using Reed-Solomon encoding of $(n, f+1)$ over Finite Field of $2^{16}$ elements where $n$ is the number of relay chain validators and $f=\lfloor\frac{n-1}{3}\rfloor$ to implement the availability scheme. 

Every parachain block alongside its extrinsics is encoded by SCALE codec and is possibly padded to make sure that the encoded data is of even length. The block then is seen as a sequence of two-byte chunks each representing an element of $GF(2^{16})$. The sequence is broken into $f+1$-length subsequences where the final subsequence is also padded by 0 to make it of consistent length with the other subsequences. Each subsequence is treated as a message word and is encoded using Reed-Solomon $(n,f+1)$ encoding into an n-tuple codeword vector whose elements are distributed between the validators. In this way, each subset of $f+1$ validators can reconstruct all of the $f+1$ subsequences and hence reconstruct the original parachain block.

Note that the implementation has not been done based on the 2D Reed-Solomon approach from https://arxiv.org/abs/1809.09044. 2D Reed-Solomon smaller proofs of non-decodability provide an improvement only if the proofs of invalidity of parachain blocks are likely to be smaller than the blocks themselves. Moreover, because the number of validators is a priori known, a 1D Reed-Solomon provides a deterministic scheme.
