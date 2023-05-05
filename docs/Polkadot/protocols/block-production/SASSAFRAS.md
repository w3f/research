---
title: SASSAFRAS
---

**Authors**: [Jeff Burdges](/team_members/jeff.md), Fatemeh Shirazi, [Alistair Stewart](/team_members/alistair.md), [Sergey Vasilyev](/team_members/Sergey.md)

BADASS BABE is a constant-time block production protocol. It intends to ensure that there is exactly one block produced with constant-time intervals rather than multiple or none. It extends on BABE to address this shortcoming of BABE. While [Jeff's Write-up](https://github.com/w3f/research/tree/master/docs/papers/habe) describes the whole design space of constant-time block production, here we describe a practical instantiation of the protocol using zk-SNARKs to construct a ring-VRF.

## Layman overview
We want to run a lottery to distribute the block production slots in an epoch, to fix the order validators produce blocks  by the beginning of an epoch. Each validator signs the same on-chain randomness (VRF input) and publishes this signature (VRF output=[value, proof]). This value is their lottery ticket, that can be validated against their public key. The problem with this approach is that the lottery-winners are publicly known in advance and risk becoming targets of attacks. We aim to keep the block production order anonymous. The assignment of the validators to the slots should be fixed for the whole epoch, but noone besides the assigned validator should know whose a slot is. However, we can't validate the tickets prior the lottery  using their public keys  as it would deanonymize the validators. If tickets were not validated prior to the lottery then instead we can validate them after the lottery by an honest validator claiming their slots when producing blocks.

However, the problem is that anyone can submit fake tickets, and though they won't be able to produce a block, slots would be preassigned to them. Effectively, it results in empty slots, which defeats the goal of the protocol. To address this problem, we need a privacy-preserving way of validating a ticket. So an honest validator when submitting their ticket accompanies it with a SNARK of the statement: "Here's my VRF output that has been generated using the given VRF input and my secret key. I'm not telling you my keys, but my public key is among those of the nominated validators", that is validated before the lottery.

Now we have a way of making the ticket itself anonymous, we need a way to anonymously publish it to the chain. All ways of doing this with full anonymity are expensive. Fortunately, one of the simplest schemes is good enough for our purposes: a validator just sends each of their tickets to a random validator who later puts it on-chain as a transaction.

## Plan
In an epoch $e_m$ we use BABE randomness $r_m$ for the epoch as ring VRF inputs to produce a number of outputs and publish them on-chain. After they get finalized we sort them and their order defines the order of block production for the epoch $e_{m+2}$.

## Parameters
$V$ - the set of nominated validators
$s$ - number of slots per epoch, for an hour-long epoch with 6 second slots $s=600$
$x$ - redundancy factor, for an epoch of $s$ slots we want to have $xs$ tickets in expectation for block production. We set $x=2$.
$a$ - attempts number of tickets generated per validator in epoch
$L$ - a bound on a number of tickets that can be gossiped, used for DoS resistance

## Keys
In addition to their regular keys, we introduce for each validator a keypair on a SNARK-friendly curve [Jubjub](https://z.cash/technology/jubjub/). We must ensure that the keys are generated before the randomness for an epoch they are used in is determined.

Given the security parameter $\lambda$ and some randomness $r$ generate a key pair $\texttt{KeyGen}_{RVRF}:\lambda,r\mapsto sk, pk$

As an optimization we introduce an aggregate public key $apk$ (called a commitment in Jeff's writeup) for the whole set of validators, that is basically a Merkle root built upon the list of individual public keys. In conjuction to that we use the copath $ask_v$ to identify a public key in the tree as a private input to a SNARK.
$\texttt{Aggregate}_{RVRF}: v, \{pk_v\}_{v\in V}\mapsto apk, ask_v$


## Phases

Here we describe the regular operation of the protocol starting from a new set of validators being nominated. Bootstrapping the protocol from the genesis or soft-forking Kusama is not described here.

### 1) Setup
Once per era, as a new set of validators $V$ gets nominated or some other parameter changes, we reinitialize the protocol with new values for the threshold $T$ and the aggregated public key $apk$.

Each validator $v \in V$
1. Calculates the threshold $T = \frac{xs}{a\mid V\mid}$ that prevents the adversary to predict how many more blocks a block producer is going to produce.
2. Computes the aggregated public key and copath of $v$s public key $$apk, spk_v = \texttt{Aggregate}_{RVRF}(v, \{pk_v\}_{v\in V})$$
3. Obtains the SNARK CRS and checks for subversion if it has changed or $v$ hasn't done it earlier.

### 2) VRF generation Phase

We aim to have at least $s$ VRF outputs (tickets) published on-chain (we can't really guarantee that, but the expected value will be $xS$).

#### Randomness
At the epoch $e_m$ we use the randomness $r_m$ as provided by [BABE](polkadot/protocols/block-production/Babe), namely
$$r_m=H(r_{m-1}, m, \rho),$$.
We use $r_m$ to create inputs to the ring-VRF, and the corresponding tickets will be consumed in $e_{m+2}$.

It's critical that $\rho$ is still the concatenation of regular BABE VRF outputs. It follows that we run regular VRFs and ring VRFs in parallel. This is because ring VRF outputs will be revealed in epoch $e_m$ and hence if we use ring VRF outputs for randomness $r_{m+1}$ would be revealed too early. Thus we use VRFs that are unrevealed until the corresponding blocks are produced.

If we have a VDF, then all this would need to be determined an epoch prior i.e.
$$r_m=VDF(H(r_{m-2}, m, \rho)),$$.
with $\rho$ being the concatenation of BABE VRFs from $e_{m-2}$. The VDF would be run at the start of $e_{m-1}$ so that the output would be on-chain before $e_{m}$ starts.

#### VRF production
Each validator $v \in V$

1. Given the randomness $r_{m}$, computes a bunch of $a$ VRF outputs for the inputs $in_{m,i}=(r_m, i)$, $i = 1,\ldots,a$:
$$out_{m,v,i}=\texttt{Compute}_{RVRF}(sk_v, in_{m, i})$$

2. Selects the "winning" outputs that are below the threshold $T$: $\texttt{bake}(out_{m,v,i}) < T$
where $\texttt{bake()}$ is a function that effectively maps VRF outputs to the interval $[0,1]$. We call the set of $i$ corresponding to winning outputs $I_{win}$.

3. Uses its copath $ask_v$ generate proofs for the selected outputs $i \in I_{win}$,
$$\pi_{m,v,i} = \texttt{Prove}_{RVRF}(sk_v, spk_v, in_{m,i} )$$
where $\texttt{Prove}_{RVRF}(sk_v, spk_v, in_{m,j} )$ consists of the SNARK and its public inputs $cpk,i$.

As the result of this phase every validator obtains a number, possibly 0, of winning tickets together with proofs of their validity $(j, out_{m, v,j}, \pi_{m,v,j})$ that need to be published on-chain.

### 3) Publishing Phase
We want block producers for at least a large fraction of slots unknown in advance. Thus well-behaved validators should keep their tickets private. To this end validators dont publish their winning VRF outputs themselves immediately, but instead relay them to another randomly selected validator (proxy) who then publishes it.

Concretely, $v$ chooses another validator $v'$, based on the output $out_{m,v,i}$ for $i \in I_{win}$. To this end, the validator takes $k=out_{m,v,i} \textrm{mod} |V|$ and sends its winning ticket to the $k$th validator in a fixed ordering. Then the validator signs the message: $(v, l, enc_v'(out_{m,v,i}, \pi_{m,v,i}))$ where $end_{v'}$ refers to encrypted to a public key of $v'$. We number the winning outputs using $l$ ranging from $0$ up to $L-1$ and gossip them. If we have more than $L$ outputs below $T$, we gossip only the lowest $L$. This limitation is so that it is impossible for a validator to spam the network.

Once a valiaotr receives a messages it checks whether it has received a message with the same $v$ and $l$ and if so it discards the new message. Otherwise, the validator forwards (gossips) the message and decrypts it to find out whether the validator is the intended proxy. Validators gossip messages that are intended for them further to be secure against traffic correlation.

Once a validator decrypts a message with their private key they verify that they were the correct proxy, i.e. that $out_{m,v,i} \textrm{mod} |V|$ corresponds to them. If so, then at some fixed block number, they send a transaction including $(out_{m,v,i}, \pi_{m,v,i}))$ for inclusion on-chain. Note that the validator might have been proxy for a number of tickets, in that case, it sends a number of transaction on designated block number.

If a validators $v$ ticket is not included on-chain before some later block number, either because the proxy is misbehaving or because they havent sent the winning ticket to any proxies, then $v$ publishes the transaction $(out_{m,v,i}, \pi_{m,v,i})$ themselves. The reason why a validator would not send a winning ticket to any proxy is that it has more than $L$ winning tickets.

### 4) Verification

A transaction of this sort is valid for inclusion in a block if it can be verified as follows.

To verify the published transactions $(out_{m, v,i}, \pi_{m,v,i})$, we need to verify the SNARK. For this we need
- the corresponding input $in_{m,i}$, which we can calculate from $i$ and $r_m$,
- the published output $out_{m,v,i}$
- the aggregate public key $apk$.

All of these are the public inputs in SNARK verification:
$$Verify(\pi_{m,v,i}, apk, out_{m,v,i}, in_{m,i)$$

### 5) Sorting
In the epoch $e_{m+2}$ we have the list $\{out_{m,k}\}_{k=1}^{K}$ of $K$ verified VRF outputs generated during the epoch $e_m$ which are finalized on-chain. For each of these outputs, we combine the ouput with the randomness $r'$, with either $r'=r_{m+1}$ if we do not have a VDF or $r'=r_{m+2}$ if we do have a VDF. Then we compute $out'_{m,k}=H(out_{m,k} || r')$.

To determine the block production order for the epoch $e_{m+2}$, each validator sorts the list of $out'_{m,k}$ in ascending order and drops the largest $s-K$ values if any: $out'_{m,1},\ldots, out'_{m,l}$, where $l\leq s$ and $out'_{m,p}\leq out'_{m,q}$ for $1\leq p<q\leq l$.

The tickets are assigned to slots in an "Outside-in" ordering as follows. If we number the $out'_{m,k} from lowest to highest as $out'_{m,k}$ from $k=1$ to $K$ in increasing order, then the last slot is $out'_{m,1}$, the first slot is $out'_{m,2}$, the penultimate slot is $out'_{m,3}$, the second slot is $out'_{m,4}$ etc.

Example of outsidein sorting: (1,2,3,4,5)->(2,4,5,3,1)

In the unlikely event that $K < s$, there will be some unassigned slots in the middle of the epoch, and for these we use AuRa.

Concretely, for the algorithm for assiging lots that uses outside-in sorting, we take lists of even and odd numbered elements, reverse the list of odd elements, then concatenate the list of even elements, the list of aura slots and the reversed list of odd elements.

### 6) Claiming the slots

To produce a block in the assigned slot, the validator needs to include the ticket, a VRF output $out_{m,v,i}$, that corresponds to the slot together with a non-anonymous proof that this is the output of their VRF.

Thus we introduce
$\texttt{Reveal}_{RVRF}: sk_v, out\mapsto \tau$
and the corresponding
$\texttt{Check}_{RVRF}: \tau, out\mapsto true/false$
calls that are basically Schnorr knowledge of exponent proofs (PoKE).
When validating the block nodes verify these proofs.

The validator must also include a never before seen VRF output, called the BABE VRF above. This may be done with the existing (non-jubjub) key on the same input (r_m || i).

## Probabilities and parameters.

The first parameter we consider is $x$. We need that there is a very small probability of their being less than $s$ winning tickets, even if up to $1/3$ of validators are offline. The probability of a ticket winning is $T=xs/a|V|$.
Let $n$ be the number of validators who actually participate and so $2|V|/3 \leq n \leq |V|$. These $n$ validators make $a$ attempts each for a total of $an$ attempts.
Let $X$ be the nimber of winning tickets.

Then it's expectation has $E[X] = Tan = xsn/|V|$. If we set $x=2$, this is $ \geq 4s/3$. In this case, $Var[X] = anT(1-T) \leq anT = xsn/|V| = 2sn/|V| \leq 2s$. Using Bernstein's inequality:
\begin{align*}
\Pr[X < s] & \leq \Pr[X < E[X]-s/3] \\
& \leq exp(-\frac{(s/3)^2}{(Var[X]+s/3)}) \\
& \leq exp(-s/(9(2+1/3))) \\
& \leq exp(-s/21)
\end{align*}

For $s=600$, this gives under $4 * 10^{-13}$, which is certainly small enough. We only need the Aura fallback to deal with censorship. On the other hand, we couldn't make $x$ smaller than $3/2$ and still have tolerance against validators going offline. So $x=2$ is a sensible choice, and we should never need the Aura fallback.

The next parameter we should set is $a$. The problem here is that if a validator $v$ gets $a$ winning tickets in an epoch, then when the adversary sees these, they now know that there will be no more blocks from $v$.




