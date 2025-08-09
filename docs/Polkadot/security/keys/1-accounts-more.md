---
title: Account signatures and keys in Polkadot
---

![](account-signatures-and-keys.jpeg)

Polkadot accounts should primarily use Schnorr signatures, with both the public key and the `R` point in the signature encoded using the [Ristretto](https://ristretto.group) point compression for the Ed25519 curve. It is recommended to collaborate with the [dalek ecosystem](https://github.com/dalek-cryptography), for which Ristretto was developed, while providing a simpler signature crate. The [schnorr-dalek](https://github.com/w3f/schnorr-dalek) library offers a first step in that direction.

## Schnorr signatures 

Despite Schnorr signatures satisfying the [Bitcoin Schnorr wishlist](https://github.com/bitcoin/bips/blob/master/bip-0340.mediawiki) and performing well on highly secure curves such as Ed25519 and secp256k1, this wishlist arguably overstates the capabilities of Schnorr-based multi-signatures. In practice, these schemes typically require three round trips, which, while suitable for industrial applications, introduces additional complexity and latency. 

An alternative scheme, call mBCJ, described on pages 21-22 of [this paper](https://eprint.iacr.org/2018/417.pdf), offers a two-round multi-signature protocol. That said, a delinearized variant of mBCJ is required for account-based systems, as discussed in [this GitHub issue](https://github.com/w3f/schnorrkel/issues/15). It is also important to note that mBCJ is not a true Schnorr signature scheme, as it uses a different verification model and structural assumptions. 

More advanced techniques, such as signature aggregation using a pairing-based curve like BLS12-381 and the BLS signature scheme, are also possible. These curves tend to be slower for single verifications. Moreover, account systems are expected to reamin secure for decades, while pairing-friendly curves may become less secure over time as number theory advances.  

Choosing Schnorr signatures over ECDSA for account keys involves a trade-off: Both signature types are 64 bytes in size, but only [ECDSA signatures allow public key recovery](https://crypto.stackexchange.com/questions/18105/how-does-recovering-the-public-key-from-an-ecdsa-signature-work). While there are obsolete Schnorr variants that [support public key recovery](https://crypto.stackexchange.com/questions/60825/schnorr-pubkey-recovery), they compromise important features such as [hierarchical deterministic (HD) key derivation](https://www.deadalnix.me/2017/02/17/schnorr-signatures-for-not-so-dummies/).  In consequence, Schnorr signatures often require an additional 32 bytes to transmit the public key.

In return, the signature scheme becomes slightly faster and enables much simpler batch verification compared to [ECDSA batch verification](http://cse.iitkgp.ac.in/~abhij/publications/ECDSA-SP-ACNS2014.pdf). It also supports more natural implementation of threshold signatures, multi-signatures, and techniques used in payment channels. Additionaly, the inclusion of public key data may improve locality during block verification, potentially unlocking optimization opportunities.

Most importantly, by combining the derandomization techniques of EdDSA with a secure random number generator, Schnorr signatures offer enhanced protection. This results in stronger side-channel resistance compared to conventional ECDSA schemes. To improve ECDSA in this regard, the first step would be to explore side-channel mitigation strategies such as [rfc6979](https://tools.ietf.org/html/rfc6979), along with considerations like batch verification and other optimizations.


## Curves

There are two commonly used elliptic curves for account keys in blockchain systems: secp256k1 and Ed25519. For slightly more speed, FourQ is a viable alternative, though it may be excessive for blockchain use, as implementations are rare and it appears to be covered by older, though not fully expired, patents.  Additionally, for fast signature verification in zkSNARKs a relevant choice is Zcash's JubJub. However, JubJub is not part of Polkadot's roadmap and also lacks widespread implementation support.

### How much secp256k1 support?

secp256k1 keys require minimal support, primarily because token sale accounts on Ethereum are tied to secp256k1 keys. As a result, some "account" type must necessarily support secp256k1.  Using the same private keys across Ethereum and Polkadot is discouraged. Employing multiple key types is adivisable, especially since secp256k1 accounts may need not support balance increases or might only allow replacing themselves with an ed25519 key. 

That said, there are valid reasons to consider broader support for secp256k1, for example, enabling Ethereum smart contracts to verify signatures originated from Polkadot. While secp256k1 accounts can be supported with limited functionality, it may be worth expanding that functionality if such cross-chain use cases become relevant. 

### Is secp256k1 risky?

Two theoretical arguments support the preference for a twisted Edwards curve over secp256k1:  First, secp256k1 has a [small CM field discriminant](https://safecurves.cr.yp.to/disc.html), which could potentially enable more effective attacks in the distant future.  Second, secp256k1 uses fairly rigid paramater choices that are [not considered optimal](https://safecurves.cr.yp.to/rigid.html). Neither of these concerns is currently regarded as critical. 

From a more practical standpoint, secp256k1 does offer [twist security](https://safecurves.cr.yp.to/twist.html), which helps eliminate several classes of attacks and strengthens its overall resilience.  

The most substantial reason to avoid secp256k1 is that all short Weierstrass curves, including secp256k1, have [incomplete addition formulas](https://safecurves.cr.yp.to/complete.html). This means certain curve points cannot be added to others without special handling. As a result, the addition code must include checks for failures, which complicates writing constant-time implementations. 

Reviewing any secp256k1 library used in Polkadot is essential to ensure it performs these checks and maintains constant-time execution. It is not possible to ensure that all third-party wallet software does the same.

Incomplete addition formulas are relatively harmless when used for basic Schnorr signatures, though forgery attacks may sill be possible. A greater concern arises when secp256k1 is used in less well explored protocols, such as multi-signaturtes and key derivation. Awareness of such use cases exists, especially those outlined in the [Bitcoin Schnorr wishlist](https://github.com/bitcoin/bips/blob/master/bip-0340.mediawiki).  

### Is Ed25519 risky?  Aka use Ristretto

Any elliptic curve used in cryptography has an order of h*l, where l is a big prime, typically close to a power of two, and h is a very small number known as the cofactor.  Cofactors complicate almost all protocol implementations, which is why implementing complex protocols is generally safer on curves with a cofactor of h=1, such as secp256k1.  

The cofactor of the Ed25519 curve is 8, but a simple convention known as "clamping" helps secure two particularly common protocols. For more complex protocols, such as multi-signaturtes, key derivation, or other advanced constructions listed in the [Bitcoin Schnorr wishlist](https://github.com/bitcoin/bips/blob/master/bip-0340.mediawiki), "clamping" must be restricted or avoided altogether.  

Simply dropping "clamping" makes protocol implemention more difficult. Fortunately, the [Ristretto](https://ristretto.group) encoding for the Ed25519 curve ensures that no curve points with 2-torsion are used, effectively eliminating cofactor-related issues. Reecommendations are as follows:
 - The secret key remains an Ed25519 "expanded" secret key.
 - The on-chain encoding, aka known as "point compression", should use Ristretto for both public keys and the `R` component of Schnorr signatures. 

In principle, simple use cases can rely on standard Ed25519 "mini" secret keys, except when requiring key derivation. Ristretto-encoded public keys can still verify standard Ed25519 signatures with ease. Ideally, Ristretto should be used throughout in place of the standard Ed25519 point compression, as it eliminates cofactor-related issues and enables safer protocol design.  

It is indeed possible to import standard Ed25519 compressed points, as the [example](https://github.com/w3f/schnorr-dalek/blob/master/src/ristretto.rs#L877) shows. This requires scalar exponentiation via the [`is_torsion_free` method](https://doc.dalek.rs/curve25519_dalek/edwards/struct.EdwardsPoint.html#method.is_torsion_free), which is significantly slower than standard signature verification. Ideally, this process should be reserved for key migration between PoCs implementations.

Ristretto is conceptually simpler than the Ed25519 curve itself, making it easy to integrate into existing Ed25519 implementations. The [curve25519-dalek](https://github.com/dalek-cryptography/curve25519-dalek) crate already offers a highly optimized pure-rust implementation of both Ristretto and Curve25519 group operations.

### Zero-knowledge proofs in the dalek ecosystem

The [dalek ecosystem](https://github.com/dalek-cryptography) offers a remarkably well-designed infrastructure for zero-knowledge proofs without relying on pairings. For deeper insights, see these two foundational articles on bulletproofs and programmable constraint systems:
 [Bulletproofs Pre-release](https://medium.com/interstellar/bulletproofs-pre-release-fcb1feb36d4b) and [Programmable Constrait Systems for Bulletproofs](https://medium.com/interstellar/programmable-constraint-systems-for-bulletproofs-365b9feb92f7)

All these crates use Ristretto points, so adopting Ristretto for account public keys gives access to the most advanced tools for building protocols that do not rely on pairings-tools that operate directly on account keys. In principle, these tools could be abstracted to support other twisted Edwards curves, such as FourQ and Zcash's Jubjub. Abstracting them for short Weierstrass curves like secp256k1 may lead to the loss of certain batching optimizations. 



