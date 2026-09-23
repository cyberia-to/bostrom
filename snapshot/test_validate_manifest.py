import hashlib
import json
import os
import unittest

from validate_manifest import (
    check_file_entries, check_particle_totals, check_coverage_pct,
    check_graph_bijection, validate,
)

GOOD_CID = "QmTsM6YazUmAkz7sNbL1NY88cMciZpiTWHZEDCo3gZVo1h"
GOOD_SHA = hashlib.sha256(b"fixture bytes").hexdigest()


class TestCheckFileEntries(unittest.TestCase):
    def test_well_formed_entry_has_no_problems(self):
        files = {"x.csv": {"cid": GOOD_CID, "sha256": GOOD_SHA, "bytes": 10}}
        self.assertEqual(check_file_entries(files), [])

    def test_short_sha256_is_a_problem(self):
        files = {"x.csv": {"cid": GOOD_CID, "sha256": "deadbeef", "bytes": 10}}
        problems = check_file_entries(files)
        self.assertEqual(len(problems), 1)
        self.assertIn("sha256", problems[0])

    def test_malformed_cid_is_a_problem(self):
        files = {"x.csv": {"cid": "not-a-cid", "sha256": GOOD_SHA, "bytes": 10}}
        problems = check_file_entries(files)
        self.assertEqual(len(problems), 1)
        self.assertIn("cid", problems[0])

    def test_zero_bytes_is_a_problem(self):
        files = {"x.csv": {"cid": GOOD_CID, "sha256": GOOD_SHA, "bytes": 0}}
        problems = check_file_entries(files)
        self.assertEqual(len(problems), 1)
        self.assertIn("bytes", problems[0])


class TestCheckParticleTotals(unittest.TestCase):
    def test_matching_totals_has_no_problems(self):
        m = {"particles_availability": {"available": 90, "missing": 10},
             "graph": {"restored_particles": 100}}
        self.assertEqual(check_particle_totals(m), [])

    def test_mismatched_totals_is_a_problem(self):
        m = {"particles_availability": {"available": 90, "missing": 10},
             "graph": {"restored_particles": 102}}
        problems = check_particle_totals(m)
        self.assertEqual(len(problems), 1)
        self.assertIn("off by -2", problems[0])


class TestCheckCoveragePct(unittest.TestCase):
    def test_matching_pct_has_no_problems(self):
        m = {"particles_availability": {"available": 90, "missing": 10, "coverage_pct": 90.0}}
        self.assertEqual(check_coverage_pct(m), [])

    def test_wrong_pct_is_a_problem(self):
        m = {"particles_availability": {"available": 90, "missing": 10, "coverage_pct": 50.0}}
        problems = check_coverage_pct(m)
        self.assertEqual(len(problems), 1)


class TestCheckGraphBijection(unittest.TestCase):
    def test_matching_counts_has_no_problems(self):
        m = {"graph": {"onchain_cyberlinks": 5, "restored_cyberlinks": 5,
                        "onchain_particles": 7, "restored_particles": 7}}
        self.assertEqual(check_graph_bijection(m), [])

    def test_mismatched_link_count_is_a_problem(self):
        m = {"graph": {"onchain_cyberlinks": 5, "restored_cyberlinks": 4,
                        "onchain_particles": 7, "restored_particles": 7}}
        problems = check_graph_bijection(m)
        self.assertEqual(len(problems), 1)
        self.assertIn("onchain_cyberlinks", problems[0])


class TestRealManifest(unittest.TestCase):
    """Pins the manifest's current, known state so a real fix or a real
    regression is the only thing that changes this test's result."""

    def test_known_particle_count_mismatch(self):
        here = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(here, "manifest.json")) as f:
            manifest = json.load(f)
        problems = validate(manifest)
        self.assertEqual(
            problems,
            ["particles_availability.available + missing = 3143648, "
             "graph.restored_particles = 3143650 (off by -2)"],
        )


if __name__ == "__main__":
    unittest.main()
