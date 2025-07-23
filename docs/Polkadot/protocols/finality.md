---
title: Finality
---

import useBaseUrl from '@docusaurus/useBaseUrl';

Owner: [Alistair Stewart](/team_members/alistair.md)

![](Grandpa.png)

GRANDPA is the finality (consensus) algorithm for Polkadot. Here we first
present a high-level overview, as an "extended abstract". Details are presented
in the full paper directly below that.

We also have an [alternative version](https://arxiv.org/abs/2007.01560) of the
full paper available on arxiv, which is more polished and a bit shorter.

What is implemented in the Polkadot software and deployed in practise, we refer
to as "Polite GRANDPA" which includes optimisations required for efficient
real-world performance in practise. These are not covered in the papers below
for brevity, but we go into [the details](#polite-grandpa) later here on this
page. The high-level concepts and design principles remain the same as GRANDPA.

## GRANDPA Abstract paper
<iframe width="100%" height="800" src={useBaseUrl('/pdf/GRANDPAabstract.pdf')} />

## GRANDPA Full paper
<iframe width="100%" height="800" src={useBaseUrl('/pdf/grandpa.pdf')} />

## Polite GRANDPA


