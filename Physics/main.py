import sys

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QDockWidget,
    QToolBar,
)
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtCore import Qt, QEvent, QSignalBlocker

from settings import (
    WINDOW_HEIGHT,
    WINDOW_HEIGHT_MIN,
    WINDOW_TITLE,
    WINDOW_WIDTH,
    WINDOW_WIDTH_MIN,
    COLOR_WINDOW_BACKGROUND,
    SHORTCUT_FULLSCREEN,
)

from interface.workspace import Workspace
from interface.component_library import ComponentLibrary
from interface.properties_panel import PropertiesPanel


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle(WINDOW_TITLE)
        self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.setMinimumSize(WINDOW_WIDTH_MIN, WINDOW_HEIGHT_MIN)

        # Ana çalışma alanı
        self.workspace = Workspace()
        self.setCentralWidget(self.workspace)

        # Bileşen kütüphanesi
        self.component_library = ComponentLibrary()
        self.component_dock = QDockWidget("Bileşenler", self)
        self.component_dock.setObjectName("componentDock")
        self.component_dock.setWidget(self.component_library)
        self.component_dock.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea
            | Qt.DockWidgetArea.RightDockWidgetArea
        )
        self.component_dock.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetMovable
            | QDockWidget.DockWidgetFeature.DockWidgetFloatable
            | QDockWidget.DockWidgetFeature.DockWidgetClosable
        )
        self.addDockWidget(
            Qt.DockWidgetArea.LeftDockWidgetArea,
            self.component_dock,
        )

        self.properties_panel = PropertiesPanel()
        self.properties_dock = QDockWidget("Özellikler", self)
        self.properties_dock.setObjectName("propertiesDock")
        self.properties_dock.setWidget(self.properties_panel)
        self.properties_dock.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea
        )
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.properties_dock)
        self.workspace.circuit_scene.selectionChanged.connect(self.update_properties)

        self.component_library.component_requested.connect(
            self.workspace.start_placement
        )
        self.component_library.placement_cancelled.connect(
            self.workspace.cancel_placement
        )
        self.workspace.placement_changed.connect(
            self.on_placement_changed
        )

        # Üst araç çubuğu
        toolbar = QToolBar("Ana araç çubuğu", self)
        toolbar.setMovable(False)
        toolbar.setObjectName("mainToolbar")
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, toolbar)

        self.fullscreen_action = QAction("Tam ekran", self)
        self.fullscreen_action.setCheckable(True)
        self.fullscreen_action.setShortcut(
            QKeySequence(SHORTCUT_FULLSCREEN)
        )
        self.fullscreen_action.setShortcutContext(
            Qt.ShortcutContext.ApplicationShortcut
        )
        self.fullscreen_action.toggled.connect(
            self.set_fullscreen
        )
        toolbar.addAction(self.fullscreen_action)

        # Görünüm menüsü
        view_menu = self.menuBar().addMenu("Görünüm")
        view_menu.addAction(self.fullscreen_action)
        view_menu.addSeparator()
        view_menu.addAction(self.component_dock.toggleViewAction())
        view_menu.addAction(self.properties_dock.toggleViewAction())

        # Durum çubuğu
        self.statusBar().showMessage(
            "Hazır  |  Orta tuş: seçim  |  Shift + orta tuş: kaydırma"
        )

        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {COLOR_WINDOW_BACKGROUND};
            }}
            QMenuBar {{
                background-color: #201d2b;
                color: #e8e3f2;
                padding: 4px;
            }}
            QMenuBar::item:selected {{
                background-color: #3b3450;
            }}
            QMenu {{
                background-color: #252230;
                color: #e8e3f2;
                border: 1px solid #494158;
            }}
            QMenu::item:selected {{
                background-color: #493b68;
            }}
            QToolBar#mainToolbar {{
                background-color: #201d2b;
                border: none;
                spacing: 6px;
                padding: 5px;
            }}
            QToolBar#mainToolbar QToolButton {{
                color: #e8e3f2;
                background-color: #302b3d;
                border: 1px solid #494158;
                border-radius: 6px;
                padding: 7px 12px;
            }}
            QToolBar#mainToolbar QToolButton:hover {{
                background-color: #493b68;
            }}
            QDockWidget {{
                color: #e8e3f2;
                titlebar-close-icon: none;
                titlebar-normal-icon: none;
            }}
            QDockWidget::title {{
                background-color: #292535;
                padding: 8px;
                border-bottom: 1px solid #393344;
            }}
            QStatusBar {{
                background-color: #201d2b;
                color: #aaa3ba;
            }}
        """)

    def update_properties(self):
        selected = self.workspace.circuit_scene.selectedItems()
        self.properties_panel.set_item(selected[0] if len(selected) == 1 else None)

    def on_placement_changed(self, component_id):
        if component_id:
            self.component_library.set_active_component(component_id)
            self.statusBar().showMessage(
                f"{component_id} yerleştirme modu: çalışma alanına tıkla. ESC ile çık."
            )
        else:
            self.component_library.set_active_component("")
            self.statusBar().showMessage(
                "Hazır  |  Orta tuş: seçim  |  Shift + orta tuş: kaydırma"
            )

    def set_fullscreen(self, enabled):
        if enabled:
            self.showFullScreen()
        else:
            self.showNormal()

    def changeEvent(self, event):
        super().changeEvent(event)

        if event.type() == QEvent.Type.WindowStateChange:
            is_fullscreen = self.isFullScreen()
            if self.fullscreen_action.isChecked() != is_fullscreen:
                blocker = QSignalBlocker(self.fullscreen_action)
                self.fullscreen_action.setChecked(is_fullscreen)
                del blocker


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
