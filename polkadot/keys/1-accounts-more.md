
# Account signatures and keys in Polkadot

We believe Polkadot accounts should primarily use Schnorr signatures with both public keys and the `R` point in the signature encoded using the [Ristretto](https://ristretto.group) point compression for the Ed25519 curve.  We should collaborate with the [dalek ecosystem](https://github.com/dalek-cryptography) for which Ristretto was developed, but provide a simpler signature crate, for which [schnorr-dalek](https://github.com/w3f/schnorr-dalek) provides a first step.


## Schnorr signatures 

We prefer Schnorr signatures because they satisfy the [Bitcoin Schnoor wishlist](https://github.com/sipa/bips/blob/bip-schnorr/bip-schnorr.mediawiki) and work fine with extremely secure curves, like secp256k1 or the Ed25519 curve.  You could do fancier tricks, including like aggregation, with a pairing based curve like BLS12-381 and the BLS signature scheme.  These curves are slower for single verifications, and worse accounts should last decades while pairing friendly curves should be expected become less secure as number theory advances.  

There is one sacrifice we make by choosing Schnorr signatures over ECDSA signatures for account keys:  Both require 64 bytes, but only [ECDSA signatures communicate their public key](https://crypto.stackexchange.com/questions/18105/how-does-recovering-the-public-key-from-an-ecdsa-signature-work).  There are obsolete Schnorr variants that [support recovering the public key from a signature](https://crypto.stackexchange.com/questions/60825/schnorr-pubkey-recovery), but 
they break important functionality like [hierarchical deterministic key derivation](https://www.deadalnix.me/2017/02/17/schnorr-signatures-for-not-so-dummies/).  In consequence, Schnorr signatures often take an extra 32 bytes for the public key.

In exchange, we gain a slightly faster signature scheme with far simpler batch verification than [ECDSA batch verification](http://cse.iitkgp.ac.in/~abhij/publications/ECDSA-SP-ACNS2014.pdf) and more natural threshold and multi-signatures, as well as tricks used by payment channels.  I also foresee the presence of this public key data may improve locality in block verification, possibly openning up larger optimisations.

Yet most importantly, we can protect Schnorr signatures using both the derandomization tricks of EdDSA along with a random number generator, which gives us stronger side-channel protections than conventional ECDSA schemes provide.  If we ever do want to support ECDSA as well, then we would first explore improvements in side-channel protections like [rfc6979](https://tools.ietf.org/html/rfc6979), along with concerns like batch verification, etc.


## Curves

There are two normal curve choices for accounts on a blockchain system, either secp256k1 or the Ed25519 curve, so we confine our discussion to them.  If you wanted slightly more speed, you might choose FourQ, but it sounds excessive for blockchains, implementations are rare, and it appears covered by older but not quite expired patents.  Also, you might choose Zcash's JubJub if you wanted fast signature verification in zkSNARKs, but that's not on our roadmap for Polkadot, and Jubjub also lacks many implementations.

### How much secp256k1 support?

We need some minimal support for secp256k1 keys because token sale accounts are tied to secp256k1 keys on Ethereum, so some "account" type must necessarily use secp256k1 keys.  At the same time, we should not encourage using the same private keys on Ethereum and Polkadot.  We might pressure users into switching key types in numerous ways, like secp256k1 accounts need not support balance increases, or might not support anything but replacing themselves with an ed25519 key.  There are conceivable reasons for fuller secp256k1 support though, like wanting ethereum smart contracts to verify some signatures on Polkadot.  We might support secp256k1 accounts with limited functionality, but consider expanding that functionality if such use cases arise. 

### Is secp256k1 risky?

There are two theoretical reasons for preferring an twisted Edwards curve over secp256k1:  First, secp256k1 has a [small CM field discriminant](https://safecurves.cr.yp.to/disc.html), which might yield better attacks in the distant future.  Second, secp256k1 has fairly rigid paramater choices but [not the absolute best](https://safecurves.cr.yp.to/rigid.html).  I do not believe either to be serious cause for concern.  Among more practical curve weaknesses, secp256k1 does have [twist security](https://safecurves.cr.yp.to/twist.html) which eliminates many attack classes.  

I foresee only one substancial reason for avoiding secp256k1:  All short Weierstrass curves like secp256k1 have [incomplete addition formulas](https://safecurves.cr.yp.to/complete.html), meaning certain curve points cannot be added to other curve points.  As a result, addition code must check for failures, but these checks make writing constant time code harder.  We could examine any secp256k1 library we use in Polkadot to ensure it both does these checks and has constant-time code.  We cannot however ensure that all implementations used by third party wallet software does so.

I believe incomplete addition formulas looks relatively harmless when used for simple Schnorr signatures, although forgery attacks might exist.  I'd worry more however if we began using secp256k1 for less well explored protocols, like multi-signaturtes and key derivation.   We ware about such use cases however, especially those listed in the [Bitcoin Schnoor wishlist](https://github.com/sipa/bips/blob/bip-schnorr/bip-schnorr.mediawiki).  

### Is Ed25519 risky?  Aka use Ristretto

Any elliptic curve used in cryptography has order h*l where l is a big prime, normally close to a power of two, and h is some very small number called the cofactor.  Almost all protocol implementations are complicated by these cofactors, so implementing complex protocols is safer on curves with cofactor h=1 like secp256k1.  

The Ed25519 curve has cofactor 8 but a simple convention called "clamping" that makes two particularly common protocols secure.  We must restrict or drop "clamping" for more complex protocols, like multi-signaturtes and key derivation, or anything else in the [Bitcoin Schnoor wishlist](https://github.com/sipa/bips/blob/bip-schnorr/bip-schnorr.mediawiki).  

If we simple dropped "clamping" then we'd make implementing protocols harder, but luckily the [Ristretto](https://ristretto.group) encoding for the Ed25519 curve ensures we avoid any curve points with 2-torsion.  I thus recommend:
 - our secret key continue being Ed25519 "expanded" secret keys, while
 - our on-chain encoding, aka "point compression" becomes Ristretto for both public keys and the `R` component of Schnoor signatures. 

In principle, we could use the usual Ed25519 "mini" secret keys for simple use cases, but not when doing key derivation.  We could thus easily verify standrad Ed25519 signatures with Ristretto encoded public keys.  We should ideally use Ristretto throughout instead of the standard Ed25519 point compression.  

In fact, we can import standard Ed25519 compressed points like I do [here](https://github.com/w3f/schnorr-dalek/blob/master/src/ristretto.rs#L877) but this requires the scalar exponentiation done in the [`is_torsion_free` method](https://doc.dalek.rs/curve25519_dalek/edwards/struct.EdwardsPoint.html#method.is_torsion_free), which runs slower than normal signature verification.  We might ideally do this only for key migration between PoCs.

Ristretto is far simpler than the Ed25519 curve itself, so Ristretto can be added to Ed25519 implementations, but the [curve25519-dalek](https://github.com/dalek-cryptography/curve25519-dalek) crate already provides a highly optimised rust implementation.

### Zero-knowledge proofs in the dalek ecosystem

In fact, the [dalek ecosystem](https://github.com/dalek-cryptography) has an remarkably well designed infrastructure for zero-knowledge proofs without pairings.  See:
 https://medium.com/interstellar/bulletproofs-pre-release-fcb1feb36d4b
 https://medium.com/interstellar/programmable-constraint-systems-for-bulletproofs-365b9feb92f7

All these crates use Ristretto points so using Ristretto for account public keys ourselves gives us the most advanced tools for building protocols not based on pairings, meaning that use our account keys.  In principle, these tools might be abstracted for twisted Edwards curves like FourQ and Zcash's Jubjub, but yu might loose some batching operations in abstracting them for short Weierstrass curves like secp256k1. 



