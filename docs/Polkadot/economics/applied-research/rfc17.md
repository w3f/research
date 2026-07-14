# Coretime Market Redesign (accepted): RFC-0017

|                 |                                                                                             |
| --------------- | ------------------------------------------------------------------------------------------- |
| **Original proposition date**  | 05.08.2023                                                                                  |
| **Revision date**  | 04.06.2025                                                                                  |
| **Description** | This RFC proposes a redesign of Polkadot's coretime market to ensure cost efficiency through a clearing-price Dutch auction. Coretime also introduces a mechanism that guarantees current coretime holders the right to renew their cores outside the market, albeit at the market price plus an additional charge. This design aligns renewal and market prices, preserving long-term access for current coretime owners. It also ensures sufficient market pressure on all purchasers, resulting in an efficient allocation.


## Summary

This entry proposes restructuring the bulk markets in the Polkadot's coretime allocation system to improve efficiency and fairness. The proposal suggests splitting the BULK_PERIOD into three consecutive phases: MARKET_PERIOD, RENEWAL_PERIOD, and SETTLEMENT_PERIOD. Such a structure enables the discovery of a market-driven price via an auction using a clearing-price Dutch mechanism, followed by renewal offers during the RENEWAL_PERIOD.

With all coretime consumers paying a unified price, one can remove all liquidity restrictions on cores purchased either during the initial market phase or renewed in the renewal phase. This creates a meaningful `SETTLEMENT_PERIOD`, where final agreements and deals between coretime consumers can be arranged on the social layer, complementing the agility this system seeks to establish.

Under the new design, it is possible to obtain the `clearing_price`, a uniform price that anchors new entrants and current tenants. Based on actual core consumption, the design includes a dynamic reserve price adjustment mechanism that complements market-based price discovery. These two components ensure robust price discovery and mitigate price collapse in cases of slight underutilisation or collusive behaviour.

## Motivation

After assessing the initial system introduced in [RFC-1](https://github.com/polkadot-fellows/RFCs/blob/6f29561a4747bbfd95307ce75cd949dfff359e39/text/0001-agile-coretime.md) under real-world conditions, several weaknesses were identified. These pertain to the capture of cores at very low prices, which can be removed from the open market and retained indefinitely since renewal costs are minimal. Here, the issue is the absence of price anchoring, which results in two divergent price paths: one for the initial purchase on the open market, and another that is fully deterministic via the renewal bump mechanism.

The proposal addresses these issues by anchoring all prices to a value derived from the market, while still preserving necessary privileges for current coretime consumers. The goal is to produce robust results across various demand conditions (low, high, or volatile).

In particular, this proposal introduces the following key changes:

* **Reverse the order of the market and renewal phases.** First, all cores are offered on the open market, and only then renewal options become available.
* **Introduce a dynamic `reserve_price`.** This is the minimum price for the coretime in a period. The price adjusts based on consumption and does not rely on market participation.
* **Make unproductive core captures sufficiently expensive.** This is because all cores are exposed to the market price.

The proposal offers a straightforward design to discover the coretime price within a period as a `clearing_price`. Long-term coretime holders still retain the privilege to keep their cores **if** they can pay the price the market discovers, with a premium for that privilege. The proposed model aims to balance out leveraging market forces for allocation while operating within defined bounds. In particular, prices are capped *within* a `BULK_PERIOD`, giving price certainty to existing teams. Under high demand, prices may increase exponentially *between* multiple market cycles. This feature is necessary to ensure proper price discovery and the efficient allocation of coretime.

The framework proposed here seeks to adhere to all requirements originally stated in RFC-1.


## Stakeholders

The primary stakeholder sets are:

- Protocol researchers, developers, and the Polkadot Fellowship.
- Polkadot Parachain teams: present, future, and their users.
- DOT token holders.

## Explanation

### Overview

After the restructuring, the `BULK_PERIOD` now has two primary segments: the `MARKET_PERIOD` and the `RENEWAL_PERIOD`, along with an auxiliary `SETTLEMENT_PERIOD`. The latter does not require any participation from the coretime system chain, except for executing ownership transfers between market participants. A significant change in the current design lies in the timing of renewals, which now occurs after the market phase. Such an adjustment aims to harmonize renewal prices with their market counterparts, ensuring a more consistent and equitable pricing model.

### Market Period (14 days)

During the Market Period, core sales go through a well-established **clearing-price Dutch auction** that features a `reserve_price`. Since the auction format is a descending clock, the auction begins at the `opening_price`. This price then descends linearly over the duration of the `MARKET_PERIOD` toward the `reserve_price`, which serves as the minimum coretime price within that period.

Each bidder should submit their desired price and the quantity of cores they wish to purchase. To secure these acquisitions, bidders must deposit an amount of DOT equal to their bid times the chosen quantity. Bidders are always allowed to post a bid at or below the current descending price, yet never above it.

The market reaches resolution once all cores are sold or the `reserve_price` is reached. In the former case, the `clearing_price` equals the selling price of the last unit. If cores remain unsold, the `clearing_price` is set to the `reserve_price`. This mechanism yields a uniform price that all buyers pay. Among other benefits mentioned in the Appendix, this promotes truthful bidding; the optimal strategy is to submit one's true valuation of coretime.

The `opening_price` is determined by `max(MIN_OPENING_PRICE, PRICE_MULTIPLIER * reserve_price)`. The recommendation is: `opening_price = max(150, 3 * reserve_price)`.



### Renewal Period (7 days)


The renewal period guarantees the privilege to renew current tenants' core(s), even if they did not win in the auction, submit a bid at or above the `clearing_price`, or participate at all.

Current tenants who obtain fewer cores from the market than expected have the right to renew their core(s) during the next 7 days. Once this information is known, the system can allocate all cores and assign ownership. If the combined number of renewals and auction winners exceeds the number of available cores, renewals are first served and the remaining cores are then allocated from highest to lowest bidder, until all are assigned (more information can be found in the mechanics section). With this, when demand exceeds supply (and some renewal decisions), some bidders may not receive the coretime they expected from the auction.

While this mechanism ensures that current coretime users are not suddenly left without an allocation, potentially disrupting their operations, it can distort price discovery in the open market. With this, a winning bidder may be displaced by a renewal decision.

Since bidding is straightforward and can be considered static (it requires only one transaction and is therefore trivially automated), renewals serve as a safety net and all coretime users may participate in the auction. To that end, a financial incentive to bid is introduced by increasing the renewal price to `clearing_price * PENALTY` (e.g., 30%). This penalty must be high enough to create a sufficient incentive for teams to prefer bidding over passively renewing.

:::note Penalty appplication 
The `PENALTY` applies when the number of unique bidders in the auction, plus current tenants with renewal rights, exceeds the number of available cores. If total demand is lower than the number of offered cores, the `PENALTY` is set to 0%, and renewers pay only the `clearing_price`. This reflects the expectation that the `clearing_price` will not exceed the `reserve_price`, even with all coretime consumers participating in the auction. To avoid reimbursements, the 30% `PENALTY` is automatically applied to all renewers as soon as the combined count of unique bidders and potential renewers surpasses the number of available cores.
:::

### Reserve price adjustment


After each `RENEWAL_PERIOD`, once renewal decisions are collected and cores are fully allocated, an updated `reserve_price` captures the demand in the next period. The goal is twofold: to ensure that prices adjust smoothly in response to demand fluctuations, rising when demand exceeds targets and falling when it is lower, and avoid excessive volatility from small deviations.

Let's define the following parameters:

* `reserve_price_t`: reserve price in the current period
* `reserve_price_{t+1}`: reserve price for the next period (final value after adjustments)
* `consumption_rate_t`: fraction of cores sold (including renewals) out of the total available in the current period
* `TARGET_CONSUMPTION_RATE`: target ratio of sold-to-available cores (90% is the proposal)
* `K`: sensitivity parameter that controls how the price responds to deviations (values should be between 2 and 3)
* `P_MIN`: minimum reserve price floor (one DOT, to prevent runaway downward spirals and computational issues)
* `MIN_INCREMENT`: minimum absolute increment applied when the market is saturated, for instance 100% consumption with a proposed value of 100 DOT

The price is updated according to the following rule:

```
price_candidate_t = reserve_price_t * exp(K * (consumption_rate_t - TARGET_CONSUMPTION_RATE))
```

Ensure the price does not fall below `P_MIN`:

```
price_candidate_t = max(price_candidate_t, P_MIN)
```

If `consumption_rate_t == 100%`, an additional adjustment is necessary:

```
if (price_candidate_t - reserve_price_t < MIN_INCREMENT) {
    reserve_price_{t+1} = reserve_price_t + MIN_INCREMENT
} else {
    reserve_price_{t+1} = price_candidate_t
}
```

In other words, the `reserve_price` is adjusted using the exponential scaling rule, except when consumption reaches 100% but the resulting price increase is less than `MIN_INCREMENT`. In this scenario, the fixed minimum increment is applied. This exception ensures that the system can recover more quickly from prolonged periods of low prices.

In a situation with persistently low prices, and a sudden surge in real demand, for instance full core consumption, such a jump is both warranted and economically justified.


### Settlement period / secondary market (7 days)

The seven remaining days of a sales cycle serve as the settlement period, where participants have ample time to trade coretime on secondary markets before the onset of the next `BULK_PERIOD`. This proposal makes no assumptions about the structure of these markets, as they are operated on the social layer and managed by buyers and sellers. In this context, maintaining restrictions on the resale of renewed cores in the secondary market appears unjustified, since prices are uniform and market-driven. In fact, such constraints could be harmful, for instance, if the primary market fails to achieve full efficiency. 

The proposal is to lift all restrictions on the resale or slicing of cores in the secondary market.

## Additional Considerations

### New Track: coretime admin

To enable rapid response, governance should have access to the model parameters. These include:

* `P_MIN`
* `K`
* `PRICE_MULTIPLIER`
* `MIN_INCREMENT`
* `TARGET_CONSUMPTION_RATE`
* `PENALTY`
* `MIN_OPENING_PRICE`

Such a setup should enable governance to adjust the parameters in a timely manner, within the duration of a `BULK_PERIOD`, so that changes can take effect before a new period begins.



### Transition to the new model

Upon acceptance of this RFC, the transition to the new design should be as smooth as possible.

* All teams that own cores in the current system should receive the same number of cores in the new system, with the possibility to renew them starting from the first period.
* The initial `reserve_price` should be chosen sensibly to avoid distortions in the early phases.
* A sufficient number of cores should be available on the market to ensure sufficient liquidity and enable proper price discovery.


### Some mechanics

* The price descends linearly from an `opening_price` to the `reserve_price` over the duration of the `MARKET_PERIOD`. Each discrete price level should be maintained for a long interval (for instance, six to twelve hours).
* When demand spikes after prolonged periods of low demand, which result in low reserve prices, issues can arise. In such an instance, the price between `reserve_price` and the upper bound (for example, the `opening_price`) may be lower than what many bidders are willing to pay. If this affects most participants, the demand will concentrate at the upper bound of the Dutch auction. This makes front-running a profitable strategy, either by excessively tipping bidding transactions or through explicit collusion with block producers.
Preventing the market from closing prematurely at the `opening_price` can mitigate this. Even if the demand exceeds available cores at this level, all orders are still collected. Instead of using a first-come, first-served approach, the next step is to randomize winners. Additionally, breaking up bulk orders and treating them as separate bids will give bidders interested in buying larger quantities a higher chance, avoiding all-or-nothing outcomes. These steps minimize the benefit of tipping or collusion, since bid timing no longer affects allocation. While such scenarios should be rare, this will not negatively impact current tenants who retain the safety net of renewal. The range should be wide enough to capture demand within its bounds after a few periods of maximum bids at maximum capacity.
* Granting the renewal privilege after the `MARKET_PERIOD` implies that some bidders, despite bidding above the `clearing_price`, may not receive coretime. This is justified because displacing an existing project causes more harm than temporarly preventing a new project from entering when no cores are available. Moreover, entities paying the `PENALTY` compensate for the inefficiency. The following additional rules should be put in place to resolve the allocation issues:
  1. The renewal decision of another party cannot displace bidders who already hold renewable cores.
  2. The process begins with the lowest submitted bids for those who *can* be displaced.
* If a current tenant wins cores on the market, they forfeit the right to renew those specific cores. For example, if an entity currently holds three cores and wins two in the market, it may opt to renew only one. A tenant can only increase the number of cores at the end of a `BULK_PERIOD` by acquiring them through the market.
* Bids **below** the current descending price should always be allowed. In other words, teams shouldn't have to wait idly for the price to drop to the desired target.
* Bids below the current descending price may be **raised** only up to the current clock price.
* Bids **above** the current descending price are **not allowed**. This is a key difference from a simple *kth*-price auction that helps prevent sniping.
* All cores that remain unallocated after the `RENEWAL_PERIOD` are transferred to the On-Demand Market.

### Implications

* The introduction of a single price (`clearing_price`) provides a consistent anchor for the available coretime. This serves as a safeguard against price divergence, preventing scenarios where entities acquire cores below-market rates and retain them at minimal costs.
* Considering the `PENALTY`, it is financially preferable for teams to participate in the auction. By bidding their true valuation, they maximize their chances of winning a core at the lowest possible price without incurring any penalty.
* In this design, it is impossible to "accidentally" lose cores, since renewals occur after the market phase and are guaranteed for current tenants.
* Prices within a `BULK_PERIOD` are bounded upward by the `opening_price`, which means that the maximum a renewer can pay is the `opening_price * PENALTY` within a round. With this, teams have ample time to prepare and secure the necessary funds in anticipation of potential price increases. By incorporating reserve price adjustments into their planning, teams can better anticipate future cost changes.

## Appendix

### Further discussion points

- **Reintroduction of candle auctions**: Polkadot has gathered vast experience with candle auctions, having conducted over 200 of them in the past two years. A detailed analysis of [this study](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5109856) shows that the mechanism is efficient and extracts nearly optimal revenue. This supports its use for allocating winners instead of relying on a descending clock auction, a change that affects the bidding process and winner determination. Core components like the k-th price, reserve price, and maximum price remain unaffected.

### Insights: clearing price dutch auctions
Having all bidders pay the market-clearing price offers benefits and disadvantages alike.

- Advantages:
    - **Fairness.** All bidders pay the same price.
    - **Active participation.** Since bidders are protected from overbidding (the winner's curse), they are more likely to engage and reveal their true valuations.  
    - **Simplicity.** A single price simplifies the process of pricing renewals later.
    - **Truthfulness.** There is no need to game the market by delaying bids; bidders can simply bid their true valuations.
    - **No sniping.** As prices descend, bidders cannot wait to place high bids at the end. They are only allowed to place bids at the current descending price. 
- Disadvantages:
    - **Potential lower revenue.** While theory predicts revenue-equivalence between a uniform-price and a pay-as-bid auction, slightly lower revenue has been observed for the former. Revenue maximization, or, in simple terms, squeezing out the maximum willingness to pay from bidders, is not Polkadot's priority. Instead, the focus lies on efficient allocation and the other benefits illustrated above.
    - **Technical complexity.** Instead of making a final purchase within the auction, the bid acts only as a deposit. Some refunds may occur after the auction concludes. This might pose additional technical challenges, like increased storage requirements.

### Prior art and references

This RFC builds extensively on the ideas put forward in [RFC-1](https://github.com/polkadot-fellows/RFCs/blob/6f29561a4747bbfd95307ce75cd949dfff359e39/text/0001-agile-coretime.md). 

Special thanks to [Samuel Haefner](https://samuelhaefner.github.io/), [Shahar Dobzinski](https://sites.google.com/site/dobzin/), and [Alistair Stewart](/team_members/alistair.md) for the fruitful discussions and helping to shape the structure of this RFC.

**For more information or inquieries, please contact:** [Jonas Gehrlein](/team_members/Jonas.md)