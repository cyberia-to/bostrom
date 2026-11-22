# genesis

How block 0 of bostrom is made, in four files.

| file | what it holds |
|---|---|
| [sources.toml](sources.toml) | the input: the burial snapshot of the old chain, by the digest of its manifest |
| [distribution.toml](distribution.toml) | who holds what: the rules that turn the snapshot's accounts and balances into owners and tokens |
| [graph.toml](graph.toml) | the starting graph: how the old chain's particles and cyberlinks are carried |
| [genesis.lock](genesis.lock) | the result, by digest: the genesis file's particle, which is the chain id, the id of block 0 and the state root |

The sources are pinned, the rules are fixed, so the result is one file and anybody can rebuild it:

```sh
cybernode genesis build --chain bostrom --snapshot ../snapshot --out bostrom.genesis
cybernode genesis verify bostrom.genesis --root
```

`build` prints the particle, the genesis supply, the subsidy, the state root and the id of block 0, and writes them with the counts and the source pins into `bostrom.genesis.json`. `verify` decodes the file strictly and recomputes them. They are the lines of the lock.

The genesis file itself, 330,841,520 bytes, is not in git. The snapshot's files are fetched into `~/.cache/cyber/snapshots/bostrom/`.

## what the lock is for

The particle of the genesis file is the chain id: every block and every signal of the network commits to it. A node that loads a file with another particle is on another network. So the lock changes only when an input changes — a source, a rule, the genesis time — and only together with a build receipt in [`audit/`](../audit/): two independent builds, the same bytes.

The lock in this folder is for the genesis time pinned for the first attempt. The launch is by readiness, after the one of pussy; when its time is set the file is rebuilt and the lock moves.

## where the rules live today

In the node: cybernode `specs/genesis.md` is the pipeline, `specs/chain.md` §4 the format and the derivation. `distribution.toml` and `graph.toml` state for bostrom what that pipeline does; it does not read them yet. The project that makes them its input is soft3 [networks as repositories](https://github.com/cyberia-to/soft3/blob/release/phase1/projects/network-repos.md).
