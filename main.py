#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
from PySide6.QtWidgets import QApplication
from app.core.app_manager import AppManager

def main():
    """Application entry point"""
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # Don't quit when window is closed
    
    # Initialize application manager
    manager = AppManager()
    manager.start()
    
    # Run application
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 