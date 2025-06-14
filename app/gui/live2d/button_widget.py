import random
import sys

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QMouseEvent
from PyQt5.QtWidgets import QPushButton, QApplication
from live2d.v3 import live2d

from app.gui.live2d.base_widget import RESOURCES_DIRECTORY
from app.gui.live2d.lip_sync_widget import LipSyncLive2DWidget
from app.gui.widgets.settings_widget import SettingsWindow


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
            PetButton(icon_path=RESOURCES_DIRECTORY / 'icons/switch.svg',
                      on_click=self.on_click_switch),
            PetButton(icon_path=RESOURCES_DIRECTORY / 'icons/settings.svg',
                      on_click=self.on_click_settings),
            PetButton(icon_path=RESOURCES_DIRECTORY / 'icons/volume.svg',
                      on_click=self.on_click_volume),
            PetButton(icon_path=RESOURCES_DIRECTORY / 'icons/news.svg',
                      on_click=None),
            PetButton(icon_path=RESOURCES_DIRECTORY / 'icons/x.svg',
                      on_click=self.on_click_x),
        ]
        self.settings_window = SettingsWindow()

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

    def on_click_switch(self):
        if self.model_list:
            self.model_path: str = random.choice(self.model_list)
        self.model = live2d.LAppModel()
        self.model.LoadModelJson(self.model_path)
        self.model.SetScale(0.5)
        self.paintGL()
        self.resizeGL(self.width(), self.height())

    def on_click_settings(self):
        self.settings_window.show()

    def on_click_volume(self):
        clicked_button = self.sender()
        if not getattr(clicked_button, 'state', None):
            clicked_button.state = 'on'
        if clicked_button.state == 'on':
            clicked_button.setIcon(QIcon(str(RESOURCES_DIRECTORY / 'icons/volume-off.svg')))
            clicked_button.state = 'off'
            self.play_sound_enabled = False
        elif clicked_button.state == 'off':
            clicked_button.setIcon(QIcon(str(RESOURCES_DIRECTORY / 'icons/volume.svg')))
            clicked_button.state = 'on'
            self.play_sound_enabled = True

    def on_click_x(self):
        # Hide all buttons
        for btn in self.buttons:
            btn.setVisible(False)
