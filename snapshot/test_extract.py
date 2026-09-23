#!/usr/bin/env python3
# unit tests for extract.py's HTTP-retry primitives (get, paged) and the
# three commands the launch #14 (6) review named as still uncovered:
# cmd_balances, cmd_supply, cmd_passport. Fixtures replace the network at
# the same seam extract.py already exposes (get/paged/smart), never a
# real LCD endpoint.
import json
import os
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(__file__))
import extract  # noqa: E402


class GetRetryTests(unittest.TestCase):
    def test_succeeds_without_retry(self):
        resp = mock.MagicMock()
        resp.__enter__.return_value = resp
        resp.__exit__.return_value = False
        resp.read.return_value = b'{"ok": true}'
        with mock.patch("extract.urllib.request.urlopen", return_value=resp) as u:
            out = extract.get("/x")
        self.assertEqual(out, {"ok": True})
        self.assertEqual(u.call_count, 1)

    def test_retries_then_succeeds(self):
        calls = {"n": 0}
        resp = mock.MagicMock()
        resp.__enter__.return_value = resp
        resp.__exit__.return_value = False
        resp.read.return_value = b'{"ok": true}'

        def flaky(url, timeout=60):
            calls["n"] += 1
            if calls["n"] < 3:
                raise OSError("boom")
            return resp

        with mock.patch("extract.urllib.request.urlopen", side_effect=flaky), \
                mock.patch("extract.time.sleep") as slept:
            out = extract.get("/x")
        self.assertEqual(out, {"ok": True})
        self.assertEqual(calls["n"], 3)
        # backoff is 2*(attempt+1): attempts 0 and 1 failed before success
        self.assertEqual([c.args[0] for c in slept.call_args_list], [2, 4])

    def test_raises_after_five_attempts(self):
        with mock.patch("extract.urllib.request.urlopen", side_effect=OSError("boom")) as u, \
                mock.patch("extract.time.sleep"):
            with self.assertRaises(OSError):
                extract.get("/x")
        self.assertEqual(u.call_count, 5)


class PagedTests(unittest.TestCase):
    def test_follows_pagination_key_until_exhausted(self):
        pages = [
            {"items": [1, 2], "pagination": {"next_key": "k1"}},
            {"items": [3], "pagination": {"next_key": None}},
        ]
        seen_paths = []

        def fake_get(path):
            seen_paths.append(path)
            return pages.pop(0)

        with mock.patch("extract.get", side_effect=fake_get):
            out = list(extract.paged("/thing", "items"))
        self.assertEqual(out, [1, 2, 3])
        self.assertEqual(len(seen_paths), 2)
        self.assertIn("pagination.key=k1", seen_paths[1])

    def test_empty_key_returns_nothing(self):
        with mock.patch("extract.get", return_value={"items": []}):
            out = list(extract.paged("/thing", "items"))
        self.assertEqual(out, [])


class CmdSupplyTests(unittest.TestCase):
    def test_writes_supply_json(self):
        fixture = [{"denom": "boot", "amount": "123"}, {"denom": "hydrogen", "amount": "7"}]
        tmp = tempfile.mkdtemp()
        with mock.patch("extract.paged", return_value=iter(fixture)), \
                mock.patch.object(extract, "OUT", tmp):
            extract.cmd_supply()
        with open(os.path.join(tmp, "supply.json")) as f:
            self.assertEqual(json.load(f), fixture)


class CmdBalancesTests(unittest.TestCase):
    def test_writes_balances_csv_and_denom_traces(self):
        owners = {
            "boot": [{"address": "addr1", "balance": {"amount": "10"}}],
            "hydrogen": [{"address": "addr2", "balance": {"amount": "5"}}],
        }
        traces = [{"hash": "abc", "path": "transfer/channel-0", "base_denom": "hydrogen"}]

        def fake_paged(path, key, limit=1000, extra=""):
            if path == "/ibc/apps/transfer/v1/denom_traces":
                return iter(traces)
            prefix = "/cosmos/bank/v1beta1/denom_owners/"
            self.assertTrue(path.startswith(prefix))
            denom = path[len(prefix):]
            return iter(owners.get(denom, []))

        tmp = tempfile.mkdtemp()
        with mock.patch("extract.denoms_of_interest", return_value=["boot", "hydrogen"]), \
                mock.patch("extract.paged", side_effect=fake_paged), \
                mock.patch.object(extract, "OUT", tmp):
            extract.cmd_balances()

        with open(os.path.join(tmp, "balances.csv")) as f:
            rows = f.read().strip().splitlines()
        self.assertEqual(rows[0], "address,denom,amount")
        self.assertIn("addr1,boot,10", rows)
        self.assertIn("addr2,hydrogen,5", rows)

        with open(os.path.join(tmp, "denom_traces.json")) as f:
            self.assertEqual(json.load(f), traces)

    def test_no_denoms_writes_header_only(self):
        tmp = tempfile.mkdtemp()
        with mock.patch("extract.denoms_of_interest", return_value=[]), \
                mock.patch("extract.paged", return_value=iter([])), \
                mock.patch.object(extract, "OUT", tmp):
            extract.cmd_balances()
        with open(os.path.join(tmp, "balances.csv")) as f:
            rows = f.read().strip().splitlines()
        self.assertEqual(rows, ["address,denom,amount"])


class CmdPassportTests(unittest.TestCase):
    def test_paginates_tokens_and_writes_jsonl(self):
        contract = "wasm1passport"
        # two tokens, no start_after pagination beyond one page
        tokens = ["1", "2"]
        nft_info = {
            "1": {"access": {"owner": "ownerA"}, "info": {"extension": {"n": "one"}, "token_uri": None}},
            "2": {"access": {"owner": "ownerB"}, "info": {"extension": None, "token_uri": "ipfs://x"}},
        }

        def fake_smart(addr, q):
            self.assertEqual(addr, contract)
            if "num_tokens" in q:
                return {"count": len(tokens)}
            if "all_tokens" in q:
                start_after = q["all_tokens"].get("start_after")
                if start_after is None:
                    return {"tokens": tokens}
                return {"tokens": []}
            if "all_nft_info" in q:
                return nft_info[q["all_nft_info"]["token_id"]]
            raise AssertionError(f"unexpected query {q}")

        tmp = tempfile.mkdtemp()
        with mock.patch("extract.smart", side_effect=fake_smart), \
                mock.patch.object(extract, "OUT", tmp), \
                mock.patch.dict(os.environ, {"PASSPORT": contract}):
            extract.cmd_passport()

        with open(os.path.join(tmp, "passports.jsonl")) as f:
            recs = [json.loads(line) for line in f]
        self.assertEqual(len(recs), 2)
        self.assertEqual(recs[0], {
            "nickname": "1", "owner": "ownerA",
            "extension": {"n": "one"}, "token_uri": None,
        })
        self.assertEqual(recs[1], {
            "nickname": "2", "owner": "ownerB",
            "extension": None, "token_uri": "ipfs://x",
        })

    def test_zero_tokens_writes_empty_file(self):
        contract = "wasm1empty"

        def fake_smart(addr, q):
            if "num_tokens" in q:
                return {"count": 0}
            if "all_tokens" in q:
                return {"tokens": []}
            raise AssertionError(f"unexpected query {q}")

        tmp = tempfile.mkdtemp()
        with mock.patch("extract.smart", side_effect=fake_smart), \
                mock.patch.object(extract, "OUT", tmp), \
                mock.patch.dict(os.environ, {"PASSPORT": contract}):
            extract.cmd_passport()

        with open(os.path.join(tmp, "passports.jsonl")) as f:
            self.assertEqual(f.read(), "")


if __name__ == "__main__":
    unittest.main()
