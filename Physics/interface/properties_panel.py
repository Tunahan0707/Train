from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QFormLayout
from PySide6.QtCore import Qt


class PropertiesPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_item = None
        self.setMinimumWidth(220)

        layout = QVBoxLayout(self)
        title = QLabel("BİLEŞEN ÖZELLİKLERİ")
        title.setStyleSheet("color:#c4b5fd;font-weight:700;font-size:12px;")
        layout.addWidget(title)

        self.empty_label = QLabel("Özelliklerini görmek için bir bileşen seç.")
        self.empty_label.setWordWrap(True)
        self.empty_label.setStyleSheet("color:#aaa3ba;")
        layout.addWidget(self.empty_label)

        form = QFormLayout()
        self.name_label = QLabel("—")
        self.value_edit = QLineEdit()
        self.value_edit.setPlaceholderText("Örn. 1000")
        self.unit_label = QLabel("—")
        form.addRow("Bileşen", self.name_label)
        form.addRow("Değer", self.value_edit)
        form.addRow("Birim", self.unit_label)
        layout.addLayout(form)
        layout.addStretch()

        self.value_edit.editingFinished.connect(self.apply_value)
        self.setStyleSheet("""
            QWidget { background:#201d2b; color:#e8e3f2; }
            QLineEdit { background:#302b3d; border:1px solid #494158; border-radius:5px; padding:6px; }
        """)
        self.set_item(None)

    def set_item(self, item):
        self.current_item = item
        if item is None:
            self.empty_label.show()
            self.name_label.setText("—")
            self.value_edit.setText("")
            self.value_edit.setEnabled(False)
            self.unit_label.setText("—")
            return

        self.empty_label.hide()
        self.name_label.setText(getattr(item, "name", "Direnç"))
        self.value_edit.setText(str(getattr(item, "value", "")))
        self.value_edit.setEnabled(hasattr(item, "set_value"))
        self.unit_label.setText(getattr(item, "unit", "Ω"))

    def apply_value(self):
        if self.current_item is not None and hasattr(self.current_item, "set_value"):
            self.current_item.set_value(self.value_edit.text().strip())
