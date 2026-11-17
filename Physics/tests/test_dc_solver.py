import unittest

from simulation.dc_solver import gaussian_solve, parse_engineering_value


class EngineeringValueTests(unittest.TestCase):
    def test_metric_suffixes(self):
        cases = {"1000 Ω": 1000.0, "4.7kΩ": 4700.0, "2.2uF": 2.2e-6, "3m": 3e-3, "1meg": 1e6}
        for source, expected in cases.items():
            with self.subTest(source=source):
                self.assertAlmostEqual(parse_engineering_value(source), expected)

    def test_rejects_invalid_and_infinite_values(self):
        for source in ("", "abc", "1k2", "1e999"):
            with self.subTest(source=source):
                with self.assertRaises(ValueError):
                    parse_engineering_value(source)


class LinearSolverTests(unittest.TestCase):
    def test_solves_linear_system(self):
        result = gaussian_solve([[2, 1], [1, 3]], [5, 6])
        self.assertAlmostEqual(result[0], 1.8)
        self.assertAlmostEqual(result[1], 1.4)

    def test_rejects_non_square_matrix(self):
        with self.assertRaises(ValueError):
            gaussian_solve([[1, 2]], [3])

    def test_rejects_singular_matrix(self):
        with self.assertRaises(ValueError):
            gaussian_solve([[1, 2], [2, 4]], [3, 6])


if __name__ == "__main__":
    unittest.main()
