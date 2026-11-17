from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QFrame
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
        ("battery", "▰   Pil"),
        ("ac_source", "∿   AC Kaynak"),
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

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 18, 14, 14)
        layout.setSpacing(9)

        title = QLabel("BİLEŞEN KÜTÜPHANESİ")
        title.setObjectName("panelTitle")
        layout.addWidget(title)

        description = QLabel("Bileşen seç, ardından çalışma alanına tıklayarak yerleştir.")
        description.setObjectName("panelDescription")
        description.setWordWrap(True)
        layout.addWidget(description)

        for section_name, components in COMPONENTS:
            section = QLabel(section_name)
            section.setObjectName("sectionTitle")
            layout.addWidget(section)
            for component_id, label in components:
                button = QPushButton(label)
                button.setObjectName("componentButton")
                button.setCheckable(True)
                button.setCursor(Qt.CursorShape.PointingHandCursor)
                button.toggled.connect(
                    lambda checked, cid=component_id: self.on_component_toggled(cid, checked)
                )
                self.buttons[component_id] = button
                layout.addWidget(button)

        layout.addStretch()
        hint = QLabel("ESC: yerleştirmeyi iptal et  •  R: döndür")
        hint.setObjectName("panelHint")
        layout.addWidget(hint)

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
            QLabel#panelHint { color: #827b91; font-size: 10px; }
        """)

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
