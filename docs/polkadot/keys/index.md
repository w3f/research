
# Signing keys in Polkadot

In this post, we shall first give a high level view of the various signing keys planned for use in Polkadot.  We then turn the discussion towards the certificate chain that stretches between staked account keys and the session keys used for our proof-of-stake design.  In other words, we aim to lay out the important questions on the "glue" between keys rolls here, but first this requires introducing the full spectrum of key rolls.

We have roughly four cryptographic layers in Polkadot:

 - *Account keys* are owned by users and tied to one actual dot denominated account on Polkadot.  Accounts could be staked/bonded, unstaked/unbonded, or unstaking/unbonding, but only an unstaked/unbonded account key can transfer dots from one account to another.
 - *Nominator keys* provide a certificate chain between staked/bonded account keys and the session keys used by nodes in block production or validating.  As nominator keys cannot transfer dots, they insulate account keys, which may remain air gapped, from nodes actually running on the internet.
 - *Session keys* are actually several keys kept together that provide the various signing functions required by validators, including a couple types of verifiable random function (VRF) keys.
 - [*Transport layer static keys*](https://forum.web3.foundation/t/transport-layer-authentication-libp2ps-secio/69) are used by libp2p to authenticate connections between nodes.  We shall either certify these with the session key or perhaps include them directly in the session key.


