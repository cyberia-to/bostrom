/* bostrom.network — the bootloader, reborn · the deck
   seven chapters, each a page: / · /rebirth · /balance · /story · /bootloader · /graph · /next
   no date on the page: the launch is a milestone — code that passes its gate
   marks: ● measured · ○ target · ◌ mock. every number carries one. */
(() => {
const $ = (s, r = document) => r.querySelector(s);
const el = (h) => { const t = document.createElement('template'); t.innerHTML = h.trim(); return t.content.firstChild; };
const esc = (t) => String(t).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
const M = (k) => `<i class="mk ${k}"></i>`;
const COLS = ['#00ff41', '#00b8ff', '#ffc400', '#ff1a00', '#ff7a00', '#1e00ff', '#7a00ff'];

const sfx = (() => {
  let ac = null, master = null, on = localStorage.getItem('cyber.sound') !== 'off', amb = null;
  const ensure = () => { if (ac) return true; try { ac = new (window.AudioContext || window.webkitAudioContext)(); master = ac.createGain(); master.gain.value = .22; master.connect(ac.destination); } catch { return false; } return true; };
  const resume = () => { if (ac && ac.state === 'suspended') ac.resume(); };
  const tone = (f0, f1, dur, type = 'sine', g = .5, at = 0) => { if (!on || !ensure()) return; resume(); const t = ac.currentTime + at; const o = ac.createOscillator(), v = ac.createGain(); o.type = type; o.frequency.setValueAtTime(f0, t); if (f1) o.frequency.exponentialRampToValueAtTime(f1, t + dur); v.gain.setValueAtTime(0, t); v.gain.linearRampToValueAtTime(g, t + .006); v.gain.exponentialRampToValueAtTime(.0005, t + dur); o.connect(v); v.connect(master); o.start(t); o.stop(t + dur + .02); };
  const noise = (dur, g = .3, hp = 2000) => { if (!on || !ensure()) return; resume(); const t = ac.currentTime; const n = ac.sampleRate * dur | 0, b = ac.createBuffer(1, n, ac.sampleRate), d = b.getChannelData(0); for (let i = 0; i < n; i++) d[i] = (Math.random() * 2 - 1) * (1 - i / n); const src = ac.createBufferSource(); src.buffer = b; const f = ac.createBiquadFilter(); f.type = 'highpass'; f.frequency.value = hp; const v = ac.createGain(); v.gain.value = g; src.connect(f); f.connect(v); v.connect(master); src.start(t); };
  const ambient = (start) => { if (!ensure()) return; if (start && !amb && on) { const v = ac.createGain(); v.gain.value = 0; v.connect(master); const f = ac.createBiquadFilter(); f.type = 'lowpass'; f.frequency.value = 220; f.connect(v); const os = [55, 55.4, 82.5].map((fr) => { const o = ac.createOscillator(); o.type = 'triangle'; o.frequency.value = fr; o.connect(f); o.start(); return o; }); v.gain.linearRampToValueAtTime(.06, ac.currentTime + 4); amb = { v, os }; } if (!start && amb) { amb.v.gain.linearRampToValueAtTime(0, ac.currentTime + 1); const a = amb; amb = null; setTimeout(() => a.os.forEach((o) => o.stop()), 1200); } };
  const NOTES = [220, 246.9, 277.2, 329.6, 370, 440, 493.9];
  return {
    get on() { return on; },
    toggle() { on = !on; localStorage.setItem('cyber.sound', on ? 'on' : 'off'); if (on) { ensure(); resume(); ambient(true); tone(660, 990, .12, 'sine', .4); } else ambient(false); return on; },
    wake() { if (on && ensure()) { resume(); ambient(true); } },
    tick() { noise(.02, .25, 3000); tone(1800, 1200, .03, 'square', .08); },
    move(dir, ch) { noise(.03, .2, 1500); tone(dir > 0 ? 440 : 520, dir > 0 ? 560 : 400, .08, 'sine', .25); if (ch != null) { const r = NOTES[ch]; tone(r, null, .5, 'sine', .18, .04); tone(r * 1.5, null, .45, 'sine', .1, .08); } },
    link() { tone(880, 1320, .16, 'sine', .35); tone(1320, 1760, .22, 'triangle', .18, .1); },
    hash() { noise(.012, .12, 4000); },
    ticket() { tone(1760, 1750, .35, 'sine', .3); tone(2640, 2630, .25, 'sine', .12, .02); },
    converge(d) { const f = 220 + 1200 * Math.min(1, Math.max(0, (-Math.log10(Math.max(d, 1e-9)) - 1) / 7)); tone(f, f * 1.02, .07, 'triangle', .22); },
    stake(v) { tone(v ? 160 : 110, 60, .25, 'sine', .45); noise(.05, .15, 800); },
    mentor() { [0, 2, 4, 6].forEach((k, i) => tone(NOTES[k] * 2, null, .3, 'sine', .22, i * .09)); },
    chord(ch) { const r = NOTES[ch]; [1, 1.25, 1.5, 2].forEach((m, i) => tone(r * m, null, .9, 'sine', .14, i * .05)); },
  };
})();


/* ------------------------------------------------------------------ chapters = pages */
const CH = [
  { id: '', path: '/', name: 'bostrom', c: COLS[0] },
  { id: 'rebirth', path: '/rebirth', name: 'rebirth', c: COLS[1] },
  { id: 'balance', path: '/balance', name: 'balance', c: COLS[2] },
  { id: 'story', path: '/story', name: 'the story', c: COLS[3] },
  { id: 'bootloader', path: '/bootloader', name: 'the bootloader', c: COLS[4] },
  { id: 'graph', path: '/graph', name: 'the graph', c: COLS[5] },
  { id: 'next', path: '/next', name: 'what next', c: COLS[6] },
];
const S = []; const push = (ch, html, cls = '', extra = {}) => S.push({ ch, cls, html, ...extra });

/* 1 · cover */
push(0, `<div><p class="kick">the bootloader of superintelligence · block 1 → halt → ∞</p><p class="hero-word boot">BOSTROM</p><p class="sub">halted · laid to rest · reborn</p><p class="lead">almost five years, 3.1M particles, 2.9M cyberlinks. halted at height <b>25,120,712</b>. it returns in a new body on soft3 when the code is ready — with $BOOT, every balance and the whole graph.</p><p class="kbd">→ or space · swipe · every arrow is one step · <span id="nslides"></span> pages</p></div>`, 'one');

/* 2 · rebirth */
push(1, `<div><p class="kick">rebirth · when the code is ready</p><h2>no date.<br><em>a gate.</em></h2><p class="lead">bostrom returns as a root chain on soft3 on the day its code passes every gate: the genesis built from the burial and matched bit-exact, the rehearsal network holding under real use, the red team finding nothing critical. not a day earlier.</p><p class="mute">space-pussy, the canary, goes through every rehearsal first. the launch page tracks the gates as they turn green.</p></div><div class="nums"><div class="n"><big>no date</big><small>a milestone is code that passes its gate ${M('m')}</small></div><div class="n"><big>genesis</big><small>built from the burial, matched bit-exact, its particle the chain id ${M('m')}</small></div><div class="n"><big>rehearsal</big><small>the canary chain under real use before the bootloader moves ${M('t')}</small></div><div class="n"><big>the launch page</big><small><a href="https://cyber.page/launch/" target="_blank" rel="noopener">cyber.page/launch</a> — the gates, as they turn green ${M('t')}</small></div></div>`, '', { bridge: 'what returns, and what changes' });
push(1, `<div><p class="kick">rebirth · what returns</p><h2>everything you had.<br><em>nothing you must do.</em></h2><p class="lead">the genesis is built from the burial snapshot by a deterministic pipeline: two independent builds give the same bytes, and the particle of that file is the chain id.</p><div class="tiles"><span class="tile"><b>$BOOT</b>every balance, liquid again</span><span class="tile"><b>the graph</b>2,949,732 links, bit-exact</span><span class="tile"><b>your keys</b>the same secp256k1 key signs</span><span class="tile"><b>47,837 names</b>every passport, a link at height 0</span></div></div><div class="steps"><div class="step"><b>balances</b><span>liquid, delegated and undelegating amounts return to the account; LP positions dissolve into their tokens at halt reserves; every denom is carried as its own token ${M('m')}</span></div><div class="step"><b>graph</b><span>every cyberlink re-played in chain order; particles re-addressed from IPFS CIDs to hemera hashes, the old address kept resolvable ${M('m')}</span></div><div class="step"><b>passports</b><span>each of the 47,837 moon passports becomes a genesis link from its owner to its name ${M('m')}</span></div><div class="step"><b>TOCYB</b><span>carried unchanged; TOCYB × 666 → CYB belongs to the $CYB genesis, not this one ${M('t')}</span></div></div>`, '', { bridge: 'the new body' });
push(1, `<div><p class="kick">rebirth · the new body</p><h2>same keys.<br><em>new body.</em></h2><p class="lead">the new bostrom runs on soft3: one binary, the bootloader as data. your keys sign as before; every balance is liquid at genesis; the graph is carried whole. the rules of the new chain are published on the launch page as they are frozen — this site repeats nothing before then.</p><p class="mute">what is already fixed: the genesis file and its chain id, and that nothing a holder must do before the rebirth.</p></div><div class="nums"><div class="n"><big>a gate</big><small>genesis the day the code passes it — no date ${M('m')}</small></div><div class="n"><big>1 file</big><small>the genesis: deterministic, its particle is the chain id ${M('m')}</small></div><div class="n"><big>0 steps</big><small>for a holder before rebirth — the same key, the same balance ${M('m')}</small></div><div class="n"><big>the launch page</big><small><a href="https://cyber.page/launch/" target="_blank" rel="noopener">cyber.page/launch</a> — the rules, as they freeze ${M('t')}</small></div></div>`, 'ink', { bridge: 'check your balance before it moves' });

/* 3 · balance */
push(2, `<div><p class="kick">balance · from the final snapshot</p><h2>what you hold<br><em>at halt.</em></h2><p class="lead">balances are read from the burial snapshot, in your browser. a mnemonic or a private key is derived locally and never leaves this page. the chain is halted, so what you see is exactly what the genesis carries.</p><div class="nums"><div class="n"><big>61,675</big><small>accounts with a known key ${M('m')}</small></div><div class="n"><big>46,039</big><small>passport owners ${M('m')}</small></div></div><p class="fine">BOOT value at halt uses warp prices from the snapshot pools; TOCYB stands apart and shows its CYB at ×666</p></div>
<div class="panel checker" id="checker"><div class="tabs"><button class="tab on" data-m="name">name</button><button class="tab" data-m="addr">address</button><button class="tab" data-m="mnem">mnemonic</button><button class="tab" data-m="priv">private key</button><button class="tab" data-m="ledger">ledger</button></div>
<div data-in="name"><input id="pname" placeholder="passport name" autocomplete="off"></div>
<div data-in="addr" hidden><input id="addr" placeholder="bostrom1…" autocomplete="off"></div>
<div data-in="mnem" hidden><textarea id="mnem" placeholder="twelve or twenty-four words — derived locally, never sent anywhere"></textarea></div>
<div data-in="priv" hidden><input id="priv" placeholder="private key hex (64 chars) — derived locally"></div>
<div data-in="ledger" hidden><p class="hint">connect a Ledger with the Cosmos app open, then check.</p></div>
<div class="row"><button class="btn" id="go">check balance</button><button class="btn ghost" id="clr">clear</button></div>
<div class="addr" id="derived"></div><div class="bal" id="bal"></div><div class="err" id="err"></div>
<p class="hint">the chain is halted — balances are read from the snapshot. keys never leave this page.</p></div>`, '', { id: 'balance', bridge: 'how it got here' });

/* 4 · the story */
push(3, `<div><p class="kick">the story · from block 1</p><h2>named after Nick Bostrom.<br><em>built as the bootloader.</em></h2><p class="lead">superintelligence did not exist, and deploying one is a project whose mistakes have no precedent. so every assumption was tested first, on a chain built to be outgrown: the proving ground where each component of planetary superintelligence runs before it graduates to the protocol.</p><p class="mute">fifty validators, one GPU each, computed the rank of every particle inside consensus, every block — a network learning what matters without an oracle.</p></div><div class="nums"><div class="n"><big>3,143,650</big><small>particles ${M('m')}</small></div><div class="n"><big>2,949,732</big><small>cyberlinks ${M('m')}</small></div><div class="n"><big>~70,000</big><small>neurons · about a thousand linking ${M('m')}</small></div><div class="n"><big>47,837</big><small>moon passports ${M('m')}</small></div><div class="n"><big>25,120,712</big><small>blocks in almost five years ${M('m')}</small></div><div class="n"><big>50</big><small>validators, a GPU each ${M('m')}</small></div></div>`, '', { bridge: 'the idea it tested' });
push(3, `<div><p class="kick">the story · the idea</p><h2>one public mind<br><em>instead of one private model.</em></h2><p class="quote">frontier AI learns by backpropagation: feed data, push error backward, adjust weights — then freeze. <b>brains don't work like that.</b> they learn live: predict, act, sense, update. a world-model that keeps adapting on 20 watts.</p><p class="lead">bostrom is that idea made collective. humans, agents, robots, animals, sensors, swarms — all linking the same living graph.</p></div><div><p class="quote">link two ideas and you open a path for attention. stake strengthens the path. where attention accumulates is what the network treats as important right now. <b>every weight is public. auditable. contestable.</b></p><p class="quote">this is diffusion with teeth. for an ergodic walk, attention provably converges to a unique equilibrium — a shared map of collective focus that anyone can verify and recompute.</p></div>`, 'ink', { bridge: 'what the experiment measured' });
push(3, `<div><p class="kick">the story · calibration</p><h2>a live thermodynamic<br><em>experiment.</em></h2><p class="lead">in its fourth year the network carried 17 million bits of negentropy at five bits per link. connectivity stood at 0.94 — still below the predicted threshold where collective intelligence ignites. the phase transition did not come; the model was confirmed where it mattered: the bottlenecks the theory predicted appeared where it predicted them.</p><p class="mute">these are calibration data. the first of many. the next body is built to cross the threshold, not to approach it.</p></div><div class="nums"><div class="n"><big>0.94</big><small>connectivity at the last measurement ${M('m')}</small></div><div class="n"><big>17 Mbit</big><small>negentropy, five bits per link ${M('m')}</small></div><div class="n"><big>10²³</big><small>Avogadro: where individual behaviour stops mattering and only the whole remains ${M('t')}</small></div><div class="n"><big>97.63 %</big><small>of all particles complete to the last chunk, 356.67 GB walked ${M('m')}</small></div></div>`, '', { bridge: 'the four tokens' });

/* 5 · the bootloader — why, and the family */
push(4, `<div><p class="kick">the bootloader · why</p><h2>test everything first,<br><em>on a chain built for it.</em></h2><p class="lead">superintelligence did not exist. deploying one is a project whose mistakes have no precedent, so every assumption was tested first on bostrom — the bootloader. five years of calibration: 3.1M particles, 2.9M cyberlinks, the names and the balances.</p><p class="mute">it returns on soft3 as one of the two root books, carrying $BOOT and everything it learned.</p></div><div class="steps"><div class="step"><b>exact</b><span>the genesis is a deterministic function of the burial snapshot; two independent builds give the same bytes and the same chain id ${M('m')}</span></div><div class="step"><b>whole</b><span>every balance, every cyberlink, every passport comes home; the graph is replayed and matched against the snapshot ${M('m')}</span></div><div class="step"><b>provable</b><span>every block proven, the present proving the past back to genesis ${M('t')}</span></div></div>`, '', { bridge: 'bostrom · pussy · cyber' });
push(4, `<div class="col"><p class="kick">the bootloader · the family</p><h2>two root books.<br><em>one money.</em></h2><p class="lead">same binary, same genesis pipeline, two genesis roots minutes apart. every neuron's own book hangs off them.</p></div><div class="fig"><table class="cmp"><thead><tr><th></th><th><i style="--c:#00ff41"></i>bostrom</th><th><i style="--c:#7a00ff"></i>pussy</th><th><i style="--c:#00b8ff"></i>cyber</th></tr></thead><tbody>
<tr><td>what</td><td>the bootloader</td><td>the canary — takes every rehearsal first</td><td>the money</td></tr>
<tr><td>token</td><td>$BOOT</td><td>$PUSSY</td><td>$CYB</td></tr>
<tr><td>genesis</td><td>when the code is ready ${M('t')}</td><td>first — the canary ${M('t')}</td><td>phase 3 ${M('t')}</td></tr>
<tr><td>carries</td><td>every balance · 2.9M links · 47,837 names</td><td>every balance · 29K links</td><td>TOCYB × 666 → CYB</td></tr>
<tr><td>consensus</td><td>foculus</td><td>foculus</td><td>foculus</td></tr>
</tbody></table><p class="fine">the rules of both chains are published on <a href="https://cyber.page/launch/" target="_blank" rel="noopener">cyber.page/launch</a> as they freeze</p></div>`, '', { bridge: 'what the hand-over carries' });
push(4, `<div><p class="kick">the bootloader · the hand-over</p><h2>every onchain token<br><em>becomes BOOT.</em></h2><p class="lead">at halt, every other onchain token is priced at the warp pool prices of the last block and swapped into BOOT. the supply audit, from the snapshot:</p><p class="mute">TOCYB stands apart: it is not swapped. at the $CYB genesis 281,405,532,467,645 TOCYB become 187,416,084,623,451,570 CYB — ×666, about 1 % of the field cap.</p></div><div class="nums"><div class="n"><big>482,287,925,778,234</big><small>BOOT native supply at halt ${M('m')}</small></div><div class="n"><big>30,031,817,136,618</big><small>of it in IBC escrows · vouchers live on osmosis ${M('m')}</small></div><div class="n"><big>+102,912,144,666,169</big><small>minted by the swap · +21.3 %, mostly H ${M('m')}</small></div><div class="n"><big>585,200,070,444,403</big><small>final total supply of BOOT ${M('m')}</small></div></div>`, '', { bridge: 'the graph itself' });

/* 6 · the graph */
push(5, `<div class="fullgraph"><div><p class="kick">the graph · a sample of the real thing</p><h2>2,949,732 links.<br><em>drawn from the burial.</em></h2><p class="lead">behind this page: 1,200 particles and 6,000 cyberlinks sampled from the real bostrom graph — the 400 heaviest particles and the 800 that link into them most, laid out by the graph's own spectrum.</p><div class="gstat"><div><b>3,143,650</b><span>particles</span></div><div><b>2,949,732</b><span>cyberlinks</span></div><div><b>1,200 · 6,000</b><span>drawn here ${M('m')}</span></div></div></div></div>`, 'one bare', { id: 'cybergraph' });
push(5, `<div><p class="kick">the graph · the datasets</p><h2>the record<br><em>outlives every server.</em></h2><p class="lead">every dataset of the burial is content-addressed on IPFS, pinned to Pinata and to the cybernode. the manifest carries the sha256 of every file; the genesis pipeline reads these files and nothing else.</p><p class="fine">reproduce every file from an archive node: <a href="https://github.com/cyberia-to/bostrom/tree/main/snapshot" target="_blank" rel="noopener">github.com/cyberia-to/bostrom/snapshot</a></p></div><div class="panel checker"><table class="files" id="files"><tbody></tbody></table><p class="hint" id="manlink"></p></div>`, '', { id: 'datasets', bridge: 'the people who ran it' });

/* 7 · next */
push(6, `<div><p class="kick">what next · the heroes</p><h2>fifty validators,<br><em>one GPU each.</em></h2><p class="lead">a hero in bostrom is a validator; the tiers follow a cosmological metaphor, from stars up to galaxies, by stake and uptime. these are the ones with a page in the book.</p></div><div class="heroes">${['galaxy', 'posthuman', 'bronbro', 'papsan', 'spectrum', 'saturnia', 'godzilla', 'blackmatter', 'subi', 'sung2v', 'techstur', 'web34ever', 'a-gaming'].map((h) => `<a href="https://cyber.page/bostrom/heroes/${h}/" target="_blank" rel="noopener">${esc(h)}<small>hero</small></a>`).join('')}</div>`, '', { bridge: 'where the knowledge goes' });
push(6, `<div><p class="kick">what next · the new body</p><h2>the knowledge<br><em>moves to soft3.</em></h2><p class="lead">bostrom was the test; soft3 is the protocol it tested. the same graph, the same names and the same balances continue on a stack that proves every computation and keeps every proof.</p><div class="ctas"><a class="btn" href="/balance">check your balance</a><a class="btn ghost" href="https://cyber.page/launch/" target="_blank" rel="noopener">the launch</a><a class="btn ghost" href="https://soft3.org" target="_blank" rel="noopener">soft3</a><a class="btn ghost" href="https://cyb.ai" target="_blank" rel="noopener">cyb · the robot</a></div></div><div class="links"><a href="https://cyber.page/bootloader/bostrom/" target="_blank" rel="noopener"><b>cyber.page</b><span>the book: architecture, tokenomics, guides</span></a><a href="https://github.com/cyberia-to/bostrom" target="_blank" rel="noopener"><b>github</b><span>snapshot, scripts, manifest, pages</span></a><a href="https://snapshot.bostrom.network" target="_blank" rel="noopener"><b>snapshot</b><span>the burial page and its datasets</span></a><a href="https://spacepussy.ai" target="_blank" rel="noopener"><b>space-pussy</b><span>the canary, reborn first</span></a><a href="https://t.me/cyber" target="_blank" rel="noopener"><b>telegram</b><span>the community chat</span></a><a href="https://x.com/cyber_devs" target="_blank" rel="noopener"><b>x</b><span>updates</span></a><a href="https://www.coingecko.com/en/coins/bostrom" target="_blank" rel="noopener"><b>coingecko</b><span>BOOT price and markets</span></a><a href="https://coinmarketcap.com/currencies/bostrom/" target="_blank" rel="noopener"><b>coinmarketcap</b><span>BOOT analytics</span></a></div><p class="fine">measured · target · mock — every number wears the word its source carries. the dead chain's numbers are measured; the new body's are pinned in its spec.</p>`, 'ink', { id: 'next' });

/* ------------------------------------------------------------------ build */
const deck = $('#deck'), segs = $('#segs');
S.forEach((s, i) => deck.appendChild(el(`<section class="slide ch${s.ch} ${s.cls || ''}" data-i="${i}" data-ch="${String(s.ch + 1).padStart(2, '0')}" ${s.id ? `id="${s.id}"` : ''} style="--c:${CH[s.ch].c}"><div class="body">${s.html}</div>${s.bridge ? `<p class="bridge">→ ${esc(s.bridge)}</p>` : ''}</section>`)));
CH.forEach((c, i) => { const d = el(`<div class="seg" style="--sc:${c.c}" data-ch="${i}"><div class="fill"></div><span class="lab">${String(i + 1).padStart(2, '0')} ${c.name}</span></div>`); d.addEventListener('click', () => go(S.findIndex((s) => s.ch === i))); segs.appendChild(d); });
$('#nslides').textContent = S.length;
let cur = -1;
const fit = () => {
  const sl = document.querySelectorAll('.slide')[cur]; if (!sl) return;
  const body = sl.querySelector('.body');
  Object.assign(body.style, { transform: '', width: '', height: '', maxHeight: '', margin: '' }); sl.classList.remove('tight', 'tighter', 'scaled');
  const availW = body.clientWidth, availH = body.clientHeight;
  const over = () => body.scrollHeight > availH + 1 || body.scrollWidth > availW + 1;
  if (!over()) return;
  sl.classList.add('tight'); if (!over()) return;
  sl.classList.add('tighter'); if (!over()) return;
  let z = Math.min(availH / body.scrollHeight, availW / body.scrollWidth);
  sl.classList.add('scaled');
  for (let k = 0; k < 5; k++) {
    z = Math.max(.4, Math.floor(z * 100) / 100);
    Object.assign(body.style, { width: availW / z + 'px', height: availH / z + 'px', maxHeight: 'none', margin: '0', transform: `scale(${z})` });
    if (body.scrollHeight <= availH / z + 1 && body.scrollWidth <= availW / z + 1) break;
    z *= .96;
  }
};

let fitT = 0; const refit = () => { clearTimeout(fitT); fitT = setTimeout(fit, 40); };
addEventListener('resize', refit); addEventListener('orientationchange', refit); document.fonts?.ready.then(refit);

/* pages: /<chapter>[/<n>] */
const pathOf = (i) => { const ch = S[i].ch, k = S.filter((s, j) => s.ch === ch && j < i).length; return CH[ch].path + (k ? `/${k + 1}` : ''); };
const fromPath = (p) => { const parts = p.replace(/^\/+|\/+$/g, '').replace(/^tokens/, 'bootloader').split('/'); const ch = parts[0] ? CH.findIndex((c) => c.id === parts[0]) : 0; if (ch < 0) return 0; const k = Math.max(1, parseInt(parts[1]) || 1); const idx = S.map((s, i) => s.ch === ch ? i : -1).filter((i) => i >= 0); return idx[Math.min(k, idx.length) - 1] ?? 0; };
const go = (i, push = true) => {
  i = Math.max(0, Math.min(S.length - 1, i)); if (i === cur) return;
  const dir = i > cur ? 1 : -1, prevCh = cur >= 0 ? S[cur].ch : -1; cur = i; deck.dataset.dir = dir;
  document.querySelectorAll('.slide').forEach((s, k) => { s.classList.toggle('on', k === i); s.classList.toggle('left', k < i); });
  document.body.classList.toggle('ink', (S[i].cls || '').includes('ink')); document.body.className = document.body.className.replace(/\bch\d+\b/g, '').trim() + ' ch' + S[i].ch;
  const ch = S[i].ch, idx = S.filter((s, k) => s.ch === ch && k <= i).length, n = S.filter((s) => s.ch === ch).length;
  document.querySelectorAll('.seg').forEach((sg, k) => { sg.classList.toggle('cur', k === ch); sg.classList.toggle('done', k < ch); $('.fill', sg).style.width = k < ch ? '100%' : k === ch ? (idx / n * 100) + '%' : '0'; });
  sfx.move(dir, ch !== prevCh ? ch : null); if (navigator.vibrate) navigator.vibrate(8);
  graph.chapter(ch, S[i].cls || ''); graph.pulse();
  $('#pos').textContent = `${String(i + 1).padStart(2, '0')} / ${S.length}`;
  const p = pathOf(i); if (location.pathname !== p) { if (push) history.pushState({ i }, '', p); else history.replaceState({ i }, '', p); }
  requestAnimationFrame(() => requestAnimationFrame(fit));
};
window.deckGo = go; window.deckCount = () => S.length; window.deckFit = fit;
$('#prev').onclick = () => go(cur - 1); $('#next').onclick = () => go(cur + 1);
document.addEventListener('keydown', (e) => { if (['INPUT', 'TEXTAREA'].includes(e.target.tagName) || (e.target.tagName === 'BUTTON' && [' ', 'Enter'].includes(e.key))) return; if (['ArrowRight', ' ', 'PageDown', 'ArrowDown'].includes(e.key)) { e.preventDefault(); go(cur + 1); } if (['ArrowLeft', 'PageUp', 'ArrowUp'].includes(e.key)) { e.preventDefault(); go(cur - 1); } if (e.key === 'Home') go(0); if (e.key === 'End') go(S.length - 1); });
let wheelLock = 0; document.addEventListener('wheel', (e) => { const sc = e.target.closest('.checker'); if (sc && sc.scrollHeight > sc.clientHeight + 4) { const top = sc.scrollTop <= 0, bot = sc.scrollTop + sc.clientHeight >= sc.scrollHeight - 2; if (!(e.deltaY > 0 && bot) && !(e.deltaY < 0 && top)) return; } const t = Date.now(); const d = Math.abs(e.deltaX) > Math.abs(e.deltaY) ? e.deltaX : e.deltaY; if (t - wheelLock < 700 || Math.abs(d) < 24) return; wheelLock = t; go(cur + (d > 0 ? 1 : -1)); }, { passive: true });
let tx = null, ty = 0; document.addEventListener('touchstart', (e) => { tx = e.target.closest('input, textarea') ? null : e.touches[0].clientX; ty = e.touches[0].clientY; }, { passive: true });
document.addEventListener('touchend', (e) => { if (tx == null) return; const dx = e.changedTouches[0].clientX - tx, dy = e.changedTouches[0].clientY - ty; if (Math.abs(dx) < 48 && Math.abs(dy) < 48) return; const sc = e.target.closest('.checker'); if (sc && Math.abs(dy) > Math.abs(dx) && sc.scrollHeight > sc.clientHeight + 4) { const top = sc.scrollTop <= 0, bot = sc.scrollTop + sc.clientHeight >= sc.scrollHeight - 2; if (!(dy < 0 && bot) && !(dy > 0 && top)) return; } if (Math.abs(dx) > Math.abs(dy)) go(cur + (dx < 0 ? 1 : -1)); else go(cur + (dy < 0 ? 1 : -1)); tx = null; });
document.addEventListener('click', (e) => { const a = e.target.closest('a[href^="/"]'); if (!a || a.target === '_blank') return; const p = a.getAttribute('href'); if (!/^\/(rebirth|balance|story|bootloader|tokens|graph|next)?(\/\d+)?$/.test(p)) return; e.preventDefault(); go(fromPath(p)); });
addEventListener('popstate', () => go(fromPath(location.pathname), false));
document.addEventListener('pointerdown', (e) => { sfx.wake(); if (e.target.closest('button, a, .seg, .tab')) sfx.tick(); }, { passive: true });
document.addEventListener('keydown', () => sfx.wake(), { once: true });
/* music: missing you bostrom — the old site's soundtrack. on by default; browsers allow sound only after a gesture, so it starts on the first touch or key */
const music = (() => { const a = new Audio('/music/missing-you-bostrom.mp3'); a.loop = true; a.preload = 'auto'; a.volume = .5; let on = localStorage.getItem('bostrom.music') !== 'off', armed = false; const btn = $('#music');
  const paint = () => { btn.textContent = (on && !a.paused ? '❚❚' : '▶') + (matchMedia('(max-width:900px)').matches ? ' missing you' : ' missing you bostrom'); btn.classList.toggle('off', !on); btn.title = 'missing you bostrom · ' + (on ? (a.paused ? 'tap anywhere to start' : 'playing') : 'play'); };
  const play = () => a.play().then(paint).catch(paint);
  btn.onclick = (e) => { e.stopPropagation(); on = !on; localStorage.setItem('bostrom.music', on ? 'on' : 'off'); if (on) play(); else { a.pause(); paint(); } };
  const arm = () => { if (on && a.paused && !armed) { armed = true; play(); } };
  document.addEventListener('pointerdown', arm, { passive: true }); document.addEventListener('keydown', arm); document.addEventListener('touchstart', arm, { passive: true });
  a.addEventListener('play', paint); a.addEventListener('pause', paint); if (on) play(); paint(); return { get on() { return on; } }; })();
const sndBtn = $('#snd'); const sndPaint = () => { sndBtn.textContent = sfx.on ? '◉ sound' : '○ sound'; sndBtn.classList.toggle('off', !sfx.on); }; sndBtn.onclick = () => { sfx.toggle(); sndPaint(); }; sndPaint();
if (matchMedia('(pointer:fine)').matches) { const dot = el('<div class="cur-dot"></div>'), ring = el('<div class="cur-ring"></div>'); document.body.append(dot, ring); let rx = 0, ry = 0, px = 0, py = 0; addEventListener('mousemove', (e) => { px = e.clientX; py = e.clientY; dot.style.transform = `translate(${px}px,${py}px)`; ring.classList.toggle('hot', !!e.target.closest('button, a, .seg, .tab, input, textarea')); }, { passive: true }); const lag = () => { rx += (px - rx) * .18; ry += (py - ry) * .18; ring.style.transform = `translate(${rx}px,${ry}px)`; requestAnimationFrame(lag); }; lag(); document.body.classList.add('has-cursor'); }

/* ------------------------------------------------------------------ the balance checker — the snapshot app's logic, same data, same local derivation */
const GW = 'https://gateway.pinata.cloud/ipfs';
const CIDS = {
  'state_export.json.gz': 'QmY8u2gHR2i5fhQWpkgdyXqByW1F6kokDqd4hCXReQDK2D', 'cyberlinks_indexed.csv.gz': 'QmUFrsLYUK8USpNMEGBbUyi3nTuq12QcLiVWiyVMMVyyFf', 'balances.csv': 'QmTsM6YazUmAkz7sNbL1NY88cMciZpiTWHZEDCo3gZVo1h', 'holdings.jsonl': 'QmQkR5jkbXjqCUNB6uj4EWaCRd7oWS7zbkcTWX1ZWtkvqW', 'prices.json': 'Qmbzevge6MmsiYG4s8D58rG21QVh5FF9CXTjCDH72VZYoA', 'passports.jsonl': 'QmTSZ1DLV61ATVMRBmqVnebDjhVG52gLijwPQYzBxq3jQQ', 'passports_by_owner.json': 'QmYyH7aZTjW1y5rbfPXE6q9LXz8MpfjB3Q3F5Eb83kdWLk', 'pools.json': 'QmbtuP9wdD6KzMxVWCb9R1Un8XAkBEnWwMeB2P9B3qLbUr', 'delegations.csv': 'QmRt9HWgGv5UFkZ4q2WYDoXtTj1T9td1DECdvXkbWXP1SY', 'validators.json': 'QmQFWhxhJmKEK6QSwL2oKCaeLxLH8NM4fUDFD4tJLMcTVu', 'pubkeys.csv': 'QmXFT8ULxLqYV1jp388YFcXUCvJdCR8ptW2yJEQsNdp2sG', 'particles_availability.json': 'QmcqgPqjXTVW7LdTzAshQYaSvkNtifK5jz54dVHP5o1L1r', 'missing_particles.txt.gz': 'QmazTcXKwB4TYAN8gu6LJM83s5KPczM7mtTAVeZDiCAoiS', 'supply.json': 'QmcyWzweYjtxM9cf1YFNh9c6Qg8yhe6yy4ghXC7wVasPaM', 'manifest.json': 'QmZok9hZkUwC5t6GkASzwAHSrR49xRNbs6ig3Eaz7ffs52',
};
const DESC = {
  'state_export.json.gz': 'full chain state at halt (all modules) — gzip', 'cyberlinks_indexed.csv.gz': 'cyberlink graph rebuilt from block events: 2,949,732 links · bit-exact to the on-chain counter', 'balances.csv': 'every holder of every denom — liquid bank balances', 'holdings.jsonl': 'per-account breakdown: liquid · delegated · per-pool (LP decomposed into underlying tokens)', 'prices.json': 'boot rate per denom from snapshot pool reserves + pool compositions', 'passports_by_owner.json': 'owner address → passport nicknames', 'passports.jsonl': '47,837 moon passports: nickname · owner · resolver', 'pools.json': '30 liquidity pools: reserves + prices at halt', 'delegations.csv': 'delegator · validator · shares · boot', 'validators.json': 'validator set with metadata', 'pubkeys.csv': '61,675 account public keys (for future claims)', 'particles_availability.json': 'availability audit: 97.62 % of all 3.14M particles complete to the last chunk (356.67 GB walked, 17M blocks); 97.63 % at root level', 'missing_particles.txt.gz': 'the 74,513 particle CIDs absent at audit time', 'supply.json': 'total supply per denom',
};
const V = '5';
const ipfsUrl = (f) => `${GW}/${CIDS[f]}/${f}`;
const localUrl = (f) => `/${f}?v=${V}`;
const fetchData = async (f) => { try { const r = await fetch(localUrl(f)); if (r.ok) return r; } catch { } return fetch(ipfsUrl(f)); };
const ORDER = ['state_export.json.gz', 'cyberlinks_indexed.csv.gz', 'holdings.jsonl', 'prices.json', 'passports_by_owner.json', 'balances.csv', 'passports.jsonl', 'pools.json', 'delegations.csv', 'validators.json', 'pubkeys.csv', 'particles_availability.json', 'missing_particles.txt.gz', 'supply.json'];
let man = {};
const fmtB = (b) => { if (!b) return ''; const u = ['B', 'KB', 'MB', 'GB']; let i = 0; while (b > 1024 && i < 3) { b /= 1024; i++; } return b.toFixed(b < 10 && i > 0 ? 1 : 0) + u[i]; };
const renderFiles = () => { const tb = $('#files tbody'); if (!tb) return; tb.innerHTML = ORDER.map((f) => `<tr><td>${f}</td><td class="desc">${DESC[f] || ''}</td><td class="sz">${man[f] ? fmtB(man[f].bytes) : ''}</td><td><a href="${localUrl(f)}" download>download ↓</a><a class="ipfs" href="${ipfsUrl(f)}" title="permanent IPFS copy">ipfs</a></td></tr>`).join(''); $('#manlink').innerHTML = `manifest (sha256 of every file): <a href="${ipfsUrl('manifest.json')}" style="color:var(--c)">${CIDS['manifest.json']}</a> · each link is &lt;CID&gt;/&lt;filename&gt; on any IPFS gateway`; };
renderFiles(); fetchData('manifest.json').then((r) => r.json()).then((m) => { man = m.files || {}; renderFiles(); }).catch(() => { });

let mode = 'name';
document.querySelectorAll('#checker .tab').forEach((t) => t.onclick = () => { mode = t.dataset.m; document.querySelectorAll('#checker .tab').forEach((x) => x.classList.toggle('on', x === t)); document.querySelectorAll('#checker [data-in]').forEach((d) => { d.hidden = d.dataset.in !== mode; }); $('#derived').textContent = ''; $('#bal').innerHTML = ''; $('#err').textContent = ''; refit(); });
['pname', 'addr', 'priv'].forEach((id) => { const e = $('#' + id); if (e) e.addEventListener('keydown', (ev) => { if (ev.key === 'Enter') $('#go').click(); }); });
$('#clr').onclick = () => { ['pname', 'addr', 'mnem', 'priv'].forEach((id) => { const e = $('#' + id); if (e) e.value = ''; }); $('#derived').textContent = ''; $('#bal').innerHTML = ''; $('#err').textContent = ''; document.querySelectorAll('.slide.has-result').forEach((x) => x.classList.remove('has-result')); refit(); };
let LIB = null;
const libs = async () => { if (LIB) return LIB; const v = await import(`/vendor.js?v=${V}`); LIB = { bip39: v.bip39, bip32: v.bip32, secp: v.secp, sha: v.sha, rip: v.rip, base: v.base }; return LIB; };
const addrOf = async (compressedPub) => { const { sha, rip, base } = await libs(); const h = rip.ripemd160(sha.sha256(compressedPub)); return base.bech32.encode('bostrom', base.bech32.toWords(h)); };
const fromMnemonic = async (m) => { const { bip39, bip32, secp } = await libs(); const seed = await bip39.mnemonicToSeed(m.trim().replace(/\s+/g, ' ')); const hd = bip32.HDKey.fromMasterSeed(seed).derive("m/44'/118'/0'/0/0"); return addrOf(secp.secp256k1.getPublicKey(hd.privateKey, true)); };
const fromPriv = async (hex) => { const { secp, base } = await libs(); const pk = base.hex.decode(hex.trim().replace(/^0x/, '').toLowerCase()); return addrOf(secp.secp256k1.getPublicKey(pk, true)); };
const fromLedger = async () => { const tp = (await import('https://cdn.jsdelivr.net/npm/@ledgerhq/hw-transport-webusb@6.28.1/+esm')).default; const Cosmos = (await import('https://cdn.jsdelivr.net/npm/@ledgerhq/hw-app-cosmos@6.30.0/+esm')).default; const transport = await tp.create(); const app = new Cosmos(transport); const { address } = await app.getAddress("m/44'/118'/0'/0/0", 'bostrom'); return address; };
let HOLD = null, PRICES = null, PASS = null, NICK = null;
const loadHoldings = async () => { if (HOLD) return HOLD; const [txt, pr, ps] = await Promise.all([fetchData('holdings.jsonl').then((r) => r.text()), fetchData('prices.json').then((r) => r.json()).catch(() => null), fetchData('passports_by_owner.json').then((r) => r.json()).catch(() => null)]); PRICES = pr; PASS = ps; HOLD = {}; for (const line of txt.split('\n')) { if (!line.trim()) continue; const r = JSON.parse(line); HOLD[r.address] = r.holdings; } return HOLD; };
const N = (x) => Number(x).toLocaleString('en-US'), NB = (x) => Number(Math.round(x)).toLocaleString('en-US');
const ORD = { TOCYB: 0, BOOT: 1, H: 2, A: 3, V: 4, PUSSY: 5, 'LP-PUSSY': 6, ATOM: 7, OSMO: 8 };
const poolName = (id) => { const p = PRICES && PRICES.pools && PRICES.pools[id]; return p ? `pool ${id} · ${p.labels.join('/')}` : `pool ${id}`; };
$('#go').onclick = async () => {
  const err = $('#err'), der = $('#derived'), bal = $('#bal'); err.textContent = ''; bal.innerHTML = ''; der.textContent = 'deriving…'; sfx.hash();
  try {
    let addr;
    if (mode === 'name') { const q = $('#pname').value.trim().toLowerCase(); if (!q) { der.textContent = ''; err.textContent = 'enter a passport name'; return; } der.textContent = 'looking up…'; await loadHoldings(); if (!NICK) { NICK = {}; for (const o in (PASS || {})) for (const n of PASS[o]) NICK[n.toLowerCase()] = o; } addr = NICK[q]; if (!addr) { der.textContent = ''; err.textContent = `passport "${q}" not found in the snapshot`; return; } }
    else if (mode === 'addr') addr = $('#addr').value.trim();
    else if (mode === 'mnem') addr = await fromMnemonic($('#mnem').value);
    else if (mode === 'priv') addr = await fromPriv($('#priv').value);
    else if (mode === 'ledger') addr = await fromLedger();
    if (!addr || !addr.startsWith('bostrom1')) { der.textContent = ''; err.textContent = 'not a bostrom address'; return; }
    der.textContent = addr; bal.innerHTML = '<p class="hint">loading snapshot holdings…</p>';
    const H = await loadHoldings(); const rec = H[addr];
    if (!rec) { bal.innerHTML = '<p class="hint">no holdings for this address in the snapshot.</p>'; refit(); return; }
    const rate = (d) => { const r = PRICES && PRICES.rates && PRICES.rates[d]; return r > 0 ? r : null; };
    const tok = {};
    for (const d in rec) { const h = rec[d], L = h.label; const t = tok[L] || (tok[L] = { rate: null, liquid: 0, delegated: 0, undelegating: 0, pools: {}, total: 0, boot: 0, priced: true }); for (const k of ['liquid', 'delegated', 'undelegating', 'total']) t[k] += h[k]; for (const id in h.pools) t.pools[id] = (t.pools[id] || 0) + h.pools[id]; const r = rate(d); if (r !== null) { t.boot += h.total * r; if (t.rate === null) t.rate = r; } else if (h.total > 0) t.priced = false; }
    const labels = Object.keys(tok).sort((a, b) => (ORD[a] ?? 99) - (ORD[b] ?? 99) || (tok[b].total - tok[a].total));
    const est = (v) => v === null ? '–' : NB(v);
    let grand = 0, unpriced = false;
    const rows = labels.map((L) => { const t = tok[L]; if (L !== 'TOCYB') { grand += t.boot; if (!t.priced) unpriced = true; } const r = L === 'TOCYB' ? null : t.rate; const subs = [['liquid', 'liquid'], ['delegated', 'delegated'], ['undelegating', 'undelegating']].filter(([k]) => t[k] > 0).map(([k, lab]) => `<div class="sub"><span class="lbl">${lab}</span><span class="amt">${N(t[k])}</span><span class="est">${r ? est(t[k] * r) : ''}</span></div>`); for (const id of Object.keys(t.pools).sort((a, b) => t.pools[b] - t.pools[a])) if (t.pools[id] > 0) subs.push(`<div class="sub"><span class="lbl">${poolName(id)}</span><span class="amt">${N(t.pools[id])}</span><span class="est">${r ? est(t.pools[id] * r) : ''}</span></div>`); const tokEst = L === 'TOCYB' ? `→ ${N(t.total * 666)} CYB` : (t.priced || t.boot > 0 ? est(t.boot) : '–'); return `<div class="tk"><div class="trow"><span class="d">${esc(L)}</span><span class="amt">${N(t.total)}</span><span class="est">${tokEst}</span></div><div class="subs">${subs.join('')}</div></div>`; }).join('');
    const tocyb = tok['TOCYB'] ? tok['TOCYB'].total : 0, cyb = tocyb * 666;
    const hero = (cyb > 0 ? `<div class="hero cyb">${N(cyb)}<span class="unit">CYB</span></div><div class="hero-sub">genesis CYB · from ${N(tocyb)} TOCYB × 666 · <a href="https://cyber.page/cyber/$cyb/" target="_blank" rel="noopener">why</a></div>` : '') + `<div class="hero">${NB(grand)}${unpriced ? ' +' : ''}<span class="unit">BOOT</span></div><div class="hero-sub">total swap value · warp prices at halt · TOCYB not included</div>`;
    const nicks = PASS && PASS[addr]; const passline = nicks && nicks.length ? `<div class="passline">passport${nicks.length > 1 ? 's' : ''}: ${nicks.map((n) => `<b>${esc(n)}</b>`).join(' · ')}</div>` : '';
    bal.innerHTML = hero + passline + `<div class="bal-grid">` + rows + `</div><p class="hint">tap a token for liquid · delegated · pools</p>`;
    bal.querySelectorAll('.trow').forEach((r) => r.addEventListener('click', () => { r.parentElement.classList.toggle('open'); refit(); }));
    document.querySelectorAll('.slide')[cur].classList.add('has-result'); sfx.chord(2); refit();
  } catch (e) { der.textContent = ''; err.textContent = String(e.message || e); }
};

/* ------------------------------------------------------------------ the graph behind everything: the real bostrom sample from graph.json, drawn as the chapter's colour */
const graph = (() => {
  const cv = $('#graph'), ctx = cv.getContext('2d'); let W = 0, H = 0, hue = COLS[0], pulse = 0, full = false, data = null, t0 = performance.now();
  const resize = () => { W = cv.width = innerWidth * devicePixelRatio; H = cv.height = innerHeight * devicePixelRatio; }; addEventListener('resize', resize); resize();
  const synth = () => { const nodes = [], links = []; for (let i = 0; i < 400; i++) nodes.push(['s', 1 + Math.floor(Math.random() * 30), Math.random(), Math.random()]); for (let i = 1; i < 400; i++) links.push([i, Math.floor(Math.pow(Math.random(), 2.2) * i)]); return { nodes, links }; };
  fetch('/graph.json').then((r) => r.ok ? r.json() : synth()).catch(synth).then((d) => { data = d; const mx = Math.max(...d.nodes.map((n) => n[1])); d.nodes.forEach((n) => { n.r = .6 + 2.6 * Math.sqrt(n[1] / mx); n.ph = Math.random() * 6.28; }); });
  const tick = () => {
    ctx.clearRect(0, 0, W, H);
    if (data) {
      const t = (performance.now() - t0) / 1000, dpr = devicePixelRatio, pad = full ? .04 : .08, sx = W * (1 - 2 * pad), sy = H * (1 - 2 * pad);
      const X = (n) => W * pad + n[2] * sx + Math.sin(t * .3 + n.ph) * 2 * dpr, Y = (n) => H * pad + n[3] * sy + Math.cos(t * .27 + n.ph) * 2 * dpr;
      ctx.lineWidth = (full ? .9 : .6) * dpr; ctx.strokeStyle = hue; ctx.globalAlpha = (full ? .22 : .1) + pulse * .25; ctx.beginPath();
      for (const [i, j] of data.links) { const a = data.nodes[i], b = data.nodes[j]; ctx.moveTo(X(a), Y(a)); ctx.lineTo(X(b), Y(b)); } ctx.stroke();
      for (const n of data.nodes) { const big = n.r > 2; ctx.globalAlpha = (full ? .55 : .3) + (big ? .4 : 0) + pulse * .3; ctx.fillStyle = big ? '#fff' : hue; ctx.beginPath(); ctx.arc(X(n), Y(n), n.r * dpr * (full ? 1.3 : 1) * (1 + pulse * .6), 0, 6.283); ctx.fill(); }
    }
    ctx.globalAlpha = 1; pulse *= .95; requestAnimationFrame(tick);
  };
  tick();
  return { chapter(c, cls) { hue = COLS[c]; full = c === 5; cv.style.opacity = cls.includes('ink') ? '.18' : full ? '1' : '.85'; }, pulse() { pulse = Math.max(pulse, .8); } };
})();

go(fromPath(location.pathname), false);
})();
