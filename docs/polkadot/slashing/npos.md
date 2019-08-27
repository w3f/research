# Slashing across eras with NPoS

We need our slashing algorithm to be fair and effective.  We discuss how this means slashing must respect nominators' exposure, be anti-Sibel, and be monotonic. 


In any era $e$, there is a fixed amount of stake aka base exposure $x_{\eta,\nu,e}$ assigned by any nominator $\eta$ to any validator $\nu$.  We demand that slashing never exceeds nominators' exposure because doing so creates an incentive to break up stash keys.  We avoid encouraging such Sibel behavior in Polkadot because doing so makes Polkadot unfair and harms our information about nominator behavior.

We remove any validator $\nu$ whenever they gets slashed, which prevents repeated slashing after that point.  There is however an issue that $\nu$ might get slashed multiple times before the chain acknowledges the slash and kicks $\nu$.  In consequence, if era $e$ sees validator $\nu$ slashed for several distinct proportions $p_i$, then we define $p_{\eta,\nu,e} := \max_i p_i$ and slash their nominator $\eta$ only $p_{\eta,\nu,e} x_{\eta,\nu,e}$.

We have no current concerns about multiple miss-behaviours from the same validator $\nu$ in one era, but if we invent some in future then the slashing lock could combine them before producing these $p_i$.  We know this would complicate cross era logic, but such issues should be addressed by considering the specific miss-behaviour.

We do however worry about miss-behaviours from different validators $\nu \ne \nu'$ both because nomination must restrict Sibels and also because correlated slashing need not necessarily involve the same validators.  We therefore let $\Nu_{\eta,e}$ denote the validators nominated by $\eta$ in era $e$ and slash $\sum_{\nu \in \Nu_e} p_{\eta,\nu,e} x_{\eta,\nu,e}$ from $\eta$ when multiple validators $\nu \in \Nu_{\eta,e}$ get slashed.


We cannot assume that all events that warrant slashing a particular stash account get detected early or occur within the same era.  If $e$ and $e'$ are distinct eras then we expect $x_{\eta,\nu_j,e} \ne x_{\eta,\nu_j,e'}$ so the above arguments fail.  Indeed, we cannot even sum slashes applied to different validators because doing so could quickly exceeds nominators exposure $x_{\eta,\nu,e}$.

We might assume $\min \{ x_{\eta,\nu_j,e}, x_{\eta,\nu_j,e'} \}$ to be the "same" stake, but this does not obviously buy us much.  We therefore suggest the slashing $\eta$ the amount $\max_e \sum_{\nu \in \Nu_e} p_{\eta,\nu,e} x_{\eta,\nu,e}$ where again $\Nu_e$ is the validators nominated by $\eta$ in era $e$


We ask that slashing by monotonic increasing for all parties so that validators cannot reduce any nominator's slash by additional miss-behavior.  In other words, the amount any nominator gets slashed can only increase with more slashings evnts, even ones involving the same validator but not the same nominator.

We think fairness imposes this condition because otherwise validators can reduce the slash of their favoured nominators, normally by making other nominators be slashed more.  We know trusted computing environments (TEE) avoid this issue, but we do not currently foresee requiring that all validators use them.

There are no meaningful limits on the diversity of nominators who nominated a particular validator within the unbonding period.  In consequence, almost every validator can be slashed simultaneously, thanks to by monotonicity and the validator adding past equivocations, which enables an array of "rage quit attacks".  In other words, we cannot bound the total stake destroyed by a combined slashing event much below the slash applied to the total stake of the network.

