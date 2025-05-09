"""
macOS-specific browser monitoring implementation.
"""

import subprocess
import traceback
import json
from datetime import datetime

from ..utils import clean_string, ensure_protocol

def get_browser_windows_macos():
    """
    Get browser windows for macOS platform.
    
    Returns:
        list: A list of dictionaries containing browser window information.
    """
    browser_windows = []
    
    try:
        # Supported browsers list - Safari is intentionally excluded
        browsers = {
            'Google Chrome': 'chrome',
            'Firefox': 'firefox',
            'Microsoft Edge': 'edge',
            'Opera': 'opera',
            'Brave Browser': 'brave'
            # Safari is intentionally excluded from monitoring
        }
        
        # Get active application
        try:
            active_app_script = '''
            tell application "System Events"
                set frontApp to name of first application process whose frontmost is true
                return frontApp
            end tell
            '''
            result = subprocess.run(['osascript', '-e', active_app_script], 
                                capture_output=True, 
                                text=True)
            active_app = result.stdout.strip() if result.returncode == 0 else ""
        except:
            active_app = ""
        
        for browser_name, process_name in browsers.items():
            try:
                # Check if this browser is the active application
                is_browser_active = active_app.lower().find(process_name.lower()) >= 0 or active_app.lower().find(browser_name.lower()) >= 0
                
                if is_browser_active:
                    # For active browser, get the active tab URL using AppleScript
                    active_tab_script = f'''
                    tell application "{browser_name}"
                        set activeURL to URL of active tab of front window
                        return activeURL
                    end tell
                    '''
                    active_result = subprocess.run(['osascript', '-e', active_tab_script], 
                                          capture_output=True, 
                                          text=True)
                    active_url = active_result.stdout.strip() if active_result.returncode == 0 else ""
                else:
                    active_url = ""
                
                # Get all tabs from the browser
                script = f'''
                tell application "{browser_name}"
                    set windowList to every window
                    set tabList to {{}}
                    repeat with theWindow in windowList
                        set tabList to tabList & (URL of every tab of theWindow)
                    end repeat
                    return tabList
                end tell
                '''
                
                result = subprocess.run(['osascript', '-e', script], 
                                    capture_output=True, 
                                    text=True)
                
                if result.returncode == 0:
                    urls = result.stdout.strip().split(', ')
                    for url in urls:
                        if url and url != 'missing value':
                            url = clean_string(ensure_protocol(url))
                            # A tab is active only if browser is active AND this URL matches the active tab URL
                            is_active = is_browser_active and (url == active_url)
                            browser_windows.append({
                                'title': browser_name,
                                'process': process_name,
                                'url': url,
                                'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                'active': is_active
                            })
            except Exception as e:
                # Log the error but continue with other browsers
                print(json.dumps({
                    'status': 'error',
                    'browser': browser_name,
                    'error': str(e),
                    'traceback': traceback.format_exc()
                }))
                continue
        
        # Even if no browser windows are found, output something Node.js can parse
        if not browser_windows:
            browser_windows.append({
                'title': 'No browsers detected',
                'process': 'none',
                'url': '',
                'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'active': False,
                'debug': 'No browser windows found on macOS'
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