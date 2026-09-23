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

    def read_jsonl(self, name):
        with open(os.path.join(self._tmp, name)) as f:
            return [json.loads(line) for line in f if line.strip()]


class CmdPassportTests(_OutDirTestCase):
    def _run(self, fake_smart):
        with mock.patch.dict(os.environ, {"PASSPORT": "bostrom1passport"}), mock.patch(
            "extract.smart", side_effect=fake_smart
        ):
            extract.cmd_passport()

    def test_writes_one_line_per_token_across_a_paginated_walk(self):
        def fake_smart(addr, q):
            self.assertEqual(addr, "bostrom1passport")
            if q == {"num_tokens": {}}:
                return {"count": 2}
            if q == {"all_tokens": {"limit": 100}}:
                return {"tokens": ["1", "2"]}
            if q == {"all_tokens": {"limit": 100, "start_after": "2"}}:
                return {"tokens": []}
            if q == {"all_nft_info": {"token_id": "1"}}:
                return {
                    "access": {"owner": "bostrom1a"},
                    "info": {"extension": {"name": "one"}, "token_uri": None},
                }
            if q == {"all_nft_info": {"token_id": "2"}}:
                return {"access": {"owner": "bostrom1b"}, "info": {}}
            raise AssertionError(f"unexpected query {q}")

        self._run(fake_smart)
        recs = self.read_jsonl("passports.jsonl")
        self.assertEqual([r["nickname"] for r in recs], ["1", "2"])
        self.assertEqual(recs[0], {
            "nickname": "1", "owner": "bostrom1a",
            "extension": {"name": "one"}, "token_uri": None,
        })
        # a token record missing extension/token_uri entirely still writes,
        # both fields defaulting to null rather than a KeyError
        self.assertEqual(recs[1], {
            "nickname": "2", "owner": "bostrom1b",
            "extension": None, "token_uri": None,
        })

    def test_start_after_carries_the_last_token_id_of_the_previous_page(self):
        seen_start_after = []

        def fake_smart(addr, q):
            if q == {"num_tokens": {}}:
                return {"count": 2}
            if "all_tokens" in q:
                sa = q["all_tokens"].get("start_after")
                seen_start_after.append(sa)
                return {"tokens": ["1", "2"]} if sa is None else {"tokens": []}
            return {"access": {"owner": "x"}, "info": {}}

        self._run(fake_smart)
        self.assertEqual(seen_start_after, [None, "2"])

    def test_empty_first_page_writes_an_empty_file_not_a_crash(self):
        def fake_smart(addr, q):
            if q == {"num_tokens": {}}:
                return {"count": 0}
            if "all_tokens" in q:
                return {"tokens": []}
            raise AssertionError("all_nft_info should not be queried for zero tokens")

        self._run(fake_smart)
        self.assertEqual(self.read_jsonl("passports.jsonl"), [])

    def test_missing_passport_env_var_fails_loud_not_with_an_empty_address(self):
        os.environ.pop("PASSPORT", None)
        with self.assertRaises(KeyError):
            extract.cmd_passport()


if __name__ == "__main__":
    unittest.main()
