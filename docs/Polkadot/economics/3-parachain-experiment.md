---
title: Experimental Investigation of Parachain Auctions
---

**Authors**: [Jonas Gehrlein](/team_members/Jonas.md), Samuel Häfner

**Last updated**: 16.08.2021

## Overview
The goal of this project is to experimentally test the combinatorial candle auction as it is used in the Polkadot and Kusama protocol. In particular, we want to compare its outcome with those of more traditional, dynamic combinatorial auction formats employed today. 

What sets the candle auction apart from other dynamic auctions is that it has a random ending time. Such a closing-rule is important for auctions run on blockchains, because it mitigates several practical problems that other, more common auction formats suffer from (cf. Häfner & Stewart, 2021, for an analysis of the sinlge-unit case). 

The combinatorial candle auction has never been studied theoretically and empirically. Therefore, this project fills a gap in the literature. We hypothesize that the candle format is at par with, or even outperforms, dynamic combinatorial auctions that use specfic activity rules. Activity rules specify the feasible bids and close the auction when no more bids are entered in the system. Thus, they put pressure on the bidders to bid seriously early on. We expect a similar effect from the random ending time. In particular, we expect that the pressure to act induces - akin to activity rules - more efficient outcomes than in an auction with a simple hard-closing rule (i.e., a fixed ending time).

We will conduct an experimental investigation with a design that mimics the basic mechanism of the Polkadot parachain auction. In particular, we conduct the experiment in a context where bidders can freely communicate and share their non-binding strategies before the auction. The implementation is off-chain and follows standard experimental economics procedures. Insights from the experiment can be used to gain an understanding of the bidding behavior and to compare efficiency across formats. 


## Dynamic Combinatorial Auctions

In this section, we first discuss how combinatorial auctions are currently used. Second, we describe the combinatorial candle auction as it used on Polkadot, explain why we use this format, and what we expect about its performance vis-a-vis more standard combinatorial auction formats. 

### Currently used Combinatorial Auctions
Historically, combinatorial auctions have emerged as successors of multi-unit auctions. Combinatorial auctions solve the so-called exposure problem from which multi-unit auctions suffer in the presence of complementarities (Porter and Smith, 2006; Cramton, 2013). In a multi-unit auction, the bidders compete for every unit separately. As a consequence, bidders aiming (and bidding) for a certain combination of items might suddenly find themselves in a situation of obtaining only a subset thereof, which has substantially lower value to them than the whole package. Combinatorial auctions allow bidders to place bids on packages directly and thus avoid this problem. That is, if you bid on a package then you either get the whole package, or nothing.

Today, combinatorial auctions are employed in many contexts. The most well known applications of combinatorial auctions are radio spectrum auctions (Porter and Smith, 2006; Cramton, 2013). Other applications include electricity (Meeus et al., 2009), bus routes, and industrial procurement (cf. Cramton et al., 2006, for an overview). 

Many combinatorial auctions are dynamic. There are two distinct formats:

1. *Ascending format*: As long as the auction is open, bidders can submit increasing bids for the different packages (experimentally studied Bichler et al. 2017). 
2. *Clock format*: The auctioneer raises the prices on the individual items or packages and in every round, the bidders have to submit their demand for the different packages. In some formats, bidders can submit last bids in one additional round of simultaneous bidding once the clock phase is over (initially suggested by Ausubel et al. 2006; further discussed in Cramton, 2013).

For example, in the case of US radio spectrum auctions, simple, ascending multi-unit auctions were used first. Then, in 2006 and 2008 among others, the FCC allowed bidding on pre-defined packages of licences in an ascending format (Porter and Smith, 2006; Cramton, 2013). The switch to clock auctions occurred later on (Levin and Skrzypacz, 2016).

An important design feature of any dynamic combinatorial auction is its so-called activity rule. The primary role of the activity rules is to encourage serious bidding from the start and to prevent sniping or jump-bidding. 

During the auction phase, the activity rule determines what kind of bids are feasible for any given bidder. In the case of the ascending bid format, the rule usually defines a minimum and a maximum increment that a new bid on a given item or package can have over an older bid (Scheffel et al., 2012). In the clock auction, the activity rule may prevent bidders from jumping onto a given package that they have ignored in earlier rounds; i.e., bidders may reduce demand but not increase it (Levin and Skrzypacz, 2016). In both the ascending auction and the clock auction, the rule sometimes also restricts bidders to bid on packages that are weakly smaller than the ones previously bid on (Cramton, 2013). 

Second, the activity rule determines when the auctions end based on all previously entered bids. In the ascending auction, the activity rule closes the auction when no new bids are entered in a round (Scheffel et al., 2012). In the clock auction, the prices on the individual packages are (simultaneously) raised until there is no excess demand for a package and the auction concludes when there is no excess demand for any of the packages (Bichler et al., 2013).



### The Combinatorial Candle Auction
In the combinatorial candle auction employed in Polkadot, bidders can submit bids in a pre-defined time window. Bids have to be increasinge but they are otherwise not restricted by an activitiy rule. After the window closes, the ending time is retroactively determined in a random fashion. 

Candle auctions are believed to have originated in medieval Europe and they derive their name from the particular way they were conducted. The auctioneer lights a candle in sight of all the bidders and accepts bids until the candle goes out. The highest bidder at the time the candle goes out is declared the winner (cf., e.g., Hobson, 1971). Earliest accounts of this kind of auction date back to 14th century France where they were used to sell chattels and leases. In England, furs were sold in candle auction up to the 18th century (cf. Füllbrunn and Sadrieh, 2012, for more details and references). 

Candle auctions have become rare today. A possible reason is that generic randomness is technically hard to achieve and that the commitment to a random device hard to verify. Recent cryptographic advances allow to circumvent these problems and put the candle auction back on the scene. For example, For example, Google held a patent on a dynamic auction with a random ending time that expired in 2020 (Patent No. US6665649B1). 

The main reason why the Polkadot protocol employs a candle mechnism is that it mitigates some of the problems associated with front-running in auctions. Front-running is a major problem of blockchain implementations of auctions. Because block production only happens at discrete intervals but all upcoming transactions are stored in the chain's mempool, tech-savvy bidders can in principle inspect and react to upcoming bids. The general worry is that this reduces the overall incentives to bid, thus reducing revenue and possibly efficiency. As argued in Häfner & Stewart (2021) cryptographic solutions to the problem -- though they exist -- are not feasible for the automated setting of Polkadot, primarily because we expect smart contracts among bidders.


To the best of our knowledge, Füllbrunn and Sadrieh (2012) is the only experimental paper to also study a candle format. Other than in our planned experiment, they consider a single-unit auction with a second-price payment rule. In the second price auction, it is a weakly dominant strategy to bid the true value whenever there is a positive probability that the current round will be the terminal round. The experimental evidence largely confirms such a prediction. Other than in the first-price auction, where equilibrium bidding depends on the termination probabilities, expected revenue is independent of the termination probabilities.

## Experimental Design

We want to look at an ascending combinatorial auction with discrete rounds $t$ in which bids can be placed. There will be three bidders in every auction. After every round, all new bids are revealed. A round lasts for $6$ seconds.

The set of items is $X = \{1,2\}$ giving us three packages $\{\{1\},\{2\},\{1,2\}\}$ on which bidders can submit bids. A bid $b=(p,x)$ consists of a price $p$ and any package $x \subseteq X$. Prices have to be increasing and must lie in a finite (fine) grid. The winning bids are selected to maximize total payment. The payment rule is pay-as-bid; i.e., winning bids have to be paid. 

### The Three Ending Formats
We want to compare three ending formats: a candle format, a hard-closing rule, and an activity rule.

|                | Communication |
|----------------|------------------|
| Candle Auction | CA            |
| Hard-Close     | HC            |
| Activity Rule  | AR            |


**Candle Format** In the candle auction, bidders can freely submit increasing bids during the auction phase, and the auction is terminated at random. In the specification that we consider, the ending time is determined retroactively; i.e, bids on packages are accepted in a predefined number of rounds, $\bar T$, after which the auctioneer announces the ending time $T \in \{1,...,\bar T\}$. The ending time $T$ is random, the probability that the auction ends in round $t$ is publicly known and given by $q_t \in (0,1)$, where $\sum_{t=1}^{\bar T}q_t=1$.

**Hard-Close Rule** In the hard-close auction, bidders can also freely submit increasing bids yet the auction ends at a fixed end time, $\bar T$. 

**Activity Rule** In the activity rule format, the ending time is determined by the activity rule. Specifically, bids have to be increasing and if no new bid is entered for $\tau$ rounds, then the auction concludes. For the experiment, we propose $\tau=5$ (corresponding to $30$ seconds).

### Communication 
Communication is ubiquitous in the blockchain setting. The different bidders are teams that work on similar technical problems, share communication channels, post on social media, etc. 

Consequently, we will allow our experimental subjects to communicate in a chat before each auction and discuss non-binding strategies. Specifically, the bidders will have both an open chat as well as closed bilateral chat channels available. The chats will be open prior to the auction start and close thereafter.

### Valuations
In every auction, three bidders will be active. Bidders can have one of two roles that are commonly known when entering the auction: (1) global bidder, (2) local bidder. There will be one global bidder and two local bidders in every auction.

The global bidder has a positive valuation only for the grand package, $\{1,2\}$. The local bidders hold valuations for the individual packages that add up in case they win the grand package. Specifically, we will assume

![](https://i.imgur.com/feIk9Hu.png)

In words, the global bidder draws a valuation $v$ for the package $\{1,2\}$ and always holds a valuation of zero for the packages $\{1\}$ and $\{2\}$. On the other hand, local bidder $i = 1,2$ draws a valuation $v_i$ for $\{1\}$, implying that she values item $\{2\}$ at $80-v_i$ and package $\{1,2\}$ at $80$.

Under this value model it is efficient for the global bidder to obtain the grand package whenever $v \geq \max \{80-v_1+v_2,80-v_2+v_1\}$ and for the two local bidders to each receive one of the items otherwise. In order to win against the global bidder, though, the local bidders must coordinate their bids accordingly.


### Hypotheses
We will be interested in the following outcome variables:

* Efficiency: In what fraction of the auctions does the resulting allocation correspond to the first-best allocation?
* Revenue: Equals to the total bids paid. This also allows us to compute average shading ratios.
* Bidding dynamic: How fast do bids increase? Do we see sniping?

In general, the random ending time puts pressure to submit serious bids early on in the auction. We expect this to have two effects vis-a-vis a hard-closing rule (under which the auction ends at a fixed end date) that are similar to what activity and feedback rules should achieve. That is, we conjecture that a candle format can replace these rules to some extent. 

* Hypothesis I: Early bids in the candle auction are higher than under the activity rule; and they are higher under the activity rule than they are under the hard-close rule.
* Hypothesis II: The candle format and the hard-close rule fare better than the hard-close rule in terms of revenue and efficiency.
* Hyptothesis III: The candle format and the hard-close rule fare similarly in terms of revenue and efficiency. Perhaps: Efficiency is slightly worse in the candle auction while revenue is slightly better.

### Procedure

#### Stage 1: Instructions
At the beginning of the experiment, participants are randomly allocated to one of the three different auction formats and receive information about specific rules of the game. To ensure that subjects understand the game, we will also ask a few comprehension question.

#### Stage 2: The Auctions
Before each auction, all bidders learn their type and their private valuations for the individual packages. Each market consists of one global and two local bidders. Their roles remain fixed throughout the experiment but new values are drawn each new auction. To better compare the results across the treatments, we can fix the random draws (i.e., the seed) for each auction across treatments. Every subject participates at n=X auctions while we make sure that we re-shuffle subjects into markets to match a (near-) perfect stranger design. Then, the communication phase starts where all participants of an auction can discuss openly in a chat-format for 45 seconds. After this, the auction starts and subjects are free to submit bids. 

The trading page features two tables:

1. (Table 1) Current winning bids: This shows all current bids per package.
  
2. (Table 2) Winning Allocation: This shows how the packages are currently allocated to bidders based on the current winning bids.

Especially table 2 is considered to significant help with this complex auction design. 

#### Stage 3: Feedback and Payoff
After the end of the auction (depending on the treatment), participants receive feedback about the final winning bids and allocation of packages. In addition, subjects in the candle auction format are informed about the realization of $T$ and the respective snapshot of winning bids to that time. Profits are calculated and shown to the subjects. Afterwards, the next auction (if there are any) is started and new valuations are drawn for each subject.


### Outcome variables
* Success of coordination (given the realized values, were the local bidders able to form a coalition?)
* Efficiency (Did the packages go to those with the highest valuation? Did they coordinate on the right allocation)
* Bidding dynamic (how quickly converges the auction)
* Revenue

### Implementation
The experiment will be implemented with [oTree](https://www.sciencedirect.com/science/article/pii/S2214635016000101), which is a software to conduct online experiments and provide the necessary infrastructure to create sessions, distribute links to users and maintain a database of behavioral data. It combines python in the back-end with a flexible front-end implementation of HTML/CSS and Django. 

## Literature
Ausubel, L. M., Cramton, P., & Milgrom, P. (2006). The clock-proxy auction: A practical combinatorial auction design. Combinatorial Auctions, 120-140.

Bichler, M., Hao, Z., & Adomavicius, G. (2017). Coalition-based pricing in ascending combinatorial auctions. Information Systems Research, 28(1), 159-179.

Cramton, P. (2013). Spectrum auction design. Review of Industrial Organization, 42(2), 161-190.

Cramton, P., Shoham, Y., & Steinberg, R. (2006). Introduction to combinatorial auctions. Combinatorial auctions, 1-14.

Füllbrunn, S. and A. Sadrieh (2012): \Sudden Termination Auctions|An Experimental Study," Journal of Economics & Management Strategy, 21, 519-540.

Häfner, S., & Stewart, A. (2021). Blockchains, Front-Running, and Candle Auctions. Working Paper, [SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3846363).

Hobson, A. (1971): A Sale by Candle in 1608," The Library, 5, 215-233.

Levin, J., & Skrzypacz, A. (2016). Properties of the combinatorial clock auction. American Economic Review, 106(9), 2528-51.

Meeus, Leonardo, Karolien Verhaegen, and Ronnie Belmans. “Block order restrictions in combinatorial electric energy auctions.” European Journal of Operational Research 196, No. 3 (2009): 1202-1206.

Porter, David, and Vernon Smith. “FCC license auction design: A 12-year experiment.” Journal of Law, Economics & Policy 3 (2006): 63.

Scheffel, T., Ziegler, G., & Bichler, M. (2012). On the impact of package selection in combinatorial auctions: an experimental study in the context of spectrum auction design. Experimental Economics, 15(4), 667-692.
