
class AddItemCommand:
    def __init__(self, scene, item, position):
        self.scene = scene
        self.item = item
        self.position = position

    def redo(self):
        self.scene.addItem(self.item)
        self.item.setPos(self.position)

    def undo(self):
        self.scene.removeItem(self.item)


class DeleteItemsCommand:
    def __init__(self, scene, items):
        self.scene = scene
        self.items = []

        for item in items:
            self.items.append({
                "item": item,
                "position": item.pos(),
                "selected": item.isSelected(),
            })

    def redo(self):
        for data in self.items:
            self.scene.removeItem(data["item"])

    def undo(self):
        for data in self.items:
            item = data["item"]

            self.scene.addItem(item)
            item.setPos(data["position"])
            item.setSelected(data["selected"])


class MoveItemCommand:
    def __init__(self, item, old_position, new_position):
        self.item = item
        self.old_position = old_position
        self.new_position = new_position

    def undo(self):
        self.item.setPos(self.old_position)

    def redo(self):
        self.item.setPos(self.new_position)



class MoveItemsCommand:
    def __init__(self, old_positions, new_positions):
        self.old_positions = old_positions
        self.new_positions = new_positions

    def undo(self):
        for item, position in self.old_positions.items():
            item.setPos(position)

    def redo(self):
        for item, position in self.new_positions.items():
            item.setPos(position)
