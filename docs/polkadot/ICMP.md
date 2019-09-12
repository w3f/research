====================================================================

**Author**: Fatemeh Shirazi

**Last updated**: 12.12.2018

**Note**: This write-up contains only notes from a ICMP workshop 15.11.18-16.11.18 in Berlin.

====================================================================

# ICMP Scheme

## Motivation
We want to enable inter-chain messaging among parachains. We want a guarantee that when we send a block we are sure that we have received all the previous messages. Moreover, we want to put a limit on the size of incoming messages to avoid overflowing.

## Inter-chain messaging scheme assumptions

We assume all parachains have an internal input and output queue. Moreover, there is a fixed amount of data each parachain can send to another parachain.

To avoid parachains being flooded and over loaded, a parachain can block messages coming from other parachains. The bridges are notified of this blocking and convey it to the users on the corresponding parachain.

PoV Block is execution proof witness data. This might include:

* Output Messages (as message bundle hash preimages)
* External data (“transactions”, “extrinsics” or any other data extrinsic to Polkadot)
* Witness (cryptogrpahic proof statements of data validity)
* New header (probably only the case for verification-only STFs like zkSTARKs or whatever)

## Steps (Order) of Receiving and Sending Messages Belonging to a Parachain Blob:

1. The collator needs to first check whether he has any incoming messages (which he might not have)
    * Collator runs relay chain light client to determine relay chain header
    * Collator tracks parachain header and that parachain’s input queue as a set of hashes of message-bundles (which requires tracking all parachain’s output queues since the last time the parachain accepted input)
    * Collator queries parachain validators or collators or availability guarantors (based on relay chain data) in order to get actual message data from bundles
2. Collator has a transaction pool
3. The collator creates block candidate based on this transaction pool, previous header, and any other data (e.g. inherents), and incoming messages
4. Collator builds a PoV block candidate for this parachain on the data from 3, this includes outgoing messages
5. Collator distributes it to all parachain validators
6. Parachain validator produces attestations on some subset of valid PoV candidates that it receives and redistributes to other parachain validators and block author
7. Block author selects a set of PoV candidates, at most one for each parachain, which are fully attested by their group
8. Block author distributes the relay chain block candidate to other validators

## Compact Routing Proofs

It may be possible to use some sort of proof-of-knowledge to prove that the output queues have been routed to the correct input queues correctly, taking into account temporarily-offline parachains.
