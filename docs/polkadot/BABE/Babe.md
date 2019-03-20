
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


## Overview

BABE stands for '**B**lind **A**ssignment for **B**lockchain **E**xtension'. 
In BABE, we deploy Ouroboros Praos [2] style block production. 

In Ouroboros [1] and Ouroboros Praos [2], the best chain (valid chain) is the longest chain. In Ouroboros Genesis, the best chain can be the longest chain or the chain which is forked long enough and denser than the other chains in some interval. We have a different approach for the best chain selection based on GRANDPA and longest chain. In addition, we do not assume that all parties can access the current slot number which is more realistic assumption.

## BABE 
In BABE, we have sequential non-overlaping epochs \((e_1, e_2,...)\), each of which contains a number of sequential slots (\(e_i = \{sl^i_{1}, sl^i_{2},...,sl^i_{t}\}\)) up to some bound \(t\).  We randomly assign each slot to a party, more than one parties, or no party at the beginning of the epoch.  These parties are called a slot leader.  We note that these assignments are private.  It is public after the assigned party (slot leader) produces the block in his slot.

Each party \(P_j\) has at least two type of secret/public key pair:

*    Account keys \((\skac_{j}, pk^a_{j})\) which are used to sign transactions.
*    Session keys consists of two keys: Verifiable random function (VRF) keys \((\skvrf_{j}, \pkvrf_{j})\) and the signing keys for blocks \((\sksgn_j,\pksgn_j)\). 

We favor VRF keys being relatively long lived, but parties should update their associated signing keys from time to time for forward security against attackers causing slashing.  More details related to these key are [here](https://github.com/w3f/research/tree/master/docs/polkadot/keys).

Each party \(P_j\) keeps a local set of blockchains \(\mathbb{C}_j =\{C_1, C_2,..., C_l\}\). These chains have some common blocks (at least the genesis block) until some height.

We assume that each party has a local buffer that contains the transactions to be added to blocks. All transactions are signed with the account keys. 


### BABE with GRANDPA Validators \(\approx\) Ouroboros Praos

In this version, we do not worry about offline parties because GRANDPA validators are online by design. Therefore, we do not consider the security problems such as speed up attacks. It is almost the same as Ouroboros Praos except chain selection rule and the slot time adjustment.

We give some parameters probability related to be selected as a slot leader in this version before giving the protocol details. As in Ouroboros Praos, we define probability of being selected as

$$p_i = \phi_c(\alpha_i) = 1-(1-c)^{\alpha_i}$$

where \(\alpha_i\) is the relative stake of the party \(P_i\) and \(c\) is a constant. Improtantly, the function \(\phi\) is that it has the '**independent aggregation**' property, which informally means the probability of being selected as a slot leader does not increase as a party splits his stakes across virtual parties.

We use \(\phi\) to set a threshold \(\tau_i\) for each party \(P_i\): 

$$\tau_i = 2^{\ell_{vrf}}\phi_c(\alpha_i)$$

where \(\ell_{vrf}\) is the length of the VRF's first output.

BABE with GRANDPA validators consists of three phases:

1. #### Genesis Phase

In this phase, we manually produce the unique genesis block.

The genesis block contain a random number \(r_1\) for use during the first epoch for slot leader assignments, the initial stake's of the stake holders (\(st_1, st_2,..., st_n\)) and their corresponding session public keys (\(\pkvrf_{1}, \pkvrf_{2},..., \pkvrf_{n}\)), \((\pksgn_{1}, \pksgn_{2},..., \pksgn_{n}\)) and account public keys (\(\pkac_{1}, \pkac_{2},..., \pkac_{n}\)).

We might reasonably set \(r_1 = 0\) for the initial chain randomness, by assuming honesty of all validators listed in the genesis block.  We could use public random number from the Tor network instead however.

TODO: In the delay variant, there is an implicit commit and reveal phase provided some suffix of our genesis epoch consists of *every* validator producing a block and *all* produced blocks being included on-chain, which one could achieve by adjusting paramaters.

2. #### Normal Phase

In normal operation, each slot leader should produce and publish a block.  All other nodes attempt to update their chain by extending with new valid blocks they observe.

We suppose each party \(P_j\) has a set of chains \(\mathbb{C}_j\) in the current slot \(sl_k\) in the epoch \(e_m\).  We have a best chain \(C\) selected in \(sl_{k-1}\) by our selection scheme, and the length of \(C\) is \(\ell\text{-}1\). 

Each party \(P_j\) produces a block if he is the slot leader of \(sl_k\).  If the first output (\(d\)) of the following VRF is less than the threshold \(\tau_j\) then he is the slot leader.

$$\vrf_{\skvrf_{j}}(r_m||sl_{k}) \rightarrow (d, \pi)$$

Remark that the more \(P_j\) has stake, the more he has a chance to be selected as a slot leader. 


If \(P_j\) is the slot leader, \(P_j\) generates a block to be added on \(C\) in \(sk_k\). The block \(B_\ell\) should contain the slot number \(sl_{k}\), the hash of the previous block \(H_{\ell\text{-}1}\), the VRF output  \(d, \pi\), transactions \(tx\), and the signature \(\sigma = \sgn_{\sksgn_j}(sl_{k}||H_{\ell\text{-}1}||d||pi||tx))\). \(P_i\) updates \(C\) with the new block and sends \(B_\ell\).


![ss](https://i.imgur.com/Yb0LTJN.png =250x )



In any case (being a slot leader or not being a slot leader), when \(P_j\) receives a block \(B = (sl, H, d', \pi', tx', \sigma')\) produced by a party \(P_t\), it validates the block  with \(\mathsf{Validate}(B)\). \(\mathsf{Validate}(B)\) should check the followings in order to validate the block:

* if \(\mathsf{Verify}_{\pksgn_t}(\sigma')\rightarrow \mathsf{valid}\),
* if \(sl \leq sl_k\) (The future blocks are discarded)

* if the party is the slot leader: \(\mathsf{Verify}_{\pkvrf_t}(\pi', r_m||sl) \rightarrow \mathsf{valid}\) and \(d' < \tau_t\). 

* if \(P_t\) did not produce another block for another chain in slot \(sl\) (no double signature),

* if there exists a chain \(C'\) with the header \(H\).

If the validation process goes well, \(P_j\) adds \(B\) to \(C'\). Otherwise, it ignores the block.


At the end of the slot, \(P_j\) decides the best chain with the function 'BestChain' (described below).




3. #### Epoch Update

Before starting a new epoch, there are certain things to be updated in the chain.
* Stakes of the parties
* (Session keys)
* Epoch randomness

If a party wants to update his stake for epoch \(e_{m+1}\), it should be updated until the beginning of epoch \(e_m\) (until the end of epoch \(e_{m-1}\)) for epoch \(e_{m+1}\). Otherwise, the update is not possible. We want the stake update one epoch before because we do not want parties to adjust their stake after seeing the randomness for the epoch \(e_{m+1}\). 

The new randomness for the new epoch is computed as in Ouroboros Praos [2]: Concatenate all the VRF outputs in blocks starting from the first slot of the epoch to the \(2R/3^{th}\) slot of \(e_m\) (\(R\) is the epoch size). Assume that the concatenation is \(\rho\). Then the randomness in the next epoch:

$$r_{m+1} = H(r_{m}||m+1||\rho)$$

This also can be combined with VDF output to prevent little bias by the adversaries for better security bounds.

## Best Chain Selection

Given a chain set \\(\mathbb{C}_j\\) an the parties current local chain \(C_{loc}\), the best chain algorithm eliminates all chains which do not include the finalized block \(B\) by GRANDPA. Let's denote the remaining chains by the set \(\mathbb{C}'_j\).
Then the algorithm outputs the longest chain which do not for from \(C_{loc}\)  more than \(k\) blocks. It discards the chains which forks from \(C_{loc}\) more than \(k\) slots.


We do not use the chain selection rule as in Ouroboros Genesis [3] because this rule is useful for parties who become online after a period of time and do not have any  information related to current valid chain (for parties always online the Genesis rule and Praos is indistinguishable with a negligible probability). Thanks to Grandpa finality, the new comers have a reference point to build their chain so we do not need the Genesis rule.


## Relative Time

It is important for parties to know the current slot  for the security and completeness of BABE. Therefore, we show how a party realizes the notion of slots. We assume that slot time \(T\) is greater than the network propogation time. We assume partial synchronous channel meaning that any message sent by a party arrives at most \(\D\)-slots later. \(\D\) is not an unknown parameter.


Each party has a local clock and this clock does not have to be synchronized with the network. When a party receives the genesis block, it stores the arrival time as \(t_0\) as a reference point of the beginning of the first slot. We are aware of the beginning of the first slot is not same for everyone. We assume that this difference is negligible comparing to \(T\). Then each party divides their timeline in slots.


**Obtaining Slot Number:** Parties who join BABE after the genesis block released or who lose notion of slot run the following protocol or who wants to resynchronze the slot number obtain the current slot number with the following protocol. 


If a party \(P_j\) is a newly joining party, he downloads chains and receives blocks at the same time. After chains' download completed, he adds the valid blocks to the corresponding chains. We have following approaches to determine the current slot time \(sl_{cur}\).

**- First Option:**
In this protocol, \(P_j\)  obtains the current slot number from the best chain \(C\). The current slot number from a block \(B'_u\) whose slot is \(sl_u\) and whose previous block belongs to \(sl_u-1\) is obtained as below:

$$sl_{cur} = sl_u + \lfloor\frac{t_{curr}-t_u}{T}\rfloor \space \space \space\space\space (1)$$

In more detail, \(sl_u\) is the slot of \((\mathsf{len}(C) - k')^{th}\)  block (B'_u) where \(k' \geq k\), \(t_u\) is the arrival time of \(B'_u\),  \((\mathsf{len}(C) - k')^{th}\) block (\(B'_u\)) to slot \(sl_u\) (i.e., \(sl_{cur} = sl_u + \lfloor\frac{t_{curr}-t_u}{T}\rfloor\)). The reason of obtaining \(sl_{cur}\) based on \(sl_u\) is  because with very high probability, \(B_u\) is in the best chain of other honest parties and will stay in the best chain. Therefore, we can assume that if this block is in the best chain forever, its chance to be sent on time is higher than to be sent earlier or later.  Clearly, if \(B_u\) is sent on time, then the party obtain a slot number at most \(\D\)-slot behind of the current slot but otherwise we cannot guarantee this. Actually, we would expect that even malicious parties sent their blocks on time because if they don't send on the right slot their blocks have chance not to be in the best chain in the future. However, we cannot trust this assumption in the security analysis. Therefore, we have second option which has higher guarantee.


**- Second Option:** Before giving the second option, let us define *lower consistent blocks*. Given consecutive blocks \(\{B'_1, B'_2,...,B'_n \in C\) if for each block pair \(B'_u\) and \(B'_v\) which belong to the slots \(sl_u\) and \(sl_v\) (\(sl_u < sl_v\)), respectively are lower consistent for a party \(P_j\), if they arrive on \(t_u\) and \(t_v\) such that \(sl_v - sl_u = \lfloor\frac{t_v - t_u}{T}\rfloor\). We call *upper consistent* if for all blocks \(sl_v - sl_u = \lceil\frac{t_v - t_u}{T}\rceil\) they Whenever \(P_j\) receives at least \(k\) either upper or lower consistent blocks, it outputs \(sl_{cur}\) as in (1) where \(sl_u\) is the slot of one of the blocks in the block set.



**Lemma 1:** Assuming that the network delay is at most \(\D\) and the honest and synchronized parties stake \(\alpha_H\) is  such that \(\alpha_H(1-c)^\D > 1/2\), \(P_j\)'s current slot is at most \(\D\)-behind the current slot of honest and synchronized parties (i.e., \(sl_{cur} \leq sl'_{cur} - \D\)).

**Proof:** According to Lemma 4 in [2], there is at least one block honestly generated by an sychronized and honest party in \(k\) slot with probability \(1 - e^{-\Omega(k)}\) assuming that  \(\alpha_H(1-c)^\D > 1/2\). We do our proof with lower consistent block. The upper consistent one is similar. 

If \(k\) blocks are lower consistent, then it means that all blocks are lower consistent with this honest and synchronized block. 

If \(P_j\) chooses the arrival time and slot number of this honest block, then \(sl_{cur} \leq sl'_{cur} - \D\) because the honest and synchronized parties' block must arrive to \(P_j\) at most \(\D\)-slots later. Now, we need to show that if \(P_j\) chooses the arrival time of a different block which does not have to be produced by an honest and synchronized party, then he is still at most \(\D\)-behind.

Assume that \(P_j\) picks \(sl_v > sl_u\) to compute the current slot number as in (1). We show that this computation is equal to \(sl_{cur} = sl_u +\lfloor\frac{t_{cur} - t_u}{T}\rfloor\). We know because of the lower consistency \(sl_v- sl_u = \lfloor\frac{t_v - t_u}{T}\rfloor\). $$sl_{cur} = sl_v - \lfloor\frac{t_v - t_u}{T}\rfloor + \lfloor\frac{t_{cur} - t_u}{T}\rfloor = sl_v + \lfloor\frac{t_{cur}-t_v}{T}\rfloor$$

So \(P_i\) is going to obtain the same \(sl_{cur}\) with all blocks. Similarly, if \(P_i\) picks \(sl_v < sl_u\), he obtains \(sl_u\)

$$\tag*{\(\blacksquare\)}$$

One of drawback of this protocol is that a party may never have \(k\) consistent blocks if an adversary randomly delays some blocks. In this case, \(P_i\) may never has consistent blocks. 

**Third Option:**
In this option, \(P_i\) obtains the slot number independent from the chain.
\(P_i\) asks the current slot number to some (or all) parties at time \(t_0\). Then, each party replies with the slot number \(\hat{sl}_i\) and the signature of it. The slot numbers with valid signatures let \(P_j\) compute some candidate current slots such as \(\{\hat{sl}_i+\lfloor\frac{|\hat{t}_i - t_0|}{T}\rfloor, \hat{sl}_i+\lceil\frac{|\hat{t}_i - t_0|}{T}\rceil\}\) where \(\hat{t}_i\) is arrival time of the slot number \(\hat{sl}_i\). Then, \(P_j\) selects the current slot time \(sl_{cur}\) according to majority among the candidate slot numbers.  



**Lemma 2:** Assuming that the network delay is at most \(\D\) and majority of parties are honest, \(P_j\)'s current slot is at most \(\D\)-behind the current slot of honest and synchronized parties (i.e., \(sl_{cur} \leq sl'_{cur} - \D\)).

**Proof:** Assume that \(P_j\) outputs \(sl_{cur} =\hat{sl}_i+\lceil\frac{|\hat{t}_i - t_0|}{T}\rfloor\) and real current slot number is \(sl'_{cur}\). \(0\leq \frac{|\hat{t}_i - t_0|}{T} \leq 2\D\) so if \(sl_{cur} =\hat{sl}_i+\lfloor\frac{|\hat{t}_i - t_0|}{T}\rfloor\), \(0\leq \lfloor\frac{|\hat{t}_i - t_0|}{T}\rfloor + a \leq 2\D\) and if \(sl_{cur} =\hat{sl}_i+\lceil\frac{|\hat{t}_i - t_0|}{T}\rceil\), \(0\leq \lfloor\frac{|\hat{t}_i - t_0|}{T}\rfloor - a \leq 2\D\). We also have \(sl'_{cur} -\hat{sl}_i \leq \D\) from the network assumption. From these two inequalities, we can obtain \(\hat{sl}_i - sl'_{cur} + \lceil\frac{|\hat{t}_i - t_0|}{T}\rfloor \leq \D \pm a\) implies that \(sl_{cur}- sl'_{cur} \leq \D \pm a\). Since we know that slot numbers are integers  \(sl_{cur}- sl'_{cur} \leq \D\).
$$\tag*{\(\blacksquare\)}$$


**Obtaining Slot Interval:** After learning the current slot, \(P_i\) has to wait for at least number of \(\D\) valid blocks in order to determine approximately beginning and end of the slot. Assume that \(P_j\) deduced \(sl_u\) is the current slot. \(P_j\) stores the arrival time of blocks  after \(sl_u\). Let us denote the stored arrival times by \(t_1,t_2,...,t_\D\) corresponds to blocks including slot numbers \(sl'_1,sl'_2,...,sl'_\D\). Remark that these slot numbers do not have to be consecutive since some slots may be empty or the slot leader is offline. \(P_j\) deduces that the current slot \(sl = sl'_\D + 1\) given that \(T_i = T(sl-sl'_i)\) is in a time interval which includes \(\{t'_1+T_1, t'_2+T_2,..., t'_\D+T_\D\}\).


![](https://i.imgur.com/evb6i6p.png)




Another critical timing issue is 'when to release the block'. In order to find a good block release time so that it arrives everyone before end of the slot, each party follow the same strategy as newly joining party. Assume that the party \(P_j\) is a slot leader in \(sl\) and the computes \(\mathcal{T}_{sl} =\{t'_1+T_1, t'_2+T_2,..., t'_\D+T_\D\}\) as above. Then the function \(f_{time}:R^\D \rightarrow R\) gives the release time given \(\mathcal{T}_{sl}\) as an input.

Possible candidates for \(f_{time}\) are average, maximum...

Then the party releases the block at time \(f_{time} - L_{avg}\) where \(L_{avg}\) is the estimaged network latency.

## Security Analysis

BABE with Grandpa validators is the same as Ouroboros Praos except the chain selection rule and  slot time extraction. Therefore, we need a new security analysis.




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
$$\mu = \mathbb{E}[X_t] = p_{0_S}p_\bot^{\D-1}+p_{0_L}p_\bot^{2\D-1} \geq \alpha_S\lambda(1-c)^{\D}+\alpha_L\lambda(1-c)^{2\D}.$$

With \( \lambda = (1-c)^{\D}\), \(\alpha = \alpha_L+\alpha_S = \beta\alpha+ \gamma \alpha\),

$$\mu \geq \lambda c\alpha(\gamma+ \lambda  \beta)$$

Remark that \(X_t\) and \(X_{t'}\) are independent if \(|t-t'| \geq 2\D\). Therefore, we define \(S_z = \{t\in S: t \equiv z \text{ mod }2\D\}\) where all \(X_t\) indexed by \(S_z\) are independent and \(|S_z| >  \frac{s-5\D}{2\D}\).

We apply a [Chernoff Bound](http://math.mit.edu/~goemans/18310S15/chernoff-notes.pdf) to each \(S_z\) with \(\D = 1/2\).

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


**Theorem 4 (Persistence and Liveness):** Fix parameters \(k, R, \D, L \in \mathbb{N}\), \(\epsilon \in (0,1)\) and \(r\). Let \(R \geq 18k/c(1+\epsilon)\) be the epoch length, \(L\) is the total lifetime of the system and $$\alpha(\gamma+(1-c)^\D\beta)(1-c)^\D \geq (1+\epsilon)/2$$
BABE satisfies persitence [2] with parameters \(k\) and liveness with parameters \(s \geq  12k/c(1+\epsilon)\) with probability \(1-\exp({\ln L\D c-\Omega(k-\ln tqk)})\) where \(r= 8tqk/(1+\epsilon)\) is the resetting power of the adversary during the randomness generation.


**Proof (Sketch):** The proof is very similar to Theorem 9 in [2]. The idea is as follows: The randomness for the next epoch starts to leak after  the slot number \(2R/3(1+\epsilon) > 12k/c(1+\epsilon)\). Now let's check the chain growth in \(s = 12k/c(1+\epsilon)\) with \(\tau= \frac{\lambda c\alpha(\gamma+ \lambda \beta)}{6}\) where \(\lambda = (1-c)^\D\).

$$\tau s = \frac{(1-c)^\D c\alpha(\gamma+ (1-c)^{\D} \beta)}{6}\frac{12k}{c(1+\epsilon)} \geq k $$

Since in \(2R/3(1+\epsilon)\) slots during epoch \(e_j\) the chain grows at least \(k\) blocks, it means that the stake distribution of the next epoch (\(e_{j+1}\)) has already finalized in the epoch \(e_{j-1}\) becuase of the common prefix property. In addition to this, chain growth property shows that there will be at least one honest block in the first \(2R/(1+\epsilon)\) block. These two implies that the adversary cannot adapt his stake according to the random number for the next epoch \(e_{j+1}\) and this random number provides good randomness for the next epoch even though the adversary has capability of resetting \(r = 8tkq/(1+\epsilon)\) times (\(t\) is the number of corrupted parties and \(q\) is the maximum number of random-oracle queries for a party). So, the common prefix property still preserved with the dynamic staking. Therefore, we can conclude that persistence is satisfied thanks to the common prefix property of dynamic stake with the probability (comes from Theorem 1) $$2r\D Lf \exp({-\frac{(s-5\D)(1-c)^\D c\alpha(\gamma+ (1-c)^\D\beta)}{16\D}}) \space\space\space (3).$$ If we use the assumptions we can simplify this probability as \(\exp({\ln L\D c-\Omega(k-\ln tqk)}\).
Liveness is the result of the chain growth and chain quality properties.
$$\tag*{\(\blacksquare\)}$$



**These results are valid assuming that the signature scheme with account key is  EUF-CMA (Existentially Unforgible Chosen Message Attack) secure, the signature scheme with the session key is forward secure, and VRF realizing is realizing the functionality defined in [2].**


**Analysis With VDF:** TODO

If we use VDF in the randomness update for the next epoch, \(r = \mathsf{log}tkq\) disappers in \(p_{sec}\) because we have completely random value which do not depend on hashing power of the adversary.



## Practical Results

In this section, we find parameters of BABE in order to achieve the security in BABE.

We fix the life time of the protocol as \(\mathcal{L}=2.5 \text{ years}  = 15768000\) seconds, maximum delay in the network \(\mathcal{D} = 5\) seconds and the slot time is \(3\) seconds. Then we find the life time of the protocol  \(L = \frac{\mathcal{L}}{T}\) and maximum delay \(\D = 1\) in terms of slot number. We assume that half of the honest parties are sychronized so \(\gamma = \beta = 0.5\).

We need to satisfy the condition \(\alpha(\gamma+(1-c)^\D\beta)(1-c)^\D \geq (1+\epsilon)/2\) to apply the result of Theorem 4. As seen in the graph below, f must be at most around 0.4 in order to have this condition. Otherwise, \(\alpha\) must equal to = 1 which is not realistic. Even \(c = 0.4\) is pretty big assumption because we need \(95 \%\) honest stake and \(\gamma > 1/2\) (i.e., less late parties). 

![](https://i.imgur.com/9skkoha.png)


Therefore, we choose \(\mathbf{f = 0.1}\) which satisfies the assumption for \(\gamma > 0\). For simplicity, we fix \(\gamma = 0.5\) which means at least half of the honest parties are synchronized. In this case **\(\mathbf{\alpha}\) must be at least \(\mathbf{0.6}\)**. We find that \(k > 70\) for a good security level in 2.5 years as shown in the graph below.

![](https://i.imgur.com/oLKeUlq.png)


If \(\mathbf{k = 72}\), finalizing block takes around 3 minutes. Remark that \(k\) is the finality that is provided by BABE. Since we have GRANDPA on top of BABE, we expect much earlier finalization. This \(k\) value is valid when GRANDPA does not work properly. If \(k = 72\), the minimum **epoch length must be 12960 slots which is around 7 hours** according to Theorem 4.





## References

[1] Kiayias, Aggelos, et al. "Ouroboros: A provably secure proof-of-stake blockchain protocol." Annual International Cryptology Conference. Springer, Cham, 2017.

[2] David, Bernardo, et al. "Ouroboros praos: An adaptively-secure, semi-synchronous proof-of-stake blockchain." Annual International Conference on the Theory and Applications of Cryptographic Techniques. Springer, Cham, 2018.

[3] Badertscher, Christian, et al. "Ouroboros genesis: Composable proof-of-stake blockchains with dynamic availability." Proceedings of the 2018 ACM SIGSAC Conference on Computer and Communications Security. ACM, 2018.

[4] Aggelos Kiayias and Giorgos Panagiotakos. Speed-security tradeoffs in blockchain protocols. Cryptology ePrint Archive, Report 2015/1019, 2015. http://eprint.iacr.org/2015/1019
