
## Nomination

In some sense, all public keys derive their authority from some combination of ceremonies and certificates, with certificate root keys deriving tehir authority entirely from ceremonies.  As an example, trust-on-first-use schemes might be considered a pair of cerimonies, the key being associated to an identity first, and the threat of other comparing keys fingerprints.

We apply this perspective to a consensus algorithm for a proof-of-stake blockchains like polkadot by regarding the chain itself as one large ceremony and treating the staked/bonded account as the root of trust.  We then have certificates issued by these staked account keys that authenticate both the session keys used by Polkadot validators and block producers, as well as the long-term transport layer authentication keys required by TLS or Noise (see concerns about libp2p's secio).  

### Stash account keys

In polkadot, these staked or bonded account keys are called "stash account keys" to help disambiguate them from other key roles discussed below.  We currently describe `unbond`, `withdraw_unbonded`, and `bond_extra` transactions in [2].  There are several ways to implement these, or related operations, but if accounts are not too constrained in size then one extremely flexible approach goes:

These stash accounts has an unstaked balance $u \ge 0$ and a list of pending unstaking dates and balances $T = \{ (t,v) \}$ with $v>0$, one of which lack any unstaking date, meaning $t = \infty$.  An unstaking operation splits $(\infini,v) \in T$ into $$(\infini,v - v')$ and $(t,v')$.  Any payment out of a staked account completes any pending unstaking operations by moving their value into the unstaked balance $u$.  In other words, at block height $h$, a payment of value $v'$ with fees $f$ out of a stash account is valid if

 - $T_1 = \{ (t,v) \in T_0 : t > h \}$,
 - $u_1 := u_0 + \sum \{ (t,v) \in T_0 : t \le h \} - h - f$ remains positive.

We might require additional metadata in $T$ so that delayed slashing cannot impact more recently added stake, but this resembles the above discussion.  TODO:  Be more detailed?

### Stake controller account keys

We must support, or may even require, that these session keys and TLS keys rotate periodically.  At the same time, we must support stash account keys being air gapped, which prevents them from signing anything regularly.  In consequence, we require another layer, called "stake controller account keys", that lies strictly between, and control the nomination of or delegation from stash account keys to session keys. 

As we require small transactions associated to staking, these "stake controller account keys" are actual account keys with their own separate balance, usually much smaller than the "stash account key" for which they manage nomination/delegation. 

In future, we might permit the certificate from the stash account key to limit the actions of a controller keys, which improves our stakers' security when certain functions permit less slashing.  In particular, we might admit modes for fishermen and block producers that prohibit nominating or running a validator.  

At the moment however, we only support one such slashing level, so all mode transitions are functions of the controller key itself, as described in [2].

### Certificate location

We could either store certificates with account data, or else provide certificates in protocol interactions, but almost surely the certificate delegating from the staked account to the nominator key belongs in the account data.

We should take care with the certificates from the controller key to the session key because the session key requires a proof-of-possesion.  If we place them into the controller account, then there is a temptation to trust them and not check the proof-of-possesion ourselves.  We cannot necessarily trust the chain for proofs-of-possesion because doing so might provides escalation for attackers who succeed in posting any invalid data.  If we provide them in interactions then there is a temptation to check the proof-of-possesion repeatedly.  We should evaluate either attaching a self-checked flag to the staked account database vs storing session keys in some self-checked account database separate from the account database for which nodes trust the chain.  

### Certificate size

We could save some space by using implicit certificates to issue nominator keys, but we consider our initial implementation in [`schnorr-dalek/src/cert.rs`](https://github.com/w3f/schnorr-dalek/blob/master/src/cert.rs#L181) insufficient, so we'd require another implicit certificate scheme for this.  In essence, an accounts nominator key could be defined by an additional 32 bytes attached to the account, along with any associated data.  Actually doing this requires understanding (a) what form this associated data should take, and (b) if the space savings are worth the complexity of an implicit certificates scheme, mostly [reviewing the literature](https://github.com/w3f/schnorr-dalek/issues/4).  We favor simplicity by avoiding implicit certificates currently.

### Implementation

[1] https://github.com/paritytech/substrate/pull/1782#discussion_r260265815
[2] https://github.com/paritytech/substrate/blob/1a2ec9eec1fe9b3cc2677bac629fd7e9b0f6cf8e/srml/staking/Staking.md aka https://github.com/paritytech/substrate/commit/1a2ec9eec1fe9b3cc2677bac629fd7e9b0f6cf8e



