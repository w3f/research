# Slashing across eras with NPoS

We need our slashing algorithm to be fair and effective.  We discuss how this means slashing must respect nominators' exposure, be anti-Sibel, and be monotonic. 


In any era $e$, there is a fixed amount of stake aka base exposure $x_{\eta,\nu,e}$ assigned by any nominator $\eta$ to any validator $\nu$.  We demand that slashing never exceeds nominators' exposure because doing so creates an incentive to break up stash keys.  We avoid encouraging such Sibel behavior in Polkadot because doing so makes Polkadot unfair and harms our information about nominator behavior.

We immediately remove any validator $\nu$ whenever they gets slashed, which prevents repeated slashing after that point.  There are however issues in that $\nu$ have committed multiple violations before the chain acknowledges the slash and kicks $\nu$, or even that $\nu$ might equivocate posted retroactively.  In consequence, if era $e$ sees validator $\nu$ slashed for several distinct proportions $p_i$, then we define $p_{\eta,\nu,e} := \max_i p_i$ and slash their nominator $\eta$ only $p_{\eta,\nu,e} x_{\eta,\nu,e}$.  

We have no current concerns about multiple miss-behaviours from the same validator $\nu$ in one era, but if we invent some in future then the slashing lock could combine them before producing these $p_i$.  We know this would complicate cross era logic, but such issues should be addressed by considering the specific miss-behaviour.  In essence, this $p_{\eta,\nu,e} := \max_i p_i$ definition provides default mechanism for combining slashes within one era that is simple, fair, and commutative, but alternative logic remains possible so long as we slash the same regardless of the order in which offenses are detected.


We do however worry about miss-behaviours from different validators $\nu \ne \nu'$ both because nomination must restrict Sibels and also because correlated slashing need not necessarily involve the same validators.  We therefore let $N_{\eta,e}$ denote the validators nominated by $\eta$ in era $e$ and slash $\sum_{\nu \in N_e} p_{\eta,\nu,e} x_{\eta,\nu,e}$ from $\eta$ when multiple validators $\nu \in N_{\eta,e}$ get slashed.


We cannot assume that all events that warrant slashing a particular stash account get detected early or occur within the same era.  If $e$ and $e'$ are distinct eras then we expect $x_{\eta,\nu_j,e} \ne x_{\eta,\nu_j,e'}$ so the above arguments fail.  Indeed, we cannot even sum slashes applied to different validators because doing so could quickly exceeds nominators exposure $x_{\eta,\nu,e}$.

We might assume $\min \{ x_{\eta,\nu_j,e}, x_{\eta,\nu_j,e'} \}$ to be the "same" stake, but this does not obviously buy us much.  We therefore suggest the slashing $\eta$ the amount $\max_e \sum_{\nu \in N_e} p_{\eta,\nu,e} x_{\eta,\nu,e}$ where again $N_e$ is the validators nominated by $\eta$ in era $e$

In particular, there is an extortion attack in which someone runs many poorly staked validators, receives nominations, and then threatens their nominators with being slashed.  We cannot prevent such attacks entirely, but this outer $\max_e$ reduces the damage over formula that add slashing from different eras.


We cannot slash for anything beyond the unbonding period and must expire slashing records when they go past the unbonding period.  We implement this by recording all slash events along with some value $s_{\eta,\nu,e}$ recording the amount actually slashed at that time.  If $e'$ is later than $e$ then we record the initial slash $s_{\eta,\nu,e} := p_{\eta,\nu,e} x_{\eta,\nu_j,e}$ at $e$ and record a lesser slash $s_{\eta,\nu,e'} := p_{\eta,\nu,e'} x_{\eta,\nu_j,e'} - p_{\eta,\nu,e} x_{\eta,\nu_j,e}$ at the later $e'$.  These $s_{\eta,\nu,e}$ values permit slashes to expire without unfairly increasing other slashes.

We take several additional actions whenever some validator $\nu$ causes the slashing of some nominator $\eta$:  

First, we post a slashing transaction to the chain, which drops $\nu$ from the active validator list by invalidating their session keys, which makes everyone ignore $\nu$ from the remainder of the era, and also invalides any future blocks that do not ignore $\nu$.  We also remove all nomination approval votes by any nominator for $\nu$, even those who currently allocate $\nu$ zero stake.

Second, we remove all $\eta$'s nomination approval votes for future eras.  We do not remove $\eta$'s current nominations for the current era or reduce the stake currently backing other validators.  Also we permit $\eta$ to add new nomination approval votes for future eras during the current era.  We also notify $\eta$ that $\nu$ cause them to be slashed.  

We treat any future nominations by $\eta$ separately from any that happen in the current era or before.  in other words, we partition the eras into _slashing periods_ for $\eta$ which are maximal contiguous sequence of eras $\bar{e} = \left[ e_1, \ldots, e_n \right]$ such that $e_n$ is the least era in which $\eta$ gets slashed for actions in one of the $e_i$.  We let $\bar{e}$ range over the slashing periods for $\eta$ then we have slashed $\eta$ in total  
$$ \sum_{\bar{e} \in \bar{E}} \max_{e \in \bar{e}} \sum_{\nu \in N_e} p_{\eta,\nu,e} x_{\eta,\nu,e} $$


We ask that slashing be monotonic increasing for all parties so that validators cannot reduce any nominator's slash by additional miss-behavior.  In other words, the amount any nominator gets slashed can only increase with more slashings events, even ones involving the same validator but not the same nominator.

We think fairness imposes this condition because otherwise validators can reduce the slash of their favoured nominators, normally by making other nominators be slashed more.  We know trusted computing environments (TEE) avoid this issue, but we do not currently foresee requiring that all validators use them.

There are no meaningful limits on the diversity of nominators who nominated a particular validator within the unbonding period.  In consequence, almost every validator can be slashed simultaneously, thanks to by monotonicity and the validator adding past equivocations, which enables an array of "rage quit attacks".  In other words, we cannot bound the total stake destroyed by a combined slashing event much below the slash applied to the total stake of the network.


