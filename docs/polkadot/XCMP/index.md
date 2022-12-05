# XCMP overview

XCMP is Polkadot's cross-chain message-passing protocol. It allows one parachain to send messages to another parachain and provides guarantees about the delivery of these messages. Polkadot allows parachains to send each other mesages as long as they have established messaging channels with each other. In this document we review first the core principle of the XCMP design and then review authentication, network delivery, channels, and finally SPREE which can be used for e.g. trustless token transfers.

## Core design principles

Parachains will host dapps on them, and interoperability between dapps is highly facilitated by ordered and timely delivery of messages. Polkadot delivery guarantees include:

- guaranteed message delivery - a receiving chain will receive the message as long as it keeps producing blocks.

- trustless delivery - Polkadot's shared security ensures the correctness of message delivery and authenticity as long as we trust the code that produces and consumes them.

- ordered delivery - messages arrive in a well-defined order.

Ordered and timely delivery of messages is not a given guarantee in many applications such as some web applications. This is because TCP gives weaker guarantees about delivery and hence the web application needs to deal with these issues. Specifically, TCP's guarantees do not cover application-level problems such as crashes. To build atomic transactions on such a layer requires a lot of work, involving acknowledgements and timeouts that persist across process lifetimes. The trade off for Polkadot however is that non-availability of XCMP messages can halt a parachain, so Polkadot needs to ensure that this never happens.

(For comparison, while Cosmos allows the choice of having ordered delivery, there may be no guarantees that messages will ever arrive due to the lack of a general incentive model for this purpose.)

We want all these properties while maintaining scalability, in that the relay chain should not be overwhelemed if 100 parachains send messages to 10,000 destinations in a single relay chain block, which we discuss in the next sections. This includes trying to minimise the data stored on the relay chain, and in particular it should be constant or near-constant with respect to the message body sizes.


## Communication model

This section talks about the XCMP communication interface from the viewpoint of a parachain, without going into the internal details on how this interface is implemented, or how its guarantees are achieved, by Polkadot.

Parachains can send each other messages once they have established messaging channels with each other.
Every (sender, recipient) parachain pair can have up to 1 open channel, allowing for bidirectional communication.

Whilst the channel is open, it contains a bounded queue of ordered messages that have been sent but not yet acknowledged by the recipient. The sender may add a message to the back of the queue (i.e. send a message), and the recipient may remove a message from the front of the queue (i.e. ack a message), by indicating as such in their respective next submission to the relay chain. Sender and recipient parachains are also expected to monitor the state of the relay chain, in order to know what is currently in the queue.

Note: all the messages for a given (sender, relay-chain block) are processed in a single batch by the recipient, so to simplify discussion without losing generality, from here on we will refer to "the" (logical) message at a given (sender, relay-chain block) even though in practice this consists of multiple smaller application-level messages.

The Polkadot relay chain & parachain validators together verify that the channel grows & is consumed, in a consistent & reliable way - for details see [authentication for consistent history](#authentication-for-consistent-history) below. They also enforce other guarantees such as boundedness as mentioned, and also *fairness* which we detail below.

### Fairness

Any given receiving parachain may have multiple incoming channels from different sending parachains. In XCMP, we guarantee that a recipient must process these incoming messages **fairly** across all senders.

Specifically, the order in which messages from different senders/channels must be acknowledged, is pre-determined and out of the control of the receiving parachain. In other words, multiple incoming channels for a given recipient are multiplexed into a single ingress queue, and the recipient must process this queue in the aforementioned pre-determined order. Additionally, a receiving parachain must acknowledge at least one new message from a block, if it has any new messages (from different senders/channels) in that block, to ensure liveness.

We provide this guarantee of fairness, mostly to ensure that no message will be left unprocessed for an infinite delay - the sender knows that the receiver must least acknowledge its contents eventually, though they can drop the message after that. This is a value judgement made at the point-of-design of XCMP; we'll monitor its performance in practice.

Although different from the internet's recipient-controlled processing, fairness does not introduce much overhead since for global ordering and reliability, message-passing is co-ordinated via the relay chain anyways, and enforcing fairness on top of this is straightforward.

If receiving parachains feel that they are being spammed by certain sending parachains, they may selectively close these channels.

### More on channels

Polkadot restricts how many different receiving chains a sending chain can send messages to. This is because sending and receiving messages to or from many chains requires resources. The authentication requires that the sending chain informs the relay chain which chains it is sending messages to. A collator of the receiving chain needs to look up data on the relay chain for every chain that could send a message. Both the sending and receiving side may need to implement queues in their state.

This restriction is enforced by allowing XCMP only between pairs of parachain who have set up channels with each other. A parathread is restricted to have at most 100 channels. We also restrict the total number of channels accross all chains in Polkadot by requiring a deposit for each channel. Since a channel requires an ongoing commitment from both sides, setting up a channel requires the permission of both chains.


## Authentication for consistent history

A fork of the Polkadot relay chain defines a possible history of Polkadot. For parachains that refer to a particular relay chain history, we want to act on those messages and only those that were sent in this history. This means that we must use the relay chain to authenticate messages. To make this efficient and scalable we make it as light in computation and data storage as possible for the relay chain. To authenticate messages, a collator can include messages in a PoV block as follows:

1. A collator should find out from the relay chain what the latest messages for their parachain are, and then try to obtain those messages from the sending parachain. They can get these from validators who validated the sending parablock, full nodes of the sending chain or nodes of the receiving chain that already have them.

2. The collator needs to obtain enough data from the relay chain and from the sending chain to produce a proof that they received the right messages as in the previous step. Messages are distributed along with messages proofs, which contain the data from the sending chain.

Once they are included, the parachain will act on messages in order.


## Expected usage profile

Every sending parachain may send up to ~1 MB per chain height in total, to all parachains. In the most unbalanced case, this will be all to a single receiving parachain.

Across all chains then, the worst case is that (C-1) parachains will each send ~1 MB to the same receiver parachain in a single block; however this need not be all distributed during the time slot for that block - see [fairness](#fairness) above.


## Networking

See [XCMP networking](/polkadot/networking/4-xcmp.html).


## XCMP and SPREE

Polkadot's shared security ensures that all parachains correctly execute their code. This means that if we trust a parachain's code, we can trust its behaviour as long as we trust Polkadot's security. SPREE gives a way of further reducing this trust, by allowing parachains to use shared code and enforcing that they execute this piece of code and no other. SPREE modules are pieces of code in parachain's logic that are shared between many chains. Their execution and state are sandboxed away from the other parachain logic and state.

XCMP will allow a SPREE module on one chain to send a message to a SPREE module on another chain and ensure that this message arrives correctly whatever the rest of the parachain logic is on either side. This ensures that knowing only the code of the SPREE module is enough to determine how a particular message will be acted on and any guarantees that this gives will be respected.

For example, there may be a cross-chain token SPREE module. This would allow permissions on which chains can mint a particular token to be managed. In particular, using such a module would allow token transfers between chains without informing the home chain for this token, while still guaranteeing that only the home chain can mint the token. The SPREE module on the chain holding the tokens would have an account for the chain, rather than home chain having accounts for all chains.  For this to work, it is important that we have a sandboxed delivery mechanism, so that the amount of tokens transferred by a message cannot be changed en route.
