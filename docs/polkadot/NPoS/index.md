# Nominated Proof-of-Stake

====================================================================

**Owners**: [Alfonso Cevallos](/team_members/alfonso.html)

====================================================================

Many blockchain projects launched in recent years substitute the highly inefficient Proof-of-Work (PoW) component of Nakamoto’s consensus protocol with Proof-of-Stake (PoS), in which validators participate in block production with a frequency proportional to their token holdings, as opposed to their computational power. While a pure PoS system allows any token holder to participate directly, most projects propose some level of centralized operation, whereby the number of validators with full participation rights is limited. Arguments for this limited validator set design choice are that:

- The increase in operational costs and communication complexity eventually outmatches the increase in decentralization benefits as the number of validators grows. 
- While many token holders may want to contribute in maintaining the system, the number of candidates with the required knowledge and equipment to ensure a high quality of service is limited.
- It is typically observed in networks (both PoW- and PoS-based) with a large number of validators that the latter tend to form pools anyway, in order to decrease the variance of their revenue and profit from economies of scale.

Therefore, rather than let pools be formed off-chain, it is more convenient for the system to formalize and facilitate pool formation on-chain, and allow users to vote with their stake to elect validators that represent them and act on their behalf. Networks following this approach include Polkadot, Cardano, EOS, Tezos, and Cosmos, among many others. While similar in spirit, the approaches in these networks vary in terms of design choices such as the incentive structure, the number of validators elected, and the election rule used to select them. 

Polkadot introduces a variant of PoS called Nominated Proof-of-Stake, with design choices based on first principles and having security, fair representation and satisfaction of users, and efficiency as driving goals. In NPoS, users are free to become validator candidates, or become nominators. Nominators approve of candidates that they trust and back them with their tokens, and once per era a committee of validators is elected according to the current nominators' preferences. In Polkadot, the number k of validators elected is in the order of hundreds, and may be thousands in the future as the number of parachains increases.

Both validators and nominators lock their tokens as collateral and receive staking rewards on a pro-rata basis, but may also be slashed and lose their collateral in case a backed validator shows negligent or adversarial behavior. Nominators thus participate indirectly in the consensus protocol with an economic incentive to pay close attention to the evolving set of candidates and make sure that only the most capable and trustworthy among them get elected.

Visit our [overview page](1. Overview.md) for a first introduction to NPoS, and our [research paper](2. Paper.md) for an in-depth analysis. We also encourage the reader to visit the [token economics research section](../overview/2-token-economics.md) for further information about staking rewards, [the section on slashing](../slashing/amounts.md), and our [Wiki pages](https://wiki.polkadot.network/docs/en/learn-staking) for more hands-on information about the staking process. We also remark that, unlike other projects, Polkadot keeps validator selection completely independent from [governance](https://wiki.polkadot.network/docs/en/learn-governance), and in particular the user's right to participate in governance is never delegated.