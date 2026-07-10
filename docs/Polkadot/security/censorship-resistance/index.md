---
title: Censorship Resistance at Parachain Level, a Technical Description
---
The recent move of staking and governance to the parachain level, specifically the AssetHub parachain (see below), has changed the security dynamics on Polkadot. Now, censorship resistance on the parachain level is also crucial to ensure the network’s security. 

## AssetHub

Recently, the Polkadot team migrated AssetHub’s core functionality from the Relay Chain, where it originally was, to one of its parachains. The main reason behind this move was twofold. First, it was an economically more viable solution, as any execution on the Relay Chain costs far more than on a parachain. Second, it has to do with what AssetHub could facilitate. Being at a parachain level, it could be used to offer features of a more general purpose smart contract chain, which translates into enabling functionalities for balances, staking, and even governance.

While the Relay Chain ensures parachain blocks do not violate safety, it does not guarantee liveness or censorship resistance at the parachain level. To address this, the research team developed a solution that provides parachains with these two features. 

## The Aura Protocol and Some Assumptions

To achieve censorship resistance at the parachain level, it was necessary to introduce a tweak to Aura, the deterministic consensus protocol that all Polkadot parachains use via the Aura-Ext pallet. Under this protocol, block production is handled by a list of authorities who take turns creating blocks via a rotating schedule that determines whose turn is next.

To introduce this tweak, the research team assumes a setting with at least one honest collator (the node that produces a parachain’s block) and an honest ‘backer’ (a relay-chain validator assigned to approve a parablock) who backs the block that other collators are trying to censor. The solution needs to hold under these realistic assumptions, which are reasonable given two-thirds honesty on the Relay Chain and that backers are assigned randomly. 

Another assumption is that the availability layer is robust, and that a collator can fetch the latest parablock directly from the availability layer (or the backer) within a reasonable time. Together, these conditions are enough to ensure the censored block is eventually produced. 

## How Aura Becomes Censorship-Resistant 

The Aura protocol can become censorship-resistant by paying attention to the checks currently performed in the PVF (Parachain Validation Function), and by understanding the nature of a concrete attack. Regarding the current checks, which exist to stop a collator from fabricating or fast-forwarding its way past an honest block, there are two main points where Aura’s block authorship rights require a closer look. 

The first one is *on_state_proof* in the ConsensusHook of the [Aura-Extension](https://github.com/paritytech/polkadot-sdk/blob/8730f3c2fa1d36161fccdc6a318e175eda459d0f/cumulus/pallets/aura-ext/src/consensus_hook.rs#L73) pallet. Here it is necessary to check that 1) the relay slot of the parablock being built is greater than or equal to the relay slot of the latest included block; 2) the velocity condition, which limits how many parablocks can be produced per relay block to prevent a collator from racing ahead, is not violated; and 3) the parablock timestamp is not too far in the future. The second point is whether the Current Slot only ever increases in the [Aura pallet](https://github.com/paritytech/polkadot-sdk/blob/8730f3c2fa1d36161fccdc6a318e175eda459d0f/substrate/frame/aura/src/lib.rs#L128C6-L128C19). This check is crucial because collators should not be able to rewind the slot counter to reclaim authorship rights.

Before moving forward, let’s consider a concrete attack. Here, three collators (A, B, and C) have been assigned to consecutive slots. For A and C to censor B, the attack would unfold as follows: if A produces a block, feeds it to the backers, and selectively withholds it from B, then C can build its own block directly on top of A’s, skipping B’s slot, and get it included before B manages to fetch A's block by recovering the data from the availability layer. If B never receives A’s block in time, B’s slot is skipped and its honest block never lands. 

The attack is possible because B only gets a single slot, too little time to recover a withheld block before its turn passes. A possible solution, then, is to give each collator a run of several consecutive slots instead of just one. This is where the idea of multi-slot collations comes in.  

## Multi-Slot Collations

Concretely, the round-robin rotates every *x* slots instead of each slot. Once the system selects a collator, it can build *x* consecutive blocks. As part of the PVF, the Aura authorship checks have to reflect this change.

Choosing *x* large enough enables the collator being censored to have enough time to recover previous blocks and build on them. This ensures a block gets backed in at least one of the *x* slots.  

Because the honest collator now controls a run of *x* slots, it has time to recover each withheld block and still produce its own. As in our previous setting with collators A, B, and C, if collator A does not share with B, then for *0 ≤ i < x*, B recovers and imports the blocks produced by A for slot *A + i* before its own slot *B + i*, so B can produce a block by its slot *B + x*.

Even in the worst case, a censored collator still produces at least one block per round, while honest collators produce up to *x*. So it is important to be more careful with how A’s delaying of its own blocks impacts timing. 

This approach is compatible with the (collator timestamp-dependent) Slot-Based collation. Such an approach, however, is vulnerable to liveness attacks where adversarial collators don't show up to stall liveness but then also lose out on block production rewards. The expected number of blocks per round therefore depends on the fraction of no-shows. If the ratio of adversarial collators is *α*, and the collator set is C, then the number of blocks per round is:

<div align="center">α⋅∣C∣+(1−α)⋅x⋅∣C∣, instead of x⋅∣C∣.</div>

Multi-slot collations work well if collators prioritise the transactions that may be censored when building their blocks. The next question to ask is how to determine the x parameter. 

### Determining the Parameter *x*

In short, we want the smallest *x* that still gives a censored collator enough time to recover and build on withheld blocks. With this in mind, it is clear that the number of consecutive slots *x* in the round-robin is lower-bounded by the time required to reconstruct the previous block from the availability layer (b) plus the block building time (a). Therefore, it is necessary to set *x* such that *x ≥ a + b*. But with async backing, a malicious collator may sequentially try to withhold the block and just-in-time front-run the honest collator for all the unincluded_segment blocks. Thus, *x* needs to be greater than *(a + b) ⋅ m*, where *m* is the *max* allowed candidate depth (unincluded segment allowed). 

An independent check on the relay chain filters out parablocks anchoring to very old relay_parents in the [verify_backed_candidates](https://github.com/paritytech/polkadot-sdk/blob/ec700de9cdca84cdf5d9f501e66164454c2e3b7d/polkadot/runtime/parachains/src/inclusion/mod.rs#L1237). Any parablock anchored to a relay parent (older than the oldest element in ‘allowed_relay_parents’) gets rejected. By doing so, the malicious collator cannot front-run and censor the subsequent collator after this delay, as the parablock is no longer valid. The update of the allowed_relay_parents occurs at [process_inherent_data](https://github.com/paritytech/polkadot-sdk/blob/ec700de9cdca84cdf5d9f501e66164454c2e3b7d/polkadot/runtime/parachains/src/paras_inherent/mod.rs#L321), where the buffer length of AllowedRelayParents is set by the scheduler parameter [lookahead](https://github.com/paritytech/polkadot-sdk/blob/875437c4aecf99e1f0ffeb8278a3b0b0017acbc2/polkadot/primitives/src/v8/mod.rs#L2148) (set to 3 by default). The async_backing delay tolerated by the relay chain backers is *3 ∗ 6s = 18s*. Either mechanism alone is enough to defeat the front-running, so we only need the cheaper of the two bounds. With this, the number of consecutive slots becomes the minimum of the above two values:

<div align="center">x ≥ min ((a + b)⋅m, a + b + async_delay)</div>

where *m* is the *max_candidate_depth*, or unincluded segment as seen from the collator's perspective. 

### Parameters for Plaza

Assuming that the previous block data can be fetched from backers, the result is *a + b ≤ 6s*. Using the current async_delay of 18s, we can set *x* to 4. If the max_candidate_depth (m) for Plaza is set such that *m ≤ 3*, then this will reduce (improve) *x* from 4 to *m*. A lower *x* is preferable, since it shortens the run of consecutive slots a single collator holds. 

## A Few Remaining Open Questions 
Beyond the inherent restriction on the async backing parameters, it is not clear whether there is an equation relating async_delay, *max_candidate_depth*, and velocity. Another point to consider is whether it is possible to claim that the elements of the allowed_relay_parents vector are always consecutive. Essentially, this update is performed by the relay chain runtime; every new relay chain block is appended while ensuring the overall buffer does not extend beyond *max_ancestry_len*.


## Final Remarks 
By executing the tweaks described above, it is possible to make the parachains censorship-resistant, which overall enables AssetHub to live on a parachain with a different role than the one it had on the Relay Chain, and to provide users with far more functionality than in the past.

Censorship resistance is the shield that keeps blockchains decentralized, neutral, and truly secure. It doesn't matter if a blockchain has the strongest cryptography in the world, because as long as a centralized group can decide who gets to use it, a system is fundamentally insecure. For this reason, as developments continue, Polkadot stays hands-on in keeping the network censorship-resistant.

**For more information or inquiries please contact:** [Jeffrey Burdges](http://localhost:3000/team_members/jeff)





