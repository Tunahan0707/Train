import unittest

from core.commands import SetNameCommand, SetSwitchStateCommand, SetWiperPositionCommand


class Item:
    def __init__(self):
        self.name = "R1"
        self.closed = False
        self.wiper_position = 0.5
        self.update_count = 0

    def update(self):
        self.update_count += 1


class CommandTests(unittest.TestCase):
    def test_rename_undo_redo(self):
        item = Item()
        command = SetNameCommand(item, "R1", "LOAD")
        command.redo()
        self.assertEqual(item.name, "LOAD")
        command.undo()
        self.assertEqual(item.name, "R1")

    def test_switch_state_undo_redo(self):
        item = Item()
        command = SetSwitchStateCommand(item, False, True)
        command.redo()
        self.assertTrue(item.closed)
        command.undo()
        self.assertFalse(item.closed)

    def test_potentiometer_wiper_undo_redo(self):
        item = Item()
        command = SetWiperPositionCommand(item, 0.5, 0.2)
        command.redo()
        self.assertAlmostEqual(item.wiper_position, 0.2)
        command.undo()
        self.assertAlmostEqual(item.wiper_position, 0.5)


if __name__ == "__main__":
    unittest.main()
