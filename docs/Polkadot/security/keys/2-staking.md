---
title: Nomination
---
<!--![](Nomination.png)-->

In a sense, all public keys derive their authority from some combination of ceremonies and certificates, with certificate root keys relying entirely on ceremonies for their authority. For example, trust-on-first-use schemes can be viewed as a pair of ceremonies: first, the key is associated with an identity, and second, its fingerprint is compared against others to detect potential threats.

This perspective also applies to consensus algorithms in proof-of-stake blockchains, like Polkadot, by viewing the chain itself as a large, ongoing ceremony and treating the staked or bonded account as the root of trust. The certificates these staked account keys issue authenticate both the session keys that Polkadot validators and block producers use and the long-term transport-layer authentication keys required by protocols like TLS or Noise (see concerns about libp2p's secio).  

## Stash account keys

In Polkadot, we call such staked or bonded account keys "stash account keys," to distinguish them from the other key roles discussed below. This [GitHub entry](https://github.com/paritytech/substrate/blob/1a2ec9eec1fe9b3cc2677bac629fd7e9b0f6cf8e/srml/staking/Staking.md) describes the transactions `unbond`, `withdraw_unbonded`, and `bond_extra`, among others. There are several ways to implement these or related operations, but if account size is not overly constrained, we can consider the following highly flexible approach.

Each stash account maintains an unstaked balance $u \ge 0$ and a list of pending unstaking dates and balances $T = { (t,v) }$ with $v>0$, where one entry lacks a specific unstaking date, i.e., $t = \infty$.  An unstaking operation splits $(\infty,v) \in T$ into $(\infty,v - v')$ and $(t,v')$.  Any payment from a staked account completes pending unstaking operations by transferring their value into the unstaked balance $u$.  In other words, at block height $h$, a payment of value $v'$ with fees $f$ from a stash account is valid if:

 - $T_1 = \{ (t,v) \in T_0 : t > h \}$,
 - $u_1 := u_0 + \sum \{ (t,v) \in T_0 : t \le h \} - h - f$ remains positive.

Additional metadata in $T$ may ensure that delayed slashing does not affect more recently added stake. This concern closely resembles the discussion above.  

## Stake controller account keys

Session keys and TLS keys must rotate periodically.  At the same time, stash account keys should remain air-gapped, preventing their use for regular signing.  In consequence, an additional layer, called "stake controller account keys," is required. These keys act as intermediaries, managing the nomination or delegation from stash account keys to session keys. 

Since staking involves small, frequent transactions, "stake controller account keys" are actual account keys with their own separate balances, typically much smaller than the "stash account key" they represent. 

In the future, stash account keys may issue certificates that restrict the actions of controller keys. This would enhance staker security, especially for functions that involve reduced slashing risk.  For example, enabling modes for fishermen or block producers could explicitly prohibit nominating or running a validator.  

Currently, however, the system supports only one slashing level. As such, the controller key itself controls all mode transitions, as the [GitHub entry](https://github.com/paritytech/substrate/blob/1a2ec9eec1fe9b3cc2677bac629fd7e9b0f6cf8e/srml/staking/Staking.md) mentioned earlier describes.

## Certificate location

Certificates can either be stored with account data or provided during protocol interactions. In most cases, the certificate delegating authority, from the staked account to the nominator key, should be stored within the account data.

Special attention must be given to certificates issued from the controller key to the session key, as the session key requires a proof of possesion.  If these certificates are stored in the controller account, there may be a temptation to trust them without verifying the proof of possesion. Yet the proof-of-possession chain is not fully trustworthy, since trusting it could let attackers escalate privileges by submitting invalid data. On the other hand, if each interaction includes a certificate, there may be a tendency to verify the proof of possession repeatedly. This trade-off should be carefully evaluated, either attaching a self-checked flag to the staked account database or by storing session keys in a separate, self-checked account database distinct from the one nodes rely on via the chain.  

## Certificate size

Using implicit certificates to issue nominator keys can save space. Yet the initial implementation in [`schnorr-dalek/src/cert.rs`](https://github.com/w3f/schnorr-dalek/blob/master/src/cert.rs#L181) proved insufficient, so this purpose would require a different implicit certificate scheme.  

In essence, an account's nominator key could be defined by appending an additional 32 bytes to the account, along with any associated data. Implementing this approach requires a clear understanding of a) the appropriate structure for the associated data, and b) whether the space savings justify the added complexity of an implicit certificate scheme, primarily through [reviewing the literature](https://github.com/w3f/schnorr-dalek/issues/4). For now, avoiding implicit certificates favors simplicity.

**For further information or questions please contact:** [Jeffrey Burdges](/team_members/jeff.md)

[^1] https://github.com/paritytech/substrate/pull/1782#discussion_r260265815



