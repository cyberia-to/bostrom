import json, urllib.request, time, csv, hashlib, base64, socket, os
socket.setdefaulttimeout(45)
from concurrent.futures import ThreadPoolExecutor

heights = sorted(int(l) for l in open("/tmp/all_txblocks.txt") if l.strip())
last = 0
try: last = int(open("/tmp/rebuild_progress.txt").read().strip())
except Exception: pass
heights = [h for h in heights if h > last]
new = (last == 0)
out = open("/tmp/cyberlinks_full.csv", "w" if new else "a", newline="")
w = csv.writer(out)
if new: w.writerow(["particle_from","particle_to","neuron","height","timestamp","transaction_hash"])
print("resuming after", last, "-", len(heights), "to go", flush=True)

def get(url):
    for _ in range(4):
        try: return json.load(urllib.request.urlopen(url, timeout=40))
        except Exception: time.sleep(1)
    return None

def work(h):
    rows = []
    br = get(f"http://localhost:26657/block_results?height={h}")
    if not br: return ("FAIL-BR", h, rows)
    txrs = br["result"].get("txs_results") or []
    if not any(ev["type"]=="cyberlink" for txr in txrs if not txr.get("code",0) for ev in txr.get("events",[])):
        return ("OK", h, rows)
    b = get(f"http://localhost:26657/block?height={h}")
    if not b: return ("FAIL-B", h, rows)
    ts = b["result"]["block"]["header"]["time"][:19].replace("T"," ")
    txs_b64 = b["result"]["block"]["data"]["txs"]
    for i, txr in enumerate(txrs):
        if txr.get("code",0): continue
        txh = hashlib.sha256(base64.b64decode(txs_b64[i])).hexdigest().upper() if i < len(txs_b64) else ""
        pending = []
        for ev in txr.get("events",[]):
            if ev["type"] != "cyberlink": continue
            attrs = {a["key"]: a["value"] for a in ev["attributes"]}
            if "particleFrom" in attrs:
                pending.append((attrs["particleFrom"], attrs["particleTo"]))
            elif "neuron" in attrs:
                for f,t in pending:
                    rows.append([f, t, attrs["neuron"], h, ts, txh])
                pending = []
        for f,t in pending:  # neuron event missing (should not happen)
            rows.append([f, t, "", h, ts, txh])
    return ("OK", h, rows)

t0=time.time(); total=0; done=0; fails=0
with ThreadPoolExecutor(max_workers=12) as ex:
    for status, h, rows in ex.map(work, heights):
        done += 1
        if status.startswith("FAIL"): fails+=1; print(status, h, flush=True)
        for r in rows: w.writerow(r)
        total += len(rows)
        if done % 2000 == 0:
            open("/tmp/rebuild_progress.txt","w").write(str(h)); out.flush()
        if done % 50000 == 0:
            print(f"{done}/{len(heights)} blocks, {total} links, {fails} fails, {time.time()-t0:.0f}s", flush=True)
out.close()
print("DONE", total, "links,", fails, "fails", flush=True)
