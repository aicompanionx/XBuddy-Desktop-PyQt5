from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QIcon, QPainter
from PyQt5.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from xbuddy.gui.utils import transparent_and_taskbar
from xbuddy.gui.widgets.base_widgets import TitleBar


class SidebarButton(QPushButton):
    """Sidebar button with selected and unselected states"""

    def __init__(self, text, icon_path=None, parent=None):
        super().__init__(text, parent)

        # Set icon if path is provided
        if icon_path:
            self.setIcon(QIcon(icon_path))
            self.setIconSize(Qt.QSize(24, 24))

        # Set button style
        self.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #b9bbbe;
                border: none;
                border-radius: 4px;
                text-align: left;
                padding: 8px 12px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #4f545c;
                color: #ffffff;
            }
            QPushButton:checked {
                background-color: #7289da;
                color: #ffffff;
            }
        """)

        # Button can be selected
        self.setCheckable(True)

        # Set minimum height
        self.setMinimumHeight(40)


class SettingsWindow(QWidget):
    def __init__(self):
        super().__init__()
        transparent_and_taskbar(self)
        self.setMinimumSize(600, 450)

        self.titleBar = TitleBar(self, "Settings")
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.titleBar)
        main_layout.setContentsMargins(2, 2, 2, 2)
        main_layout.setSpacing(0)

        # Create content area layout (horizontal layout, left menu + right content)
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # Create left sidebar area
        self.sidebar = QFrame()
        self.sidebar.setStyleSheet("""
            QFrame {
                background-color: #2f3136;
                border-right: 1px solid #202225;
                min-width: 150px;
                max-width: 200px;
            }
        """)

        # Create sidebar layout
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(8, 16, 8, 16)
        sidebar_layout.setSpacing(8)

        # Add menu buttons
        self.menu_buttons = []

        # Create common menu buttons
        self.btn_general = SidebarButton("General")
        self.btn_appearance = SidebarButton("Appearance")
        self.btn_model = SidebarButton("Model")
        self.btn_voice = SidebarButton("Voice")
        self.btn_about = SidebarButton("About")

        # Add buttons to layout
        sidebar_layout.addWidget(self.btn_general)
        sidebar_layout.addWidget(self.btn_appearance)
        sidebar_layout.addWidget(self.btn_model)
        sidebar_layout.addWidget(self.btn_voice)
        sidebar_layout.addWidget(self.btn_about)

        # Add stretch space
        sidebar_layout.addStretch()

        # Add buttons to list for management
        self.menu_buttons = [
            self.btn_general,
            self.btn_appearance,
            self.btn_model,
            self.btn_voice,
            self.btn_about,
        ]

        # Create stacked widget for content area to switch between pages
        self.content_stack = QStackedWidget()
        self.content_stack.setStyleSheet("background-color: #36393f;")

        # Create individual pages
        self.page_general = QWidget()
        self.page_general.setStyleSheet("background-color: #36393f;")
        general_layout = QVBoxLayout(self.page_general)
        general_layout.addWidget(QLabel("General Settings Page"))

        self.page_appearance = QWidget()
        self.page_appearance.setStyleSheet("background-color: #36393f;")
        appearance_layout = QVBoxLayout(self.page_appearance)
        appearance_layout.addWidget(QLabel("Appearance Settings Page"))

        self.page_model = QWidget()
        self.page_model.setStyleSheet("background-color: #36393f;")
        model_layout = QVBoxLayout(self.page_model)
        model_layout.addWidget(QLabel("Model Settings Page"))

        self.page_voice = QWidget()
        self.page_voice.setStyleSheet("background-color: #36393f;")
        voice_layout = QVBoxLayout(self.page_voice)
        voice_layout.addWidget(QLabel("Voice Settings Page"))

        self.page_about = QWidget()
        self.page_about.setStyleSheet("background-color: #36393f;")
        about_layout = QVBoxLayout(self.page_about)
        about_layout.addWidget(QLabel("About Page"))

        # Add pages to stacked widget
        self.content_stack.addWidget(self.page_general)
        self.content_stack.addWidget(self.page_appearance)
        self.content_stack.addWidget(self.page_model)
        self.content_stack.addWidget(self.page_voice)
        self.content_stack.addWidget(self.page_about)

        # Connect button click signals
        self.btn_general.clicked.connect(lambda: self.switch_page(0))
        self.btn_appearance.clicked.connect(lambda: self.switch_page(1))
        self.btn_model.clicked.connect(lambda: self.switch_page(2))
        self.btn_voice.clicked.connect(lambda: self.switch_page(3))
        self.btn_about.clicked.connect(lambda: self.switch_page(4))

        # Set default selected page
        self.switch_page(0)

        # Add sidebar and content area to the content layout
        content_layout.addWidget(self.sidebar)
        content_layout.addWidget(self.content_stack, 1)

        # Add content layout to main layout
        main_layout.addLayout(content_layout, 1)

        # Set main layout
        self.setLayout(main_layout)

        self._maximized = False

    def switch_page(self, index):
        """Switch page and update button states"""
        # Update all button selection states
        for i, btn in enumerate(self.menu_buttons):
            btn.setChecked(i == index)

        # Switch to corresponding page
        self.content_stack.setCurrentIndex(index)

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
