# Networking for Polkadot

The two main networking protocols we require for Polkadot are for GRANDPA and Parachains/Interchain-message-passing. 

GRANDPA nodes want to distribute and receive valid messages about current rounds, without being DoS'ed by messages from an infinite number of possible future rounds _or_ being sent messages from all the rounds that have occurred but whose specific votes are not relevant to the software. Gossip networks are a good candidate for this, but the scope of messages that can be gossipped to a specific peer must be limited.

Parachain networking consists of the following goals (in no particular order):
  1. Distribution of candidate announcements (up to N) and attestation. Happens on every block. Nodes need to have means of processing messages only for blocks which they know actually exist and are not too old. At the very least, combined majority attestations from all parachain groups must be available to the block author, who belongs to only one group. Gossip is suitable for distribution of these statements, which are generally small. Here data is sent from validators to all other validators. Such type of routing is described below. 
  2. Distribution of proof-of-validation (PoV) data (up to N) to all parachain validators in a parachain validation group. This data is generally too large to be gossiped and so must be routed in a more targeted manner. Here data is sent from collators to parachain validators directly. 
  3. Distribution of erasure-coding chunks of the PoV + extrinsic data (egress) to all validators. (up to N^2 chunks per block). These are also generally large and should be distributed in a targeted manner. Here data is sent from parachain validators to all other validators.  
  4. Recovery of PoV + Extrinsic data by querying all validators (who have voted in Grandpa) for pieces of the erasure-coding. For now we can use gossiping, but eventually should also be done in a targeted manner. The recovery (which includes a request and a reply) is done by validators (which are a few) who are selected to check validity and availability and is sent to all validators. 
  5. Distribution of all unrouted egress queues to parachain collators. This is technically redundant with goal 4, but a fast path for following recent egress messages is desirable. Here data is sent from collators (or parachain validators?) of the sending parachain to the collator of the recipient parachain. The routing scheme is described below. This is difficult for a couple reasons:
      - Any full node may be a collator and thus the distribution method needs to be widespread
      - Pending egress may go arbitrarily far back.

## General gossip protocol methodology

Unlike traditional gossip protocols, where the number of nodes are known and known to be honest, we are dealing with a network in which non-staked nodes can participate and thus there are untrusted members in the network. Since there is a lack of a barrier-to-entry, an unbounded number of nodes may be controlled by the adversary.

However, we assume that there is a means for validators to discover one another and that honest validators are all at the very least transitively connected to each other in times of good network connectivity. (exluding all other nodes from the graph). In practice, this assumption is fulfilled by validators signing DHT entries about their network ID, for discoverability.

The primary category of DoS vectors we have to deal with are those relating to messages originating from dishonest validators. In most of the consensus protocols we deal with, there is an unbounded number of possible future consensus-protocol states. Attempting to hold onto and cache messages which are in the future relative to our view of consensus can be exploited, if done without limit.

This is why we design our gossip protocols (polite-grandpa, attestation gossip, and ICMP message queue gossip) in the following manner:
  - Nodes give their neighbors in the gossip graph (i.e. their peers) current information about what they will accept. These are called "neighbor updates". Neighbor updates are typically lightweight, as in a set of recent chain heads or a protocol round number.
  - Nodes are only allowed to send each other messages which should be accepted, according to the latest neighbor update they've received. Having received no neighbor update means no messages should be sent.
  - Nodes are expected to employ some method of peer-set cultivation, where peers that send them messages that they should have known not to are treated as less valuable than others. This will lead to a natural culling of spamming peers.

## Dealing with Attacks
Next, we review a number of relevant attacks and explain how we deal with them. In most cases, the attacks only have an overwhelming impact on Polkadots security if the attack is applied to a significant number of Polkadot nodes. Such attacks would be expensive. 

### Dealing with Delaying
Since we wont have a completely connected network, some honest communication needs to be routed through adverserial nodes. These adverserial nodes may delay everything they receive before forwarding it to the next node. Such an attack is very hard to detect in a decetralized setup, in particular if the forwarding delay is small at each adverserial node, but adds up to more than our thresholds in total. 

*What is the impact of the adversary manipulating the network delay for >f honest users?*

For Grandpa network delaying impacts only liveness. The adversary can halt Grandpa, but cannot impact safety. For BABE, network delays are more critical, the adversay could potentially gain a critical advantage.

For availability delaying can cause communication overhead since it will trigger the validators to ask for their erasure-coded pieces. 

For auctions, since it is very dependent on th security of BABE, delaying may cause problems too?Since we have random close, the problem is very minor here. 

Delaying, in smaller scale even, is a serious problem for bridging, in particular when the rate between DOT and the bridged chain token changes significantly.

### Dealing with Eclipsing

At the moment, we allow non-staked nodes to participate in our networking scheme, which gives us extra bandwidth and helps with traffic congestion. However, Sybil attacks are fairly easy to carry out. We can make it difficult for the adversary to carry out an eclipse attack in practice. The validator set is known to everyone and a validator can attempt to ensure it is directly connected to a large number (i.e.,>f) of other validators. For a small number of validators (<=200) it is probably feasible for all validators to connect to almost all others. If a validator is only connected directly to adverserial validators there is not much it can do. And while if the node is receiving no messages at all it gets alarmed about it, detecting whether the adverserial nodes are delaying communication or manipulating it is not possible. 

There are also some small suggestions by the literature to make eclipsing attacks more difficult such as having a limit on incoming connections in addition to the total incoming/outgoing connections limit. Some of these might be already taken into consideration? However, I read in a blog that not all of them are deployed. This is mainly because Ethereum is considered hard to attack from the networking point of view since it has large number of nodes. Paper (proposed countermeasures are in Section V):

https://www.cs.bu.edu/~goldbe/projects/eclipseEth.pdf

The combination of Kademlia (k-buckets prevent pushing out established peers) and peer-set cultivation (see below) based on cost/benefit of the peer should also serve as some degree of sybil protection. 

Note: There is also a paper suggesting countermeasures for bitcoins P2P, but I dont know how relevant that is. 

*What is the impact of eclipsing attack on different parts of Polkadot?* 

In Grandpa, if more than $f$ voters are eclipsed they will not be able to participate in Grandpa. Granpda will halt and those validators are punished. The primary is randomly selected, so eclipsing the primary is difficult and has insignificant impact. 

When more than $f$ block producers are eclipsed in BABE, the chain quality is harmed. Block producers are randomly selected, so eclipsing them is difficult. 

What happens if the bank (vault) or the bridge relay in the bridge protocol are eclipsed? 

When parachain validators are eclipsed, which is a small scale attack, the adversary can harm the parachain validators. For example, the adversary could only block all erasure-coded piece that are sent out and any request for them nd nothing more. In such an attack, the parachain validators will be slashed for not assuring availability. The only gain the adversary would make by this attack is forcing the replacement of the slashed parachain validator and hoping that the next randomly chosen parachain validator will be adverserial. But in that case DoS-ing that parachain validator might do the same job. This attack would be avoided if parachain validators could detect this, for example, by waiting for receipts back?

### Dealing with Dropped Traffic and Unresponsiveness
Generaly, dropping traffic only slows down things and is detected at some point. 

It is rather problematic when we are using targeted routing, where it can cause heavy communication overhead. For example, when we distribute erasure-coded pieces of parachain blocks are dropped. 

To deal with unresponsive peers we have a _peer-set cultivation scheme_ as follows. 
- A peer-set manager substrate/core/peerset acts as an intermediary between the discovery layer and the transport
- Protocols that use the transport (GRANDPA-gossip, sync, etc.) inform the peerset whenever a peer performs some action -- either that processing the peer's data has incurred a cost or resulted in a benefit. Perhaps both (we express as an i32)
- The peer-set manager algorithm amalgamates cost/benefit from all the protocols and attempts to filter out peers who are not providing high-benefit interaction. 

## Peer Discovery 

TODO: Description

For rotating parachain validators we need to figure out how node discovery will be done for new validator/collator connections.

The easiest way to make validators discoverable is to place their multiaddresses in either the chain state or the DHT.

