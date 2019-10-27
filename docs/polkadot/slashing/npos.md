# Slashing across eras with NPoS

Authors:  Jeffrey Burdges, Robert Habermeier, Alfonso Cevallos, (and Alistair Stewart once he reviews it closely)


We need our slashing algorithm to be fair and effective.  We discuss how this means slashing must respect nominators' exposure, be anti-Sibel, and be monotonic. 

TODO:  Anything about era boundaries?

## Reduced rewards

TODO:  How small should a slash be to ignore the slashing span system?

## Slashing within one era

In any era $e$, there is a fixed amount of stake aka base exposure $x_{\eta,\nu,e}$ assigned by any nominator $\eta$ to any validator $\nu$.  We demand that slashing never exceeds nominators' exposure because doing so creates an incentive to break up stash keys.  We avoid encouraging such Sibel-ish behavior in Polkadot because doing so makes Polkadot less fair and harms our information about nominator behavior.

We immediately remove any validator $\nu$ whenever they gets slashed, which prevents repeated slashing after that block height.  There is however an inconsistency in that $\nu$ might commit multiple violations before the chain acknowledges the slash and kicks $\nu$.  We fear this introduces significant randomness into our slashing penalties, which increases governance workload and makes the slashing less fair.  We also worry that $\nu$ might equivocate retroactively, perhaps to extort their own nominators.  As a counter measure, if era $e$ sees validator $\nu$ slashed for several distinct proportions $p_i$, then we define $p_{\nu,e} := \max_i p_i$ and slash their nominator $\eta$ only $p_{\nu,e} x_{\eta,\nu,e}$.  

<small>As an aside, we could write $p_{\eta,\nu,e}$ throughout if we wanted to slash different nominators differently, like by slashing the validator themselves more, i.e. $p_{\nu,\nu,e} > p_{\eta,\nu,e}$ for $\nu \ne \eta$.  We abandoned this idea because validators could always be their own nominators.</small>

We actually have only minimal concerns about multiple miss-behaviours from the same validator $\nu$ in one era, but if we discover some in future then the slashing lock could combine them before producing these $p_i$.  In other words, $p_{\nu,e} \ge \max_i p_i$ with equality by default, but a strict inequality remains possible for some $p_i$ combinations.  We expect this would complicate cross era logic, but such issues should be addressed by considering the specific miss-behaviour.  

In essence, this $p_{\nu,e} := \max_i p_i$ definition provides default mechanism for combining slashes within one era that is simple, fair, and commutative, but alternative logic remains possible so long as we slash the same regardless of the order in which offenses are detected.  We emphasise that future slashing logic might take numerous factors into consideration, so doing $\max_i p_i_$ here retains the most flexibility for future slashing logic.


We do however worry about miss-behaviours from different validators $\nu \ne \nu'$ both because nomination must restrict Sibels and also because correlated slashing need not necessarily involve the same validators.  We therefore let $N_{\eta,e}$ denote the validators nominated by $\eta$ in era $e$ and slash $\sum_{\nu \in N_e} p_{\nu,e} x_{\eta,\nu,e}$ from $\eta$ when multiple validators $\nu \in N_{\eta,e}$ get slashed.

## Slashing in past eras

As hinted above, we cannot assume that all events that warrant slashing a particular stash account get detected early or occur within the same era.  If $e$ and $e'$ are distinct eras then we expect $x_{\eta,\nu_j,e} \ne x_{\eta,\nu_j,e'}$ so the above arguments fail.  Indeed, we cannot even sum slashes applied to different validators because doing so could quickly exceeds nominators exposure $x_{\eta,\nu,e}$.

We might assume $\min \{ x_{\eta,\nu_j,e}, x_{\eta,\nu_j,e'} \}$ to be the "same" stake, but this does not obviously buy us much.  We therefore suggest slashing $\eta$ the amount
$$ \max_e \sum_{\nu \in N_e} p_{\nu,e} x_{\eta,\nu,e} $$
where again $N_e$ is the validators nominated by $\eta$ in era $e$

In particular, there is still an extortion attack in which someone runs many poorly staked validators, receives nominations, and then threatens their nominators with being slashed.  We cannot prevent such attacks entirely, but this outer $\max_e$ reduces the damage over formula that add slashing from different eras.

## Slashing spans

We thus far kept our slashing relatively simple and fixed some fairness issues with the outer maximum $\max_e \cdots$, but created another problem:  If $\nu$ gets slashed once, then $\nu$ could thereafter commit similar offenses with impunity, which is neither fair nor effective.  As noted above, we accept this within a single era because validators get removed when they get slashed, but across eras nominators can support multiple validators.  We therefore need another mechanism that removes this impunity to minimize any further risks to the network going forwards. 

We propose to limit the eras spanned by this outer maximum to an explicit spans $\bar{e}$ that end after an eras $e \in \bar{e}$ in which any slashing events for that span $\bar{e}$ gets detected.  In concrete terms, we partition the eras of some nominator $\eta$ into _slashing spans_ which are maximal contiguous sequence of eras $\bar{e} = \left[ e_1, \ldots, e_n \right]$ such that $e_n$ is the least era in which $\eta$ gets slashed for actions in one of the $e_i \in \bar{e}$.  

We shall sum offences across slashing spans.  In other words, if we $\bar{e}$ range over the slashing spans for $\eta$ then we have slashed $\eta$ in total  
$$ \sum_{\bar{e} \in \bar{E}} \max_{e \in \bar{e}} \sum_{\nu \in N_e} p_{\nu,e} x_{\eta,\nu,e} \tag{\dag} $$
In particular, if $\eta$ gets slashed in epoch 1 with the detection occurring in epoch 2, then resumes nomination in epoch 3, and only then gets slashed again for actions in epoch 1 and 2, then these later slashes are counted as part of the same slashing span as $\eta$'s first slash from epoch 1, but any slash in epoch 3 count afresh in a new span that gets added.  

Slashing Span Lemma.  Any slashing span-like construction must end whenever we detect some slash.  

Proof.  Let $x'$ be the validators' minimum self exposure and let $y$ be the stake to become a validator.  Some nominator $\eta_1$ nominates validators $\nu_e$ for $e=1\ldots$ with her account of $y-x'$ stake.  In epoch $e-1$, $\nu_i$ stakes enough to become a validator in epoch $e$, so $\nu_1$ stakes only $x'$ and $\nu_i$ for $i>1$ stakes somewhat more.  In epoch $i$, $\nu_i$ commits a violation.  If we did not end $\eta_1$'s slashing span $\bar{e}$ then then $max_{e \in \bar{e}}$ rule would prevent these slashes from actually slashing $\eta_1$ further.  In this way, a planned series of violations causing slashes across epochs only actually slashes $x' / y$ of the desired slash value.  $\square$

There are many design choices that restrain this lemma somewhat, but they make our slashing fragile, which harms our analysis and compossibility. 

## Actions

We now detail several additional actions taken whenever some validator $\nu$ causes the slashing of some nominator $\eta$.  Among other concerns, these help mitigate reenlistment mistakes that nominators would occasionally make.

We first post a slashing transaction to the chain, which drops the offending validator $\nu$ from the active validator list by invalidating their controller key, or maybe just their session keys.  In consequence, all nodes ignore $\nu$ for the remainder of the era.  It invalidates any future blocks that do not ignore $\nu$ too.  We also remove all nomination approval votes by any nominator for $\nu$, even those who currently allocate $\nu$ zero stake.  

We handle the nominator $\eta$ less speedily though.  We merely update the slashing accounting below when the offense occurred in some past slashing span for $\eta$, meaning we need not end their current slashing span.  We go further assuming the usual case that the offense occurred in $\eta$'s currently running slashing span though:  We terminate $\eta$'s current slashing span at the end of the current era, which should then start a new slashing span for $\eta$.  

We also mark $\eta$ _suppressed_ which partially _suppresses_ all of $\eta$'s nomination approval votes for future eras.  We do not suppress or remove $\eta$'s current nominations for the current era or reduce the stake currently backing other validators.  In principle, we could suppresses $\eta$'s nomination approval votes somewhat whenever $\eta$ gets slashed in previous slashing spans, but doing so appears unnecessary because suppression really comes only as part of ending a slashing span. 

Also, we permit $\eta$ to update their nomination approval votes for future eras during the current or future era, but doing so removes them from the aka suppressed state.  We also notify $\eta$ that $\nu$ cause them to be slashed and suppressed.  

These state alterations reduce the risks of unintentional reenlistment of any nominator, while also balancing risks to the network.  In particular, these measures provide justification for treating any future nominations by $\eta$ separately from any that happen in the current era or before.

## Accounting

We cannot slash for anything beyond the unbonding period and must expire slashing records when they go past the unbonding period.  We address this easily thanks to slashing spans:  We track the maximum slash $s_{\eta}$ within each slashing span, which we update anytime a slash raises the slashing span's maximum slash.  We shall use $s_{\eta}$ again below in rewards computations. 

As an aside, there was another accounting strategy here:  Record all slash events along with some value $s_{\eta,\nu,e}$ recording the amount actually slashed at that time.  If $e'$ is later than $e$ then we record the initial slash $s_{\eta,\nu,e} := p_{\nu,e} x_{\eta,\nu_j,e}$ at $e$ and record a lesser slash $s_{\eta,\nu,e'} := p_{\nu,e'} x_{\eta,\nu_j,e'} - p_{\nu,e} x_{\eta,\nu_j,e}$ at the later $e'$.  These $s_{\eta,\nu,e}$ values permit slashes to expire without unfairly increasing other slashes.  We believe this extra complexity and storage, does not improve network security, and strengthens extortion attacks on nominators.

## Monotonicity

We ask that slashing be monotonic increasing for all parties so that validators cannot reduce any nominator's slash by additional miss-behavior.  In other words, the amount any nominator gets slashed can only increase with more slashings events, even ones involving the same validator but not the same nominator.

We think fairness imposes this condition because otherwise validators can reduce the slash of their favoured nominators, normally by making other nominators be slashed more.  We know trusted computing environments (TEE) avoid this issue, but we do not currently foresee requiring that all validators use them.

We have achieved monotonicity with ($\dag$) because summation and maximums are monotonically increasing  over the positive real numbers, assuming any logic that adjusts the $p_{\nu,e}$ also adheres to monotonicity.

There are no meaningful limits on the diversity of nominators who nominated a particular validator within the unbonding period.  As a direct consequence of monotonicity, almost every nominators can be slashed simultaneously, even if only one validator gets slashed.  In particular, there are "rage quit attacks" in which one widely trusted validator adds past equivocations that cover many nominators.  We therefore cannot bound the total stake destroyed by a combined slashing event much below the slash applied to the total stake of the network.

In particular, we cannot prevent validators from retroactively validating invalid blocks, which causes a 100% slash.  We could reduce these high slashes from old offenses if truly uncorrelated, but if correlated then only governance could interveen by searching historical logs for the invalid block hash.

## Suppressed nominators in Phragmen

Above, we defined a slashing span $\bar{e}$ for a nominator $\eta$ to end after the era $e$ during which a slashing event during $\bar{e}$ gets detected and acknowledged by the chain.  We asked above that all $\eta$'s nomination approval votes, for any validator, should be _suppressed_ after the era $e$ that ends a slashing span $\bar{e}$, but never defined suppressed.  

We introduce a network paramater $\xi$ called the _suppression factor_.  We let $s_{\eta,\bar{e}}$ denote the value slashed from nominator $\eta$ in slashing span $\bar{e}$.  We also let $E$ denote the slashing spans of $\eta$ within the unbonding period, or possibly some shorter duration.  We now ignore $\xi \sum_{\bar{e} \in E} s_{\eta,\bar{e}}$ of $\eta$'s stake in Phragmen when $\eta$ is marked as suppressed. 

If suppression does nothing ($\xi = 0$), then at the next epoch $\eta$ enters a fresh slashing span by the Slashing Span Lemma, and risks additive slashing.  We consider this problematic for several reasons:  First, we consider $\eta$'s judgement flawed, so they should reevaluate their votes' risks, both for themselves and the network's good.  Second, $\eta$ could easily be slashed several times if reports are prompt, but only once if reports are delayed, which incentivizes delaying reports.  Also, slashes could be caused by intermittent bugs.

If suppression removes all $\eta$'s nominations ($\xi = \infty$), then $\eta$ remains completely safe, but widespread slashing could remove massive amounts of stake from the system if many nominators get slashed nearly simultaneously, perhaps only by some small amount.  If these fail to renominate quickly, then much of the total stake invested by nominators becomes suppressed, not unlike the "rage quit attacks" enabled by monotonicity.  We consider this problematic because an adversary might suddenly control more than one third of the stake.

We think $\xi = 1$ or $2$ sounds reasonable.  We suspect $\xi > 2$ meshes poorly with our 2/3rds honest assumption elsewhere.  At some point $\xi < 0.5$ creates similar issues to $\xi = 0$, but no intuitive arguments present themselves. 

We have intentionally kept the above computation $\xi \sum_{\bar{e} \in E} s_{\eta,\bar{e}}$ extremely simple so that $\xi$ can dynamically be changed by governance to reintroduce suppressed stake in an emergency.  We code could change $\xi$ automatically but doing so appears pointless.

TODO:  Import any discussion from Alfonso's text

## Rewards for slashable offense reports

Interestingly, we find that monotonicity also constrains our rewards for offense reports that result in slashing:  If a validator $\nu$ gets slashed, then they could freely equivocate more and report upon themselves to earn back some of the slashed value.  

### Rewards based on slashing nominators

We define $f_\infty$ to be the maximum proportion of a slash that ever gets paid out, presumably $f_\infty < 0.1$.  We also define $f_1 \le {1\over2}$ to be the proportion of $f_\infty$ paid out initially on the first offence detection.  So a fresh slash of value $s$ results in a payout of $f_\infty f_1 s$.  Set $f_0 := {1-f_1 \over f_1} f_\infty$ so that $f_\infty = {f_1 \over 1-f_1} f_0$.

We consider a slash of value $s := p_{\nu,e} x_{\eta,\nu,e}$ being applied to the nominator $\eta$.  We let $s_{\eta,i}$ and $s_{\eta,i+1}$ denote $\eta$'s actual slash in slashing span $\bar{e}$ given by $\max_{e \in \bar{e}} \sum_{\nu \in N_e} p_{\nu,e} x_{\eta,\nu,e}$ before and after applying the new slash, respectively, so when $\eta$'s slash increases by $s_{\eta,i+1} - s_{\eta,i}$.

We track the value $s_{\eta,i}$ in $\eta$'s slashing span record, but we also track another value $t_{\eta,i} < s_{\eta,i}$ that represents the total amount paid out so far.  If $s_{\eta,i+1} > s_{\eta,i}$ then we pay out $r := f_1 (f_0 s_{\eta,i+1} - t_{\eta,i})$ and increase $t_{\eta,i}$ by this amount.  If $s_{\eta,i+1} = s_{\eta,i}$ then we pay out $r := f_1 \max(f_0 s - t_{\eta,i},0)$.  In either case, we store $t_{\eta,i+1} := t_{\eta,i} + r$.

In this way, our validator $\nu$ cannot reclaim more than $f_{\infty} f_1 s$ from a slash of value $s$, even by repeatedly equivocations.  Any slash of size $s_{\eta,i}$ always results in some payout, but slashes less than $t_{\eta,i}$ never pay out.

### Rewards based on slashing only validators

We dislike that the above reward scheme requires considering all impacted $\eta$ when doing payouts, so we propose to compute rewards only for validators being slashed instead.  We shall require that validators always get slashed whenever their nominators get slashed, which means validators cannot be slashed 100% without their nominators all also being slashed 100%.

We have some minimum exposure aka stake $x'$ that validator operators must provide themselves, meaning $x_{\nu,\nu,e} \ge x'$.  As a simplifying assumption, we ask that $f_\infty$ be kept small enough that rewards can always be covered by the validators' exposure, meaning $x' \ge f_{\infty} \sum_\eta x_{\eta,\nu,e}$.  We do not explore any cases where this fails here, but doing so requires a subtle definition of some $x' > x_{\nu,\nu,e}$ such that rewards still cannot create inflation. 

We now define $f' > f_0$ such that $f' x' = {1-f_1 \over f_1} f_{\infty} x_{\min}$ where $x_{\min} = \sum_\eta x_{\eta,\nu,e}$ is our required minimum total stake for any validator.  In the above scheme, we shall replace $f_{\infty}$ by $f'$ and only apply the payouts to slashes against validator operators minimum exposure $x'$, meaning replace the slash value $p_{\nu,e} x_{\eta,\nu,e}$ by $\max_{e \in \bar{e}} p_{\nu,e} x'$.


We consider a slash of value $s := p_{\nu,e} x_{\nu,\nu,e}$ being applied to the validator $\nu$.  We define the _minimum validator adjusted slash_ value $s' := p_{\nu,e} x'$ to be the fraction of this slash applied to the minimum validator stake $x'$.  We have a _total minimum validator adjusted slash_ given by $\max_{e \in \bar{e}} p_{\nu,e} x'$, which provides an analog of total regular slashes but only considering the validator themselves.

We next let $s^\prime_{\nu,i}$ and $s^\prime_{\nu,i+1}$ denote $\nu$'s total validator adjusted slash in their slashing span $\bar{e}$ before and after applying the new slash, respectively, so when $\nu$'s total validator adjusted slash increases by $s^\prime_{\nu,i+1} - s^\prime_{\nu,i} = \max(s^\prime - s^\prime_{\nu,i},0)$.

We track the value $s^\prime_{\nu,i}$ in the validator $\nu$'s slashing span record, but we also track another value $t_{\nu,i} < s^\prime_{\nu,i}$ that represents the total amount paid out so far.  If $s^\prime_{\nu,i+1} > s^\prime_{\nu,i}$ then we pay out $r := f_1 (f' s^\prime_{\nu,i+1} - t_{\nu,i})$ and increase $t_{\eta,i}$ by this amount.  If $s^\prime_{\nu,i+1} = s^\prime_{\nu,i}$ then we pay out $r := f_1 \max(f' s' - t_{\nu,i},0)$.  In either case, we store $t_{\nu,i+1} := t_{\nu,i} + r$.

In this way, our validator $\nu$ cannot reclaim more than $f' f_1 s$ from a slash of value $s$, even by repeatedly equivocations.  Any slash of size $s_{\nu,i}$ always results in some payout, but slashes less than $t_{\nu,i}$ never pay out.

In both scheme, we have similar payouts initially, but our second scheme with payouts based only on the validator slashes results in smaller reward payouts when cross era slashing logic kicks in.  As an example, if a validator $\nu$ gets similar slashes for different epochs, then the $r_1$ factor would reduce the entire reward if payouts are based only on the validator slashes, but if $\nu$ has disjoin nominators in every epoch then the $r_1$ factor makes only a minimal appearance. 


