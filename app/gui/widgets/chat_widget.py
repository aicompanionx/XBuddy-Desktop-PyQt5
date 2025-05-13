from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton,
                            QLineEdit, QLabel)
from PyQt5.QtCore import pyqtSignal, QSize, Qt, QEvent, QTimer, QUrl
from PyQt5.QtGui import QFont, QIcon
from app.api.client import ApiClient
from app.gui.widgets.chat_window_widget import ChatWindowWidget
from app.api.chat_ws_client import ChatWebSocketClient
from app.api.endpoints import ApiRoutes

class ChatWidget(QWidget):
    # Signal emitted when a new message is sent
    message_sent = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.microphone_active = False
        self.input_padding = 16 # From previous calculation: (8px top + 8px bottom)
        self.one_line_input_height = 0
        self.three_lines_input_height = 0
        self.is_first_chunk = True # For managing streaming display

        # Test the chat window widget
        self.chat_window_instance = None # Initialize instance variable for the chat window
        
        # For answer display height calculation
        self.answer_padding = 20 # 10px top + 10px bottom from its stylesheet
        self.answer_min_height = 0
        self.answer_max_height = 0
        
        # Chat WebSocket client
        self.chat_ws_client = ChatWebSocketClient(self)
        self.chat_ws_client.message_received.connect(self.on_message_received)
        self.chat_ws_client.connected.connect(self.on_ws_connected)
        self.chat_ws_client.disconnected.connect(self.on_ws_disconnected)
        self.chat_ws_client.error.connect(self.on_ws_error)
        
        # Connect to chat WebSocket
        QTimer.singleShot(500, self.connect_to_chat_websocket)
        
        self.init_ui()
        
    def connect_to_chat_websocket(self):
        """Connect to the chat WebSocket server"""
        try:
            # Use ApiRoutes to get the WebSocket URL
            base_url = ApiClient.base_url
            if not base_url:  
                base_url = "https://api.xbuddy.me/dev/api/v1"
                
            api_routes = ApiRoutes(base_url)
            ws_url = api_routes.chat_ws()
            
            self.chat_ws_client.connect_to_server(ws_url)
            print(f"Connecting to chat WebSocket at: {ws_url}")
        except Exception as e:
            print(f"Error connecting to chat WebSocket: {e}")
            # 发生错误时使用硬编码URL作为备选
            try:
                fallback_url = "wss://api.xbuddy.me/dev/api/v1/chat/ws"
                print(f"Trying fallback chat WebSocket URL: {fallback_url}")
                self.chat_ws_client.connect_to_server(fallback_url)
            except Exception as fallback_e:
                print(f"Fallback chat connection also failed: {fallback_e}")
    
    def on_ws_connected(self):
        """Handle successful WebSocket connection"""
        print("Connected to chat WebSocket server")
    
    def on_ws_disconnected(self):
        """Handle WebSocket disconnection"""
        print("Disconnected from chat WebSocket server")
    
    def on_ws_error(self, error_message):
        """Handle WebSocket error"""
        print(f"Chat WebSocket error: {error_message}")
        
    def on_message_received(self, message, code):
        """Handle received message from WebSocket"""
        if code == 0: 
            if self.is_first_chunk:
                self.answer_display_area.clear()
                self.is_first_chunk = False
            self.stream_assistant_response_chunk(message)
        elif code == 1: 
            self.answer_display_area.clear()
            self.answer_display_area.setText(f"Error: {message}")
            self.finalize_assistant_response()
        elif code == 2:
            self.finalize_assistant_response()
        else:
            print(f"Unknown message code: {code}")

    def init_ui(self):
        # Allow ChatWidget itself to receive focus
        self.setFocusPolicy(Qt.StrongFocus)

        # Set up the main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(5) # Add a little spacing between answer and input
        self.setLayout(main_layout)
        
        # --- Answer Display Area (New) ---
        self.answer_display_area = QTextEdit()
        self.answer_display_area.setReadOnly(True)
        self.answer_display_area.setFont(QFont('Arial', 13)) # Slightly smaller than input
        self.answer_display_area.setStyleSheet("""
            QTextEdit {
                background-color: rgba(80, 80, 80, 0.9); /* Solid, slightly darker */
                color: #f0f0f0;
                border: none;
                border-radius: 15px; /* Consistent rounding */
                padding: 10px;
            }
        """)
        
        # Calculate min/max heights for answer_display_area
        ans_font_metrics = self.answer_display_area.fontMetrics()
        ans_line_height = ans_font_metrics.height()
        self.answer_min_height = ans_line_height + self.answer_padding # Min 1 line
        self.answer_max_height = (ans_line_height * 6) + self.answer_padding # Max 6 lines
        self.answer_display_area.setMinimumHeight(int(self.answer_min_height))
        self.answer_display_area.setMaximumHeight(int(self.answer_max_height))
        self.answer_display_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff) # No scrollbar
        self.answer_display_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.answer_display_area.hide() # Initially hidden

        # --- Input Container --- 
        self.input_container = QWidget() # Made it an instance variable
        input_container_layout = QHBoxLayout(self.input_container)
        input_container_layout.setContentsMargins(4, 4, 4, 4)
        input_container_layout.setSpacing(2)
        
        # Message input field - use QTextEdit for multi-line support
        self.message_input = QTextEdit()
        self.message_input.setPlaceholderText("Type your message here...")
        self.message_input.setFont(QFont('Arial', 14))
        self.message_input.setStyleSheet("""
            QTextEdit {
                background-color: transparent;
                color: #f0f0f0;
                border: none;
                padding: 8px 10px;
            }
        """)
        self.message_input.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff) # Hide horizontal scrollbar
        self.message_input.setAcceptRichText(False)
        
        # Calculate dynamic heights
        font_metrics = self.message_input.fontMetrics()
        text_line_height = font_metrics.height()
        self.one_line_input_height = text_line_height + self.input_padding
        self.three_lines_input_height = ((text_line_height + 5) * 3) + self.input_padding

        self.message_input.setMinimumHeight(int(self.one_line_input_height))
        self.message_input.setMaximumHeight(int(self.three_lines_input_height))
        self.message_input.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff) # Hide scrollbar
        
        # Connect text changed event to auto-adjust height
        self.message_input.textChanged.connect(self.adjust_input_height)
        self.message_input.installEventFilter(self) # Install event filter
        self.message_input.clearFocus() # Ensure input field doesn't have initial focus
        
        # Create send button
        send_action = QPushButton(self)
        send_action.setIcon(QIcon("resources/icons/send-icon.png"))
        send_action.setIconSize(QSize(18, 18))
        send_action.clicked.connect(self.send_message)
        
        # Create microphone button
        microphone_action = QPushButton(self)
        microphone_action.setIcon(QIcon("resources/icons/microphone-icon.png"))
        microphone_action.setIconSize(QSize(18, 18))
        microphone_action.clicked.connect(self.toggle_microphone)
        
        button_style = """
            QPushButton {
                background-color: transparent;
                border: none;
                min-width: 20px;
                max-width: 20px;
                min-height: 20px;
                max-height: 20px;
                border-radius: 10px;
            }
            QPushButton:last {
                margin-right: 10px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
            }
            QPushButton:pressed {
                background-color: rgba(0, 0, 0, 0.1);
            }
        """
        send_action.setStyleSheet(button_style)
        microphone_action.setStyleSheet(button_style)
        
        # Add widgets to the input container layout
        input_container_layout.addWidget(self.message_input, 1)  # Give input stretch factor
        input_container_layout.addWidget(microphone_action, 0)
        input_container_layout.addWidget(send_action, 0)
        
        # Apply style to the container
        self.input_container.setStyleSheet(""" 
            QWidget {
                background-color: rgba(102, 102, 102, 0.9);
                border-radius: 20px;
                color: #ffffff;
                padding: 4px;
            }
        """)
        
        # Add widgets to main layout
        main_layout.addWidget(self.answer_display_area, 0) # Added, will manage visibility
        main_layout.addWidget(self.input_container, 0)
        
        # Set overall widget style
        self.setStyleSheet("background-color: #222;")
        
        # Set initial height of the input field
        self.adjust_input_height()
        self.setFocus() # Give initial focus to the ChatWidget itself
    
    def eventFilter(self, obj, event):
        if obj is self.message_input and event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
                if event.modifiers() & Qt.ShiftModifier:
                    # Shift+Enter: Let QTextEdit handle it for a newline
                    return super().eventFilter(obj, event) # Or simply return False
                else:
                    # Enter alone: Send message and consume the event
                    self.send_message()
                    return True # Event handled
        # Default processing for other objects or events
        return super().eventFilter(obj, event)
    
    def adjust_input_height(self):
        """Adjust the height of the input field based on content"""
        doc_height = self.message_input.document().size().toSize().height()
        # Ideal height of the widget based on content and its internal padding
        target_widget_height = doc_height + self.input_padding
        
        # Clamp the target height between the pre-calculated 1-line and 3-line heights
        clamped_height = max(self.one_line_input_height, min(target_widget_height, self.three_lines_input_height))
        
        # Ensure integer value and update if different
        clamped_height = int(clamped_height)
        if self.message_input.height() != clamped_height:
            self.message_input.setFixedHeight(clamped_height)
    
    def adjust_answer_display_height(self):
        """Adjusts the height of the answer display area based on its content."""
        doc_height = self.answer_display_area.document().size().toSize().height()
        target_widget_height = doc_height + self.answer_padding
        clamped_height = max(self.answer_min_height, min(target_widget_height, self.answer_max_height))
        clamped_height = int(clamped_height)
        if self.answer_display_area.height() != clamped_height:
            self.answer_display_area.setFixedHeight(clamped_height)
    
    def toggle_microphone(self):
        """Toggle microphone input"""
        print("Toggle microphone")
        self.microphone_active = not self.microphone_active

        # Test the chat window widget
        if self.chat_window_instance is None or not self.chat_window_instance.isVisible():
            self.chat_window_instance = ChatWindowWidget()
            self.chat_window_instance.resize(800, 500)
            self.chat_window_instance.setMinimumWidth(600)
            self.chat_window_instance.setMinimumHeight(400)
            self.chat_window_instance.setWindowTitle("XBuddy/Chat")
            
            # Connect the chat window's WebSocket client to the main chat widget's client
            # This allows for shared connection between both interfaces
            if hasattr(self, 'chat_ws_client') and self.chat_ws_client.is_connected:
                self.chat_window_instance.set_chat_ws_client(self.chat_ws_client)
            
            self.chat_window_instance.show()
            
            # Connect signals for message forwarding
            self.chat_window_instance.send_message_signal.connect(self.handle_chat_window_message)
        else:
            self.chat_window_instance.activateWindow()
            self.chat_window_instance.raise_()
            
    def handle_chat_window_message(self, message):
        """Handle messages sent from the chat window"""
        if self.chat_ws_client.is_connected:
            # Detect language of message from chat window
            lang = self.detect_language(message)
            self.chat_ws_client.send_message(message, lang)
    
    def send_message(self):
        """Handle sending a new message"""
        message = self.message_input.toPlainText().strip()
        if message:
            # Detect language of message
            lang = self.detect_language(message)
            
            # --- Add user message to the separate chat window if it exists --- 
            if self.chat_window_instance and self.chat_window_instance.isVisible():
                self.chat_window_instance.add_message(message, True)
            # ---------------------------------------------------------------
            
            self.input_container.hide() # Hide input while assistant is responding

            self.answer_display_area.clear() 
            self.answer_display_area.setText("Let me think...")
            self.adjust_answer_display_height() 
            if not self.answer_display_area.isVisible():
                self.answer_display_area.show()
            self.is_first_chunk = True

            self.message_input.clear()
            self.message_sent.emit(message)
            
            # Send message via WebSocket with language parameter
            if self.chat_ws_client.is_connected:
                self.chat_ws_client.send_message(message, lang)
            else:
                print("Cannot send message: Not connected to chat server")
                self.answer_display_area.setText("Error: Not connected to chat server")
                self.finalize_assistant_response()

    def detect_language(self, text):
        """Detect if text is primarily Chinese or English"""
        # Simple check for Chinese characters
        chinese_chars = 0
        for char in text:
            if '\u4e00' <= char <= '\u9fff':
                chinese_chars += 1
                
        # If more than 20% of characters are Chinese, consider it Chinese
        if chinese_chars > 0 and chinese_chars / len(text) > 0.2:
            return "zh"
        return "en"

    # --- Methods for streaming response --- 
    def stream_assistant_response_chunk(self, chunk: str):
        """Appends a chunk of the assistant's response to the display area."""
        if self.is_first_chunk:
            self.answer_display_area.clear() # Clear "Let me think..."
            self.is_first_chunk = False
        self.answer_display_area.insertPlainText(chunk)
        self.answer_display_area.ensureCursorVisible() # Scroll to end
        self.adjust_answer_display_height() # Adjust height after each chunk

    def finalize_assistant_response(self):
        """Called when the assistant has finished streaming its response."""
        # --- Add final assistant response to the separate chat window if it exists --- 
        if self.chat_window_instance and self.chat_window_instance.isVisible():
            full_response = self.answer_display_area.toPlainText()
            self.chat_window_instance.add_message(full_response, False)
        # -------------------------------------------------------------------------
        
        # Answer area remains visible with its content.
        self.input_container.show() # Show input again
        self.message_input.setFocus()