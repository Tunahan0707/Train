import unittest
from unittest.mock import patch

from simulation.dc_solver import solve_dc_operating_point


class Component:
    def __init__(self, component_id, name, value):
        self.component_id = component_id
        self.instance_id = f"id-{component_id}-{name}"
        self.name = name
        self.value = value


class DCSolverModelTests(unittest.TestCase):
    def test_capacitor_open_and_inductor_short_in_dc_steady_state(self):
        source = Component("voltage_source", "V1", "5")
        inductor = Component("inductor", "L1", "10m")
        resistor = Component("resistor", "R1", "1k")
        capacitor = Component("capacitor", "C1", "100u")
        topology = {
            "component_nodes": {
                source: [1, 0],
                inductor: [1, 2],
                resistor: [2, 0],
                capacitor: [1, 0],
            },
            "ground_nodes": [0],
            "unconnected_terminals": [],
        }
        with patch("simulation.dc_solver.build_netlist", return_value=topology):
            result = solve_dc_operating_point(object())

        self.assertAlmostEqual(result["node_voltages"][1], 5.0, places=9)
        self.assertAlmostEqual(result["node_voltages"][2], 5.0, places=9)
        self.assertAlmostEqual(result["resistors"][0]["current"], 0.005, places=9)
        self.assertAlmostEqual(result["inductors"][0]["current"], 0.005, places=9)
        self.assertAlmostEqual(result["capacitors"][0]["voltage"], 5.0, places=9)
        self.assertEqual(result["capacitors"][0]["current"], 0.0)

    def test_source_resistor_power_and_current_signs(self):
        source = Component("voltage_source", "V1", "5")
        resistor = Component("resistor", "R1", "1k")
        topology = {
            "component_nodes": {source: [1, 0], resistor: [1, 0]},
            "ground_nodes": [0],
            "unconnected_terminals": [],
        }
        with patch("simulation.dc_solver.build_netlist", return_value=topology):
            result = solve_dc_operating_point(object())
        self.assertAlmostEqual(result["resistors"][0]["current"], 0.005, places=9)
        self.assertAlmostEqual(result["resistors"][0]["power"], 0.025, places=9)
        self.assertAlmostEqual(result["sources"][0]["power_delivered"], 0.025, places=9)
        self.assertAlmostEqual(result["sources"][0]["power_absorbed"], -0.025, places=9)
        self.assertIn(resistor.instance_id, result["component_measurements"])
        self.assertEqual(result["component_measurements"][resistor.instance_id]["Akım"], "0.005 A")

    def test_forward_diode_uses_piecewise_linear_model(self):
        source = Component("voltage_source", "V1", "5")
        resistor = Component("resistor", "R1", "1k")
        diode = Component("diode", "D1", "")
        topology = {
            "component_nodes": {source: [2, 0], resistor: [2, 1], diode: [1, 0]},
            "ground_nodes": [0],
            "unconnected_terminals": [],
        }
        with patch("simulation.dc_solver.build_netlist", return_value=topology):
            result = solve_dc_operating_point(object())
        diode_result = result["diodes"][0]
        self.assertTrue(diode_result["conducting"])
        self.assertAlmostEqual(diode_result["voltage"], 0.7 + 0.01 * diode_result["current"], places=8)
        self.assertAlmostEqual(diode_result["current"], 4.3 / 1000.01, places=8)

    def test_reverse_diode_stays_off(self):
        source = Component("voltage_source", "V1", "5")
        resistor = Component("resistor", "R1", "1k")
        diode = Component("diode", "D1", "")
        topology = {
            "component_nodes": {source: [2, 0], resistor: [2, 1], diode: [0, 1]},
            "ground_nodes": [0],
            "unconnected_terminals": [],
        }
        with patch("simulation.dc_solver.build_netlist", return_value=topology):
            result = solve_dc_operating_point(object())
        self.assertFalse(result["diodes"][0]["conducting"])
        self.assertAlmostEqual(result["diodes"][0]["current"], 0.0)
        self.assertAlmostEqual(result["resistors"][0]["current"], 0.0, places=9)

    def test_non_positive_reactive_value_is_rejected(self):
        capacitor = Component("capacitor", "C1", "0")
        topology = {
            "component_nodes": {capacitor: [1, 0]},
            "ground_nodes": [0],
            "unconnected_terminals": [],
        }
        with patch("simulation.dc_solver.build_netlist", return_value=topology):
            with self.assertRaisesRegex(ValueError, "sıfırdan büyük"):
                solve_dc_operating_point(object())


if __name__ == "__main__":
    unittest.main()
