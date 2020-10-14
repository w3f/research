====================================================================

**Authors**: Jonas Gehrlein

**Last updated**: 14.10.2020

====================================================================

# Validator selection

Validator selection is a tedious and demanding task. nominators need to invest substantial cognitive resources to evaluate the various available validators and process all information to come up with a satisfactory selection. To help nominators with that challenge, we can provide an algorithm which learns the user's preferences and, based on that, give a recommendation on an optimal selection.

# Problem
In addition to the issue that nominators have limited cognitive resources, it is not desirable to provide an exogenous recommendation on a good set of validators. One reason is that it is outside our competence to decide on various trade-offs of the selection process on behalf of nominators. This means, the preferences of nominators (e.g. risk-preferences) are quite different for individual nominators. To illustrate this issue, consider the following example:

| | Commission | Self-Stake | Identity | Era-Points |
| -------- | -------- | -------- | -------- | -------- |
| Validator 1     | 4%     | 26 DOTs     | Yes | Average |
| Validator 2 | 7% | 280 DOTs | No | Average - 1%|
| Validator 3 | 1% | 1 DOT | No | Average + 5% |

All validators in the table have different profiles, where none is pareto-dominated (i.e. there is no Validator which is worse in every dimension than another). Validator 3 potentially yield high profits but does not have much self-stake (skin-in-the-game) and is without registered identity. Validator 1 charges a higher fee for their service but leverages a registered identity. Validator 2 requires substantial fees but has the most skin-in-the-game. We could easily think of different preferences of users who would prefer any one of those validators. While probably every user could make a choice from that table, the problem gets increasingly difficult for a table with 200-1000 validators.


## Requirements on an algorithm
As mentioned before, we cannot and do not want to give an exogenous recommendation to the users. We prefer a method which uses some user input and generates a recommendation based on their stated preferences.

# Solution: UTAStar

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

$$u(\textbf{g}) = \sum_{i=1}^{n} u_i(g_i)$$ 
where $\textbf{g}$ is a vector of performances. with the following constraints:

$$\sum_{i=1}^{n} u_i(g^\star) = 1 \; \text{and} \; u_i(g_{i\star}) = 0 \; \forall i = 1,2,...,n$$

where $u_i, i=1,2...,n$ are non decreasing valued functions which are normalized between 0 and 1 (also called utility functions).

Thereby the value of each alternative $x \in X_L$:
$$ u'[\textbf{g}(x)]=\sum_{i=1}^{n}u_i[g_i(x)])+ \sigma^{+}(x) + \sigma^{-}(x) \forall x \in X_L$$
where $\sigma^{+}(x)$ and $\sigma^{-}(x)$ are the under- and overestimation error. is a potential error relative to $u'[\textbf{g}(x)]$

The corresponding utility functions are defined in a piecewise linear form to be estimated by linear interpolation. For each criterion, the interval $[g_{i\star}, g_i^\star]$ is cut into $(\alpha_i - 1)$ intervals and the endpoints $g_i^j$ are given by:

$$g_i^j = g_{i\star} + \frac{j - 1}{\alpha_i - 1} (g_i^\star - g_{i\star}) \forall j = 1,2,...\alpha_i$$

The marginal utility function of x is approximated by linear interpolation and thus for $g_i(x) \in [g_i^j - g_i^{j+1}]$

$$ u_i[g_i(x)]= u_i(g_i^j) + \frac{g_i(x)-g_i^j}{g_i^{j+1}-g_i^j}[u_i(g_i^{j+1}) - u_i(g_i^j)]$$

The learning set $X_L$ is rearranged such that $x_1$ (best) is the head and $x_m$ is the tail (worst). This ranking is given by the user.

$$\Delta(x_k, x_{k+1}) = u'[\textbf{g}(x_k)] - u'(\textbf{g}(x_{k+1}))$$
then we can be sure that the following holds:

$$ \Delta(x_k, a_{k+1}) \geq \delta \; \textrm{iff} \; x_k > x_{k+1}$$ and
$$ \Delta(x_k, x_{k+1}) = \delta \; \textrm{iff} \; x_k \backsim x_{k+1}$$ 

where $\delta$ is a small and positive number which is an exogenous parameter set as the minimum discrepancy between the utilities of two consecutive options.
In order to ensure monotonicity we further transform the utility differences between two consecutive interval endpoints:

$$ w_{ij} = u_i(g_i^{j+1}) - u_i(g_i^j) \geq 0 \forall i=1,...n \; and \; j = 1,... \alpha_i -1 $$

### Algorithm
**Step 1**: Express the global value of the alternatives in the learning set $u[g(x_k)], k=1,2,...m$ in terms of marginal values $u_i(g_i)$ and then transform to $w_{ij}$ according to the above mentioned formula and by means of

$$ u_i(g_i^1) = 0 \; \forall i = 1,2...n$$ and
$$ u_i(g_i^j) = \sum^{j-1}_{i=1}w_{ij} \; \forall i = 1,2..N \; and \; j=2,3,...\alpha_i - 1$$

**Step 2**: Introduce two error functions $\sigma^{+}$ and $\sigma^{-}$ on $X_L$ by writing each pair of consecutive alternatives as:

$$\Delta(x_k,x_k+1) = u[\textbf{g}(x_k)] - \sigma^{+}(x_k) + \sigma^{-}(x_k) - u[\textbf{g}(x_{k+1})] + \sigma^{+}(x_{k+1}) - \sigma^{-}(x_{k+1})$$

**Step 3**: Solve the linear problem:

$$[min] z = \sum_{k=1}^{m}[\sigma^{+}(x_k) + \sigma^{-}(x_k)] \\
\text{subject to} \\
\Delta(x_k, a_{k+1}) \geq \delta \; \textrm{iff} \; x_k > x_{k+1} \\ 
\Delta(x_k, x_{k+1}) = \delta \; \textrm{iff} \; x_k \backsim x_{k+1} \; \forall k \\
\sum_{i=1}^n \sum_{j=1}^{\alpha_i - 1}w_{ij} = 1 \\
w_{ij} \geq 0, \sigma^{+}(x_k)\geq 0, \sigma^{-}(x_k)\geq 0 \forall i,j,k$$

**Step 4**: Robustness analysis to find find suitable solutions for the above LP. 

**Step 5**: Apply utility functions to the full set of validators and return the 16 best scoring ones.

**Step 6**: Make some ad hoc adjustments to the final set (based on input of the user). For example:
* include favorites
* at most one validator per operator
* at least X inactive validators
* etc.


### Remaining Challenges
There remain a few challenges when we want to apply the theory to our validator selection problem. 
1) One challenge is how to construct the learning set. The algorithm needs sufficient information to generate the marginal utility functions.
    * Find methods to guarantee performance dispersion of the different criteria.
    * Use machine learning approaches to iteratively provide smaller learning sets which gradually improve the information gathered.
    * Potentially use simulations to simulate a wide number of learning sets and all potential rankings on them to measure which learning set improves the information the most.
2) UTAStar assumes piece-wise linear monotone marginal utility functions. Other, methods improve on that but might be more difficult to implement.


