import base64
import hashlib
import unittest
from unittest.mock import patch

import graph_rebuild
from graph_rebuild import work


def cyberlink_event(**attrs):
    return {"type": "cyberlink", "attributes": [{"key": k, "value": v} for k, v in attrs.items()]}


def block_results(txs_results):
    return {"result": {"txs_results": txs_results}}


def block(time_str, txs_b64):
    return {"result": {"block": {"header": {"time": time_str}, "data": {"txs": txs_b64}}}}


class WorkDispatchTests(unittest.TestCase):
    def test_block_results_fetch_failure_short_circuits(self):
        with patch.object(graph_rebuild, "get", return_value=None) as mock_get:
            status, h, rows = work(100)
        self.assertEqual((status, h, rows), ("FAIL-BR", 100, []))
        mock_get.assert_called_once_with("http://localhost:26657/block_results?height=100")

    def test_no_cyberlink_events_skips_the_block_fetch(self):
        br = block_results([{"code": 0, "events": [{"type": "transfer", "attributes": []}]}])
        with patch.object(graph_rebuild, "get", return_value=br) as mock_get:
            status, h, rows = work(200)
        self.assertEqual((status, h, rows), ("OK", 200, []))
        mock_get.assert_called_once()

    def test_failed_txs_results_entries_carry_no_events_and_are_ignored(self):
        br = block_results([{"code": 0}])
        with patch.object(graph_rebuild, "get", return_value=br) as mock_get:
            status, h, rows = work(201)
        self.assertEqual((status, h, rows), ("OK", 201, []))
        mock_get.assert_called_once()

    def test_block_fetch_failure_after_a_cyberlink_event_is_seen(self):
        br = block_results([{"code": 0, "events": [cyberlink_event(particleFrom="A", particleTo="B")]}])

        def side_effect(url):
            return br if "block_results" in url else None

        with patch.object(graph_rebuild, "get", side_effect=side_effect) as mock_get:
            status, h, rows = work(300)
        self.assertEqual((status, h, rows), ("FAIL-B", 300, []))
        self.assertEqual(mock_get.call_count, 2)

    def test_full_dispatch_pairs_events_and_computes_tx_hash(self):
        tx_bytes = b"a real tx"
        tx_b64 = base64.b64encode(tx_bytes).decode()
        expected_hash = hashlib.sha256(tx_bytes).hexdigest().upper()

        br = block_results(
            [
                {
                    "code": 0,
                    "events": [
                        cyberlink_event(particleFrom="A", particleTo="B"),
                        cyberlink_event(neuron="N"),
                    ],
                }
            ]
        )
        b = block("2021-11-05T13:22:42.000000000Z", [tx_b64])

        def side_effect(url):
            return br if "block_results" in url else b

        with patch.object(graph_rebuild, "get", side_effect=side_effect):
            status, h, rows = work(400)

        self.assertEqual(status, "OK")
        self.assertEqual(h, 400)
        self.assertEqual(rows, [["A", "B", "N", 400, "2021-11-05 13:22:42", expected_hash]])

    def test_failed_tx_within_a_successful_block_is_skipped(self):
        br = block_results(
            [
                {"code": 11, "events": [cyberlink_event(particleFrom="A", particleTo="B"), cyberlink_event(neuron="N")]},
                {"code": 0, "events": [cyberlink_event(particleFrom="C", particleTo="D"), cyberlink_event(neuron="N")]},
            ]
        )
        b = block("2021-11-05T13:22:42.000000000Z", [base64.b64encode(b"tx0").decode(), base64.b64encode(b"tx1").decode()])

        def side_effect(url):
            return br if "block_results" in url else b

        with patch.object(graph_rebuild, "get", side_effect=side_effect):
            status, h, rows = work(500)

        self.assertEqual(status, "OK")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][:3], ["C", "D", "N"])

    def test_tx_index_beyond_the_block_txs_array_gets_an_empty_hash(self):
        br = block_results(
            [{"code": 0, "events": [cyberlink_event(particleFrom="A", particleTo="B"), cyberlink_event(neuron="N")]}]
        )
        b = block("2021-11-05T13:22:42.000000000Z", [])

        def side_effect(url):
            return br if "block_results" in url else b

        with patch.object(graph_rebuild, "get", side_effect=side_effect):
            status, h, rows = work(600)

        self.assertEqual(status, "OK")
        self.assertEqual(rows, [["A", "B", "N", 600, "2021-11-05 13:22:42", ""]])

    def test_pending_pairs_without_a_trailing_neuron_event_get_an_empty_neuron(self):
        br = block_results(
            [{"code": 0, "events": [cyberlink_event(particleFrom="A", particleTo="B")]}]
        )
        b = block("2021-11-05T13:22:42.000000000Z", [base64.b64encode(b"tx0").decode()])

        def side_effect(url):
            return br if "block_results" in url else b

        with patch.object(graph_rebuild, "get", side_effect=side_effect):
            status, h, rows = work(700)

        self.assertEqual(status, "OK")
        self.assertEqual(rows[0][:3], ["A", "B", ""])


if __name__ == "__main__":
    unittest.main()
