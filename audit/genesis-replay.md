---
title: genesis replay — counts and roots against the burial manifests
tags: cyber, bostrom, pussy, audit, genesis
crystal-type: audit
crystal-domain: cyber
---

# genesis replay — counts and roots against the burial manifests

The record `cybergraph/specs/genesis-replay.md` § verification step 3 asks
for: source counts, genesis counts and the resulting root, dated, against the
exact manifest CIDs replayed. Pipeline: `soft3 genesis build`
(`soft3/specs/genesis.md`); full run report `soft3/audit/genesis-2026-10-15.md`.

## 2026-10-15

Pipeline: `soft3 genesis build` producing the chain.md §4 genesis file (one
tade stream whose hemera particle is the chain id); full run report
`soft3/audit/genesis-2026-10-15.md`; blessed values `soft3/conformance/chain.snap`.

### space-pussy

Manifest `space-pussy/snapshot/manifest.json` (sha256 `b46cb327ca87222c…`),
halt 19,940,993 · 2026-06-14T08:36:41Z. Files replayed:
`cyberlinks_indexed.csv.gz` QmQQ1Xz8edsEeGRwnvgA831Ve7bRjsqYfEESLSwGtEG2iX,
`balances.csv` QmPZJtShm1tQzzYc6aJMBFcV1YHoCxiKs5r29DVH5UF7Pc,
`pubkeys.csv` QmSHTTz46f87KYjY936SLwjdkExD1WN2QFKLnJ8bu6ANvz,
`delegations.csv` QmZFu4fvS7BDr6Ny4FvJz4VpyjwWvVV2LgP6uLXWCq3dgw,
`holdings.jsonl` QmcxDahwm8hSwZdp8gBWhnBZx8BRBXKyaNkdviiynaFeYi,
`passports.jsonl` QmTvMKGSjB44arkBNwc8qdBWCEScj1PHCg4c4y2nj8r8nx,
`pools.json` Qmb5gLZEx12vC6W4PkRR5PwnCp38t2GmzLpHZuQ272qo91,
`supply.json` QmXPkBWZ6XkhQJxrFAfMVYnGDf4BL3Z67r1ceSPFCsaGhA.

| dataset | rows in source | genesis entries | match |
|---|---|---|---|
| cyberlinks | 29,112 (manifest: restored 29,112 of 48,370) | 29,112 `l` | yes |
| passports | 1 | 1 `l` (height 0) | yes |
| accounts (`pubkeys.csv`) | 616 | 616 owners | yes |
| pussy supply | 1,099,389,810,279,114,036 | 1,099,389,810,279,114,036 (S0) | yes |
| every other carried denom (22) | `supply.json` | Σ `b` per token | yes |
| particles | 16,271 distinct CIDs in restored links | 16,271 | yes |

Known gap: 19,258 early links are unrecoverable (pruned before indexing);
declared in the genesis report, not replayed.

**chain id (genesis particle) `2a83e54fe395ffbd924fc74a54a5c805eeec5396f97bf4c73fced8631a9e61b5`**
· **state root `f2296834490e79d855673b18b0f9eb5c8242e4f48761e85b645d60a8cbeb5827`**
· block-0 id `b863ce2877524e718bb51ea6dc7c5aba9540860f08d70162348d8e84b3eba304`
· S0 1,099,389,810,279,114,036 · SUBSIDY 10,458,426,657 · 1,385 `b` / 29,113 `l`
· 4 s · byte-identical across three builds · `soft3 genesis verify --root` clean.
Root against bbg `1d39975` (DIMENSION_VERSION 2, no `NeuronRecord.nonce`).

### bostrom

Manifest `bostrom/snapshot/manifest.json` (sha256 `9def76d42ef90b80…`),
halt 25,120,712 · 2026-08-05T08:55:00Z. Files replayed:
`cyberlinks_indexed.csv.gz` QmUFrsLYUK8USpNMEGBbUyi3nTuq12QcLiVWiyVMMVyyFf,
`balances.csv` QmTsM6YazUmAkz7sNbL1NY88cMciZpiTWHZEDCo3gZVo1h,
`pubkeys.csv` QmXFT8ULxLqYV1jp388YFcXUCvJdCR8ptW2yJEQsNdp2sG,
`delegations.csv` QmRt9HWgGv5UFkZ4q2WYDoXtTj1T9td1DECdvXkbWXP1SY,
`holdings.jsonl` QmQkR5jkbXjqCUNB6uj4EWaCRd7oWS7zbkcTWX1ZWtkvqW,
`passports.jsonl` QmTSZ1DLV61ATVMRBmqVnebDjhVG52gLijwPQYzBxq3jQQ,
`pools.json` QmbtuP9wdD6KzMxVWCb9R1Un8XAkBEnWwMeB2P9B3qLbUr,
`supply.json` QmcyWzweYjtxM9cf1YFNh9c6Qg8yhe6yy4ghXC7wVasPaM.

| dataset | rows in source | genesis entries | match |
|---|---|---|---|
| cyberlinks | 2,949,732 (manifest: on-chain 2,949,732) | 2,949,732 `l` | yes |
| passports | 47,837 | 47,837 `l` (height 0) | yes |
| particles | 3,143,650 (manifest: on-chain 3,143,650) | 3,143,650 | yes |
| accounts (`pubkeys.csv`) | 61,675 | 61,675 owners | yes |
| boot supply | 482,287,925,778,234 | 482,287,925,778,234 (S0) | yes |
| tocyb | 281,405,532,467,645 | 281,405,532,467,645 (carried unchanged) | yes |
| every other carried denom (47) | `supply.json` | Σ `b` per token | yes |
| excluded | 2 denoms (36 rows) above 2^64 − 1 | not carried, listed | by rule |

genesis particle `50d829b8d4a9237386645652336269b4e6755ffd53f6c4bdf32f2783f4dc75db`
(330,841,445 bytes) · S0 482,287,925,778,234 · SUBSIDY 4,587,974 · 93,472 `b`
/ 2,997,569 `l` · 122 s · **state root: not yet** — four bbg dimensions
exceed lens Brakedown's 2^20 field-element cap (particles needs 2^26); the
report records `root_blocked`. The per-batch recommit of launch row 43 is
not what blocks it (the pipeline bulk-loads and commits once); the
commitment size cap and two bbg inflations are. Detail in
`soft3/audit/genesis-2026-10-15.md`.

Steps 1–2 of the replay contract run clean on both chains; step 3 (the root)
closes for space-pussy today and waits on bbg/lens for bostrom.
