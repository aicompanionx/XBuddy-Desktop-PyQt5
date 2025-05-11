import sys
import platform
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QHBoxLayout
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QMouseEvent

from app.gui.widgets.pet_widget import PetWidget
from app.gui.widgets.chat_widget import ChatWidget


class MainWindow(QMainWindow):
    """Main application window containing Live2D pet widget and chat widget"""

    def __init__(self, app_manager):
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
            
    def apply_platform_fixes(self):
        """Apply platform-specific fixes for window transparency and shadows"""
        if platform.system() == "Darwin":  # macOS
            try:
                # Try to use standard Qt approach first
                self.setWindowOpacity(0.99)  # Slightly less than 1 to trigger transparency
                print("Applied basic macOS window fixes")
            except Exception as e:
                print(f"Failed to apply basic macOS fixes: {e}")
                
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
