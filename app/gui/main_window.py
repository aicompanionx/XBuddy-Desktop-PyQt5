import sys
import platform
<<<<<<< HEAD
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QHBoxLayout
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QMouseEvent

from app.gui.widgets.pet_widget import PetWidget
from app.gui.widgets.chat_widget import ChatWidget
=======
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtGui import QCloseEvent

from app.gui.live2d.pet_widget import PetWidget
>>>>>>> 93293c1bbb225a1e30b10f00d02a13418468370f


class MainWindow(QMainWindow):
    """Main application window containing Live2D pet widget and chat widget"""

    def __init__(self, app_manager):
<<<<<<< HEAD
        super().__init__()
        self.app_manager = app_manager
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Create chat widget
        self.chat_widget = ChatWidget()
        self.chat_widget.setFixedHeight(300)  # Set fixed height for chat widget
        
        # Create pet widget
        self.pet_widget = PetWidget()
        
        # Add widgets to layout
        main_layout.addWidget(self.chat_widget)
        main_layout.addWidget(self.pet_widget)
        
        # Connect chat signals
        self.chat_widget.message_sent.connect(self.handle_user_message)
        
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
        
        # Set window size
        self.resize(400, 800)  # Width: 400, Height: 800
        
        # Initialize dragging variables
        self.dragging = False
        self.drag_offset = QPoint()
        
        print("MainWindow initialized successfully")
=======
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
>>>>>>> 93293c1bbb225a1e30b10f00d02a13418468370f
            
    def apply_platform_fixes(self):
        """Apply platform-specific fixes for window transparency and shadows"""
        if platform.system() == "Darwin":  # macOS
            try:
                # Try to use standard Qt approach first
                self.setWindowOpacity(0.99)  # Slightly less than 1 to trigger transparency
                print("Applied basic macOS window fixes")
            except Exception as e:
                print(f"Failed to apply basic macOS fixes: {e}")
                
<<<<<<< HEAD
    def handle_user_message(self, message):
        """Handle messages sent from the chat widget"""
        print(f"Received message: {message}")
        # Here you can add your message handling logic
        # For example, you could trigger pet animations or responses
        self.pet_widget.model.SetRandomExpression()
        self.pet_widget.model.StartRandomMotion(
            priority=3,
            onStartMotionHandler=self.pet_widget.on_start_motion_callback,
            onFinishMotionHandler=self.pet_widget.on_finish_motion_callback
        )
        
        # Example response
        response = f"I received your message: {message}"
        self.chat_widget.receive_message(response)
        
    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse press events for dragging the entire window"""
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.drag_offset = event.globalPos() - self.pos()
        super().mousePressEvent(event)
        
    def mouseMoveEvent(self, event: QMouseEvent):
        """Handle mouse move events for dragging the entire window"""
        if self.dragging and event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_offset)
        super().mouseMoveEvent(event)
        
    def mouseReleaseEvent(self, event: QMouseEvent):
        """Handle mouse release events for dragging the entire window"""
        if event.button() == Qt.LeftButton:
            self.dragging = False
        super().mouseReleaseEvent(event)
=======
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
>>>>>>> 93293c1bbb225a1e30b10f00d02a13418468370f
