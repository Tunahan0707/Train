from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton,
    QScrollArea, QMenu, QSizePolicy,
)
from PySide6.QtCore import Qt, Signal, QMimeData, QPoint
from PySide6.QtGui import QDrag, QAction
from PySide6.QtWidgets import QApplication

COMPONENTS = [
    ("Pasif", [("resistor", "Direnç"), ("capacitor", "Kondansatör"), ("inductor", "Bobin"), ("fuse", "Sigorta"), ("potentiometer", "Potansiyometre")]),
    ("Yarı iletken", [("diode", "Diyot"), ("led", "LED"), ("bjt", "BJT"), ("mosfet", "MOSFET")]),
    ("Kaynaklar", [("voltage_source", "DC Kaynak"), ("ac_source", "AC Kaynak"), ("battery", "Pil")]),
    ("Bağlantı", [("switch", "Anahtar"), ("ground", "Toprak"), ("wire", "İletken")]),
]


class ComponentButton(QPushButton):
    add_requested = Signal(str, bool)

    def __init__(self, component_id, label, parent=None):
        super().__init__(label, parent)
        self.component_id = component_id
        self.drag_start = QPoint()
        self._dragged = False
        self.setObjectName("componentButton")
        self.setCursor(Qt.CursorShape.OpenHandCursor)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.clicked.connect(self._clicked)

    def _clicked(self):
        if self._dragged:
            self._dragged = False
            return
        shift = bool(QApplication.keyboardModifiers() & Qt.KeyboardModifier.ShiftModifier)
        self.add_requested.emit(self.component_id, shift)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragged = False
            self.drag_start = event.position().toPoint()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if not (event.buttons() & Qt.MouseButton.LeftButton):
            return
        if (event.position().toPoint() - self.drag_start).manhattanLength() < QApplication.startDragDistance():
            return
        self._dragged = True
        mime = QMimeData()
        mime.setData("application/x-physics-component", self.component_id.encode("utf-8"))
        drag = QDrag(self)
        drag.setMimeData(mime)
        drag.exec(Qt.DropAction.CopyAction)


class ComponentLibrary(QWidget):
    add_requested = Signal(str, bool)
    menu_action = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("componentLibrary")
        self.setMinimumHeight(42)
        self.setMaximumHeight(190)
        self.expanded = False
        self.active_category = None
        self.shift_add_count = 0

        root = QVBoxLayout(self)
        root.setContentsMargins(8, 5, 8, 5)
        root.setSpacing(5)

        self.drawer = QWidget()
        self.drawer.setObjectName("componentDrawer")
        drawer_layout = QHBoxLayout(self.drawer)
        drawer_layout.setContentsMargins(0, 0, 0, 0)
        drawer_layout.setSpacing(7)
        self.scroll = QScrollArea()
        self.scroll.setObjectName("componentScrollArea")
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.items_host = QWidget()
        self.items_host.setObjectName("componentItemsHost")
        self.items_layout = QHBoxLayout(self.items_host)
        self.items_layout.setContentsMargins(2, 2, 2, 2)
        self.items_layout.setSpacing(7)
        self.scroll.setWidget(self.items_host)
        self.scroll.viewport().setObjectName("componentScrollViewport")
        for surface in (self.drawer, self.scroll, self.scroll.viewport(), self.items_host):
            surface.setAutoFillBackground(True)
        drawer_layout.addWidget(self.scroll)
        root.addWidget(self.drawer, 1)

        bottom = QHBoxLayout()
        bottom.setContentsMargins(0, 0, 0, 0)
        bottom.setSpacing(5)
        self.menu_button = QPushButton("Menü")
        self.menu_button.setObjectName("paletteMenuButton")
        menu = QMenu(self.menu_button)
        for label, key in [("Yeni devre", "new"), ("Aç", "open"), ("Kaydet", "save"), ("Farklı kaydet", "save_as")]:
            action = QAction(label, menu)
            action.triggered.connect(lambda checked=False, value=key: self.menu_action.emit(value))
            menu.addAction(action)
        menu.addSeparator()
        for label, key in [("Bağlantıları denetle", "check"), ("DC çalışma noktası", "simulate")]:
            action = QAction(label, menu)
            action.triggered.connect(lambda checked=False, value=key: self.menu_action.emit(value))
            menu.addAction(action)
        self.menu_button.setMenu(menu)
        bottom.addWidget(self.menu_button)

        self.category_buttons = {}
        for category, components in COMPONENTS:
            button = QPushButton(category)
            button.setCheckable(True)
            button.setObjectName("paletteTab")
            button.clicked.connect(lambda checked=False, name=category: self.toggle_category(name))
            self.category_buttons[category] = button
            bottom.addWidget(button)
        bottom.addStretch(1)
        root.addLayout(bottom)

        self.drawer.hide()
        self.setStyleSheet("")

    def toggle_category(self, category):
        if self.active_category == category and self.expanded:
            self.collapse()
            return
        self.active_category = category
        self.shift_add_count = 0
        for name, button in self.category_buttons.items():
            button.setChecked(name == category)
        self._populate(category)
        self.expand()

    def _populate(self, category):
        while self.items_layout.count():
            item = self.items_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        components = dict(COMPONENTS)[category]
        for component_id, label in components:
            button = ComponentButton(component_id, label, self.items_host)
            button.add_requested.connect(self._add_component)
            self.items_layout.addWidget(button)
        self.items_layout.addStretch(1)

    def _add_component(self, component_id, shift):
        self.add_requested.emit(component_id, shift)
        if shift:
            self.shift_add_count += 1
        else:
            self.collapse()

    def expand(self):
        self.expanded = True
        self.drawer.show()
        self.setMaximumHeight(190)

    def collapse(self):
        self.expanded = False
        self.drawer.hide()
        self.active_category = None
        self.shift_add_count = 0
        for button in self.category_buttons.values():
            button.setChecked(False)
        self.setMaximumHeight(48)

    def reset_shift_stack(self):
        self.shift_add_count = 0

    def apply_theme(self, colors):
        from PySide6.QtGui import QColor, QPalette

        surface = QColor(colors["panel_alt"])
        surfaces = (self.drawer, self.scroll, self.scroll.viewport(), self.items_host)
        for widget in surfaces:
            palette = widget.palette()
            palette.setColor(QPalette.ColorRole.Window, surface)
            palette.setColor(QPalette.ColorRole.Base, surface)
            widget.setPalette(palette)
            widget.setBackgroundRole(QPalette.ColorRole.Window)
            widget.setAutoFillBackground(True)
            widget.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
            # QScrollArea'nın viewport'u ayrı bir QWidget olduğundan rengi
            # yalnızca QScrollArea'ya verilen stil sayfasından devralmayabilir.
            widget.setStyleSheet(
                "background-color: " + colors["panel_alt"] + ";"
                "color: " + colors["text"] + ";"
                "border: none;"
            )

        self.setStyleSheet(
            "QWidget#componentLibrary { background-color: " + colors["panel"] + "; }"
            "QWidget#componentDrawer, QScrollArea#componentScrollArea, "
            "QWidget#componentScrollViewport, QWidget#componentItemsHost { "
            "background-color: " + colors["panel_alt"] + "; color: " + colors["text"] + "; border: none; }"
            "QScrollBar:horizontal { height: 8px; background: " + colors["panel"] + "; border: none; }"
            "QScrollBar::handle:horizontal { background: " + colors["muted"] + "; min-width: 25px; border-radius: 4px; }"
        )
