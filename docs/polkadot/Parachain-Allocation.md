# Parachain Allocation

## Introduction
To run a parachain in Polkadot a parachain slot needs to be obtained. Parachain slots are locked on a deposit basis. We define two types of parachains, namely, community beta slots and commercial slots. We want to reserve 20% slots for community beta parachain slots (“fair”, non- or limited-premine) chains that W3F will deploy or support. The remaining 80% of the slots can be more “publicly” or “commercially” opened. Commercial slot are auctioned as follows. 

## Auctioning Parachain Slots
We use auctions to have a fair and transparent parachain allocation procedure. Since implementing seal-bid auctions are difficult and to avoid bid sniping we adopt an Candle auction with a retroactively determined close as follows. 

Once the auction has started within a fixed window (1 week?) bidders can post bids for the auction. Bids go into the block as transactions. Bidders are allowed to submit multiple bids. Bids that a bidder is submitting either should intersect with all winning bids by same bidder or be contiguous with winning bids by the same bidder. If an incoming bid is not changing the winners it is ignored. 

For 4 lease_periods we have 10 possible ranges. We store the winner for each one of the 10 ranges in a designated data structure. We need to make sure that a new bid does not have a gap with a winning bid on another interval from the same bidder. This means that once a bidder has won a bid for a given range, say for example lease_periods 1-2, then he cannot bid on 4 unless someone overbids him for 1-2. 

For any incoming bid the new winner is calculated by choosing the combination of bids where the average deposit for overall all 4 lease_periods is most. Once a bid is added to the block, the amount of their bid gets reserved. 

Once a fixed number of blocks have been produced for the auction a random numbers decides which one of the previous blocks was the closing block and we return the winners and their corresponding ranges for that closing block. The reserved funds of losers are going to be released once the ending time of the auction is determined and the final winners are decided. 

For example, let us assume we have three bidders that want to submit bids for a parachain slot. Bidder $B_1$ submits the bid (1-4,75 DOT), bidder $B_2$ submits (3-4, 90 DOTs), and bidder $B_3$ submits (1-2, 30). In this example bidder $B_1$ wins because if bidder $B_2$ and bidder $B_3$ win each unit would only be locked for an average of 60 DOTs or something else equivalent to 240 DOT-intervals, while of bidder_1 wins each unit is locked for 75 DOTs. 
