import sys

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QDockWidget, QToolBar,
    QFileDialog, QMessageBox,
)
from PySide6.QtGui import QAction, QColor
from PySide6.QtCore import Qt

from settings import (
    WINDOW_HEIGHT, WINDOW_HEIGHT_MIN, WINDOW_TITLE,
    WINDOW_WIDTH, WINDOW_WIDTH_MIN,
)
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

        self.workspace = Workspace()
        self.setCentralWidget(self.workspace)

        self.component_library = ComponentLibrary()
        self.component_dock = QDockWidget("Bileşenler", self)
        self.component_dock.setObjectName("componentDock")
        self.component_dock.setWidget(self.component_library)
        self.component_dock.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea
        )
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.component_dock)

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

        self.current_file = None
        self.build_menus()

        toolbar = QToolBar("Tema", self)
        toolbar.setMovable(False)
        toolbar.setObjectName("themeToolbar")
        toolbar.setFloatable(False)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, toolbar)
        self.theme_switch = ThemeSwitch(dark=True)
        toolbar.addWidget(self.theme_switch)
        self.theme_switch.progress_changed.connect(self.apply_theme_progress)
        self.apply_theme_progress(1.0)

    def build_menus(self):
        file_menu = self.menuBar().addMenu("Dosya")
        actions = [
            ("Yeni devre", "Ctrl+N", self.new_circuit),
            ("Aç...", "Ctrl+O", self.open_circuit),
            ("Kaydet", "Ctrl+S", self.save_circuit),
            ("Farklı kaydet...", None, self.save_circuit_as),
        ]
        for label, shortcut, callback in actions:
            action = QAction(label, self)
            if shortcut:
                action.setShortcut(shortcut)
            action.triggered.connect(callback)
            file_menu.addAction(action)

        circuit_menu = self.menuBar().addMenu("Devre")
        analyze = QAction("Bağlantıları denetle", self)
        analyze.triggered.connect(self.check_connections)
        circuit_menu.addAction(analyze)

        simulation_menu = self.menuBar().addMenu("Simülasyon")
        solve = QAction("DC çalışma noktası", self)
        solve.triggered.connect(self.run_dc_simulation)
        simulation_menu.addAction(solve)

        view_menu = self.menuBar().addMenu("Görünüm")
        view_menu.addAction(self.component_dock.toggleViewAction())
        view_menu.addAction(self.properties_dock.toggleViewAction())

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
        colors = {
            key: self.blend_color(LIGHT[key], DARK[key], amount)
            for key in DARK
        }
        set_current(colors)
        self.workspace.apply_theme(colors)

        self.setStyleSheet(f"""
            QMainWindow, QWidget#componentLibrary, QWidget#propertiesPanel {{
                background: {colors["panel"]};
                color: {colors["text"]};
            }}
            QMenuBar {{
                background: {colors["window"]};
                color: {colors["text"]};
                padding: 3px 5px;
            }}
            QMenuBar::item:selected, QMenu::item:selected {{
                background: {colors["hover"]};
            }}
            QMenu {{
                background: {colors["panel"]};
                color: {colors["text"]};
                border: 1px solid {colors["border"]};
                padding: 4px;
            }}
            QToolBar#themeToolbar {{
                background: {colors["window"]};
                border: none;
                spacing: 8px;
                padding: 2px 10px;
            }}
            QDockWidget {{
                color: {colors["text"]};
                font-size: 12px;
            }}
            QDockWidget::title {{
                background: {colors["window"]};
                padding: 7px 9px;
                border-bottom: 1px solid {colors["border"]};
            }}
            QLineEdit#componentSearch, QLineEdit {{
                background: {colors["panel_alt"]};
                color: {colors["text"]};
                border: 1px solid {colors["border"]};
                border-radius: 7px;
                padding: 7px 9px;
                selection-background-color: {colors["accent"]};
            }}
            QLabel#sectionTitle {{
                color: {colors["muted"]};
                font-size: 10px;
                font-weight: 600;
                padding: 8px 2px 3px 2px;
            }}
            QPushButton#componentButton {{
                background: transparent;
                color: {colors["text"]};
                border: 1px solid transparent;
                border-radius: 6px;
                padding: 8px 10px;
                text-align: left;
            }}
            QPushButton#componentButton:hover {{
                background: {colors["hover"]};
                border-color: {colors["border"]};
            }}
            QScrollArea {{ border: none; background: transparent; }}
            QToolTip {{
                background: {colors["panel_alt"]};
                color: {colors["text"]};
                border: 1px solid {colors["border"]};
                padding: 4px;
            }}
        """)

    def check_connections(self):
        QMessageBox.information(
            self, "Bağlantı analizi",
            format_netlist_report(self.workspace.circuit_scene),
        )

    def run_dc_simulation(self):
        try:
            QMessageBox.information(
                self, "DC çalışma noktası",
                format_dc_report(self.workspace.circuit_scene),
            )
        except (ValueError, ZeroDivisionError) as error:
            QMessageBox.warning(self, "DC çözümü yapılamadı", str(error))

    def new_circuit(self):
        self.workspace.circuit_scene.clear()
        self.workspace.history.undo_stack.clear()
        self.workspace.history.redo_stack.clear()
        self.current_file = None
        self.setWindowTitle(WINDOW_TITLE)
        self.update_properties()

    def open_circuit(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Devre aç", "", "Physics Devreleri (*.physics);;JSON (*.json)"
        )
        if not file_path:
            return
        try:
            load_circuit(self.workspace.circuit_scene, file_path)
            self.workspace.history.undo_stack.clear()
            self.workspace.history.redo_stack.clear()
            self.current_file = file_path
            self.setWindowTitle(f"{WINDOW_TITLE} — {file_path}")
            self.update_properties()
        except (OSError, ValueError, KeyError, TypeError, IndexError, AttributeError) as error:
            QMessageBox.critical(self, "Devre açılamadı", str(error))

    def save_circuit(self):
        if self.current_file is None:
            self.save_circuit_as()
            return
        try:
            save_circuit(self.workspace.circuit_scene, self.current_file)
        except OSError as error:
            QMessageBox.critical(self, "Kaydedilemedi", str(error))

    def save_circuit_as(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Devreyi kaydet", "", "Physics Devreleri (*.physics)"
        )
        if not file_path:
            return
        if not file_path.lower().endswith(".physics"):
            file_path += ".physics"
        try:
            save_circuit(self.workspace.circuit_scene, file_path)
        except OSError as error:
            QMessageBox.critical(self, "Kaydedilemedi", str(error))
            return
        self.current_file = file_path
        self.setWindowTitle(f"{WINDOW_TITLE} — {file_path}")

    def update_properties(self):
        selected = self.workspace.circuit_scene.selectedItems()
        item = selected[0] if len(selected) == 1 else None
        self.properties_panel.set_item(
            item if getattr(item, "component_id", None) != "wire" else None
        )


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
