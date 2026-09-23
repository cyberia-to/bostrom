import unittest

from holdings import (
    clean, build_ibc_map, denom_label, pool_rate, compute_rates,
    compose_liquid, compose_pools, compose_delegated_undelegating,
    build_holdings_record,
)


class TestClean(unittest.TestCase):
    def test_known_denom(self):
        self.assertEqual(clean("pussy"), "PUSSY")

    def test_u_prefixed_alpha(self):
        self.assertEqual(clean("uatom"), "ATOM")

    def test_gravity_erc20(self):
        self.assertEqual(clean("gravity0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"), "ERC20:eB48")

    def test_fallback_truncated(self):
        self.assertEqual(clean("somestrangelongdenom"), "somestrangelongdenom"[:10])


class TestIbcMap(unittest.TestCase):
    def test_builds_hash_to_base(self):
        traces = [{"path": "transfer/channel-0", "base_denom": "uatom"}]
        ibc = build_ibc_map(traces)
        self.assertEqual(len(ibc), 1)
        h, base = next(iter(ibc.items()))
        self.assertTrue(h.startswith("ibc/"))
        self.assertEqual(base, "uatom")


class TestDenomLabel(unittest.TestCase):
    def test_core_denom(self):
        self.assertEqual(denom_label("boot", {}), "BOOT")

    def test_ibc_denom_resolved(self):
        ibc = {"ibc/ABCDEF": "uatom"}
        self.assertEqual(denom_label("ibc/ABCDEF", ibc), "ATOM")

    def test_unresolved_ibc_denom(self):
        self.assertEqual(denom_label("ibc/DEADBEEF00", {}), "ibc:" + "ibc/DEADBEEF00"[4:10])

    def test_factory_denom(self):
        self.assertEqual(denom_label("factory/addr/foo", {}), "LP")

    def test_unknown_denom_truncated(self):
        self.assertEqual(denom_label("someveryraredenom", {}), "someveryraredenom"[:12])


class TestPoolRate(unittest.TestCase):
    def test_rate_below_min_reserve_is_none(self):
        p = {"reserves": {"boot": 100, "hydrogen": 100}}
        self.assertIsNone(pool_rate(p, "boot", "hydrogen"))

    def test_rate_computed_when_above_min(self):
        p = {"reserves": {"boot": 4_000_000, "hydrogen": 2_000_000}}
        self.assertEqual(pool_rate(p, "boot", "hydrogen"), 2.0)


class TestComputeRates(unittest.TestCase):
    def test_direct_boot_pool_wins_over_hydrogen_route(self):
        pools = {
            "pool1": {"denoms": ["boot", "hydrogen"], "reserves": {"boot": 2_000_000, "hydrogen": 1_000_000}},
            "pool2": {"denoms": ["boot", "atom"], "reserves": {"boot": 3_000_000, "atom": 1_000_000}},
        }
        rates = compute_rates(pools)
        self.assertEqual(rates["hydrogen"], 2.0)
        self.assertEqual(rates["atom"], 3.0)

    def test_hydrogen_routed_denom(self):
        pools = {
            "pool1": {"denoms": ["boot", "hydrogen"], "reserves": {"boot": 2_000_000, "hydrogen": 1_000_000}},
            "pool2": {"denoms": ["hydrogen", "milliampere"], "reserves": {"hydrogen": 1_000_000, "milliampere": 2_000_000}},
        }
        rates = compute_rates(pools)
        self.assertEqual(rates["hydrogen"], 2.0)
        self.assertEqual(rates["milliampere"], 1.0)

    def test_dust_pool_yields_zero_rate(self):
        pools = {"pool1": {"denoms": ["boot", "hydrogen"], "reserves": {"boot": 10, "hydrogen": 10}}}
        rates = compute_rates(pools)
        self.assertEqual(rates["hydrogen"], 0.0)


class TestComposeLiquid(unittest.TestCase):
    def test_builds_address_to_coin_map(self):
        balances = [{"address": "addr1", "coins": [{"denom": "boot", "amount": "100"}]}]
        liquid = compose_liquid(balances)
        self.assertEqual(liquid, {"addr1": {"boot": 100}})


class TestComposePools(unittest.TestCase):
    def test_builds_pool_reserves_from_liquid(self):
        liquid = {"reserve_acc": {"boot": 1000, "hydrogen": 500}}
        pool_records = [{
            "pool": {"id": 1, "pool_coin_denom": "pool1-lp", "reserve_account_address": "reserve_acc",
                     "reserve_coin_denoms": ["boot", "hydrogen"]},
            "pool_metadata": {"pool_coin_total_supply": {"amount": "1000000"}},
        }]
        pools = compose_pools(pool_records, liquid)
        self.assertEqual(pools["pool1-lp"]["reserves"], {"boot": 1000, "hydrogen": 500})
        self.assertEqual(pools["pool1-lp"]["supply"], 1000000)


class TestDelegatedUndelegating(unittest.TestCase):
    def test_delegation_converted_to_boot_by_share_ratio(self):
        validators = [{"operator_address": "val1", "tokens": "1000", "delegator_shares": "1000.0"}]
        delegations = [{"validator_address": "val1", "delegator_address": "addr1", "shares": "500.0"}]
        delegated, undel = compose_delegated_undelegating(validators, delegations, [])
        self.assertEqual(delegated["addr1"], 500)
        self.assertEqual(undel, {})

    def test_unbonding_sums_entries(self):
        unbonding = [{"delegator_address": "addr1", "entries": [{"balance": "10"}, {"balance": "20"}]}]
        delegated, undel = compose_delegated_undelegating([], [], unbonding)
        self.assertEqual(undel["addr1"], 30)


class TestBuildHoldingsRecord(unittest.TestCase):
    def test_liquid_only(self):
        rec = build_holdings_record("addr1", {"addr1": {"boot": 100}}, {}, {}, {}, {})
        self.assertEqual(rec["boot"]["total"], 100)
        self.assertEqual(rec["boot"]["label"], "BOOT")

    def test_lp_token_decomposed_into_reserves(self):
        liquid = {"addr1": {"pool1-lp": 100}}
        pools = {"pool1-lp": {"id": 1, "denoms": ["boot", "hydrogen"],
                               "reserves": {"boot": 1000, "hydrogen": 500}, "supply": 1000}}
        rec = build_holdings_record("addr1", liquid, {}, {}, pools, {})
        self.assertEqual(rec["boot"]["pools"][1], 100)
        self.assertEqual(rec["hydrogen"]["pools"][1], 50)

    def test_delegated_and_undelegating_bucketed_under_boot(self):
        rec = build_holdings_record("addr1", {}, {"addr1": 500}, {"addr1": 200}, {}, {})
        self.assertEqual(rec["boot"]["delegated"], 500)
        self.assertEqual(rec["boot"]["undelegating"], 200)

    def test_empty_holdings_returns_none(self):
        rec = build_holdings_record("addr1", {}, {}, {}, {}, {})
        self.assertIsNone(rec)


if __name__ == "__main__":
    unittest.main()
