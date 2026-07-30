---
title: Nominated Proof-of-Stake
---

<!--![](Nominated-proof-of-stake.png)-->

In recent years, many blockchain projects have replaced the highly inefficient Proof-of-Work (PoW) component of Nakamoto’s consensus protocol with Proof-of-Stake (PoS). In PoS systems, validators participate in block production at a frequency proportional to their token holdings, rather than their computational power. Although a pure PoS model lets any token holder participate directly, most projects adopt some degree of centralization by limiting the number of validators with full participation rights. The rationale for this limited validator set design is based on the following considerations:

- As the number of validators increases, operational costs and communication complexity eventually outweigh the benefits of decentralization.
- While many token holders may wish to contribute to system maintenance, the number of candidates with the necessary knowledge and equipment to ensure high-quality service remains limited.
- In both PoW- and PoS-based networks, when the number of validators becomes large, participants in the latter tend to form pools to reduce revenue variance and benefit from economies of scale.

Rather than allowing pools to form off-chain, it is more effective to formalize and facilitate their formation on-chain, enabling users to vote with their stake to elect validators who represent them and act on their behalf. Networks that follow this model include Polkadot, Cardano, EOS, Tezos, and Cosmos, among others. While united in principle, these networks differ in design choices such as incentive structures, validator set sizes, and election mechanisms.

Polkadot introduces a Nominated Proof-of-Stake (NPoS) system. Its design choices are rooted in first principles, with security, fair representation, user satisfaction, and efficiency as guiding goals. In NPoS, users may either become validator candidates or act as nominators. Nominators select trusted candidates and support them by backing their stake. Once per era, a validator committee is elected based on the preferences of the current set of nominators. The number of elected validators *k*, is currently in the hundreds and may scale into the thousands as the number of parachains grows.

Validators and nominators lock their tokens as collateral and receive staking rewards on a pro-rata basis. They may be slashed and lose their collateral if a supported validator engages in negligent or adversarial behavior. Nominators participate indirectly in the consensus protocol and have an economic incentive to monitor the evolving candidate set closely, helping ensure the election of only the most capable and trustworthy validators.

In the [overview page](1.%20Overview.md) you can learn about NPoS, and for an in-depth analysis you can read the [research paper](2.%20Paper.md). For more details on staking rewards, check out the [token economics research section](https://wiki.polkadot.com/learn/learn-dot/), and learn about slashing in [this section](Polkadot/security/slashing/amounts.md). For a broader understanding of the staking process, explore [Wiki pages](https://wiki.polkadot.network/docs/en/learn-staking). 

Unlike other projects, Polkadot maintains complete independence between validator selection and [governance](https://wiki.polkadot.network/docs/en/learn-governance). In particular, users' rights to participate in governance are never delegated.
