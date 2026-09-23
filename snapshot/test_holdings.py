import unittest

from holdings import clean, denom_label, pool_rate, compose_rates, compose_account_holdings, MIN_RESERVE


class CleanTests(unittest.TestCase):
    def test_known_base_denom(self):
        self.assertEqual(clean("boot"), "BOOT")
        self.assertEqual(clean("liquidpussy"), "LP-PUSSY")

    def test_u_prefixed_denom_uppercased(self):
        self.assertEqual(clean("uatom"), "ATOM")

    def test_erc20_gravity_bridge(self):
        self.assertEqual(clean("gravity0x1234567890abcdef"), "ERC20:cdef")
        self.assertEqual(clean("0x1234567890abcdef"), "ERC20:cdef")

    def test_unknown_base_truncated_to_ten(self):
        self.assertEqual(clean("someverylongbasedenom"), "someverylo")


class DenomLabelTests(unittest.TestCase):
    def test_core_denom(self):
        self.assertEqual(denom_label("boot", {}), "BOOT")
        self.assertEqual(denom_label("milliampere", {}), "A")

    def test_ibc_denom_resolves_through_trace(self):
        ibc = {"ibc/AAAA": "uatom"}
        self.assertEqual(denom_label("ibc/AAAA", ibc), "ATOM")

    def test_ibc_denom_without_trace_falls_back_to_hash_prefix(self):
        self.assertEqual(denom_label("ibc/1234567890", {}), "ibc:123456")

    def test_factory_denom_labeled_lp(self):
        self.assertEqual(denom_label("factory/bostrom1abc/poolcoin", {}), "LP")

    def test_unknown_denom_truncated_to_twelve(self):
        self.assertEqual(denom_label("someverylongdenomname", {}), "someverylong")


class PoolRateTests(unittest.TestCase):
    def test_rate_is_want_over_other(self):
        p = {"reserves": {"boot": 4_000_000, "hydrogen": 2_000_000}}
        self.assertEqual(pool_rate(p, "boot", "hydrogen"), 2.0)

    def test_below_min_reserve_returns_none(self):
        p = {"reserves": {"boot": MIN_RESERVE - 1, "hydrogen": 2_000_000}}
        self.assertIsNone(pool_rate(p, "boot", "hydrogen"))

    def test_missing_denom_treated_as_zero_reserve(self):
        p = {"reserves": {"boot": 2_000_000}}
        self.assertIsNone(pool_rate(p, "boot", "hydrogen"))


class ComposeRatesTests(unittest.TestCase):
    def test_direct_boot_pool_wins_over_hydrogen_route(self):
        pools = {
            "lp-bh": {"denoms": ["boot", "hydrogen"], "reserves": {"boot": 2_000_000, "hydrogen": 4_000_000}},
            "lp-bx": {"denoms": ["boot", "x"], "reserves": {"boot": 10_000_000, "x": 5_000_000}},
            "lp-hx": {"denoms": ["hydrogen", "x"], "reserves": {"hydrogen": 1_000_000, "x": 1_000_000}},
        }
        rates = compose_rates(pools)
        self.assertEqual(rates["hydrogen"], 0.5)
        # the direct boot/x pool (2.0) is set before the hydrogen route is ever tried
        self.assertEqual(rates["x"], 2.0)

    def test_hydrogen_routed_when_no_direct_boot_pool(self):
        pools = {
            "lp-bh": {"denoms": ["boot", "hydrogen"], "reserves": {"boot": 2_000_000, "hydrogen": 4_000_000}},
            "lp-hx": {"denoms": ["hydrogen", "x"], "reserves": {"hydrogen": 1_000_000, "x": 2_000_000}},
        }
        rates = compose_rates(pools)
        # hydrogen = 0.5 boot; x = 0.5 hydrogen per unit x, routed: 0.5 * 0.5 = 0.25
        self.assertEqual(rates["hydrogen"], 0.5)
        self.assertEqual(rates["x"], 0.25)

    def test_dust_pool_below_min_reserve_quotes_zero_not_none(self):
        # pool_rate(p, ...) returns None for a dust pool, but compose_rates
        # folds that into 0.0 via `or 0.0` rather than leaving the denom
        # unquoted — a zero rate, not a missing one.
        pools = {"lp-bx": {"denoms": ["boot", "x"], "reserves": {"boot": 1, "x": 1}}}
        rates = compose_rates(pools)
        self.assertEqual(rates["x"], 0.0)

    def test_no_pools_leaves_only_boot(self):
        self.assertEqual(compose_rates({}), {"boot": 1.0, "hydrogen": 0.0})


class ComposeAccountHoldingsTests(unittest.TestCase):
    def label(self, d):
        return d.upper()

    def test_plain_liquid_leg(self):
        rec = compose_account_holdings({"boot": 5}, {}, 0, 0, self.label)
        self.assertEqual(rec, {"boot": {"label": "BOOT", "liquid": 5, "delegated": 0,
                                         "undelegating": 0, "pools": {}, "total": 5}})

    def test_pool_coin_decomposes_pro_rata_into_reserve_denoms(self):
        # holding half the pool-coin supply claims half of each reserve
        pools = {"lp-bh": {"id": "1", "denoms": ["boot", "hydrogen"],
                            "reserves": {"boot": 100, "hydrogen": 200}, "supply": 10}}
        rec = compose_account_holdings({"lp-bh": 5}, pools, 0, 0, self.label)
        self.assertEqual(rec["boot"]["pools"], {"1": 50})
        self.assertEqual(rec["hydrogen"]["pools"], {"1": 100})
        self.assertEqual(rec["boot"]["total"], 50)

    def test_pool_coin_with_zero_supply_contributes_nothing(self):
        pools = {"lp-bh": {"id": "1", "denoms": ["boot", "hydrogen"],
                            "reserves": {"boot": 100, "hydrogen": 200}, "supply": 0}}
        rec = compose_account_holdings({"lp-bh": 5}, pools, 0, 0, self.label)
        self.assertEqual(rec, {})

    def test_delegated_and_undelegating_join_the_boot_leg(self):
        rec = compose_account_holdings({}, {}, 30, 7, self.label)
        self.assertEqual(rec["boot"], {"label": "BOOT", "liquid": 0, "delegated": 30,
                                        "undelegating": 7, "pools": {}, "total": 37})

    def test_pool_leg_and_delegated_boot_accumulate_in_the_same_bucket(self):
        pools = {"lp-bx": {"id": "1", "denoms": ["boot", "x"],
                            "reserves": {"boot": 100, "x": 50}, "supply": 10}}
        rec = compose_account_holdings({"lp-bx": 2}, pools, 30, 0, self.label)
        self.assertEqual(rec["boot"]["pools"], {"1": 20})
        self.assertEqual(rec["boot"]["delegated"], 30)
        self.assertEqual(rec["boot"]["total"], 50)

    def test_zero_total_denom_is_dropped(self):
        rec = compose_account_holdings({"boot": 0}, {}, 0, 0, self.label)
        self.assertEqual(rec, {})

    def test_empty_input_yields_empty_record(self):
        self.assertEqual(compose_account_holdings({}, {}, 0, 0, self.label), {})


if __name__ == "__main__":
    unittest.main()
