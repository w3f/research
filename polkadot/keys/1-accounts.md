

## Account signatures and keys

We believe Polkadot accounts should primarily use Schnorr signatures with both public keys and the `R` point in the signature encoded using the [Ristretto](https://ristretto.group) point compression for the Ed25519 curve.  We should collaborate with the [dalek ecosystem](https://github.com/dalek-cryptography) for which Ristretto was developed, but provide a simpler signature crate, for which [schnorr-dalek](https://github.com/w3f/schnorr-dalek) provides a first step.

I'll write a another comment giving more details behind this choice, but the high level summary goes:


Account keys must support the diverse functionality desired of account keys on other systems like Ethereum and Bitcoin.  As such, our account keys shall use Schnorr signatures because these support fast batch verification and hierarchical deterministic key derivation ala [BIP32](https://github.com/bitcoin/bips/blob/master/bip-0032.mediawiki#Child_key_derivation_CKD_functions). All features from the [Bitcoin Schnoor wishlist](https://github.com/sipa/bips/blob/bip-schnorr/bip-schnorr.mediawiki) provides a case for Schnorr signatures matter too, like

 - interactive threshold and multi-signaturtes, as well as
 - adaptor, and perhaps even blind, signatures for swaps and payment channels. 


We make conservative curve choices here because account keys must live for decades.  In particular, we avoid pairing-based cryptography and BLS signatures for accounts, at the cost of true aggregation of the signatures in a block when verifying blocks, and less interactive threshold and multi-signaturtes. [1]. 

In the past, there was a tricky choice between the more secure curves:

 - miss-implementation resistance is stronger with Edwards curves, including the Ed25519 curve, but
 - miss-use resistance in stronger when curves have cofactor 1, like secp256k1.

In fact, miss-use resistance was historically a major selling point for Ed25519, which itself is a Schnorr variant, but this miss-use resistance extends only so far as the rudimentary signature scheme properties it provided.  Yet, any advanced signature scheme functions, beyond batch verification, break precisely due to Ed25519's miss-use resistance.  In fact, there are tricks for doing at least hierarchical deterministic key derivation on Ed25519, as implemented in [hd-ed25519](https://github.com/w3f/hd-ed25519), but almost all previous efforts [produced insecure results](https://forum.web3.foundation/t/key-recovery-attack-on-bip32-ed25519/44).

We observe that secp256k1 provides a good curve choice from among the curves of cofactor 1, which simplify make implementing fancier protocols.  We do worry that such curves appear at least slightly weaker than Edwards curves.   We worry much more than such curves tend to be harder to implement well, due to having incomplete addition formulas, and thus require more review (see [safecurves.cr.yp.to](https://safecurves.cr.yp.to)).  We could select only solid implementations for Polkadot itself, but we cannot control the implementations selected elsewhere in our ecosystem, especially by wallet software.

In short, we want an Edwards curve but without the cofactor, which do not exist, except..

In Edwards curve of with cofactor 4, [Mike Hamburg's Decaf point compression](https://www.shiftleft.org/papers/decaf/) only permits serialising and deserialising points on the subgroup of order $l$, which provides a perfect solution.  [Ristretto](https://ristretto.group) pushes this point compression to cofactor 8, making it applicable to the Ed25519 curve.  Implementations exist in both [Rust](https://doc.dalek.rs/curve25519_dalek/ristretto/index.html) and [C](https://github.com/Ristretto/libristretto255).  If required in another language, the compression and decompression functions are reasonable to implement using an existing field implementation, and fairly easy to audit.  

In the author's words, "Rather than bit-twiddling, point mangling, or otherwise kludged-in ad-hoc fixes, Ristretto is a thin layer that provides protocol implementors with the correct abstraction: a prime-order group."

---

[1] Aggregation can dramatically reduce signed message size when applying numerous signatures, but if performance is the only goal then batch verification techniques similar results, and exist for mny signature schemes, including Schnorr.  There are clear advantages to reducing interactiveness in threshold and multi-signaturtes, but parachains can always provide these on Polkadot.  Importantly, there are numerous weaknesses in all known curves that support pairings, but the single most damning weakness is the pairing $e : G_1 \times G_2 \to G_T$ itself.    In essence, we use elliptic curves in the first palce because they insulate us somewhat from mathematicians ever advancing understanding of number theory.  Yet, any known pairing maps into a group $G_T$ that re-exposes us, so attacks based on index-calculus, etc. improve more quickly.  As a real world example, there were weaknesses found in BN curve of the sort used by ZCash during development, so after launch they needed to develop and migrate to a [new curve](https://z.cash/blog/new-snark-curve/).  We expect this to happen again for roughly the same reasons that RSA key sizes increase slowly over time.


