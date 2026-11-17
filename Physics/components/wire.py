from PySide6.QtWidgets import QGraphicsPathItem
from PySide6.QtGui import QPainterPath, QPen, QColor
from PySide6.QtCore import Qt, QPointF

from settings import COLOR_COMPONENT, COLOR_COMPONENT_SELECTED


class WireItem(QGraphicsPathItem):
    def __init__(self, start, end, parent=None):
        super().__init__(parent)
        self.component_id = "wire"
        self.start_point = self.to_point(start)
        self.end_point = self.to_point(end)
        self.setFlag(QGraphicsPathItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setPen(QPen(QColor(color("component")), 8))
        self.setZValue(-1)
        self.update_path()

    @staticmethod
    def to_point(value):
        if hasattr(value, "x") and hasattr(value, "y"):
            return QPointF(value.x(), value.y())
        return QPointF(float(value[0]), float(value[1]))

    def terminal_positions(self):
        return [
            (self.start_point.x(), self.start_point.y()),
            (self.end_point.x(), self.end_point.y()),
        ]

    def update_path(self):
        path = QPainterPath(self.start_point)
        # Schematic wires use a clean right-angle route.
        path.lineTo(self.end_point.x(), self.start_point.y())
        path.lineTo(self.end_point)
        self.setPath(path)

    def set_end_point(self, point):
        self.end_point = self.to_point(point)
        self.update_path()

    def paint(self, painter, option, widget=None):
        color_value = color("selected") if self.isSelected() else color("component")
        pen = QPen(QColor(color_value), 2.5)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(self.path())
