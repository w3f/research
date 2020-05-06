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
* [Data Structures and Types](#Data-Structures-and-Types)
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

However, there is a problem with this formulation. In order for another validator to check the previous group of validators' work after the fact, the PoV must remain _available_ so the other validator can fetch it in order to check the work. The PoVs are expected to be too large to include in the blockchain directly, so we require an alternate _data availability_ scheme which requires validators to prove that the inputs to their work will remain available, and so their work can be checked. Empirical tests tell us that many PoVs may be between 1 and 10MB during periods of heavy load.

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
  - The collator is not able to propagate the candidate to any validators assigned to the parachain.
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

Node-side behavior is split up into various Processes. Processes are long-lived workers that perform a particular category of work. Processes can communicate with each other, and typically do so via an Overseer that prevents race conditions.

Runtime logic is divided up into Modules and APIs. Modules encapsulate particular behavior of the system. Modules consist of storage, routines, and entry-points. Routines are invoked by entry points, by other modules, upon block initialization or closing. Routines can read and alter the storage of the module. Entry-points are the means by which new information is introduced to a module. Each block in the blockchain contains a set of Extrinsics. Each extrinsic targets a a specific entry point to trigger and which data should be passed to it. Runtime APIs provide a means for Node-side behavior to extract meaningful information from the state of a fork.

These two aspects of the implementation are heavily dependent on each other. The Runtime depends on Node-side behavior to author blocks, and to include Extrinsics which trigger the correct entry points. The Node-side behavior relies on Runtime APIs to extract information necessary to determine which actions to take.

### Architecture: Node-side

**Design Goals**

* Modularity: Components of the system should be as self-contained as possible. Communication boundaries between components should be well-defined and mockable. This is key to creating testable, easily reviewable code.
* Minimizing side effects: Components of the system should aim to minimize side effects and to communicate with other components via message-passing.
* Operational Safety: The software will be managing signing keys where conflicting messages can lead to large amounts of value to be slashed. Care should be taken to ensure that no messages are signed incorrectly or in conflict with each other.

The architecture of the node-side behavior aims to embody the Rust principles of ownership and message-passing to create clean, isolatable code. Each resource should have a single owner, with minimal sharing where unavoidable.

Many operations that need to be carried out involve the network, which is asynchronous. This asynchrony affects all core processes that rely on the network as well. The approach of hierarchical state machines is well-suited to this kind of environment.

We introduce a hierarchy of state machines consisting of an overseer supervising processes, where processes can contain their own internal hierarchy of jobs. This is elaborated on in the [Processes](#Processes) section.

---

### Architecture: Runtime

The best architecture at this time is unclear. Let's start by setting down the requirements of the runtime and then trying to come up with an architecture that encompasses all of them.

There are three key points during the execution of a block that we are generally interested in:
  * initialization: beginning the block and doing set up works. Runtime APIs draw information from the state directly after initialization.
  * inclusion of new parachain information
  * finalization: final checks and clean-up work before completing the block.

In order to import parachains, handle misbehavior reports, and keep data accessible, we need to keep this data in the storage/state:
  * All currently registered parachains.
  * All currently registered parathreads.
  * The head of each registered para.
  * The validation code of each registered para.
  * Historical validation code for each registered para.
  * Historical, but not yet expired validation code for paras that were previously registered but are now not. (old code must remain available so secondary checkers can check after-the-fact yadda yadda in this case we do that by keeping it in the runtime state.)
  * Configuration: number of parathread cores, number of parachain slots. Length of scheduled parathread "lookahead". Length of parachain slashing period. How long to keep old validation code for. etc.

This information should not change at any point between block initialization and inclusion of new parachain information. The reason for that is that the inclusoin of new parachain information will be checked against these values in the storage, but the new parachain information is produced by Node-side processes which draw information from Runtime APIs. Runtime APIs execute on top of the state directly after the initialization, so a divergence from that state would lead to validators producing unacceptable inputs.

In the Substrate implementation, we may also have to worry about state changing due to other modules invoking `Call`s that change storage during initialization, but after the point at which parachain-specific modules run their initialization procedures. This could cause problems: parachain-specific modules could compute scheduling, parachain assignments, etc. during its initialization procedure, which would then become inconsistent afterwards. Other modules that might realistically cause such race conditions are Governance modules (which execute arbitrary `Call`s, or the `Scheduler` module). This implies that the runtime design should ensure that no racy entry points can affect storage that is used during parachain-specific module initialization. One way to accomplish this is to separate active storage items from pending storage updates. Other modules can add pending updates, but only the initialization or finalization logic can apply those to the active state. (of course, governance can reach in and break anything by mangling storage, but this is more about exposing a preventative API than a bulletproof one). One alternative is to ensure that all configuration is presented only as constants, which requires a full runtime upgrade to alter and as such does not suffer from these race conditions.

Here is an attempted-exhaustive list of tasks the runtime is expected to carry out in each phase.

initialization:
  * determine scheduled parachains and parathreads for the upcoming block or blocks.
  * determine validator assignments to scheduled paras for the upcoming block or blocks.

parachain inputs:
  * TODO


----

## Processes

### Processes and Jobs

In this section we define the notions of Processes and Jobs. These are guidelines for how we will employ an architecture of hierarchical state machines. We'll have a top-level state machine which oversees the next level of state machines which oversee another layer of state machines and so on. The next sections will lay out these guidelines for what we've called Processes and Jobs, since this model applies to many of the tasks that the Node-side behavior needs to encompass, but these are only guidelines and some processes may have deeper hierarchies internally.

Processes are long-lived worker tasks that are in charge of performing some particular kind of work. All processes can communicate with each other via a well-defined protocol. Processes can't communicate directly, but must communicate through an Overseer, which is responsible for relaying messages, handling process failures, and dispatching work signals.

Most work that happens on the Node-side is related to building on top of a specific relay-chain block, which is contextually known as the "relay parent". We call it the relay parent to explicitly denote that it is a block in the relay chain and not on a parachain. We refer to the parent because when we are in the process of building a new block, we don't know what that new block is going to be. The parent block is our only stable point of reference, even though it is usually only useful when it is not yet a parent but in fact a leaf of the block-DAG expected to soon become a parent (because validators are authoring on top of it). Furthermore, we are assuming a forkful blockchain-extension protocol, which means that there may be multiple possible children of the relay-parent. Even if the relay parent has multiple children blocks, the parent of those children is the same, and the context in which those children is authored should be the same. The parent block is the best and most stable reference to use for defining the scope of work items and messages, and is typically referred to by its cryptographic hash.

Since this goal of determining when to start and conclude work relative to a specific relay-parent is common to most, if not all processes, it is logically the job of the Overseer to distribute those signals as opposed to each process duplicating that effort, potentially being out of synchronization with each other. Process A should be able to expect that Process B is working on the same relay-parents as it is. One of the Overseer's tasks is to provide this heartbeat, or synchronized rhythm, to the system.

The work that Processes spawn to be done on a specific relay-parent is known as a job. Processes should set up and tear down jobs according to the signals received from the overseer. Processes may share or cache state between jobs.

### Overseer

The overseer is responsible for these tasks:
1. Setting up, monitoring, and handing failure for overseen processes.
2. Providing a "heartbeat" of which relay-parents processes should be working on.
3. Acting as a message bus between processes.


The hierarchy of processes:
```
+--------------+      +------------------+    +------------------+    
|              |      |                  |---->   Process A      |    
| Block Import |      |                  |    +------------------+    
|    Events    |------>                  |    +------------------+    
+--------------+      |                  |---->   Process B      |    
                      |   Overseer       |    +------------------+    
+--------------+      |                  |    +------------------+    
|              |      |                  |---->   Process C      |    
| Finalization |------>                  |    +------------------+    
|    Events    |      |                  |    +------------------+
|              |      |                  |---->   Process D      |
+--------------+      +------------------+    +------------------+   
                                                  
```

The overseer determines work to do based on block import events and block finalization events (TODO: are finalization events needed?). It does this by keeping track of the set of relay-parents for which work is currently being done. This is known as the "active leaves" set. It determines an initial set of active leaves on startup based on the data on-disk, and uses events about blockchain import to update the active leaves. Updates lead to `OverseerSignal::StartWork` and `OverseerSignal::StopWork` being sent according to new relay-parents, as well as relay-parents to stop considering.

The overseer's logic can be described with these functions:

*On Startup*
* Start all Processes
* Determine all blocks of the blockchain that should be built on. This should typically be the head of the best fork of the chain we are aware of. Sometimes add recent forks as well.
* For each of these blocks, send an `OverseerSignal::StartWork` to all processes.
* Begin listening for block import events.

*On Block Import Event*
* Apply the block import event to the active leaves. A new block should lead to its addition to the active leaves set and its parent being deactivated.
* For any deactivated leaves send an `OverseerSignal::StopWork` message to all processes.
* For any activated leaves send an `OverseerSignal::StartWork` message to all processes.

(TODO: in the future, we may want to avoid building on too many sibling blocks at once. the notion of a "preferred head" among many competing sibling blocks would imply changes in our "active set" update rules here)

*On Message Send Failure*
* If sending a message to a process fails, that process should be restarted and the error logged.


When a process wants to communicate with another process, or, more typically, a job within a process wants to communicate with its counterpart under another process, that communication must happen via the overseer. Consider this example where a job on Process A wants to send a message to its counterpart under Process B. This is a realistic scenario, where you can imagine that both jobs correspond to work under the same relay-parent.

```                                  
     +--------+                                                           +--------+      
     |        |                                                           |        |      
     |Job A-1 | (sends message)                       (receives message)  |Job B-1 | 
     |        |                                                           |        |      
     +----|---+                                                           +----^---+      
          |                  +------------------------------+                  ^          
          v                  |                              |                  |          
+---------v---------+        |                              |        +---------|---------+
|                   |        |                              |        |                   |
| Process A         |        |       Overseer / Message     |        | Process B         |
|                   -------->>                  Bus         -------->>                   |
|                   |        |                              |        |                   |
+-------------------+        |                              |        +-------------------+
                             |                              |                             
                             +------------------------------+                             
```

This communication prevents a certain class of race conditions. When the Overseer determines that it is time for processes to begin working on top of a particular relay-parent, it will dispatch a `StartWork` message to all processes to do so, and those messages will be handled asynchronously by those processes. Some processes will receive those messsages before others, and it is important that a message sent by Process A after receiving `StartWork` message will arrive at Process B after its `StartWork` message. If Process A maintaned an independent channel with Process B to communicate, it would be possible for Process B to handle the side message before the `StartWork` message, but it wouldn't have any logical course of action to take with the side message - leading to it being discarded or improperly handled. Well-architectured state machines should have a single source of inputs, so that is what we do here.

It's important to note that the overseer is not aware of the internals of processes, and this extends to the jobs that they spawn. The overseer isn't aware of the existence or definition of those jobs, and is only aware of the outer processes with which it interacts. This gives process implementations leeway to define internal jobs as they see fit, and to wrap a more complex hierarchy of state machines than having a single layer of jobs for relay-parent-based work.

Futhermore, the protocols by which processes communicate with each other should be well-defined irrespective of the implementation of the process. In other words, their interface should be distinct from their implementation. This will prevent processes from accessing aspects of each other that are beyond the scope of the communication boundary.

---

### Candidate Backing Process

#### Description

The Candidate Backing Process is the process that a validator engages in to contribute to the backing of parachain candidates submitted by other validators.

Its role is to produce backed candidates for inclusion in new relay-chain blocks. It does so by issuing signed [Statements](#Statement-type) and tracking received statements signed by other validators. Once enough statements are received, they can be combined into backing for specific candidates.

It also detects double-vote misbehavior by validators as it imports votes, passing on the misbehavior to the correct reporter and handler.

When run as a validator, this is the process which actually validates incoming candidates.

#### Protocol

This process receives messages of the type [CandidateBackingProcessMessage](#Candidate-Backing-Process-Message).

#### Functionality

The process should maintain a set of handles to Candidate Backing Jobs that are currently live, as well as the relay-parent to which they correspond.

*On Overseer Signal*
* If the signal is an `OverseerSignal::StartWork(relay_parent)`, spawn a Candidate Backing Job with the given relay parent, storing a bidirectional channel with the Candidate Backing Job in the set of handles.
* If the signal is an `OverseerSignal::StopWork(relay_parent)`, cease the Candidate Backing Job under that relay parent, if any.

*On CandidateBackingProcessMessage*
* If the message corresponds to a particular relay-parent, forward the message to the Candidate Backing Job for that relay-parent, if any is live.


(big TODO: "contextual execution"
* At the moment we only allow inclusion of _new_ parachain candidates validated by _current_ validators.
* Allow inclusion of _old_ parachain candidates validated by _current_ validators.
* Allow inclusion of _old_ parachain candidates validated by _old_ validators.

This will probably blur the lines between jobs, will probably require inter-job communcation and a short-term memory of recently backed, but not included candidates.
)

#### Candidate Backing Job

The Candidate Backing Job represents the work a node does for backing candidates with respect to a particular relay-parent.

The goal of a Candidate Backing Job is to produce as many backed candidates as possible. This is done via signed [Statements](#Statement-type) by validators. If a candidate receives a majority of supporting Statements from the Parachain Validators currently assigned, then that candidate is considered backed.

*on startup*
* Fetch current validator set, validator -> parachain assignments from runtime API.
* Determine if the node controls a key in the current validator set. Call this the local key if so.
* If the local key exists, extract the parachain head and validation function for the parachain the local key is assigned to.

*on receiving new signed Statement*
```rust
if let Statement::Seconded(candidate) = signed.statement {
  if candidate is unknown and in local assignment {
    spawn_validation_work(candidate, parachain head, validation function)
  }
}
```

*spawning validation work*
```rust
fn spawn_validation_work(candidate, parachain head, validation function) {
  asynchronously {
    let pov = (fetch pov block).await

    // dispatched to sub-process (OS process) pool.
    let valid = validate_candidate(candidate, validation function, parachain head, pov).await;
    if valid {
      // make PoV available for later distribution.
      // sign and dispatch `valid` statement to network if we have not seconded the given candidate.
    } else {
      // sign and dispatch `invalid` statement to network.
    }
  }
}
```

*fetch pov block*

Create a `(sender, receiver)` pair.
Dispatch a `PovFetchProcessMessage(relay_parent, candidate_hash, sender)` and listen on the receiver for a response.

*on receiving CandidateBackingProcessMessage*
* If the message is a `CandidateBackingProcessMessage::RegisterBackingWatcher`, register the watcher and trigger it each time a new candidate is backed. Also trigger it once initially if there are any backed candidates at the time of receipt.
* If the message is a `CandidateBackingProcessMessage::Second`, sign and dispatch a `Seconded` statement only if we have not seconded any other candidate and have not signed a `Valid` statement for the requested candidate. Signing both a `Seconded` and `Valid` message is a double-voting misbehavior with a heavy penalty, and this could occur if another validator has seconded the same candidate and we've received their message before the internal seconding request.

(TODO: send statements to Statement Distribution Process, handle shutdown signal from parent process)

---

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


#### Overseer Signal

Signals from the overseer to a process.

```rust
enum OverseerSignal {
  /// Signal to start work localized to the relay-parent hash H.
  StartWork(H),
  /// Signal to stop (or phase down) work localized to the relay-parent hash H.
  StopWork(H),
}
```


#### Candidate Backing Process Message

```rust
enum CandidateBackingProcessMessage {
  /// Registers a stream listener for updates to the set of backed candidates that could be included
  /// in a child of the given relay-parent, referenced by its hash H
  RegisterBackingWatcher(H, TODO),
  /// Note that the Candidate Backing Process should second the given candidate in the context of the 
  /// given relay-parent (ref. by hash H). This candidate must be validated.
  Second(H, CandidateReceipt)
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
- Process: A long-running task which is responsible for carrying out a particular category of work.
- Proof-of-Validity (PoV): A stateless-client proof that a parachain candidate is valid, with respect to some validation function.
- Relay Parent: A block in the relay chain, referred to in a context where work is being done in the context of the state at this block.
- Runtime: The relay-chain state machine.
- Runtime Module: See Module.
- Runtime API: A means for the node-side behavior to access structured information based on the state of a fork of the blockchain.
- Secondary Checker: A validator who has been randomly selected to perform secondary checks on a parablock which is pending approval.
- Validator: Specially-selected node in the network who is responsible for validating parachain blocks and issuing attestations about their validity.
- Validation Function: A piece of Wasm code that describes the state-transition function of a parachain.

Also of use is the [Substrate Glossary](https://substrate.dev/docs/en/overview/glossary).

## Index

- Polkadot Wiki on Consensus: https://wiki.polkadot.network/docs/en/learn-consensus
- Polkadot Runtime Spec: https://github.com/w3f/polkadot-spec/tree/spec-rt-anv-vrf-gen-and-announcement/runtime-spec

[0]: https://wiki.polkadot.network/docs/en/learn-consensus
[1]: https://github.com/w3f/polkadot-spec/tree/spec-rt-anv-vrf-gen-and-announcement/runtime-spec 
