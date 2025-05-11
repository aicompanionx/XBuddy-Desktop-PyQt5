import sys
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QColor, QPainter, QIcon
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel,
    QVBoxLayout, QHBoxLayout, QFrame, QSizePolicy
)


class TitleBar(QFrame):
    def __init__(self, parent=None, title=''):
        super().__init__(parent)
        self.setFixedHeight(35)
        self.setStyleSheet("background-color: #2f3136;")
        self.start = QPoint(0, 0)
        self.pressing = False

        self.title = QLabel(title)
        self.title.setStyleSheet("color: white; font-size: 14px;")
        self.title.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)

        self.minBtn = QPushButton("-")
        self.maxBtn = QPushButton("□")
        self.closeBtn = QPushButton("×")

        for btn in [self.minBtn, self.maxBtn, self.closeBtn]:
            btn.setFixedSize(30, 30)
            btn.setStyleSheet("""
                QPushButton {
                    color: white;
                    background-color: transparent;
                    border: none;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #4f545c;
                }
            """)

        self.minBtn.clicked.connect(parent.showMinimized)
        self.maxBtn.clicked.connect(parent.toggleMaximize)
        self.closeBtn.clicked.connect(parent.close)

        layout = QHBoxLayout()
        layout.addWidget(self.title)
        layout.addStretch()
        layout.addWidget(self.minBtn)
        layout.addWidget(self.maxBtn)
        layout.addWidget(self.closeBtn)
        layout.setContentsMargins(10, 0, 0, 0)
        self.setLayout(layout)

    def mousePressEvent(self, event):
        self.start = event.globalPos()
        self.pressing = True

    def mouseMoveEvent(self, event):
        if self.pressing:
            self.parent().move(self.parent().pos() + event.globalPos() - self.start)
            self.start = event.globalPos()

    def mouseReleaseEvent(self, event):
        self.pressing = False


class SettingsWindow(QWidget):
    def __init__(self):
        super().__init__()
        # Configure window for transparency and always-on-top without focus stealing
        self.setWindowFlags(
            Qt.FramelessWindowHint |  # Borderless window
            Qt.WindowStaysOnTopHint |  # Always on top
            Qt.Tool |  # Do not show in taskbar
            Qt.NoDropShadowWindowHint |  # No shadow
            Qt.WindowDoesNotAcceptFocus  # Don't steal focus
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setMinimumSize(500, 400)

        self.titleBar = TitleBar(self, 'Settings')

        self.mainContent = QLabel("Main Area")
        self.mainContent.setStyleSheet("color: #dcddde; font-size: 16px;")
        self.mainContent.setAlignment(Qt.AlignCenter)


        layout = QVBoxLayout()
        layout.addWidget(self.titleBar)
        layout.addWidget(self.mainContent)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(0)
        self.setLayout(layout)

        self._maximized = False

    def toggleMaximize(self):
        if self._maximized:
            self.showNormal()
        else:
            self.showMaximized()
        self._maximized = not self._maximized

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QColor("#36393f"))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(self.rect(), 10, 10)
