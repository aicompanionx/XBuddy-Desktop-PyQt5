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
    def __init__(self, parent=None, icon_path=None, on_click=None):
        super().__init__(parent)

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

    def set_scale(self, scale):
        self.setFixedSize(int(50 * scale), int(50 * scale))
        self.setIconSize(QSize(int(24 * scale), int(24 * scale)))


class ButtonLive2DWidget(LipSyncLive2DWidget):
    def __init__(self):
        super().__init__()
        self.buttons = [
            PetButton(self, icon_path=RESOURCES_DIRECTORY / 'icons/message.svg',
                      on_click=self.on_click_message),
            PetButton(self, icon_path=RESOURCES_DIRECTORY / 'icons/switch.svg',
                      on_click=self.on_click_switch),
            PetButton(self, icon_path=RESOURCES_DIRECTORY / 'icons/settings.svg',
                      on_click=self.on_click_settings),
            PetButton(self, icon_path=RESOURCES_DIRECTORY / 'icons/volume.svg',
                      on_click=self.on_click_volume),
            PetButton(self, icon_path=RESOURCES_DIRECTORY / 'icons/news.svg',
                      on_click=None),
            PetButton(self, icon_path=RESOURCES_DIRECTORY / 'icons/x.svg',
                      on_click=self.on_click_x),
        ]
        self.settings_window = SettingsWindow()

        self.buttons[0].move(50, 150)
        self.buttons[1].move(0, 275)
        self.buttons[2].move(50, 400)
        self.buttons[3].move(500, 150)
        self.buttons[4].move(550, 275)
        self.buttons[5].move(500, 400)

    def mousePressEvent(self, event: QMouseEvent):
        super().mousePressEvent(event)
        if event.button() == Qt.MouseButton.RightButton:
            print('show buttons')
            # Show all buttons
            for btn in self.buttons:
                btn.setVisible(True)
        else:
            print('hide buttons')
            # Hide all buttons
            for btn in self.buttons:
                btn.setVisible(False)

    def on_click_message(self):
        self.set_scale(0.8)

    def on_click_switch(self):
        if self.model_list:
            self.model_path: str = random.choice(self.model_list)
        self.model = live2d.LAppModel()
        self.model.LoadModelJson(self.model_path)
        self.model.SetScale(0.8)
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

    def set_scale(self, scale):
        for btn in self.buttons:
            btn.set_scale(scale)

        self.model = live2d.LAppModel()
        self.model.LoadModelJson(self.model_path)
        self.model.SetScale(0.8 * scale)
        self.paintGL()
        self.resizeGL(self.width(), self.height())


def run(window_class: type):
    live2d.init()
    app = QApplication(sys.argv)
    win = window_class()
    win.show()
    app.exec()
    # Clean up worker thread by deleting the window object which calls its destructor
    del win
    live2d.dispose()


if __name__ == '__main__':
    run(ButtonLive2DWidget)
