import unittest

from graph_scan import find_tx_heights, window_min, next_max_height


class TestFindTxHeights(unittest.TestCase):
    def test_keeps_only_blocks_with_txs(self):
        metas = [
            {"header": {"height": "10"}, "num_txs": "0"},
            {"header": {"height": "11"}, "num_txs": "3"},
            {"header": {"height": "12"}, "num_txs": "0"},
        ]
        self.assertEqual(find_tx_heights(metas), ["11"])

    def test_preserves_order(self):
        metas = [
            {"header": {"height": "5"}, "num_txs": "1"},
            {"header": {"height": "4"}, "num_txs": "2"},
        ]
        self.assertEqual(find_tx_heights(metas), ["5", "4"])

    def test_empty_input(self):
        self.assertEqual(find_tx_heights([]), [])

    def test_num_txs_is_a_string(self):
        metas = [{"header": {"height": "1"}, "num_txs": "0"}]
        self.assertEqual(find_tx_heights(metas), [])


class TestWindowMin(unittest.TestCase):
    def test_full_window(self):
        self.assertEqual(window_min(1, 100), 81)

    def test_clamped_to_lo(self):
        self.assertEqual(window_min(90, 100), 90)

    def test_exact_boundary(self):
        self.assertEqual(window_min(81, 100), 81)

    def test_custom_window(self):
        self.assertEqual(window_min(1, 100, window=5), 95)


class TestNextMaxHeight(unittest.TestCase):
    def test_decrements(self):
        self.assertEqual(next_max_height(50), 49)

    def test_can_go_negative(self):
        self.assertEqual(next_max_height(0), -1)


if __name__ == "__main__":
    unittest.main()
