import sys

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QDockWidget, QToolBar, QWidget,
    QVBoxLayout, QFileDialog, QMessageBox, QInputDialog,
)
from PySide6.QtGui import QAction, QColor
from PySide6.QtCore import Qt

from settings import WINDOW_HEIGHT, WINDOW_HEIGHT_MIN, WINDOW_TITLE, WINDOW_WIDTH, WINDOW_WIDTH_MIN
from interface.workspace import Workspace
from interface.component_library import ComponentLibrary
from interface.properties_panel import PropertiesPanel
from interface.theme_switch import ThemeSwitch
from core.project_io import save_circuit, load_circuit
from circuit.netlist import format_netlist_report
from simulation.dc_solver import format_dc_report
from theme import DARK, LIGHT, set_current


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(WINDOW_TITLE)
        self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.setMinimumSize(WINDOW_WIDTH_MIN, WINDOW_HEIGHT_MIN)
        self.menuBar().hide()
        self.current_file = None
        self.circuit_name = "Yeni devre"

        central = QWidget()
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.workspace = Workspace()
        self.component_library = ComponentLibrary()
        layout.addWidget(self.workspace, 1)
        layout.addWidget(self.component_library, 0)
        self.setCentralWidget(central)

        self.properties_panel = PropertiesPanel()
        self.properties_dock = QDockWidget("Özellikler", self)
        self.properties_dock.setObjectName("propertiesDock")
        self.properties_dock.setWidget(self.properties_panel)
        self.properties_dock.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea
        )
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.properties_dock)

        self.workspace.circuit_scene.selectionChanged.connect(self.update_properties)
        self.workspace.history_changed.connect(self.update_properties)
        self.properties_panel.value_change_requested.connect(self.workspace.set_component_value)
        self.properties_panel.name_change_requested.connect(self.workspace.set_component_name)
        self.component_library.add_requested.connect(self.add_component_from_palette)
        self.component_library.menu_action.connect(self.handle_palette_menu)
        self.workspace.component_dropped.connect(self.component_library.collapse)

        toolbar = QToolBar("Tema", self)
        toolbar.setMovable(False)
        toolbar.setFloatable(False)
        toolbar.setObjectName("themeToolbar")
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, toolbar)
        self.theme_switch = ThemeSwitch(dark=True)
        toolbar.addWidget(self.theme_switch)
        self.theme_switch.progress_changed.connect(self.apply_theme_progress)
        self.apply_theme_progress(1.0)

    def add_component_from_palette(self, component_id, shift):
        if shift:
            index = self.component_library.shift_add_count
            if self.workspace.add_component(component_id, True, index):
                self.component_library.shift_add_count += 1
        else:
            self.workspace.add_component(component_id, False, 0)

    def handle_palette_menu(self, action):
        actions = {
            "new": self.new_circuit,
            "rename": self.rename_circuit,
            "open": self.open_circuit,
            "save": self.save_circuit,
            "save_as": self.save_circuit_as,
            "check": self.check_connections,
            "simulate": self.run_dc_simulation,
        }
        callback = actions.get(action)
        if callback:
            callback()

    @staticmethod
    def blend_color(first, second, amount):
        a, b = QColor(first), QColor(second)
        return QColor(
            round(a.red() + (b.red() - a.red()) * amount),
            round(a.green() + (b.green() - a.green()) * amount),
            round(a.blue() + (b.blue() - a.blue()) * amount),
        ).name()

    def apply_theme_progress(self, progress):
        amount = max(0.0, min(1.0, progress))
        colors = {key: self.blend_color(LIGHT[key], DARK[key], amount) for key in DARK}
        set_current(colors)
        self.workspace.apply_theme(colors)
        self.component_library.apply_theme(colors)
        self.setStyleSheet(f"""
            QMainWindow, QWidget#componentLibrary, QWidget#propertiesPanel {{
                background: {colors["panel"]};
                color: {colors["text"]};
            }}
            QWidget#componentDrawer, QWidget#componentItemsHost {{
                background: {colors["panel_alt"]};
                color: {colors["text"]};
            }}
            QWidget, QLabel, QLineEdit, QPushButton, QMenu, QDockWidget {{
                color: {colors["text"]};
            }}
            QLabel#propertyStaticValue {{
                color: {colors["text"]};
            }}
            QToolBar#themeToolbar {{
                background: {colors["window"]};
                border: none;
                padding: 2px 8px;
            }}
            QDockWidget {{ color: {colors["text"]}; }}
            QDockWidget::title {{
                background: {colors["window"]};
                color: {colors["text"]};
                padding: 6px 8px;
                border: none;
            }}
            QPushButton#paletteTab, QPushButton#paletteMenuButton {{
                background: transparent;
                color: {colors["text"]};
                border: none;
                border-right: 1px solid {colors["border"]};
                padding: 7px 13px;
            }}
            QPushButton#paletteMenuButton::menu-indicator {{ image: none; width: 0px; }}
            QPushButton#paletteTab:hover, QPushButton#paletteMenuButton:hover {{
                background: {colors["hover"]};
            }}
            QPushButton#paletteTab:checked {{
                background: {colors["hover"]};
                border-bottom: 2px solid {colors["accent"]};
            }}
            QPushButton#componentButton {{
                background: {colors["panel"]};
                color: {colors["text"]};
                border: 1px solid {colors["border"]};
                border-radius: 0px;
                padding: 7px 12px;
                min-width: 0px;
            }}
            QPushButton#componentButton:hover {{
                background: {colors["hover"]};
            }}
            QScrollBar:vertical {{
                width: 8px;
                background: {colors["panel"]};
                border: none;
            }}
            QScrollBar:vertical {{ width: 8px; }}
            QScrollBar::handle:vertical {{
                background: {colors["muted"]};
                min-height: 25px;
            }}
            QLineEdit#inlinePropertyValue {{
                background: transparent;
                color: {colors["text"]};
                border: none;
                border-bottom: 1px solid transparent;
                padding: 1px 0;
            }}
            QLineEdit#inlinePropertyValue:focus {{
                border-bottom: 1px solid {colors["accent"]};
            }}
            QLabel#propertyGroupTitle {{
                color: {colors["text"]};
                font-weight: 600;
                padding-top: 4px;
            }}
            QFrame, QFrame#propertySeparator {{
                color: {colors["border"]};
                background: transparent;
            }}
            QLineEdit#inlinePropertyValue::placeholder {{
                color: {colors["muted"]};
            }}
            QMenu {{
                background: {colors["panel"]};
                color: {colors["text"]};
                border: 1px solid {colors["border"]};
                padding: 4px;
            }}
            QMenu::item:selected {{ background: {colors["hover"]}; }}
            QToolTip {{
                background: {colors["panel_alt"]};
                color: {colors["text"]};
                border: 1px solid {colors["border"]};
            }}
        """)

    def rename_circuit(self):
        name, accepted = QInputDialog.getText(self, "Devreyi yeniden adlandır", "Devre adı:", text=self.circuit_name)
        name = name.strip()
        if not accepted or not name:
            return
        self.circuit_name = name
        self._update_window_title()

    def _update_window_title(self):
        suffix = f" — {self.current_file}" if self.current_file else ""
        self.setWindowTitle(f"{WINDOW_TITLE} · {self.circuit_name}{suffix}")

    def check_connections(self):
        QMessageBox.information(self, "Bağlantı analizi", format_netlist_report(self.workspace.circuit_scene))

    def run_dc_simulation(self):
        try:
            QMessageBox.information(self, "DC çalışma noktası", format_dc_report(self.workspace.circuit_scene))
        except (ValueError, ZeroDivisionError) as error:
            QMessageBox.warning(self, "DC çözümü yapılamadı", str(error))

    def new_circuit(self):
        self.workspace.circuit_scene.clear()
        self.workspace.history.undo_stack.clear()
        self.workspace.history.redo_stack.clear()
        self.current_file = None
        self.circuit_name = "Yeni devre"
        self._update_window_title()
        self.update_properties()

    def open_circuit(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Devre aç", "", "Physics Devreleri (*.physics);;JSON (*.json)")
        if not file_path:
            return
        try:
            self.circuit_name = load_circuit(self.workspace.circuit_scene, file_path)
            self.workspace.history.undo_stack.clear()
            self.workspace.history.redo_stack.clear()
            self.current_file = file_path
            self._update_window_title()
            self.update_properties()
        except (OSError, ValueError, KeyError, TypeError, IndexError, AttributeError) as error:
            QMessageBox.critical(self, "Devre açılamadı", str(error))

    def save_circuit(self):
        if self.current_file is None:
            self.save_circuit_as()
            return
        try:
            save_circuit(self.workspace.circuit_scene, self.current_file, self.circuit_name)
        except OSError as error:
            QMessageBox.critical(self, "Kaydedilemedi", str(error))

    def save_circuit_as(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Devreyi kaydet", "", "Physics Devreleri (*.physics)")
        if not file_path:
            return
        if not file_path.lower().endswith(".physics"):
            file_path += ".physics"
        try:
            save_circuit(self.workspace.circuit_scene, file_path, self.circuit_name)
        except OSError as error:
            QMessageBox.critical(self, "Kaydedilemedi", str(error))
            return
        self.current_file = file_path
        self._update_window_title()

    def update_properties(self):
        self.properties_panel.set_items(self.workspace.circuit_scene.selectedItems())


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
