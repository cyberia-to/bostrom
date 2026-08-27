#!/usr/bin/env python3
# bostrom final snapshot extractor — run next to an archive node (LCD :1317).
# Every dataset is a separate file in an open format; see README.md.
import json, csv, sys, os, urllib.request, base64, hashlib, time

LCD = os.environ.get("LCD", "http://localhost:1317")
OUT = os.environ.get("OUT", "./out")
CORE = ["boot", "hydrogen", "milliampere", "millivolt", "tocyb"]

def get(path):
    for attempt in range(5):
        try:
            with urllib.request.urlopen(LCD + path, timeout=60) as r:
                return json.load(r)
        except Exception as e:
            if attempt == 4: raise
            time.sleep(2 * (attempt + 1))

def paged(path, key, limit=1000, extra=""):
    next_key = None
    while True:
        q = f"?pagination.limit={limit}{extra}"
        if next_key: q += "&pagination.key=" + urllib.parse.quote(next_key)
        d = get(path + q)
        for item in d.get(key, []): yield item
        next_key = (d.get("pagination") or {}).get("next_key")
        if not next_key: break

import urllib.parse

def denoms_of_interest():
    ds = list(CORE)
    for s in paged("/cosmos/bank/v1beta1/supply", "supply"):
        d = s["denom"]
        if d.startswith("ibc/") or "/li" in d or d.startswith("pool"):
            ds.append(d)
    return ds

def cmd_balances():
    os.makedirs(OUT, exist_ok=True)
    w = csv.writer(open(f"{OUT}/balances.csv", "w"))
    w.writerow(["address", "denom", "amount"])
    n = 0
    for denom in denoms_of_interest():
        enc = urllib.parse.quote(denom, safe="")
        for o in paged(f"/cosmos/bank/v1beta1/denom_owners/{enc}", "denom_owners"):
            w.writerow([o["address"], denom, o["balance"]["amount"]]); n += 1
        print(f"  {denom}: done ({n} rows total)", flush=True)
    # denom traces so ibc/... hashes are self-describing
    traces = list(paged("/ibc/apps/transfer/v1/denom_traces", "denom_traces"))
    json.dump(traces, open(f"{OUT}/denom_traces.json", "w"), indent=1)
    print("balances.csv + denom_traces.json done")

def cmd_supply():
    os.makedirs(OUT, exist_ok=True)
    sup = list(paged("/cosmos/bank/v1beta1/supply", "supply"))
    json.dump(sup, open(f"{OUT}/supply.json", "w"), indent=1)
    print("supply.json done")

def cmd_pools():
    os.makedirs(OUT, exist_ok=True)
    pools = []
    for p in paged("/cosmos/liquidity/v1beta1/pools", "pools"):
        acc = p["reserve_account_address"]
        bal = get(f"/cosmos/bank/v1beta1/balances/{acc}")["balances"]
        reserves = {b["denom"]: b["amount"] for b in bal}
        a, b = p["reserve_coin_denoms"][0], p["reserve_coin_denoms"][1]
        ra, rb = int(reserves.get(a, 0)), int(reserves.get(b, 0))
        price_ab = (rb / ra) if ra else None
        pools.append({"id": p["id"], "type": "native-liquidity",
                      "denoms": [a, b], "reserves": reserves,
                      "pool_coin_denom": p["pool_coin_denom"],
                      "price": {f"{a}_in_{b}": price_ab}})
    json.dump(pools, open(f"{OUT}/pools.json", "w"), indent=1)
    print(f"pools.json done ({len(pools)} pools)")

def smart(addr, q):
    enc = base64.b64encode(json.dumps(q).encode()).decode()
    return get(f"/cosmwasm/wasm/v1/contract/{addr}/smart/{urllib.parse.quote(enc)}")["data"]

def cmd_passport():
    addr = os.environ["PASSPORT"]
    os.makedirs(OUT, exist_ok=True)
    total = smart(addr, {"num_tokens": {}})["count"]
    print("passports:", total, flush=True)
    out = open(f"{OUT}/passports.jsonl", "w")
    start_after, n = None, 0
    while True:
        q = {"all_tokens": {"limit": 100}}
        if start_after: q["all_tokens"]["start_after"] = start_after
        toks = smart(addr, q)["tokens"]
        if not toks: break
        for t in toks:
            info = smart(addr, {"all_nft_info": {"token_id": t}})
            rec = {"nickname": t,
                   "owner": info["access"]["owner"],
                   "extension": info["info"].get("extension"),
                   "token_uri": info["info"].get("token_uri")}
            out.write(json.dumps(rec, ensure_ascii=False) + "\n"); n += 1
        start_after = toks[-1]
        if n % 2000 == 0: print(f"  {n}/{total}", flush=True)
    print(f"passports.jsonl done ({n})")

def cmd_staking():
    os.makedirs(OUT, exist_ok=True)
    w = csv.writer(open(f"{OUT}/delegations.csv", "w"))
    w.writerow(["delegator", "validator", "shares", "balance_boot"])
    vals = list(paged("/cosmos/staking/v1beta1/validators", "validators", extra="&status="))
    json.dump(vals, open(f"{OUT}/validators.json", "w"), indent=1)
    for v in vals:
        va = v["operator_address"]
        for d in paged(f"/cosmos/staking/v1beta1/validators/{va}/delegations", "delegation_responses"):
            w.writerow([d["delegation"]["delegator_address"], va,
                        d["delegation"]["shares"], d["balance"]["amount"]])
        print("  " + v["description"]["moniker"], flush=True)
    print("delegations.csv + validators.json done")

def cmd_pubkeys():
    os.makedirs(OUT, exist_ok=True)
    w = csv.writer(open(f"{OUT}/pubkeys.csv", "w"))
    w.writerow(["address", "pubkey_type", "pubkey_base64"])
    n = 0
    for a in paged("/cosmos/auth/v1beta1/accounts", "accounts", limit=500):
        base = a.get("base_account") or a.get("base_vesting_account", {}).get("base_account") or a
        pk = base.get("pub_key") or {}
        w.writerow([base.get("address", ""), pk.get("@type", ""), pk.get("key", "")]); n += 1
        if n % 20000 == 0: print(f"  {n} accounts", flush=True)
    print(f"pubkeys.csv done ({n})")

def cmd_manifest():
    files = sorted(f for f in os.listdir(OUT) if os.path.isfile(f"{OUT}/{f}") and f != "manifest.json")
    man = {"chain_id": "bostrom", "final_height": 25120712,
           "final_block_time": "2026-08-05T08:55:00Z",
           "method": "https://github.com/cyberia-to/bootloader/tree/main/snapshot",
           "files": {}}
    for f in files:
        h = hashlib.sha256(open(f"{OUT}/{f}", "rb").read()).hexdigest()
        man["files"][f] = {"sha256": h, "bytes": os.path.getsize(f"{OUT}/{f}")}
    json.dump(man, open(f"{OUT}/manifest.json", "w"), indent=1)
    print(json.dumps(man, indent=1))

if __name__ == "__main__":
    {"balances": cmd_balances, "supply": cmd_supply, "pools": cmd_pools,
     "passport": cmd_passport, "staking": cmd_staking, "pubkeys": cmd_pubkeys,
     "manifest": cmd_manifest}[sys.argv[1]]()
