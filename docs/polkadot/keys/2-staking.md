
## Nominator keys

In some sense, all public keys derive their authority from some combination of ceremonies and certificates, with certificate root keys deriving tehir authority entirely from ceremonies.  As an example, trust-on-first-use schemes might be considered a pair of cerimonies, the key being associated to an identity first, and the threat of other comparing keys fingerprints.

We apply this perspective to a consensus algorithm for a proof-of-stake blockchains like polkadot by regarding the chain itself as one large ceremony and treating the staked account as the root of trust.  We then have certificates issued by these staked account keys that authenticate both the session keys used by Polkadot validators and block producers, as well as the long-term transport layer authentication keys required by TLS or Noise (see concerns about libp2p's secio).  

We must support, or may even require that, these session keys and TLS keys rotate periodically.  At thesame time, we must support staked account keys being air gapped, which prevents them from signing anything regularly.  In consequence, we require a layer layer called nominator keys that lies strictly between staked account keys and session keys.  In this post, we shall discuss the certificate scheme for delegating from staked account keys to nominator keys and delegating from nominator keys to session keys, which includes several unanswered questions.

In principle, any certificate format should work for nominator keys, but some certificate schemes provide more flexibility, while others save space.  We do not require much flexibility per se, but at least some of these certificates should live inside the staked account, and have some associated data:

 - block hash and height when staked,
 - unstaking block hash and height, if unstaking, and
 - permissions, like only block production, validator nomination, and validator operator.

### One vs two layer

We can support nominated proof-of-stake with only one layer per se.  We would have validator operator nominator keys point directly to their validator's current session keys, while nominator keys that only nominate would likely point to validator operator's nominator keys.  We expect all nominator keys act as owners for a block production node's session key because we do not permit delegation for block production.

We could require another layer, either by envisioning the session key itself as two layer, or by adding a second layer of nominator key.  I think a two layer session key simplifies session key rollover, which improves forward security and thus reduces the benefits of compromising nodes.  

### Certificate location

We could either store certificates with account data, or else provide certificates in protocol interactions, but almost surely the certificate delegating from the staked account to the nominator key belongs in the account data.

We should take care with the certificates from the nominator key to the session key because the session key requires a proof-of-possesion.  If we place them into the account, then there is a temptation to trust them and not check the proof-of-possesion ourselves.  We cannot necessarily trust the chain for proofs-of-possesion because doing so might provides escalation for attackers who succeed in posting any invalid data.  If we provide them in interactions then there is a temptation to check the proof-of-possesion repeatedly.  We should evaluate either attaching a self-checked flag to the staked account database vs storing session keys in some self-checked account database separate from the account database for which nodes trust the chain.  

### Certificate size

We could save some space by using implicit certificates to issue nominator keys, but we consider our initial implementation in [`schnorr-dalek/src/cert.rs`](https://github.com/w3f/schnorr-dalek/blob/master/src/cert.rs#L181) insufficient.  In essence, an accounts nominator key could be defined by an additional 32 bytes attached to the account, along with any associated data.  

We need to hold a conversation about (a) what form this associated data should take, and (b) if the space savings are worth the complexity of an implicit certificates scheme, mostly [reviewing the literature](https://github.com/w3f/schnorr-dalek/issues/4).  

We clearly need non-implicit certificates for non-owning nominators.  As a result, we might actually reduce the code complexity by not using implicit certificates in the nomination process.  We might then achieve better code reuse by not using implicit certificates anywhere. 

