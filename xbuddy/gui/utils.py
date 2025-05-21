import logging
import sys
from logging.handlers import RotatingFileHandler

from live2d.v3 import live2d
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget

from xbuddy.settings import PROJECT_DIR


def get_logger(name=__name__):
    logger = logging.getLogger(name)
    if logger.hasHandlers():
        return logger

    logger.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)

    log_dir = PROJECT_DIR / "logs"
    log_dir.mkdir(exist_ok=True)
    file_handler = RotatingFileHandler(
        log_dir / "app.log", maxBytes=5 * 1024 * 1024, backupCount=3
    )
    file_handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


def transparent_and_taskbar(widget: QWidget) -> None:
    widget.setWindowFlags(
        Qt.FramelessWindowHint  # Borderless window
        | Qt.WindowStaysOnTopHint  # Always on top
        | Qt.NoDropShadowWindowHint  # No shadow
    )
    # Enable transparent background
    widget.setAttribute(Qt.WA_TranslucentBackground)


def transparent(widget: QWidget) -> None:
    widget.setWindowFlags(
        Qt.FramelessWindowHint  # Borderless window
        | Qt.WindowStaysOnTopHint  # Always on top
        | Qt.Tool  # Do not show in taskbar
        | Qt.NoDropShadowWindowHint  # No shadow
    )
    # Enable transparent background
    widget.setAttribute(Qt.WA_TranslucentBackground)


def run(window_class: type) -> None:
    live2d.init()
    app = QApplication(sys.argv)
    win = window_class()
    win.show()
    app.exec()
    del win
    live2d.dispose()
