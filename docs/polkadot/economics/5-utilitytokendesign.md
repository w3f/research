====================================================================

**Authors**: Samuel Häfner

**Last updated**: October 13, 2021

====================================================================

# Utility Token Design

**Paper Link:** [TBD]

In this project, I analyze some general design principles of utility tokens that are native to a proof-of-stake blockchain. Utility tokens are cryptographic tokens whose main economic use is to access and consume the respective token issuer’s services. 

The DOT, issued by the Polkadot network, is a utility token. The services offered by the Polkadot network consist of parachain slots, which come with shared security and means to communicate with other parachains. To obtain one of the slots, the users --- i.e., the teams building on Polkadot --- need to put forth DOTs in recurrent slot auctions.  

For the analysis, I set up a dynamic general equilibrium model of utility tokens that serve as a means of payment on a two-sided market platform and are repeatedly traded in a spot market. 

On the one side of the platform, there are users that derive utility from consuming the services provided by the platform. On the other side, there are validators that provide the required security and receive tokens in return. Validators need to repeatedly sell some of their tokens to cover their costs; users need to repeatedly buy tokens to consume the services. The token market balances token supply and token demand.

The main results of the analysis are the following: First, I find that utility token markets are generally efficient because they result in the socially optimal provision of services. Second, I uncover a tension between the price dynamics of utility tokens, the evolution of the provided services, and the payment details on the users’ side. The findings have implications both for antitrust regulation and for practical token design.
