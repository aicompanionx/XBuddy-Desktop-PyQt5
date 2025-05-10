#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
from PyQt5.QtWidgets import QApplication
from live2d.v3 import live2d

from app.core.app_manager import AppManager


def main():
    """Application entry point"""
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
