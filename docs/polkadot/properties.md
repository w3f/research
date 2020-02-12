# State Transition Properties

![Figure 4 -State transition properties](images/properties.png)


## 1 Utility

Each state transition should bring some utility to the system participants. In order to ensure that this is the case:

- state machines should provide some utility to participants
- state transitions processed by these state machines reflect well the state transition needs of participants.

![Utility](images/usefulness.png)

To ensure that the state machines provide utility we should ensure that there is a mechansim that enables participants to decide what state machines should be included and how they should change to reflect participant needs. This mechanism is the [Polkadot governance scheme](https://github.com/paritytech/polkadot/wiki/Governance).

To ensure that useful state transitions are processed by those state machines, we will want to ensure that useful transactions get included in Polkadot blocks. Polkadot will have a transaction fee mechanism on the relay chain to ensure that transactions issued by parties willing to pay a reasonable price for them are included. There will also be a certain portion of each block that is dedicated to certain high-priority transactions, such as misbehaviour reporting. The utility of the parachain state transitions has to be ensured by the state transition function of a given chain.

## 2 Validity

![Validity](images/validity.png)

The notion of validity in Polkadot is determined by a state transition validation function (STVF). Each chain in the ecosystem has to have one implemented. In order for all nodes to be able to run this function it is being distributed as deterministic WebAssembly (Wasm) code which can be executed by the Polkadot Runtime Environment.

The blocks are produced by parachain collators, then they get validated using the STVF by the subset of validators responsible for the given parachain to finally get included in the Polkadot Relay Chain. During this process validators, parachain collators and other parties are free to challenge claims of validity to trigger additional check, these parties are referred to as fishermen. [Read here about parachain validity](Availability_and_Validity.md).

## 3 Finality

![Finality](images/canonicality.png)

Finality of the Polkadot network state machines is achieved via a combination of a block production mechanism with eventual probabilistic consistency ([BABE scheme](BABE/Babe.md)) and [GRANDPA finality gadget](GRANDPA.md).

This approach allows for block production (thus transaction confirmations) to be fast, while allowing for as fast as possible economic finality with compact proofs.

## 4 Availability

![Availability](images/availability.png)

In order for the critical data from all chains to remain reachable by users and subsequent block producers, Polkadot makes use of an erasure coding based [availability scheme](Availability_and_Validity.md).

## 5 Messaging reliability

![Messaging](images/messaging.png)

Besides ensuring all the above properties for all parachain, a crucial element of Polkadot is that these state machines are able to affect each others state transitions. This is done via the [Cross-Chain Message Passing (XCMP) scheme](XCMP.md).

## 6 Size

![Size](images/size.png)

To ensure that the state transitions can be processed and stored by the network their size has to be reasonable. Mechanisms such as transaction fees and block limits are there to limit the storage size and computation required for each block.

### Light client

The protocol is being designed with light client support in mind with existing Substrate implementation supporting one.

## 7 Bandwidth

To ensure usability in realistic network conditions a reasonable bandwidth requirements have to be maintained.
