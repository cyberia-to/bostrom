import unittest
from unittest.mock import patch

import graph_scan
from graph_scan import fetch_window, tx_heights, window_min


class WindowMinTests(unittest.TestCase):
    def test_takes_the_19_block_window_above_lo(self):
        self.assertEqual(window_min(1000, 1), 981)

    def test_clamps_to_lo_near_the_floor(self):
        self.assertEqual(window_min(10, 1), 1)

    def test_exact_boundary_leaves_no_gap(self):
        self.assertEqual(window_min(20, 1), 1)


class TxHeightsTests(unittest.TestCase):
    def test_keeps_only_blocks_with_transactions(self):
        metas = [
            {"header": {"height": "5"}, "num_txs": "0"},
            {"header": {"height": "6"}, "num_txs": "3"},
        ]
        self.assertEqual(tx_heights(metas), ["6"])

    def test_preserves_input_order(self):
        metas = [
            {"header": {"height": "9"}, "num_txs": "1"},
            {"header": {"height": "8"}, "num_txs": "2"},
        ]
        self.assertEqual(tx_heights(metas), ["9", "8"])

    def test_empty_input_yields_empty_output(self):
        self.assertEqual(tx_heights([]), [])


class FetchWindowRetryTests(unittest.TestCase):
    def test_succeeds_on_the_first_attempt(self):
        payload = {"result": {"block_metas": []}}
        with patch.object(graph_scan.json, "load", return_value=payload) as mock_load, \
             patch.object(graph_scan.urllib.request, "urlopen") as mock_urlopen:
            result = fetch_window(1, 20)
        self.assertEqual(result, payload)
        mock_urlopen.assert_called_once()
        mock_load.assert_called_once()

    def test_recovers_after_transient_failures(self):
        payload = {"result": {"block_metas": []}}
        with patch.object(graph_scan.json, "load", side_effect=[Exception("boom"), Exception("boom"), payload]), \
             patch.object(graph_scan.urllib.request, "urlopen"), \
             patch.object(graph_scan.time, "sleep") as mock_sleep:
            result = fetch_window(1, 20)
        self.assertEqual(result, payload)
        self.assertEqual(mock_sleep.call_count, 2)

    def test_gives_up_after_four_failed_attempts(self):
        with patch.object(graph_scan.json, "load", side_effect=Exception("boom")), \
             patch.object(graph_scan.urllib.request, "urlopen"), \
             patch.object(graph_scan.time, "sleep") as mock_sleep:
            result = fetch_window(1, 20)
        self.assertIsNone(result)
        self.assertEqual(mock_sleep.call_count, 4)

    def test_url_carries_the_min_and_max_height(self):
        captured = {}

        def fake_urlopen(url, timeout):
            captured["url"] = url
            captured["timeout"] = timeout
            return None

        with patch.object(graph_scan.urllib.request, "urlopen", side_effect=fake_urlopen), \
             patch.object(graph_scan.json, "load", return_value={"result": {"block_metas": []}}):
            fetch_window(100, 119)
        self.assertEqual(
            captured["url"],
            "http://localhost:26657/blockchain?minHeight=100&maxHeight=119",
        )
        self.assertEqual(captured["timeout"], 25)


if __name__ == "__main__":
    unittest.main()
