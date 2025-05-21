from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
)


class TitleBar(QFrame):
    def __init__(self, parent=None, title=""):
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
        self.maxBtn.clicked.connect(self.toggle_max_restore)
        self.closeBtn.clicked.connect(parent.close)

        layout = QHBoxLayout()
        layout.addWidget(self.title)
        layout.addStretch()
        layout.addWidget(self.minBtn)
        layout.addWidget(self.maxBtn)
        layout.addWidget(self.closeBtn)
        layout.setContentsMargins(10, 0, 0, 0)
        self.setLayout(layout)

    def toggle_max_restore(self):
        parent = self.parent()
        if parent.isMaximized():
            parent.showNormal()
            self.maxBtn.setText("□")
        else:
            parent.showMaximized()
            self.maxBtn.setText("❐")

    def mousePressEvent(self, event):
        self.start = event.globalPos()
        self.pressing = True

    def mouseMoveEvent(self, event):
        if self.pressing:
            self.parent().move(self.parent().pos() + event.globalPos() - self.start)
            self.start = event.globalPos()

    def mouseReleaseEvent(self, event):
        self.pressing = False
