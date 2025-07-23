---
title: BABE
---

![](BABE.png)

Polkadot produces relay chain blocks using the **B**lind **A**ssignment for **B**lockchain **E**xtension protocol (BABE). BABE assigns block production slots based on a randomness cycle similar to that used in Ouroboros Praos [2]. The process unfolds as follows: All block producers possess a verifiable random function (VRF) key, which is registered alongside their locked stake. These VRFs generate secret randomness, determining when each producer is eligible to create a block. The process carries an inherent risk that producers may attempt to manipulate the outcome by grinding through multiple VRF keys. To mitigate this, the VRF inputs must incorporate public randomness that is created only after the VRF key is established. 

As a result, the system operates in epochs, during which fresh public on-chain randomness is created by hashing together all the VRF outputs revealed through block production within that epoch This establishes a cycle that alternates between private, verifiable randomness and collaborative public randomness.

BABE differs from Ouroboros Praos [2] in two main aspects: (1) its best chain selection mechanism, which integrates GRANDPA with the longest-chain rule, and (2) its slot synchronization assumptions. In the latter case, BABE block producers do not depend on a central authority, such as Network Time Protocol (NTP), to count slots. Instead, they build and maintain local clocks to track slot progression. 

---
 
## 1. Epochs, Slots, and Keys 

BABE consists of sequential, non-overlapping epochs $(e_1, e_2,\ldots)$, each with a set of consecutive block production slots ($e_i = \{sl^i_{1}, sl^i_{2},\ldots,sl^i_{t}\}$) up to a bound $t$.  At the start of each epoch, block production slots are randomly assigned to "slot leaders", sometimes to one party, no party, or multiple parties. The assignments are initially private, known only to the designated slot leader. This changes once they publicly claim their slots by producing a new block. 

Each party $P_j$ possesses a *session key* that includes at least two types of secret/public key pairs:

* A verifiable random function (VRF) key pair $(\skvrf_{j}, \pkvrf_{j})$
* A signing key pair for blocks $(\sksgn_j,\pksgn_j)$

VRF keys are preferred because they are relatively long-lived; new VRF keys cannot be used until well after they've been created and submitted to the chain. Yet, parties should periodically update their associated signing keys to maintain forward security, protecting against attackers who might exploit outdated keys to create slashable equivocations. For more details on session keys see [here](Polkadot/security/keys/3-session.md).

Each party $P_j$ maintains a local set of blockchains $\mathbb{C}_j =\{C_1, C_2,..., C_l\}$.  These chains share a common prefix of blocks, at minimum the genesis block, up to a certain height.

Each party also maintains a local buffer containing a set of transactions to be added to blocks. Before entering this buffer, all transactions are validated using a transaction validation function.

The aim is to ensure that each validator has an equal opportunity to be selected as a block producer for any given slot. The probability of selection for each validator is

$$
p = \phi_c(\theta) = 1-(1-c)^{\frac{1}{n}}
$$

where $0 \leq c \leq 1$ is a constant parameter and $n$ denotes the number of validators.


To ensure equitable slot assignment among validators in BABE, it is necessary to define a threshold parameter. To guide the slot selection process, we follow the approach described in [2] and obtain

$$
\tau = 2^{\ell_{vrf}}\phi_c(\theta),
$$

where $\ell_{vrf}$ is the length of the VRF's first output (randomness value).

## 2. Phases

BABE consists of three phases:

#### 1st: Genesis Phase

The unique genesis block, manually produced in this phase, contains a random number $r_1$ that is used during the first two epochs for slot leader assignments. Session public keys of initial validators are ($\pkvrf_{1}, \pkvrf_{2},..., \pkvrf_{n}$), $(\pksgn_{1}, \pksgn_{2},..., \pksgn_{n}$).


#### 2nd: Normal Phase

By the time the second phase begins, each validator must have divided their timeline into slots after receiving the genesis block. Validators determine the current slot number according to their local timeline, as explained in [Section 4](./Babe.md#-4.-clock-adjustment--relative-time-algorithm-). And if validators join BABE after the genesis block, they should also divide their timelines into slots.

During normal operation, the designated slot leader should produce and publish a block.  All other nodes update their chains based on the new valid blocks they observe.

Each validator $V_j$ maintains a set of chains $\mathbb{C}_j$ for the current slot $sl_k$ in epoch $e_m$, and a best chain $C$ selected during slot $sl_{k-1}$ according to the selection scheme described in Section 3. The length of $C$ is $\ell\text{-}1$.

A validator $V_j$ may produce a block if selected as the slot leader for $sl_k$.  If the first output ($d$) of the following VRF computation is less than the threshold $\tau$, the validator is considered the slot leader.

$$
\vrf_{\skvrf_{j}}(r_m||sl_{k}) \rightarrow (d, \pi)
$$

If $P_j$ is the slot leader, it generates a block to be added to chain $C$ during slot $sl_k$. The block $B_\ell$ must contain at minimum: the slot number $sl_{k}$, the hash of the previous block $H_{\ell\text{-}1}$, the VRF output $d, \pi$, the transactions $tx$, and the signature $\sigma = \sgn_{\sksgn_j}(sl_{k}||H_{\ell\text{-}1}||d||\pi||tx))$. Validator $P_i$ then updates $C$ with the new block and relays $B_\ell$.

Regardless of whether $V_j$ is a slot leader, upon receiving a block $B = (sl, H, d', \pi', tx', \sigma')$ produced by validator $V_t$, it excecutes $\mathsf{Validate}(B)$. To validate the block, the function $\mathsf{Validate}(B)$ must, at minimum, check the following criteria:

* $\mathsf{Verify}_{\pksgn_t}(\sigma')\rightarrow \mathsf{valid}$ – signature verification

* if the validator is the slot leader: $\mathsf{Verify}_{\pkvrf_t}(\pi', r_m||sl) \rightarrow \mathsf{valid}$ and $d' < \tau$ – verification using the VRF's algorithm

* There exists a chain $C'$ with header $H$,

* The transactions in $B$ are valid.

If all checks pass, $V_j$ adds $B$ to $C'$; otherwise, it discards the block. At the end of the slot, $P_j$ selects the best chain according to the chain selection rule outlined in Section 3.


#### 3rd: Epoch Update

Before starting a new epoch $e_m$, validators must obtain the new epoch randomness and the updated active validator set. A new epoch begins every $R$ slots, starting from the first slot. 

To ensure participation in epoch $e_m$, the validator set must be included in the relay chain by the end of the last block of epoch $e_{m-3}$. This timing enables validators to actively engage in block production for epoch $e_{m}$. Newly added validators may join block production no earliers that two epochs later after being included in the relay chain.

Fresh randomness for epoch $e_m$ is computed the Ouroboros Praos [2] method: concatenate all VRF outputs from blocks produced in epoch $e_{m-2}$ (denoted as $\rho$). Then, the randomness for epoch $e_{m}$ is derived as follows:

$$
r_{m} = H(r_{m-2}||m||\rho)
$$

Including a validator two epochs later ensures that the VRF keys of newly added validators, submitted to the chain prior to the randomness generation of their active epoch, are properly revealed.

---

## 3. Best Chain Selection

Given a chain set $\mathbb{C}_j$, and the party's current local chain $C_{loc}$, the best chain selection algorithm eliminates all chains that do not contain the finalized block $B$ determined by GRANDPA. The remaining chains form a subset denoted by $\mathbb{C}'_j$. If GRANDPA finalty is not required for a block, the algorithm resorts to probabilistic finality. In this case, the probabillistically finlazed block is defined as the block that is $k$ blocks prior to the latest block in $C_{loc}$.


In this case, the chain selection rule does not follow Ouroboros Genesis [3], as that rule is intended for parties that come online after a period of inactivity and lack information about the current valid chain. For parties that remain continously online, the Genesis rule and Praos are indistinguishable with  negligible probability. Thanks to Grandpa finality, newcomers have a reliable reference point to build their chain, making the Genesis rule unnecessary.

---

## 4. Clock Adjustment (Relative Time Algorithm)

It is important for parties to know the current slot for the security and completeness of BABE. For this, validators can use their computer clocks which is adjusted by the Network Time Protocol. However, in this case, we need to trust servers of NTP. If an attack happens to one of these servers than we cannot claim anymore that BABE is secure. Therefore, we show how a validator realizes the notion of slots without using NTP. Here, we assume we have a partial synchronous network meaning that any message sent by a validator arrives at most $\D$-slots later. $\D$ is an unknown parameter.


Each party has a local clock and this clock is not updated by any external source such as NTP or GPS. When a validator receives the genesis block, it stores the arrival time as $t_0$ as a reference point of the beginning of the first slot. We are aware that the beginning of the first slot is not the same for everyone. We assume that the maximum difference of start time of the first slot between validators is at most $\delta$. Then each party divides their timeline in slots and update periodically its local clock with the following algorithm.



**Median Algorithm:**
The median algorithm is run by all validators in the end of sync-epochs (we note that epoch and sync-epoch are not related). The first sync-epoch ($\varepsilon = 1$) starts just after the genesis block is released. The other sync-epochs ($\varepsilon > 1$) start when the slot number of the last (probabilistically) finalized block is $\bar{sl}_{\varepsilon}$ which is the smallest slot number such that  $\bar{sl}_{\varepsilon} - \bar{sl}_{\varepsilon-1} \geq s_{cq}$ where $\bar{sl}_{\varepsilon-1}$ is the slot number of the last (probabilistically) finalized block in the sync-epoch $\varepsilon-1$. Here, $s_{cq}$ is the parameter of the chain quality (CQ) property. If the previous epoch is the first epoch then $sl_{e-1} = 0$. We define the last (probabilistically) finalized block as follows: Retrieve the best blockchain according to the best chain selection rule, prune the last $k$ blocks of the best chain, then the last (probabilistically) finalized block will be the last block of the pruned best chain. Here, $k$ is defined according to the common prefix property.

The details of the protocol is the following: Each validator stores the arrival time $t_i$ of valid blocks constantly according to its local clock.  In the end of a sync-epoch, each validator retrieves the arrival times of valid and finalized blocks which has a slot number $sl'_x$ where
* $\bar{sl}_{\varepsilon-1} < sl_x \leq \bar{sl}_{\varepsilon}$ if $\varepsilon > 1$.
* $\bar{sl}_{\varepsilon-1} \leq sl_x \leq \bar{sl}_{\varepsilon}$ if $\varepsilon = 1$.

Let's assume that there are $n$  such blocks that belong to the current sync-epoch and let us denote the stored arrival times of blocks in the current sync-epoch by $t_1,t_2,...,t_n$ whose slot numbers are $sl'_1,sl'_2,...,sl'_n$, respectively. A validator selects a slot number $sl > sl_e$ and runs the median algorithm which works as follows:


```
for i = 0 to n:
    a_i = sl - sl'_i
    store t_i + a_i * T to lst
lst = sort (lst)
return median(lst)
```

In the end, the validator adjusts its clock by mapping $sl$ to the output of the median algorithm.


The following image with chains explains the algorithm with an example in the first epoch where $s_{cq} = 9$ and $k=1$:

![](https://i.imgur.com/jpiuQaM.png)


**Lemma 1:** (The difference between outputs of median algorithms of validators) Asuming that $\delta\_max$ is the maximum network delay, the maximum difference between start time is at most $\delta\_max$.

**Proof Sketch:** Since all validators run the median algorithm with the arrival time of the same blocks, the difference between the output of the median algorithm of each validator differs at most $\delta\_max$.

**Lemma 2:** (Adjustment Value) Assuming that the maximum total drift on clocks between sync-epochs is at most $\Sigma$ and $2\delta\_max + |\Sigma| \leq \theta$, the maximum difference between the new start time of a slot $sl$ and the old start time of $sl$ is at most $\theta$.

This lemma says that the block production may stop at most $\theta$ at the beginning of the new synch-epoch.

**Proof Sketch:** With the chain quality property, we can guarantee that more than half of arrival times of the blocks used in the median algorithm sent on time. Therefore, the output of all validators' median algorithm is the one which is sent on time. The details of the proof is in Theorem 1 our paper [Consensus on Clocks](https://eprint.iacr.org/2019/1348).

Having $\theta$ small enough is important not to slow down the block production mechanism a while after a sync-epoch. For example, (a very extreme example)  we do not want to end up with a new clock that says that we are in the year 2001 even if we are in 2019. In this case, honest validators may wait 18 years to execute an action that is supposed to be done in 2019.

### Temporarily Clock Adjustment

For validators who were offline at some point during one synch-epoch, they can adjust their clock temporarily (till the next synch epoch) with the following algorithm.

**1. Case:** If $V$ was online at some point of a synch-epoch and when he becomes online if his clock works well, he should continue to collect the arrival time of valid blocks and produce his block according to his clock as usual. A block is considered as valid in this case if it is not equivocated, if the block is sent by the right validator and if its slot number belong to the current synch epoch. In the end of the synch-epoch, if he has collected $n$ arrival time of valid blocks he runs the median algorithm with these blocks.
If it has less than $n$ blocks it should wait till collecting $n$ arrival time of valid blocks. We note that he does not run the median algorithm not only with the arrival time of the finalized blocks.

**2. Case:** If $V$ was online at some point of a synch-epoch and when he becomes online if his clock does not work anymore, he should continue to collect the arrival time of valid blocks. He can adjust his clock according to e.g., the arrival time of the last finalized block in GRANDPA to continue to produce block. He can use this clock till collecting $n$ valid blocks. After collecting $n$ valid blocks he should readjust his clock according to the output of the median algorithm with these $n$ valid blocks.

With the temporary clock adjustment, we can guarantee that the difference between this new clock and an honest parties clock is at most $2\delta_{max} + |\Sigma|$.

**We note that during one sync-epoch the ratio of such offline validators should not be more than 0.05 otherwise it can affect the security of the relative time algorithm.**

---

## 5. Security Analysis

(If you are interested in parameter selection and practical results based on the security analysis, you can directly go to the next section)
BABE is the same as Ouroboros Praos except for the chain selection rule and clock adjustment. Therefore, the security analysis is similar to Ouroboros Praos with few changes.


### Definitions
We give the definitions of security properties before jumping to proofs.

**Definition 1 (Chain Growth (CG)) [1,2]:** Chain growth with parameters $\tau \in (0,1]$ and $s \in \mathbb{N}$ ensures that if the best chain owned by an honest party at the onset of some slot $sl_u$ is $C_u$, and the best chain owned by an honest party at the onset of slot $sl_v \geq sl_u+s$ is $C_v$, then the difference between the length of $C_v$ and $C_u$ is greater or equal than/to $\tau s$.

The honest chain growth (HCG) property is a weaker version of CG which is the same definition with the restriction that $sl_v$  and $sl_u$ are assigned to honest validators. The parameters of HCG are $\tau_{hcg}$ and $s_{hcg}$ instead of $\tau$ and $s$ in the CG definition.

**Definition 2 (Existential Chain Quality (ECQ)) [1,2]:** Consider a chain $C$ possessed by an honest party at the onset of a slot $sl$. Let $sl_1$ and $sl_2$ be two previous slots for which $sl_1 + s_{ecq} \leq sl_2 \leq sl$. Then $C[sl_1 : sl_2]$ contains at least one block generated by an honest party.

**Definition 2 (Chain Density (CD)):** The CD property with parameters $s_{cd} \in \mathbb{N}$ ensures that any portion $B[s_u:s_v]$ of  a final blockchain $B$ spanning between rounds $s_u$ and $s_v  = s_u + s_{cd}$   contains more honest blocks.


**Definition 3 (Common Prefix)** Common prefix with parameters $k \in \mathbb{N}$ ensures that any chains $C_1, C_2$ possessed by two honest parties at the onset of the slots $sl_1 < sl_2$ are such satisfies $C_1^{\ulcorner k} \leq C_2$ where  $C_1^{\ulcorner k}$ denotes the chain obtained by removing the last $k$ blocks from $C_1$, and $\leq$ denotes the prefix relation.


With using these properties, we show that BABE has persistence and liveness properties. **Persistence** ensures that, if a transaction is seen in a block deep enough in the chain, it will stay there and **liveness** ensures that if a transaction is given as input to all honest players, it will eventually be inserted in a block, deep enough in the chain, of an honest player.

### Security Proof of BABE
We analyze BABE with the NTP protocol and with the Median algorithm.

We first prove that BABE (both versions) satisfies chain growth, existential chain quality and common prefix properties in one epoch. We also show the chain density property for the BABE with median. Then, we prove that BABE is secure by showing that BABE satisfies persistence and liveness in multiple epochs.

In Polkadot, all validators have equal stake (the same chance to be selected as slot leader), so the relative stake is $\alpha_i = 1/n$ for each validator where $n$ is the total number of validators. We assume that the ratio of honest validators is $\alpha$ and the ratio of validators sending on time is $\alpha_{timely}$.

We use notation $p_h$ (resp. $p_m$) to show the probability of an honest validator (resp. a malicious validator) is selected. Similarly, we use $p_H$ (resp. $p_M$) to show the probability of *only*  honest validators (resp. malicious validators) are selected. $p_{\bot}$ is the probability of having an empty slot (no validator selected).

$$
p_\bot=\mathsf{Pr}[sl = \bot] = \prod_{i\in \mathcal{P}}1-\phi(\alpha_i) = \prod_{i \in \mathcal{P}} (1-c)^{\alpha_i} = 1-c
$$

$$
p_M = \prod_{i \in \mathcal{P_h}} 1- \phi(1/n) \sum_{i \in \mathcal{P}_m} \binom{\alpha n}{i}\phi(1/n)^i (1- \phi(1/n))^{\alpha n - i} 
$$

$$
p_h = c - p_M
$$

$$
p_H = \prod_{i \in \mathcal{P_m}} 1- \phi(1/n) \sum_{i \in \mathcal{P}_h} \binom{\alpha n}{i}\phi(1/n)^i (1- \phi(1/n))^{\alpha n - i}
$$

$$
p_m = c - p_H
$$

The probability of having timely validator is 

$$
p_H\_\mathsf{timely} = \prod_{i \in \mathcal{P_m}} 1- \phi(1/n) \sum_{i \in \mathcal{P}_h} \binom{\alpha_{timely} n}{i}\phi(1/n)^i (1- \phi(1/n))^{\alpha_{timely} n - i}
$$

and probability of having non-timely validator is $p_m\_\mathsf{timely} = c - p_H\_\mathsf{timely}$.


The validators in BABE with NTP are perfectly synchronized (i.e., the difference between their clocks is 0). On the other hand, the validators in BABE with the median algorithm have their clocks differ at most $\delta\_max + |2\Sigma|$.
In BABE with the NTP, any honest validator builds on top of an honest block generated in slot $sl$ for sure if the block arrives all validators before starting the next **non-empty** slot $sl_{\mathsf{next}}$. We call these slots good slots. In BABE with NTP, a slot $sl$ is good if it is assigned to only honest validators and the next $\D = \lfloor \frac{\delta\_max}{T}\rfloor$ slots are empty. However, it is different in BABE with the median algorithm because of the clock difference between validators. If a slot is assigned to an honest validator that has the earliest clock, in order to make her to build on top of blocks of all previous honest slots for sure, we should make sure that this validator sees all blocks of the previous slots before generating her block. We can guarantee this if previous $\lfloor \frac{\delta\_max + |2 \Sigma|}{T}\rfloor$ slots are empty. Also, if a slot is assigned to an honest validator that has the latest clock,  we should make sure that the next honest block producers see the block of the latest validator before generating her block. We can guarantee this if the next  $\lfloor \frac{2\delta\_max + |2 \Sigma|}{T}\rfloor$ slots are empty. We use $\D_m = \lfloor \frac{2\delta\_max + |2 \Sigma|}{T}\rfloor + \lfloor \frac{\delta\_max + |2 \Sigma|}{T}\rfloor$ in our analysis below.


**Theorem 1:** BABE with NTP satisfies HCG property with parameters $\tau_{hcg} = p_hp_\bot^\D(1-\omega)$ where $0 < \omega < 1$ and $s_{hcg} > 0$ in $s_{hcg}$ slots  with probability $1-\exp(-\frac{ p_h s_{hcg} \omega^2}{2})$.

**Proof:** We need to count the honest and good slots (i.e., the slot assigned to at least one honest validator and the next $\D$ slots are empty) (Def. Appendix E.5. in [Genesis](https://eprint.iacr.org/2018/378.pdf)) to show the HCG property. The best chain grows one block in honest slots. If honest slots out of $s_{hcg}$ slot are less than $s_{hcg}\tau_{hcg}$, the HCG property is violated. The probability of having an honest and good slot is $p_hp_\bot^\D$.

We find below the probability of less than $\tau_{hcg} s_{hcg}$ slots are honest slots. From Chernoff bound we know that

$$
\Pr[\sum honest \leq  (1-\omega) p_h p_\bot s_{hcg}] \leq \exp(-\frac{p_hp_\bot^\D s_{hcg} \omega^2}{2})
$$

$$
\tag{$\blacksquare$}
$$
<br/>
<br/>

BABE with median satisfies HCG property with parameters $\tau_{hcg} = p_hp_\bot^{D_m}(1-\omega)$ where $0 < \omega < 1$ and $s_{hcg} > 0$ in $s_{hcg}$ slots  with probability $1-\exp(-\frac{ p_hp_\bot^{\D_m} s_{hcg} \omega^2}{2})$.


**Theorem 2 (Chain Densisty)**  Chain desisty property is satisfied with $s_{cd}$ in BABE with probability $1 - \exp(-\frac{p_H\_\mathsf{timely}p_\bot^{\D_m} s_{cd} \omega_H^2}{2}) - \exp(-\frac{\gamma^2s_{cd}p_m\_\mathsf{timely}}{2+\gamma}) - \exp(-\ell)$ where $\omega_H \in (0,1)$ and $\gamma > 0$.

**Proof:** We first find the minimum difference between the number of honest slots and the number of malicious slots in $s_{cd}$ slots belonging one synch-epoch. For this, we need to find the minimum number of honest slots $H$ and a maximum number of honest slots $m$.

We can show with the Chernoff bound that for all $\omega \in (0,1)$

$$
\Pr[H <  (1-\omega_H) p_H\_\mathsf{timely} p_\bot^{\D_m} s_{cd}] \leq \exp(-\frac{p_H\_\mathsf{timely}p_\bot^{\D_m} s_{cd} \omega^2}{2})
$$

and for all $\gamma >0$

$$
\Pr[m >  (1+\gamma) p_m\_\mathsf{timely} s_{cd}] \leq \exp(-\frac{\gamma^2s_{cd}p_m\_\mathsf{timely}}{2+\gamma})
$$

So, $dif = h-m \geq s_{cd}((1-\omega)p_H\_\mathsf{timely}p_\bot^{\D_m} - (1+\gamma) p_m\_\mathsf{timely})$. Let's denote $dif = m + \ell$ where $\ell \geq dif - (1+\gamma) p_m\_\mathsf{timely} s_{cd}$

Assume that the last block of the previous sync-epoch is $B$. So, we only consider the chains that are constructed on top of $B$. Consider a chain $C$ which has finalized blocks spanned in subslots $sl_u$ and $sl_v = sl_u + s_{cd}$. The longest subchain produced between $sl_u$ and $sl_v$ is $h \geq 2m + \ell$ because of the honest chain growth among the chains constructed on top $B$. The longest subchain with more malicious blocks than the honest blocks is possible with $m$ malicious blocks and $m$ honest blocks. However, this chain can never beat the longest subchain produced at the end of $sl_u$ except with probability $\frac{1}{2^\ell}$. This means that there is not any subchain that has more malicious block and can be finalized except with a negligible probability. Therefore, all finalized chains in a synch epoch has more honest slots.

$$
\tag{$\blacksquare$}
$$
<br/>
<br/>

We note that we need the chain densisty property only for the BABE with the median algorithm.

**Theorem 3 (Existential Chain Quality):** Let $\D \in \mathbb{N}$ and let $\frac{p_h\\p_\bot^\D}{c} > \frac{1}{2}$. Then, the probability of an adversary $\A$ violates the ECQ property with parameters $k_{cq}$ with probability at most $e^{-\Omega(k_{cq})}$ in BABE with NTP.

**Proof (sketch):** If $k$ proportion of a chain does not include any honest blocks, it means that the malicious slots are more than the good and honest slots between the slots that spans these $k$ blocks. Since the probability of having good and honest slots is greater than $\frac{1}{2}$, having more bad slots falls exponentially with $k_{cq}$. Therefore, the ECQ property is broken in $R$ slots at most with the probability $e^{-\Omega(k_{cq})}$.

$$
\tag{$\blacksquare$}
$$
<br/>
<br/>

Let $\D_m \in \mathbb{N}$ and let $\frac{p_Hp_\bot^{\D_m}}{c} > \frac{1}{2}$. Then, the probability of an adversary $\A$ violates the ECQ property with parameters $k_{cq}$ with probability at most $e^{-\Omega(k_{cq})}$ in BABE with median.

**Theorem 4 (Common Prefix):** Let $k,\D \in \mathbb{N}$ and let $\frac{p_H p_\bot^\D}{c} > \frac{1}{2}$, the adversary violates the common prefix property with parammeter $k$ in $R$ slots with probability at most $\exp(− \Omega(k))$  in BABE with NTP.
We should have the condition $\frac{p_Hp_\bot^{\D_m}}{c} > \frac{1}{2}$ for BABE with median.

#### Overall Results:

According to Lemma 10 in [Genesis](https://eprint.iacr.org/2018/378.pdf) **chain growth** is satisfied with

$$
s_{cg} = 2 s_{ecq} + s_{hcg} \text{ and } \tau = \tau_{hcg} \frac{s_{hcg}}{2 s_{ecq} + s_{hcg}}
$$ 

and **chain quality** is satisfied with 

$$
s_{cq} = 2 s_{ecq} + s_{hcq} \text{ and } \mu = \tau_{hcq}\frac{s_{hcq}}{2s_{ecq}+s_{hcq}}
$$

**Theorem 5 (Persistence and Liveness BABE with NTP):** Assuming that $\frac{p_H p_\bot^\D}{c} > \frac{1}{2}$ and given that  $k_{cq}$ is the ECQ parameter, $k > 2k_{cq}$ is the CP parameter, $s_{hcg} = k/\tau_{hcg}$, $s_{ecq} = k_{cq}/\tau$, the epoch length is $R = 2s_{ecq} + s_{hcg}$ BABE with NTP is persistent and live.

**Proof (Sketch):** The overall result says that $\tau = \tau_{hcg}\frac{s_{hcg}}{2s_{ecq}+s_{hcg}} = \frac{k}{s_{hcg}}\frac{s_{hcg}}{2s_{ecq}+s_{hcg}} = \frac{k}{R}$. The best chain at the end of an epoch grows at least $k$ blocks in one epoch thanks to the chain growth.

 Since $k > 2k_{cq}$, the last $k_{cq}$ block of includes at least one honest block. Therefore, the randomness includes one honest randomness and the adversary can have at most $s_{ecq}$ slots to change the randomness. This grinding effect can be upper-bounded by $s_{ecq}(1-\alpha)nq$ where $q$ is the hashing power [2]. The randomness generated by an epoch is finalized at latest one epoch later thanks to the common prefix property. Similary, the session key update which is going to be used in three epochs later is finalized one epoch later before a randomness of the epoch where the new key are going to be used starts to leak.
Therefore, BABE with NTP is persistent and live.

$$
\tag{$\blacksquare$}
$$
<br/>
<br/>

**Theorem 6 (Persistence and Liveness BABE with the Median Algorithm):** Assuming that $\frac{p_H p_\bot^{\D_m}}{c} > \frac{1}{2}$ and  $\tau_{hcg}-\tau_{hcg}\mu_{hcq} > p_m (1+\gamma)$ where $\tau_{hcg} = p_h p_\bot^{\D_m} (1-\omega)$, $s_{cd}$, the clock difference is between honest valdators is at most $\D_m$, BABE with median is persistent and live given that given that  $k_{cq}$ is the ECQ parameter, $k > 2k_{cq}$ is the CP parameter, $s_{hcg} = k/\tau_{hcg}$, $s_{ecq} = k_{cq}/\tau$.

**These results are valid assuming that the signature scheme with account key is  EUF-CMA (Existentially Unforgible Chosen Message Attack) secure, the signature scheme with the session key is forward secure, and VRF realizing is realizing the functionality defined in [2].**

---

## 6. Practical Results

In this section, we find parameters of two versions of BABE to achieve the security in BABE.

We fix the lifetime of the protocol as $\mathcal{L}=3 \text{ years}  = 94670777$ seconds. We denote the slot time by $T$ (e.g., $T = 6$ seconds).
The lifetime of the protocol in terms of slots is $L = \frac{\mathcal{L}}{T}$. The maximum network delay is $\D$.

### BABE with the NTP

* Define $\delta\_max$ and $T$. Let $\D = 0$ if $\delta_{\max} < T$. Otherwise, let $\D = \lceil \frac{\delta\_max - T}{T}\rceil$
* Decide the parameter $c$ such that the condition $\frac{p_Hp_\bot^{\D}}{c} > \frac{1}{2}$ is satisfied. If there is not any such $c$, then consider to increase $\alpha$ (honest validator assumption) or decrease $\D$ (more optimistic network assumption).
* Set up a security bound $p_{attack}$ to define the probability of an adversary to break BABE in e.g., 3 years. Of course, very low $p$ is better for the security of BABE but on the other hand it may cause to have very long epochs and long probabilistic finalization. Therefore, I believe that setting $p_{attack}=0.005$ is reasonable enough in terms of security and performance.
* Set  $\omega \geq 0.5$ (e.g., 0.5) and find $s_{ecq}$ and $s_{hcq}$ to set the epoch length $R = 2 s_{ecq} + s_{hcg}$ such that $p_{attack} \leq p$. For this we need an initial value $k_{cp}$ and find $s_{ecq}, s_{hcg}$ and $\tau$ that satisfies the three equations below:

From Theorem 6, we want that the best chain grows at least $k$ blocks. Therefore, we need

$$
(2s_{ecq} + s_{hcg})\tau = k\text{ }\text{ }\text{ }\text{ }\text{ }\text{ (1)}
$$

We need $s_{ecq}$ slots to guarantee $k_{cq}$ blocks growth for the ECQ property. So, we need:

$$
\tau s_{ecq} = k_{cq} \text{ }\text{ }\text{ }\text{ }\text{ }\text{ }\text{ }\text{ }\text{ (2)}
$$

Lastly, we need the following as given in the Overall Result:

$$
\tau = \tau_{hcg} \frac{s_{hcg}}{2 s_{ecq} + s_{hcg}}\text{ }\text{ }\text{ }\text{ }\text{ (3)}
$$

Iterate $k_{cp}$ to find $s_{hcg}, s_{ecq}, \tau$ that satisfy above conditions until $p_{attack} \leq p$:

1.   Let $k = 4 k_{cp}$ (The CQ property parameter) We note that $4 k_{cp}$ is the optimal value that minimizes $R = 2 s_{ecq} + s_{hcg}$.
1.   $t_{hcg} = p_h  p_\bot^\D  (1-\omega)$ (to satisfy the condition in Theorem 1)
1.   $s_{hcg} = k / t_{hcg}$ (from Equation (1) and (3))
1.   $\tau = \frac{k - 2k_{cq}}{s_{hcg}}$ (from Equation (1) and (2))
1.   $s_{ecq} = k_{cq}/\tau$
1.   $p = \lceil \frac{L}{T}\rceil\frac{2^{20}(1-\alpha)n}{R}(p_{ecq} + p_{cp} + p_{cg})$

After finding $k_{cq}$ such that $p \leq p_{attack}$, let the epoch length $R = 2s_{ecq}+s_{hcg}$.

The parameters below are computed with the code in https://github.com/w3f/research/blob/master/experiments/parameters/babe_NTP.py. In this code, we choose the parameter $c$ not only according to security conditions but also according to having in expectation twice more single leader than multiple leaders.

-################### PARAMETERS OF BABE WITH NTP $\D = 0$ ###################

c = 0.52, slot time T = 6

It is secure in 3 years with a probability 0.99523431732

It is resistant to (6 - block generation time) second network delay

-~~~~~~~~~~~~~~ Common Prefix Property ~~~~~~~~~~~~~~

k = 140

It means: Prune the last 140 blocks of the best chain. All the remaining ones are probabilistically finalized

-~~~~~~~~~~~~~~ Epoch Length ~~~~~~~~~~~~~~

Epoch length should be at least 1440 slots,2.4 hours


If we want more network resistance, $e.g.,\D = 1$, the parameters should be selected as follows:

-################### PARAMETERS OF BABE WITH NTP $\D = 1$ ###################

c = 0.22, slot time T = 6

It is secure in 3 years with probability 0.996701592969

It is resistant to (12 - block generation time) second network delay

-~~~~~~~~~~~~~~ Common Prefix Property ~~~~~~~~~~~~~~

k = 172

It means: Prun the last 172 blocks of the best chain. All the remaining ones are probabilistically finalized

-~~~~~~~~~~~~~~ Epoch Length ~~~~~~~~~~~~~~

Epoch length should be at least 4480 slots, 7.46666666667 hours



### BABE with the Median Algorithm

* Define $\alpha_{timely} = 0.85$, $\ell = 20$, $\omega_H = 0.3$ and $\gamma = 0.5$ in Theorem 2.

* Define $\delta\_max$ and $T$. Let $\D_m = \lfloor \frac{2\delta\_max + |2 \Sigma|}{T}\rfloor + \lfloor \frac{\delta\_max + |2 \Sigma|}{T}\rfloor$

* Decide the parameter $c$ such that the condition $\frac{p_Hp_\bot^{\D}}{c} > \frac{1}{2}$ and $\frac{p_H\_\mathsf{timely} (1- \omega_H)}{p_m\_\mathsf{timely} (1+\gamma)} > 2$
is satisfied. If there is not any such $c$, then consider increasing $\alpha$  (honest validator assumption) or $\alpha_{timely}$ or decreasing $\D$ (more optimistic network assumption).

* Do the rest as in BABE with NTP.

Finding synch-epoch length

1.  Set $s_{cd}$ with respect to Theorem 2.


The parameters below are computed with the code in https://github.com/w3f/research/blob/master/experiments/parameters/babe_median.py

-############## PARAMETERS OF BABE WITH THE MEDIAN ALGORITHM ##############

c = 0.38, slot time T = 6

It is secure in 3 years with probability 0.99656794973

It is resistant to 2.79659722222 second network delay and 0.198402777778 seconds drift in one sync-epoch

-~~~~~~~~~~~~~~ Common Prefix Property ~~~~~~~~~~~~~~

k = 140
It means: Prune the last 140 blocks of the best chain. All the remaining ones are probabilistically finalized

-~~~~~~~~~~~~~~ Epoch Length ~~~~~~~~~~~~~~

Sync-Epoch length should be at least 2857 slots, 4.76166666667 hours

Epoch length should be at least 2000 slots,3.33333333333 hours

-~~~~~~~~~~~~~~ Offline validators' parameters for clock adjustment ~~~~~~~~~~~~~~

$n = 200$ for temporarily clock adjustment.

Offline validators should collect

**Some Notes about clock drifts:**
http://www.ntp.org/ntpfaq/NTP-s-sw-clocks-quality.htm#AEN1220
All computer clocks are not very accurate because the frequency that makes time increase is never exactly right. For example the error about 0.001% make a clock be off by almost one second per day.
Computer clocks drift because the frequency of clocks varies over time, mostly influenced by environmental changes such as temperature, air pressure or magnetic fields, etc. Below, you can see the experiment in a non-air conditioned environment on linux computer clocks.  12 PPM correspond to one second per day roughly. I seems that in every 10000 second the change on the clocks are around 1 PPM (i.e., every 3 hours the clocks drifts 0.08 seconds.). We can roughly say that the clock drifts around 1 second per day. If we have sync epoch around 12 hours it means that we have 0.5 second drift and

[![](https://i.imgur.com/Slspcg6.png)](http://www.ntp.org/ntpfaq/NTP-s-sw-clocks-quality.htm#AEN1220)

**Figure. Frequency Correction within a Week**
**For inquieries or questions, please contact** 

[1] Kiayias, Aggelos, et al. "Ouroboros: A provably secure proof-of-stake blockchain protocol." Annual International Cryptology Conference. Springer, Cham, 2017.

[2] David, Bernardo, et al. "Ouroboros praos: An adaptively-secure, semi-synchronous proof-of-stake blockchain." Annual International Conference on the Theory and Applications of Cryptographic Techniques. Springer, Cham, 2018.

[3] Badertscher, Christian, et al. "Ouroboros genesis: Composable proof-of-stake blockchains with dynamic availability." Proceedings of the 2018 ACM SIGSAC Conference on Computer and Communications Security. ACM, 2018.

[4] Aggelos Kiayias and Giorgos Panagiotakos. Speed-security tradeoffs in blockchain protocols. Cryptology ePrint Archive, Report 2015/1019, 2015. http://eprint.iacr.org/2015/1019
