
import sys

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
)
from PySide6.QtCore import Qt
from settings import (
    WINDOW_HEIGHT,
    WINDOW_HEIGHT_MIN,
    WINDOW_TITLE,
    WINDOW_WIDTH,
    WINDOW_WIDTH_MIN
    )

from interface.workspace import Workspace

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Pencere ayarları
        self.setWindowTitle(WINDOW_TITLE)
        self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.setMinimumSize(WINDOW_WIDTH_MIN, WINDOW_HEIGHT_MIN)

        # Ana çalışma alanı
        self.workspace = Workspace()

        self.setCentralWidget(self.workspace)

        # Genel pencere görünümü
        self.setStyleSheet("""
            QMainWindow {
                background-color: #201d2b;
            }
        """)


def main():
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
