
UPDATE: This discussion of swaps implemented with ZKCP might prove relevant to building bridges, but a bridge itself exists to support clients who cannot track chains. 




We envision a bridge that manages security for atomic swaps by observing the bitcoin blockchain, but does not itself hold bitcoins, and only holds dots as stake.  Aside from the bridge nodes and polkadot infrastructure, we have two customers, Paula who trade dots and Brit who trades bitcoin, although atomicity could generalise either to a group.  

I'll give a handy wavy sketch that should be informed by going over ZKCP literature: 

Step 0.  Paula's offer of Dot and Brit's offer of BTC get matched via some trading network, placing them into communication.  I donno if MPC helps here.

Step 1.  Paula and Brit negotiate their transaction: 
 - Paula provides Brit with her BTC wallet hash and her bridge supported test for considering the transaction settled on bitcoin.  
 - If Brits consider the test reasonable, then Brit secretly crafts but does not publish her BTC payment x to Paula, and gives Paula the hash of x.
 
Step 2.  Paula submits a bridge parachain transaction y to Brit that registers the trade with the bridge and time locks the funds she wishes to trade.  Registration reveals the test, the Dot and BTC amounts, Paula's BTC wallet hash, and the BTC transaction hash. 

Step 3.  After the parachain transaction is finalised, Brit submits her BTC transaction x, or maybe gives it to Paula so she can submit it.  If Brit does not do so fast enough then Paula's time lock expires.  

Step 4.  The bridges publish and finalize a transaction signing the release of funds from y to Brit, after recognising that x matches its hash commitment, sends the correct BTC amount to Paula's BTC hash, and has persisted long enough to past the test.  

Importantly, we use ordinary parachain finalization logic for the "threshold" signature by the bridges in steps 3 and 4, which should be a simple aggregate signature, not a true threshold signature, which anonymises the signers, so that the individual bridges can be held accountable.

We could improve perceived latency for Brit, and maybe simplify client code, by having Brit threshold encrypt x to the bridges in step 2, so the bridges carry out step 3 after finalising.  We expect polkadot to be fast though, so imho Brit should prefer the latency and simpler security model above.  Also I'd expect the above scheme simplifies bridge code far more than alternative schemes simplify client code.





In this design, Brit needs to trust the bridges will eventually unlock Paula's transaction y and Paula needs to trust that the bridges will wait until the test for Brit's transaction x checks out before unlicking her transaction y.  

Attack 1.  Bridges screw Brit.  At minimum Brit can appeal to governance to manually slash the bridges.  We could automatically slash the bridges based on evidence from bitcoin, but we cannot assess network conditions automatically and someone must assess this evidence, and worse hostil bitcoin miners could attack bridges via slashing.  We could make Brit produce a zero-knowledge or WI proof that her transaction worse as desired, but either bridges must still assess bitcoin, or else "dumb" tests much be hard wired into the parachain, like show 12 bitcoin blocks with however many zeros, which sounds game-able by bitcoin miners. 

Attack 2.  Bridges screw Paula.  We could make Brit actually publish a time locked contract x' on bitcoin that requires revealing a hash x'' and the bridges merely wait until passing the bitcoin test before revealing x''.  We still have a fair exchange problem in how long x' and y lock funds, which malicious bridges may exploit.  If Brit submits a time locked transaction this way, then ultimately the swap requires two BTC transactions, which sounds expensive, and may add latency for Paula.




