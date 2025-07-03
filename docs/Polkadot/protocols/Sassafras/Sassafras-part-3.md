# Sassafras Part 3: Compare and Convince

Authors: Elizabeth Crites, Handan Kılınç Alper, Alistair Stewart, and Fatemeh Shirazi

This is the third in a series of three blog posts that describe the new consensus protocol Sassafras, which is planned to be integrated into Polkadot, replacing the current [BABE](https://wiki.polkadot.network/docs/learn-consensus#block-production-babe)+[Aura](https://openethereum.github.io/Aura.html) consensus mechanism. 

Here is an overview of the three blog posts:

**[Part 1 - A Novel Single Secret Leader Election Protocol](sassafras-part-1):** The aim of this blog post is to give an introduction that is understandable to any reader with a slight knowledge of blockchains. It explains why Sassafras is useful and gives a high-level overview of how it works.

**[Part 2 - Deep Dive](sassafras-part-2):** The aim of this blog post is to dive into the details of the Sassafras protocol, focusing on technical aspects and security.

**Part 3 - Compare and Convince:** The aim of this blog post is to offer a comparison to similar protocols and convince the reader of Sassafras's value.

## If you have not read Part 1 and Part 2
Here is a a summary: 
- Sassafras is a consensus protocol for electing the leader who will produce the next block. It may be combined with a finality gadget that ensures transactions are finalized, such as [Grandpa](https://wiki.polkadot.network/docs/learn-consensus#finality-gadget-grandpa), to achieve a blockchain with blocks that are finalized in constant time intervals (e.g., every 6 seconds on Polkadot).
- It works by validators sending the tickets they have generated using online public randomness to other validators, who act as identity guards. Validators then publish these tickets on-chain where they get sorted. The first validator in the sorted list reveals their identity and produces the next block.
- Sassafras achieves a unique balance: it ensures enough security to make forking attacks infeasible, while being extremely efficient. This combination makes it an attractive option for deployment in the real world.

Let's jump into a comparison with other leader election protocols.

## Non-Single Leader Election

In [Part 1](sassafras-part-1) of this series, we discuss how [BABE](https://wiki.polkadot.network/docs/learn-consensus#block-production-babe)  finds block producers.  More formally, BABE is based on probabilistic leader election (PLE), which is quite common in proof-of-stake (PoS) protocols. Due to the probabilistic nature, multiple leaders may be elected for a slot, or no leaders at all.  The additional runoff procedure for selecting a leader increases the time needed to extend the blockchain.  Concretely, [Azouvi and Cappelleti](https://arxiv.org/abs/2109.07440) show that the block finality time for a PoS protocol is decreased by 25% when single secret leader election (SSLE) is used versus PLE. Even more important, for an adversary who controls at most $1/3$ of the validators, SSLE provides higher security than PLE against private attacks, the most damaging kind of attack, where an adversary can create a private chain that overtakes the honest chain. 

PLE-based PoS protocols provide security with more adversarial power (up to 49%), but are significantly slower (25%) to finalize the blocks. Sassafras provides security with less adversarial power ($1/3$), but finalizes the blocks significantly faster.

## Single Secret Leader Election

Given the advantages of SSLE, several protocols have been proposed.  We begin by providing a brief overview of various approaches.

### Shuffling

The most common approach to SSLE is shuffling, where each participant registers a commitment in a list, which is repeatedly shuffled, and the winning index is selected via a randomness beacon (i.e., a public source of randomness). The main drawback of these protocols is the significant overhead associated with the proofs for correct execution of the shuffle operations. The cost to verify a proof scales linearly with the number of parties, which is impractical for on-chain use. To address this issue, [Boneh et al.](https://eprint.iacr.org/2020/025) suggest dividing the list into sublists of size $\sqrt{N}$ and shuffling only the sublist instead of the entire list (called "stirring").  We refer to this protocol as Shuffle-1. 

### WHISK

[WHISK](https://hackmd.io/@asn-d6/HyD3Yjp2Y) is an efficient SSLE protocol proposed for Ethereum, based on the Shuffle-1 approach (i.e., "stirring"). Like Sassafras, it performs batch leader elections, in which a single leader is selected for several elections at once. The batch capability enables scalable deployment as a leader election protocol for blockchain, as the rate of leader election aligns with the rate of block production.  We give a detailed comparison of WHISK and Sassafras at the end of this blog post.


### PEKS

Functional encryption is a generalization of public key encryption where decryption yields a function of the encrypted message (instead of simply the encrypted message itself as in standard encryption). Public key encryption with keyword search (PEKS) is a form of functional encryption, which is used by [Catalano et al.](https://eprint.iacr.org/2021/344) to construct an SSLE protocol as follows. Each participant who registers in an election is given a secret key $sk_i$ for $i \in \{1,...,N\}$. A subset of participants collaboratively generate a ciphertext $c$ that encrypts a random "keyword" $i^* \in \{1,...,N\}$. The participant holding $sk_{i^*}$ is able to decrypt $c$, and provides a proof that attests to this fact in order to claim leadership.

### Other Approaches to SSLE

There are other approaches to SSLE, including indistinguishability obfuscation (IO) and threshold fully homomorphic encryption (TFHE); however, they are impractical due to the heavy cryptographic operations required.

    
## Comprehensive Comparison

We now give a comprehensive comparison in terms of the security guarantees and communication and computational overhead of the above protocols and Sassafras.

### Security Comparison

We assess the security of SSLE protocols based on three criteria, summarized in Table 1.

1. *Public Slots:* A public slot is one in which the leader for that slot is known (either publicly or to the adversary).

In Sassafras, a slot is public if the repeater of the ticket assigned to a slot is malicious, as described in [Part 2](sassafras-part-2).  The leader of a public slot may be attacked.

2. *Unpredictability Level:* The unpredictability level of a leader is the reciprocal of the anonymity set.

Shuffle-2 and Shuffle-3, by [Catalano et al.](https://eprint.iacr.org/2022/687), as well as the PEKS-based protocol exhibit the highest level of unpredictability. For all non-public slots, Sassafras achieves a similar level of unpredictability.

3. *Security Model:*  Protocols are proven secure via a security game, or in the universal composability (UC) model, which guarantees security when composed with other protocols in a larger system.  Security is proven either against a static adversary, who is assumed to control a set of parties from the onset only, or against a stronger adaptive adversary, who may dynamically corrupt parties as the protocol progresses.
 
Sassafras and Shuffle-3 achieve the highest level of security, against adaptive adversaries in the UC model.  Shuffle-1 and WHISK are insecure in our threat model.  We discuss this in detail at end of this blog post.


| Protocol |Public|Anonymity Set|Security|
| -------- |-------- |-------- |-------- |
|Shuffle-1|none &#x2713;|$(1-\alpha)\sqrt{N}$|game-based, static (*insecure in our threat model*)|
|Shuffle-2|none &#x2713;|$(1-\alpha) N$&#x2713;|UC, static|
|Shuffle-3|none &#x2713;|$(1-\alpha) N$&#x2713;|UC, adaptive &#x2713;|
|PEKS-based|none &#x2713;|$(1-\alpha) N$ &#x2713; |UC, static|
|WHISK| $-1.25\frac{\ln((1-\alpha)}{\sqrt{N}} N$ |$(1-\alpha) \sqrt{N}$|no formal security analysis *(insecure in our threat model)*|
|**Sassafras**|$(1-\alpha)\alpha N$| $(1-\alpha) N/2$ &#x2713;|UC, adaptive &#x2713;|

Table 1: Single secret leader election (SSLE) protocols. $N$ is the total number of participants, $\alpha$ is the fraction of corrupt parties, and $(1-\alpha)$ is the fraction of honest parties. For batch election protocols WHISK and Sassafras, values are given per election.
Public is the fraction of leaders in an election that are leaked. The unpredictability level of a leader  is the reciprocal of the anonymity set, e.g., $\frac{1}{(1-\alpha) \sqrt{n}}$. UC is the universal composability model.

We now give a detailed efficiency comparison of SSLE protocols.

### Communication Overhead

We consider $N = 2^{14} = 16384$ validators running an SSLE protocol to elect single leaders for $2^{13} = 8192$ slots.  These are the parameters proposed for WHISK as well as the PEKS-based scheme. 

Our analysis demonstrates that Sassafras outperforms other protocols in terms of computational and communication costs on the blockchain.

In particular, we conducted a comprehensive comparison of various protocols based on message size during the setup phase and off-chain and on-chain election communication. The setup overhead includes messages added on the chain or exchanged off-chain related to the keys or commitments used by validators before the elections. Similarly, the election overhead includes messages added on the blockchain and exchanged off-chain during the election protocol to elect $2^{13}$ leaders.

While the setup phase is expected to be rare in PoS blockchain protocols, shuffle-based solutions (with the exception of WHISK) impose impractical levels of message overhead. For election messages on the blockchain, Shuffle-2 and Shuffle-3 are highly inefficient. In stark contrast, Sassafras introduces a mere 7.64 MB overhead on the blockchain. 

    
| Protocol || Setup | Election |
| -------- |--------| -------- | -------- |
|Shuffle-1|<div class="subcolumn">Off-Chain</div><div>On-Chain</div>|<div class="subcolumn">-</div>$8790.15$ MB<div></div>|<div class="subcolumn">-</div>$123.7$ MB<div></div>|
|Shuffle-2|<div class="subcolumn">Off-Chain</div><div>On-Chain</div>|<div class="subcolumn">-</div>$13527.97$ MB<div></div>|<div class="subcolumn">-</div>$4831.84$ MB<div></div>|
|Shuffle-3|<div class="subcolumn">Off-Chain</div><div>On-Chain</div>|<div class="subcolumn">-</div>$17823.72$ MB<div></div>|<div class="subcolumn">-</div>$17718.31$ MB<div></div>|
|PEKS-based|<div class="subcolumn">Off-Chain</div><div>On-Chain</div>|<div class="subcolumn">$252$ MB</div>$1.08$ MB<div></div>|<div class="subcolumn">$23592.96$ MB</div>$301.47$ MB<div></div>|
|WHISK|<div class="subcolumn">Off-Chain</div><div>On-Chain</div>|<div class="subcolumn">-</div>$4.72$ MB<div></div>|<div class="subcolumn">-</div>$90.44$ MB<div></div>|
|**Sassafras**|<div class="subcolumn">Off-Chain</div><div>On-Chain</div>|<div class="subcolumn">-</div>$1.57$ MB &#x2713;<div></div>|<div class="subcolumn">$42.47$ MB</div>$7.64$ MB &#x2713;<div></div>|

Table 2: Communication overhead of SSLE protocols on a blockchain.

### Computational Overhead

We similarly conducted a comparison of various protocols based on on-chain computation required to verify election messages and the leader. <!--The number of group operations performed is considered the primary overhead in this context. -->Efficient on-chain computation is crucial in blockchain protocols, as they need to be performed quickly to facilitate timely block propagation.

<!--Table 3 demonstrates the superior efficiency of Sassafras compared to other protocols in terms of on-chain computation. -->
In terms of both communication and computational overhead, Sassafras outperforms other SSLE protocols by an order of magnitude or more. Further details of our benchmark analysis can be found in [the paper](https://eprint.iacr.org/2023/031).

 Protocol | On-Chain Comp. during the Election| Benchmark |
| -------- | -------- | -------- |
|Shuffle-1|$O(\sqrt{N})$|$40.9$ ms|
|Shuffle-2|$O(N)$|$5241.9$ ms|
|Shuffle-3|$O(N)$|$11793.6$ ms|
|PEKS-based|$O(\log^2 N)$|$16.9$ ms|
|WHISK|$O(\sqrt{N})$|$20$ ms|
|**Sassafras**|$O(1)$|$7.81$ ms &#x2713;|

Table 3: Computational overhead of SSLE protocols on a blockchain.  $N$ is the total number of participants.


## Key Takeaways

This concludes the three-part blog post series on Sassafras.  Here are some key takeaways:

* **Single leader election:** Sassafras elects a single block producer for each slot, ensuring faster consensus compared to protocols that rely on probabilistic leader election, which may not guarantee a unique leader or a leader at all times.
* **Maintaining the secrecy of a block producer:** Sassafras ensures the secrecy of block producers to mitigate against denial-of-service (DoS) attacks.
* **Lightweight:** Sassafras features exceptionally low communication and computational complexity and scales better than existing solutions.
<!-- * **Lightweight computational and block overhead:** Sassafras features exceptionally low communication and computational complexity and scales better than existing solutions. High computational costs often result in slow block propagation, while significant block overhead on the blocks causes very slow synchronization for the new nodes. -->
<!-- * **Implicit forward-secure signature properties:** In PoS-based blockchain protocols, employing a forward-secure signature scheme is crucial to be secure against adaptive adversaries because it prevents validators from producing blocks in the past after being compromised. However, forward-secure signature schemes are typically less efficient than, for example, the Schnorr signature scheme commonly used in blockchain protocols. Sassafras achieves forward security without explicitly deploying a forward-secure signature scheme, utilizing the efficient Schnorr signature scheme (or any other signature scheme) instead. -->

------

### Further Reading: Security Comparison with WHISK

For the interested reader, we now give a detailed comparison of the unpredictability levels achieved by WHISK and Sassafras under the assumption that the adversary can corrupt up to $1/3$ of parties. These can be a combination of corrupted and weakly corrupted parties, captured by $\alpha + \alpha_w \leq 1/3$, where $\alpha_w$ is the maximum fraction of weak corruptions (e.g., DoS-type attacks; see [Part 2](sassafras-part-2) for more details.) WHISK, like Sassafras, permits a fraction of leaders to be leaked, as seen in Table 1 under the "Public" column. 

Let us consider the following toy example to demonstrate the implications of this in both protocols. Out of one million validators on Ethereum, the proposed number of validators to run the WHISK protocol is $N = 2^{14} = 16384$. Now consider when $\alpha = \alpha_w =  1/6$, so that $\alpha N = (1/6)(16384) = 2730$ parties can be corrupted, and $2730$ parties can be weakly corrupted.  Sassafras results in $(1-\alpha)\alpha N = (1-1/6)(1/6)(16384)= 2276$ leaked leaders, but the anonymity set is of size  $(1-\alpha)N/2 = 6826$, so the leaders remaining achieve good privacy, and, as discussed in [Part 2](https://hackmd.io/@W3F64sDIRkudVylsBHxi4Q/Bkr59i7ekg) , the leaked leaders still allow consensus to succeed. In contrast, WHISK only leaks $\frac{-1.25 \ln(1-\alpha)}{\sqrt{N}} N = 29$ leaders, but the anonymity set is only of size $(1-\alpha) \sqrt{n} = 107$ for the remaining honest leaders. That is, all honest leaders in the set of $16384$ parties can be easily targeted for weak corruption. Indeed, it is in the adversary's interest to simply weakly corrupt all $1/3 n = 5460$ parties in its "corruption budget." Thus, WHISK is *insecure* under our threat model, as is the single election protocol Shuffle-1. The main purpose of deploying SSLE protocols in blockchains is to mitigate against DoS attacks, which our model accounts for strongly, and Sassafras achieves by design.

WHISK targets efficiency over other SSLE protocols by performing $\ell < N$ batch elections with $O(\sqrt{N})$ communication and computational complexity (see Table 3).  Sassafras's efficiency surpasses that of WHISK by performing an arbitrary number (not restricted to $\ell < n$) of batch elections with $O(1)$ communication and computational complexity.

<!--- 
## References

[[2]](http://www0.cs.ucl.ac.uk/staff/J.Groth/MinimalShuffle.pdf) Stephanie  Bayer and Jens Groth. "*Efficient zero-knowledge argument for correctness of a shuffle.*" EUROCRYPT 2012. 
- [[3]](https://eprint.iacr.org/2022/687.pdf) Dario Catalano, Dario Fiore, and Emanuele Giunta. "*Adaptively secure single secret leader election from DDH.*" ACM Symposium on Principles of Distributed Computing. 2022.
- [[4]](https://eprint.iacr.org/2021/344.pdf) Dario Catalano, Dario Fiore, and Emanuele Giunta. "*Efficient and universally composable single secret leader election from pairings.*" PKC 2023.
- [[6]](https://eprint.iacr.org/2020/025.pdf) Dan Boneh, Saba Eskandarian, Lucjan Hanzlik, and Nicola Greco. "*Single secret leader election.*" AFT 2020.-->

<!--

## Description of Sassafras

Sassafras is a blockchain protocol based on a proof-of-stake mechanism, characterized by long epochs including short, sequential block production slots. Within each epoch, the protocol select a single secret leader (a block producer) for each slot of the upcoming epoch. The identity of these leaders remains secret mostly until they produce a block.

In simple terms, validators initiate the process by generating random numbers using their secret keys, with fixed, public inputs serving as the seed. If these random numbers are valid, they are added to the blockchain during the respective epoch. The distinctive aspect of these random numbers is their verifiability using only the set of validators' public keys. Consequently, when subjected to verification, the ownership of the random numbers cannot be ascribed to any specific validator within the set.

At the end of the epoch, the anonymous random numbers are sorted to establish the order of leaders in the subsequent epoch. When a validator's turn comes in the following epoch, they generate the block and show their ownership of the corresponding random number assigned to the slot.

Sassafras derives its security from our novel cryptographic protocol called  "ring verifiable random function (ring VRF)". Now, we give an overview about it:


**Ring VRF:** Ring VRF [7] operates in a manner akin to both VRF and ring signatures, leveraging the properties of uniqueness, pseudorandomness, and anonymity. In ring VRF, a user can generate a ring VRF output, which is a unique pseudorandom number $y$, with her key and her input $m$ similar to VRF. She also signs $m$ with a set of public keys $ring$ including her key, similar to the ring signatures, to generate a signature which assures that $y$ is the unique output of $m$ generated with one of the public keys in $ring$. 

We would like to highlight that while the signers have the option to use the entire set $ring$ as an input, it is not necessary. Instead, they can utilize a commitment of the set and the corresponding opening, such as the Merkle Tree root of the keys in $ring$ and a membership proof of $pk \in ring$. This approach enables a logarithmic time complexity for the signing process, relative to the size of the ring. In the context of this write-up, we consistently refer to the use of the entire $ring$ as an input for simplicity and clarity.







We have developed [a ring VRF protocol](https://eprint.iacr.org/2023/002.pdf) that can be instantiated efficiently using a Chaum-Pedersen Zero-Knowledge Proof (ZKP) and either a KZG-based SNARK ([the implementation available](https://github.com/w3f/ring-vrf)) or Groth16-based SNARK ([implementation available](https://github.com/w3f/ring-proof)). One notable feature of our construction is its ability to sign an additional message, denoted as $aux$, without increasing the size of the signature. This property is particularly useful in Sassafras, as it allows us to achieve the forward-secure signature property without the need to deploy a separate forward secure signature scheme while signing the blocks.


Now, let's look at the details of Sassafras. Sassafras has two crucial parameters called `max_attempts`  and `c`. The `max_attempts` parameter refers to the number of ring VRF outputs that a validator generates using a ring VRF.  The `c` parameter acts as a threshold, playing a crucial role in determining the eligibility of a ring VRF output to participate in the election. 



Sassafras has a straightforward setup for new validators joining to the election. Whenever a new validator  joins, it generates a static Diffie-Hellman key ($K_a = aG$) and signs it with her signing key. Once the signature verification for their DH key is successful, it is added to the blockchain. To establish secure communication between validators with DH keys  $K_a$ and $K_b$, Sassafras uses the static DH key exchange protocol i.e., establish a symmetric key $K = aK_b = bK_a$ between validators. A validator with DH key $K_a$ uses $K$ specifically for encrypting messages intended for a particular validator with the DH key $K_b$.

Sassafras consists of the following phases, assuming that the randomness value $r$, the set of validators' public keys $ring$ and the static DH keys participating in the election for epoch $e$ have been finalized and are known to all validators before initiating the election process:



* **Preparation Phase:** During this phase, which takes place off-chain, each validator executes the ring VRF evaluation algorithm `max_attempts` times. For each evaluation $i$, the input is set as $m_i = e||r||i$, resulting in the output $y_i$. We note that the ring VRF evaluation algorithm involves one multiplication in the group $G$ and two hash operations: one hash to the field and one hash to the curve.

    Then, each validator determines which of the outputs satisfy the threshold condition `c`. If $y_i \leq c$, it indicates that $y_i$ has successfully passed the threshold.  In such cases, the validator proceeds to generate a ring signature. To initiate the ring signature generation, the validator first generates an ephemeral secret/public key pair $(esk_i, epk_i)$, using the key generation process of the Schnorr signature scheme. It is important to note that this step is independent of the election mechanism and is included here just to incorporate forward secrecy into the signature scheme used for block signing.
Then, she signs the message $m_i = e||r||i$ and $aux = epk_i$ by executing the ring VRF signature generation algorithm with the keys $ring$  and her own secret key.  $\sigma_i$ only shows that $y_i$ is the corresponding output of $m_i = e||r||i$ and $epk$ is the ephemeral key generated by the validator who generated $y_i$. In the end, the validator defines $ticket_i = (e, \sigma_i, i,epk_i)$. Conversely, if $y_i$ fails to meet the threshold criteria, the validator creates an empty ticket denoted as $ticket_i = \perp$ which is the same size with a valid ticket. This is neccessary to hide the number of ring VRF outputs of a validator that pass the threshold, as this information could be valuable to malicious parties who want to have some knowledge about a potential block producer in epoch $e$.
We note that if $ticket_i$ is assigned to a slot $sl$ of $e$ during  this election process, then the owner of the $ticket_i$ will use the ephemeral key $(epk_i)$ in $ticket_i$ while generating the block of $sl$ i.e., sign the block with $esk_i$. After this usage, the ephemeral key is immediately deleted.
This approach ensures that validators use a one-time verified key to sign blocks, effectively preventing them from generating blocks for previous epochs once they have been compromised. 

 *    **Distribution Phase:**    Now, let's proceed to the publication of the tickets. The issue here is that a validator cannot  publicly publish her tickets since the anonymity of the tickets would be compromised. Therefore, each validator requires an extra anonymity layer to address this issue.  Instead of employing a complex and not live anonymous broadcast  mechanishm, we adopt a simpler approach. Each validator randomly selects another validator, referred  as a repeater, for each of her tickets. Subsequently, each of them encrypts her ticket using AES encryption with a shared key established during the setup phase between the validator and the repeater. The encrypted ticket is then made public by the validator by sending it to everyone. We note that the distribution phase is an off-chain process. 
Whenever a validator receives an AES-encrypted ticket attributed to a validator $V$, she attempts to decrypt it using the symmetric key between herself and $V$. If she successfully decrypts it and obtains its contents i.e., $m = (e, \sigma_i, i,epk_i)$, she deduces that she is the repeater for this specific ticket. Consequently, she can infer that the owner of the ticket is validator $V$ as well, but remark that at this point, she is the only validator with this knowledge, as other validators are unable to decrypt the encrypted ticket. If a validator is unable to decrypt a message, meaning that they cannot obtain meaningful content from it, they simply ignore it.

* **Submission Phase:** Whenever a repeater obtains a ticket $ticket_i = (e, \sigma_i, i,epk_i)$ by decrypting, she first ensures that $1 \leq i \leq$`max_attempts`. If this condition is satisfied, the repeater proceeds with the verification of $\sigma_i$ by executing the ring VRF verification algorithm with the message $m = e||r||i||epk_i$ and the key set $ring$. If the verification algorithm successfully verifies $\sigma_i$, it outputs $y_i$. If it is the case and $y_i \leq c$, indicating that it is a valid and eligible random number for the election, the repeater publishes the ticket to be added to the blockchain. Othwerwise, she ignores it.
In  Sassafras, we designate a specific time interval for the submission phase within the election epoch. During this interval, the last $t_{last}$ slots are reserved exclusively for honest validators who may have selected a malicious repeater for some of their tickets. In the event that a validator does not see her valid ticket on the blockchain until the last $t_{last}$ slots of the submission phase, she has the option to independently publish her ticket, although this action poses a risk to the anonymity of the ticket. It is important to note that this concern has been mitigated since the behaviour of the repeater implies her malicious intent, thereby already compromising the anonymity of the ticket.


* **Sortition Phase:** After the  submission phase, validators await the finalization of all tickets generated for $e$. Once the finalization process is complete, validators employ the ring VRF verification algorithm, with  the message $m = e||r||i||epk_i$ and the key set $ring$, to obtain the corresponding output $y_i$ for each finalized ticket $ticket_i$. Then, they sort these outputs in a descending order, establishing the block-production order for validators within epoch e. 
Consequently, it can be deduced that for a given slot $j$ within epoch $e$, the validator generated with the random number in the $j$-th position will produce the block. It is important to note that only the owner of the ticket and its designated repeater have knowledge regarding the block producer of slot $j$ in epoch $e$ in the end of the election, provided the repeater is honest.


When the leader of slot $j$ produces a block, it generates a proof that shows that the random number in the $j^{th}$ order is generated by herself by using the linkability property of the ring VRF scheme. The leader signs the block with the ephemeral key in her ticket and deletes it immediately. This provides forward secrecy because even if a validator is corrupted in future, she cannot produce a block for a past slot since she deleted the signing key just after that slot.
   
   
## Unpredictibility of Block Producers in Sassafras

The unpredictability level is defined by Boneh et al. [6] as the probability of an adversary guesses the leader of a slot. Therefore, the best a protocol can achieve is $\frac{1}{\alpha N}$ where $\alpha N$ is the number of honest validators. Intuitively, in Sassafras, if a validator selects an honest repeater for her ticket assigned to a slot $sl$, then noone except the honest repeater knows the leader of $sl$ in the end of the election process. Therefore, the unpredictability level of $sl$ is $\frac{1}{\alpha N}$  in the end of the election. However, if the repeater is malicious then the unpredictability of $sl$ is 1 meaning that the adversary knows the block producer of $sl$. Our analysis also shows that during the epoch $e$ where the leaders produce block and reveal their identity, the adversary gains a tiny bit information about who would not be a leader for a specific slot. This information reduces the unpredictability level of the last slot leader to $\frac{2}{(1-\alpha) N}$. Specifically, assume that a validator $V$ is the leader of $sl$ assosiated with  $ticket_i = (e, \sigma_i, j,epk_i)$. After $V$ produces her block at $sl$, anybody can deduce that $V$ is not the leader of slots which has the index $j$ in their corresponding ticket. The reason of it is that we know that each validator can have at most 1 ticket having the index $j$ because of the design of the ticket generation in the preparation phase. We analyse the unpredictability level of Sassafras formally in our paper [1]. Our analysis shows that with small threshold value $c$, we can sparse the indexes in the tickets and the adversary is able to get only a little bit information about who might/might not be a block producer of a particular slot (see Table 3).


-->
