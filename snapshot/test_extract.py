import hashlib
import os
import tempfile
import unittest

from extract import (
    is_denom_of_interest, pool_record, delegation_row, account_pubkey_row,
    build_manifest,
)


class TestIsDenomOfInterest(unittest.TestCase):
    def test_ibc_prefix(self):
        self.assertTrue(is_denom_of_interest("ibc/ABCDEF"))

    def test_pool_prefix(self):
        self.assertTrue(is_denom_of_interest("pool123"))

    def test_li_substring(self):
        self.assertTrue(is_denom_of_interest("factory/addr/lien"))

    def test_unrelated_denom(self):
        self.assertFalse(is_denom_of_interest("boot"))

    def test_gravity_denom_not_matched(self):
        self.assertFalse(is_denom_of_interest("gravity0xdeadbeef"))


class TestPoolRecord(unittest.TestCase):
    def test_normal_reserves(self):
        p = {"id": 7, "reserve_coin_denoms": ["boot", "hydrogen"],
             "pool_coin_denom": "pool7"}
        reserves = {"boot": "1000", "hydrogen": "2000"}
        rec = pool_record(p, reserves)
        self.assertEqual(rec["id"], 7)
        self.assertEqual(rec["type"], "native-liquidity")
        self.assertEqual(rec["denoms"], ["boot", "hydrogen"])
        self.assertEqual(rec["reserves"], reserves)
        self.assertEqual(rec["pool_coin_denom"], "pool7")
        self.assertEqual(rec["price"]["boot_in_hydrogen"], 2.0)

    def test_zero_reserve_a_yields_none_price(self):
        p = {"id": 1, "reserve_coin_denoms": ["boot", "hydrogen"],
             "pool_coin_denom": "pool1"}
        reserves = {"boot": "0", "hydrogen": "500"}
        rec = pool_record(p, reserves)
        self.assertIsNone(rec["price"]["boot_in_hydrogen"])

    def test_missing_other_reserve_prices_as_zero(self):
        p = {"id": 2, "reserve_coin_denoms": ["boot", "milliampere"],
             "pool_coin_denom": "pool2"}
        rec = pool_record(p, {"boot": "10"})
        self.assertEqual(rec["reserves"], {"boot": "10"})
        self.assertEqual(rec["price"]["boot_in_milliampere"], 0.0)

    def test_missing_want_reserve_prices_as_none(self):
        p = {"id": 3, "reserve_coin_denoms": ["boot", "milliampere"],
             "pool_coin_denom": "pool3"}
        rec = pool_record(p, {"milliampere": "10"})
        self.assertIsNone(rec["price"]["boot_in_milliampere"])


class TestDelegationRow(unittest.TestCase):
    def test_row_shape(self):
        d = {"delegation": {"delegator_address": "bostrom1abc", "shares": "123.0"},
             "balance": {"amount": "456"}}
        self.assertEqual(delegation_row(d, "bostromvaloper1xyz"),
                          ["bostrom1abc", "bostromvaloper1xyz", "123.0", "456"])


class TestAccountPubkeyRow(unittest.TestCase):
    def test_base_account(self):
        a = {"base_account": {"address": "bostrom1a",
                               "pub_key": {"@type": "/cosmos.crypto.secp256k1.PubKey", "key": "AbC="}}}
        self.assertEqual(account_pubkey_row(a),
                          ["bostrom1a", "/cosmos.crypto.secp256k1.PubKey", "AbC="])

    def test_base_vesting_account_fallback(self):
        a = {"base_vesting_account": {"base_account": {"address": "bostrom1v",
                                                         "pub_key": {"@type": "t", "key": "k"}}}}
        self.assertEqual(account_pubkey_row(a), ["bostrom1v", "t", "k"])

    def test_no_base_account_uses_top_level(self):
        a = {"address": "bostrom1raw"}
        self.assertEqual(account_pubkey_row(a), ["bostrom1raw", "", ""])

    def test_missing_pub_key(self):
        a = {"base_account": {"address": "bostrom1nopk", "pub_key": None}}
        self.assertEqual(account_pubkey_row(a), ["bostrom1nopk", "", ""])


class TestBuildManifest(unittest.TestCase):
    def test_hashes_and_sizes_every_file_except_manifest(self):
        with tempfile.TemporaryDirectory() as d:
            with open(f"{d}/a.csv", "w") as f:
                f.write("x,y\n1,2\n")
            with open(f"{d}/manifest.json", "w") as f:
                f.write("{}")
            man = build_manifest(d, chain_id="pussy", final_height=1,
                                  final_block_time="t", method="m")
            self.assertEqual(man["chain_id"], "pussy")
            self.assertEqual(man["final_height"], 1)
            self.assertNotIn("manifest.json", man["files"])
            self.assertIn("a.csv", man["files"])
            with open(f"{d}/a.csv", "rb") as f:
                content = f.read()
            self.assertEqual(man["files"]["a.csv"]["sha256"], hashlib.sha256(content).hexdigest())
            self.assertEqual(man["files"]["a.csv"]["bytes"], len(content))

    def test_empty_dir(self):
        with tempfile.TemporaryDirectory() as d:
            man = build_manifest(d)
            self.assertEqual(man["files"], {})
            self.assertEqual(man["chain_id"], "bostrom")


if __name__ == "__main__":
    unittest.main()
