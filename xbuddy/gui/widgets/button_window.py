import sys

from PyQt5.QtCore import (
    QEasingCurve,
    QPropertyAnimation,
    QSize,
    Qt,
    QTimer,
)
from PyQt5.QtGui import (
    QIcon,
)
from PyQt5.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from xbuddy.gui.utils import get_logger, transparent
from xbuddy.settings import QSS, RESOURCES_DIRECTORY

logger = get_logger(__name__)


class InputPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self._set_stylesheet()

        self.setVisible(True)
        self.input_field.setVisible(False)
        self.send_button.setVisible(False)
        self.microphone_button.setVisible(False)
        self.message_label.setVisible(False)

    def _set_stylesheet(self):
        self.input_field.setStyleSheet(QSS)

        self.send_button.setObjectName("sendBtn")
        self.send_button.setStyleSheet(QSS)
        self.microphone_button.setObjectName("microphoneBtn")
        self.microphone_button.setStyleSheet(QSS)

        self.message_label.setStyleSheet(QSS)
        self.message_label.setMinimumWidth(300)
        self.message_label.setMaximumHeight(100)
        # size = self.message_label.sizeHint()
        # self.message_label.setFixedHeight(size.height())

    def init_ui(self):
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(15)

        self.input_layout = QHBoxLayout()
        self.input_layout.setContentsMargins(0, 0, 0, 0)
        self.input_layout.setSpacing(0)

        self.message_layout = QHBoxLayout()
        self.message_layout.setContentsMargins(0, 0, 0, 0)
        self.message_layout.setSpacing(0)

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Type your message...")
        self.input_field.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        self.send_button = QPushButton()
        self.send_button.setIcon(QIcon(str(RESOURCES_DIRECTORY / "icons/send.svg")))
        self.send_button.setIconSize(QSize(24, 24))
        self.send_button.setCursor(Qt.PointingHandCursor)
        self.send_button.clicked.connect(self.on_send)

        self.microphone_button = QPushButton()
        self.microphone_button.setIcon(
            QIcon(str(RESOURCES_DIRECTORY / "icons/microphone.svg"))
        )
        self.microphone_button.setIconSize(QSize(24, 24))
        self.microphone_button.setCursor(Qt.PointingHandCursor)
        self.microphone_button.clicked.connect(self.on_microphone)

        self.message_label = QLabel('no content')
        self.message_label.setAlignment(Qt.AlignCenter)
        self.message_label.setWordWrap(True)

        self.input_layout.addWidget(self.input_field)
        self.input_layout.addWidget(self.send_button)
        self.input_layout.addWidget(self.microphone_button)

        self.message_layout.addWidget(self.message_label)

        self.main_layout.addLayout(self.message_layout)
        self.main_layout.addLayout(self.input_layout)

        self.setLayout(self.main_layout)

        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)

        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self._fade_out)

    def show_toast(self, text: str, duration: int = 6000):
        self.message_label.setText(text)
        self.message_label.show()
        self.timer.start(duration)

    def _fade_out(self):
        self.message_label.hide()

    def on_send(self):
        content = self.input_field.text()
        print("send:", content)
        self.input_field.setText("")

    def on_microphone(self):
        print("on microphone")


class RightButton(QPushButton):
    BUTTON_SIZE = 50
    ICON_SIZE = 25

    def __init__(self, parent=None, icon_path=None, on_click=None):
        super().__init__(parent)
        self.setStyleSheet(QSS)

        self.setFixedSize(self.BUTTON_SIZE, self.BUTTON_SIZE)
        self.setCursor(Qt.PointingHandCursor)

        if icon_path:
            self.setIcon(QIcon(str(icon_path)))
            self.setIconSize(
                QSize(self.ICON_SIZE, self.ICON_SIZE)
            )  # Adjust icon size if needed

        if on_click:
            self.clicked.connect(on_click)

    def set_scale(self, scale):
        self.setFixedSize(int(self.BUTTON_SIZE * scale), int(self.BUTTON_SIZE * scale))
        self.setIconSize(
            QSize(int(self.ICON_SIZE * scale), int(self.ICON_SIZE * scale))
        )


class ButtonWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.init_window()
        self.init_widgets()
        self.move_widgets()
        # self.update_window_mask()

    def init_window(self):
        self.setGeometry(400, 200, 600, 900)
        self.setWindowOpacity(0.8)
        transparent(self)

    def init_widgets(self):
        self.input_panel = InputPanel(self)
        self.input_panel.setMaximumHeight(200)
        self.input_panel.setMaximumWidth(400)

        self.central_widget = QWidget(self)
        self.central_widget.setAttribute(Qt.WA_TranslucentBackground)
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)
        self.layout.addWidget(self.input_panel, alignment=Qt.AlignHCenter)
        placeholder_widget = QWidget(self.central_widget)
        placeholder_widget.setMaximumWidth(1)
        self.layout.addWidget(placeholder_widget)

        self.message_btn = RightButton(
            self.central_widget,
            icon_path=RESOURCES_DIRECTORY / "icons/message.svg",
        )
        self.switch_btn = RightButton(
            self.central_widget,
            icon_path=RESOURCES_DIRECTORY / "icons/switch.svg",
        )
        self.settings_btn = RightButton(
            self.central_widget,
            icon_path=RESOURCES_DIRECTORY / "icons/settings.svg",
        )
        self.volume_btn = RightButton(
            self.central_widget,
            icon_path=RESOURCES_DIRECTORY / "icons/volume.svg",
        )
        self.news_btn = RightButton(
            self.central_widget,
            icon_path=RESOURCES_DIRECTORY / "icons/news.svg",
        )
        self.close_btn = RightButton(
            self.central_widget,
            icon_path=RESOURCES_DIRECTORY / "icons/x.svg",
            on_click=self.hide,
        )

        self.buttons = [
            self.message_btn,
            self.switch_btn,
            self.settings_btn,
            self.volume_btn,
            self.news_btn,
            self.close_btn,
        ]

    def move_window_to(self, ref_window: QWidget):
        center_pos = ref_window.geometry().center()
        new_x = center_pos.x() - self.size().width() // 2
        new_y = center_pos.y() - self.size().height() // 2
        self.move(new_x, new_y)

    def move_widgets(self, scale: float = 1):
        center_x = self.width() // 2
        center_y = self.height() // 2

        self.message_btn.move(
            center_x + int(-200 * scale), center_y + int(-150 * scale)
        )
        self.switch_btn.move(center_x + int(-250 * scale), center_y + int(-25 * scale))
        self.settings_btn.move(
            center_x + int(-200 * scale), center_y + int(100 * scale)
        )
        self.volume_btn.move(center_x + int(150 * scale), center_y + int(-150 * scale))
        self.news_btn.move(center_x + int(200 * scale), center_y + int(-25 * scale))
        self.close_btn.move(center_x + int(150 * scale), center_y + int(100 * scale))

        self.input_panel.move(center_x, center_y)

    def show_widgets(self):
        self.show()
        for button in self.buttons:
            button.show()
        self.input_panel.input_field.setVisible(True)
        self.input_panel.send_button.setVisible(True)
        self.input_panel.microphone_button.setVisible(True)
        print(f"show button widget at {self.geometry().center()}")

    def hide_widgets(self):
        for button in self.buttons:
            button.hide()
        self.input_panel.input_field.setVisible(False)
        self.input_panel.send_button.setVisible(False)
        self.input_panel.microphone_button.setVisible(False)

    # def update_window_mask(self):
    #     pixmap = QPixmap(self.size())
    #     pixmap.fill(Qt.transparent)
    #     image = pixmap.toImage()
    #
    #     region = None
    #     mask_mono_image = image.createAlphaMask(Qt.ThresholdAlphaDither)
    #     if not mask_mono_image.isNull():
    #         mask_bitmap = QBitmap.fromImage(mask_mono_image)
    #         region = QRegion(mask_bitmap)
    #     if region:
    #         self.setMask(region)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ButtonWindow()
    window.show()
    sys.exit(app.exec_())
