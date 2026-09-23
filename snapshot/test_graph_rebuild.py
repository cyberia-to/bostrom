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


if __name__ == "__main__":
    unittest.main()
