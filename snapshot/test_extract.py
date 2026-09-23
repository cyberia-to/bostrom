import csv
import os
import shutil
import tempfile
import unittest
from unittest import mock

import extract


class _OutDirTestCase(unittest.TestCase):
    """cmd_* functions write to the module-level OUT dir; point it at a
    scratch directory for the duration of each test."""

    def setUp(self):
        self._tmp = tempfile.mkdtemp()
        self._patch_out = mock.patch.object(extract, "OUT", self._tmp)
        self._patch_out.start()

    def tearDown(self):
        self._patch_out.stop()
        shutil.rmtree(self._tmp, ignore_errors=True)

    def read_csv(self, name):
        with open(os.path.join(self._tmp, name), newline="") as f:
            return list(csv.reader(f))


class CmdPubkeysTests(_OutDirTestCase):
    def test_plain_account_pubkey_written(self):
        accounts = [{
            "base_account": {
                "address": "bostrom1plain",
                "pub_key": {"@type": "/cosmos.crypto.secp256k1.PubKey", "key": "AbCdEf=="},
            }
        }]
        with mock.patch("extract.paged", return_value=iter(accounts)) as p:
            extract.cmd_pubkeys()
        rows = self.read_csv("pubkeys.csv")
        self.assertEqual(rows[0], ["address", "pubkey_type", "pubkey_base64"])
        self.assertEqual(rows[1], ["bostrom1plain", "/cosmos.crypto.secp256k1.PubKey", "AbCdEf=="])
        self.assertEqual(p.call_args.args, ("/cosmos/auth/v1beta1/accounts", "accounts"))
        self.assertEqual(p.call_args.kwargs, {"limit": 500})

    def test_vesting_account_unwraps_the_nested_base_account(self):
        accounts = [{
            "base_vesting_account": {
                "base_account": {
                    "address": "bostrom1vesting",
                    "pub_key": {"@type": "/cosmos.crypto.secp256k1.PubKey", "key": "VeSt=="},
                }
            }
        }]
        with mock.patch("extract.paged", return_value=iter(accounts)):
            extract.cmd_pubkeys()
        rows = self.read_csv("pubkeys.csv")
        self.assertEqual(rows[1], ["bostrom1vesting", "/cosmos.crypto.secp256k1.PubKey", "VeSt=="])

    def test_module_account_with_no_wrapper_falls_back_to_the_bare_entry(self):
        accounts = [{"address": "bostrom1module", "name": "mint"}]
        with mock.patch("extract.paged", return_value=iter(accounts)):
            extract.cmd_pubkeys()
        rows = self.read_csv("pubkeys.csv")
        self.assertEqual(rows[1], ["bostrom1module", "", ""])

    def test_missing_pub_key_writes_empty_type_and_key_not_a_crash(self):
        accounts = [{"base_account": {"address": "bostrom1nokey"}}]
        with mock.patch("extract.paged", return_value=iter(accounts)):
            extract.cmd_pubkeys()
        rows = self.read_csv("pubkeys.csv")
        self.assertEqual(rows[1], ["bostrom1nokey", "", ""])

    def test_multiple_accounts_all_written_in_order(self):
        accounts = [
            {"base_account": {"address": "a1", "pub_key": {"@type": "t1", "key": "k1"}}},
            {"base_account": {"address": "a2", "pub_key": {"@type": "t2", "key": "k2"}}},
        ]
        with mock.patch("extract.paged", return_value=iter(accounts)):
            extract.cmd_pubkeys()
        rows = self.read_csv("pubkeys.csv")
        self.assertEqual([r[0] for r in rows[1:]], ["a1", "a2"])


if __name__ == "__main__":
    unittest.main()
