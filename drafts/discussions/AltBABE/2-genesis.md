
## Genesis Phase

We shall manually produce a genesis block from which the chain begins.  In this genesis block, we specify an initial random number $r_1$ for use during the first epoch for slot leader assignments, the initial stake's $b_j$ of the stake holders and their corresponding session public keys $V_j$, and account public keys $A_j$

We might reasonably set \(r_1 = 0\) for the initial chain randomness, by assuming honesty of all validators listed in the genesis block.  We could use public random number from the Tor network instead however.

In our approach with a VDF below, there is an implicit commit and reveal phase provided some suffix of our genesis epoch consists of *every* validator producing a block and *all* produced blocks being included on-chain, which one could achieve by adjusting paramaters.

