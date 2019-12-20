====================================================================

**Authors**: Fatemeh Shirazi (design also from Gavin Wood and Alistair Stewart)

**Last updated**: 20.12.2019

**Note**: In progress

====================================================================

# Parachain Allocation

## Introduction
To run a parachain in Polkadot a parachain slot needs to be obtained. Parachain slots are locked on a deposit basis. We define two types of parachains, namely, community beta slots and commercial slots. We want to reserve 20% slots for community beta parachain slots (“fair”, non- or limited-premine) chains that W3F will deploy or support. The remaining 80% of the slots can be more “publicly” or “commercially” opened. Commercial slot are auctioned as follows.

## Auctioning Parachain Slots
Since some of the bidders are smart contracts sealed-bid auctions are difficult to realise in our context. We use auctions to have a fair and transparent parachain allocation procedure. Since implementing seal-bid auctions are difficult and to avoid bid sniping we adopt a Candle auction with a retroactively determined close as follows.

Once the auction has started within a fixed window bidders can post bids for 1-4 lease periods, where each lease period is 6 months. Bids go into the block as transactions. Bidders are allowed to submit multiple bids. Bids that a bidder is submitting either should intersect with all winning bids by same bidder or be contiguous with winning bids by the same bidder. If an incoming bid is not changing the winners it is ignored.

For 4 lease periods we have 10 possible ranges. We store the winner for each one of the 10 ranges in a designated data structure. We need to make sure that a new bid does not have a gap with a winning bid on another interval from the same bidder. This means that once a bidder has won a bid for a given range, say for example lease periods 1-2, then he cannot bid on 4 unless someone overbids him for 1-2.

For any incoming bid the new winner is calculated by choosing the combination of bids where the average deposit for overall all 4 lease periods is most. Once a bid is added to the block, the amount of their bid gets reserved.

Once a fixed number of blocks have been produced for the auction a random numbers decides which one of the previous blocks was the closing block and we return the winners and their corresponding ranges for that closing block. The reserved funds of losers are going to be released once the ending time of the auction is determined and the final winners are decided.

For example, let us assume we have three bidders that want to submit bids for a parachain slot. Bidder $B_1$ submits the bid (1-4,75 DOT), bidder $B_2$ submits (3-4, 90 DOTs), and bidder $B_3$ submits (1-2, 30). In this example bidder $B_1$ wins because if bidder $B_2$ and bidder $B_3$ win each unit would only be locked for an average of 60 DOTs or something else equivalent to 240 DOT-intervals, while of bidder $B_1$ wins each unit is locked for 75 DOTs.

# Analysis
English auctions can be used when bidders have private/public valuations and vickery auctions can be used when the bidders have private valuations. Both these auctions have weakly dominant strategies, where the best a bidder can do is be truthful about their valuation. 

Our auction design has two fundamental design differences with English auctions; 1) A retroactive  close 2) valuations of bidders is partly private and partly public. 

For our analysis, we are interested in a number of goals such as *fairness*, *having a dominant strategy*, and *maximizing revenue*. 


## Fairness
By being *fair* we mean that a bidder with a higher valuation than another bidder will have a higher chance of winning the auction that is relative to the difference in their valuation. 

Having a random close means that bidders need to submit serious bids early on the in the bidding stage and cannot wait until just before the end. Otherwise, having a random retroactive close does not reduce fairness for bidders with private valuation. 
We want to show that the Candle auction is fair for smarts contracts that are bidders with public strategy profiles such that they can only be griefed by users who accept a significant risk of incurring cost for them. By griefing we refer to bidding above ones valuation for the purpose of force the winner to pay more.

We want to present a strategy for smart contracts that is nearly dominant when everyone does not bid above their valuation. By a strategy profile being nearly dominant we refer to Epsilon-equilibrium [[1](http://www.cs.cmu.edu/~sandholm/cs15-892F13/algorithmic-game-theory.pdf)]. A strategy profile that is nearly dominant, satisfies the condition of Nash equilibrium [] within a factor of some well-defined epsilon. We follow up by showing that bidding above ones valuation, i.e. with the intention of griefing, introduces risks for those bidders. 


## Bidding Strategy for Smart Contracts
The aim is to find a strategy profile that minimizes the disadvantage a smart contract has compared to a bidder with a private strategy profile. 

Let us assume we have a bidder $P$ who has a valuation $V$ for an auctioned item, i.e., parachain slot. We want to find an $\alpha \in (0,1]$ for a defined strategy $S_P$ for bidder $P$ as follows. 

If the following two conditions hold:

1. in the last block $P$ was not winning, 
2. for the winning bid, $b$, of the last block $b<V-\alpha V$ holds
 
then in next block, $P$ bids $b+\alpha V$.

Choosing $\alpha$ is a trade-off between avoiding overpaying and increasing the chance of winning. Intuitively, for big $n$, $\alpha$ can be small and for small $n$, $\alpha$ needs to be large. A bigger $\alpha$ increases the chance of winning but might incur unnecessary overpaying for the winner. Next, we first characterize both the chance of winning and utility for a smart contract and then calculate $\alpha$ using the number of total blocks, the valuation of $P$, and maximum valuation of all other bidders.

### Chance of Winning


**Claim**: There are at most $\frac{1}{\alpha}-1$ blocks when 

* P is not winning and
* $b < V-\alpha V$.

Suppose we have $n$ blocks in total, we want to calculate the probability that $P$ wins when we have the following conditions holding: 

* If no one is bidding over their own valuation
* The maximum valuation of others $V_{max}$ and $V_{max}<V-\alpha V$

The probability that $P$ wins is at least as follows.

$Pr$[$P$ is winning]=$1-\frac{1}{\alpha n}+\frac{1}{n}=\frac{n-(\frac{1}{\alpha}-1)}{n}$

where $(\frac{1}{\alpha}-1)$ is the probability that is $P$ is not winning. Note that $P$ only wins with high probability if $V(1 - \alpha) > V_{max}$.

### Utility for any winning bidder

Now, let us assume $P$ is winning. How much does it have to pay? And what is its utility? Once $P$ wins the item in the auction, its utility refers to the amount it has saved compared to its real valuation for the item, defined as follows. 
$U_P=\begin{cases}
    0       & \quad \text{if } P \text{ is not winning}  
    V-b  & \quad \text{if } P \text{ is winning}
  \end{cases}
$
where $b$ is the winning bid in the block that is the closing block of the auction. The most $P$ has to pay is $V_{max}+\alpha V$. The expected utility of $P$ is at least equal to the probability that P is winning times the cost P is paying most. 

EX[$U_P$]=$(1-\frac{1}{\alpha n}+\frac{1}{n})$ $\times$ $(V-(V_{max}+\alpha V))$

We want to compare the expected utility to $V-V_{max}$, which is the most utility $P$ is guaranteed getting against any strategy. We need differentiate these two to find the value of $\alpha=\frac{1}{\sqrt[2]{n-1}}$.
