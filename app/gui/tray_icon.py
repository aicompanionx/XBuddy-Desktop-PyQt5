import os
from PySide6.QtWidgets import QSystemTrayIcon, QMenu
from PySide6.QtGui import QIcon, QAction
from PySide6.QtCore import Slot

class TrayIcon(QSystemTrayIcon):
    """System tray icon for the application"""
    
    def __init__(self, app_manager):
        super().__init__()
        self.app_manager = app_manager
        
        # Set icon (use a default icon if the custom one doesn't exist)
        icon_path = os.path.join("resources", "icons", "tray_icon.png")
        if os.path.exists(icon_path):
            self.setIcon(QIcon(icon_path))
        else:
            # Use a system icon as fallback
            self.setIcon(QIcon.fromTheme("application-x-executable"))
        
        self.setup_menu()
        self.setup_connections()
    
    def setup_menu(self):
        """Set up the tray icon context menu"""
        menu = QMenu()
        
        # Show/hide action
        self.show_action = QAction("Show", self)
        menu.addAction(self.show_action)
        
        # Settings action
        self.settings_action = QAction("Settings", self)
        menu.addAction(self.settings_action)
        
        # Separator
        menu.addSeparator()
        
        # Exit action
        self.exit_action = QAction("Exit", self)
        menu.addAction(self.exit_action)
        
        self.setContextMenu(menu)
    
    def setup_connections(self):
        """Set up signal connections"""
        # Connect tray icon activation
        self.activated.connect(self.on_activated)
        
        # Connect menu actions
        self.show_action.triggered.connect(self.on_show)
        self.settings_action.triggered.connect(self.on_settings)
        self.exit_action.triggered.connect(self.on_exit)
    
    @Slot(QSystemTrayIcon.ActivationReason)
    def on_activated(self, reason):
        """Handle tray icon activation"""
        if reason == QSystemTrayIcon.DoubleClick:
            self.on_show()
    
    @Slot()
    def on_show(self):
        """Show/hide the main window"""
        if self.app_manager.main_window.isVisible():
            self.app_manager.main_window.hide()
            self.show_action.setText("Show")
        else:
            self.app_manager.main_window.show()
            self.show_action.setText("Hide")
    
    @Slot()
    def on_settings(self):
        """Show settings dialog"""
        # TODO: Implement settings dialog
        pass
    
    @Slot()
    def on_exit(self):
        """Exit the application"""
        self.app_manager.exit_application() 