---
tags: cyber
crystal-type: process
crystal-domain: cyber
---
[first multisig](https://github.com/cybercongress/cybercongress/commit/3498fddfddb71d2c66cda35ebdcbc64363ea3447#diff-b335630551682c19a781afebcf4d07bf978fb1f8ac04c6bf87428ed5106870f5R71) with gleb

- ethereum: [0x9f4062F6153Ff4Dbf93F6A6F686eD3C906Bf0684](https://bloxy.info/address/0x9f4062F6153Ff4Dbf93F6A6F686eD3C906Bf0684)
- signers:
	- [0xfbb2a29dff113d518893c00387f6d5492898354e](https://bloxy.info/address/0xfbb2a29dff113d518893c00387f6d5492898354e)
	- [0x00B8Fe1A1A2b899418702e32A96E276Ff56A4D05](https://bloxy.info/address/0x00B8Fe1A1A2b899418702e32A96E276Ff56A4D05)
	- [0x00725D89a2A2FB3B21Fd1035B579cbCDE4a0991b](https://bloxy.info/address/0x00725D89a2A2FB3B21Fd1035B579cbCDE4a0991b)

second multisg with nick

- ethereum: [0xE46c088b5DD483cDa2400EE70296baD4903fC845](https://bloxy.info/address/0xE46c088b5DD483cDa2400EE70296baD4903fC845)

current multisig

- ethereum: [0xa0a55e68dc52b47f8a9d5d05329fab5bdabffb14](https://bloxy.info/address/0xa0a55e68dc52b47f8a9d5d05329fab5bdabffb14)
	- signers:
		- [0xb3aE2C46D2342e8c4e22bd12B08fF1545d2f36b7](https://bloxy.info/address/0xb3aE2C46D2342e8c4e22bd12B08fF1545d2f36b7)
		- ...
- bostrom: [QmZHBdeWb7E7UQ82PXLVU15mCzoN3s7tZNfBT64wmcEDvp](https://cyb.ai/oracle/ask/QmZHBdeWb7E7UQ82PXLVU15mCzoN3s7tZNfBT64wmcEDvp)
## chaingear fee trail (verified on-chain 2026-09-09)

Question: 22 databases × 10 ETH were paid into Chaingear
[0x02e0c94355562693B3608077732d7437bd7a78ca](https://etherscan.io/address/0x02e0c94355562693B3608077732d7437bd7a78ca)
(2019-01 → 2020-03). Where did the 220 ETH go?

Answer: nothing ever stayed in Chaingear. It is a `PaymentSplitter` with ONE payee
holding 100/100 shares, and that payee is the cyber•Congress ops multisig
[0xB52B7EdA722249499e3a28B5BB6c778ee0Ac462c](https://etherscan.io/address/0xB52B7EdA722249499e3a28B5BB6c778ee0Ac462c)
(Gnosis `MultiSigWalletWithDailyLimit`; signers 0x00B8Fe1A + 0xfBb2A29D — the
"first multisig" signers above). The multisig is also `owner()` of Chaingear.

- `getTotalReleased()` = 220 ETH, `getReleased(0xB52B…)` = 220 ETH, `getCreationFeeWei()` = 10 ETH,
  `totalSupply()` = 22 CHG. Every `createDatabase` batch was followed by `release()` from 0x00B8Fe1A (10 calls).
- The other 2 ETH (two `fundDatabase` deposits, 2019-07/09) sat in the Safe
  0x86ed5b9a56b9f9ee7b399a68999c658384941ca1 until `claimDatabaseFunds` on databases 0 and 1 (2026-09) — that is the "found 2 ETH".
- Multisig → Aragon **Finance** 0xa0A55e68 (the "current multisig" above; vault = **Agent** 0x3A1F8600):
  200 ETH in 7 executed transfers — 50 (2019-12-10), 20 (12-30), 30 (2020-01-20), 10 (01-29), 20 (02-20), 10 (03-04), 60 (03-18).
  Matches Finance ledger inflow from 0xB52B exactly (200 ETH). The first 20 ETH of fees (Jan–Feb 2019, pre-Aragon)
  left the multisig on 2019-11-01 with the remaining balance straight to the Agent (24.476 + 0.42 ETH executed;
  three sibling ~24.9 ETH attempts were `ExecutionFailure`).
- Finance ledger (`getTransaction(1..237)`): ETH in 919, out 951 (direct-to-Agent deposits don't appear as inflows).
  Recipients: 0xb3aE2C46 421.7 ETH / 20 payments 2021-07→2024-09 (incl. 200 on 2021-08-31, 100 on 2022-05-19;
  refs "BOOT liquidity", "warp listing", "Teams Funding", "reserve"); 0xda07097f 160.3 ETH / 21 payments 2019-11→2020-12;
  0x97975Ed1 102 ETH / 22 payments 2020-06→2024-07 (also deposited 176.5 ETH); monthly payroll 2019-12→2020-12 to
  0x8b5b2864 (57.1), 0xe8298160 (51.3), 0x00ca47db (41.1), 0x3a9d2cc5 (39.5), 0xa3da86c8 (7 × 1 ETH); one-offs
  0x80631c54 35 ETH (2021-11-27), 0xc4afcc52 7.6, 0xd6e705c0 5.0, 0x00B8Fe1A 3.5.
- Today: Chaingear 0 ETH, multisig 0.0002 ETH + dust tokens, Agent 0 ETH + dust (GOL/KICK/GOLD/REP). Nothing of the
  220 ETH remains in any of the three contracts; it funded cyber•Congress operations 2019–2024.

Method: blockscout v2 API (txs/logs/internal), publicnode `eth_call` for splitter state and the full Finance ledger,
sources github.com/cyberia-to/chaingear (`contracts/common/PaymentSplitter.sol`, `chaingear/FeeSplitterChaingear.sol`).
