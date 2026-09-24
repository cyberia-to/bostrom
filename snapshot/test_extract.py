#!/usr/bin/env python3
# unit coverage for extract.py's smart, cmd_pools, cmd_staking, cmd_pubkeys and
# cmd_manifest. The network is replaced by patching extract.get/extract.paged;
# cmd_balances, cmd_supply and cmd_passport are covered elsewhere.
import json, os, tempfile, unittest
from unittest import mock

import extract


class SmartTests(unittest.TestCase):
    def test_encodes_query_and_returns_data_field(self):
        with mock.patch.object(extract, "get", return_value={"data": {"count": 3}}) as m:
            out = extract.smart("bostrom1contract", {"num_tokens": {}})
        self.assertEqual(out, {"count": 3})
        (path,), _ = m.call_args
        self.assertTrue(path.startswith("/cosmwasm/wasm/v1/contract/bostrom1contract/smart/"))


class CmdPoolsTests(unittest.TestCase):
    def _run(self, pools, balances_by_acc):
        with tempfile.TemporaryDirectory() as tmp:
            extract.OUT = tmp
            with mock.patch.object(extract, "paged", return_value=iter(pools)):
                with mock.patch.object(extract, "get", side_effect=lambda p: {
                    "balances": balances_by_acc[p.split("/")[-1]]
                }):
                    extract.cmd_pools()
            return json.load(open(f"{tmp}/pools.json"))

    def test_computes_price_from_reserve_balances(self):
        pools = [{"id": 1, "reserve_account_address": "acc1",
                  "reserve_coin_denoms": ["boot", "hydrogen"],
                  "pool_coin_denom": "pool1"}]
        balances = {"acc1": [{"denom": "boot", "amount": "200"},
                              {"denom": "hydrogen", "amount": "100"}]}
        out = self._run(pools, balances)
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0]["reserves"], {"boot": "200", "hydrogen": "100"})
        self.assertEqual(out[0]["price"]["boot_in_hydrogen"], 0.5)

    def test_zero_reserve_yields_null_price_not_a_crash(self):
        pools = [{"id": 2, "reserve_account_address": "acc2",
                  "reserve_coin_denoms": ["boot", "hydrogen"],
                  "pool_coin_denom": "pool2"}]
        balances = {"acc2": []}
        out = self._run(pools, balances)
        self.assertIsNone(out[0]["price"]["boot_in_hydrogen"])


class CmdStakingTests(unittest.TestCase):
    def test_writes_validators_and_delegations(self):
        validators = [{"operator_address": "valoper1",
                       "description": {"moniker": "node-a"}}]
        delegations = [{"delegation": {"delegator_address": "del1"},
                        "balance": {"amount": "500"}}]
        delegations[0]["delegation"]["shares"] = "500.0"

        def fake_paged(path, key, limit=1000, extra=""):
            if "validators/valoper1/delegations" in path:
                return iter(delegations)
            return iter(validators)

        with tempfile.TemporaryDirectory() as tmp:
            extract.OUT = tmp
            with mock.patch.object(extract, "paged", side_effect=fake_paged):
                extract.cmd_staking()
            vals = json.load(open(f"{tmp}/validators.json"))
            rows = open(f"{tmp}/delegations.csv").read().splitlines()
        self.assertEqual(vals, validators)
        self.assertEqual(rows[0], "delegator,validator,shares,balance_boot")
        self.assertEqual(rows[1], "del1,valoper1,500.0,500")


class CmdPubkeysTests(unittest.TestCase):
    def _run(self, accounts):
        with tempfile.TemporaryDirectory() as tmp:
            extract.OUT = tmp
            with mock.patch.object(extract, "paged", return_value=iter(accounts)):
                extract.cmd_pubkeys()
            return open(f"{tmp}/pubkeys.csv").read().splitlines()

    def test_reads_base_account_pubkey(self):
        rows = self._run([{"base_account": {"address": "addr1",
                                             "pub_key": {"@type": "/t", "key": "k1"}}}])
        self.assertEqual(rows[1], "addr1,/t,k1")

    def test_falls_back_to_base_vesting_account(self):
        rows = self._run([{"base_vesting_account": {
            "base_account": {"address": "addr2", "pub_key": {"@type": "/t", "key": "k2"}}}}])
        self.assertEqual(rows[1], "addr2,/t,k2")

    def test_missing_pubkey_writes_empty_fields(self):
        rows = self._run([{"base_account": {"address": "addr3"}}])
        self.assertEqual(rows[1], "addr3,,")


class CmdManifestTests(unittest.TestCase):
    def test_hashes_every_output_file_and_excludes_itself(self):
        with tempfile.TemporaryDirectory() as tmp:
            extract.OUT = tmp
            open(f"{tmp}/supply.json", "w").write('{"a":1}')
            open(f"{tmp}/balances.csv", "w").write("address,denom,amount\n")
            with mock.patch("builtins.print"):
                extract.cmd_manifest()
            man = json.load(open(f"{tmp}/manifest.json"))
        self.assertEqual(man["chain_id"], "bostrom")
        self.assertIn("supply.json", man["files"])
        self.assertIn("balances.csv", man["files"])
        self.assertNotIn("manifest.json", man["files"])
        self.assertEqual(man["files"]["balances.csv"]["bytes"],
                          len("address,denom,amount\n"))


if __name__ == "__main__":
    unittest.main()
