from PySide6.QtWidgets import QGraphicsItem
from PySide6.QtGui import QPainter, QPen, QBrush, QColor, QPainterPath
from PySide6.QtCore import QRectF, Qt

from settings import (
    COLOR_COMPONENT,
    COLOR_COMPONENT_SELECTED,
    COMPONENT_LINE_WIDTH,
    COMPONENT_WIDTH,
    COMPONENT_HEIGHT,
    GRID_SIZE,
)


class BasicComponent(QGraphicsItem):
    """Simple schematic symbol with editable value and two electrical terminals."""

    DEFINITIONS = {
        "capacitor": ("Kondansatör", "100", "µF"),
        "inductor": ("Bobin", "10", "mH"),
        "voltage_source": ("DC Kaynak", "5", "V"),
        "battery": ("Pil", "9", "V"),
        "diode": ("Diyot", "", ""),
        "led": ("LED", "", ""),
        "switch": ("Anahtar", "", ""),
        "ground": ("Toprak", "", ""),
    }

    def __init__(self, component_id, parent=None):
        super().__init__(parent)
        if component_id not in self.DEFINITIONS:
            raise ValueError(f"Bilinmeyen bileşen: {component_id}")
        self.component_id = component_id
        self.name, self.value, self.unit = self.DEFINITIONS[component_id]
        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsMovable
            | QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
            | QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges
        )

    def boundingRect(self):
        return QRectF(-COMPONENT_WIDTH / 2, -COMPONENT_HEIGHT / 2,
                      COMPONENT_WIDTH, COMPONENT_HEIGHT)

    def terminal_positions(self):
        half = COMPONENT_WIDTH / 2
        return [(-half, 0), (half, 0)]

    def set_value(self, value):
        self.value = str(value)
        self.update()

    def paint(self, painter, option, widget=None):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        color = QColor(COLOR_COMPONENT_SELECTED if self.isSelected() else COLOR_COMPONENT)
        pen = QPen(color, COMPONENT_LINE_WIDTH)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)

        w, h = COMPONENT_WIDTH / 2, COMPONENT_HEIGHT / 2
        path = QPainterPath()
        path.moveTo(-w, 0)
        path.lineTo(-18, 0)

        if self.component_id == "capacitor":
            path.moveTo(-8, -h); path.lineTo(-8, h)
            path.moveTo(8, -h); path.lineTo(8, h)
            path.moveTo(8, 0); path.lineTo(w, 0)
        elif self.component_id == "inductor":
            path.moveTo(-18, 0)
            for i in range(4):
                x = -12 + i * 8
                path.cubicTo(x - 2, -h - 8, x + 6, -h - 8, x + 8, 0)
            path.lineTo(w, 0)
        elif self.component_id in ("voltage_source", "battery"):
            path.moveTo(-18, 0); path.lineTo(-12, 0)
            path.addEllipse(QRectF(-12, -12, 24, 24)) if self.component_id == "voltage_source" else None
            if self.component_id == "voltage_source":
                path.moveTo(-5, 0); path.lineTo(5, 0)
                path.moveTo(0, -5); path.lineTo(0, 5)
                path.moveTo(12, 0); path.lineTo(w, 0)
            else:
                path.moveTo(-7, -h); path.lineTo(-7, h)
                path.moveTo(7, -h / 2); path.lineTo(7, h / 2)
                path.moveTo(7, 0); path.lineTo(w, 0)
        elif self.component_id in ("diode", "led"):
            path.moveTo(-18, 0); path.lineTo(-8, 0)
            path.moveTo(-8, -12); path.lineTo(10, 0); path.lineTo(-8, 12); path.closeSubpath()
            path.moveTo(10, -12); path.lineTo(10, 12)
            path.moveTo(10, 0); path.lineTo(w, 0)
            if self.component_id == "led":
                path.moveTo(0, -17); path.lineTo(8, -25)
                path.moveTo(5, -17); path.lineTo(8, -25); path.lineTo(1, -23)
        elif self.component_id == "switch":
            path.moveTo(-18, 0); path.lineTo(-8, 0)
            path.moveTo(-8, 0); path.lineTo(10, -12)
            path.addEllipse(QRectF(-11, -3, 6, 6))
            path.addEllipse(QRectF(8, -3, 6, 6))
            path.moveTo(14, 0); path.lineTo(w, 0)
        elif self.component_id == "ground":
            path.moveTo(0, -h); path.lineTo(0, 0)
            path.moveTo(-16, 0); path.lineTo(16, 0)
            path.moveTo(-11, 6); path.lineTo(11, 6)
            path.moveTo(-5, 12); path.lineTo(5, 12)
        painter.drawPath(path)

        if self.value:
            painter.setPen(QPen(color, 1))
            painter.drawText(QRectF(-w, h + 5, COMPONENT_WIDTH, 18),
                             Qt.AlignmentFlag.AlignHCenter, f"{self.value} {self.unit}".strip())
