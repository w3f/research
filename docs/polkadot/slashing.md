# Slashing mechanisms

## General principles

**Security threat levels.** The yearly interest rate of a validator pool is between 10% and 20%. So, slashing 1% of their stake is already a strong punishment (worth many weeks of work). With this in mind, we define the following security threat levels and corresponding punishments. Besides the security risk, here we also consider factors like likelihood of the misconduct happening in good faith, level of coordination/correlation among validators, and computational costs for the system.

* Level 1. Misconducts that are likely to happen eventually to most validators, such as isolated cases of unresponsiveness. We slash up to 0.1% of the stake in the validator slot, or exercise non-slashing punishments only like kicking out the validator. 

* Level 2. Misconducts that can occur in good faith, but show bad practices. Examples are concurrent cases of unresponsiveness, and isolated cases of equivocation. We want culprits to seriously re-consider their practices, and we slash up to 1%.

* Level 3. Misconducts that are unlikely to happen in good faith or by accident, but do not lead to serious security risks or resource use. They show i) a concerning level of coordination/correlation among validators, ii) that the software of the validator node has been modified, iii) that a validator account has been hacked, or iv) that there is a bug in the software (if this last case is confirmed we would reimburse any slashings). Examples are concurrent cases of equivocation, or isolated cases of unjustified voting in Grandpa. We want culprits to lose a considerable amount of power, meaning both stake and reputation, and we want the punishment to work as a deterrent. We slash up to 10%.

* Level 4. Misconducts that a) pose a serious security risk to the system, b) show large levels of collusion among validators, and/or c) force the system to spend a large amount of resources to deal with them. We want the punishment to work as the worst possible deterrent, so we slash up to 100%.

**Details on how we slash validators and nominators.** When a validator is found guilty of a misconduct, we slash the corresponding validator slot (validator plus nominators) a fixed percentage of their stake (and NOT a fixed amount of DOTs). This means that validator slots with more stake will be slashed more DOTs. We do this to encourage nominators to gradually shift their support to less popular validators.

*(Q. Should we slash the validator more than his nominators? How much more? We should be careful not to bankrupt him for misconducts of levels 1 and 2).*

**Kicking out.** *Context: There is an NPoS election of candidates at the beginning of each era. Under normal circumstances, current validators are automatically considered as candidates in the next election (unless they state otherwise), and we keep the nominators' lists of trusted candidates unmodified (unless nominators state otherwise). On the other hand, unelected candidates need to re-confirm their candidacy in each era, to make sure they are online.*

When a validator is found guilty of a misconduct: 

a) We remove them from the list of candidates in the next NPoS validator election (for all misconducts).

b) We immediately mark them as inactive in the current era (for misconducts of levels 2 and up).

c) We remove them from all the nominators' lists of trusted candidates (for misconduct of levels 3 and up).

The reasons to do this are the following:

* As a punishment to the validator, as he won't be able to perform payable actions, and won't get paid while he is kicked out.

* As a safeguard to protect the system and the validator himself. If a validator node has committed a misconduct, chances are that it will do it again soon. To err on the side of security, we assume that the validator node remains unreliable until the validator gives confirmation that the necessary checks are in place and he's ready to continue operating. Furthermore, if the validator has been heavily slashed, he may decide to stop being a validator immediately, and we shouldn't assume otherwise.

* As a safeguard for nominators. If a validator is heavily slashed, we should ensure that his backing nominators are aware of this. We should wait for them to give consent that they still want to back him in the future, and not assume it.

To avoid operational issues, when a validator is kicked out we modify schemes as little as possible. The duration of the current epoch is not shortened, and for the remainder of the epoch this validator is still assigned to parachains as before, etc. In other words, kicking someone out just means marking him as inactive; we act as if that validator was non-responsive and we ignore his messages.

If a large number of validators are kicked out, or simply unresponsive, we can optionally end the era early, after the completion of an epoch, so that we can elect new validators. Or, we just wait for the end of the era; during this time finality may stop but Babe should continue going, and Grandpa will catch up at the beginning of the next era.

**Database of validators.** We need to keep a database of the current validators and previous validators. In this database, we register


* if a validator is active or inactive (kicked out),
* the misconducts that each validator has been found guilty of,
* any rewards for reporting a misconduct,
* the (weighted) nominators supporting each validator (to know who to slash/reward),
* the number of payable actions of each validator so far in the current era,
* whether that validator is the target of an ongoing challenge (for unjustified votes in Grandpa), etc.

This database should be off-chain and should *resist chain reversions*. Moreover, we should be able to see who the validators were, up to 8 weeks in the past, so that we can slash the culprits of a misconduct that is detected late (this is the same period that we freeze the nominators and validators' stake). We will also use this database to ensure that a validator is not slashed twice for the same misconduct.

Finally, we can also use this database to run an extra protocol where, if a validator has had a cumulative slashing of more than 1% for whatever reason, then we remove him from all the nominators' lists (example: if a validator is unresponsive in one era, we won't remove him from the nominators' lists, but if he is unresponsive in several eras, then we should remove him, as a safeguard to nominators.)

*(Q. How to maintain such database? How to keep it memory efficient?)*



**Detection mechanisms.** In order to slash somebody, we want to have an on-chain "attestation of misconduct" that is objective, short, and *valid on all forks*. Moreover it should remain valid in case of *chain reversion*. We also need to ensure that two attestations for the same misconduct cannot both be valid simultaneously, so that we don't punish twice for the same crime. We take care of this by using the above mentioned database.

We identify two types of detection mechanisms.

* **Proof of misconduct.** The easy case is when there is a short proof of misconduct, which can be inserted on-chain as a transaction, and whose validity can be quickly verified by the block producer (hence both producing and verifying the proof can be done efficiently). An example is equivocation in Grandpa, where a proof consists of two signed votes by the same validator in the same round.

* **Voting certificate.** When there is no proof of misconduct, we resort to a mechanism where all validators vote. At the end, we can issue a certificate of the voting decision, with the signed votes, and this can be used as an attestation of misconduct. All the mechanism occurs off-chain, with only the final certificate added on-chain. This procedure is resource expensive, so we avoid it whenever possible and use it only for level 4 misconducts. 

**Reporters and their rewards.** In general we give a reward to the actor(s) who run the protocols necessary to detect the culprits. We usually limit rewards to 10% of the total amount slashed, with the remainder going to treasury. So, if the council ever decides to reimburse a slashing event, most of the DOTS are readily available in treasury, and we only need to mint new DOTS to make up for the part that went to rewards. We consider three cases, depending on the detection mechanism and the security level.

* For levels 1 and 2, we reward around 10% of the slashed amount to whoever first submits a transaction with the proof of misconduct. The reward is expected to be pretty low, just large enough to disincentivize a "no-snitch code of honor" among validators.

* For misconducts of levels 3 and 4 that admit a proof of misconduct, we do as above, except that we only allow for *validators* to submit reports, and we require that the reward be shared among all nominators in the corresponding validator slot. We do this to dilute the reward and not let a single actor claim it, to avoid compounding wealth to a few. There may be several culprits and several reporters involved in the same mechanism (e.g. for rejecting set of votes in Grandpa); in any case, the total rewards are no more than 10% of the total slashings, and also no more than 100% of the slashed validators' self-stake. This last bound is to discourage an attack where a validator fails on purpose to have a personal gain at the expense of his nominators (e.g. if the same organization runs a validator A with 1% of self-stake and a validator B with 100% of sef-stake, it may be tempted to make B report A, if the reward is higher than A's self-stake). Finally, each validator reporter gets a reward no more than 20% of her own stake (an amount equal to her yearly interest rate), as this should be a large enough incentive.

* For level 4 misconducts that require voting, we need **fishermen**. A fisherman is any staked actor which is running checks on the system anonymously, and at some point posts a **report** as a transaction, with some details of a suspected misconduct, but without proof. In this transaction, it also bonds some stake -- the "bait". The report starts an **inspection phase** which engages some of the validators, and which may or may not lead to a full blown **voting phase** by all validators. If there is a vote and the voting decision confirms the fisherman report, the latter gets rewarded a large amount of DOTs. Otherwise, the fisherman loses all of its bait. This last possibility discourages spamming by fisherman reports, which would lead to a lot of wasted resources. On the other hand, the reward should be large enough so that it is worth the inherent risk and the cost of constantly running checks on the system. There can be several fishermen reporting the same misconduct, and we weigh the seriousness of the threat by the total amount of bait. The higher this value, the more resources are assigned in the inspection phase. The reward is shared by all the fishermen that provided reports early on, before the start of the voting phase; thus, if a single fisherman detects a misconduct, it is in its interest to convince other fishermen or validators to join in asap to inspect it. We pay fishermen: no more than 10% of all the slashings, and no more than 100% of the slashed validators' self-stake; and we pay each fisherman no more than 10 times its own bait.
 
## Network Protocol

### Unresponsiveness

We propose two different methods to detect unresponsiveness.

**Method 1.** Validators have an "I'm online" heartbeat, which is a signed message submitted on-chain every session. If a validator takes too long to send this message, we can mark them as inactive. 

The advantage of this method is that we can detect unresponsive validators very quickly, and act upon this information, for instance by ending the current era early. A disadvantage is that it only detects validators that are accidentally off-line, and not those who are purposely unresponsive as part of an attack on the system.

**Method 2.** Recall that we keep counters of all the payable actions performed by each validator (blocks produced in Babe, uncle references, validity statements), and we use these counters to compute the payouts at the end of each era. In particular, validators should be able to sign validity statements of parachain blocks consistently. Thus, we can use this counter as a measure of responsiveness. Let $c_v$ be the number of validity statements signed by validator $v$ during an era. Our proposal is to consider $v$ unresponsive if 

$$c_v < \frac{1}{4}\cdot \max_{v'} c_{v'},$$

where the maximum is taken over all validators in the same era.

**Lemma.** *No validator will be wrongfully considered unresponsive in a billion years.*

*Proof.* (We critically assume in this proof that validators are shuffled among parachains often enough so that, in every era, any two validators have the opportunity to validate a similar amount of parachain blocks, even if some parachains have a higher block production rate than others. If this assumption is incorrect, the threshold of $1/4$ can be lowered and the analysis can be adjusted accordingly.)

Fix an era, and let $n$ be the total number of parachain blocks that a validator can *potentially* validate. Being conservative, we have $n\geq 1000$ (3 blocks per minute, 60 min per hour, 6 hours per era). Now fix a responsive validator $v$, and let $p$ be the probability that $v$ successfully issues a validity statement for any of these blocks. The value of $p$ will depend on many factors, but it should be the case that $p\geq 1/2$ if $v$ is responsive. Therefore, the number $c_v$ of validity statements produced by $v$ follows a binomial distribution with expected value $p\cdot n \geq 500$. 

The crux of the argument is that this distribution is highly concentrated around its expectation. Notice that the maximum number of validity statements over all validators in this era is at most $n$. Hence, $v$ would be wrongfully considered unresponsive only if it produces $c_v < n/4\leq p\cdot n/2$ validity statements. Using Chernoff's inequality to bound the tail of the binomial distribution, we get that the probability of this occurence is at most 

$$e^{-\frac{(p\cdot n - c_v)^2}{2p\cdot n}} \leq e^{- \frac{(p\cdot n/2)^2}{2p\cdot n}} = e^{-\frac{p\cdot n}{8}}\leq e^{-\frac{500}{8}}\approx 7\cdot 10^{-28}.$$

This probability is negligible.
$\square$

We use the following slashing mechanism, which has no reporters. If at the end of an era we find that $k$ out of $n$ validators are unresponsive, then we slash a fraction

$0.05\cdot \min\{\frac{3(k-1)}{n}, 1\}$

from each one of them. Notice that this fraction is zero for isolated cases, less than one third of a percent for two concurrent cases (assuming $n\geq 50$), growing to 5% for the critical case when around 1/3 of all validators are unresponsive (we don't want to punish too harshly for concurrent unresponsiveness, as it could potentially happen in good faith. The parameter of 5% can be adjusted). We consider it a misconduct of level 1 if the slashing fraction is at most 1%, and of level 3 otherwise. However, we do not immediately remove unresponsive validators from the current era, as removing a validator is equivalent to marking it as unresponsive (so the cure would not be better than the disease), and because it is algorithmically simpler to just check at the end of each era. 
 
## Grandpa


### Unjustified vote

Relative to a block $B$ that was finalized in Grandpa round $r_B$, an unjustified vote is either a pre-vote or a pre-commit signed by a validator $v$ in some round $r_v>r_B$, for a chain that does not contain $B$. Simply put, it means voting for a chain that is incompatible with the current chain of finalized blocks. 


It follows from Grandpa paper that this can only occur if either the validator $v$ is not following the standard protocol (level 3 misconduct), or $v$ observed a *rejecting set of votes* (defined further below) for $B$ in a prior round. The detection mechanism thus works as follows. It starts when another validator $v'$ submits a transaction $T$ containing a reference to block $B$ with a proof that it is finalized, and the unjustified vote (or collection or votes in case of concurrence) relative to $B$. This transaction raises a public time-bound challenge. If the challenge goes unanswered for some time (to be defined), we slash 10% from the signer(s) of the unjustified vote(s), and reward $v'$ 10% of the slashings (as the signer(s) should be in capacity to answer the challenge if they are honest). Otherwise, any validator $v''$ can answer the challenge by, in turn, starting a detection mechanism for a *rejecting set of votes* (defined below). In that case, we finalize the current mechanism without penalizing anybody, and we keep a register of all the validators that have raised or answered challenges so far (i.e. $v'$ and $v''$), as they will all be rewarded when the culprits are eventually found.

As mentioned before, we slash 10% if a single validator is guilty of an unjustified vote. We will say more about slashing concurrent cases of unjustified votes by several validators further below. We ignore any further unjustified votes by the same validator in the same era (we will ignore all messages from that validator in the remainder of the era anyway).

### Rejecting set of votes

*Context: Recall from the Grandpa paper that a set $S$ of votes has supermajority for a block $B$ if there are $>2/3$ validators who vote in $S$ for chains that contain $B$. Similarly, we say that it is impossible for set $S$ to have supermajority for block $B$ if there are $>2/3$ validators who vote in $S$ for chains that don't contain $B$. It follows that a set $S$ has both of these properties simultaneously only when there are $>1/3$ validators that equivocate in $S$. Recall also that if block $B$ is finalized in a round $r_B$, then (assuming honest behaviors) there must be a set $V_B$ of pre-votes and a set $C_B$ of pre-commits on that round, so that both sets have supermajority for $B$. Finally, a validator $v$ considers block $B$ as finalized iff $v$ can see such a set $C_B$ of pre-commits, even if it does not yet see sufficiently many pre-votes.*

Relative to a block $B$ finalized in round $r_B$, a rejecting set of votes is a set $S$ of votes of the same type (either pre-votes or pre-commits) and on the same round $r_S\geq r_B$, for which it is impossible to have a supermajority for $B$.

Such a set implies the collusion of $>1/3$ of validators, and is one of the most dangerous attacks on the system as it can lead to finalizing blocks in different chains (see Section 4.1 in Grandpa paper). We consider it of level 4 and slash 100% from all culprits. 

The detection mechanism is somewhat involved. It starts when a validator $v$ submits a transaction $T$ containing a) the rejecting set of votes $S$ in round $r_S$, b) a reference to block $B$ together with a set $C_B$ of pre-commit votes in round $r_B$ having supermajority for $B$ (proving that $B$ was finalized), and c) a reference to a previous challenge, if the current transaction is an answer to it. We now explain how to process this transaction, depending on the value of $(r_S-r_B)$ and the type of votes in $S$.

If $r_S=r_B$ and $S$ is a set of pre-commits, then $S\cup C_B$ is a set of pre-commits which simultaneously has supermajority for $B$, and for which it is impossible to have supermajority for $B$; hence there must be $>1/3$ validators that equivocate in $S\cup C_B$, and transaction $T$ has enough information to identify them quickly. We slash 100% from all equivocators.

If $r_S=r_B$ and $S$ is a set of pre-votes, transaction $T$ raises a time-bound challenge which can be answered by any validator, and where a valid answer consists of a new transaction $T'$ containing a) a set $V_B$ of pre-votes in round $r_B$ which has supermajority for $B$, and b) a reference to $T$. If a validator $v'$ provides such answer, then $S\cup V_B$ is a set of pre-votes which simultaneously has supermajority for $B$, and for which it is impossible to have supermajority for $B$. As before, there must be $>1/3$ validators that equivocate in this set, and we slash all of them  100%. If nobody answers the challenge within a specified period of time, we slash 100% from all the validators that voted in set $C_B$, because each one of them should be in capacity to answer the challenge immediately (and be rewarded if they are the first to do so) if they are honest.

Finally, if $r_s>r_B$, transaction $T$ raises a time-bound challenge which can be answered by any validator, and where a valid answer consists of a new transaction $T'$ containing a) set $C_B$ and a reference to block $B$, b) a set $S'$ of votes of the same type (either pre-votes or pre-commits) and on the same round $r_{S'}$ for some $r_B\leq r_{S'}<r_S$ for which it is impossible to have a supermajority for $B$, and c) a reference to $T$. If a validator $v'$ provides such a transaction $T'$, we remark that $S'$ is a rejecting set of votes relative to $B$, so the whole detection mechanism performs a new iteration. As the value of $(r_s-r_B)$ decreases with every iteration, the mechanism must eventually stop. In contrast, if nobody answers the current challenge within a specified period of time, we slash 100% from all validators that voted in set $S$, because each one of them should be able to answer the challenge if they are honest (proved in Lemma 4.2 of Granpa paper).

Throughout the iterations, we only need to keep track of what the current challenge is, and the list of validators who have raised or answered previous challenges, as we will reward them all at the end.

*(Q. What to do in the case that such a chain of challenges eventually targets a group of validators from a previous era, who are not currently validators (nor online) anymore?)*

### Equivocation / concurrent cases of unjustified vote

An equivocation is defined as a validator signing two or more votes in the same round, for the same vote type (either pre-vote or pre-commit). It admits a short proof of misconduct consisting of two signed votes. Notice that a set of votes proving multiple equivocations can be submitted in a single transaction.

A validator can equivocate by mistake (for an isolated case) if the nodes are run in several computers and there is imperfect coordination between them, so we consider it a level 2 misconduct. We ignore any additional equivocations by the same validator in the same era.

In every era, we will keep a counter $k$ on the number of validators that committed Grandpa equivocations or unjustified votes so far. We keep a single counter for both misconducts because an adversary might use a combination of both to attack the finality tool, so several concurrent cases of both misconducts should be considered as a single collusion attack. We now describe a slashing mechanism that depends on this counter, and which is used for isolated and concurrent cases of equivocation, and also for concurrent cases of unjustified vote. In the last case, this slashing occurs in addition to the slashing described in the corresponding section above.

Suppose that a new proof of misconduct arrives for equivocation or unjustified vote, raising the current counter to $k$. We slash each culprit a proportion of their stake equal to

$$\min\{(3k/n)^2, 1\},$$

where $n$ is the number of validators. Notice that this amount starts small, under 0.4% for an isolated case (for $n\geq 50$), and rises quadratically to 100% when $k$ approaches the critical value $n/3$. Once the slashed fraction goes above 1%, we consider it of level 3.

The rewards given to the reporters do not grow with $k$. Namely, they receive 10% of what would have been the slashing for $k=1$ (times the number of reported validators). This ensures that a reporter has no incentive to withold information in wait for the counter $k$ to go higher. Also, for operational convenience we do not retro-actively slash culprits as new cases of concurrence arrive. This could also give an economical incentive to a member of a colluding party to report themselves early on, to be slashed less.

### Invalid vote

*Context: in our current protocol for validating parachain blobs, we make a distinction between **minimally validated** blobs (having, say, one or two validity statements) and **fully validated** blobs (having a certain minimum number of votes, say five, where this minimum increases if there are fishermen reports about that blob). We allow Babe block producers to include references of minimimally validated blobs, but in contrast we only allow Grandpa voters to vote for relay chain blocks that contain only fully validated blobs (we call such a block a validated block).*

An invalid vote is defined as a vote (either pre-vote or pre-commit) for a chain that contains a non-validated block, i.e. a block which contains a reference to a parachain blob that is not fully validated.

For the time being we propose not to slash this misconduct, because it does not lead to a dangerous attack, assuming an honest majority of Grandpa voters, and because there does not seem to be an efficient detection mechanism. 

As a safeguard, we only advise adjusting the Grandpa protocol so that each voter keeps track of the validity status of all relay chain blocks (and of all parachain blobs), and that by default a voter A ignores any vote from a voter B for a chain which, from the point of view of A, contains non-validated blocks. Similarly, a Granpa voter should ignore any vote that is either currently being challenged or found to be faulty, by a procedure of unjustified vote or rejecting set of votes (see sections above).

## Babe

### Babe Equivocation

An equivocation in Babe corresponds to a block producer producing two or more relay chain blocks in the same time slot. It admits a short proof of misconduct containing references to both blocks. It can occur in good faith if a validator node is run in several computers and there is bad coordination among them, so we consider it of level 2. We ignore additional equivocations by the same validator in the same era.

Equivocations do not pose a threat to Babe, unless there is a long sequence of colluding block producers who grow two branches of a fork simultaneously, but such an attack is highly unlikely to succeed as long as the colluding party is a minority. For this reason, we propose to disregard concurrent equivocations in the same era. Alternatively, we could keep a counter $k$ on the number of block producers that have equivocated so far in the current era, and slash new culprits a fraction of their stake equal to 

$$\min\{(3k/n)^2, 1\},$$

where $n$ is the number of validators. Once this fraction is above 1%, we consider it of level 3. We do not retro-actively adjust the slashings as new cases arrive, and we do not make the reporters' rewards grow with $k$ (we pay them 10% of what would be the slashing if $k=1$.)

### Invalid Block

An invalid block can occur, for instance, if the block producer adds a reference to a parachain blob which has no validity statements. Invalid blocks do not pose a threat to Babe, unless there is a large fraction of block producers who decide to build on top of an invalid block, but this attack is unlikely to succeed. For this reason, we suggest not to slash this misconduct.

If we eventually decide to have a slashing mechanism, we could either have all validators vote on the validity of the block. Alternatively, a block producer can include the whole invalid block in a new block, as proof of misconduct. 

## Parachain validity-availability protocol

### Invalid validity statement

This misconduct is defined as a parachain validator who issues a validity statement for an invalid blob. This misconduct poses the highest security risk, especially in case of concurrence, and unfortunately it does not admit a proof of misconduct, so we are forced to deal with it via a voting mechanism. We consider it a level 4 misconduct and slash 100%.

The detection mechanism is as follows. Inspection phase: in the current standard protocol, Babe block producers will add references to *minimally validated* blobs (having one validity statement). After a blob has been added to a relay chain block, the protocol will randomly select some extra validators to check the blob and provide more validity statements, until there are sufficiently many statements to make the blob *fully validated*. If one or more fishermen submit reports with a reference to certain blob, the protocol automatically adjusts, making the bar to get fully validated higher and selecting more validators to inspect that blob. These validators get paid for issuing these extra validity statements, as these are payable actions, but only the validators selected by the protocol have the right to issue them. On the other hand, fishermen are checking for the validity of blobs all the time.

Voting phase: the voting phase starts as soon as there is at least one statement of validity and one statement of invalidity issued by validators for the same blob. This can happen before or after the blob is referred to in a Babe block (if before, the inspection phase is skipped; and in any case, fishermen reports are ignored once there is a statment of invalidity). When a validator sees a statement of validity and a statement of invalidity for a blob, she inspects it as well and issues a statement, so eventually most of the relay chain validators will vote (and will get paid for it as payable actions). We count the number of statement of validity, and the number of statements of invalidity: as soon as one of these numbers is $>n/3$ (where $n$ is the number of validators), and the other is not, we take the plurality vote as official. If it is decided that the blob is invalid, we slash all validators that stated otherwise and we reward all fishermen; if it is decided that the blob is valid, we slash fishermen and all validators that stated otherwise. 

If it happens that both the number of statements of validity and the number of statements of invalidity are $>n/3$, we unfortunately don't know who the culprits are (this should never happen). In this case we slash no-one (and reimburse any slashing done), and consider the blob as invalid to err on the safe side.

