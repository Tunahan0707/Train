import unittest

from PySide6.QtCore import QPointF

from simulation.dc_solver import solve_dc_operating_point
from circuit.netlist import build_netlist


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


class FakeWire:
    component_id = "wire"

    def __init__(self, start, end):
        self.start_point = QPointF(*start)
        self.end_point = QPointF(*end)
        self.position = QPointF(0, 0)

    def mapToScene(self, point):
        return QPointF(point.x() + self.position.x(), point.y() + self.position.y())


class FakeScene:
    def __init__(self, items):
        self._items = items

    def items(self):
        return list(self._items)


class SimulationValidationTests(unittest.TestCase):
    def test_unsupported_component_is_not_silently_ignored(self):
        capacitor = FakeComponent("ac_source", "AC Kaynak V1")
        with self.assertRaisesRegex(ValueError, "fiziksel modeli henüz uygulanmadı"):
            solve_dc_operating_point(FakeScene([capacitor]))

    def test_empty_scene_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "bileşen bulunamadı"):
            solve_dc_operating_point(FakeScene([]))

    def test_wire_stub_does_not_hide_a_dangling_component_terminal(self):
        capacitor = FakeComponent("capacitor", "C1")
        wire = FakeWire((-40, 0), (-20, 0))
        result = build_netlist(FakeScene([capacitor, wire]))
        self.assertEqual(len(result["unconnected_terminals"]), 2)


if __name__ == "__main__":
    unittest.main()
