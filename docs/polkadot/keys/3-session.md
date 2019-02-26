


## Session keys

A session public key should consist of roughly four public keys types: 
 
 - Ristretto Schnorr public key (32 bytes public keys, 64 byte signatures, 96 byte VRFs)
 
   We issue these from the nominator keys acting as validator operators.  We might use an implicit certificate but doing so either restricts us to one validator operator, or else increases code complexity and forces a primary validator operator.  Implicit certificates also make session key records impossible to authenticate without the nominator account, but this sounds desirable.  
   
   We know signers can easily batch numerous VRF outputs into a single proof with these, ala CloudFlare's Privacy Pass.  If we employ these VRFs for block production then signers could periodically publish a "sync digest" that consolidated thousands of their past block production VRFs into a single check, which improves syncing speed.  There is also an avenue to batch verify these VRFs by multiply signers, but it requires enlarging the VRF output and proofs from from 96 to 128 bytes.

 - Small curve of BLS12-381 (48 byte public keys, 96 byte signatures)

   Aggregated signatures verify can faster when using this key if the signer set for a particular message is large but irregularly composed, as in GRANDPA.  Actual signatures are slower than the opposite orientation, and non-constant time extension field arithmetic makes them even slower, or more risky.  Aggregating signatures on the same message like this incurs malleability risks too.  We also envision using this scheme in some fishermen schemes.

   We should consider [slothful reduction](https://eprint.iacr.org/2017/437) as discussed in https://github.com/zkcrypto/pairing/issues/98 for these eventually, but initially key splitting should provide solid protection against timing attacks, but with even slower signature speed.

 - Big curve of BLS12-381 (96 bytes public keys, 48 byte signatures)
 
   Aggregated signatures in which we verify many messages by the same signer verify considerably faster when using this key.  We might use these for block production VRFs because they aggregating over the same signer sounds useful for syncing.  Initially, we envisioned aggregation being useful for some VRF non-winner proofs designs, but our new non-winner proof design mostly avoids this requirement.  Right now, we favor the Ristretto Schnorr VRF for block production because individual instances verify faster and it provides rather extreme batching over the same signer already.

   We also expect faster aggregate verification from these when signer sets get repeated frequently, so conceivably these make sense for some settings in which small curve keys initially sound optimal.  We envision signature aggregation being "wild" in GRANDPA, so the small curve key still sounds best there.
 
 - Authentication key for the transport layer.
 
   We might ideally include node identity form libp2p, but secio handles authentication poorly ([see the secio discussion](https://forum.web3.foundation/t/transport-layer-authentication-libp2ps-secio/69)).

A session public key record has a prefix consisting of the above three keys, along with a certificate from the validator operator on the Ristretto Schnorr public key and some previous block hash and height.  We follow this prefix with a first signature block consisting two BLS signatures on the prefix, one by each the BLS keys.  We close the session public key record with a second signature block consisting of a Ristretto Schnorr signature on both the prefix and first signature block.  In this way, we may rotate our BLS12-381 keys without rotating our Ristretto Schnorr public key, possibly buying us some forward security.

We include the recent block hash in the certificate, so that if the chain were trusted for proofs-of-possession then attackers cannot place rogue keys that attack honestly created session keys created after their fork.  We recommend against trusting the chain for proofs-of-possession however because including some recent block hash like this only helps against longer range attacks. 

We still lack any wonderful aggregation strategy for block production VRFs, so they may default to Ristretto Schnorr VRFs.  In this case, the Ristretto Schnorr session key component living longer also help minimize attacks on our random beacon. 
