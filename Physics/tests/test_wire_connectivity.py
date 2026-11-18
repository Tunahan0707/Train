import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QPointF
from PySide6.QtWidgets import QApplication, QGraphicsScene

from circuit.netlist import build_netlist
from components.wire import WireItem
from components.resistor import Resistor
from interface.workspace import Workspace


class PinComponent:
    component_id = "test_component"

    def __init__(self, x, y, name):
        self.x = x
        self.y = y
        self.name = name

    def terminal_positions(self):
        return [(0, 0)]

    def terminal_names(self):
        return ["P"]

    def mapToScene(self, point):
        return QPointF(point.x() + self.x, point.y() + self.y)


class WireConnectivityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_moved_wire_connects_using_its_scene_position(self):
        scene = QGraphicsScene()
        first = PinComponent(50, 50, "X1")
        second = PinComponent(150, 50, "X2")
        wire = WireItem((0, 0), (100, 0))
        wire.setPos(50, 50)
        scene.addItem(wire)
        # The fake pins are supplied through a small scene adapter because
        # QGraphicsScene owns only QGraphicsItems.
        class SceneAdapter:
            def items(self):
                return [first, second, wire]
        result = build_netlist(SceneAdapter())
        self.assertEqual(result["component_nodes"][first][0], result["component_nodes"][second][0])
        self.assertEqual(result["unconnected_terminals"], [])

    def test_wire_tool_snaps_to_component_terminals(self):
        workspace = Workspace()
        resistor = Resistor()
        workspace.circuit_scene.addItem(resistor)
        snapped = workspace._snap_wire_point(QPointF(-35, 0))
        self.assertEqual(snapped, QPointF(-40, 0))
        workspace.deleteLater()

    def test_selecting_wire_tool_enters_drawing_mode_instead_of_adding_stub(self):
        workspace = Workspace()
        self.assertTrue(workspace.add_component("wire"))
        self.assertTrue(workspace.wire_mode)
        self.assertEqual(workspace.circuit_scene.items(), [])
        workspace.cancel_wire_mode()
        workspace.deleteLater()

    def test_wire_remains_at_origin_by_default(self):
        wire = WireItem((10, 20), (40, 20))
        self.assertEqual(wire.pos(), QPointF(0, 0))
        self.assertEqual(wire.scene_start_point(), QPointF(10, 20))


if __name__ == "__main__":
    unittest.main()
