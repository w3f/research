=================================================================

**Authors**: Fatemeh Shirazi, Rob Habermeier

**Last updated**: 12.09.2019

**Note**: This write-up contains notes from a networking workshop 05.08.19-06.08.19 in Berlin at Parity Technologies.

=================================================================
# Networking for Polkadot

## Overview

In Polkadot we need to send a number of messages to a number of entities. Below we give an overview of where and how each type of message is sent. The column *Nets* refers to the networks where a type of message is traversing and the column *Mode* refers to the type of  routing. The column *Static DHT Prefixes* refers to the DHT prefixes of the receivers if we use a one DHT for all and use prefixes to separate sub-networks.

We use gossiping mainly when the message type is small. For example, GRANDPA votes and attestation are very small. For bigger data structures we need to either use bloom filters or use direct routing.

Nets:
PC = Parachain Collator and parachain full nodes
PV= Parachain Validators
V = Validator and relay chain full nodes (->Validator Network ID on chain)

Mode:
D = Direct transfer
G = Gossip

B = Big / Bloomfiltered
R= Receving e.g., $PC_{R}$ refers to the receiving parachain's collators and full nodes
S= Sending e.g., $PC_{S}$ refers to the sending parachain's collators and full nodes

\* should soon change gossiping into direct routing

| Message type              | Nets        | Mode      | Static DHT Prefixes|
| ----------------- | ----------- | --------- |-----|
| Parachain TXs     | PC          | G        |Depends on Parachain|
| PoV block         | PC + PV    | D         |-|
| Parachain Block   | PC + PV     | G:PC, D:PV  |$P_0$,...,$P_n$|
| Attestations      | V           | G        |V|
| Relay chain TXs   | V           | G         |V|
| Relay chain block | PC + V       | G$^B$        |General|
| Messages         | $PC_{R + S}$ | G (fallback->D:$PV_{R}$ request $PV_{S}$ and then uses G at $PC_{R}$ to spread them, second fallback->D: $PV_{R}$ recover messages from erasure codes obtained from V and use G at $PC_{R}$ to spread them)         |V|
| Erasure coded    | V           | $G^*$         |V|
| GRANDPA Votes     | V           | G        |V|


## Critical Paths for Networking

We have two important goals: a) inclusion of parachain blocks (PBlocks) in Relay chain, and b) Relay chain blocks (RBlocks) get finalized.

The critical networking for reaching these goals are in order as follows.

### a) PBlock gets included on Relay chain

1. Validators $\xrightarrow[]{\text{latest RBlock}}$ Collator: G and Syncing
2. Collator $\xrightarrow[]{\text{included PBlock}}$ Collator: G and Syncing
3. Collator/PV $\xrightarrow[]{\text{Messages}}$ Collators(of receving parachain): G and Direct requesting (see below for more details on Interchain Messaging)
4. Collator $\xrightarrow[]{\text{PoV Block}}$ PValidator(of receving parachain): Advertise and Direct sending
5. PValidator $\xrightarrow[]{\text{Attestations+PBlock Header}}$ Validators: G


### b) RBlocks get Finalized

1. Validator $\xrightarrow[]{\text{PoV Block erasure-coded pieces}}$ Validators: Direct sending
2. Collators/Fishermen/Validators $\xrightarrow[\text{Post-inclusion claims}]{\text{TXs}}$ Validators: G

3. PValidators or Validators $\xrightarrow[]{\text{PoV Blocks}}$ Validators: G, Direct sending
4. Validators$\xrightarrow[]{\text{GRANDPA Votes}}$ Validators: G

## Interchain Messaging
To send messages from one parachain (sending parachain) to another parachain (receiving parachain) depending on the setup the follwong steps will be carried out.

1. When full nodes of the sending parachain are also part of the domain of the receiving parachain, gossiping the message suffices
2. A relay chain full node is in the domain of both the sending and receiving parachain, gossiping the message suffices
3. Parachain validator of receiving parachain does not see the message being gossiped, then it request the message directly from the parachain validator of the sending parachain (PV at the moment of sending). The PV of the sending parachain are responsible to keep the messages available. The parachain validators of the sending parachain directly send the messages to the receiving parachain PV's. Finally, the PV's of the receiving parachain gossip the messages in the receiving parachain network.


The are three main networking protocols we require for Polkadot as follows:

i) GRANDPA gossiping

ii) Parachain networking, which includes: gossiping parachain blocks and sending/ receiving erasure coded pieces

iii) Interchain message-passing

Next, these schemes will be described.
