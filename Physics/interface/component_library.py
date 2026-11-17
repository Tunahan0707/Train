from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QScrollArea
)
from PySide6.QtCore import Qt, Signal


COMPONENTS = [
    ("PASİF BİLEŞENLER", [
        ("resistor", "Ω   Direnç"),
        ("capacitor", "║   Kondansatör"),
        ("inductor", "∿   Bobin"),
        ("fuse", "▭   Sigorta"),
        ("potentiometer", "↗   Potansiyometre"),
    ]),
    ("YARI İLETKENLER", [
        ("diode", "▷   Diyot"),
        ("led", "◈   LED"),
        ("bjt", "◁   BJT Transistör"),
        ("mosfet", "⊢   MOSFET"),
    ]),
    ("GÜÇ KAYNAKLARI", [
        ("voltage_source", "＋   DC Kaynak"),
        ("ac_source", "∿   AC Kaynak"),
        ("battery", "▰   Pil"),
    ]),
    ("KONTROL VE BAĞLANTI", [
        ("switch", "／   Anahtar"),
        ("ground", "⏚   Toprak (GND)"),
        ("wire", "─   İletken / Tel"),
    ]),
]


class ComponentLibrary(QWidget):
    component_requested = Signal(str)
    placement_cancelled = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("componentLibrary")
        self.setMinimumWidth(210)
        self.setMaximumWidth(290)
        self.buttons = {}
        self.section_groups = []

        outer = QVBoxLayout(self)
        outer.setContentsMargins(12, 14, 12, 10)
        outer.setSpacing(9)

        title = QLabel("BİLEŞEN KÜTÜPHANESİ")
        title.setObjectName("panelTitle")
        outer.addWidget(title)

        description = QLabel("Bileşen seç, ardından çalışma alanına tıklayarak yerleştir.")
        description.setObjectName("panelDescription")
        description.setWordWrap(True)
        outer.addWidget(description)

        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Bileşen ara...")
        self.search_edit.textChanged.connect(self.filter_components)
        outer.addWidget(self.search_edit)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(8)

        for section_name, components in COMPONENTS:
            section = QLabel(section_name)
            section.setObjectName("sectionTitle")
            layout.addWidget(section)
            section_buttons = []
            self.section_groups.append((section, section_buttons))

            for component_id, label in components:
                button = QPushButton(label)
                button.setObjectName("componentButton")
                button.setCheckable(True)
                button.setCursor(Qt.CursorShape.PointingHandCursor)
                button.toggled.connect(
                    lambda checked, cid=component_id: self.on_component_toggled(cid, checked)
                )
                self.buttons[component_id] = button
                section_buttons.append(button)
                layout.addWidget(button)

        layout.addStretch()
        scroll.setWidget(content)
        outer.addWidget(scroll, 1)

        hint = QLabel("ESC: iptal  •  R: döndür  •  Ctrl+D: çoğalt")
        hint.setObjectName("panelHint")
        outer.addWidget(hint)

        self.setStyleSheet("""
            QWidget#componentLibrary { background-color: #201d2b; color: #e8e3f2; }
            QLabel#panelTitle { color: #c4b5fd; font-size: 12px; font-weight: 700; letter-spacing: 1px; }
            QLabel#panelDescription { color: #aaa3ba; font-size: 12px; }
            QLabel#sectionTitle { color: #8e879f; font-size: 10px; font-weight: 700; margin-top: 10px; }
            QPushButton#componentButton {
                color: #e8e3f2; background-color: #302b3d; border: 1px solid #494158;
                border-radius: 8px; padding: 10px; text-align: left; font-size: 13px;
            }
            QPushButton#componentButton:hover { background-color: #3b3450; border-color: #8b75c7; }
            QPushButton#componentButton:checked { background-color: #493b68; border: 1px solid #a78bfa; color: white; }
            QLineEdit { color:#e8e3f2; background:#302b3d; border:1px solid #494158; border-radius:7px; padding:8px; }
            QLabel#panelHint { color: #827b91; font-size: 10px; }
            QScrollArea { border: none; background: transparent; }
        """)

    def filter_components(self, query):
        query = query.casefold().strip()
        for section, buttons in self.section_groups:
            visible_count = 0
            for button in buttons:
                visible = query in button.text().casefold()
                button.setVisible(visible)
                visible_count += int(visible)
            section.setVisible(visible_count > 0)

    def on_component_toggled(self, component_id, checked):
        if checked:
            self.set_active_component(component_id)
            self.component_requested.emit(component_id)
        else:
            self.placement_cancelled.emit()

    def set_active_component(self, component_id):
        for key, button in self.buttons.items():
            button.blockSignals(True)
            button.setChecked(key == component_id)
            button.blockSignals(False)
