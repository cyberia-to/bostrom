#!/usr/bin/env python3
# Structural and cross-field consistency checks over snapshot/manifest.json —
# no network, no live files; the manifest's own numbers must agree with
# themselves before genesis trusts them.
import json, re, sys

SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
CID_RE = re.compile(r"^Qm[1-9A-HJ-NP-Za-km-z]{44}$")  # CIDv0, base58btc


def check_file_entries(files):
    """Every file entry has a well-formed sha256, a well-formed CIDv0, and positive bytes."""
    problems = []
    for name, meta in files.items():
        sha = meta.get("sha256", "")
        if not SHA256_RE.match(sha):
            problems.append(f"{name}: sha256 is not 64 lowercase hex chars: {sha!r}")
        cid = meta.get("cid", "")
        if not CID_RE.match(cid):
            problems.append(f"{name}: cid is not a well-formed CIDv0: {cid!r}")
        if meta.get("bytes", 0) <= 0:
            problems.append(f"{name}: bytes is not positive: {meta.get('bytes')!r}")
    return problems


def check_particle_totals(manifest):
    """available + missing must equal the graph's restored particle count."""
    pa = manifest.get("particles_availability", {})
    graph = manifest.get("graph", {})
    available, missing = pa.get("available"), pa.get("missing")
    restored = graph.get("restored_particles")
    if available is None or missing is None or restored is None:
        return []
    total = available + missing
    if total != restored:
        return [
            f"particles_availability.available + missing = {total}, "
            f"graph.restored_particles = {restored} (off by {total - restored})"
        ]
    return []


def check_coverage_pct(manifest, tolerance=0.01):
    """coverage_pct must match available / (available + missing) within tolerance."""
    pa = manifest.get("particles_availability", {})
    available, missing, claimed = pa.get("available"), pa.get("missing"), pa.get("coverage_pct")
    if available is None or missing is None or claimed is None or (available + missing) == 0:
        return []
    computed = available / (available + missing) * 100
    if abs(computed - claimed) > tolerance:
        return [f"coverage_pct claims {claimed}, computed {computed:.4f}"]
    return []


def check_graph_bijection(manifest):
    """onchain and restored counts must match, for both links and particles."""
    graph = manifest.get("graph", {})
    problems = []
    for onchain_key, restored_key in [
        ("onchain_cyberlinks", "restored_cyberlinks"),
        ("onchain_particles", "restored_particles"),
    ]:
        a, b = graph.get(onchain_key), graph.get(restored_key)
        if a is not None and b is not None and a != b:
            problems.append(f"graph.{onchain_key} = {a} != graph.{restored_key} = {b}")
    return problems


def validate(manifest):
    problems = []
    problems += check_file_entries(manifest.get("files", {}))
    problems += check_particle_totals(manifest)
    problems += check_coverage_pct(manifest)
    problems += check_graph_bijection(manifest)
    return problems


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "manifest.json"
    with open(path) as f:
        manifest = json.load(f)
    problems = validate(manifest)
    if problems:
        print(f"{len(problems)} problem(s) found in {path}:")
        for p in problems:
            print(" -", p)
        sys.exit(1)
    print(f"{path}: all checks passed")


if __name__ == "__main__":
    main()
