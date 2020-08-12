# HRMP channels

## Data Structures

```
Candidate {
  dmq_watermark: BlockNumber,
  hrmp_messages: [HRMP_Message]

  // .. rest irrelevant fields
}

HRMP_Message {
  sender: ParaId
  recipient: ParaId
  payload: bytes
}
```

A HRMP channel is:

```
Channel {
  sender_deposit: Balance    // balances of sender and recipient.
  recipient_deposit: Balance // consider merging if symetrical

  // number of messages and total number of bytes used
  // by the sender in this channel
  used_places: integer
  used_bytes: integer
  
  // if a channel is sealed, then it doesn't accept new messages.
  // If it is sealed and `used_places` reaches 0 then the channel
  // can be removed at the next session boundary.
  sealed: boolean
  
  // note that this doesn't contain the messages. The messages
  // are stored in the recipients' DMQs.
}

channels: map (ParaId, ParaId) => Channel
```

```
ChOpenRequest {
  sender: ParaId
  recipient: ParaId
  // true - if the recipient sent `accept_open_channel`
  confirmed: boolean
  // the age of this request. At each session boundary this value is
  // incremented by 1. When it reaches a certain pre-configured
  // value the request deemed expired.
  age: integer
}
// A list of pending channel open requests.
open_requests: [ChOpenRequest]

ChCloseRequest {
  initiator: ParaId // should be equal to either sender or recipient
  sender: ParaId
  recipient: ParaId
}
// A list of pending channel close requests.
close_requests: [ChCloseRequest]

// TODO: Number of open requests per a sender.
// TODO: There should be a set for quickly checking the close requests
```

## Messages

`init_open_channel(recipient)`:

- check the following conditions. If any of them doesn't hold - bail:
    - sender (= origin of this message) and recipient exist
    - sender is not recipient
    - sender doesn't have a channel to recipient.
    - there is no existing intention to open a channel between sender and recipient
    - sender has capacity for a new channel (open requests count towards the capacity)
    - the origin has enough funds to cover the deposit.
- reserve deposit for a sender
- append a new entry into the open channel request list.

`accept_open_channel(i)`, `i` - is the index of open channel request.

- check:
    - the ith channel open request exists
    - ith open channel request recipient is the origin of this message
    - the origin has enough funds to cover the deposit
- reserve deposit for a recipient
- confirm the ith request in the open channel request list.

`close_channel(sender, recipient)`:

- check
    - the channel between `(sender, recipient)` exists
    - the channel is not sealed
    - origin of the message is either sender or recipient
    - that there is no existing close request for the channel
- append a new entry into the close channel request list.

## Processing Rules

### Acceptance Function

> ℹ️ Acceptance criteria MUST not depend on the relay-chain data that is able to change during the session (unless it is the para specific data)

for each candidate $C$ for para $P$:

1. Check that `C.hrmp_messages` are sorted by recipient Para Id ascension. Along the way, check that there are no two messages per one recipient.
2. For each HRMP message $M$ in `C.hrmp_messages` check:
    1. $M$ is sent to a channel that is opened. I.e. the channel `(P, M.recipient)` exist and it is not sealed.
    1. doesn't overfill $M$'s recipient channel. I.e. the size after adding the message doesn't exceed the configured limits.
3. Check that the candidate correctly updates the watermark.
    1. the watermark should be strictly greater than the last watermark for $P$,
    1. :question: TODO: the watermark cannot be smaller than the earliest message in the DMQ **OR** the watermark should point on an existing message in the DMQ or the latest block.

### Enactment

> ℹ️ We rely on the invariants set by the acceptance function here.

for each candidate $C$ for para $P$:

1. Prune the DMQ up to `C.dmq_watermark`. For each pruned DMQ message of kind `HRMP_Message` $M$,
    1. decrement the space used by $M$ in the channel `(M.sender, P)`.
1. for each message $M$ in `C.hrmp_messages`:
    1. append $M$ into the corresponding DMQ of the $M$'s recipient.
    2. increment the space used by $M$ in the channel `(P, M.recipient)`
1. Update $P$'s watermark

### On Session Change

1. Handle para offboarding. For an offboarded para `P` we should:
    - Remove all inbound channels of $P$, i.e. `(_, P)`
    - Remove all outbound channels of $P$, i.e. `(P, _)`. 
2. For each request $R$ in the open channel request list:
    1. if $R$ is not confirmed,
        1. increment its age.
        2. if the age reached a preconfigured time-to-live limit, then
            1. refund the sender deposit to the sender
            2. remove $R$
    2. if $R$ is confirmed,
        1. create a new channel between sender → recipient
        2. remove $R$
3. for each pending channel close requests:
    1. if the channel has no messages, remove it eagerly. Otherwise, set `sealed` to true.
4. remove all channels that are sealed and has no messages.

to remove a channel:

1. return the sender's and recipient's deposits.
2. remove the channel entry from `channels`
