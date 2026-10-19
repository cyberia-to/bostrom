# TOCYB holders, the gift multisig, and what sits across IBC — 2026-10-19

Inputs: the burial snapshot in `~/.cache/cyber/snapshots/bostrom` and
`…/pussy` (files of 2026-10-15: `holdings.jsonl`, `balances.csv`,
`supply.json`, `state_export.json.gz`, `passports_by_owner.json`); Osmosis
live state from `https://lcd.osmosis.zone` on 2026-10-19 (bostrom is halted,
so the Osmosis side of channel-95 is frozen except for in-flight packets).
Names come from passports (`passports_by_owner.json`), module and contract
labels from `state_export.json.gz`. Amounts are raw chain units; 1 TOCYB unit
becomes 666 cy at the cyber genesis (`cyber/tokens.md`, `$CYB.md`).

## TOCYB

Supply 281,405,532,467,645 over 1,434 holders; the top 20 hold 93.6 %.

| # | name | address | TOCYB | share | genesis treatment (soft3/specs/genesis.md) |
|---|---|---|---|---|---|
| 1 | cybergift multisig (2 of 3) | bostrom1qs9w7ry45axfxjgxa4jmuhjthzfvj78sxh5p6e | 97.0 T | 34.5 % | `legacy_owner`, dormant (multisig) |
| 2 | community pool (distribution module; the senate) | bostrom1jv65s3grqf6v6jl3dp4t6c9t9rk99cd8yvs0hc | 50.7 T | 18.0 % | `legacy_owner`, dormant (module) |
| 3 | congress | bostrom1mqn6z7tpyy3glwqfsmg9lly87vjs8dgkt3zs3a | 50.0 T | 17.8 % | key known |
| 4 | founder | bostrom16230lc9r27vrxlzd4wlvcz2l66quzj84vlkxc5 | 10.4 T | 3.7 % | key known |
| 5 | cyberhead, wndrfl | bostrom1gxhs5wzam5rlgf6cs0lkme400ut64d4ncpfs2h | 10.0 T | 3.6 % | key known |
| 6 | master | bostrom1qn8sr2hzmktlecusdtxj9hwj0upnm0jft9snar | 9.2 T | 3.3 % | key known |
| 7 | rockets | bostrom1s4czxghmh29aw2ldynk8r9lnkfccw5ph8rjpxa | 4.4 T | 1.6 % | key known |
| 8 | superhuman | bostrom1pntx8ql2v7cqxu05etg8c4v0r2vz7qnq9uqmpy | 4.0 T | 1.4 % | key known |
| 9 | cyberdeep | bostrom1ttd4h585vgy29gj0xe0p338drvw9w4m4hzwj9p | 4.0 T | 1.4 % | key known |
| 10 | soul | bostrom1qwzsnnuk2u6avvh059c9p50gqqquvcu5svvwrs | 4.0 T | 1.4 % | key known |
| 11 | zlobabah | bostrom1m8yf3g2m9p7danjvt4ga6vzewy380pk52kcu9z | 4.0 T | 1.4 % | key known |
| 12 | sigma | bostrom1g07gj9ph0r2hjx6ffqn8vl38u4agd5mpqx9m7f | 4.0 T | 1.4 % | key known |
| 13 | encom | bostrom1t3222ju7ssu58xsm3m2xw445p94cqn2qrex3vy | 2.0 T | 0.7 % | key known |
| 14 | andromeda | bostrom1edlrze5f48jjaw0wxcve4asqqf2tcjdl59ln8q | 2.0 T | 0.7 % | key known |
| 15 | dreamcitizencosmos | bostrom1wnpak7sfawsfv9c8vqe7naxfa4g99lv77d7c0z | 1.6 T | 0.6 % | key known; 404 links |
| 16 | — | bostrom10c8znaj94y900syues06dz50hw6y9qpkhunn25 | 1.4 T | 0.5 % | key known |
| 17 | — | bostrom1s3lgc3mgy4ltwr796qk6j73xmau4njueds0mgu | 1.3 T | 0.5 % | never signed; kind-3 claim |
| 18 | — | bostrom10556xtnp39nvx3ec3yjafug662pyt6af84n477 | 1.3 T | 0.5 % | never signed; kind-3 claim |
| 19 | main | bostrom1t4vzrx79r8pfunwhrhqzlkmplh3zxfdk8lwwcx | 1.1 T | 0.4 % | key known |
| 20 | rodiki | bostrom1s4wntr9selfaznc2ezjkwnwt2y0terx9tqpda3 | 1.0 T | 0.4 % | key known |

The periodic-vesting accounts among them vest only H/A/V (investmint), never
TOCYB; every TOCYB balance above is liquid.

## the multisig is the cybergift multisig

- `go-cyber/app/upgrades/v6/upgrades.go:233–243` (commit 1b62e564,
  2025-09-03, "added gift burn on upgrade") names
  `bostrom1qs9w7ry45axfxjgxa4jmuhjthzfvj78sxh5p6e` as `giftMSAddress` and
  burns 603 T BOOT and 603 T TOCYB from it.
- `space-pussy/ts/src/utils/finalResultGoL.js` gives it `gift: 700 T` in the
  game-of-links final result; cyber-prophet/bostrom-journal `bj001.md`: "70 %
  of supply is allocated to the Gift" linking this address.
- `bostrom/finalization of $BOOT distribution.md`: "cybergift multisig under
  cybercongress control: 603T BOOT and 700T TOCYB". 700 T − 603 T burned =
  the 97 T TOCYB left; its BOOT is 0 (97 T BOOT went to the cybergift
  contract earlier, the rest was burned).
- Members (secp256k1, threshold 2): bostrom18wmu3larp6xxjaxn0gk2tzxte29mtch2eg765f,
  bostrom1tvz7kpf0pwwf3pfguxqxgynkx9lhyv8zvqz9h8,
  bostrom17jrh028fcsq9zk44mumfudm6rhcds8uf07ka2c. None of them holds a
  balance, a pubkey, a delegation or a passport on bostrom, and none appears
  in any public GitHub file: keys used only inside the multisig. Account
  sequence 2.
- Why 97 T TOCYB survived the burn: at genesis the multisig held 700 T BOOT
  and 700 T TOCYB (`go-cyber/networks/bostrom/genesis.json`); 97 T BOOT left
  it for the cybergift claim contract, its TOCYB never moved; v6 burned a
  fixed 603 T of each, sized to the BOOT left, so the BOOT went to 0 and
  97 T TOCYB stayed. The supply confirms the upgrade ran: 1,000 T − 603 T
  (gift) − 115,594,467,532,355 (congress) = 281,405,532,467,645, the
  snapshot supply to the unit.
- The congress multisig of v6 is a different account,
  bostrom1xszmhkfjs3s00z2nvtn7evqxw3dtus6yr8e4pw: its 115.59 T TOCYB and
  its BOOT were burned; at the halt it holds only A and V. The `congress`
  passport account (#3) is a single key.

## IBC escrow on bostrom (tokens that live on other chains)

Escrow address = `sha256("ics20-1\0transfer/<channel>")[:20]`, for every
transfer channel in the export.

| denom | in escrow | supply | share | of which Osmosis (channel-2 ↔ osmosis channel-95) |
|---|---|---|---|---|
| boot | 30,031,818,136,617 | 482,287,925,778,234 | 6.23 % | 29,948,781,923,024 |
| hydrogen | 16,356,013,373,264 | 305,452,862,328,021 | 5.35 % | 16,307,648,876,474 |
| tocyb | 101,838,741,187 | 281,405,532,467,645 | 0.04 % | 101,031,208,714 |

Other channels: space-pussy channel-11 62.8 G BOOT, 48.0 G H, 0.81 G TOCYB;
cosmoshub channels 4/5/8 19.7 G BOOT; gravity, juno, desmos, evmos, axelar,
deep below 0.05 G BOOT each.

Osmosis supply of the bostrom denoms on 2026-10-19: BOOT
29,948,183,715,294 (0.6 G below the escrow: in-flight or timed-out packets),
H 16,307,648,876,474, TOCYB 101,031,208,714 — equal to escrow.

Holders on Osmosis (`denom_owners_by_query`): BOOT 1,876 accounts holding
25.74 T (4.21 T of the supply is not on any listed account, unresolved);
51 % of the listed BOOT sits in six pool module accounts, the rest on
20-byte keys whose bostrom twins are the same key (e.g. singleton/nexus
1.04 T, asadovka 0.56 T, mrgalaxy 0.52 T). H: 291 accounts, master 3.59 T,
zlobobah 2.10 T, ibcbot 1.18 T, pools ≈ 5.4 T. TOCYB: 62 accounts, asadovka
79.9 G and one unnamed key 19.3 G hold 99 %.

At the cyber genesis the escrow accounts are address-only, so they fall to
`legacy_owner` and stay dormant: the 30 T BOOT held on Osmosis has no owner
on the reborn bostrom unless the genesis credits the Osmosis holders.

## pussy

PUSSY escrow 5,389,836,483,227,616 (0.49 % of 1.0994 E), almost all on
channel-0 to bostrom (it lives on bostrom as an ibc denom); liquidpussy
1.93 P (2.2 %). The pussy distribution module holds 982.67 P PUSSY, 98 % of
the supply — dormant at genesis like bostrom's community pool.
