---
title: the history of bostrom
tags: cyber, bostrom, bootloader, history
alias: bostrom history, the old chain of bostrom, bostrom story, the story of bostrom, why we need bootloader, bostrom tokenomics, bostrom token model, bostrom/mint, bostrom mint, energy mint, bostrom genesis, bostrom/genesis, bostrom infrastructure, bootloader improvement proposal, bootloader improvement proposals, bips, finalization of $BOOT distribution, neuron of bostrom, moon-passport, .moon names, cw-cyber
crystal-type: article
crystal-domain: cyber
---

# the history of bostrom

One page for the first life of bostrom: the cosmos chain that ran from 2021 to 2026 as the bootloader of [[cyber]]. It replaces the pages this repository carried about that chain. They are kept whole on the branch [`legacy/graph-pages`](https://github.com/cyberia-to/bostrom/tree/legacy/graph-pages).

## the line of time

| when | what |
|---|---|
| 2016 | the idea arrives as cyberChain |
| 2018 | the euler network puts a rank over a graph inside consensus, on graphics cards; its tokens are test tokens |
| 2021-11-05 13:22:42 UTC | bostrom begins |
| 2022 | space-pussy begins beside it, the second network on the same software |
| 2024-12 | 70,000 neurons, about a thousand of them linking; 2.9 million cyberlinks over 3.1 million particles; connectivity 0.94 |
| 2026-08-05 08:55:00 UTC | bostrom is halted at height 25,120,712 |
| 2026-08-28 | its state is extracted and buried, every file pinned |
| 2026-10-17 | the genesis of the new bostrom is built from the burial and its digests are blessed |

## why a bootloader

Superintelligence did not exist, and a mistake in its first state was judged to cost more than any mistake before it. So every assumption was to be tried first on a network where mistakes were allowed. bostrom was that network: an experimental ground that would bring the expertise and the resources the goal needed, and the place where the starting knowledge of cyber would be gathered.

The same page of 2021 named what the final network needed and the hardware of the time could not give: hashing and signatures that hold against quantum computers, a larger particle space, privacy by zero knowledge, a computing model that runs in parallel by itself. Those became [soft3](https://github.com/cyberia-to/soft3).

The scale thought necessary for bootloading was a trillion cyberlinks and ten million neurons. The chain reached five orders of magnitude less in links and three less in neural activity. Connectivity stayed below the threshold where the theory predicts that collective intelligence ignites. The bottlenecks appeared where the theory said they would: that is the calibration the chain left.

## what the chain was

| | |
|---|---|
| the software | go-cyber: a cosmos chain with tendermint consensus, up to 92 validators, called heroes |
| the graph | a cyberlink was a neuron, two particles and a time; a particle was a content address of the old kind |
| the rank | computed over the whole graph inside consensus, every block, on one graphics card per validator |
| bandwidth | a neuron spent will to link and paid no fee for a cyberlink; the price followed the load |
| programs | wasm contracts: the moon passport and its names, the gift, the senate |
| liquidity | a pool module with batched swaps at one price per batch, 0.3 % fee |
| the bridge | transfers to and from the cosmos chains |

Its improvement process was the bootloader improvement proposal, with the states draft, accepted, rejected, tested on space-pussy, implemented on bostrom.

## its six tokens

| token | denom | role | at the halt |
|---|---|---|---|
| BOOT | `boot` | consensus and governance; 1.09 % inflation; bonding created H one to one | 482,287,925,778,234 |
| H | `hydrogen` | the liquid form of staked BOOT; burned to mint V and A | 305,452,862,328,021 |
| V | `millivolt` | will: a cyberlink burned V at the bandwidth price; the mint price doubled every 4 billion ever minted | 2,182,319,343 |
| A | `milliampere` | focus: the weight of a neuron's links in the rank; the mint price doubled every 32 billion | 13,889,231,915 |
| TOCYB | `tocyb` | the promise of CYB to its holder | 281,405,532,467,645 |
| LI | a contract token | the late gateway token | — |

Every token derived from the one above it: H needed staked BOOT, V and A needed burned H, so every unit of the network's resources had a cost in committed stake. A transfer of V or A burned 2 % of it.

The resource tokens do not return. What they priced — the room to write and the weight of a link — the new network prices with a stake on the link itself. The planned economy is in [economics](economics.md).

## how BOOT was distributed

One structure for BOOT and TOCYB at the genesis of 2021:

| share | to |
|---|---|
| 70 % | the gift, for the holders of other networks |
| 11.6 % | cybercongress, the founders |
| 8.3 % | the community of the first test networks |
| 5.1 % | the senate |
| 5 % | the great web foundation |

Most of the gift was never claimed and stayed in multisigs through the five years: 603T BOOT and 700T TOCYB in the gift's multisig, 148T BOOT claimed. That is why control of the majority of BOOT ended with the founder, and why the first job of the reborn bostrom is to dilute that majority by work.

## the passports

47,837 moon passports were issued by a contract: a nickname, an owner, an avatar. A name cost by its length, from 100G BOOT for three symbols to 1M BOOT for eight. Every passport is one link of the new genesis, from its owner to the particle of its nickname.

## how it was buried

Nothing was thrown away. The state at the halt was extracted into files, every file was pinned by its content address, its sha256 and its size, and the list of pins is [`snapshot/manifest.json`](../snapshot/manifest.json). The graph was rebuilt from the blocks themselves: all 25,120,712 were scanned, and the 2,949,732 cyberlinks found equal the chain's own counter. The burial is served at [snapshot.bostrom.network](https://snapshot.bostrom.network), and the page in [`snapshot/app/`](../snapshot/app/) checks a balance from a name, an address, a mnemonic, a key or a ledger, on the visitor's machine.

How much of the content the particles name can still be fetched — 97.6 % — is in [`audit/particle-availability-2026-10-17.md`](../audit/particle-availability-2026-10-17.md).

## how it comes back

The burial is the genesis of the new network. The balances are carried as they stood, delegated and unbonding coins return to their owners, liquidity positions are dissolved into their reserves, and every cyberlink is carried with its author and its place. The rules are in [`genesis/`](../genesis/), and the result is pinned in [`genesis/genesis.lock`](../genesis/genesis.lock).

An owner of the old chain is the same owner on the new one: a key that signed on the old chain controls the same balances, and an account that never signed claims its own through the legacy bridge.

## what was learned

The papers that read the chain as an experiment stay in [`research/`](research/): the architecture of the chain, the scale at which intelligence appears, the derivation of that scale, the starting state that is provably best, and the graph compiled into a model.

## where the old pages are

On [`legacy/graph-pages`](https://github.com/cyberia-to/bostrom/tree/legacy/graph-pages), as they stood on 2026-11-22: the pages of the modules, the validators, the guides, the improvement proposals, the plan of a migration to rust and the specification of a virtual machine on graphics cards, both replaced by soft3. The chain's code is [go-cyber](https://github.com/cyberia-to/go-cyber).
