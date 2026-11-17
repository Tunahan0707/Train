import unittest

from PySide6.QtCore import QPointF

from simulation.dc_solver import solve_dc_operating_point


class FakeComponent:
    def __init__(self, component_id, name):
        self.component_id = component_id
        self.name = name
        self.value = "10uF"

    def terminal_positions(self):
        return [(-40, 0), (40, 0)]

    def terminal_names(self):
        return ["Uç 1", "Uç 2"]

    def mapToScene(self, point):
        return QPointF(point)


class FakeScene:
    def __init__(self, items):
        self._items = items

    def items(self):
        return list(self._items)


class SimulationValidationTests(unittest.TestCase):
    def test_unsupported_component_is_not_silently_ignored(self):
        capacitor = FakeComponent("capacitor", "Kondansatör C1")
        with self.assertRaisesRegex(ValueError, "fiziksel modeli henüz uygulanmadı"):
            solve_dc_operating_point(FakeScene([capacitor]))

    def test_empty_scene_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "bileşen bulunamadı"):
            solve_dc_operating_point(FakeScene([]))


if __name__ == "__main__":
    unittest.main()
