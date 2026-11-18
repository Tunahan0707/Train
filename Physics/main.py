import sys
import uuid

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QDockWidget, QToolBar, QWidget,
    QVBoxLayout, QFileDialog, QMessageBox, QInputDialog,
    QTabWidget, QToolButton,
)
from PySide6.QtGui import QColor
from PySide6.QtCore import Qt

from settings import WINDOW_HEIGHT, WINDOW_HEIGHT_MIN, WINDOW_TITLE, WINDOW_WIDTH, WINDOW_WIDTH_MIN
from interface.workspace import Workspace
from interface.component_library import ComponentLibrary
from interface.properties_panel import PropertiesPanel
from interface.theme_switch import ThemeSwitch
from core.project_io import save_project, load_project
from circuit.netlist import format_netlist_report
from simulation.dc_solver import format_dc_report, solve_dc_operating_point
from theme import DARK, LIGHT, set_current


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(WINDOW_TITLE)
        self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.setMinimumSize(WINDOW_WIDTH_MIN, WINDOW_HEIGHT_MIN)
        self.menuBar().hide()
        self.current_file = None
        self.workspace = None
        self.component_library = None
        self.circuit_name = "Devre 1"
        self.current_theme_colors = None
        self.simulation_results = {}
        self.is_dirty = False

        central = QWidget()
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.tabs = QTabWidget()
        self.tabs.setObjectName("circuitTabs")
        self.tabs.setMovable(True)
        self.tabs.setTabsClosable(True)
        self.tabs.currentChanged.connect(self.activate_circuit_tab)
        self.tabs.tabCloseRequested.connect(self.close_circuit_tab)
        self.add_tab_button = QToolButton()
        self.add_tab_button.setText("+")
        self.add_tab_button.setToolTip("Yeni devre ekle")
        self.add_tab_button.clicked.connect(self.new_circuit)
        self.tabs.setCornerWidget(self.add_tab_button, Qt.Corner.TopRightCorner)
        layout.addWidget(self.tabs, 1)
        self.setCentralWidget(central)

        self.properties_panel = PropertiesPanel()
        self.properties_dock = QDockWidget("Özellikler", self)
        self.properties_dock.setObjectName("propertiesDock")
        self.properties_dock.setWidget(self.properties_panel)
        self.properties_dock.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea
        )
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.properties_dock)

        self.properties_panel.value_change_requested.connect(self._set_component_value)
        self.properties_panel.name_change_requested.connect(self._set_component_name)
        self.properties_panel.wiper_change_requested.connect(self._set_component_wiper)

        toolbar = QToolBar("Tema", self)
        toolbar.setMovable(False)
        toolbar.setFloatable(False)
        toolbar.setObjectName("themeToolbar")
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, toolbar)
        self.theme_switch = ThemeSwitch(dark=True)
        toolbar.addWidget(self.theme_switch)
        self.theme_switch.progress_changed.connect(self.apply_theme_progress)

        self._add_circuit_tab("Devre 1", select=True)
        self.apply_theme_progress(1.0)

    def _add_circuit_tab(self, name, circuit_id=None, items=None, select=True):
        page = QWidget()
        page.circuit_id = str(circuit_id or uuid.uuid4())
        page.circuit_name = str(name or "Devre")
        page.content_layout = QVBoxLayout(page)
        page.content_layout.setContentsMargins(0, 0, 0, 0)
        page.content_layout.setSpacing(0)
        page.workspace = Workspace(page)
        page.component_library = ComponentLibrary(page)
        page.content_layout.addWidget(page.workspace, 1)
        page.content_layout.addWidget(page.component_library, 0)
        for item in items or []:
            page.workspace.circuit_scene.addItem(item)

        page.workspace.circuit_scene.selectionChanged.connect(self.update_properties)
        page.workspace.history_changed.connect(lambda circuit_id=page.circuit_id: self.invalidate_simulation(circuit_id))
        page.workspace.history_changed.connect(self.mark_dirty)
        page.workspace.history_changed.connect(self.update_properties)
        page.component_library.add_requested.connect(
            lambda component_id, shift, workspace=page.workspace, library=page.component_library:
                self.add_component_from_palette(component_id, shift, workspace, library)
        )
        page.component_library.menu_action.connect(self.handle_palette_menu)
        page.workspace.component_dropped.connect(page.component_library.collapse)

        index = self.tabs.addTab(page, page.circuit_name)
        if self.current_theme_colors is not None:
            page.workspace.apply_theme(self.current_theme_colors)
            page.component_library.apply_theme(self.current_theme_colors)
        if select:
            self.tabs.setCurrentIndex(index)
        return page

    def activate_circuit_tab(self, index):
        if index < 0 or index >= self.tabs.count():
            self.workspace = None
            self.component_library = None
            self.properties_panel.clear_rows()
            return
        page = self.tabs.widget(index)
        self.workspace = page.workspace
        self.component_library = page.component_library
        self.circuit_name = page.circuit_name
        self.update_properties()
        self._update_window_title()

    def close_circuit_tab(self, index):
        if index < 0 or index >= self.tabs.count():
            return
        page = self.tabs.widget(index)
        answer = QMessageBox.question(
            self, "Devreyi kapat", f'"{page.circuit_name}" devresi projeden kaldırılsın mı?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        self.simulation_results.pop(page.circuit_id, None)
        self.mark_dirty()
        if self.tabs.count() == 1:
            page.workspace.circuit_scene.clear()
            page.workspace.history.undo_stack.clear()
            page.workspace.history.redo_stack.clear()
            page.circuit_id = str(uuid.uuid4())
            page.circuit_name = "Devre 1"
            self.tabs.setTabText(index, page.circuit_name)
            self.tabs.setCurrentIndex(index)
            self.activate_circuit_tab(index)
            return
        removed = self.tabs.widget(index)
        self.tabs.removeTab(index)
        removed.deleteLater()
        self.activate_circuit_tab(self.tabs.currentIndex())

    def add_component_from_palette(self, component_id, shift, workspace=None, library=None):
        workspace = workspace or self.workspace
        library = library or self.component_library
        if workspace is None or library is None:
            return
        if shift:
            index = library.shift_add_count
            if workspace.add_component(component_id, True, index):
                library.shift_add_count += 1
        else:
            workspace.add_component(component_id, False, 0)

    def _set_component_value(self, items, value):
        if self.workspace is not None:
            self.workspace.set_component_value(items, value)

    def _set_component_name(self, items, name):
        if self.workspace is not None:
            self.workspace.set_component_name(items, name)

    def _set_component_wiper(self, items, position):
        if self.workspace is not None:
            self.workspace.set_component_wiper_position(items, position)

    def handle_palette_menu(self, action):
        actions = {
            "new": self.new_circuit,
            "duplicate": self.duplicate_circuit,
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
        self.current_theme_colors = colors
        set_current(colors)
        for index in range(self.tabs.count()):
            page = self.tabs.widget(index)
            page.workspace.apply_theme(colors)
            page.component_library.apply_theme(colors)
        self.setStyleSheet(f"""
            QMainWindow, QWidget#componentLibrary, QWidget#propertiesPanel {{
                background: {colors["panel"]};
                color: {colors["text"]};
            }}
            QWidget#componentDrawer, QWidget#componentItemsHost {{
                background: {colors["panel_alt"]};
                color: {colors["text"]};
            }}
            QWidget, QLabel, QLineEdit, QPushButton, QMenu, QDockWidget, QTabBar {{
                color: {colors["text"]};
            }}
            QTabWidget::pane {{ border: none; background: {colors["panel"]}; }}
            QTabBar::tab {{ background: {colors["panel_alt"]}; padding: 7px 14px; border: none; }}
            QTabBar::tab:selected {{ background: {colors["hover"]}; border-bottom: 2px solid {colors["accent"]}; }}
            QToolButton {{ background: {colors["panel_alt"]}; border: none; padding: 4px 10px; }}
            QLabel#propertyStaticValue {{ color: {colors["text"]}; }}
            QToolBar#themeToolbar {{ background: {colors["window"]}; border: none; padding: 2px 8px; }}
            QDockWidget {{ color: {colors["text"]}; }}
            QDockWidget::title {{ background: {colors["window"]}; color: {colors["text"]}; padding: 6px 8px; border: none; }}
            QPushButton#paletteTab, QPushButton#paletteMenuButton {{
                background: transparent; color: {colors["text"]}; border: none;
                border-right: 1px solid {colors["border"]}; padding: 7px 13px;
            }}
            QPushButton#paletteMenuButton::menu-indicator {{ image: none; width: 0px; }}
            QPushButton#paletteTab:hover, QPushButton#paletteMenuButton:hover {{ background: {colors["hover"]}; }}
            QPushButton#paletteTab:checked {{ background: {colors["hover"]}; border-bottom: 2px solid {colors["accent"]}; }}
            QPushButton#componentButton {{
                background: {colors["panel"]}; color: {colors["text"]}; border: 1px solid {colors["border"]};
                border-radius: 0px; padding: 7px 12px; min-width: 0px;
            }}
            QPushButton#componentButton:hover {{ background: {colors["hover"]}; }}
            QScrollBar:vertical {{ width: 8px; background: {colors["panel"]}; border: none; }}
            QScrollBar::handle:vertical {{ background: {colors["muted"]}; min-height: 25px; }}
            QLineEdit#inlinePropertyValue {{
                background: transparent; color: {colors["text"]}; border: none;
                border-bottom: 1px solid transparent; padding: 1px 0;
            }}
            QLineEdit#inlinePropertyValue:focus {{ border-bottom: 1px solid {colors["accent"]}; }}
            QLabel#propertyGroupTitle {{ color: {colors["text"]}; font-weight: 600; padding-top: 4px; }}
            QFrame, QFrame#propertySeparator {{ color: {colors["border"]}; background: transparent; }}
            QLineEdit#inlinePropertyValue::placeholder {{ color: {colors["muted"]}; }}
            QMenu {{ background: {colors["panel"]}; color: {colors["text"]}; border: 1px solid {colors["border"]}; padding: 4px; }}
            QMenu::item:selected {{ background: {colors["hover"]}; }}
            QToolTip {{ background: {colors["panel_alt"]}; color: {colors["text"]}; border: 1px solid {colors["border"]}; }}
        """)

    def rename_circuit(self):
        page = self.tabs.currentWidget()
        if page is None:
            return
        name, accepted = QInputDialog.getText(
            self, "Devreyi yeniden adlandır", "Devre adı:", text=page.circuit_name
        )
        name = name.strip()
        if not accepted or not name:
            return
        page.circuit_name = name
        self.tabs.setTabText(self.tabs.currentIndex(), name)
        self.circuit_name = name
        self.mark_dirty()
        self._update_window_title()

    def _update_window_title(self):
        page = self.tabs.currentWidget() if hasattr(self, "tabs") else None
        active_name = page.circuit_name if page is not None else self.circuit_name
        suffix = f" — {self.current_file}" if self.current_file else ""
        dirty_mark = "*" if getattr(self, "is_dirty", False) else ""
        self.setWindowTitle(f"{dirty_mark}{WINDOW_TITLE} · {active_name}{suffix}")

    def new_circuit(self):
        name = f"Devre {self.tabs.count() + 1}"
        self._add_circuit_tab(name, select=True)
        self.mark_dirty()

    def duplicate_circuit(self):
        source = self.tabs.currentWidget()
        if source is None:
            return
        snapshots = source.workspace._capture_items(source.workspace.circuit_scene.items())
        copies, positions = source.workspace._create_item_copies(snapshots, 40)
        for item, position in positions.items():
            item.setPos(position)
        self._add_circuit_tab(f"{source.circuit_name} kopya", items=copies, select=True)
        self.mark_dirty()

    def _collect_circuits(self):
        return [
            {
                "id": self.tabs.widget(index).circuit_id,
                "name": self.tabs.widget(index).circuit_name,
                "scene": self.tabs.widget(index).workspace.circuit_scene,
            }
            for index in range(self.tabs.count())
        ]

    def invalidate_simulation(self, circuit_id):
        self.simulation_results.pop(circuit_id, None)

    def check_connections(self):
        if self.workspace is None:
            return
        QMessageBox.information(self, "Bağlantı analizi", format_netlist_report(self.workspace.circuit_scene))

    def run_dc_simulation(self):
        if self.workspace is None:
            return
        try:
            page = self.tabs.currentWidget()
            result = solve_dc_operating_point(self.workspace.circuit_scene)
            self.simulation_results[page.circuit_id] = result
            self.update_properties()
            QMessageBox.information(self, "DC çalışma noktası", format_dc_report(result=result))
        except (ValueError, ZeroDivisionError) as error:
            if self.tabs.currentWidget() is not None:
                self.simulation_results.pop(self.tabs.currentWidget().circuit_id, None)
                self.update_properties()
            QMessageBox.warning(self, "DC çözümü yapılamadı", str(error))

    def open_circuit(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Physics projesi aç", "", "Physics Projeleri (*.physics);;JSON (*.json)"
        )
        if not file_path:
            return
        try:
            project = load_project(file_path)
        except (OSError, ValueError, KeyError, TypeError, IndexError, AttributeError) as error:
            QMessageBox.critical(self, "Proje açılamadı", str(error))
            return

        self.simulation_results.clear()
        while self.tabs.count():
            page = self.tabs.widget(0)
            self.tabs.removeTab(0)
            page.deleteLater()
        for entry in project["circuits"]:
            self._add_circuit_tab(entry["name"], entry["id"], entry["items"], select=False)
        active_index = next(
            (index for index in range(self.tabs.count())
             if self.tabs.widget(index).circuit_id == project["active_circuit_id"]),
            0,
        )
        self.current_file = file_path
        self.is_dirty = False
        self.tabs.setCurrentIndex(active_index)
        self.activate_circuit_tab(active_index)
        self.apply_theme_progress(self.theme_switch.position)

    def save_circuit(self):
        if self.current_file is None:
            self.save_circuit_as()
            return
        try:
            active = self.tabs.currentWidget()
            save_project(self._collect_circuits(), self.current_file, active.circuit_id if active else None)
            self.is_dirty = False
            self._update_window_title()
        except (OSError, ValueError) as error:
            QMessageBox.critical(self, "Kaydedilemedi", str(error))

    def save_circuit_as(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Physics projesini kaydet", "", "Physics Projeleri (*.physics)")
        if not file_path:
            return
        if not file_path.lower().endswith(".physics"):
            file_path += ".physics"
        try:
            active = self.tabs.currentWidget()
            save_project(self._collect_circuits(), file_path, active.circuit_id if active else None)
        except (OSError, ValueError) as error:
            QMessageBox.critical(self, "Kaydedilemedi", str(error))
            return
        self.current_file = file_path
        self.is_dirty = False
        self._update_window_title()

    def mark_dirty(self):
        if not self.is_dirty:
            self.is_dirty = True
            self._update_window_title()

    def closeEvent(self, event):
        if not self.is_dirty:
            event.accept()
            return
        answer = QMessageBox.question(
            self, "Kaydedilmemiş değişiklikler",
            "Projede kaydedilmemiş değişiklikler var. Kaydedilsin mi?",
            QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Save,
        )
        if answer == QMessageBox.StandardButton.Cancel:
            event.ignore()
            return
        if answer == QMessageBox.StandardButton.Save:
            self.save_circuit()
            if self.is_dirty:
                event.ignore()
                return
        event.accept()

    def update_properties(self):
        if self.workspace is None:
            self.properties_panel.clear_rows()
            return
        page = self.tabs.currentWidget()
        result = self.simulation_results.get(page.circuit_id) if page is not None else None
        self.properties_panel.set_items(self.workspace.circuit_scene.selectedItems(), result)


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
