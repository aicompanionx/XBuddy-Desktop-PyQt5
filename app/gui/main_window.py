from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QWidget
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QMouseEvent

from app.gui.widgets.pet_widget import PetWidget

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
        # Set window properties
        self.setWindowTitle("XBuddy Desktop")
        # self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        # self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create layout
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create pet widget
        self.pet_widget = PetWidget(self.app_manager)
        layout.addWidget(self.pet_widget)
    
    def load_settings(self):
        """Load window settings"""
        config = self.app_manager.config_manager
        
        # Set window size and position
        width = config.get("window.width", 300)
        height = config.get("window.height", 400)
        x = config.get("window.x", 100)
        y = config.get("window.y", 100)
        
        self.resize(width, height)
        self.move(x, y)
        
        # Set window properties
        if not config.get("window.always_on_top", True):
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowStaysOnTopHint)
    
    def mousePressEvent(self, event: QMouseEvent):
        """Mouse press event for window dragging"""
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event: QMouseEvent):
        """Mouse move event for window dragging"""
        if event.buttons() & Qt.LeftButton and self.dragging:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()
    
    def mouseReleaseEvent(self, event: QMouseEvent):
        """Mouse release event for window dragging"""
        if event.button() == Qt.LeftButton:
            self.dragging = False
            
            # Save window position
            self.app_manager.config_manager.set("window.x", self.x())
            self.app_manager.config_manager.set("window.y", self.y())
    
    def closeEvent(self, event):
        """Handle window close event"""
        # Hide window instead of closing
        event.ignore()
        self.hide() 