# Polkadot
## Overview
Polkadot consists of a main chain called the relay chain and multiple sharded chains called parachains. The relay chain is maintained by validators that are selected through the [NPoS scheme](NPoS/index.md#the-npos-scheme) and is responsible for producing blocks of the relay chain (via [BABE](BABE/Babe.md)) and keeping the state of all the parachains.
These validators need to vote on the consensus, see [GRANDPA](GRANDPA.md), over all the parachains blocks. For parachains, there are additional actors called collators and fishermen that are responsible for parachain block production  and reporting invalid parachain blocks respectively. In the figure below an example cut-out of Polkadot with part of the relay chain, one parachain, three validators and five collators are shown. 

![Figure 1 - Relay chain, Validators, Parachain, and Collators](images/data_structure.png)

Validators are assigned to parachains, which are responsible for validating parachain blockd and keeping them available via the [A&V scheme](Availability_and_Validity.md). Moreover, another feature of Polkadot is enabling interchain messaging among parachains, called [XCMP](XCMP.md). 

The security goal of Polkadot is to be Byzantine fault tolerant when the participants are rational. Rewards are given out when validators behave correctly and validators misbehaviour is punished via the [Slashing mechanism](slashing). More details on incentives and economics are reviewed [here](Token%20Economics.md).

Furthermore, Polkadot has a decentralised governance scheme that can change any Polkadot design decisions and parameterisation. Details on low-level cryptographic primitives can be found [here](keys/index.md) and Polkadot's networking schemes is in progress with some details being reviewed [here](networking/overview.md).  


![Figure 2 - Data structures and participants](images/whole.png)


## Keys

To identify unique individual participants that will perform duties on the network we use public key cryptography. You can read more about our approach [here](keys) and see the particular crypto for the first implementation in the [Schnorrkel repo](https://github.com/w3f/schnorrkel).

Validator keys indicated by the staking key are:
 - transport layer: ed25519
 - GRANDPA and consolidated reporting: BLS
 - block production (VRF): Ristretto

## Proof-of-Stake

In order to keep certain parties accountable for ensuring various properties listed below we make sure to be able to punish these participants by taking away some of their funds (Proof-of-Stake). The primary nodes running the network are the validators. To ensure a large set of participants is able to contribute to the security of the network we introduce a Nominated Proof of Stake scheme (NPoS). This scheme allows participants which do not wish to run nodes to be able to help with the validator selection. The current method used to distribute that stake is the [Sequential Phragmén Method](NPoS/index.md#the-npos-scheme).

For Polkadot use Phragmén's method as a fallback, but allow for better solutions to be submitted. As an edge case, if no good solution is submitted, run the slow heuristic which provides a 2-approximation (TODO: publish).

Judging NPoS solutions:

- Check if a submitted solution is locally optimal in the sense of a certain local search procedure. Locally optimal solutions have a fairness property. Thus we only accept solutions that are fair (TODO: publish).
- Among the submissions that observe the first property about fairness, select the one that maximizes the minimum stake of any selected validator. This ensures maximum security threshold for each parachain validator group.

A comprehensive list of misbehaviours that have to be penalized can be found in the [sanctioning sheet](https://docs.google.com/spreadsheets/d/1HSCiAf9pyxUSwojGQzg_pestlS_8yupCOTGnIGSvp9Q/edit?usp=sharing).

## Why not use different sets for different tasks?

Use the same validator set for BABE as for GRANDPA as to avoid paying more in total for block production + finality.


## Desired architectural qualities

* Minimal: Polkadot should have as little functionality as possible.
* Simple: No additional complexity should be present in the base protocol.
* General: Polkadot can be optimized through making the model into which extensions fit as abstract as possible.
* Robust: Polkadot should provide a fundamentally stable base-layer.


For other information regarding the project please refer to the [wiki page](https://wiki.polkadot.network).

We are working on a implementation level specification of the protocol [here](https://github.com/w3f/polkadot-re-spec).
