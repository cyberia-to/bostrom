import unittest

from graph_rebuild import parse_tx_events


def ev(type_, **attrs):
    return {"type": type_, "attributes": [{"key": k, "value": v} for k, v in attrs.items()]}


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

    def test_multiple_links_batched_under_one_neuron_event(self):
        events = [
            ev("cyberlink", particleFrom="A", particleTo="B"),
            ev("cyberlink", particleFrom="C", particleTo="D"),
            ev("cyberlink", neuron="N"),
        ]
        self.assertEqual(
            parse_tx_events(events, 5, "ts", "TX"),
            [["A", "B", "N", 5, "ts", "TX"], ["C", "D", "N", 5, "ts", "TX"]],
        )

    def test_two_link_batches_in_one_tx_get_their_own_neuron(self):
        events = [
            ev("cyberlink", particleFrom="A", particleTo="B"),
            ev("cyberlink", neuron="N1"),
            ev("cyberlink", particleFrom="C", particleTo="D"),
            ev("cyberlink", neuron="N2"),
        ]
        self.assertEqual(
            parse_tx_events(events, 5, "ts", "TX"),
            [["A", "B", "N1", 5, "ts", "TX"], ["C", "D", "N2", 5, "ts", "TX"]],
        )

    def test_non_cyberlink_events_are_ignored(self):
        events = [
            ev("transfer", sender="X", recipient="Y"),
            ev("cyberlink", particleFrom="A", particleTo="B"),
            ev("cyberlink", neuron="N"),
            ev("message", action="cyberlink"),
        ]
        self.assertEqual(
            parse_tx_events(events, 1, "ts", "TX"),
            [["A", "B", "N", 1, "ts", "TX"]],
        )

    def test_neuron_event_missing_falls_back_to_empty_neuron(self):
        # observed shape never expected on-chain, but the parser must not
        # drop the link if the neuron event never arrives
        events = [ev("cyberlink", particleFrom="A", particleTo="B")]
        self.assertEqual(
            parse_tx_events(events, 1, "ts", "TX"),
            [["A", "B", "", 1, "ts", "TX"]],
        )

    def test_neuron_event_with_no_pending_pairs_yields_nothing(self):
        events = [ev("cyberlink", neuron="N")]
        self.assertEqual(parse_tx_events(events, 1, "ts", "TX"), [])

    def test_no_events(self):
        self.assertEqual(parse_tx_events([], 1, "ts", "TX"), [])


if __name__ == "__main__":
    unittest.main()
