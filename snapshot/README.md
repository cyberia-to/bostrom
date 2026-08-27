---
title: bostrom final snapshot
tags: cyber, bootloader
crystal-type: source
crystal-domain: cyber
---
# bostrom final snapshot

the bootloader chain halted at height 25,120,712 (2026-08-05 08:55 UTC) and is laid to rest. this directory holds the extraction scripts, the manifest, and the dashboard at [snapshot.bostrom.network](https://snapshot.bostrom.network).

every dataset is content-addressed on IPFS — pinned to Pinata **and** the cybernode for redundancy — so the record outlives every server. links are `<CID>/<filename>` on any gateway.

## datasets (see manifest.json for CIDs + sha256)

| file | contents |
|------|----------|
| state_export.json.gz | full chain state at halt (all modules) |
| cyberlinks_indexed.csv.gz | cyberlink graph: from, to, neuron, height, time, tx |
| balances.csv | every holder of BOOT, H, A, V, TOCYB, PUSSY, LP |
| passports.jsonl | all 47,837 moon passports: nickname, owner, resolver |
| pools.json | 30 liquidity pools: reserves + prices at halt |
| delegations.csv, validators.json | staking |
| pubkeys.csv | 61,675 account public keys (future claims) |
| supply.json | total supply per denom |

## reproduce

next to a bostrom archive node with LCD on :1317:

```bash
python3 extract.py supply && python3 extract.py pools && python3 extract.py balances
python3 extract.py staking && python3 extract.py pubkeys
PASSPORT=bostrom1xut80d09q0tgtch8p0z4k5f88d3uvt8cvtzm5h3tu3tsy4jk9xlsfzhxel python3 extract.py passport
python3 extract.py manifest
```

the full state comes from `cyber export` on the stopped node.

## app

`app/index.html` — the dashboard + balance checker (connect Ledger, enter a mnemonic or private key, or paste a bostrom address; balances read from the snapshot, keys never leave the browser). pure static, works from any IPFS gateway.
