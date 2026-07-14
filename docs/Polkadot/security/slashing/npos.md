---
title: Slashing Across Eras with NPoS
---
<!--![](Slashing-with-NPoS.png)-->

The slashing algorithm must be both fair and effective. To achieve this, slashing should respect nominators' exposure, be resistant to Sybil attacks, and maintain monotonicity.

# Reduced rewards

## Slashing within one era

In any era $e$, a fixed amount of stake, also referred to as base exposure, denoted by $x_{\eta,\nu,e}$, is assigned by a nominator $\eta$ to a validator $\nu$. Slashing should never exceed a nominators' exposure, as doing so incentivizes fragmentation of stash keys. Encouraging such Sybil-like behavior within Polkadot undermines fairness and distorts insights into nominator behavior. 

The first step is to remove any validator $\nu$ immediately upon being slashed, which prevents repeated slashing beyond that block height. However, an inconsistency arises when $\nu$ commits multiple violations before the chain acknowledges the slash and removes them. This can introduce significant randomness into slashing penalties, increasing the governance workload and reducing slashing fairness. Additionaly, $\nu$ might equivocate retroactively, potentially to extort their own nominators.  As a countermeasure, if the system slashes validator $\nu$ in era $e$ for several distinct proportions $p_i$, then $p_{\nu,e} := \max_i p_i$ can ensure that nominator $\eta$ is only slashed by $p_{\nu,e} x_{\eta,\nu,e}$.

As an aside, one could define $p_{\eta,\nu,e}$ throughout to allow different slashing rates across nominators. For example, slashing the validator more heavily, i.e., $p_{\nu,\nu,e} > p_{\eta,\nu,e}$ for $\nu \ne \eta$. This approach, however, is problematic as validators can always nominate themselves.

Although there are minimal concerns about multiple misbehaviors by the same validator $\nu$ within a single era, in such cases, the slashing mechanism could combine them before computing the individual slashing proportions $p_i$.  In other words, $p_{\nu,e} \ge \max_i p_i$ with equality by default. Yet, strict inequality may occur for certain combinations of $p_i$. This could complicate cross-era logic, although such issues can be addressed by considering the specific nature of each misbehavior.

In essence, the definition $p_{\nu,e} := \max_i p_i$ provides a default mechanism that is simple, fair, and commutative for combining slashes within a single era. Alternative logic remains possible, as long as the resulting slash is independent of the order in which offenses are detected. Future slashing logic may incorporate additional factors, so using $\max_i p_i$ here retains flexibility for future enhancements.


Misbehaviors from different validators $\nu \ne \nu'$ present a separate concern. This is both because nomination must be resistant to Sybil attacks and because correlated slashing events may involve multiple validators.  Therefore, if $N_{\eta,e}$ denotes the set of validators nominated by $\eta$ in era $e$, then the total slash applied to $\eta$ when multiple validators $\nu \in N_{\eta,e}$ are slashed is:

$$
\sum_{\nu \in N_e} p_{\nu,e} x_{\eta,\nu,e}
$$

## Slashing in past eras

As hinted above, it would be misleading to assume that all events warranting the slashing of a particular stash account are detected early or occur within the same era.  If $e$ and $e'$ are distinct eras, then $x_{\eta,\nu_j,e} \ne x_{\eta,\nu_j,e'}$, and thus the previous arguments no longer hold.  In fact, summing slashes applied to different validators could quickly exceed the nominators exposure $x_{\eta,\nu,e}$.

One might assume that $\min \{ x_{\eta,\nu_j,e}, x_{\eta,\nu_j,e'} \}$ represents the "same" stake across eras, but this assumption offers limited practical benefit. The suggestion, therefore, is to slash $\eta$ the amount

$$
\max_e \sum_{\nu \in N_e} p_{\nu,e} x_{\eta,\nu,e}
$$

where $N_e$ denotes the set of validators nominated by $\eta$ in era $e$

An extortion attack remains plausible: an adversary could run many poorly staked validators, attract nominations, and then threaten nominators with slashing.  While such attacks cannot be entirely prevented, the outer $\max_e$ helps mitigate the impact of compounded slashing across different eras.

## Slashing spans

Hitherto, slashing has been kept relatively simple, addressing some fairness concerns through the outer maximum $\max_e \cdots$. This simplicity introduces another issue:  if $\nu$ is slashed once, they may subsequently commit similar offenses without further consequences, an outcome neither fair nor effective.  As previously noted, this can occur within a single era due to validator removal upon slashing. Yet, nominators may continue to support multiple validators across eras. To eliminate this impunity and reduce ongoing risk to the network, an additional mechanism is required.

The problem may be resolved by limiting the eras spanned by the outer maximum to explicit ranges $\bar{e}$. Termination occurs following an era $e \in \bar{e}$ in which any slashing events for that span $\bar{e}$ are detected. Concretely, the eras associated with a nominator $\eta$ are divided into _slashing spans_, maximal contiguous sequence of eras $\bar{e} = \left[ e_1, \ldots, e_n \right]$ such that $e_n$ is the earliest era in which $\eta$ is slashed for actions commited in one of the $e_i \in \bar{e}$.

Offences are then summed across slashing spans.  In other words, if $\bar{e}$ ranges over the slashing spans for $\eta$, then the total amount slashed from $\eta$ is:
$$
\sum_{\bar{e} \in \bar{E}} \max_{e \in \bar{e}} \sum_{\nu \in N_e} p_{\nu,e} x_{\eta,\nu,e} \tag{\dag}
$$
In particular, if $\eta$ is slashed in epoch 1 with the detection occurring in epoch 2, nomination resumes in epoch 3, and only then is $\eta$ slashed again for actions commited in epoch 1 and 2. These later slashes are counted as part of the same slashing span, originating from $\eta$'s initial slash in epoch 1. Any slash occurring in epoch 3 is treated as a new event and initiates a fresh slashing span.

Slashing Span Lemma.  Any slashing span-like construction must terminate whenever slash is detected.

Proof.  Let $x'$ be the validators' minimum self-exposure, and let $y$ be the total stake required to become a validator.  Suppose a nominator $\eta_1$ nominates validators $\nu_e$ for $e=1\ldots$, using their account with stake $y-x'$. In epoch $e-1$, each $\nu_i$ stakes enough to become a validator in epoch $e$, with $\nu_1$ staking only $x'$ and $\nu_i$ for $i>1$ slightly more.  

Now, suppose $\nu_i$ commits a violation in epoch $i$. If the system does not end $\eta_1$'s slashing span $\bar{e}$, then the rule $max_{e \in \bar{e}}$ would prevent subsequent slashing events from further penalizing $\eta_1$.  As a result, a planned series of violations across epochs would only slash a fraction $x' / y$ of the intended penalty, undermining the effectiveness of the slashing mechanism.
$$
\tag{$\blacksquare$}
$$
<br/>
<br/>

Many design choices constrain this lemma to some extent, but they also make slashing fragile, complicating analysis and reducing composability.

## Actions

Several additional mechanisms are triggered whenever a validator $\nu$ causes the slashing of a nominator $\eta$. Among other considerations, these mechanisms help mitigate reenlistment mistakes that nominators may occasionally make.

The first step then is to post a slashing transaction to the chain, which removes the offending validator $\nu$ from the active validator set by invalidating either their controller key or, potentionally, just their session keys. As a result, all nodes ignore $\nu$ for the rest of the era. Any future blocks that fail to ignore $\nu$ are considered invalid. All nomination approval votes by any nominator for $\nu$ are also removed, including those currently allocating $\nu$ zero stake.

Nominator $\eta$ is handled with less urgency. The slashing accounting is updated only when the offense occurred in a past slashing span for $\eta$, meaning it is not necessary to terminate their current span. In the more typical case, where the offense occurrs during $\eta$'s currently active slashing span, that span is terminated at the end of the current era, and a new slashing span begins for $\eta$.

Nominator $\eta$ is then _suppressed_, which partially suppresses all of $\eta$'s nomination approval votes for future eras. $\eta$'s current nominations for the ongoing era are not suppressed or removed, and the stake currently backing other validators remains unaffected.  In principle, it is possible to suppress $\eta$'s nomination approval votes whenever they are slashed in a previous slashing span. This seems to be unnecessary, as suppression is primarily tied to the termination of a slashing span.

Additionally, $\eta$ can update their nomination approval votes for future eras during the current or any subsequent era. Doing so removes them from the suppressed state. $\eta$ also receives a notification indicating that validator $\nu$ caused them to be slashed and suppressed.

These state changes help reduce the risk of unintentional reenlistment by nominators, while also balancing systemic risks to the network.  In particular, they provide justification for treating any future nominations by $\eta$ separately from those made in the current or previous eras.

## Accounting

Slashing is not permitted for any events occurring beyond the unbonding period, and slashing records must expire once this period has elapsed. Slashing spans help address this requirement by tracking the maximum slash $s_{\eta}$ within each span. This value can be updated whenever a new slash increases the span's maximum. The $s_{\eta}$ is referenced again below in reward computations.

As an aside, consider an alternative accounting strategy. By recording all slashing events along with a value $s_{\eta,\nu,e}$, it is possible to represent the amount actually slashed at time $e$.  If $e'>e$, then the initial slash is recorded as

$$
s_{\eta,\nu,e} := p_{\nu,e} x_{\eta,\nu_j,e}
$$

at time $e$. A subsequent lesser slash is then recorded as 

$$
s_{\eta,\nu,e'} := p_{\nu,e'} x_{\eta,\nu_j,e'} - p_{\nu,e} x_{\eta,\nu_j,e}
$$  

at time $e'$. These $s_{\eta,\nu,e}$ values allow slashes to expire without unfairly increasing future slashes. The added complexity and storage overhead does not enhance network security and may exacerbate extortion attacks against nominators.

## Monotonicity

Slashing must be monotonically increasing for all parties, ensuring that validators cannot reduce a nominator's penalty through additional misbehavior.  In other words, the amount any nominator is slashed can only increase with more slashing events, even those involving the same validator but different nominators.

Fairness demands this condition; otherwise, validators could manipulate slashing to benefit favored nominators, typically by increasing the penalties applied to others. Trusted Execution Environments (TEE) can help prevent such manipulation, but not all validators are expected to use them.

Monotonicity can be achieved with ($\dag$), since both summation and maximum operations are monotonically increasing over the positive real numbers, assuming that any logic to adjust $p_{\nu,e}$ also preserves monotonicity.

The diversity of nominators who may nominate a particular validator during the unbonding period is unlimited.  As a direct consequence of monotonicity, nearly all nominators can be slashed simultaneously, even if only one validator is penalized. This opens the door to "rage quit attacks," where a widely trusted validator retroactively introduces equivocations that implicate many nominators. As a result, the total stake destroyed by a combined slashing event, though far below the total stake of the network, cannot be reliably bounded.

Moreover, validators can retroactively validate invalid blocks, which results in a 100% slash.  While it may be possible to reduce the severity of slashes for older offenses if they are truly uncorrelated, in case of correlation, only governance can intervene by searching historical logs to identify the invalid block hash.

## Suppressed nominators in Phragmen

The slashing span $\bar{e}$ for a nominator $\eta$ is defined to end in the era $e$ during which the chain can detect and acknowledge a slashing event within $\bar{e}$. Under this definition all of $\eta$'s nomination approval votes, for any validator, should be _suppressed_ after the era $e$ that concludes a slashing span $\bar{e}$. The notion of suppression itself has not been formally defined, though.

Let $\xi$ be the _suppression factor_, a recently introduced network parameter.  Let $s_{\eta,\bar{e}}$ denote the amount slashed from nominator $\eta$ during slashing span $\bar{e}$, and let $E$ represent the set of slashing spans $\eta$ within the unbonding period during which $\eta$ has not updated their nominations.  When $\eta$ is marked as suppressed, a portion of their stake in Phragmen, specifically $\xi \sum_{\bar{e} \in E} s_{\eta,\bar{e}}$ of $\eta$'s, is ignored.

If suppression has no effect ($\xi = 0$), then at the next epoch, $\eta$ enters a new slashing span by the Slashing Span Lemma, risking additive slashing. This is problematic for several reasons:  

* First, $\eta$'s judgement is flawed, and they should reassess the risks associated with their vote, for both their own sake and the network's integrity.  
* Second, $\eta$ could be slashed multiple times if reports are prompt, but only once if reports are delayed, creating a perverse incentive to delay reporting.  
* Additionally, intermittent bugs could trigger slashes.

If suppression removes all $\eta$'s nominations ($\xi = \infty$), then $\eta$ remains completely safe. However, widespread slashing could eliminate large amounts of stake from the system if many nominators are slashed nearly simultaneously, even by small amounts.  If these nominators fail to renominate quickly, a significant portion of the total stake becomes suppressed, unlike the "rage quit attacks" that monotonicity enables. This poses a risk, as an adversary could suddenly control more than one-third of the stake.

A suppression factor of $\xi = 1$ or $2$ sounds reasonable, as values of $\xi > 2$ may conflict with the protocol's assumption of two-thirds honest participation. Conversely, when $\xi < 0.5$, issues similar to those at $\xi = 0$ arise, though no intuitive arguments currently support this threshold.

The computation $\xi \sum_{\bar{e} \in E} s_{\eta,\bar{e}}$ is intentionally simple. This allows governance to dinamically adjust $\xi$ to reintroduce suppressed stake in the event of an emergency.  While the code could theoretically modify $\xi$ automatically, this appears unnecessary and offers little practical benefit.


## Rewards for slashable offense reports

Interestingly, monotonicity also places constraints on the reward structure for offense reports that lead to slashing. For example, if a validator $\nu$ is slashed, they could freely equivocate again and report themselves in an attempt to recover some of the slashed value. To prevent this exploit, slashing must always penalize the validator's self-stake by an amount greater than any reward granted for the report.

### Rewards based on slashing nominators

An inefficient straw-man proposal describes issuing rewards based upon slashing nominators.

Let $f_\infty$ be the maximum proportion of a slash that can ever be paid out, presumably with $f_\infty < 0.1$. Let $f_1 \le {1\over2}$ represent the proportion of $f_\infty$ paid out initially upon first offence detection. A fresh slash of value $s$ then results in a payout of $f_\infty f_1 s$. Define $f_0 := {1-f_1 \over f_1} f_\infty$ so that $f_\infty = {f_1 \over 1-f_1} f_0$.

Consider a slash of value $s := p_{\nu,e} x_{\eta,\nu,e}$ applied to the nominator $\eta$.  Let $s_{\eta,i}$ and $s_{\eta,i+1}$ denote $\eta$'s actual slash in slashing span $\bar{e}$, given by 

$$
\max_{e \in \bar{e}} \sum_{\nu \in N_e} p_{\nu,e} x_{\eta,\nu,e}
$$ 

before and after applying the new slash, respectively. Thus, $\eta$'s slash increases by $s_{\eta,i+1} - s_{\eta,i}$.

Track the value $s_{\eta,i}$ in $\eta$'s slashing span record, along with another value $t_{\eta,i} < s_{\eta,i}$ representing the total amount paid out so far.  If $s_{\eta,i+1} > s_{\eta,i}$, then the pay out is

$$
r := f_1 (f_0 s_{\eta,i+1} - t_{\eta,i}),
$$ 

increasing $t_{\eta,i}$ by this amount.  If $s_{\eta,i+1} = s_{\eta,i}$, then the payout is $r := f_1 \max(f_0 s - t_{\eta,i},0)$.  

In either case, the updated value stored is $t_{\eta,i+1} := t_{\eta,i} + r$.

In this way, validator $\nu$ cannot reclaim more than $f_{\infty} f_1 s$ from a slash of value $s$, even through repeated equivocations. For this reason, the product $f_{\infty} f_1$ should remain below the required self-stake.  Any slash of size $s_{\eta,i}$ always results in some payout, yet slashes smaller than $t_{\eta,i}$ never trigger a payout.

### Rewards based on slashing only validators

Since the above reward scheme requires both accounting for all impacted nominators $\eta$ during payouts and enforcing the constraint that $f_{\infty} f_1$ remains below the valitor's self-stake, the proposal is to compute rewards only for validators who are directly slashed. This approach requires validators to always be slashed whenever their nominators are slashed, meaning a validator cannot be slashed 100% unless all of their nominators are also slashed 100%.

Let $x'$ denote the minimum self-exposure (i.e., stake) that validator operators must provide, such that $x_{\nu,\nu,e} \ge x'$.  As a simplifying assumption, $f_\infty$ should be kept small enough to ensure that rewards are always covered by validators' self-exposure, i.e., 

$$
x' \ge f_{\infty} \sum_\eta x_{\eta,\nu,e}
$$  

Cases where this condition fails are not explored further here. Addressing such scenarios would require a more nuanced definition of $x' > x_{\nu,\nu,e}$ to ensure that reward payouts do not introduce inflationary pressure.

Define $f' > f_0$ such that $f' x' = {1-f_1 \over f_1} f_{\infty} x_{\min}$ where $x_{\min} = \sum_\eta x_{\eta,\nu,e}$ represents the required minimum total stake for any validator.  In the revised scheme, replace $f_{\infty}$ with $f'$, and apply payouts to slashes against the validator operator's minimum exposure $x'$. This means replacing the slash value $p_{\nu,e} x_{\eta,\nu,e}$ with $\max_{e \in \bar{e}} p_{\nu,e} x'$.

A slash of value $s := p_{\nu,e} x_{\nu,\nu,e}$ is applied to validator $\nu$. The _minimum validator adjusted slash_ value $s' := p_{\nu,e} x'$ represents the fraction of this slash applied to the minimum validator stake $x'$. The _total minimum validator-adjusted slash_, given by $\max_{e \in \bar{e}} p_{\nu,e} x'$, serves as an analog to total regular slashes, but considers only the validator's own exposure.

The next step is to let $s^\prime_{\nu,i}$ and $s^\prime_{\nu,i+1}$ denote validator $\nu$'s total validator-adjusted slash within their slashing span $\bar{e}$, before and after applying the new slash, respectively. When the total validator-adjusted slash increases, the change is given by

$$
s^\prime_{\nu,i+1} - s^\prime_{\nu,i} = \max(s^\prime - s^\prime_{\nu,i},0).
$$

Now, track the value $s^\prime_{\nu,i}$ in validator $\nu$'s slashing span record, along with another value $t_{\nu,i} < s^\prime_{\nu,i}$, which represents the total payout issued so far.  If $s^\prime_{\nu,i+1} > s^\prime_{\nu,i}$, then the payout is $r := f_1 (f' s^\prime_{\nu,i+1} - t_{\nu,i})$ and $t_{\eta,i}$ increases by this amount.  If $s^\prime_{\nu,i+1} = s^\prime_{\nu,i}$, then the payout is $r := f_1 \max(f' s' - t_{\nu,i},0)$.  In both cases, the system stores the updated value $t_{\nu,i+1} := t_{\nu,i} + r$.

In this way, validator $\nu$ cannot reclaim more than $f' f_1 s$ from a slash of value $s$, even through repeated equivocations.  Any slash of size $s_{\nu,i}$ always results in some payout, but slashes smaller than $t_{\nu,i}$ do not trigger additional rewards.

Both schemes yield similar payouts initially, but the second scheme, where rewards are based only on validator slashes, results in smaller payouts when cross-era slashing logic is applied. For instance, if validator $\nu$ receives similar slashes across multiple epochs, the $r_1$ factor reduces the total reward under the validator-only scheme. Still, if $\nu$ has disjoint nominators in each epoch, the impact of the $r_1$ factor is minimal.


**For further questions and inquieries, please contact:** [Jeffrey Burdges](/team_members/jeff.md)


