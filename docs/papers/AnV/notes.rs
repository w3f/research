
/// Sequences parachain validators in the order the specified validator contacts them for erasure coded pieces.
/// 
/// Requires the parachain validator list be canonically ordered.  Omit any disabled or otherwise non-particiating parachain validators assuming we have consensus on their non-particiation.
fn foo(val: &Validator, pvals: &mut [Validator]) {
    // Fairly distribute the first validator assignment.
    vals.swap(0, val % pval.len());

    // Define a seed that depends upon the validator and parachain
    use sha3::Shake128;
    use sha3::digest::{Input,FixedOutput,ExtendableOutput,XofReader};
    let mut seed = [0u8; 32];
    let mut h = Shake128::default();
    h.input(vals[val].pk);
    for pval in pvals { h.input(pval.pk) };
    h.xof_result().read(&mut seed);

    // Apply a Fisher–Yates shuffle to sequence the remaining parachain validators
    use rand::{Rng, SeedableRng, seq::SliceRandom};
    vals[1..].shuffle(&mut  rand_chacha::ChaChaRng::from_seed(seed));
}



