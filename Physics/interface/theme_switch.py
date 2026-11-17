from PySide6.QtCore import Qt, Signal, Property, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QWidget


class ThemeSwitch(QWidget):
    mode_changed = Signal(bool)
    progress_changed = Signal(float)

    def __init__(self, dark=True, parent=None):
        super().__init__(parent)
        self._dark = dark
        self._position = 1.0 if dark else 0.0
        self.setFixedSize(62, 34)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip("Temayı değiştir")

        self.animation = QPropertyAnimation(self, b"position", self)
        self.animation.setDuration(520)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutCubic)

    def get_position(self):
        return self._position

    def set_position(self, value):
        self._position = max(0.0, min(1.0, float(value)))
        self.progress_changed.emit(self._position)
        self.update()

    position = Property(float, get_position, set_position)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._dark = not self._dark
            self.animation.stop()
            self.animation.setStartValue(self._position)
            self.animation.setEndValue(1.0 if self._dark else 0.0)
            self.animation.start()
            self.mode_changed.emit(self._dark)
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        t = self._position
        track = QColor(
            round(222 + (24 - 222) * t),
            round(230 + (43 - 230) * t),
            round(240 + (70 - 240) * t),
        )
        knob = QColor(
            round(255 + (220 - 255) * t),
            round(255 + (230 - 255) * t),
            round(255 + (244 - 255) * t),
        )
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(track)
        painter.drawRoundedRect(1, 3, 60, 28, 14, 14)

        x = 4 + 28 * t
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(knob)
        painter.drawEllipse(round(x), 6, 22, 22)

        # Aktif temanın simgesi hareketli düğmenin üzerinde kalır.
        icon_color = QColor("#52677f")
        painter.setPen(QPen(icon_color, 1.35))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        cx = round(x) + 11
        if t < 0.5:
            painter.drawEllipse(cx - 4, 13, 8, 8)
            painter.drawLine(cx, 9, cx, 11)
            painter.drawLine(cx, 23, cx, 25)
            painter.drawLine(cx - 8, 17, cx - 6, 17)
            painter.drawLine(cx + 6, 17, cx + 8, 17)
            painter.drawLine(cx - 6, 11, cx - 5, 12)
            painter.drawLine(cx + 5, 22, cx + 6, 23)
        else:
            painter.drawArc(cx - 5, 11, 11, 12, 35 * 16, 285 * 16)
        painter.end()
