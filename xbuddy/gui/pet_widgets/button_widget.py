from live2d.v3 import live2d
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QMouseEvent

from xbuddy.api.schemas.news import News
from xbuddy.api.utils import WebSocketWorker
from xbuddy.gui.widgets.button_window import ButtonWindow
from xbuddy.gui.pet_widgets.penetration_widget import PenetrationLive2DWidget
from xbuddy.gui.utils import get_logger, run
from xbuddy.settings import DEFAULT_MODEL_SCALE, RESOURCES_DIRECTORY

logger = get_logger(__name__)


class ButtonLive2DWidget(PenetrationLive2DWidget):
    def __init__(self):
        super().__init__()
        self.btn_win = ButtonWindow()
        self.btn_win.hide_widgets()
        self.btn_win.show()

        self.btn_win.message_btn.clicked.connect(self.on_click_message)
        self.btn_win.switch_btn.clicked.connect(self.on_click_switch)
        self.btn_win.settings_btn.clicked.connect(self.on_click_settings)
        self.btn_win.volume_btn.clicked.connect(self.on_click_volume)
        self.btn_win.news_btn.clicked.connect(self.on_click_news)

        self.news_worker = WebSocketWorker("/dev/api/v1/news/ws", News)
        self.news_worker.message_received.connect(self.update_label)
        self.news_worker.start()

    def mousePressEvent(self, a0: QMouseEvent | None):
        super().mousePressEvent(a0)
        if a0.button() == Qt.MouseButton.RightButton:
            print("show buttons")
            self.btn_win.move_window_to(self)
            self.btn_win.show_widgets()
        else:
            print("hide buttons")
            self.btn_win.hide_widgets()

    def mouseMoveEvent(self, a0: QMouseEvent | None):
        super().mouseMoveEvent(a0)
        self.btn_win.move_window_to(self)

    def update_label(self, message):
        self.btn_win.move_window_to(self)
        self.btn_win.input_panel.show_toast(News.model_validate_json(message).abstract)

    def on_click_message(self):
        pass

    def on_click_switch(self):
        index = self.model_list.index(self.model_path)
        self.model_path = self.model_list[(index + 1) % len(self.model_list)]

        self.model = live2d.LAppModel()
        self.model.LoadModelJson(self.model_path)
        self.model.SetScale(DEFAULT_MODEL_SCALE)
        self.paintGL()
        self.resizeGL(self.width(), self.height())

    def on_click_settings(self):
        pass
        # self.settings_window.show()

    def on_click_volume(self):
        clicked_button = self.sender()
        if not getattr(clicked_button, "state", None):
            clicked_button.state = "on"
        if clicked_button.state == "on":
            clicked_button.setIcon(
                QIcon(str(RESOURCES_DIRECTORY / "icons/volume-off.svg"))
            )
            clicked_button.state = "off"
            self.play_sound_enabled = False
        elif clicked_button.state == "off":
            clicked_button.setIcon(QIcon(str(RESOURCES_DIRECTORY / "icons/volume.svg")))
            clicked_button.state = "on"
            self.play_sound_enabled = True

    def on_click_news(self):
        pass

    def closeEvent(self, a0):
        super().closeEvent(a0)
        self.news_worker.stop()
        self.news_worker.quit()
        self.news_worker.wait()


if __name__ == "__main__":
    run(ButtonLive2DWidget)
