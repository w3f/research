
\(
   \def\skvrf{\mathsf{sk}^v}
   \def\pkvrf{\mathsf{pk}^v}
   \def\sksgn{\mathsf{sk}^s}
   \def\pksgn{\mathsf{pk}^s}
   \def\skac{\mathsf{sk}^a}
   \def\pkac{\mathsf{pk}^a} 
   \def\D{\Delta}
   \def\A{\mathcal{A}}
   \def\vrf{\mathsf{VRF}}
   \def\sgn{\mathsf{Sign}}
\)

# BABE


## 1. Overview

In Polkadot, we produce relay chain blocks using our
 **B**lind **A**ssignment for **B**lockchain **E**xtension protocol,
 abbreviated BABE.
BABE assigns blocks production slots, according to stake,
 using roughly the randomness cycle from Ouroboros Praos [2].

In brief, all block producers have a verifiable random function (VRF)
keys which they register with locked stake.  These VRFs produce secret
randomness which determines when they produce blocks.  A priori, there
is a risk that block producers could grind through VRF keys to bias
results, so VRF inputs must include public randomness created only
after the VRF key.  We therefore have epochs in which we create fresh
public on-chain randomness by hashing together all the VRF outputs
revealed in block creation during the epoch.  In this way, we cycle
between private but verifiable randomness and collaborative public
randomness.

... TODO ...

In Ouroboros [1] and Ouroboros Praos [2], the best chain (valid chain) is the longest chain. In Ouroboros Genesis, the best chain can be the longest chain or the chain which is forked long enough and denser than the other chains in some interval.  We have a different approach for the best chain selection based on GRANDPA and longest chain.  In addition, we do not assume that all parties can access the current slot number which is more realistic assumption.

## 2. BABE 

In BABE, we have sequential non-overlaping epochs \((e_1, e_2,\ldots)\), each of which consists of a number of sequential block production slots (\(e_i = \{sl^i_{1}, sl^i_{2},\ldots,sl^i_{t}\}\)) up to some bound \(t\).  At the beginning of an epoch, we randomly assign each block production slot to a "slot leader", often one party or no party, but sometimes more than one party.  These assignments are initially secrets known only to the assigned slot leader themselves, but eventually they publicly claim their slots when they produce a new block in one.

Each party \(P_j\) has as *session key* containing at least two types of secret/public key pair:

* a verifiable random function (VRF) key \((\skvrf_{j}, \pkvrf_{j})\), and
* a signing key for blocks \((\sksgn_j,\pksgn_j)\), possibly the same as the VRF key. 

We favor VRF keys being relatively long lived because new VRF keys cannot be used until well after creation and submission to the chain.  Yet, parties should update their associated signing keys from time to time to provide forward security against attackers who might exploit from creating slashable equivocations.  There are more details about session key available [here](https://github.com/w3f/research/tree/master/docs/polkadot/keys).

Each party \(P_j\) keeps a local set of blockchains \(\mathbb{C}_j =\{C_1, C_2,..., C_l\}\).  All these chains have some common blocks, at least the genesis block, up until some height.

We assume that each party has a local buffer that contains the transactions to be added to blocks. All transactions in a block is validated with a transaction validation function.


### BABE with GRANDPA Validators \(\approx\) Ouroboros Praos

BABE is almost the same as Ouroboros Praos [2] except chain selection rule and the slot time adjustment.

In BABE, all validators have same amount of stake so their probability of being selected as slot leaders is equal. Given that we have $n$ validators and relative stake of each party is $\theta = 1/n$  the probability of being selected is

$$p = \phi_c(\theta) = 1-(1-c)^{\theta}$$

where \(c\) is a constant. 

The threshold used in BABE for each validator \(P_i\) is 

$$\tau = 2^{\ell_{vrf}}\phi_c(\theta)$$

where \(\ell_{vrf}\) is the length of the VRF's first output (randomness value).

BABE consists of three phases:

#### 1. Genesis Phase

In this phase, we manually produce the unique genesis block.

The genesis block contain a random number \(r_1\) for use during the first epoch for slot leader assignments, the initial stake's of the stake holders (\(st_1, st_2,..., st_n\)) and their corresponding session public keys (\(\pkvrf_{1}, \pkvrf_{2},..., \pkvrf_{n}\)), \((\pksgn_{1}, \pksgn_{2},..., \pksgn_{n}\)).

We might reasonably set \(r_1 = 0\) for the initial chain randomness, by assuming honesty of all validators listed in the genesis block.  We could use public random number from the Tor network instead however.

TODO: In the delay variant, there is an implicit commit and reveal phase provided some suffix of our genesis epoch consists of *every* validator producing a block and *all* produced blocks being included on-chain, which one could achieve by adjusting paramaters.

#### 2. Normal Phase

We assume that each validator divided their timeline in slots after receiving the genesis block. They determine the current slot number according to their timeline. If a new validator joins to BABE after the genesis block, this validator divides his timeline into slots with the Median algorithm we give in Section 4.

In normal operation, each slot leader should produce and publish a block.  All other nodes attempt to update their chain by extending with new valid blocks they observe.

We suppose each validator \(P_j\) has a set of chains \(\mathbb{C}_j\) in the current slot \(sl_k\) in the epoch \(e_m\).  We have a best chain \(C\) selected in \(sl_{k-1}\) by our selection scheme, and the length of \(C\) is \(\ell\text{-}1\). 

Each validator \(P_j\) produces a block if he is the slot leader of \(sl_k\).  If the first output (\(d\)) of the following VRF is less than the threshold \(\tau\) then he is the slot leader.

$$\vrf_{\skvrf_{j}}(r_m||sl_{k}) \rightarrow (d, \pi)$$

If \(P_j\) is the slot leader, \(P_j\) generates a block to be added on \(C\) in slot \(sl_k\). The block \(B_\ell\) should contain the slot number \(sl_{k}\), the hash of the previous block \(H_{\ell\text{-}1}\), the VRF output  \(d, \pi\), transactions \(tx\), and the signature \(\sigma = \sgn_{\sksgn_j}(sl_{k}||H_{\ell\text{-}1}||d||pi||tx))\). \(P_i\) updates \(C\) with the new block and sends \(B_\ell\).


![ss](https://i.imgur.com/Yb0LTJN.png =250x )



In any case (being a slot leader or not being a slot leader), when \(P_j\) receives a block \(B = (sl, H, d', \pi', tx', \sigma')\) produced by a validator \(P_t\), it validates the block  with \(\mathsf{Validate}(B)\). \(\mathsf{Validate}(B)\) should check the followings in order to validate the block:

* if \(\mathsf{Verify}_{\pksgn_t}(\sigma')\rightarrow \mathsf{valid}\) (signature verification),

* if the party is the slot leader: \(\mathsf{Verify}_{\pkvrf_t}(\pi', r_m||sl) \rightarrow \mathsf{valid}\) and \(d' < \tau_t\) (verification with the VRF's verification algorithm). 

* if \(P_t\) did not produce another block for another chain in slot \(sl\) (no double signature),

* if there exists a chain \(C'\) with the header \(H\),

* if the transactions in $B$ are valid.

If the validation process goes well, \(P_j\) adds \(B\) to \(C'\). Otherwise, it ignores the block.


At the end of the slot, \(P_j\) decides the best chain with the chain selection rule we give in Section 3.




#### 3. Epoch Update

Before starting a new epoch $e_m$, there are certain things to be completed in the current epoch $e_{m-1}$.
* Validators update
* (Session keys)
* Epoch randomness

If there is a validator update in BABE, this update has to be done until the end of the last block of the current epoch $e_{m-1}$ so that they are able to actively participate the block production in epoch $e_{m+2}$. So, any validator update will valid in the BABE after at least two epoch's later.

The new randomness for the new epoch is computed as in Ouroboros Praos [2]: Concatenate all the VRF outputs of blocks in the current epoch $e_{m-1}$ (let us assume  the concatenation is \(\rho\)). Then the randomness in epoch $e_{m+1}$:

$$r_{m+1} = H(r_{m}||m+1||\rho)$$

This also can be combined with VDF output to prevent little bias by the adversaries for better security bounds. BABE is secure without VDF but if we combine VDF with the randomness produced by blocks, we have better parachain allocation.

## 3. Best Chain Selection

Given a chain set \(\mathbb{C}_j\) an the parties current local chain \(C_{loc}\), the best chain algorithm eliminates all chains which do not include the finalized block \(B\) by GRANDPA. Let's denote the remaining chains by the set \(\mathbb{C}'_j\). If we do not have a finalized block by GRANDPA, then we use the probabilistic finality in the best chain selection algorithm (the probabilistically finalized block is the block which is $k$ block before than the last block of $C_{loc}$). 


We do not use the chain selection rule as in Ouroboros Genesis [3] because this rule is useful for parties who become online after a period of time and do not have any  information related to current valid chain (for parties always online the Genesis rule and Praos is indistinguishable with a negligible probability). Thanks to Grandpa finality, the new comers have a reference point to build their chain so we do not need the Genesis rule.


## 4. Relative Time

It is important for parties to know the current slot  for the security and completeness of BABE. Therefore, we show how a party realizes the notion of slots. Here, we assume partial synchronous channel meaning that any message sent by a party arrives at most \(\D\)-slots later. \(\D\) is not an unknown parameter.


Each party has a local clock and this clock does not have to be synchronized with the network. When a party receives the genesis block, it stores the arrival time as \(t_0\) as a reference point of the beginning of the first slot. We are aware of the beginning of the first slot is not same for everyone. We assume that this difference is negligible comparing to \(T\) since there will not be too many validators in the beginning. Then each party divides their timeline in slots. 


**Obtaining Slot Number:** Parties who join BABE after the genesis block released or who lose notion of slot run the following protocol to obtain the current slot number with the Median Algorithm and then updates with the consistency algorithm if it sees a inconsistency with the output of median algorithm after running the consistency algorithm. 


If a party \(P_j\) is a newly joining party, he downloads chains and receives blocks at the same time. After chains' download completed, he adds the valid blocks to the corresponding chains. Assuming that a slot number $sl$ is executed in a (local) time interval $[t_{start}, t_{end}]$ of party $P_j$, we have the following protocols for $P_j$ to output $sl$ and $t \in [t_{start}, t_{time}]$.


**- Median Algorithm:**
The party $P_j$ stores the arrival time $t_i$ of $n$ valid blocks having a slot number $sl_i$ which is greater than  the slot number of the last finalized block (GRANDPA block or if GRANDPA is slower than the probabilistic finality then probabilistically finalized block).
Let us denote the stored arrival times of blocks by \(t_1,t_2,...,t_n\) whose slot numbers are \(sl_1,sl_2,...,sl_n\), respectively. Remark that these slot numbers do not have to be consecutive since some slots may be empty, with multiple slot leaders or the slot leader is offline, late or early. After storing $n$ arrival times, $P_j$ sorts the following list \(\{t_1+a_1T, t_2+a_2T,..., t_n+a_nT_\}\) where $a_i = sl - sl_i$. Here, $sl$ is a slot number that $P_j$ wants to learn at what time it corresponds in his local time. At the end. $P_j$  outputs the median of the ordered list as ($t$) and $sl$. 

![](https://i.imgur.com/yGYw9CL.png)

**Lemma 1:** Asuming that $\D$ is the maximum network delay in terms of slot number and \(\alpha\gamma(1-c)^\D \geq (1+\epsilon)/2\)  where \(\alpha\) is the honest stake and $\gamma\alpha$ is the honest and synchronized parties' stake and $\epsilon \in (0,1)$,  \(sl' - sl \leq \D\) with the median algorithm where $sl'$ the correct slot number of time $t$ with probability 1 - \exp(\frac{\delta^2\mu}{2} where $0 < \delta \leq \frac{\epsilon}{1+\epsilon}$ and $\mu = n(1+\epsilon)/2$.

**Proof:** Let us first assume that more than half of the blocks among $n$ blocks are sent by the honest and synchronized parties and  $t = t_i + a_iT$. Then, it means that more than half of the blocks sent on time. If the block of $sl_i$ is sent by an honest and synchronized party, we can conclude it is sent at earliest at $t_i' \leq t_i - \D T$. In this case, the correct slot number $sl'$ at time $t$ is $sl_i + \lceil\frac{t-t_i'}{T}\rfloor = sl_i + \lceil\frac{t_i + a_iT - t_i'}{T}\rfloor$. If $\D T = 0$, sl' = sl, otherwise $sl' \geq sl_i + \lceil\frac{a_iT + \D T}{T}\rfloor = sl+\D$.

If the median does not corresponds to time derived from an honest and synchronized parties' block, we can say that there is at least one honest and synchronized time after the median because more than half of the times are honest and synchronized.  Let's denote this time by $t_u + a_uT$.  Let's assume that the latest honest one in the ordered list is delayed $\D' \leq \D$ slots. It means that if the median was this one, $sl_u' - sl \leq \D'$ as shown above where $sl_u'$ is the correct slot number of time $t_u + a_uT$. Clearly, $sl \leq sl_u'$. Then, we can conclude that $sl' - sl \leq sl_u' - sl \leq \D' \leq \D$.

Now, we show the probability of having more than half honest and synchronized blocks in $n$ blocks. If \(\alpha\gamma(1-c)^\D \geq (1+\epsilon)/2\), then the blocks of honest and synchronized parties are added to the best chain even if there are $\D$ slots delay (it is discussed in the proof of Theorem 2) with the probability more than $(1+\epsilon)/2$. We define a random variable $X_v \in \{0,1\}$ which is 1 if $t_v$ is the arrival time of an honest and synchronized block. Then the expected number of honest and synchronized blocks among $n$ blocks is $\mu = n(1+\epsilon)/2$. We bound this with the Chernoff bound:

$$\mathsf{Pr}[ \sum_{v = 1}^n X_v \leq \mu(1-\delta)] \leq \exp(\frac{\delta^2\mu}{2}) $$

Given that $0 < \delta \leq \frac{\epsilon}{1+\epsilon}$, $\mu(1-\delta) \geq n/2$, this probability should be negligibly small with a $\delta \approx 1$ in order to have more than half honest and synchronized blocks in $n$ slots.
$$\tag*{\(\blacksquare\)}$$

If $\epsilon \geq 0.1$ and $\delta = 0.09$, the probability of having less than half is less than $0.06$ if $n \geq 1200$.


We give another algorithm called consistency algorithm below. This can be run after the median algorithm to verify or update $t$ later on.

**- Consistency Algorithm:** Let us first define *lower consistent blocks*. Given consecutive blocks \(\{B'_1, B'_2,...,B'_n \in C\) if for each block pair \(B'_u\) and \(B'_v\) which belong to the slots \(sl_u\) and \(sl_v\) (\(sl_u < sl_v\)), respectively are lower consistent for a party \(P_j\), if they arrive on \(t_u\) and \(t_v\) such that \(sl_v - sl_u = \lfloor\frac{t_v - t_u}{T}\rfloor\). We call *upper consistent* if for all blocks \(sl_v - sl_u = \lceil\frac{t_v - t_u}{T}\rceil\). Whenever \(P_j\) receives at least \(k\) either upper or lower consistent blocks, it outputs $t$ and \(sl = sl_u + \lfloor\frac{t-t_u}{T}\rfloor\) where \(sl_u\) is the slot of one of the blocks in the block set.


**Lemma 2:** Assuming that the network delay is at most \(\D\) and the honest parties' stake satisfies the condion in Theorem 2, \(P_j\)'s current slot is at most \(\D\)-behind or $2\D$ -behind of the correct slot $sl'$ at time $t$ (i.e., \(sl' - sl \leq \D\)).

**Proof:** According to Theorem 2, there is at least one block honestly generated by an honest party in \(k\) slot with probability \(1 - e^{-\Omega(k)}\). Therefore, one of the blocks in the lower oe upper consistent blocks belong to an honest party. We do our proof with lower consistent block. The upper consistent one is similar. Let's denote $\hat{\D} = \D$ or $\hat{\D} = 2\D$ 

If \(k\) blocks are lower consistent, then it means that all blocks are lower consistent with the honest block. 

If \(P_j\) chooses the arrival time and slot number of this honest block, then \(sl \leq sl' - \hat{\D}\) because the honest parties' block must arrive to \(P_j\) at most \(\hat{\D}\)-slots later. Now, we need to show that if \(P_j\) chooses the arrival time of a different block which does not have to be produced by an honest and synchronized party, then he is still at most \(\D\)-behind.

Assume that \(P_j\) picks \(sl_v > sl_u\) to compute $sl$ for $t$. We show that this computation is equal to \(sl = sl_u +\lfloor\frac{t - t_u}{T}\rfloor\). We know because of the lower consistency \(sl_v- sl_u = \lfloor\frac{t_v - t_u}{T}\rfloor\). $$sl = sl_v - \lfloor\frac{t_v - t_u}{T}\rfloor + \lfloor\frac{t - t_u}{T}\rfloor = sl_v + \lfloor\frac{t-t_v}{T}\rfloor$$

So \(P_i\) is going to obtain the same \(sl\) and $t$ with all blocks. Similarly, if \(P_i\) picks \(sl_v < sl_u\), he obtains \(sl\)

$$\tag*{\(\blacksquare\)}$$


There are two drawbacks of this protocol. One of drawbacks is that a party may never have \(k\) consistent blocks if an adversary randomly delays some blocks. In this case, \(P_i\) may never has consistent blocks. The other drawback is that if the honest block in $k$-consistent block is not a synchronized party then consistency algorithm performs worse than the median. However, this protocol can be used after the median protocol to update or verify the slot number with the consistency algorithm.  If this party sees $k$-consistent blocks and the slot number $sl'$ obtained with the 
the consistency algorithm is less than slot number obtained from the median protocol, he updates it with $sl'$.



## 5. Security Analysis

(If you are interested in parameter selection based on the security analysis, you can directly go to the next section)
BABE is the same as Ouroboros Praos except the chain selection rule and  slot time extraction. Therefore, we need a new security analysis. 


### Definitions
We give the definitions of  security properties before jumping to proofs.

**Definition 1 (Chain Growth (CG)) [1,2]:** Chain growth with parameters \(\tau \in (0,1]\) and \(s \in \mathbb{N}\) ensures that if the best chain owned by an honest party at the onset of some slot \(sl_u\) is \(C_u\), and the best chain owned by a honest party at the onset of slot \(sl_v \geq sl_v+s\) is \(C_v\), then the difference between the length of \(C_v\) and \(C_u\) is greater or equal than/to \(\tau s\).

**Definition 2 (Chain Quality (CQ)) [1,2]:** Chain quality with parameters \(\mu \in (0,1]\) and \(k \in \mathbb{N}\) ensures that the ratio of honest blocks in any \(k\) length portion of an honest chain is \(\mu\). 

**Definition 3 (Common Prefix)** Common prefix with parameters \(k \in \mathbb{N}\) ensures that any chains \(C_1, C_2\) possessed by two honest parties at the onset of the slots \(sl_1 < sl_2\) are such satisfies \(C_1^{\ulcorner k} \leq C_2\) where  \(C_1^{\ulcorner k}\) denotes the chain obtained by removing the last \(k'\) blocks from \(C_1\), and \(\leq\) denotes the prefix relation.


We define a new and stronger conmmon prefix property since we have a chance to finalize blocks earlier (smaller \(k\)) than the probabilistic finality that Ouroboros Praos [2] provides thanks to GRANDPA.

**Definition 4: (Strong Common Prefix (SCP))** Assuming that the common prefix property is satisfied with parameter \(k\), strong common prefix  with parameter \(k \in \mathbb{N}\) ensures that there exists \(k' < k\) and a slot number \(sl_1\) such that for any two chain \(C_1,C_2\) possessed by two honest parties at the onset of \(sl_1\) and \(sl_2\) where \(sl_1 < sl_2\), \(C_1^{\ulcorner k'} \leq C_2\).

In a nutshell, strong common prefix property ensures that there is a least one block which is finalized earlier than other blocks. 

It has been shown [4] that the persistence and liveness is satisfied if the block production ensure chain growth, chain quality and common prefix proerties. **Persistence** ensures that, if a transaction is seen in a block deep enough in the chain, it will stay there and **liveness** ensures that if a transaction is given as input to all honest players, it will eventually be inserted in a block, deep enough in the chain, of an honest player.

### Security Proof of BABE

We first prove that BABE satisfies chain growth, chain quality and strong common prefix properties in one epoch. Second, we prove that BABE's secure by showing that BABE satisfies persistence and liveness in multiple epochs. 

Before starting the security analysis, we give probabilities of being selected as a slot leader [2] or noone selected. We use the notations \(sl = \bot\) if a slot \(sl\) is empty,  \(sl = 0_{L}\) if \(sl\) is given to only one late honest party (\(\D\) behind the current slot) and \(sl = 0_S\)  if \(sl\) is given to only one synchronized honest party.

$$p_\bot=\mathsf{Pr}[sl = \bot] = \prod_{i\in \mathcal{P}}1-\phi(\alpha_i) = \prod_{i \in \mathcal{P}} (1-c)^{\alpha_i} = 1-c$$

$$p_{0_L} = \sum_{i\in\mathcal{H}_L}\phi(\alpha_i)(1-\phi(1-\alpha_i)) = \sum_{i\in\mathcal{H}_L}(1-(1-c)^{\alpha_i})(1-c)^{1-\alpha_i}$$

similarly,
$$p_{0_S} = \sum_{i\in\mathcal{H}_S}(1-(1-c)^{\alpha_i})(1-c)^{1-\alpha_i}$$

where \(\mathcal{P}\) is the set of indexes of all parties, \(\mathcal{H}_L\) is the set of indexes of all late and honest parties, \(\mathcal{H}_S\) is the set of indexes of all honest and synchronized parties with using Proposition 1 in [2]. 

We can bound \(p_{0_S}\) and \(p_{0_L}\) as \(p_{0_S} \geq \phi(\alpha_S)(1-c) \geq \alpha_Sc(1-c)\) and \(p_{0_L} \geq \phi(\alpha_L)c(1-c)\geq \alpha_L(1-c)\) where \(\alpha_S\) denotes the total relative stake of synchronized and honest parties and \(\alpha_L\) denotes the total relative stake of honest and late parties. For the rest, we denote \(\alpha = \alpha_S + \alpha_L = \gamma\alpha + \beta\alpha\) where \(\gamma + \beta = 1\) and \(\alpha\) is the relative stakes of honest parties.





In Lemma 1 and Lemma 2, we prove that a late party can be at most \(\D\) behind of the current slot. If a late party is a slot leader then his block is added to the best chain if there are at least \(2\D\) consecutive empty slots because he sends his block \(\D\) times later and his block may be received \(\D\) times later by other honest parties becuase of the network delay. Having late parties in BABE influences chain growth. 

**Theorem 1 (CG):** Let \(k, R, \D \in \mathbb{N}\) and let \(\alpha = \alpha_S + \alpha_L = \gamma\alpha + \beta\alpha\) is the total relative stake of honest parties. Then, the probability that an adversary \(\A\) makes BABE violate the chain growth property (Definition 1) with parameters \(s \geq 6 \D\) and \(\tau = \frac{\lambda c\alpha(\gamma+ \lambda \beta)}{6}\) throughout a period of \(R\) slots, is no more than \(2\D Rc  \exp({-\frac{(s-5\D)\lambda c\alpha(\gamma+ \lambda \beta)}{16\D}})\), where c denotes the constant \(\lambda = (1-c)^{\D}\).

**Proof:** We define two types of slot. We call a slot *\(2\D\)-right isolated* if the slot leader is one late party and the next \(2\D - 1\) slots are empty (no party is assigned). We call a slot *\(\D\)-right isolated* if the slot leader is only one synchronized honest party (not late party) and the next consecutive \(\D-1\) slots are empty. 

Now consider a chain owned by an honest party in \(sl_u\) and a chain owned by an honest party in \(sl_v \geq sl_u + s\). We need to show that honest parties' blocks are added most of times between \(sl_u\) and \(sl_v\). Therefore, we need to find the expected number of \(2\D\)-right isolated slots between \(sl_u\) and \(sl_v\)  given that the relative stake of late parties is \(\alpha_L = \beta \alpha\) and expected number of \(\D\)-right isolated slots given that the relative stake of synchronized honest parties is \(\alpha_S = \gamma\alpha\). Remark that a slot can be either \(2\D\)-right isolated or \(\D\)-right isolated or neither of them.

Consider the chains \(C_u\) and \(C_v\) in slots \(sl_u\) and \(sl_v\) owned by the honest parties, respectively where \(sl_u\) is the first slot of the epoch. We can guarantee that \(C_u\) is one of the chains of everyone in \(sl_u + 2\D\) and the chain \(C_v\) is one of the chains of everyone if it is sent in slot \(sl_v - 2\D\). Therefore, we are interested in slots between \(sl_u + 2\D\) and \(sl_v - 2\D\). Let us denote the set of these slots by \(S = \{sl_u + 2\D, sl_u+2\D+1,...,sl_v-2\D\}\). Remark that \(|S| = s-4\D\).

Now, we define a random variable \(X_t \in \{0,1\}\) where \(t\in S\). \(X_t = 1\) if \(t\) is \(2\D\) or \(\D\)-right isolated with respect to the probabilities \(p_\bot, p_{0_L}, p_{0_S}\). Then 
$$\mu = \mathbb{E}[X_t] = p_{0_S}p_\bot^{\D-1}+p_{0_L}p_\bot^{2\D-1} \geq \alpha_Sc(1-c)^{\D}+\alpha_Lc(1-c)^{2\D}.$$

With \( \lambda = (1-c)^{\D}\), \(\alpha = \alpha_L+\alpha_S = \beta\alpha+ \gamma \alpha\),

$$\mu \geq \lambda c\alpha(\gamma+ \lambda  \beta)$$

Remark that \(X_t\) and \(X_{t'}\) are independent if \(|t-t'| \geq 2\D\). Therefore, we define \(S_z = \{t\in S: t \equiv z \text{ mod }2\D\}\) where all \(X_t\) indexed by \(S_z\) are independent and \(|S_z| >  \frac{s-5\D}{2\D}\).

We apply a [Chernoff Bound](http://math.mit.edu/~goemans/18310S15/chernoff-notes.pdf) to each \(S_z\) with \(\delta = 1/2\).

$$\mathsf{Pr}[\sum_{t \in S_z}X_t < |S_z|\mu/2] \leq e^{-\frac{|S_z|\mu}{8}}\leq e^{-\frac{(s-4\D)\mu}{16\D}}$$


Recall that we want to bound the number of \(2\D\) and \(\D\)-right isolated slots. Let's call this number \(H\). If for all \(z\), \(\sum_{t \in S_z}X_t \geq |S_z|\mu/2\), then \(H = \sum_{t\in S} X_t \geq |S|\mu/2\). With union bound

$$\mathsf{Pr}[H < |S|\mu/2] \leq 2\D e^{-\frac{(s-5\D)\mu}{16\D}}$$

since \(\mu \geq \lambda c\alpha(\gamma+  \beta)\)

$$\mathsf{Pr}[H < |S|\frac{\lambda c\alpha(\gamma+ \lambda \beta)}{2}] \leq \mathsf{Pr}[H < |S|\mu/2]\leq 2\D \exp({-\frac{(s-5\D)\lambda c\alpha(\gamma+ \lambda \beta)}{16\D}})\space\space\space (2)$$


We find that in the first \(s\) slot of an epoch the chain grows \(\tau s\) block with the probability given in (2). Now consider the chain growth from slot \(sl_{u+1}\) to \(sl_{v+1}\). We know that the chain grows at least \(\tau s -1\) blocks between \(sl_{u+1}\) to \(sl_v\). So, the chain grows one block for sure if \(sl_{v+1}\) is \(\D\) or \(2\D\)-right isolated which with probability \(\alpha f c(\gamma+c\beta)\).    
If we apply the same for each \(sl > sl_u\) we obtain

$$2\D R \alpha \lambda  c(\gamma+\lambda\beta) \exp({-\frac{(s-5\D)\lambda c\alpha(\gamma+ \lambda \beta)}{16\D}})$$


given \(|S| = s-4\D\) and if \(s \geq 6\D\), \(|S| \geq \frac{s}{3}\) (\(\tau s = \frac{\lambda c\alpha(\gamma+ \lambda \beta)}{6}s \geq \frac{\lambda c\alpha(\gamma+ \lambda \beta)}{2}|S|\)). 

$$\tag*{\(\blacksquare\)}$$


**Theorem 2 (CQ):** Let \(k,\D \in \mathbb{N}\) and \(\epsilon \in (0,1)\). Let \(\alpha(\gamma+(1-c)^\D\beta)(1-c)^\D \geq (1+\epsilon)/2\) where \(\alpha = \alpha_S+\alpha_L = \gamma\alpha + \beta\alpha\) is the relative stake of honest parties. Then, the probability of an adversary \(\A\) whose relative stake is at most \(1-\alpha\) violate the chain growth property (Definition 2) with parammeters \(k\) and \(\mu = 1/k\) in \(R\) slots with probability at most \(Re^{-\Omega(k)}\).

**Proof (sketch):** The proof is very similar to the proof in [2]. It is based on the fact that the number of \(2\D\) and \(\D\) isolated slots are more than normal slots because of the assumption \((\alpha(\gamma+(1-c)^\D\beta)(1-c)^\D \geq (1+\epsilon)/2\). Remark that probability of having \(2\D\)-right isolated slot is \(\alpha\beta(1-c)^{2\D}\), having \(\D\)-right isolated slot is \(\alpha\gamma(1-c)^{\D}\) and sum of them are greater than 1/2 because of the assumption. 

$$\tag*{\(\blacksquare\)}$$


**Theorem 3 (SCP):** Let \(k,\D \in \mathbb{N}\) and \(\epsilon \in (0,1)\). Let \(\alpha(\gamma+(1-c)^\D\beta)(1-c)^\D \geq (1+\epsilon)/2\) where \(\alpha = \alpha_S+\alpha_L = \gamma\alpha + \beta\alpha\) is the relative stake of honest parties. Assuming that the GRANDPA finality gadget finalizes a block at most \(\kappa\) slots later with the probability \(\theta\), then the probability of an adversary \(\A\) whose relative stake is at most \(1-\alpha_L+\alpha_S\) violate the **strong** common prefix property with parammeter \(k\) in \(R\) slots with probability at most \((\theta Rc^{k+1}(1-c)^{\kappa - k} + (1-\theta))\exp(\ln R +  − \Omega(k-2\D))\).


**Proof Sketch:** First of all, we need to show that common prefix prefix property is satisfied with the honest relative-stake assumption. With a similar proof in [2] in Theorem 5, we can conclude that the common prefix property can be violated with the probability at most \(\exp(\ln R +  − \Omega(k-2\D))\). 

SCP property is violated if there is no  two chain \(C_1,C_2\) at any slot number \(sl_1\) such that \(C_1^{\ulcorner k'} \leq C_2\) and \(k'\leq k\) where \(C_2\) is a chain of an honest party in slot \(sl_2>sl_1\). If \(\kappa\) slots later, the chain grows more than \(k\), then the probabilistic finality passes the GRANDPA finality gadget. So, if for all \(\kappa\) slots after a non-empty slot, the chains grows more than \(k\) or the GRANDPA finality gadget finalize a block after \(\kappa\) slots then strong common prefix proerty is violated given that the GRANDPA finality gadget finalizes a block at most    \(\kappa\) slots later with the probability \(\theta\). This happens with at least the probability \(\theta Rc^{k+1}(1-c)^{\kappa - k} + (1-\theta)\) in \(R\) slots. 

$$\tag*{\(\blacksquare\)}$$

Remark than even if \(\theta = 0\), we still have the common prefix property as in Ouroboros Praos [2].


**Theorem 4 (Persistence and Liveness):** Fix parameters \(k, R, \D, L \in \mathbb{N}\), \(\epsilon \in (0,1)\) and \(r\). Let \(R \geq 12k/c(1+\epsilon)\) be the epoch length, \(L\) is the total lifetime of the system and $$\alpha(\gamma+(1-c)^\D\beta)(1-c)^\D \geq (1+\epsilon)/2$$
BABE satisfies persitence [2] with parameters \(k\) and liveness with parameters \(s \geq  12k/c(1+\epsilon)\) with probability \(1-\exp({\ln L\D c-\Omega(k-\ln tqk)})\) where \(r= 8tqk/(1+\epsilon)\) is the resetting power of the adversary during the randomness generation.


**Proof (Sketch):** The proof is very similar to Theorem 9 in [2]. The idea is as follows: The randomness for the next epoch is resettable until  the end of the epoch \(R/c(1+\epsilon) > 12k/c(1+\epsilon)\). Now let's check the chain growth in \(s = 12k/c(1+\epsilon)\) with \(\tau= \frac{\lambda c\alpha(\gamma+ \lambda \beta)}{6}\) where \(\lambda = (1-c)^\D\).

$$\tau s = \frac{(1-c)^\D c\alpha(\gamma+ (1-c)^{\D} \beta)}{6}\frac{12k}{c(1+\epsilon)} \geq k $$

The stake distribution (for epoch $e_{j+3}$) which is updated until the end of epoch $e_j$ is finalized at latest in the last slot $12k/c(1+\epsilon)$ of epoch $e_{j+1}$. So it is finalized before the randomness of the epoch ($e_{j+3}$) generated. In addition to this, the chain growth property shows that there will be at least one honest block in the first $12k/c(1+\epsilon)$ slots. These two imply that the adversary cannot adapt validators' in or out according to the random number for the epoch \(e_{j+3}\) and this random number provides good randomness for the epoch even though the adversary has capability of resetting \(r = 8tkq/(1+\epsilon)\) times (\(t\) is the number of corrupted parties and \(q\) is the maximum number of random-oracle queries for a party). So, the common prefix property still preserved with the dynamic update. Therefore, we can conclude that persistence is satisfied thanks to the common prefix property of dynamic stake with the probability (comes from Theorem 1) $$2r\D Lf \exp({-\frac{(s-5\D)(1-c)^\D c\alpha(\gamma+ (1-c)^\D\beta)}{16\D}}) \space\space\space (3).$$ If we use the assumptions we can simplify this probability as \(\exp({\ln L\D c-\Omega(k-\ln tqk)}\).
Liveness is the result of the chain growth and chain quality properties.
$$\tag*{\(\blacksquare\)}$$



**These results are valid assuming that the signature scheme with account key is  EUF-CMA (Existentially Unforgible Chosen Message Attack) secure, the signature scheme with the session key is forward secure, and VRF realizing is realizing the functionality defined in [2].**


**Analysis With VDF:** TODO

If we use VDF in the randomness update for the next epoch, \(r = \mathsf{log}tkq\) disappers in \(p_{sec}\) because we have completely random value which do not depend on hashing power of the adversary.



## 6. Practical Results

In this section, we find parameters of BABE in order to achieve the security in BABE. In addition to this, we show block time of BABE in worst cases (big network delays, many malicious parties) and in average case.

We fix the life time of the protocol as \(\mathcal{L}=2.5 \text{ years}  = 15768000\) seconds. Then we find the life time of the protocol  \(L = \frac{\mathcal{L}}{T}\). We find the network delay in terms of slot number with $\lfloor \frac{D}{T}\rfloor$ where $D$ is the network delay in seconds. Assuming that parties send their block in the beginning of their slots, $\lfloor\rfloor$ operation is the enough to compute the delay in terms of slots. 


The parameter $c$ is very critical because it specifies the number of empty slots because probability of having empty slot is $1-c$. If $c$ is very small, we have a lot of empty slots and so we have longer block time. If $c$ is big, we may not satisfy the  condition \(\alpha(\gamma+(1-c)^\D\beta)(1-c)^\D \geq (1+\epsilon)/2\) to apply the result of Theorem 4. So, we need to have a tradeoff between security and practicality. 

We need to satisfy two conditions $$\frac{1}{c}(\phi(\alpha\gamma)(1-c)^{\D-\alpha}(1-c)^{\D-1}+ \phi(\alpha\beta)(1-c)^{2\D-\alpha\beta} \geq \alpha(\gamma+(1-c)^\D\beta)(1-c)^\D > 1/2$$ to apply the result of Theorem 4 and $$\frac{1}{c}(\phi(\alpha\gamma)(1-c)^{\D-\alpha}(1-c)^{\D-1} \geq \alpha\gamma(1-c)^\D > 1/2$$ to apply the result of Lemma 1 . Remark that the second condition implies the first one so it it enough to satistfy the second condition.  In order to find a $c$ value which provide resistance against maxumum network delays, we let $\alpha = 0.65$ and $\gamma = 0.8$. Given this if we  want to be secure even if we have maximum delay $D$, we need following $c$ values. 

* c = 0.278 if $\D = \lfloor \frac{D}{T}\rfloor = 1$,
*  c = 0.034 if $\D = \lfloor \frac{D}{T}\rfloor = 2$
*  c = 0.018 if $\D = \lfloor \frac{D}{T}\rfloor = 3$
*  c =  0.0125 if $\D = \lfloor \frac{D}{T}\rfloor = 4$
*  c =  0.0094 if $\D = \lfloor \frac{D}{T}\rfloor = 5$
*  c =  0.0076 if $\D = \lfloor \frac{D}{T}\rfloor = 6$


We compute the average block time in the case that the network delay is in average 1 second and all validators behave honestly, $gamma = 0.8$. In order to find, the probability of an unsychronized party's block added to the best chain, we find the probability of having $2\D$-right isolated slot meaning that the leaders are all honest and late and the next $2\D-1$ slots are empty. Remark that the definitions of $2\D$ right isolated slot is more relaxed than the definition in the proof of Theorem 1 because we do not care the growth of other chains as we care in the security analysis. We compute the expected number of  $2\D$-isolated slot according to average delay (1 sec) even though we use the secure $c$ value to have maximum network resistance. So, $\D = $\lfloor\frac{1}{T}\rfloor$ in the below computations.

Given a non-empty slot, the probability that this slot is $2\D$-right isolated slot is  
$$p_{H_L} \geq \frac{\phi(\alpha\beta)(1-c)^{1-\alpha\beta}}{c}(1-c)^{2\D-1}.$$ 

The expected number of non-empty slot in $L$ is $Lc$. So, the expected number of  $2\D$-right isolated slot in $Lc$ slot is  
$\mathbb{E} = Lcp_{H_S}.$ Then, the block time $T_{block} \leq \frac{LT}{\mathbb{E}} = \frac{T}{c p_{H_S}}$. 

We give graphs for required slot time to have the block time in $(-1,+1)$-neighborhood of the time in the x-axis with different maximum network delay ($D = 1,2,3,4,5,6$ seconds) resistance. Slot time being 0 in the graphs means is that it is not possible to have the corresponding block time.

![](https://i.imgur.com/Sz2iRE1.png)

If we decide to be resistant 6 seconds delay, we can choose $T = 3.905$ and have around 14 seconds block time if the average network delay is 1 second. In this case, the epoch length has to be around 4.5 hours to make sure that we have a good randomness and $k = 96$. If GRANDPA works well the epoch length can be around half of 4.5 hours.

If we decide to be resistant 4 seconds delay, we can choose $T = 2.78   $ and have around 10 seconds block time if the average network delay is 1 second. In this case, the epoch length has to be around 3.2 hours to make sure that we have a good randomness and $k = 97$. If GRANDPA works well the epoch length can be around half of 3.2 hours.


## References

[1] Kiayias, Aggelos, et al. "Ouroboros: A provably secure proof-of-stake blockchain protocol." Annual International Cryptology Conference. Springer, Cham, 2017.

[2] David, Bernardo, et al. "Ouroboros praos: An adaptively-secure, semi-synchronous proof-of-stake blockchain." Annual International Conference on the Theory and Applications of Cryptographic Techniques. Springer, Cham, 2018.

[3] Badertscher, Christian, et al. "Ouroboros genesis: Composable proof-of-stake blockchains with dynamic availability." Proceedings of the 2018 ACM SIGSAC Conference on Computer and Communications Security. ACM, 2018.

[4] Aggelos Kiayias and Giorgos Panagiotakos. Speed-security tradeoffs in blockchain protocols. Cryptology ePrint Archive, Report 2015/1019, 2015. http://eprint.iacr.org/2015/1019
