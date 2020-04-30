## The Polkadot Parachain Host Implementers' Guide

## Ramble / Preamble

This document aims to describe the purpose, functionality, and implementation of a host for Polkadot's _parachains_. It is not for the implementor of a specific parachain but rather for the implementor of the Parachain Host, which provides security and advancement for constituent parachains. In practice, this is for the implementors of the Relay Chain. 

There are a number of other documents describing the research in more detail. All referenced documents will be linked here and should be read alongside this document for the best understanding of the full picture. However, this is the only document which aims to describe key aspects of Polkadot's particular instantiation of much of that research down to low-level technical details and software architecture.

## Table of Contents
* [Origins](#Origins)
* [Parachains: Basic Functionality](#Parachains-Basic-Functionality)
* [Glossary / Jargon](#Glossary)


## Origins

Parachains are the solution to a problem. As with any solution, it cannot be understood without first understanding the problem. So let's start by going over the issues faced by blockchain technology that let to us beginning to explore the design space for something like parachains.

#### Issue 1: Scalability

It became clear a few years ago that the transaction throughput of simple Proof-of-Work blockchains such as Bitcoin, Ethereum, and myriad others was simply too low. [TODO: PoS, sharding, what if there were more blockchains, etc. etc.]

[TODO: note about network effects & bridging]

#### Issue 2: Flexibility / Specialization

"dumb" VMs don't give you the flexibility. Any engineer knows that being able to specialize on a problem and create coarser-grained operations gives them and their users more _leverage_.  [TODO]


Having recognized these issues, we set out to find a solution to these problems, which could allow developers to create and deploy purpose-built blockchains unified under a common source of security, with the capability of message-passing between them; a _heterogeneous sharding solution_, which we have come to know as **Parachains**.


---

## Parachains: Basic Functionality

This section aims to describe, at a high level, the architecture, actors, and processes involved in the implementation of parachains. It also illuminates certain subtleties and challenges faces in the design and implementation of those processes.

First, it's important to go over the main actors we have involved in the Polkadot network.
1. Validators. These nodes are responsible for validating proposed parachain blocks. They do so by checking a Proof-of-Validity (PoV) of the block and ensuring that the PoV remains available. They put financial capital down as "skin in the game" which can be revoked if they are proven to have misvalidated.
2. Collators. These nodes are responsible for creating the Proofs-of-Validity that validators know how to check. Creating a PoV typically requires familiarity with the transaction format and block authoring rules of the parachain, as well as having access to the full state of the parachain.
3. Fishermen. These are user-operated, permissionless nodes whose goal is to catch out misbehaving validators in exchange for a bounty. Collators and validators can behave as Fishermen too.

This alludes to a simple pipeline where collators send validators parachain blocks and their requisite PoV to check. Then, validators validate the block using the PoV, signing statements to that effect, and then the block can be included. If a fisherman detects that a validator or group of validators incorrectly signed a statement claiming a block was valid, then those validators will be _slashed_, with the fisherman receiving a bounty.

However, there is a problem with this formulation. In order for a fisherman to check the validators' work after the fact, the PoV must remain _available_ so a fisherman can fetch it in order to check the work. The PoVs are expected to be too large to include in the blockchain directly, so we require an alternate _data availability_ scheme which requires validators to prove that the inputs to their work will remain available, and so their work can be checked.

Here is a description of the Inclusion Pipeline: the path a parachain block (or parablock, for short) takes from creation to inclusion:
1. Validators are selected and assigned to parachains by the Validator Assignment Process.
1. A collator produces the parachain block, which is known as a parachain candidate or candidate, along with a PoV for the candidate.
1. The collator forwards the candidate and PoV to validators assigned to the same parachain via the Collation Distribution Process.
1. The validators assigned to a parachain at a given point in time participate in the Candidate Backing Process to validate candidates that were put forward for validation. Candidates which gather enough signed validity statements from validators are considered "backed" and are called backed candidates. Their backing is the set of signed validity statements.
1. A relay-chain block author, selected by BABE, can include up to one (1) backed candidate for each parachain to include in the relay-chain block alongside its backing.
1. Once included, the parachain candidate is considered to be "pending availability". It is not considered fully included until it is proven available.
1. In the following relay-chain blocks, validators will participate in the Availability Distribution Process to ensure availability of the candidate. Information regarding the availability of the candidate will be included in the subsequent relay-chain blocks.
1. Once the relay-chain state machine has enough information to consider the candidate's PoV as being available, the candidate is considered fully included and is graduated to being a full parachain block, or parablock for short.

Note that the candidate can fail to be included in any of the following ways:
  - The collator is not able to propagate the candidate to any validators.
  - The candidate is not fully backed by validators participating in the Candidate Backing Process.
  - The candidate is not selected by a relay-chain block author to be included in the relay chain
  - The candidate's PoV is not considered as available within a timeout and is discarded from the relay chain.

This process can be divided further down. Steps 2 & 3 relate to the work of the collator in collating and distributing the candidate to validators via the Collation Distribution Process. Steps 3 & 4 relate to the work of the validators in the Candidate Backing Process and the block author (itself a validator) to include the block into the relay chain. Steps 6, 7, and 8 correspond to the logic of the relay-chain state-machine (otherwise known as the Runtime) used to fully incorporate the block into the chain. Step 7 requires further work on the validators' parts to participate in the Availability Distribution process and include that information into the relay chain for step 8 to be fully realized.

This brings us to the second part of the process. Once a parablock is "fully included", it is still "pending approval". At this stage in the pipeline, the parablock has been backed by a majority of validators in the group assigned to that parachain, and its data has been guaranteed available by the set of validators as a whole. However, the validators in the parachain-group (known as the "Parachain Validators" for that parachain) are sampled from a validator set which contains some proportion of byzantine, or arbitrarily malicious members. This implies that the Parachain Validators for some parachain may be majority-dishonest, which means that secondary checks must be done on the block before it can be considered approved.

The Approval Process looks like this:
1. Parablocks are pending approval for a time-window known as the secondary checking window.
1. During the secondary-checking window, validators randomly self-select to perform secondary checks on the parablock.
1. These validators, known in this context as secondary checkers, acquire the parablock and its PoV, and re-run the validation function.
1. The secondary checkers submit the result of their checks to the relay chain. Contradictory results lead to escalation, where even more secondary checkers are selected and the secondary-checking window is extended.
1. At the end of the Approval Process, the parablock is either Approved or it is rejected. More on the rejection process later.

These two pipelines sum up the sequence of events necessary to extend and acquire full security on a Parablock. Note that the Inclusion Pipeline must conclude for a specific parachain before a new block can be accepted on that parachain. After inclusion, the Approval Process kicks off, and can be running for many parachain blocks at once.

[TODO Diagram: Inclusion Pipeline & Approval Processes interaction]

It is also important to take note of the fact that the relay-chain is extended by BABE, which is a forkful algorithm. That means that different block authors can be chosen at the same time, and may not be building on the same block parent. Furthermore, the set of validators is not fixed, nor is the set of parachains. And even with the same set of validators and parachains, the validators' assignments to parachains is flexible. This means that the architecture proposed in the next chapters must deal with the variability and multiplicity of the network state.

[TODO Diagram: Forkfulness]

## Secondary Checking

[TODO]

## Validator Assignment Process

[TODO]

## Collation Distribution Process

[TODO]

## Candidate Backing Process

[TODO]

## Availability Distribution Process

[TODO]

## Glossary

Here you can find definitions of a bunch of jargon, usually specific to the Polkadot project.

- BABE: (Blind Assignment for Blockchain Extension). The algorithm validators use to safely extend the Relay Chain. See [the Polkadot wiki][0] for more information.
- Backed Candidate: A Parachain Candidate which is backed by a majority of validators assigned to a given parachain.
- Backing: A set of statements proving that a Parachain Candidate is backed.
- Collator: A node who generates Proofs-of-Validity (PoV) for blocks of a specific parachain.
- GRANDPA: (Ghost-based Recursive ANcestor Deriving Prefix Agreement). The algorithm validators use to guarantee finality of the Relay Chain.
- Node: A participant in the Polkadot network, who follows the protocols of communication and connection to other nodes. Nodes form a peer-to-peer network topology without a central authority.
- Parachain Candidate, or Candidate: A proposed block for inclusion into a parachain.
- Parablock: A block in a parachain.
- Parachain: A constituent chain secured by the Relay Chain's validators.
- Parachain Validators: A subset of validators assigned during a period of time to back candidates for a specific parachain
- Parathread: A parachain which is scheduled on a pay-as-you-go basis.
- Proof-of-Validity: A stateless-client proof that a parachain block is valid, with respect to some validation function.
- Runtime: The relay-chain state machine.
- Secondary Checker: A validator who has been randomly selected to perform secondary checks on a parablock which is pending approval.
- Validator: Specially-selected node in the network who is responsible for validating parachain blocks and issuing attestations about their validity.
- Validation Function: A piece of Wasm code that describes the state-transition function of a parachain.


## Index

- Polkadot Wiki on Consensus: https://wiki.polkadot.network/docs/en/learn-consensus
- Polkadot Runtime Spec: https://github.com/w3f/polkadot-spec/tree/spec-rt-anv-vrf-gen-and-announcement/runtime-spec

[0]: https://wiki.polkadot.network/docs/en/learn-consensus
[1]: https://github.com/w3f/polkadot-spec/tree/spec-rt-anv-vrf-gen-and-announcement/runtime-spec 