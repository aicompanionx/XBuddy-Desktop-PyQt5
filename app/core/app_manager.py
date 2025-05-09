from PySide6.QtCore import QObject, Signal, Slot
from app.core.config_manager import ConfigManager
from app.core.event_system import EventSystem
from app import __version__

class AppManager(QObject):
    """Application manager responsible for coordinating components"""
    
    def __init__(self):
        super().__init__()
        self.config_manager = ConfigManager()
        self.event_system = EventSystem.instance()
        self.main_window = None
        self.tray_icon = None
        self.model_manager = None
        self.app_version = __version__
        
    def start(self):
        """Start the application"""
        # Load configuration
        self.config_manager.load_config()
        
        # Import here to avoid circular imports
        from app.gui.main_window import MainWindow
        from app.gui.tray_icon import TrayIcon
        from app.live2d.model_manager import ModelManager
        
        # Initialize Live2D model manager
        self.model_manager = ModelManager(self)
        self.model_manager.init()
        
        # Create main window
        self.main_window = MainWindow(self)
        self.main_window.show()
        
        # Create system tray icon
        self.tray_icon = TrayIcon(self)
        self.tray_icon.show()
        
    def exit_application(self):
        """Exit the application"""
        # Save window position and size
        if self.main_window:
            self.config_manager.set("window.x", self.main_window.x())
            self.config_manager.set("window.y", self.main_window.y())
            self.config_manager.set("window.width", self.main_window.width())
            self.config_manager.set("window.height", self.main_window.height())
        
        # Clean up resources
        if self.model_manager:
            self.model_manager.cleanup()
            
        # Quit application
        from PySide6.QtWidgets import QApplication
        QApplication.quit()