---
title: Non-monetary incentives for collective members
---

![](collective-members.jpeg)

Behavioral economics has demonstrated that non-monetary incentives can be powerful motivators, offering a viable alternative to financial rewards (see, e.g., [Frey & Gallus, 2015](https://www.bsfrey.ch/articles/C_600_2016.pdf)). This is especially true in environments where intrinsic motivation drives behavior. In such contexts, monetary incentives may even crowd out intrinsic motivation, ultimately reducing engagement ([Gneezy & Rustichini, 2000](https://academic.oup.com/qje/article-abstract/115/3/791/1828156)). 

Recent advances in technologies surrounding Non-fungible Tokens (NFTs) present a promising new layer of incentives for governance participation and collective engagement. NFTs, as a tool, can be effectively combined with insights from academic literature on gamification to encourage participation and reward good behavior. This can help address several inherent challenges in governance, particularly low participation.

### Problem statement

Governance is one of the most critical aspects for the future of decentralized systems, such as DAOs and other collectives. These systems rely on token holders to participate actively in order to enable efficient decision-making. However, turnout rates tend to be quite low, which creates the risk of governance exploits by a highly motivated minority. Several factors can help mitigate this risk, for example enhancing usability and user experience within the governance process. 

This write-up explores non-monetary incentives as a means to encourage more active engagement within a collective. The approach can be applied to layer0 governance as well as smaller collectives, such as DAOs.


### Goals

The goals is to design a mechanism that automatically applies selected gamification tools such as badges, achievements, and levels to collective members in order to:

* Promote the engagement and liveness of members.
* Leverage established techniques from the literature to improve the overall governance process. 
* Enable users to evaluate and compare members more efficiently.

Advancing in these areas would further strengthen the network's position within the blockchain ecosystem.

## Literature 

In recent years, gamification has received growing attention, so much that it has been called the "most notable technological developments for human
engagement" ([Majuri et al., 2018](https://trepo.tuni.fi/bitstream/handle/10024/104598/gamification_of_education_2018.pdf)). Gammification is used to enhance learning outcomes (e.g., [Denny, 2013](https://dl.acm.org/doi/abs/10.1145/2470654.2470763?casa_token=XsWtSZeFt-QAAAAA:MPWbtFfjzQZgWzyTI9hWROarJb1gJDWqDHNG4Fyozzvz3QIK-kMuMxfSwE26y9lKYUuZnV7aDZI)), model online communities (e.g., [Bista, 2012a](https://ieeexplore.ieee.org/abstract/document/6450959)), and promote sustainable behavior (e.g., [Berengueres et al., 2013](https://ieeexplore.ieee.org/abstract/document/6483512?casa_token=tmdUK7mtSSEAAAAA:ZxJnvYNAcuRaMHbwNqTJnahpbxal9xc9kHd6mY4lIahFhWn2Gmy32VDowMLVREQjwVIMhd9wcvY)). Gamification can serve as a "means of supporting user engagement and enhancing positive patterns in service use, such as increasing user activity, social interaction, or quality and productivity of actions" ([Hamari, Koivisto & Sarsa, 2014](https://ieeexplore.ieee.org/abstract/document/6758978?casa_token=F2o_LQE-CNgAAAAA:vA_xBEe0ltKmMPRmTfkyW78LThHP9hLKK06oj1gKpOeDfoCTG7l_p-KSVlcdhNpaErLjzrm8p90)). 

While a universally accepted definition is still lacking, gammification is best described as "a process of enhancing a service with affordances for gameful experiences in order to support user's [sic] overall value creation” ([Huotari & Hamari, 2012, p. 19](https://dl.acm.org/doi/abs/10.1145/2393132.2393137?casa_token=MU2yq2P4TOoAAAAA:Xuy9ZEzo2O7H-WCbqMheezkrodpab2DlFWkLjVt3jYExuP--vsjEROt4BKt5ZEbVou9rVnQSQBs)). In other words, applying gammification does not turn a service into a game, it rather enriches it with motivational elements popular in gaming, such as points, levels, badges, and leaderboards ([Deterding, 2012](https://dl.acm.org/doi/fullHtml/10.1145/2212877.2212883?casa_token=B9RD9ZPneIMAAAAA:34lrdGKwOUZyZu8fLobERuPLIBzNQxxwlgWLJnonn5Ws8Ya65aO_pdifhlHiSBwjDb0mWyFD0aM), [Hamari, Koivisto & Sarsa, 2014](https://ieeexplore.ieee.org/abstract/document/6758978?casa_token=F2o_LQE-CNgAAAAA:vA_xBEe0ltKmMPRmTfkyW78LThHP9hLKK06oj1gKpOeDfoCTG7l_p-KSVlcdhNpaErLjzrm8p90)). 
Zichermann & Linder (2010) argue that intrinsic motivation is unreliable and variable. Therefore, gamification can be used to craft extrinsic motivators that help internalize intrinsically motivated behavior. It is crucial to do this with non-economic incentives, as monetary rewards may crowd out intrinsic motivation ([Gneezy & Rustichini, 2000](https://academic.oup.com/qje/article-abstract/115/3/791/1828156)). 

One field where gamification has not yet been systematically applied is voting behavior, particularly governance participation. A notable exception is a large-scale experiment involving 61 million Facebook users, where researchers found that an *I voted* indication on users' status pages may have led to approximately 340,000 additional voters in the 2010 U.S. election ([Bond et al., 2012](https://www.nature.com/articles/nature11421) and [this article](https://www.nature.com/news/facebook-experiment-boosts-us-voter-turnout-1.11401)). The main driver was considered to be peer pressure among Facebook friends. While researchers did not explicitly link this intervention to gamification, it can be interpreted as such, and may have incentivize participation among a small group. 

A similar example is the well-known *I voted* badge used in U.S. elections, which has proven quite successful ([see](https://www.usvotefoundation.org/voter-reward-badge)). Voters enjoy displaying the badge and often motivate others to vote as well. Some business even offer perks to customers who show the badge.

 A review of 91 scientific studies on gamificaton in education revealed that 71% reported mainly positive effects, such as increased engagement and enjoyment, while 25% showed no significant effect, and only 3% reported negative outcomes ([Majuri et al., 2018](https://trepo.tuni.fi/bitstream/handle/10024/104598/gamification_of_education_2018.pdf)). While acknowledging the effectiveness is context-dependent, and despite the overwhelming majority of positive results, some studies do not report negative effects, highlighting important caveats. One source of negative impact is increased perceived competition among peers, which can demotivate certain users ([Hakulinen et al., 2013](https://ieeexplore.ieee.org/abstract/document/6542238)). Another common critique is the lack of a clear theoretical foundation, leading to diverse and inconsistent approaches across studies. 

The design process behind gamification elements can be further informed by research from related social science, particularly in countering psychological biases that affect decision-making in small committees, and in leveraging additionally motivational factors such as *loss-aversion* and the resulting *endowment effect*.

Literature has shown that small decision-making groups often suffer from *groupthink*, a bias in which the outcome of the decision process is far from optimal, as individuals do not freely express their opinions ([Janis, 1971](http://agcommtheory.pbworks.com/f/GroupThink.pdf)) or are influenced to act against their better judgement, whether consciously or unconsciously. This issue is particularly pronounced in groups comprised of members with differing levels of power and status. Major disasters have been attributed to *groupthink*, including the *Bay of Pigs Invasion* and the *Space Shuttle Challenger disaster* ([Janis, 1991](https://williamwolff.org/wp-content/uploads/2016/01/griffin-groupthink-challenger.pdf)). 

Subsequent analyses revealed that committe members often willfully ignored substantial evidence. This problem is closely tied to the pressure to conform to authority figures, as demonstrated by well-known psychological experiments such as those by [Milgram, 1963](https://www.demenzemedicinagenerale.net/pdf/MilgramOriginalWork.pdf) and [Asch, 1961](https://psycnet.apa.org/record/1952-00803-001). 

It is crucial to remain aware of these dynamics and mitigate them by distributing final decision-making power among key stake-holders. With this awareness, mechanisms can be implemented to further improve decision outcomes. For example, a study by [MacDougall & Baum (1997)](https://journals.sagepub.com/doi/abs/10.1177/104973239700700407) demonstrated that explicitly appointing a "devil's advocate" can enhance results by regularly challenging group consensus.

Studies in behavioral economics show that individual decision-making is influenced by *loss-aversion*. This phenomenon arises from a non-linear utility function, where the subjective evaluation of outcomes differs between gains and lossess relative to a reference point. Specifically, the disutility of a loss is greater than the utility gained from an equivalent gain ([Kahneman & Tversky, 1992](https://link.springer.com/article/10.1007/BF00122574)). One consequence of this is the *endowment effect* ([Kahneman, Knetsch & Thaler, 1990](https://www.journals.uchicago.edu/doi/abs/10.1086/261737)), which describes the tendency to value an item more simply because one possesses it. A practical implication for incentive system design is that users tend to exert greater effort to retain something when there is a possibility of losing it. 
 
 
In conclusion, carefully designing a gamified experience can enhance the overall governance process, leading to more active discussions, and, ideally, better decisions.


## Awarding mechanism (WIP)
In general, the most commonly used gamification elements include ([Hamari, Koivisto & Sarsa, 2014](https://ieeexplore.ieee.org/abstract/document/6758978?casa_token=F2o_LQE-CNgAAAAA:vA_xBEe0ltKmMPRmTfkyW78LThHP9hLKK06oj1gKpOeDfoCTG7l_p-KSVlcdhNpaErLjzrm8p90)):

* Points
* Badges (or trophies)
* Achievements
* Levels

Designing an automatic mechanism to award members NFTs based on their on-chain (and potentially off-chain) behavior is highly complex. On one hand, focusing solely on easily measurable outcomes, such as voting speed or the sheer number of propositions, can backfire and is prone to abuse. Moreover, assessing the quality of a vote through quantitative metrics alone is challenging. To address this, it is essential to observe the entire process and the eventual outcome of the election. 

On the other hand, incentivizing only positive election outcomes could lead members to become onverly conservative, proposing only safe, likely-to-win ideas while neglecting provocative but potentially beneficial proposals. The best strategy, therefore, is to design a mix of different NFTs, where the positive weighting of each individual NFTs is less pronounced, allowing room for a broader range of behaviors. 

In addition, the proposed NFTs should incorporate important key insights from social science research, as mentioned above. For example, some NFTs could include preventive measures against *Groupthink*, while others could be designed to leverage *Loss-Aversion*.

### Achievements (static)

Achievements are absolute milestones that, once reached, cannot be lost. Potential triggers include:

* Become a collective member of a certain age


### Badges (perishable)
Badges are generally perishable and resemble an achievement relative to a specific status or condition. In other words, once the relative status is lost, the badge is forfeited. This dynamic introduces an intriguing motivational factor known as the *endowment-effect* (see literature section), where individuals are more driven to retain something they already possess. 

Badges are well-suited to reflect situational states such as:

* Being the most backed member (if a hierarchy exists within the system)
* Being the oldest member
* Acting as the devil's advocate (frequently voting against the majority) 

### Levels (ranks)
Earning certain badges opens the possibility of implementing a level system that could essentially sum up all badges and achievements into one quantifiable metric.

### Actions
The following list, compiled by Raul Romanutti, highlights several common actions that members can perform, offering a solid basis of outcome variables to be integrated into an awarding mechanism. While highly context-specific, the list may serve as a useful reference for treasury expenditures and other proposals.

* Vote on a treasury proposal motion
* Vote on a runtime upgrade motion
* Vote on a referendum 
* Submit an external motion proposal
* Submit a preimage for a proposal 
* Close a motion after majority is reached
* Vote on a treasury proposal motion (submitted by community members)
* Endorse a tip proposal (submitted by community members)
* Open a tip for a community member
* Open a bounty proposal
* Vote on a bounty proposal
* Vote on a bounty curator nomination
* Propose a motion to unassign a bounty curator
* Serve as the curator of an active bounty
* Propose an external motion for a specific chain to use a common-good chain slot
* Vote on an external motion for a specific chain to use a common-good chain slot

## NFT Gallery
For NFTs to develop a motivating effect, they must be visually displayed and accessible through NFT galleries. Support from wallets and blockchain explorers is essential to achieve this. Given the popularity of NFTs, many projects are actively developing such solutions, from which further improvements are expected. 

As an additional benefit, governance-focused applications could present members, their achievements, badges, and levels in an organized an appealing way. This would make it easier and more enjoyable for outsiders, those not direcly involved in the decision-making process, to compare and engage with collective members. A possible outcome would be a substantial improvement in member engagement, leading to a more accurate representation of all stakeholders' opinions. In turn, this could further enhance the incentives that NFTs offer to members.

**For inquieries or questions please contact**: [Jonas Gehrlein](/team_members/Jonas.md)
