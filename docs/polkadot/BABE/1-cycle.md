
## Randomness cycle

In Polkadot, we produce relay chain blocks using our
 blind assignment for blockchain extension (BABE) protocol.  
BABE assigns blocks production slots, according to stake,
 using roughly the randomness cycle from Ouroboros.

In this setting, any block producer $\nu$ has at least

 - an account key pair $(A_\nu,a_\nu)$ with a balance $b_\nu$ marked as "staked" for the purpose of certifying
 - a verifiable random function (VRF) key pair $(V_\nu, v_\nu)$.

So $A_\nu = a_\nu G$ and $V_\nu = v_\nu G$,
 if using an elliptic curve with basepoint $G$.
In practice, there are several keys that accompany the VRF key $V$,
which collectively we call a "session key".
See:  https://github.com/w3f/research/blob/master/docs/polkadot/keys/2-staking.md

As one expects, all parties $\nu$ maintain a local set of blockchains
$\mathbb{C}_\nu = \{C_1, C_2,..., C_l\}$ too, which have
 a common prefix up until some height,
 at least including the genesis block.

As in Ouroboros, we cycle between 

 1. a block producer $\nu$ identify the slots for which they should
    claim slot leadership by applying their $\mathtt{VRF}_{v_\nu}$ to some
    collaborative randomness $r_i$ and additional deterministic data, 
 2. the collaborative randomness $r_j$ with $j>i$ gets constructed from
    the VRF outputs appearing in appropriate recent blocks.

In Ouroboros, the additional data is simply the slot number, and
 the slot leadership condition is simply that the VRF output
 falls below some linear function of the stake $b_\nu$.
In BABE, we improve telemetry and liveness by altering
 this additional data and the slot leadership condition, 
as discussed in section ?? below.

Importantly, any VRF key $V_\nu$ only becomes usable for block production
_after_ our collaborative randomness registers the VRF key $V_\nu$
 as being staked by the account key $A_\nu$. 
We shall discuss in section ?? the analysis from Ouroboros Praos(?)
of how this cycle reduces the bias malicious block producers achieve
 by select their VRF key $v_\nu$.

In consequence, we have sequential non-overlaping epochs, each of which
 defines a collaborative random value $(r_1, r_2, \ldots)$ and
 contains a fixed number $T_{\texttt{epoch}}$ of sequential block production slots.
Inside any epoch, the VRFs make slot leadership allocation both private
and deterministic, but at the cost of occasional conflicts in which 
several block producers win the same slot.  We somewhat limit these
slot allocation conflicts by having a slot rate much higher than
the desired block rate.  We address any remaining slot allocation
conflicts as we address all other forks, using
 our chain selection rules described in section ??? and
 our consensus rules, as largely given by our finality gadget GRANDPA ???.

We note that VRF keys being forced to be relatively long-lived benefits
our analysis by reducing malicious influence, but any signing keys used
in issuing blocks or the consensus rules benefit from forward security
against attackers causing slashing if they can be short-lived.
More details related to these key are [here](https://github.com/w3f/research/tree/master/docs/polkadot/keys).  TODO:  Really?

We also note the RANDAO proposal for Ethereum 2.0 roughly fits into this
model as a VRF whose domain is the series of singleton tuples $\{(i,j)\}$
with $i$ the epoch and $j$ the slot number.  We dislike RANDAO because
first revealing a hash from every block producer for each slot costs
quadratic bandwidth, or at least computation, and second adversaries
might choose their final reveal. 

