import unittest

from graph_scan import height_ranges


class HeightRangesTests(unittest.TestCase):
    def flatten(self, lo, hi, window):
        heights = []
        for mn, h in height_ranges(lo, hi, window):
            heights.extend(range(mn, h + 1))
        return heights

    def test_covers_every_height_exactly_once_exact_multiple(self):
        # 40 heights, window 20: two full chunks
        heights = self.flatten(1, 40, 20)
        self.assertEqual(sorted(heights), list(range(1, 41)))
        self.assertEqual(len(heights), len(set(heights)))

    def test_covers_every_height_exactly_once_non_multiple(self):
        # 45 heights, window 20: two full chunks + a short final chunk
        heights = self.flatten(1, 45, 20)
        self.assertEqual(sorted(heights), list(range(1, 46)))
        self.assertEqual(len(heights), len(set(heights)))

    def test_lo_not_one(self):
        heights = self.flatten(1000, 1050, 20)
        self.assertEqual(sorted(heights), list(range(1000, 1051)))

    def test_single_height(self):
        self.assertEqual(list(height_ranges(5, 5, 20)), [(5, 5)])

    def test_hi_below_lo_yields_nothing(self):
        self.assertEqual(list(height_ranges(10, 5, 20)), [])

    def test_window_one_yields_one_chunk_per_height(self):
        chunks = list(height_ranges(1, 3, 1))
        self.assertEqual(chunks, [(3, 3), (2, 2), (1, 1)])

    def test_descending_non_overlapping_chunks_at_most_window_wide(self):
        chunks = list(height_ranges(1, 45, 20))
        self.assertEqual(chunks, [(26, 45), (6, 25), (1, 5)])
        for mn, mx in chunks:
            self.assertLessEqual(mx - mn + 1, 20)


if __name__ == "__main__":
    unittest.main()
