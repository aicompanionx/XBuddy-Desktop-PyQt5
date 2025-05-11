import sys

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QMouseEvent
from PyQt5.QtWidgets import QPushButton, QApplication
from live2d.v3 import live2d

from app.gui.live2d.base_widget import RESOURCES_DIRECTORY
from app.gui.live2d.lip_sync_widget import LipSyncLive2DWidget


class PetButton(QPushButton):
    def __init__(self, text='', icon_path=None, on_click=None, parent=None):
        super().__init__(text, parent)

        # Set window flags: frameless, always on top, no taskbar
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowOpacity(0.8)

        # Set style
        self.setStyleSheet("""
            QPushButton {
                background-color: #40444b;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #5865f2;
            }
        """)

        self.setVisible(False)  # Initially hidden
        self.setFixedSize(50, 50)
        self.setCursor(Qt.PointingHandCursor)

        # Set icon if provided
        if icon_path:
            self.setIcon(QIcon(str(icon_path)))
            self.setIconSize(QSize(24, 24))  # Adjust icon size if needed

        # Set click handler if provided
        if on_click:
            self.clicked.connect(on_click)


def on_click(*args, **kwargs):
    try:
        print("Button clicked")
    except Exception as e:
        print(f"Error handling button click: {e}")


class ButtonLive2DWidget(LipSyncLive2DWidget):
    def __init__(self):
        super().__init__()
        self.buttons = [
            PetButton(icon_path=RESOURCES_DIRECTORY / 'icons/message.svg',
                      on_click=on_click),
            PetButton(icon_path=RESOURCES_DIRECTORY / 'icons/transfer.svg',
                      on_click=None),
            PetButton(icon_path=RESOURCES_DIRECTORY / 'icons/settings.svg',
                      on_click=None),
            PetButton(icon_path=RESOURCES_DIRECTORY / 'icons/volume.svg',
                      on_click=None),
            PetButton(icon_path=RESOURCES_DIRECTORY / 'icons/news.svg',
                      on_click=None),
            PetButton(icon_path=RESOURCES_DIRECTORY / 'icons/x.svg',
                      on_click=None),
        ]

    def mousePressEvent(self, event: QMouseEvent):
        super().mousePressEvent(event)
        if event.button() == Qt.MouseButton.RightButton:

            # Set fixed positions for each button relative to the main window
            center = self.frameGeometry().center()
            x = center.x()
            y = center.y()
            self.buttons[0].move(x - 200, y - 100)
            self.buttons[1].move(x - 250, y)
            self.buttons[2].move(x - 200, y + 100)
            self.buttons[3].move(x + 200, y - 100)
            self.buttons[4].move(x + 250, y)
            self.buttons[5].move(x + 200, y + 100)

            # Show all buttons
            for btn in self.buttons:
                btn.setVisible(True)
        else:
            # Hide all buttons
            for btn in self.buttons:
                btn.setVisible(False)
