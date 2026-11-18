import json
import tempfile
import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from pathlib import Path

from PySide6.QtWidgets import QApplication, QGraphicsScene

from components.basic import BasicComponent
from components.resistor import Resistor
from components.wire import WireItem
from core.project_io import load_circuit, save_circuit, load_project, save_project


class ProjectIOTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_component_names_and_values_round_trip(self):
        scene = QGraphicsScene()
        resistor = Resistor()
        resistor.name = "R_LOAD"
        resistor.set_value("4.7k")
        resistor.setPos(120, -40)
        capacitor = BasicComponent("capacitor")
        capacitor.name = "C_FILTER"
        capacitor.set_value("22u")
        capacitor.setPos(-80, 30)
        wire = WireItem((0, 0), (40, 0))
        wire.setPos(30, 70)
        scene.addItem(resistor)
        scene.addItem(capacitor)
        scene.addItem(wire)

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "test.physics"
            save_circuit(scene, path, "Power supply")
            loaded = QGraphicsScene()
            loaded_name = load_circuit(loaded, path)

        by_type = {item.component_id: item for item in loaded.items()}
        self.assertEqual(loaded_name, "Power supply")
        loaded_wire = next(item for item in loaded.items() if item.component_id == "wire")
        self.assertEqual(loaded_wire.instance_id, wire.instance_id)
        self.assertEqual(loaded_wire.pos().x(), 30)
        self.assertEqual(loaded_wire.pos().y(), 70)
        self.assertEqual(by_type["resistor"].instance_id, resistor.instance_id)
        self.assertEqual(by_type["capacitor"].instance_id, capacitor.instance_id)
        self.assertEqual(by_type["resistor"].name, "R_LOAD")
        self.assertEqual(by_type["resistor"].value, "4.7k")
        self.assertEqual(by_type["capacitor"].name, "C_FILTER")
        self.assertEqual(by_type["capacitor"].value, "22u")
        self.assertEqual(by_type["resistor"].pos().x(), 120)

    def test_multi_circuit_project_round_trip(self):
        first_scene = QGraphicsScene()
        first_item = Resistor()
        first_item.name = "R_MAIN"
        first_scene.addItem(first_item)
        second_scene = QGraphicsScene()
        second_item = BasicComponent("voltage_source")
        second_item.name = "V_AUX"
        second_scene.addItem(second_item)
        first_id = "0d85a6a7-4d74-44c1-86a0-3e9caa1305a1"
        second_id = "e7f5e740-8b16-42e5-9a2f-f0f6f60ec1e1"

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "multi.physics"
            save_project([
                {"id": first_id, "name": "Ana devre", "scene": first_scene},
                {"id": second_id, "name": "Yardımcı", "scene": second_scene},
            ], path, second_id)
            project = load_project(path)

        self.assertEqual(project["active_circuit_id"], second_id)
        self.assertEqual([entry["name"] for entry in project["circuits"]], ["Ana devre", "Yardımcı"])
        self.assertEqual(project["circuits"][0]["items"][0].instance_id, first_item.instance_id)
        self.assertEqual(project["circuits"][1]["items"][0].name, "V_AUX")

    def test_single_circuit_file_opens_as_one_circuit_project(self):
        scene = QGraphicsScene()
        scene.addItem(Resistor())
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "legacy_single.physics"
            save_circuit(scene, path, "Legacy single")
            project = load_project(path)
        self.assertEqual(len(project["circuits"]), 1)
        self.assertEqual(project["circuits"][0]["name"], "Legacy single")

    def test_version_one_projects_remain_loadable(self):
        legacy = {
            "format": "physics-circuit",
            "version": 1,
            "components": [{"type": "resistor", "x": 5, "y": 8, "value": "220"}],
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "legacy.physics"
            path.write_text(json.dumps(legacy), encoding="utf-8")
            scene = QGraphicsScene()
            load_circuit(scene, path)
        item = scene.items()[0]
        self.assertEqual(item.component_id, "resistor")
        self.assertEqual(item.value, "220")
        self.assertEqual(item.name, "Direnç")

    def test_unknown_component_type_is_rejected_without_clearing_scene(self):
        invalid = {
            "format": "physics-circuit",
            "version": 2,
            "components": [{"type": "unknown_device"}],
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "invalid.physics"
            path.write_text(json.dumps(invalid), encoding="utf-8")
            scene = QGraphicsScene()
            existing = Resistor()
            scene.addItem(existing)
            with self.assertRaisesRegex(ValueError, "Desteklenmeyen bileşen türü"):
                load_circuit(scene, path)
            self.assertEqual(scene.items(), [existing])


if __name__ == "__main__":
    unittest.main()
