# XCMP

## Core design principles

Guaranteed message delivery - a chain will receive the message as long as it keeps producing blocks
This makes coding dapps much easier as we don't have to deal with so many failure cases such as timeouts.

Trustless delivery - Polkadot's shared security ensures the correctness of message delivery and autehenticity as long as we trust the code that produces and consumes them.

Ordered delivery - 


## Key trade-offs - What makes XCMP different?

Polkadot's shared security model allows it to have much stronger guarantees about ordering and eventual delivery than most cross-chain message systems. 


## Authentication 
- XCMP authentication works like this:

1) A fork of the Polkadot relay chain defines a history of Polkadot. We want to act on those messages and only those that were sent in this history. This means that we must use the relay chain to authenticate messages.

2) A collator should find out from the relay chain what the latest messages for their parachain are, and then try to obtain those messages from the sending parachain. They can get these from validators who validated the sending parablock, full nodes of the sending chain or nodes of the receiving chain that already have them.

3) The collator needs to obtain enough data from the relay chain and from the sending chain to produce a proof that they received the right messages as in 1.

4) Messages are acted on in order


## Channels

## Networking

## SPREE





