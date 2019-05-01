(tentative plan for)

# Parachains - Allocation & Scaling

## Introduction:
A parachain is a peer-to-peer data structure that connects to the relay chain to become globally-coherent with other parachains connected to the relay chain.

To run a parachain in Polkadot a parachain slot within Polkadot needs to be obtained. Since Polkadot is a resource-constraint system, there are a finite number of slots, which are rolled out gradually. Parachain slots are locked on a deposit basis.
- Cost comes from implied dilution.
- Should the dilution-fee not be sufficient to support network validation, i.e. because validators rewards become so low, a rental fee could also be introduced by the governance process.

The costs covers a number of things, for example, transaction fees paid to block producer of the relay chain, blocking the slot, etc. Once a parachain wants to leave Polkadot its locked tokens for that slot are released. There is no waiting period, however, releasing happens only once finality is reached.

## Parachain Allocation

We define two types of parachains, namely, community beta slots and commercial slots. 

We want to reserve 20% slots for community beta parachain slots (“fair”, non- or limited-premine) chains that W3F will deploy or support. This includes: Edgware, Ethereum-bridge, Bitcoin-bridge, Z-cash bridge. These parachain slots will be granted for up to a 2-year period. The remaining 80% of the slots can be more “publicly” or “commercially” opened.
As long as at least one commercial slot is free, there is an associated price given by some sort of progressive curve, to control rapid increase of demand. If a commercial slot becomes free and no commercial slots are already free, then it is auctioned as follows.

## Auctioning Parachain Slots:

To determine the parachain allocation fee we carry out auctions periodically as follows. We mainly use auctions to have a fair and transparent parachain allocation procedure.

If a commercial slot becomes free and no commercial slots are already free, then it is set for auction with a 2-week window (we might increase this later) for posting blind bids for the auction. To participate in an auction for obtaining a slot, a parachain needs to deposit DOTs. A parachain candidate can issue additional native tokens in order to acquire DOTs. If a parachain fails to obtain the slot, the returned DOTs can be used to buy back the native token and burn it.

### Auction Scheme

In the literature, many variations of auctions have been proposed that each have advantages and disadvantages. Two popular types of auctions are Vickery [1,2] and English [2] auctions, where the bidders submit their true value as bids. In Vickery auctions, all the bids are sealed and the winner pays the amount of the second highest bid. In English auctions, everyone openly submits bids and bidders overbid each other until the end of the auction. The winner pays the amount of his winning bid. Since sealed-bid auctions are hard to implement in a decentralized setup such as blockchains and in English auctions bid sniping, where a bidder submits a slightly higher bid just before the closing time of the auction is one of the main problems. To address both these problems we use an multi-unit English auction with an unknown closing time as follows. 

Let us assume we have a number of parachain slots available at the time we start the auction. We divide each slot into time units of six months. A bidder can bid on a continuous range of units between 1 and 4. A bid is a tuple consisting of a unit range and bid value in DOTs. These open bids are added into a block that is added to the relay chain. There is no distinction between individual slots that means for now everyone can bid only for one slot at any given moment and bidding on overlapping units is not permitted.  

Once the block with the bids is added to the relay chain, everyone computes the winners according to all bids that are added to the block. To determine the winner we compute the highest DOT per unit for all bids entered, by calculating the average locked DOT per unit for a subset of non-overlapping bids for each slot. 

For example, let us assume we have three bidders that want to submit bids for a parachain slot. Bidder $B_1$ submits the bid (1-4,75 DOT), bidder $B_2$ submits (3-4, 90 DOTs), and bidder $B_3$ submits (1-2, 30). In this example bidder $B_1$ wins because if bidder $B_2$ and bidder $B_3$ win each unit would only be locked for 60 DOTs, while of bidder_1 wins each unit is locked for 75 DOTs. 

For the next block, everyone who has a higher valuation for the parachain slot submits new bids to the next block to outbid winners from the previous blocks. This procedure continues until the end of the epoch. In the next epoch, some randomness obtained from a VRF function (see [BABE](BABE/Babe.md), where the VRF function is also used for more information) is going to determine which block from the previous epoch was the last (closing) block of the auction. Hence, the auction closing time is determined retroactively. 

The winner of the auction is determined based all the bids submitted in blocksuntil and including the closing block. The winners pay the value amount of their winning bids. 

**Strategy for bidding:** 
Bidders can bid on any consecutive range of units. However, everyone will add bids with the maximum unit range that they need and only submit bids for smaller unit ranges if they lose the bid in a given block for higher ranges. While in the first auction bidders with a high valutaion for parachain slots will aim at bidding first on only high ranges, in next auctions, units that are immediately after the previous range that the bidder has already obtained are of very high value for those bidders because it prevents disruption in their parachain operation. 

**Advantages of our scheme compared to English auctions:**

- Serious bidding from the start: since the auction might close at the first block, bidders submit serious bids in the first block
- Prevention of overbidding and bid sniping: Bid sniping is unfair to other bidders since they will loose the auction not because they had a lower valuation for the item but because they were not given the chance to counterbid. Avoiding overbidding may harm total revenue for the seller, but this is not an objective for us.
- Weaker bidders have a chance to win: which encourages participation. However, note that we do not have a completely random auction close time and the bidder still needs to be the best bidder among all bids in an entire given block for the least. For example, if the first block is the closing block, the bidders need to be a winner among the bids in that block. Our scheme is rather a hybrid between a hard close and a random close. 

By allowing for an n-sided market to determine the cost of connecting to the system, we ensure a weakly dominant Nash-equilibrium between the bidders in question and allow for appropriate valuation of connecting to the system. 


## Parachain Scaling

At Polkadot genesis there will be an estimated 5-15 available and the number of available slots will increase during the first 1-2 years of operation to between 50 and 200 parachains total. 
We will auction parachains slots off in batches of 4 over the course of the 1st year, with new auctions planned every few weeks. Each batch of 4 will include a 6-month, 12-month, 18-month and 24-month parachain slot for auction. The general idea is that, in perpetuity, there is a constant rolling availability of parachains auctions so that if your project wants to become a “native parachain” in Polkadot there will be sufficient opportunities to claim a parachain slot.
One of the objectives of our roll-out plan is to maintain demand-supply balance for parachain slots such that there are appropriate economic incentives to be a validator on the network. Moreover, we want to allow for the proliferation of experimentation and novel use-cases as the network scales. 

## References

[1] Vickrey, William. "Counterspeculation, Auctions, and Competitive Sealed Tenders". The Journal of Finance, 16 (1): 8–37, 1961.

[2] Preston McAfee and John McMillan. "Auctions and Bidding". Journal of Economic Literature, 699–738, 1987.


