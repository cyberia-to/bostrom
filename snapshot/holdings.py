#!/usr/bin/env python3
# Build the authoritative per-account holdings from the state export:
#   liquid (bank) + delegated (staking, boot) + undelegating + pool decomposition
# LP/pool-coin holdings are decomposed into the underlying reserve tokens.
import json, gzip, csv

S = json.load(gzip.open("/archive/snapshot/pub/state_export.json.gz"))["app_state"]

# 1. liquid balances (complete — all 79 denoms)
liquid = {}          # addr -> {denom: int}
for a in S["bank"]["balances"]:
    liquid[a["address"]] = {c["denom"]: int(c["amount"]) for c in a["coins"]}

# 2. pools: pool_coin_denom -> (reserves, total_supply) for LP decomposition
supply = {c["denom"]: int(c["amount"]) for c in S["bank"]["supply"]}
pools = {}
for pr in S["liquidity"]["pool_records"]:
    pool = pr["pool"]
    pc = pool["pool_coin_denom"]
    racc = pool["reserve_account_address"]
    reserves = {c["denom"]: int(c["amount"]) for c in S["bank"]["balances"] and liquid.get(racc, {}).items() and [type("X",(object,),{})] or []} if False else dict(liquid.get(racc, {}))
    reserves = {d: reserves.get(d, 0) for d in pool["reserve_coin_denoms"]}
    tot = int(pr["pool_metadata"]["pool_coin_total_supply"]["amount"])
    pools[pc] = {"reserves": reserves, "supply": tot}

# 3. delegated boot per delegator (shares -> tokens via validator ratio)
vtok, vshares = {}, {}
for v in S["staking"]["validators"]:
    vtok[v["operator_address"]] = int(v["tokens"])
    vshares[v["operator_address"]] = float(v["delegator_shares"])
delegated = {}       # addr -> boot
for d in S["staking"]["delegations"]:
    va = d["validator_address"]; sh = float(d["shares"])
    if vshares.get(va):
        boot = int(sh * vtok[va] / vshares[va])
        delegated[d["delegator_address"]] = delegated.get(d["delegator_address"], 0) + boot
# unbonding (none at halt, but handle generally)
undel = {}
for u in S["staking"]["unbonding_delegations"]:
    tot = sum(int(e["balance"]) for e in u["entries"])
    undel[u["delegator_address"]] = undel.get(u["delegator_address"], 0) + tot

# 4. compose holdings: per token, per source. pools decompose into reserve tokens.
CORE = ["boot","hydrogen","milliampere","millivolt","tocyb"]
def denom_label(d):
    return {"boot":"BOOT","hydrogen":"H","milliampere":"A","millivolt":"V","tocyb":"TOCYB"}.get(
        d, "PUSSY" if d.startswith("ibc/") else d)

addrs = set(liquid) | set(delegated) | set(undel)
out = open("/archive/snapshot/pub/holdings.jsonl", "w")
n = 0
for addr in addrs:
    lq = liquid.get(addr, {})
    tokens = {}   # denom -> {liquid, delegated, undelegating, pools}
    def bucket(denom):
        return tokens.setdefault(denom, {"liquid":0,"delegated":0,"undelegating":0,"pools":0})
    # liquid (skip pool/factory LP — those decompose)
    for d, amt in lq.items():
        if d in pools:  # a pool coin held liquid -> decompose
            p = pools[d]
            if p["supply"]:
                for rd, rv in p["reserves"].items():
                    bucket(rd)["pools"] += amt * rv // p["supply"]
        else:
            bucket(d)["liquid"] += amt
    # delegated / undelegating (boot)
    if delegated.get(addr): bucket("boot")["delegated"] += delegated[addr]
    if undel.get(addr):     bucket("boot")["undelegating"] += undel[addr]
    # emit only non-empty
    rec = {}
    for d, b in tokens.items():
        tot = b["liquid"]+b["delegated"]+b["undelegating"]+b["pools"]
        if tot>0:
            rec[d] = {"label":denom_label(d), **b, "total":tot}
    if rec:
        out.write(json.dumps({"address":addr, "holdings":rec}, separators=(",",":"))+"\n"); n+=1
out.close()
print("holdings.jsonl:", n, "accounts")

# also rewrite the flat complete balances.csv from bank (all denoms)
w = csv.writer(open("/archive/snapshot/pub/balances.csv","w"))
w.writerow(["address","denom","amount"])
for addr, coins in liquid.items():
    for d, amt in coins.items():
        w.writerow([addr, d, amt])
print("balances.csv rewritten (complete)")
