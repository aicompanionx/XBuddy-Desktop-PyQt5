from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QMouseEvent

from app.gui.widgets.pet_widget import PetWidget


class MainWindow(PetWidget):
    """Main application window"""

    def __init__(self, app_manager):
        super().__init__()
        self.app_manager = app_manager
