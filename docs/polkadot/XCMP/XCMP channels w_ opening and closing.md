# XCMP channels w/ opening and closing

## Data Structures

Operational data structures. These can be changed each block.

```
watermark: map ParaId => (BlockNumber, ParaId)

Channel {
  last_updated: BlockNumber
  mqc_head: Hash | null // ← null in case there is no prior messages
}
cst: map ParaId => [Channel]
cst_roots: map ParaId => Hash
```

Metadata of channels. Can be changed only at the session boundary.

```
ChMetadata {
  recipient: ParaId
  
  // the maximum number of messages this channel can store
  capacity: integer 

  sender_deposit: Balance    // balances of sender and recipient.
  recipient_deposit: Balance // consider merging if symetrical
  // ❓ what else? 
}
cmt: map ParaId => [ChMetadata]
```

Bookkeeping for the upcoming changes at the session boundary. Can be modified during the session. 

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

// also sets for quickly checking if there are pending open/close requests
// from certain sender / recipients
```

Data maintained between sessions. The condemned set can only be altered at the session change boundary.

```
/// An index of a channel. Used for refer columns in a CST row.
type ChannelIndex

CondemnedCh {
  sender: ParaId
  // ❓ storing an index here is problematic since this structure 
  // can live multiple sessions and the indexes can be destroyed by offboarding.
  n: ChannelIndex
  // each session this counter is decremented by 1. If reaches zero
  // this channel is removed.
  counter: integer
}

/// The channels that were registered to be closed.
condemned_channels: [CondemnedCh]
```

## Messages

Those perhaps are gonna be some sort of upward messages.

`init_open_channel(recipient)`

- checks if sender already has a channel to recipient or if there is already intention to open a channel.
- checks if the sender is within the limit of opened channels.
- checks if the sender is equal to recipient.
- eagerly reserve the deposit for opening the channel. The deposit is taken from the parachain account.
- appends a request to open a channel to the list of pending changes.
- ❓send a DM to the recipient

`accept_open_channel(i)`: `i` - index in the list of pending open requests.

- check that ith request exists
- check that the origin of this `accept_open_channel` message corresponds to the recipient of the entry for ith pending open request.
- eagerly reserve the deposit for the channel. The deposit is taken from the parachain account.
- confirms the ith request

`close_channel(sender, i)` , `i` - index of a channel in the CST row of `sender`.

- checks that `sender` has ith column in its CST row
- checks that the origin of this `close_channel` is either the sender or the recipient.
- checks if there is already a pending request registered.
- inserts a new entry to a list of close requests.

## Processing rules

### Acceptance Function

for each candidate for para $P$:

1. Check if the XCMP bitfield is valid. Specifically:
    1. that it's length is at most that of the CST row length for $P$.
2. Check that each channel in the bitfield can accept messages.
    1. the channel should be open, i.e. it should not be present in the condemned set.
3. Check if the watermark found in the candidate is valid. :question: How exactly do we want to check the watermark? Depends on the checking regime.

### Enactment

For a candidate for para $P$ we do the following:

1. Locate the CST row $R$ keyed by $P$.
    1. For each index of an each bit set to 1:
        1. update the row to `(MR, RC)` where `MR` is the `sender_message_queue_merkle_root` found in the candidate receipt and `RC` is the current relay-chain block height.
        2. Recompute the new root hash for $R$
2. Then update the watermark corresponding to $P$ found in the candidate receipt.

### On Session Change

1. ❓Handle chain offboarding (potentially onboarding as well?). This could skew some channel indexes in CST rows.
2. For each request $R$ in the open channel request list:
    1. if $R$ is not confirmed,
        1. increment its age.
        2. if the age reached a preconfigured time-to-live limit, then 
            1. refund the sender deposit to the sender
            2. remove $R$
    3. if $R$ is confirmed, 
        1. append a new CST column with the initial value.
        2. remove $R$
        3. :question: should we watch out for the races (caused by e.g. staggered channel open requests)
3. dequeue all pending channel close requests:
    1. append an entry to the condemned channel set. The counter is initialized to a preconfigured value.
2. decrease the counter for the channels in the condemned set.
3. if the counter hits 0 OR if the channel empty, then finalize closure:
    1. if there are still messages left in the channel, send a DM containing the contents of the CST column.
    1. remove the CST column
    1. remove the corresponding entry from the CMT.
    1. remove the entry from the condemned set.
    1. return the deposits.
4. Recompute roots of dirty CST rows.
