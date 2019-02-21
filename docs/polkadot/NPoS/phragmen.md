# Sequential Phragmén Method - the simple version

This note outlines a multiwinner election method introduced by Edvard Phragmén in the 1890's and specified as a sequential greedy algorithm by [Brill et al. (2017)](https://aaai.org/ocs/index.php/AAAI/AAAI17/paper/download/14757/13791), adapted to the problem of electing validators in Polkadot. In particular, we have adapted Brill et al.'s algorithm and proofs to the weighted case. 

We give needed notations in Section 1. In Section 2, we show that this algorithm runs in time 
$$O(m|E|)$$
if each lookup and floating arithmetic operation is considered constant time, where $m$ is the number of elected validators, and $|E|$ is the number of edges in the graph (the sum over the nominators of the number of supported candidates). 

In Section 3, we also show that the elected commitee observes the property of Proportional Justified Representation (PJR), a popular axiom in the area of election theory showing that an election is "fair".

Finally, in Section 4 we propose a post-computation that runs in time $\tilde{O}(m|E|)$ (ignoring logarithmic terms) and computes for the elected set the precise budget distribution that maximizes the minimum stake in the elected committee.

### 1. Notation
 
We follow the notation set on our [hackmd note on the max-min support problem](https://hackmd.io/ICl8_NuHQNyH6hO-cU39Bg). Namely, an instance is given by a bipartite graph $(N\cup V, E)$, where $nv\in E$ represents the approval by nominator $n\in E$ of candidate validator $v$, a vector of nominator budgets $b\in \mathbb{R}_{\geq 0}^N$, and the number $m$ of candidate validators to be elected. We also denote by $V_n\subseteq V$ the  set of candidates supported by nominator $n$, and by $N_v\subseteq N$ the set of nominators that support validator $v$. 

An election is given by the pair $(S,w)$ where $S\subseteq V$ is a group of $m$ elected validators, and $w\in\mathbb{R}_{\geq 0}^E$ is a vector of edge weights where $w_{nv}$ represents the precise amount of stake that nominator $n$ assigns to validator $v$. Besides non-negativity constraints, vector $w$ must observe the budget constraints: $\sum_{v\in V_n} w_{nv} \leq b_n \ \forall n\in N$. 

__Remark__: we do not consider validators to have their own budget. Rather, a validator $v$'s budget can be represented as an additional nominator having said budget and supporting only $v$, and having priority over other nominators to assign load to $v$ in the case that $v$ is elected. This priority can be ensured as a post-computation.


### 2. Algorithm

As a high level intuition, we first find a candidate set $S\subseteq V$ of size $m$, and then find the best edge weight vector $w$ for $S$. In this section we describe the first part of the computation, namely an algorithm that finds a candidate set $S$. It also computes an accompanying feasible weight vector $w$, which is not necessarily good. The post-computation for a better vector $w$ is given in Section 4.

The sequential Phragmén algorithm is described below. 

* Set $S \leftarrow \emptyset, \ 
l_n \leftarrow 0 \ \forall n\in N, \ 
l_v \leftarrow 0 \ \forall v\in V$. 
* For $i=1,\cdots,m$:
    * Update $l_v \leftarrow \frac{1+\sum_{n\in N_v} l_n\cdot b_n}{\sum_{n\in N_v} b_n}$ for each $v\in V\setminus S$ ($l_v$ unchanged for $v\in S$),
    * Let $v_i\in argmin_{v\in V\setminus S} l_v$ and update $S\leftarrow S\cup \{v_i\}$,
    * For each $n\in N_{v_i}$, store $w_{nv_i}\leftarrow (l_{v_i} - l_n)b_n$, and update  $l_n \leftarrow l_{v_i}$ ($l_n$ unchanged for $n\in N\setminus N_{v_i}$),
* Update the weight vector $w\leftarrow w/l_{v_m}$.
* Return set $S$ and edge weight vector $w$.

__Running time__: We assume that each candidate validator has at least one supporter. Each one of the $m$ rounds performs $O(|E|)$ arithmetic operations, because each relation $nv\in E$ is inspected at most twice per round. Hence, assuming that floating operations and table lookups take constant time, the running time of the algorithm is $O(m|E|)$.

__General idea__: The algorithm elects validators sequentially. It executes $m$ rounds, electing a new validator $v_i$ in the $i$-th round, and adding it to set $S$. The algorithm also progressively builds an edge weight vector, defining all weights $\{w_{nv_i}: \ n\in N_{v_i}\}$ of edges incident to $v_i$ as soon as $v_i$ is elected. Finally, the weight vector $w$ is multiplied by a scalar to ensure it observes the budget constraints.

The algorithm keeps track of _scores_ over nominators and validators. For each nominator $n\in N$, $n$'s score is the fraction of its budget $b_n$ that has been used up so far; i.e., $l_n:=\frac{1}{b_n}\sum_{v\in V_n} w_{nv}$. The guiding principle of this heuristic is to _try to minimize the maximum score $l_n$ over all nominators in each round_. Consider round $i$: if a new validator $v_i$ is elected, we assign one unit of support to it, i.e. we define edge weights so that $\sum_{n\in N_{v_i} }w_{nv_i}=1$ (this choice of constant is irrevelant, and will change when vector $w$ is scaled in the last step). These edge weights are chosen so that all supporters of $v_i$ end up with the same score at the end of round $i$, i.e. for all $n'\in N_{v_i}$:
\begin{align}
l_{n'}^{new} 
&= \frac{\sum_{n\in N_{v_i}} l_n^{new}\cdot b_n}{\sum_{n\in N_{v_i}}  b_n} \\
& = \frac{\sum_{n\in N_{v_i}} (l_n^{old}\cdot b_n +w_{nv_i})}{\sum_{n\in N_{v_i}}  b_n} \\
& = \frac{1+ \sum_{n\in N_{v_i}} l_n^{old}\cdot b_n}{\sum_{n\in N_{v_i}}  b_n} =: l_{v_i}.\\
\end{align}

This common nominator score is precisely our definition of validator $v_i$'s score $l_{v_i}$, and the algorithm greedily chooses the validator with smallest score in each round (breaking ties arbitrarily). 

__Proof of correctness__: It remains to show that the chosen edge weights are always non-negative, and that they observe the budget constraints after the last scaling. For this, we need the following lemma, which states that scores never decrease. Let $l_n^{(i)}$ and $l_v^{(i)}$ represent respectively that scores of nominator $n$ and validator $v$ at the end of the $i$-th round. 

__Lemma 1__: $l_v^{(i)}\leq l_v^{(i+1)}$ and $l_n^{(i)}\leq l_n^{(i+1)}$ for each $n\in N$, $v\in S$ and $i<m$.

_Proof_. We prove the inequalities by strong induction on $i$, where the base case $i=0$ is trivial if we set $l_v^{(0)}=l_n^{(0)}:=0$ for each $n$ and $v$. Assume now that all the proposed inequalities hold up to $i-1$.

Validator inequalities: Consider a validator $v_j\in S$. If $j\leq i$, then the identity $l_{v_j}^{(i+1)}=l_{v_j}^i$ follows from the fact that a validator's score doesn't change anymore once it has been elected. Else, if $j>i$, 
$$l_{v_j}^{(i+1)}:=\frac{1+\sum_{n\in N_{v_j} } b_n\cdot l_n^{(i)}}{\sum_{n\in N_{v_j} } b_n} 
\geq \frac{1+\sum_{n\in N_{v_j} } b_n\cdot l_n^{(i-1)}}{\sum_{n\in N_{v_j} } b_n} \geq =:l_{v_j}^{(i)},$$
where we used the nominator inequalities $l_n^{(i-1)}\leq l_n^{(i)}$ assumed by induction hypothesis. This shows the validator inequalities up to $i$.

Nominator inequalities: Consider now a nominator $n$, and assume by contradiction that $l_n^{(i+1)}<l_n^{(i)}$. As $n$'s score has changed in round $i+1$, $n$ must support validator $v_{i+1}$, and so $l_n^{(i+1)}=l_{v_{i+1}}^{(i+1)}$. On the other hand, $l_n^{(i)}=l_n^{(j)} = l_{v_{j}}^{(j)}$ for some $j\leq i$. Putting things together,
$$l_{v_j}^{(j)} = l_n^{(i)} > l_n^{(i+1)} = l_{v_{i+1}}^{(i+1)} \geq l_{v_{i+1}}^{(j)}, $$
where the last inequality follows from validator inequalities up to $i$, which we just proved in the previous paragraph. We conclude that in round $j$, validator $v_{i+1}$ had a strictly smaller score than $v_j$, which contradicts the choice of $v_j$.
$\square$

It easily follows that all edge weights are non-negative. Moreover, using the definition of the nominator scores,  before the final weight scaling the budget inequalities are equivalent to $l_n\leq l_{v_m}$ for each $n\in N$, and this inequality holds because for each $n\in N$ there is an $i\leq m$ such that $l_n=l_{v_i}\leq l_{v_m}$.

### Section 4. Axiomatic properties

In the research literature of approval-based miltiwinner elections, it is common to take an axiomatic approach and define properties of voting methods that are intuitively desirable (see our main reference [Brill et al. (2017)](https://aaai.org/ocs/index.php/AAAI/AAAI17/paper/download/14757/13791), as well as [Sánchez-Fernández et al. (2018)](https://arxiv.org/abs/1609.05370)). These properties apply to the elected committee only, ignoring the edge weights.

For example, a voting method is called _house monotonic_ if, for any instance, the elected candidates are all still elected if the number $m$ of winners is increased. As our algorithm elects validators iteratively, it is trivially house monotonic.

We focus on the property of _proportional justified representation_ (PJR), which establishes that if a group of nominators has sufficient budget, and their preferences are sufficiently aligned, then they must be well represented in the elected committee. More formally, a voting method satifies PJR if for any instance $(N\cup V, E, b, m)$ electing a committee $S$, and any integer $1\leq t\leq m$, there is no nominator subset $N'\subseteq N$ such that
* $\sum_{n \in N'} b_n \geq \frac{t}{m} \cdot \sum_{n \in N} b_n$, 
*  $|\cap_{n\in N'} V_n| \geq t$, and 
*  $|S\cap (\cup_{n\in N'} V_n)| < t$.

Brill et al (2017) proved that the proposed algorithm, sequential Phragmén, satifies PJR,  making it the first known polynomial-time method with this property. We present a proof next.

__Lemma 2:__ Sequential Phragmén satisfies PJR.

_Proof:_ Assume the opposite, hence there is an instance $(N\cup V, E, b, m)$ with output committe $S$, an integer $1\leq t\leq m$ and a nominator subset $N'\subseteq N$ as in the definition above.

For simplicity, we ignore the last scaling of the edge weight vector in the algorithm. Hence, every elected validator in $S$ receives a support of one unit, and the sum of supports over $S$ is $m$. Since we know that each budget constraint is violated by a multiplicative term of at most $l_{v_m}$ (the score of the last added validator), we obtain the bound  
\begin{equation}
l_{v_m}\geq \frac{m}{\sum_{n\in N} b_n}.
\end{equation}
As $l_{v_m}$ is an upper bound on the nominator score $l_n$ for each $n\in N$ (by Lemma 1), and $l_n$ is the proportion of $m$'s budget that's used, the previous inequality is tight only if $l_n = m/\sum_{n\in N} b_n$ for each $n\in N$.

Let $S'=S\cap(\cup_n\in N') V_n$, where $|S|<=t-1$ by hypothesis. Since nominators in $N'$ only need to provide support to validators in $S'$, the sum over $N'$ of used budgets must be smaller than $|S'|$, i.e. 
$$\sum_{n\in N'} l_n\cdot b_n \leq |S'| <= t-1.$$
By a (weighted) average argument, this implies that there is a nominator $n'\in N'$ with score 
$$l_{n'}\leq \frac{\sum_{n\in N'} l_n\cdot b_n}{\sum_{n\in N'} b_n} < \frac{t}{\sum_{n\in N'} b_n} \leq \frac{t}{\frac{t}{m} \sum_{n\in N} b_n} = \frac{m}{ \sum_{n\in N} b_n},$$
where the last inequality is by hypothesis. This implies that the inequality $l_{v_m} > m/\sum_{n\in N} b_n$ is not tight.

Consider now running a new round (round $m+1$) on the algorithm, and fix an unelected validator $v'\in \cap_{n\in N'} V_n$ (which must exist by hypothesis). If we compute the score of $v'$ in this round, we get 
$$l_{v'} = \frac{1+\sum_{n\in N_{v'} } l_n\cdot b_n}{\sum_{n\in N_{v'}} b_n}\leq 
\frac{1+\sum_{n\in N'} l_n\cdot b_n}{\sum_{n\in N'} b_n},$$
where we used the fact that $N'\subseteq N_{v'}$, and that reducing the set of nominators over which the unit support for $v'$ is split can only increase the nominator scores. Using the known upper bound on the nominator, and the known lower bound on the denominator, we obtain 
$$l_{v'}\leq \frac{1+\sum_{n\in N'} l_n\cdot b_n}{\sum_{n\in N'} b_n}
\leq \frac{1 + (t-1)}{\frac{t}{m} \sum_{n\in N} b_n} = \frac{m}{\sum_{n\in N} b_n} < l_{v_m}.$$
This implies that $l_{v_m} > l_{v'} \geq l_{v_{m+1}}$, which contradicts Lemma 1.
$\square$

### Section 4. Post-computation for edge weights

Recall that the axiomatic properties in the previous section are independent of the edge weight vector returned by the algorithm. Hence, we can modify this vector at will while still keeping the properties.

In particular, we can find the weight vector that maximizes the minimum support over the elected set $S$, up to a factor of $(1-\varepsilon)$, in time $O(m|E|\log(\log (k)/\varepsilon))$, following the algorithm described in our [hackmd note on the max-support problem](https://hackmd.io/ICl8_NuHQNyH6hO-cU39Bg), with the only difference that we do not need to perform the inner loop which selects different tentative committees. 



### Section 5. Alistair's analysis.

We now describe a round of the algorithm. Let $S$ be the set of elected candidates so far. In each round we compute for every unelected candidate

$$t_v = \frac{1+ \sum_{n:v \in A_n} l_n s_n}{\sum_{n:v \in A_n} s_n}$$

where $l_n = \max_{v \in A_n \cap E} t_v$ and $l_n=0$ if $A_n \cap E$ is empty. (Note that this definition is not circular since the $l_n$s only depend on the $t_v$ for elected validators.)

Then we elect the candidate with the least $t_v$ and store that value.

After the $m$th round, when we have elected the desired number of candidates $m$, we assign the weights of nominator $n$ with non-empty $A_n \cap E$ to a validator $v \in A_n \cap E$ as follows:

$$w_{n,v} = (s_n/t_{v_{last}}) (t_v - t_{v_{prev}})$$

where $v_{prev}$ is the validator in $A_n \cap E$ that immediately precedes $v$ in order of election and $v_{last}$ is the validator in $A_n \cap E$ that was elected last. If $v$ was elected first in $A_n \cap E$, then take $t_{v_{prev}}=0$.

It is easy to show by induction that the $t_v$ of elected candidates is increasing (but not necessarily strictly). As long as it is the existing elected candidates, then $l_n$ for every nominator and  $t_v$ for unelected candidates increase with time. Since the next candidate to be elected didn't get elected in the last election, its $t_v$ was at least as high as the least elected candidate then and so is still at least as high now.

Thus  $t_v - t_{v_{prev}}$ terms are all non-negative and sum to $t_{v_{last}}$. Hence the $w_{n,v}$ are all non-negative and $\sum_v w_{n,v} = s_n$ for any nominator with $A_n \cap E$ non-empty.


## Incentiving the nominators to distribute the stake for more security

Note that any nominator who nominates any elected validator has all their stake assigned. Nothing stops most of them just voting for one candidate, in which case all stake is assigned, but the security is low. We should try to incentivize nominators to avoid this. One way of doing that would be to compute $s_v = \sum_n w_{n,v}$ for every elected validator, then compute, say, the ($m- \lfloor m/3 \rfloor$)-th highest $s_v$, $s$, then weight the nominators payments by some factor, e.g. paying nominator $n$ proportionally to

$$\sum_v w_{n,v} \cdot \min \{2, 1+ s/s_v\},$$

so any nominator has an incentive to vote for validators in the bottom $1/3$, which would increase security. We can replace $1/3$ with something smaller for Polkadot-style chains or be even more aggressive than a factor of two if necessary

## Implementation and time complexity

Let $V$ be the total bit size of the votes, $c$ the number of candidates and  $m$ as before the number of validators we elect. We claim that the running time $O(V(m+\log \max_n |A_n|))$ or $O(V(m+\log c+\log \max_n |A_n|))$ or $O(V(m + \log \max_n |A_n|)\log c)$ depending on data structure choice. We note that if candidate identifiers are of fixed length then $V \geq (\log_2 c) \sum_n |A_n|$. We store the candidates state in some data structure with O(log c) addition, lookup and update and note that either
* a) we can make the cost of these operations linear in the candidate identifier size, in which case we get O(Vm) time,
* b) after preporcessing, we can store the candidates data in an array, replacing all identifier with indices in the votes, in which case we get $O(V(m+\log c))$ time, or
* c) we can just not bother with such ridiculous optimizations and get $O(Vm \log c)$ time.

After doing this we can do each of the following in one iteration through the vote list
1. compute $\sum_{n: v \in A_n} s_n$ for every candidate who recieves a nomination
2. compute the scores $t_v$ for every unelected candidate in any round or
3. compute $w_n,v$ for each nominator

For 2, we note that we can compute $l_n$ with one iteration through the nominator's votes and $|A_n|$ candidate lookups. Then we can add $l_n s_n/(\sum_{n: v \in A_n} s_n)$ to each unelected validator in $A_n \setminus E$ again in an iteration through the the nominator's votes and $|A_n|$ candidate lookups and updates.

For 3, we'll need to sort $A_n \cap E$ by election order, which will take time $O(|A_n| \log \max_n |A_n|)$. Then we just need to look up $t_v$ for each candidate.

For the incentive thing, we'll need a pass over the votes to compute $\sum_v w_n,v$ for each $v \in E$, then time $O(m \log m)$ to sort the validator list by it. 
