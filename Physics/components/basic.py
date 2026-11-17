from PySide6.QtWidgets import QGraphicsItem, QApplication
from PySide6.QtGui import QPainter, QPen, QBrush, QColor, QPainterPath
from PySide6.QtCore import QRectF, Qt

from theme import color

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
        "fuse": ("Sigorta", "", ""),
        "potentiometer": ("Potansiyometre", "10", "kΩ"),
        "ac_source": ("AC Kaynak", "5", "V"),
        "bjt": ("BJT Transistör (NPN)", "", ""),
        "mosfet": ("MOSFET (N-Kanal)", "", ""),
    }

    def __init__(self, component_id, parent=None):
        super().__init__(parent)
        if component_id not in self.DEFINITIONS:
            raise ValueError(f"Bilinmeyen bileşen: {component_id}")
        self.component_id = component_id
        self.name, self.value, self.unit = self.DEFINITIONS[component_id]
        self.closed = False if component_id == "switch" else None
        self._press_scene_pos = None
        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsMovable
            | QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
            | QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges
        )

    def boundingRect(self):
        return QRectF(-COMPONENT_WIDTH / 2, -36,
                      COMPONENT_WIDTH, 86)

    def terminal_names(self):
        names = {
            "ground": ["GND"],
            "bjt": ["Base", "Collector", "Emitter"],
            "mosfet": ["Gate", "Drain", "Source"],
            "potentiometer": ["Uç 1", "Uç 2", "Sürgü"],
        }
        return names.get(self.component_id, ["Uç 1", "Uç 2"])

    def terminal_positions(self):
        if self.component_id == "ground":
            return [(0, -COMPONENT_HEIGHT / 2)]
        if self.component_id == "bjt":
            return [(-COMPONENT_WIDTH / 2, 0), (COMPONENT_WIDTH / 2, -24), (COMPONENT_WIDTH / 2, 24)]
        if self.component_id == "mosfet":
            return [(-COMPONENT_WIDTH / 2, 0), (COMPONENT_WIDTH / 2, -24), (COMPONENT_WIDTH / 2, 24)]
        if self.component_id == "potentiometer":
            return [(-COMPONENT_WIDTH / 2, 0), (COMPONENT_WIDTH / 2, 0), (0, -32)]
        half = COMPONENT_WIDTH / 2
        return [(-half, 0), (half, 0)]

    def set_value(self, value):
        self.value = str(value)
        self.update()

    def mousePressEvent(self, event):
        self._press_scene_pos = event.scenePos()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        start = self._press_scene_pos
        super().mouseReleaseEvent(event)
        if self.component_id == "switch" and start is not None:
            moved = (event.scenePos() - start).manhattanLength()
            if moved < QApplication.startDragDistance():
                self.closed = not self.closed
                self.update()
        self._press_scene_pos = None

    def paint(self, painter, option, widget=None):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        color_value = QColor(color("selected") if self.isSelected() else color("component"))
        pen = QPen(color_value, COMPONENT_LINE_WIDTH)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)

        w, h = COMPONENT_WIDTH / 2, COMPONENT_HEIGHT / 2
        path = QPainterPath()
        if self.component_id != "ground":
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
        elif self.component_id in ("voltage_source", "battery", "ac_source"):
            path.moveTo(-18, 0); path.lineTo(-12, 0)
            path.addEllipse(QRectF(-12, -12, 24, 24)) if self.component_id in ("voltage_source", "ac_source") else None
            if self.component_id in ("voltage_source", "ac_source"):
                if self.component_id == "voltage_source":
                    path.moveTo(-7, 0); path.lineTo(-1, 0)
                    path.moveTo(-4, -3); path.lineTo(-4, 3)
                    path.moveTo(3, 0); path.lineTo(8, 0)
                else:
                    path.moveTo(-7, 0)
                    path.cubicTo(-4, -8, 0, -8, 3, 0)
                    path.cubicTo(6, 8, 10, 8, 12, 0)
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
        elif self.component_id == "fuse":
            path.moveTo(-18, 0); path.lineTo(-12, 0)
            path.addRect(QRectF(-12, -8, 24, 16))
            path.moveTo(12, 0); path.lineTo(w, 0)
        elif self.component_id == "potentiometer":
            path.moveTo(-18, 0); path.lineTo(-12, 0)
            for i in range(4):
                x = -12 + i * 6
                path.lineTo(x + 3, -h if i % 2 == 0 else h)
            path.lineTo(12, 0); path.lineTo(w, 0)
            path.moveTo(0, -h - 12); path.lineTo(0, -h - 2)
            path.lineTo(-4, -h - 7)
            path.moveTo(0, -h - 2); path.lineTo(4, -h - 7)
        elif self.component_id == "switch":
            path.moveTo(-18, 0); path.lineTo(-8, 0)
            path.moveTo(-8, 0); path.lineTo(10, 0 if self.closed else -12)
            path.addEllipse(QRectF(-11, -3, 6, 6))
            path.addEllipse(QRectF(8, -3, 6, 6))
            path.moveTo(14, 0); path.lineTo(w, 0)
        elif self.component_id == "bjt":
            path.moveTo(-40, 0); path.lineTo(-5, 0)
            path.moveTo(-5, -15); path.lineTo(-5, 15)
            path.moveTo(-5, -9); path.lineTo(12, -24); path.lineTo(40, -24)
            path.moveTo(-5, 9); path.lineTo(12, 24); path.lineTo(40, 24)
            path.moveTo(3, 16); path.lineTo(12, 24); path.lineTo(1, 23)
        elif self.component_id == "mosfet":
            path.moveTo(-40, 0); path.lineTo(-10, 0)
            path.moveTo(-5, -16); path.lineTo(-5, 16)
            path.moveTo(5, -18); path.lineTo(5, 18)
            path.moveTo(5, -12); path.lineTo(22, -24); path.lineTo(40, -24)
            path.moveTo(5, 12); path.lineTo(22, 24); path.lineTo(40, 24)
        elif self.component_id == "ground":
            path.moveTo(0, -h); path.lineTo(0, 0)
            path.moveTo(-16, 0); path.lineTo(16, 0)
            path.moveTo(-11, 6); path.lineTo(11, 6)
            path.moveTo(-5, 12); path.lineTo(5, 12)
        painter.drawPath(path)

