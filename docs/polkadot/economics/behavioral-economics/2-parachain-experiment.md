====================================================================

**Authors**: Jonas Gehrlein

**Last updated**: 14.01.2021

====================================================================

# Experimental Investigation of Parachain Auctions

# Introduction

## Goals
The goal of this project is to gain some concept of the expected bidding behavior of participants in the upcoming [parachain candle auctions](../2-parachain-allocation.md) on Kusama/Polkadot. Currently, the planned format can be described as a multi-object first-price candle auction, which in that form has never been analyzed theoretically or empirically in the literature.

We will conduct an experimental investigation, with a design which models the basic mechanisms of the auction. The implementation is off-chain and follows standard experimental economics procedures, but mimics the key features of the blockchain (i.e., six second blocks, (potentially) transaction costs). Insights from the experiment can be used to gain an understanding of the bidding behavior, learn how organize the UI and potentially improve the overall design before going live. Generally, the project has the following goals:

1) Elicit and analyze the bidding behavior of the players and compare it to some theoretical benchmarks.
   
2) Develop and test a suitable UI, which can be migrated and used in the live auctions.
   
3) Test crucial variations to the baseline design and observe the influence on key metrics.
   
4) Provide this tool as learning/practicing device for participants who plan to participate at one of the upcoming auctions.

## Why an experiment?
* Generally, due to its complexity, theoretical predictions for a multi-object first-price candle auction are missing.
* The literature has shown that first-price auctions can lead to inefficiencies and low revenues.
* We can gather real behavioral data in a controlled environment.
* We can make informed decisions which design elements to change (or leave) for the upcoming live implementation.


## Motivation and Background in the Literature
Experiments can be used to give recommended course of action for real-world applications. One example is the 700 MHZ spectrum auction orchestrated by the Federal Communications Commission (FCC)). The FCC has "increasingly relied on laboratory experiments to evaluate the performance of alternative spectrum auctions" ([Brunner et al. (2010)](https://www.aeaweb.org/articles?id=10.1257/mic.2.1.39)) and even discarded one of their initial designs, because it was experimentally proven to perform worse than an alternative format. The FCC stresses the importance of experiments in their [public notice](http://fjallfoss.fcc.gov/edocs_public/attachmatch/DA-07-3415A1.pdf). The total sum of winning bids in auction 73 was [$19,592,420,000](https://www.fcc.gov/auction/73/factsheet) which stresses the impact of this experiment.

Generally, the theoretical analyses of multi-object auction is scarce due to their complexity and therefore studies rely on empirical data from the field or the laboratory. Regarding [candle auctions](https://en.wikipedia.org/wiki/Candle_auction) scientific studies are also scarce. A noteworthy exception to that is the study of [Füllbrunn & Sadrieh 2012](https://onlinelibrary.wiley.com/doi/full/10.1111/j.1530-9134.2012.00329.x?casa_token=HwBec_2N52IAAAAA%3A0hM0WHPyE6HA03-74BNY6h-_x4dtLAi-zjmPtIxeqUC8jgt9XlMNRBKWY5Ma9erXOg4vudVWkHSKRg) who investigated a second-price single-unit candle auction and compared the results to other auction formats. They found, that after some learning periods, all formats performed equally well in terms of efficiency and revenue and that the candle mechanism successfully induces earlier truth-full bidding; a desired property in auction design.

# Experimental Design
The following sections illustrate various details of the design and the procedure.

## Model
Following [Füllbrunn & Sadrieh 2012](https://onlinelibrary.wiley.com/doi/full/10.1111/j.1530-9134.2012.00329.x?casa_token=HwBec_2N52IAAAAA%3A0hM0WHPyE6HA03-74BNY6h-_x4dtLAi-zjmPtIxeqUC8jgt9XlMNRBKWY5Ma9erXOg4vudVWkHSKRg) the candle design can be described as an random termination auction in discrete time with a fixed number of $T$ bidding stages. In each stage $t$, every bidder has the opportunity to make the first bid or to raise an existing bid (improvement rule) on any of the available packages. The auction terminates after any bidding stage $t$ with probability $q_t\geq0$ and is characterized by an increasing termination probability, i.e., $q_t < q_{t+1}$ for all $t < T$ and $q_T=1$, that is, the auction terminates at $T$ the latest. We denote $\hat{t}$ as the trading period which was randomly determined to be decisive for the outcome of the auction.

## Bundles
There are 4 individual leasing periods available. Bidders are free to bid on any combination of those such that the resulting packages are of consecutive time. This leads to a total of 10 bundles. Those are:

| Period/Bundle 	| 1 	| 2 	| 3 	| 4 	| 5 	| 6 	| 7 	| 8 	| 9 	| 10 	|
|-	|-	|-	|-	|-	|-	|-	|-	|-	|-	|-	|
| 1 	| x 	| x 	| x 	| x 	|  	|  	|  	|  	|  	|  	|
| 2 	|  	| x 	| x 	| x 	| x 	| x 	| x 	|  	|  	|  	|
| 3 	|  	|  	| x 	| x 	|  	| x 	| x 	| x 	| x 	|  	|
| 4 	|  	|  	|  	| x 	|  	|  	| x 	|  	| x 	| x 	|


## Bidders
We assume to have two types of bidders (i.e., projects), which are defined by a different distribution function of private values. Intuitively, the role of bidder, $B_L$ can be regarded as larger scale project, which has significant funding but needs multiple leasing periods to operate. In contrast to that, the other role, $B_S$, models a smaller project with less capital but is interested in any of the four available packages which contain only a single leasing period. 


## Pricing and Allocation Rule
In this specific design of multi-object auction, bidders who submitted the maximum bid for a package do not necessarily win that package. Rather, an algorithm maximizes the allocation of packages to bidders such that the sum of winning bids are maximized across the full leasing period. 


## Termination Time
The experiment lasts in any case until $T$ trading periods are reached. However, at the end we randomly determine $\hat{t}$, which *actually* terminates the auction. After doing so, the historic state of the auction at point $\hat{t}$ is implemented and is payoff-relevant. All bids submitted in $t>\hat{t} \leq T$ become irrelevant for the participants.


## Termination Profile
[Füllbrunn & Sadrieh 2012](https://onlinelibrary.wiley.com/doi/full/10.1111/j.1530-9134.2012.00329.x?casa_token=HwBec_2N52IAAAAA%3A0hM0WHPyE6HA03-74BNY6h-_x4dtLAi-zjmPtIxeqUC8jgt9XlMNRBKWY5Ma9erXOg4vudVWkHSKRg) experimentally compared a candle-auction with linear termination profile to that of a concave one. In the latter one, relatively more termination probability was allocated to earlier $t$. They showed that there were no significant differences in the important outcome metrics (such as market efficiency and revenue) but trading sped up. However, a linear termination profile might be easier to grasp for study subjects and therefore it is reasonable to implement that.

## Potential Parameters (Baseline)
|  	| Parameter 	| Explanation 	|
|-	|-	|-	|
| Name 	| - 	| First-Price Multi-Object Candle Auction 	|
| $T$ 	| $60$ 	| Trading periods defined as multiple of 6 second blocks 	|
| $N$ 	| $8$ 	| Number of bidders per auction 	|
| $n_L$ 	| 2 	| Number of large bidders per auction 	|
| $n_S$ 	| 6 	| Number of small bidders per auction 	|
| $V_L$ 	| $[100,300]$ 	| Valuation for large bidders 	|
| $V_S$ 	| $[0,50]$ 	| Valuation for small bidders 	|
| $q_t$ 	| $1/60$ 	| Termination probability for each trading period 	|
| $R$ 	| $3$ 	| Number of auctions a single participant plays 	|
| $E(t$) 	| $30$ 	| Expected trading rounds ($\hat{t}$) 	|

## Analysis: Outcome measures
We will analyse **bidding dynamics**, that is, when and how participants bid in the course of the auction. In addition, we can analyse **efficiency** (i.e., the slot goes to the players with the highest valuations).

## Treatments:
In this section, we can think about meaningful deviations from the baseline design. The following things are reasonable:

1. **Smart-Contracts:** 
   * We can include automated bidders with fixed bidding strategy and valuation. Currently, the code for those *crowdfunding modules* is already implemented and therefore gives us a straight-forward way to include them in the experiment.
2. **Collusion:**
   * The outcome of auctions is influenced by bidder collusion and multi-identity bidding. Those two factors are rarely as much expressed than in the setting of an blockchain auction with anonymous bidders. 
   * We could induce incentives (or options) to collude between the bidders and compare the result on the outcome.
3. **Other formats:**
   * The Vickrey-Grove-Clarke mechanism in an extension of the Vickrey auction for multi-object auctions and basically implements a second-price mechanism. 
   * Ascending clock auctions which received some attention in the multi-object auction literature.

## Procedure
### Stage 1: Instructions
Participants receive information about the auction and the procedure of the experiment in with written information. In those instructions, the basics about the parachain auctions (as applied in the experiment) are explained, how payoffs are determined and which role they play (either a large or small bidder). We will also ask a few comprehension question and make sure that players understand the game.

### Stage 2: The Auction
Before each auction, all bidders learn their private valuation. Once the auction starts, every bidder is free to submit any bid for any package as long as it increases the previous bid (improvement rule). Bids can be submitted at any time but only every 6 seconds they are "finalized" and have an actual impact. This corresponds to the six second blocks from the blockchain (while the practical impact on the experiment is rather negligible). Note that the total sum of bids per bidder can exceed their total valuation. The trading page features two tables:

1. (Table 1) Current bids: This shows all current bids per package.
  
2. (Table 2) Allocation of packages: This shows the result of the allocation algorithm as if this period was implemented as $\hat{t}$. That means, subjects receive live feedback about the allocation if the auction terminates in the current stage.

Especially table 2 is considered to significant help with this complex auction design. 

### Stage 3: Feedback and Payoff
After $T$, participants enter a feedback screen which gives information about the random determination of $\hat{t}$ and the corresponding snapshot of that state. Profits are calculated and shown to the subjects. Afterwards, the next auction (if there are any) is started and a new draw of $v_i$ is made.

# Organizational aspects

## Recruitment & Payment
Participants can be recruited from the KSM / DOT community. This has the advantage, that basic concepts of the blockchain are already known and that we can frame the experiment in the context of parachain auctions (i.e. that we talk from blocks, transactions etc.). We specify a fixed conversion rate of valuation to ECU which is pegged to USD. This has the advantage that the final payment will be constant in USD even if prices of DOT / KSM fluctuate during the time of the whole study. Funding could be requested from the KSM or DOT treasury.



## Implementation
The experiment will be implemented with [oTree](https://www.sciencedirect.com/science/article/pii/S2214635016000101), which is a software to conduct online experiments and provide the necessary infrastructure to create sessions, distribute links to users and maintain a database of behavioral data. It combines python in the back-end with a flexible front-end implementation of HTML/CSS and Django. The front-end can also leverage javascript which offers the option to closely integrate the [`polkadot.js`](https://polkadot.js.org/apps/#/explorer) front-end.

### UI
Some suggestions for how information can be displayed will be shown here.

