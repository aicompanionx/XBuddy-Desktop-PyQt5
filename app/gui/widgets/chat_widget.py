from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, 
                            QLineEdit, QAction)
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QFont, QIcon

class ChatWidget(QWidget):
    # Signal emitted when a new message is sent
    message_sent = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.microphone_active = False
        self.init_ui()
        
    def init_ui(self):
        # Set up the main layout
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        
        # Create message display area
        self.message_area = QTextEdit()
        self.message_area.setReadOnly(True)
        self.message_area.setStyleSheet("""
            QTextEdit {
                background-color: #666;
                color: #ffffff;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        self.message_area.setFont(QFont('Arial', 12))
        
        # Create input area
        input_layout = QHBoxLayout()
        
        # Message input field
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Type your message here...")
        self.message_input.setStyleSheet("""
            QLineEdit {
                background-color: #666;
                color: #ffffff;
                border-radius: 10px;
                padding: 10px 15px;
            }
        """)
        self.message_input.returnPressed.connect(self.send_message)
        
        # Create send icon action
        send_action = QAction(self)
        send_action.setIcon(QIcon("resources/icons/tray_icon.png"))
        send_action.triggered.connect(self.send_message)
        self.message_input.addAction(send_action, QLineEdit.TrailingPosition)
        
        # Create microphone icon action
        microphone_action = QAction(self)
        microphone_action.setIcon(QIcon("resources/icons/logo.png"))
        microphone_action.triggered.connect(self.toggle_microphone)
        self.message_input.addAction(microphone_action, QLineEdit.TrailingPosition)
        
        # Add widgets to input layout
        input_layout.addWidget(self.message_input)
        
        # Add widgets to main layout
        main_layout.addWidget(self.message_area)
        main_layout.addLayout(input_layout)
        
        # Set window properties
        self.setWindowTitle("Chat")
        self.setGeometry(100, 100, 400, 500)
        self.setStyleSheet("background-color: #2c3e50;")
    
    # TODO: Implement microphone input
    def toggle_microphone(self):
        """Toggle microphone input"""
        print("Toggle microphone")
        if self.microphone_active:
            self.microphone_active = False
        else:
            self.microphone_active = True
        
    # TODO: Implement send message
    def send_message(self):
        """Handle sending a new message"""
        message = self.message_input.text().strip()
        if message:
            self.add_message(message, is_user=True)
            self.message_input.clear()
            self.message_sent.emit(message)
            
    def add_message(self, message, is_user=True):
        """Add a message to the chat display"""
        # Format the message with different colors for user and other messages
        if is_user:
            self.message_area.append(f'You: {message}')
        else:
            self.message_area.append(f'Assistant: {message}')
        
        # Scroll to the bottom
        self.message_area.verticalScrollBar().setValue(
            self.message_area.verticalScrollBar().maximum()
        )
        
    def receive_message(self, message):
        """Handle receiving a message from the assistant"""
        self.add_message(message, is_user=False)
