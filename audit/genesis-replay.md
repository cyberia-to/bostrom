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

### space-pussy

Manifest `space-pussy/snapshot/manifest.json` (sha256 `b46cb327ca87222c…`),
halt 19,940,993 · 2026-06-14T08:36:41Z. Files replayed:
`cyberlinks_indexed.csv.gz` QmQQ1Xz8edsEeGRwnvgA831Ve7bRjsqYfEESLSwGtEG2iX,
`balances.csv` QmPZJtShm1tQzzYc6aJMBFcV1YHoCxiKs5r29DVH5UF7Pc,
`pubkeys.csv` QmSHTTz46f87KYjY936SLwjdkExD1WN2QFKLnJ8bu6ANvz,
`delegations.csv` QmZFu4fvS7BDr6Ny4FvJz4VpyjwWvVV2LgP6uLXWCq3dgw,
`holdings.jsonl` QmcxDahwm8hSwZdp8gBWhnBZx8BRBXKyaNkdviiynaFeYi,
`passports.jsonl` QmTvMKGSjB44arkBNwc8qdBWCEScj1PHCg4c4y2nj8r8nx,
`supply.json` QmXPkBWZ6XkhQJxrFAfMVYnGDf4BL3Z67r1ceSPFCsaGhA.

| dataset | rows in source | genesis entries | match |
|---|---|---|---|
| cyberlinks | 29,112 (manifest: restored 29,112 of 48,370) | 29,112 | yes |
| accounts (`pubkeys.csv`) | 616 | 616 | yes |
| passports | 1 | 1 | yes |
| pussy supply | 1,099,389,810,279,114,036 | 1,099,389,810,279,114,036 | yes |
| particles | 16,271 distinct CIDs in restored links | 16,271 | yes |

Known gap: 19,258 early links are unrecoverable (pruned before indexing);
they are declared in the genesis manifest's `gaps`, not replayed.

genesis hash `8339b4ad98f973155269e63272bdc282e2dee62081f927caa64107a4073e78b6`
· **state root `f5b10b87d7eccffbba82c77fd30c14e62793ce11e0dd188bf481108672757093`**
· 5 s · deterministic across two builds · `soft3 genesis verify --root` clean.

### bostrom

Manifest `bostrom/snapshot/manifest.json` (sha256 `9def76d42ef90b80…`),
halt 25,120,712 · 2026-08-05T08:55:00Z. Files replayed:
`cyberlinks_indexed.csv.gz` QmUFrsLYUK8USpNMEGBbUyi3nTuq12QcLiVWiyVMMVyyFf,
`balances.csv` QmTsM6YazUmAkz7sNbL1NY88cMciZpiTWHZEDCo3gZVo1h,
`pubkeys.csv` QmXFT8ULxLqYV1jp388YFcXUCvJdCR8ptW2yJEQsNdp2sG,
`delegations.csv` QmRt9HWgGv5UFkZ4q2WYDoXtTj1T9td1DECdvXkbWXP1SY,
`holdings.jsonl` QmQkR5jkbXjqCUNB6uj4EWaCRd7oWS7zbkcTWX1ZWtkvqW,
`passports.jsonl` QmTSZ1DLV61ATVMRBmqVnebDjhVG52gLijwPQYzBxq3jQQ,
`supply.json` QmcyWzweYjtxM9cf1YFNh9c6Qg8yhe6yy4ghXC7wVasPaM.

| dataset | rows in source | genesis entries | match |
|---|---|---|---|
| cyberlinks | 2,949,732 (manifest: on-chain 2,949,732) | 2,949,732 | yes |
| particles | 3,143,650 (manifest: on-chain 3,143,650) | 3,143,650 | yes |
| accounts (`pubkeys.csv`) | 61,675 | 61,675 | yes |
| passports | 47,837 | 47,837 | yes |
| boot supply | 482,287,925,778,234 | 482,287,925,778,234 | yes |
| cyb (tocyb × 666) | 281,405,532,467,645 × 666 | 187,416,084,623,451,570 | yes (= audited `genesis_cyb`) |

genesis hash `da45937f32613a7ca894c45453a7f6fa9b695c1c98d2889b425fc07118cb47b0`
· **state root: not yet** — six bbg dimensions exceed lens Brakedown's 2^20
field-element cap (particles needs 2^27); the manifest records `root_blocked`.
Tables deterministic across two builds; 104 s, 5.2 GB. The per-batch recommit
of launch row 43 is not what blocks it (the pipeline bulk-loads and commits
once); the commitment size cap is. Detail in `soft3/audit/genesis-2026-10-15.md`.

Steps 1–2 of the replay contract run clean on both chains; step 3 (the root)
closes for space-pussy today and waits on bbg/lens for bostrom.
