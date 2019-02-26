# Parachain Validity

How do we ensure that Parachain blocks whose header is included in the relay chain is valid? To ensure scalability, by default only a small fraction of relay chain validators can check the validity of each parachain block before it's header is included.

On the other hand, a popular public parachain will have many full nodes, all of which will check the validity of the blocks in that parachain.

So what we do is have a few validators validate a parachain candidate block and sign for its validity. Then if an invalid block is included, a wider group of actors known as fisherman can flag up that an invalid block is included in a relay chain block. If this happens, we need to agree on a chain that does not include this parachain block.

Because this may be expensive for the protocol, we will slash the validators who signed for the parachain candidates validity 100% of their stake. The hope is that will make this a rare event.



## Parachain block inclusion protocol

1. A parachain collator produces a PoV(proof of validity) block.

2. The collator sends this PoV block to the parachain validators, the subset of relay chain validators who validate this chain.

3. The parachain validators run the state transition validity function on the PoV block. If it passes, they sign the block header, which is a promise that the block is valid and that they will keep the PoV block available

4. A relay chain block producer can include the parachain header in a relay chain block if it signed by a sufficently large majority of parachain validators.

This ensures that any parachain block whose header is included in the relay chain is claimed to be valid by several staked validators.

The parachain validators are themselves selected at random from the set of relay chain validators. This means that even if a few of the relay chain validators are malicious, it is unlikely that enough of them are validating the same parachain at the same time. However, since the number of parachain validators is small and we switch these sets often, the probability that the majority of parachain validators are malicious might not be negligible in this case.


## Fisherman

The idea here is that a fisherman, someone who meets certain criteria, can publish somewhere a claim that a block is incorrect and a proof of that, which may be the entire PoV block.

Then we do not buld on the relay chain block including that parachain header, even if it was finalised by GRANDPA and slash the parachain validators who signed it.

There are a number of issues to designing a protocol for this.
