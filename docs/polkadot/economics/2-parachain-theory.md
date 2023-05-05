---
title: Theoretical Analysis of Parachain Auctions
---

====================================================================

**Authors**: Samuel Häfner and Alistair Stewart

**Last updated**: April 17, 2021

====================================================================

As explained [here](/polkadot/overview/3-parachain-allocation.md) and [here](https://wiki.polkadot.network/docs/en/learn-auction) Polkadot uses a candle auction format to allocate parachain slots. A candle auction is a dynamic auction with the distinguishing feature that the ending time is random. In this project, we analyze the effects of such a random-closing rule on equilibrium play when some bidders have front-running opportunities.

Front-running opportunities emerge on blockchains because upcoming transaction become known among the network participants before they are included in new blocks. For blockchain implementations of auctions, this means that some bidders can see and potentially react to other bidders' bids before they come into effect; i.e., are recorded on the chain and are thus taken into account by the auction mechanism. In first-price auctions, this gives tech-savvy bidders the possibility to outbid other bidders as they please. In second-price auctions, the auctioneer could raise the payment of the winning bidder at no cost by registering his own (pseudonymous) bidder.

Whereas cryptographic solutions to these problems exist, they are either very computing intensive or require multiple actions by the bidders. In the presence of smart contracts, they do not work at all, because the actions of smart contracts are perfectly anticipatable. As an alternative that works without encrypting bids, this project analyzes a dynamic single-unit first-price auction with a random ending time. Time is discrete and in every round two bidders move sequentially in a fixed order.  We show that a random-closing rule both revenue-dominates a hard-closing rule and makes participation for the bidder being front-run more attractive. In particular, under a uniform ending time distribution both the utility of the disadvantaged bidder and total revenues approach that of a second-price auction as the number of rounds grows large. Furthermore, the good is allocated efficiently.

Reference:
Samuel Häfner and Alistair Stewart (2021): Blockchains, Front-Running, and Candle Auctions. Working Paper. [SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3846363)
