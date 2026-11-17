from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
)
from PySide6.QtCore import Qt, Signal


class ComponentLibrary(QWidget):
    component_requested = Signal(str)
    placement_cancelled = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setObjectName("componentLibrary")
        self.setMinimumWidth(210)
        self.setMaximumWidth(280)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 18, 14, 14)
        layout.setSpacing(12)

        title = QLabel("BİLEŞEN KÜTÜPHANESİ")
        title.setObjectName("panelTitle")
        layout.addWidget(title)

        description = QLabel(
            "Bir bileşen seç, ardından çalışma alanına tıklayarak yerleştir."
        )
        description.setObjectName("panelDescription")
        description.setWordWrap(True)
        layout.addWidget(description)

        section = QLabel("PASİF BİLEŞENLER")
        section.setObjectName("sectionTitle")
        layout.addWidget(section)

        self.resistor_button = QPushButton("Ω   Direnç")
        self.resistor_button.setObjectName("componentButton")
        self.resistor_button.setCheckable(True)
        self.resistor_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.resistor_button.setToolTip(
            "Direnç yerleştirme modunu aç"
        )
        self.resistor_button.toggled.connect(
            self.on_resistor_toggled
        )
        layout.addWidget(self.resistor_button)

        coming_soon = QFrame()
        coming_soon.setObjectName("comingSoon")
        coming_layout = QVBoxLayout(coming_soon)
        coming_layout.setContentsMargins(10, 10, 10, 10)

        coming_label = QLabel(
            "Kondansatör, bobin ve diğer bileşenler sonraki aşamalarda eklenecek."
        )
        coming_label.setObjectName("comingSoonText")
        coming_label.setWordWrap(True)
        coming_layout.addWidget(coming_label)
        layout.addWidget(coming_soon)

        layout.addStretch()

        self.hint = QLabel(
            "ESC: yerleştirme modundan çık"
        )
        self.hint.setObjectName("panelHint")
        layout.addWidget(self.hint)

        self.setStyleSheet("""
            QWidget#componentLibrary {
                background-color: #201d2b;
                color: #e8e3f2;
            }
            QLabel#panelTitle {
                color: #c4b5fd;
                font-size: 12px;
                font-weight: 700;
                letter-spacing: 1px;
            }
            QLabel#panelDescription {
                color: #aaa3ba;
                font-size: 12px;
            }
            QLabel#sectionTitle {
                color: #8e879f;
                font-size: 10px;
                font-weight: 700;
                margin-top: 12px;
            }
            QPushButton#componentButton {
                color: #e8e3f2;
                background-color: #302b3d;
                border: 1px solid #494158;
                border-radius: 8px;
                padding: 12px;
                text-align: left;
                font-size: 13px;
            }
            QPushButton#componentButton:hover {
                background-color: #3b3450;
                border-color: #8b75c7;
            }
            QPushButton#componentButton:checked {
                background-color: #493b68;
                border: 1px solid #a78bfa;
                color: #ffffff;
            }
            QFrame#comingSoon {
                background-color: #252230;
                border: 1px dashed #484253;
                border-radius: 8px;
            }
            QLabel#comingSoonText {
                color: #827b91;
                font-size: 11px;
            }
            QLabel#panelHint {
                color: #827b91;
                font-size: 10px;
            }
        """)

    def on_resistor_toggled(self, checked):
        if checked:
            self.component_requested.emit("resistor")
        else:
            self.placement_cancelled.emit()

    def set_active_component(self, component_id):
        checked = component_id == "resistor"

        # Durum güncellenirken toggled sinyalini tekrar tetikleme.
        self.resistor_button.blockSignals(True)
        self.resistor_button.setChecked(checked)
        self.resistor_button.blockSignals(False)
