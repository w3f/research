https://forum.web3.foundation/t/account-key-creation-ideas-for-polkadot/68


# Account key creation ideas for Polkadot

We found a trick for using Ed25519 "mini" private keys in [schnorr-dalek](https://github.com/w3f/schnorr-dalek/blob/master/src/keys.rs), meaning users' "mini" private key consists of 32 bytes of unstructured entropy.  

There are no serious problems with [BIP39](https://github.com/bitcoin/bips/blob/master/bip-0039.mediawiki) so we suggest a similar strategy for deriving secret keys in Polkadot.  We could however modernize BIP39 in a couple small but straightforward ways: 

 - *Argon2id should replace PBKDF2.*  Adam Langely sugests [using time=2 and 64mb of memopry](https://github.com/golang/crypto/commit/d9133f5469342136e669e85192a26056b587f503) for interactive scenarios like this.  In principle, one might question if this scenario should truly be considered interactive, but conversely one could imagine running this on relatively constrained devices. We might also improve the [argone2rs](https://github.com/bryant/argon2rs/issues) crate too, especially to [ensure we use at least v1.3 since v1.2.1 got weaker](https://crypto.stackexchange.com/a/40000).
 - *Rejection sampling to support larger wordlists.*  We could employ rejection sampling from the initial entropy stream to avoid tying ourselves to the list size being a power of two, as BIP39 seemingly requires.  We can provide roughly the existing error correction from BIP32, even working in a ring of this order.
 - *Actually provide a larger wordlist.*  We're discussing enough entropy that users might benefit form using diceware-like word lists with 12.9 bits of entropy per word, as opposed to BIP32's 11 bits of entropy per word.  It's possible some diceware word lists contained confusable words, but reviews exists at least for English.  We might worry that larger wordlists might simply not exist for some languges.  It's also easier to quickly curate shorter lists.

There are also more speculative directions for possible improvements: 

 - *Improve error correction.*  Right now BIP39 has only a basic checksum for error correction.  We could design schemes that corrected errors by choosing the words using Reed-Solomon, meaning non-systematic word list creation with code words, except naively this limits our word list sizes to finite field sizes, meaning prime powers.  We would instead likely run Reed-Solomon separately on each prime power divisor of the word list's order.  We should however evaluate alternatives like other [generalisations of Reed-Solomon codes to rings](https://hal.inria.fr/hal-00670004/file/article.pdf), or even working in a field of slightly larger order and reject choices that fall outside the wordlist.
 - *Support multiple Argon2id configurations.*  We might conceivably support multiple argon2id configurations, if small device constraints become a serious concern.  We could select among a few argon2id configuration options using yet another output from the Reed-Solomon code.  We'd simply use rejection sampling to choose the user's desired configuration.

