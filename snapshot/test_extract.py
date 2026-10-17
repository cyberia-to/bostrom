import csv
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

    def read_jsonl(self, name):
        with open(os.path.join(self._tmp, name)) as f:
            return [json.loads(line) for line in f if line.strip()]

    def read_csv(self, name):
        with open(os.path.join(self._tmp, name), newline="") as f:
            return list(csv.reader(f))


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
