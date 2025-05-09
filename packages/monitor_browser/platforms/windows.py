"""
Windows-specific browser monitoring implementation.
"""

import traceback
from datetime import datetime

from ..utils import get_process_name, clean_string, ensure_protocol

def get_browser_windows_windows():
    """
    Get browser windows for Windows platform.
    
    Returns:
        list: A list of dictionaries containing browser window information.
    """
    try:
        import win32gui
        import win32process
        import uiautomation as auto
        
        browser_windows = []
        browser_processes = {'chrome', 'firefox', 'edge', 'opera', 'brave'}
        active_hwnd = win32gui.GetForegroundWindow()
        
        def callback(hwnd, extra):
            if win32gui.IsWindowVisible(hwnd):
                try:
                    _, pid = win32process.GetWindowThreadProcessId(hwnd)
                    process_name = get_process_name(pid)
                    
                    if process_name and any(browser in process_name for browser in browser_processes):
                        title = clean_string(win32gui.GetWindowText(hwnd))
                        is_active = (hwnd == active_hwnd)
                        if title:
                            try:
                                element = auto.ControlFromHandle(hwnd)
                                if element:
                                    edit = element.EditControl()
                                    if edit and (edit.Name in ["地址和搜索栏", "Address and search bar", 
                                                             "在此处输入搜索内容或网址", "Enter your search or web address"]):
                                        url = clean_string(edit.GetValuePattern().Value)
                                        if url:
                                            url = ensure_protocol(url)
                                            browser_windows.append({
                                                'title': title,
                                                'process': process_name,
                                                'url': url,
                                                'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                                'active': is_active
                                            })
                            except Exception as e:
                                # If we can't get the URL through UI Automation, we'll still add the window
                                # with an empty URL to show it was detected
                                browser_windows.append({
                                    'title': title,
                                    'process': process_name,
                                    'url': '',
                                    'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                    'active': is_active,
                                    'error': str(e)
                                })
                except Exception as e:
                    pass
            return True
        
        win32gui.EnumWindows(callback, None)
        
        # Even if no browser windows are found, output something Node.js can parse
        if not browser_windows:
            # Force at least one output for debugging
            browser_windows.append({
                'title': 'No browsers detected',
                'process': 'none',
                'url': '',
                'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'active': False,
                'debug': 'No browser windows found'
            })
            
        return browser_windows
    except Exception as e:
        # Return error information in a format Node.js can parse
        return [{
            'title': 'Error detecting browsers',
            'process': 'error',
            'url': '',
            'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'active': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }] 