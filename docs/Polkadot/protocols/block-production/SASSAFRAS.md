---
title: SASSAFRAS
---

BADASS BABE is a constant-time block production protocol designed to ensure that exactly one block is produced at constant-time intervals, thereby avoiding multiple block production and empty slots. It builds upon BABE to address this limitation in the original protocol. While [Jeff's Write-up](https://github.com/w3f/research/tree/master/docs/papers/habe) explores the full design space of constant-time block production, the focus here is on a practical instantiation using zk-SNARKs to construct a ring-VRF.

## Layman overview
The objective is twofold: to run a lottery that distributes the block production slots in an epoch, and to fix the order in which validators produce blocks at the start of that epoch. Each validator signs the same on-chain randomness (VRF input) and publishes the resulting signature (VRF output=[value, proof]). This value serves as their lottery ticket, which can be validated against their public key. 

This approach reveals the lottery winners in advance, making them potential targets for attacks. The goal is then to keep the block production order anonymous. While the assignment of the validators to slots should remain fixed throughout the epoch, no one other than the assigned validator should know which slot belongs to whom. 

Validating tickets before the lottery using public keys can compromise anonymity. Instead, tickets can be validated after the lottery, when an honest validator claims their slot by producing a block.

The main issue with this approach is that anyone can submit fake tickets. Although these entities wouldn't be able to produce blocks, slots could still be preassigned to them, resulting in empty slots, which undermines the goal of the protocol. What's needed is a privacy-preserving method for validating a tickets. Relying on such a method, an honest validator could submit their ticket along with a SNARK, validated before the lottery, proving the statement: "This my VRF output, generated using the given VRF input and my secret key. I won't reveal my keys, but my public key is among those of the nominated validators." 


Once the ticket is made anonymous, the next step is to publish it to the chain without revealing its origin. While fully anonymous methods tend to be costly, a simple scheme suffices to achieve the core objectives: each validator can send their ticket to a randomly chosen peer, who then submits it on-chain as a transaction.

## Plan
In an epoch $e_m$ we use the BABE randomness $r_m$ as the ring VRF input to generate a set of outputs, which are then published on-chain. Once finalized, these outputs are sorted, and their order determines the block production sequence for epoch $e_{m+2}$.

## Parameters
* $V$: The set of nominated validators
* $s$: Number of slots per epoch. For an hour-long epoch with 6-second slots, $s=600$
* $x$: Redundancy factor. For an epoch with $s$ slots, we aim to have $xs$ tickets generated in expectation for block production. Here, we set $x=2$.
* $a$: Number of ticket-generation attempts per validator in an epoch
* $L$: A bound on the number of tickets that can be gossiped, used for DoS resistance

## Keys
In addition to their regular keys, each validator must posssess a keypair on a SNARK-friendly curve such as [Jubjub](https://z.cash/technology/jubjub/). It is essential that these keys are generated before the randomness used for the epoch is derived or finalized.

Given a security parameter $\lambda$ and randomness $r$, generate a key pair using the RVRF key generation function 
$$
\texttt{KeyGen}_{RVRF}:\lambda,r\mapsto sk, pk
$$

To optimize the process, an aggregate public key $apk$, referred to as a commitment in Jeff's writeup, is introduced for the full set of validators. This key is essentially a Merkle root derived from the list of individual public keys. 

$$
\texttt{Aggregate}_{RVRF}: v, \{pk_v\}_{v\in V}\mapsto apk, ask_v
$$

The copath $ask_v$ serves to identify a specific public key within the tree as a private input to a SNARK.

## Phases

Bootstrapping the protocol from genesis or through a soft fork of Kusama is beyond the scope of this description. The regular operation of the protocol thus begins with the nomination of a new set of validators.

### 1) Setup
As a new set of validators $V$ is nominated, or another protocol parameter changes, the protocol reinitializes once per era with updated values for the threshold $T$ and the aggregated public key $apk$.

Each validator $v \in V$
1. Calculates the threshold $T = \frac{xs}{a\mid V\mid}$. This value prevents adversaries to predicting how many additional blocks a block producer will generate.
2. Computes the aggregated public key and copath of $v$s public key
$$
apk, spk_v = \texttt{Aggregate}_{RVRF}(v, \{pk_v\}_{v\in V})
$$
3. Obtains the SNARK CRS and verifies whether the subversion status has changed or if $v$ has not previously performed this step.

### 2) VRF generation Phase

The objective is to have at least $s$ VRF outputs (tickets) published on-chain. Although this cannot be strictly guaranteed, the expected value is $xS$.

#### Randomness
At the epoch $e_m$, we use the randomness $r_m$ as provided by [BABE](polkadot/protocols/block-production/Babe), defined as

$$
r_m=H(r_{m-1}, m, \rho)
$$

Here, $r_m$ creates inputs to the ring-VRF, with resulting tickets consumed in epoch $e_{m+2}$.

It's critical that $\rho$ remains the concatenation of regular BABE VRF outputs. Standard VRFs and ring VRFs are then excecuted regularly and concurrently, with ring-VRF outputs revealed in epoch $e_m$. If VRF outputs are used prematurely for randomness, $r_{m+1}$ would be exposed too early. Thus, only unrevealed VRFs are used until their corresponding blocks have been produced.

In the case of a VDF, randomness would need to be determined one epoch earlier, i.e.,

$$
r_m=VDF(H(r_{m-2}, m, \rho))
$$

where $\rho$ is the concatenation of BABE VRFs from epoch $e_{m-2}$. The VDF would be excecuted at the start of $e_{m-1}$, ensuring that its output is available on-chain before $e_{m}$ begins.

#### VRF production
Each validator $v \in V$ performs the following steps:

1. Computes $a$ VRF outputs using the randomness $r_{m}$, for inputs $in_{m,i}=(r_m, i)$, where $i = 1,\ldots,a$:

$$
out_{m,v,i}=\texttt{Compute}_{RVRF}(sk_v, in_{m, i})
$$

2. Selects "winning" outputs below the threshold $T$: $\texttt{bake}(out_{m,v,i}) < T$
where $\texttt{bake()}$ maps VRF outputs to the interval $[0,1]$. The indices correponding to winning outputs form the set $I_{win}$.

3. Generates proofs using its copath $ask_v$ for each winning output $i \in I_{win}$,
$$
\pi_{m,v,i} = \texttt{Prove}_{RVRF}(sk_v, spk_v, in_{m,i} )
$$
where $\texttt{Prove}_{RVRF}(sk_v, spk_v, in_{m,j} )$ includes the SNARK and associated public inputs $cpk,i$.

Once this phase concludes, each validator holds zero or more winning tickets and corresponding validity proofs $(j, out_{m, v,j}, \pi_{m,v,j})$. These must later be published on-chain.

### 3) Publishing Phase
The goal is to identify block producers for a large portion of slots unknown in advance. Well-behaved validators should keep their tickets private. To achieve this, validators do not publish their winning VRF outputs immediately; instead, they relay them to another randomly selected validator (a proxy), who is responsible for publishing them on-chain.

Concretely, validator $v$ selects another validator $v'$ based on the output $out_{m,v,i}$ for $i \in I_{win}$. The validator computes $k=out_{m,v,i} \textrm{mod} |V|$ and sends its winning ticket to the $k$th validator according to a fixed ordering. Then, validator $v$ signs the message: $(v, l, enc_v'(out_{m,v,i}, \pi_{m,v,i}))$ where $end_{v'}$ denotes encryption using the public key of $v'$. Winning outputs are indexed using $l$ ranging from $0$ to $L-1$, and are gossiped through the network. If there are more than $L$ outputs below the threshold $T$, only the lowest $L$ are disseminated. This limitation helps prevent validator from spamming the network.

Once a validator receives a messages, it checks whether it has already received a message with the same $v$ and $l$; if so, it discards the new message. Otherwise, it decrypts the message to determine whether it is the intended proxy and forwards (gossips) the message. Validators further gossip messages addressed to themselves to mitigate traffic correlation risks.

When a validator decrypts a message using its private key, it verifies whether it was the correct proxy by checking out that $out_{m,v,i} \textrm{mod} |V|$ corresponds to its index. If confirmed, then at a designated block number, it broadcasts a transaction containing $(out_{m,v,i}, \pi_{m,v,i}))$ for inclusion on-chain. If the validator serves as a proxy for multiple tickets, it submits multiple transactions at the appointed block.

If validator $v$'s ticket is not included on-chain before a certain block number, either due to proxy misbehavior or because it did not forward the ticket to any proxy, then $v$ submits the transaction $(out_{m,v,i}, \pi_{m,v,i})$ independently. A validator might refrain from selecting a proxy when it holds more than $L$ winning tickets.

### 4) Verification

A transaction of this type is valid for block inlcusion if it can be verified as follows.

To verify the published transactions $(out_{m, v,i}, \pi_{m,v,i})$, the corresponding SNARK proof must be checked. This verification requires:
- the input $in_{m,i}$, which can be computed from $i$ and $r_m$,
- the published output $out_{m,v,i}$
- the aggregate public key $apk$.

These values constitute the public inputs to the SNARK verifier:
$$
Verify(\pi_{m,v,i}, apk, out_{m,v,i}, in_{m,i})
$$

### 5) Sorting
Epoch $e_{m+2}$ contains the list $\{out_{m,k}\}_{k=1}^{K}$ of $K$ verified VRF outputs generated during the epoch $e_m$, which are finalized on-chain. Each output is combined with a source of randomness $r'$, where:
- $r'=r_{m+1}$ if no VDF is use, or 
- $r'=r_{m+2}$ if a VDF is used. 

The resulting hash is computed as: $out'_{m,k}=H(out_{m,k} || r')$

**Block production order determination** Each validator sorts the list of $out'_{m,k}$ values in ascending order and removes the largest $s-K$ values (if any). This results in the filtered subset

$out'_{m,1},\ldots, out'_{m,l}$, where $l\leq s$ and $out'_{m,p}\leq out'_{m,q}$ for $1\leq p<q\leq l$.

**Slot assignment via "Outside-in" sorting** Ticket values $out'_{m,k}$ are assigned to slots using an outside-in ordering: 

- The lowest value $out'_{m,1}$ maps the last slot
- The second lowest $out'_{m,2}$ maps the first slot
- The third $out'_{m,3}$ maps the penultimate slot
- The fourth $out'_{m,4}$ maps to the second slot, and so on. 

Example of outside-in ordering: Input: (1,2,3,4,5) Result: (2,4,5,3,1)

In the unlikely event that $K < s$, some slots will remain unassigned in the middle of the epoch. These gaps are filled using the AuRa protocol.

To assign slots using outside-in sorting, split the list of outputs into even- and odd-numbered elements, reverse the list of odd elements, then concatenate the even elements, followed by the Aura-assigned slots, and finally the reversed odd elements.

### 6) Claiming the slots

To produce a block in the assigned slot, a validator needs to include a ticket, specifically a VRF output $out_{m,v,i}$, corresponding to the slot, along with a non-anonymous proof that this output is the result of their VRF.

Introducing the following functions facilitates this: 

$\texttt{Reveal}_{RVRF}: sk_v, out\mapsto \tau$

$\texttt{Check}_{RVRF}: \tau, out\mapsto true/false$

These are esssentially Schnorr-style proofs of knowledge of exponent (PoKE).
When validating a block, nodes must verify these proofs. Additionally, the validator must include a previously unseen VRF output-referred to as the BABE VRF above. This can be generated using the existing (non-jubjub) key on the same input (r_m || i).

## Probabilities and parameters.

The first parameter under consideration is $x$. The goal is to ensure a very low probability of having fewer than $s$ winning tickets, even if up to $1/3$ of validators are offline. The probability that any given attempt yields a winning ticket is $T=xs/a|V|$.
Let $n$ be the number of validators who actually participate such that $2|V|/3 \leq n \leq |V|$. These $n$ validators each make $a$ attempts; resulting in a total of $an$ attempts.
Let $X$ be the number of winning tickets. Its expected value is

$$
E[X] = Tan = xsn/|V|
$$

Setting $x=2$ yields $\geq 4s/3$. In this case, the variance is 

$$
Var[X] = anT(1-T) \leq anT = xsn/|V| = 2sn/|V| \leq 2s
$$

Using Bernstein's inequality:
$$
\begin{align*}
\Pr[X < s] & \leq \Pr[X < E[X]-s/3] \\
& \leq exp(-\frac{(s/3)^2}{(Var[X]+s/3)}) \\
& \leq exp(-s/(9(2+1/3))) \\
& \leq exp(-s/21)
\end{align*}
$$

For $s=600$, this yields a probability below $4 * 10^{-13}$, which is sufficiently small. The Aura fallback mechanism is needed only as a safeguard against censorship. It is not feasible to reduce $x$ below $3/2$ while retaining tolerance for offline validators, making $x=2$ a prudent choice. Under this configuration, the Aura fallback should remain unused.

The next parameter to configure is $a$. A challenge arises in that if a validator $v$ receives $a$ winning tickets during an epoch, an adversary observing this will deduce that no additional blocks will be produced by $v$.

**For inquieries or questions, please contact** [Jeff Burdges](/team_members/JBurdges.md)




