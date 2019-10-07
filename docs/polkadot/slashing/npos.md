# Slashing across eras with NPoS

We need our slashing algorithm to be fair and effective.  We discuss how this means slashing must respect nominators' exposure, be anti-Sibel, and be monotonic. 


In any era $e$, there is a fixed amount of stake aka base exposure $x_{\eta,\nu,e}$ assigned by any nominator $\eta$ to any validator $\nu$.  We demand that slashing never exceeds nominators' exposure because doing so creates an incentive to break up stash keys.  We avoid encouraging such Sibel behavior in Polkadot because doing so makes Polkadot unfair and harms our information about nominator behavior.

We immediately remove any validator $\nu$ whenever they gets slashed, which prevents repeated slashing after that block height.  There are however issues in that $\nu$ have committed multiple violations before the chain acknowledges the slash and kicks $\nu$, or even that $\nu$ might equivocate posted retroactively.  In consequence, if era $e$ sees validator $\nu$ slashed for several distinct proportions $p_i$, then we define $p_{\nu,e} := \max_i p_i$ and slash their nominator $\eta$ only $p_{\nu,e} x_{\eta,\nu,e}$.  

<small>As an aside, we could write $p_{\eta,\nu,e}$ throughout if we wanted to slash different nominators differently, like by slashing the validator themselves more, i.e. $p_{\nu,\nu,e} > p_{\eta,\nu,e}$ for $\nu \ne \eta$.  We abandoned this idea because validators could always be their own nominators.</small>

We have no current concerns about multiple miss-behaviours from the same validator $\nu$ in one era, but if we invent some in future then the slashing lock could combine them before producing these $p_i$.  We know this would complicate cross era logic, but such issues should be addressed by considering the specific miss-behaviour.  In essence, this $p_{\nu,e} := \max_i p_i$ definition provides default mechanism for combining slashes within one era that is simple, fair, and commutative, but alternative logic remains possible so long as we slash the same regardless of the order in which offenses are detected.


We do however worry about miss-behaviours from different validators $\nu \ne \nu'$ both because nomination must restrict Sibels and also because correlated slashing need not necessarily involve the same validators.  We therefore let $N_{\eta,e}$ denote the validators nominated by $\eta$ in era $e$ and slash $\sum_{\nu \in N_e} p_{\nu,e} x_{\eta,\nu,e}$ from $\eta$ when multiple validators $\nu \in N_{\eta,e}$ get slashed.


We cannot assume that all events that warrant slashing a particular stash account get detected early or occur within the same era.  If $e$ and $e'$ are distinct eras then we expect $x_{\eta,\nu_j,e} \ne x_{\eta,\nu_j,e'}$ so the above arguments fail.  Indeed, we cannot even sum slashes applied to different validators because doing so could quickly exceeds nominators exposure $x_{\eta,\nu,e}$.

We might assume $\min \{ x_{\eta,\nu_j,e}, x_{\eta,\nu_j,e'} \}$ to be the "same" stake, but this does not obviously buy us much.  We therefore suggest slashing $\eta$ the amount
$$ \max_e \sum_{\nu \in N_e} p_{\nu,e} x_{\eta,\nu,e} $$
where again $N_e$ is the validators nominated by $\eta$ in era $e$

In particular, there is an extortion attack in which someone runs many poorly staked validators, receives nominations, and then threatens their nominators with being slashed.  We cannot prevent such attacks entirely, but this outer $\max_e$ reduces the damage over formula that add slashing from different eras.


We kept our slashing simple and fixed some fairness issues with the outer maximum $\max_e \cdots$, but created another problem:  If $\nu$ gets slashed once, then $\nu$ could thereafter commit similar offenses with impunity.  As this situation is neither fair nor effective, we must limit $\eta$ and $\nu$ impunity either by limiting the eras spanned by this outer maximum, or else by removing their impunity gradually.  

We want this impunity to disappear as quickly as possible and minimize further risks to the network.  We suggest defining an explicit span based on offence detection times and the nominator's own voluntary reenlistment.  As nominators might make mistakes in reenlistment, we detail several additional actions taken whenever some validator $\nu$ causes the slashing of some nominator $\eta$.  

First, we post a slashing transaction to the chain, which drops $\nu$ from the active validator list by invalidating their session keys, which makes everyone ignore $\nu$ for the remainder of the era, and also invalidates any future blocks that do not ignore $\nu$.  We also remove all nomination approval votes by any nominator for $\nu$, even those who currently allocate $\nu$ zero stake.

Second, we remove all $\eta$'s nomination approval votes for future eras.  We do not remove $\eta$'s current nominations for the current era or reduce the stake currently backing other validators.  Also we permit $\eta$ to add new nomination approval votes for future eras during the current era.  We also notify $\eta$ that $\nu$ cause them to be slashed.  

These state alterations minimize the risks of unintentional reenlistment any nominator, while also minimising risks to the network.  We thus feel justified in treating any future nominations by $\eta$ separately from any that happen in the current era or before, which now permits defining the eras spanned by the outer maximum:

We partition the eras into _slashing spans_ for $\eta$ which are maximal contiguous sequence of eras $\bar{e} = \left[ e_1, \ldots, e_n \right]$ such that $e_n$ is the least era in which $\eta$ gets slashed for actions in one of the $e_i$.  We let $\bar{e}$ range over the slashing spans for $\eta$ then we have slashed $\eta$ in total  
$$ \sum_{\bar{e} \in \bar{E}} \max_{e \in \bar{e}} \sum_{\nu \in N_e} p_{\nu,e} x_{\eta,\nu,e} $$

In particular, if $\eta$ gets slashed in epoch 1 with the detection occurring in epoch 2, then resumes nomination in epoch 3, and only then gets slashed again for actions in epoch 1 and 2, then these later slashes are counted as part of the same slashing span as $\eta$'s first slash from epoch 1.  

We cannot slash for anything beyond the unbonding period and must expire slashing records when they go past the unbonding period.  We address this easily thanks to slashing spans:  We track the maximum slash within each slashing span, which we update anytime a slash raises the slashing span's maximum slash.  

<small>As an aside, there was another accounting strategy here:  Record all slash events along with some value $s_{\eta,\nu,e}$ recording the amount actually slashed at that time.  If $e'$ is later than $e$ then we record the initial slash $s_{\eta,\nu,e} := p_{\nu,e} x_{\eta,\nu_j,e}$ at $e$ and record a lesser slash $s_{\eta,\nu,e'} := p_{\nu,e'} x_{\eta,\nu_j,e'} - p_{\nu,e} x_{\eta,\nu_j,e}$ at the later $e'$.  These $s_{\eta,\nu,e}$ values permit slashes to expire without unfairly increasing other slashes.  We believe this extra complexity and storage, does not improve network security, and strengthens extortion attacks on nominators.</small>


We ask that slashing be monotonic increasing for all parties so that validators cannot reduce any nominator's slash by additional miss-behavior.  In other words, the amount any nominator gets slashed can only increase with more slashings events, even ones involving the same validator but not the same nominator.

We think fairness imposes this condition because otherwise validators can reduce the slash of their favoured nominators, normally by making other nominators be slashed more.  We know trusted computing environments (TEE) avoid this issue, but we do not currently foresee requiring that all validators use them.

There are no meaningful limits on the diversity of nominators who nominated a particular validator within the unbonding period.  In consequence, almost every validator can be slashed simultaneously, thanks to by monotonicity and the validator adding past equivocations, which enables an array of "rage quit attacks".  In other words, we cannot bound the total stake destroyed by a combined slashing event much below the slash applied to the total stake of the network.


In fact, we find that monotonicity also constrains our rewards for offense reports that result in slashing:  If a validator $\nu$ gets slashed, then they could freely equivocate more and report upon themselves to earn back some of the slashed value.  

We define $f_\infty < 0.1$ to be the maximum proportion of a slash that ever gets paid out.  We also define $f_1 < {1\over2}$ to be the proportion of $f_\infty$ paid out initially on the first offence detection.  So a fresh slash of value $s$ results in a payout of $f_\infty f_1 s$.

We consider a slash of value $s := p_{\nu',e} x_{\eta,\nu',e}$ being applied to the nominator $\eta$.  We let $s_{\eta,i}$ and $s_{\eta,i+1}$ denote $\eta$'s actual slash in slashing span $\bar{e}$ given by $\max_{e \in \bar{e}} \sum_{\nu \in N_e} p_{\nu,e} x_{\eta,\nu,e}$ before and after applying the new slash, respectively, so when $\eta$'s slash increases by $s_{\eta,i+1} - s_{\eta,i}$.

We track the value $s_{\eta,i}$ in $\eta$'s slashing span record, but we also track another value $t_{\eta,i} < s_{\eta,i}$ that represents the total amount paid out so far.  If $s_{\eta,i+1} > s_{\eta,i}$ then we pay out $r := f_1 (f_\infty s_{\eta,i+1} - t_{\eta,i})$ and increase $t_{\eta,i}$ by this amount.  If $s_{\eta,i+1} = s_{\eta,i}$ then we pay out $r := f_1 \max(f_\infty s - t_{\eta,i},0)$.  In either case, we store $t_{\eta,i+1} := t_{\eta,i} + r$.

In this way, our validator $\nu$ cannot reclaim more than $f_{\infty} f_1 s$ from a slash of value $s$, even by repeatedly equivocations.  Any slash of size $s_{\eta,i}$ always results in some payout, but slashes less than $t_{\eta,i}$ never pay out.

We acknowledge the above scheme requires considering all impacted $\eta$ when doing payouts.  We have some minimum stake $x'$ that validator operators must provide themselves, meaning $x_{\nu,\nu,e} > x'$.  If $x_{\nu,\nu,e} > f_{\infty} \sum_\eta x_{\eta,\nu,e}$ then we could replace $f_{\infty}$ above with the $f_{\nu,e}$ such that $f_{\nu,e} x_{\nu,\nu,e} = f_{\infty} \sum_\eta x_{\eta,\nu,e}$, and only apply the payouts to slashes against validator operators.  We'd have similar payouts initially, but smaller payouts in cross era slashing.  We suppose validator operators could exploit this make reporting unprofitable, but only in rather niche situations.

