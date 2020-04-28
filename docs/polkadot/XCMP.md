====================================================================

**Author**: Alistair Stewart, Fatemeh Shirazi (minor)

**Last update**: 20.12.2019

====================================================================
# XCMP - Relay chain light client design

In this document, we describe how messages are stored and retrieved for XCMP. This write up does not cover ICMP networking, but rather the emphasis is on what data is on-chain such that parachains and parathreads can be sure about which messages they have been received.

## Motivation
Parachains and parathreads can have various reasons to send messages. To name a few examples: there can be a need for a token transfer, sharing/transferring smart contracts or providing a service by a parachain to another. This should all be accomodated for by XCMP. 

## Problem
The problem is that parachain collators need to be aware of messages they have received from sending parachains. In particular, they need to be aware of messages they have not acted on yet. In order to do so, and to avoid too much parachain-parachain traffic, the relay chain needs to be able to authenticate both the messages and the information on which messages a parachain has acted on. 

However, to keep all the hashes of these messages on the relay chain is a lot of data and may require looking for that data in many places. 

Furthermore, the period since the parachain has acted on messages might be long and parachain validators might have been reassigned already or not be validators at all anymore.

This latter problem is especially true for parathreads, that might have long gaps between parablocks.

## Goals
XCMP should accomodate for the following:
(1) All validators should be able to validate PoVs for as long as possible, at least a day after a parablock has been produced. To do this, the validators need to check that the right incoming messages were acted on. 

(2) A minimal relay chain state storage should be used. Relay chain processing and state access per block also needs to be feasible.

(3) A full node of a receiving parachain or parathread needs to know whether it has a new message from any parachain since the last relay chain block that it acted on messages. 

(4) If a particular sending parachain sends a receiving parachain a message, and then this sending parachain produces blocks that do not send any messages to that receiver, then a collator of the receiving parachain does not need any data from full nodes or parachain validators of that particular sending parachain. In particular, this means that there is only parachain-parachain traffic when a receiver needs to act on new messages from a sender.

## Assumptions 

A receiving parachain acts on messages in order of the relay chain block that includes the header of the parablocks that iniated that message. If multiple sending parachains have sent a receiving parachain messages in the same relay chain block then the order of messages that the receiving para will act on is according to a rule such as increasing parachain id, or alternatively a deterministic shuffle based the relay chain block number. It is reasonable to assume that a parachain can act on at least all messages sent by another single parachain in a single parablock. Hence, we can always assume once a receiving parachain has acted on a parablock in the relay chain it has acted on all messages associated to that parablock. 
Thus there is well-defined *watermark=(relay chain block number, paraid)* that indicates the last parablock whose messages the receiving para has acted on. 

The parablock's watermark should be in the parachain header that goes into a relay chain block and the last watermark needs to be stored in the relay chain state associated with the para.

By construction each parachain can talk to every other parachain. However, since there may be a very large number of parathreads, there should be a limited number of places a parachain collator has to query every time it wants to build a block. Hence, there should be a limit to the amount of data the relay chain has to store for messages sent from parathreads.

Either parachain collators have to query the relay chain in lots of places or else the relay chain logic (and so all full nodes of the relay chain) has to query lots of places in the relay chain. To limit this, we limit the number of chains the parathread can communicate with to 100 and refer to those as *channels*. This means a parachain can communicate to all other parachains (also up to a 100) and also have channels to a known number of parathreads (possibly more than 100). The list of channels is stored on the relay chain state. Both parachains of a channel need to agree to set up such a channel, and while it is open, both need to have the other as one of their channels.

Note that we assume here that channels are one directional, but they may be implemented as bidirectional.

There also needs to be a limitation on the number of unreceived messages one parachain can send to the other.

## Solution Overview

We want to have a data structure that is compressed, but also ensures receiving parachains can still find the messages sent to them. Next, we describe how to construct such a data structure. 

### Data Structure: Merkle Tree and Bitfield

We want to build a data structure that allows having a small amount of data on the relay chain blocks and relay chain state, but enabling verfication of all received messages in a PoV block. 

**Message Queue Chain**: 
To keep a minimal amount of data for messages on the relay chain, messages are chained in a message queue chain where only the head of the chain is stored. This also ensures that messages have an order in which the receiver should act on it. 

We define the message queue hash chain as follows. We have a $H(Head_{HC})$: $Head_{HC}$ $=H(m)|| b || H(\text{ previous } Head_{HC}))$, 

where *m* is a message, *H()* is a hash function, and *b* is the relay chain block number we last sent a message (not $m$, but the previous message). 

See [here](https://github.com/paritytech/polkadot/issues/597) for more details. 

For each parablock there is a tuple that consists of the parablock *message root* (that is the sender_message_queue_merkle_root) and a *bitfield*, which are stored in the parablock header of the relay chain block.

The message root is the root of a *Merkle tree* that can be used to look up the $head_{HC}$ from the receiving paraid. The bitfield has one bit for each channel and indicates which receiving parachains this parachain block sent messages to. The message root and bitfield will be in the sending parachain header and will be used to update the relay chain state.  

When a receiving parachain is building a PoV block it includes the latest of these message roots from the parachains that have channels open to this parachain. Using the message root, the receiving parachain needs to prove that it got all the messages from the last watermark up to the current watermark. This can be done by giving the message root and a Merkle proof to the head of the sending parachain message queue and revealing the hash chain back to the earliest message that came after the last watermark. This contains the hashes of all the current messages which can be used to verify that all the received messages were correct. Moreover, the message hash chain that is revealed also can be used to verify that the last message before the ones we acted on had a block number that is lower than the last watermark.

**Creating a Block PoV block**: Thus there are two things that collators need to work to produce a parablock. First, collators need to get all the messages and the corresponding Merkle proofs. Second, to produce a PoV block, they need to be able to query the relay chain for the latest message root with the corresponding block number, for the last message received in each channel. 

To validate a PoV block the parachain validators need to be able to find these message roots for at least a day after. This has a potentially large relay chain storage requirement if these are still on-chain. It would also be nice for light clients of the relay chain to be fishermen, and so be able to validate relay-chain blocks. For this reason, we will use relay chain light client state proofs for these message roots.

That is, for each channel, in the PoV block there will be a chain of hashes, starting at a relay chain state root, that consists of 3 parts:
- a relay chain light client proof of the message root,
- the Merkle proof of the head of the hash chain, and
- the hash chain expanded back to the point where the previous block number is before the previous watermark. This has the hashes of all messages the parachain need to act on in that channel.


### Implementation details about Relay-chain egress data
The Channel State Table (CST) is a construct that exists within the relay-chain's state and tracks the latest sender message queue roots. The CST items are stored in rows, where all items share the same sender. They are paired with the target's ParaId into a storage map. A second storage item contains a Merkle root of each row.

See [here](https://github.com/paritytech/polkadot/issues/597) for more details.

When the relay chain processes a parablock header, which includes the message root and bitfield, the relay chain nodes update a row of the CST corresponding to the sending parachain and the Merkle root of this row. The row contains the latest message root and block numbers for each parachain that has a channel from the chain that this parablock belongs to.

This row may be quite large, but it can be updated with a single storage write as it is in one place.

In principle, if we use this design, along with the bitfield, we can have a large number of outgoing channels, at the cost of more data in this single write opration. In particular, parachains will be allowed to connect to many more than 100 parathreads.

Optionally, parachains could have ingress queues that consist of (paraid, last message root, block number) for all  incoming channels.  The relay chain could update this every block. This would make it possible to have 10,000 channels for one chain and not to have to look up 10,000 places on the relay chain.

### Which Data is Stored Where? 

**Parachain-header/candidate_receipt in the relay chain block**: the message root and a bitfield that refer to receiving paras. Since we have a limited number of known channels this bitfield could be 128 bits for parathreads but for parachains it might need to be variably sized. It also needs the watermark (relay chain block number and paraid) to indicate whose messages the receiving para has acted on and the relay chain state root plus corresponding block number for which all relay light client proofs in the PoV block are based on.

**Sending parachain state**: the sending parachain state stores the hash chain back to the last watermark it has seen for the receiving para on the relay chain. It also stores the merkle proofs for each message root for all links in the hash chain (not just the head of the hash chain). Link refers to the triple which is hash of message, previous block number, and hash of previous link. 

The size of the hash chain determines how full the channel is. Old messages can be dropped on receiving evidence (via relay chain light client proofs) that the watermark of the receiving chain has been updated.

**Sending para validators**: they keep the message that has been sent at parablocks that they attested to, the full Merkle tree and the latest head of hash chain $Head_{HC}$. This data is stored for a day. 
 
**Relay chain state on-chain**: that is the CST that was described in the previous section.

![XCMP_CST](https://github.com/w3f/research/blob/xcmp-suggestions-leon/docs/polkadot/images/XCMP_clean.png)
This is an example of a Channel State Tables for paras A,B,C,D,E, that have nine channels in total amongst the paras. The Relay Chain State can help authenticate XCMP messages by storing the XCMP_root, which is the root of the Trie that contains all channel watermarks (i.e. *(relay chain block number, paraid)'s*). In this example, para A last acted on messages in relay chain block rc_1, para B last acted on messages in relay chain block rc_2, etc. The envelopes at the bottom correspond to the actual message content in the Message Queue Chain's for the channels. Only the head of these chains is used to construct the sending message roots. 

### Producing a PoV block
A PoV block needs to include a nested Merkle proof and hash chain expansion thats starts at the light client state root and ends at each incoming message that needs to be acted on. The Merkle proofs will have a lot of parts in common and can be optimized by sharing the common parts (future work). 

Consider a collator $C_A$ that wants to produce a PoV block for para $A$. We assume para B has a channel to para A (can send messages to A) and para A has a channel to para D (can send messages to D). Note that if channels are unidirectional then A might not be able to send messages to B and D not to A. 

The collator $C_A$ asks some full node of the relay chain to construct a light client proof of what the message roots for all channel that are open to para $A$ (e.g., para B). Note that $C_A$ and the full node might be running on the same machine. 

$C_A$ also needs light client proofs for the watermarks of paras that para A has channels to (e.g., para D). All these light client proofs should be constructed simultaneously from the relay chain state, which means they all start with the same relay chain state root. This relay chain state root and corresponding block number will be in the parachain header (candidate_receipt). 

**Optional**: For parachains, if we are going with ingress queues for them, we maintain a list of (paraid, last message root, block number) for all incoming channels that the relay chain updates every block. Thus the relay chain light client proof is just this list and a Merkle proof. 

If there is no special distinction between parathreads and parachains, the full node needs to look at egress data in the CST for up to 100 rows (or more for parachains) corresponding to paras that the sending para has channels with (i.e., all channels of para B). For each of these channels, a Merkle proof is needed that starts at the relay chain state root and ends at the (message root, block number) pair of the receiving para (i.e., para A). That is, for each channel there is a nested Merkle proof, where the first Merkle proof refers to the complete CST row and the second Merkle proof (of the nested Merkle tree) refers to the entry corresponding to receiving para (i.e., para A). 

We include all 100+ of these channel Merkle proofs in the relay chain light client proof.

After the full node has given the collater, $C_A$, all the light client proofs, $C_A$ has the block number and message root of all latest messages. Thus it can verify if para A has correctly received any particular message's content (payload) already. 

In case a message, say from para B, has not been acted on by para A, then $C_A$ needs that message and its proof from the message root. $C_A$ may have this message and proof already, but if $C_A$ does not, it needs to ask either any full node of para B that it happens to be connected to, or the para validators of A or B at the corresponding block number of the message. If the messages from para B are coming from its para validators, this may mean asking many validators who were para validators of B at different times, since the para validators of paras rotate as a function of block number. Note that full nodes of para B would know all of these messages and should be asked first.

Along with the latest message from B, $C_A$ should receive the proof that links the latest message to the message root and also the block number of the previous message, so it knows if it needs to ask for earlier messages as well. 

When $C_A$ has both: 
- all proofs of messages from message roots, 
- all proofs of messages roots from one relay chain state root (the nested Merkle proofs described above), 
it can combine them to get proofs for all messages from the relay chain state root and put these proofs along with all messages acted on into the PoV block.

For example, if para A has received many messages from para B since its last watermark, then the PoV block should include:

- A Merkle proof from the relay chain state root in the parachain header (or candidate receipt) to the CST row hash of B's row in the CST
- A Merkle proof of the message root and block number corresponding to the last message from B to A at the block height of the relay chain state root from the CST row hash.
- A Merkle proof of the head of the hash chain of messages from B to A from the message root
- An expansion of the hash chain (the triples) for the channel from B to A back to the point where the previous block number is before A's previous watermark
- Messages from B to A from after A's previous watermark and up to its new watermark, whose hashes correspond to those in the hash chain expansion.

Note that if the relay chain state root is correct and it is for a block number no ealier than the new watermark, then this proof shows that these are exactly the messages from B that A should be acting on.

It is likely that the parachain block, that full nodes of the parachain use to update their state, will contain unproven assertions about the received messages, watermark updates etc.

![XCMP_POV](https://github.com/w3f/research/blob/xcmp-suggestions-leon/docs/polkadot/images/XCMP_clean_PoV.png)
In this example, para A needs to show it acted on the last two messages that para B sent to A, i.e. those are the new messages. To prove this, collator C_A includes the following proofs in the PoV block. 1) the Merkle proof (the red nodes in the figure) from the relay chain state root to the CST row hash of B. 2) the Merkle proof (the blue nodes) of the message root and block number corresponding to the last messager from B to A at the block height (rc_1) of the relay chain state root from the CST row hash. 3) the Merkle proof (the orange nodes) of the head of the hash chain of messages from B to A. 4) The expansion of the hash chain (the triples) plus the messages from B to A from A's previous watermark up to its new watermark (the nodes + envelopes in green).

### Validating a PoV block


Given the scheme above, anyone who knows these three things are able to validate a PoV block: 
- The PoV block itself, 
- the state-transition-validation-funtion (STVF) 
- the parachain block header. 
This would enable fishermen who are not clients of either or both the parachain and the relay chain to validate PoV blocks.

However there is a downside to the scheme if we cannot *trust the STVF* (once we have SPREE, which we'll talk about below, this will not be an issue anymore.) The downside when there is a malicous STVF is that the relay chain does not verify the hash chain updates, and they are left in the parachain state. If this parachain state was changed by the STVF, it would be possible to require a sending para to receive a message with a hash for which no message has ever been sent and so eventually stalling the receiving para.

Before SPREE, we should require that the parachain validators verify the hash chain update independently of the STVF verification. The parachain validators would need to check the 1) Merkle proof of the new message and hash chain head from the relay chain root, and 2) the Merkle proof from the last message root, which is currently in the relay chain. Checking (1) and (2) satisfy that the previous hash and block number in the new hash chain head indeed corresponds to the previous hash chain head.

Failing to do that correctly should be a slashing condition for the parachain validators as well. However if we are going to implement SPREE soon, then this is a low priority as we may end up skipping it.

### SPREE integration

SPREE is a method of having modules with state and execution sandboxed from the rest of the wasm execution. We want a SPREE module on one chain (can be para or maybe relay chain) to send a message to the same SPREE module on another chain and for it to be impossible for the STVF of either chain to interfere with that message.

Since our solution requires parachain state for messages, the obvious way to do this is to have the message handling code and state itself be handles by a SPREE module. We would have a central SPREE module that all parachains would require if they wanted to participate in XCMP at all.

The message handling SPREE module would be called first on execution of an STVF and it would route incoming messages to other SPREE modules and to the bulk of the STVF, before handing over control to the rest of the STVF.

We think that receiving modules should not act on the messages on receipt, but merely add the incoming messages to a buffer and wait for the STVF to scedule them time to act on them.


### How much data is this?

The egress data for a sending parachain has a Merkle root and block number for receiving paras. The Merkle root will be a 32 byte hash and the block number 4 bytes. 


We may have up to a million channels. This means 36 MB data on-chain or 72MB if we include the Merkle trees as well as the data and the Merkle root for each egress table. In the worst case, half of these would be updated in a block.


We need to hash twice this amount of data to calulate its Merkle root. Blake2b is fast, see https://blake2.net/ , and in 1 second, it can hash over 100 MB on a modern processor. So we'd be looking at 36 MB and 360ms.

But even this is unlikely.












