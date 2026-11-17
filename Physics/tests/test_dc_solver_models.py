import unittest
from unittest.mock import patch

from simulation.dc_solver import solve_dc_operating_point


class Component:
    def __init__(self, component_id, name, value):
        self.component_id = component_id
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
