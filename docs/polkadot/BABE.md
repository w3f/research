*moved to http://research.web3.foundation/en/latest/polkadot/BABE/*

# BLOCK PRODUCTION (BABE)


## Overview of BABE

BABE stands for '**B**lind **A**ssignment for **B**lockchain **E**xtension'. 
In BABE, we deploy Ouroboros style block production with some changes in the slot-leader selection and best-chain selection. 

In Ouroboros Praos [2], each party is selected to produce a block in a slot with the probability proportional to the party's stake. In our block production, it is the same if parties are not offline in the slots that they supposed to produce a block. However, if they were offline, then they are punished by having less chance to be selected in the future slots.

In Ouroboros [1] and Ouroboros Praos [2], the best chain (valid chain) is the longest chain. In Ouroboros Genesis, the best chain can be the longest chain or the chain which is forked long enough and denser than the other chains in some interval. The details related to Ouroboros protocol are [here](https://hackmd.io/5N1sv7vtQLClvUh7B_75qQ?view). We have a different approach for the best chain selection based on GRANDPA and longest chain. 

We have two versions of BABE. The first version is almost the same as Ourobooros Praos [2]. We give it in this file. The second version is [here](https://hackmd.io/vL1Sji5BRd6QJOr3tHoqpg?view) which solves the problem related to offline parties as explained above.


## BABE 
In BABE, we have sequential non-overlaping epochs \((e_1, e_2,...)\), each of which contains a number of sequential slots (\(e_i = \{s^i_{1}, s^i_{2},...,s^i_{t}\}\)) up to some bound \(t\).  We randomly assign each slot to a party, more than one parties, or no party at the beginning of the epoch.  These parties are called a slot leader.  We note that these assignments are private.  It is public after the assigned party (slot leader) produces the block in his slot.

Each party \(P_j\) has at least two type of secret/public key pair:

*    Account keys \((sk^a_{j}, pk^a_{j})\) which are used to sign transactions.
*    Session keys consists of two keys: Verifiable random function (VRF) keys \((sk_{j}^{vrf}, pk^{vrf}_{j})\) and the signing keys for blocks \((sk^{sgn}_j,pk^{sgn}_j)\). 

We favor VRF keys being relatively long lived, but parties should update their associated signing keys from time to time for forward security against attackers causing slashing.  More details related to these key are [here](https://github.com/w3f/research/tree/master/docs/polkadot/keys).

Each party \(P_j\) keeps a local set of blockchains \(\mathbb{C}_j =\{C_1, C_2,..., C_l\}\). These chains have some common blocks (at least the genesis block) until some height.

We assume that each party has a local buffer that contains the transactions to be added to blocks. All transactions are signed with the account keys. 

The first version which is almost the same as Ouroboros Praos can be conveniently used with GRANDPA validators who are supposed to be online all the time. The second version is designed for more general users which can be offline time to time.

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

The genesis block contain a random number \(r_1\) for use during the first epoch for slot leader assignments, the initial stake's of the stake holders (\(st_1, st_2,..., st_n\)) and their corresponding session public keys \((pk_1^{vrf}, pk_2^{vrf},..., pk_{n}^{vrf})\), \((pk^{sgn}_{1}, pk^{sgn}_{2},..., pk_{n}^{sgn}\)) and account public keys (\(pk^a_{1}, pk^a_{2},..., pk^a_{n}\)).

We might reasonably set \(r_1 = 0\) for the initial chain randomness, by assuming honesty of all validators listed in the genesis block.  We could use public random number from the Tor network instead however.

TODO: In the delay variant, there is an implicit commit and reveal phase provided some suffix of our genesis epoch consists of *every* validator producing a block and *all* produced blocks being included on-chain, which one could achieve by adjusting paramaters.

2. #### Normal Phase

In normal operation, each slot leader should produce and publish a block.  All other nodes attempt to update their chain by extending with new valid blocks they observe.

We suppose each party \(P_j\) has a set of chains \(\mathbb{C}_j\) in the current slot \(sl_k\) in the epoch \(e_m\).  We have a best chain \(C\) selected in \(sl_{k-1}\) by our selection scheme, and the length of \(C\) is \(\ell\text{-}1\). 

Each party \(P_j\) produces a block if he is the slot leader of \(sl_k\).  If the first output (\(d\)) of the following VRF is less than the threshold \(\tau_j\) then he is the slot leader.

$$\mathsf{VRF}_{sk^{vrf}_{j}}(r_m||sl_{k}) \rightarrow (d, \pi)$$

Remark that the more \(P_j\) has stake, the more he has a chance to be selected as a slot leader. 

 
If \(P_j\) is the slot leader, \(P_j\) generates a block to be added on \(C\) in \(sk_k\). The block \(B_\ell\) should contain the slot number \(sl_{k}\), the hash of the previous block \(H_{\ell\text{-}1}\), the VRF output  \(d, \pi\), transactions \(tx\), and the signature \(\sigma = \mathsf{Sign}_{sk_j^{sgn}}(sl_{k}||H_{\ell\text{-}1}||d||pi||tx))\). \(P_i\) updates \(C\) with the new block and sends \(B_\ell\).


![ss](https://i.imgur.com/Yb0LTJN.png =250x )



In any case (being a slot leader or not being a slot leader), when \(P_j\) receives a block \(B = (sl, H, d', \pi', tx', \sigma')\) produced by a party \(P_t\), it validates the block  with \(\mathsf{Validate}(B)\). \(\mathsf{Validate}(B)\) should check the followings in order to validate the block:

* if \(\mathsf{Verify}_{pk^{sgn}_t}(\sigma')\rightarrow \mathsf{valid}\),
* if \(sl \leq sl_k\) (The future blocks are discarded)

* if the party is the slot leader: \(\mathsf{Verify}_{pk^{vrf}_t}(\pi', r_m||sl) \rightarrow \mathsf{valid}\) and \(d' < \tau_t\). 

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

Given a chain set \(\mathbb{C}_j\) an the parties current local chain \(C_{loc}\), the best chain algorithm eliminates all chains which do not include the finalized block \(B\) by GRANDPA. Let's denote the remaining chains by the set \(\mathbb{C}'_j\).
Then the algorithm outputs the longest chain which do not for from \(C_{loc}\)  more than \(k\) blocks. It discards the chains which forks from \(C_{loc}\) more than \(k\) slots.


We do not use the chain selection rule as in Ouroboros Genesis [3] because this rule is useful for parties who become online after a period of time and do not have any  information related to current valid chain (for parties always online the Genesis rule and Praos is indistinguishable with a negligible probability). Thanks to Grandpa finality, the new comers have a reference point to build their chain so we do not need the Genesis rule.


## Relative Time

It is important for parties to know the current slot  for the security and completeness of BABE. Therefore, we show how a party realizes the notion of slots. We assume that slot time \(T\) is greater than the network propogation time.


Each party has a local clock and this clock does not have to be synchronized with the network. When a party receives the genesis block, it stores the arrival time as \(t_0\) as a reference point of the beginning of the first slot. We are aware of the beginning of the first slot is not same for everyone. We assume that this difference is negligible comparing to \(T\).

Now, we consider parties who join BABE after genesis block released because these parties do not know the current slot when they join. 
These parties have to wait for at least number of \(\delta\) valid blocks in order to determine approximately beginning and end of the slot. Assume that a party \(P_j\) joins the network and then decides the best chain \(C\) whose header generated in slot \(sl_u\). \(P_j\) stores the arrival time of blocks  after \(sl_u\). Let us denote the stored arrival times by \(t_1,t_2,...,t_\delta\) corresponds to blocks including slot numbers \(sl'_1,sl'_2,...,sl'_\delta\). Remark that these slot numbers do not have to be consecutive since some slots may be empty or the slot leader is offline. \(P_j\) deduces that the current slot \(sl = sl'_\delta + 1\) given that \(T_i = T(sl-sl'_i)\) is in a time interval which includes \(\{t'_1+T_1, t'_2+T_2,..., t'_\delta+T_\delta\}\).


![](https://i.imgur.com/evb6i6p.png)




Another critical timing issue is 'when to release the block'. In order to find a good block release time so that it arrives everyone before end of the slot, each party follow the same strategy as newly joining party. Assume that the party \(P_j\) is a slot leader in \(sl\) and the computes \(\mathcal{T}_{sl} =\{t'_1+T_1, t'_2+T_2,..., t'_\delta+T_\delta\}\) as above. Then the function \(f_{time}:R^\delta \rightarrow R\) gives the release time given \(\mathcal{T}_{sl}\) as an input.

Possible candidates for \(f_{time}\) are average, maximum...

Then the party releases the block at time \(f_{time} - L_{avg}\) where \(L_{avg}\) is the estimaged network latency.

## Informal Security Analysis

BABE with Grandpa validators is the same as Ouroboros Praos except the chain selection rule and relative time based slot-time extraction. 

Since we do not use the longest chain rule only, the security bounds shown in Ouroboros Praos is not be the same. However, it seems that we have better selection rule comparing to longest chain rule. So, we have probably have better security bounds than Ouroboros Praos. Hence, if we show that we achieve their assumption related to timing with our relative time algorithm, it seems it is not harmful to use their security bounds in order to find good parameters for security.

Informally, the following important results are shown in Ouroboros Praos [2] with dynamic stakes for security:

* They show that the common prefix with parameter \(k\), chain growth, and chain quality properties are satisfied by Ouroboros Praos.
* Related to new randomness selection, they show that there will be at least one honest block in the first 2R/3 blocks of an epoch.
* They show that the honest block chains grows at least \(k\) blocks in \(2R/3\) slots. It means that the stake distribution for the next epoch has been determined before the new randomness generated.
* They show that any transaction given to honest parties is validated in \(2R/3\) slot (liveness property). This is proven based on the fact that in \(2R/3\) slot the chain grows at least \(k\) blocks.  


The formal statement that shows the above results is:  Ouroboros Praos satisfies persistence with parameter \(k\) and liveness with parameter \(u = \frac{8k}{(1+\epsilon)}\) in a period with \(L\) slots with the epoch size \(R = \frac{24k}{(1+\epsilon)}\) in the \(\Delta\)-semisynchronnous execution with probability 

$$p_{s}= 1- \mathsf{exp}(\mathsf{ln}L+\Delta-\Omega(k-\mathsf{log}tkq))$$

assuming that \(\alpha_H(1-f)^\Delta \geq \frac{1+\epsilon}{2}\) where \(\alpha_H\) is the relative stake of honest parties, fixed parameters are \(k, R, \Delta, L \in \mathbb{N}\), \(\epsilon, \sigma \in (0,1)\).

Here, \(k\) is the common prefix parameter, \(\Delta\) is maximum delay in the network in term of slot number, \(L\) is the life time of the protocol, \(\sigma\) is the maximum stake shift over \(R\) slots. \(t\) is the number of corrupted parties and \(q\) is the maximum number of random-oracle queries for a party. This can be considered as the hashing power (bruth forcing the hash).

If we use VDF in the randomness update for the next epoch, \(\mathsf{log}tkq\) disappers in \(p_{sec}\) because we have completely random value which do not depend on hashing power of the adversary.

$$p^{vdf}_{s}= 1- \mathsf{exp}(\mathsf{ln}L+\Delta-\Omega(k))$$

**These results are valid assuming that the signature scheme with account key is  EUF-CMA (Existentially Unforgible Chosen Message Attack) secure, the signature scheme with the session key is forward secure, and VDF realizing is realizing the functionality defined in [2].**

We want to have \(p_{s}\) and \(p^{vdf}_s\) close to 1 so (\(p_\mathcal{A} = \mathsf{exp}(\mathsf{ln}L+\Delta-\Omega(k-\mathsf{log}tkq)\) or \(\mathsf{exp}(\mathsf{ln}L+\Delta-\Omega(k)\) close to 0).

If lifetime increases the \(k\) value should increase too to have \(p_{s} \approx 1\). In addition, if \(\Delta\) increases the \(p_{s}\) decreases. \(k\) value is very critical because after \(k\) blocks later a block is added with very high probability to all honest parties' blockchain. We would like to have it as small as possible to have short time to finalize the blocks.


We fix the life time of the protocol as \(\mathcal{L}=5 \text{ years}  = 31536000\) seconds and maximum delay in the network \(\mathcal{D} = 60\) seconds. Then we find the life time of the protocol \(L = \frac{\mathcal{L}}{T}\) and maximum delay \(\Delta = \frac{\mathcal{D}}{T}\) in terms of slot. We consider the adversaries hashing power is \(q=2^{30}\) in each slot (which can also change depending on the slot time but for simplicity we use this parameter as an average power for all slot times). We note that changes on number of corruption (\(t\)) do not significantly affect \(p_{sec}\). (Of course dramatical changes affects).
Given \(L, \Delta, q, t\), we find the common prefix parameter \(k\) for some slot times \(T\).
As it can be seen in the graph we have smaller common prefix parameter if we use VDF in the randomness update. In addition, even if we increase the slot time, \(k\) does not change much. 

![](https://i.imgur.com/QX3pgjb.png)



The more generic version of BABE with any participants are [here](https://hackmd.io/vL1Sji5BRd6QJOr3tHoqpg?view).


## References

[1] Kiayias, Aggelos, et al. "Ouroboros: A provably secure proof-of-stake blockchain protocol." Annual International Cryptology Conference. Springer, Cham, 2017.

[2] David, Bernardo, et al. "Ouroboros praos: An adaptively-secure, semi-synchronous proof-of-stake blockchain." Annual International Conference on the Theory and Applications of Cryptographic Techniques. Springer, Cham, 2018.

[3] Badertscher, Christian, et al. "Ouroboros genesis: Composable proof-of-stake blockchains with dynamic availability." Proceedings of the 2018 ACM SIGSAC Conference on Computer and Communications Security. ACM, 2018.


