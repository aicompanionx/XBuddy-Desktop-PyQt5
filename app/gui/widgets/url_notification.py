"""
URL notification widget that shows phishing detection results.
"""

from PyQt5.QtWidgets import QLabel, QWidget, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import Qt, QTimer, pyqtSlot, QPropertyAnimation, QEasingCurve, QRect
from PyQt5.QtGui import QColor, QPalette, QFont

from app.gui.widgets.check_url import CheckURL


class URLNotificationWidget(QWidget):
    """
    Widget that shows URL phishing detection results above the pet.
    
    Features:
    - Automatically appears when a URL is detected
    - Shows phishing detection results
    - Automatically disappears after a delay
    - Animated appearance and disappearance
    """
    
    def __init__(self, app_manager, parent=None):
        """
        Initialize the URL notification widget.
        
        Args:
            app_manager: Application manager
            parent: Parent widget
        """
        super().__init__(parent)
        self.app_manager = app_manager
        
        # Create URL checker
        self.url_checker = CheckURL(self.app_manager.api_client, self)
        
        # Connect signals
        self.url_checker.check_completed.connect(self._on_check_completed)
        self.app_manager.event_system.url_changed.connect(self._on_url_changed)
        
        # Set up UI
        self._setup_ui()
        
        # Hide initially
        self.hide()
        
        # Animation properties
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        
        # Auto-hide timer
        self.hide_timer = QTimer(self)
        self.hide_timer.setSingleShot(True)
        self.hide_timer.timeout.connect(self.hide_notification)
        
        # Current URL being checked
        self.current_url = None
        
        # Cooldown timer to prevent checking the same URL repeatedly
        self.cooldown_timer = QTimer(self)
        self.cooldown_timer.setSingleShot(True)
        self.cooldown_timer.timeout.connect(self._reset_cooldown)
        self.cooldown_urls = set()
        
        # Track cleanup state
        self._is_cleaned_up = False
    
    def _setup_ui(self):
        """Set up the UI components."""
        # Configure window
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool |
            Qt.NoDropShadowWindowHint
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        
        # Create layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Create content widget with background
        self.content_widget = QWidget(self)
        content_layout = QVBoxLayout(self.content_widget)
        content_layout.setContentsMargins(15, 10, 15, 10)
        
        # Set rounded corners and background color
        self.content_widget.setStyleSheet("""
            background-color: rgba(40, 40, 40, 0.9);
            border-radius: 10px;
            color: white;
        """)
        
        # Create labels
        self.title_label = QLabel("Security Check")
        self.title_label.setStyleSheet("font-weight: bold; color: white; font-size: 14px;")
        
        self.url_label = QLabel()
        self.url_label.setStyleSheet("color: #cccccc; font-size: 12px;")
        self.url_label.setWordWrap(True)
        self.url_label.setMaximumWidth(250)
        
        self.status_label = QLabel()
        self.status_label.setWordWrap(True)
        
        # Add labels to layout
        content_layout.addWidget(self.title_label)
        content_layout.addWidget(self.url_label)
        content_layout.addWidget(self.status_label)
        
        # Add content widget to main layout
        layout.addWidget(self.content_widget)
        
        # Set fixed size
        self.setFixedWidth(300)
        self.adjustSize()
    
    def position_above_parent(self):
        """Position the notification above the parent widget."""
        if self.parent():
            parent_rect = self.parent().geometry()
            x = parent_rect.x() + (parent_rect.width() - self.width()) // 2
            y = parent_rect.y() - self.height() - 10  # 10px gap
            
            # Ensure notification is visible on screen
            if y < 0:
                y = parent_rect.y() + parent_rect.height() + 10
            
            self.setGeometry(x, y, self.width(), self.height())
    
    @pyqtSlot(str, bool)
    def _on_url_changed(self, url, is_active):
        """
        Handle URL change event.
        
        Args:
            url (str): New URL
            is_active (bool): Whether the window is active
        """
        # Skip if already cleaned up
        if self._is_cleaned_up:
            return
            
        # Skip if URL is in cooldown
        if url in self.cooldown_urls:
            return
        
        # Skip if URL is empty or not a web URL
        if not url or not (url.startswith("http://") or url.startswith("https://")):
            return
        
        # Add URL to cooldown
        self.cooldown_urls.add(url)
        self.cooldown_timer.start(60000)  # 1 minute cooldown
        
        # Set current URL
        self.current_url = url
        
        # Update URL label
        self.url_label.setText(self._format_url(url))
        
        # Show checking status
        self.show_checking_status()
        
        # Check URL
        self.url_checker.check_url(url)
    
    def _format_url(self, url):
        """Format URL for display (truncate if too long)."""
        max_length = 40
        if len(url) > max_length:
            return url[:max_length] + "..."
        return url
    
    def show_checking_status(self):
        """Show checking status."""
        self.title_label.setText("Security Check")
        self.status_label.setText("Checking URL safety...")
        self.status_label.setStyleSheet("color: #cccccc;")
        
        # Show notification
        self.show_notification()
    
    @pyqtSlot(str, bool, str)
    def _on_check_completed(self, url, is_phishing, message):
        """
        Handle check completion.
        
        Args:
            url (str): Checked URL
            is_phishing (bool): Whether URL is a phishing site
            message (str): Additional message from the API
        """
        # Skip if already cleaned up
        if self._is_cleaned_up:
            return
            
        # Skip if not the current URL
        if url != self.current_url:
            return
        
        # Update UI based on result
        if is_phishing:
            self.show_warning(url, message)
        else:
            self.show_safe(url, message)
    
    def show_warning(self, url, message):
        """Show warning for phishing URL."""
        self.title_label.setText("⚠️ Security Warning")
        self.status_label.setText(message or "This website may be dangerous!")
        self.status_label.setStyleSheet("color: #ff9966; font-weight: bold;")
        
        # Show notification for longer time for warnings
        self.show_notification(10000)  # 10 seconds
    
    def show_safe(self, url, message):
        """Show safe URL notification."""
        self.title_label.setText("✓ Website Safe")
        self.status_label.setText(message or "This website appears to be safe.")
        self.status_label.setStyleSheet("color: #99cc99;")
        
        # Show notification
        self.show_notification(5000)  # 5 seconds
    
    def show_notification(self, duration=5000):
        """
        Show the notification with animation.
        
        Args:
            duration (int): Auto-hide duration in milliseconds
        """
        # Skip if already cleaned up
        if self._is_cleaned_up:
            return
            
        # Position above parent
        self.position_above_parent()
        
        # Stop any running animations
        self.animation.stop()
        
        # Show widget
        self.show()
        self.raise_()
        
        # Animate appearance
        start_rect = self.geometry()
        start_rect.setHeight(0)
        
        end_rect = self.geometry()
        
        self.animation.setStartValue(start_rect)
        self.animation.setEndValue(end_rect)
        self.animation.start()
        
        # Start auto-hide timer
        self.hide_timer.stop()
        self.hide_timer.start(duration)
    
    def hide_notification(self):
        """Hide the notification with animation."""
        # Skip if already cleaned up
        if self._is_cleaned_up:
            return
            
        # Stop any running animations
        self.animation.stop()
        
        # Animate disappearance
        start_rect = self.geometry()
        
        end_rect = self.geometry()
        end_rect.setHeight(0)
        
        self.animation.setStartValue(start_rect)
        self.animation.setEndValue(end_rect)
        self.animation.finished.connect(self.hide)
        self.animation.start()
    
    def _reset_cooldown(self):
        """Reset URL cooldown."""
        self.cooldown_urls.clear()
        
    def cleanup(self):
        """Clean up resources before destruction."""
        if self._is_cleaned_up:
            return
            
        print("Cleaning up URL notification widget")
        self._is_cleaned_up = True
        
        # Disconnect signals
        try:
            self.url_checker.check_completed.disconnect(self._on_check_completed)
            self.app_manager.event_system.url_changed.disconnect(self._on_url_changed)
        except Exception as e:
            print(f"Error disconnecting signals: {e}")
        
        # Stop timers
        self.hide_timer.stop()
        self.cooldown_timer.stop()
        
        # Stop animation
        if self.animation.state() == QPropertyAnimation.Running:
            self.animation.stop()
            
    def __del__(self):
        """Ensure cleanup when object is destroyed."""
        self.cleanup() 