
from PySide6.QtWidgets import QGraphicsItem
from PySide6.QtGui import QPainter, QPen, QColor, QPainterPath
from PySide6.QtCore import QRectF, Qt

from settings import (
    COLOR_COMPONENT,
    COLOR_COMPONENT_SELECTED,
    RESISTOR_WIDTH,
    RESISTOR_HEIGHT,
    RESISTOR_LINE_WIDTH,
)


class Resistor(QGraphicsItem):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.component_id = "resistor"
        self.name = "Direnç"
        self.value = "1000"
        self.unit = "Ω"

        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsMovable
            | QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
            | QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges
        )

    def terminal_positions(self):
        half = RESISTOR_WIDTH / 2
        return [(-half, 0), (half, 0)]

    def set_value(self, value):
        self.value = str(value)
        self.update()

    def boundingRect(self):
        return QRectF(
            -RESISTOR_WIDTH / 2,
            -RESISTOR_HEIGHT / 2,
            RESISTOR_WIDTH,
            RESISTOR_HEIGHT,
        )

    def paint(self, painter, option, widget=None):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        color = (
            COLOR_COMPONENT_SELECTED
            if self.isSelected()
            else COLOR_COMPONENT
        )

        pen = QPen(QColor(color), RESISTOR_LINE_WIDTH)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)

        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)

        half_width = RESISTOR_WIDTH / 2
        half_height = RESISTOR_HEIGHT / 2

        path = QPainterPath()

        path.moveTo(-half_width, 0)
        path.lineTo(-half_width * 0.6, 0)

        path.lineTo(-half_width * 0.4, -half_height)
        path.lineTo(-half_width * 0.2, half_height)
        path.lineTo(0, -half_height)
        path.lineTo(half_width * 0.2, half_height)
        path.lineTo(half_width * 0.4, -half_height)
        path.lineTo(half_width * 0.6, 0)

        path.lineTo(half_width, 0)

        painter.drawPath(path)
