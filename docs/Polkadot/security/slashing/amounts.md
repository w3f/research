---
title: Slashing Mechanisms
---

<!--![](Slashing-mechanisms.jpeg)-->

## General principles

To define appropriate slashing amounts, it is important to understand the annual earnings of validators. Validator pool interest rates typically range between 10% and 20%. Therefore, slashing just 1% of a validator's stake already represents a significant penalty, roughly equivalent to several weeks of earnings. 

**Security threat levels.** With this in mind, it is necessary to define security threat levels and corresponding punishments. In addition to assessing the severity of the security risk, it is also important to consider factors such as the likelihood of the misconduct occurring in good faith, the degree of coordination or correlation among validators, and the computational costs imposed on the system.

* Level 1: misconduct likely to eventually occur among most validators, for example isolated cases of unresponsiveness. The penalty involves slashing up to 0.1% of the stake in the validator slot, or applying non-slashing punishments such as removing the validator from the set.

* Level 2: misconduct that may occur in good faith but reflects poor practices. Examples include concurrent cases of unresponsiveness and isolated instances of equivocation. The goal is to promt culprits to seriously reconsider their behavior, so the slashing amount can be up to 1%.

* Level 3: misconduct unlikely to happen in good faith or by accident, yet not serious enough to pose security risks or consume significant system resources. Such cases may indicate i) a concerning level of coordination or correlation among validators, ii) modification of the validator node software, iii) a compromised validator account, or iv) a bug in the software (if confirmed, any slashing is reimbursed). Examples include concurrent cases of equivocation, or isolated instances of unjustified voting in GRANDPA. In such cases, validators should lose a substantial amount of both stake and reputation, with punishments designed as a deterrent. The slashing amount can be up to 10%.

* Level 4: misconduct that i) poses a serious security risk to the system, ii) involves significant collusion among validators, and/or iii) requires the system to expend considerable resources to address. Punishments at this level should serve as the strongest possible deterrent, with slashing amounts of up to 100%.

**Details on slashing validators and nominators.** When a validator is found guilty of misconduct, the corresponding validator slot (which includes the validator and their nominators) is slashed by a fixed percentage of their stake, not a fixed amount of DOT. This means that validator slots with larger stakes will incur greater losses in DOT. The goal is to incentivize nominators to gradually shift their support to less popular validators.

:::note Question
Should the validator be slashed more heavily than their nominators? If so, by how much? Care must be taken to avoid bankrupting validators for Level 1 and Level 2 misconducts.*

**Kicking out.** 
At the beginning of each era, an NPoS election is held to select validator candidates. Under normal circumstances, current validators are automatically considered candidates for the next election (unless they opt out), and nominators' lists of trusted candidates remain unchanged unless explicitly modified. In contrast, unelected candidates must reconfirm their candidacy in each era to ensure they are online and active.
:::

When a validator is found guilty of misconduct:

a) The system removes them from the list of candidates in the next NPoS validator election. This applies to all levels of misconduct.

b) The system marks them as inactive for the current era. This applies to level 2 misconduct and beyond.

c) The system deletes them from all nominators' lists of trusted candidates. This applies to level 3 misconduct and above.

Rationale for these actions:

* **Punishment for the validator.** The validator loses the ability to perform payable actions and will not receive rewards while excluded.

* **System and validator protection.** If a validator node has committed misconduct, there is a high likelihood it may do so again. To err on the side of caution, assume the node remains unreliable until the validator confirms all necessary checks are complete and is ready to resume operations. Additionaly, if the validator has been heavily slashed, they may choose to exit the role immediately; no further assumptions should be made about their continued participation.

* **Protection for nominators.** In cases of heavy slashing, nominators should be aware. Their continued support should not be assumed; instead, explicit consent should be obtained before allowing them to back the validator again.

To minimize disruption, validator removal should involve minimal changes to existing schemes. The duration of the current epoch remains unchanged, and the system continues to assign the validator to parachains for the rest of the epoch. In practice, being "kicked out" simply means that the validator is inactive and non-responsive, and that all their messages are ignored.

If a large number of validators are kicked out, or become unresponsive, the era may end early, after the completion of an epoch, to allow for the election of new validators. Alternatively, the system may wait until the end of the era. During this time, Finality may pause, while BABE continues producing blocks. GRANDPA can catch up at the beginning of the next era.

**Validators database.** This off-chain database tracks both current and past validators and should include: 

* whether a validator is active or inactive (i.e., kicked out)
* the misconduct each validator has been found guilty of
* any rewards issued for reporting a misconduct
* the (weighted) nominators supporting each validator, to determine who the system should slash or reward
* the number of payable actions each validator performs in the current era
* whether a validator is the target of an ongoing challenge (e.g., for unjustified votes in GRANDPA)
* other relevant metadata

This database must be off-chain and designed to *resist chain reversions*. It should retain visibility into validator history for up to eight weeks, enabling slashing of validators for misconduct detected after the fact. This retention period aligns with the freeze duration for nominators' and validators' stakes. Additionally, the database must ensure the system does not slash validators more than once for the same misconduct.

Finally, the database should support an auxiliary protocol: if a validator accumulates more than 1% slashing, regardless of the reason, they should be removed from all the nominators' lists. For example, a validator who is unresponsive in a single era may not be removed, but repeated unresponsiveness over several eras should trigger removals as a safeguard for nominators.

:::note Question
How can such a database be efficiently maintained while keeping memory usage low?
:::

**Detection mechanisms.** To slash a validator, the system requires an objective on-chain "attestation of misconduct." This must be short, *valid on all forks*, and remain valid even in the event of a *chain reversion*. Two attestations for the same misconduct cannot be valid simultaneously, preventing double punishment for a single offense. The previously mentioned database plays a key role in supporting this logic.

There are two types of detection mechanisms:

* **Proof of misconduct.** This is the straighforward case, where a concise proof of misconduct can be submitted on-chain as a transaction. The block producer can quickly verify the proof's validity, making both the generation and verification of the proof efficient. A typical example is equivocation in GRANDPA, where the proof consists of two signed votes by the same validator in the same round.

* **Voting certificate.** When no direct proof is available, a collecting voting mechanism is used. Validators vote off-chain, and a certificate of the final decision (containing the signed votes) is issued and submitted on-chain as the attestation of misconduct. This procedure is resource-intensive; hence, it applies only to level 4 misconduct and avoided whenever possible.

**Reporters and their rewards.** In general, rewards are available for actors who execute the protocols necessary to detect misconduct. These rewards are capped at 10% of the total amount slashed, with the rest allocated to the treasury. Should the council choose to reimburse a slashing event, sufficient DOT is typically available in the treasury, and only a small portion may need to be minted to cover the reward payout. Depending on the detection mechanism and the security level, the system considers three reward scenarios:

* **Levels 1 and 2.** The first party to submit a valid transaction with proof of misconduct earns a reward of approximately 10% of the slashed amount. The reward is intentionally modest, just enough to discourage a "no-snitch code of honor" among validators.

* **Levels 3 and 4 (with proof of misconduct).** The same procedure applies, but only *validators* are allowed to submit reports. All nominators share the reward in the corresponding validator slot to prevent wealth concentration. A single misconduct case (e.g., rejecting a set of GRANDPA votes) may involve multiple culprits and reporters. Regardless, total rewards must not exceed 10% of the total slashed amount, nor exceed 100% of the slashed validators' self-stake. This cap prevents an attack scenario where a validator intentionally fails to benefit at the expense of their nominators. For example, if an entity runs Validator A with 1% self-stake and Validator B with 100%, it might be tempted to have B report A if the potential reward exceeds A's self-stake. Additionally, each validator reporter may receive a reward no greater than 20% of their own stake, roughly equivalent to their annual interest rate, ensuring the incentive remains meaningful but not excessive.

* **Level 4 misconduct requiring voting.** In this case **fishermen**, staked actors who anonymously monitor the system, play a critical role. At some point, a fisherman may submit a  **report** as a transaction, detailing suspected misconduct, but without providing direct proof. Along with the report the fisherman bonds a portion of their stake, referred to as the "bait." This report initiates an **inspection phase**, during which a subset of validators conduct an investigation. Depending on the outcome, this may escalate into a full **voting phase** involving all validators. If the vote confirms the fisherman's report, the fisherman is rewarded with a substantial amount of DOT. If the report is rejected, the fisherman forfeits their bait. This penalty discourages spam reports, which would otherwise waste system resources. At the same time, the reward must be high enough to justify the risk and the ongoing cost of running system checks. Multiple fishermen may report the same misconduct. In such cases, the seriousness of the threat is gauged by the total amount of bait bonded. The higher the total bait, the more resources are allocated during the inspection phase. The system distributes rewards to all fishermen who submited reports before the voting phase begins. Therefore, if a single fisherman detects misconducts, it is in their interest to quickly rally other fishermen or validators to join the inspection. Fishermen rewards are capped at:
  * no more than 10% of all the total slashed amount 
  * no more than 100% of the slashed validators' self-stake
  * no more than 10 times the fisherman's own bait. 

## Network protocol

### Unresponsiveness

Two types of detection mechanisms are in place for identifying unresponsiveness.

**Method 1.** Validators submit an "I'm online" heartbeat, a signed message posted on-chain every session. If a validator takes too long to submit this message, the system marks them as inactive.

The advantage of this method is that it enables rapid detection of unresponsive validators, allowing the system to act quickly, for example by ending the current era early. A disadvantage is that it only identifies validators who are accidentally offline, not those who are deliberately unresponsive as part of a coodinated attack.

**Method 2.** The system tracks counters for all payable actions performed by each validator (e.g., blocks produced in BABE, uncle references, validity statements, etc.). These counters are used to calculate payouts at the end of each era. In particular, validators are expected to consistently sign validity statements for each parachain block. This counter serves as a measure of responsiveness. Let $c_v$ be the number of validity statements validator $v$ signs during an era. Validator $v$ is considered unresponsive if:

$$
c_v < \frac{1}{4}\cdot \max_{v'} c_{v'}
$$

where the maximum is taken over all validators in the same era.

**Lemma.** *No validator will be wrongfully considered unresponsive in a billion years.*

:::note Assumption
Validators are shuffled among parachains frequently enough that, in every era, any two validators have the opportunity to validate a similar number of parachain blocks, even if some parachains produce blocks at a higher rate than others. If this assumption does not hold, the threshold of $1/4$ can be lowered, and the analysis adjusted accordingly.
:::

**Proof.** Fix an era, and let $n$ be the total number of parachain blocks a validator can *potentially* validate. Conservatively, take $n\geq 1000$, based on 3 blocks per minute, 60 minutes per hour, and 6 hours per era. Consider a responsive validator $v$, and let $p$ be the probability that $v$ successfully issues a validity statement for any given block. Although $p$ depends on many factors, assume $p\geq 1/2$ for a responsive validator. Then the number $c_v$ of validity statements that $v$ produces follows a binomial distribution with expected value $p\cdot n \geq 500$.

This distribution is tightly concentrated around its expectation. The maximum number of validity statements across all validators in the era is at most $n$. Hence, validator $v$ would be wrongfully considered unresponsive only if it produces fewer than $c_v < n/4\leq p\cdot n/2$ validity statements. Applying Chernoff's inequality to bound the tail of the binomial distribution yields:

$$
e^{-\frac{(p\cdot n - c_v)^2}{2p\cdot n}} \leq e^{- \frac{(p\cdot n/2)^2}{2p\cdot n}} = e^{-\frac{p\cdot n}{8}}\leq e^{-\frac{500}{8}}\approx 7\cdot 10^{-28}
$$

This probability is negligible, confirming the claim.
$$
\tag{$\blacksquare$}
$$
<br/>
<br/>

The following slashing mechanism operates without reporters. If at the end of an era $k$ out of $n$ validators are unresponsive, then the system slashes the fraction

$$
0.05\cdot \min\{\frac{3(k-1)}{n}, 1\}
$$

from each of them. This fraction is zero in isolated cases, less than one-third of a percent for two concurrent cases (assuming $n\geq 50$), and increases to 5% in the critical scenario where approximately one-third of all validators are unresponsive. The intention is to avoid overly harsh penalties for concurrent unresponsiveness, which may occur in good faith. The 5% parameter  can be adjusted as needed. Misconduct is classified as Level 2 if the slashing fraction is at most 1%, and as Level 3 otherwise. Unresponsive validators, however, are not removed immediately during the current era. Removing a validator is equivalent to marking them as unresponsive, which would not improve the situation. Additionally, it is algorithmically simpler to perform these checks at the end of each era.

## GRANDPA


### Unjustified vote

Relative to a block $B$ finalized in GRANDPA round $r_B$, an unjustified vote is defined as either a prevote or a precommit that a validator $v$ signs in some round $r_v>r_B$, for a chain that does not include $B$. Simply put, it refers to voting for a chain incompatible with the current chain of finalized blocks.


According to the GRANDPA paper, this behavior can only occur under two conditions: either the validator $v$ is not following the standard protocol (classified as Level 3 misconduct), or $v$ has observed a *rejecting set of votes* (defined further below) for block $B$ in a prior round. The detection mechanism thus operates as follows. It begins when another validator $v'$ submits a transaction $T$. This transaction includes a reference to block $B$, proof that $B$ is finalized, and the unjustified vote (or a collection of votes, in case of concurrence) associated with $B$. 

This transaction initiates a public, time-bound challenge. If the challenge goes unanswered within a specified time frame, the system slashes 10% of the stake from the signer(s) of the unjustified vote(s), on the assumption that honest signers should be able to respond. Validator $v'$ is then rewarded with 10% of the slashed amount. Alternatively, any validator $v''$ may respond to the challenge by initiating a detection mechanism for a *rejecting set of votes* (defined below). In this case, the current mechanism ends without penalizing anyone, and the system keeps a record of all validators who have raised or answered challenges (i.e., $v'$ and $v''$). The system will reward these validators once the actual culprits are identified.

As previously mentioned, a 10% slash is applied if a single validator is found guilty of an unjustified vote. Additionaly, below you can find details about slashing in cases of concurrent unjustified votes by multiple validators. The same validator faces no additional penalty for further unjustified votes in that era, and the system disregards all their subsequent messages for the rest of the era.

### Rejecting a set of votes

:::note Context 
According to the GRANDPA paper, a set $S$ of votes has supermajority for a block $B$ if more than $2/3$ of validators in $S$ vote for chains that contain $B$. Similarly, it is impossible for set $S$ to have supermajority for $B$ if more than $2/3$ of validators vote for chains that don't contain $B$. Therefore, a set $S$ can exhibit both properties simultaneously only if more than $1/3$ of validators equivocate within $S$.
 
If block $B$ is finalized in a round $r_B$, and assuming honest behavior, there must exist a set $V_B$ of prevotes and a set $C_B$ of precommits in that round, both forming a supermajority for $B$. A validator $v$ considers block $B$ finalized if it can observe such a set $C_B$ of precommits, even if it has not yet seen a sufficient number of prevotes.
:::

Relative to a block $B$ finalized in round $r_B$, a rejecting set of votes is defined as a set $S$ of votes of the same type (either prevotes or precommits), cast in the same round $r_S\geq r_B$, for which it is impossible to achieve a supermajority for $B$.

Such a set implies collusion among more than $1/3$ of validators and represents one of the most dangerous attacks on the system, as it can lead to the finalization of blocks on conflicting chains (see Section 4.1 of the [GRANDPA paper](http://localhost:3000/Polkadot/protocols/finality)). This is classified as a Level 4 misconduct, with a 100% slash applied to all culprits.

The detection mechanism begins when a validator $v$ submits a transaction $T$ containing: a) the rejecting set of votes $S$ from round $r_S$, b) a reference to block $B$, along with a set $C_B$ of precommit votes from round $r_B$ demonstrating supermajority for $B$ (proving its finalization), and c) a reference to a previous challenge, if the current transaction is a response to one. 

The next step is to explain how to process this transaction, depending on the value of $(r_S-r_B)$ and the type of votes contained in $S$. If $r_S=r_B$ and $S$ is a set of precommits, then $S\cup C_B$ forms a set of precommits that has a supermajority for block $B$, yet for which it is impossible to achieve a supermajority for $B$. This contradiction implies that more than $1/3$ of validators must have equivocated within $S\cup C_B$, and transaction $T$ contains sufficient information to identify them efficiently. All equivocators will be slashed 100%. If $r_S=r_B$ and $S$ is a set of prevotes, transaction $T$ initiates a time-bound challenge that any validator may respond to. A valid answer consists of a new transaction $T'$ containing: a) a set $V_B$ of prevotes from round $r_B$ with supermajority for $B$, and b) a reference to $T$. 

If a validator $v'$ submits such a response, then the combined set $S\cup V_B$ simultaneously satisfies two contradictory conditions: it has a supermajority for $B$, and it is impossible to have a supermajority for $B$. This implies that more than $1/3$ of validators must have equivocated within the set, and all such validators are slashed 100%. 

If no validator responds to the challenge within the specified time window, the system slashes 100% of the stake of all validators who voted in set $C_B$. This is because each of them, assuming honest behavior, should be able to respond to the challenge immediately, with the first one to do so receiving the reward. 

If $r_s>r_B$, transaction $T$ raises a time-bound challenge that any validator may answer. A valid response consists of a new transaction $T'$ containing: a) the set $C_B$ and a reference to block $B$, b) a set $S'$ of votes of the same type (either prevotes or precommits), cast in the same round $r_{S'}$ for some $r_B\leq r_{S'}<r_S$, for which it is impossible to have a supermajority for $B$, and c) a reference to $T$. If a validator $v'$ submits such a transaction $T'$, then $S'$ constitutes a rejecting set of votes relative to $B$, and the detection mechanism proceeds to a new iteration. Since the value of $(r_s-r_B)$ decreases with each iteration, the process must eventually stop. In contrast, if no validator responds to the challenge within the specified time frame, the system slashes 100% of the stake of all validators who voted in set $S$, as each of them should be able to respond to the challenge if they are honest (as demonstrated in Lemma 4.2 of the GRANDPA paper).

Throughout the iterations, it is sufficient to track the current challenge and maintain the list of validators who have raised or answered previous challenges, as the system will reward them at the end of the process.

:::note Question
What should be done if such a chain of challenges eventually targets a group of validators from a previous era who are no longer active (i.e., not currently validators or online)?
:::

### Equivocation / concurrent cases of unjustified vote

An equivocation refers to a validator signing two or more votes in the same round for the same vote type (either prevote or precommit). It admits a short proof of misconduct consisting of two signed votes. A set of votes proving multiple equivocations may be submitted in a single transaction.

A validator may accidentally equivocate in isolated cases. For example, if the nodes are run on multiple computers with imperfect coordination. Such cases are considered Level 2 misconduct. The system ignores additional equivocations by the same validator within the same era.

In each era, a counter $k$ can track the number of validators who have committed GRANDPA equivocations or unjustified votes. A single counter is used for both types of misconducts, as an adversary may combine them to attack the finality mechanism. A single collusion event may involve multiple concurrent cases of either or both types of misconduct. The slashing mechanism described below depends on this counter and applies to isolated and concurrent cases of equivocation, as well as concurrent cases of unjustified vote. In the latter case, this slashing applies on top of the penalties described in the relevant section above.

Suppose a new proof of misconduct is submitted, either for equivocation or unjustified voting, raising the current counter to $k$. Each culprit is then slashed by a proportion of their stake equal to

$$
\min\{(3k/n)^2, 1\}
$$

where $n$ is the total number of validators. This amount starts small, under 0.4% for an isolated case (assuming $n\geq 50$), and increases quadratically to 100% as $k$ approaches the critical threshold of $n/3$. Once the slashed fraction exceeds 1%, the system classifies the misconduct as Level 3.

Reporter rewards do not scale with $k$. Specifically, reporters receive 10% of what the slashing would have been for $k=1$, multiplied by the number of reported validators. This ensures that reporters have no incentive to withhold information while waiting for the counter to increase. For operational simplicity, culprits are not retroactively slashed as new cases of concurrence arise. This design may also incentivize members of a colluding group to self-report early, thereby receiving a reduced penalty. 

### Invalid vote

:::note Context
In the current protocol for validating parachain blobs, there is a distinction between **minimally validated** blobs (having, for example, one or two validity statements) and **fully validated** blobs (having a certain minimum number of votes, say five, which increases if there are fishermen reports concerning that blob). BABE block producers may include references to minimimally validated blobs, but GRANDPA voters can only vote for relay chain blocks that contain exclusively fully validated blobs (referred to as validated blocks).
:::

An **invalid vote** is defined as a vote, either prevote or precommit, for a chain that includes a non-validated block, i.e., a block referencing a parachain blob that has not been fully validated. At present, this form of misconduct is not subject to slashing, as it does not pose a serious threat (assuming an honest majority among GRANDPA voters) and due to the lack of an efficient detection mechanism.

As a safeguard, the GRANDPA protocol should be adjusted so that each voter tracks the validity status of all relay chain blocks (and all parachain blobs). By default, a voter *A* should ignore any vote from a voter *B* for a chain that, from *A*'s perspective, contains non-validated blocks. Similarly, a GRANDPA voter should disregard any vote that is currently challenged, or that a procedure has deemed faulty, whether through unjustified votes or a rejected set of votes (see the relevant sections above).

## BABE

### BABE equivocation

An equivocation in BABE occurs when a block producer generates two or more relay chain blocks within the same time slot. This misconduct admits a concise proof of misconduct consisting of references to both blocks. It may happen in good faith, if a validator node runs across multiple machines with poor coordination, so the system classifies it as Level 2. It then ignores any additional equivocations by the same validator within the same era.

Equivocations do not pose a significant threat to BABE unless a long sequence of colluding block producers simultaneously extends two branches of a fork. Such an attack is highly unlikely to succeed as long as the colluding party remains a minority. For this reason, the proposal is to disregard concurrent equivocations within the same era. Alternatively, a counter $k$ could track the number of block producers who committed equivocations in the current era. The system slashes new culprits by a fraction of their stake equal to:

$$
\min\{(3k/n)^2, 1\}
$$

where $n$ is the total number of validators. Once this fraction exceeds 1%, the misconduct is classified as Level 3. Slashings are not retroactively adjusted as new cases arise, and reporter rewards do not scale with $k$. Specifically, reporters receive 10% of what the slashing would have been for $k=1$.

### Invalid block

An invalid block can occur, for instance, when a block producer includes a reference to a parachain blob that lacks any validity statements. Invalid blocks do not pose a threat to BABE unless a large fraction of block producers choose to build on top of such a block. This type of attack, however, is unlikely to succeed. For this reason, this misconduct is not currently subject to slashing.

If a slashing mechanism is eventually required, one option would be for all validators to vote on the validity of the block. Alternatively, a block producer could include the entire invalid block in a new block as proof of misconduct.

## Parachain validity-availability protocol

### Invalid validity statement

This misconduct is defined as a parachain validator issuing a validity statement for an invalid blob. It poses the highest security risk, especially in case of concurrence, and unfortunately does not admit a direct proof of misconduct. As a result, the only viable response is through a voting mechanism. This is classified as Level 4 misconduct and subject to a 100% slash.

The detection mechanism comprises two phases. Inspection phase: in the current standard protocol, BABE block producers include references to *minimally validated* blobs (i.e., blobs with one validity statement). Once a blob is added to a relay chain block, the protocol will randomly select additional validators to inspect the blob and issue further validity statements. This process continues until the blob becomes *fully validated*. 

If one or more fishermen submit reports referring to a specific blob, the protocol automatically raises the threshold for full validation and selects more validators to inspect that blob. These validators are compensated for issuing additional validity statements, as these are considered payable actions. However, only those validators the protocol selects may issue them. In contrast, fishermen continously monitor the validity of blobs independently.

Voting phase: begins as soon as validators have issued at least one validity statement and one invalidity statement for the same blob. This can occur either before or after the blob is referenced in a BABE block. If it occurs beforehand, the inspection phase is skipped. In any case, fishermen reports are ignored once a statment of invalidity has been issued.

When a validator sees both a validity statement and an invalidity statement for a blob, they inspect the blob and issue their own statement. Eventually, most relay chain validators will participate in the vote and will be compensated for doing so, as these are considered payable actions. By counting the number of validity statements and the number of invalidity statements, as soon as one of these counts exceeds $n/3$ (where $n$ is the number of validators), and the other does not, the plurality vote becomes official. 

* if the blob is deemed invalid, the system slashes all validators who stated otherwise, and rewards for fishermen become available 

* if the blob is deemed valid, the system slashes both the fishermen and the validators who stated otherwise.

If both the number of validity statements and the number of invalidity statements exceed $n/3$, there is unfortunately no way to determine who the culprits are. In such a case, which by the way should never occur,  no slashes apply, any prior slashing is reimbursed, and the blob is considered invalid to err on the side of caution.

**For further questions and inquiries please contact:** [Jeffrey Burdges](/team_members/jeff.md)

