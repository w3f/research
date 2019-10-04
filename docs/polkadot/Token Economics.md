====================================================================

**Authors**: Alfonso Cevallos, Fatemeh Shirazi (minor)

**Last updated**: 04.10.2019

====================================================================

# Token Economics

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

* **NPoS payment and inflation:** We describe how we reward well-behaving validators and nominators in our nominated proof-of-stake. Since the DOT minting for this end is the main cause of inflation in the system, we also describe our inflation model here.
* **Transaction fees:** We analyse the optimal transaction fees on the relay chain to cover for costs, discourage harmful behaviors, and handle eventual peaks of activity and long inclusion times.
* **Treasury:** We discuss how and when to raise dots to pay for the continued maintenance of the network.

Finally, in the last paragraph of the note we provide links to additional relevant references about the Polkadot protocol.

## NPoS payments and inflation

We consider here payments to validators and nominators for their participation in the protocols of block production (BABE) and finality (GRANDPA). We consider only the payments coming from minting new tokens, in normal circumstances. In particular we do not consider slashings, rewards to misconduct reporters and fishermen, or rewards from transaction fees. These will be considered in other sections.

As these payments are the main driver of inflation in the system, we first study our inflation model.

### Inflation model

Let \(x\) be the *staking rate* in NPoS at a particular point in time, i.e. the total amount of tokens staked by nominators and validators, divided by the total token supply. \(x\) is always a value between 0 and 1.

__Adjustable parameter:__ Let \(\chi_{ideal}\) be the staking rate we would like to attain ideally in the long run. This value should probably lie between 0.3 and 0.6, and we originally set it at \chi_{ideal}=0.5\. If it falls, the security is compromised, so we should give strong incentives to DOT holders to stake more. If it rises, we lose liquidity, which is also undesirable, so we should decrease the incentives sharply.

Let \(i=i(x)\) be the yearly *interest rate* in NPoS; i.e., the total yearly amount of tokens minted to pay all validators and nominators for block production and Grandpa, divided by the total amount of tokens staked by them. We consider it as a function of \(x\). Intuitively, \(i(x)\) corresponds to the incentive we give people to stake. Hence, \(i(x)\) should be a monotone decreasing function of \(x\), as less incentive is needed when \(x\) increases.

* We study the yearly interest rate (instead of the interest rate per block or per epoch) for ease of comprehension. This means that \(i(x)\) is the total payout perceived by somebody that continuously stakes one DOT during a year. The interest rate per block can be easily computed from it. **(Q: do we consider compound interest in this computation? In other words, can the staked parties immediately reinvest their payment into stake?)**
* Not every staked party will be paid proportional to their stake. For instance, a validator will be paid more than a nominator with equal stake, and a validator producing a block will be temporarily paid more than a validator not producing a block. So, \(i(x)\) only works as a guide of the average interest rate.

__Adjustable parameter:__ Let \(i_{ideal}:=i(\chi_{ideal})\) be the interest rate we pay in the ideal scenario where \(x=\chi_{ideal}\). This is the interest rate we should be paying most of the time. We suggest the value \(i_{ideal}=0.2\), i.e. an ideal yearly interest rate of 20%.

Let \(I\) be the yearly *inflation rate*; i.e.

$$I=\frac{\text{token supply at end of year} - \text{token supply at begining of year}}{\text{token supply at begining of year}}.$$

The inflation rate is given by

$$I=I_{NPoS}+I_{treasury}-I_{slashing} - I_{tx-fees},$$

where $I_{NPoS}$ is the inflation caused by token minting to pay nominators and validators, $I_{treasury}$ is the inflation caused by minting for treasury, $I_{slashing}$ is the deflation caused by burning following a misconduct, and $I_{tx-fees}$ is the deflation caused by burning transaction fees.

* The rewards perceived by block producers from transaction fees (and tips) do not come from minting, but from tx senders. Similarly, the rewards perceived by reporters and fishermen for detecting a misconduct do not come from minting but from the slashed party. This is why these terms do not appear in the formula above.

$I_{NPoS}$ should be by far the largest of these amounts, and thus the main driver of overall inflation. Notice that by channelling all of the tokens destined to burning -due to both slashing and transaction fees- into treasury, we decrease the other terms in the formula (see the section on treasury). If we consider $I_{NPoS}$ as a function of the staking rate $x$, then clearly the relation between $I_{NPoS}(x)$ and $i(x)$ is given by

$$I_{NPoS}(x)=x\cdot i(x).$$

From our previous analysis, we can see that $I_{NPoS}(\chi_{ideal})=\chi_{ideal}\cdot i_{ideal}$. Since we want to steer the market toward a staking rate of $x=\chi_{ideal}$, it makes sense that the inflation rate **$I_{NPoS}(x)$ should be maximal at this value**.

__Adjustable parameter:__ Let $I_0$ be the limit of $I_{NPoS}(x)$ as $x$ goes to zero (i.e. when neither validators nor nominators are staking any DOTs). The value of $I_0$ shoud be close to zero but should not be zero, because we need to make sure to always cover at least the operational costs of the validators, even if nominators get paid nothing. Hence, $I_0$ represents an estimate of the operational costs of all validators, expressed as a fraction of the total token supply. We will make sure that $I_{NPoS}(x)$ is always above $I_0$ for all values of $x$, in particular also in the limit when $x$ goes to one.

For simplicity, we propose that the inflation function grow linearly between $x=0$ and $x=\chi_{ideal}$. On the other hand, we propose that it decay exponentially between $x=\chi_{ideal}$ and $x=1$. We choose an exponential decrease for $I_{NPoS}(x)$ because this implies an exponential decrease for $i(x)$ as well, and we want the interest rate to fall sharply beyond $\chi_{ideal}$ to avoid illiquidity, while still being able to control its rate of change, $i(x+\varepsilon)/i(x)$, when $x$ increases by a small amount $\varepsilon$. Bounding how fast the interest rate changes is important for the nominators and validators.

__Adjustable parameter:__ Define the *decay rate* $d$ so that the inflation rate decreases by at most 50% when $x$ shifts $d$ units to the right of $\chi_{ideal}$, i.e. $I_{NPoS}(\chi_{ideal} + d) \geq I_{NPoS}/2$. We suggest $d=0.05$.

 From the previous discussion, we propose the following interest rate and inflation rate functions, which depend on the parameters $\chi_{ideal}$, $i_{ideal}$, $I_0$ and $d$. Let

\begin{align}
I_{NPoS}(x) &= \begin{cases}
I_0 + x\Big(i_{ideal} - \frac{I_0}{\chi_{ideal}}\Big)
&\text{for } 0<x\leq \chi_{ideal}\\
I_0 + (i_{ideal}\cdot \chi_{ideal} - I_0)\cdot 2^{(\chi_{ideal}-x)/d}
&\text{for } \chi_{ideal} < x \leq 1
\end{cases}, \text{ and}\\
\\
i(x)&= I_{NPoS}(x)/x.
\end{align}

It can be checked that $I_{NPoS}\geq I_0$ for all $0\leq x \leq 1$ with equality for $x=0$, $i(\chi_{ideal})=i_{ideal}$, $I_{NPoS}(x)$ is maximal at $x=\chi_{ideal}$ where it achieves a value of $\chi_{ideal}\cdot i_{ideal}$, and $i(x)$ is monotone decreasing.

These functions can be plotted following this link: https://www.desmos.com/calculator/2om7wkewhr

As an example, when $I_0=0.025$, $\chi_{ideal}=0.5$, $i_{ideal}=0.2$ and $d=0.05$, we obtain the following plots, with $i(x)$ in green and $I_{NPoS}(x)$ in blue.

![](https://i.imgur.com/Kk1MLJH.png)


### Payment details

There are several protocols that honest validators are involved in, and we reward their successful participation or slash their lack thereof (whichever is easier to detect). From this point of view, we decide to reward validators (and their nominators) only for *validity checking* and for *block production*, because they are easy to detect.

In the branch of validity checking, we reward:

* a parachain validator for each validity statement of the parachain block that it issues.

In the branch of block production, we reward:

* the block producer for producing a (non-uncle) block in the relay chain,
* the block producer for each reference to a previously unreferenced uncle, and
* the producer of each referenced uncle block.

These are thus considered "payable actions". We define a point system where a validator earns a certain amount of points for each payable action executed, and at the end of each era they are paid proportional to their earned points. (The exact DOT value of each point is not known a priori because it depends on the total number of points earned by all validators in a given era. This is because the total payout per era depends on the inflation model established above, and not on the number of payable actions). 

__Adjustable parameter:__ We propose the following point system: 

* 20 points for each validity statement,
* 20 points for each (non-uncle) block produced,
* 2 points (to the block producer) for each reference to a previously unreferenced uncle, and
* 1 point to the producer of each referenced uncle.

Notice that what is important here is not the absolute points but the point ratios, which establish the reward ratios of the payable actions. These points are parameters to be adjusted by governance. 

In each era $e$, and for each validator $v$, we keep a counter $c_v^e$ on the number of points earned by $v$. Let $c^e = 
sum_{\text{validators } v} c_v^e$ be the total number of points earned by all validators in era $e$, and let $P^e_{NPoS}$ be our target total payout to all validators -- and their nominators -- in that era (see previous section on inflation model to see how to establish $P^e_{NPoS}$). Then, at the end of era $e$, the payout corresponding to validator $v$ and his nominators is given by 

$$\frac{c_v^e}{c^e} \cdot P^e_{NPoS}.$$

We remark that we can also use the counters to combat unresponsiveness: if a validator has earned close to zero points in payable actions during an era (or any other period of time being measured), we kick him out. See the note on Slashings for more details.

### Distribution of payment within validator slots

In any given era, a nominator's stake is typically distributed among several validators, e.g. 80% of her stake is assigned to validator 1, 20% to validator 2, 0% to validator 3, etc. This distribution is decided automatically by the NPoS validator election mechanism that runs at the beginning of each era (see notes on NPoS for details). 

However, in what follows we assume for simplicity that 
Suppos
Suppose we have $m$ relay chain validators, elected by the NPoS algorithm. A nominator's stake is typically distributed among several validators; however, when it comes to payment we can think of nominators supporting a single validator each, because a nominator's total reward is just the sum of the rewards relative to each validator. So, we think of "validator slots" as a partitioning of the staking parties into m pools, where each validator slot consists of a validator and the nominators supporting it.

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

The tentative plan for parachain allocation is described [here](Parachain-Allocation.md)

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

The [availability scheme](Availability_and_Validity.md)

Block production protocol [BABE](BABE/Babe.md)

[Parachain Validity](Availability_and_Validity.md) scheme

The [NPoS scheme](NPoS/index.md) for selecting validators
