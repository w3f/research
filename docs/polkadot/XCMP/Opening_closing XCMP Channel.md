# Opening/closing XCMP Channel
This write up describes how [XCMP channels](./index.html) are opened and closed.

**Definition[Unidirection XCMP Channel]** In this type of channel messages flow only in one direction. Each channel has its unique configuration. Agreeing on opening/closing of the channel and the configurations of the channel is still done by both sides. The deposit can put down by both or one party.

**Definition[Bidirectional XCMP Channel]** In this type of channel messages can flow in both directions. The configuration for this channel will be the same for both directions, which means that one side cannot send more messages than the other side. The deposit can be put down by one or both sides.

The trade-off is that unidirectional channel type is more flexible and bidirectional channel type is more efficient in terms of openin and closing the channels. However, note that in bidirectional channel types there might be more need for interaction to agree on configurations and how to split the deposit of the channel.

For this writeup we assume XCMP channels are unidirectioonal, mainly because of the flexibility it gives us.

When opening a channel a deposit needs to be put down. The deposit is locked as long as the request for the channel is not withdrawn or the channel is still open. In this document, we denote the initiator of the channel as party $A$ and the other party of the (potential) channel as party $B$. Note that both parties are able to send and receive.


To open a channel both parties $A$, $B$ have to agree to the opening of the channel, however, closing a channel can be done from one side. Since messages that are not acted on yet or are still being routed when the  closing of channels are signaled, we need to incorporate two types of delay. For opening a channel, this delay should be high enough such that party $B$ has enough time to potentially close existing channels in case it has reached its limit of total channels. For closing a channel a delay is important to ensure that messages are not lost in the time needed to ensure both sides are aware of the closing.

A channel is opened after party $B$ acknowledges the channel.

We need to have two delays $D$ and $\delta$ defined by the network (to ensure that channels obey at least that delay). This delay should depend on the time it takes for a change in the relay chain be noticed by a parachain and the time it takes for messages on the way to arrive.

## Opening can works as follows:

**Phase 0**: A parachain can initiate a channel to another parachain by sending an upward `init_open_channel` message to the relay chain, that includes:

* The recipient's (party $B$) parachain/parathread ID
* Conditions for closing that channel: define a local delay $\delta$ such that $\delta >= D$, how many messages can be sent before any of them is received (basically size of buffer that either end needs), size of messages maybe (!).

**Phase 1**: This upward message will add an entry to $A$'s parachain CST on the relay chain. In this table every entry has information such as the recipient parachain ID, configurations such as the size or number of messages allowed on this channel, and the status of the channel that can be "open", "pending open", "pending closing", and "closing - receiving messages". At this stage the status of the channel will be set to "pending open". Note that recipient party $B$ needs to also lock a predefined amount of funds for this channel.

**Phase 2**: Once the relay chain sees such a message it needs to send a downward message to the party $B$'s parachain that includes the metadata of the channel (see above), that consists of the parachain ID of initiator $A$, the sizes and number of messages.

**Phase 3**: If $B$'s parachain has less than the limit (which is currently set at 100 channels) and is willing to have a channel open with the iniator parachain $A$, it needs to send an upward `accept_open_channel` message to the relay chain. This upward message includes the metadata it was sent earlier.

**Phase 4**: Once the relay chain receives the `accept_open_channel` message it needs to check whether the metadata sent by $B$'s message is in accordance with the created entry in $A$'s parachain CST entry that was created earlier for this purpose. If it does, the status in $A$'s CST entry corresponding to this channel is set to "open". A corresponding entry in $B$'s CST is also created with the status "open". This should be followed by a generation of a default first entry for the channel in the CST: both $A$'s and $B$'s parachain get an entry in the CST with the all-zero bitstring (so the tuple: (0x00..00, 00).

**Phase 4'**:If $B$'s parachain does not respond to the relay chain message, $A$ can withdraw its channel initiation at any moment and get their funds released. Note there needs to be a minimum time passed between initating an opening of a channel and withdrawing this request to avoid race conditions.

## Closing can work as follows:
Let us assume there is a unidirection channel between $A$ and $B$ and $A$ wants to close this channel. In this section, we denote the initator of the closure by party $A$ and the other side of the channel with party $B$.

**Phase 0**: Party $A$ can send the request for closure as an upward `init_close_channel` message to the relay chain. After this point no new XCMP messages of $A$'s parachain are accepted for that channel.

**Phase 1**: On the relay chain the status of the channel becomes "pending closing".

**Phase 2**: The relay chain sends a downward message to $B$'s parachain to signal closing.

**Phase 3**: $B$'s parachain has up to $D$ time slots after the close initialisation (or some other definition of time) to react, by acting on all left open messages in the queue plus potentially sending new messages (for the last time) to $A$'s parachain. It then can end the channel with some `accept_close_channel` message. After this point $B$'s parachain cannot send messages on this channel. Once $B$ has sent this message we can go to **Phase 5**.

**Phase 4**: In case $B$ does not respond, we need to wait for $D$ time to make sure $B$ has time to notice the closing process.

**Phase 5**: Once this timeout is finished or $B$ has sent an acklodegement: Either $A$ needs to have received and acted on all messages that were sent by $B$ until the end of the previous timeout or another timeout $\delta$ needs to pass (basically Phase 3 or 4, which ever happens first). During Phase 5, the status of the channel is "closing - receiving messages".

With waiting for messages to be received, we can prove that they have been using the watermark, which means that we optimistically we can close much faster than the timeout. In particular, with parathreads, the not sending delay can be shorter than their average block time, but the delay for receiving cannot be. We'd close channels between two parathreads a lot faster if these were different numbers.

**Phase 6**: At this stage all messages in $A$'s queue are dropped and the channel is closed. The other parachain, $B$, is not able to respond (via XCMP). But the participants in the channel could of course make other agreements for this situation.

**Phase 7**: Now the entries can be deleted in channel metadata table of both $A$ and $B$ on the relay chain. And also on the corresponding CST tables. The deposit for this channel will be released to boths sides of the channel.




------

## Implementation Questions and Answers

**Unanswered questions are in bold.**

* How much does it cost to open a channel?
    * Answer: A sensible cost for the relay chain time plus a more significant deposit. The deposit should scale to limit the total number of channels.
    * Follow-up questions: **Who pays the deposit? Is it paid out of the parachain bond? What about for parathreads?**
        * Answer: The deposit is paid out of the parachain account and the same for parathreads. Paras do have DOTs that are not locked for their bond, right?
    * **Are you imagining an exponential ramp-up of cost/deposit? How should the costs differ based on channel capacity?**
        * Answer: Np, we are imagining a fixed cost per channel for now. The storage /throughput on the relay chain side do not depend on the channel capacity, so the relay chain deposit and costs will not do either.
* How many channels can any para open at any time? Should this be different for chains and threads?
    * Answer: It's different for chains and threads. The plan was 100 per thread and chains unlimited, but the deposit should put an economic limit.
* What are the guarantees about message delivery in channels? Are these guarantees upheld at channel-closing or the sender-para being offboarded?
    * Answer: Channel closing is planned to be slow to give the receiver a chance to receive messages. We have no plans to keep messages beyond sender offboarding.
    * An alternative to our design above would be to move message data from relay chain state associated with the sender to that of the receiver. That would deal with the off-boarding issue, but require more code complexity. I think this is not part of the XCMP MVP and we should implement it later if at all.
    * Another alternative is for there to be a downwards message to the receiver in the event that removing data from the senders' CST row causes messages to be dropped.
    * However both of these would be really expensive if a chain with many channels was off-boarded. If possible, it would be better to keep the chain metadata around for the channel closing timeout and trigger the closing process for all channels. Then you just have the problem of how to delay the clean up.
* What information does a para receive about messages lost when a channel is closed? On either the sending or receiving side of the channel?
    * Answer: Unless we change the design above, none. It's unclear how we could send information to both sides because then we are not sure if anything is actually dropped.
* How are open channels handled when a para migrates from chain to thread or vice-versa?
    * Answer: For thread to chain, we should just keep them open. For chain to thread, we should either keep them all open or introduce more states. Whatever we do, there should be no messages dropped as a result. We should code doing nothing and then fix it later.
    * The issue here is not just the numbers, but the channel capacity. Parachains will typically have many low capacity channels and parachreads will want few channels with high capcity. There may be a limit on total capacity. This means that we need mechanisms for changing the capacity of existing channels.
