
## Epoch updates

We begin a new epoch $i+1$ by simultaneously (a) accepting new VRF keys aka session keys and updating to new stake values, for which requests were registered far enough in the past, and (b) switching to our new collaborative randomness $r_{i+1}$, which must previously be computed.  We primarily discuss $r_{i+1}$ below, while discussion of unstaking lies in ???.

We start epochs at specific slot numbers to help prevent adversaries
from influencing both which collaborative random value $r_i$ gets used,
as well as the creation of any subsequence collaborative random value
$r_j$ for $j>i$.

Ouroboros Praos [Praos] computes the new collaborative randomness
$r_{i+1} := H(r_i || i+1 || \rho)$ from the previous collaborative
randomness $r_i$ together with the concatenation $\rho$ of all VRF
outputs in the $i$th epoch from slot 1 through slot ${2\over3} T_{\mathtt{epoch}}$.
This computation makes Ouroboros the simplest but weakest secure
block production scheme, in the sense that block production itself
is proven secure despite adversaries being able to bias these
collaborative random values, but that the bias may impact using the
randomness elsewhere.

### Unbiased randomness

In Polkadot, we must strengthen our collaborative randomness because
shard aka parachain assignments would be far more vulnerable to bias
than block production.  

In the classical literature, one accomplishes this by using either
verifiable secret sharing (VSS) like DFinity [DFinity] or else
publicly verifiable secret sharing (PVSS) like RoundHound [??] / RandHerd [??].

Any naive threshold secret sharing design has an unfortunate failure
mode in which a large enough majority of stake holders can foresee or
even heavily influence the randomness.  Advanced schemes like RandHerd
address such weaknesses with a subcommittee selection procedure that
prevents an adversary from always foreseeing the output.  
All this involves a complex synchronous protocol separate from block
production, likely including accusation and slashing logic.  
We expect the synchronous requirement to harm livesness.

### Verifiable Delay Function

In Polkadot, we instead obtain unbiased randomness using a recent
cryptographic construction called a verifiable delay function (VDF)
[vdfresearch].  Intuitively, a VDF consists of 

 1. a compute routine that, given an input byte string $x$, yields the
    output $y$ of some slow non-parallelizable computation, along with
	a proof $\pi$ that $y$ is the correct output corresponding to $x$,
    as well as
 2. a verify routine that quickly checks that proof proves the correctness
    of $y$ for the given input $x$.

There is no stake arrangement, political scenario, etc. in which
an adversary can learn the VDF output significantly faster, although
an adversary could delay their inputs to give themselves a head start
and/or use faster computation like ASICs or super-conducting computing,
or find a mathematical breakthrough against the VDF primitive.

In practical terms, an adversary with a $k$ fold advantage against 
the VDF can impact $r_i$ when they control the final $e/k$th of the
slots in an epoch, where $e$ is the number of epochs for which the
VDF runs.   A larger $k$ thus permits an adversary control fewer slots
with correspondingly less stake but also fewer bits impacted. 

We improve efficiency when fewer parties actually compute the VDF
output.  As a non-example, the caucus leader election protocol of
Fantômette [Fantomette] violtes this principle by running VDFs
on many distinct inputs.

There is also a second converse worry that an adversary who reliably
computes the VDF fastest can impact the protocol by revealing their
output late.  In principle, one might address this by manually
tuning the VDF with experiments on known hardware.

In https://ethresear.ch/t/minimal-vdf-randomness-beacon/3566
Justin Drake addresses both adversaries who speed up and who delay
together by describing the adversary's required advantage as
the ratio between the epoch duration in which we accept input
contributions and the number of epochs the VDF waits.
As a result, Justin recommend numerous parallel VDFs runs
ending at different times, which we consider excessive.

Instead, we propose that VDFs be evaluated in stages, so that
an adversary cannot delay beyond one stage without another node
taking over

$$ \begin{align}
  r_{i+1,0} & := H(r_i || m+1 || \rho)  \\
  r_{i+1,j+1} & := \mathtt{VDF}_T(r_{i+1,j})  \\
  r_{i+1} & := r_{i+1,\mathtt{numstages}} \\
\end{align} $$

A priori, we now require an $O(\mathtt{numstages})$ space proof of
correctness on-chain, although optimisations exist at some complexity cost.

### Class-group VDFs

There are now several VDF constructions but the two most likely
ones by Pietrzak [Pietrzak] and Wesolowski [Wesolowski] both compute
squarings in a group of unknown order for the slow non-parallelizable
computation, but differ in their proofs $\pi$ [VDFsurevey] and
the recommended group of unknown order.

In both cases however, the proof $\pi$ involves a Fiat-Shamir transform
using $H_0(x ++ y)$.  We prefer a VDF for which the proof $\pi$ can
be "owned" by a particular prover.  We therefore replace this $H_0$
by $\pi_0 := VRF_{v_j}(x ++ y)$.  As in Appendix C of [Praos],
we always take $VRF(m).out() := H(m, v_j H'(m))$ where $H'$ hashes to
a curve element, so the outer $H$ ensures our VRF itself acts as a
random oracle whenever the right parties know $v_j H'(m)$, and thus  
our adjustment supports many Fiat-Shamir transforms.

There are proposals like [Pietrzak] to employ an RSA composite
$p q$ with $p$ and $q$ unknown for the group of unknown order, but
such RSA composites require a trusted setup far messier and more
worrisome than those required by zkSNARKs.  If we ignore these trust
issues, we still notice that ZCash had relatively few participants
in their second Sapling trusted setup, so we judge the Polkadot
community unprepared for doing a quality trusted setup.

In [Wesolowski], Wesolowski proposes using the class group of an
imaginary quadratic order $\mathbb{Q}(\sqrt{-p})$ for the group
of unknown order.  We'd prefer if these objects were better explored
by cryptographers, but they nicely address our worries with RSA
composites.  There is an elementary discussion of the mathematics in
https://github.com/Chia-Network/vdf-competition/blob/master/classgroups.pdf

Implementations actually hash to the prime $p$ like
https://github.com/poanetwork/vdf/blob/master/vdf/src/create_discriminant.rs
which should prevent precompute attacks, and surprisingly even makes
the VDF "quantum annoying".  In the short term, we judge this
resistance to precompute attacks as outweighing class groups
being less well understood. 

Justin Drake recommends using an RSA composite instead of a class group
on the grounds that

 - the smaller circuit size for RSA permits doing the squarings inside an ASIC,
 - that ASICs provide a thousand fold speed up over CPUs, and
 - that exotic approaches like superconducting computing yield only about another ten fold increase over ASICs.

We cannot independently confirm his assessments here but consider it
reasonable.  We believe however that many techniques should be
explored, especially given the relative youth of VDFs as a primitive.
ASICs require investing far too much in one approach, while only
a fraction of this investment would yield advances in various
relevant cryptography fields, like imaginary quadratics and isogenies.

### Isogenies VDF

There is another recent VDF [isogenies] designed by
 Luca De Feo, Simon Masson, Christophe Petit, and Antonio Sanso,
based on isogenies between super-singular elliptic curves with pairings.
We should support further research into this VDF for several reasons: 

 - verification appears faster than other VDF approaches, only two pairings on 1500 bit super-singular curves,
 - the same problem underlies the post-quantum key exchange CSIDH [CSIDH], which attracts deeper cryptoanalytic work,
 - a related isogenies-based schemes provides small signatures and VRFs, currently the only "quantum annoying" signatures to be "blockchain friendly", and 
 - isogenies-based schemes provide the smallest candidates for actual post-quantum signatures.

In the isogenies VDF, we'd require a trusted setup to identify a
starting curve for which the endomorphism ring is unknown, but this
trusted setup seems less problematic than the RSA trusted setup.
Avoiding this setup might be possible if we could produce random
super-singular curves.

At first blush, there is no proof required for the isogenies VDF but
Luca de Feo and I devised one that permits outputs to be owned.
Interestingly, this isogenies based VDF admits an $O(1)$ space proof
on-chain even in the worst case, while the VDFs by Pietrzak and
Wesolowski have a worst case $O(\mathtt{numstages})$ space proof
on-chain when all stages wind up evaluated by different parties, and
improving this incurs considerable complexity to reduce this.

As an aside, we could encrypt a message to the future evaluation of
this isogeny-based VDF by treating the isogeny as a master secret key
for an IBE scheme in which the VDF result is the derived private key:
After first producing the VDF input $r'$, we select a secret scalar
$x$ and encrypt the message using the right hand side of the following
equation, and then publish the encrypted message along with $x G_1$.
We later learn $\psi(H_2(r'))$ by evaluating the VDF, which makes the
message decryptable.
$$ e( \phi(G_1), x H_2(r') ) = e( x G_1, \psi(H_2(r')) ) $$

As present, the isogenies VDF construction benefits from one unique
pre-computed field element per isogeny computation, which perhaps
reduces their performance almost entirely to memory bandwidth. 
It remains to assess if this provides a more foreseeable delay less 
impacted by ASICs, etc.


 [Wesolowski]:  https://eprint.iacr.org/2018/623.pdf
 [Pietrzak]: https://eprint.iacr.org/2018/627.pdf
 [VDFsurevey]: https://eprint.iacr.org/2018/712.pdf
 [Boneh]: https://eprint.iacr.org/2018/601.pdf
 [vdfresearch]: https://vdfresearch.org
 [isogenies]: https://eprint.iacr.org/2019/166.pdf
 [CSIDH]: https://csidh.isogeny.org
 [Praos]: https://eprint.iacr.org/2017/573.pdf
 [Fantomette]: https://export.arxiv.org/pdf/1805.06786


