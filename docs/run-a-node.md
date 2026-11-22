# run a node

What it takes to stand a node of bostrom, to mine on it and to look at it. The network is not launched. The launch being prepared is the one of pussy, and its rehearsal network is where the same commands can be tried today ([space-pussy](https://github.com/cyberia-to/space-pussy/blob/main/docs/run-a-node.md)).

## the binary

The node is [cybernode](https://github.com/cyberia-to/cybernode), one binary for every network. From a checkout of it:

```sh
cargo install --path rs
```

## the genesis

The node needs the genesis file of the network it joins. Build it from this repository and check it against the lock:

```sh
cybernode genesis build --chain bostrom --snapshot snapshot --out bostrom.genesis
cybernode genesis verify bostrom.genesis --root
```

The particle `verify` prints is the chain id in [genesis/genesis.lock](../genesis/genesis.lock). A file with another particle is another network.

## the node

```sh
cybernode node --chain bostrom --genesis bostrom.genesis --home ~/.bostrom \
  --bind 127.0.0.1:7782 --radio 0.0.0.0:7792 --peers peers.toml --moniker my-node
```

- `--bind` is the node's API, kept on the machine.
- `--radio` is the wire to other nodes, UDP, open to the network.
- `--peers` is a file of the endpoint ids of nodes to meet; `cybernode node id --home ~/.bostrom` prints this node's own.

The node's state is under `--home`. The defaults of the ports are in [network.toml](../network.toml).

## mining

```sh
cybernode mine --address NEURON --chain bostrom --node http://127.0.0.1:7782
cybernode mine bench
```

`--address` is the neuron the block's reward goes to. `bench` measures what this machine does on each of its backends.

## looking at it

- the node's own API: `curl http://127.0.0.1:7782/status`
- the explorer of pussy reads any node: `https://spacepussy.ai/explorer/?api=<base>`

## what the rules are

- the chain, the wire and their conformance: [cybernode specs](https://github.com/cyberia-to/cybernode/tree/main/specs)
- this network's values: [network.toml](../network.toml)
