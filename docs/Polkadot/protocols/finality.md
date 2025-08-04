---
title: Finality
---

import useBaseUrl from '@docusaurus/useBaseUrl';

Owner: [Alistair Stewart](/team_members/alistair.md)

![](Grandpa.png)

GRANDPA is the finality (consensus) algorithm used in Polkadot. To get started, you can read our "extended abstract," which provides a high-level overview. If you're eager to dive deeper into the technical details, feel free to skip ahead to the full paper just below. And as bonus, there is a more polished and slightly shorter version of the full paper available on [arxiv](https://arxiv.org/abs/2007.01560). 

"Polite GRANDPA" is the implementation of GRANDPA used in the Polkadot software and deployed in practice.  It includes optimizations tailored for efficient real-world performance in practise, which are not covered in the papers below for the sake of brevity, You can find the [details](#polite-grandpa) later on this page. The high-level concepts and design principles remain consistent with GRANDPA.

## GRANDPA Abstract paper
<iframe width="100%" height="800" src={useBaseUrl('/pdf/GRANDPAabstract.pdf')} />

## GRANDPA Full paper
<iframe width="100%" height="800" src={useBaseUrl('/pdf/grandpa.pdf')} />

## Polite GRANDPA


