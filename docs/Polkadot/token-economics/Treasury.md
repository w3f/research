---
title: Treasury
---

**Authors**: [Alfonso Cevallos](/team_members/alfonso.md), [Jonas Gehrlein](/team_members/Jonas.md)

**Last Updated**: October 17, 2023


The system needs to continually raise funds, which we call the treasury. These funds are used to pay for developers that provide software updates, apply any changes decided by referenda, adjust parameters, and generally keep the system running smoothly.

Funds for treasury are raised in two ways:

1.   by minting new tokens, leading to inflation, and
2.   by channelling the tokens from transaction fees and slashings, which would otherwise be set for burning.

Notice that these methods to raise funds mimic the traditional ways that governements raise funds: by minting coins which leads to controlled inflation, and by collecting taxes and fines.

We could raise funds solely from minting new tokens, but we argue that it makes sense to redirect into treasure the tokens from tx fees and slashing that would otherwise be burned:

- By doing so we reduce the amount of actual stake burning, and this gives us better control over the inflation rate (notice that stake burning leads to deflation, and we can’t control or predict the events that lead to burning).

- Following an event that produced heavy stake slashing, goverance might often want to reimburse the slashed stake partially, if there is a bug in the code or there are extenuating circumstances. Thus it makes sense to have the DOTs availabe in treasury, instead of burning and then minting.

- Suppose that there is a period in which there is an unusually high amount of stake burning, due to either misconducts or transaction fees. This fact is a symptom that there is something wrong with the system, that needs fixing. Hence, this will be precisely a period when we need to have more funds available in treasury to afford the development costs to fix the problem.
