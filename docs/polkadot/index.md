# Polkadot: Overview

Polkadot consists of a main chain called the relay chain and multiple sharded chains called parachains. The relay chain is maintained by validators that are selected through the [NPoS scheme](NPoS/index.md#the-npos-scheme) and is responsible for producing blocks of the relay chain (via [BABE](BABE/Babe.md)) and keeping the state of all the parachains.
These validators need to vote on the consensus, see [GRANDPA](GRANDPA.md), over all the parachains blocks. For parachains, there are additional actors called collators and fishermen that are responsible for parachain block production  and reporting invalid parachain blocks respectively. In the figure below an example cut-out of Polkadot with part of the relay chain, one parachain, three validators and five collators are shown.

![Figure 1 - Relay chain, Validators, Parachain, and Collators](images/data_structure.png)

Validators are assigned to parachains, which are responsible for validating parachain blockd and keeping them available via the [A&V scheme](Availability_and_Validity.md). Moreover, another feature of Polkadot is enabling interchain messaging among parachains, called [XCMP](XCMP.md).

The security goal of Polkadot is to be Byzantine fault tolerant when the participants are rational. Rewards are given out when validators behave correctly and validators misbehaviour is punished via the [Slashing mechanism](slashing). More details on incentives and economics are reviewed [here](Token%20Economics.md).

Furthermore, Polkadot has a decentralised governance scheme that can change any Polkadot design decisions and parameterisation. Details on low-level cryptographic primitives can be found [here](keys/index.md) and Polkadot's networking schemes is in progress with some details being reviewed [here](networking.html).


![Figure 2 - Data structures and participants](images/whole.png)


**For other information regarding the project please refer to the [wiki page](https://wiki.polkadot.network).**

**We are working on a implementation level specification of the protocol [here](Polkadot-Runtime-Environment.md).**
