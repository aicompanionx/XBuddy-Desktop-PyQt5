from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QMouseEvent

from app.gui.widgets.pet_widget import PetWidget  # 确保 PetWidget 也已改为 PyQt5


class MainWindow(QMainWindow):
    """Main application window"""

    def __init__(self, app_manager):
        super().__init__()
        self.app_manager = app_manager
        self.dragging = False
        self.drag_position = QPoint()

        self.init_ui()
        self.load_settings()

    def init_ui(self):
        """Initialize UI"""
        self.setWindowTitle("XBuddy Desktop")
        # self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        # self.setAttribute(Qt.WA_TranslucentBackground)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)

        self.pet_widget = PetWidget(self.app_manager)
        layout.addWidget(self.pet_widget)

    def load_settings(self):
        """Load window settings"""
        config = self.app_manager.config_manager

        width = config.get("window.width", 300)
        height = config.get("window.height", 400)
        x = config.get("window.x", 100)
        y = config.get("window.y", 100)

        self.resize(width, height)
        self.move(x, y)

        if not config.get("window.always_on_top", True):
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowStaysOnTopHint)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        if event.buttons() & Qt.LeftButton and self.dragging:
            self.move(event.globalPos() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.dragging = False
            self.app_manager.config_manager.set("window.x", self.x())
            self.app_manager.config_manager.set("window.y", self.y())

    def closeEvent(self, event):
        event.ignore()
        self.hide()
