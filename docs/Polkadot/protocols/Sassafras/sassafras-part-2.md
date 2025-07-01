# Sassafras Part 2: Deep Dive

Authors: Elizabeth Crites and Fatemeh Shirazi

This is the second in a series of three blog posts that describe the new consensus protocol Sassafras, which is planned to be integrated into Polkadot, replacing the current [BABE](https://wiki.polkadot.network/docs/learn-consensus#block-production-babe)+[Aura](https://openethereum.github.io/Aura.html) consensus mechanism. 

Here is an overview of the three blog posts:

**[Part 1 - Gentle-as-Fluff Introduction](https://hackmd.io/4UjkyZ04Q82d7ZisGTno2A):** The aim of this blog post is to give an introduction that is understandable to any reader with a slight knowledge of blockchains. It explains why Sassafras is useful and gives a high-level overview of how it works.

**Part 2 - Deep Dive:** The aim of this blog post is to dive into the details of the Sassafras protocol, focusing on technical aspects and security.

**[Part 3 - Compare and Convince](https://hackmd.io/I8VSv8c6Rfizi9JWmzX25w):**
The aim of this blog post is to offer a comparison to similar protocols and convince the reader of Sassafras's value.

Let's now take a deep dive into the Sassafras protocol, starting with some background on leader election protocols.

## Sassafras: Efficient Batch Single Leader Election

### Leader Election
Leader election is used in blockchain protocols to assign the producer of the next block. As discussed in [Part 1](https://hackmd.io/4UjkyZ04Q82d7ZisGTno2A), it is an important part of the consensus mechanism and affects security and efficiency considerably.  For example, if too many consecutive blocks are produced by an adversary, the chain becomes vulnerable to forking attacks and double spending.

### Single Secret Leader Election (SSLE)
A common type of leader election is single secret leader election (SSLE). In SSLE, a set of participants (e.g., validators) elect exactly one leader (e.g., the block producer), and the
leader remains anonymous until they announce themselves by providing proof that they are indeed the elected leader.
The practical advantages of electing exactly one leader are discussed in [Part 1](https://hackmd.io/4UjkyZ04Q82d7ZisGTno2A) and [Part 3](https://hackmd.io/I8VSv8c6Rfizi9JWmzX25w).
The anonymity of the leader is an important property for security, as the leader makes for an attractive target, especially for denial-of-service (DoS) attacks.
The main security properties of SSLE are uniqueness (i.e., electing only one leader), unpredictability (i.e., hiding the leader), and fairness (i.e., having equal chance of becoming the leader).[^5]

### Threat Model for Leader Election

A realistic threat model for leader election considers an adversary that may (1) control some fraction of the election participants and (2) dynamically attack identified leaders to temporarily disrupt their availability. In the blockchain setting, capability (2) could lead to DoS attacks on honest block producers, compromising chain safety. Thus, achieving a high level of security against this type of attack is critical, and a main design consideration for Sassafras.

### Sassafras

We propose a novel single leader election protocol, Sassafras, and describe how it can be deployed on a blockchain to elect block producers.
Sassafras departs substantially from other approaches to SSLE, the most common approach being shuffling (see [Part 3](https://hackmd.io/I8VSv8c6Rfizi9JWmzX25w)).

The main technical novelty of Sassafras is the use of a [ring verifiable random function (VRF)](https://eprint.iacr.org/2023/002) to hide the identity of the leader within a set  of election participants (called a "ring"). The output of a ring VRF is unique and pseudorandom, and can be verified by anyone, so it meets the SSLE security requirements defined above.  The use of a ring VRF instead of, e.g., shuffling, dramatically reduces on-chain communication and computation (see [Part 3](https://hackmd.io/I8VSv8c6Rfizi9JWmzX25w)). 

Sassafras achieves unparalleled efficiency in block production while retaining sufficient anonymity to maintain blockchain security (discussed further below). It accomplishes this through its slightly relaxed notion of leader anonymity, where most honest leaders enjoy a high degree of anonymity.

Moreover, Sassafras is designed for *batch* leader elections, in which a single leader is selected for several elections at once.
The batch capability of Sassafras allows the rate of leader election to align with the rate of block production, an often-sought property not met by most SSLE protocols. Thus, Sassafras enables scalable deployment as a leader election protocol for blockchains.

<!-- This proposal is joint work with Jeffrey Burdges, Handan Kılınç Alper, Alistair Stewart, and Sergey Vasilyev. -->

## Overview of Sassafras

We now describe the Sassafras protocol in more detail.  (A high-level description is given in [Part 1](https://hackmd.io/4UjkyZ04Q82d7ZisGTno2A).)

The figure below describes the protocol in phases: **Phase A,B,C,D,E**. 
<!--Green dots are honest parties, red dots are adversarial parties, and orange dots are parties whose identities are leaked.-->

![sassafrass-diagram](https://hackmd.io/_uploads/rJxipBYVxl.png)


<!--![Copy of Sassafras](https://hackmd.io/_uploads/Byb0krT1xx.png)-->

<!--
<img src="https://hackmd.io/_uploads/ByY2E76Jlx.png" width="625" height="500" />
-->

<!--We first give a description of the Sassafras protocol in phases.  We then describe each phase in more detail.

**Phase A)** All validators first obtain a random number from a randomness beacon, and use it to generate $n_t$ pseudorandom numbers, where $n_t$ is the number of tickets. parties in Sassafras run the ring VRF evaluation algorithm $n_t$ times with inputs $r||i$ for 
$1 \leq i \leq n_t$.  They check if the evaluation outputs $y_i$ fall below a fixed threshold – these are the winning outputs. To prove $y_i$ is generated correctly without revealing their identity, a party signs $r||i$, resulting in a signature $\sigma_i$.  Each validator hides $y_i, \sigma_i$ and the repeater's identity by encrypting $y_i, \sigma_i$ using a shared symmetric key with a randomly chosen validator, called a repeater. Then, they multicast the encryption to all parties.[^2]

**Phase B)** Each repeater receives all tickets and decrypts tickets for which it holds the decryption key. Each ticket and its repeater are hidden. Repeaters publish the tickets they received on chain.
In the end, the repeater capable of decrypting the ticket publishes $y_i, \sigma_i$ on behalf of the sender party. All repeaters publish all tickets at once.

**Phase C)** All tickets are sorted on chain. 

**Phase D)** An adversary can attack validators whose identities are leaked during Phase B (orange dots). An honest validator whose identity was not leaked and is first on the sorted list sends proof that they are the next block producer.

**Phase E)** They then produce the next block.
-->

To begin with, parties taking part in the election (e.g., validators) first obtain a random number from a randomness beacon (i.e., a public source of randomness), and use it to generate $n_t$ pseudorandom numbers, where $n_t$ is the number of tickets.[^1]  The parties then determine which numbers qualify as winning, and anonymously publish, verify, and agree on these winners. The numbers are sorted to determine the order of the (secret) leaders, with the position of a number indicating its leader’s rank.

The core challenge in Sassafras is generating verifiable pseudorandom numbers while maintaining anonymity. A standard verifiable random function (VRF) could be used to generate them; however, the verification algorithm requires the public key of the generating party, ultimately revealing their identity. To avoid this, Sassafras employs a [ring verifiable random function](https://eprint.iacr.org/2023/002) to ensure a unique and verifiable pseudorandom output, as in a standard VRF, but without revealing which party within the set of public keys $\mathcal{PK}$ generated it.
In more detail (**Phase A**), parties in Sassafras run the ring VRF evaluation algorithm $n_t$ times with inputs $r||i$ for $1 \leq i \leq n_t$  after obtaining $r$ from the randomness beacon. They check if the evaluation outputs $y_i$ fall below a fixed threshold -- these are the winning outputs. To prove $y_i$ is generated correctly without revealing their identity, a party signs $r||i$, resulting in a signature $\sigma_i$ that can be verified by anyone with $\mathcal{PK}$, but without identifying the signer.

At this point, parties need to publish their winning outputs and signatures anonymously. If they publish them  in clear, then their anonymity is immediately broken, even if $\sigma_i$ can be verified without their keys, because an adversary could observe the network traffic and learn the source of any message.
Thus, Sassafras requires an extra anonymity layer. The goal is to have a randomly selected party, called a repeater, receive a party's ticket $y_i, \sigma_i$.[^3] This is accomplished as follows.
The party hides $y_i, \sigma_i$ and the repeater's identity by encrypting $y_i, \sigma_i$ using a shared symmetric key with the repeater[^4] and multicasting the ciphertext to all parties.[^2]

The repeater who can decrypt the ticket publishes $y_i, \sigma_i$ on behalf of the sender party (**Phase B**). All repeaters publish all tickets at once (on chain).  

All $y_i$ values are then sorted (on chain) and determine the order of the leaders (**Phase C**).

Now, if the repeater is malicious, the anonymity of the sender is compromised. An adversary can attack validators whose identities are leaked during Phase B (orange dots with X).
Otherwise, anonymity is preserved because the owner of $y_i$ is known by the honest repeater only, and other parties are unable to decrypt the ciphertext.
In the next epoch, the first honest party on the sorted list who was not attacked claims the winning ticket by signing $r||i$ again, but this time using the ring consisting of their public key only, deanonymizing themself (**Phase D**).

Finally, the leader produces the next block (**Phase E**).

## Security

Let us now see why the anonymity guarantees of Sassafras are sufficient for blockchain consensus. (Warning: This part is a bit technical. However, it is not necessary for understanding the rest of the blog posts and can be skipped.)

Suppose there are up to $\alpha = 1/3$ corrupt parties and $2/3$ honest parties.[^6] For each election, one of these parties is randomly selected as the repeater of the winning ticket.  With probability at least $(2/3)(2/3) = 4/9$, both the ticket holder and the repeater are honest.  Thus, the identity of the honest leader is protected.  With probability at least $(2/3)(1/3) = 2/9$, the ticket holder is honest, but the repeater is adversarial.  In this case, the repeater learns the identity of the ticket holder and can attack them when they are due to be the next leader.[^7]
During the attack, the compromised party is unable to produce blocks; these empty slots do not contribute to the total number of blocks for reasoning about chain safety. For each slot, the probability that the adversary produces a block is at most 1/3, and the probability that an honest party produces a block is at least 4/9 (> 1/3). (In the figure above, there are more green dots than red ones in Phase D.) In expectation, there will be more honest blocks appended to the current longest chain than adversarial blocks.  

From there, by adapting the security proof for probabilistic leader election (PLE)-based proof-of-stake blockchains (e.g., Ouroboros Praos), we can identify a 𝑘 such that all public chains will include the same blocks that are more than 𝑘 slots old. This follows intuitively from the fact that, by Chernoff bounds, any sufficiently long sequence of slots will contain more honest blocks than adversarial ones.  Thus, we see that even if an adversary can corrupt up to $1/3$ of parties, the longest chain rule is not violated and consensus succeeds. You can find the formal security analysis in [the paper](https://eprint.iacr.org/2023/002).

### Network-Layer Anonymity

Finally, let us provide more intuition on how leaders publish the winning outputs and their signatures anonymously.  As described above, each party multicasts their ticket encrypted to the repeater, who posts it on chain. Common practice is to have three hops relaying for anonymity; however, with $2/3$ honest validators, one hop is sufficient because it provides enough anonymity to achieve safety, while being efficient. 

Even for a strong adversary 
that has global view and can observe all the traffic between parties, traffic correlation for tickets sent to honest repeaters cannot be used to link leaders and their tickets.
This is because: 1) tickets are encrypted via a shared key between leader and repeater, 
which makes the tickets sent to different receivers indistinguishable,
2) tickets sent by all leaders are of the same size, and 3) the repeaters send out all of the winning tickets they received at the same time, eliminating the possibility of correlation via timing signatures.

We now move to [Part 3](https://hackmd.io/I8VSv8c6Rfizi9JWmzX25w), which gives a detailed efficiency analysis and comparison with other approaches to leader election.

[^1]: We show how to chose the parameter $n_t$ in [the paper](https://eprint.iacr.org/2023/002). For example, $n_t$ should be at least 6 for $2^{13}$ elections, under the assumption that the fraction $\alpha$ of corrupt parties is less than $\approx 0.3$ with $2^{14} = 16384$ total parties. (This is the number of validators running the leader election protocol proposed for Ethereum; see [Part 3](https://hackmd.io/I8VSv8c6Rfizi9JWmzX25w).)

[^2]: Formally, the communication between sender and receiver occurs via a secure diffusion functionality $\mathcal{F}_{\mathsf{com}}^s$, which hides the message and the receiver. Here, we describe Sassafras with a simple and efficient instantiation of $\mathcal{F}_{\mathsf{com}}^s$ using symmetric encryption.  By "multicasting the ciphertext to all parties," we mean one-to-many communication via a standard diffusion functionality $\mathcal{F}_{\mathsf{com}}$.  Details are given in [the paper](https://eprint.iacr.org/2023/002).

[^3]: Technically, only $\sigma_i$ needs to be sent, as $y_i$ can be derived publicly from $\sigma_i.$  Also, all non-winning tickets (or even dummy tickets of the same size) are sent to hide the number of winning tickets from the adversary.

[^4]: For example, Diffie-Hellman key exchange together with semantically secure encryption could be used.  In [the paper](https://eprint.iacr.org/2023/002), we provide a non-interactive solution that can be performed on the fly, so that validators do not need to store secret key pairs with every other validator.

[^5]: In Polkadot, validators have equal weight and therefore equal chance of becoming the leader. This is what we assume for Sassafras in these blog posts.

[^6]: Polkadot assumes $\alpha < 1/3$, as does every chain using traditional Byzantine Agreement that is asynchronously safe (e.g., Ethereum, Cosmos, Aptos, Sui).  Thus, Sassafras makes an attractive option for deployment in many proof-of-stake blockchains.

[^7]: Here, we consider DoS-type attacks that take the (honest) party out of networking entirely.  The attacked party cannot send or receive blocks during the attack. Afterward, the party receives all missed messages, but there is no guarantee that messages sent during the attack were delivered.  In [the paper](https://eprint.iacr.org/2023/002), we also consider a stronger type of attack, called adaptive corruption, where parties may be corrupted by the adversary at any point during the protocol execution.  In this case, an attacked party could produce blocks on an adversarial fork and is therefore treated as malicious (i.e., as red dots) in the security analysis.

