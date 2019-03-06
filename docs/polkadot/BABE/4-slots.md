
## Winning slot leadership

We suppose $\nu$ knows a set $\mathbb{C}_\nu$ of chains
appropriate (TODO) to the current slot height $h$, and
selects a best chain $C$ according to our for choice rules.
We let $\ell$ denote the length of $C$, so that if $\nu$ wins slot
leadership then he should create a block $C[\ell]$ extending $C$
by containing a hash of $C[\ell-1]$ and correctly advancing the
state of $C[\ell-1]$

### Winner and non-winner proofs

As in Ouroboros Praos [Praos], we set block producer $\nu$'s
probability of winning any particular slot to be 
$$ p_\nu := 1-(1-c)^{\beta_\nu} $$
where $\beta_\nu = b_\nu / \sum_\mu b_\mu$ is their relative stake,
and $c$ is constant.

Importantly, the mapping $\{(\nu,b_\nu)\} \mapsto \{(\nu,p_\nu)\}$ has the
independent aggregation property, meaning block producers cannot
increase their odds by splitting their stakes across virtual parties.
In Ouroboros Praos, the $i$th block producer wins whenever
$$ H_{\mathtt{opbp}}(\mathtt{VRF}{v_\nu}( r_i || \mathtt{slotnum} )) < p_\nu $$

As discussed [BP1,BP2], we wish to defend against "speed up attacks"
by limiting how quickly staked but inactive nodes can impact the
block production rate.  We therefore adjust the above VRF "winner"
formula to facilite these "non-winner" proofs that improve block rate
information.  Intuitively, we produce a time until our next block from
the VRF evaluation, instead of evaluating our VRF on every slot.
We note this cannot protect against randomness bias because
nodes can always ensure their block cannot influence the randomness,
say by landing only as an uncle.

If block producer $\nu$'s $j$th VRF win occurred in epoch $i$ then
we define their subsequent VRF output to be
$$ s_{\nu,j+1} & := \mathtt{VRF}{v_\nu}(r_i || j || s_{\nu,j}) $$
We imagine their zeroth win as being the first slot in the first
epoch in which their VRF key registration became active, and
take $s_{\nu,0} = 0$, but do not actually give them this slot.

We then define the slot number of their $j+1$st win by sampling
a delay $d_{\nu,j+1}$ from a Poisson distribution with rate $1/p_\nu$ whose
source of randomness is a stream cipher seeded with $s_{\nu,j+1}$.
In pseudo code, this resembles
```
let $d_{\nu,j+1}$ = rand::Poisson::new($p_\nu$)
    .sample(&mut rand_chacha::ChaChaRng::from_seed($s_{\nu,j+1}$));
```
If the slot height of their $j$th slot is $h_{\nu,j}$ then
we compute the slot height for their $j+1$st slot as
$h_{\nu,j+1} := h_{\nu,j} + d_{\nu,j+1}$, which naturally falls in
epoch $h_{\nu,j+1} / T_{\texttt{epoch}}$.

We now observe that $E(h_{\nu,j+1} - h_{\nu,j}) = E(d_{\nu,j+1}) = 1/p_\nu$
in agreement with Ouroboros Praos.

In this, we implicitly required that $\nu$'s session key contain
$(h_{\nu,j},s_{\nu,j})$ along with $V_\nu$, and that $r_i$ be recorded somewhere.
We cannot demand that all blocks appear on our chain $C$ however, so
$\nu$'s session key actually contains $(h_{\nu,j_0},s_{\nu,j_0})$
for some $j_0 \le j$, and all $r_i$ must be recorded.
It follows that $\nu$'s $j+1$st block attempt should actually provide
a batched VRF proof of $s_{\nu,j'}$ for all $j_0 \le j' \le j$.

We expect this costs around $128 (j-j_0)$ bytes using Ristretto VRFs,
less if using BLS.  We update the $(h_{\nu,\cdot},s_{\nu,\cdot})$
components of $\nu$'s session key only when $\nu$ produces a block,
or registering or unstakes, because doing so with transactions,
including uncles, etc. only increases verification time and saves
no block space in aggregate.

Aside from consuming block space, we shall penalize chains with too
many missed blocks in our fork choice rule.  (TODO: Chain selection)

We should also permit block producers to unstake after they have waited
?three?months? from their last block.  We require require block producers
have some minimum stake to prevent them from continually restaking with
minuscule stake.  (TODO: Unstaking)

### Correctness

Any node $\mu$ receiving $B_\ell = (\cdots)$ validates the following conditions:

 - The session key of $\nu$ is correctly staked.
 - $\nu$ signed $B_\ell$.
 - The batched VRF proof correctly evolves the $(h_{\nu,j},s_{\nu,j})$ field in $\nu$'s session key into $(h_{\nu,j+1},s_{\nu,j+1})$.
 - $B_\ell$ correctly extends some chain $C' \in \mathbb{C}_\mu$ (TODO: gossip?).
 - The new slot height $h_{\nu,j+1}$ is appropriate to $\mathbb{C}_\mu$.
 - $\nu$ signed no other block at slot height $h_{\nu,j+1}$ in $\mathbb{C}_\mu$. (TODO: ban height or slash?),

...


[BP1] https://forum.parity.io/t/inter-chain-message-passing-research-meeting/153
[BP2] https://medium.com/web3foundation/w3f-research-workshop-outcomes-6320ae328222


