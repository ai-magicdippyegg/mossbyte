import unittest

from mossbyte import Terrarium


class TerrariumTests(unittest.TestCase):
    def test_same_seed_produces_same_world(self):
        first = Terrarium(width=30, height=10, seed=412)
        second = Terrarium(width=30, height=10, seed=412)

        for _ in range(25):
            first.step()
            second.step()

        self.assertEqual(first.grid, second.grid)
        self.assertEqual(first.moisture, second.moisture)
        self.assertEqual(first.render(color=False), second.render(color=False))

    def test_different_seeds_can_make_different_worlds(self):
        first = Terrarium(width=30, height=10, seed=1)
        second = Terrarium(width=30, height=10, seed=2)
        self.assertNotEqual(first.grid, second.grid)

    def test_every_step_preserves_world_dimensions(self):
        garden = Terrarium(width=24, height=8, seed=99)

        for _ in range(40):
            garden.step()
            self.assertEqual(len(garden.grid), 8)
            self.assertTrue(all(len(row) == 24 for row in garden.grid))
            self.assertTrue(all(len(row) == 24 for row in garden.moisture))
            self.assertTrue(all(0 <= value <= 100 for row in garden.moisture for value in row))

    def test_stats_cover_every_cell(self):
        garden = Terrarium(width=20, height=7, seed=7)
        stats = garden.stats()
        total = stats["empty"] + stats["moss"] + stats["fern"] + stats["bloom"] + stats["stone"]
        self.assertEqual(total, 20 * 7)
        self.assertIn("humidity", stats)

    def test_render_supports_ascii_and_unicode(self):
        garden = Terrarium(width=20, height=7, seed=18)
        unicode_frame = garden.render(color=False)
        ascii_frame = garden.render(color=False, ascii_only=True)

        self.assertIn("MOSSBYTE", unicode_frame)
        self.assertIn("MOSSBYTE", ascii_frame)
        self.assertIn("Y", ascii_frame)
        self.assertNotIn("\033[", ascii_frame)

    def test_small_world_is_rejected(self):
        with self.assertRaises(ValueError):
            Terrarium(width=5, height=5)


if __name__ == "__main__":
    unittest.main()
