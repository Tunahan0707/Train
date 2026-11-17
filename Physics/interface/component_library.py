from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit,
    QScrollArea, QApplication
)
from PySide6.QtCore import Qt, Signal, QMimeData, QPoint
from PySide6.QtGui import QDrag


COMPONENTS = [
    ("PASİF", [
        ("resistor", "Direnç"),
        ("capacitor", "Kondansatör"),
        ("inductor", "Bobin"),
        ("fuse", "Sigorta"),
        ("potentiometer", "Potansiyometre"),
    ]),
    ("YARI İLETKEN", [
        ("diode", "Diyot"),
        ("led", "LED"),
        ("bjt", "BJT"),
        ("mosfet", "MOSFET"),
    ]),
    ("KAYNAKLAR", [
        ("voltage_source", "DC Kaynak"),
        ("ac_source", "AC Kaynak"),
        ("battery", "Pil"),
    ]),
    ("BAĞLANTI", [
        ("switch", "Anahtar"),
        ("ground", "Toprak"),
        ("wire", "İletken"),
    ]),
]


class ComponentButton(QPushButton):
    def __init__(self, component_id, label, parent=None):
        super().__init__(label, parent)
        self.component_id = component_id
        self.drag_start = QPoint()
        self.setObjectName("componentButton")
        self.setCursor(Qt.CursorShape.OpenHandCursor)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_start = event.position().toPoint()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if not (event.buttons() & Qt.MouseButton.LeftButton):
            return
        if (event.position().toPoint() - self.drag_start).manhattanLength() < QApplication.startDragDistance():
            return

        mime = QMimeData()
        mime.setData("application/x-physics-component", self.component_id.encode("utf-8"))
        drag = QDrag(self)
        drag.setMimeData(mime)
        drag.exec(Qt.DropAction.CopyAction)


class ComponentLibrary(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("componentLibrary")
        self.setMinimumWidth(205)
        self.setMaximumWidth(280)
        self.section_groups = []

        outer = QVBoxLayout(self)
        outer.setContentsMargins(10, 10, 10, 10)
        outer.setSpacing(8)

        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Ara")
        self.search_edit.setObjectName("componentSearch")
        self.search_edit.textChanged.connect(self.filter_components)
        outer.addWidget(self.search_edit)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        for section_name, components in COMPONENTS:
            section = QLabel(section_name)
            section.setObjectName("sectionTitle")
            layout.addWidget(section)
            buttons = []
            self.section_groups.append((section, buttons))

            for component_id, label in components:
                button = ComponentButton(component_id, label)
                buttons.append(button)
                layout.addWidget(button)

        layout.addStretch()
        scroll.setWidget(content)
        outer.addWidget(scroll, 1)

    def filter_components(self, query):
        query = query.casefold().strip()
        for section, buttons in self.section_groups:
            visible_count = 0
            for button in buttons:
                visible = query in button.text().casefold()
                button.setVisible(visible)
                visible_count += int(visible)
            section.setVisible(visible_count > 0)
