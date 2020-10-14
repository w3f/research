# XCMP

XCMP is Polkadot's cross chain message passing protocol. It allows one parachain to send messages to another parachain and provides guarantees about the delivery of these messages. Polkadot allows parahchians to send each other mesages as long as they have established messagng channels with each other. In this document we review first the core priciple of the XCMP deisgn and then review authentication, network delivery, channels, and SPREE that can be used for example trustless token transfers. 

## Core design principles

Parachain will host dapps on them and interoperability among dapps is highly facilitated by ordered and timely delivery messages. Polkadot delivery gurantees include: 

- guaranteed message delivery - a chain will receive the message as long as it keeps producing blocks.

- trustless delivery - Polkadot's shared security ensures the correctness of message delivery and autehenticity as long as we trust the code that produces and consumes them.

- ordered delivery - messages arrive in a definied order.

Ordered and timely delivery of messages is not given in many applications such as some web applciatin or. This is because TCP/IP gives weaker guarantees about delivery and hence the web application eeds to deal with these issues. 
This involves having message acknowledgements and timeouts. To build atomic transactions on such a layer requires a lot of work. Polkadot's shared security allows us to get much stronger guarantees than TCP/IP does.
While Cosmos allows the choice of havig ordered delivery, there are no guranatees that messages will arrive ever due lack of an general incentive model for this purpose. 
The trade off for Polkadot however is that non-availability of XCMP messages can halt a parachain, so Polkadot needs to ensure that this never happens.

We want all these properties while maintaining scalability, in that the relay chain should not be overwhelemed if 100 parachains send messages to 10,000 destinations in a single relay chain block, which we discuss in the next sections.


## Authentication for consistent history

A fork of the Polkadot relay chain defines a history of Polkadot. Chains may act on messages before the sending of this message was finalised. We want to act on those messages and only those that were sent in this history. This means that we must use the relay chain to authenticate messages. To make this efficient and sclable we make it as light in computation and data storage as possible for the relay chain. To autheticate messages, a collator can include messages in a PoW block as follows:

1. A collator should find out from the relay chain what the latest messages for their parachain are, and then try to obtain those messages from the sending parachain. They can get these from validators who validated the sending parablock, full nodes of the sending chain or nodes of the receiving chain that already have them.

2. The collator needs to obtain enough data from the relay chain and from the sending chain to produce a proof that they received the right messages as in 1. Messages are distributed along with messages proofs, which contain the data from the sending chain. 

Once they are inlcuded, the parachain will act on messages in order. 


## Channels

Being able to send and receive messages to or from many chains requires resoucres. The authentication requires that the sending chain informs the relay chain which chains it is sending messages to. A collator of the receiving chain needs to look up data on the relay chain for every chain that could send a message. Both the sending and receiving side may need to implement queues in their state.

As a consequence, Polkadot restricts how many different chains a chain can send messages to. 

## Networking

## XCMP and SPREE

Polkadot's shared security ensures that all parachains correctly execute their code. This means that if we trust a parachain's code, we can trust its behaviour as long as we trust Polkadot's security. SPREE gives a way of further reducing this trust, byu allowing parachains to use shared code. SPREE modules are pieces of code in parachain's logic that are shared between many chains. Their execution and state are sandboxed away from the other parachain logic and state.

XCMP will allow a SPREE module on one chain to send a message to a SPREE module on another chain and ensure that this message arrives correctly whatever the rest of the parachain logic is on either side.







