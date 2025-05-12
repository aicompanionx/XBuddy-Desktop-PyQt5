"""
Browser monitoring service that integrates with the event system.
"""
import threading
import time
import json
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QThread

from packages.monitor_browser import BrowserMonitor


class BrowserMonitorThread(QThread):
    """Thread for monitoring browser URLs without blocking the main thread."""
    
    # Signal emitted when a URL changes
    url_detected = pyqtSignal(str, bool)
    
    def __init__(self, interval=1.0):
        """
        Initialize the browser monitor thread.
        
        Args:
            interval (float): Polling interval in seconds
        """
        super().__init__()
        self.interval = interval
        self.running = False
        self.monitor = BrowserMonitor()
        self.last_url = None
    
    def run(self):
        """Run the browser monitoring thread."""
        self.running = True
        
        while self.running:
            try:
                # Get current browser windows
                windows = self.monitor.get_windows()
                
                # Find active window or first window with URL
                active_window = None
                first_window = None
                
                for window in windows:
                    if window.get('url'):
                        if not first_window:
                            first_window = window
                        
                        if window.get('active', False):
                            active_window = window
                            break
                
                # Use active window if available, otherwise first window with URL
                current_window = active_window or first_window
                
                if current_window and current_window.get('url'):
                    url = current_window.get('url')
                    is_active = current_window.get('active', False)
                    
                    # Only emit signal if URL changed
                    if url != self.last_url:
                        self.last_url = url
                        self.url_detected.emit(url, is_active)
            except Exception as e:
                print(f"Error in browser monitor thread: {e}")
            
            # Sleep for interval
            time.sleep(self.interval)
    
    def stop(self):
        """Stop the browser monitoring thread."""
        self.running = False
        
        # Wait for the thread to finish with a timeout
        if not self.wait(3000):  # 3 second timeout
            print("Warning: Browser monitor thread did not stop in time, terminating")
            self.terminate()
            self.wait()


class BrowserMonitorService(QObject):
    """
    Service that monitors browser URLs and integrates with the event system.
    """
    
    def __init__(self, app_manager, interval=1.0):
        """
        Initialize the browser monitor service.
        
        Args:
            app_manager: Application manager
            interval (float): Polling interval in seconds
        """
        super().__init__()
        self.app_manager = app_manager
        self.interval = interval
        self.monitor_thread = None
    
    def start(self):
        """Start the browser monitoring service."""
        if self.monitor_thread is None or not self.monitor_thread.isRunning():
            self.monitor_thread = BrowserMonitorThread(self.interval)
            self.monitor_thread.url_detected.connect(self._on_url_detected)
            self.monitor_thread.start()
            print("Browser monitoring service started")
    
    def stop(self):
        """Stop the browser monitoring service."""
        if self.monitor_thread and self.monitor_thread.isRunning():
            print("Stopping browser monitor thread...")
            self.monitor_thread.stop()
            self.monitor_thread = None
            print("Browser monitoring service stopped")
    
    @pyqtSlot(str, bool)
    def _on_url_detected(self, url, is_active):
        """
        Handle URL detection.
        
        Args:
            url (str): Detected URL
            is_active (bool): Whether the window is active
        """
        # Emit URL changed event
        self.app_manager.event_system.url_changed.emit(url, is_active)
        
    def __del__(self):
        """Ensure thread is stopped when object is destroyed."""
        try:
            if hasattr(self, 'monitor_thread') and self.monitor_thread:
                print("Cleaning up browser monitor thread in destructor")
                self.stop()
        except Exception as e:
            print(f"Error cleaning up browser monitor thread: {e}") 