---
title: Validator selection
---

**Authors**: [Jonas Gehrlein](/team_members/Jonas.md)

**Last updated**: 07.12.2020

## Introduction

The validator elections are essential for the security of the network, where nominators have the important task to evaluate and select the most trustworthy and competent validators. However, in reality this task is quite challenging and comes with significant effort. The vast amount of data on validators (which is constantly increasing) requires a substantial technical expertise and engagement. Currently, the process is too cumbersome and many nominators are either not staking or avoiding spending too much time to go through the large amount of data. Therefore, we need to provide tools, which both aid nominators in the selection process, while still ensuring that the outcome is beneficial for the network. 

The following write-up provides an overview of several potential steps, which benefit the nominators while maintaining their freedom of choice. As a first step, it is helpful to illustrate why recommendations should be based on user's preferences and cannot be universal for all individuals.

### Problem
It is not desirable to provide an exogenous recommendation of a set of validators, because user's preferences (especially risk-preferences) are quite different. Therefore, a comparison between metrics on different scales (e.g., self-stake in DOTs vs. performance in %) is not exogenously not possible. In addition, the shape of the marginal utility functions even within one dimension is unclear and based on individual's preferences. It is outside our competence to decide on various trade-offs of the selection process on behalf of nominators. To illustrate this issue, consider the following simple example:

| | Commission | Self-Stake | Identity | Era-Points |
| -------- | -------- | -------- | -------- | -------- |
| Validator 1     | 4%     | 26 DOTs     | Yes | Average |
| Validator 2 | 7% | 280 DOTs | No | Average - 1%|
| Validator 3 | 1% | 1 DOT | No | Average + 5% |

All validators in the table have different profiles, where none is dominated. Validator 3 potentially yield high profits but does not have much self-stake (skin-in-the-game) and is without registered identity. Validator 1 charges a higher fee for their service but might leverage a reputable identity. Validator 2 requires substantial fees but has the most self-stake. One could easily think of different preferences of users, who would prefer any one of those validators. While probably every user could make a choice from that selection, the problem gets increasingly difficult for a set of 200-1000 validators.


### Code of conduct for recommendations
As mentioned before, we cannot and do not want to give an exogenous recommendation to the users. We prefer methods, which values this insight and generates a recommendation based on their stated preferences. While valuing the preferences of the users, we still can *nudge* their decisions in a direction beneficial for the network (e.g., to promote decentralization). Nevertheless, the recommendation should be as objective as possible and should not discriminate against any specific validator.  

### Organization
Validator selection is divided into several chapters. In the sections "Underlying dataset" (Link), we illustrate which data might be useful and how additional metrics can be generated. Afterwards, we can apply a simple concept from economics to significantly reduce the size of potentially intresting validators. Afterwards,  This is the first step to give users a way to choose at hand. Then, we discuss some ideas to further curate the set of validators to promote goals of the network. As a last section the UTAStar method illustrates a sophisticated approach to estimate the individual marginal preference functions of the user and make a more precise recommendation.


# Underlying Data
This section explains which data can be gathered about validators in Polkadot and Kusama and are relevant for a selection process. Those metrics indicated with a * are used in the final data-set, the other variables are used to generate additional metrics. Currently, we focus on quantitative on-chain data as those are verifiable and easy to process. This purely quantitative approach should be regarded as complementary to a selection process based on qualitative data, where nominators are e.g., voting for validators based on their identity or influence / engagement in the community.

## Retrievable data
| Name 	| Historical 	| On-Chain 	| Description 	|
|-	|-	|-	|-	|
| Public Address* 	| No 	| Yes 	| The public identifier of the validator. 	|
| Identity* 	| No 	| Yes 	| Is there a verified on-chain identity? 	|
| Self-stake* 	| No 	| Yes 	| The amount of tokens used to self-elect. Can be seen as skin-in-the-game. 	|
| Other-Stake 	| No 	| Yes 	| The amount of allocated stake (potentially) by other nominators. 	|
| Total-Stake 	| No 	| Yes 	| The sum of self-stake and other-stake. 	|
| Commission 	| Maybe 	| Yes 	| The amount of commission in % which is taken by the validator for their service. 	|
| Era-Points 	| Yes 	| Yes 	| The amount of points gathered per era.  	|
| Number of Nominators* 	| No 	| Yes 	| The amount of nominators allocated to a validator. 	|

**Era-Points**: The era-points are awarded to a validator for performing beneficial action for the network. Currently this is mainly driven by block production. In general, the distribution of era-points should be uniformly distributed in the long run. However, this can vary if validators operates on a superior setup (stronger machine, more robust internet connection). In addition, there is significant statistical noise from randomness in the short-term, which can create deviations from the uniform distribution.



## Generated metrics
Some of the retrieved on-chain data might be not very useful for nominators or can serve some additional metrics, which help in the selection process.

| Name 	| Historical 	| On-Chain 	| Description 	|
|-	|-	|-	|-	|
| Average Adjusted Era-Points 	| Yes 	| Yes 	| The average adjusted era-points from previous eras.  	|
| Performance 	| Yes 	| Yes 	| The performance of a validator determined by era-points and commission. 	|
| Relative Performance* 	| Yes 	| Yes 	| The performance normalized to the set of validators. 	|
| Outperforming MLE 	| Yes 	| Yes 	| An indicator how often a validator has outperformed the average era-points. Should be 0.5 for an average validator. 	|
| Average Performer* 	| - 	| Yes 	| A statistical test of the outperforming MLE against the uniform distribution. Indicates if a validator statistically over- or underperforms. 	|
| Active Eras* 	| Yes 	| Yes 	| The number of active eras. 	|
| Relative total stake* 	| No 	| Yes 	| The total stake normalized to the set of validators. 	|
| Operator Size* 	| No 	| Yes 	| The number of validators which share a similar on-chain identity. 	|

**Average Adjusted Era-Points**
To get a more robust estimate of the era-points, additional data from previous eras should be gathered. Since the total era-points are distributed among all active validators, and the set of active validators might change, it could bias the results. To counter that, we can adjust the era-points of each era by the active set size of that era. As this is the only biasing factor on the theoretical per-capita era-points, we can thereby make the historic data comparable.

It is unclear how many previous eras should be used as having a too long history might bias the results towards the average while too short of a history diminishes the robustness of the metric. One idea could be to use the average of $active-eras$. 

**Performance**: The performance of a validator from the point of view of a nominator is determined by the amount of era-points gathered by that validator, the nominator's share of the total stake and the commission a validator is charging. In addition, the performance level is linear in the bond of the nominator and is thereby independent from that. We can combine those metrics into one:

$$
performance = \frac{averageEraPoints \times (1 - commission)}{totalStake}
$$

The **relative performance** is then simply defined by: 
$$
\frac{performance - min(performance)}{max(performance) - min(performance)}
$$
This gives a more understandable measure as the performance is normalized between 0 and 1. Additionally, it is robust to potential changes within the network (e.g. with a larger number of validators the era-points are reduced per era) and prevents false anchoring effects.

**Outperforming MLE**: By gathering the historic era-points per validator during past eras, we can calculate how often a validator outperformed the average. As era-points should be distributed uniformly, a validator should outperform the average 50% of times. However, as mentioned before, in reality additional factors as hardware-setup and internet connection can influence this. This helps nominators to select the best performing validators while creating incentives for validators to optimize their setup.

**Significance MLE**: As the expected value of the outperforming MLE is 0.5 and the distribution should be uniformly, we can calculate whether a validator significantly over- or underperforms by: 
$$
z = \frac{outperformingMLE - 0.5}{\sqrt{\frac{0.5 \times (1-0.5)}{numberActive}}}
$$

If $z > 1.645$ we can say that the respective validator outperforms significantly (10% significance level), while $z < -1.645$ indicates significant underperformance.

**Operator Size**: Based on the identity of a validator, we can estimate how many validators are run by the same entity. It is both in the interest of users and the network that there are not too many operators and that those operators are not too large. Selecting validators of larger operators might increase the risk of superlinear slashing, because it is reasonable to assume that those operators follow similar security practices. A failure of one validator might mean a failure of several of those validators which increases the punishment superlinearly. A counter-argument to this might be that larger operators are much more sophisticated with their setup and processes. Therefore, this objective measure should be left to the user to judge.  

# Filtering Phase

## Dominance-Filtering
After constructing the dataset as elaborated in the section "underlying data", we can start reducing the set of validators to reduce the amount of information a nominator has to process. One concept is to remove dominated validators. As we do not make qualitative judgements e.g., which "identity" is better or worse than another, we can remove validators who are inferior to another, since there is no rational reason to nominate them. A validator is dominated by another validator if all her properties are equal and at least one property is worse. Consider the following example:

## Example:
| Number 	| Public Address 	| Identity 	| Self-stake 	| Nominators 	| Relative Performance 	| Outperformer 	| Active Eras 	| Operator Size 	|
|-	|-	|-	|-	|-	|-	|-	|-	|-	|
| 1 	| 1N6xclmDjjA 	| 0 	| 10 	| 10 	| 0 	| 0 	| 3 	| 0 	|
| 2 	| 1ohS7itG5Np 	| 0 	| 200 	| 40 	| 0.7 	| 0 	| 4 	| 2 	|
| 3 	| 1xgFnMhdOui 	| 1 	| 100 	| 89 	| 0.3 	| 0 	| 16 	| 3 	|
| 4 	| 1vO7JLtSm4F 	| 1 	| 5000 	| 89 	| 1 	| 1 	| 29 	| 3 	|

Validator 1 is dominated by Validator 2, which means that it is worse in every dimension (note, as mentioned above a user might prefer larger operators in which case this would not be true). Validator 3 is dominated by Validator 3 and therefore can be removed from the set. By this process the set can be reduced to two validators. In practice, this shows to be quite powerful to vastly reduce the set size.

## Further curation 
Here we have the opportunity to do additional cleanup to the remaining set. As mentioned in the code of conduct, those should be optional but we can suggest default values for users.
* Include at least 1 inactive validator. (we might suggest some inactive nodes based on some other processes.)
* Reduce risk of super-linear slashing (i.e., remove validators from operators).
* Remove validators who run on the same machine (some analysis of IP addresses possible?).

# Manual selection
After the set has been reduced by removing dominated validators and giving some filter option the user can easily select preferred validators manually. In this step, the selection is purely based on personal preferences and for example a nominator might order the validators by their relative performance and select those who also satisfy some requirements on a minimum self-stake.


# UTAStar
This method takes the filtered table from section LINK as input and therefore can be seen as a natural extension to the method before.
## Overview
UTA (UTilité Additive) belongs to the methods of preference disaggregation ([Jacquet-Lagrèze & Siskos, 1982](https://www.sciencedirect.com/science/article/abs/pii/0377221782901552)). UTAStar is an improvement on the original algorithm. The general idea is that the marginal utility functions of a decision makers (DM) on each dimension of an alternative (i.e. criterion) can be deduced from a-priori ranked lists of alternatives. It uses linear programming to search for utility functions which satisfy the initial ranking of the DM while giving other properties (such as the maximum utility is normalized to 1).

### Some notation:
**This writeup relies strongly on [Siskos et al., 2005](https://www.researchgate.net/publication/226057347_UTA_methods)**
* $u_i$: marginal utility function of criteria i.
* $g_1,g_2,...g_n$: Criteria.
* $g_i(x)$: Evaluation of alternative x on the $i^{th}$ crterion.
* $\textbf{g}(x)$: Vector of performances of alternative $x$ on $n$ criteria.
* $x_1, x_2, ..., x_m \in X_L:$ Learning set which contain alternatives presented to the DM to give a ranking on. Note, that the index on the alternative is dropped.


### Model
The UTAStar method infers an unweighted additive utility function:

$$
u(\textbf{g}) = \sum_{i=1}^{n} u_i(g_i)
$$

where $\textbf{g}$ is a vector of performances. with the following constraints:

$$
\sum_{i=1}^{n} u_i(g^\star) = 1 \; \text{and} \; u_i(g_{i\star}) = 0 \; \forall i = 1,2,...,n
$$

where $u_i, i=1,2...,n$ are non decreasing valued functions which are normalized between 0 and 1 (also called utility functions).

Thereby the value of each alternative $x \in X_L$:
$$
u'[\textbf{g}(x)]=\sum_{i=1}^{n}u_i[g_i(x)])+ \sigma^{+}(x) + \sigma^{-}(x) \forall x \in X_L
$$
where $\sigma^{+}(x)$ and $\sigma^{-}(x)$ are the under- and overestimation error. is a potential error relative to $u'[\textbf{g}(x)]$

The corresponding utility functions are defined in a piecewise linear form to be estimated by linear interpolation. For each criterion, the interval $[g_{i\star}, g_i^\star]$ is cut into $(\alpha_i - 1)$ intervals and the endpoints $g_i^j$ are given by:

$$
g_i^j = g_{i\star} + \frac{j - 1}{\alpha_i - 1} (g_i^\star - g_{i\star}) \forall j = 1,2,...\alpha_i
$$

The marginal utility function of x is approximated by linear interpolation and thus for $g_i(x) \in [g_i^j - g_i^{j+1}]$

$$
u_i[g_i(x)]= u_i(g_i^j) + \frac{g_i(x)-g_i^j}{g_i^{j+1}-g_i^j}[u_i(g_i^{j+1}) - u_i(g_i^j)]
$$

The learning set $X_L$ is rearranged such that $x_1$ (best) is the head and $x_m$ is the tail (worst). This ranking is given by the user.

$$
\Delta(x_k, x_{k+1}) = u'[\textbf{g}(x_k)] - u'(\textbf{g}(x_{k+1}))
$$

then we can be sure that the following holds:

$$ 
\Delta(x_k, a_{k+1}) \geq \delta \; \textrm{iff} \; x_k > x_{k+1}
$$

and

$$
\Delta(x_k, x_{k+1}) = \delta \; \textrm{iff} \; x_k \backsim x_{k+1}
$$ 

where $\delta$ is a small and positive number which is an exogenous parameter set as the minimum discrepancy between the utilities of two consecutive options.
In order to ensure monotonicity we further transform the utility differences between two consecutive interval endpoints:

$$
w_{ij} = u_i(g_i^{j+1}) - u_i(g_i^j) \geq 0 \forall i=1,...n \; and \; j = 1,... \alpha_i -1
$$

### Algorithm
**Step 1**: Express the global value of the alternatives in the learning set $u[g(x_k)], k=1,2,...m$ in terms of marginal values $u_i(g_i)$ and then transform to $w_{ij}$ according to the above mentioned formula and by means of

$$
u_i(g_i^1) = 0 \; \forall i = 1,2...n
$$

and

$$
u_i(g_i^j) = \sum^{j-1}_{i=1}w_{ij} \; \forall i = 1,2..N \; and \; j=2,3,...\alpha_i - 1
$$

**Step 2**: Introduce two error functions $\sigma^{+}$ and $\sigma^{-}$ on $X_L$ by writing each pair of consecutive alternatives as:

$$
\Delta(x_k,x_k+1) = u[\textbf{g}(x_k)] - \sigma^{+}(x_k) + \sigma^{-}(x_k) - u[\textbf{g}(x_{k+1})] + \sigma^{+}(x_{k+1}) - \sigma^{-}(x_{k+1})
$$

**Step 3**: Solve the linear problem:

$$
[min] z = \sum_{k=1}^{m}[\sigma^{+}(x_k) + \sigma^{-}(x_k)] \\
\text{subject to} \\
\Delta(x_k, a_{k+1}) \geq \delta \; \textrm{iff} \; x_k > x_{k+1} \\ 
\Delta(x_k, x_{k+1}) = \delta \; \textrm{iff} \; x_k \backsim x_{k+1} \; \forall k \\
\sum_{i=1}^n \sum_{j=1}^{\alpha_i - 1}w_{ij} = 1 \\
w_{ij} \geq 0, \sigma^{+}(x_k)\geq 0, \sigma^{-}(x_k)\geq 0 \forall i,j,k
$$

**Step 4**: Robustness analysis to find find suitable solutions for the above LP. 

**Step 5**: Apply utility functions to the full set of validators and return the 16 best scoring ones.

**Step 6**: Make some ad hoc adjustments to the final set (based on input of the user). For example:
* include favorites
* at most one validator per operator
* at least X inactive validators
* etc.


### Remaining Challenges
There remain a few challenges when we want to apply the theory to our validator selection problem.

1. One challenge is how to construct the learning set. The algorithm needs sufficient information to generate the marginal utility functions.
   - Find methods to guarantee performance dispersion of the different criteria.
   - Use machine learning approaches to iteratively provide smaller learning sets which gradually improve the information gathered.
   - Potentially use simulations to simulate a wide number of learning sets and all potential rankings on them to measure which learning set improves the information the most.
2. UTAStar assumes piece-wise linear monotone marginal utility functions. Other, methods improve on that but might be more difficult to implement.



