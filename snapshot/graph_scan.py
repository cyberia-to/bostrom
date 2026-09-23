import json, urllib.request, time

def find_tx_heights(block_metas):
    return [bm["header"]["height"] for bm in block_metas if int(bm["num_txs"]) > 0]

def next_max_height(mn):
    return mn - 1

def window_min(lo, h, window=19):
    return max(lo, h - window)

def main():
    out = open("/tmp/all_txblocks.txt", "w")
    lo, hi = 1, 25120712
    t0 = time.time(); found = 0
    h = hi
    while h >= lo:
        mn = window_min(lo, h)
        url = f"http://localhost:26657/blockchain?minHeight={mn}&maxHeight={h}"
        for attempt in range(4):
            try:
                d = json.load(urllib.request.urlopen(url, timeout=25)); break
            except Exception: time.sleep(1)
        else:
            print("FAIL", mn, h, flush=True); h = next_max_height(mn); continue
        for height in find_tx_heights(d["result"]["block_metas"]):
            out.write(height + "\n"); found += 1
        h = next_max_height(mn)
        if (hi - h) % 1000000 < 20:
            print(f"{hi-h} scanned, {found} tx-blocks, {time.time()-t0:.0f}s", flush=True)
    out.close()
    print("DONE", found, flush=True)

if __name__ == "__main__":
    main()
