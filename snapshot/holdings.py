#!/usr/bin/env python3
# Authoritative per-account holdings from the state export:
#   liquid (bank) + delegated + undelegating + per-pool decomposition,
# plus prices.json: every denom's rate in boot from snapshot pool reserves.
import json, gzip, csv, hashlib

MIN_RESERVE = 1_000_000  # micro-units; dust pools do not quote

CORE_LABELS = {"boot": "BOOT", "hydrogen": "H", "milliampere": "A",
               "millivolt": "V", "tocyb": "TOCYB"}


def clean(base):
    m = {"pussy": "PUSSY", "boot": "BOOT", "hydrogen": "H", "milliampere": "A",
         "millivolt": "V", "tocyb": "TOCYB", "liquidpussy": "LP-PUSSY"}
    if base in m: return m[base]
    if base.startswith("u") and base[1:].isalpha(): return base[1:].upper()
    if base.startswith("gravity0x") or base.startswith("0x"): return "ERC20:" + base[-4:]
    return base[:10]


def build_ibc_map(denom_traces):
    ibc = {}
    for t in denom_traces:
        h = "ibc/" + hashlib.sha256((t["path"] + "/" + t["base_denom"]).encode()).hexdigest().upper()
        ibc[h] = t["base_denom"]
    return ibc


def denom_label(d, ibc):
    if d in CORE_LABELS: return CORE_LABELS[d]
    if d in ibc: return clean(ibc[d])
    if d.startswith("ibc/"): return "ibc:" + d[4:10]
    if d.startswith("factory"): return "LP"
    return d[:12]


def pool_rate(p, want, other, min_reserve=MIN_RESERVE):
    rw, ro = p["reserves"].get(want, 0), p["reserves"].get(other, 0)
    if rw < min_reserve or ro < min_reserve: return None
    return rw / ro


def compute_rates(pools, min_reserve=MIN_RESERVE):
    # direct boot pool wins; otherwise route through hydrogen.
    rates = {"boot": 1.0}
    h_rate = None
    for p in pools.values():
        if set(p["denoms"]) == {"boot", "hydrogen"}:
            h_rate = pool_rate(p, "boot", "hydrogen", min_reserve)
    rates["hydrogen"] = h_rate or 0.0
    for p in pools.values():
        ds = p["denoms"]
        if "boot" in ds:
            other = ds[0] if ds[1] == "boot" else ds[1]
            rates.setdefault(other, pool_rate(p, "boot", other, min_reserve) or 0.0)
    for p in pools.values():
        ds = p["denoms"]
        if "hydrogen" in ds and h_rate:
            other = ds[0] if ds[1] == "hydrogen" else ds[1]
            r = pool_rate(p, "hydrogen", other, min_reserve)
            if r is not None:
                rates.setdefault(other, r * h_rate)
    return rates


def compose_liquid(bank_balances):
    liquid = {}
    for a in bank_balances:
        liquid[a["address"]] = {c["denom"]: int(c["amount"]) for c in a["coins"]}
    return liquid


def compose_pools(pool_records, liquid):
    pools = {}
    for pr in pool_records:
        pool = pr["pool"]
        pc = pool["pool_coin_denom"]
        racc = pool["reserve_account_address"]
        reserves = {d: liquid.get(racc, {}).get(d, 0) for d in pool["reserve_coin_denoms"]}
        tot = int(pr["pool_metadata"]["pool_coin_total_supply"]["amount"])
        pools[pc] = {"id": pool["id"], "denoms": pool["reserve_coin_denoms"],
                     "reserves": reserves, "supply": tot}
    return pools


def compose_delegated_undelegating(validators, delegations, unbonding_delegations):
    vtok, vshares = {}, {}
    for v in validators:
        vtok[v["operator_address"]] = int(v["tokens"])
        vshares[v["operator_address"]] = float(v["delegator_shares"])
    delegated = {}
    for d in delegations:
        va = d["validator_address"]; sh = float(d["shares"])
        if vshares.get(va):
            boot = int(sh * vtok[va] / vshares[va])
            delegated[d["delegator_address"]] = delegated.get(d["delegator_address"], 0) + boot
    undel = {}
    for u in unbonding_delegations:
        tot = sum(int(e["balance"]) for e in u["entries"])
        undel[u["delegator_address"]] = undel.get(u["delegator_address"], 0) + tot
    return delegated, undel


def build_holdings_record(addr, liquid, delegated, undel, pools, ibc):
    lq = liquid.get(addr, {})
    tokens = {}
    def bucket(denom):
        return tokens.setdefault(denom, {"liquid": 0, "delegated": 0, "undelegating": 0, "pools": {}})
    for d, amt in lq.items():
        if d in pools:
            p = pools[d]
            if p["supply"]:
                for rd, rv in p["reserves"].items():
                    bp = bucket(rd)["pools"]
                    bp[p["id"]] = bp.get(p["id"], 0) + amt * rv // p["supply"]
        else:
            bucket(d)["liquid"] += amt
    if delegated.get(addr): bucket("boot")["delegated"] += delegated[addr]
    if undel.get(addr):     bucket("boot")["undelegating"] += undel[addr]
    rec = {}
    for d, b in tokens.items():
        tot = b["liquid"] + b["delegated"] + b["undelegating"] + sum(b["pools"].values())
        if tot > 0:
            rec[d] = {"label": denom_label(d, ibc), **b, "total": tot}
    return rec or None


def main():
    S = json.load(gzip.open("/archive/snapshot/pub/state_export.json.gz"))["app_state"]
    ibc = build_ibc_map(S.get("transfer", {}).get("denom_traces", []))
    liquid = compose_liquid(S["bank"]["balances"])
    pools = compose_pools(S["liquidity"]["pool_records"], liquid)
    delegated, undel = compose_delegated_undelegating(
        S["staking"]["validators"], S["staking"]["delegations"], S["staking"]["unbonding_delegations"])
    rates = compute_rates(pools)

    json.dump({
        "note": "1 micro-unit of denom valued in micro-boot, from snapshot pool reserves; hydrogen-routed when no direct boot pool",
        "pools": {p["id"]: {"denoms": p["denoms"], "labels": [denom_label(d, ibc) for d in p["denoms"]]}
                  for p in pools.values()},
        "rates": rates,
        "labels": {d: denom_label(d, ibc) for d in rates},
    }, open("/archive/snapshot/pub/prices.json", "w"), indent=1)
    print("prices.json:", len(rates), "rates,", len(pools), "pools")

    addrs = set(liquid) | set(delegated) | set(undel)
    out = open("/archive/snapshot/pub/holdings.jsonl", "w")
    n = 0
    for addr in addrs:
        rec = build_holdings_record(addr, liquid, delegated, undel, pools, ibc)
        if rec:
            out.write(json.dumps({"address": addr, "holdings": rec}, separators=(",", ":")) + "\n"); n += 1
    out.close()
    print("holdings.jsonl:", n, "accounts")

    w = csv.writer(open("/archive/snapshot/pub/balances.csv", "w"))
    w.writerow(["address", "denom", "amount"])
    for addr, coins in liquid.items():
        for d, amt in coins.items():
            w.writerow([addr, d, amt])
    print("balances.csv rewritten")


if __name__ == "__main__":
    main()
