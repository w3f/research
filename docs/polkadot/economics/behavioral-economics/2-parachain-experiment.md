====================================================================

**Authors**: Jonas Gehrlein

**Last updated**: 07.12.2020

====================================================================

# Experimental Investigation of Parachain Auctions (WIP)

Why experiments?

The goal of this project is to get a better understanding of the bidding behavior of real humans in the upcoming parachain candle auctions on Kusama/Polkadot. To do so, we will conduct an experiment which simulate the basic mechanisms of the auction. The implementation is off-chain but mimics the key features of the blockchain (i.e., six second blocks, transaction costs). Insights from the experiment can be used to gain an understanding of the bidding behavior, learn how organize the UI and potentially improve the overall design before going live. Generally, the project has the following goals:
1) Elicit and analyze the bidding behavior of the players and compare it to some theoretical benchmarks.
2) Develop and test a suitable UI, which can be migrated and used in the live auctions.
3) Test variations made to the auction design, UI or automated bidding strategies (i.e., smart-contracts) and compare with benchmarks and baseline implementation.
4) Provide this tool as learning/practicing device for participants who plan to participate at one of the upcoming auctions.

## Motivation and Background in the Literature
The experiment at hand can be regarded as simultaneous multiple-item
auctions package-bidding auction similar to those used sell telecommunication frequencies worth billions (the 700 MHZ spectrum auction had a *minimum* price of 10 billion set by the Federal Communications Commission (FCC)). The FCC has "increasingly relied on laboratory experiments to evaluate the performance of alternative spectrum auctions"(Brunner et al. (2010)) and even discarded one of their initial designs, because it was experimentally proven to perform worse than an alternative format. The FCC stresses the importance of experiments in their [public notice](http://fjallfoss.fcc.gov/edocs_public/attachmatch/DA-07-3415A1.pdf). Generally, the spectrum auctions share important similarities to the parachain auctions. Specifically, the complementaries between time-slots and the package-building is captured nicely by experimental investigations of the experiments. Goeree et al. (2010) propose a pricing mechanism, which can be used in our case. Those auctions share the feature of complementaries between the goods and thereby the value of a package can be worth more than the sum of the individual goods. Additionally, the combinatorial problem of finding non-overlapping bids which maximize revenue is NP-Hard and therefore, we opt for package-bidding to reduce computational complexity.

## Experimental Design
In this experiment, we model a parachain auction by incorporating important planned features such as automated bidders (smart-contracts), the candle design (randomly determined termination time) and our specific pricing function. We assume to have two types of bidders (i.e., projects), which manifests in different endowments and valuations for leasing periods. The one type of bidder can be regarded as large scale projects, who are interested in getting multiple leasing periods as well as smaller projects, who are mostly interested in a single leasing period. The following sections illustrate various details of the design and the procedure.

### Bundles
There are 4 individual leasing periods available. Bidders are free to bid on any combination of those such that the resulting packages are of consecutive time. This leads to a total of 10 bundles. Those are:

| Period/Bundle 	| 1 	| 2 	| 3 	| 4 	| 5 	| 6 	| 7 	| 8 	| 9 	| 10 	|
|-	|-	|-	|-	|-	|-	|-	|-	|-	|-	|-	|
| 1 	| x 	| x 	| x 	| x 	|  	|  	|  	|  	|  	|  	|
| 2 	|  	| x 	| x 	| x 	| x 	| x 	| x 	|  	|  	|  	|
| 3 	|  	|  	| x 	| x 	|  	| x 	| x 	| x 	| x 	|  	|
| 4 	|  	|  	|  	| x 	|  	|  	| x 	|  	| x 	| x 	|

### Bidders
To model the different interests of bidders, we can allocate different valuations for the various bundles. It is reasonable to assume, that we'll have a bidders who aim for longer leasing periods (i.e., larger established projects) and bidders who want are financially more restricted and aim for shorter leasing periods. This situation is similar to the previously mentioned spectrum auctions. Brunner et al. [2010](https://www.aeaweb.org/articles?id=10.1257/mic.2.1.39) propose some model how to express this situation with valuations.

### Complementaries of bundles
Obtaining multiple leasing periods is assumed to create complementaries and can be modeled linearly. That means, if a bidder obtains K leasing periods, the value of each goes up by a factor $1 + \alpha(K-1)$. The factor $\alpha$ determines the size of the synergies.

### Pricing Rule
Given that we have certain bids, we can compute the individual slot prices and allocate the.

### Termination time(s)
The key feature of a candle auction is that the termination time is not known to the bidders. This is implemented in our protocol by basically having two different termination times. The first termination time, is the official end of the auction (known to every user). However, there is a second, much more meaningful termination time which is determines at what. ending time is determined by the 
- Distribution?


## Procedure
### Stage 1: Instructions
Participants receive information about the auction and the procedure of the experiment in with written information. In those instructions, the basics about the parachain auctions are explained and how their payoff will be determined. We will also ask a few comprehension question and make sure that players understand the game.

### Stage 1/2: Inspection of Smart-Contracts
Automated bidders (i.e., smart-contracts) are also involved in the auction. Those automated bidders have a pre-determined bidding function which can be observed by every player of the game. To reduce complication of reading code, we can summarize the bidding strategy in some easy-to-understand template which can be viewed at any time. This templates includes information about:
* The endowment of the smart-contract.
* The valuations for the various items.
* The bidding strategy.

### Stage 2: The Auction
At the beginning of the auction, each bidder learns their type (i.e., their endowment and their valuations for the respective bundles). The auction starts and every player is free to submit any bid for the bundles as long as a single bid does not exceed their endowment (note that the total sum of bids can exceed the endowment). The trading page illustrates important information such as the current allocation of bundles to the respective (anonymized) players and the respective prices (if the auction ends at that point).


### Stage 3: Feedback and Payoff
At the end of the official termination period, the participants receive information about the actual termination period and the respective winners of the bundles and the prices. Profits can be calculated and shown to each individual player.


## Recruitment & Payment
We can recruit participants from the KSM / DOT community. This has the advantage, that basic concepts of the blockchain are already known and that we can frame the experiment (i.e. that we talk from blocks, transactions etc. instead of abstracting it to the lowest possible level). Participants are incentivized with KSM / DOT, which makes it easy to process payments. In addition, it is possible to create a treasury proposal for the payment of players.

### Analysis: Outcome measures
Allocative efficiency $E(X)$ can be used to compare the results of the different variations of the experiments. This is defined by:

$$E(X) := \frac{\text{actual surplus}}{\text{optimal surplus}} \times 100\%$$

Additionally, we can measure the auctioneer's revenue R(X) by:

$$R(X) := \frac{\text{auctioneer's revenue}}{\text{optimal surplus}} \times 100\%$$

### Research Questions
- Vary Pricing Rule.
- Vary distribution of ending time.
- Vary Bidding strategies of smart-contracts.

## Implementation
The experiment can be implemented with oTree, which is a software to conduct online experiments and provide the necessary infrastructure to create sessions, distribute links to users and maintain a database of the experiment to later analyze. The current version of the experiment can be found [here](https://github.com/w3f/otree_blockchain_candle_auction). It combines python in the back-end with a flexible front-end implementation of HTML/CSS and Django.

### Overview

1. Frontend constructs bid transaction
2. Transaction is send to Backend
3. Backend update state
4. Frontend receives update

### Frontend
 
In the optimal case the user interface used for the final auction should be as close as possible to the one used in `polkadot.js`.

### UI

### Backend

The backend was modeled as close as possible to the current auction interface in the current Rust implementation.

### Potential Treatments
* Vary pricing rules (Originally proposed vs. HPB) and examine efficiency.
* Test different ending distributions and examine efficiency.
* Vary bidding-strategies of smart-contracts and examine responds from humans.
* To have a large impact in literature: compare our design to common methods like RAD, MPB and SMR.

### Adjusted Pricing Rule
To reduce computational complexity, we define packages ex-ante and do not allow for flexible package bidding. This means, we only allow to bid for time-slots which have continous operation time. Fortunately, this aligns with a reasonable assumption that the parachain only is only really operational without any breaks. We can apply a pricing rule from [Goeree & Holt (2010)](https://www.zora.uzh.ch/id/eprint/42542/1/2010_GoereeJ_iewwp436.pdf) which builds on a hierarchical representation of the packages. 
