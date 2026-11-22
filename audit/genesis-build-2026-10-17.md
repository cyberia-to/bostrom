---
title: genesis build 2026-10-17 — the receipt the lock is blessed from
tags: cyber, bostrom, audit, genesis
crystal-type: audit
crystal-domain: cyber
---

# genesis build 2026-10-17 — the receipt the lock is blessed from

The receipt `AGENTS.md` asks for beside `genesis/genesis.lock`: which runs of
the pipeline produced the bytes the lock pins, and under what the root was
taken. Every value below is read from the run reports in cybernode
`audit/chain/hemera-0.4-2026-10-16.md` § 3 and
`audit/chain/economy-2026-10-17.md` § genesis under dimension version 4, and
from soft3 `conformance/chain-genesis.toml` `[bostrom]` on `release/phase1`,
the blessed scalars the lock was copied from.

## the two runs

Same input both times: the burial of `snapshot/manifest.json`, sha256
`9def76d42ef90b80c1feccb362817e4bd9a5917772369ca6acfd7c0fd96e29a5`, every
file fetched by its pin and verified by sha256 and size; same genesis time
1793884962; pipeline `cybernode genesis build` — `soft3 genesis build` in the
reports, written before the node moved to cybernode — against hemera
`7237a23` (cyber-hemera 0.4.0, profile #15, `release/0.4`).

| | 2026-10-16 | 2026-10-17 |
|---|---|---|
| bbg | `eb152fa`, dimension version 3 | `be5c5db` (bbg#51), dimension version 4 |
| particle (the chain id) | `f78c60ed…b425` | `f78c60ed…b425` |
| file | 330,841,520 B, sha256 `ffa3d6dd…6443` | 330,841,520 B, sha256 `ffa3d6dd…6443` |
| state root | `c50a6d8438ed8b0ef72450e7f83cab81e78bfd4e833106add9d62a0831bcdf13` | `fa0c2c9404a6eff04737ed7dfe11c63c1992b4820fdf039a55c6d2f103d7508d` |
| block-0 id | `9ab9fc49967caa7c5324f877512254969fcb56fada55b57cf0ba0b2187d3aa67` | `a13f0f627dae47a00fe50f7f9c538148345f52ab6200518e2360798c504fc3d5` |
| S0 / subsidy | 482,287,925,778,234 / 4,587,974 | 482,287,925,778,234 / 4,587,974 |
| frames | b 93,472, l 2,997,569 | b 93,472, l 2,997,569 |
| cost | 327 s wall, 110.5 s user, 5.9 GB max RSS | 73 s wall, 91 s user, 7.9 GB max RSS |

The second run rebuilt the file into `/tmp` and it came out **byte-identical**
to the first: the chain id, the sha256 and the 330,841,520 bytes of
`genesis/genesis.lock` are the result of two runs of the pipeline a day apart.
Both ran on the owner's desk from the same pinned inputs, so what they show
is that the pipeline is deterministic over its inputs, not that two
implementations agree.

The state root and the block-0 id are not a property of the file: they are
bbg's commitment over the state the file loads into, and bbg's dimension
version moved from 3 to 4 between the runs (bbg#51 added `CardRecord`
`author`, `valence`, `since`). So the lock takes those two from the
2026-10-17 run alone, and `[built_with] state = "bbg dimension version 4"`
is the pin that makes them reproducible. A later dimension version moves
them again without moving the chain id.

## why the 2026-10-15 replay reads differently

`audit/genesis-replay.md` § 2026-10-15 § bostrom records particle
`50d829b8…75db`, 330,841,445 bytes and `state root: not yet` from the same
manifest. That is an earlier genesis file, not a disagreement about this one:

- it was built before the pool record of cybernode `specs/chain.md` §11.9 and
  against hemera 0.3. The pool record adds the 75 bytes
  (330,841,445 → 330,841,520) and moves the particle to `d984145f…`; hemera
  0.4 moves it again to the `f78c60ed…` of the lock (soft3
  `audit/genesis-dimension-v3-2026-10-16.md`, cybernode
  `audit/chain/hemera-0.4-2026-10-16.md` § 3);
- its root was blocked, not wrong: four bbg dimensions exceeded lens
  Brakedown's 2²⁰ field-element cap, and the report recorded `root_blocked`.
  The cap is gone on lens `release/0.2` (`conformance/chain-genesis.toml`,
  the `lens` line), which is why the root commits in the runs above.

What did not move across any of the three runs: the source manifest, the
genesis supply 482,287,925,778,234, the subsidy 4,587,974, the 93,472 balance
frames and the 2,997,569 link frames.

## not here

The genesis file itself is never committed (`AGENTS.md` § rules); it is built
from the pinned snapshot and checked against this lock with
`cybernode genesis verify FILE --root`. The full run reports stay in
cybernode `audit/chain/`; this page is the receipt that the lock in this
repository is blessed from them.
