---
title: the economy of BOOT
tags: cyber, bostrom, cybernomics
alias: BOOT economics, the planned economy of BOOT
crystal-type: article
crystal-domain: economics
---

# the economy of BOOT

What BOOT is for, what the node pays today, what is proposed and what is still open. The three are kept apart: a figure moves from proposed to running only when the node carries it.

## the job

BOOT is the coin of bostrom, the bootloader: a small, clean graph that devices and other collective intelligences start from. It is one of three coins with three jobs ([tokens](https://cyber.page/tokens/)):

| | CYB | BOOT | PUSSY |
|---|---|---|---|
| network | cyber | bostrom | pussy |
| job | root money | bootloader | community |
| purpose | hard money | small kernel | fast growth |

One policy cannot hold three opposite needs. The money of cyber must be as hard as arithmetic. The kernel must fit in a device, stay clean, and dilute a founder's majority by work. The community must grow faster than it decays.

## running: what the node carries today

These are the values of [`network.toml`](../network.toml), the same for both networks.

| | |
|---|---|
| the supply at genesis | 482,287,925,778,234 micro-units, the bank supply of the old chain at its halt |
| new coins | 1 % of the genesis supply a year: 4,587,974 micro-units a block, constant |
| who receives them | the miner of a block, and the focus pool, which takes at most half |
| a stake | a position on a cyberlink, locked seven days |
| an epoch | 240 blocks: focus is recomputed, positions are settled |
| a position's reward | at most 1 % of the stake it added, in an epoch |
| surprise and karma | constants at launch |

The old resource tokens are carried as balances and have no function in the new network.

## proposed: the kernel's own policy

Proposed on 2026-09-27 and open until the genesis fixes it. None of it is in the node.

| | proposed for BOOT | for comparison, PUSSY |
|---|---|---|
| the supply | up once | up for years |
| emission | three times the base in the first year, half of it in the first quarter, then nothing | nine times the base in the first year, then halving to a floor of 3 % a year |
| who receives | work | work and serving |
| writing a link | a burn that grows with how full the graph is | a lock |
| a link lives | forever | until unlocked |
| capacity | 2²² links | no limit |
| a neuron's weight | capped at 5 % of the effective stake | the square root of its stake |
| the founder's majority | an endowment, burned over ten years against an equal mint to work | — |
| dormant balances | burned after a year | burned and minted again to the subsidy |
| the root fee | receives it in BOOT and burns it | pays it |
| registering a book | 10 % of the book's own premint | 2 % |
| parameters | fixed | by vote |

Why these: emission goes only to work, so a passive stake earns rank and never income, and the founder's share — which the proposal puts at about 60 %, its own figure, read from [tokens](https://cyber.page/tokens/) note 4 — shrinks without a balance being touched. The cap on weight means that owning 60 % never weighs 60 %. The burn for space keeps the graph small enough to boot a device. The root fee is the one bond between the two networks: a child network pays the kernel in BOOT for its name and its finality.

The source of the proposal, with its notes: [tokens](https://cyber.page/tokens/).

## open: what the launch decides

Two projects of the launch replace the constant subsidy and the constant surprise, and they come before the kernel's own policy.

- [the hybrid economy](https://github.com/cyberia-to/soft3/blob/release/phase1/projects/hybrid-economy-at-genesis.md): a budget that follows how much is staked, so that the reward for staking is high when little is staked and falls as the stake grows.
- [complete rewards](https://github.com/cyberia-to/soft3/blob/release/phase1/projects/complete-rewards.md): the surprise, karma and the losing side's payment, which close the loop from a stake to focus.

The law itself: [tru specs/rewards.md](https://github.com/cyberia-to/tru/blob/master/specs/rewards.md). How a stake on a link is settled, with a calculator: [truth, from claim to payout](https://cyberia.blog/soft3/tru/docs/explanation/truth/).

## the promise of CYB

TOCYB is carried into the genesis of bostrom unchanged: 281,405,532,467,645 micro-units at the halt. It is the claim on CYB. At the genesis of cyber every TOCYB becomes 666 CYB, about 1 % of the cap of cyber, which is the order of the Goldilocks field.

## before

The economy of the first chain, with its six tokens and the distribution of 2021, is in [history](history.md).
