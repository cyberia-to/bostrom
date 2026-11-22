---
title: bostrom
tags: cyber, bostrom, bootloader
alias: enhanced blockchain
icon: "🟢"
---
# bostrom

The network repository of bostrom, the network of BOOT: its genesis and its configuration, the input [cybernode](https://github.com/cyberia-to/cybernode) takes to run it. Beside them stand the network's site, the burial of the chain it is reborn from, and its documents.

bostrom is the bootloader of [[cyber]]: the proving ground where every part of a planetary [[superintelligence]] runs before it enters the protocol. Its first life was a cosmos chain that began on 2021-11-05 and was halted at height 25,120,712 on 2026-08-05. In almost five years its neurons taught it 3.1 million [[particles]] with 2.9 million [[cyberlinks]], under 47,837 moon passports. Its state was buried with every byte pinned. This repository is where it comes back: the same balances and the same cyberlinks, on [soft3](https://github.com/cyberia-to/soft3), secured by proof of work.

## what is here

| path | what it is |
|---|---|
| [network.toml](network.toml) | the network's identity and rules: name, coin, the clock of work, block limits, finality, emission, the epoch, the reward parameters, ports |
| [genesis/](genesis/) | how block 0 is made: the pinned sources, the rules of distribution, the starting graph, and the lock with the digests of the result |
| [endpoints.toml](endpoints.toml) | where the network is met: the site, the peers |
| [site/](site/) | [bostrom.network](https://bostrom.network): the deck, static, no build |
| [snapshot/](snapshot/) | the burial of the old chain: the manifest of pins, the tools that extracted it, the balance checker |
| [audit/](audit/) | receipts: what was measured, with its date |
| [docs/](docs/) | the history, the economy of BOOT, how to run a node, the research papers |

The layout is the standard of a network repository, cybernode [`specs/network.md`](https://github.com/cyberia-to/cybernode/blob/main/specs/network.md). The twin is [space-pussy](https://github.com/cyberia-to/space-pussy), the network of PUSSY.

## the network in numbers

| | |
|---|---|
| the coin | boot |
| the supply at genesis | 482,287,925,778,234 micro-units, the bank supply of the old chain at its halt |
| new coins | 1 % of the genesis supply a year, 4,587,974 micro-units a block |
| a block | 30 seconds |
| an epoch | 240 blocks, about two hours: focus is recomputed and stakes are settled |
| a stake | locked seven days |
| final | 120 blocks deep |
| the graph at genesis | 2,997,569 links: 2,949,732 of the old chain and 47,837 passports |
| balances at genesis | 93,472 |

Every number is in [network.toml](network.toml) or [genesis/genesis.lock](genesis/genesis.lock), with where it comes from.

## where it stands

The network is not launched. The launch being prepared is the one of pussy, the canary; bostrom follows by readiness and has no date. What the launch waits for is on [the launch's page](https://github.com/cyberia-to/cyberia/blob/main/projects/pussy.md).

Three things in this repository are ahead of the node, and say so themselves. The node still carries the values of `network.toml` as constants of its binary and the rules of `genesis/` as code: the files state them for this network, and the day cybernode reads a network from its repository they become its input ([networks as repositories](https://github.com/cyberia-to/soft3/blob/release/phase1/projects/network-repos.md)). The reward parameters are the node's today, while the reward law is being completed ([complete rewards](https://github.com/cyberia-to/soft3/blob/release/phase1/projects/complete-rewards.md)). And the kernel's own policy of emission is a proposal: [the economy of BOOT](docs/economics.md) keeps the running and the proposed apart.

## build the genesis and check it

```sh
cybernode genesis build --chain bostrom --snapshot snapshot --out bostrom.genesis
cybernode genesis verify bostrom.genesis --root
```

The build fetches every file the manifest pins, verifies each by sha256 and size, and writes the genesis file with a report beside it. The particle, the block-0 id and the state root it prints are the ones in [genesis/genesis.lock](genesis/genesis.lock). The file is 330,841,520 bytes; two runs of the pipeline, on 2026-10-16 and on 2026-10-17, gave the same bytes, and the second took 73 seconds and 7.9 GB of memory — the receipt is [audit/genesis-build-2026-10-17.md](audit/genesis-build-2026-10-17.md).

## run a node

```sh
cybernode node --chain bostrom --genesis bostrom.genesis --home ~/.bostrom --moniker my-node
```

More in [run a node](docs/run-a-node.md).

## how it works

- [truth, from claim to payout](https://cyberia.blog/soft3/tru/docs/explanation/truth/): what a stake on a link claims, who pays whom, with a calculator
- the chain: [cybernode specs](https://github.com/cyberia-to/cybernode/tree/main/specs)
- the reward law: [tru specs/rewards.md](https://github.com/cyberia-to/tru/blob/master/specs/rewards.md)

## the old chain

The pages this repository carried about the cosmos chain — its modules, validators, guides and improvement proposals — left the default branch on 2026-11-22 and are kept whole on the branch [`legacy/graph-pages`](https://github.com/cyberia-to/bostrom/tree/legacy/graph-pages). What the chain was, on one page: [history](docs/history.md).
