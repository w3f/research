
# Cryptographic sortition for constant-time block production 

We think anonymous block production helps prevent censorship however, which weighs in favor of Ouroboros Praos style block production algorithms.  We dislike that numerous empty block production slots and erratic block times intrinsic to Ouroboros Praos though, because these effects. constrains our security analysis and create problems whenever block production requires extensive computational work.  

We thus want block production algorithm that is constant-time in the sense that it assigns all block production slots before an epoch starts, but that also keeps block production slots anonymous.  We shall outline roughly the solution categories below.

We first quickly address sortition schemes with a bespoke, but often near perfect, anonymity layer built using cryptographic shuffles.  Almost all other schemes require pre-announces that reveal each block slot's owner to one random other block producer.

There are important advantages to schemes in which each slot has an associated public key to which users can encrypt their transactions, because this strengthens privacy schemes like QuisQuis and Grin aka MimbleWimble.


## Shuffles

A cryptographic shuffle has one node reorder and mutate entries, normally ciphertexts or public keys, so that only the node knows the resulting ordering.  Among all schemes listed here, shuffles are unique in that they operate an on-chain anonymity network, which naturally avoids pre-announces, and initially provides strong anonymity for block producers.  

A priori, shuffles require on-chain bandwidth of order hops count times list size.  We achieve the strongest anonymity when both the list is several repetitions of the full block producer list and then every block producer applies a hop, making the hops count is also the block producer set size, but this sounds excessive.

We should shuffle more slots than required, but consume them only partially because otherwise anonymity would degrade throughout an epoch as exhaust our candidates.  Any shuffle invokes storage operations linear in the shuffled set size, so we improve performance if validators shuffle less than our full list, and this costs us less confidence if all validators do some such partial shuffle.  

We expect this last requirement for repeated partial shuffles favours ElGammal ciphertexts, although nice shuffles for curve points exists too.  In essence, any shuffle needs "guide points" that pass through the same cryptographic operations as the shuffled public keys, but if lists do not change then only one guide point is required, while ElGammal-like scheme attaches a guide point to every public key, which works well if combining many partial shuffles (see universal re-encryption).


### Verifiable shuffles

A verifiable shuffle produces a cryptographic proof that the shuffle happened correctly.  Andrew Neff's verifiable shuffle from [_A Verifiable Secret Shuffle and its Application to E-Voting_](http://web.cs.elte.hu/~rfid/p116-neff.pdf) costs $8 k + 5$ scalar multiplications where $k$ denotes the number of validators shuffled (see also [implementations](https://crypto.stackexchange.com/a/41674)).  

TODO: Review more recent modern verifiable shuffle literature


### Accountable shuffles

We might reduce costs with a simple non-verifiable shuffle for validator public keys that becomes accountable thanks to slashing:

We ask that initially all $k$ validators have their public keys $V_i = v_i G$ registered on-chain.  We also ask that validators register some keys to be shuffled $S_j = s_j G$ on-chain.  We shuffle lists of points $L$, which initially consists of some $S_j$ not appearing in other lists, along with guide point(s), whether one $P_j$ per $S_j$, or one distinguished guide point $P$ overall, which we initially take to be $G$.  Importantly, we avoid needing a [VRF that outputs a public private key pair](https://forum.web3.foundation/t/verifiable-random-commitments-or-public-keys/39) by shuffle these points instead of $V_i$.

In each shuffle step, our $i$th validator multiplies this shuffle key $s_i$ by all points in the list $L$ and by its associated guide point $P$ and produce a DLEQ proof that $\sum L'$ and $P'$ were correctly multiplied by $v_i$ from the input $\sum L$ and $P$.  Any validator can find itself in $L'$ by computing $s_j P'$, which ultimately tells it when to produce the block.  

At this point, if $i$ has not performed the shuffle correctly then an omitted validator can prove this by producing a DLEQ proof of the $s_j P'$ that does not exist in the list $L'$, resulting in $i$ being slashed.  There is significant on-chain logic involved in orchestrating these shuffles, but at least the slashing logic appears simple because all behavior is deterministic, after declaring the $S_i$.


We give a rough cost estimate:

Initially the first $k$ block producers permute a batch of 128 $S_i$ selected randomly by VRF, so that 128 k provides enough candidate block producers.  Second, we have 7ish additional block producers further permute each of these lists.  At this point, each batch of 128 block producers has cost us slightly more than 64kb on-chain, so $k/8$ mb in total, but only 4kb per block.

We next create new batches of 128 points pulled randomly from all $k$ output lists and rerun the shuffle algorithm, but now all $k$ guide points must appear with each shuffle.  If we repeat this $l$ times then we have $k^l$ guide points on-chain.  We could reduce this to $2^l$ with more staggered mixing.  

We could reduce the amount on-chain by sending the intermediate lists directly between block producers, and our challenge protocol could unwind through several levels, but actually doing this invites its own censorship issues.  

TODO: Replace with ElGammal version.


## Cryptographic pre-announcements

All remaining schemes operate via some anonymous pre-announcement phase after which we determine the block production slot assignment by sorting the pre-announcements.  

We must constrain valid pre-announcements so that malicious validators cannot create almost empty epochs by spamming fake pre-announcements, while preserving anonymity for block producers.  We outline several fixes below, both cryptographic and softer economic ones. 

As a rule, we accept the anonymity lost by revealing our block production slot to one other validator.  Yet, almost all these schemes could achieve stronger anonymity by forwarding messages an extra hop, or perhaps coupling with shuffles.


### Ring VRFs

A ring VRF operates like a VRF but only proves its key comes from a specific list without giving any information about which specific key.  Any ring VRF yields sortition:

In a pre-announce phase, all block producers anonymously publish ring VRF outputs, which either requires revealing their identity to another block producer, or else requires a multi-hop anonymity network.  We then sort these ring VRF outputs and block producers claim them when making blocks.

There is no slashing when using ring VRFs because we check all ring VRF proofs' correctness when placing them on-chain.  We expect this pure ring VRF solution to provide the most orthogonality with the most reusable components, due to the on-chain logic being quite simple, and the cryptography sounding useful elsewhere.

Any naive ring VRF construction has a signature size linear in the number of block producers, meaning they scale worse than well optimised accountable shuffles.  

There are also constant-size ring VRFs built using zkSNARKs however ala https://ethresear.ch/t/cryptographic-sortition-possible-solution-with-zk-snark/5102  In principle, these constructions should work with 10k to 20k constraints for 10,000 validators.  (Do you agree Sergey?)

There are also ring signature constructions that do not require pairings and require only logarithmic size, like (_One-out-of-Many Proofs: Or How to Leak a Secret and Spend a Coin_)[https://eprint.iacr.org/2014/764] by Jens Groth and Markulf Kohlweiss.  In that scheme, ring signatures need about 32*7 bytes times the logarithm of the number of validators, so under 3kb for 10,000 validators.  

We expect a ring VRF could be defined using these techniques, likely leveraging proof circuits implemented in the [dalek bulletproofs crate](https://doc-internal.dalek.rs/bulletproofs/notes/index.html), which might prove more efficient by some constant factor.  We also note that ring VRFs are linkable ring signatures, so some existing linkable ring signatures implementations may already provide ring VRFs.

At these sizes, we expect the non-pairing based technique prove fairly competitive with zkSNARKs, but verification still requires all the public keys being multiplied.  At 10k validators, zkSNARK would costs the prover like 10k-20k scalar multiplications, but provide faster verification, while the non-pairing based scheme might cost verifiers 10k scalar multiplications per slot.  We thus judge zkSNARK scheme more efficient, especially since weak hash functions like MIMC or ??? suffice for the Merkle tree.  


### Group VRFs

A group signature also hides the specific signer, like a ring signature, but group signatures require initial setup via some issuer or MPC. 

We build a group VRF similarly to a group signature by using the rerandomizable signature scheme from [_Short Randomizable Signatures_](https://eprint.iacr.org/2015/525) by David Pointcheval and Olivier Sanders as a blind rerandomizable certificate.  Our issuer would first blind sign each validator's private key, like in section 6.1, so that later each validator can prove correctness their VRF output, replacing the proof of knowledge from section 6.2 there.  We believe this final step resembles the schnorrkel VRF except with the public key replaced by the signature inputs, but run on the pairing based curve.

In this, we must take care with our pairing assumptions because we loose anonymity if $x H$ with $H$ known ever appears on the curve not used for the VRF output.  

We expect group VRFs only require a few curve points, and verification only requires two pairings and a few scalar multiplications, making them far smaller and faster than ring VRFs.  We require an issuer however, which dramatically complicates the protocol:

We'd want at least two thirds, but preferable all, of validators to be aggregate certificate issuers, meaning they have certified the blinded public keys of all validators and we aggregate all certificates and public keys.  We might achieve this with an MPC but doing so requires choosing when we issuers issue certificates.  

In other words, all new prospective validators certify all previously added prospective validators, and all previously added prospective validators must eventually recertify all more recently added prospective validators.  In this way, any spammed slots originate from prospective but not actual validators, probably along with an actual validator who posts them.  

We become therefore tempted to run this MPC after election but before establishing final validator list, but this complicates protocol layering unacceptably.  We could look into group signatures with "verifier local revocation" but these get much more complicated if I remember.


## Non-cryptographic pre-announces

We could pre-announce VRF outputs without employing any ring or group VRF construction, provided we can tolerate some false VRF outputs being spammed on-chain.  We discuss strategies to limit this spam below.

In general, there are several approaches that work with smaller numbers of slots and validators, but we shall discuss only schemes tweaked for numerous validators.

### Secondary randomness

We limit the damage caused by spamming pre-announces by resorting the pre-announces using randomness created only after their publication.

In epoch $e$, any block producer $V = v G$ creates a limited number of VRF outputs 
$$ (\omega_{V,e,i},\pi_{V,e,i}) := VRF_v(r_e || i) \quad \textrm{for $i < N$,} $$
each of which they send to another block producer $V'$ identified by $H(\omega_{V,e,i} || "WHO")$.

We divide epoch $e+1$ into three steps:  In the first half, $V'$ publishes at most $N'$ such values $H(\omega_{V,e,i})$.  In the second half, if $V'$ did not publish $H(\omega_{V,e,i})$, then $V$ may publish $H(\omega_{V,e,i})$ itself.  At the end of epoch $e+1$, we sort the $H(r_{e+1} || H(\omega_{V,e,i}))$.  The first $N''$ of these are the blocks of epoch $e+2$, which block producers claim by revealing $(\omega_{V,e,i},\pi_{V,e,i})$.  

If $V$ does not make the block for $\omega_{V,e,i}$ then $V'$ reveals $(\omega'_{V',e},\pi'_{V',e})$ in epoch $e+3$.  We might slash $V'$ for not doing this, but doing this does not appear essential. 

In epoch $e+4$, we define $r_{e+4}$ by hashing $r_{e+3}$ together with all revealed $\omega_{V,e,i}$ in their block production order, irregardless of whether the block got produced or not.



