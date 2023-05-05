---
title: Token Economics
---

**Authors**: [Alfonso Cevallos](/team_members/alfonso.md), [Jonas Gehrlein](/team_members/Jonas.md)

Polkadot will have a native token called DOT. Its main functions are as follows:

1. Economics: Polkadot will mint or burn DOTs in order to reward the nodes that run the consensus protocol, to fund the treasury, to control the inflation rate, etc.

2. Slashing: DOTs also play a role in the slashing protocols designed to desincentivize attacks or adversarial behaviors.

3. Governance: DOTs are also used as voting power, to let DOT holders express their opinion in governance decisions via referenda.

3. Parachain allocation: Finally, DOTs are used to decide which projects are allocated a parachain slot, via auctions and deposits.


In this section we focus on the first use above, while each of the other three uses is analyzed in a separate section.

## Introduction

Polkadot is a proof-of-stake based platform where a set of validators, who have staked DOTs, produce blocks and reach consensus.  If a validator steers away from the protocol, some of his DOTs are slashed, but otherwise he gets paid for their contribution (roughly) proportional to his staked DOTs. The set of nodes elected as validators changes constantly (in each era, i.e. around once a day), but the number remains limited. However, any number of DOT holders can also participate indirectly in the decision-making processes as *nominators*, in what we call *nominated proof-of-stake*. A nominator indicates which validator candidates she trusts, and puts some DOTs at stake to support her nomination. If one or more of her nominated candidates are elected as validators in an era, she shares with them any economical rewards or punishments, proportional to her stake. Being a nominator is a way of investing one's DOTs, and of helping in the security of the system. Indeed, the larger the total amount of DOTs staked by nominators and validators, the higher the system security, because an adversary needs that much more stake -- or nominators' trust -- before it gets any nodes elected as validators.

We therefore aim at having a considerable percentage of the total DOT supply be staked by validators and nominators. Another large percentage of the DOT supply will be frozen as deposits by the commercial blockchains who get a parachain slot. We originally aim to have around 50% of DOTs staked in NPoS, and 30% in parachain deposits. As a reference, the percentage staked in other PoS-based projects is as follows.
- Tezos is 65.73% staked
- DASH is 58.69% staked
- Lisk is 58.20% staked
- EOS is only 35.49% staked, but that is because it is DPoS and the yield is low.


## Organization

This note contains the following subsections.

* **NPoS payment and inflation:** We describe how we reward well-behaving validators and nominators in our nominated proof-of-stake. Since the DOT minting for this end is the main cause of inflation in the system, we also describe our inflation model here. **Note, that the currently implemented inflation model has different parameters.**
* **Transaction fees:** We analyse the optimal transaction fees on the relay chain to cover for costs, discourage harmful behaviors, and handle eventual peaks of activity and long inclusion times.
* **Treasury:** We discuss how and when to raise DOTs to pay for the continued maintenance of the network.

Finally, in the last paragraph of the note we provide links to additional relevant references about the Polkadot protocol.

## NPoS payments and inflation

We consider here payments to validators and nominators for their participation in the protocols of block production (BABE) and finality (GRANDPA). We consider only the payments coming from minting new tokens, in normal circumstances. In particular we do not consider slashings, rewards to misconduct reporters and fishermen, or rewards from transaction fees. These will be considered in other sections.

As these payments are the main driver of inflation in the system, we first study our inflation model. Note that we suggest two sets of adjustable parameters: One for the eventual situation of launched parachains and one for the meantime, where liquidity is not constrained by parachain bonds.

### Inflation model

Let \(x\) be the *staking rate* in NPoS at a particular point in time, i.e. the total amount of tokens staked by nominators and validators, divided by the total token supply. \(x\) is always a value between 0 and 1.

__Adjustable parameter:__ Let \(\chi_{ideal}\) be the staking rate we would like to attain ideally in the long run. This value should probably lie between 0.3 and 0.6, and we originally set it at \(\chi_{ideal}=0.5\). If it falls, the security is compromised, so we should give strong incentives to DOT holders to stake more. If it rises, we lose liquidity, which is also undesirable, so we should decrease the incentives sharply. In the absence of parachains, we suggest an \(\chi_{ideal}=0.75\), as liquidity is not constrained by locked parachain bonds.

Let \(i=i(x)\) be the yearly *interest rate* in NPoS; i.e., the total yearly amount of tokens minted to pay all validators and nominators for block production and Grandpa, divided by the total amount of tokens staked by them. We consider it as a function of \(x\). Intuitively, \(i(x)\) corresponds to the incentive we give people to stake. Hence, \(i(x)\) should be a monotone decreasing function of \(x\), as less incentive is needed when \(x\) increases.

* We study the yearly interest rate (instead of the interest rate per block or per epoch) for ease of comprehension. This means that \(i(x)\) is the total payout perceived by somebody that continuously stakes one DOT during a year. The interest rate per block can be easily computed from it.
* Not every staked party will be paid proportional to their stake. For instance, a validator will be paid more than a nominator with equal stake, and a validator producing a block will be temporarily paid more than a validator not producing a block. So, \(i(x)\) only works as a guide of the average interest rate.

__Adjustable parameter:__ Let \(i_{ideal}:=i(\chi_{ideal})\) be the interest rate we pay in the ideal scenario where \(x=\chi_{ideal}\). This is the interest rate we should be paying most of the time. We suggest the value \(i_{ideal}=0.2\), i.e. an ideal yearly interest rate of 20%. In the absence of parachains, we suggest an \(i_{ideal}=0.133\).

Let \(I\) be the yearly *inflation rate*; i.e.

$$I=\frac{\text{token supply at end of year} - \text{token supply at beginning of year}}{\text{token supply at beginning of year}}.$$

The inflation rate is given by

$$I=I_{NPoS}+I_{treasury}-I_{slashing} - I_{tx-fees},$$

where $I_{NPoS}$ is the inflation caused by token minting to pay nominators and validators, $I_{treasury}$ is the inflation caused by minting for treasury, $I_{slashing}$ is the deflation caused by burning following a misconduct, and $I_{tx-fees}$ is the deflation caused by burning transaction fees.

* The rewards perceived by block producers from transaction fees (and tips) do not come from minting, but from tx senders. Similarly, the rewards perceived by reporters and fishermen for detecting a misconduct do not come from minting but from the slashed party. This is why these terms do not appear in the formula above.

$I_{NPoS}$ should be by far the largest of these amounts, and thus the main driver of overall inflation. Notice that by channelling all of the tokens destined to burning -due to both slashing and transaction fees- into treasury, we decrease the other terms in the formula (see the section on treasury). If we consider $I_{NPoS}$ as a function of the staking rate $x$, then clearly the relation between $I_{NPoS}(x)$ and $i(x)$ is given by

$$I_{NPoS}(x)=x\cdot i(x).$$

From our previous analysis, we can see that $I_{NPoS}(\chi_{ideal})=\chi_{ideal}\cdot i_{ideal}$. Since we want to steer the market toward a staking rate of $x=\chi_{ideal}$, it makes sense that the inflation rate **$I_{NPoS}(x)$ should be maximal at this value**.

__Adjustable parameter:__ Let $I_0$ be the limit of $I_{NPoS}(x)$ as $x$ goes to zero (i.e. when neither validators nor nominators are staking any DOTs). The value of $I_0$ shoud be close to zero but not zero, because we need to make sure to always cover at least the operational costs of the validators, even if nominators get paid nothing. Hence, $I_0$ represents an estimate of the operational costs of all validators, expressed as a fraction of the total token supply. We will make sure that $I_{NPoS}(x)$ is always above $I_0$ for all values of $x$, in particular also in the limit when $x$ goes to one.

For simplicity, we propose that the inflation function grow linearly between $x=0$ and $x=\chi_{ideal}$. On the other hand, we propose that it decay exponentially between $x=\chi_{ideal}$ and $x=1$. We choose an exponential decrease for $I_{NPoS}(x)$ because this implies an exponential decrease for $i(x)$ as well, and we want the interest rate to fall sharply beyond $\chi_{ideal}$ to avoid illiquidity, while still being able to control its rate of change, $i(x+\varepsilon)/i(x)$, when $x$ increases by a small amount $\varepsilon$. Bounding how fast the interest rate changes is important for the nominators and validators.

__Adjustable parameter:__ Define the *decay rate* $d$ so that the inflation rate decreases by at most 50% when $x$ shifts $d$ units to the right of $\chi_{ideal}$, i.e. $I_{NPoS}(\chi_{ideal} + d) \geq I_{NPoS}/2$. We suggest $d=0.05$.

 From the previous discussion, we propose the following interest rate and inflation rate functions, which depend on the parameters $\chi_{ideal}$, $i_{ideal}$, $I_0$ and $d$. Let

\begin{align}
I_{NPoS}(x) &= \begin{cases}
I_0 + \Big(I_{NPoS}(\chi_{ideal}) - I_0\Big)\frac{x}{\chi_{ideal}}
&\text{for } 0<x\leq \chi_{ideal}\\
I_0 + (I_{NPoS}(\chi_{ideal}) - I_0)\cdot 2^{(\chi_{ideal}-x)/d}
&\text{for } \chi_{ideal} < x \leq 1
\end{cases}, \text{ and}\\
\\
i(x)&= I_{NPoS}(x)/x.
\end{align}

It can be checked that $I_{NPoS}\geq I_0$ for all $0\leq x \leq 1$ with equality for $x=0$, $i(\chi_{ideal})=i_{ideal}$, $I_{NPoS}(x)$ is maximal at $x=\chi_{ideal}$ where it achieves a value of $\chi_{ideal}\cdot i_{ideal}$, and $i(x)$ is monotone decreasing.

These functions can be plotted for different parameters following this link: https://www.desmos.com/calculator/2om7wkewhr

### Inflation model with parachains
Following our suggestions for the economics after the implementation with parachains we show the graph with the following adjustable parameters: $I_0=0.025$, $\chi_{ideal}=0.5$, $i_{ideal}=0.2$ and $d=0.05$. We obtain the following plots, with $i(x)$ in green and $I_{NPoS}(x)$ in blue.

![](https://i.imgur.com/Kk1MLJH.png)

### Inflation model without parachains (current implementation)
In the absence of parachains, we suggest the following adjustable parameters: $I_0=0.025$, $\chi_{ideal}=0.75$, $i_{ideal}=0.133$ and $d=0.05$,. With the adjusted parameter we obtain the following plot, with $i(x)$ in green and $I_{NPoS}(x)$ in blue.

![](https://i.imgur.com/i8t1Q5y.png)

### Payment details

There are several protocols that honest validators are involved in, and we reward their successful participation or slash their lack thereof (whichever is easier to detect). From this point of view, we decide to reward validators (and their nominators) only for *validity checking* and for *block production*, because they are easy to detect.

In the branch of validity checking, we reward:

* a parachain validator for each validity statement of the parachain block that it issues.

In the branch of block production, we reward:

* the block producer for producing a (non-uncle) block in the relay chain,
* the block producer for each reference to a previously unreferenced uncle, and
* the producer of each referenced uncle block.

These are thus considered "payable actions". We define a point system where a validator earns a certain amount of points for each payable action executed, and at the end of each era they are paid proportional to their earned points. (The exact DOT value of each point is not known in advance because it depends on the total number of points earned by all validators in a given era. This is because we want the total payout per era to depend on the inflation model established above, and not on the number of payable actions executed).

__Adjustable parameters:__ We propose the following point system:

* 20 points for each validity statement,
* 20 points for each (non-uncle) block produced,
* 2 points (to the block producer) for each reference to a previously unreferenced uncle, and
* 1 point to the producer of each referenced uncle.

Notice that what is important here is not the absolute points but the point ratios, which establish the reward ratios of the payable actions. These points are parameters to be adjusted by governance.

In each era $e$, and for each validator $v$, we keep a counter $c_v^e$ on the number of points earned by $v$. Let $c^e =
\sum_{\text{validators } v} c_v^e$ be the total number of points earned by all validators in era $e$, and let $P^e_{NPoS}$ be our target total payout to all validators -- and their nominators -- in that era (see previous section on inflation model to see how to establish $P^e_{NPoS}$). Then, at the end of era $e$, the payout corresponding to validator $v$ and his nominators is given by

$$\frac{c_v^e}{c^e} \cdot P^e_{NPoS}.$$

We remark that we can also use the counters to combat unresponsiveness: if a validator has earned close to zero points in payable actions during an era (or any other period of time being measured), we kick them out. See the note on Slashings for more details.

### Distribution of payment within a validator slot

In any given era, the stake of a nominator $n$ is typically distributed among several validators, e.g. 70% of $n$'s stake is assigned to validator 1, 20% to validator 2, 10% to validator 3, etc. This distribution is decided automatically by the NPoS validator election mechanism that runs at the beginning of each era (see notes on NPoS for details).

If there are $m$ validators, then this stake distribution partitions the global stake pool into $m$ slots: one per validator. The stake in each validator slot is comprised of 100% of that validator's stake, and some fraction (possibly zero) of the stake of each nominator that approved of the validator. We sometimes refer to a validator's stake as "self-stake", to distinguish it from the *validator slot's stake*, which is typically much larger. In the previous subsection we explained how the payouts are assigned to each validator slot in a given era. In this subsection, we explain how this payout is distributed within a slot, i.e. among the validator and the nominators in it. Ultimately, a nominator's payout in a given era corresponds to the sum of her payouts with respect to each slot that contains some of her stake.

We remark that, since none of the nominators or validators can individually control the above-mentioned stake partition into validator slots (which is decided automatically by the validator election mechanism) or the exact payouts (which depend on global parameters such as the staking rate), none of the participants knows in advance exactly how much reward they will get during an era. In the future, we might allow nominators to specify their desired interest rates. We block this feature for the time being to simplify the corresponding optimization problem that the validator election mechanism solves.

We also remark that our mechanism takes as much of the nominators' available stake as possible; i.e. if a nominator has at least one of her approved validators elected, all of her available stake will be used. The idea is that the more stake, the more security we have. In contrast, we follow the policy that validator slots are paid equally for equal work, and they are NOT paid proportional to their stakes. So if a validator slot A has less stake than another validator slot B, then the parties in A are paid more per staked DOT. This should motivate nominators to rapidly adjust their preferences in future eras, to favor less popular validators, so that we can achieve a more balanced distribution of stake across validator slots (which is one of the main objectives of the validator election mechanism; see notes on NPoS for more details). This should also help new validator candidates have a better chance to get elected, which is important to ensure decentralization.

Within a validator slot, the payment is as follows: First, validator $v$ is paid his "commission fee", which is an amount entirely up to $v$ to decide, and which is publicly announced in advance by him, before nominators reveal their votes for the era. This fee is intended to cover $v$'s operational costs. Then, the remainder is shared among all parties (i.e. $v$ and the nominators) proportional to their stake within the validator slot. In other words, when it comes to payment, validator $v$ is considered as two entities: a non-staked validator that is rewarded a fixed commission fee, and a staked nominator that is treated like any other nominator and rewarded pro rata. Notice that a higher commission fee set by the validator means a higher total payout for him and a lower payout to his nominators, but since this fee is publicly known in advance, nominators will prefer to back validators with low fees (all else being equal). We thus let the market regulate itself. On one hand, a validator candidate with a high commission fee risks not getting enough votes to be elected as validator. On the other hand, validators who have built a strong reputation of being reliable and high performing will likely get away with charging a higher fee (which is fair), as they will still be preferred over other validators. And for a nominator, supporting riskier validators will be correlated with more rewards (which makes sense).


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

$$fee(tx) = base\_fee + type(tx) \cdot length(tx) + c_{traffic} \cdot weight(tx),$$

where $c_{traffic}$ is a parameter independent from the transaction, that evolves over time depending on the network traffic; we explain this parameter in the next subsection. Parameter $type(tx)$ depends on the transaction type only; in particular for operational transactions, we currently set $type(tx)$ to zero.

Intuitively, the term $weight(tx)$ covers the processing cost of the block producer, while the term $type(tx) \cdot length(tx)$ covers the opportunity cost of processing one transaction instead of another one in a block.

### Adjustment of fees over time

The demand for transactions is typically quite irregular on blockchains. On one hand, there are peaks of activity at the scale of hours within a day or days within a month. On the other hand, there are long term tendencies. We need a mechanism that automatically updates the transaction fees over time taking these factors into consideration. By the law of supply and demand, raising the fee should decrease the demand, and vice-versa.

To deal with peaks of activity, we face a trade-off between hiking up transaction fees rapidly or potentially having long transaction inclusion times - both undesirable effects. We propose two mechanisms. The first one adjusts the price very quickly, at the same pace as the peaks and valleys of activity. The second one adjusts slowly, at the pace of long term tendencies, and uses tipping to give users the possibility of controlling waiting times at peak hours. We propose to use the slow adjusting mechanism with tips, but provide details of both mechanisms for completeness.

#### 1. Fast adjusting mechanism

In this mechanism the transaction fees vary greatly through time, but are fixed for all users at each block (no tipping).

Recall that we set a hard limit on the sum of lengths and weights of all transactions allowed on a block. We also set a second hard limit, this time on the sum of lengths and weights of "normal" txs (non-operational txs), which is equal to 75% of the first limit.

**Definition.** We define a block's saturation level (relative to normal txs) as a fraction $s$ between 0 and 1 which describes how close the limit on normal txs is from being full. Explicitly, the saturation level of a block $B$ is

$$s(B):=\max\{\frac{\sum_{\text{normal } tx \in B} length(tx)}{\text{normal length limit}}, \frac{\sum_{\text{normal } tx \in B} weight(tx)}{\text{normal weight limit}}\},$$

where the normal length limit (the block length limit on normal transactions) is 75% of the overall length limit, and the normal weight limit is 75% of the overall weight limit.

**Adjustable parameter** Let \(s^*\) be our target block saturation level. This is our desired long-term average of the block saturation level (relative to normal txs). We originally suggest \(s^*=0.25\), so that blocks are 25% full on average and the system can handle sudden spikes of up to 4x the average volume of normal transactions. This parameter can be adjusted depending on the observed volumes during spikes compared to average volumes, and in general it provides a trade-off between higher average fees and longer transaction inclusion times during spikes.

Recall that a transaction fee is computed as $fee(tx) = base\_fee + type(tx) \cdot length(tx) + c_{traffic} \cdot weight(tx)$, for a parameter $c_{traffic}$ that is independent of the transaction. Let \(s\) be the saturation level of the current block. If \(s>s^*\) we slightly increase $c_{traffic}$, and if \(s<s^*\) we slightly decrease it.

**Adjustable parameter:** Let $v$ be a fee variability factor, which controls how quickly the transaction fees adjust. We update $c_{traffic}$ from one block to the next as follows:

$$c_{traffic} \leftarrow c_{traffic}\cdot (1+ v(s-s^*) + v^2(s-s^*)^2/2).$$

This is thus a feedback loop with multiplicative weight updates. It is a very good approximation to using the more involved update \(c_{traffic} \leftarrow c_{traffic}\cdot e^{v(s-s^*)}\), which in turn has the following properties:

* Assuming that $v$ is small, the relative change of parameter $c_{traffic}$ is approximately proportional to the difference $(s-s^*)$, i.e.

$$\frac{c_{traffic}^{new} - c_{traffic}^{old}}{c_{traffic}^{old}}\approx v(s-s^*).$$

* If there is a period of time during which \(k\) blocks are produced and the average saturation level is \(s_{average}\), the relative change of parameter $c_{traffic}$ during this period is approximately proportional to $k$ times the difference $(s_{average} - s^*)$, i.e.

$$\frac{c_{traffic}^{final} - c_{traffic}^{initial}}{c_{traffic}^{initial}}\approx vk(s_{average}-s^*).$$

How to choose the variability factor $v$? Suppose that we decide that the fees should not change by more than a fraction $p$ during a period of $k$ blocks, even if there is 100% saturation in that period. We obtain the formula

$$ \text{fees relative change} \leq \frac{c_{traffic}^{final} - c_{traffic}^{initial}}{c_{traffic}^{initial}}\approx vk(s_{average}-s^*) \leq vk(1-s^*)\leq p,$$

which gives us the bound $v\leq \frac{p}{k(1-s^*)}$.

For instance, suppose that we detect that during peak times some transactions have to wait for up to $k=20$ blocks to be included, and we consider it unfair to the user if the fees increase by more than 5% $(p=0.05)$ during that period. If \(s^*=0.25\) then the formula above gives $v\leq 0.05/[20(1-0.25)]\approx 0.0033$.

#### 2. Slow adjusting mechanism

In this mechanism, fees stay almost constant during short periods, adjusting only to long-term tendencies. We accept the fact that during spikes there will be long inclusion times, and allow the transactions to include tips to create a market for preferential inclusion.

We use the same formula as above to update the transaction fees in each block, i.e. \(c_{traffic} \leftarrow c_{traffic}\cdot (1 + v(s-s^*) + v^2(s-s^*)^2/2\), except that we select a much smaller variability factor $v$. For instance, suppose that we want the fees to change by at most 30% per day, and there are around \(k=14000\) blocks produced in a day. If \(s^*=0.25\) then we obtain \(v\leq 0.3/[14000(1-0.25)] = 0.00003\).

The transaction fee is considered a base price. There will be a different field in the transaction called tip, and a user is free to put any amount of tokens in it or leave it at zero. Block producers receive 100% of the tip on top of the standard 20% of the fee, so they have an incentive to include transactions with large tips. There should be a piece of software that gives live suggestions to users for tip values, that depend on the market conditions and the size of the transaction; it should suggest no tip most of the time.

## Treasury

The system needs to continually raise funds, which we call the treasury. These funds are used to pay for developers that provide software updates, apply any changes decided by referenda, adjust parameters, and generally keep the system running smoothly.

Funds for treasury are raised in two ways:

1.   by minting new tokens, leading to inflation, and
2.   by channelling the tokens from transaction fees and slashings, which would otherwise be set for burning.

Notice that these methods to raise funds mimic the traditional ways that governements raise funds: by minting coins which leads to controlled inflation, and by collecting taxes and fines.

We could raise funds solely from minting new tokens, but we argue that it makes sense to redirect into treasure the tokens from tx fees and slashing that would otherwise be burned:

- By doing so we reduce the amount of actual stake burning, and this gives us better control over the inflation rate (notice that stake burning leads to deflation, and we can’t control or predict the events that lead to burning).

- Following an event that produced heavy stake slashing, goverance might often want to reimburse the slashed stake partially, if there is a bug in the code or there are extenuating circumstances. Thus it makes sense to have the DOTs availabe in treasury, instead of burning and then minting.

- Suppose that there is a period in which there is an unusually high amount of stake burning, due to either misconducts or transaction fees. This fact is a symptom that there is something wrong with the system, that needs fixing. Hence, this will be precisely a period when we need to have more funds available in treasury to afford the development costs to fix the problem.

--
Additional notes

Finality gadget [GRANDPA](https://github.com/w3f/consensus/blob/master/pdf/grandpa.pdf)

Block production protocol [BABE](polkadot/protocols/block-production/Babe.md)

The [NPoS scheme](polkadot/protocols/NPoS/index.md) for selecting validators
