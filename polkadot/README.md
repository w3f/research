# Polkadot

*DRAFT*

Polkadot speaking in abstract terms provides a number of connected canonical state machines. Connected means that a state transition of one machine can affect a transition of another machine. The state machines are canonical, since they transition in a globally consistent manner. We would also like to enable adding, removing and changing of the state machines as the time goes on. This will be the role of the governance process.

The research focuses on how to enable having such publicly available system in the face of possible adversarial conditions. The public can use the system by interacting with state machines that they are interested in via the internet. Each state machine can provide different functionalities and behave in different ways (have a different state and state transition scheme).

So let us start with abstract state machines. A state machine has a certain state type and state transition type. As the time goes on, state transitions occur.

The data that determines the state transitions is structured as bundles of transactions - individual small state transitions triggered by the users of the system. Each bundle is called a block. In order to achieve its properties, ensures that those blocks are hash connected forming joint data structure.

## Specification of the Polkadot Runtime Environment

https://github.com/w3f/polkadot-re-spec

## Identifying actors to run the network

To identify unique individuals a 

https://github.com/w3f/research/tree/master/polkadot/keys

https://github.com/w3f/schnorrkel

[Sequential Phragmén Method](NPoS/phragmen.md)

## Ensuring state transition properties

### Usefulness

Each state transition should bring some utility to the system participants. In order to ensure that this is the case:

- state machines should be useful to participants
- state transitions processed by these state machines reflect well the state transition needs of participants.

To ensure that the state machines are useful we should ensure that there is a mechansim that enables participants to decide what state machines should be included and how they should change to reflect participant needs. This mechanism is the [Polkadot governance scheme](https://github.com/paritytech/polkadot/wiki/Governance).

To ensure that useful state transitions are processed by those state machines, we will want to ensure that useful transactions get included in Polkadot blocks. Polkadot will have a transaction fee mechanism on the relay chain to ensure that transactions issued by parties willing to pay a reasonable price for them are included. There will also be a certain portion of each block that is dedicated to certain high-priority transactions, such as misbehaviour reporting. The usefulness of the parachain state transitions has to be ensured by the state transition function of a given chain.

### Validity

The notion of validity in Polkadot is determined by a state transition validation function (STVF). Each chain in the ecosystem has to have one implemented. In order for all nodes to be able to run this function it is being distributed as deterministic WebAssembly (Wasm) code which can be executed by the Polkadot Runtime Environment.

The blocks are produced by parachain collators, then they get validated using the STVF by the subset of validators responsible for the given parachain to finally get included in the Polkadot Relay Chain. During this process validators, parachain collators and other parties are free to challenge claims of validity to trigger additional check, these parties are referred to as fishermen.

### Canonicality

[Finality gadget](https://github.com/w3f/consensus/blob/master/pdf/grandpa.pdf)

### Availability

[Availability scheme](availability.md)

## Ensuring reliable messaging between state machines

[ICMP scheme](ICMP.md)

## Keeping resource usage under control

### Reasonable size

In order to ensure that the state transitions can be processed and stored by the network their size has to be reasonable. Mechanisms such as transaction fees and block limits are there to limit the storage size and computation required for each block.

### Light client

The protocol is being designed with light client support in mind.

## Desired qualities

- Minimal: Polkadot should have as little functionality as possible.
- Simple: No additional complexity should be present in the base protocol.
- General: Polkadot can be optimized through making the model into which extensions fit as abstract as possible.
- Robust: Polkadot should provide a fundamentally stable base-layer.