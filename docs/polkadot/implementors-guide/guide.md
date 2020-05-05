## The Polkadot Parachain Host Implementers' Guide

## Ramble / Preamble

This document aims to describe the purpose, functionality, and implementation of a host for Polkadot's _parachains_. It is not for the implementor of a specific parachain but rather for the implementor of the Parachain Host, which provides security and advancement for constituent parachains. In practice, this is for the implementors of the Relay Chain. 

There are a number of other documents describing the research in more detail. All referenced documents will be linked here and should be read alongside this document for the best understanding of the full picture. However, this is the only document which aims to describe key aspects of Polkadot's particular instantiation of much of that research down to low-level technical details and software architecture.

## Table of Contents
* [Origins](#Origins)
* [Parachains: Basic Functionality](#Parachains-Basic-Functionality)
* [Architecture](#Architecture)
  * [Node-side](#Architecture-Node-side)
  * [Runtime](#Architecture-Runtime)
* [Processes](#Processes)
  * [Overseer](#Overseer-Process)
  * [Candidate Backing](#Candidate-Backing)
* [Data Structures and Formats](#Data-Structures-and-Formats)
* [Glossary / Jargon](#Glossary)


## Origins

Parachains are the solution to a problem. As with any solution, it cannot be understood without first understanding the problem. So let's start by going over the issues faced by blockchain technology that let to us beginning to explore the design space for something like parachains.

#### Issue 1: Scalability

It became clear a few years ago that the transaction throughput of simple Proof-of-Work (PoW) blockchains such as Bitcoin, Ethereum, and myriad others was simply too low. [TODO: PoS, sharding, what if there were more blockchains, etc. etc.]

Proof-of-Stake (PoS) systems can accomplish higher throughput than PoW blockchains. PoS systems are secured by bonded capital as opposed to spent effort - liquidity opportunity cost vs. burning electricity. The way they work is by selecting a set of validators with known economic identity who lock up tokens in exchange for earning the right to "validate" or participate in the consensus process. If they are found to carry out that process wrongly, their tokens will be burned. This provides a strong disincentive in the direction of misbehavior.

Since the consensus protocol doesn't revolve around wasting effort, block times and agreement can occur much faster. Solutions to PoW challenges don't have to be found before a block can be authored, so the overhead of authoring a block is reduced to only the costs of creating and distributing the block.

However, consensus on a PoS chain requires full agreement of 2/3+ of the validator set for everything that occurs at Layer 1: all logic which is carried out as part of the blockchain's state machine. This means that everybody still needs to check everything.

Parachains are an example of a **sharded** protocol. Sharding is a concept borrowed from traditional database architecture. Rather than requiring every participant to check every transaction, we require each participant to check some subset of transactions, with enough redundancy baked in that byzantine (arbitrarily malicious) participants can't sneak in invalid transactions - at least not without being detected and getting slashed, with those transactions reverted.

Sharding and Proof-of-Stake in coordination with each other allow a parachain host to provide full security on many parachains, even without all participants checking all state transitions.

[TODO: note about network effects & bridging]

#### Issue 2: Flexibility / Specialization

"dumb" VMs don't give you the flexibility. Any engineer knows that being able to specialize on a problem and create coarser-grained operations gives them and their users more _leverage_.  [TODO]


Having recognized these issues, we set out to find a solution to these problems, which could allow developers to create and deploy purpose-built blockchains unified under a common source of security, with the capability of message-passing between them; a _heterogeneous sharding solution_, which we have come to know as **Parachains**.


----

## Parachains: Basic Functionality

This section aims to describe, at a high level, the architecture, actors, and processes involved in the implementation of parachains. It also illuminates certain subtleties and challenges faces in the design and implementation of those processes. Our goal is to carry a parachain block from authoring to secure inclusion, and define a process which can be carried out repeatedly and in parallel for many different parachains to extend them over time. Understanding of the high-level approach taken here is important to provide context for the proposed architecture further on.

First, it's important to go over the main actors we have involved in the Polkadot network.
1. Validators. These nodes are responsible for validating proposed parachain blocks. They do so by checking a Proof-of-Validity (PoV) of the block and ensuring that the PoV remains available. They put financial capital down as "skin in the game" which can be revoked if they are proven to have misvalidated.
2. Collators. These nodes are responsible for creating the Proofs-of-Validity that validators know how to check. Creating a PoV typically requires familiarity with the transaction format and block authoring rules of the parachain, as well as having access to the full state of the parachain.
3. Fishermen. These are user-operated, permissionless nodes whose goal is to catch out misbehaving validators in exchange for a bounty. Collators and validators can behave as Fishermen too. Fishermen aren't necessary for security, and aren't covered in-depth by this document.

This alludes to a simple pipeline where collators send validators parachain blocks and their requisite PoV to check. Then, validators validate the block using the PoV, signing statements which describe either the positive or negative outcome, and with enough positive statements, the block can be included. If another validator later detects that a validator or group of validators incorrectly signed a statement claiming a block was valid, then those validators will be _slashed_, with the checker receiving a bounty.

However, there is a problem with this formulation. In order for another validator to check the previous group of validators' work after the fact, the PoV must remain _available_ so the other validator can fetch it in order to check the work. The PoVs are expected to be too large to include in the blockchain directly, so we require an alternate _data availability_ scheme which requires validators to prove that the inputs to their work will remain available, and so their work can be checked.

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

This brings us to the second part of the process. Once a parablock is "fully included", it is still "pending approval". At this stage in the pipeline, the parablock has been backed by a majority of validators in the group assigned to that parachain, and its data has been guaranteed available by the set of validators as a whole. However, the validators in the parachain-group (known as the "Parachain Validators" for that parachain) are sampled from a validator set which contains some proportion of byzantine, or arbitrarily malicious members. This implies that the Parachain Validators for some parachain may be majority-dishonest, which means that secondary checks must be done on the block before it can be considered approved. This is necessary only because the Parachain Validators for a given parachain are sampled from an overall validator set which is assumed to be up to <1/3 dishonest - meaning that there is a chance to randomly sample Parachain Validators for a parachain that are majority or fully dishonest and can back a candidate wrongly. The Approval Process allows us to detect such misbehavior after-the-fact without allocating more Parachain Validators and reducing the throughput of the system.

The Approval Process looks like this:
1. Parablocks that have been included by the Inclusion Pipeline are pending approval for a time-window known as the secondary checking window.
1. During the secondary-checking window, validators randomly self-select to perform secondary checks on the parablock.
1. These validators, known in this context as secondary checkers, acquire the parablock and its PoV, and re-run the validation function.
1. The secondary checkers submit the result of their checks to the relay chain. Contradictory results lead to escalation, where even more secondary checkers are selected and the secondary-checking window is extended.
1. At the end of the Approval Process, the parablock is either Approved or it is rejected. More on the rejection process later.

These two pipelines sum up the sequence of events necessary to extend and acquire full security on a Parablock. Note that the Inclusion Pipeline must conclude for a specific parachain before a new block can be accepted on that parachain. After inclusion, the Approval Process kicks off, and can be running for many parachain blocks at once.

[TODO Diagram: Inclusion Pipeline & Approval Processes interaction]

It is also important to take note of the fact that the relay-chain is extended by BABE, which is a forkful algorithm. That means that different block authors can be chosen at the same time, and may not be building on the same block parent. Furthermore, the set of validators is not fixed, nor is the set of parachains. And even with the same set of validators and parachains, the validators' assignments to parachains is flexible. This means that the architecture proposed in the next chapters must deal with the variability and multiplicity of the network state.

[TODO Diagram: Forkfulness]

----

## Architecture

Our Parachain Host is a blockchain. A blockchain is a Directed Acyclic Graph (DAG) of state transitions, where every block can be considered to be the head of a linked-list (known as a "chain" or "fork") with a cumulative state which is determined by applying the state transition of each block in turn. All paths through the DAG terminate at the Genesis Block.

[TODO Diagram: Blockchain / Block-DAG]

A blockchain network is comprised of nodes. These nodes each have a view of many different forks of a blockchain and must decide which forks to follow and what actions to take based on the forks of the chain that they are aware of.

So in specifying an architecture to carry out the functionality of a Parachain Host, we have to answer two categories of questions:
1. What is the state-transition function of the blockchain? What is necessary for a transition to be considered valid, and what information is carried within the implicit state of a block?
2. Being aware of various forks of the blockchain as well as global private state such as a view of the current time, what behaviors should a node undertake? What information should a node extract from the state of which forks, and how should that information be used?

The first category of questions will be addressed by the Runtime, which defines the state-transition logic of the chain. Runtime logic only has to focus on the perspective of one chain, as each state has only a single parent state.

The second category of questions addressed by Node-side behavior. Node-side behavior defines all activities that a node undertakes, given its view of the blockchain/block-DAG. Node-side behavior can take into account all or many of the forks of the blockchain, and only conditionally undertake certain activities based on which forks it is aware of, as well as the state of the head of those forks.

[TODO Diagram: Runtime vs. Node-side]

It is also helpful to divide Node-side behavior into two further categories: Networking and Core. Networking behaviors relate to how information is distributed between nodes. Core behaviors relate to internal work that a specific node does. These two categories of behavior often interact, but can be heavily abstracted from each other. Core behaviors care that information is distributed and received, but not the internal details of how distribution and receipt function. Networking behaviors act on requests for distribution or fetching of information, but are not concerned with how the information is used afterwards. This allows us to create clean boundaries between Core and Networking activities, improving the modularity of the code.

[TODO Diagram: Node-side divided into Networking and Core]

Node-side behavior is split up into various Processes. These processes may be long-running or short-lived. They may communicate with each other.

Runtime logic is divided up into Modules and APIs. Modules encapsulate particular behavior of the system. Modules consist of storage, routines, and entry-points. Routines are invoked by entry points, by other modules, upon block initialization or closing. Routines can read and alter the storage of the module. Entry-points are the means by which new information is introduced to a module. Each block in the blockchain contains a set of Extrinsics. Each extrinsic targets a a specific entry point to trigger and which data should be passed to it. Runtime APIs provide a means for Node-side behavior to extract meaningful information from the state of a fork.

These two aspects of the implementation are heavily dependent on each other. The Runtime depends on Node-side behavior to author blocks, and to include Extrinsics which trigger the correct entry points. The Node-side behavior relies on Runtime APIs to extract information necessary to determine which actions to take.

### Architecture: Node-side

**Design Goals**

* Modularity: Components of the system should be as self-contained as possible. Communication boundaries between components should be well-defined and mockable. This is key to creating testable, easily reviewable code.
* [TODO] anything else?

[TODO]

### Architecture: Runtime

[TODO]

----

## Processes


### Overseer Process

This process oversees the scheduling of, communication between, and teardown of other sub-processes.
Most new work for validators to do is scheduled upon the import of a new block. This is the component that listens to block import events and schedules work to be done. At the same time, it can also decide that other work has become obsolete and should be unscheduled.

```
+--------------+      +------------------+    +------------------+    
|              |      |                  |----> Subprocess A     |    
| Block Import |      |                  |    +------------------+    
|    Events    |------+   Overseer       |    +------------------+    
+--------------+      |                  |----> Subprocess B     |    
                      |                  |    +------------------+    
+--------------+      |                  |    +------------------+    
|              |      |   Process        |----> Subprocess C     |    
| Finalization |------+                  |    +------------------+    
|    Events    |      |                  |---->------------------+    
+--------------+      +------------------+    | Subprocess D     |    
                                              +------------------+    
```

[TODO: specific conditions under which new processes are created]
---

### Candidate Backing Process

The Candidate Backing Process is the process that a validator engages in to contribute to the backing of parachain candidates submitted by other validators.

Many instances of this process may be live at the same time. Each instance is scoped to a particular relay-chain block, known contextually as the _relay parent_.

The goal of the Candidate Backing Process is to produce as many backed candidates as possible. This is done via signed [Statements](#Statement-type) by validators. If a candidate receives a majority of supporting Statements from the Parachain Validators currently assigned, then that candidate is considered backed.

The Candidate Backing Process is straightforward and consists of 3 tasks:
* Fetching new Statements about candidates from a network interface
* Performing work based on those Statements. Either validating new candidates that the process was previously unaware of, keeping track of which candidates have received backing, or submitting misbehavior reports.
* Issuing new Statements based on work done.

In order to carry out its operations, this process depends on input parameters. In practice, this will be fetched from the state of the relay parent using Runtime APIs.

**Parameters**
* The current Validator set.
* Validator -> Parachain Assignments
* Local Key - the current node' validation key, if any.
* Local Assignment - the parachain the current node is assigned to, as a validator.
* Local Assignment parachain head - what to treat as the head of the parachain
* Local Assignment parachain code - the validation function of the parachain
* Network - a mockable interface for receiving and submitting signed statements about candidates.

If the local key is not present or there is no local assignment, the candidate process will run in an observer mode where it will witness candidates that other validators backs without participating in the process itself.

**Operation**

Pseudocode:
```rust
loop {
  let signed: SignedStatement = network_statements.next()?;
  if let Statement::Seconded(candidate) = signed.statement {
    if candidate is unknown and in local assignment {
      spawn_validation_work(candidate);
    }
  }

  // Track which candidates are now backed and watch out for double-voting misbehavior.
  track_statement(signed);
}
```

```rust
fn spawn_validation_work(candidate) {
  asynchronously {
    let pov = network.fetch_pov(candidate).await;
    let valid = validate_candidate(candidate, validation_function, parachain_head, pov);
    if valid {
      // make PoV available for later distribution.
      // sign and dispatch `valid` statement to network.
    } else {
      // sign and dispatch `invalid` statement to network.
    }
  }
}
```

[TODO: how to dispatch `Seconded` message. Kind of hard - note that dispatching a `Seconded` and `Valid` message is illegal so this is racy]

### Candidate Proposal Process

[TODO: get candidate from collator, feed to candidate backing process. ]

### Secondary Checking

[TODO]

### Validator Assignment Process

[TODO]

### Collation Distribution Process

[TODO]

### Availability Distribution Process

[TODO]

----

## Data Structures and Types

[TODO]
* CandidateReceipt
* CandidateCommitments
* AbridgedCandidateReceipt
* GlobalValidationSchedule
* LocalValidationData

#### Block Import Event
```rust
/// Indicates that a new block has been added to the blockchain.
struct BlockImportEvent {
  /// The block header-hash.
  hash: Hash,
  /// The header itself.
  header: Header,
  /// Whether this block is considered the head of the best chain according to the 
  /// event emitter's fork-choice rule.
  new_best: bool,
}
```

#### Block Finalization Event
```rust
/// Indicates that a new block has been finalized.
struct BlockFinalizationEvent {
  /// The block header-hash.
  hash: Hash,
  /// The header of the finalized block.
  header: Header,
}
```

#### Statement Type
```rust
/// A statement about the validity of a parachain candidate.
enum Statement {
  /// A statement about a new candidate.
  Seconded(CandidateReceipt),
  /// A statement about the validity of a candidate, based on candidate's hash.
  Valid(Hash),
  /// A statement about the invalidity of a candidate.
  Invalid(Hash),
}
```

#### Signed Statement Type

This is a signed statement. The actual signed payload should reference only the hash of the CandidateReceipt and should include
a relay parent which provides context to the signature. This prevents against replay attacks and allows the candidate receipt itself
to be omitted when checking a signature on a `Seconded` statement.

```rust
/// A signed statement.
struct SignedStatement {
  statement: Statement,
  signed: ValidatorId,
  signature: Signature
}
```

----

## Glossary

Here you can find definitions of a bunch of jargon, usually specific to the Polkadot project.

- BABE: (Blind Assignment for Blockchain Extension). The algorithm validators use to safely extend the Relay Chain. See [the Polkadot wiki][0] for more information.
- Backed Candidate: A Parachain Candidate which is backed by a majority of validators assigned to a given parachain.
- Backing: A set of statements proving that a Parachain Candidate is backed.
- Collator: A node who generates Proofs-of-Validity (PoV) for blocks of a specific parachain.
- Extrinsic: An element of a relay-chain block which triggers a specific entry-point of a runtime module with given arguments. 
- GRANDPA: (Ghost-based Recursive ANcestor Deriving Prefix Agreement). The algorithm validators use to guarantee finality of the Relay Chain.
- Inclusion Pipeline: The set of steps taken to carry a Parachain Candidate from authoring, to backing, to availability and full inclusion in an active fork of its parachain.
- Module: A component of the Runtime logic, encapsulating storage, routines, and entry-points.
- Module Entry Point: A recipient of new information presented to the Runtime. This may trigger routines.
- Module Routine: A piece of code executed within a module by block initialization, closing, or upon an entry point being triggered. This may execute computation, and read or write storage.
- Node: A participant in the Polkadot network, who follows the protocols of communication and connection to other nodes. Nodes form a peer-to-peer network topology without a central authority.
- Parachain Candidate, or Candidate: A proposed block for inclusion into a parachain.
- Parablock: A block in a parachain.
- Parachain: A constituent chain secured by the Relay Chain's validators.
- Parachain Validators: A subset of validators assigned during a period of time to back candidates for a specific parachain
- Parathread: A parachain which is scheduled on a pay-as-you-go basis.
- Proof-of-Validity: A stateless-client proof that a parachain block is valid, with respect to some validation function.
- Runtime: The relay-chain state machine.
- Runtime Module: See Module.
- Runtime API: A means for the node-side behavior to access structured information based on the state of a fork of the blockchain.
- Secondary Checker: A validator who has been randomly selected to perform secondary checks on a parablock which is pending approval.
- Validator: Specially-selected node in the network who is responsible for validating parachain blocks and issuing attestations about their validity.
- Validation Function: A piece of Wasm code that describes the state-transition function of a parachain.


## Index

- Polkadot Wiki on Consensus: https://wiki.polkadot.network/docs/en/learn-consensus
- Polkadot Runtime Spec: https://github.com/w3f/polkadot-spec/tree/spec-rt-anv-vrf-gen-and-announcement/runtime-spec

[0]: https://wiki.polkadot.network/docs/en/learn-consensus
[1]: https://github.com/w3f/polkadot-spec/tree/spec-rt-anv-vrf-gen-and-announcement/runtime-spec 