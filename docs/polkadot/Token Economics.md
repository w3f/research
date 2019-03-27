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
* **Slashing:** We enumerate the scenarios where the stake of a validator (and that of nominators supporting it) gets slashed in order to discourage certain negative behaviors. We also describe the rewards given to the "fishermen" who report these misbehaviors.
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

Let $x$ be the *staking rate* in NPoS at a particular point in time, i.e. the total amount of tokens staked by nominators and validators, divided by the total token supply. $x$ is always a value between 0 and 1. 

__Parameter:__ Let $\chi_{ideal}$ be the staking rate we would like to attain ideally in the long run. This value is probably between $0.3$ and $0.6$, and notice that our 3:2:1 rule calls for $\chi_{ideal}=0.5$. If it falls, the security is compromised, so we should give strong incentives to stake more. If it rises, we lose liquidity, which is also undesirable, so we should decrease the incentives sharply.

Let $i=i(x)$ be the yearly *interest rate* in NPoS; i.e., the total yearly amount of tokens minted to pay all validators and nominators for block production and Grandpa, divided by the total amount of tokens staked by them. We consider it as a function of $x$. Intuitively, $i(x)$ corresponds to the incentive we give people to stake. Hence, $i(x)$ should be a monotone decreasing function of $x$, as less and less incentives are needed when $x$ increases.

* We study the yearly interest rate (instead of the interest rate per block or per epoch) for ease of comprehension. This means that $i(x)$ is the total payout perceived by somebody that continuously stakes one unit of tokens during a year. The interest rate per block can be easily computed from it **(Q: do we consider compound interest in this computation? In other words, can the staked parties immediately reinvest their payment into stake?)**
* Not every staked party will be paid proportional to their stake. For instance, a validator will be paid more than a nominator with equal stake, and a validator producing a block will be paid more than other validators. So, $i(x)$ only works as a guide of the average interest rate.

__Parameter:__ Let $i_{ideal}:=i(\chi_{ideal})$ be the interest rate we pay in the ideal scenario where $x=\chi_{ideal}$. This is the interest rate we should be paying most of the time. 

We propose that when $x>\chi_{ideal}$, the interest rate have an exponential decrease. We choose an exponential decrease because we want the interest rate to fall sharply -to avoid illiquidity- while still being able to control its rate of change, $i(x+\varepsilon)/i(x)$, when $x$ increases by a small amount $\varepsilon$. Bounding how fast the interest rate changes is important for the nominators and validators. 

__Parameter:__ Define the *decay rate* $d$ so that the interest rate halfs every time $x$ increases by $d$ units, provided that $x>\chi_{ideal}$. More concretely, if $x=\chi_{ideal}+kd$ for some $k>0$ then $i(x)=i_{ideal}/2^k$.

Let $I$ be the yearly *inflation rate*; i.e.
$$I=\frac{\text{token supply at end of year} - \text{token supply at begining of year}}{\text{token supply at begining of year}}.$$

The inflation rate is given by
$$I=I_{NPoS}+I_{treasury}+I_{fishermen}-I_{slashing} - I_{tx-fees},$$
where $I_{NPoS}$ is the inflation caused by token minting to pay nominators and validators, $I_{treasury}$ is the inflation caused by minting for treasury, $I_{fishermen}$ is the inflation caused by minting to pay fishermen who detected a misconduct, $I_{slashing}$ is the deflation caused by burning following a misconduct, and $I_{tx-fees}$ is the deflation caused by burning transaction fees.

* The rewards perceived by block producers from transaction fees (and tips) do not come from minting. This is why this term does not appear in the formula above.

$I_{NPoS}$ should be by far the largest of these amounts, and thus the main driver of overall inflation. Notice that by channelling some of the tokens destined to burning -due to both slashing and transaction fees- into treasury, we decrease the other terms in the formula (see the section on treasury). If we consider $I_{NPoS}$ as a function of the staking rate $x$, then clearly the relation between $I_{NPoS}(x)$ and $i(x)$ is given by 
$$I_{NPoS}(x)=x\cdot i(x).$$

From our previous analysis, we can see that $I_{NPoS}(\chi_{ideal})=\chi_{ideal}\cdot i_{ideal}$. Since we want to steer the market toward a staking rate of $x=\chi_{ideal}$, it makes sense that the inflation rate $I_{NPoS}(x)$ should be maximal at this value.

__Parameter:__ Let $I_0$ as the limit of $I_{NPoS}(x)$ as $x$ goes to zero. On one hand, this value should be as small as possible, because we want to upper-bound the interest rate. On the other hand, it should not be zero, because we need to make sure to always cover at least the operational costs of the validators, even if nominators get paid nothing. Hence, $I_0$ represents an upper-bound estimate of the operational costs of all validators, expressed as a fraction of the total token supply.


For simplicity, we propose that the inflation function be linear between $x=0$ and $x=\chi_{ideal}$. From the previous observations, we obtain the following interest rate and inflation rate functions, which depend on the parameters $\chi_{ideal}$, $i_{ideal}$, $d$, and $I_0$. Let
\begin{align}
i(x)&=\begin{cases}
\frac{I_0}{x} + i_{ideal} - \frac{I_0}{\chi_{ideal}} 
&\text{for } 0<x\leq \chi_{ideal}\\
i_{ideal}\cdot 2^{(\chi_{ideal}-x)/d} 
&\text{for } \chi_{ideal} < x \leq 1 
\end{cases}, \text{ and}\\
\\
I_{NPoS}(x) = x\cdot i(x) &= \begin{cases}
I_0 + x\Big(i_{ideal} - \frac{I_0}{\chi_{ideal}}\Big) 
&\text{for } 0<x\leq \chi_{ideal}\\
i_{ideal}\cdot x\cdot  2^{(\chi_{ideal}-x)/d} 
&\text{for } \chi_{ideal} < x \leq 1 
\end{cases}.
\end{align}

It can be checked that $I_{NPoS}(0)=I_0$, $i(\chi_{ideal})=i_{ideal}$, $I_{NPoS}(x)$ is maximal at $x=\chi_{ideal}$ where it achieves a value of $\chi_{ideal}\cdot i_{ideal}$, and $i(x)$ is monotone decreasing, halving value every $d$ units for $x>\chi_{ideal}$.

These functions can be plotted following this link: https://www.desmos.com/calculator/dnlxegtgpk
As an example, when $I_0=0.05$, $\chi_{ideal}=0.5$, $i_{ideal}=0.2$ and $d=0.05$, we obtain the following plots, with $i(x)$ in red and $I_{NPoS}(x)$ in blue.
![](https://i.imgur.com/qPzgxsN.png)


### Payment details

There are several protocols that honest validators are involved in, and we incentivize their involvement by either rewarding them for successful participation or slashing them in case of lack of participation, whichever is easier to detect. From this point of view, we decide to reward validators only for *block production* and for *validity checking*, because they are easy to detect. 

Let $P_{NPoS}$ be our target average payment to all validators and nominators per time slot. The value of $P_{NPoS}$ is computed from the interest rate function (see section on inflation model). Then $$P_{NPoS}=P_{production}+P_{validity},$$

where $P_{production}$ and $P_{validity}$ are our target average payments per time slot for block production and for validity checking respectively. We suggest the values 
\begin{align}
P_{production}&=0.1\cdot P_{NPoS}\\
P_{validity}&=0.9\cdot P_{NPoS},
\end{align}

because checking for validity is more critical for the system. (Q: should the ratio between $P_{production}$ and $P_{validity}$ depend on the number of validators?)


#### Block production

Block producers will include information about previously undiscovered uncles in their blocks, and we will reward both the block producer and the producers of the uncles. Let $P_{producer}$ and $P_{uncle}$ be the precise amounts we pay per block to the block producer and to each uncle, respectively. By the random nature of the protocol, the total amout we pay varies all the time, but we want it to be close to $P_{production}$ on average per time slot. Consequently, we first need to estimate the number of block producers and uncles per time slot.

Recall from the block-production protocol that in each time slot there can be no blocks, one block, or several blocks produced, depending on the number of validators that are slot leaders. Each validator $v$ is independently selected as slot leader with probability $1-(1-c)^{\alpha_v}$, where $\alpha_v$ is the relative stake of $v$ as a fraction of all validators' stake, and $c$ is a fixed constant between 0 and 1. If there are $m$ validators and they all have the same probability of becoming a leader then this probability is $1-(1-c)^{1/m}$.

Let $e_{producers}$ be an estimate on the average number of (non-uncle) block producers per time slot, or in other words, the average proportion of time slots with at least one leader. The model above predicts that $e_{producers}=c$, so we initialize the estimate to that value. However, in practice this average might change as not all validators will be online and angaged in the protocol at all times. We update our estimate in each block using an exponential moving average, as follows. Suppose we are producing a block $B$ with slot number $t$, having as parent a block $B'$ with slot number $t'$ ($t'<t$) and estimate $e'_{producers}$. We then define the new estimate for block $B$ as 

$$e_{producers}=p+(1-p)^{t-t'} e'_{producers},$$

where $p$ is a parameter between 0 and 1 that determines the update speed of this estimate (and of other estimates defined below). We suggest a very small parameter $p$, say $p\leq 10^{-4}$, because we want our estimate to ignore random noise and react only to long-term trends, and we want the payments perceived by validators to evolve slowly. To understand the update formula for estimate $e_{producers}$, notice that if $1_t$ is an indicator variable having value 1 if time slot $t$ has at least one block producer and 0 otherwise, then in the long run the estimate at time slot $t$ is 

$$e_{producers}=p\cdot[1_t+(1-p)\cdot 1_{t-1}+(1-p)^2\cdot 1_{t-2}+\cdots].$$

Similarly, we keep track of an estimate $e_{uncles}$ of the average number of uncles per time slot. According to our model, the expected number of blocks per time slot is around $m[1-(1-c)^{1/m}]$, so the expected number of uncles would be $m[1-(1-c)^{1/m}]-c$. We initialize $e_{uncles}$ to that value. However, this value might vary in practice as block producers may not detect all uncles. We update it using again an exponential moving average, as follows. If we are producing a block $B$ at time slot $t$ which has detected $u$ uncles, and its parent block is $B'$ at time slot $t'$ ($t'<t$) having an estimate $e'_{uncles}$, we define the new estimate for block $B$ as

$$e_{uncles}=p\cdot u + (1-p)^{t-t'}\cdot e'_{uncles}.$$

We can now use these estimates to obtain the following formula for the expected total production payment per time slot:
$$P_{production}=e_{producers}\cdot P_{producer} + e_{uncles}\cdot P_{uncle}, $$

where we recall that $P_{producer}$ and $P_{uncle}$ are the payments per block to the block producer and to each uncle, respectively. If, for instance, we set the ratio $P_{producer}=4\cdot P_{uncle}$, the formula above gives $P_{uncle}=P_{production}/(4\cdot e_{producers}+e_{uncles})$. These last two formulas will be our definitions of $P_{uncle}$ and $P_{producer}$, and they will be computed in each block after updating the estimates. As our estimates evolve slowly over time, so do the payment amounts.

#### Validity checking

In each parachain, the group of validators assigned to it have the responsibility of checking the validity of each parachain block and issuing validity statements for it. The block producer of the relay chain will then include these statements from each parachain to its block. We then pay an amount $P_{statement}$ per block to the issuer of each (parachain) validity statement appearing in a relay chain block. We want the amount $P_{statement}$ to evolve slowly and to make the total average payment per time slot be close to $P_{validity}$.

Let $e_{statements}$ be an estimate on the number of validity statements issued per time slot. If there are $m$ relay chain validators, then ideally all $m$ should issue validity statements of the different parachains in each block, so the value of $e_{statement}$ should be $m\cdot e_{producers}=m\cdot c$. We initialize it to that value, and update it using exponential moving averages as follows. If $B$ is the current relay chain validator at time slot $t$ having $s$ validity statements, and its parent is $B'$ at time slot $t'$ ($t'<t$) having an estimate $e'_{statements}$, then the new estimate for $B$ is 
$$e_{statements} = p\cdot s + (1-p)^{t-t'}e'_{statements},$$

for the same parameter $p$ as in block production. The formula for the total average payment per block gives
$$P_{validity} = e_{statements}\cdot P_{statement},$$

and so in each block, after updating $e_{statements}$, we compute the amount $P_{statement}=P_{validity}/e_{statements}$, and pay it to each issuer of a validity statement.

### Distribution of payment within validator slots

Suppose we have m relay chain validators, elected by the NPoS algorithm. A nominator's stake is typically distributed among several validators; however, when it comes to payment we can think of nominators supporting a single validator each, because a nominator's total reward is just the sum of the rewards relative to each validator. So, we think of "validator slots" as a partitioning of the staking parties into m pools, where each validator slot consists of a validator and the nominators supporting it.

The total minting-based payout to validators and nominators is decided globally, having considerations such as the desired inflation rate. This means that these parties don't know in advance exactly how much reward they will get (as they don't know the output of the election algorithm). In the future, we might allow nominators to specify their desired interest rates. We block this feature for the time being to simplify the corresponding NPoS optimization problem.

We take as much of the nominators' available stake as possible; i.e. if a nominator has at least one of its trusted validators elected, all of its available stake will be used. The idea is that the more stake, the more security we have. In contrast, we follow the policy that validator slots are paid equally for equal work, and NOT proportional to their stakes. So if a validator slot A has less stake than another slot B, then the parties in A are paid more per staked token. This should motivate nominators to rapidly adjust their lists of supported validator candidates so that we can achieve a more balanced distribution of stake. It should also help new validator candidates have a better chance to get elected, which is important to ensure decentralization.

Within a validator slot, the payment is as follows: First, validator v receives a fixed amount that was chosen and publicly announced in advance by v. Then, the remainder is shared among all parties (the nominators and v) proportional to their stake. In other words, when it comes to payment the validator v is considered as two entities: a non-staked validator charging a fixed amount, and a staked nominator treated as any other nominator. The validator's fixed payment reflects her operational costs, which must be covered. A higher validator's payment means a smaller payment for her nominators, but as this payment is publicly known in advance, there will be a market where nominators prefer to back validators with smaller costs. On the other hand, validators that have built a reputation of being reliable will likely get away with charging more, as they will still be preferred over other validators. So, for a nominator, supporting riskier validators will be correlated with more rewards, which makes sense.


## Relay-chain transaction fees

We make transaction fees a global parameter to simplify transaction handling logic. 


### How a transaction fee is constituted and split

A transaction fee includes a base fee to cover for signature verification costs and a variable fee that is proportional to the number of bytes to be put on chain. That is,
$$f(tx):=f_{base}+size(tx)\cdot f_{byte},$$
for some parameters $f_{base}$ and $f_{byte}$ and where $size(tx)$ is the number of bytes of transaction.

Part of the transaction fee needs to go as a reward to block producers for transaction inclusion, as otherwise they would have an incentive not to include transactions since smaller blocks are faster to produce, distribute and incorporate in chain. Another part should be burned, to discourage validators from stuffing blocks. The burned proportion should be an adjustable parameter via governance. 
**(Q: what are relevant parameters for deciding the amount that is burned? For a block producer, what should be the ratio between rewards from transaction fees and rewards from minting new tokens?)**

Moreover, fees are determined by transaction type. Allow an additional fee to be given to block producer per transaction type, which can be adjusted by governance. This is to ensure that certain heavier transactions can be made to be included if usually ignored.

Create an additional space for certain transactions in the block that can be included even if the block is full  for some system crucial transactions. For example, fishermen transactions that report misbehaviour or other similar system transactions.

Evaluate all functions to determine the typical resource usage in order to add potential additional fees. 


### Adjustment of fees over time

The demand for transactions is  typically quite irregular on blockchains. On one hand, there are peaks of activity at the scale of hours within a day or days within a month. On the other hand, there are long term tendencies. We need a mechanism that automatically updates the transaction fees over time taking these factors into consideration. By the law of supply and demand, raising the fee should decrease the demand, and vice-versa.

To deal with peaks of activity, we face the dilemma of hiking up transaction fees rapidly or having long transaction inclusion times - both undesirable effects. We propose two mechanisms. The first one adjusts the price very quickly, at the same pace as the peaks and valleys of activity. The second one adjusts slowly, at the pace of long term tendencies, and uses tipping to deal with long queues at peak hours.

#### 1. Fast adjusting mechanism

In this mechanism the transaction fees vary greatly through time, but are fixed for all users at each block (no tipping).

Recall that a transaction fee is computed as $f(tx)=f_{base}+size(tx)\cdot f_{byte}$, for some parameters $f_{base}$ and $f_{byte}$, and where $size(tx)$ is the number of bytes in transaction. For simplicity, we fix the ratio between $f_{base}$ and $f_{byte}$ and scale both parameters by the same factor when adjusting over time. So it is enough to describe how we adjust $f_{byte}$.

__Parameter:__ Let $s^*$ be our target block saturation level. This is a value between 0 and 1 that we select to be the desired long-term average of the saturation level of blocks. We originally suggest $s^*=0.25$, so that blocks are 25% full on average and the system can handle sudden spikes of up to 4x the average volume of transactions. This parameter can be adjusted depending on the observed volumes during spikes compared to average volumes, and in general it provides a trade-off between large average fees and long transaction inclusion times during spikes.

Let $s$ be the saturation level of the current block. If $s>s^*$ we slightly increase the transaction fees, and if $s<s^*$ we slightly decrease them. 

**Parameter:** Let $v$ be a fee variability factor, which controls how quickly the transaction fees adjust. We update the per-byte transaction fee $f_{byte}$ from one block to the next as follows:
$$f_{byte}^{new}= f_{byte}^{old}\cdot e^{v(s-s^*)}$$
This is thus a feedback loop with multiplicative weight updates. It has the following desirable properties.
* Assuming that $v$ is small, the relative change in fees is approximately proportional to the difference $(s-s^*)$, i.e.
$$\frac{f_{byte}^{new} - f_{byte}^{old}}{f_{byte}^{old}}=e^{v(s-s^*)}-1\approx v(s-s^*).$$ 
* If there is a period of time during which the blocks produced have an average saturation level of exactly $s^*$, the per-byte transaction fee will be exactly the same at the beginning and at the end of that period.

How to choose the variability factor $v$? Suppose that we decide that the fees should not change by more than a fraction $p$ during a period of $k$ blocks, even if there is 100% saturation in that period. We obtain the formula
$$\frac{f_{byte}^{final} - f_{byte}^{initial}}{f_{byte}^{initial}}=e^{vk(s_{average}-s^*)}-1\leq e^{vk(1-s^*)} -1 \leq p,$$
which gives us the bound $v\leq \frac{\ln(1+p)}{k(1-s^*)}$.

For instance, suppose that we detect that during peak times some transactions have to wait for up to $k=20$ blocks to be included, and we consider it unfair for the user if the fees increase by more than 5% $(p=0.05)$ during that period. If $s^*=0.25$ then the formula above gives $v\leq \ln(1.05)/[20(1-0.25)]=0.00325$.

#### 2. Slow adjusting mechanism

In this mechanism, fees stay almost constant during short periods, adjusting only to long-term tendencies. We accept the fact that during spikes there will be long inclusion times, and allow the transactions to include tips to create a market for preferential inclusion.

We use the same parameters and the same formula as above to update the transaction fees in each block, i.e. $f_{byte}^{new}= f_{byte}^{old}\cdot e^{v(s-s^*)}$, except that we select a much smaller variability factor $v$, so that fees change by, say, at most 10% daily.

The transaction fee is considered a base price. There will be a different field in the transaction called tip, and a user is free to put any amount of tokens in it or leave it at zero. Block producers can charge both the fee and tip, so they have an incentive to include transactions with large tips. There should be a piece of software that gives live suggestions to users for tips values, that depend on the market conditions and the size of the transaction; it should suggest no tip most of the time.


## Slashing 

Misbehavior in Polkadot is punished by slashing deposited stake. We impose slashing depending on the security impact they have Polkadot and whether it was part of an organized attack. 

Parachain validators get slashed for misbehaving on availability, validation, and being offline. Relay chain validators get slashed for misbehaing in GRANDPA, block production, and availability. We do not slash relay chain validators for being offline currently because their offlineness is GRANDPA and block production has less of a negative impact and is expensive prove. 

Furthermore, fishermen who are responsible to detect and report misbehavior in parachain validation, also have to put down stake. They submit claims of invality and get rewared if confirmed and slashed otherwise.

Next we review slashing for validators (in both roles) and rewarding/slashing of fishermen.  

### Consensus slashing:
We slash relay chain validators for equivocation and incorrect voting without justification. 

For **equivocation we slash ~5% of the misbehaving validator's stake if it happens unorganized and 100% otherwise**. The validator who reported the equivocation is rewarded 10 % of the slashed amount. 

A GRANDPA vote is considered incorrect, if a validator votes for a chain at any given round that does not include a block that could have been finalized in previous rounds. Once this happens any one can challenge the incorrect vote and the validator needs to justify its incorrect vote. The only justifcation would be a proof that at least $n-f$ validators have equivocated or voted incorrectly in previous rounds. This justfication serves as a challenge for those validators, who need to provide justification for the new challenges. This process iterates until $n-f$ validators cannot justify their behavior or $f+1$ validators have equivocated and are going to be slashed for it. 

For **incorrectness without justification we slash 15% of the misbehaving validator's stake if it is unorganized and 100% otherwise**. The validator who reported the incorrect vote without justification is rewarded 10 % of the slashed amount. 

### Block production slashing:

We slash relay chain validators for equivocation and incorrect block production. 
When a block producer equivocates, produces more than one valid block only one of them can be added to the relay chain. The danger is that valid forks are established. The forks will be resolved once the next block producer doesnt equivocate anymore. Hence, equivocation is not a real threat to security as long as the majority of selected block producers dont equivocate. Therefore, we slash the **block producer who equivocates 1 % of his stake**. If a **validator produces an incorrect block it is also slashed 1%**.The validator who reported the equivocation or incorrect block production is rewarded 10 % of the slashed amount. 


### Parachain validation slashing:

We will **slash the parachain validators who signed for the parachain block validity that is not valid, 100% of their stake**.

Once a fisherman has made a claim of invalidity for a parachain blob header, a number of relay chain validators are going to investigate this claim. If these validator agree on the claim, eiher the parachain validators or the fisherman will be slashed. If a single parachain blob header has both signed claims by validators that it is valid and that it is invalid, then all validators download the block and check its correctness.

When relay chain validators disagree:
- If 1/3 validators sign to say it is incorrect and we do not have 1/3 signed saying it is correct as well, then we slash all validators who signed to say it is correct. If this includes a majority of parachain validators, then **they should be slashed 100%**.

- If over 1/3 sign to say it is correct but at most 1/3 to say that it is incorrect, then we **slash all validators who said it was incorrect 100 % of their stake**. 

- If both happen, we consider the block invalid but don’t slash anyone. This can only happen if either we have 1/3 malicious validators or the state transition validation function is ambiguous on this input.  

### Availability slashing: 

Every parachain validator who signed off on the Merkle root is responsible for the correct construction and distribution of erasure coded pieces.

Parachain validators can cause unavailability by either not distributing the erasure coded pieces or sending out pieces that cannot reconstruct a parachain blob. Hence, we slash parachain validators when
a) a proof is submitted that $f+1$ erasure coded pieces of a blob cannot reconstruct the blob, or 
b) $\frac{2}{3}$ relay chain validators claim they have not received an erasure coded piece for that blob. 

Note, that if one or the minority of parachain validator misbehaves, the remainder parachain validators can guarantee availability. Hence, is a) or b) happens the majority of parachain validators are simultanously misbehaving. 
In cases of a), it is an obvious attack and we **slash the misbehaving parachain validators who signed off on the blob header 100% of its stake**. In case of b), the security of Polkadot is not harmed and the only consequence is delay in finality and extra effort for carrying out attestion games. Moreover, there is a very small chance that the majority of parachain validators have, for example, all crashed at the same time. Hence, in case of b), we **slash the parachain validators who signed off on the blob header 10 % of their stake**. 
The entity who reported a), the assigned validator, is rewarded 10 % of the slashed amount. 

Each relay chain validator is responsible to keep the erasure coded piece it has received and only vote in GRANDPA if the erasure coded piece is available to him. 

Once, a number of relay chain validators claim they have not received erasure coded pieces, all relay chain validators who voted in GRANDPA are requested to hand over their piece. We slash a relay chain validator who refuses to hand over the erasure coded piece of a parachain blob after it has voted for the relay chain block that includes the header of that parachain blob. This is proven by all relay chain validators asking for that piece and $\frac{2}{3}$ of relay chain validators reporting they have not received it. We **slash the misbehaving relay chain validator 100 % of their stake**. 

When a blob is unavailable we carry out an attestion game to prove b). We **slash the relay chain validators who attested to an unavailable block 100%  of their stake**. Basically this are the minority who voted different then the $\frac{2}{3}$ of realy chain validators. The entity who reported it is rewarded 10% of the slashed amount. 

### Offlineness slashing: 
We want to encourage onlineness for validators at all time. In particular, for parachain validators being offline has a significant impact on the security of the parachain, therefore, we measure offlineness with responsiveness of validators for their parachain duties. If a parachain validator did not validate a parachain blob, within a certain time frame it needs to either challenge availability or validity otherwise it is considered unresponsive. If **offlineness happens for the first time we slash the unresponsive parachain validator a very small amount, e.g., 0.001 % of its stake**. However, if this happens in more than one consecutive rounds the slasing amount increases until a pre-set threshold (that can be set by the validator itself). Once the threshold is reached we kick the parachain validator out until it becomes responsive again. 

If **offlineness happens simultaneously in mass, we slash a significant amount, e.g., 100 % of their stake**. 



## Adding and removing parachains 

The tentative plan for parachain allocation is described in:
https://github.com/w3f/research/blob/master/docs/polkadot/ParachainAllocation.md


## Treasury 

The system needs to continually raise funds, which we call the treasury. These funds are used to pay for developers that provide software updates, apply any changes decided by referenda, adjust parameters, and generally keep the system running smoothly.

Funds for treasury are raised in two ways:
1. by minting new tokens, leading to inflation, and
2. by channelling some of the tokens set for burning from transaction fees and slashing.

Notice that these methods to raise funds mimic the traditional ways that governements raise funds: by minting coins which leads to controlled inflation, and by collecting taxes and fines.

We could raise funds solely from minting new tokens, but we argue that it makes sense to redirect some of the stake set for burning into treasury: 
  * By doing so we reduce the amount of actual stake burning, and this gives us better control over the inflation rate (notice that stake burning leads to deflation, and we can't control or predict the events that lead to burning).
  * Suppose that there is a period in which there is an unusually high amount of stake burning, due to either misconducts or transaction fees. This fact is a symptom that there is something wrong with the system, that needs fixing. Hence, this will be precisely a period when we need to have more funds available in treasury to afford the development costs to fix the problem.

-----
## Additional notes
GRANDPA:
https://github.com/w3f/consensus/blob/master/pdf/grandpa.pdf 
 
Availability Scheme:
https://github.com/w3f/research/blob/master/docs/polkadot/availability.md 
 
BABE:
https://github.com/w3f/research/tree/master/docs/polkadot/BABE

Parachain Validity:
https://github.com/w3f/research/blob/master/docs/polkadot/validity.md  
