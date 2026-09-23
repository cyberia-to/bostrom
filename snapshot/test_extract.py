import hashlib
import io
import json
import os
import shutil
import tempfile
import unittest
from unittest import mock

import extract
from extract import build_manifest, is_extra_denom, pool_price, resolve_base_account


class _FakeResponse:
    """a context manager standing in for urllib.request.urlopen's return value"""

    def __init__(self, payload):
        self._payload = payload

    def __enter__(self):
        return io.BytesIO(json.dumps(self._payload).encode())

    def __exit__(self, *exc):
        return False


class IsExtraDenomTests(unittest.TestCase):
    def test_ibc_denom(self):
        self.assertTrue(is_extra_denom("ibc/AAAA"))

    def test_liquidity_pool_coin(self):
        self.assertTrue(is_extra_denom("pool_coin_1"))

    def test_slash_li_marker(self):
        self.assertTrue(is_extra_denom("gravity/liabc"))

    def test_core_denom_not_extra(self):
        self.assertFalse(is_extra_denom("boot"))
        self.assertFalse(is_extra_denom("hydrogen"))


class PoolPriceTests(unittest.TestCase):
    def test_price_is_rb_over_ra(self):
        self.assertEqual(pool_price(2_000_000, 4_000_000), 2.0)

    def test_zero_ra_returns_none_not_divide_by_zero(self):
        self.assertIsNone(pool_price(0, 4_000_000))


class ResolveBaseAccountTests(unittest.TestCase):
    def test_plain_base_account(self):
        a = {"base_account": {"address": "bostrom1x", "pub_key": {"key": "k"}}}
        self.assertEqual(resolve_base_account(a)["address"], "bostrom1x")

    def test_vesting_account_unwraps_nested_base_account(self):
        a = {"base_vesting_account": {"base_account": {"address": "bostrom1y"}}}
        self.assertEqual(resolve_base_account(a)["address"], "bostrom1y")

    def test_vesting_account_explicit_null_does_not_crash(self):
        # a real LCD payload can carry the key with a JSON null value
        # instead of omitting it; a bare `.get(k, {})` default is skipped
        # when the key is present, so `.get("base_account")` on None
        # raised AttributeError before this fix
        a = {"base_vesting_account": None, "address": "bostrom1z"}
        self.assertEqual(resolve_base_account(a)["address"], "bostrom1z")

    def test_module_account_falls_back_to_record_itself(self):
        a = {"address": "bostrom1mod", "@type": "/cosmos.auth.v1beta1.ModuleAccount"}
        self.assertEqual(resolve_base_account(a)["address"], "bostrom1mod")


class GetTests(unittest.TestCase):
    def test_returns_parsed_json_on_first_success(self):
        with mock.patch("extract.urllib.request.urlopen", return_value=_FakeResponse({"ok": True})):
            self.assertEqual(extract.get("/x"), {"ok": True})

    def test_retries_on_transient_failure_then_succeeds(self):
        calls = {"n": 0}

        def flaky(*a, **k):
            calls["n"] += 1
            if calls["n"] < 3:
                raise TimeoutError("boom")
            return _FakeResponse({"ok": True})

        with mock.patch("extract.urllib.request.urlopen", side_effect=flaky), \
             mock.patch("extract.time.sleep") as sleep:
            self.assertEqual(extract.get("/x"), {"ok": True})
        self.assertEqual(calls["n"], 3)
        self.assertEqual(sleep.call_count, 2)

    def test_reraises_the_real_exception_after_five_failed_attempts(self):
        with mock.patch("extract.urllib.request.urlopen", side_effect=TimeoutError("boom")), \
             mock.patch("extract.time.sleep"):
            with self.assertRaises(TimeoutError):
                extract.get("/x")

    def test_backoff_grows_linearly_by_attempt_and_never_sleeps_after_the_last(self):
        with mock.patch("extract.urllib.request.urlopen", side_effect=TimeoutError("boom")), \
             mock.patch("extract.time.sleep") as sleep:
            with self.assertRaises(TimeoutError):
                extract.get("/x")
        self.assertEqual([c.args[0] for c in sleep.call_args_list], [2, 4, 6, 8])


class PagedTests(unittest.TestCase):
    def test_single_page_yields_all_items(self):
        with mock.patch("extract.get", return_value={"items": [1, 2, 3],
                                                       "pagination": {"next_key": None}}) as g:
            self.assertEqual(list(extract.paged("/x", "items")), [1, 2, 3])
        g.assert_called_once()

    def test_follows_next_key_across_pages(self):
        pages = [
            {"items": [1, 2], "pagination": {"next_key": "abc"}},
            {"items": [3], "pagination": {"next_key": None}},
        ]
        with mock.patch("extract.get", side_effect=pages) as g:
            self.assertEqual(list(extract.paged("/x", "items")), [1, 2, 3])
        self.assertEqual(g.call_count, 2)
        self.assertIn("pagination.key=abc", g.call_args_list[1].args[0])

    def test_missing_pagination_block_stops_after_one_page(self):
        with mock.patch("extract.get", return_value={"items": [1]}):
            self.assertEqual(list(extract.paged("/x", "items")), [1])

    def test_missing_key_yields_nothing(self):
        with mock.patch("extract.get", return_value={"pagination": {"next_key": None}}):
            self.assertEqual(list(extract.paged("/x", "items")), [])

    def test_extra_query_string_is_appended(self):
        with mock.patch("extract.get", return_value={"items": [],
                                                       "pagination": {"next_key": None}}) as g:
            list(extract.paged("/x", "items", extra="&status=BOND"))
        self.assertIn("&status=BOND", g.call_args.args[0])

    def test_next_key_is_url_quoted(self):
        # urllib.parse.quote's default safe="/" leaves a base64 next_key's
        # slash literal and only escapes its '+'; harmless in a query value,
        # pinned here rather than assumed
        pages = [
            {"items": [1], "pagination": {"next_key": "a/b+c"}},
            {"items": [], "pagination": {"next_key": None}},
        ]
        with mock.patch("extract.get", side_effect=pages) as g:
            list(extract.paged("/x", "items"))
        self.assertIn("pagination.key=a/b%2Bc", g.call_args_list[1].args[0])


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


class CmdSupplyTests(_OutDirTestCase):
    def test_writes_the_paged_supply_list_verbatim(self):
        supply = [{"denom": "boot", "amount": "123"}, {"denom": "hydrogen", "amount": "7"}]
        with mock.patch("extract.paged", return_value=iter(supply)) as p:
            extract.cmd_supply()
        self.assertEqual(self.read_json("supply.json"), supply)
        self.assertEqual(p.call_args.args[0], "/cosmos/bank/v1beta1/supply")

    def test_empty_supply_still_writes_an_empty_list(self):
        with mock.patch("extract.paged", return_value=iter([])):
            extract.cmd_supply()
        self.assertEqual(self.read_json("supply.json"), [])


class CmdPoolsTests(_OutDirTestCase):
    def test_pool_price_and_reserves_come_from_the_balances_lookup(self):
        pool = {
            "id": "1",
            "reserve_account_address": "bostrom1reserve",
            "reserve_coin_denoms": ["boot", "hydrogen"],
            "pool_coin_denom": "pool1",
        }
        balances = {"balances": [{"denom": "boot", "amount": "100"}, {"denom": "hydrogen", "amount": "250"}]}
        with mock.patch("extract.paged", return_value=iter([pool])), mock.patch(
            "extract.get", return_value=balances
        ) as g:
            extract.cmd_pools()
        [written] = self.read_json("pools.json")
        self.assertEqual(written["reserves"], {"boot": "100", "hydrogen": "250"})
        self.assertEqual(written["price"], {"boot_in_hydrogen": pool_price(100, 250)})
        self.assertEqual(g.call_args.args[0], "/cosmos/bank/v1beta1/balances/bostrom1reserve")

    def test_a_reserve_denom_absent_from_balances_prices_as_none_not_a_crash(self):
        pool = {
            "id": "2",
            "reserve_account_address": "bostrom1empty",
            "reserve_coin_denoms": ["boot", "hydrogen"],
            "pool_coin_denom": "pool2",
        }
        with mock.patch("extract.paged", return_value=iter([pool])), mock.patch(
            "extract.get", return_value={"balances": []}
        ):
            extract.cmd_pools()
        [written] = self.read_json("pools.json")
        self.assertEqual(written["reserves"], {})
        self.assertIsNone(written["price"]["boot_in_hydrogen"])

    def test_multiple_pools_all_written_in_order(self):
        pools = [
            {"id": "1", "reserve_account_address": "a1", "reserve_coin_denoms": ["boot", "hydrogen"], "pool_coin_denom": "p1"},
            {"id": "2", "reserve_account_address": "a2", "reserve_coin_denoms": ["milliampere", "millivolt"], "pool_coin_denom": "p2"},
        ]
        with mock.patch("extract.paged", return_value=iter(pools)), mock.patch(
            "extract.get", return_value={"balances": []}
        ):
            extract.cmd_pools()
        written = self.read_json("pools.json")
        self.assertEqual([w["id"] for w in written], ["1", "2"])


class BuildManifestTests(unittest.TestCase):
    def test_hashes_and_sizes_match_file_content(self):
        with tempfile.TemporaryDirectory() as d:
            with open(f"{d}/supply.json", "wb") as f:
                f.write(b"content-a")
            man = build_manifest(d)
            self.assertEqual(
                man["files"]["supply.json"]["sha256"],
                hashlib.sha256(b"content-a").hexdigest(),
            )
            self.assertEqual(man["files"]["supply.json"]["bytes"], len(b"content-a"))

    def test_excludes_its_own_output_file(self):
        with tempfile.TemporaryDirectory() as d:
            open(f"{d}/supply.json", "wb").close()
            open(f"{d}/manifest.json", "wb").close()
            man = build_manifest(d)
            self.assertNotIn("manifest.json", man["files"])

    def test_excludes_subdirectories(self):
        with tempfile.TemporaryDirectory() as d:
            open(f"{d}/supply.json", "wb").close()
            os.makedirs(f"{d}/subdir")
            man = build_manifest(d)
            self.assertEqual(list(man["files"]), ["supply.json"])

    def test_file_order_is_sorted_and_deterministic(self):
        with tempfile.TemporaryDirectory() as d:
            for name in ["pubkeys.csv", "balances.json", "supply.json"]:
                open(f"{d}/{name}", "wb").close()
            man = build_manifest(d)
            self.assertEqual(
                list(man["files"]), ["balances.json", "pubkeys.csv", "supply.json"]
            )

    def test_empty_directory_yields_empty_files(self):
        with tempfile.TemporaryDirectory() as d:
            man = build_manifest(d)
            self.assertEqual(man["files"], {})

    def test_fixed_genesis_metadata(self):
        with tempfile.TemporaryDirectory() as d:
            man = build_manifest(d)
            self.assertEqual(man["chain_id"], "bostrom")
            self.assertEqual(man["final_height"], 25120712)


class CmdManifestTests(_OutDirTestCase):
    def test_writes_manifest_json_matching_build_manifest(self):
        with open(f"{self._tmp}/supply.json", "wb") as f:
            f.write(b"x")
        extract.cmd_manifest()
        on_disk = self.read_json("manifest.json")
        self.assertEqual(on_disk, build_manifest(self._tmp))


if __name__ == "__main__":
    unittest.main()
