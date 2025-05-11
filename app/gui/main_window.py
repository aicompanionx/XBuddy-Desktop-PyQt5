import sys
import platform
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtGui import QCloseEvent

from app.gui.live2d.pet_widget import PetWidget


class MainWindow(PetWidget):
    """Main application window containing Live2D pet widget"""

    def __init__(self, app_manager):
        # Initialize pet widget first
        try:
            super().__init__()
            self.app_manager = app_manager
            
            # Configure window for proper transparency
            self.setAttribute(Qt.WA_TranslucentBackground)
            
            # Set attribute to prevent taking focus
            self.setAttribute(Qt.WA_ShowWithoutActivating)
            
            # Make sure the window has no background
            self.setStyleSheet("background: transparent;")
            
            # Configure window flags for frameless window with no shadow
            self.setWindowFlags(
                self.windowFlags() |
                Qt.FramelessWindowHint |        # No frame
                Qt.WindowStaysOnTopHint |       # Stay on top
                Qt.Tool |                       # No taskbar icon
                Qt.NoDropShadowWindowHint |     # No shadow
                Qt.WindowDoesNotAcceptFocus |    # Don't steal focus
                Qt.WindowStaysOnTopHint
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
                
    def closeEvent(self, event: QCloseEvent):
        """Handle window close event"""
        # Don't actually close, just hide the window
        event.ignore()
        self.hide()
        
    def changeEvent(self, event):
        """Handle window state change events"""
        if event.type() == QEvent.WindowStateChange:
            # If window was minimized, restore it immediately
            if self.windowState() & Qt.WindowMinimized:
                # Delay restoration slightly to avoid fighting with the OS
                from PyQt5.QtCore import QTimer
                QTimer.singleShot(100, self.restore_window)
                
        super().changeEvent(event)
        
    def restore_window(self):
        """Restore window from minimized state without stealing focus"""
        self.setWindowState(self.windowState() & ~Qt.WindowMinimized)
        self.show()
        # Do not call raise_() to avoid bringing window to front and stealing focus
        
    def event(self, event):
        """Filter focus-related events to prevent stealing focus"""
        
        # Block activation/focus events
        if event.type() in [QEvent.WindowActivate, QEvent.FocusIn]:
            return True  # Block these events
        
        return super().event(event)
