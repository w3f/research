====================================================================

**Owners**: [Jeff Burdges](/team_members/jeff.html)

====================================================================

# Polkadot's keys

In polkadot, we necessarily distinguish among different permissions and functionalities with different keys and key types, respectively.  We roughly categories these into account keys with which users interact and session keys that nodes manage without operator intervention beyond the certification process.

## Account keys

Account keys have an associated balance of which portions can be _locked_ to play roles in staking, resource rental, and governance, including waiting out some unlocking period.  We allow several locks of varying durations, both because these roles impose different restrictions, and for multiple unlocking periods running concurrently.

We encourage active participation in all these roles, but they all require occasional signatures from accounts.  At the same time, account keys have better physical security when kept in inconvenient locations, like safety deposit boxes, which makes signing arduous.  We avoid this friction for users as follows.

Accounts declare themselves to be _stash accounts_ when locking funds for staking.  All stash accounts register a certificate on-chain that delegates all validator operation and nomination powers to some _controller account_, and also designates some _proxy key_ for governance votes.  In this state, the controller and proxy accounts can sign for the stash account in staking and governance functions, respectively, but not transfer fund.

As a result, the stash account's locked funds can benefit from maximum physical security, while still actively participating via signatures from their controller or proxy account keys.  At anytime the stash account can replace its controller or proxy account keys, such as if operational security mistakes might've compromised either.

At present, we suport both ed25519 and schnorrkel/sr25519 for account keys.  These are both Schnorr-like signatures implemented using the Ed25519 curve, so both offer extremely similar security.  We recommend ed25519 keys for users who require HSM support or other external key management solution, while schnorrkel/sr25519 provides more blockchain-friendly functionality like HDKD and multi-signatures.

In particular, schnorrkel/sr25519 uses the [Ristretto](https://doc.dalek.rs/curve25519_dalek/ristretto/index.html) implementation of section 7 of Mike Hamburg's [Decaf](https://eprint.iacr.org/2015/673.pdf) paper, which provide the 2-torsion free points of the Ed25519 curve as a prime order group.  Avoiding the cofactor like this means Ristretto makes implementing more complex protocols significantly safer.  We employ Blake2b for most conventional hashing in polkadot, but schnorrkel/sr25519 itself uses the [merlin](https://doc.dalek.rs/merlin/index.html) limited implementation of Mike Hamberg's [STROBE](http://strobe.sourceforge.io/), which is based on Keccak-f(1600) and provides a hashing interface well suited to signatures and NIZKs.  See https://github.com/w3f/schnorrkel/blob/master/annoucement.md for more detailed design notes.

## Session keys

Session keys each fill roughly one particular role in consensus or security.  All session keys gain their authority from a session certificate that is signed by some controller key and that delegates appropriate stake.

At any time, the controller key can pause or revoke this session certificate and/or issue replacement with new session keys.  All new session keys can be registered in advance, and some must be, so validators can cleanly transition to new hardware by issuing session certificates that only become valid after some future session.  We suggest using pause for emergency maintenance and using revocation if a session key might be compromised.

We suggest session keys remain tied to one physical machine, so validator operators issue the session certificate using the RPC protocol, not handle the session secret keys themselves.   In particular, we caution against duplicating session secret keys across machines because such "high availability" designs invariably gets validator operators slashed.  Anytime new validator hardware must be started quickly the operator should first start the new node, and then certify the new session keys it creates using the RPC protocol.


We impose no prior restrictions on the cryptography employed by specific substrate modules or associated session keys types.

In BABE, validators use schnorrkel/sr25519 keys both for a verifiable random function (VRF) based on on [NSEC5](https://eprint.iacr.org/2017/099.pdf), as well as for regular Schnorr signatures.

A VRF is the public-key analog of a pseudo-random function (PRF), aka cryptographic hash function with a distinguished key, such as many MACs.  We award block productions slots when the block producer scores a low enough VRF output $\mathtt{VRF}(r_e || \mathtt{slot_number} )$, so anyone with the VRF public keys can verify that blocks were produced in the correct slot, but only the block producers know their slots in advance via their VRF secret key.

As in [Ouroboros Praos](https://eprint.iacr.org/2017/573.pdf), we provide a source of randomness $r_e$ for the VRF inputs by hashing together all VRF outputs form the previous session, which requires that BABE keys be registered at least one full session before being used.

We reduce VRF output malleability by hashing the signer's public key along side the input, which dramatically improves security when used with HDKD.  We also hash the VRF input and output together when providing output used elsewhere, which improves compossibility in security proofs. See the 2Hash-DH construction from Theorem 2 on page 32 in appendix C of ["Ouroboros Praos: An adaptively-secure, semi-synchronous proof-of-stake blockchain"](https://eprint.iacr.org/2017/573.pdf).

In GRANDPA, validators shall vote using BLS signatures, which supports convenient signature aggregation and select ZCash's BLS12-381 curve for performance.  There is a risk that BLS12-381 might drops significantly below 128 bits of security, due to number field sieve advancements.  If and when this happens, we expect upgrading GRANDPA to another curve to be straightforward.  See also https://mailarchive.ietf.org/arch/msg/cfrg/eAn3_8XpcG4R2VFhDtE_pomPo2Q

TODO: ImOnline ..  ref. https://github.com/paritytech/substrate/issues/3546 etc.

We treat libp2p's transport keys roughly like session keys too, but they include the transport keys for sentry nodes, not just for the validator itself.  As such, the operator interacts slightly more with these.




## old

In this post, we shall first give a high level view of the various signing keys planned for use in Polkadot.  We then turn the discussion towards the certificate chain that stretches between staked account keys and the session keys used for our proof-of-stake design.  In other words, we aim to lay out the important questions on the "glue" between keys rolls here, but first this requires introducing the full spectrum of key rolls.

We have roughly four cryptographic layers in Polkadot:

 - [*Account keys*](1-accounts.md) are owned by users and tied to one actual dot denominated account on Polkadot.  Accounts could be staked/bonded, unstaked/unbonded, or unstaking/unbonding, but only an unstaked/unbonded account key can transfer dots from one account to another.  ([more](1-accounts-more.md))
 - [*Nomination*](2-staking.md) provide a certificate chain between staked/bonded account keys and the session keys used by nodes in block production or validating.  As nominator keys cannot transfer dots, they insulate account keys, which may remain air gapped, from nodes actually running on the internet.
 - [*Session keys*](3-session.md) are actually several keys kept together that provide the various signing functions required by validators, including a couple types of verifiable random function (VRF) keys.
 - [*Transport layer static keys*](https://forum.web3.foundation/t/transport-layer-authentication-libp2ps-secio/69) are used by libp2p to authenticate connections between nodes.  We shall either certify these with the session key or perhaps include them directly in the session key.


