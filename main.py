#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
from PyQt5.QtWidgets import QApplication
from live2d.v3 import live2d
from PyQt5.QtCore import QCoreApplication, Qt, QEvent
from PyQt5.QtGui import QSurfaceFormat

from app.core.app_manager import AppManager


def configure_opengl():
    fmt = QSurfaceFormat()
    fmt.setVersion(2, 1) 
    fmt.setProfile(QSurfaceFormat.CompatibilityProfile) 
    QSurfaceFormat.setDefaultFormat(fmt)


class Application(QApplication):
    """Custom application class to handle system events"""
    
    def __init__(self, argv):
        super().__init__(argv)
        self.setQuitOnLastWindowClosed(False)  # Don't quit when window is closed
        
        # Set attributes to prevent focusing windows
        self.setAttribute(Qt.AA_DisableWindowContextHelpButton)
    
    def event(self, event):
        """Handle system events"""
        # Intercept close events using correct event type
        if event.type() == QEvent.Close:
            print("System close event intercepted - preventing close")
            return True  # Block the close event
            
        # # Handle desktop session logout/shutdown without focusing windows
        if hasattr(QEvent, 'ApplicationStateChange') and event.type() == QEvent.ApplicationStateChange:
            print("Application state changed, ensuring windows remain visible")
            # Ensure windows remain visible after system events
            for window in self.topLevelWidgets():
                if window.isVisible():
                    # Only prevent minimizing without activating
                    if window.windowState() & Qt.WindowMinimized:
                        window.setWindowState(window.windowState() & ~Qt.WindowMinimized)
                    # Do not call raise_() or activateWindow() to avoid stealing focus
                    
        # Block activation events
        if event.type() in [QEvent.ApplicationActivate, QEvent.WindowActivate, QEvent.FocusIn]:
            return True  # Block these events
                    
        return super().event(event)


def main():
    """Application entry point"""
    configure_opengl()
    
    # Set application attributes
    QCoreApplication.setAttribute(Qt.AA_UseDesktopOpenGL)  # Force desktop OpenGL
    
    # Prevent activating windows on show
    QCoreApplication.setAttribute(Qt.AA_MacPluginApplication, True)  # Acts more like a plugin on macOS
    
    live2d.init()
    
    # Use our custom application class
    app = Application(sys.argv)
    
    # Initialize application manager
    manager = AppManager()
    manager.start()

    # Run application
    app.exec_() 
    live2d.dispose()


if __name__ == "__main__":
    main()
