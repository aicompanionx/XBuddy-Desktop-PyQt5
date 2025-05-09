"""
Utility functions for the browser monitor package.
"""

import json
import sys
import re
import io
from datetime import datetime

# Ensure proper encoding for output
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Ensure output is flushed immediately
sys.stdout.reconfigure(line_buffering=True)

# Cache process info to avoid repeated queries
process_cache = {}

def get_process_name(pid):
    """
    Get the process name for a given process ID.
    
    Args:
        pid (int): Process ID
        
    Returns:
        str or None: Process name or None if process not found
    """
    if pid in process_cache:
        return process_cache[pid]
    try:
        import psutil
        process = psutil.Process(pid)
        name = process.name().lower()
        process_cache[pid] = name
        return name
    except:
        return None

def ensure_protocol(url):
    """
    Ensure URL has a protocol; add https:// if missing.
    
    Args:
        url (str): URL to check
        
    Returns:
        str: URL with protocol
    """
    if url and not re.match(r'^[a-zA-Z]+://', url):
        return f"https://{url}"
    return url

def clean_string(text):
    """
    Remove problematic characters like zero-width spaces.
    
    Args:
        text (str): Text to clean
        
    Returns:
        str: Cleaned text
    """
    if not text:
        return text
    # Remove zero-width space and other invisible characters
    return re.sub(r'[\u200b\u200c\u200d\u2060\ufeff]', '', text)

def safe_json_print(data):
    """
    Print JSON data safely with newline at the end.
    
    Args:
        data (dict): Data to print as JSON
    """
    try:
        # Use plain JSON without ensure_ascii to avoid encoding issues
        json_str = json.dumps(data)
        print(json_str)
        sys.stdout.flush()
    except Exception as e:
        # Fallback for any error
        try:
            print(json.dumps({
                'error': f"Error outputting data: {str(e)}",
                'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }))
            sys.stdout.flush()
        except:
            pass 