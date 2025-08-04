---
title: Validator selection
---

![](validator-selection.png)

Validator elections play a critical role in securing the network, placing nominators in charge of selecting the most trustworthy and competent validators. This responsibility is both complex and demanding. The vast amount of validator data, constantly growing, requires significant technical expertise and sustained engagement. As a result, the process can become overly cumbersome, leading many nominators to either avoid staking altogether or refrain from investing the time needed to evaluate the data thoroughly. In this context, effective tools are essential, not only to support nominators in making informed selections, but also to help ensure the network's long-term health and resilience. 

This note outlines several potential steps to support nominators while preserving their freedom of choice. As a starting point, it is important to highlight why recommendations should consider individual user preferences rather than attempting to make them universal.

**Problem.** Providing an exogenous recommendation for a set of validators is not advisable, as user preferences, particularly risk preferences, vary significantly. Comparing metrics accross different scales, such as self-stake in DOTs versus performance in percentage, is not feasible in an exogenous framework. Moreover, even when considering a single dimension, the shape of marginal utility functions remains unclear and is inherently tied to individual preferences. Determining the trade-offs involved in the selection process on behalf of nominators lies beyond the scope of this note. But to illustrate this issue, consider the following simple example:

| | Commission | Self-Stake | Identity | Era-Points |
| -------- | -------- | -------- | -------- | -------- |
| Validator 1     | 4%     | 26 DOTs     | Yes | Average |
| Validator 2 | 7% | 280 DOTs | No | Average - 1%|
| Validator 3 | 1% | 1 DOT | No | Average + 5% |

The table presents validators with diverse profiles, none of which clearly dominate. Validator 3 may offer high potential profits but lacks significant self-stake (skin-in-the-game) and does not have a registered identity. Validator 1 charges a higher service fee, yet may benefit from a reputable identity. Validator 2 has the highest self-stake, but also demands substantial fees. Clearly, user preferences can vary, some may favor one validator over another depending on their priorities. While most users could reasonably make a choice from this small set, the complexity increases dramatically when faced with a selection of 200 to 1,000 validators.


**Code of conduct for recommendations.** As previously mentioned, the goal is not to provide exogenous recommendations to users, but rather to offer strategies that respect user insight and generate suggestions aligned with their stated preferences. While valuing individual preferences, recommendations may gently nudge decisions toward outcomes beneficial for the network, such as promoting decentralization. These recommendations should remain as objective as possible and must not discriminate against any specific validator.  

**Organization.** This note is divided into several sections. "Underlying data" presents potentially useful data and explains how to derive additional metrics. "Filtering Phase" demonstrates how a simple concept from economics can significantly reduce the number of potentially interesting validators, providing users with a more manageable set of choices. The third section explores ideas to further curate the validator set in support of the network's goals. Lastly, the "UTAStar" section outlines a sophisticated approach for estimating each user's individual marginal preference functions, enabling more precise recommendations.


# 1. Underlying Data
This section examines collectible data from Polkadot and Kusama validators relevant to the selection process. Metrics marked with an asterisk (*) are included in the final data-set, while other variables are used to derive additional metrics. The primary focus is on quantitative on-chain data, as it is verifiable and straightforward to process. This purely quantitative approach intends to complement a selection process that incorporates qualitative factors, such as a validator’s identity, reputation, or community engagement, which often influence how nominators cast their votes.

## Retrievable data
| Name 	| Historical 	| On-Chain 	| Description 	|
|-	|-	|-	|-	|
| Public Address* 	| No 	| Yes 	| The public identifier of the validator. 	|
| Identity* 	| No 	| Yes 	| Is there a verified on-chain identity? 	|
| Self-stake* 	| No 	| Yes 	| Tokens used for self-election represent a form of "skin in the game". 	|
| Other-Stake 	| No 	| Yes 	| The amount of stake (potentially) allocated stake by other nominators. 	|
| Total-Stake 	| No 	| Yes 	| The combined total of self-stake and other-stake. 	|
| Commission 	| Maybe 	| Yes 	| The percentage of commission taken by the validator for their service. 	|
| Era Points 	| Yes 	| Yes 	| The number of points accumulated per era.  	|
| Number of Nominators* 	| No 	| Yes 	| The number of nominators assigned to a validator. 	|

**Era Points** are awarded to validators for performing beneficial actions that support the network, primarily driven by block production. Over time, these points should be uniformly distributed, although distribution may vary if validators operate on superior setups, like more powerful hardware or more reliable internet connections. In addition, randomness may introduce significant statistical noise in the short term, leading to deviations from a uniform distribution.



## Generated metrics
Some of the retrieved on-chain data might not be particularly useful for nominators, but it can still provide additional metrics that help in the selection process.

| Name 	| Historical 	| On-Chain 	| Description 	|
|-	|-	|-	|-	|
| Average Adjusted Era-Points 	| Yes 	| Yes 	| The average adjusted era points from previous eras.  	|
| Performance 	| Yes 	| Yes 	| Validator performance is determined by era points and commission. 	|
| Relative Performance* 	| Yes 	| Yes 	| This represents performance normalized across the set of validators. 	|
| Outperforming MLE 	| Yes 	| Yes 	| An indicator of how frequently a validator has outperformed the average era points. A typical validator should score around 0.5. 	|
| Average Performer* 	| - 	| Yes 	| A statistical test of the MLE for outperformance against a uniform distribution. It indicates whether a validator statistically overperforms or underperforms. 	|
| Active Eras* 	| Yes 	| Yes 	| The number of active eras. 	|
| Relative total stake* 	| No 	| Yes 	| Total stake normalized across the validator set. 	|
| Operator Size* 	| No 	| Yes 	| The number of validators that share a similar on-chain identity. 	|

**Average Adjusted Era Points.**
To obtain a more robust estimate of the era points, additional data from previous eras should be collected. Since the total era points are distributed among all active validators, and the validator set may vary over time, this could introduce bias into the results. To correct for this, era points from each era can be adjusted based on the active set size during that period. As this is the sole factor influencing theoretical per-capita era points, such normalization enables meaningful comparison across historical data.

The optimal number of previous eras to include remains uncertain. Using too long a history may bias results toward the average, while too short a history can weaken the metric’s robustness. One possible approach is to use the average number of $active-eras$. 

**Performance.** From a nominator's perspective, validator performance is determined by three main factors: the number of era points earned, the nominator's share of the total stake, and the commission charged by the validator. Since performance scales linearly with the nominator's bond, it can be considered independent of the bond amount. These metrics can be combined into a single performance indicator:

$$
performance = \frac{averageEraPoints \times (1 - commission)}{totalStake}
$$

The **relative performance** is then simply defined by: 
$$
\frac{performance - min(performance)}{max(performance) - min(performance)}
$$
These calculations offer a more intuitive measure, as the performance is normalized between 0 and 1. The measure remains robust against potential changes within the network. For instance, when the number of validators increases, the era points per validator tend to decrease. The metric also avoids false anchoring effects.

**Outperforming MLE.** By collecting historical era-points per validator accross previous eras, one can determine how frequently a validator outperforms the average. Assuming a uniform distribution of era points, a validator is expected to outperform the average approximately 50% of the time. In practice, other factors like hardware-setup and internet connectivity, can influence this performance metric. These insights not only help nominators identify top-performing validators but also encourage validators to optimize their setup.

**Significance MLE.** Given that the expected value of the outperforming MLE is 0.5 under a presumably uniform distribution, a statistical test can be conducted to assess whether a validator significantly overperforms or underperforms relative to this benchmark: 
$$
z = \frac{outperformingMLE - 0.5}{\sqrt{\frac{0.5 \times (1-0.5)}{numberActive}}}
$$

If $z > 1.645$, the respective validator significantly outperforms at the 10% significance level, while $z < -1.645$ indicates significant underperformance.

**Operator Size.** Based on the identity of a validator, it is possible to estimate how many validators are operated by the same entity. For users and the network, a reduced number of moderately sized operators is often the most convenient. Selecting validators from larger operators may increase the risk of superlinear slashing, as these entities likely follow similar security practices. The failure of one validator could therefore imply the failure of several others, increasing superlinearly the likelihood of punishment. On the other hand, larger operators may have more sophisticated setups and processes, which could mitigate such risks. This metric should ultimately be considered an objective measure, leaving the final judgment to the user.  

# 2. Filtering Phase

## Dominance-Filtering
After shaping the dataset elaborated in the section "Underlying Data," it is time to begin reducing the set of validators to ease the information load for nominators. One approach is to eliminate dominated validators. Since qualitative judgements remian out of the picture, such as determining whether one "identity" is better or worse than another, it is reasonable to remove validators that are objectively inferior, as there is no rational basis for nominating them. A validator is said to dominate another when all properties are equal and at least one is strictly better. Consider the following example:

## Example:
| Number 	| Public Address 	| Identity 	| Self-stake 	| Nominators 	| Relative Performance 	| Outperformer 	| Active Eras 	| Operator Size 	|
|-	|-	|-	|-	|-	|-	|-	|-	|-	|
| 1 	| 1N6xclmDjjA 	| 0 	| 10 	| 10 	| 0 	| 0 	| 3 	| 0 	|
| 2 	| 1ohS7itG5Np 	| 0 	| 200 	| 40 	| 0.7 	| 0 	| 4 	| 2 	|
| 3 	| 1xgFnMhdOui 	| 1 	| 100 	| 89 	| 0.3 	| 0 	| 16 	| 3 	|
| 4 	| 1vO7JLtSm4F 	| 1 	| 5000 	| 89 	| 1 	| 1 	| 29 	| 3 	|

Validator 2 dominates Validator 1, meaning the latter is strictly worse in every dimension[^1]. Validator 3 also dominates Validator 1, so it can be removed from the set. Through this process, the validator set can be reduced to two. In practice, this method proves to be a powerful tool for significantly shrinking the set size.

## Further curation 
Additional cleanup can still be performed on the remaining set. As stated in the code of conduct, this step is optional, yet here are some suggested default actions for users:
* Include at least one inactive validator. We may suggest inactive nodes based on separate processes.
* Reduce the risk of super-linear slashing, for instance by removing multiple validators run by the same operator.
* Remove validators running on the same machine (some analysis of IP addresses possible?).

# 3. Manual selection
After reducing the set by removing dominated validators and applying some filtering options, the user can easily select preferred validators manually. In this step, the selection is purely based on personal preferences. For example, a nominator might order the validators by their relative performance, and select those who also meet certain minimum self-stake requirements.


# 4. UTAStar
As input, this method uses the filtered table from Section LINK and can be considered a natural extension of the previous method.
### Overview
 UTilité Additive (UTA) is a preference disaggregation method introduced by [Jacquet-Lagrèze & Siskos (1982)](https://www.sciencedirect.com/science/article/abs/pii/0377221782901552). UTAStar is an enhanced version of the original algorithm. The core idea is that the marginal utility functions of a decision maker (DM), defined over each dimension of a given criterion, can be inferred from a priori ranked lists of alternatives. The method employs linear programming to indentify utility functions that respect the DM's initial ranking while incorporating additional properties, such as normalizing the maximum utility to 1.

### Some notation
**This write-up relies heavily on [Siskos et al., 2005](https://www.researchgate.net/publication/226057347_UTA_methods)**
* $u_i$: Marginal utility function of criterion i.
* $g_1,g_2,...g_n$: Criteria.
* $g_i(x)$: Evaluation of alternative x on the $i^{th}$ criterion.
* $\textbf{g}(x)$: Vector of performances of alternative $x$ across $n$ criteria.
* $x_1, x_2, ..., x_m \in X_L:$ Learning set containing alternatives presented to the decision maker (DM) for ranking. Note that the index on the alternative is dropped.


### Model
The UTAStar method infers an additive utility function with equal weighting across criteria:

$$
u(\textbf{g}) = \sum_{i=1}^{n} u_i(g_i)
$$

where $\textbf{g}$ is a vector of performances, subject to the following constraints:

$$
\sum_{i=1}^{n} u_i(g^\star) = 1 \; \text{and} \; u_i(g_{i\star}) = 0 \; \forall i = 1,2,...,n
$$

Each $u_i, i=1,2...,n$ is a non-decreasing function normalized between 0 and 1, also referred to as a utility function.

The estimated utility of each alternative $x \in X_L$ is given by:
$$
u'[\textbf{g}(x)]=\sum_{i=1}^{n}u_i[g_i(x)])+ \sigma^{+}(x) + \sigma^{-}(x) \forall x \in X_L
$$
where $\sigma^{+}(x)$ and $\sigma^{-}(x)$ and represent the underestimation and overestimation errors, respectively, each reflecting potential deviation in the estimation of $u'[\textbf{g}(x)]$

The utility functions are approximated in piecewise linear form using linear interpolation. For each criterion, the interval $[g_{i\star}, g_i^\star]$ is divided into $(\alpha_i - 1)$ subintervals, and the endpoints $g_i^j$ are defined as:

$$
g_i^j = g_{i\star} + \frac{j - 1}{\alpha_i - 1} (g_i^\star - g_{i\star}) \forall j = 1,2,...\alpha_i
$$

The marginal utility function of x is approximated by linear interpolation. Thus, for $g_i(x) \in [g_i^j - g_i^{j+1}]$, we have:

$$
u_i[g_i(x)]= u_i(g_i^j) + \frac{g_i(x)-g_i^j}{g_i^{j+1}-g_i^j}[u_i(g_i^{j+1}) - u_i(g_i^j)]
$$

The learning set $X_L$ is rearranged such that $x_1$ (the best alternative) is placed at the head and $x_m$ is the tail. This ranking is provided by the user. The utility difference between two consecutive alternatives is defined as:

$$
\Delta(x_k, x_{k+1}) = u'[\textbf{g}(x_k)] - u'(\textbf{g}(x_{k+1}))
$$

then the following holds:

$$ 
\Delta(x_k, a_{k+1}) \geq \delta \; \textrm{iff} \; x_k > x_{k+1}
$$

and

$$
\Delta(x_k, x_{k+1}) = \delta \; \textrm{iff} \; x_k \backsim x_{k+1}
$$ 

Here, $\delta$ is a small, positive, exogenous parameter representing the minimum acceptable discrepancy between the utilities of two consecutive options.
To enforce monotonicity, we further transform the utility differences between two consecutive interval endpoints:

$$
w_{ij} = u_i(g_i^{j+1}) - u_i(g_i^j) \geq 0 \forall i=1,...n \; and \; j = 1,... \alpha_i -1
$$

### Algorithm
**Step 1.** Express the global utility of the alternatives in the learning set $u[g(x_k)], k=1,2,...m$, in terms of marginal utility functions $u_i(g_i)$. Transform these into coefficients $w_{ij}$ according to the formula provided, using the following constraints:

$$
u_i(g_i^1) = 0 \; \forall i = 1,2...n
$$

and

$$
u_i(g_i^j) = \sum^{j-1}_{i=1}w_{ij} \; \forall i = 1,2..N \; and \; j=2,3,...\alpha_i - 1
$$

**Step 2.** Introduce two error functions, $\sigma^{+}$ and $\sigma^{-}$, on the learning set $X_L$. Represent each pair of consecutive alternatives as:

$$
\Delta(x_k,x_k+1) = u[\textbf{g}(x_k)] - \sigma^{+}(x_k) + \sigma^{-}(x_k) - u[\textbf{g}(x_{k+1})] + \sigma^{+}(x_{k+1}) - \sigma^{-}(x_{k+1})
$$

**Step 3.** Solve the following linear optimization problem:

$$
[min] z = \sum_{k=1}^{m}[\sigma^{+}(x_k) + \sigma^{-}(x_k)] \\
\text{subject to} \\
\Delta(x_k, a_{k+1}) \geq \delta \; \textrm{iff} \; x_k > x_{k+1} \\ 
\Delta(x_k, x_{k+1}) = \delta \; \textrm{iff} \; x_k \backsim x_{k+1} \; \forall k \\
\sum_{i=1}^n \sum_{j=1}^{\alpha_i - 1}w_{ij} = 1 \\
w_{ij} \geq 0, \sigma^{+}(x_k)\geq 0, \sigma^{-}(x_k)\geq 0 \forall i,j,k
$$

**Step 4.** Perform a robustness analysis to identify suitable solutions for the linear program (LP) described aboveabove. 

**Step 5.** Apply the derived utility functions to the full set of validators and select the 16 highest-scoring ones.

**Step 6.** Introduce ad hoc adjustments to the final set based on user-defined preferences. For example:
* Include user-designated favorites
* Ensure no more than one validator per operator
* Require at least X inactive validators
* Additional custom constraints as needed


### Remaining Challenges
Several challenges remain in applying the theoretical framework to the validator selection problem:

1. **Constructing the learning set** The algorithm requires sufficient information to generate the marginal utility functions. Key subchallenges include:
   - Developing methods that ensure performance dispersion across criteria.
   - Applying machine learning techniques to iteratively construct smaller learning sets to gradually improve the collected information.
   - Using simulations to generate a wide number of learning sets and corresponding rankings, enabling evaluation of which configurations most effectively improve utility estimation. 
2. **Limitations of UTAStar** UTAStar assumes piecewise linear and monotonic marginal utility functions. While alternative methods offer improvements in this regard, they may introduce additional implementation complexity. 


[^1]: As mentioned above, a user might prefer larger operators in which case the statement would not be true.

**For inquieries or questions, please contact** [Jonas Gehrlein](/team_members/Jonas.md)

