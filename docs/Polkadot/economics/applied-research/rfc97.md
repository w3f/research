# Unbonding Queue (accepted): RFC-0097

|                 |                                                                                             |
| --------------- | ------------------------------------------------------------------------------------------- |
| **Date**  | 19.06.2024                                                                                  |
| **Description** | This RFC proposes a safe mechanism to adjust the unbonding time for staking on the Relay Chain, making it proportional to the overall unbonding stake. Such an approach significantly reduces the expected duration of unbonding and ensures that a substantial portion of the stake remains available to slash validators who behave maliciously, within a 28-day window.                                                                                                           |

## Summary

This RFC proposes a flexible unbonding mechanism for tokens locked for [staking](https://wiki.polkadot.network/docs/learn-staking) on the Relay Chain (DOT/KSM). Its main aim is to enhance user convenience without compromising system security. 

Locking tokens for staking is what allows Polkadot to slash tokens that back misbehaving validators. Changing the locking period requires ensuring that Polkadot can still slash enough tokens to deter misbehavior. In this context, not all tokens can be unbonded immediately, yet it is possible to allow some tokens to be unbonded quickly.

By queuing new unbonding requests and scaling their unbonding duration relative to the queue size, the new mechanism reduces the average unbonding time. When the queue is comparatively empty, new requests can be executed with a minimum of 2 days (instead of the conventional 28 days) if the sum of stake requests exceeds a threshold. In scenarios between these two bounds, the unbonding duration scales proportionately. It is worth emphasizing that the new mechanism will never perform worse than the current fixed 28-day period.  

This entry also presents an empirical analysis that retrospectively fits the proposed mechanism to the historic unbonding timeline, showing that the average unbonding duration decreases significantly while remaning sensitive to large unbonding events. The entry also touches upon implications for UI, UX, and conviction voting.

:::note
This proposition focuses on the locks imposed from staking. Other locks, such as governance, remain unchanged. Such a mechanism should not be confused with the existing [FastUnstake](https://wiki.polkadot.network/docs/learn-staking#fast-unstake) feature, which lets users unstake tokens without earning rewards for 28 days or longer.
:::

Before considering the model's integration into Polkadot, one may first implement and test it on Kusama. With appropriate adjustments to the parameters, one can gauge its effectiveness and stability. This entry, however, focuses on Polkadot. 

## Motivation

Since security is an important goal, Polkadot has one of the longest unbonding periods among all Proof-of-Stake protocols. Staking on Polkadot remains attractive compared to other protocols due to its above-average staking APY. The long unbonding period, however, harms usability and deters potential participants who want to contribute to the netwrok's security. 

The current length of the unbonding period imposes significant costs on entities that want to perform basic tasks such as the reorganization or consolidation of their stashes, or the updating of private key infrastructure. The long period also limits the participation of users who prefer liquidity.

The combination of long unbonding periods and high returns has led to the proliferation of [liquid staking](https://www.bitcoinsuisse.com/learn/what-is-liquid-staking). Here, parachains or centralised exchanges offer users their staked tokens either in the original DOT/KSM form or as derivative tokens before the 28-day unbonding period is over. If few tokens are involved, liquid staking is harmless. But with a large fraction of DOT, a few entities may select many validators, leading to centralization and opening the door to attacks (see [here](https://dexola.medium.com/is-ethereum-about-to-get-crushed-by-liquid-staking-30652df9ec46) for further discussion on the threats of liquid staking).   

The new mechanism greatly increases Polkadot's competitiveness, without interferring with its security.


## Stakeholders

- Every DOT/KSM token holder

## Explanation

Polkadot has a 28-day unbonding period to prevent long-range attacks (LRA), which can occur if more than one-third of validators collude. 

In essence, an LRA describes the innability of users who disconnect from the consensus at time t<sub>0</sub>, and reconnect later to realize that legitimate validators at that earlier time, but who have since dropped out, can no longer be trusted. This means that a user syncing the state could be fooled into trusting validators who have fallen out of the active set since t<sub>0</sub> and are building a competing malicious chain (fork).

The use of trusted checkpoints, assumed to be no more than 28 days old, can mitigate LRAs that last longer than 28 days. A new node syncing Polkadot will start from the checkpoint and verify finality proofs for subsequent blocks signed by two-thirds of validators. In an LRA fork, some validator sets may differ if two-thirds of a validator set signed something incorrect within the last 28 days. 

With the current unbonding period, detecting an LRA of no more than 28 days means the possibility to identify misbehavior from over one-third of validators whose nominators are still bonded. The stake backing these validators represents a considerable portion of the total stake, around 28.7% in practice. Allowing the unbonding of more stake than this, without verifying the backing validators, opens the door to a cost-free LRA attack. The proposed mechanism thus allows up to half of this stake to unbond within 28 days. This reduces the amount of slashable tokens by half, still a very large amount in absolute terms. For example, at the time of writing (19 June 2024), this would translate to around 120 million DOT.

Attacks other than LRAs, such as backing incorrect parachain blocks, can be detected and slashed within two days. This is why the mechanism includes a minimum unbonding period.

In practice, an LRA does not affect clients who follow consensus more frequently than every two days, such as full nodes or bridges. Yet, an attacker could still mislead a node if it connects before the node syncs Polkadot.  

Given the benefits, maintaining a fraction of the total stake as slashable is a reasonable trade-off that helps protect against LRAs at any given time.

## Mechanism

When a user, either a [nominator](https://wiki.polkadot.network/docs/learn-nominator) or a validator, decides to unbond their tokens, those tokens are not instantly available. Rather, they enter an *unbonding queue*. This specification illustrates how the queue works, assuming a user wishes to unbond a portion of their stake,  denoted as `new_unbonding_stake`. The variable `max_unstake`tracks how much stake can be unbonded earlier than 28 eras (28 days on Polkadot and 7 days on Kusama).

To calculate `max_unstake`, it is necessary to record, for each era, the amount of stake used to back the lowest-backed one-third of validators. This information is stored for the last 28 eras, with `min_lowest_third_stake` representing the minimum value across that period. `MIN_SLASHABLE_SHARE` x `min_lowest_third_stake` determines `max_unstake`. In addition, `UPPER_BOUND` and `LOWER_BOUND` are variables used to scale the unbonding duration of the queue.

The variable `back_of_unbonding_queue_block_number`  represents the block number at which all existing unbonders have completed unbonding. It can be stored at any time.

If a user wants to unbond some of their stake (`new_unbonding_stake`) at an arbitrary block number (`current_block`), then:

```
unbonding_time_delta = new_unbonding_stake / max_unstake * UPPER_BOUND
```

This number is added to the `back_of_unbonding_queue_block_number` under the condition that it does not undercut `current_block + LOWER_BOUND` or exceed `current_block + UPPER_BOUND`. 

```
back_of_unbonding_queue_block_number = max(current_block_number, back_of_unbonding_queue_block_number) + unbonding_time_delta
```

Such an expression determines the block at which the user's tokens are unbonded, ensuring that it falls within the limits defined by `LOWER_BOUND` and `UPPER_BOUND`.

```
unbonding_block_number = min(UPPER_BOUND, max(back_of_unbonding_queue_block_number - current_block_number, LOWER_BOUND)) + current_block_number
```

Ultimately, the user's token are unbonded at `unbonding_block_number`.


### Proposed parameters

Although up for discussion, the following exogenously set constants are recommended:
- `MIN_SLASHABLE_SHARE`: `1/2`. The share of stake backing the lowest one-third of validators that is slashable at any point in time. This parameter offers a trade-off between security and unbonding time. Setting it to one-half provides sufficient stake for slashing while maintaining a short average unbonding time.
- `LOWER_BOUND`: 28,800 blocks (or 2 eras). A value that represents the minimum unbonding time for any 2-day stake. 
- `UPPER_BOUND`: 403,200 blocks (or 28 eras). A value that represents the maximum unbonding time a user may face. It equals the current unbonding time and should be familiar to users.

### Rebonding

Users who choose to unbond may want to cancel their request and rebond. This action does not result in any security loss, although, under the scheme described above, a large unbond may increase the unbonding time for subsequent users in the queue. When the large stake is rebonded, those next in the queue move forward and can unbond more quickly than originally estimated. This would require an additional extrinsic from the user.

The `unbonding_time_delta` should thus be stored with the unbonding account. If the account rebonds when still unbonding, this value must be subtracted from the `back_of_unbonding_queue_block_number`. Unbonding and rebonding leave this number unaffected. The `unbonding_time_delta` must be stored because, in later eras, `max_unstake` may change and cannot be recomputed.

### Empirical analysis

The proposed unbonding queue calculation, together with the recommended parameters, can simulate the queue over Polkadot's unbonding history. Instead of analysing on a per-block basis, the calculation is performed on a daily basis. The unbonding queue is simulated using two inputs: the ratio of the daily total stake of the lowest third of backed validators to the total daily stake, which determines the `max_unstake`, and the sum of daily and newly unbonded tokens. 

Due to the [NPoS algorithm](https://wiki.polkadot.network/docs/learn-phragmen), the first number fluctuates slightly. By sampling data from several past eras it is possible to determine a constant of about 0.287. Parity's data infrastructure was essential for this analysis.

The following graph illustrates two metrics: `Unbonded Amount` and `Unbonding Days`. `Unbonded Amount` is the sum of daily and newly unbonded tokens over time, scaled to a 28-day y-axis via `daily_unbonded / max(daily_unbonded) * 28`. `Unbonding Days` is the daily expected unbonding duration, given the history of `daily_unbonded`.


<div align="center">
  <div style={{width: "70%"}}>
    <img src="https://raw.githubusercontent.com/polkadot-fellows/RFCs/fd7dbb2cc6defefaa0c601d463be8fa86347ec4e/text/empirical_analysis.png" alt="Empirical Queue" style={{width: "100%"}} />
  </div>
</div>

Historical unbonds only trigger unbonding times greater than `LOWER_BOUND` during periods of extensive and/or clustered unbonding. The average unbonding time across the entire time series is approximately 2.67 days. This mechanism increases unbonding times during large unbonding events, reaching a maximum of 28 days at the extreme. The results confirm that the mechanism is sufficiently sensitive, making it reasonable to match `UPPER_BOUND` with the historically largest unbonds. 

The main parameter affecting the situation is `max_unstake`. The relationship is straightforward: decreasing `max_unstake` makes the queue more sensitive. For instance, the queue spikes more quickly and reaches higher levels during unbonding events. Since these events were historically associated with parachain auctions, it is reasonable to assume that in the absence of major systemic events, users will experience significantly reduced unbonding times.

The analysis can be extrapolated or adapted to other parameters using a repository such as this [one](https://github.com/jonasW3F/unbonding_queue_analysis).


## Additional considerations

### Deferred slashing

Allowing multiple slashes within the 28-day period enables governance to cancel slashes caused by bugs. While rare on Polkadot, such bugs can account for a significant portion of all slashes. This includes slashing for attacks other than LRAs, which should be detected and executed within two days. Still, two days are not enough to cancel slashes via OpenGov.

Due to the way exposures are stored, which nominators back which validators and with how many tokens, it is difficult to determine whether a nominator has deferred slashes not yet applied on-chain. Therefore, it is not possible to simply check for deferred slashes when nominators attempt to withdraw their bond. 

Freezing the unbonding queue while there are pending slashes in the staking system helps solve this issue. In the worst case, when a slash is applied, one can force all members of the queue to unbond within 28 days minus the number of days they have already been waiting. In other words, nobody needs to wait longer than 28 days. The unbonding queue would then remain paused until resolving all deferred slashes in the system. 

This solution may be easier to implement, although it could cause disruptions for unbonding stakers who are not slashed, as they would not benefit from the queue. It is crucial to note that unbonding remains possible for all stakers within the usual 28 days. Since slashes occur rarely, distruptions should not happen often. In addition, a new extrinsic that lets any account identify unbonding accounts with deferred slashes could complement the solution. The chain would then set the `unbonding_block_number` of affected accounts to a time after the slash is applied, no more than 28 days from when the staker unbonded. 

After removing the offenders from the queue, the unbonding queue remains unfrozen, and operations for unslashed accounts are restored immediately. Identifying nominators with deferred slashes requires iterating through all nominators, which is only feasible off-chain. Incentives for non-slashed unbonding accounts to act should be sufficient, as they seek to reduce the opportunity cost of waiting longer than necessary. 

The solution resolves the issue securely. And if no user submits the extrinsic, no staker would exceed the standard 28-day unbonding duration, and all slashes would still be applied as intended.

### UX/UI
Because of the design of the unbonding queue, the more a user splits up their stake to be unbonded, the shorter their expected unbonding time becomes. This, however, comes with a cost: it can, for instance, lead to higher transaction fees due to more and/or larger transactions. 

UI implementations should provide a good UX that informs users about this trade-off, and helps them decide whether paying more for faster unbonding is worthwhile. For most users, splitting their stake will not offer a meaningful advantage, as their impact on the queue is negligible.

### Conviction voting
Changing the (expected) unbonding period indirectly affects conviction voting, as governance locks do not stack with the staking locks. Simply put, if a user is already locked through staking, they can freely choose a conviction vote less than or equal to that locking time. With the 28-day unbonding period, the `3x` conviction vote essentially comes for free. 

Ongoing discussions aim to [rescale the conviction weights](https://github.com/polkadot-fellows/RFCs/pull/20#issuecomment-1673553108) and thereby improve parametrization. The transition between the old locks and new locks, however, poses significant challenges. 

**Under this unbonding queue, the current conviction voting scheme aligns more closely with governance and avoids the need for an expensive migration of existing locks to a new scheme.** For example, if the average staking unbonding period is around two days, locking tokens for an additional 26 days justifies a higher `3x` voting weight. Voters who seek maximum liquidity can do so freely, but it is fair that their votes carry less weight in governance decisions, which naturally affect Polkadot's long-term success.

### Potential extension
In addition to a simple queue, a market component could let users unbond with the minimum possible waiting time (for instance, `LOWER_BOUND`, which might be two days) by paying a variable fee. 

A reasonable approach would be to split the total unbonding capacity into two parts: one for the simple queue and one for the fee-based unbonding. This enables users to choose between the quickest unbonding option, by paying a dynamic fee, or joining the regular queue. Setting capacity limits for both queues ensures a predictable unbonding time in the simple queue, while also giving users the option to pay for an even faster exit. 

Fees are dynamically adjusted and proportional to the unbonding stake, expressed as a percentage of the requested amount. In contrast to a unified queue, this prevents users from paying a fee to jump ahead of others who do not, which would push their unbonding time back and harm UX. The resulting revenue could be burned.

This extension and additional specifications are not considered in this RFC, as they would add unnecessary complexity. The empirical analysis above also suggests that the average unbonding time is already close to the `LOWER_BOUND`, indicating that a more complex design may be unnecessary. It is advisable first to implement the discussed mechanism and then, after gaining some experience, assess whether an extension is desirable. 

## Drawbacks

- **Lower security for LRAs.** It is undeniable that the theoretical security against LRAs decreases. Yet, such an attack remains largely theoretical and sufficiently costly to be unlikely in practice. In this regard, the benefits outweigh the costs.
- **Griefing attacks.** A large holder could attempt to unbond a significant amount of tokens to prevent other users from exiting the network earlier. This would be costly as the holder would lose staking rewards. The larger the impact on the queue, the higher the cost. In any case, the `UPPER_BOUND` remains at 28 days, so nominators will never face an unbonding period longer than the current one. In this scenario, an attacker would not gain enough to justify the expense, making such behaviour unlikely.
- **Challenge for custodians and liquid staking providers.** Changing the unbonding time, especially making it flexible, requires entities offering staking derivatives to rethink and adapt their products.

## Testing, security, and privacy

N/A

## Performance, ergonomics, and compatibility

N/A

### Performance

The authors do not foresee any potential impact on performance.

### Ergonomics

The authors do not see any potential impact on ergonomics for developers. Potential impact on UX/UI users are discussed above.

### Compatibility

The technical teams should assess any compatibility issues.


### Prior art and references
- Ethereum proposed a [similar solution](https://blog.stake.fish/ethereum-staking-all-you-need-to-know-about-the-validator-queue/)
- Alistair Stuart wrote an intitial [overview](https://hackmd.io/SpzFSNeXQM6YScW1iODC_A)
- [Other research](https://arxiv.org/pdf/2208.05408.pdf) further mitigates the risk of LRAs.

**For more information or inquieries, please contact:** [Jonas Gehrlein](/team_members/Jonas.md) or [Alistair Stewart](/team_members/alistair.md)