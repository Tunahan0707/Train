from PySide6.QtCore import Qt, Signal, Property, QPropertyAnimation, QEasingCurve, QRectF
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
        self.setToolTip("Açık / koyu tema")

        self.animation = QPropertyAnimation(self, b"position", self)
        self.animation.setDuration(620)
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
        painter.drawRoundedRect(QRectF(1, 3, 60, 28), 14, 14)

        knob_x = 4 + 28 * t
        painter.setBrush(knob)
        painter.drawEllipse(QRectF(knob_x, 6, 22, 22))

        # Simge de düğmeyle birlikte döner; güneş ve ay birbirine yumuşakça geçer.
        painter.save()
        painter.translate(knob_x + 11, 17)
        painter.rotate(180 * t)
        painter.setBrush(Qt.BrushStyle.NoBrush)

        sun_alpha = round(255 * (1.0 - t))
        if sun_alpha:
            sun_color = QColor(164, 119, 35, sun_alpha)
            painter.setPen(QPen(sun_color, 1.35))
            painter.drawEllipse(QRectF(-3.5, -3.5, 7, 7))
            for x1, y1, x2, y2 in [
                (0, -7, 0, -5), (0, 5, 0, 7),
                (-7, 0, -5, 0), (5, 0, 7, 0),
                (-5, -5, -4, -4), (4, 4, 5, 5),
                (-5, 5, -4, 4), (4, -4, 5, -5),
            ]:
                painter.drawLine(x1, y1, x2, y2)

        moon_alpha = round(255 * t)
        if moon_alpha:
            moon_color = QColor(76, 100, 133, moon_alpha)
            painter.setPen(QPen(moon_color, 1.6))
            painter.drawArc(QRectF(-5, -6, 11, 12), 48 * 16, 264 * 16)
            painter.drawArc(QRectF(-1, -5, 8, 10), 70 * 16, 220 * 16)

        painter.restore()
        painter.end()
