import sys
import platform
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QFrame
from PyQt5.QtCore import Qt, QEvent, QTimer, QUrl
from PyQt5.QtGui import QCloseEvent

from app.api.client import ApiClient
from app.gui.live2d.pet_widget import PetWidget
from app.gui.widgets.chat_widget import ChatWidget
from app.gui.widgets.news_widget import NewsWidget
from app.model.news_model import NewsModel
from app.api.news_ws_client import NewsWebSocketClient
from app.api.endpoints import ApiRoutes, Endpoints


class MainWindow(QMainWindow):
    """Main application window containing Live2D pet widget and chat widget"""

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
                Qt.FramelessWindowHint |     # No frame
                Qt.WindowStaysOnTopHint |     # Stay on top
                Qt.NoDropShadowWindowHint     # No shadow
            )
            
            # Apply platform-specific fixes
            self.apply_platform_fixes()
            
            # Create central widget and layout
            central_widget = QWidget()
            central_widget.setAttribute(Qt.WA_TranslucentBackground)
            self.setCentralWidget(central_widget)
            
            # Main layout
            self.layout = QVBoxLayout(central_widget)
            self.layout.setContentsMargins(0, 0, 0, 0)
            self.layout.setSpacing(0)
            
            # Create a fixed-size placeholder for news
            self.news_container = QFrame()
            self.news_container.setFixedHeight(65)  # Much smaller height to reduce gap
            self.news_container.setFixedWidth(200)  #
            self.news_container.setStyleSheet("background: transparent;")
            self.news_layout = QVBoxLayout(self.news_container)
            self.news_layout.setContentsMargins(0, 0, 0, 0)
            self.news_layout.setSpacing(0)
            # Set alignment to top instead of using stretch
            self.news_layout.setAlignment(Qt.AlignBottom)
            
            # Create pet widget and set its fixed size
            self.pet_widget = PetWidget()
            self.pet_widget.setFixedSize(200, 400) # Pet widget has a fixed size
            
            # Set window fixed width to match pet widget width
            self.setFixedWidth(200)
            
            self.chat_widget = ChatWidget() # Chat widget has an adaptive height

            # News widget
            self.current_news_widget = None
            self.news_timer = QTimer(self)
            self.news_timer.setSingleShot(True)  # Make sure it's single-shot
            self.news_timer.timeout.connect(self.hide_news_widget)
            
            # Dictionary to track open news detail windows by news ID
            self.open_news_windows = {}
            
            # WebSocket client for news
            self.news_ws_client = NewsWebSocketClient(self)
            self.news_ws_client.news_received.connect(self.on_news_received)
            self.news_ws_client.connected.connect(self.on_news_ws_connected)
            self.news_ws_client.disconnected.connect(self.on_news_ws_disconnected)
            self.news_ws_client.error.connect(self.on_news_ws_error)
            
            # Order of widgets in layout
            self.layout.addStretch(1) # This spacer takes up available space at the top
            self.layout.addWidget(self.news_container, 0, Qt.AlignCenter)  # Center align news container
            self.layout.addWidget(self.chat_widget, 0, Qt.AlignCenter) # Center align chat widget
            self.layout.addWidget(self.pet_widget, 0, Qt.AlignCenter)  # Center align pet widget
            
            print("MainWindow initialized successfully with Live2D pet widget")
            
            # Connect to WebSocket after window setup is complete
            QTimer.singleShot(500, self.connect_to_news_websocket)
            
        except Exception as e:
            print(f"Error initializing MainWindow: {str(e)}")
            # Try a minimal initialization to avoid crash
            QMainWindow.__init__(self)  # Use direct class initialization instead of super()
            self.app_manager = app_manager
            print("MainWindow initialized with minimal setup due to error")
            
    def connect_to_news_websocket(self):
        """Connect to the news WebSocket server"""
        try:
            base_url = self.app_manager.config_manager.get("api.base_url")
            if not base_url: 
                base_url = "https://api.xbuddy.me/dev/api/v1"
                
            api_routes = ApiRoutes(base_url)
            ws_url = api_routes.news_ws()
            
            self.news_ws_client.connect_to_server(ws_url)
            print(f"Connecting to news WebSocket at: {ws_url}")
        except Exception as e:
            print(f"Error connecting to news WebSocket: {e}")
            try:
                fallback_url = "wss://api.xbuddy.me/dev/api/v1/news/ws"
                print(f"Trying fallback WebSocket URL: {fallback_url}")
                self.news_ws_client.connect_to_server(fallback_url)
            except Exception as fallback_e:
                print(f"Fallback connection also failed: {fallback_e}")
    
    def on_news_ws_connected(self):
        """Handle successful WebSocket connection"""
        print("Connected to news WebSocket server")
    
    def on_news_ws_disconnected(self):
        """Handle WebSocket disconnection"""
        print("Disconnected from news WebSocket server")
    
    def on_news_ws_error(self, error_message):
        """Handle WebSocket error"""
        print(f"News WebSocket error: {error_message}")
    
    def on_news_received(self, news_model):
        """Handle received news data from WebSocket"""
        print(f"Received new news: {news_model.title}")
        
        # Remove any existing news widget
        self.hide_news_widget()
        
        # Create and add the new news widget
        try:
            self.current_news_widget = NewsWidget(news=news_model)
            
            # Connect to the detail window creation to track open windows
            self.current_news_widget.detail_window_opened.connect(
                lambda window: self.track_detail_window(news_model.id, window)
            )
            
            # Add news widget to container and ensure it's visible
            self.news_layout.insertWidget(0, self.current_news_widget)
            self.current_news_widget.setVisible(True)
            
            # Start the timer to hide the news widget after exactly 5 seconds
            self.news_timer.start(5000)  # Exactly 5000 milliseconds = 5 seconds
        except Exception as e:
            print(f"Error displaying news widget: {e}")
    
    def track_detail_window(self, news_id, window):
        """Track an open news detail window"""
        print(f"Tracking detail window for news ID: {news_id}")
        if news_id not in self.open_news_windows or not self.open_news_windows[news_id].isVisible():
            self.open_news_windows[news_id] = window
            # When the window is closed, remove it from our tracking
            window.destroyed.connect(lambda obj=None: self.remove_detail_window(news_id))
    
    def remove_detail_window(self, news_id):
        """Remove a detail window from tracking when it's closed"""
        if news_id in self.open_news_windows:
            print(f"Removing tracked detail window for news ID: {news_id}")
            del self.open_news_windows[news_id]
    
    def hide_news_widget(self):
        """Remove the current news widget if it exists"""
        if self.current_news_widget:
            print("Hiding news widget")
            # Detach the signal to avoid reference issues
            try:
                self.current_news_widget.detail_window_opened.disconnect()
            except Exception as e:
                print(f"Error disconnecting signal: {e}")
                
            # Remove widget from layout
            self.news_layout.removeWidget(self.current_news_widget)
            self.current_news_widget.setParent(None)  # Remove parent to fully detach from layout
            self.current_news_widget.deleteLater()    # Schedule for deletion
            self.current_news_widget = None

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
        # Clean up pet widget first
        if hasattr(self, 'pet_widget') and self.pet_widget:
            self.pet_widget.cleanup()
        
        # Close any open news windows
        if hasattr(self, 'open_news_windows'):
            for window in self.open_news_windows.values():
                if window and window.isVisible():
                    window.close()
        
        # Close the WebSocket connections
        if hasattr(self, 'news_ws_client'):
            self.news_ws_client.disconnect_from_server()
            
        # Close chat WebSocket connection if it exists
        if hasattr(self, 'chat_widget') and hasattr(self.chat_widget, 'chat_ws_client'):
            self.chat_widget.chat_ws_client.disconnect_from_server()
            
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
