import sys
import platform
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QMouseEvent

from app.gui.widgets.pet_widget import PetWidget


class MainWindow(PetWidget):
    """Main application window containing Live2D pet widget"""

    def __init__(self, app_manager):
        # Initialize pet widget first
        try:
            super().__init__()
            self.app_manager = app_manager
            
            # Configure window for proper transparency
            self.setAttribute(Qt.WA_TranslucentBackground)
            
            # Make sure the window has no background
            self.setStyleSheet("background: transparent;")
            
            # Configure window flags for frameless window with no shadow
            self.setWindowFlags(
                Qt.FramelessWindowHint |        # No frame
                Qt.WindowStaysOnTopHint |       # Stay on top
                Qt.Tool |                       # No taskbar icon
                Qt.NoDropShadowWindowHint       # No shadow
            )
            
            # Apply platform-specific fixes
            self.apply_platform_fixes()
            
            print("MainWindow initialized successfully")
        except Exception as e:
            print(f"Error initializing MainWindow: {str(e)}")
            # Try a minimal initialization to avoid crash
            QMainWindow.__init__(self)  # Use direct class initialization instead of super()
            self.app_manager = app_manager
            print("MainWindow initialized with minimal setup due to error")
            
    def apply_platform_fixes(self):
        """Apply platform-specific fixes for window transparency and shadows"""
        if platform.system() == "Darwin":  # macOS
            try:
                # Try to use standard Qt approach first
                self.setWindowOpacity(0.99)  # Slightly less than 1 to trigger transparency
                
                print("Applied basic macOS window fixes")
            except Exception as e:
                print(f"Failed to apply basic macOS fixes: {e}")
