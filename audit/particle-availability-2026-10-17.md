---
title: particle availability — the manifest's two-particle gap and a joined line in the missing list
tags: cyber, bostrom, audit, genesis
crystal-type: audit
crystal-domain: cyber
---

# particle availability — the manifest's two-particle gap and a joined line in the missing list

date: 2026-10-17 · repository revision: origin/main `798cfec` · artifacts:
the published burial files as pinned in `snapshot/manifest.json`, read from a
local copy (`$SNAP` below) whose sha256 match the manifest:

| file | sha256 |
|---|---|
| `cyberlinks_indexed.csv.gz` | `e442ff7a0e905591f1bda94dcac89fd350c28824ccc71b56992da1ae0555e4ae` |
| `missing_particles.txt.gz` | `38301c24cb838985e49a31a8f1d733e6420dcc429c52c499993d7f39813b91f8` |
| `particles_availability.json` | `bbc07355562a26a45c19872d6c1f6eae4ea3bb32d137dd74a211d6cdaa86a219` |

First raised on 2026-09-23 by the launch row 14 slice (4) (bostrom#15), which
found that `snapshot/validate_manifest.py` reports one problem in the
manifest: `available + missing = 3,143,648` against
`graph.restored_particles = 3,143,650`. This record re-derives both numbers
from the artifacts.

## finding 1 — the −2 is two non-CID particles the audit never checked

`python3 snapshot/validate_manifest.py snapshot/manifest.json` (exit 1):

    particles_availability.available + missing = 3143648, graph.restored_particles = 3143650 (off by -2)

`particles_availability.json` itself declares `unique_particles_in_graph:
3143650` and `checked: 3143648`; the manifest copied `available`, `missing`
and `coverage_pct` but not `checked`, so the sum does not close inside the
manifest alone. The two unchecked particles are the only particles of the
graph that are not CIDv0 (the audit method resolves CIDv0 → multihash →
flatfs path, so it cannot check anything else):

| cyberlink | neuron | height | tx |
|---|---|---|---|
| `Q` → `m` | `bostrom1h29u0h2y98rkhdrwsx0ejk5eq8wvslygexr7p8` | 3,954,754 (2022-07-30 12:36:20) | `DC5E4301333E3AED4B0E08F5A1478B5B30AAFA5CA2867B3E7670119307A5DEBF` |

The link appears twice in `cyberlinks_indexed.csv.gz` (two identical rows,
same tx), which the on-chain counter also counts, so the graph totals
(2,949,732 links, 3,143,650 particles) stand. The gap is a reporting gap,
not a counting error.

Fix when the manifest is next republished: carry
`particles_availability.checked = 3143648`. `validate_manifest.py` compares
`available + missing` against `checked` when present, so the check goes
green on that change alone. The two non-CID particles need a genesis rule of
their own (row 20 re-addressing): they have no bytes and no CID, so their
identity is the hash of the literal string.

## finding 2 — `missing_particles.txt.gz` joins two CIDs on one line

The list has 74,513 lines for 74,514 missing particles. Line 23,591 is two
CIDv0 concatenated without a newline:

    QmfM3iSTKBVjPtdYWEfWfS9hQwNzSYeYjq3QSFsFkJErxM  (graph particle, linked at height 8,112,932)
    QmaWotG1HtSS5vMF2T9XqzqCBb47NLiHdPKCZdf6y4oQt1  (graph particle, linked at height 12,140,663)

Every other line is a 46-character CIDv0 present in the graph; the file
breaks sort order exactly at that line. Split correctly, the list holds
74,514 particles and `3,143,648 − 74,514 = 3,069,134 = available`, so the
manifest's `available` and `missing` are right and the file is what is
wrong. The dashboard caption in `snapshot/app/index.html` ("the 74,513
particle CIDs absent at audit time") follows the line count, not the
missing count.

Consequence: any consumer that reads the list line by line (the row 20
re-addressing run over the burial blockstore is one) sees a 92-character
token that matches no particle and silently treats both particles as
present. Fix: republish the list with the line split (new CID and sha256),
update its manifest entry and the dashboard caption. The artifact is pinned
and published, so the republish is the owner's call; until then, consumers
must split tokens of length 92 into two CIDv0.

## cross-checks that passed

- `extract.build_manifest($SNAP)` reproduces sha256 and bytes of all 14
  files in `snapshot/manifest.json`.
- The refactored `snapshot/holdings.py` (pure functions, launch row 14
  slice (3)) run over `$SNAP/state_export.json.gz` reproduces
  `holdings.jsonl` (57,371 records, set-equal; the script iterates a set, so
  line order is not fixed) and `prices.json` exactly.

## commands

    # distinct particles, non-CIDv0 particles, missing-list line shapes
    python3 - "$SNAP" <<'PY'
    import csv, gzip, re, sys
    d = sys.argv[1]; cid0 = re.compile(r"^Qm[1-9A-HJ-NP-Za-km-z]{44}$")
    ps = set()
    with gzip.open(f"{d}/cyberlinks_indexed.csv.gz", "rt", newline="") as f:
        r = csv.reader(f); next(r)
        for row in r: ps.update(row[:2])
    print(len(ps), sorted(p for p in ps if not cid0.match(p)))
    lines = gzip.open(f"{d}/missing_particles.txt.gz", "rb").read().split(b"\n")
    print(len(lines) - 1, [(i + 1, l) for i, l in enumerate(lines) if len(l) not in (0, 46)])
    PY
