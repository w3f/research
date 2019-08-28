
# Cryptographic sortition for constant-time block production 

We believe the numerous empty block production slots and erratic block times produced by Ouroboros Praos constrain the security analysis and create problems whenever block production requires extensive computational work.  We therefore seek a constant-time block production algorithm that assigns all block production slots.  We shall outline roughly the solution categories here.

In all designs, we need some ...

We first divide sortition schemes into those with a bespoke, but often near perfect, anonymity layer and those that require pre-announces that reveal each block slot's owner to one random other block producer.


# Bespoke anonymity

...


## Accountable shuffles

Among all schemes listed here, shuffles are unique in that they operate an on-chain anonymity network, which naturally avoids pre-announces, and initially provides strong anonymity for block producers. 

A priori, accountable shuffles require on-chain bandwidth of order hops count times list size.  We achieve the strongest anonymity being when both the list is the full block producer list and the every block producer applies a hop, so the hops count is also the block producer set size, but this sounds excessive.

In principle, anonymity degrades throughout the epoch as the accountable shuffles exhaust their candidates.  We'd therefore run several shuffles simultaneously but consume them only partially.  We should further mix between these shuffles with additional shuffles, at the cost of the "guide points" multiplying.


There are cryptographically verifiable shuffles but afaik only with considerable overhead, although maybe simpler ones exist for shuffling public keys.  We can however make an extremely simple non-verifiable shuffle for node public keys that becomes accountable thanks to slashing:

We ask that initially all nodes have their public keys $V_i = v_i G$ registered on-chain.  We also ask that nodes register some keys to be shuffled $S_j = s_j G$ on-chain.  We shuffle lists of points $L$, which initially consists of some $S_j$ not appearing in other lists, along with one distinguished guide point $P$, which we initially take to be $G$.  Importantly, we avoid needing a [VRF that outputs a public private key pair](https://forum.web3.foundation/t/verifiable-random-commitments-or-public-keys/39) by shuffle these points instead of $V_i$.

In each shuffle step, our $i$th node multiplies this shuffle key $s_i$ by all points in the list $L$ and by its associated guide point $P$ and produce a DLEQ proof that $\sum L'$ and $P'$ were correctly multiplied by $v_i$ from the input $\sum L$ and $P$.  Any node can find itself in $L'$ by computing $s_j P'$, which ultimately tells it when to produce the block.  

At this point, if $i$ has not performed the shuffle correctly then an omitted node can prove this by producing a DLEQ proof of the $s_j P'$ that does not exist in the list $L'$, resulting in $i$ being slashed.  There is significant on-chain logic involved in orchestrating these shuffles, but at least the slashing logic appears simple because all behavior is deterministic, after declaring the $S_i$.


We give a rough cost estimate:

Initially the first $k$ block producers permute a batch of 128 $S_i$ selected randomly by VRF, so that 128 k provides enough candidate block producers.  Second, we have 7ish additional block producers further permute each of these lists.  At this point, each batch of 128 block producers has cost us slightly more than 64kb on-chain, so $k/8$ mb in total, but only 4kb per block.

We next create new batches of 128 points pulled randomly from all $k$ output lists and rerun the shuffle algorithm, but now all $k$ guide points must appear with each shuffle.  If we repeat this $l$ times then we have $k^l$ guide points on-chain.  We could reduce this to $2^l$ with more staggered mixing.  

We could reduce the amount on-chain by sending the intermediate lists directly between block producers, and our challenge protocol could unwind through several levels, but actually doing this invites its own censorship issues.  


## Aggregate blind pre-announces

...

In epoch $e$, all block producers $V = v G$ create a limit number of VRF outputs 
$$ (\omega_{V,e,i},\pi_{V,e,i}) := VRF_v(r_e || i) \quad \textrm{for $i < N$.} $$
Next they derive blinding factors $b_i := H(\omega_{V,e,j} || "blind")$, so
$$ \omega' := b_i \omega_{V,e,i} = b_i v H_1(r_e || i) = VRF_{b_i v}(r_e || i) $$

TODO: Last line in unnecessarily complex, but maybe helps with DLOG blind signature crap.  Blind ECQV?

We now determine some block producer $V'= v' G$ by $\tau := VRF_v(r_e || i || "signer")$ and send to them $\tau$, $\omega'$, and maybe a DLEQ proof that $b_i V$ is product of $b_i G$ and $V$.  Now $V'$ blind signs $\omega_{V,e,i}$ with an aggregatable signature scheme like BLS.  At this point, $V$ unblinds the signature on $\omega_{V,e,i}$, aggregates these from several signers, and places the resulting aggregates signature onto the chain somehow.  

We sadly deanonymise ourselves with the aggregation, but now the pre-announce has multiple signers who never saw the output.

meh

...


# Pre-announced

...


## Ring VRFs

A ring VRF operates like a VRF but only proves its key comes from a specific list without giving any information about which specific key.  Any ring VRF yields sortition:

In a pre-announce phase, all block producers anonymously publish ring VRF outputs, which either requires revealing their identity to another block producer, or else requires a multi-hop anonymity network.  We then sort these ring VRF outputs and block producers claim them when making blocks.

There is no slashing when using ring VRFs because we check all ring VRF proofs correctness when placing them on-chain.  We expect this pure ring VRF solution to provide the most orthogonality with the most reusable components, due to the on-chain logic being quite simple, and the cryptography sounding useful elsewhere.

Any naive ring VRF construction has a signature size linear in the number of block producers, meaning they scale worse than well optimised accountable shuffles.  There are constant-size ring VRFs built using zkSNARKs however ala https://ethresear.ch/t/cryptographic-sortition-possible-solution-with-zk-snark/5102

TODO: Evaluate zkSNARK circuit complexity

In between, there are an array of linkable ring signature constructions, many of which yield ring VRFs, so we might discover something quite efficient without pairings.  We think techniques from bulletproofs sounds promising here.

TODO: Evaluate ring VRF constructions


## Insecure pre-announces

We could pre-announce VRF outputs without employing a ring VRF construction, provided we can tolerate false VRF outputs being spammed on-chain.  We discuss strategies to limit this spam below.


### Secondary randomness

We could limit the damage caused by spamming pre-announces by resorting the pre-announces using randomness created after their publication.

In epoch $e$, any block producer $V = v G$ creates a limit number of VRF outputs 
$$ (\omega_{V,e,i},\pi_{V,e,i}) := VRF_v(r_e || i) \quad \textrm{for $i < N$,} $$
which they send to another block producer $V'$ identified by $H(\omega_{V,e,i} || "WHO")$.

In epoch $e+1$, $V'$ publishes at most $N'$ such values $H(\omega_{V,e,i})$ along with another VRF output
$$ (\omega'_{V',e},\pi'_{V',e}) := VRF_v(r_e || "SORT") $$
If $V'$ does not do so, then $V$ may publish $H(\omega_{V,e,i})$ itself.

In epoch $e+2$, we compute $r'_e$ by hashing together all $\omega'_{V',e}$ and sort $H(r'_e || H(\omega_{V,e,i}))$.  The first $N''$ of these are the blocks of epoch $e+3$, which block producers claim by revealing $(\omega_{V,e,i},\pi_{V,e,i})$.  

If $V$ does not make the block for $\omega_{V,e,i}$ then $V'$ reveals $(\omega'_{V',e},\pi'_{V',e})$ in epoch $e+4$.  We might slash $V'$ for not doing this, but doing this does not appear essential. 

In epoch $e+5$, we define $r_{e+5}$ by hashing $r'_e$ together with all revealed $\omega_{V,e,i}$ in their block production order, irregardless of whether the block got produced or not.

### 


