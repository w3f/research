# Polkadot Token

## Introduction

Polkadot will have a native token called dots, which we mint or burn in order to encourage or discourage certain behaviors, respectively. Polkadot is a proof-of-stake chain where a set of validators, who have put down stake, produce blocks and reach consensus.  If a validator steers away from the protocol, some of its dots are slashed, but otherwise it gets paid for participating proportional to the dots it has staked. The set of nodes elected as validators changes constantly, but its number is limited. However, we also encourage general dot holders to participate indirectly in the decision-making processes as nominators, in what we call nominated proof-of-stake. A nominator indicates which validators it trusts, and puts some of its money at stake to support them with, and share any economical rewards or punishments with them. Being a nominator is a way of investing one's tokens, and helping in the security of the system. Indeed, the larger the total amount of dots staked by nominators and validators, the higher the security of the system, because any adversary must first gain enough trust from a large group of users before it can get to be a validator. We therefore aim at having a large percentage of the total token supply be staked by validators and nominators. 

Another large percentage of the token supply will be frozen as deposits by the commercial blockchains who get a parachain slot. We originally aim to have a 3:2:1 distribution for dots, which corresponds to staking (3), parachain deposits (2), and liquidity (1). (Q: How to decide on the optimal distribution ratios? Is 16.6% a healthy level of liquidity? The percentage staked in other projects is: 
- Tezos is 65.73% staked 
- DASH is 58.69% staked
- Lisk is 58.20% staked
- EOS is only 35.49% staked, but that is because its DPoS and the yield is low) 


### Organization

This note contains the following sections.

* **Goverance:** We explain how dot holders express their opinion through referenda and how dots are used to determine voting power.
* **NPoS payment and inflation:** We describe how we reward well-behaving validators and nominators in our nominated proof-of-stake. Since the dot minting for this end is the main cause of inflation in the system, we also describe our inflation model here.
* **Transaction fees:** We analyse the optimal transaction fees on the relay chain to cover for costs, discourage harmful behaviors, and handle eventual peaks of activity and long inclusion times.
* **Adding/removing parachains:** We explain how dots are used when we add or remove commercial parachain slots, in processes such as auctions and deposits.
* **Treasury:** We discuss how and when to raise dots to pay for the continued maintenance of the network.

Finally, in the last section of the note we provide links to additional references about the Polkadot protocol.

## Governance 

The governance system of Polkadot is founded wholly around the idea of stakeholder voting. A key and unfailing rule is: All changes to the protocol must be agreed upon by stake-weighted referendum; the majority of stake can always command the network.

To vote in the governace scheme, a voter must lock their tokens up for at least the enactment delay period beyond the end of the referendum. This is in order to ensure that some minimal economic buy-in to the result is needed and to dissuade vote selling. The amount of token that is locked up as well as the time period impact the weights of everyones vote in the referendum. 

There is no limit to the amount of token that is blocked for voting. 

The governance scheme is described in:
https://github.com/paritytech/polkadot/wiki/Governance



## NPoS payments and inflation

In this section we consider payments to validators and nominators for block production and for Grandpa. We consider only the payments coming from minting new tokens, in normal circumstances. In other words, we do not consider slashings, rewards to fishermen, nor rewards from transaction fees. These will be considered in other sections. 

As these payments are the main driver of inflation in the system, we first study our inflation model.

### Inflation model

Let \(x\) be the *staking rate* in NPoS at a particular point in time, i.e. the total amount of tokens staked by nominators and validators, divided by the total token supply. \(x\) is always a value between 0 and 1. 

__Parameter:__ Let \(\chi_{ideal}\) be the staking rate we would like to attain ideally in the long run. This value is probably between 0.3 and 0.6, and notice that our 3:2:1 rule calls for \(\chi_{ideal}=0.5\). If it falls, the security is compromised, so we should give strong incentives to stake more. If it rises, we lose liquidity, which is also undesirable, so we should decrease the incentives sharply.

Let \(i=i(x)\) be the yearly *interest rate* in NPoS; i.e., the total yearly amount of tokens minted to pay all validators and nominators for block production and Grandpa, divided by the total amount of tokens staked by them. We consider it as a function of \(x\). Intuitively, \(i(x)\) corresponds to the incentive we give people to stake. Hence, \(i(x)\) should be a monotone decreasing function of \(x\), as fewer and fewer incentives are needed when \(x\) increases.

* We study the yearly interest rate (instead of the interest rate per block or per epoch) for ease of comprehension. This means that \(i(x)\) is the total payout perceived by somebody that continuously stakes one unit of tokens during a year. The interest rate per block can be easily computed from it **(Q: do we consider compound interest in this computation? In other words, can the staked parties immediately reinvest their payment into stake?)**
* Not every staked party will be paid proportional to their stake. For instance, a validator will be paid more than a nominator with equal stake, and a validator producing a block will be paid more than other validators. So, \(i(x)\) only works as a guide of the average interest rate.

__Parameter:__ Let \(i_{ideal}:=i(\chi_{ideal})\) be the interest rate we pay in the ideal scenario where \(x=\chi_{ideal}\). This is the interest rate we should be paying most of the time. We suggest the value \(i_{ideal}=0.2\), i.e. an ideal yearly interest rate of 20%.

Let \(I\) be the yearly *inflation rate*; i.e.

$$I=\frac{\text{token supply at end of year} - \text{token supply at begining of year}}{\text{token supply at begining of year}}.$$

The inflation rate is given by

$$I=I_{NPoS}+I_{treasury}+I_{fishermen}-I_{slashing} - I_{tx-fees},$$

where $I_{NPoS}$ is the inflation caused by token minting to pay nominators and validators, $I_{treasury}$ is the inflation caused by minting for treasury, $I_{fishermen}$ is the inflation caused by minting to pay fishermen who detected a misconduct, $I_{slashing}$ is the deflation caused by burning following a misconduct, and $I_{tx-fees}$ is the deflation caused by burning transaction fees.

* The rewards perceived by block producers from transaction fees (and tips) do not come from minting. This is why this term does not appear in the formula above.

$I_{NPoS}$ should be by far the largest of these amounts, and thus the main driver of overall inflation. Notice that by channelling all of the tokens destined to burning -due to both slashing and transaction fees- into treasury, we decrease the other terms in the formula (see the section on treasury). If we consider $I_{NPoS}$ as a function of the staking rate $x$, then clearly the relation between $I_{NPoS}(x)$ and $i(x)$ is given by 

$$I_{NPoS}(x)=x\cdot i(x).$$

From our previous analysis, we can see that $I_{NPoS}(\chi_{ideal})=\chi_{ideal}\cdot i_{ideal}$. Since we want to steer the market toward a staking rate of $x=\chi_{ideal}$, it makes sense that the inflation rate **$I_{NPoS}(x)$ should be maximal at this value**.

__Parameter:__ Let $I_0$ be the limit of $I_{NPoS}(x)$ as $x$ goes to zero. On one hand, this value should be as small as possible, because we want to upper-bound the interest rate. On the other hand, it should not be zero, because we need to make sure to always cover at least the operational costs of the validators, even if nominators get paid nothing. Hence, $I_0$ represents a tight upper-bound on our estimate of the operational costs of all validators, expressed as a fraction of the total token supply. We will make sure that $I_{NPoS}(x)$ is always above $I_0$ for all values of $x$, in particular also in the limit when $x$ goes to one.

For simplicity, we propose that the inflation function grow linearly between $x=0$ and $x=\chi_{ideal}$. On the other hand, we propose that it decay exponentially between $x=\chi_{ideal}$ and $x=1$. We choose an exponential decrease for $I_{NPoS}(x)$ because this implies an exponential decrease for $i(x)$ as well, and we want the interest rate to fall sharply beyond $\chi_{ideal}$ to avoid illiquidity, while still being able to control its rate of change, $i(x+\varepsilon)/i(x)$, when $x$ increases by a small amount $\varepsilon$. Bounding how fast the interest rate changes is important for the nominators and validators. 

__Parameter:__ Define the *decay rate* $d$ so that the inflation rate decreases by at most 50% when $x$ shifts $d$ units to the right of $\chi_{ideal}$, i.e. $I_{NPoS}(\chi_{ideal} + d) \geq I_{NPoS}/2$. We suggest $d=0.05$. 

 From the previous observations, we obtain the following interest rate and inflation rate functions, which depend on the parameters $\chi_{ideal}$, $i_{ideal}$, $d$, and $I_0$. Let

\begin{align}
I_{NPoS}(x) &= \begin{cases}
I_0 + x\Big(i_{ideal} - \frac{I_0}{\chi_{ideal}}\Big) 
&\text{for } 0<x\leq \chi_{ideal}\\
I_0 + (i_{ideal}\cdot \chi_{ideal} - I_0)\cdot 2^{(\chi_{ideal}-x)/d} 
&\text{for } \chi_{ideal} < x \leq 1 
\end{cases}, \text{ and}\\
\\
i(x)&= I(x)/x.
\end{align}

It can be checked that $I_{NPoS}\geq I_0$ for all $0\leq x \leq 1$ with equality for $x=0$, $i(\chi_{ideal})=i_{ideal}$, $I_{NPoS}(x)$ is maximal at $x=\chi_{ideal}$ where it achieves a value of $\chi_{ideal}\cdot i_{ideal}$, and $i(x)$ is monotone decreasing. 

These functions can be plotted following this link: https://www.desmos.com/calculator/2om7wkewhr

As an example, when $I_0=0.025$, $\chi_{ideal}=0.5$, $i_{ideal}=0.2$ and $d=0.05$, we obtain the following plots, with $i(x)$ in red and $I_{NPoS}(x)$ in blue.

![](https://i.imgur.com/Kk1MLJH.png)


### Payment details

There are several protocols that honest validators are involved in, and we incentivize their involvement by either rewarding them for successful participation or slashing them in case of lack of participation, whichever is easier to detect. From this point of view, we decide to reward validators (and their nominators) only for *validity checking* and for *block production*, because they are easy to detect. 

In the branch of validity checking, we reward:
* a parachain validator for each validity statement of the parachain block that it issues.

In the branch of block production, we reward: 
* the block producer for producing a (non-uncle) block in the relay chain,
* the block producer for each reference to a previously unreferenced uncle, and
* the producer of each referenced uncle block.


The ratio between the rewards for each of these actions are parameters to be decided and adjusted by governance. We originally propose ratios of 20:20:2:1, meaning that for some constant $C$ we pay $20C$ for each validity statement, $20C$ for producing a block, $2C$ to the block producer for each referenced uncle, and $C$ to the producer of each referenced uncle. 

Let $P_{NPoS}$ be our target total payout to all validators (and their nominators) per epoch. The value of $P_{NPoS}$ is decided by governance depending on the desired interest rate and inflation rate (see section on inflation model). In order to decide the correct value of constant $C$ that ensures that the total payout is close to target $P_{NPoS}$, we need a mechanism to keep track of the average number of payable actions taking place in an epoch. We propose two mechanisms for it.

**Keeping counters:** In each epoch, we can keep counters $n_{statements}$, $n_{blocks}$ and $n_{uncles}$ respectively on the number of issued validity statements, the number of (non-uncle) blocks produced, and the number of referenced uncles. At the end of the epoch, assuming the $20:20:2:1$ rule, we have the formula

$$P_{NPoS}=20C\cdot n_{statements}+
20C\cdot n_{blocks}+3C\cdot n_{uncles},$$

from which $C$ can be obtained and all the payouts can be computed. That is, assuming we only pay validators at the end of each epoch.

To compute the payouts, we keep counters of all the payable actions that *each* relay chain validator performed in the epoch; the above-mentioned counters are simply the aggregates of all the validators' counters. We also **use these counters to combat unresponsiveness:** If there is a relay chain validator $v$ that has zero payable actions throughout an entire epoch or a certain number of epochs, we kick $v$ out.

(The method above is the one we suggest. The next method is given just for informational purposes.)

**Keeping estimates:** Another option is to keep estimates $e_{statements}$, $e_{blocks}$ and $e_{uncles}$ respectively on the number of issued validity statements, the number of (non-uncle) blocks produced, and the number of referenced uncles *per time slot* (NOT per epoch). The advantage of this mechanism is that it allows us to pay validators in each block, using the formula

$$\frac{P_{NPoS}}{\text{# time slots per epoch}}=20C\cdot e_{statements}+
20C\cdot e_{blocks}+3C\cdot e_{uncles},$$

and from which $C$ and the payouts can be computed in each block. The estimates can be continuously updated, from one block to the next, using an exponential moving average as follows. Suppose we are producing a block $B$ with slot number $t$, having as parent a block $B'$ with slot number $t'$ ($t'<t$). Suppose moreover that $B'$ has estimates \(e'_{statements}\), \(e'_{blocks}\) and \(e'_{uncles}\), and that in block $B$ we identify $u$ uncle references and $s$ validity statements. We then update the estimates for block $B$ as 

\begin{align}
e_{statements}&=p\cdot s + (1-p)^{t-t'}\cdot e'_{statements}, \\
e_{blocks}&=p\cdot 1+(1-p)^{t-t'}\cdot e'_{blocks}, \\
e_{uncles}&=p\cdot u + (1-p)^{t-t'}\cdot e'_{uncles}.
\end{align}

where $p$ is a small parameter (say $p\approx 10^{-4}$) that determines the update speed of these estimates. The intuition behind these updates is as follows. If $s_t$ is the number of validity statements at time slot $t$ (where $s_t=0$ whenever the time slot has no block), then in the long term the value of estimate $e_{statements}$ at time slot $t$ will be a convex combination of all values $(s_{t'})_{t'\leq t}$ with exponentially decreasing weights. Namely,

$$e_{estimate}=p\cdot[s_t + (1-p)\cdot s_{t-1} + (1-p)^2\cdot s_{t-2}+\cdots],$$

and similarly for $e_{blocks}$ and $e_{uncles}$. We suggest to have a somewhat larger parameter $p$ at genesis, so that our estimates converge quickly to realistic values and do not depend heavily on their initializations. However, in the long term $p$ should be small because we want our estimates to react only to long-term trends, and the payments perceived by validators to evolve slowly. At genesis, we initialize these estimates as follows:

\begin{align}
e_{statements} &= m\cdot c \\
e_{blocks} &= c \\
e_{uncles} &= m\cdot [1-(1-c)^{1/m}]-c,
\end{align}

where we recall from the BABE block production model that $c$ is the expected fraction of time slots having at least one leader, and $m\cdot [1- (1-c)^{1/m}]$ is the expected number of leaders per time slot. 

### Distribution of payment within validator slots

Suppose we have m relay chain validators, elected by the NPoS algorithm. A nominator's stake is typically distributed among several validators; however, when it comes to payment we can think of nominators supporting a single validator each, because a nominator's total reward is just the sum of the rewards relative to each validator. So, we think of "validator slots" as a partitioning of the staking parties into m pools, where each validator slot consists of a validator and the nominators supporting it.

The total minting-based payout to validators and nominators is decided globally, having considerations such as the desired inflation rate. This means that these parties don't know in advance exactly how much reward they will get (as they don't know the output of the election algorithm). In the future, we might allow nominators to specify their desired interest rates. We block this feature for the time being to simplify the corresponding NPoS optimization problem.

We take as much of the nominators' available stake as possible; i.e. if a nominator has at least one of its trusted validators elected, all of its available stake will be used. The idea is that the more stake, the more security we have. In contrast, we follow the policy that validator slots are paid equally for equal work, and NOT proportional to their stakes. So if a validator slot A has less stake than another slot B, then the parties in A are paid more per staked token. This should motivate nominators to rapidly adjust their lists of supported validator candidates so that we can achieve a more balanced distribution of stake. It should also help new validator candidates have a better chance to get elected, which is important to ensure decentralization.

Within a validator slot, the payment is as follows: First, validator v receives a fixed amount that was chosen and publicly announced in advance by v. Then, the remainder is shared among all parties (the nominators and v) proportional to their stake. In other words, when it comes to payment the validator v is considered as two entities: a non-staked validator charging a fixed amount, and a staked nominator treated as any other nominator. The validator's fixed payment reflects her operational costs, which must be covered. A higher validator's payment means a smaller payment for her nominators, but as this payment is publicly known in advance, there will be a market where nominators prefer to back validators with smaller costs. On the other hand, validators that have built a reputation of being reliable will likely get away with charging more, as they will still be preferred over other validators. So, for a nominator, supporting riskier validators will be correlated with more rewards, which makes sense.


## Relay-chain transaction fees

We make transaction fees a global parameter to simplify transaction handling logic. 


### How a transaction fee is constituted and split

There will be several types of transactions, with different fee levels. This fee differentiation is used to reflect the different costs in resources incurred by transactions, and to encourage/discourage certain types of transactions. Thus, we need to analyze the resource usage of each type of transaction, to adjust the fees (to be done).

Part of the transaction fee needs to go as a reward to the block producer for transaction inclusion, as otherwise they would have an incentive not to include transactions since smaller blocks are faster to produce, distribute and incorporate in chain. However, the block producer should not be rewarded the full amount of the fee, so they are discouraged from stuffing blocks. How much of the tx fee goes to the block producer is an adjustable parameter via governance; we originally suggest 20%, and suggest that the other 80% go to treasury (instead of burning) to keep better control of inflation/deflation). This percentage might depend on the transaction type, to encourage the block producer to include certain tx types without necessarily increasing the fee. 

There will be an additional space in each block that is reserved only for crucial or urgent transactions, so that they can be included even if the block is full. Fishermen txs that report misbehaviours would be an example of crucial transaction.

A transaction fee includes a base fee and a variable fee that is proportional to the number of bytes to be put on chain. That is,

$$f(tx):=f_{base}+size(tx)\cdot f_{byte},$$

for some parameters $f_{base}$ and $f_{byte}$ and where $size(tx)$ is the number of bytes of transaction. The base fee will depend on the type of transaction, while the per-byte fee may be the same for all types.

### Adjustment of fees over time

The demand for transactions is typically quite irregular on blockchains. On one hand, there are peaks of activity at the scale of hours within a day or days within a month. On the other hand, there are long term tendencies. We need a mechanism that automatically updates the transaction fees over time taking these factors into consideration. By the law of supply and demand, raising the fee should decrease the demand, and vice-versa.

To deal with peaks of activity, we face the dilemma of hiking up transaction fees rapidly or having long transaction inclusion times - both undesirable effects. We propose two mechanisms. The first one adjusts the price very quickly, at the same pace as the peaks and valleys of activity. The second one adjusts slowly, at the pace of long term tendencies, and uses tipping to deal with long queues at peak hours. We propose to use the slow adjusting mechanism with tips, but provide details of both mechanisms for completeness.

#### 1. Fast adjusting mechanism

In this mechanism the transaction fees vary greatly through time, but are fixed for all users at each block (no tipping).

Recall that a transaction fee is computed as $f(tx)=f_{base}+size(tx)\cdot f_{byte}$, for some parameters $f_{base}$ and $f_{byte}$, and where $size(tx)$ is the number of bytes in transaction. For simplicity, we fix the ratio between $f_{base}$ and $f_{byte}$ and scale both parameters by the same factor when adjusting over time. So it is enough to describe how we adjust $f_{byte}$.

__Parameter:__ Let \(s^*\) be our target block saturation level. This is a value between 0 and 1 that we select to be the desired long-term average of the saturation level of blocks. We originally suggest \(s^*=0.25\), so that blocks are 25% full on average and the system can handle sudden spikes of up to 4x the average volume of transactions. This parameter can be adjusted depending on the observed volumes during spikes compared to average volumes, and in general it provides a trade-off between higher average fees and longer transaction inclusion times during spikes.

Let \(s\) be the saturation level of the current block. If \(s>s^*\) we slightly increase the transaction fees, and if \(s<s^*\) we slightly decrease them. 

**Parameter:** Let $v$ be a fee variability factor, which controls how quickly the transaction fees adjust. We update the per-byte transaction fee $f_{byte}$ from one block to the next as follows:

$$f_{byte} \leftarrow f_{byte}\cdot (1+ v(s-s^*) + v^2(s-s^*)^2/2).$$

This is thus a feedback loop with multiplicative weight updates. It is a very good approximation to using the more involved update \(f_{byte} \leftarrow f_{byte}\cdot e^{v(s-s^*)}\), which in turn has the following properties:

* Assuming that $v$ is small, the relative change in fees is approximately proportional to the difference $(s-s^*)$, i.e.

$$\frac{f_{byte}^{new} - f_{byte}^{old}}{f_{byte}^{old}}\approx v(s-s^*).$$ 

* If there is a period of time during which \(k\) blocks are produced and the average saturation level is \(s_{average}\), the relative change in fees during this period is approximately proportional to $k$ times the difference $(s_{average} - s^*)$, i.e.

$$\frac{f_{byte}^{final} - f_{byte}^{initial}}{f_{byte}^{initial}}\approx vk(s_{average}-s^*).$$

How to choose the variability factor $v$? Suppose that we decide that the fees should not change by more than a fraction $p$ during a period of $k$ blocks, even if there is 100% saturation in that period. We obtain the formula

$$\frac{f_{byte}^{final} - f_{byte}^{initial}}{f_{byte}^{initial}}\approx vk(s_{average}-s^*) \leq vk(1-s^*)\leq p,$$

which gives us the bound $v\leq \frac{p}{k(1-s^*)}$.

For instance, suppose that we detect that during peak times some transactions have to wait for up to $k=20$ blocks to be included, and we consider it unfair for the user if the fees increase by more than 5% $(p=0.05)$ during that period. If \(s^*=0.25\) then the formula above gives $v\leq 0.05/[20(1-0.25)]\approx 0.0033$.

#### 2. Slow adjusting mechanism

In this mechanism, fees stay almost constant during short periods, adjusting only to long-term tendencies. We accept the fact that during spikes there will be long inclusion times, and allow the transactions to include tips to create a market for preferential inclusion.

We use the same formula as above to update the transaction fees in each block, i.e. \(f_{byte} \leftarrow f_{byte}\cdot (1 + v(s-s^*) + v^2(s-s^*)^2/2\), except that we select a much smaller variability factor $v$. For instance, suppose that we want the fees to change by at most 30% during a day, and there are around \(k=10000\) blocks produced in a day. If \(s^*=0.25\) then we obtain \(v\leq 0.3/[10000(1-0.25)] = 0.00004\).

The transaction fee is considered a base price. There will be a different field in the transaction called tip, and a user is free to put any amount of tokens in it or leave it at zero. Block producers can charge both the fee and tip, so they have an incentive to include transactions with large tips. There should be a piece of software that gives live suggestions to users for tips values, that depend on the market conditions and the size of the transaction; it should suggest no tip most of the time.

## Adding and removing parachains

The tentative plan for parachain allocation is described [here](https://github.com/w3f/research/blob/master/docs/polkadot/Parachain%20Allocation.md)

## Treasury

The system needs to continually raise funds, which we call the treasury. These funds are used to pay for developers that provide software updates, apply any changes decided by referenda, adjust parameters, and generally keep the system running smoothly.

Funds for treasury are raised in two ways:

1.   by minting new tokens, leading to inflation, and
2.   by channelling the tokens set for burning from transaction fees and slashing.

Notice that these methods to raise funds mimic the traditional ways that governements raise funds: by minting coins which leads to controlled inflation, and by collecting taxes and fines.

We could raise funds solely from minting new tokens, but we argue that it makes sense to redirect into treasure the tokens from tx fees and slashing that would otherwise be burned:

- By doing so we reduce the amount of actual stake burning, and this gives us better control over the inflation rate (notice that stake burning leads to deflation, and we can’t control or predict the events that lead to burning).

- Following an event that produced heavy stake slashing, we might often have to reimburse the slashed stake, if there is evidence of no wrongdoing. Thus it makes sense to have the dots availabe in treasury, instead of burning and then minting.

- Suppose that there is a period in which there is an unusually high amount of stake burning, due to either misconducts or transaction fees. This fact is a symptom that there is something wrong with the system, that needs fixing. Hence, this will be precisely a period when we need to have more funds available in treasury to afford the development costs to fix the problem.

--
Additional notes

Finality gadget [GRANDPA](https://github.com/w3f/consensus/blob/master/pdf/grandpa.pdf)

The [availability scheme](availability.md)

Block production protocol [BABE](BABE/Babe.md)

[Parachain Validity](validity.md) scheme

The [NPoS scheme](1.%20An%20introduction%20to%20the%20validator%20election%20problem.md) for selecting validators
