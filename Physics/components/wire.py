from PySide6.QtWidgets import QGraphicsPathItem
from PySide6.QtGui import QPainterPath, QPen, QColor
from PySide6.QtCore import Qt, QPointF

from settings import COLOR_COMPONENT, COLOR_COMPONENT_SELECTED


class WireItem(QGraphicsPathItem):
    def __init__(self, start, end, parent=None):
        super().__init__(parent)
        self.component_id = "wire"
        self.start_point = QPointF(start)
        self.end_point = QPointF(end)
        self.setFlag(QGraphicsPathItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setZValue(-1)
        self.update_path()

    def update_path(self):
        path = QPainterPath(self.start_point)
        # Schematic wires use a clean right-angle route.
        path.lineTo(self.end_point.x(), self.start_point.y())
        path.lineTo(self.end_point)
        self.setPath(path)

    def set_end_point(self, point):
        self.end_point = QPointF(point)
        self.update_path()

    def paint(self, painter, option, widget=None):
        color = COLOR_COMPONENT_SELECTED if self.isSelected() else COLOR_COMPONENT
        pen = QPen(QColor(color), 2.5)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(self.path())
