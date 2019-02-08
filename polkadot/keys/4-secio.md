https://forum.web3.foundation/t/transport-layer-authentication-libp2ps-secio/69



## Transport layer authentication - libp2p's SECIO

We must authenticate connections as the transport layer from session keys, which could happen in several ways, like signing a hash provided by the transport layer.  A priori, we could simplify everything if the session key simply included the static key used in authentication component of the transport layer's key exchange, which might help avoid some security mistakes elsewhere too.  

There are numerous transports for libp2p, but only QUIC was actually designed to be secure.  Instead, one routes traffic through [libp2p's secio protocol](https://github.com/libp2p/specs/pull/106).  We trust QUIC's cryptographic layer which is TLS 1.3, but secio itself is a home brew job with no serious security analysis, which usually [goes](https://github.com/tendermint/tendermint/issues/3010) [poorly](https://github.com/tendermint/kms/issues/111).  

There has been minimal discussion of secio's security but [Dominic Tarr](https://github.com/auditdrivencrypto/secure-channel/blob/master/prior-art.md#ipfss-secure-channel) raised some concerns in the [original pull request](https://github.com/ipfs/go-ipfs/pull/34).  I'll reraise several concerns from that discussion: 

First, there is no effort made to hide secio node keys because "IPFS has no interest in [metadata privacy]" according to Brendan McMillion, so nodes leak their identities onto the raw internet.  We think identifying nodes sounds easy anyways, but at minimum this invites attacks.  There is an asymmetry to key exchanges that leaks less by first establishing a secure channel and only then authenticating.  We might reasonably break this asymmetry by deciding that specific roles require more privacy.  We might for example help protect validator operators or improve censorship resistance in some cases, like fishermen. 

Second, there is cipher suit agility in secio, at minimum in their use of multihash, but maybe even in the underlying key exchange itself.  We've seen numerous attacks on TLS <= 1.2 due to cipher suit agility, especially the downgrade attacks.  I therefore strongly recommend using TLS 1.3 *if* cipher suit agility is required.  We could likely version the entire protocol though, thus avoiding any cipher suit agility.  In any case, constructs like multihash should be considered hazardous in even basic key exchanges, but certainly in more advanced protocols involving signatures or associated data.

Third, there are [no ACKs in secio](https://github.com/libp2p/go-libp2p-secio/issues/12) which might yield attacks when a higher level protocol actually depends upon the underlying insecure transport's own ACKs.  I suppose UDP transport support already requires higher level protocol handle any required ACKs themselves anyways.  ([related](https://github.com/OpenBazaar/openbazaar-go/issues/483)).

As QUIC uses UDP only, we could add TCP based transport that uses TLS 1.3, perhaps by extending libp2p's existing transport with support for TLS 1.3, or perhaps adding a more flexible TLS 1.3 layer.  We might prefer a flexible TLS 1.3 layer over conventional TLS integration into libp2p extending transports because our authentication privacy demands might work differently from TLS's server oriented model.  

We could identify some reasonable [Noise](https://noiseprotocol.org/noise.html) [variant](https://github.com/mcginty/snow), *if* avoiding the complexity of TLS sounds like a priority and ACKs are always handled by higher layers.  I believe Noise XX fits the blockchain context well, due to Alice and Bob roles being easily reversible, improved modularity, and more asynchronous key certification from on-chain data.  At the extreme, we could imagine identifying particular handshakes for particular interactions though, like GRANDPA using KK and fishermen using NK.  

In short, we should make a new years resolution to replace secio, with our two simplest routes being either TLS 1.3 or Noise XX. 

---

Aside from these authentication repairs, there are two additional directions for possible future work:

 - *Post-quantum key exchange.*  We'd likely employ LWE scheme here.  Right now, CSIDH remains young and slow, but the small key size and long-term keys claims indicate that   [CSIDH](https://www.esat.kuleuven.be/cosic/csidh-post-quantum-key-exchange-using-isogeny-based-group-actions/) might integrate better with Noise and blockchains.  I'd skip the [existing specification](https://github.com/noiseprotocol/noise_wiki/wiki/Post-Quantum-Noise-with-New-Hope) for integrating Noise with New Hope Simple.  Adam Langely has good arguments for [selecting the NTRU variant NRSS+SXY for Google's CECPQ2 experiment](https://www.imperialviolet.org/2018/12/12/cecpq2.html).  I  the module-LWE [Kyber](https://pq-crystals.org/kyber/)
 - *Forward-security.*  There is some multi-hop message forwarding in libp2p, but it provides only another addressing technique, not a true connection abstraction layer like say GNUNet's CADET layer.  CADET actually employs the Axolotl forward secure ratchet.  
 
 I'm always a fan of both post-quantum and forward security for encryption, but the benefits might prove minimal in our context.
 

