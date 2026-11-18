from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QFrame
from PySide6.QtCore import Signal, Qt


class PropertiesPanel(QWidget):
    value_change_requested = Signal(object, str)
    name_change_requested = Signal(object, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("propertiesPanel")
        self.root = QVBoxLayout(self)
        self.root.setContentsMargins(8, 8, 8, 8)
        self.root.setSpacing(8)

    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            child_layout = item.layout()
            if widget is not None:
                widget.hide()
                widget.setParent(None)
                widget.deleteLater()
            elif child_layout is not None:
                self._clear_layout(child_layout)
                child_layout.deleteLater()

    def clear_rows(self):
        self._clear_layout(self.root)

    def set_items(self, items, simulation_result=None):
        self.clear_rows()
        grouped = {}
        for item in items:
            component_id = getattr(item, "component_id", None)
            if component_id and component_id != "wire":
                grouped.setdefault(component_id, []).append(item)

        for index, (component_id, group_items) in enumerate(grouped.items()):
            heading = QLabel(getattr(group_items[0], "name", component_id))
            heading.setObjectName("propertyGroupTitle")
            self.root.addWidget(heading)
            self._add_name_row(group_items)

            if all(hasattr(item, "set_value") for item in group_items):
                self._add_value_row(group_items)
            if component_id == "switch":
                states = {bool(getattr(item, "closed", False)) for item in group_items}
                state_text = ("Kapalı" if True in states else "Açık") if len(states) == 1 else "Karışık"
                self._add_static_row("Durum", state_text)

            unit = getattr(group_items[0], "unit", "")
            if unit:
                self._add_static_row("Birim", unit)

            if index < len(grouped) - 1:
                separator = QFrame()
                separator.setFrameShape(QFrame.Shape.HLine)
                separator.setFrameShadow(QFrame.Shadow.Plain)
                separator.setObjectName("propertySeparator")
                self.root.addWidget(separator)
        measurements = (simulation_result or {}).get("component_measurements", {})
        for item in items:
            measured = measurements.get(getattr(item, "instance_id", None))
            if not measured:
                continue
            heading = QLabel("Son DC ölçümü")
            heading.setObjectName("propertyGroupTitle")
            self.root.addWidget(heading)
            for label, value_text in measured.items():
                self._add_static_row(label, value_text)
        self.root.addStretch(1)

    def _add_name_row(self, items):
        row = QHBoxLayout()
        row.addWidget(QLabel("Ad:"))
        edit = QLineEdit()
        edit.setFrame(False)
        edit.setObjectName("inlinePropertyValue")
        edit.setAlignment(Qt.AlignmentFlag.AlignLeft)
        names = {str(getattr(item, "name", getattr(item, "component_id", ""))) for item in items}
        if len(names) == 1:
            edit.setText(next(iter(names)))
        else:
            edit.setPlaceholderText("Farklı adlar")
        edit.editingFinished.connect(lambda selected=tuple(items), field=edit: self._apply_name(selected, field))
        row.addWidget(edit, 1)
        self.root.addLayout(row)

    def _add_value_row(self, items):
        row = QHBoxLayout()
        row.addWidget(QLabel("Değer:"))
        edit = QLineEdit()
        edit.setFrame(False)
        edit.setClearButtonEnabled(False)
        edit.setAlignment(Qt.AlignmentFlag.AlignLeft)
        edit.setObjectName("inlinePropertyValue")
        values = {str(getattr(item, "value", "")) for item in items}
        if len(values) == 1:
            edit.setText(next(iter(values)))
        else:
            edit.setPlaceholderText("Farklı değerler")
        edit.editingFinished.connect(lambda selected=tuple(items), field=edit: self._apply_value(selected, field))
        row.addWidget(edit, 1)
        self.root.addLayout(row)

    def _add_static_row(self, label_text, value_text):
        row = QHBoxLayout()
        row.addWidget(QLabel(f"{label_text}:"))
        value = QLabel(value_text)
        value.setObjectName("propertyStaticValue")
        row.addWidget(value, 1)
        self.root.addLayout(row)

    def _apply_name(self, items, field):
        name = field.text().strip()
        if name:
            self.name_change_requested.emit(list(items), name)

    def _apply_value(self, items, field):
        value = field.text().strip()
        if value:
            self.value_change_requested.emit(list(items), value)

    def set_item(self, item):
        self.set_items([item] if item is not None else [])
