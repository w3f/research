---
title: Token Economics
---

import DocCardList from '@theme/DocCardList';


![](polkadottoken.png)


Polkadot is a proof-of-stake–based platform in which a set of validators, who have staked DOTs[^1], produce blocks and reach consensus. Polkadot validators are rewarded roughly in proportion to their staked amount, unless they deviate from the protocol, in which case a portion of their DOTs is slashed.

On this platform, the set of nodes elected as validators changes constantly in each era, approximately once a day, although their total number remains limited. However, any number of DOT holders can participate indirectly in the decision-making processes as *nominators*, under a system known as *nominated proof-of-stake*. A nominator selects validator candidates they trust and stakes DOTs to support their nomination. If one or more of their nominated candidates are elected as validators in an era, the nominator shares with them any economic reward or penalty, proportional to their stake. 

Being a nominator is a way to invest one's DOTs while contributing to the security of the system. The greater the total amount of DOTs staked by nominators and validators, the higher the system’s security—since an adversary would require significantly more stake, or nominators' trust, to succeed in getting nodes elected as validators.

We therefore aim for a considerable percentage of the total DOT supply to be staked by validators and nominators. Another significant portion of the DOT supply will be locked as deposits by commercial blockchains that secure parachain slots. 

In these sections, we pay attention to three key topics. In **NPoS payment and inflation**, we outline how well-behaved validators and nominators are rewarded under Polkadot’s nominated proof-of-stake system. In **transaction fees**, we analyze optimal fee structures on the relay chain to cover operational costs, mitigate harmful behavior, and manage periods of high activity or delayed transaction inclusion. Finally, in the **treasury** section, we discuss how and when to raise DOTs to support ongoing network maintenance. The closing paragraph provides links to further resources related to the Polkadot protocol.

[^1]: DOTs are Polkadot's native token and their main functions are: 1) Economics: Polkadot will mint or burn DOTs in order to reward the nodes that run the consensus protocol, to fund the treasury, to control the inflation rate, etc. 2) Slashing: DOTs also play a role in the slashing protocols designed to desincentivize attacks or adversarial behaviors. 3) Governance: DOTs are also used as voting power, to let DOT holders express their opinion in governance decisions via referenda. 4) Parachain allocation: Finally, DOTs are used to decide which projects are allocated a parachain slot, via auctions and deposits. In this section we have focused on the first use, while each of the other three uses is analyzed in a separate section.


<DocCardList />
