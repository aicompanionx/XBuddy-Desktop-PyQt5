"""
Browser Monitor Core Module

This module provides the main BrowserMonitor class that handles browser window monitoring.
"""

import time
from datetime import datetime
import platform
import traceback

from .utils import safe_json_print
from .platforms import get_browser_windows

class BrowserMonitor:
    """
    Browser Monitor class for tracking browser windows and their URLs.
    
    This class provides methods to start monitoring browser windows
    and retrieve information about them.
    """
    
    def __init__(self):
        """Initialize the BrowserMonitor."""
        self.system = platform.system()
    
    def get_windows(self):
        """
        Get current browser windows.
        
        Returns:
            list: A list of dictionaries containing browser window information.
        """
        return get_browser_windows()
    
    def start(self, interval=0.5):
        """
        Start monitoring browser windows.
        
        Args:
            interval (float): Time interval between checks in seconds.
        """
        # Output initial status message
        status = {
            'status': 'starting',
            'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'platform': self.system
        }
        
        safe_json_print(status)
        
        try:
            while True:
                windows = self.get_windows()
                
                for window in windows:
                    safe_json_print(window)
                
                # Output at least one message per cycle
                if not windows:
                    safe_json_print({
                        'status': 'running',
                        'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'message': 'No browser windows detected'
                    })
                
                time.sleep(interval)
                
        except KeyboardInterrupt:
            # Final message when stopped
            safe_json_print({
                'status': 'stopped',
                'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
        except Exception as e:
            # Error message
            safe_json_print({
                'status': 'error',
                'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'error': str(e),
                'traceback': traceback.format_exc()
            }) 