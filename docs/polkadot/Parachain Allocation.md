(tentative plan for)

# Parachains - Allocation & Scaling

## Introduction:
A parachain is a peer-to-peer data structure that connects to the relay chain to become globally-coherent with other parachains connceted to the relay chain.

To run a parachain in Polkadot a parachain slot within Polkadot needs to be obtained. Since Polkadot is a resource-constraint system, there are a finite number of slots, which are rolled out gradually. 
Parachain slots are locked on a deposit basis.
- Cost comes from implied dilution.
- Should the dilution-fee not be sufficient to support network validation, i.e. because validators rewards become so low, a rental fee could also be introduced by the governance process.

The costs covers a number of things, for example, tx fees paid to block producer of the relay chain, blocking the slot, etc.
Once a parachain wants to leave Polkadot its deposited tokens are released. There is no waiting period, however, releasing happens only once finality is reached.

## Parachain Allocation

We define two types of parachains, namely, community beta slots and commercial slots. 

We want to reserve 20% slots for community beta parachain slots (“fair”, non- or limited-premine) chains that W3F will deploy or support. This includes: Edgware, Ethereum-bridge, Bitcoin-bridge, Z-cash bridge. These parachain slots will be granted for up to a 2-year period. 
The remaining 80% of the slots can be more “publicly” or “commercially” opened.
As long as at least one commercial slot is free, there is an associated price given by some sort of progressive curve, to control rapid increase of demand. If a commercial slot becomes free and no commercial slots are already free, then it is auctioned as follows.

## Auctioning Parachain Slots:
We mainly use auctions to have a fair and transparent parachain allocation procedure. 

If a commercial slot becomes free and no commercial slots are already free, then it is set for auction with a 2-week window for posting blind bids for the auction.
To participate in an auction for obtaining a slot, a parachain needs to deposit DOTs. A parachain candidate can issue additional native tokens in order to acquire DOTs. 
If a parachain fails to obtain the slot, the returned DOTs can be used to buy back the native token and burn it.

### Auction Scheme

Since sealed-bid auctions are hard to implement in a decentralized set up we decided to use an open (English) auction with some changes as follows. 

Let us assume we have a number of parachain slots available at the time we start the auction. We divide each slot into time units of six months. A bidder can bid on a continuous range of units between 1 and 4. A bid is a tuple consisting of a unit range and bid value in DOTs. There is no distinction between individual slots that means for now everyone can bid only for one slot and bidding on overlapping units is not permitted. These open bids are added into a block that is added to the relay chain. Once this block is added to the relay chain, everyone computes the winners according to the bids in the all the added block(s) and submits new bids to the next block to outbid those winners. This prodecure continues until the end of the epoch. In the next epoch, randomness obtained from a VRF function is going to determine which block from the previous epoch was the last (closing) block. Hence, the auction ending time is determined retroactively. We compute the highest DOT per unit for all bids entered in blocks until and including the closing block. The winners pay the value amount of their winning bids. 

Advantages: 
- bidders submit serious bids from the beginning
- we prevent overbidding and snipping (this can harm total revenue for the seller, but this is not an objective for us)
- weaker bidders have a chance to win in the auction, which encourages participation. However, note that we do not have a comlteltey random close and the bidder still needs to be the best bidder among all bids in an entire given block for the least. For example, if the first block is the closing block, the bidders needs to be a winner amoung the bids in that block. This means that if high bids are in the first blocks, weaker bidders do not have much chance anymore. 

TODO: does a weakly dominant strategy of English auctions still hold for our extension?

By allowing for an n-sided market to determine the cost of connecting to the system, we ensure a weakly dominant Nash-equilibrium between the actors in question and allow for appropriate valuation of connecting to the system. 

## Parachain Scaling

At Polkadot genesis there will be an estimated 5-15 available and the number of available slots will increase during the first 1-2 years of operation to between 50 and 200 parachains total. 
We will auction parachains slots off in batches of 4 over the course of the 1st year, with new auctions planned every few weeks. Each batch of 4 will include a 6-month, 12-month, 18-month and 24-month parachain slot for auction. The general idea is that, in perpetuity, there is a constant rolling availability of parachains auctions so that if your project wants to become a “native parachain” in Polkadot there will be sufficient opportunities to claim a parachain slot.
One of the objectives of our roll-out plan is to maintain demand-supply balance for parachain slots such that there are appropriate economic incentives to be a validator on the network. Moreover, we want to allow for the proliferation of experimentation and novel use-cases as the network scales. 

## References

