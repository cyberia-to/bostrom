# bostrom.network — the bootloader, reborn

the deck of bostrom in the house style (cyber.page · cyb.ai · cyb.money): seven chapters, each a page —
`/` · `/rebirth` · `/balance` · `/story` · `/bootloader` (`/tokens` still resolves) · `/graph` · `/next` (and `/<chapter>/<n>` for a slide inside).
flat navigation: every arrow, key, wheel and swipe on either axis moves one state. no calendar years on the page: the countdown carries the date.

- `index.html` · `deck.js` · `bostrom.css` — the deck; `style.css` is the house stylesheet (copy of `cyb/landing/style.css`)
- `graph.json` — 1,200 particles and 6,000 cyberlinks sampled from the real graph (copy of `cyber/landing/graph.json`), drawn behind every page
- the balance checker is the snapshot app's logic (`../snapshot/app/index.html`): name · address · mnemonic · private key · ledger, derived locally; data and `vendor.js` are read same-origin from the snapshot's files
- `music/missing-you-bostrom.mp3` — the old bostrom.network soundtrack (recovered from the legacy SPA's `public/audio/background-music.mp3`, commit 6067589); on by default, starts on the first gesture
- the countdown targets `2026-11-05T13:22:42Z`, five years to the second after block 1 (kept in code only)

## deploy

deimos (`cyber@195.201.105.229:8333`), `/archive/snapshot-new/pub/`, served as the apex bostrom.network; nginx maps the datasets and `vendor.js` onto
`/archive/snapshot/pub/` (the burial snapshot, still served as snapshot.bostrom.network), everything else is `try_files … /index.html`.
new.bostrom.network redirects here. config: `cybernode/servers/deimos/nginx/snapshot.bostrom.network`. the twin: `space-pussy/site` → spacepussy.ai.

```sh
rsync -az -e "ssh -p 8333" site/ cyber@195.201.105.229:/archive/snapshot-new/pub/
```

checks: `python3 ~/cyber/cyber/scripts/cdp.py https://bostrom.network/ --eval '…'` (no node).
