from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction, QApplication, QMenu, QSystemTrayIcon

from xbuddy.settings import RESOURCES_DIRECTORY


class TrayIcon(QSystemTrayIcon):
    """System tray icon for the application"""

    def __init__(self):
        super().__init__()

        icon_path = RESOURCES_DIRECTORY / "icons/tray_icon.png"
        self.setIcon(QIcon(str(icon_path)))

        self.setup_menu()
        self.setup_connections()

    def setup_menu(self):
        """Set up the tray icon context menu"""
        menu = QMenu()

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
        self.settings_action.triggered.connect(self.on_settings)
        self.exit_action.triggered.connect(self.on_exit)

    def on_settings(self):
        """Show settings dialog"""
        # TODO: Implement settings dialog
        pass

    def on_exit(self):
        """Exit the application"""
        QApplication.quit()
