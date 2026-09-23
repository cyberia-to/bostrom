import base64
import hashlib
import unittest
from unittest import mock

from graph_rebuild import parse_tx_events, work


def ev(type_, **attrs):
    return {"type": type_, "attributes": [{"key": k, "value": v} for k, v in attrs.items()]}


def _block_results(txrs):
    return {"result": {"txs_results": txrs}}


def _block(time_, txs_bytes):
    return {"result": {"block": {
        "header": {"time": time_},
        "data": {"txs": [base64.b64encode(t).decode() for t in txs_bytes]},
    }}}


def _fake_get(block_results=None, block=None):
    def fake(url):
        return block_results if "block_results" in url else block
    return fake


class ParseTxEventsTests(unittest.TestCase):
    def test_single_link(self):
        events = [
            ev("cyberlink", particleFrom="A", particleTo="B"),
            ev("cyberlink", neuron="N"),
        ]
        self.assertEqual(
            parse_tx_events(events, 100, "ts", "TX"),
            [["A", "B", "N", 100, "ts", "TX"]],
        )

    def test_multiple_links_one_neuron(self):
        events = [
            ev("cyberlink", particleFrom="A", particleTo="B"),
            ev("cyberlink", particleFrom="C", particleTo="D"),
            ev("cyberlink", neuron="N"),
        ]
        self.assertEqual(
            parse_tx_events(events, 1, "ts", "TX"),
            [["A", "B", "N", 1, "ts", "TX"], ["C", "D", "N", 1, "ts", "TX"]],
        )

    def test_two_separate_pairs_in_one_tx(self):
        events = [
            ev("cyberlink", particleFrom="A", particleTo="B"),
            ev("cyberlink", neuron="N1"),
            ev("cyberlink", particleFrom="C", particleTo="D"),
            ev("cyberlink", neuron="N2"),
        ]
        self.assertEqual(
            parse_tx_events(events, 1, "ts", "TX"),
            [["A", "B", "N1", 1, "ts", "TX"], ["C", "D", "N2", 1, "ts", "TX"]],
        )

    def test_non_cyberlink_events_ignored(self):
        events = [
            ev("transfer", sender="X"),
            ev("cyberlink", particleFrom="A", particleTo="B"),
            ev("cyberlink", neuron="N"),
            ev("message", action="foo"),
        ]
        self.assertEqual(
            parse_tx_events(events, 1, "ts", "TX"),
            [["A", "B", "N", 1, "ts", "TX"]],
        )

    def test_missing_neuron_event_falls_back_to_empty_string(self):
        events = [ev("cyberlink", particleFrom="A", particleTo="B")]
        self.assertEqual(
            parse_tx_events(events, 1, "ts", "TX"),
            [["A", "B", "", 1, "ts", "TX"]],
        )

    def test_particle_to_missing_is_dropped_not_raised(self):
        # a real malformed-event shape: particleFrom without its particleTo.
        # the pre-fix code did `attrs["particleTo"]` unconditionally and
        # raised KeyError, which would abort an hours-long rebuild.
        events = [
            ev("cyberlink", particleFrom="A"),
            ev("cyberlink", neuron="N"),
        ]
        self.assertEqual(parse_tx_events(events, 1, "ts", "TX"), [])

    def test_particle_from_missing_is_dropped_not_raised(self):
        events = [
            ev("cyberlink", particleTo="B"),
            ev("cyberlink", neuron="N"),
        ]
        self.assertEqual(parse_tx_events(events, 1, "ts", "TX"), [])

    def test_no_events(self):
        self.assertEqual(parse_tx_events([], 1, "ts", "TX"), [])


class WorkTests(unittest.TestCase):
    def test_no_cyberlink_events_returns_ok_without_fetching_the_block(self):
        br = _block_results([{"code": 0, "events": [ev("transfer", sender="X")]}])
        with mock.patch("graph_rebuild.get", side_effect=_fake_get(block_results=br)) as g:
            self.assertEqual(work(100), ("OK", 100, []))
        g.assert_called_once()  # only block_results, block never fetched

    def test_block_results_fetch_failure_reports_fail_br(self):
        with mock.patch("graph_rebuild.get", side_effect=_fake_get(block_results=None)):
            self.assertEqual(work(100), ("FAIL-BR", 100, []))

    def test_block_fetch_failure_after_a_real_cyberlink_reports_fail_b(self):
        br = _block_results([{"code": 0, "events": [ev("cyberlink", particleFrom="A", particleTo="B")]}])
        with mock.patch("graph_rebuild.get", side_effect=_fake_get(block_results=br, block=None)):
            self.assertEqual(work(100), ("FAIL-B", 100, []))

    def test_failed_tx_is_skipped_even_if_it_carries_cyberlink_events(self):
        # code != 0 means the tx reverted; its events (incl. a cyberlink
        # shape) never happened on chain and must not trigger a block fetch
        br = _block_results([{"code": 5, "events": [ev("cyberlink", particleFrom="A", particleTo="B")]}])
        with mock.patch("graph_rebuild.get", side_effect=_fake_get(block_results=br)) as g:
            self.assertEqual(work(100), ("OK", 100, []))
        g.assert_called_once()

    def test_successful_tx_yields_rows_with_computed_hash_and_timestamp(self):
        txb = b"raw-tx-bytes"
        br = _block_results([{"code": 0, "events": [
            ev("cyberlink", particleFrom="A", particleTo="B"),
            ev("cyberlink", neuron="N"),
        ]}])
        b = _block("2021-11-05T13:22:42.000000000Z", [txb])
        with mock.patch("graph_rebuild.get", side_effect=_fake_get(block_results=br, block=b)):
            status, h, rows = work(100)
        expected_hash = hashlib.sha256(txb).hexdigest().upper()
        self.assertEqual(status, "OK")
        self.assertEqual(h, 100)
        self.assertEqual(rows, [["A", "B", "N", 100, "2021-11-05 13:22:42", expected_hash]])

    def test_tx_index_past_the_block_data_gets_empty_hash(self):
        # txs_results can in principle outrun data.txs; the hash falls back
        # to "" rather than indexing out of range
        br = _block_results([{"code": 0, "events": [
            ev("cyberlink", particleFrom="A", particleTo="B"),
            ev("cyberlink", neuron="N"),
        ]}])
        b = _block("2021-11-05T13:22:42.000000000Z", [])  # no tx bytes at all
        with mock.patch("graph_rebuild.get", side_effect=_fake_get(block_results=br, block=b)):
            _, _, rows = work(100)
        self.assertEqual(rows, [["A", "B", "N", 100, "2021-11-05 13:22:42", ""]])


if __name__ == "__main__":
    unittest.main()
