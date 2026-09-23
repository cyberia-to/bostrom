import unittest

from extract import is_extra_denom, pool_price, resolve_base_account


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


if __name__ == "__main__":
    unittest.main()
