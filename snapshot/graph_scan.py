import json, urllib.request, time
OUT = open("/tmp/all_txblocks.txt", "w")
lo, hi = 1, 25120712
t0 = time.time(); found = 0
h = hi
while h >= lo:
    mn = max(lo, h - 19)
    url = f"http://localhost:26657/blockchain?minHeight={mn}&maxHeight={h}"
    for attempt in range(4):
        try:
            d = json.load(urllib.request.urlopen(url, timeout=25)); break
        except Exception: time.sleep(1)
    else:
        print("FAIL", mn, h, flush=True); h = mn - 1; continue
    for bm in d["result"]["block_metas"]:
        if int(bm["num_txs"]) > 0:
            OUT.write(bm["header"]["height"] + "\n"); found += 1
    h = mn - 1
    if (hi - h) % 1000000 < 20:
        print(f"{hi-h} scanned, {found} tx-blocks, {time.time()-t0:.0f}s", flush=True)
OUT.close()
print("DONE", found, flush=True)
