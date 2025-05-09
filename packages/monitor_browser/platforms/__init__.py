"""
Platform-specific browser monitoring implementations.
"""

import platform
from datetime import datetime

from .windows import get_browser_windows_windows
from .macos import get_browser_windows_macos

def get_browser_windows():
    """
    Get browser windows for the current platform.
    
    Returns:
        list: A list of dictionaries containing browser window information.
    """
    system = platform.system()
    if system == 'Windows':
        return get_browser_windows_windows()
    elif system == 'Darwin':  # macOS
        return get_browser_windows_macos()
    else:
        # Return a parseable error for unsupported OS
        return [{
            'title': 'Unsupported OS',
            'process': 'error',
            'url': '',
            'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'active': False,
            'error': f'Unsupported operating system: {system}'
        }] 