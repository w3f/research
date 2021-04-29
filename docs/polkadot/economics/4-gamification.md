====================================================================

**Authors**: Jonas Gehrlein

**Last updated**: 22.04.2021

====================================================================

# Non-monetary incentives for council members

## Overview 

Behavioral economics has proven that non-monetary incentives are viable motivators and resemble an alternative to incentives created by money (see, e.g., [Frey & Gallus, 2015](https://www.bsfrey.ch/articles/C_600_2016.pdf)). This is especially true for environments where behavior is mainly driven by intrinsic motivation. In those situations, monetary incentives can even crowd-out the intrinsic behavior leading to less motivation ([Gneezy & Rustichini, 2000](https://academic.oup.com/qje/article-abstract/115/3/791/1828156)). The current advances in technologies surrounding Non-fungible Tokens (NFTs) can be utilized as an additional incentive layer for council member's engagement and participation. NFTs as tool can be perfectly combined with insights from the academic literature about the concept of "gamification" to foster engagement and reward good behavior.

This can help improve on a few issues the network has today: Namely governance participation is low and staking behavior is not optimal.

### Problem statement

Governance is one of the most important aspects of the Polkadot ecosystem and relies on active participation both of the token holders and the elected council. However, turnout-rates of referenda are mostly below 5%, reaching super low rates of below 1% in some cases. To improve on that, the lottery pallet proposed for Kusama introduces monetary incentives to increase voting turnouts. 

In comparison to that, council members are expected to be less responsive to monetary incentives and might be better motivated with non-economic incentives. The proposed system is aimed mainly to improve on council member participation. This can easily be extended in the future for all token holders to incentivize good behavior (with regard to staking, and governance).

### Goals

The goals is to design a mechanism which automatically applies certain tools from gamification (e.g., badges, achievements, levels) to council members to...

* ... promote the engagement and liveness of council members.
* ... use established techniques from the literature to improve on the whole council governance process. 
* ... make it easier for users to evaluate and compare council members.

Improving on all those domains would further strengthen the position of the network in the blockchain ecosystem.

## Literature 

Gamification received increasing attention in the recent years and was even called the "most notable technological developments for human
engagement" ([Majuri et al., 2018](https://trepo.tuni.fi/bitstream/handle/10024/104598/gamification_of_education_2018.pdf)). It is used to enhance learning outcomes (e.g., [Denny, 2013](https://dl.acm.org/doi/abs/10.1145/2470654.2470763?casa_token=XsWtSZeFt-QAAAAA:MPWbtFfjzQZgWzyTI9hWROarJb1gJDWqDHNG4Fyozzvz3QIK-kMuMxfSwE26y9lKYUuZnV7aDZI)), model online communities (e.g., [Bista, 2012a](https://ieeexplore.ieee.org/abstract/document/6450959)) and improve sustainable behavior (e.g., [Berengueres et al., 2013](https://ieeexplore.ieee.org/abstract/document/6483512?casa_token=tmdUK7mtSSEAAAAA:ZxJnvYNAcuRaMHbwNqTJnahpbxal9xc9kHd6mY4lIahFhWn2Gmy32VDowMLVREQjwVIMhd9wcvY)). Gamification can be used as "means of supporting user engagement and enhancing positive patterns in service use, such as increasing user activity, social interaction, or quality and productivity of actions" ([Hamari, Koivisto & Sarsa, 2014](https://ieeexplore.ieee.org/abstract/document/6758978?casa_token=F2o_LQE-CNgAAAAA:vA_xBEe0ltKmMPRmTfkyW78LThHP9hLKK06oj1gKpOeDfoCTG7l_p-KSVlcdhNpaErLjzrm8p90)). While there is no agreed-upon definition, it can be best described as "a process of enhancing a service with affordances for gameful experiences in order to support user's [sic] overall value creation” ([Huotari & Hamari, 2012, p. 19](https://dl.acm.org/doi/abs/10.1145/2393132.2393137?casa_token=MU2yq2P4TOoAAAAA:Xuy9ZEzo2O7H-WCbqMheezkrodpab2DlFWkLjVt3jYExuP--vsjEROt4BKt5ZEbVou9rVnQSQBs)). That means, applying this concept does change the underlying service into a game but rather enriches it with motivational affordances popular in gaming (points, levels, badges, leaderboards) ([Deterding, 2012](https://dl.acm.org/doi/fullHtml/10.1145/2212877.2212883?casa_token=B9RD9ZPneIMAAAAA:34lrdGKwOUZyZu8fLobERuPLIBzNQxxwlgWLJnonn5Ws8Ya65aO_pdifhlHiSBwjDb0mWyFD0aM), [Hamari, Koivisto & Sarsa, 2014](https://ieeexplore.ieee.org/abstract/document/6758978?casa_token=F2o_LQE-CNgAAAAA:vA_xBEe0ltKmMPRmTfkyW78LThHP9hLKK06oj1gKpOeDfoCTG7l_p-KSVlcdhNpaErLjzrm8p90)). 
Zichermann & Linder (2010) argue that that intrinsic motivation is unreliable and variable. Thereby, gamification can craft extrinsic motivators to internalize the intrinsically motivated behavior. It is crucial that this is done with non-economic incentives, because monetary incentives could lead to the crowding-out of intrinsic motivation ([Gneezy & Rustichini, 2000](https://academic.oup.com/qje/article-abstract/115/3/791/1828156)). A field where gamification has not yet been (explicitly) applied systematically is voting behavior (i.e., governance participation). One notable exception is a large-scale experiment with 61 million users of facebook, where researchers found that an *I voted* indication on their status page, could have been responsible for about 340'000 additional voters in the 2010 election ([Bond et al., 2012](https://www.nature.com/articles/nature11421) and [this article](https://www.nature.com/news/facebook-experiment-boosts-us-voter-turnout-1.11401)). The main driver here is considered to be peer-pressure elicited on facebook friends. While the researchers did not explicitly link this intervention with gamification, it could be perceived as such and might also work to incentivize participation of a small group. A similar application is the famous *I voted* badge in US elections, which has proven to be successful ([see](https://www.usvotefoundation.org/voter-reward-badge)). Voters like to show off badge and motivate others to go as well (some shops even offer perks for customers having that badge).

 A review on 91 scientific studies reveals that gamification provides overall positive effects in 71% of cases, 25% of cases no effect and only in 3% of studies were negative results reported ([Majuri et al., 2018](https://trepo.tuni.fi/bitstream/handle/10024/104598/gamification_of_education_2018.pdf)). such as increased engagement and enjoyment, while awcknowledging that the effectiveness is context-dependent. Despite the overwhelming majority of positive results, some studies indicate negative effects of gamification and suggest that there are some caveats. One source of negative effects are higher perceived competition of the interaction with peers, which could demotivate some users ([Hakulinen et al., 2013](https://ieeexplore.ieee.org/abstract/document/6542238)). Another reason for critique is the lack of clear theoretical foundation and the resulting diverse approach to the questions. 

The design process of the gamification elements can be further influenced by insights from related social science research. Namely how to counter some psychological biases affecting decision making in small committees as well as leveraging additionally motivational factors generated by *loss-aversion* and the resulting *endowment effect*.

Literature has shown, that small decision making groups tend to suffer from *group think*. This bias describes the situation, where the outcome from the decision process is far from optimal, because the individuals of the group do not speak their opinions freely ([Janis, 1971](http://agcommtheory.pbworks.com/f/GroupThink.pdf)) or are influenced in a way that they act against their best knowledge (consciously or unconsciously). This issue arises especially in groups comprised of members with different power and status. Major disasters have been accounted to *group think*, such as the *Bay of Pigs Invasion* and the *Space Shuttle Challenger disaster* ([Janis, 1991](https://williamwolff.org/wp-content/uploads/2016/01/griffin-groupthink-challenger.pdf)). In later analyses it was found that there were plenty of evidence available, which had been willingful neglected by committee members. This problem is also related to the pressure to behave conform with authority figures, as illustrated by famous psychological experiments (e.g., [Milgram, 1963](https://www.demenzemedicinagenerale.net/pdf/MilgramOriginalWork.pdf), [Asch, 1961](https://psycnet.apa.org/record/1952-00803-001)). Fortunately, the current governance process already mitigates that problem by dividing the final decision between the council and all token holders. However, knowing about this issue, we can implement mechanisms to further improve the outcome of council decision making. A study by [MacDougall & Baum (1997)](https://journals.sagepub.com/doi/abs/10.1177/104973239700700407) has shown that explicitly announcing a "devil's advocate" can improve the outcome by challenging the consensus frequently.

Studies in behavioral economics further show that individual decision making is influenced by *loss-aversion*. This results from a non-linear utility function with different shapes in the gain and loss domain of a subjective evaluation of an outcome relative to some reference point. Specifically, the absolute dis-utility of a loss is higher than the gain in utility of a corresponding gain ([Kahneman & Tversky, 1992](https://link.springer.com/article/10.1007/BF00122574)). A resulting effect of that is the *endowment effect* ([Kahneman, Knetsch & Thaler, 1990](https://www.journals.uchicago.edu/doi/abs/10.1086/261737)), which describes the situation where a good is valued much more only because of the fact of possessing it. A practical implication for design of incentive systems is that users are exerting higher effort to keep something once there is the option to lose it again. 
 
 
In conclusion, a carefully designing gamified experience can improve the overall governance process and result in more active discussions, and hopefully better decisions.


## Awarding mechanism (WIP)
In general, the most commonly used gamification elements are ([Hamari, Koivisto & Sarsa, 2014](https://ieeexplore.ieee.org/abstract/document/6758978?casa_token=F2o_LQE-CNgAAAAA:vA_xBEe0ltKmMPRmTfkyW78LThHP9hLKK06oj1gKpOeDfoCTG7l_p-KSVlcdhNpaErLjzrm8p90)):

* Points
* Badges (Trophies)
* Achievements
* Levels

A very complex task is to design an automatic mechanism to award council members NFTs based on their on-chain (and potentially off-chain) behavior. On the one hand, focusing only on easily measurable outcome levels of participation (e.g., speed of voting, pure quantity of propositions) can easily backfire and are prone to be abused. In addition, it is hard to deduce the quality of a vote by those quantitative measurements. To mitigate this, it is important to observe the whole process and the later outcome of the election. 

On the other hand, only incentivizing positive election outcomes could make council members too conservative, only proposing winners, neglecting provocative but potentially beneficial proposals. The best strategy is to come up with a mix of different NFTs where the positive weights of the individual NFTs are less severe and therefore leave enough space for all behavior. 

In addition, the proposed NFTs should also incorporate important insights from social science research (as mentioned above e.g., to incorporate preventive measures against *Groupthink* or design some NFTs to leverage *Loss-Aversion*).

### Achievements (static)

Achievements are absolute steps to be reached and cannot be lost, once obtained. Potential triggers could be:

* Become a council member


### Badges (perishable)
Generally, Badges are perishable and resemble an achievement relative to something. This means, once the relative status is lost, so is the badge. This is a very interesting concept as it incorporates the motivating factor of the *endowment-effect* (see literature section), where individuals exert higher motivation to hold on to the badge.

Those are good to include states of the situation such as:

* Be the most backed council member
* Be the oldest council member
* The devil's advocate (vote against the majority of other council members) 

### Levels (ranks)
Gaining certain badges could also mean we can implement some level system which could essentially sum up all the badges and achievements into one quantifiable metric.

### Council actions
The following list, composed by Raul Romanutti, illustrates several frequent actions council members can perform and build a good basis of outcome variables to be entwined in an awarding mechanism. 

* Vote on a treasury proposal motion
* Vote on a runtime upgrade motion
* Vote on referendum 
* Submit an external motion proposal
* Submit a regular motion to Council
* Submit an external motion to Council (we can have a lot of granularity here)
* Submit a preimage for a proposal 
* Close a motion after majority is reached
* Submit a runtime upgrade motion to Council (external motion)
* Vote on a treasury proposal motion (proposed by community members) - how do we judge rejections here?
* Vote on an identity registrar proposal (proposed by community members)
* Endorse a tip proposal (proposed by community members or councillors)
* Open a tip to a community member
* Propose a Technical Committee nomination (proposed by councillors)
* Vote on a Technical Committee nomination
* Open a bounty proposal
* Vote on a bounty proposal
* Vote on a Bounty curator nomination (proposed by councillors)
* Open a motion to unassign a bounty curator
* Become the curator of an active bounty
* Propose an external motion for a specific chain to use a common-good chain slot
* Vote on an external motion for a specific chain to use a common-good chain slot

## NFT Gallery
A prerequisite for NFTs to develop their motivating effect, it is necessary to visually display them and make them viewable in NFT galleries. This requires the support of wallets and explorers. Due to the popularity of NFTs, many of projects are currently working on those solutions and it is expected that solutions will further improve.

As an additional benefit, governance focused applications could orderly display the council members, their achievements / badges and levels, which can make it also much more easy and enjoyable for nominators to compare and engage with the council members. This could substantially improve the turnout rates in council member elections, and results are more precise in representing the opinion of all stakeholders. This, in turn, would further increase the incentives exerted by the NFTs on the council members.

