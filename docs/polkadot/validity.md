(tentative scheme for)

# Parachain Validity

How do we ensure that Parachain blocks whose header is included in the relay chain is valid? To ensure scalability, by default only a small fraction of relay chain validators can check the validity of each parachain block before it's header is included.

On the other hand, a popular public parachain will have many full nodes, all of which will check the validity of the blocks in that parachain.

So what we do is have a few validators validate a parachain candidate block and sign for its validity. Then if an invalid block is included, a wider group of actors known as fisherman can flag up that an invalid block is included in a relay chain block. If this happens, we need to agree on a chain that does not include this parachain block.

Because this may be expensive for the protocol, we will slash the validators who signed for the parachain candidates validity 100% of their stake. The hope is that will make this a rare event.

We want an off-chain protocol, one which large parachain blocks do not need to be put on the chain. This makes validity mildly subjective.

## Parachain block inclusion protocol

1. A parachain collator produces a PoV(proof of validity) block.

2. The collator sends this PoV block to the parachain validators, the subset of relay chain validators who validate this chain.

3. The parachain validators run the state transition validity function on the PoV block. If it passes, they sign the block header, which is a promise that the block is valid and that they will keep the PoV block available. If it fails, then they sign a claim that the parachain header refers to an invalid block. They still promise to keep the PoV block available. This may initiate the protocol below.

4. A relay chain block producer can include the parachain header in a relay chain block if the parachain header is signed by a sufficently large majority of parachain validators.

5. As a parachain validator, if a relay chain block appears with an unseen header, then they should attempt to get hold of this block, by asking full nodes of the network, other parachain validators and eventually recovering from erasure coded pieces (see [citation needed]). If we do, then we do 3.


This ensures that any parachain block whose header is included in the relay chain is claimed to be valid by several staked validators.

The parachain validators are themselves selected at random from the set of relay chain validators. This means that even if a few of the relay chain validators are malicious, it is unlikely that enough of them are validating the same parachain at the same time. However, since the number of parachain validators is small and we switch these sets often, the probability that the majority of parachain validators are malicious might not be negligible in this case.

## When validators disagree

If a single parachain header has both signed claims by validators that it is valid and that it is invalid, then all validators download the block and check its correctness.  We then aggregate signatures for these claims and post a transaction on chain when we have over 1/3 validators in either direction.

Validators also keep available any PoV block they have claimed is valid or invalid.

If 1/3 sign to say that it is incorrect, then the parachain block and any relay chain block that contains it are considered invalid.

If 1/3 sign to say it is incorrect and we do not have 1/3 signed saying it is correct as well, then we slash all validators who signed to say it is correct. If this includes a majority of parachain validators, then they should be slashed 100%.

If 1/3 sign to say it is correct but not 1/3 to say that it is incorrect, then we slash all validators who said it was incorrect.

If both happen, we consider the block invalid but don't slash anyone. This can only happen if either we have 1/3 malicious validators or the state transition validation function is ambiguous on this input. So hopefully never.

A challenging fisherman may also be required to keep available the challenged PoV block and validators may ask them for the block (since its signers may have an interest in keeping it unavailable if it is invalid).


## Fisherman

The idea here is that a fisherman, someone who meets certain criteria, can publish somewhere a claim that a PoV block, that some validator sign to say was correct, actually is incorrect. They do this by submitting a transaction to the relay chain. 

The fisherman have some kind of fishing power. If multiple fisherman make the same challenge, we sum their fishing power. (Submissions for a cooler name than fishing power are open.)

We consider the challenge answered (for now) if

min(no. of parachain validators + floor(sum of fishing power), ceiling(no. of validators/3))

sign to say it is correct and either none say it is incorrect or we have 1/3 signing for either possibility. Note that an answered challenge may later be unanswered if more fishermen join in.

If 1/3 of validators sign to say it is incorrect, the challenge is vindicated.

If a fisherman has a challenge that is answered but not vindicated, then we ignore any further challenges from them. If it remains answered but not vindicated at the end of the challenge period then we slash or otherwise remove the fishing priviledges from the fisherman.

If it is vindicated, then they may be eligible for a reward taken from slashed validators.

## When do validators dowload a PoV block and verify it?

If we are a parachain validator for that chain or validators disagree then we always do this. Otherwise each validator has a number a chsoen uniformly from [0,1] associated with each parachain block. The number should be unknown to other validators and it's probably easist to derive it deterministically from something. Then we download the block if it is in a relay chain block and

a < 1/(5 * No. of parachains)

. If it has been challenged, then whether or not it is in a relay chain block, this changes to


a < 1/(No. of parachains) + total fishing power/num validators + some constant rate * time challenge has gone unanswered.

The idea here is that:

1. Even if there are no fishermen for a parachain, it is still risky for parachain validators to validate an invalid block

2. Even if only fishermen with small fishing power challenge something, as long as most validators are honest, then probably some honest validator will check it.

3. But in case 1 or 2, the number of PoV blocks dowloaded by a validator has constant expectation, so the system is still scalable.

4. A challenge has a good probability of being answered quickly and is always eventually answered.

5. The expected number of additional validators who check something is bounded by the total fishing power of the challenge.

## Challenges and finality




