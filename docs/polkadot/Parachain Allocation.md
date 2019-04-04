(tentative plan for)

# Parachains - Allocation & Scaling

### Introduction:
A parachain is a peer-to-peer data structure that connects to the relay chain to become globally-coherent with other parachains connceted to the relay chain.

To run a parachain in Polkadot a parachain slot within Polkadot needs to be obtained. Since Polkadot is a resource-constraint system, there are a finite number of slots, which are rolled out gradually. 
Parachain slots are locked on a deposit basis.
- Cost comes from implied dilution.
- Should the dilution-fee not be sufficient to support network validation, i.e. because validators rewards become so low, a rental fee could also be introduced by the governance process.

The costs covers a number of things, for example, tx fees paid to block producer of the relay chain, blocking the slot, etc.
Once a parachain wants to leave Polkadot its deposited tokens are released. There is no waiting period, however, releasing happens only once finality is reached.

### Parachain Allocation

We define two types of parachains, namely, community beta slots and commercial slots. 

We want to reserve 20% slots for community beta parachain slots (“fair”, non- or limited-premine) chains that W3F will deploy or support. This includes: Edgware, Ethereum-bridge, Bitcoin-bridge, Z-cash bridge. These parachain slots will be granted for up to a 2-year period. 
The remaining 80% of the slots can be more “publicly” or “commercially” opened.
As long as at least one commercial slot is free, there is an associated price given by some sort of progressive curve, to control rapid increase of demand. If a commercial slot becomes free and no commercial slots are already free, then it is auctioned as follows.

### Auctioning Parachain Slots:

We use a Vickrey auction [1], second-price sealed-bid auctions, for parachain slots when the demand is higher than the available slots. We chose a sealed-bid auction because it needs less communication overhead for bidding than open-bid (iterative) auctions. Aong sealed-bid auctions we chose Vickrey auctions because:

a) it has a weakly dominant strategy that is bidding the true value of the bidder [2], which makes it more efficenit for bidders
b) in multiunit auctions, when the bids are interdependent and identically distributed, the expected price paid by a winner bidder of a Vickrey auction is at least as high as the expected price paid by a winner bidder of a first-price sealed-bid  (discriminatory) auctions [3]

Weaknesses:
c) does not necessarily maximize seller profit 
d) vulnerable to bidder collusion and shilling

To mitigate c) we can reserve a price. Note that b) still holds in the reserved price setting. 

**How do we carry out a Vickrey auction in a decentrliazed fashion?**
We want to implement the auction without the presence of a dealer. Since, we do not aim to keep bids sealed, we could use some sort of a commit-reveal scheme for bidding. Maybe we also could implement it with threshold public key encryption scheme?


If a commercial slot becomes free and no commercial slots are already free, then it is set for auction with a 2-week window for posting blind bids for the auction.
To participate in an auction for obtaining a slot, a parachain needs to deposit DOTs. A parachain candidate can issue additional native tokens in order to acquire DOTs. If a parachain fails to obtain the slot, the returned DOTs can be used to buy back the native token and burn it.
Everyone places a DOT deposit (that must be 10% of their revealed bid) together with a hash of their bid. Hashes are revealed in the final day of the parachain that is freeing up. Unrevealed hashes result in the total deposit being given to the winner. It is to avoid using many bids which you have no intention of revealing if they are winning to drive up costs for the winner in a Vickrey auction. The downside is that the winner can use unrevealed bids to fake competition for free. The winner is the second highest revealed bid. All non-winning bids that have been revealed get their deposits back.

**(Q:Auction economics?)**

By allowing for an n-sided market to determine the cost of connecting to the system, we ensure a Nash-equilibrium between the actors in question and allow for appropriate valuation of connecting to the system. 


### Parachain Scaling

At Polkadot genesis there will be an estimated 5-15 available and the number of available slots will increase during the first 1-2 years of operation to between 50 and 200 parachains total. 
We will auction parachains slots off in batches of 4 over the course of the 1st year, with new auctions planned every few weeks. Each batch of 4 will include a 6-month, 12-month, 18-month and 24-month parachain slot for auction. The general idea is that, in perpetuity, there is a constant rolling availability of parachains auctions so that if your project wants to become a “native parachain” in Polkadot there will be sufficient opportunities to claim a parachain slot.
One of the objectives of our roll-out plan is to maintain demand-supply balance for parachain slots such that there are appropriate economic incentives to be a validator on the network. Moreover, we want to allow for the proliferation of experimentation and novel use-cases as the network scales. 

## References
[1] Vickrey, William. (1961). Counterspeculation, Auctions, and Competitive Sealed Tenders. The Journal of Finance. 

[2] 

[3] Milgrom, Paul. (2019). The economics of competitive bidding: a selective survey. 
