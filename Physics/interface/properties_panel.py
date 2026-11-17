from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QFormLayout
from PySide6.QtCore import Signal


class PropertiesPanel(QWidget):
    value_change_requested = Signal(object, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("propertiesPanel")
        self.current_item = None
        self.setMinimumWidth(210)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        title = QLabel("ÖZELLİKLER")
        title.setObjectName("propertiesTitle")
        layout.addWidget(title)

        form = QFormLayout()
        self.name_label = QLabel("—")
        self.value_edit = QLineEdit()
        self.value_edit.setPlaceholderText("—")
        self.unit_label = QLabel("—")
        form.addRow("Bileşen", self.name_label)
        form.addRow("Değer", self.value_edit)
        form.addRow("Birim", self.unit_label)
        layout.addLayout(form)
        layout.addStretch()

        self.value_edit.editingFinished.connect(self.apply_value)
        self.set_item(None)

    def set_item(self, item):
        self.current_item = item
        if item is None:
            self.name_label.setText("—")
            self.value_edit.setText("")
            self.value_edit.setEnabled(False)
            self.unit_label.setText("—")
            return

        self.name_label.setText(getattr(item, "name", "—"))
        self.value_edit.setText(str(getattr(item, "value", "")))
        self.value_edit.setEnabled(hasattr(item, "set_value"))
        self.unit_label.setText(getattr(item, "unit", "—"))

    def apply_value(self):
        if self.current_item is not None and hasattr(self.current_item, "set_value"):
            self.value_change_requested.emit(
                self.current_item, self.value_edit.text().strip()
            )
