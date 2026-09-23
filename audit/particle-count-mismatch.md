---
tags: bostrom, audit, launch
crystal-type: report
crystal-domain: cyber
---
# particle count mismatch in the burial manifest

date: 2026-09-23 · revision: bc01d7d (origin/main) · command: `python3 snapshot/validate_manifest.py snapshot/manifest.json`

`snapshot/manifest.json`, the canonical burial manifest published at
[snapshot.bostrom.network](https://snapshot.bostrom.network), carries two
particle totals that disagree by 2:

- `particles_availability.available` (3,069,134) + `particles_availability.missing`
  (74,514) = 3,143,648
- `graph.restored_particles` = 3,143,650

Both numbers are asserted elsewhere in the same file and in
[[cyber/launch]] (3,143,650 particles rebuilt bit-exact). `coverage_pct`
(97.63) rounds the same either way, so the discrepancy did not show up
as a visibly wrong percentage — it only shows up as a sum that does not
close.

`snapshot/validate_manifest.py` checks the manifest's own numbers
against each other (file-entry shape: sha256, CIDv0, positive byte
count; particle-total closure; coverage_pct arithmetic; onchain vs.
restored bijection for both particles and cyberlinks) and currently
reports exactly this one problem — the cyberlink counts (2,949,732 both
sides) and every file entry's sha256/cid/bytes are well-formed.

This is a two-particle discrepancy in metadata, not a data-loss claim:
`particles_availability.json` and `missing_particles.txt.gz` (the actual
audited sets) are not re-derived here, only the manifest's declared
totals. Row 14 — genesis is bijective with the snapshot — should not
treat `graph.restored_particles` and `particles_availability.available +
missing` as interchangeable until this closes; whoever re-runs the
particle availability audit should reconcile which of the two counts
(3,143,648 or 3,143,650) is the corrected one and fix the other.
