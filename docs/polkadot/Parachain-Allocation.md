(tentative plan for)

# Parachains - Allocation

## Introduction:
To run a parachain in Polkadot a parachain slot needs to be obtained. Parachain slots are locked on a deposit basis. We define two types of parachains, namely, community beta slots and commercial slots. We want to reserve 20% slots for community beta parachain slots (“fair”, non- or limited-premine) chains that W3F will deploy or support. The remaining 80% of the slots can be more “publicly” or “commercially” opened. Commercial slot are auctioned as follows. 

## Auctioning Parachain Slots
We use auctions to have a fair and transparent parachain allocation procedure. Since implementing seal-bid auctions are difficult and to avoid bid sniping we adopt an Candle auction with a retroactively determined close as follows. 

Once the auction has started within a fixed window (1 week?) bidders can post bids for the auction. Bidders are allowed to submit multiple and overlapping bids. Bids either should intersect with all winning bids by same bidder or be contiguous with winning bids by the same bidder. Bids go into the block as transactions. If an incoming bid is not changing the winners it is ignored. For 4 lease_periods we have 10 ranges. We store the winner for each one of the 10 ranges. We need to make sure that the new bid does not have a gap with **his winning** bid. This means that once a bidder B has won a bid for a given range, say for example lease_periods 1-2 and his bid is a winning bid, then he cannot bid on 4 unless someone overbids him for 1-2. For any incoming bid the new winner is calculated by choosing the combination of bids where the average deposit for overall all 4 lease_periods is most. Once a bid is added to the block, the amount of their bid gets reserved. The reserved funds of losers are going to be released once the ending time of the auction is determined and the final winners are decided. 

For example, let us assume we have three bidders that want to submit bids for a parachain slot. Bidder $B_1$ submits the bid (1-4,75 DOT), bidder $B_2$ submits (3-4, 90 DOTs), and bidder $B_3$ submits (1-2, 30). In this example bidder $B_1$ wins because if bidder $B_2$ and bidder $B_3$ win each unit would only be locked for 60 DOTs, while of bidder_1 wins each unit is locked for 75 DOTs.  

Bidders can bid on any consecutive range of units. However, everyone will add bids with the maximum unit range that they need and only submit bids for smaller unit ranges if they lose the bid in a given block for higher ranges. While in the first auction bidders with a high valutaion for parachain slots will aim at bidding first on only high ranges, in next auctions, units that are immediately after the previous range that the bidder has already obtained are of very high value for those bidders because it prevents disruption in their parachain operation. 

**Advantages of our scheme compared to English auctions:**

- Serious bidding from the start: since the auction might close at the first block, bidders submit serious bids in the first block
- Prevention of overbidding and bid sniping: Bid sniping is unfair to other bidders since they will loose the auction not because they had a lower valuation for the item but because they were not given the chance to counterbid. Avoiding overbidding may harm total revenue for the seller, but this is not an objective for us.
- Weaker bidders have a chance to win: which encourages participation. 

By allowing for an n-sided market to determine the cost of connecting to the system, we ensure a weakly dominant Nash-equilibrium between the bidders in question and allow for fair valuation of connecting to Polkadot. 



