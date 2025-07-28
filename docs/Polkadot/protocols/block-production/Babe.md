---
title: BABE
---

![](BABE.png)

Polkadot produces relay chain blocks using the **B**lind **A**ssignment for **B**lockchain **E**xtension protocol (BABE), which assigns block production slots based on a randomness cycle similar to that used in Ouroboros Praos [2]. The process unfolds as follows: All block producers possess a verifiable random function (VRF) key, which is registered alongside their locked stake. These VRFs generate secret randomness, determining when each producer is eligible to create a block. The process carries an inherent risk that producers may attempt to manipulate the outcome by grinding through multiple VRF keys. To mitigate this, the VRF inputs must incorporate public randomness that is created only after the VRF key is established. 

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


In this case, the chain selection rule does not follow Ouroboros Genesis [3], as that rule is intended for parties that come online after a period of inactivity and lack information about the current valid chain. For parties that remain continously online, the Genesis rule and Praos are indistinguishable with negligible probability. Thanks to Grandpa finality, newcomers have a reliable reference point to build their chain, making the Genesis rule unnecessary.

---

## 4. Clock Adjustment (Relative Time Algorithm)

 For the security and completeness of BABE, parties must be aware of the current slot. Typically, validators rely on system clocks sinchronized via by the Network Time Protocol. This introduces a trust assumption, and if an NTP server is compromised, BABE's security can no longer be upheld. To mitigate such a risk, validators can determine slot timing without relying on NTP. 
 
 Let's assume a partially synchronous network scenario, where any message sent by a validator is delivered within at most $\D$-slots, an unknown parameter. Since each party relies on a local clock not sinchronized by any external source such as NTP or GPS, a validator should store the arrival time of the genesis block as $t_0$, which serves as a reference point marking the start of the first slot. This starting point varies accross validators. Assuming the maximum deviation in first slot start time between validators is at most $\delta$, each party should divide its timeline into slots and periodically update its local clock according to the following algorithm.



**Median Algorithm:**
The median algorithm is executed by all validators at the end of sync-epochs [4]. The first sync-epoch ($\varepsilon = 1$) begins once the genesis block is released. Subsequent sync-epochs ($\varepsilon > 1$) begin when the slot number of the last (probabilistically) finalized block is $\bar{sl}_{\varepsilon}$, defined as the smallest slot number such that  $\bar{sl}_{\varepsilon} - \bar{sl}_{\varepsilon-1} \geq s_{cq}$ where $\bar{sl}_{\varepsilon-1}$ is the slot number of the last finalized block from sync-epoch $\varepsilon-1$, and $s_{cq}$ is the chain quality (CQ) parameter. If the previous epoch is the first epoch then $sl_{e-1} = 0$.

To identify the last (probabilistically) finalized block: Retrieve the best blockchain according to the chain selection rule, prune the final $k$ blocks from this chain, and define the last finalized block as the last block of the pruned best chain, where $k$ is set according to the common prefix property.

The protocol details are as follows: Each validator records the arrival time $t_i$ of valid blocks using its local clock. At the end of a sync-epoch, each validator retrieves the arrival times of valid and finalized blocks with slot number $sl'_x$ where
* $\bar{sl}_{\varepsilon-1} < sl_x \leq \bar{sl}_{\varepsilon}$ if $\varepsilon > 1$.
* $\bar{sl}_{\varepsilon-1} \leq sl_x \leq \bar{sl}_{\varepsilon}$ if $\varepsilon = 1$.

Assuming that no such $n$ blocks belong to the current sync-epoch, and denoting the stored arrival times of blocks in this sync-epoch as $t_1,t_2,...,t_n$, with corresponding slot numbers $sl'_1,sl'_2,...,sl'_n$, validators should select a slot number $sl > sl_e$ and execute the median algorithm as follows:


```
for i = 0 to n:
    a_i = sl - sl'_i
    store t_i + a_i * T to lst
lst = sort (lst)
return median(lst)
```

Ultimately, each validator adjusts its local clock by mapping slot $sl$ to the output of the median algorithm.


The image below illustrates the algorithm using a chain-based example in the first epoch, where $s_{cq} = 9$ and $k=1$:

![](https://i.imgur.com/jpiuQaM.png)


**Lemma 1** or the difference between outputs of validators' median algorithms: Asuming $\delta\_max$ is the maximum network delay, the maximum difference between start time is at most $\delta\_max$.

**Proof Sketch:** Since all validators run the median algorithm using the arrival times of the same blocks, the difference between the output of each validator's median algorithm is bounded by at most $\delta\_max$.

**Lemma 2** or Adjustment Value: Assuming the maximum total drift between sync-epochs is at most $\Sigma$ and that $2\delta\_max + |\Sigma| \leq \theta$, the maximum difference between the new start time of a slot $sl$ and the old start time of $sl$ is at most $\theta$.

In simple terms, this lemma states that the block production may be delayed by at most $\theta$ at the beginning of the new synch-epoch.

**Proof Sketch:** The chain quality property ensures that more than half of arrival times for blocks used in the median algorithm are timely. As a result, the output of each validator's median algorithm corresponds to a block that was delivered on time. A formal proof is provided in Theorem 1 of our paper [Consensus on Clocks](https://eprint.iacr.org/2019/1348).

Keeping $\theta$ small is crucial to prevent delays in block production after a sync-epoch. For example (albeit an extreme one), we wouldn't want a validstor's adjusted clock to indicate the year 2001 when it's actually 2019. In such a case, honest validators might have to wait 18 years before executing an action that was originally scheduled for 2019.

### Temporary Clock Adjustment

The following algorithm permits validators who were offline during part of a synch-epoch to temporarily adjust their local clocks, valid until the next synch-epoch.

**1. Case:** If validator $V$ was online at any point of a synch-epoch, and upon returning online its clock is functioning correclty, it should resume collecting the arrival times of valid blocks and produce blocks according to its local clock as usual. A block is considered valid in this case if it is not equivocated, is sent by the right validator,and its slot number falls within the current synch epoch. 

At the end of the synch-epoch, if $V$ has collected $n$ valid block arrival times, it should run the median algorithm using these blocks. In case it has fewer than $n$ blocks, it must wait until the required $n$ arrival times have been gathered. The validator does not run the median algorithm solely with the arrival times of finalized blocks.

**2. Case:** If $V$ was online at any point during a synch-epoch and, upon reconnecting, its clock is no longer functioning properly, it should continue collecting the arrival times of valid blocks. The validator may temporarily adjust its clock using, for example, the arrival time of the last finalized block in GRANDPA, and resume block production accordingly. This temporary clock can be used until $n$ valid blocks have been collected. Once this condition is met, the validator should re-adjust its clock based on the output of the median algorithm applied to these blocks.

With the temporary clock adjustment, it is possible to ensure that the difference between the time recorded by the adjusted clock and that of an honest party's clock is bounded by at most $2\delta_{max} + |\Sigma|$.

**We note that during one sync-epoch the ratio of such offline validators should not be more than 0.05 otherwise it can affect the security of the relative time algorithm.**

---

## 5. Security Analysis

BABE functions similarly to Ouroboros Praos, with the exception of the chain selection rule and clock synchronization mechanism. From a security analysis perspective, BABE closely resembles Ouroboros Praos, albeit with a few notable differences. If you are more interested in parameter selection and practical outcomes resulting from the security analysis, feel free to skip this section and proceed directly to the next.


### Definitions
Before we dive into the proofs, let’s establish some key definitions.

**Definition 1 or Chain Growth (CG) [1,2]:** Chain growth with parameters $\tau \in (0,1]$ and $s \in \mathbb{N}$ guarantees that if the best chain held by an honest party at the beginning of slot $sl_u$ is $C_u$, and the best chain at the beginning of slot $sl_v \geq sl_u+s$ is $C_v$, then the length of $C_v$ is at least $\tau s$ greater than the length of $C_u$.

The honest chain growth (HCG) property is a relaxed version of the Chain Growth (CG) property, defined identically except for the added constraint that both $sl_v$ and $sl_u$ are assigned to honest validators. The parameters for HCG are $\tau_{hcg}$ and $s_{hcg}$, in place of $\tau$ and $s$ used in the CG definition.

**Definition 2 or Existential Chain Quality (ECQ) [1,2]:** Consider a chain $C$ held by an honest party at the beginning of slot $sl$. Let $sl_1$ and $sl_2$ be two earlier slots such that $sl_1 + s_{ecq} \leq sl_2 \leq sl$. Then, the segment $C[sl_1 : sl_2]$ contains at least one block produced by an honest party.

**Definition 2 or Chain Density (CD):** The CD property, with parameter $s_{cd} \in \mathbb{N}$, ensures that any segment $B[s_u:s_v]$ of the final blockchain $B$, spanning rounds $s_u$ to $s_v  = s_u + s_{cd}$, contains a majority of blocks produced by honest parties.


**Definition 3 or Common Prefix** The Common Prefix property, with parameter $k \in \mathbb{N}$, ensures that for any chains $C_1, C_2$ held by two honest parties at the beginning of slots $sl_1$ and $sl_2$, respectively, where $sl_1 < sl_2$, it holds that $C_1^{\ulcorner k} \leq C_2$. Here,  $C_1^{\ulcorner k}$ denotes the chain obtained by removing the last $k$ blocks from $C_1$, and $\leq$ represents the prefix relation.


The use of these properties demonstrates BABE's persistence and liveness properties. **Persistence** ensures that if a transaction appears in a block sufficiently deep in the chain, it will remain there permanently. **Liveness** guaranteess that if a transaction is provided as input to all honest parties, it will eventually be included in a block, deep enough in the chain, by an honest party.

### Security Proof of BABE
We analyze BABE with the NTP protocol and with the Median algorithm.

The first step is to prove that both versions of BABE satisfy the chain growth, existential chain quality, and common prefix properties within a single epoch, as well as to establish the chain density property specifically for BABE with median. The next step is to demonstrate BABE's overall security by showing that it satisfies persistence and liveness across multiple epochs.

In Polkadot, all validators have an equal chance of being selected as slot leaders due to equal stake allocation. As a result, each validator's relative stake is given by $\alpha_i = 1/n$, where $n$ is the total number of validators. We assume that the proportion of honest validators is $\alpha$, and the proportion of validators sending on time is denoted by $\alpha_{timely}$.

Using the notation $p_h$ (resp. $p_m$), we express the probability of selecting an honest (respectively malicious) validator. Similarly, $p_H$ (respectively $p_M$) denotes the probability of selecting *only*  honest (respectively malicious) validators. $p_{\bot}$ represents the probability of an empty slot, where no validator is selected.

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

The probability of selecting a timely validator is 

$$
p_H\_\mathsf{timely} = \prod_{i \in \mathcal{P_m}} 1- \phi(1/n) \sum_{i \in \mathcal{P}_h} \binom{\alpha_{timely} n}{i}\phi(1/n)^i (1- \phi(1/n))^{\alpha_{timely} n - i}
$$

Meanwhile, the probability of selecting a non-timely validator is given by $p_m\_\mathsf{timely} = c - p_H\_\mathsf{timely}$.


Validators in BABE who use NTP are perfectly synchronized (i.e., there is no difference between the time shown on their clocks), whereas validators using the median algorithm may experience a clock discrepancy of up to $\delta\_max + |2\Sigma|$.
An honest validator in BABE with the NTP can build upon an honest block generated in slot $sl$ if the block reaches all validators before the next **non-empty** slot $sl_{\mathsf{next}}$. Such slots are referred to as good slots. In other words, a slot $sl$ is considered good if it is assigned exclusively to an honest validators and the following $\D = \lfloor \frac{\delta\_max}{T}\rfloor$ slots are empty. 

For validators in BABE that rely on the median algorithm, the process diverges due to clock offsets among validators. If a slot is assigned to an honest validator whose clock runs earliest, then in order to build on top of all blocks from prior honest slots, that validator must see those blocks before generating their own. This requirement is met only if the preceding $\lfloor \frac{\delta\_max + |2 \Sigma|}{T}\rfloor$ slots are empty. 

Conversly, if a slot is assigned to an honest validator whose clock runs latest, it is crucial that subsequent honest block producers see this validator's block before producing their own. This can be ensured if the next  $\lfloor \frac{2\delta\_max + |2 \Sigma|}{T}\rfloor$ slots are empty. 

To accomodate both scenarios in our analysis, we use the parameter $\D_m = \lfloor \frac{2\delta\_max + |2 \Sigma|}{T}\rfloor + \lfloor \frac{\delta\_max + |2 \Sigma|}{T}\rfloor$


**Theorem 1:** BABE with NTP satisfies the HCG property with parameters $\tau_{hcg} = p_hp_\bot^\D(1-\omega)$ where $0 < \omega < 1$ and $s_{hcg} > 0$. The property holds over $s_{hcg}$ slots with probability $1-\exp(-\frac{ p_h s_{hcg} \omega^2}{2})$.

**Proof:** To demonstrate the HCG property, it is necesssary to count the *honest* and *good* slots (slots assigned to at least one honest validator, followed by $\D$ slots are empty) (see Definition E.5. in [Genesis](https://eprint.iacr.org/2018/378.pdf)). The best chain grows one block during each honest slot. If the number of honest slots within $s_{hcg}$ total slots is less than $s_{hcg}\tau_{hcg}$, the HCG property no longer holds. The probability of encountering an honest and good slot is given by $p_hp_\bot^\D$.

Below, we present the probability that fewer than $\tau_{hcg} s_{hcg}$ of the slots are honest. Using the Chernoff bound, we know that

$$
\Pr[\sum honest \leq  (1-\omega) p_h p_\bot s_{hcg}] \leq \exp(-\frac{p_hp_\bot^\D s_{hcg} \omega^2}{2})
$$

$$
\tag{$\blacksquare$}
$$
<br/>
<br/>

BABE with median algorithm satisfies the HCG property with parameters $\tau_{hcg} = p_hp_\bot^{D_m}(1-\omega)$, where $0 < \omega < 1$ and $s_{hcg} > 0$. The probability holds over $s_{hcg}$ slots with probability $1-\exp(-\frac{ p_hp_\bot^{\D_m} s_{hcg} \omega^2}{2})$.


**Theorem 2 or Chain Density**  The Chain Density (CD) property is satisfied over $s_{cd}$ slots in BABE with probability $1 - \exp(-\frac{p_H\_\mathsf{timely}p_\bot^{\D_m} s_{cd} \omega_H^2}{2}) - \exp(-\frac{\gamma^2s_{cd}p_m\_\mathsf{timely}}{2+\gamma}) - \exp(-\ell)$, where $\omega_H \in (0,1)$ and $\gamma > 0$.

**Proof:** The first step is to determine the minimum difference between the number of honest slots and the number of malicious slots within $s_{cd}$ slots of a single synch-epoch. To achieve this, we must identify the minimum number of honest slots, denoted by $H$, and the maximum number of malicious slots, denoted by $m$.

Using the Chernoff bound, we can bound the probability of deviation for all $\omega \in (0,1)$:

$$
\Pr[H <  (1-\omega_H) p_H\_\mathsf{timely} p_\bot^{\D_m} s_{cd}] \leq \exp(-\frac{p_H\_\mathsf{timely}p_\bot^{\D_m} s_{cd} \omega^2}{2})
$$

and for all $\gamma >0$

$$
\Pr[m >  (1+\gamma) p_m\_\mathsf{timely} s_{cd}] \leq \exp(-\frac{\gamma^2s_{cd}p_m\_\mathsf{timely}}{2+\gamma})
$$

So, $dif = h-m \geq s_{cd}((1-\omega)p_H\_\mathsf{timely}p_\bot^{\D_m} - (1+\gamma) p_m\_\mathsf{timely})$. Let's denote $dif = m + \ell$ where $\ell \geq dif - (1+\gamma) p_m\_\mathsf{timely} s_{cd}$

Assuming the last block of the previous sync-epoch is denoted by $B$, the chains under consideration are those constructed on top of $B$. Let $C$ be a chain with finalized blocks spanning subslots $sl_u$ to $sl_v$, where  $sl_v = sl_u + s_{cd}$. The longest subchain produced between $sl_u$ and $sl_v$ satisfies $h \geq 2m + \ell$, due to the honest chain growth among chains built on top of $B$. 

A subchain containing more malicious blocks than honest blocks is achievable with $m$ malicious and $m$ honest blocks. However, such a chain cannot surpass the longest honest subchain, except with probability at most $\frac{1}{2^\ell}$. In other words, a subchain dominated by malicious blocks that can be finalized is possible only with negligible probability. 

Therefore, all finalized chains within a synch epoch contain a majority of honest slots.

$$
\tag{$\blacksquare$}
$$
<br/>
<br/>

The chain densisty property is required only for BABE with the median algorithm.

**Theorem 3 or Existential Chain Quality:** If $\D \in \mathbb{N}$ and $\frac{p_h\\p_\bot^\D}{c} > \frac{1}{2}$ are satisfied, then the probability that an adversary $\A$ violates the ECQ property with parameter $k_{cq}$ is at most $e^{-\Omega(k_{cq})}$ in BABE with NTP.

**Proof (sketch):** If a proportion $k$ of a chain contains no honest blocks, this implies that the number of malicious slots exceeds the number of good and honest slots within the slot range spanning those $k$ blocks. Given that the probability of a slot being good and honest is greater than $\frac{1}{2}$, the likelihood of encountering more bad slots than good ones diminishes exponentially with $k_{cq}$. As a result, the ECQ property may be violated in at most $R$ slots, with probability bounded by $e^{-\Omega(k_{cq})}$.

$$
\tag{$\blacksquare$}
$$
<br/>
<br/>

In BABE with the median algorithm, if $\D_m \in \mathbb{N}$ and $\frac{p_Hp_\bot^{\D_m}}{c} > \frac{1}{2}$, then the probability that an adversary $\A$ violates the ECQ property with parameter $k_{cq}$ is at most $e^{-\Omega(k_{cq})}$.

**Theorem 4 or Common Prefix:** If $k,\D \in \mathbb{N}$ and $\frac{p_H p_\bot^\D}{c} > \frac{1}{2}$, then an adversary can violate the Common Prefix property with parameter $k$ over $R$ slots with probability at most $\exp(− \Omega(k))$ in BABE with NTP.
For BABE with the median algorithm, the condition $\frac{p_Hp_\bot^{\D_m}}{c} > \frac{1}{2}$ must be considered instead.

#### Overall Results:

According to Lemma 10 in [Genesis](https://eprint.iacr.org/2018/378.pdf), the **Chain Growth** property is satisfied with

$$
s_{cg} = 2 s_{ecq} + s_{hcg} \text{ and } \tau = \tau_{hcg} \frac{s_{hcg}}{2 s_{ecq} + s_{hcg}}
$$ 

and the **Chain Quality** property is satisfied with 

$$
s_{cq} = 2 s_{ecq} + s_{hcq} \text{ and } \mu = \tau_{hcq}\frac{s_{hcq}}{2s_{ecq}+s_{hcq}}
$$

**Theorem 5 or Persistence and Liveness of BABE with NTP:** Assuming $\frac{p_H p_\bot^\D}{c} > \frac{1}{2}$ and given that $k_{cq}$ is the ECQ parameter, $k > 2k_{cq}$ is the Common Prefix parameter, $s_{hcg} = k/\tau_{hcg}$ and $s_{ecq} = k_{cq}/\tau$, then the epoch length is $R = 2s_{ecq} + s_{hcg}$, and BABE with NTP is persistent and liveness.

**Proof (Sketch):** The overall result shows that $\tau = \tau_{hcg}\frac{s_{hcg}}{2s_{ecq}+s_{hcg}} = \frac{k}{s_{hcg}}\frac{s_{hcg}}{2s_{ecq}+s_{hcg}} = \frac{k}{R}$. So by the chain growth property, the best chain increases by at least $k$ blocks over the course of a single epoch. 

 Since $k > 2k_{cq}$, the last $k_{cq}$ blocks must contain at least one honest block, and the associated randomness must include at least one honest input. This implies that the adversary has at most $s_{ecq}$ slots to attempt to manipulate the randomness. Such a grinding effect can be upper-bounded by $s_{ecq}(1-\alpha)nq$, where $q$ is the adversary's hashing power [2]. 
 
By the Common Prefix property, the randomness generated during an epoch must be finalized no later than one epoch afterward. Similary, the session key update, used three epochs later, must be finalized one epoch earlier, before the randomness of the epoch in which the new key will be used begins to leak.
Therefore, BABE with NTP is persistent and live.

$$
\tag{$\blacksquare$}
$$
<br/>
<br/>

**Theorem 6 or Persistence and Liveness of BABE with the Median Algorithm:** Assuming that $\frac{p_H p_\bot^{\D_m}}{c} > \frac{1}{2}$ and $\tau_{hcg}-\tau_{hcg}\mu_{hcq} > p_m (1+\gamma)$, where $\tau_{hcg} = p_h p_\bot^{\D_m} (1-\omega)$, $s_{cd}$, and the clock difference between honest valdators is at most $\D_m$, then BABE with median algorithm satisfies persistence and liveness given that:
    
* $k_{cq}$ is the ECQ parameter
 
* $k > 2k_{cq}$ is the CP parameter
 
* $s_{hcg} = k/\tau_{hcg}$
 
* $s_{ecq} = k_{cq}/\tau$.

**These results hold under the following assumptions: the signature scheme using the account key is EUF-CMA (Existentially Unforgeability under Chosen Message Attack) secure, the signature scheme based on the session key is forward-secure, and the VRF correctly realizes the functionality as defined in [2].**

---

## 6. Practical Results

The aim of this section is to present the parameters necessary to achieve security in both versions of BABE.

The protocol lifetime is fixed as $\mathcal{L}=3 \text{ years}  = 94670777$ seconds. Let $T$ denote the slot durationi (e.g., $T = 6$ seconds). The total number of slots over the lifetime is $L = \frac{\mathcal{L}}{T}$. Finally, the maximum network delay is $\D$.

### BABE with the NTP

* Define $\delta\_max$ and $T$. Let $\D = 0$ if $\delta_{\max} < T$; otherwise, let $\D = \lceil \frac{\delta\_max - T}{T}\rceil$
* Choose the parameter $c$ such that $\frac{p_Hp_\bot^{\D}}{c} > \frac{1}{2}$ is satisfied. If no such $c$ exists, consider increasing the honest validator assumption $\alpha$, or adopting a more optimistic network assumption by decreasing $\D$.
* Define a security bound $p_{attack}$ to represent the probability that an adversary can break BABE over a fixed duration (e.g., 3 years). A lower value of $p$ improves security, but may lead to longer epochs and extended probabilistic finalization. A value of $p_{attack}=0.005$ is considered a reasonable compromise between security and performance.
* Set  $\omega \geq 0.5$ (e.g., 0.5), and compute $s_{ecq}$ and $s_{hcq}$ to define the epoch length $R = 2 s_{ecq} + s_{hcg}$ such that the condition $p_{attack} \leq p$ holds. To do this, select an initial value $k_{cp}$ and solve $s_{ecq}, s_{hcg}$ and $\tau$ that satisfy the following three equations:

From Theorem 6, the goal is for the best chain to grow by at least $k$ blocks. To ensure this, the following condition must hold: 

$$
(2s_{ecq} + s_{hcg})\tau = k\text{ }\text{ }\text{ }\text{ }\text{ }\text{ (1)}
$$

To guarantee $k_{cq}$ blocks for the ECQ property, the following is required:

$$
\tau s_{ecq} = k_{cq} \text{ }\text{ }\text{ }\text{ }\text{ }\text{ }\text{ }\text{ }\text{ (2)}
$$

Finally, the Overall Result gives:

$$
\tau = \tau_{hcg} \frac{s_{hcg}}{2 s_{ecq} + s_{hcg}}\text{ }\text{ }\text{ }\text{ }\text{ (3)}
$$

Iterate over $k_{cp}$ to find values for $s_{hcg}, s_{ecq}, \tau$ that satisfy the above conditions until $p_{attack} \leq p$:

1.   Set the parameter for the Chain Quality (CQ) property at $k = 4 k_{cp}$. $4 k_{cp}$ is the optimal value that minimizes the epoch length $R = 2 s_{ecq} + s_{hcg}$.
1.   Compute $t_{hcg} = p_h  p_\bot^\D  (1-\omega)$ to satisfy the condition in Theorem 1
1.   Calculate $s_{hcg} = k / t_{hcg}$ based on Equations (1) and (3)
1.   Determine $\tau = \frac{k - 2k_{cq}}{s_{hcg}}$ by using Equations (1) and (2)
1.   Compute $s_{ecq} = k_{cq}/\tau$
1.   Calculate the security parameter: $p = \lceil \frac{L}{T}\rceil\frac{2^{20}(1-\alpha)n}{R}(p_{ecq} + p_{cp} + p_{cg})$

Once a value for $k_{cq}$ such that $p \leq p_{attack}$ is found, set the epoch length $R = 2s_{ecq}+s_{hcg}$.

The parameters below are computed using the code available at https://github.com/w3f/research/blob/master/experiments/parameters/babe_NTP.py. The parameter $c$ is chosen not only to satisfy security conditions, but also to ensure that, in expectation, the number of single-leader slots is at least twice the number of multi-leader slots. 

-################### PARAMETERS OF BABE WITH NTP $\D = 0$ ###################

c = 0.52, slot time T = 6 seconds

Secure over a 3-year horizon with probability 0.99523431732

Resistant to network delays of up to 6 - block generation time seconds 

-~~~~~~~~~~~~~~ Common Prefix Property ~~~~~~~~~~~~~~

k = 140

This means the last 140 blocks of the best chain are pruned. All preceding blocks are considered probabilistically finalized

-~~~~~~~~~~~~~~ Epoch Length ~~~~~~~~~~~~~~

Epoch length should be at least 1440 slots (2.4 hours)

If greater network resistance is desired ($e.g.,\D = 1$), the parameters should be selected as follows:

-################### PARAMETERS OF BABE WITH NTP $\D = 1$ ###################

c = 0.22, slot time T = 6 seconds

Secure over a 3-year period with probability 0.996701592969

Resistant to network delays of up to 12 - block generation time seconds

-~~~~~~~~~~~~~~ Common Prefix Property ~~~~~~~~~~~~~~

k = 172

This means: Prune the last 172 blocks of the best chain. All preceding blocks are considered probabilistically finalized

-~~~~~~~~~~~~~~ Epoch Length ~~~~~~~~~~~~~~

Epoch length should be at least 4480 slots (approximately 7.46666666667 hours)



### BABE with the Median Algorithm

* Define the following parameters for Theorem 2: $\alpha_{timely} = 0.85$, $\ell = 20$, $\omega_H = 0.3$ and $\gamma = 0.5$.

* Define $\delta\_max$ and $T$. Let $\D_m = \lfloor \frac{2\delta\_max + |2 \Sigma|}{T}\rfloor + \lfloor \frac{\delta\_max + |2 \Sigma|}{T}\rfloor$

* Choose the parameter $c$ such that both of the following conditions are satisfied: $\frac{p_Hp_\bot^{\D}}{c} > \frac{1}{2}$ and $\frac{p_H\_\mathsf{timely} (1- \omega_H)}{p_m\_\mathsf{timely} (1+\gamma)} > 2$. If no such $c$ exists, consider increasing $\alpha$ (honest validator assumption), increasing $\alpha_{timely}$, or decreasing $\D$ (adopting a more optimistic network assumption).

* Proceed with the remaining steps as in BABE with NTP.

Next, determine the synch-epoch length and set $s_{cd}$ according to Theorem 2.

The parameters below are computed using the script available at https://github.com/w3f/research/blob/master/experiments/parameters/babe_median.py

-############## PARAMETERS OF BABE WITH THE MEDIAN ALGORITHM ##############

c = 0.38, slot time T = 6 seconds 

Security over 3 years with probability 0.99656794973

Resistant to network delay of 2.79659722222 seconds and clock drift of 0.198402777778 seconds per sync-epoch

-~~~~~~~~~~~~~~ Common Prefix Property ~~~~~~~~~~~~~~

k = 140 –> Prune the last 140 blocks of the best chain. All remaining blocks are probabilistically finalized

-~~~~~~~~~~~~~~ Epoch Length ~~~~~~~~~~~~~~

Sync-Epoch length: at least 2857 slots (~4.7617 hours)

Epoch length: at least 2000 slots (~3.3333 hours)

-~~~~~~~~~~~~~~ Offline validators' parameters for clock adjustment ~~~~~~~~~~~~~~

$n = 200$ for temporary clock adjustment.

Offline validators should collect

**Some Notes on clock drifts:**

Computer clocks are inherently imprecise because the frequency that drives time progression is never exactly accurate. For instance, a frequency error of about 0.001% can cause a clock to drift by nearly one second per day.

Clock drift occurs because the oscillation frequency varies over time, primarily due to environmental factors such as temperature, air pressure, and magnetic fields. Experiments conducted on Linux systems in non-air conditioned environments show that a drift of 12 PPM (parts per million) corresponds to roughly one second per day. 

Observation suggets that over every 10000 second, the clock frequency changes are by 1 PPM, meaning the clock drifts approximately 0.08 seconds every three hours. Thus, a rough estimate of one second of drift per day is reasonable. If the sync-epoch spans 12 hours, this implies a drift of 0.5 second during that period. For more detailed information, refer to the [NTP Clock Quality FAQ](http://www.ntp.org/ntpfaq/NTP-s-sw-clocks-quality.htm#AEN1220)

[![](https://i.imgur.com/Slspcg6.png)](http://www.ntp.org/ntpfaq/NTP-s-sw-clocks-quality.htm#AEN1220)

**Figure. Frequency Correction within a Week**

**For inquieries or questions, please contact** [Bhargav Nagajara Bhatt](/team_members/JBhargav.md)

[1] Kiayias, Aggelos, et al. "Ouroboros: A provably secure proof-of-stake blockchain protocol." Annual International Cryptology Conference. Springer, Cham, 2017.

[2] David, Bernardo, et al. "Ouroboros praos: An adaptively-secure, semi-synchronous proof-of-stake blockchain." Annual International Conference on the Theory and Applications of Cryptographic Techniques. Springer, Cham, 2018.

[3] Badertscher, Christian, et al. "Ouroboros genesis: Composable proof-of-stake blockchains with dynamic availability." Proceedings of the 2018 ACM SIGSAC Conference on Computer and Communications Security. ACM, 2018.

[4] An epoch and a sync-epoch are distinct concepts

[5] Aggelos Kiayias and Giorgos Panagiotakos. Speed-security tradeoffs in blockchain protocols. Cryptology ePrint Archive, Report 2015/1019, 2015. http://eprint.iacr.org/2015/1019
