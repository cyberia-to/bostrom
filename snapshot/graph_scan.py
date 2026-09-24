import json, urllib.request, time

def window_min(h, lo):
    return max(lo, h - 19)

def tx_heights(block_metas):
    return [bm["header"]["height"] for bm in block_metas if int(bm["num_txs"]) > 0]

def fetch_window(min_h, max_h):
    url = f"http://localhost:26657/blockchain?minHeight={min_h}&maxHeight={max_h}"
    for _ in range(4):
        try: return json.load(urllib.request.urlopen(url, timeout=25))
        except Exception: time.sleep(1)
    return None

def main():
    OUT = open("/tmp/all_txblocks.txt", "w")
    lo, hi = 1, 25120712
    t0 = time.time(); found = 0
    h = hi
    while h >= lo:
        mn = window_min(h, lo)
        d = fetch_window(mn, h)
        if d is None:
            print("FAIL", mn, h, flush=True)
            h = mn - 1
            continue
        for height in tx_heights(d["result"]["block_metas"]):
            OUT.write(height + "\n"); found += 1
        h = mn - 1
        if (hi - h) % 1000000 < 20:
            print(f"{hi-h} scanned, {found} tx-blocks, {time.time()-t0:.0f}s", flush=True)
    OUT.close()
    print("DONE", found, flush=True)

if __name__ == "__main__":
    main()
