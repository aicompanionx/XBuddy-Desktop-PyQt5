"""
Main entry point for the monitor_browser package.

This module allows the package to be run directly using:
python -m monitor_browser
"""

from .monitor import BrowserMonitor

def main():
    """Run the browser monitor."""
    monitor = BrowserMonitor()
    monitor.start()

if __name__ == "__main__":
    main() 