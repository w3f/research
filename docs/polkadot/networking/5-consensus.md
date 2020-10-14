====================================================================

**Authors**: Rob Habermeier, Fatemeh Shirazi

====================================================================

## Consensus broadcast

This document defines a _bounded_ gossip protocol for circulation of GRANDPA votes.

We have a number of entities:

- Authorities might be grandpa voters or block producers, but for now we assume they are the same.
- Participants are not voters or block producers and only follow Grandpa's progress

Authorities progress in rounds casting votes:

- For each round a new _round topic_ is created. That is a hash where the preimage includes round number.
- All votes for a round are categorized under the round topic.
- The expected number of messages under honest conditions on a round topic is: N_Authorities * 2 + 1.

Round message types:
- Prevote (max 2 per voter per round)
- Precommit (max 2 per voter per round)
- Primary-Broadcast (max 2 per round _from a single, known, per-round rotating voter_).

Although it says max 2 above, honest behavior of voters is to sign and send only one. However, we _must_ import and propagate both votes if we receive more than one. Once we have received 2 of a kind, we can ignore further ones -- GRANDPA vote-counting makes further double-votes irrelevant, but accounting for the first double-vote might be necessary to advance consensus.

This is because in GRANDPA equivocations are sometimes needed to complete a round, but a double-equivocation (i.e. triple-voting) is redundant. If an equivocation has occurred, it may lead to supermajority vote-weight on some block which is not possible to achieve through any other combination of issued votes. This means that if we witness an equivocation, we have to make sure our peers also see the equivocation to ensure they see the same result in the round that we do. Otherwise, that can cause a liveness fault. However, f+1 nodes equivocating can cause a safety fault, so this is behavior we want to disincentivize. Our current thinking is that isolated incidents of equivocation would be slashed very little, but the slashing amount would grow very fast with more equivocations happening in a short span of time.

Additionally, there's a _global topic_ for every voter set. Global topic is for commit messages and catch-up requests. Both these messages are not necessarily related to any specific round, but they are localized to a set of voters. Global topics provide that localization.
- For each completed round of GRANDPA within that voter set, zero or more messages are broadcast on this global topic.
- Messages in the global topic refer to a given round but are not necessary for completion of that round. Rather, messages in the global topic are more relevant to peers who are not interested in the details of how a round has proceeded, but instead are interested in what a particular voter-set has accomplished within its reign.

**Global message types**:
- Commit (localized to round. proves finality of a block). Format is `(round, target_number, target_hash, Vec<SignedPrecommit>)` where the precommits prove supermajority of the block with target hash and number.
- Catch-up replies: a collection of messages that allow a peer to be caught up to the point where the sender is _within the same voter set_. Should only be sent after receiving catch-up request.

Additionally, there are non-gossipped messages that give peers information about their neighbors in the graph.

**Neighbor messages:**
  - View Update: `(round, set_id, commit_height)`. Sent to all neighbors in the gossip graph periodically to inform of the current view of the protocol.
  - Catch-up request: if a neighbor sends a view that indicates it is at the same voter set, but significantly ahead in round ("significant" is meant to be arbitrary!), the node which is behind will request to be caught-up to the latest state.

A note about catch-ups: in GRANDPA, catch-ups within the same voter set can be done in bounded space. Catching up to the current voter set is done as part of the synchronization process. We special-case commit messages which finalize set-change blocks. These commit messages are kept for all nodes and they are meant to be eagerly sent along with the relevant blocks. If the commit messages are not sent along, the Substrate implementation of GRANDPA contains logic to request peers for them. Assuming they are available, catching up to the latest voter set happens naturally as part of the chain synchronization process. Therefore, the primary downside going offline is that you will need a way to catch up to the most recent round in the current voter set.

https://hackmd.io/BJ-HY2fYTmu-7pRsIWst1w?both contains a run-down of "politeness" of messages.

We can "time-out" messages from voters after receiving double-votes from them (again, only after processing those votes). Messages from timed-out voters can be safely ignored, but the time-out should be limited (10 minutes?) and we must be careful not to have more than $f = max(n-1, 0)/3$ timed-out at any moment. A FIFO would be good for that.

<br/>


### Expiration

- We can use our local view of the GRANDPA protocol to decide on message expiration.
- We want to guarantee liveness of all messages for the current and last N (3?) rounds
	- Messages in the global topic that refer to these rounds.
	- All messages in round topics for the given rounds.
	- N=3 is chosen arbitrarily, but is reasonable. there is a way for nodes to catch up even if N=0, but a small N means we fall back on that less.
- Messages only expire based on this (no TTL). In case GRANDPA stalls, e.g. 1/3 of validators go offline, we need these messages to be available until they come back online and the GRANDPA protocol resumes progress.

### Validation

- Incoming messages for the topics we are subscribed to need to be validated at a higher level.
	- Is the message signature valid?
	- Is the vote from an authority in the current set? etc.
- We only propagate valid messages and we should assume honest nodes will follow this behavior as well.
- Double votes are _valid_ messages that lead to time-out of the voter (not the sending peer!) _after_ processing.

### Requirements

- Messages in the round topic only need to reach other authorities (includes block producers -- same for now)
  - Only authorities subscribe to round topics, but we can't assume full connectivity among authorities, so these messages might need to go through nodes that are not subscribing to the topic.
  - We assume that each authrity (voter) is directly connected to at least $f+1$ other voters, where the total number of voters is $n=3f+1$. If the number of conncetion to distinct voters goes down for anyone we should be warned that en eclipse attack is becoming easier.
- Messages in the global topic are only produced by authorities but all full nodes will subscribe to global topics as well.
- Messages in round topics need higher delivery guarantees.
- Messages in the global topic can be missed and don't need to reach all nodes.
- When a node subscribes to a round topic it should eventually get all messages if the given round topic is within the last N rounds of a majority of nodes (either by fetching them or because the other nodes on the topic rebroadcast them).
- When a node subscribes to a global topic it should eventually get all live messages (i.e. messages for the latest rounds).

### Dealing with DoS
The countermeasure we take to prevent DoS attacks are as follows.

- We only propagate valid messages, if we receive any invalid message we report the peer with severe misbehavior.
- We only propagate messages that we consider live according to our local view of the GRANDPA protocol. If we receive an expired message from a peer we might (point to discuss!) report it as light misbehavior. Additionally, we might want to send the set of messages we believe would allow GRANDPA to make progress.
- Receiving a duplicate message from the same peer should be reported with light misbehavior (but how do we do repropagation?)
- Future messages from a different set GRANDPA set ID than we are currently on cannot be validated. If we discard these messages, we need to ensure we can get them back later. That probably means communicating to our peers that we aren't ready for a certain topic yet.
- Future messages from the same set ID can be validated, but pose a DoS risk because they can be arbitrarily far ahead. Again, we can discard these but should make sure we can get them again later. Another approach is to start with a small TTL. The TTL grows based on the number of voters we have seen valid messages (of any kind) for in that round. Once we have seen messages from $f+1$ voters, the round can be trusted.
- Past (completed) rounds are not a DoS vector. However, we should not accumulate too many in order to avoid gossip spam.
- We should tolerate messages about old rounds from peers -- this should not lead to disconnect. However, introducing a periodic "neighbor" message that gets sent to all neighbors (and not propagated further) where we can tell peers our current (set_id, round) makes this less of a problem. If a neighbor gives us a (set_id, round) pair, it would be misbehavior to send them messages about rounds earlier than that.
