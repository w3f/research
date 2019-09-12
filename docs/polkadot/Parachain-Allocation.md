====================================================================

**Authors**: Fatemeh Shirazi

**Last updated**: 12.09.2019

**Note**: In progress

====================================================================

# Parachain Allocation

## Introduction
To run a parachain in Polkadot a parachain slot needs to be obtained. Parachain slots are locked on a deposit basis. We define two types of parachains, namely, community beta slots and commercial slots. We want to reserve 20% slots for community beta parachain slots (“fair”, non- or limited-premine) chains that W3F will deploy or support. The remaining 80% of the slots can be more “publicly” or “commercially” opened. Commercial slot are auctioned as follows.

## Auctioning Parachain Slots
We use auctions to have a fair and transparent parachain allocation procedure. Since implementing seal-bid auctions are difficult and to avoid bid sniping we adopt an Candle auction with a retroactively determined close as follows.

Once the auction has started within a fixed window bidders can post bids for the auction. Bids go into the block as transactions. Bidders are allowed to submit multiple bids. Bids that a bidder is submitting either should intersect with all winning bids by same bidder or be contiguous with winning bids by the same bidder. If an incoming bid is not changing the winners it is ignored.

For 4 lease periods we have 10 possible ranges. We store the winner for each one of the 10 ranges in a designated data structure. We need to make sure that a new bid does not have a gap with a winning bid on another interval from the same bidder. This means that once a bidder has won a bid for a given range, say for example lease periods 1-2, then he cannot bid on 4 unless someone overbids him for 1-2.

For any incoming bid the new winner is calculated by choosing the combination of bids where the average deposit for overall all 4 lease periods is most. Once a bid is added to the block, the amount of their bid gets reserved.

Once a fixed number of blocks have been produced for the auction a random numbers decides which one of the previous blocks was the closing block and we return the winners and their corresponding ranges for that closing block. The reserved funds of losers are going to be released once the ending time of the auction is determined and the final winners are decided.

For example, let us assume we have three bidders that want to submit bids for a parachain slot. Bidder $B_1$ submits the bid (1-4,75 DOT), bidder $B_2$ submits (3-4, 90 DOTs), and bidder $B_3$ submits (1-2, 30). In this example bidder $B_1$ wins because if bidder $B_2$ and bidder $B_3$ win each unit would only be locked for an average of 60 DOTs or something else equivalent to 240 DOT-intervals, while of bidder $B_1$ wins each unit is locked for 75 DOTs.

## Analysis
Our auction design has two fundamental design differences with English auctions; 1) A retroactive random close 2) a non uniformity on having private or public valuation for the item on auction.

TODO: Summarize existing results fo analyzing English auctions.

For our analysis, we are interested in a number of goals such as *fairness*, *having a dominant strategy*, and *maximizing revenue*. Finally we discuss how we could keep the auction results relatively similar accross a number of auctions. We might need this to have a stable valuation for our token DOT.

One of the main objectives of our action scheme is to make it *fair*. By being fair we mean that a bidder with a higher valuation than another bidder will have a higher chance of winning the auction that is relative to the difference in their valuation.

Having a random retroactive close does not reduce fairness for bidders with private valuation. Hence, we want to show that the Candle auction is fair for users (bidders with private strategy profiles) and smarts contracts (bidders with public strategy profiles).

We want to show that we are fair towards smart contracts such that they cannot be grieved with no costs by users who will bid above their valuation for this purpose.

We want to present a strategy for smart contracts that is nearly dominant when everyone does not bid above their valuation. By nearly dominant we refer to Epsilon-equilibrium \cite{}. A strategy profile that is nearly dominant, satisfies the condition of Nash equilibrium within a factor of some well defined epsilon.

We follow up by showing that bidding above ones valuation (with the intention of grieving for example) introduces risks for those bidders.
