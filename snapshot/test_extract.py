import csv
import json
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

    def read_json(self, name):
        with open(os.path.join(self._tmp, name)) as f:
            return json.load(f)

    def read_csv(self, name):
        with open(os.path.join(self._tmp, name)) as f:
            return list(csv.reader(f))


class CmdBalancesTests(_OutDirTestCase):
    def test_writes_balances_csv_and_denom_traces_json(self):
        traces = [{"denom_trace": "path/base", "base_denom": "boot"}]

        def fake_paged(path, key, limit=1000, extra=""):
            if path == "/cosmos/bank/v1beta1/supply":
                return iter([])  # no extra ibc/pool denoms beyond CORE
            if path == "/cosmos/bank/v1beta1/denom_owners/boot":
                return iter([{"address": "bostrom1a", "balance": {"amount": "100"}}])
            if path == "/ibc/apps/transfer/v1/denom_traces":
                return iter(traces)
            return iter([])

        with mock.patch("extract.paged", side_effect=fake_paged):
            extract.cmd_balances()
        rows = self.read_csv("balances.csv")
        self.assertEqual(rows[0], ["address", "denom", "amount"])
        self.assertIn(["bostrom1a", "boot", "100"], rows)
        self.assertEqual(self.read_json("denom_traces.json"), traces)

    def test_extra_denom_from_supply_is_also_queried_for_owners(self):
        seen_paths = []

        def fake_paged(path, key, limit=1000, extra=""):
            seen_paths.append(path)
            if path == "/cosmos/bank/v1beta1/supply":
                return iter([{"denom": "ibc/AAAA"}])
            if path == "/ibc/apps/transfer/v1/denom_traces":
                return iter([])
            return iter([])

        with mock.patch("extract.paged", side_effect=fake_paged):
            extract.cmd_balances()
        self.assertIn("/cosmos/bank/v1beta1/denom_owners/ibc%2FAAAA", seen_paths)

    def test_no_owners_still_writes_header_only_csv(self):
        with mock.patch("extract.paged", return_value=iter([])):
            extract.cmd_balances()
        self.assertEqual(self.read_csv("balances.csv"), [["address", "denom", "amount"]])
        self.assertEqual(self.read_json("denom_traces.json"), [])


class CmdStakingTests(_OutDirTestCase):
    def test_writes_validators_json_and_delegations_csv(self):
        validators = [{"operator_address": "bostromvaloper1x", "description": {"moniker": "val1"}}]
        delegations = [
            {
                "delegation": {"delegator_address": "bostrom1d", "shares": "1000.0"},
                "balance": {"amount": "1000"},
            }
        ]

        def fake_paged(path, key, limit=1000, extra=""):
            if path == "/cosmos/staking/v1beta1/validators":
                return iter(validators)
            if path == "/cosmos/staking/v1beta1/validators/bostromvaloper1x/delegations":
                return iter(delegations)
            return iter([])

        with mock.patch("extract.paged", side_effect=fake_paged):
            extract.cmd_staking()
        self.assertEqual(self.read_json("validators.json"), validators)
        rows = self.read_csv("delegations.csv")
        self.assertEqual(rows[0], ["delegator", "validator", "shares", "balance_boot"])
        self.assertIn(["bostrom1d", "bostromvaloper1x", "1000.0", "1000"], rows)

    def test_multiple_validators_each_queried_by_own_operator_address(self):
        validators = [
            {"operator_address": "bostromvaloper1a", "description": {"moniker": "val-a"}},
            {"operator_address": "bostromvaloper1b", "description": {"moniker": "val-b"}},
        ]
        queried = []

        def fake_paged(path, key, limit=1000, extra=""):
            if path == "/cosmos/staking/v1beta1/validators":
                return iter(validators)
            if path.startswith("/cosmos/staking/v1beta1/validators/"):
                queried.append(path)
            return iter([])

        with mock.patch("extract.paged", side_effect=fake_paged):
            extract.cmd_staking()
        self.assertEqual(
            queried,
            [
                "/cosmos/staking/v1beta1/validators/bostromvaloper1a/delegations",
                "/cosmos/staking/v1beta1/validators/bostromvaloper1b/delegations",
            ],
        )

    def test_no_validators_yields_empty_files_not_a_crash(self):
        with mock.patch("extract.paged", return_value=iter([])):
            extract.cmd_staking()
        self.assertEqual(self.read_json("validators.json"), [])
        self.assertEqual(
            self.read_csv("delegations.csv"),
            [["delegator", "validator", "shares", "balance_boot"]],
        )


if __name__ == "__main__":
    unittest.main()
