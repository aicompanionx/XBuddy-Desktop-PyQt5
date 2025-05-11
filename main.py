#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
from PyQt5.QtWidgets import QApplication
from live2d.v3 import live2d
from PyQt5.QtCore import QCoreApplication, Qt
from PyQt5.QtGui import QSurfaceFormat

from app.core.app_manager import AppManager


def configure_opengl():
    fmt = QSurfaceFormat()
    fmt.setVersion(2, 1) 
    fmt.setProfile(QSurfaceFormat.CompatibilityProfile) 
    QSurfaceFormat.setDefaultFormat(fmt)

def main():
    """Application entry point"""
    configure_opengl()
    
    # Set application attributes
    QCoreApplication.setAttribute(Qt.AA_UseDesktopOpenGL)  # Force desktop OpenGL
    
    live2d.init()
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # Don't quit when window is closed

    # Initialize application manager
    manager = AppManager()
    manager.start()

    # Run application
    app.exec_()  # NOTE: PyQt5 uses exec_ instead of exec
    live2d.dispose()


if __name__ == "__main__":
    main()
