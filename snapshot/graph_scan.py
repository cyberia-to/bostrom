import json, urllib.request, time

WINDOW = 20


def height_ranges(lo, hi, window=WINDOW):
    """Tile [lo, hi] into descending, non-overlapping, gap-free chunks of at
    most `window` heights each, as (min_height, max_height) pairs from hi
    down to lo. The scan and rebuild scripts read the chain in reverse, so
    a resumed run can trust everything below the last-seen height is done."""
    h = hi
    while h >= lo:
        mn = max(lo, h - window + 1)
        yield (mn, h)
        h = mn - 1


def main():
    out = open("/tmp/all_txblocks.txt", "w")
    lo, hi = 1, 25120712
    t0 = time.time(); found = 0
    for mn, h in height_ranges(lo, hi):
        url = f"http://localhost:26657/blockchain?minHeight={mn}&maxHeight={h}"
        d = None
        for attempt in range(4):
            try:
                d = json.load(urllib.request.urlopen(url, timeout=25)); break
            except Exception:
                time.sleep(1)
        if d is None:
            print("FAIL", mn, h, flush=True)
            continue
        for bm in d["result"]["block_metas"]:
            if int(bm["num_txs"]) > 0:
                out.write(bm["header"]["height"] + "\n"); found += 1
        if (hi - mn + 1) % 1000000 < WINDOW:
            print(f"{hi-mn+1} scanned, {found} tx-blocks, {time.time()-t0:.0f}s", flush=True)
    out.close()
    print("DONE", found, flush=True)


if __name__ == "__main__":
    main()
