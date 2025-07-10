---
title: Transaction Fees
---

**Authors**: [Alfonso Cevallos](/team_members/alfonso.md), [Jonas Gehrlein](/team_members/Jonas.md)

**Last Updated**: October 17, 2023

## Relay-chain transaction fees and per-block transaction limits

Some of the properties we want to achieve relative to relay-chain transactions are as follows:

1. Each relay-chain block should be processed efficiently, even on less powerful nodes, to avoid delays in block production.
2. The growth rate of the relay chain state is bounded. 2'. Better yet if the absolute size of the relay chain state is bounded.
3. Each block has *guaranteed availability* for a certain amount of operational, high-priority txs such as misconduct reports.
4. Blocks are typically far from full, so that peaks of activity can be dealt with effectively and long inclusion times are rare.
5. Fees evolve slowly enough, so that the fee of a particular tx can be predicted accurately within a frame of a few minutes.
6. For any tx, its fee level is strictly larger than the reward perceived by the block producer for processing it. Otherwise, the block producer is incentivized to stuff blocks with fake txs.
7. For any tx, the processing reward perceived by the block producer is high enough to incentivize tx inclusion, yet low enough not to incentivize a block producer to create a fork and steal the transactions of the previous block. Effectively, this means that the marginal reward perceived for including an additional tx is higher than the corresponding marginal cost of processing it, yet the total reward for producing a full block is not much larger than the reward for producing an empty block (even when tips are factored in).

For the time being, we focus on satisfying properties 1 through 6 (without 2'), and we leave properties 2' and 7 for a further update. We also need more analysis on property 2.

The amount of transactions that are processed in a relay-chain block can be regulated in two ways: by imposing limits, and by adjusting the level of tx fees. We ensure properties 1 through 3 above by imposing hard limits on resource usage, while properties 4 through 6 are achieved via fee adjustments. These two techniques are presented in the following two subsections respectively.


### Limits on resource usage

We identify four resources which can be consumed when processing a tx:

* Length: data size of the tx in bytes within the relay-chain block,
* Time: time it takes to import it (i/o and cpu),
* Memory: amount of memory it takes when processing,
* State: amount of state storage increase it induces.

Notice that unlike the other three resources which are consumed only once, state storage has a permanent cost over the network. Hence for state storage we could have rent or other Runtime mechanisms, to better match fees with the true cost of a tx, and ensure the state size remains bounded. This needs further consideration. We could also consider a mechanism that doesn't impose a hard limit on state increase but rather controls it via fees; however we prefer to add a limit for soundness, in order to avoid edge cases where the state grows out of control.

**Adjustable parameters.** For the time being, we suggest the following limits on resource usage when processing a block. These parameters are to be further adjusted via governance based on real-life data or more sophisticated mechanisms.

* Length: 5MB
* Time: 2 seconds
* Memory: 10 GB
* State: 1 MB increase

In principle, a tx consumes some amount of the last three resources depending on its length, type, input arguments, and current state. However, for simplicity we decided to consider, for each transaction type, only the worst-case state, and only the byte length of its input arguments. Consequently, we classify transactions based on length, type and argument length, and run tests (based on worst-case state) to examine their typical resource usage.

For the time being, we are considering a model where every transaction within a block is processed in sequence. So, in order to ensure the block memory bound above, it is sufficient to ensure that each tx observes the memory bound. We make sure this is the case. However, in the future we may consider parallelism.

To simplify our model further, we define a tx *weight* as a parameter that captures the time usage and state increase of a tx. Specifically, we define a tx weight as the *max* of its typical time and state usage, each measured as a fraction of the corresponding block limit. Then, given a collection of txs, we will sum up their lengths on one hand, and their weights on the other hand, and we will allow them within the same block only if both limits are respected. This is a hard constraint on resource usage which must be respected in each block.

We add a further constraint on resource usage. We distinguish between "normal" txs and "operational" txs, where the latter type corresponds to high-priority txs such a fisherman reports. A collection of normal txs is allowed within the same block only if both their sum of lengths and their sum of weights are below 75% of the respective limits. This is to ensure that each block has a guaranteed space for operational txs (at least 25% of resources).

**Details about establishing typical resource usage for txs.** Length is easy to determine by inspection. For time and memory usage, we prepare the chain with the worst-case state (the state for which the time and memory requirements to import this tx type should be the largest). We generate 10k transactions for a given transaction type with input which should take the longest to import for that state, and we measure the mean and standard deviation for the resource usage with the Wasm environment. If the standard deviation is greater than 10% of the mean, we increase the sample space above 10k. Finally, state increase is by inspection, based on worst cases for a large sample of txs.


### Setting transaction fees

We use the model described above to set the fee level of a tx based on three parameters: the tx type, its length, and its weight (parameters defined in the previous subsection). This fee differentiation is used to reflect the different costs in resources incurred per transaction, and to encourage/discourage certain tx market behaviors.

As mentioned earlier, part of the tx fee needs to go to the block producer, to incentivize inclusion, but not all of it, so the block producer is discouraged from stuffing blocks with bogus txs. For simplicity, we originally suggest that 20% of each tx fee goes to the block producer, with the remaining 80% going to treasury. We remark that a fraction could also be set for burning, but we choose not to do so to keep better control of the inflation rate. In the future this percentage may be adjusted, and could be made dependent on the tx type, to encourage the block producer to include certain tx types without necessarily adjusting the fee.

A transaction fee tx is computed as follows:

$$
fee(tx) = base\_fee + type(tx) \cdot length(tx) + c_{traffic} \cdot weight(tx)
$$

where $c_{traffic}$ is a parameter independent from the transaction, that evolves over time depending on the network traffic; we explain this parameter in the next subsection. Parameter $type(tx)$ depends on the transaction type only; in particular for operational transactions, we currently set $type(tx)$ to zero.

Intuitively, the term $weight(tx)$ covers the processing cost of the block producer, while the term $type(tx) \cdot length(tx)$ covers the opportunity cost of processing one transaction instead of another one in a block.

### Adjustment of fees over time

The demand for transactions is typically quite irregular on blockchains. On one hand, there are peaks of activity at the scale of hours within a day or days within a month. On the other hand, there are long term tendencies. We need a mechanism that automatically updates the transaction fees over time taking these factors into consideration. By the law of supply and demand, raising the fee should decrease the demand, and vice-versa.

To deal with peaks of activity, we face a trade-off between hiking up transaction fees rapidly or potentially having long transaction inclusion times - both undesirable effects. We propose two mechanisms. The first one adjusts the price very quickly, at the same pace as the peaks and valleys of activity. The second one adjusts slowly, at the pace of long term tendencies, and uses tipping to give users the possibility of controlling waiting times at peak hours. We propose to use the slow adjusting mechanism with tips, but provide details of both mechanisms for completeness.

#### 1. Fast adjusting mechanism

In this mechanism the transaction fees vary greatly through time, but are fixed for all users at each block (no tipping).

Recall that we set a hard limit on the sum of lengths and weights of all transactions allowed on a block. We also set a second hard limit, this time on the sum of lengths and weights of "normal" txs (non-operational txs), which is equal to 75% of the first limit.

**Definition.** We define a block's saturation level (relative to normal txs) as a fraction $s$ between 0 and 1 which describes how close the limit on normal txs is from being full. Explicitly, the saturation level of a block $B$ is

$$
s(B):=\max\{\frac{\sum_{\text{normal } tx \in B} length(tx)}{\text{normal length limit}}, \frac{\sum_{\text{normal } tx \in B} weight(tx)}{\text{normal weight limit}}\}
$$

where the normal length limit (the block length limit on normal transactions) is 75% of the overall length limit, and the normal weight limit is 75% of the overall weight limit.

**Adjustable parameter** Let $s^*$ be our target block saturation level. This is our desired long-term average of the block saturation level (relative to normal txs). We originally suggest $s^*=0.25$, so that blocks are 25% full on average and the system can handle sudden spikes of up to 4x the average volume of normal transactions. This parameter can be adjusted depending on the observed volumes during spikes compared to average volumes, and in general it provides a trade-off between higher average fees and longer transaction inclusion times during spikes.

Recall that a transaction fee is computed as $fee(tx) = base\_fee + type(tx) \cdot length(tx) + c_{traffic} \cdot weight(tx)$, for a parameter $c_{traffic}$ that is independent of the transaction. Let $s$ be the saturation level of the current block. If $s>s^*$ we slightly increase $c_{traffic}$, and if $s<s^*$ we slightly decrease it.

**Adjustable parameter:** Let $v$ be a fee variability factor, which controls how quickly the transaction fees adjust. We update $c_{traffic}$ from one block to the next as follows:

$$
c_{traffic} \leftarrow c_{traffic}\cdot (1+ v(s-s^*) + v^2(s-s^*)^2/2)
$$

This is thus a feedback loop with multiplicative weight updates. It is a very good approximation to using the more involved update $c_{traffic} \leftarrow c_{traffic}\cdot e^{v(s-s^*)}$, which in turn has the following properties:

* Assuming that $v$ is small, the relative change of parameter $c_{traffic}$ is approximately proportional to the difference $(s-s^*)$, i.e.

$$
\frac{c_{traffic}^{new} - c_{traffic}^{old}}{c_{traffic}^{old}}\approx v(s-s^*)
$$

* If there is a period of time during which $k$ blocks are produced and the average saturation level is $s_{average}$, the relative change of parameter $c_{traffic}$ during this period is approximately proportional to $k$ times the difference $(s_{average} - s^*)$, i.e.

$$
\frac{c_{traffic}^{final} - c_{traffic}^{initial}}{c_{traffic}^{initial}}\approx vk(s_{average}-s^*)
$$

How to choose the variability factor $v$? Suppose that we decide that the fees should not change by more than a fraction $p$ during a period of $k$ blocks, even if there is 100% saturation in that period. We obtain the formula

$$
\text{fees relative change} \leq \frac{c_{traffic}^{final} - c_{traffic}^{initial}}{c_{traffic}^{initial}}\approx vk(s_{average}-s^*) \leq vk(1-s^*)\leq p
$$

which gives us the bound $v\leq \frac{p}{k(1-s^*)}$.

For instance, suppose that we detect that during peak times some transactions have to wait for up to $k=20$ blocks to be included, and we consider it unfair to the user if the fees increase by more than 5% $(p=0.05)$ during that period. If $s^*=0.25$ then the formula above gives $v\leq 0.05/[20(1-0.25)]\approx 0.0033$.

#### 2. Slow adjusting mechanism

In this mechanism, fees stay almost constant during short periods, adjusting only to long-term tendencies. We accept the fact that during spikes there will be long inclusion times, and allow the transactions to include tips to create a market for preferential inclusion.

We use the same formula as above to update the transaction fees in each block, i.e. $c_{traffic} \leftarrow c_{traffic}\cdot (1 + v(s-s^*) + v^2(s-s^*)^2/2$, except that we select a much smaller variability factor $v$. For instance, suppose that we want the fees to change by at most 30% per day, and there are around $k=14000$ blocks produced in a day. If $s^*=0.25$ then we obtain $v\leq 0.3/[14000(1-0.25)] = 0.00003$.

The transaction fee is considered a base price. There will be a different field in the transaction called tip, and a user is free to put any amount of tokens in it or leave it at zero. Block producers receive 100% of the tip on top of the standard 20% of the fee, so they have an incentive to include transactions with large tips. There should be a piece of software that gives live suggestions to users for tip values, that depend on the market conditions and the size of the transaction; it should suggest no tip most of the time.
